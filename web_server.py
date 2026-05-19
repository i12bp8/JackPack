#!/usr/bin/env python3
"""
JackPack WebUI HTTP server
--------------------------
Serves the static WebUI and exposes a small, read-only API to browse loot/.

Routes:
  /                  -> static WebUI (web/)
  /api/loot/list      -> JSON directory listing (read-only)
  /api/loot/download  -> file download (read-only)
  /api/loot/view      -> text preview (read-only)
    /api/loot/nmap      -> normalized Nmap XML (read-only)
  /api/system/status  -> live system monitor metrics
  /api/settings/discord_webhook -> get/save Discord webhook
  /api/auth/*         -> bootstrap/login/session endpoints

Environment:
  RJ_WEB_HOST  Host to bind (default: 0.0.0.0)
  RJ_WEB_PORT  Port to bind (default: 8080)
  RJ_WS_TOKEN  Optional shared token for API access (Bearer header)
  RJ_WS_TOKEN_FILE Optional token file (default: <repo>/.webui_token)
  RJ_WEB_AUTH_FILE Auth user storage file (default: /root/JackPack/.webui_auth.json)
  RJ_WEB_AUTH_SECRET_FILE Session signing secret file (default: /root/JackPack/.webui_session_secret)
  RJ_WEB_SESSION_TTL Session lifetime seconds (default: 28800)
  RJ_WEB_WS_TICKET_TTL WS ticket lifetime seconds (default: 120)
"""

from __future__ import annotations

import ast
import json
import base64
import hmac
import hashlib
import mimetypes
import os
import re
import secrets
import shutil
import socket
import subprocess
import threading
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote

from nmap_parser import parse_nmap_xml_file

try:
    from packjack import payload_runner
except Exception:
    payload_runner = None

try:
    from packjack import interfaces as jp_ifaces
except Exception:
    jp_ifaces = None

ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"
LOOT_DIR = ROOT_DIR / "loot"
PAYLOADS_DIR = ROOT_DIR / "payloads"
NATIVE_PAYLOADS_DIR = PAYLOADS_DIR / "jackpack"
PAYLOAD_STATE_PATH = Path("/dev/shm/rj_payload_state.json")
DISCORD_WEBHOOK_PATH = ROOT_DIR / "discord_webhook.txt"
WIGLE_CREDENTIALS_PATH = ROOT_DIR / ".wigle_credentials.json"
TOKEN_FILE = Path(os.environ.get("RJ_WS_TOKEN_FILE", str(ROOT_DIR / ".webui_token")))
AUTH_FILE = Path(os.environ.get("RJ_WEB_AUTH_FILE", "/root/JackPack/.webui_auth.json"))
AUTH_SECRET_FILE = Path(os.environ.get("RJ_WEB_AUTH_SECRET_FILE", "/root/JackPack/.webui_session_secret"))
SESSION_COOKIE_NAME = "rj_session"
SESSION_TTL_SECONDS = int(os.environ.get("RJ_WEB_SESSION_TTL", str(8 * 60 * 60)))
WS_TICKET_TTL_SECONDS = int(os.environ.get("RJ_WEB_WS_TICKET_TTL", "120"))
TAILSCALE_KEY_PATH = ROOT_DIR / ".tailscale_auth_key"
TAILSCALE_STATUS_PATH = Path("/dev/shm/rj_tailscale_status.json")
PAYLOAD_LOG_PATH = LOOT_DIR / "payload.log"
PACKJACK_ENV_PATH = Path(os.environ.get("JACKPACK_ENV_FILE", "/etc/packjack/packjack.env"))
PACKJACK_ENV_FALLBACK_PATH = ROOT_DIR / ".packjack.env"
UPDATE_STATUS_PATH = Path(os.environ.get("JACKPACK_UPDATE_STATUS_PATH", "/dev/shm/jackpack_update_status.json"))

_UPDATE_LOCK = threading.Lock()
_PAYLOAD_LIST_CACHE: dict[str, object] = {"ts": 0.0, "payload": None}
_IFACE_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,32}$")
_MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
_HOSTNAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_ALLOWED_RUNTIME_CONFIG = {
    "JACKPACK_AP_IFACE",
    "JACKPACK_AP_SSID",
    "JACKPACK_AP_PASSWORD",
    "JACKPACK_AP_ADDRESS",
    "JACKPACK_AP_CHANNEL",
    "JACKPACK_ATTACK_IFACE",
    "JACKPACK_WIRED_IFACE",
    "JACKPACK_HOSTNAME",
    "RJ_WEB_PORT",
    "RJ_WS_PORT",
}
_SENSITIVE_RUNTIME_CONFIG = {"JACKPACK_AP_PASSWORD"}
_CATEGORY_INFO = {
    "reconnaissance": ("Reconnaissance", "Discover hosts, services, cameras, wireless clients, and useful network context."),
    "wifi": ("WiFi", "Wireless assessment workflows for the external USB adapter."),
    "network": ("Network", "Layer 2/3 network tools for the Pi 5 Ethernet port and connected target networks."),
    "credentials": ("Credentials", "Credential audit helpers for authorized lab and red-team engagements."),
    "exfiltration": ("Exfiltration", "Controlled data movement simulations and alerting tests."),
    "remote_access": ("Remote Access", "Operator tunnels, pivots, and callback utilities for owned systems."),
    "evasion": ("Evasion", "Defensive validation and stealth-behavior simulations."),
    "bluetooth": ("Bluetooth", "BLE and classic Bluetooth discovery and testing."),
    "nfc_rfid": ("NFC/RFID", "NFC and RFID reader, writer, and research workflows."),
    "sdr": ("SDR", "Software-defined radio receivers and RF analysis utilities."),
    "usb": ("USB", "USB HID, storage, and device-behavior tests."),
    "hardware": ("Hardware", "GPS, GPIO, LTE, and local hardware support tools."),
    "utilities": ("Utilities", "Maintenance, diagnostics, setup helpers, and everyday field tools."),
    "games": ("Games", "LCD-era games kept for compatibility testing and downtime."),
    "examples": ("Examples", "Payload templates and reference implementations."),
    "ai": ("AI", "Local model demos and sensor-assisted experiments."),
    "payloads": ("Payloads", "Imported or uncategorized payload scripts."),
    "general": ("General", "General-purpose payload scripts."),
}
PORTAL_SITES_DIR = Path(os.environ.get("JACKPACK_PORTAL_SITES_DIR", str(ROOT_DIR / "config" / "portal_sites")))


def _workflow_schema(rel_path: str) -> dict | None:
    if rel_path == "wifi/deauth.py":
        return {
            "type": "wifi_ap_targets",
            "title": "WiFi Deauth",
            "summary": "Scan APs, select authorized test targets, choose mode, then launch the payload.",
            "scan_label": "Scan APs",
            "target_mode": "multi",
            "requires_authorization": True,
            "fields": [
                {
                    "name": "iface",
                    "env": "JACKPACK_SELECTED_IFACE",
                    "label": "WiFi Adapter",
                    "type": "interface",
                    "iface_type": "wifi",
                    "required": True,
                    "default": _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1"),
                    "help": "External USB WiFi adapter used for scanning and payload traffic.",
                    "allow_control_iface": False,
                },
                {
                    "name": "mode",
                    "env": "JACKPACK_DEAUTH_MODE",
                    "label": "Mode",
                    "type": "select",
                    "default": "DTH",
                    "choices": ["DTH", "DTH+CAP"],
                    "help": "DTH+CAP also attempts EAPOL capture when Scapy is available.",
                },
                {
                    "name": "scan_timeout",
                    "env": "JACKPACK_DEAUTH_SCAN_TIMEOUT",
                    "label": "Scan Time",
                    "type": "number",
                    "default": "12",
                    "min": 5,
                    "max": 60,
                    "help": "Seconds to scan before showing AP results.",
                },
            ],
            "target_env": "JACKPACK_DEAUTH_TARGETS",
            "autostart_env": "JACKPACK_DEAUTH_AUTOSTART",
        }
    if rel_path == "wifi/captive_portal.py":
        return {
            "type": "captive_portal",
            "title": "Captive Portal",
            "summary": "Select a portal template, set the AP SSID, then launch the portal on the external WiFi adapter.",
            "requires_authorization": True,
            "portal_endpoint": "/api/payloads/workflow/portals",
            "fields": [
                {
                    "name": "iface",
                    "env": "JACKPACK_SELECTED_IFACE",
                    "label": "WiFi Adapter",
                    "type": "interface",
                    "iface_type": "wifi",
                    "required": True,
                    "default": _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1"),
                    "help": "External USB WiFi adapter used to host the portal AP.",
                    "allow_control_iface": False,
                },
                {
                    "name": "ssid",
                    "env": "JACKPACK_CAPTIVE_PORTAL_SSID",
                    "label": "Portal SSID",
                    "type": "text",
                    "default": "FreeWiFi",
                    "required": True,
                    "help": "Name broadcast by the portal AP.",
                },
                {
                    "name": "portal",
                    "env": "JACKPACK_CAPTIVE_PORTAL_TEMPLATE",
                    "label": "Portal Template",
                    "type": "portal_select",
                    "default": "",
                    "help": "Use Built-in or a template from config/portal_sites.",
                },
                {
                    "name": "whitelist",
                    "env": "JACKPACK_CAPTIVE_PORTAL_WHITELIST",
                    "label": "Allowed MACs",
                    "type": "textarea",
                    "default": "",
                    "rows": 3,
                    "help": "Optional comma or newline separated MAC addresses that should bypass the portal.",
                },
            ],
            "autostart_env": "JACKPACK_CAPTIVE_PORTAL_AUTOSTART",
        }
    return None


def _native_payload_rel_paths() -> list[str]:
    paths: list[str] = []
    if NATIVE_PAYLOADS_DIR.exists():
        for path in sorted(NATIVE_PAYLOADS_DIR.glob("*.py"), key=lambda p: p.name.lower()):
            if path.name.startswith("_"):
                continue
            try:
                paths.append(str(path.relative_to(PAYLOADS_DIR)).replace("\\", "/"))
            except Exception:
                continue
    return paths


def _slugify_payload_name(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", str(value or "").strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:48] or "new_payload"


def _load_shared_token() -> str | None:
    """Load auth token from env first, then token file."""
    env_token = str(os.environ.get("RJ_WS_TOKEN", "")).strip()
    if env_token:
        return env_token
    try:
        if TOKEN_FILE.exists():
            for line in TOKEN_FILE.read_text(encoding="utf-8").splitlines():
                value = line.strip()
                if value and not value.startswith("#"):
                    return value
    except Exception:
        pass
    return None


def _load_line_secret(path: Path) -> str | None:
    try:
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value and not value.startswith("#"):
                return value
    except Exception:
        pass
    return None


def _load_or_create_auth_secret() -> str:
    existing = _load_line_secret(AUTH_SECRET_FILE)
    if existing:
        return existing
    generated = secrets.token_urlsafe(48)
    try:
        AUTH_SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
        AUTH_SECRET_FILE.write_text(generated + "\n", encoding="utf-8")
        os.chmod(AUTH_SECRET_FILE, 0o600)
    except Exception:
        # Fallback for environments where file creation is not possible.
        pass
    return generated

HOST = os.environ.get("RJ_WEB_HOST", "0.0.0.0")
PORT = int(os.environ.get("RJ_WEB_PORT", "8080"))
TOKEN = _load_shared_token()
AUTH_SECRET = _load_or_create_auth_secret()
HEADLESS_MODE = os.environ.get("RJ_HEADLESS", "0") == "1"

# WebUI only listens on the Pi 5 wired port, control AP, and tunnels by default.
# The payload WiFi interface stays free for monitor/client work.
_env_webui_ifaces = os.environ.get("RJ_WEBUI_INTERFACES", "").strip()
if _env_webui_ifaces:
    WEBUI_INTERFACES = [i.strip() for i in _env_webui_ifaces.split(",") if i.strip()]
else:
    _wired = jp_ifaces.wired_iface() if jp_ifaces is not None else "eth0"
    _ap = jp_ifaces.ap_iface() if jp_ifaces is not None else "wlan0"
    WEBUI_INTERFACES = [_wired, _ap, "tailscale0"]


def _get_interface_ip(interface: str) -> str | None:
    """Get the IPv4 address of a network interface."""
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show", interface],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "inet " in line:
                    return line.split("inet ")[1].split("/")[0]
    except Exception:
        pass
    return None


def _get_webui_bind_addrs() -> list[tuple[str, str]]:
    """Return (ip, iface_label) pairs the WebUI should bind to."""
    addrs: list[tuple[str, str]] = []
    for iface in WEBUI_INTERFACES:
        ip = _get_interface_ip(iface)
        if ip:
            addrs.append((ip, iface))
    # Always include localhost for local access
    addrs.append(("127.0.0.1", "lo"))
    return addrs
PREVIEW_MAX_BYTES = int(os.environ.get("RJ_LOOT_PREVIEW_MAX", str(200 * 1024)))
TEXT_EXTS = {
    ".txt", ".log", ".md", ".json", ".csv", ".conf", ".ini", ".yaml", ".yml",
    ".pcapng.txt", ".xml", ".sqlite", ".db", ".out", ".py", ".sh"
}

_CPU_SNAPSHOT = None
_LOGIN_FAILS: dict[str, list[float]] = {}


def _is_valid_discord_webhook(url: str) -> bool:
    return url.startswith("https://discord.com/api/webhooks/")


def _read_discord_webhook_url() -> str:
    """Read the configured Discord webhook URL from file."""
    try:
        if not DISCORD_WEBHOOK_PATH.exists():
            return ""
        for line in DISCORD_WEBHOOK_PATH.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            if _is_valid_discord_webhook(value):
                return value
        return ""
    except Exception:
        return ""


def _write_discord_webhook_url(url: str) -> tuple[bool, str]:
    """Write or clear Discord webhook URL in file."""
    value = str(url or "").strip()
    try:
        if not value:
            if DISCORD_WEBHOOK_PATH.exists():
                DISCORD_WEBHOOK_PATH.unlink()
            return True, "cleared"
        if not _is_valid_discord_webhook(value):
            return False, "invalid webhook url"
        DISCORD_WEBHOOK_PATH.write_text(value + "\n", encoding="utf-8")
        return True, "saved"
    except Exception as exc:
        return False, f"write error: {exc}"


def _read_wigle_credentials() -> dict[str, str]:
    try:
        if not WIGLE_CREDENTIALS_PATH.exists():
            return {"api_name": "", "api_token": ""}
        raw = WIGLE_CREDENTIALS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw) if raw else {}
        if not isinstance(data, dict):
            return {"api_name": "", "api_token": ""}
        return {
            "api_name": str(data.get("api_name") or "").strip(),
            "api_token": str(data.get("api_token") or "").strip(),
        }
    except Exception:
        return {"api_name": "", "api_token": ""}


def _write_wigle_credentials(api_name: str, api_token: str) -> tuple[bool, str]:
    clean_name = str(api_name or "").strip()
    clean_token = str(api_token or "").strip()
    try:
        if not clean_name and not clean_token:
            if WIGLE_CREDENTIALS_PATH.exists():
                WIGLE_CREDENTIALS_PATH.unlink()
            return True, "cleared"
        if not clean_name or not clean_token:
            return False, "api name and api token are required"
        WIGLE_CREDENTIALS_PATH.write_text(
            json.dumps({"api_name": clean_name, "api_token": clean_token}) + "\n",
            encoding="utf-8",
        )
        try:
            os.chmod(WIGLE_CREDENTIALS_PATH, 0o600)
        except Exception:
            pass
        return True, "saved"
    except Exception as exc:
        return False, f"write error: {exc}"


def _mask_secret(value: str, keep_start: int = 3, keep_end: int = 2) -> str:
    secret = str(value or "")
    if not secret:
        return ""
    if len(secret) <= (keep_start + keep_end):
        return "*" * len(secret)
    return secret[:keep_start] + ("*" * (len(secret) - keep_start - keep_end)) + secret[-keep_end:]


def _tailscale_write_status(payload: dict) -> None:
    """Persist last Tailscale install/bootstrap status for the WebUI."""
    try:
        TAILSCALE_STATUS_PATH.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        pass


def _tailscale_read_status() -> dict:
    try:
        if not TAILSCALE_STATUS_PATH.exists():
            return {}
        raw = TAILSCALE_STATUS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw) if raw else {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _tailscale_installed() -> bool:
    """Return True if the tailscale CLI appears to be installed."""
    try:
        return _which("tailscale") is not None
    except Exception:
        return False


def _tailscale_status() -> dict:
    """
    Best-effort snapshot of the Tailscale daemon.
    Returns {"backend_state": str|None, "ip": str|None}.
    """
    summary: dict[str, str | None] = {"backend_state": None, "ip": None}
    if not _tailscale_installed():
        return summary
    try:
        res = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode != 0 or not res.stdout:
            return summary
        data = json.loads(res.stdout)
        if not isinstance(data, dict):
            return summary
        summary["backend_state"] = str(data.get("BackendState") or "") or None
        self_info = data.get("Self") or {}
        if isinstance(self_info, dict):
            ips = self_info.get("TailscaleIPs") or []
            if isinstance(ips, list) and ips:
                summary["ip"] = str(ips[0])
    except Exception:
        pass
    return summary


def _tailscale_write_key(key: str) -> tuple[bool, str]:
    """Store the auth key in a root-only file so tailscale can read it."""
    value = str(key or "").strip()
    if not value:
        return False, "missing auth key"
    try:
        TAILSCALE_KEY_PATH.write_text(value + "\n", encoding="utf-8")
        try:
            os.chmod(TAILSCALE_KEY_PATH, 0o600)
        except Exception:
            # On some platforms chmod may fail; do not treat as fatal.
            pass
        return True, "ok"
    except Exception as exc:
        return False, f"write error: {exc}"


def _tailscale_run_install_and_up() -> None:
    """
    Run the official install script and bring Tailscale up using the stored auth key.
    This is executed in a background thread so HTTP handlers can return quickly.
    """
    _tailscale_write_status({"installing": True, "ok": False, "error": None})

    try:
        if not TAILSCALE_KEY_PATH.exists():
            _tailscale_write_status({
                "installing": False,
                "ok": False,
                "error": "auth key not found",
            })
            return
    except Exception:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": "auth key not found",
        })
        return

    # 1) Install Tailscale using the official script.
    try:
        install_res = subprocess.run(
            ["sh", "-c", "curl -fsSL https://tailscale.com/install.sh | sh"],
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": "tailscale install timeout",
        })
        return
    except Exception as exc:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": str(exc),
        })
        return

    if install_res.returncode != 0:
        msg = (install_res.stderr or install_res.stdout or "").strip()
        if not msg:
            msg = f"tailscale install failed (code {install_res.returncode})"
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": msg[:200],
        })
        return

    # 2) Bring the daemon up using the stored auth key (non-interactive).
    try:
        auth_arg = f"--auth-key=file:{TAILSCALE_KEY_PATH}"
        up_res = subprocess.run(
            ["tailscale", "up", auth_arg, "--ssh"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": "tailscale up timeout",
        })
        return
    except Exception as exc:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": str(exc),
        })
        return

    if up_res.returncode != 0:
        msg = (up_res.stderr or up_res.stdout or "").strip()
        if not msg:
            msg = f"tailscale up failed (code {up_res.returncode})"
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": msg[:200],
        })
        return

    _tailscale_write_status({
        "installing": False,
        "ok": True,
        "error": None,
    })


def _tailscale_run_reauth() -> None:
    """
    Re-authenticate an existing Tailscale install using the stored auth key.
    Does not re-run the install script, only `tailscale up --reset --auth-key=... --ssh`.
    """
    _tailscale_write_status({"installing": True, "ok": False, "error": None})

    try:
        if not TAILSCALE_KEY_PATH.exists():
            _tailscale_write_status({
                "installing": False,
                "ok": False,
                "error": "auth key not found",
            })
            return
    except Exception:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": "auth key not found",
        })
        return

    try:
        auth_arg = f"--auth-key=file:{TAILSCALE_KEY_PATH}"
        up_res = subprocess.run(
            ["tailscale", "up", "--reset", auth_arg, "--ssh"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": "tailscale up timeout",
        })
        return
    except Exception as exc:
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": str(exc),
        })
        return

    if up_res.returncode != 0:
        msg = (up_res.stderr or up_res.stdout or "").strip()
        if not msg:
            msg = f"tailscale up failed (code {up_res.returncode})"
        _tailscale_write_status({
            "installing": False,
            "ok": False,
            "error": msg[:200],
        })
        return

    _tailscale_write_status({
        "installing": False,
        "ok": True,
        "error": None,
    })


def _read_cpu_percent() -> float:
    """Best-effort CPU usage based on /proc/stat delta."""
    global _CPU_SNAPSHOT
    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            line = f.readline().strip()
        if not line.startswith("cpu "):
            return 0.0
        parts = [int(x) for x in line.split()[1:]]
        idle = parts[3] + (parts[4] if len(parts) > 4 else 0)
        total = sum(parts)
        if _CPU_SNAPSHOT is None:
            _CPU_SNAPSHOT = (idle, total)
            return 0.0
        prev_idle, prev_total = _CPU_SNAPSHOT
        _CPU_SNAPSHOT = (idle, total)
        idle_delta = idle - prev_idle
        total_delta = total - prev_total
        if total_delta <= 0:
            return 0.0
        pct = 100.0 * (1.0 - (idle_delta / total_delta))
        return max(0.0, min(100.0, pct))
    except Exception:
        return 0.0


def _read_meminfo() -> tuple[int, int]:
    """Return used_bytes, total_bytes from /proc/meminfo."""
    try:
        vals = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                key, rest = line.split(":", 1)
                vals[key.strip()] = int(rest.strip().split()[0]) * 1024
        total = int(vals.get("MemTotal", 0))
        available = int(vals.get("MemAvailable", vals.get("MemFree", 0)))
        used = max(0, total - available)
        return used, total
    except Exception:
        return 0, 0


def _read_temp_c() -> float | None:
    try:
        raw = Path("/sys/class/thermal/thermal_zone0/temp").read_text(encoding="utf-8").strip()
        val = float(raw)
        return val / 1000.0 if val > 1000 else val
    except Exception:
        return None


def _read_uptime_seconds() -> int:
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            return int(float(f.read().split()[0]))
    except Exception:
        return 0


def _read_ipv4_interfaces() -> list[dict]:
    out = []
    try:
        res = subprocess.run(
            ["ip", "-o", "-4", "addr", "show", "up"],
            capture_output=True, text=True, timeout=3,
        )
        if res.returncode != 0:
            return out
        for line in res.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface = parts[1]
            if iface == "lo":
                continue
            try:
                inet_idx = parts.index("inet")
                addr = parts[inet_idx + 1].split("/")[0]
            except Exception:
                addr = "-"
            out.append({"name": iface, "ipv4": addr, "up": True})
    except Exception:
        pass
    return out


def _env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = str(os.environ.get(name, "")).strip()
        if value:
            return value
    return default


def _iface_role(name: str) -> str:
    if jp_ifaces is not None:
        return jp_ifaces.interface_role(name)
    ap_iface = _env_first("JACKPACK_AP_IFACE", "PACKJACK_AP_IFACE", default="wlan0")
    attack_iface = _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1")
    wired_iface = _env_first("JACKPACK_WIRED_IFACE", "PACKJACK_WIRED_IFACE", default="eth0")
    if name == ap_iface:
        return "control_ap"
    if name == attack_iface:
        return "attack_wifi"
    if name == wired_iface:
        return "wired_target"
    if name.startswith("tailscale"):
        return "tunnel"
    return "network"


def _valid_iface_name(value: str) -> bool:
    return bool(_IFACE_RE.match(str(value or "")))


def _configured_iface_names(include_missing: bool = True) -> list[str]:
    names: list[str] = []
    for value in (
        _env_first("JACKPACK_AP_IFACE", "PACKJACK_AP_IFACE", default="wlan0"),
        _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1"),
        _env_first("JACKPACK_WIRED_IFACE", "PACKJACK_WIRED_IFACE", default="eth0"),
    ):
        if value and value not in names:
            names.append(value)
    try:
        for item in sorted(Path("/sys/class/net").iterdir()):
            name = item.name
            if name == "lo" or name in names:
                continue
            if include_missing or item.exists():
                names.append(name)
    except Exception:
        pass
    return names


def _is_wireless_iface(iface: str) -> bool:
    try:
        return Path(f"/sys/class/net/{iface}/wireless").is_dir()
    except Exception:
        return False


def _nmcli_split(line: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in line:
        if escaped:
            buf.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ":":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(char)
    parts.append("".join(buf))
    return parts


def _run_command(args: list[str], timeout: int = 15) -> tuple[int, str, str]:
    try:
        res = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT_DIR),
        )
        return res.returncode, res.stdout or "", res.stderr or ""
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "command timed out"
    except Exception as exc:
        return 1, "", str(exc)


def _which(cmd: str) -> str | None:
    path = shutil.which(cmd)
    if path:
        return path
    for base in ("/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin"):
        candidate = Path(base) / cmd
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _nmcli_status_by_iface() -> dict[str, dict]:
    if _which("nmcli") is None:
        return {}
    code, stdout, _ = _run_command(
        ["nmcli", "-t", "-e", "yes", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
        timeout=8,
    )
    if code != 0:
        return {}
    status: dict[str, dict] = {}
    for line in stdout.splitlines():
        parts = _nmcli_split(line)
        if len(parts) < 4:
            continue
        iface, kind, state, connection = parts[:4]
        if iface:
            status[iface] = {
                "type": kind,
                "state": state,
                "connection": connection,
            }
    return status


def _network_status() -> dict:
    nm = _nmcli_status_by_iface()
    ipv4 = {item.get("name"): item.get("ipv4") for item in _read_ipv4_interfaces()}
    headless = _read_headless_status()
    ap_iface = str((headless.get("ap") or {}).get("iface") or "wlan0")
    attack_iface = str((headless.get("attack") or {}).get("iface") or "wlan1")
    interfaces = []
    for name in _configured_iface_names(include_missing=True):
        if not _valid_iface_name(name):
            continue
        role = _iface_role(name)
        present = Path(f"/sys/class/net/{name}").exists()
        info = nm.get(name, {})
        interfaces.append({
            "name": name,
            "role": role,
            "present": present,
            "wireless": _is_wireless_iface(name),
            "protected": name == ap_iface,
            "recommended": name == attack_iface,
            "ipv4": ipv4.get(name) or None,
            "state": info.get("state") or ("unavailable" if not present else "unknown"),
            "connection": info.get("connection") or "",
            "type": info.get("type") or ("wifi" if _is_wireless_iface(name) or role in {"control_ap", "attack_wifi", "wifi"} else "ethernet"),
        })
    return {
        "ok": True,
        "nmcli": _which("nmcli") is not None,
        "ap_iface": ap_iface,
        "attack_iface": attack_iface,
        "interfaces": interfaces,
    }


def _wifi_scan(iface: str) -> tuple[bool, dict]:
    if not _valid_iface_name(iface):
        return False, {"error": "invalid interface"}
    if _which("nmcli") is None:
        return False, {"error": "nmcli is not installed"}
    if not Path(f"/sys/class/net/{iface}").exists():
        return False, {"error": f"{iface} is not present"}
    if not _is_wireless_iface(iface):
        return False, {"error": f"{iface} is not a WiFi interface"}
    code, stdout, stderr = _run_command(
        [
            "nmcli",
            "-t",
            "-e",
            "yes",
            "-f",
            "SSID,SECURITY,SIGNAL,CHAN,BSSID",
            "device",
            "wifi",
            "list",
            "ifname",
            iface,
            "--rescan",
            "yes",
        ],
        timeout=20,
    )
    if code != 0:
        return False, {"error": (stderr or stdout or "scan failed").strip()}
    seen: set[str] = set()
    networks = []
    for line in stdout.splitlines():
        parts = _nmcli_split(line)
        if len(parts) < 5:
            continue
        ssid, security, signal, channel, bssid = parts[:5]
        key = bssid or f"{ssid}:{security}:{channel}"
        if key in seen:
            continue
        seen.add(key)
        security = security.strip()
        networks.append({
            "ssid": ssid,
            "security": security,
            "open": not security or security == "--",
            "signal": int(signal) if str(signal).isdigit() else None,
            "channel": channel,
            "bssid": bssid,
        })
    networks.sort(key=lambda item: (item.get("signal") is None, -(item.get("signal") or 0), item.get("ssid") or ""))
    return True, {"ok": True, "iface": iface, "networks": networks}


def _wifi_profile_name(iface: str, ssid: str) -> str:
    safe_ssid = re.sub(r"[^A-Za-z0-9_.-]+", "-", ssid).strip("-")[:28] or "network"
    return f"jackpack-uplink-{iface}-{safe_ssid}"


def _security_key_mgmt(security: str, password: str) -> str:
    text = str(security or "").upper()
    if not password:
        return ""
    if ("SAE" in text or "WPA3" in text) and "WPA2" not in text and "WPA" not in text.replace("WPA3", ""):
        return "sae"
    if "WEP" in text:
        return "none"
    return "wpa-psk"


def _connect_wifi(
    iface: str,
    ssid: str,
    password: str,
    hidden: bool,
    force_control_iface: bool,
    security: str = "",
    bssid: str = "",
) -> tuple[bool, dict]:
    if not _valid_iface_name(iface):
        return False, {"error": "invalid interface"}
    ssid = str(ssid or "").strip()
    if not ssid:
        return False, {"error": "ssid is required"}
    if len(ssid.encode("utf-8", "ignore")) > 128:
        return False, {"error": "ssid is too long"}
    status = _network_status()
    ap_iface = status.get("ap_iface")
    if iface == ap_iface and not force_control_iface:
        return False, {
            "error": "Refusing to change the control AP from the WebUI. Use the external adapter, or enable the force option if you are physically near the Pi.",
            "control_iface": True,
        }
    if _which("nmcli") is None:
        return False, {"error": "nmcli is not installed"}
    profile = _wifi_profile_name(iface, ssid)
    _run_command(["nmcli", "connection", "delete", profile], timeout=10)
    code, stdout, stderr = _run_command(
        [
            "nmcli",
            "connection",
            "add",
            "type",
            "wifi",
            "ifname",
            iface,
            "con-name",
            profile,
            "ssid",
            ssid,
        ],
        timeout=15,
    )
    if code != 0:
        return False, {"error": (stderr or stdout or "profile creation failed").strip()}

    modify_args = [
        "nmcli",
        "connection",
        "modify",
        profile,
        "connection.interface-name",
        iface,
        "connection.autoconnect",
        "yes",
        "802-11-wireless.mode",
        "infrastructure",
        "802-11-wireless.ssid",
        ssid,
        "ipv4.method",
        "auto",
        "ipv6.method",
        "ignore",
    ]
    if hidden:
        modify_args.extend(["802-11-wireless.hidden", "yes"])
    if bssid and _MAC_RE.match(bssid):
        modify_args.extend(["802-11-wireless.bssid", bssid])
    key_mgmt = _security_key_mgmt(security, password)
    if key_mgmt:
        modify_args.extend(["802-11-wireless-security.key-mgmt", key_mgmt])
        if key_mgmt == "none":
            modify_args.extend(["802-11-wireless-security.wep-key0", password])
        else:
            modify_args.extend(["802-11-wireless-security.psk", password])

    code, stdout, stderr = _run_command(modify_args, timeout=15)
    if code != 0:
        return False, {"error": (stderr or stdout or "profile configuration failed").strip()}

    code, stdout, stderr = _run_command(["nmcli", "connection", "up", profile, "ifname", iface], timeout=35)
    if code != 0:
        return False, {"error": (stderr or stdout or "connect failed").strip()}
    return True, {"ok": True, "message": stdout.strip(), "profile": profile, "status": _network_status()}


def _disconnect_iface(iface: str, force_control_iface: bool) -> tuple[bool, dict]:
    if not _valid_iface_name(iface):
        return False, {"error": "invalid interface"}
    status = _network_status()
    ap_iface = status.get("ap_iface")
    if iface == ap_iface and not force_control_iface:
        return False, {
            "error": "Refusing to disconnect the control AP from the WebUI.",
            "control_iface": True,
        }
    if _which("nmcli") is None:
        return False, {"error": "nmcli is not installed"}
    code, stdout, stderr = _run_command(["nmcli", "device", "disconnect", iface], timeout=15)
    if code != 0:
        return False, {"error": (stderr or stdout or "disconnect failed").strip()}
    return True, {"ok": True, "message": stdout.strip(), "status": _network_status()}


def _read_headless_status() -> dict:
    interfaces = _read_ipv4_interfaces()
    for iface in interfaces:
        iface["role"] = _iface_role(str(iface.get("name") or ""))

    payload_status = {"running": False, "path": None, "mode": "headless" if HEADLESS_MODE else "classic"}
    if HEADLESS_MODE and payload_runner is not None:
        try:
            payload_status = payload_runner.status()
        except Exception:
            pass
    elif PAYLOAD_STATE_PATH.exists():
        try:
            raw = PAYLOAD_STATE_PATH.read_text(encoding="utf-8")
            payload_status = json.loads(raw) if raw else payload_status
        except Exception:
            pass

    ap_iface = _env_first("JACKPACK_AP_IFACE", "PACKJACK_AP_IFACE", default="wlan0")
    attack_iface = _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1")
    wired_iface = _env_first("JACKPACK_WIRED_IFACE", "PACKJACK_WIRED_IFACE", default="eth0")
    ap_ssid = _env_first("JACKPACK_AP_SSID", "PACKJACK_AP_SSID", default="JackPack")
    ap_address = _env_first("JACKPACK_AP_ADDRESS", "PACKJACK_AP_ADDRESS", default="10.66.0.1/24")
    hostname = _env_first("JACKPACK_HOSTNAME", "PACKJACK_HOSTNAME", default="jackpack")
    fallback_host = ap_address.split("/", 1)[0]

    return {
        "name": "JackPack",
        "headless": HEADLESS_MODE,
        "web": {
            "hostname": f"{hostname}.local",
            "url": f"http://{hostname}.local:{PORT}",
            "fallback_url": f"http://{fallback_host}:{PORT}",
        },
        "ap": {
            "iface": ap_iface,
            "ssid": ap_ssid,
            "address": ap_address,
            "present": any(i.get("name") == ap_iface for i in interfaces),
        },
        "attack": {
            "iface": attack_iface,
            "present": any(i.get("name") == attack_iface for i in interfaces),
        },
        "wired": {
            "iface": wired_iface,
            "present": any(i.get("name") == wired_iface for i in interfaces),
        },
        "interfaces": interfaces,
        "payload": payload_status,
    }


def _payload_meta(path: Path) -> dict:
    meta = {
        "headless": "unknown",
        "needs_display": False,
        "uses_wifi": False,
        "uses_external_wifi": False,
        "tags": [],
        "description": "",
    }
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return meta

    try:
        tree = ast.parse(text)
        doc = ast.get_docstring(tree) or ""
        first = next((line.strip() for line in doc.splitlines() if line.strip()), "")
        meta["description"] = first[:180]
    except Exception:
        pass

    display_markers = ("LCD_", "LCD.", "ImageDraw", "ScaledDraw", "_display_helper")
    input_markers = ("get_button", "KEY3", "KEY_PRESS", "_input_helper")
    wifi_markers = ("wlan", "airmon", "airodump", "aireplay", "iw ", "iwconfig", "hostapd")
    external_wifi_markers = ("wlan1", "PACKJACK_ATTACK_IFACE", "JACKPACK_ATTACK_IFACE", "get_best_interface")

    meta["needs_display"] = any(marker in text for marker in display_markers)
    meta["uses_input"] = any(marker in text for marker in input_markers)
    meta["uses_wifi"] = any(marker in text for marker in wifi_markers)
    meta["uses_external_wifi"] = any(marker in text for marker in external_wifi_markers)
    if "RJ_HEADLESS" in text or "headless" in text.lower():
        meta["headless"] = "aware"
    elif meta["needs_display"] or meta["uses_input"]:
        meta["headless"] = "compat"
    else:
        meta["headless"] = "native"

    if meta["headless"] == "native":
        meta["tags"].append("native")
    elif meta["headless"] == "aware":
        meta["tags"].append("headless-aware")
    else:
        meta["tags"].append("compat")
    if meta["uses_wifi"]:
        meta["tags"].append("wifi")
    if meta["uses_external_wifi"]:
        meta["tags"].append("wlan1")
    if meta["needs_display"]:
        meta["tags"].append("lcd-compat")
    return meta


def _ast_literal(value) -> object | None:
    try:
        return ast.literal_eval(value)
    except Exception:
        return None


def _ast_eval_static(node, env: dict[str, object] | None = None) -> object | None:
    env = env or {}
    literal = _ast_literal(node)
    if literal is not None:
        return literal
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.Dict):
        keys = [_ast_eval_static(key, env) for key in node.keys]
        values = [_ast_eval_static(value, env) for value in node.values]
        if all(key is not None for key in keys):
            return dict(zip(keys, values))
        return None
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        items = [_ast_eval_static(item, env) for item in node.elts]
        if any(item is None for item in items):
            return None
        if isinstance(node, ast.Tuple):
            return tuple(items)
        if isinstance(node, ast.Set):
            return set(items)
        return items
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in {"list", "tuple", "set", "sorted"} and len(node.args) == 1:
            value = _ast_eval_static(node.args[0], env)
            if value is None:
                return None
            try:
                if node.func.id == "list":
                    return list(value)
                if node.func.id == "tuple":
                    return tuple(value)
                if node.func.id == "set":
                    return set(value)
                return sorted(value)
            except Exception:
                return None
        if isinstance(node.func, ast.Attribute) and node.func.attr == "keys" and not node.args:
            value = _ast_eval_static(node.func.value, env)
            if isinstance(value, dict):
                return list(value.keys())
    return None


def _module_literal_env(tree: ast.AST) -> dict[str, object]:
    env: dict[str, object] = {}
    if not isinstance(tree, ast.Module):
        return env
    for node in tree.body:
        if isinstance(node, ast.Assign):
            value = _ast_eval_static(node.value, env)
            if value is None:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    env[target.id] = value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id.isupper():
            value = _ast_eval_static(node.value, env)
            if value is not None:
                env[node.target.id] = value
    return env

_ACTION_BUTTONS = {"UP", "DOWN", "LEFT", "RIGHT", "OK", "KEY1", "KEY2", "KEY3"}
_ACTION_ALIASES = {"DN": "DOWN", "K1": "KEY1", "K2": "KEY2", "K3": "KEY3"}


def _normalize_action(item: object) -> dict | None:
    if isinstance(item, str):
        button = item.strip().upper()
        if button in _ACTION_BUTTONS:
            return {"button": button, "label": button, "description": "", "group": "actions"}
        return None
    if not isinstance(item, dict):
        return None
    button = str(item.get("button") or item.get("key") or "").strip().upper()
    if button not in _ACTION_BUTTONS:
        return None
    label = str(item.get("label") or item.get("name") or button).strip()[:36]
    description = str(item.get("description") or item.get("help") or "").strip()[:120]
    group = str(item.get("group") or ("navigation" if button in {"UP", "DOWN", "LEFT", "RIGHT", "OK"} else "actions")).strip()
    return {"button": button, "label": label, "description": description, "group": group}


def _actions_from_controls_text(source: str) -> list[dict]:
    actions: list[dict] = []
    seen: set[str] = set()

    def add(button: str, description: str) -> None:
        button = _ACTION_ALIASES.get(button.upper(), button.upper())
        if button not in _ACTION_BUTTONS or button in seen:
            return
        clean = re.sub(r"\s+", " ", description.strip().strip(".")).strip()
        if not clean:
            return
        seen.add(button)
        label = clean.split(";", 1)[0].split(",", 1)[0].strip()[:28] or button
        actions.append({
            "button": button,
            "label": label,
            "description": clean[:120],
            "group": "navigation" if button in {"UP", "DOWN", "LEFT", "RIGHT", "OK"} else "actions",
        })

    for raw in source.splitlines():
        line = raw.strip().strip("#").strip()
        match = re.match(r"^(UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123])(?:\s*/\s*(UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123]))?\s*(?:[-:=]+|--|—)\s*(.+)$", line, re.I)
        if match:
            description = match.group(3)
            has_more_actions = re.search(
                r"\b(UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123])\b\s*(?::|=|--|—|\s{2,})",
                description,
                re.I,
            )
            if not has_more_actions:
                buttons = [match.group(1).upper()]
                if match.group(2):
                    buttons.append(match.group(2).upper())
                for button in buttons:
                    add(button, description)
                continue

        # Catch compact docs and embedded LCD labels, e.g.
        # "Controls: OK=start, KEY1=toggle mode" or "KEY1  Scan subnet".
        compact = line
        if "controls:" in compact.lower():
            compact = compact.split(":", 1)[1]
        for match in re.finditer(
            r"\b(UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123])\b"
            r"(?:\s*/\s*(UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123]))?"
            r"\s*(?::|=|--|—|\s{2,})\s*"
            r"([^\"'`,;|]{2,70}?)(?=\s+\b(?:UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123])\b(?:\s*/\s*(?:UP|DOWN|DN|LEFT|RIGHT|OK|KEY[123]|K[123]))?\s*(?::|=|--|—|\s{2,})|[,;|]|$)",
            compact,
            re.I,
        ):
            desc = match.group(3)
            add(match.group(1), desc)
            if match.group(2):
                add(match.group(2), desc)
    return actions


def _payload_actions(tree: ast.AST, literal_env: dict[str, object], source: str) -> list[dict]:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "JACKPACK_ACTIONS" for t in targets):
                value = _ast_eval_static(node.value, literal_env)
                if isinstance(value, (list, tuple)):
                    normalized = [action for action in (_normalize_action(item) for item in value) if action]
                    if normalized:
                        return normalized
    inferred = _actions_from_controls_text(source)
    if inferred:
        return inferred
    return []


def _infer_headless_fields(tree: ast.AST, meta: dict) -> list[dict]:
    fields: list[dict] = []
    has_selected_iface = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "select_interface"):
            continue
        iface_type = "any"
        require_monitor = False
        for keyword in node.keywords:
            value = _ast_eval_static(keyword.value, {})
            if keyword.arg == "iface_type" and isinstance(value, str):
                iface_type = value
            elif keyword.arg == "require_monitor":
                require_monitor = bool(value)
        if len(node.args) >= 5:
            value = _ast_eval_static(node.args[4], {})
            if isinstance(value, str):
                iface_type = value
        if not has_selected_iface:
            default = _env_first(
                "JACKPACK_ATTACK_IFACE",
                "PACKJACK_ATTACK_IFACE",
                default="wlan1",
            )
            if iface_type in {"eth", "wired"}:
                default = _env_first("JACKPACK_WIRED_IFACE", "PACKJACK_WIRED_IFACE", default="eth0")
            fields.append({
                "name": "selected_iface",
                "env": "JACKPACK_SELECTED_IFACE",
                "label": "Payload Interface",
                "type": "interface",
                "required": True,
                "default": default,
                "help": "Used by JackPack's headless interface picker.",
                "iface_type": iface_type,
                "require_monitor": require_monitor,
            })
            has_selected_iface = True
    if meta.get("uses_wifi") and not has_selected_iface:
        fields.append({
            "name": "attack_iface",
            "env": "JACKPACK_ATTACK_IFACE",
            "label": "Attack WiFi",
            "type": "interface",
            "required": False,
            "default": _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1"),
            "help": "External USB WiFi used by WiFi payloads.",
            "iface_type": "wifi",
        })
    return fields


def _payload_form_schema(path: Path) -> dict:
    meta = _payload_meta(path)
    schema = {
        "mode": "args",
        "fields": [],
        "actions": [],
        "raw_args": True,
        "meta": meta,
    }
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except Exception:
        return schema
    literal_env = _module_literal_env(tree)
    schema["actions"] = _payload_actions(tree, literal_env, source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "JACKPACK_FORM" for t in targets):
                value = _ast_eval_static(node.value, literal_env)
                if isinstance(value, dict):
                    form_meta = value.get("meta") if isinstance(value.get("meta"), dict) else {}
                    merged_meta = {**meta, **form_meta}
                    value.setdefault("raw_args", True)
                    value["meta"] = merged_meta
                    value.setdefault("actions", schema["actions"])
                    value.setdefault("requirements", {})
                    return value

    fields: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "add_argument"):
            continue
        option_strings = [
            arg.value for arg in node.args
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
        ]
        if not option_strings:
            continue
        long_option = next((item for item in option_strings if item.startswith("--")), option_strings[0])
        dest = long_option.lstrip("-").replace("-", "_")
        field = {
            "name": dest,
            "arg": long_option,
            "label": dest.replace("_", " ").title(),
            "type": "text",
            "required": False,
            "default": "",
            "help": "",
        }
        for keyword in node.keywords:
            key = keyword.arg
            if not key:
                continue
            value = _ast_eval_static(keyword.value, literal_env)
            if key == "dest" and isinstance(value, str) and value:
                field["name"] = value
                field["label"] = value.replace("_", " ").title()
            elif key == "required":
                field["required"] = bool(value)
            elif key == "default" and value is not None:
                field["default"] = str(value)
            elif key == "help" and isinstance(value, str):
                field["help"] = value
            elif key == "choices" and isinstance(value, (list, tuple)):
                field["type"] = "select"
                field["choices"] = [str(item) for item in value]
            elif key == "action" and value in {"store_true", "store_false"}:
                field["type"] = "checkbox"
                field["checked_value"] = value
                field["default"] = value == "store_false"
            elif key == "type":
                text = ""
                if isinstance(keyword.value, ast.Name):
                    text = keyword.value.id
                elif isinstance(value, str):
                    text = value
                if text in {"int", "float"}:
                    field["type"] = "number"
        lower_name = str(field.get("name") or "").lower()
        lower_arg = str(field.get("arg") or "").lower()
        if any(token in lower_name or token in lower_arg for token in ("iface", "interface")):
            field["type"] = "interface"
            if not field.get("default"):
                field["default"] = _env_first(
                    "JACKPACK_ATTACK_IFACE",
                    "PACKJACK_ATTACK_IFACE",
                    default="wlan1" if meta.get("uses_wifi") else "eth0",
                )
        if lower_name in {"port", "lport", "rport"} or lower_name.endswith("_port"):
            field["type"] = "number"
        fields.append(field)

    for inferred in _infer_headless_fields(tree, meta):
        key = inferred.get("env") or inferred.get("arg") or inferred.get("name")
        if key and not any((field.get("env") or field.get("arg") or field.get("name")) == key for field in fields):
            fields.insert(0, inferred)

    if fields:
        schema.update({
            "mode": "form",
            "fields": fields,
            "raw_args": True,
        })
    return schema


def _runtime_env_path() -> Path:
    if PACKJACK_ENV_PATH.exists() or os.geteuid() == 0:
        return PACKJACK_ENV_PATH
    return PACKJACK_ENV_FALLBACK_PATH


def _read_env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        if not path.exists():
            return values
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key:
                values[key] = value.strip().strip('"').strip("'")
    except Exception:
        pass
    return values


def _runtime_config_payload() -> dict:
    path = _runtime_env_path()
    file_values = _read_env_values(path)
    defaults = {
        "JACKPACK_AP_IFACE": "wlan0",
        "JACKPACK_AP_SSID": "JackPack",
        "JACKPACK_AP_PASSWORD": "",
        "JACKPACK_AP_ADDRESS": "10.66.0.1/24",
        "JACKPACK_AP_CHANNEL": "6",
        "JACKPACK_ATTACK_IFACE": "wlan1",
        "JACKPACK_WIRED_IFACE": "eth0",
        "JACKPACK_HOSTNAME": "jackpack",
        "RJ_WEB_PORT": str(PORT),
        "RJ_WS_PORT": os.environ.get("RJ_WS_PORT", "8765"),
    }
    values = {}
    for key in sorted(_ALLOWED_RUNTIME_CONFIG):
        value = file_values.get(key, os.environ.get(key, defaults.get(key, "")))
        values[key] = str(value)
    masked = {
        key: (_mask_secret(value) if key in _SENSITIVE_RUNTIME_CONFIG else value)
        for key, value in values.items()
    }
    return {
        "ok": True,
        "path": str(path),
        "exists": path.exists(),
        "values": masked,
        "configured": {key: bool(values.get(key)) for key in _SENSITIVE_RUNTIME_CONFIG},
    }


def _validate_runtime_config(updates: dict[str, str]) -> tuple[bool, str]:
    for key, value in updates.items():
        if key not in _ALLOWED_RUNTIME_CONFIG:
            return False, f"{key} is not editable"
        if key.endswith("_IFACE") and not _valid_iface_name(value):
            return False, f"{key} is not a valid interface name"
    hostname = updates.get("JACKPACK_HOSTNAME")
    if hostname:
        normalized = hostname.lower().removesuffix(".local")
        if not _HOSTNAME_RE.match(normalized):
            return False, "hostname must be a valid single-label mDNS name"
        updates["JACKPACK_HOSTNAME"] = normalized
    password = updates.get("JACKPACK_AP_PASSWORD")
    if password is not None and password and len(password) < 8:
        return False, "AP password must be at least 8 characters"
    for port_key in ("RJ_WEB_PORT", "RJ_WS_PORT"):
        if port_key in updates:
            try:
                port = int(updates[port_key])
                if port < 1 or port > 65535:
                    raise ValueError
            except Exception:
                return False, f"{port_key} must be a port between 1 and 65535"
    if "JACKPACK_AP_CHANNEL" in updates:
        try:
            channel = int(updates["JACKPACK_AP_CHANNEL"])
            if channel < 1 or channel > 165:
                raise ValueError
        except Exception:
            return False, "AP channel must be 1-165"
    if "JACKPACK_AP_ADDRESS" in updates and "/" not in updates["JACKPACK_AP_ADDRESS"]:
        return False, "AP address must include CIDR, for example 10.66.0.1/24"
    return True, "ok"


def _write_runtime_config(updates: dict[str, str]) -> tuple[bool, str]:
    clean = {
        str(key): str(value).strip()
        for key, value in updates.items()
        if str(key) in _ALLOWED_RUNTIME_CONFIG and str(value).strip() != ""
    }
    ok, msg = _validate_runtime_config(clean)
    if not ok:
        return False, msg
    if "JACKPACK_AP_IFACE" in clean or "JACKPACK_WIRED_IFACE" in clean:
        current = _read_env_values(_runtime_env_path())
        wired = clean.get("JACKPACK_WIRED_IFACE") or current.get("JACKPACK_WIRED_IFACE") or "eth0"
        ap = clean.get("JACKPACK_AP_IFACE") or current.get("JACKPACK_AP_IFACE") or "wlan0"
        clean["RJ_WEBUI_INTERFACES"] = f"{wired},{ap},tailscale0"

    path = _runtime_env_path()
    try:
        old_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines() if path.exists() else [
            "# JackPack runtime configuration",
            "# Edited by the WebUI",
            "",
        ]
        seen: set[str] = set()
        new_lines: list[str] = []
        for raw in old_lines:
            stripped = raw.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in clean:
                    new_lines.append(f"{key}={clean[key]}")
                    seen.add(key)
                    continue
            new_lines.append(raw)
        for key in sorted(clean):
            if key not in seen:
                new_lines.append(f"{key}={clean[key]}")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(path)
        return True, "saved"
    except Exception as exc:
        return False, f"write error: {exc}"


def _write_update_status(payload: dict) -> None:
    data = {"ts": time.time(), **payload}
    try:
        UPDATE_STATUS_PATH.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def _read_update_status() -> dict:
    try:
        if not UPDATE_STATUS_PATH.exists():
            return {"running": False, "ok": None, "message": "No update run yet."}
        raw = UPDATE_STATUS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw) if raw else {}
        return data if isinstance(data, dict) else {"running": False}
    except Exception:
        return {"running": False, "ok": None, "message": "Update status unavailable."}


def _git_rev() -> str:
    code, stdout, _ = _run_command(["git", "rev-parse", "--short", "HEAD"], timeout=8)
    return stdout.strip() if code == 0 else ""


def _diagnostic_check(
    key: str,
    label: str,
    ok: bool | None,
    detail: str = "",
    severity: str = "error",
) -> dict:
    if ok is True:
        status = "pass"
    elif ok is False:
        status = "fail" if severity == "error" else "warn"
    else:
        status = "warn"
    return {
        "key": key,
        "label": label,
        "status": status,
        "detail": detail,
        "severity": severity,
    }


def _systemctl_state(service: str) -> tuple[str, str]:
    if _which("systemctl") is None:
        return "warn", "systemctl unavailable"
    active_code, active_out, active_err = _run_command(["systemctl", "is-active", service], timeout=8)
    enabled_code, enabled_out, _ = _run_command(["systemctl", "is-enabled", service], timeout=8)
    active = active_out.strip() or active_err.strip() or "unknown"
    enabled = enabled_out.strip() if enabled_code == 0 else "not enabled"
    state = "pass" if active_code == 0 and active == "active" else "warn"
    return state, f"{active}, {enabled}"


def _git_summary() -> dict:
    branch_code, branch_out, _ = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=8)
    remote_code, remote_out, _ = _run_command(["git", "remote", "get-url", "origin"], timeout=8)
    status_code, status_out, _ = _run_command(["git", "status", "--short"], timeout=8)
    return {
        "branch": branch_out.strip() if branch_code == 0 else "",
        "origin": remote_out.strip() if remote_code == 0 else "",
        "dirty": bool(status_out.strip()) if status_code == 0 else None,
        "status": status_out.strip(),
        "rev": _git_rev(),
    }


def _pi_model() -> str:
    for path in (Path("/proc/device-tree/model"), Path("/sys/firmware/devicetree/base/model")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").replace("\x00", "").strip()
            if text:
                return text
        except Exception:
            pass
    return ""


def _system_diagnostics() -> dict:
    checks: list[dict] = []
    model = _pi_model()
    checks.append(_diagnostic_check(
        "pi_model",
        "Raspberry Pi 5 model",
        None if not model else ("Raspberry Pi 5" in model),
        model or "Not running on Pi hardware or model unavailable",
        severity="warning",
    ))
    checks.append(_diagnostic_check(
        "root",
        "Running with required privileges",
        os.geteuid() == 0,
        "root" if os.geteuid() == 0 else f"uid {os.geteuid()}",
        severity="error",
    ))
    env_path = _runtime_env_path()
    checks.append(_diagnostic_check(
        "env_file",
        "Runtime config file",
        env_path.exists(),
        str(env_path),
        severity="error",
    ))
    checks.append(_diagnostic_check(
        "auth",
        "WebUI authentication initialized",
        _auth_initialized(),
        str(AUTH_FILE),
        severity="error",
    ))

    required_commands = [
        "nmcli", "ip", "iw", "git", "systemctl", "nmap", "tcpdump",
        "tshark", "airmon-ng", "airodump-ng", "hostapd", "dnsmasq",
        "avahi-daemon",
    ]
    for cmd in required_commands:
        path = _which(cmd)
        severity = "error" if cmd in {"nmcli", "ip", "git"} else "warning"
        checks.append(_diagnostic_check(
            f"cmd_{cmd}",
            f"Command available: {cmd}",
            bool(path),
            path or "missing",
            severity=severity,
        ))

    for service in ("packjack-ap.service", "packjack-web.service", "packjack-ws.service", "packjack-pin-wifi.service", "avahi-daemon.service"):
        state, detail = _systemctl_state(service)
        checks.append({
            "key": f"svc_{service}",
            "label": f"Service: {service}",
            "status": state,
            "detail": detail,
            "severity": "warning" if service == "avahi-daemon.service" else "error",
        })

    net = _network_status()
    iface_map = {item.get("role"): item for item in net.get("interfaces", [])}
    for role, label, severity in (
        ("control_ap", "Control AP interface", "error"),
        ("attack_wifi", "External payload WiFi interface", "warning"),
        ("wired_target", "Built-in Ethernet interface", "warning"),
    ):
        item = iface_map.get(role) or {}
        checks.append(_diagnostic_check(
            f"iface_{role}",
            label,
            bool(item.get("present")),
            f"{item.get('name') or '-'} · {item.get('state') or 'missing'}",
            severity=severity,
        ))

    git_info = _git_summary()
    checks.append(_diagnostic_check(
        "git_origin",
        "GitHub origin configured",
        bool(git_info.get("origin")),
        git_info.get("origin") or "missing",
        severity="warning",
    ))
    checks.append(_diagnostic_check(
        "git_clean",
        "Git tree clean for auto-update",
        git_info.get("dirty") is False,
        "dirty working tree" if git_info.get("dirty") else "clean",
        severity="warning",
    ))

    counts = {
        "pass": sum(1 for item in checks if item.get("status") == "pass"),
        "warn": sum(1 for item in checks if item.get("status") == "warn"),
        "fail": sum(1 for item in checks if item.get("status") == "fail"),
    }
    ready = counts["fail"] == 0
    return {
        "ok": True,
        "ready": ready,
        "counts": counts,
        "checks": checks,
        "network": net,
        "git": git_info,
        "update": _read_update_status(),
        "web": _read_headless_status().get("web", {}),
    }


def _run_update_job(restart: bool = False, apply_installer: bool = False) -> None:
    if not _UPDATE_LOCK.acquire(blocking=False):
        return
    output: list[str] = []
    started = time.time()
    try:
        rev_before = _git_rev()
        _write_update_status({
            "running": True,
            "ok": None,
            "started_at": started,
            "rev_before": rev_before,
            "output": "Starting update...",
        })
        steps = [
            ["git", "fetch", "origin", "main", "--prune"],
            ["git", "pull", "--ff-only", "origin", "main"],
        ]
        if apply_installer:
            steps.append(["bash", "scripts/install_packjack_rpi5.sh", "--non-interactive", "--no-packages"])
        ok = True
        for args in steps:
            output.append(f"$ {' '.join(args)}")
            timeout = 420 if args[:2] == ["bash", "scripts/install_packjack_rpi5.sh"] else 180
            code, stdout, stderr = _run_command(args, timeout=timeout)
            if stdout.strip():
                output.append(stdout.strip())
            if stderr.strip():
                output.append(stderr.strip())
            if code != 0:
                ok = False
                break
            _write_update_status({
                "running": True,
                "ok": None,
                "started_at": started,
                "rev_before": rev_before,
                "output": "\n".join(output)[-8000:],
            })
        rev_after = _git_rev()
        if ok and restart and _which("systemctl"):
            output.append("$ systemctl restart packjack-web.service packjack-ws.service")
            subprocess.Popen(["systemctl", "restart", "packjack-web.service", "packjack-ws.service"])
        _write_update_status({
            "running": False,
            "ok": ok,
            "started_at": started,
            "finished_at": time.time(),
            "rev_before": rev_before,
            "rev_after": rev_after,
            "message": "Updated and applied. Restart or reboot if services changed." if ok and apply_installer else ("Updated. Restart the WebUI if files changed." if ok else "Update failed."),
            "output": "\n".join(output)[-12000:],
        })
    finally:
        _UPDATE_LOCK.release()


def _tail_text(path: Path, max_bytes: int = 65536) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes), os.SEEK_SET)
            return handle.read().decode("utf-8", "replace")
    except FileNotFoundError:
        return ""
    except Exception as exc:
        return f"log read error: {exc}"


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _hmac_sign(payload: str) -> str:
    mac = hmac.new(AUTH_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    return _b64url_encode(mac)


def _issue_signed_token(claims: dict) -> str:
    payload = _b64url_encode(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
    sig = _hmac_sign(payload)
    return f"{payload}.{sig}"


def _read_signed_token(token: str) -> dict | None:
    try:
        payload, sig = token.split(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(_hmac_sign(payload), sig):
        return None
    try:
        raw = _b64url_decode(payload)
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _read_auth_config() -> dict | None:
    try:
        if not AUTH_FILE.exists():
            return None
        data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        if not data.get("username") or not data.get("password_hash"):
            return None
        return data
    except Exception:
        return None


def _auth_initialized() -> bool:
    return _read_auth_config() is not None


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    rounds = 210000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), rounds)
    return f"pbkdf2_sha256${rounds}${salt}${_b64url_encode(dk)}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algo, rounds, salt, digest = encoded.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(rounds))
        return hmac.compare_digest(_b64url_encode(dk), digest)
    except Exception:
        return False


def _write_auth_config(username: str, password: str) -> tuple[bool, str]:
    user = str(username or "").strip()
    pwd = str(password or "")
    if len(user) < 3:
        return False, "username must be at least 3 characters"
    if len(user) > 32:
        return False, "username too long"
    if len(pwd) < 8:
        return False, "password must be at least 8 characters"
    rec = {
        "username": user,
        "password_hash": _hash_password(pwd),
        "created_at": int(time.time()),
    }
    try:
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        AUTH_FILE.write_text(json.dumps(rec), encoding="utf-8")
        os.chmod(AUTH_FILE, 0o600)
        return True, "ok"
    except Exception as exc:
        return False, f"write error: {exc}"


def _session_from_cookie(handler: SimpleHTTPRequestHandler) -> dict | None:
    raw = str(handler.headers.get("Cookie", "") or "")
    if not raw:
        return None
    c = SimpleCookie()
    try:
        c.load(raw)
    except Exception:
        return None
    morsel = c.get(SESSION_COOKIE_NAME)
    if not morsel:
        return None
    claims = _read_signed_token(morsel.value)
    if not claims:
        return None
    if claims.get("typ") != "session":
        return None
    if int(claims.get("exp", 0)) < int(time.time()):
        return None
    if not claims.get("usr"):
        return None
    return claims


def _bearer_token_from_request(handler: SimpleHTTPRequestHandler, query: dict) -> str:
    try:
        authz = str(handler.headers.get("Authorization", "")).strip()
        if authz.lower().startswith("bearer "):
            return authz[7:].strip()
    except Exception:
        pass
    # Legacy fallback for older links.
    return str(query.get("token", [""])[0] or "").strip()


def _auth_context(handler: SimpleHTTPRequestHandler, query: dict) -> dict | None:
    sess = _session_from_cookie(handler)
    if sess:
        return {"method": "session", "user": str(sess.get("usr")), "claims": sess}
    bearer = _bearer_token_from_request(handler, query)
    if TOKEN and bearer and hmac.compare_digest(bearer, TOKEN):
        return {"method": "token", "user": "token-admin", "claims": None}
    if not _auth_initialized():
        return {"method": "bootstrap", "user": "bootstrap", "claims": None}
    return None


def _auth_ok(handler: SimpleHTTPRequestHandler, query: dict) -> bool:
    ctx = _auth_context(handler, query)
    return ctx is not None and ctx.get("method") != "bootstrap"


def _request_is_https(handler: SimpleHTTPRequestHandler) -> bool:
    """Return True for direct TLS or trusted local reverse proxy TLS."""
    if getattr(handler, "request_version", "").startswith("HTTPS/"):
        return True
    proto = str(handler.headers.get("X-Forwarded-Proto", "") or "").strip().lower()
    if proto != "https":
        return False
    try:
        ip = str(handler.client_address[0])
    except Exception:
        ip = ""
    # Trust forwarded scheme only from local proxy hops.
    return ip in ("127.0.0.1", "::1")


def _session_cookie_header(username: str, secure: bool = False, ttl_seconds: int = SESSION_TTL_SECONDS) -> tuple[str, str]:
    now = int(time.time())
    claims = {"typ": "session", "usr": username, "iat": now, "exp": now + int(ttl_seconds)}
    token = _issue_signed_token(claims)
    secure_attr = "; Secure" if secure else ""
    cookie = f"{SESSION_COOKIE_NAME}={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={int(ttl_seconds)}{secure_attr}"
    return ("Set-Cookie", cookie)


def _clear_session_cookie_header(secure: bool = False) -> tuple[str, str]:
    secure_attr = "; Secure" if secure else ""
    return ("Set-Cookie", f"{SESSION_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0{secure_attr}")


def _safe_loot_path(raw_path: str) -> Path | None:
    raw_path = raw_path.strip().lstrip("/")
    target = (LOOT_DIR / raw_path).resolve()
    try:
        loot_root = LOOT_DIR.resolve()
    except FileNotFoundError:
        loot_root = LOOT_DIR
    if loot_root in target.parents or target == loot_root:
        return target
    return None


def _safe_payload_path(raw_path: str) -> Path | None:
    raw_path = raw_path.strip().lstrip("/")
    target = (PAYLOADS_DIR / raw_path).resolve()
    try:
        payload_root = PAYLOADS_DIR.resolve()
    except FileNotFoundError:
        payload_root = PAYLOADS_DIR
    if payload_root in target.parents or target == payload_root:
        return target
    return None


def _json_response(
    handler: SimpleHTTPRequestHandler,
    payload: dict,
    status: int = 200,
    extra_headers: list[tuple[str, str]] | None = None,
) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    if extra_headers:
        for key, value in extra_headers:
            handler.send_header(key, value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: SimpleHTTPRequestHandler) -> dict | None:
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except Exception:
        length = 0
    try:
        raw = handler.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8", "ignore")) if raw else {}
    except Exception:
        return None


def _is_text_file(path: Path) -> bool:
    ctype, _ = mimetypes.guess_type(str(path))
    if ctype and ctype.startswith("text/"):
        return True
    ext = "".join(path.suffixes).lower() or path.suffix.lower()
    if ext in TEXT_EXTS:
        return True
    return False


class JackPackHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if (
            parsed.path.startswith("/api/loot/")
            or parsed.path.startswith("/api/payloads/")
            or parsed.path.startswith("/api/system/")
            or parsed.path.startswith("/api/headless/")
            or parsed.path.startswith("/api/network/")
            or parsed.path.startswith("/api/settings/")
            or parsed.path.startswith("/api/auth/")
            or parsed.path.startswith("/api/wardriving/")
        ):
            query = parse_qs(parsed.query or "")
            if parsed.path == "/api/auth/bootstrap-status":
                self._handle_auth_bootstrap_status()
                return
            if parsed.path == "/api/auth/me":
                self._handle_auth_me(query)
                return

            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return

            if parsed.path == "/api/payloads/list":
                self._handle_payloads_list()
                return
            if parsed.path == "/api/payloads/status":
                self._handle_payloads_status()
                return
            if parsed.path == "/api/payloads/log":
                self._handle_payloads_log(query)
                return
            if parsed.path == "/api/payloads/schema":
                self._handle_payloads_schema(query)
                return
            if parsed.path == "/api/payloads/workflow/portals":
                self._handle_payloads_workflow_portals()
                return

            if parsed.path == "/api/loot/list":
                self._handle_loot_list(query)
                return
            if parsed.path == "/api/loot/download":
                self._handle_loot_download(query)
                return
            if parsed.path == "/api/loot/view":
                self._handle_loot_view(query)
                return
            if parsed.path == "/api/loot/nmap":
                self._handle_loot_nmap(query)
                return
            if parsed.path == "/api/wardriving/sessions":
                self._handle_wardriving_sessions()
                return
            if parsed.path == "/api/wardriving/live":
                self._handle_wardriving_live()
                return
            if parsed.path == "/api/wardriving/session":
                self._handle_wardriving_session(query)
                return

            if parsed.path == "/api/system/status":
                self._handle_system_status()
                return
            if parsed.path == "/api/system/diagnostics":
                self._handle_system_diagnostics()
                return
            if parsed.path == "/api/system/update-status":
                self._handle_system_update_status()
                return
            if parsed.path == "/api/headless/status":
                self._handle_headless_status()
                return
            if parsed.path == "/api/network/status":
                self._handle_network_status()
                return
            if parsed.path == "/api/settings/discord_webhook":
                if not _auth_ok(self, query):
                    _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                    return
                self._handle_settings_webhook_get()
                return
            if parsed.path == "/api/settings/wigle":
                if not _auth_ok(self, query):
                    _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                    return
                self._handle_settings_wigle_get()
                return
            if parsed.path == "/api/settings/tailscale":
                if not _auth_ok(self, query):
                    _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                    return
                self._handle_settings_tailscale_get()
                return
            if parsed.path == "/api/settings/runtime":
                self._handle_settings_runtime_get()
                return

            _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/auth/bootstrap":
            self._handle_auth_bootstrap()
            return
        if parsed.path == "/api/auth/login":
            self._handle_auth_login()
            return
        if parsed.path == "/api/auth/logout":
            self._handle_auth_logout()
            return
        if parsed.path == "/api/auth/ws-ticket":
            query = parse_qs(parsed.query or "")
            self._handle_auth_ws_ticket(query)
            return

        if parsed.path == "/api/system/restart-ui":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_system_restart_ui()
            return
        if parsed.path == "/api/system/update":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_system_update()
            return
        if parsed.path == "/api/network/scan":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_network_scan()
            return
        if parsed.path == "/api/network/connect":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_network_connect()
            return
        if parsed.path == "/api/network/disconnect":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_network_disconnect()
            return

        if parsed.path == "/api/wardriving/start":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_wardriving_start()
            return
        if parsed.path == "/api/wardriving/stop":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_wardriving_stop()
            return

        if parsed.path in ("/api/payloads/start", "/api/payloads/run"):
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_payloads_start()
            return
        if parsed.path == "/api/payloads/stop":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_payloads_stop()
            return
        if parsed.path == "/api/payloads/native":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_payloads_native_create()
            return
        _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/settings/discord_webhook":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_settings_webhook_put()
            return
        if parsed.path == "/api/settings/wigle":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_settings_wigle_put()
            return
        if parsed.path == "/api/settings/tailscale":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_settings_tailscale_put()
            return
        if parsed.path == "/api/settings/runtime":
            query = parse_qs(parsed.query or "")
            if not _auth_ok(self, query):
                _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
                return
            self._handle_settings_runtime_put()
            return
        _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def _handle_loot_list(self, query: dict) -> None:
        raw = unquote(query.get("path", [""])[0])
        target = _safe_loot_path(raw)
        if target is None or not target.exists():
            _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return
        if not target.is_dir():
            _json_response(self, {"error": "not a directory"}, status=HTTPStatus.BAD_REQUEST)
            return

        items = []
        try:
            for entry in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                if entry.name.startswith("."):
                    continue
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "type": "dir" if entry.is_dir() else "file",
                    "size": stat.st_size,
                    "mtime": int(stat.st_mtime),
                })
        except Exception as exc:
            _json_response(self, {"error": f"read error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        parent = "" if target == LOOT_DIR else str(target.relative_to(LOOT_DIR).parent)
        current = "" if target == LOOT_DIR else str(target.relative_to(LOOT_DIR))
        _json_response(self, {
            "path": current,
            "parent": "" if parent == "." else parent,
            "items": items,
        })

    def _handle_payloads_list(self) -> None:
        cached = _PAYLOAD_LIST_CACHE.get("payload")
        if cached and (time.time() - float(_PAYLOAD_LIST_CACHE.get("ts") or 0)) < 5:
            _json_response(self, cached)
            return
        items: list[dict] = []
        if not PAYLOADS_DIR.exists():
            _json_response(self, {"categories": []})
            return

        for clean_rel_path in _native_payload_rel_paths():
            full_path = (PAYLOADS_DIR / clean_rel_path).resolve()
            if not full_path.is_file():
                continue
            workflow = _workflow_schema(clean_rel_path)
            schema = None if workflow else _payload_form_schema(full_path)
            form_meta = schema.get("meta", {}) if isinstance(schema, dict) and isinstance(schema.get("meta"), dict) else {}
            meta = _payload_meta(full_path)
            tags = form_meta.get("tags") if isinstance(form_meta.get("tags"), list) else None
            meta.update({
                "headless": "native",
                "needs_display": False,
                "tags": tags or ["jackpack-native", *(["wifi", "wlan1"] if workflow else [])],
                "description": (workflow or {}).get("summary") or form_meta.get("description") or meta.get("description") or "JackPack-native payload.",
            })
            items.append({
                "name": (workflow or {}).get("title") or (schema or {}).get("title") or full_path.stem.replace("_", " ").title(),
                "path": clean_rel_path,
                "meta": meta,
            })

        payload_categories = [{
            "id": "jackpack",
            "label": "JackPack",
            "description": "Native WebUI payloads only. Legacy RaspyJack payloads are source material for porting.",
            "items": sorted(items, key=lambda x: x["name"].lower()),
        }]

        payload = {"categories": payload_categories}
        _PAYLOAD_LIST_CACHE["payload"] = payload
        _PAYLOAD_LIST_CACHE["ts"] = time.time()
        _json_response(self, payload)

    def _handle_payloads_schema(self, query: dict) -> None:
        raw = query.get("path", [""])[0]
        target = _safe_payload_path(raw)
        if target is None or not target.is_file():
            _json_response(self, {"error": "payload not found"}, status=HTTPStatus.NOT_FOUND)
            return
        try:
            if NATIVE_PAYLOADS_DIR.resolve() not in target.resolve().parents:
                _json_response(self, {"error": "payload not ported"}, status=HTTPStatus.NOT_FOUND)
                return
        except Exception:
            _json_response(self, {"error": "payload not found"}, status=HTTPStatus.NOT_FOUND)
            return
        try:
            payload_root = PAYLOADS_DIR.resolve()
            rel_path = str(target.resolve().relative_to(payload_root)).replace("\\", "/")
        except Exception:
            rel_path = raw
        workflow = _workflow_schema(rel_path)
        if workflow:
            _json_response(self, {
                "mode": "workflow",
                "fields": [],
                "actions": [],
                "raw_args": False,
                "meta": {
                    "headless": "native",
                    "needs_display": False,
                    "uses_wifi": True,
                    "uses_external_wifi": True,
                    "tags": ["web-native", "wifi", "wlan1"],
                    "description": workflow.get("summary", ""),
                },
                "path": rel_path,
                "name": workflow.get("title") or Path(rel_path).stem.replace("_", " ").title(),
                "workflow": workflow,
            })
            return
        schema = _payload_form_schema(target)
        schema["path"] = rel_path
        schema["name"] = Path(rel_path).stem.replace("_", " ").title()
        _json_response(self, schema)

    def _handle_payloads_workflow_portals(self) -> None:
        portals = [{"id": "", "label": "Built-in WiFi Login", "builtin": True}]
        search_dirs = [PORTAL_SITES_DIR, Path("/root/JackPack/config/portal_sites")]
        seen = {""}
        for root in search_dirs:
            try:
                if not root.exists() or not root.is_dir():
                    continue
                for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
                    if not entry.is_dir() or entry.name.startswith("."):
                        continue
                    if entry.name in seen:
                        continue
                    if any((entry / name).is_file() for name in ("index.html", "login.html", "index.php")):
                        seen.add(entry.name)
                        portals.append({"id": entry.name, "label": entry.name.replace("_", " "), "builtin": False})
            except Exception:
                continue
        _json_response(self, {"ok": True, "portals": portals})

    def _handle_payloads_start(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return

        rel_path = str(body.get("path", "")).strip().lstrip("/").replace("\\", "/")
        if not rel_path.endswith(".py"):
            _json_response(self, {"error": "invalid payload path"}, status=HTTPStatus.BAD_REQUEST)
            return

        target = (PAYLOADS_DIR / rel_path).resolve()
        try:
            payloads_root = PAYLOADS_DIR.resolve()
        except FileNotFoundError:
            payloads_root = PAYLOADS_DIR
        if payloads_root not in target.parents or not target.exists():
            _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return

        if HEADLESS_MODE and payload_runner is not None:
            raw_args = body.get("args")
            args = raw_args if isinstance(raw_args, list) else None
            raw_env = body.get("env")
            extra_env = {
                str(key): str(value)
                for key, value in (raw_env.items() if isinstance(raw_env, dict) else [])
                if re.match(r"^[A-Z0-9_]{1,64}$", str(key))
            }
            workflow = _workflow_schema(rel_path)
            if workflow:
                selected_iface = str(extra_env.get("JACKPACK_SELECTED_IFACE") or extra_env.get("JACKPACK_ATTACK_IFACE") or "").strip()
                control_iface = _env_first("JACKPACK_AP_IFACE", "PACKJACK_AP_IFACE", default="wlan0")
                if selected_iface and (selected_iface == control_iface or _iface_role(selected_iface) == "control_ap"):
                    _json_response(
                        self,
                        {"error": f"{selected_iface} is the JackPack control AP; choose the USB WiFi adapter"},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
            try:
                status = payload_runner.start(rel_path, args, extra_env=extra_env)
                _json_response(self, {"ok": True, **status})
            except payload_runner.PayloadError as exc:
                _json_response(self, {"error": str(exc)}, status=HTTPStatus.CONFLICT)
            except Exception as exc:
                _json_response(self, {"error": f"start failed: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        try:
            request_path = Path("/dev/shm/rj_payload_request.json")
            request_path.write_text(json.dumps({
                "action": "start",
                "path": rel_path,
            }))
        except Exception as exc:
            _json_response(self, {"error": f"request failed: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        _json_response(self, {"ok": True})

    def _handle_payloads_status(self) -> None:
        if HEADLESS_MODE and payload_runner is not None:
            try:
                _json_response(self, payload_runner.status())
            except Exception:
                _json_response(self, {"running": False, "path": None, "mode": "headless"})
            return
        try:
            if not PAYLOAD_STATE_PATH.exists():
                _json_response(self, {"running": False, "path": None})
                return
            raw = PAYLOAD_STATE_PATH.read_text(encoding="utf-8")
            data = json.loads(raw) if raw else {}
            _json_response(self, {
                "running": bool(data.get("running")),
                "path": data.get("path"),
                "ts": data.get("ts"),
            })
        except Exception:
            _json_response(self, {"running": False, "path": None})

    def _handle_payloads_log(self, query: dict) -> None:
        try:
            max_bytes = int(query.get("bytes", ["65536"])[0])
        except Exception:
            max_bytes = 65536
        max_bytes = max(1024, min(262144, max_bytes))
        text = _tail_text(PAYLOAD_LOG_PATH, max_bytes=max_bytes)
        _json_response(self, {
            "path": str(PAYLOAD_LOG_PATH.relative_to(ROOT_DIR)) if PAYLOAD_LOG_PATH.is_absolute() else str(PAYLOAD_LOG_PATH),
            "bytes": max_bytes,
            "text": text,
            "exists": PAYLOAD_LOG_PATH.exists(),
            "mtime": int(PAYLOAD_LOG_PATH.stat().st_mtime) if PAYLOAD_LOG_PATH.exists() else None,
        })

    def _handle_payloads_stop(self) -> None:
        if HEADLESS_MODE and payload_runner is not None:
            try:
                _json_response(self, {"ok": True, **payload_runner.stop()})
            except Exception as exc:
                _json_response(self, {"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        try:
            sock_path = os.environ.get("RJ_INPUT_SOCK", "/dev/shm/rj_input.sock")
            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            try:
                s.sendto(json.dumps({"button": "KEY3", "state": "press"}).encode(), sock_path)
                time.sleep(0.08)
                s.sendto(json.dumps({"button": "KEY3", "state": "release"}).encode(), sock_path)
            finally:
                s.close()
            _json_response(self, {"ok": True, "status": "stopping"})
        except Exception as exc:
            _json_response(self, {"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_headless_status(self) -> None:
        _json_response(self, _read_headless_status())

    def _handle_network_status(self) -> None:
        _json_response(self, _network_status())

    def _handle_network_scan(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        iface = str(body.get("iface", "")).strip()
        ok, payload = _wifi_scan(iface)
        _json_response(self, payload, status=HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST)

    def _handle_network_connect(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        ok, payload = _connect_wifi(
            str(body.get("iface", "")).strip(),
            str(body.get("ssid", "")).strip(),
            str(body.get("password", "")),
            bool(body.get("hidden")),
            bool(body.get("force_control_iface")),
            str(body.get("security", "")).strip(),
            str(body.get("bssid", "")).strip(),
        )
        _json_response(self, payload, status=HTTPStatus.OK if ok else HTTPStatus.CONFLICT)

    def _handle_network_disconnect(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        ok, payload = _disconnect_iface(
            str(body.get("iface", "")).strip(),
            bool(body.get("force_control_iface")),
        )
        _json_response(self, payload, status=HTTPStatus.OK if ok else HTTPStatus.CONFLICT)

    def _handle_payloads_native_create(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return

        title = str(body.get("title") or "").strip()
        if not title:
            _json_response(self, {"error": "name required"}, status=HTTPStatus.BAD_REQUEST)
            return
        slug = _slugify_payload_name(body.get("slug") or title)
        description = str(body.get("description") or "JackPack native payload.").strip()[:240]
        iface_kind = str(body.get("iface_kind") or "none").strip().lower()
        if iface_kind not in {"none", "wifi", "wired"}:
            iface_kind = "none"
        raw_fields = str(body.get("fields") or "").strip()

        fields: list[dict] = []
        if iface_kind == "wifi":
            fields.append({
                "name": "iface",
                "env": "JACKPACK_SELECTED_IFACE",
                "label": "WiFi Adapter",
                "type": "interface",
                "iface_type": "wifi",
                "default": _env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1"),
                "help": "External USB WiFi adapter.",
                "allow_control_iface": False,
            })
        elif iface_kind == "wired":
            fields.append({
                "name": "iface",
                "env": "JACKPACK_SELECTED_IFACE",
                "label": "Ethernet",
                "type": "interface",
                "iface_type": "wired",
                "default": _env_first("JACKPACK_WIRED_IFACE", "PACKJACK_WIRED_IFACE", default="eth0"),
                "help": "Built-in Pi 5 Ethernet.",
            })

        for line in raw_fields.splitlines():
            parts = [part.strip() for part in line.split(":")]
            if not parts or not parts[0]:
                continue
            name = _slugify_payload_name(parts[0])
            label = parts[1] if len(parts) > 1 and parts[1] else name.replace("_", " ").title()
            ftype = parts[2].lower() if len(parts) > 2 and parts[2] else "text"
            if ftype not in {"text", "number", "checkbox", "textarea", "select", "password", "url", "email"}:
                ftype = "text"
            field = {
                "name": name,
                "env": f"JACKPACK_FIELD_{name.upper()}",
                "label": label[:60],
                "type": ftype,
                "default": "",
                "required": False,
            }
            if ftype == "select" and len(parts) > 3:
                choices = [choice.strip() for choice in parts[3].split(",") if choice.strip()]
                if choices:
                    field["choices"] = choices
            fields.append(field)

        target = (NATIVE_PAYLOADS_DIR / f"{slug}.py").resolve()
        if NATIVE_PAYLOADS_DIR.resolve() not in target.parents:
            _json_response(self, {"error": "invalid path"}, status=HTTPStatus.BAD_REQUEST)
            return
        if target.exists():
            _json_response(self, {"error": "payload already exists"}, status=HTTPStatus.CONFLICT)
            return

        form = {
            "mode": "form",
            "title": title,
            "raw_args": False,
            "fields": fields,
            "requirements": {"tools": []},
            "meta": {
                "description": description,
                "tags": ["jackpack-native"],
                "headless": "native",
            },
        }
        source = (
            "#!/usr/bin/env python3\n"
            f"{description!r}\n\n"
            "import os\n\n"
            "from packjack.payload_engine import PayloadContext\n\n"
            f"JACKPACK_FORM = {repr(form)}\n\n"
            "def main():\n"
            f"    ctx = PayloadContext({slug!r})\n"
            f"    ctx.log({(title + ' started')!r})\n"
            "    env = {k: v for k, v in os.environ.items() if k.startswith('JACKPACK_')}\n"
            "    ctx.write_json('last_env.json', env)\n"
            "    ctx.log('Add payload logic here. WebUI fields are available as environment variables.')\n"
            "    ctx.heartbeat('template complete', 0)\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n"
        )
        try:
            NATIVE_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
            os.chmod(target, 0o755)
            _PAYLOAD_LIST_CACHE["payload"] = None
            rel = str(target.relative_to(PAYLOADS_DIR)).replace("\\", "/")
            _json_response(self, {"ok": True, "path": rel})
        except Exception as exc:
            _json_response(self, {"error": f"create error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_loot_download(self, query: dict) -> None:
        raw = unquote(query.get("path", [""])[0])
        target = _safe_loot_path(raw)
        if target is None or not target.exists() or not target.is_file():
            _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return

        ctype, _ = mimetypes.guess_type(str(target))
        ctype = ctype or "application/octet-stream"
        try:
            size = target.stat().st_size
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
            self.end_headers()
            with target.open("rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except Exception:
            _json_response(self, {"error": "read error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_loot_view(self, query: dict) -> None:
        raw = unquote(query.get("path", [""])[0])
        target = _safe_loot_path(raw)
        if target is None or not target.exists() or not target.is_file():
            _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return
        if not _is_text_file(target):
            _json_response(self, {"error": "not text"}, status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            return

        try:
            size = target.stat().st_size
            read_size = min(size, PREVIEW_MAX_BYTES)
            with target.open("rb") as f:
                raw_data = f.read(read_size)
            text = raw_data.decode("utf-8", errors="replace")
            _json_response(self, {
                "name": target.name,
                "path": raw,
                "content": text,
                "truncated": size > PREVIEW_MAX_BYTES,
                "size": size,
                "mtime": int(target.stat().st_mtime),
            })
        except Exception:
            _json_response(self, {"error": "read error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_loot_nmap(self, query: dict) -> None:
        raw = unquote(query.get("path", [""])[0])
        target = _safe_loot_path(raw)
        if target is None or not target.exists() or not target.is_file():
            _json_response(self, {"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return
        if target.suffix.lower() != ".xml":
            _json_response(self, {"error": "not xml"}, status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            return

        include_raw = str(query.get("include_raw", [""])[0]).strip().lower() in {"1", "true", "yes", "on"}
        try:
            payload = parse_nmap_xml_file(target, include_raw_xml=include_raw)
            payload.setdefault("file", {})["loot_path"] = raw
            _json_response(self, payload)
        except ValueError as exc:
            _json_response(self, {"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            _json_response(self, {"error": f"parse error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    # ── Wardriving API ────────────────────────────────────────────
    def _handle_wardriving_sessions(self) -> None:
        """List all wardriving session files."""
        sessions_dir = str(LOOT_DIR / "wardriving" / "sessions")
        loot_dir = str(LOOT_DIR / "wardriving")
        result = []
        # Session files
        if os.path.isdir(sessions_dir):
            for f in sorted(os.listdir(sessions_dir), reverse=True):
                if f.endswith("_wigle.csv"):
                    result.append({
                        "name": f.replace("_wigle.csv", ""),
                        "path": os.path.join(sessions_dir, f),
                        "size": os.path.getsize(os.path.join(sessions_dir, f)),
                    })
        # Also include legacy live file
        live = os.path.join(loot_dir, "wardriving_live.csv")
        if os.path.isfile(live):
            result.insert(0, {
                "name": "Live (current)",
                "path": live,
                "size": os.path.getsize(live),
            })
        _json_response(self, result)

    def _handle_wardriving_live(self) -> None:
        """Serve the live wardriving CSV."""
        path = str(LOOT_DIR / "wardriving" / "wardriving_live.csv")
        if os.path.isfile(path):
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_wardriving_session(self, query: dict) -> None:
        """Serve a specific session CSV file."""
        path = query.get("path", [""])[0]
        # Security: only allow files in the wardriving loot dir
        wardriving_root = str((LOOT_DIR / "wardriving").resolve()) + os.sep
        if not path or not os.path.abspath(path).startswith(wardriving_root):
            self.send_response(403)
            self.end_headers()
            return
        if os.path.isfile(path):
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_wardriving_start(self) -> None:
        """Start wardriving in headless auto mode."""
        try:
            if HEADLESS_MODE and payload_runner is not None:
                try:
                    status = payload_runner.start("reconnaissance/wardriving.py", ["--auto"])
                    _json_response(self, {"ok": True, **status})
                except payload_runner.PayloadError as exc:
                    if "already running" in str(exc):
                        _json_response(self, {"ok": True, "status": "already_running", **payload_runner.status()})
                    else:
                        _json_response(self, {"error": str(exc)}, status=HTTPStatus.CONFLICT)
                return
            if PAYLOAD_STATE_PATH.exists():
                raw = PAYLOAD_STATE_PATH.read_text(encoding="utf-8")
                pdata = json.loads(raw) if raw else {}
                if pdata.get("running"):
                    _json_response(self, {"ok": True, "status": "already_running", "path": pdata.get("path")})
                    return
            request_path = Path("/dev/shm/rj_payload_request.json")
            request_path.write_text(json.dumps({
                "action": "start",
                "path": "reconnaissance/wardriving.py",
                "args": ["--auto"],
            }))
            _json_response(self, {"ok": True, "status": "starting"})
        except Exception as exc:
            _json_response(self, {"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_wardriving_stop(self) -> None:
        """Stop the currently running wardriving payload."""
        try:
            if HEADLESS_MODE and payload_runner is not None:
                _json_response(self, {"ok": True, **payload_runner.stop()})
                return
            sock_path = "/dev/shm/rj_input.sock"
            if not os.path.exists(sock_path):
                _json_response(self, {"ok": False, "error": "input socket not found"})
                return
            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            try:
                s.sendto(json.dumps({"button": "KEY3", "state": "press"}).encode(), sock_path)
                time.sleep(0.15)
                s.sendto(json.dumps({"button": "KEY3", "state": "release"}).encode(), sock_path)
            finally:
                s.close()
            _json_response(self, {"ok": True, "status": "stopping"})
        except Exception as exc:
            _json_response(self, {"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_system_status(self) -> None:
        try:
            cpu = _read_cpu_percent()
            mem_used, mem_total = _read_meminfo()
            du = shutil.disk_usage("/")
            temp_c = _read_temp_c()
            uptime_s = _read_uptime_seconds()
            ifaces = _read_ipv4_interfaces()
            load1, load5, load15 = os.getloadavg()
            payload_running = False
            payload_path = None
            if HEADLESS_MODE and payload_runner is not None:
                try:
                    pstatus = payload_runner.status()
                    payload_running = bool(pstatus.get("running"))
                    payload_path = pstatus.get("path")
                except Exception:
                    pass
            else:
                try:
                    if PAYLOAD_STATE_PATH.exists():
                        raw = PAYLOAD_STATE_PATH.read_text(encoding="utf-8")
                        pdata = json.loads(raw) if raw else {}
                        payload_running = bool(pdata.get("running"))
                        payload_path = pdata.get("path")
                except Exception:
                    pass

            role_map = {i.get("name"): i.get("role") for i in _read_headless_status().get("interfaces", [])}
            for iface in ifaces:
                iface["role"] = role_map.get(iface.get("name"), _iface_role(str(iface.get("name") or "")))

            _json_response(self, {
                "cpu_percent": round(cpu, 1),
                "mem_used": mem_used,
                "mem_total": mem_total,
                "disk_used": int(du.used),
                "disk_total": int(du.total),
                "temp_c": (round(temp_c, 1) if temp_c is not None else None),
                "uptime_s": uptime_s,
                "load": [round(load1, 2), round(load5, 2), round(load15, 2)],
                "interfaces": ifaces,
                "payload_running": payload_running,
                "payload_path": payload_path,
            })
        except Exception as exc:
            _json_response(self, {"error": f"status error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_system_restart_ui(self) -> None:
        try:
            subprocess.run(
                ["systemctl", "restart", "packjack-web.service"],
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            _json_response(self, {"ok": True})
        except subprocess.TimeoutExpired:
            _json_response(self, {"error": "restart timed out"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        except subprocess.CalledProcessError as exc:
            err = (exc.stderr or exc.stdout or "").strip() or "restart failed"
            _json_response(self, {"error": err}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as exc:
            _json_response(self, {"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_system_update_status(self) -> None:
        _json_response(self, _read_update_status())

    def _handle_system_diagnostics(self) -> None:
        _json_response(self, _system_diagnostics())

    def _handle_system_update(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        if _UPDATE_LOCK.locked():
            _json_response(self, {"error": "update already running"}, status=HTTPStatus.CONFLICT)
            return
        restart = bool(body.get("restart"))
        apply_installer = bool(body.get("apply_installer"))
        _write_update_status({
            "running": True,
            "ok": None,
            "started_at": time.time(),
            "message": "Update queued.",
            "output": "",
        })
        threading.Thread(
            target=_run_update_job,
            kwargs={"restart": restart, "apply_installer": apply_installer},
            daemon=True,
        ).start()
        _json_response(self, {"ok": True, "running": True})

    def _client_ip(self) -> str:
        try:
            return str(self.client_address[0])
        except Exception:
            return "unknown"

    def _handle_auth_bootstrap_status(self) -> None:
        _json_response(self, {"initialized": _auth_initialized()})

    def _handle_auth_bootstrap(self) -> None:
        if _auth_initialized():
            _json_response(self, {"error": "already initialized"}, status=HTTPStatus.CONFLICT)
            return
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        username = str(body.get("username", "")).strip()
        password = str(body.get("password", ""))
        ok, msg = _write_auth_config(username, password)
        if not ok:
            _json_response(self, {"error": msg}, status=HTTPStatus.BAD_REQUEST)
            return
        _json_response(
            self,
            {"ok": True, "initialized": True, "user": username},
            extra_headers=[_session_cookie_header(username, secure=_request_is_https(self))],
        )

    def _handle_auth_login(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        username = str(body.get("username", "")).strip()
        password = str(body.get("password", ""))
        now = time.time()
        ip = self._client_ip()
        failures = [ts for ts in _LOGIN_FAILS.get(ip, []) if now - ts < 600]
        _LOGIN_FAILS[ip] = failures
        if len(failures) >= 6:
            _json_response(self, {"error": "too many attempts"}, status=HTTPStatus.TOO_MANY_REQUESTS)
            return

        cfg = _read_auth_config()
        if not cfg:
            _json_response(self, {"error": "auth not initialized"}, status=HTTPStatus.PRECONDITION_FAILED)
            return
        if username != str(cfg.get("username", "")) or not _verify_password(password, str(cfg.get("password_hash", ""))):
            failures.append(now)
            _LOGIN_FAILS[ip] = failures
            _json_response(self, {"error": "invalid credentials"}, status=HTTPStatus.UNAUTHORIZED)
            return

        _LOGIN_FAILS[ip] = []
        _json_response(
            self,
            {"ok": True, "user": username},
            extra_headers=[_session_cookie_header(username, secure=_request_is_https(self))],
        )

    def _handle_auth_logout(self) -> None:
        _json_response(self, {"ok": True}, extra_headers=[_clear_session_cookie_header(secure=_request_is_https(self))])

    def _handle_auth_me(self, query: dict) -> None:
        ctx = _auth_context(self, query)
        if ctx is None or ctx.get("method") == "bootstrap":
            _json_response(self, {"authenticated": False}, status=HTTPStatus.UNAUTHORIZED)
            return
        _json_response(self, {
            "authenticated": True,
            "method": ctx.get("method"),
            "user": ctx.get("user"),
            "initialized": _auth_initialized(),
        })

    def _handle_auth_ws_ticket(self, query: dict) -> None:
        ctx = _auth_context(self, query)
        if ctx is None or ctx.get("method") == "bootstrap":
            _json_response(self, {"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
            return
        now = int(time.time())
        claims = {
            "typ": "ws_ticket",
            "usr": str(ctx.get("user", "user")),
            "iat": now,
            "exp": now + int(WS_TICKET_TTL_SECONDS),
        }
        _json_response(self, {
            "ok": True,
            "ticket": _issue_signed_token(claims),
            "expires_in": int(WS_TICKET_TTL_SECONDS),
        })

    def _handle_settings_webhook_get(self) -> None:
        webhook_url = _read_discord_webhook_url()
        _json_response(self, {
            "configured": bool(webhook_url),
            "url": webhook_url,
        })

    def _handle_settings_webhook_put(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        url = str(body.get("url", "")).strip()
        ok, status = _write_discord_webhook_url(url)
        if not ok:
            _json_response(self, {"error": status}, status=HTTPStatus.BAD_REQUEST)
            return
        _json_response(self, {
            "ok": True,
            "status": status,
            "configured": bool(url),
            "url": url if url else "",
        })

    def _handle_settings_wigle_get(self) -> None:
        creds = _read_wigle_credentials()
        api_name = creds.get("api_name", "")
        api_token = creds.get("api_token", "")
        _json_response(self, {
            "configured": bool(api_name and api_token),
            "api_name_masked": _mask_secret(api_name),
            "api_token_masked": _mask_secret(api_token),
        })

    def _handle_settings_wigle_put(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        clear_requested = bool(body.get("clear"))
        incoming_name = str(body.get("api_name", "")).strip()
        incoming_token = str(body.get("api_token", "")).strip()
        current = _read_wigle_credentials()
        if clear_requested:
            api_name = ""
            api_token = ""
        else:
            api_name = incoming_name or current.get("api_name", "")
            api_token = incoming_token or current.get("api_token", "")
        ok, status = _write_wigle_credentials(api_name, api_token)
        if not ok:
            _json_response(self, {"error": status}, status=HTTPStatus.BAD_REQUEST)
            return
        _json_response(self, {
            "ok": True,
            "status": status,
            "configured": bool(api_name and api_token),
            "api_name_masked": _mask_secret(api_name),
            "api_token_masked": _mask_secret(api_token),
        })

    def _handle_settings_tailscale_get(self) -> None:
        status = _tailscale_read_status()
        installed = _tailscale_installed()
        has_key = TAILSCALE_KEY_PATH.exists()
        ts = _tailscale_status() if installed else {"backend_state": None, "ip": None}
        _json_response(self, {
            "installed": installed,
            "has_key": has_key,
            "installing": bool(status.get("installing")),
            "ok": status.get("ok"),
            "error": status.get("error"),
            "backend_state": ts.get("backend_state"),
            "ip": ts.get("ip"),
        })

    def _handle_settings_tailscale_put(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        reauth = bool(body.get("reauth"))
        raw_key = str(body.get("auth_key", "")).strip()
        if not raw_key:
            _json_response(self, {"error": "auth key required"}, status=HTTPStatus.BAD_REQUEST)
            return
        if not raw_key.startswith("tskey-"):
            _json_response(self, {"error": "auth key must start with 'tskey-'"}, status=HTTPStatus.BAD_REQUEST)
            return
        ok, msg = _tailscale_write_key(raw_key)
        if not ok:
            _json_response(self, {"error": msg}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if _tailscale_installed():
            if not reauth:
                _json_response(self, {"error": "tailscale already installed"}, status=HTTPStatus.CONFLICT)
                return
            threading.Thread(target=_tailscale_run_reauth, daemon=True).start()
        else:
            threading.Thread(target=_tailscale_run_install_and_up, daemon=True).start()
        _json_response(self, {"ok": True})

    def _handle_settings_runtime_get(self) -> None:
        _json_response(self, _runtime_config_payload())

    def _handle_settings_runtime_put(self) -> None:
        body = _read_json(self)
        if body is None:
            _json_response(self, {"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return
        updates = body.get("values") if isinstance(body.get("values"), dict) else body
        ok, msg = _write_runtime_config(updates)
        if not ok:
            _json_response(self, {"error": msg}, status=HTTPStatus.BAD_REQUEST)
            return
        payload = _runtime_config_payload()
        payload.update({"ok": True, "status": msg})
        _json_response(self, payload)


def main() -> None:
    if TOKEN:
        print("[WebUI] Token auth enabled")
    else:
        print("[WebUI] WARNING: Token auth disabled (set RJ_WS_TOKEN or token file)")

    # If a specific host was set via env var, honour it as-is (single bind)
    if HOST != "0.0.0.0":
        server = ThreadingHTTPServer((HOST, PORT), JackPackHandler)
        print(f"[WebUI] Serving on http://{HOST}:{PORT}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return

    bind_addrs = _get_webui_bind_addrs()
    servers: list[ThreadingHTTPServer] = []
    for addr, iface in bind_addrs:
        try:
            server = ThreadingHTTPServer((addr, PORT), JackPackHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            servers.append(server)
            print(f"[WebUI] Serving on http://{addr}:{PORT} ({iface})")
        except Exception as exc:
            print(f"[WebUI] Could not bind {addr}:{PORT} ({iface}): {exc}")

    if not servers:
        server = ThreadingHTTPServer(("0.0.0.0", PORT), JackPackHandler)
        print(f"[WebUI] Serving on http://0.0.0.0:{PORT} (fallback)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
    return

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        for srv in servers:
            srv.server_close()


if __name__ == "__main__":
    main()

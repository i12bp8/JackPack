#!/usr/bin/env python3
"""
JackPack native payload -- Captive Portal Lab

WebUI-first captive portal for authorized training and lab validation. It
starts an AP on the selected USB WiFi interface, redirects clients to a preset
portal page, streams activity to the payload log, and writes loot under
loot/jackpack/captive_portal/.

This native port intentionally does not store passwords, tokens, or secrets.
Secret-looking POST fields are redacted before being written to loot.
"""

from __future__ import annotations

import html
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, unquote_plus


ROOT = Path(__file__).resolve().parents[2]
LOOT_DIR = ROOT / "loot" / "jackpack" / "captive_portal"
HOSTAPD_CONF = Path("/tmp/jackpack_native_portal_hostapd.conf")
DNSMASQ_CONF = Path("/tmp/jackpack_native_portal_dnsmasq.conf")
GATEWAY_IP = "10.66.77.1"
DHCP_RANGE = "10.66.77.20,10.66.77.240,12h"
HTTP_PORT = 80
IPTABLES_COMMENT = "JACKPACK_NATIVE_CAPTIVE_PORTAL"
SECRET_FIELD_RE = re.compile(r"(pass|password|pwd|token|secret|key|otp|code|pin|credential)", re.I)
MAC_RE = re.compile(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}")


JACKPACK_FORM = {
    "mode": "form",
    "raw_args": False,
    "meta": {
        "description": "Native WebUI captive portal for authorized training. Logs visits and redacted form submissions to loot.",
        "tags": ["jackpack-native", "wifi", "portal", "loot"],
        "headless": "native",
    },
    "fields": [
        {
            "name": "authorized",
            "env": "JACKPACK_PORTAL_AUTHORIZED",
            "label": "Authorized lab/test",
            "type": "checkbox",
            "required": True,
            "default": False,
            "help": "Required. Only run this on networks and devices you are authorized to test.",
        },
        {
            "name": "iface",
            "env": "JACKPACK_SELECTED_IFACE",
            "label": "USB WiFi Adapter",
            "type": "interface",
            "iface_type": "wifi",
            "required": True,
            "default": os.environ.get("JACKPACK_ATTACK_IFACE") or os.environ.get("PACKJACK_ATTACK_IFACE") or "wlan1",
            "help": "External adapter used to host the portal AP. JackPack refuses the control AP interface.",
            "allow_control_iface": False,
        },
        {
            "name": "ssid",
            "env": "JACKPACK_PORTAL_SSID",
            "label": "AP SSID",
            "type": "text",
            "default": "Guest-WiFi",
            "required": True,
            "help": "Network name broadcast by the training portal.",
        },
        {
            "name": "preset",
            "env": "JACKPACK_PORTAL_PRESET",
            "label": "Portal Preset",
            "type": "select",
            "default": "wifi_login",
            "choices": ["wifi_login", "guest_terms", "device_enrollment", "conference_wifi"],
            "help": "Preset page to serve. Submissions are logged with secret fields redacted.",
        },
        {
            "name": "event",
            "env": "JACKPACK_PORTAL_EVENT",
            "label": "Loot Folder Label",
            "type": "text",
            "default": "field-test",
            "help": "Short label written into loot metadata.",
        },
        {
            "name": "allowed_macs",
            "env": "JACKPACK_PORTAL_ALLOWED_MACS",
            "label": "Bypass MACs",
            "type": "textarea",
            "rows": 3,
            "default": "",
            "help": "Optional comma/newline separated MACs that should bypass the portal redirect.",
        },
    ],
}


PRESETS = {
    "wifi_login": {
        "title": "WiFi Access",
        "heading": "Guest WiFi",
        "body": "Enter your training identifier to continue.",
        "fields": [
            ("email", "Email or training ID", "email"),
            ("access_code", "Access code", "text"),
        ],
        "button": "Continue",
    },
    "guest_terms": {
        "title": "Guest Terms",
        "heading": "Guest Network",
        "body": "Accept the lab network terms to continue.",
        "fields": [
            ("name", "Name", "text"),
            ("team", "Team or company", "text"),
        ],
        "button": "Accept",
    },
    "device_enrollment": {
        "title": "Device Enrollment",
        "heading": "Device Enrollment",
        "body": "Register this test device with the lab portal.",
        "fields": [
            ("device_name", "Device name", "text"),
            ("owner", "Owner", "text"),
        ],
        "button": "Register",
    },
    "conference_wifi": {
        "title": "Conference WiFi",
        "heading": "Conference WiFi",
        "body": "Use the conference training portal to request access.",
        "fields": [
            ("badge_id", "Badge ID", "text"),
            ("email", "Email", "email"),
        ],
        "button": "Request access",
    },
}


stop_event = threading.Event()
hostapd_proc: subprocess.Popen | None = None
dnsmasq_proc: subprocess.Popen | None = None
portal_server: HTTPServer | None = None
current_preset = PRESETS["wifi_login"]
session_meta: dict[str, str] = {}
loot_lock = threading.Lock()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(value or "").strip()).strip("_")
    return slug[:64] or "portal"


def env(name: str, default: str = "") -> str:
    return str(os.environ.get(name, default) or default).strip()


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    printable = " ".join(cmd)
    print(f"[JackPack] $ {printable}", flush=True)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=12, check=check)


def command_exists(name: str) -> bool:
    return subprocess.run(["sh", "-c", f"command -v {name} >/dev/null 2>&1"]).returncode == 0


def require_tools() -> None:
    missing = [tool for tool in ("hostapd", "dnsmasq", "iptables", "ip") if not command_exists(tool)]
    if missing:
        raise RuntimeError(f"missing tools: {', '.join(missing)}")


def is_control_iface(iface: str) -> bool:
    control = env("JACKPACK_AP_IFACE", env("PACKJACK_AP_IFACE", "wlan0"))
    return bool(iface) and iface == control


def write_jsonl(path: Path, payload: dict) -> None:
    with loot_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")


def redact_fields(fields: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    redacted: dict[str, str] = {}
    secret_keys: list[str] = []
    for key, value in fields.items():
        clean_key = str(key or "").strip()[:80]
        clean_value = str(value or "")[:500]
        if SECRET_FIELD_RE.search(clean_key):
            redacted[clean_key] = "[redacted]"
            secret_keys.append(clean_key)
        else:
            redacted[clean_key] = clean_value
    return redacted, secret_keys


def render_portal_html() -> str:
    preset = current_preset
    fields = "\n".join(
        f'<input name="{html.escape(name)}" type="{html.escape(ftype)}" placeholder="{html.escape(label)}" required>'
        for name, label, ftype in preset["fields"]
    )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(preset["title"])}</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:#000; color:#f7f8ff; font-family:Inter,Arial,sans-serif; }}
    main {{ width:min(92vw,420px); border:1px solid #202330; border-radius:18px; background:#05060a; padding:28px; box-sizing:border-box; }}
    h1 {{ margin:0 0 10px; font-size:32px; letter-spacing:0; }}
    p {{ color:#9aa2b4; line-height:1.45; }}
    input {{ width:100%; margin:8px 0; padding:13px 14px; border-radius:10px; border:1px solid #202330; background:#02030a; color:#fff; box-sizing:border-box; }}
    button {{ width:100%; margin-top:12px; padding:14px; border:1px solid rgba(85,255,173,.45); border-radius:10px; background:#082015; color:#55ffad; font-weight:800; }}
    small {{ display:block; margin-top:14px; color:#6f7688; }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(preset["heading"])}</h1>
    <p>{html.escape(preset["body"])}</p>
    <form method="POST" action="/submit">
      {fields}
      <button>{html.escape(preset["button"])}</button>
    </form>
    <small>Training portal session {html.escape(session_meta.get("event", "lab"))}</small>
  </main>
</body>
</html>"""


SUCCESS_HTML = """<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#000;color:#f7f8ff;font-family:Inter,Arial,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}main{max-width:420px;padding:28px;border:1px solid #202330;border-radius:18px;background:#05060a}h1{color:#55ffad}</style>
</head><body><main><h1>Submitted</h1><p>This lab portal recorded the training event. You can close this page.</p></main></body></html>"""


class PortalHandler(BaseHTTPRequestHandler):
    def _send(self, body: str, status: int = 200, content_type: str = "text/html") -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        write_jsonl(LOOT_DIR / "visits.jsonl", {
            "ts": now_iso(),
            "src_ip": self.client_address[0],
            "path": path,
            "user_agent": self.headers.get("User-Agent", ""),
            **session_meta,
        })
        if path in ("/success", "/submitted"):
            self._send(SUCCESS_HTML)
        else:
            self._send(render_portal_html())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        parsed = parse_qs(raw, keep_blank_values=True)
        fields = {key: unquote_plus(values[0]) if values else "" for key, values in parsed.items()}
        redacted, secret_keys = redact_fields(fields)
        event = {
            "ts": now_iso(),
            "src_ip": self.client_address[0],
            "path": self.path.split("?", 1)[0],
            "fields": redacted,
            "redacted_fields": secret_keys,
            "user_agent": self.headers.get("User-Agent", ""),
            **session_meta,
        }
        write_jsonl(LOOT_DIR / "submissions_redacted.jsonl", event)
        print(
            f"[JackPack] submission from {event['src_ip']} preset={session_meta.get('preset')} "
            f"fields={list(redacted.keys())} redacted={secret_keys}",
            flush=True,
        )
        self._send(SUCCESS_HTML)

    def log_message(self, fmt: str, *args) -> None:
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def write_configs(iface: str, ssid: str, allowed_macs: list[str]) -> None:
    HOSTAPD_CONF.write_text(
        "\n".join([
            f"interface={iface}",
            "driver=nl80211",
            f"ssid={ssid}",
            "hw_mode=g",
            "channel=6",
            "auth_algs=1",
            "ignore_broadcast_ssid=0",
            "wmm_enabled=1",
            "",
        ]),
        encoding="utf-8",
    )
    DNSMASQ_CONF.write_text(
        "\n".join([
            f"interface={iface}",
            f"dhcp-range={DHCP_RANGE}",
            f"dhcp-option=3,{GATEWAY_IP}",
            f"dhcp-option=6,{GATEWAY_IP}",
            "address=/#/" + GATEWAY_IP,
            "log-queries",
            "log-dhcp",
            "",
        ]),
        encoding="utf-8",
    )
    (LOOT_DIR / "hostapd.conf").write_text(HOSTAPD_CONF.read_text(encoding="utf-8"), encoding="utf-8")
    (LOOT_DIR / "dnsmasq.conf").write_text(DNSMASQ_CONF.read_text(encoding="utf-8"), encoding="utf-8")
    (LOOT_DIR / "allowed_macs.json").write_text(json.dumps(allowed_macs, indent=2), encoding="utf-8")


def setup_iptables(iface: str, allowed_macs: list[str]) -> None:
    teardown_iptables(iface)
    for mac in allowed_macs:
        run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-m", "mac", "--mac-source", mac, "-m", "comment", "--comment", IPTABLES_COMMENT, "-j", "RETURN"], check=False)
    run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", "80", "-m", "comment", "--comment", IPTABLES_COMMENT, "-j", "REDIRECT", "--to-ports", str(HTTP_PORT)], check=False)
    run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", "443", "-m", "comment", "--comment", IPTABLES_COMMENT, "-j", "REDIRECT", "--to-ports", str(HTTP_PORT)], check=False)
    run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "udp", "--dport", "53", "-m", "comment", "--comment", IPTABLES_COMMENT, "-j", "REDIRECT", "--to-ports", "53"], check=False)


def teardown_iptables(iface: str = "") -> None:
    try:
        saved = subprocess.run(["sudo", "iptables-save", "-t", "nat"], capture_output=True, text=True, timeout=6)
    except Exception:
        saved = None
    lines = (saved.stdout.splitlines() if saved and saved.returncode == 0 else [])
    rules = [line for line in lines if IPTABLES_COMMENT in line and line.startswith("-A ")]
    for line in rules:
        parts = line.split()
        if len(parts) < 3:
            continue
        chain = parts[1]
        rule = parts[2:]
        if iface and "-i" in rule:
            try:
                idx = rule.index("-i")
                if idx + 1 < len(rule) and rule[idx + 1] != iface:
                    continue
            except ValueError:
                pass
        subprocess.run(["sudo", "iptables", "-t", "nat", "-D", chain, *rule], capture_output=True, text=True)


def stop_process(proc: subprocess.Popen | None, name: str) -> None:
    if not proc:
        return
    if proc.poll() is None:
        print(f"[JackPack] stopping {name}", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def cleanup() -> None:
    global portal_server
    print("[JackPack] cleaning up captive portal", flush=True)
    if portal_server:
        try:
            portal_server.shutdown()
            portal_server.server_close()
        except Exception:
            pass
        portal_server = None
    stop_process(dnsmasq_proc, "dnsmasq")
    stop_process(hostapd_proc, "hostapd")
    teardown_iptables(session_meta.get("iface", ""))


def handle_signal(signum, frame) -> None:
    stop_event.set()


def parse_allowed_macs(raw: str) -> list[str]:
    return sorted({mac.lower() for mac in MAC_RE.findall(raw or "")})


def main() -> int:
    global hostapd_proc, dnsmasq_proc, portal_server, current_preset, session_meta

    if env("JACKPACK_PORTAL_AUTHORIZED") != "1":
        print("[JackPack] Refusing to start: confirm Authorized lab/test in the WebUI.", flush=True)
        return 2

    iface = env("JACKPACK_SELECTED_IFACE", env("JACKPACK_ATTACK_IFACE", "wlan1"))
    ssid = env("JACKPACK_PORTAL_SSID", "Guest-WiFi")
    preset_id = env("JACKPACK_PORTAL_PRESET", "wifi_login")
    event_label = safe_slug(env("JACKPACK_PORTAL_EVENT", "field-test"))
    allowed_macs = parse_allowed_macs(env("JACKPACK_PORTAL_ALLOWED_MACS", ""))

    if not iface:
        print("[JackPack] No WiFi interface selected.", flush=True)
        return 2
    if is_control_iface(iface):
        print(f"[JackPack] Refusing to use control AP interface {iface}. Choose the USB WiFi adapter.", flush=True)
        return 2

    current_preset = PRESETS.get(preset_id, PRESETS["wifi_login"])
    session_meta = {"event": event_label, "preset": preset_id, "ssid": ssid, "iface": iface}

    LOOT_DIR.mkdir(parents=True, exist_ok=True)
    (LOOT_DIR / "portal.html").write_text(render_portal_html(), encoding="utf-8")
    (LOOT_DIR / "session.json").write_text(json.dumps({**session_meta, "started_at": now_iso()}, indent=2), encoding="utf-8")
    write_jsonl(LOOT_DIR / "events.jsonl", {"ts": now_iso(), "event_type": "start", **session_meta})

    require_tools()
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    print(f"[JackPack] Captive portal starting on {iface}", flush=True)
    print(f"[JackPack] SSID={ssid!r} preset={preset_id!r} loot={LOOT_DIR}", flush=True)
    print("[JackPack] Secret-looking fields are redacted before saving.", flush=True)

    write_configs(iface, ssid, allowed_macs)
    run(["sudo", "ip", "addr", "flush", "dev", iface], check=False)
    run(["sudo", "ip", "addr", "add", f"{GATEWAY_IP}/24", "dev", iface], check=False)
    run(["sudo", "ip", "link", "set", iface, "up"], check=False)

    hostapd_proc = subprocess.Popen(["sudo", "hostapd", str(HOSTAPD_CONF)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.3)
    if hostapd_proc.poll() is not None:
        out = hostapd_proc.stdout.read() if hostapd_proc.stdout else ""
        print(f"[JackPack] hostapd failed: {out[-800:]}", flush=True)
        return 1

    dnsmasq_proc = subprocess.Popen(["sudo", "dnsmasq", "-C", str(DNSMASQ_CONF), "--no-daemon"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(0.5)
    if dnsmasq_proc.poll() is not None:
        out = dnsmasq_proc.stdout.read() if dnsmasq_proc.stdout else ""
        print(f"[JackPack] dnsmasq failed: {out[-800:]}", flush=True)
        return 1

    setup_iptables(iface, allowed_macs)
    portal_server = ThreadedHTTPServer(("0.0.0.0", HTTP_PORT), PortalHandler)
    threading.Thread(target=portal_server.serve_forever, daemon=True).start()
    print(f"[JackPack] Portal live at http://{GATEWAY_IP}/", flush=True)
    print("[JackPack] Loot: loot/jackpack/captive_portal/{visits,submissions_redacted,events}.jsonl", flush=True)

    try:
        while not stop_event.is_set():
            if hostapd_proc.poll() is not None:
                print("[JackPack] hostapd stopped unexpectedly", flush=True)
                return 1
            if dnsmasq_proc.poll() is not None:
                print("[JackPack] dnsmasq stopped unexpectedly", flush=True)
                return 1
            time.sleep(1)
    finally:
        write_jsonl(LOOT_DIR / "events.jsonl", {"ts": now_iso(), "event_type": "stop", **session_meta})
        cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

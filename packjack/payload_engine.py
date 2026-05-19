from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
LOOT_ROOT = ROOT_DIR / "loot" / "jackpack"


def field(
    name: str,
    label: str | None = None,
    type: str = "text",
    *,
    env: str | None = None,
    default: Any = "",
    required: bool = False,
    help: str = "",
    choices: Iterable[str] | None = None,
    rows: int | None = None,
    min: int | float | None = None,
    max: int | float | None = None,
    **extra: Any,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "name": name,
        "label": label or name.replace("_", " ").title(),
        "type": type,
        "env": env or f"JACKPACK_FIELD_{name.upper()}",
        "default": default,
        "required": bool(required),
        "help": help,
    }
    if choices is not None:
        item["choices"] = list(choices)
    if rows is not None:
        item["rows"] = rows
    if min is not None:
        item["min"] = min
    if max is not None:
        item["max"] = max
    item.update(extra)
    return item


def text(name: str, label: str | None = None, **kwargs: Any) -> dict[str, Any]:
    return field(name, label, "text", **kwargs)


def password(name: str, label: str | None = None, **kwargs: Any) -> dict[str, Any]:
    return field(name, label, "password", **kwargs)


def textarea(name: str, label: str | None = None, **kwargs: Any) -> dict[str, Any]:
    return field(name, label, "textarea", **kwargs)


def number(name: str, label: str | None = None, **kwargs: Any) -> dict[str, Any]:
    return field(name, label, "number", **kwargs)


def checkbox(name: str, label: str | None = None, **kwargs: Any) -> dict[str, Any]:
    return field(name, label, "checkbox", **kwargs)


def select(name: str, label: str | None = None, choices: Iterable[str] = (), **kwargs: Any) -> dict[str, Any]:
    return field(name, label, "select", choices=choices, **kwargs)


def interface(
    name: str = "iface",
    label: str = "Interface",
    *,
    kind: str = "wifi",
    env: str = "JACKPACK_SELECTED_IFACE",
    default: str | None = None,
    allow_control_iface: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    if default is None:
        if kind in ("eth", "wired"):
            default = os.environ.get("JACKPACK_WIRED_IFACE") or os.environ.get("PACKJACK_WIRED_IFACE") or "eth0"
        else:
            default = os.environ.get("JACKPACK_ATTACK_IFACE") or os.environ.get("PACKJACK_ATTACK_IFACE") or "wlan1"
    return field(
        name,
        label,
        "interface",
        env=env,
        default=default,
        iface_type=kind,
        allow_control_iface=allow_control_iface,
        **kwargs,
    )


def form(
    *,
    title: str = "",
    description: str = "",
    fields: Iterable[dict[str, Any]] = (),
    tags: Iterable[str] = (),
    tools: Iterable[str] = (),
    raw_args: bool = False,
    requires_authorization: bool = False,
) -> dict[str, Any]:
    final_fields = list(fields)
    if requires_authorization and not any(item.get("name") == "authorized" for item in final_fields):
        final_fields.insert(0, checkbox(
            "authorized",
            "Authorized test",
            env="JACKPACK_AUTHORIZED",
            required=True,
            help="Required. Confirm you have explicit permission for this workflow.",
        ))
    return {
        "mode": "form",
        "raw_args": bool(raw_args),
        "title": title,
        "fields": final_fields,
        "requirements": {"tools": list(tools)},
        "meta": {
            "description": description,
            "tags": ["jackpack-native", *list(tags)],
            "headless": "native",
        },
    }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slug(value: str, fallback: str = "payload") -> str:
    clean = re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(value or "").strip()).strip("_")
    return clean[:80] or fallback


@dataclass
class ToolResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


class PayloadContext:
    def __init__(self, name: str, *, event: str | None = None) -> None:
        self.name = slug(name)
        self.event = slug(event or self.env("JACKPACK_EVENT", "run"))
        self.started_at = now_iso()
        self.loot_dir = LOOT_ROOT / self.name / self.event
        self.loot_dir.mkdir(parents=True, exist_ok=True)

    def env(self, key: str, default: str = "") -> str:
        return str(os.environ.get(key, default) or default).strip()

    def bool_env(self, key: str, default: bool = False) -> bool:
        raw = self.env(key, "1" if default else "0").lower()
        return raw in {"1", "true", "yes", "on", "checked"}

    def require_authorized(self, key: str = "JACKPACK_AUTHORIZED") -> None:
        if not self.bool_env(key):
            raise RuntimeError("authorized test confirmation is required")

    def selected_iface(self, default: str = "wlan1") -> str:
        return self.env("JACKPACK_SELECTED_IFACE", self.env("JACKPACK_ATTACK_IFACE", default))

    def ensure_not_control_iface(self, iface: str) -> None:
        control = self.env("JACKPACK_AP_IFACE", self.env("PACKJACK_AP_IFACE", "wlan0"))
        if iface and iface == control:
            raise RuntimeError(f"{iface} is the JackPack control AP")

    def require_tools(self, tools: Iterable[str]) -> None:
        missing = [tool for tool in tools if shutil.which(tool) is None]
        if missing:
            raise RuntimeError(f"missing required tools: {', '.join(missing)}")

    def log(self, message: str) -> None:
        print(f"[JackPack] {message}", flush=True)

    def write_json(self, name: str, payload: Any) -> Path:
        path = self.loot_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def write_jsonl(self, name: str, payload: dict[str, Any]) -> Path:
        path = self.loot_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": now_iso(), **payload}, sort_keys=True) + "\n")
        return path

    def write_text(self, name: str, content: str) -> Path:
        path = self.loot_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run(
        self,
        args: list[str] | str,
        *,
        check: bool = False,
        timeout: int | float | None = None,
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
    ) -> ToolResult:
        cmd = shlex.split(args) if isinstance(args, str) else [str(item) for item in args]
        self.log("$ " + " ".join(shlex.quote(item) for item in cmd))
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT_DIR),
            env={**os.environ, **(env or {})},
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.stdout:
            print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n", flush=True)
        if proc.stderr:
            print(proc.stderr, end="" if proc.stderr.endswith("\n") else "\n", flush=True)
        result = ToolResult(cmd, proc.returncode, proc.stdout, proc.stderr)
        self.write_jsonl("commands.jsonl", {
            "args": cmd,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        })
        if check and proc.returncode != 0:
            raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}")
        return result

    def heartbeat(self, label: str = "running", interval: float = 1.0) -> None:
        self.write_json("status.json", {
            "name": self.name,
            "event": self.event,
            "status": label,
            "started_at": self.started_at,
            "updated_at": now_iso(),
        })
        time.sleep(interval)


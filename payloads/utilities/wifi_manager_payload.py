#!/usr/bin/env python3
"""JackPack WiFi manager payload.

This replaces the old LCD WiFi manager launcher with a headless status view.
The WebUI owns interactive WiFi/AP controls; this payload is useful as a quick
log/status command from the launchpad.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "wifi"))


def _run(args: list[str]) -> str:
    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=12)
    except Exception as exc:
        return f"{args[0]} error: {exc}"
    return (res.stdout or res.stderr or "").strip()


def main() -> int:
    ap_iface = os.environ.get("JACKPACK_AP_IFACE") or os.environ.get("PACKJACK_AP_IFACE", "wlan0")
    attack_iface = os.environ.get("JACKPACK_ATTACK_IFACE") or os.environ.get("PACKJACK_ATTACK_IFACE", "wlan1")

    payload = {
        "ap_iface": ap_iface,
        "attack_iface": attack_iface,
        "ip_addr": _run(["ip", "-br", "addr"]),
        "wifi_devices": _run(["iw", "dev"]),
        "routes": _run(["ip", "route"]),
    }

    out_dir = ROOT / "loot" / "network"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "wifi_status.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nSaved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


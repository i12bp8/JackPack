from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ApConfig:
    iface: str = os.environ.get("JACKPACK_AP_IFACE") or os.environ.get("PACKJACK_AP_IFACE", "wlan0")
    ssid: str = os.environ.get("JACKPACK_AP_SSID") or os.environ.get("PACKJACK_AP_SSID", "JackPack")
    password: str = os.environ.get("JACKPACK_AP_PASSWORD") or os.environ.get("PACKJACK_AP_PASSWORD", "jackpack-change-me")
    address: str = os.environ.get("JACKPACK_AP_ADDRESS") or os.environ.get("PACKJACK_AP_ADDRESS", "10.66.0.1/24")
    channel: str = os.environ.get("JACKPACK_AP_CHANNEL") or os.environ.get("PACKJACK_AP_CHANNEL", "6")


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=30)


def status(config: ApConfig | None = None) -> dict:
    cfg = config or ApConfig()
    res = run(["nmcli", "-t", "-f", "GENERAL.STATE,GENERAL.CONNECTION", "dev", "show", cfg.iface])
    return {
        "iface": cfg.iface,
        "ssid": cfg.ssid,
        "address": cfg.address,
        "available": res.returncode == 0,
        "nmcli": (res.stdout or res.stderr).strip(),
    }

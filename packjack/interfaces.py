from __future__ import annotations

import os
from pathlib import Path


def env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = str(os.environ.get(name, "")).strip()
        if value:
            return value
    return default


def ap_iface() -> str:
    return env_first("JACKPACK_AP_IFACE", "PACKJACK_AP_IFACE", default="wlan0")


def attack_wifi_iface() -> str:
    return env_first("JACKPACK_ATTACK_IFACE", "PACKJACK_ATTACK_IFACE", default="wlan1")


def wired_iface() -> str:
    return env_first("JACKPACK_WIRED_IFACE", "PACKJACK_WIRED_IFACE", default="eth0")


def is_wireless(iface: str) -> bool:
    return Path(f"/sys/class/net/{iface}/wireless").is_dir()


def is_virtual(iface: str) -> bool:
    if iface.startswith(("br-", "docker", "veth", "virbr")):
        return True
    return not Path(f"/sys/class/net/{iface}/device").exists()


def is_control_iface(iface: str) -> bool:
    return iface == ap_iface()


def interface_role(iface: str) -> str:
    if iface == ap_iface():
        return "control_ap"
    if iface == attack_wifi_iface():
        return "attack_wifi"
    if iface == wired_iface():
        return "wired_target"
    if iface.startswith("tailscale"):
        return "tunnel"
    if is_wireless(iface):
        return "wifi"
    return "network"


def prefer_wired(ifaces: list[str]) -> list[str]:
    preferred = wired_iface()
    return sorted(ifaces, key=lambda name: (name != preferred, name))


def prefer_attack_wifi(ifaces: list[str], include_control: bool = False) -> list[str]:
    attack = attack_wifi_iface()
    control = ap_iface()
    filtered = [name for name in ifaces if include_control or name != control]
    return sorted(filtered, key=lambda name: (name != attack, name == control, name))


def default_payload_iface(kind: str = "any") -> str:
    if kind == "wifi":
        return attack_wifi_iface()
    if kind in {"eth", "wired"}:
        return wired_iface()
    return wired_iface()

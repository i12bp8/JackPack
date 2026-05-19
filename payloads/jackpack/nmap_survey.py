#!/usr/bin/env python3
"""JackPack native payload -- Nmap Survey"""

from __future__ import annotations

import re

from packjack.payload_engine import PayloadContext, slug


JACKPACK_FORM = {
    "mode": "form",
    "title": "Nmap Survey",
    "raw_args": False,
    "fields": [
        {
            "name": "authorized",
            "env": "JACKPACK_AUTHORIZED",
            "label": "Authorized test",
            "type": "checkbox",
            "required": True,
            "default": False,
            "help": "Required. Only scan systems and networks you are authorized to assess.",
        },
        {
            "name": "iface",
            "env": "JACKPACK_SELECTED_IFACE",
            "label": "Network Interface",
            "type": "interface",
            "required": False,
            "default": "eth0",
            "allow_control_iface": False,
            "help": "Use eth0 for wired targets or wlan1 after joining an authorized WiFi network.",
        },
        {
            "name": "target",
            "env": "JACKPACK_NMAP_TARGET",
            "label": "Target",
            "type": "text",
            "required": True,
            "default": "192.168.1.0/24",
            "help": "Host, CIDR, or authorized target list understood by nmap.",
        },
        {
            "name": "profile",
            "env": "JACKPACK_NMAP_PROFILE",
            "label": "Scan Profile",
            "type": "select",
            "default": "quick_tcp",
            "choices": [
                {"value": "ping_sweep", "label": "Ping sweep", "description": "Host discovery only"},
                {"value": "quick_tcp", "label": "Quick TCP", "description": "Top ports, practical first look"},
                {"value": "service", "label": "Service detect", "description": "Adds version detection"},
                {"value": "full_tcp", "label": "Full TCP", "description": "All TCP ports, slower"},
            ],
        },
        {
            "name": "timing",
            "env": "JACKPACK_NMAP_TIMING",
            "label": "Timing",
            "type": "select",
            "default": "T3",
            "choices": ["T2", "T3", "T4"],
        },
        {
            "name": "top_ports",
            "env": "JACKPACK_NMAP_TOP_PORTS",
            "label": "Top Ports",
            "type": "number",
            "default": 100,
            "min": 10,
            "max": 5000,
            "help": "Used by Quick TCP and Service Detect.",
        },
        {
            "name": "skip_discovery",
            "env": "JACKPACK_NMAP_SKIP_DISCOVERY",
            "label": "Treat hosts as online (-Pn)",
            "type": "checkbox",
            "default": False,
        },
        {
            "name": "no_dns",
            "env": "JACKPACK_NMAP_NO_DNS",
            "label": "Skip reverse DNS (-n)",
            "type": "checkbox",
            "default": True,
        },
        {
            "name": "label",
            "env": "JACKPACK_NMAP_LABEL",
            "label": "Loot Label",
            "type": "text",
            "default": "survey",
            "help": "Short label for the loot folder.",
        },
    ],
    "requirements": {"tools": ["nmap"]},
    "meta": {
        "description": "Authorized Nmap survey with profiles, live output, and XML/text loot.",
        "tags": ["jackpack-native", "network", "nmap", "ethernet", "wifi"],
        "headless": "native",
    },
}


SAFE_TARGET_RE = re.compile(r"^[a-zA-Z0-9_./:,*?\-\[\]]{1,500}$")


def clamp_int(value: str, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(str(value).strip())
    except Exception:
        return default
    return max(minimum, min(maximum, parsed))


def build_command(ctx: PayloadContext) -> tuple[list[str], str]:
    target = ctx.env("JACKPACK_NMAP_TARGET")
    if not target or not SAFE_TARGET_RE.match(target):
        raise RuntimeError("target is empty or contains unsupported characters")

    profile = ctx.env("JACKPACK_NMAP_PROFILE", "quick_tcp")
    timing = ctx.env("JACKPACK_NMAP_TIMING", "T3")
    if timing not in {"T2", "T3", "T4"}:
        timing = "T3"
    top_ports = clamp_int(ctx.env("JACKPACK_NMAP_TOP_PORTS", "100"), 100, 10, 5000)

    label = slug(ctx.env("JACKPACK_NMAP_LABEL", "survey"), "survey")
    xml_path = ctx.loot_dir / f"{label}.xml"
    text_path = ctx.loot_dir / f"{label}.txt"

    cmd = ["nmap", f"-{timing}", "-oX", str(xml_path), "-oN", str(text_path)]
    if ctx.bool_env("JACKPACK_NMAP_NO_DNS", True):
        cmd.append("-n")
    if ctx.bool_env("JACKPACK_NMAP_SKIP_DISCOVERY", False):
        cmd.append("-Pn")

    iface = ctx.env("JACKPACK_SELECTED_IFACE")
    if iface:
        ctx.ensure_not_control_iface(iface)
        cmd.extend(["-e", iface])

    if profile == "ping_sweep":
        cmd.append("-sn")
    elif profile == "service":
        cmd.extend(["-sV", "--version-light", "--top-ports", str(top_ports)])
    elif profile == "full_tcp":
        cmd.extend(["-p-", "--max-retries", "2"])
    else:
        cmd.extend(["--top-ports", str(top_ports)])

    cmd.append(target)
    return cmd, label


def main() -> int:
    ctx = PayloadContext("nmap_survey", event=ctx_event_label())
    ctx.require_authorized()
    ctx.require_tools(["nmap"])
    cmd, label = build_command(ctx)
    ctx.log("Starting authorized Nmap survey")
    result = ctx.run(cmd, check=False)
    ctx.write_json("summary.json", {
        "label": label,
        "returncode": result.returncode,
        "command": result.args,
        "stdout_file": f"{label}.txt",
        "xml_file": f"{label}.xml",
    })
    ctx.log(f"Nmap survey complete with exit code {result.returncode}")
    return result.returncode


def ctx_event_label() -> str:
    # Keep event folders stable and readable before PayloadContext exists.
    import os

    return slug(os.environ.get("JACKPACK_NMAP_LABEL", "survey"), "survey")


if __name__ == "__main__":
    raise SystemExit(main())

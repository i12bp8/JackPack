# JackPack Payload Engine

JackPack payloads are native, headless workflows for the Raspberry Pi 5 WebUI. The engine exists so contributors and AI coding agents can port RaspyJack ideas into clean browser controls instead of LCD menus, button navigation, or hardcoded Pi Zero HAT assumptions.

Use this document as the contract for new payloads.

> [!CAUTION]
> JackPack payloads must be written for authorized security testing, lab research, education, and owned infrastructure. Do not add workflows whose purpose is credential theft, unauthorized persistence, stealthy compromise, destructive activity, or bypassing consent.

## Goals

A good JackPack payload should feel like a small focused app:

- Clear setup form with text inputs, selectors, checkboxes, number fields, and interface pickers.
- Safe Pi 5 interface behavior: `wlan0` is the phone AP, `wlan1` is external WiFi, `eth0` is wired target access.
- Fast launch with useful live output.
- Structured loot saved where the WebUI can show it.
- No LCD simulation, no `up/down/left/right` button maze, no mystery defaults.
- One payload, one understandable workflow.

## File Location

Runnable native payloads live here:

```text
payloads/jackpack/<payload_name>.py
```

Hidden templates or shared examples can start with `_`:

```text
payloads/jackpack/_template_payload.py
```

Legacy RaspyJack scripts stay in their original folders until they are ported. They are source material, not WebUI-ready payloads.

## Minimal Payload

```python
#!/usr/bin/env python3
"""Network survey example."""

from packjack.payload_engine import PayloadContext

JACKPACK_FORM = {
    "mode": "form",
    "title": "Network Survey",
    "raw_args": False,
    "fields": [
        {
            "name": "iface",
            "env": "JACKPACK_SELECTED_IFACE",
            "label": "Interface",
            "type": "interface",
            "iface_type": "wired",
            "default": "eth0",
            "required": True,
        },
        {
            "name": "target",
            "env": "JACKPACK_FIELD_TARGET",
            "label": "Target Range",
            "type": "text",
            "required": True,
            "help": "Example: 192.168.1.0/24 in an authorized lab.",
        },
    ],
    "requirements": {"tools": ["nmap"]},
    "meta": {
        "description": "Runs an authorized network inventory scan and saves output to loot.",
        "tags": ["jackpack-native", "network"],
        "headless": "native",
    },
}


def main():
    ctx = PayloadContext("network_survey")
    iface = ctx.selected_iface("eth0")
    target = ctx.env("JACKPACK_FIELD_TARGET")
    ctx.require_tools(["nmap"])
    ctx.log(f"Scanning {target} via {iface}")
    result = ctx.run(["nmap", "-oX", str(ctx.loot_dir / "scan.xml"), target], check=False)
    ctx.write_text("stdout.txt", result.stdout)
    ctx.write_text("stderr.txt", result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
```

## `JACKPACK_FORM`

`JACKPACK_FORM` must be a literal Python dictionary. Do not build it with functions, imports, or runtime code. The WebUI parses it statically with `ast` so payload listing is fast and safe.

Top-level keys:

- `mode`: use `form`.
- `title`: human name shown in the payload browser.
- `raw_args`: usually `False` for native payloads.
- `fields`: ordered setup controls.
- `requirements.tools`: binaries used by the payload.
- `meta.description`: one sentence that tells the user what the payload does.
- `meta.tags`: short category tags such as `wifi`, `ethernet`, `sdr`, `bluetooth`, `inventory`, `analysis`.
- `meta.headless`: use `native`.

## Field Types

Use fields instead of LCD menus. Every old “press left/right” choice should become a direct browser control.

### Text

```python
{"name": "target", "env": "JACKPACK_FIELD_TARGET", "label": "Target", "type": "text", "required": True}
```

### Password

Use only for legitimate configuration secrets such as lab WiFi credentials or API tokens. Do not save password values to loot unless the user explicitly expects that for their own lab workflow.

```python
{"name": "api_key", "env": "JACKPACK_FIELD_API_KEY", "label": "API Key", "type": "password"}
```

### Number

```python
{"name": "timeout", "env": "JACKPACK_FIELD_TIMEOUT", "label": "Timeout", "type": "number", "default": 30, "min": 1, "max": 3600}
```

### Textarea

```python
{"name": "targets", "env": "JACKPACK_FIELD_TARGETS", "label": "Targets", "type": "textarea", "rows": 5}
```

### Checkbox

```python
{"name": "authorized", "env": "JACKPACK_AUTHORIZED", "label": "Authorized test", "type": "checkbox", "required": True}
```

### Select

Plain choices:

```python
{"name": "mode", "env": "JACKPACK_FIELD_MODE", "label": "Mode", "type": "select", "choices": ["quick", "full"]}
```

Labelled choices:

```python
{
    "name": "profile",
    "env": "JACKPACK_FIELD_PROFILE",
    "label": "Profile",
    "type": "select",
    "choices": [
        {"value": "passive", "label": "Passive", "description": "Listen and collect metadata"},
        {"value": "inventory", "label": "Inventory", "description": "Enumerate approved targets"},
    ],
    "default": "passive",
}
```

### Interface

WiFi payloads should default to the external adapter:

```python
{
    "name": "iface",
    "env": "JACKPACK_SELECTED_IFACE",
    "label": "WiFi Adapter",
    "type": "interface",
    "iface_type": "wifi",
    "default": "wlan1",
    "required": True,
    "allow_control_iface": False,
}
```

Wired payloads should use the Pi 5 Ethernet port:

```python
{
    "name": "iface",
    "env": "JACKPACK_SELECTED_IFACE",
    "label": "Ethernet",
    "type": "interface",
    "iface_type": "wired",
    "default": "eth0",
    "required": True,
}
```

## Launch Safety

The WebUI shows an authorized-use warning before every payload launch by default. Operators can disable that reminder in Settings, but native payloads that perform security testing should still include an explicit authorization checkbox and call `ctx.require_authorized()` at runtime.

## Runtime API

Import the runtime helper:

```python
from packjack.payload_engine import PayloadContext
```

Create context:

```python
ctx = PayloadContext("payload_name")
```

Read fields:

```python
target = ctx.env("JACKPACK_FIELD_TARGET")
enabled = ctx.bool_env("JACKPACK_FIELD_SAVE_OUTPUT")
```

Check authorization:

```python
ctx.require_authorized()
```

Protect the phone AP:

```python
iface = ctx.selected_iface("wlan1")
ctx.ensure_not_control_iface(iface)
```

Check tools:

```python
ctx.require_tools(["iw", "nmap"])
```

Run tools and stream output:

```python
result = ctx.run(["nmap", "-oX", str(ctx.loot_dir / "scan.xml"), target], check=False)
```

Save loot:

```python
ctx.write_json("summary.json", {"target": target, "returncode": result.returncode})
ctx.write_text("stdout.txt", result.stdout)
ctx.write_jsonl("events.jsonl", {"event": "scan_complete"})
```

Long running payloads:

```python
while running:
    ctx.heartbeat("listening", 1.0)
```

## Domain Patterns

These are implementation patterns for authorized workflows. Keep payload language specific and user-facing. Avoid generic “attack” labels when the actual job is inventory, validation, lab simulation, capture analysis, or configuration testing.

### WiFi

Use `wlan1` unless the user deliberately chooses another non-control adapter. WebUI controls should expose adapter, channel/profile, target selection, timeout, and output options. Prefer scanner-first flows where the UI scans, lists networks, and lets the user choose authorized lab targets.

Good native patterns:

- AP inventory and channel survey.
- Kismet collection launcher for owned test space.
- Lab captive portal simulation with clear authorization gates and safe loot handling.
- Handshake or capture file analysis when the user supplies their own capture.
- Adapter diagnostics: monitor mode support, driver, injection self-test in a lab.

### Ethernet

Use `eth0` by default. Expose target CIDR, scan profile, timeout, output format, and whether to save XML/JSON/text. Always make target scope explicit.

Good native patterns:

- Nmap inventory.
- Service/version reporting.
- DHCP/DNS diagnostics.
- ARP table and gateway discovery.
- Authorized vulnerability scanner wrappers that save reports.

### SDR

Expose device, frequency, sample rate, gain, duration, decoder/profile, and output path. Validate tools before launch and keep captures in loot.

Good native patterns:

- `rtl_433` sensor decoding in a lab.
- HackRF/RTL-SDR diagnostics.
- Spectrum snapshots.
- Capture-to-file workflows for later analysis.

### Bluetooth

Expose adapter, scan duration, passive/active mode where applicable, and output format. Keep workflows focused on discovery and owned-device assessment.

Good native patterns:

- Device inventory.
- BLE advertisement logging.
- Known-device presence checks in a lab.

### CCTV And IoT

Expose scope, ports, protocol profile, auth mode if the user is testing their own devices, and report output. Do not add default credential stuffing or unauthorized access flows.

Good native patterns:

- Owned camera inventory.
- RTSP/ONVIF discovery where authorized.
- Firmware/version reporting.
- Screenshot/report generation only when the user has credentials or explicit authorization.

### Capture Analysis And Cracking

Prefer offline analysis workflows. The user should provide capture files or select loot from previous authorized runs. Expose wordlist/profile selectors carefully and save reports, not secrets.

Good native patterns:

- PCAP summaries.
- Handshake quality checks.
- Hash format detection.
- Lab password-audit wrappers where scope and authorization are explicit.

## Porting From RaspyJack

1. Read the old script and identify its real workflow.
2. Write down every LCD screen, button choice, and hidden default.
3. Convert those choices into `JACKPACK_FORM` fields.
4. Replace hardcoded interfaces with `JACKPACK_SELECTED_IFACE`, `JACKPACK_ATTACK_IFACE`, or `JACKPACK_WIRED_IFACE`.
5. Use `ctx.ensure_not_control_iface()` before any WiFi operation.
6. Replace print-only artifacts with structured loot files.
7. Make stop behavior graceful: handle `KeyboardInterrupt`, clean up child processes, restore interfaces when needed.
8. Test on the Pi 5 hardware layout before exposing it as native.

## Quality Bar

Before a payload is considered native:

- It launches from the WebUI without raw args.
- It has clear required fields and helpful labels.
- It streams progress in plain language.
- It writes useful loot.
- It does not break the JackPack AP.
- It fails early when tools are missing.
- It handles stop/interrupt cleanly.
- It has no LCD/button dependency.
- It has a focused README note or docstring.

## AI Agent Checklist

When an AI agent creates or ports a payload, it should produce:

- One file in `payloads/jackpack/`.
- A literal `JACKPACK_FORM` with all setup fields.
- Runtime code using `PayloadContext`.
- Tool declarations in `requirements.tools` and matching `ctx.require_tools()`.
- Interface protection for WiFi workflows.
- Loot writes for final output.
- No credential theft, persistence, stealth, destructive behavior, or unauthorized access flow.
- A short note in the final response explaining how to test it from the WebUI.

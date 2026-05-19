# JackPack Native Payloads

This folder is for WebUI-first JackPack payloads.

Legacy RaspyJack payloads stay in their original folders as porting source. They should only appear in the JackPack runtime after they have been adapted to a native form/workflow model. Native payloads define a static `JACKPACK_FORM` so the WebUI can render setup controls without importing or executing the payload.

## Native Payload Shape

A native payload has two parts:

- `JACKPACK_FORM`: a literal Python dictionary that describes the WebUI form.
- `PayloadContext`: the runtime helper from `packjack.payload_engine` for logs, tool checks, command execution, interface safety, and loot files.

Keep `JACKPACK_FORM` literal. The server parses it with `ast`, which keeps the payload list fast and avoids running payload code just to draw a form.

```python
#!/usr/bin/env python3
"""Short payload description."""

from packjack.payload_engine import PayloadContext

JACKPACK_FORM = {
    "mode": "form",
    "title": "Example Survey",
    "raw_args": False,
    "fields": [
        {
            "name": "iface",
            "env": "JACKPACK_SELECTED_IFACE",
            "label": "WiFi Adapter",
            "type": "interface",
            "iface_type": "wifi",
            "default": "wlan1",
            "required": True,
            "allow_control_iface": False,
        },
        {
            "name": "target",
            "env": "JACKPACK_FIELD_TARGET",
            "label": "Target",
            "type": "text",
            "required": True,
        },
        {
            "name": "mode",
            "env": "JACKPACK_FIELD_MODE",
            "label": "Mode",
            "type": "select",
            "choices": [
                {"value": "quick", "label": "Quick"},
                {"value": "full", "label": "Full"},
            ],
            "default": "quick",
        },
    ],
    "requirements": {"tools": ["iw"]},
    "meta": {
        "description": "Example native JackPack workflow.",
        "tags": ["jackpack-native", "wifi"],
        "headless": "native",
    },
}


def main():
    ctx = PayloadContext("example_survey")
    iface = ctx.selected_iface()
    ctx.ensure_not_control_iface(iface)
    ctx.require_tools(["iw"])
    ctx.log(f"Using {iface}")
    ctx.write_json("result.json", {"iface": iface})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Field Types

Supported form controls:

- `text`, `password`, `email`, `url`
- `number`
- `textarea`
- `checkbox`
- `select` with string choices or `{value, label, description}` objects
- `interface` for protected Pi interface selection

Useful field keys:

- `name`: stable field id.
- `env`: environment variable passed to the payload.
- `label`: UI label.
- `help`: short helper text.
- `required`: validate before launch.
- `default`: initial value.
- `choices`: select options.
- `iface_type`: `wifi`, `wired`, or omitted.
- `allow_control_iface`: keep this `False` for payloads so the JackPack AP stays online.

## Runtime Helpers

`PayloadContext` gives payloads a consistent runtime:

- `ctx.env()` and `ctx.bool_env()` read WebUI fields.
- `ctx.selected_iface()` reads the chosen payload interface.
- `ctx.ensure_not_control_iface()` protects the phone AP.
- `ctx.require_tools()` fails early when a required binary is missing.
- `ctx.run()` executes tools, streams output, and writes command summaries to loot.
- `ctx.write_json()`, `ctx.write_jsonl()`, and `ctx.write_text()` save structured loot.
- `ctx.heartbeat()` updates status files for long-running workflows.

## Porting Rules

Port one RaspyJack payload at a time. Replace LCD menus with explicit WebUI fields, selectors, and buttons. Replace button navigation with direct actions. Put target selection, interface selection, and payload options at the top of the form. Stream progress to stdout so the live output stays useful, and save final artifacts under `loot/jackpack/<payload>/<event>/` through `PayloadContext`.

Do not present a legacy payload as native until its setup, live output, stop behavior, interface handling, and loot output are actually tested on the Pi 5 target layout.

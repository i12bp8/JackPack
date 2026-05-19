#!/usr/bin/env python3
"""Hidden template for JackPack native payload ports."""

from packjack.payload_engine import PayloadContext

JACKPACK_FORM = {
    "mode": "form",
    "title": "Template Payload",
    "raw_args": False,
    "fields": [
        {
            "name": "iface",
            "env": "JACKPACK_SELECTED_IFACE",
            "label": "Payload Interface",
            "type": "interface",
            "iface_type": "wifi",
            "default": "wlan1",
            "required": True,
            "allow_control_iface": False,
            "help": "Use the external adapter. Do not use the JackPack phone AP.",
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
        {
            "name": "authorized",
            "env": "JACKPACK_AUTHORIZED",
            "label": "Authorized test",
            "type": "checkbox",
            "required": True,
            "help": "Confirm you have explicit permission for this workflow.",
        },
    ],
    "requirements": {"tools": []},
    "meta": {
        "description": "Copy this file when porting a RaspyJack payload to JackPack native UI.",
        "tags": ["jackpack-native", "template"],
        "headless": "native",
    },
}


def main():
    ctx = PayloadContext("template_payload")
    ctx.require_authorized()
    iface = ctx.selected_iface()
    ctx.ensure_not_control_iface(iface)
    ctx.log(f"Selected interface: {iface}")
    ctx.write_json("input.json", {
        "iface": iface,
        "target": ctx.env("JACKPACK_FIELD_TARGET"),
        "mode": ctx.env("JACKPACK_FIELD_MODE", "quick"),
    })
    ctx.heartbeat("complete", 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

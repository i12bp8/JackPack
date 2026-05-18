# JackPack WebUI

The WebUI is the primary JackPack interface.

## Access

After installation, open `http://jackpack.local:8080` from a device connected to the JackPack AP. If mDNS is unavailable on the client, use `http://10.66.0.1:8080`.

## Entry Points

- `index.html`: phone-first control deck.
- `ide.html`: payload editor.
- `wardriving.html`: wardriving session viewer.
- `pcap.html` / `pcap-analyzer.html`: packet capture tools.

## Backend APIs

Served by `web_server.py`:

- `/api/headless/status`
- `/api/system/status`
- `/api/system/update-status`
- `/api/system/update`
- `/api/network/status`
- `/api/network/scan`
- `/api/network/connect`
- `/api/network/disconnect`
- `/api/payloads/list`
- `/api/payloads/schema`
- `/api/payloads/start`
- `/api/payloads/stop`
- `/api/payloads/status`
- `/api/payloads/log`
- `/api/loot/*`
- `/api/settings/runtime`
- `/api/auth/*`

WebSocket features are served by `device_server.py`.

## Design Direction

The control deck should stay phone-first and headless-first. Avoid adding new
LCD-emulator workflows. Legacy compatibility belongs in backend shims; the WebUI
should use direct API controls, launch forms, logs, loot browsers, and readable
status panels.

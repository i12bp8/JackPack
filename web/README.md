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
- `/api/payloads/list`
- `/api/payloads/start`
- `/api/payloads/stop`
- `/api/payloads/status`
- `/api/payloads/log`
- `/api/loot/*`
- `/api/auth/*`

WebSocket features are served by `device_server.py`.

## Design Direction

The control deck should stay phone-first and headless-first. Avoid adding new
LCD-emulator workflows as the main path. Legacy frame/input compatibility can
remain available for payloads that still need it, but new features should use
direct API controls and readable status panels.


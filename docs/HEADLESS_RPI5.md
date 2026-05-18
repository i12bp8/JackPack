# JackPack: Raspberry Pi 5 Headless Fork

JackPack is the Pi 5-first, headless direction for RaspyJack.

The design target is:

- Raspberry Pi 5 in a bag or field case.
- Built-in Ethernet for wired work.
- Built-in WiFi pinned to `wlan0` and used only for the phone-control access point.
- External USB WiFi pinned to `wlan1` and reserved for payloads that need monitor mode, injection, or client operations.
- Browser-first control surface, no LCD/button emulation as the primary workflow.

## Runtime Layout

- `web_server.py` serves the WebUI and API.
- `device_server.py` serves WebSocket features such as terminal, input, and streamed frames.
- `packjack/payload_runner.py` starts/stops payloads directly in headless mode.
- `payloads/` remains compatible with upstream RaspyJack payloads.
- `deploy/systemd/` contains the Pi 5 services.
- `deploy/network/packjack-ap.sh` configures the onboard WiFi AP through NetworkManager.

## Interface Policy

`wlan0` is control-plane only. It hosts the AP your phone connects to.

`wlan1` is payload-plane only. New WiFi payloads should default to `JACKPACK_ATTACK_IFACE`, falling back to `PACKJACK_ATTACK_IFACE` and then `wlan1`.

`eth0` is the Pi 5 built-in Ethernet port and is the default wired target
interface. Override it with `JACKPACK_WIRED_IFACE` only for unusual hardware.

## Payload Porting Rules

- Keep payloads in `payloads/<category>/<name>.py`.
- Put reusable logic in `payloads/_*.py`, `extensions/`, or a small module under `packjack/`.
- Use `payloads._input_helper.get_button()` for cancel/confirm flows.
- Treat `KEY3` as cancel/stop for LCD-compatible payloads.
- Avoid direct assumptions that `wlan0` is available for attack mode.
- Avoid direct assumptions that wired work needs an Ethernet HAT. Prefer
  `JACKPACK_WIRED_IFACE`, falling back to `eth0`.
- Write outputs to `loot/<feature>/` so the WebUI can browse them.

## Installer

```bash
sudo -i
git clone <your-fork-url> /root/JackPack
cd /root/JackPack
chmod +x scripts/install_packjack_rpi5.sh
./scripts/install_packjack_rpi5.sh
reboot
```

The installer prompts for:

- Control AP SSID and WPA2 password.
- Onboard/control AP interface, normally `wlan0`.
- External/payload WiFi interface, normally `wlan1`.
- Built-in wired target interface, normally `eth0`.
- Friendly local hostname, normally `jackpack` for `jackpack.local`.
- AP address/CIDR, channel, WebUI port, and WebSocket port.

It writes `/etc/packjack/packjack.env`, syncs the project to `/root/JackPack`
by default, configures Avahi/mDNS for `jackpack.local`, installs the
`packjack-*` systemd services, and enables stable WiFi interface naming. When needed, it creates `/root/Raspyjack` as a compatibility
link to the JackPack install directory so legacy payload paths still resolve.

For scripted rebuilds:

```bash
chmod +x scripts/install_packjack_rpi5.sh
sudo ./scripts/install_packjack_rpi5.sh \
  --non-interactive \
  --ssid JackPack \
  --password 'change-this-jackpack-pass' \
  --ap-iface wlan0 \
  --attack-iface wlan1 \
  --wired-iface eth0 \
  --hostname jackpack \
  --start-now
```

After boot, connect your phone to the configured AP and open:

```text
http://jackpack.local:8080
# fallback: http://10.66.0.1:8080
```

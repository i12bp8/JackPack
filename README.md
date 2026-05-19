# JackPack

<p align="center">
  <img alt="JackPack logo" src="docs/assets/jackpacklogo.png" width="180">
</p>

<p align="center">
  <strong>Headless Raspberry Pi 5 field toolkit forked from RaspyJack</strong><br>
  <sub>Phone-first WebUI • Pi 5 networking • Authorized red-team workflows</sub>
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg">
  <img alt="Platform: Raspberry Pi 5" src="https://img.shields.io/badge/Platform-Raspberry%20Pi%205-c51a4a?logo=raspberrypi&logoColor=white">
  <img alt="Interface: Headless WebUI" src="https://img.shields.io/badge/Interface-Headless%20WebUI-111827">
  <img alt="URL: jackpack.local" src="https://img.shields.io/badge/URL-jackpack.local-22c55e">
</p>

<p align="center">
  <strong>Open the deck from your phone at <code>http://jackpack.local:8080</code></strong><br>
  <sub>Fallback on the control AP: <code>http://10.66.0.1:8080</code></sub>
</p>

## Overview

JackPack is a Raspberry Pi 5-first, headless fork of **RaspyJack**. It keeps the payload ecosystem, but removes the Pi Zero handheld/LCD workflow as the primary product. The target build is a Pi 5 in a backpack or field case, powered by a battery, controlled from a phone over the Pi's internal WiFi access point, and using the Pi 5 Ethernet port plus an external USB WiFi adapter for authorized testing work.

The goal is simple: no tiny screen, no button choreography, no web page pretending to be an LCD. JackPack is a clean control deck for a headless Pi 5.

> [!IMPORTANT]
> JackPack is intended only for systems, networks, labs, and client environments where you have explicit authorization. I do not condone illegal use, unauthorized access, vandalism, credential theft, disruption, or misuse of this project.

## Hardware Target

- **Raspberry Pi 5** running Raspberry Pi OS Lite.
- **Internal WiFi / `wlan0`:** JackPack control AP for your phone.
- **External USB WiFi / `wlan1`:** payload WiFi adapter for monitor, injection, client, and AP workflows.
- **Built-in Ethernet / `eth0`:** wired target-network interface.
- **Power bank or field battery.**
- **No LCD HAT, no Ethernet HAT, no physical buttons required.**

## Features

- **Phone-first WebUI:** modern headless dashboard for launch/status/logging.
- **Connect panel:** scan from internal or external WiFi, join open or passworded networks, and protect the control AP from accidental disconnects.
- **Friendly local URL:** installer sets up `jackpack.local` with Avahi/mDNS.
- **Direct payload runtime:** start, configure, stop, and inspect payloads without simulating LCD buttons.
- **Payload form engine:** payloads can expose structured launch fields through `JACKPACK_FORM`; JackPack also auto-detects common `argparse` options.
- **Pi 5 interface policy:** `wlan0` stays control-only, `wlan1` stays payload WiFi, `eth0` stays wired target.
- **Payload compatibility:** legacy display/input imports are quarantined under `packjack/compat/`.
- **Loot browser:** browse runtime output and captures from the WebUI.
- **Nmap visualization:** inspect scan output from the browser.
- **Mobile wardriving map:** clustered map and phone-friendly network list.
- **Browser terminal:** on-demand WebSocket shell bridge for field control.
- **WebUI updater:** pull the latest `origin/main` from the browser, then restart the WebUI.
- **Field diagnostics:** browser-based checks for services, dependencies, interfaces, config, auth, and Git readiness.
- **Clean installer:** interactive or scripted setup for AP name, AP password, hostname, ports, and interface roles.

## Getting Started

From a fresh Raspberry Pi OS Lite install on the Pi 5:

```bash
sudo apt update
sudo apt install -y git
sudo -i
git clone https://github.com/i12bp8/JackPack.git /root/JackPack
cd /root/JackPack
chmod +x scripts/install_packjack_rpi5.sh
./scripts/install_packjack_rpi5.sh
reboot
```

After reboot:

1. Connect your phone to the JackPack AP.
2. Open `http://jackpack.local:8080`.
3. If `.local` does not resolve on your phone, use `http://10.66.0.1:8080`.

For a fully scripted install:

```bash
chmod +x scripts/install_packjack_rpi5.sh
sudo ./scripts/install_packjack_rpi5.sh \
  --non-interactive \
  --ssid JackPack \
  --password 'change-this-jackpack-pass' \
  --hostname jackpack \
  --ap-iface wlan0 \
  --attack-iface wlan1 \
  --wired-iface eth0 \
  --ap-address 10.66.0.1/24
```

## Installer

The installer configures the Pi 5 for the intended JackPack layout:

- Installs NetworkManager, Avahi/mDNS, Python dependencies, wireless tooling, and common payload utilities.
- Writes `/etc/packjack/packjack.env`.
- Sets the local hostname, defaulting to `jackpack`, so the WebUI is reachable at `jackpack.local`.
- Configures the internal WiFi as the control AP.
- Pins onboard WiFi to `wlan0` and the first USB WiFi adapter to `wlan1`.
- Enables `packjack-ap.service`, `packjack-web.service`, `packjack-ws.service`, and `packjack-pin-wifi.service`.
- Creates `/root/Raspyjack -> /root/JackPack` when needed so older payloads with hardcoded upstream paths still resolve.

## Runtime Services

- `packjack-ap.service`: configures the onboard WiFi AP.
- `packjack-web.service`: serves the WebUI and HTTP API.
- `packjack-ws.service`: serves terminal/input/frame WebSocket features.
- `packjack-pin-wifi.service`: keeps Pi 5 WiFi interface names stable at boot.

## WebUI Controls

- **Dashboard:** payload launchpad, active payload state, logs, and on-demand terminal.
- **Connect:** pick `wlan0` or `wlan1`, scan nearby WiFi, connect to open or secured networks, and disconnect safely. JackPack blocks control-AP changes unless you explicitly allow them.
- **Config:** edit AP SSID, AP password, hostname, interface roles, and service ports from the browser.
- **Updater:** fast-forward pull from GitHub, optionally re-apply JackPack services, and restart the WebUI after updating.
- **Diagnostics:** run a field-readiness check before an engagement or after swapping adapters.

## Project Layout

```text
packjack/                 Headless runtime modules and compatibility shims
web/                      JackPack WebUI
payloads/                 RaspyJack-compatible payload collection
extensions/               Reusable payload gates/actions
wifi/                     WiFi/interface helper modules
vendor/                   Third-party tools used by payloads
deploy/systemd/           JackPack services
deploy/network/           Onboard AP setup
config/                   Example runtime configuration
loot/                     Runtime output; ignored except bundled wordlists
```

## Payload Porting Rules

- Keep payloads in `payloads/<category>/<name>.py`.
- Put shared helpers in `payloads/_*.py`, `extensions/`, or `packjack/`.
- Use `JACKPACK_ATTACK_IFACE`, then `PACKJACK_ATTACK_IFACE`, then `wlan1` for WiFi payload work.
- Use `JACKPACK_WIRED_IFACE`, then `eth0` for wired payload work.
- Do not use `wlan0` for attacks; it is the phone-control AP.
- Write output under `loot/<feature>/` so the WebUI can browse it.
- Prefer non-interactive CLI/API behavior. If a legacy payload still expects LCD/buttons, keep it compatible through `packjack.compat` and mark it as compat.
- Add a `JACKPACK_FORM = {...}` dictionary or normal `argparse` options when a payload needs user input; the WebUI turns those into launch fields automatically.

## FAQ

**Why not keep the LCD files in the root?**

Because JackPack is headless. Legacy compatibility lives in `packjack/compat/`; the root should describe the product, not the old hardware.

**Does `jackpack.local` always work on phones?**

It works on many systems through mDNS/Avahi. If your phone does not resolve `.local`, use the fallback AP address: `http://10.66.0.1:8080`.

**Can I still port upstream RaspyJack payloads?**

Yes. Keep them under `payloads/`, use the JackPack interface environment variables, and avoid assuming LCD hardware or Pi Zero add-on boards.

**Why does the default install run services as root?**

Some payloads need raw sockets, monitor mode, packet injection, interface changes, and privileged network tooling. The installer keeps the default simple for a dedicated field Pi, while WebUI authentication and the control AP limit casual access. A future hardening pass can split the WebUI into a non-root service with narrow privileged helpers.

## Credits

JackPack is based on the original **RaspyJack** project by **7h30th3r0n3** and contributors. This fork changes the product direction toward a clean Raspberry Pi 5 headless workflow while preserving as much payload compatibility as practical.

## Disclaimer

> [!CAUTION]
> **STRICTLY FOR AUTHORIZED SECURITY TESTING AND RESEARCH**
>
> JackPack is an independent project intended for authorized red teaming, internal security testing, lab research, education, and work on systems and networks you own or have explicit written permission to assess.
>
> I do **not** condone, encourage, or authorize illegal activity or misuse of this project. Do not use JackPack for unauthorized access, credential theft, persistence on systems you do not own, network disruption, surveillance, vandalism, fraud, or harm of any kind.
>
> You are solely responsible for how you use this software and for complying with all applicable laws, contracts, policies, and rules of engagement. The creator and contributors assume no liability for misuse, damage, legal consequences, or third-party claims arising from this project.

## License

Licensed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

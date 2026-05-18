#!/usr/bin/env bash
set -euo pipefail

AP_IFACE="${JACKPACK_AP_IFACE:-${PACKJACK_AP_IFACE:-wlan0}}"
AP_SSID="${JACKPACK_AP_SSID:-${PACKJACK_AP_SSID:-JackPack}}"
AP_PASSWORD="${JACKPACK_AP_PASSWORD:-${PACKJACK_AP_PASSWORD:-jackpack-change-me}}"
AP_ADDRESS="${JACKPACK_AP_ADDRESS:-${PACKJACK_AP_ADDRESS:-10.66.0.1/24}}"
AP_CHANNEL="${JACKPACK_AP_CHANNEL:-${PACKJACK_AP_CHANNEL:-6}}"
CONNECTION_NAME="${JACKPACK_AP_CONNECTION:-${PACKJACK_AP_CONNECTION:-jackpack-ap}}"

if [ "${#AP_PASSWORD}" -lt 8 ]; then
  echo "JACKPACK_AP_PASSWORD must be at least 8 characters" >&2
  exit 2
fi

if ! command -v nmcli >/dev/null 2>&1; then
  echo "NetworkManager/nmcli is required for JackPack AP mode" >&2
  exit 2
fi

nmcli radio wifi on || true
nmcli connection delete "$CONNECTION_NAME" >/dev/null 2>&1 || true
nmcli connection add type wifi ifname "$AP_IFACE" con-name "$CONNECTION_NAME" autoconnect yes ssid "$AP_SSID"
nmcli connection modify "$CONNECTION_NAME" \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  802-11-wireless.channel "$AP_CHANNEL" \
  ipv4.method shared \
  ipv4.addresses "$AP_ADDRESS" \
  ipv6.method disabled \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "$AP_PASSWORD"
nmcli connection up "$CONNECTION_NAME"

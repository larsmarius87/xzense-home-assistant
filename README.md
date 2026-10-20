# Xzense Alpha

Experimental Home Assistant custom integration for **Exodraft Xzense** over Bluetooth LE.

Current version: **0.5.2 Alpha**.

The core BLE session, authentication, live status decoding and selected controls are working against a real Xzense system. Protocol mapping is still in progress, so several settings remain intentionally raw or disabled.

The Home Assistant domain remains `xzense_full_preview` for compatibility with existing installations. The user-facing name is now **Xzense Alpha**.

## Confirmed so far

- BLE discovery and connection to the Xzense control panel
- PIN/session authentication
- Live operating state and state timer
- Chimney, inside and outside temperatures
- Air pressure
- Actual fan speed
- Firmware version from CONNECT ACK (`410` -> `4.10`)
- Boost on/off
- GLOBAL `0x50` = fan speed setpoint, direct %
- GLOBAL `0x54` = minimum fan voltage, direct V; observed at 80 V and 105 V
- GLOBAL `0x34` = contrast, strong live match

## 0.5.2 corrections

- `0x50` is **Fan speed setpoint**, not Boost fan speed.
- `0x52` is currently unidentified.
- `0x54` is **Minimum fan voltage**.
- `0x55` is currently unidentified.
- `0x33` is not direct Sound/Volume.
- The user-facing integration name is now **Xzense Alpha**.

## Source package

The complete tested 0.5.2 source package is committed in this private repository as:

`xzense-alpha-0.5.2-source.zip`

The package contains the full `custom_components/xzense_full_preview/` integration, tests, protocol notes and protocol manifest.

## Tests

Local regression suite: **30 passed**.

## Disclaimer

Unofficial reverse-engineered integration. Not affiliated with or endorsed by Exodraft.

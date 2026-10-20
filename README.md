# Xzense Alpha

Experimental Home Assistant custom integration for **Exodraft Xzense** over Bluetooth LE.

Current integration version: **0.5.5 Alpha**. This release is built from the preserved **0.5.3 Alpha** source baseline. The discarded 0.5.4 regression build is not used as source.

> The Home Assistant domain remains `xzense_full_preview` for compatibility with existing installations. The user-facing name remains **Xzense Alpha**.

## Working now

- BLE discovery and connection to the Xzense control panel
- Xzense PIN/session authentication
- Temporary **Release Bluetooth to app** helper from 0.5.3
- Live operating state and state timer
- Chimney, inside and outside temperatures
- Air pressure
- Actual fan speed
- Firmware version from CONNECT ACK (`410` -> `4.10`)
- Power source (`0x05`: Battery / External power)
- Boost on/off (`0x08`)
- Sound (`0x32`)
- Contrast (`0x33`)
- Brightness (`0x34`)
- Start temperature (`0x4B`)
- Stop temperature (`0x4C`)
- Boost time (`0x4D`)
- Afterrun time (`0x4E`)
- Boost speed (`0x4F`)
- Boost stop temperature (`0x52`)
- Chimney draught setpoint (`0x53`)
- Minimum fan voltage (`0x54`)

## 0.5.5 live mapping correction

A direct comparison between the physical Xzense controller and GLOBAL values established the following block:

| GLOBAL | Setting | Live value example |
|---:|---|---:|
| `0x32` | Sound | 24 -> 24 % |
| `0x33` | Contrast | 75 -> 75 % |
| `0x34` | Brightness | 68 -> 68 % |
| `0x4B` | Start temperature | 502 -> 50.2 °C |
| `0x4C` | Stop temperature | 398 -> 39.8 °C |
| `0x4D` | Boost time | 900 s -> 15 min |
| `0x4E` | Afterrun time | 1800 s -> 30 min |
| `0x4F` | Boost speed | 100 -> 100 % |
| `0x52` | Boost stop temperature | 600 -> 60.0 °C |
| `0x53` | Chimney draught setpoint | 26 -> 26 Pa |
| `0x54` | Minimum fan voltage | 105 -> 105 V |

`0x35`, `0x36`, `0x50`, `0x51` and `0x55` remain unidentified and are exposed only as disabled diagnostic raw sensors. The previous 0.5.3 interpretation of `0x50` as a writable fan-speed setpoint is **not** carried forward.

## Power source

GLOBAL `0x05` was physically A/B tested:

- `2` = **Battery**
- `3` = **External power**

The integration deliberately says *External power*, not *Charging*, because charge state itself has not been proven.

## Operating-state mapping

| Raw | State |
|---:|---|
| 2 | Ready for lighting |
| 3 | Boosting |
| 4 | Operation |
| 5 | Refueling |
| 6 | Afterrun |

## Setting ranges and scaling

The GLOBAL ID/scaling map comes from live controller correlation. Home Assistant ranges for Sound, Contrast, Brightness, Start/Stop temperature, Boost/Afterrun time, Boost speed, chimney draught and minimum fan voltage follow the published Xzense manual. Temperatures are converted from tenths of a degree and timer values from seconds to minutes.

Boost-stop temperature is live-correlated (`600 = 60.0 °C`), but the manual does not publish an explicit adjustment range; Alpha 0.5.5 therefore uses a conservative HA UI bound while leaving the controller to validate the write.

## Still locked / pending

Start Fire, Stop Fire, Refueling and Ventilation remain unavailable until their exact packet payloads are verified. System Control, Temperature sensor, External start and the `0x59`-`0x5B` candidates remain non-writable.

## Installation

Copy:

```text
custom_components/xzense_full_preview/
```

into:

```text
/config/custom_components/xzense_full_preview/
```

Restart Home Assistant and reload/add **Xzense Alpha**.

## Repository notes

- `PROTOCOL_NOTES.md` contains packet-level findings and chronology.
- `PROTOCOL_MANIFEST.md` is the current GLOBAL/packet source of truth.
- `FEATURE_MATRIX.md` tracks Home Assistant exposure and confidence.
- `tests/` contains protocol and regression tests that do not require a live Xzense device.

## Safety / scope

This is an unofficial reverse-engineered integration and is not affiliated with or endorsed by Exodraft. Destructive operations such as factory reset and network reset are intentionally not exposed.

## 0.5.5 release verification

- Baseline: recovered Xzense Alpha 0.5.3 source package
- Regression suite: **42 passed**
- `python -m compileall`: passed
- Source package: `xzense-alpha-0.5.5-source.zip`
- SHA-256: `0ce25e74b678a7462aefdda2e8ba0218e6271e1e1aaee70a078df9dd33e18ecd`
- `client.py`, `button.py` and `version.py` are byte-identical to the recovered 0.5.3 baseline; BLE connection/release and firmware-formatting code were not rewritten in 0.5.5.
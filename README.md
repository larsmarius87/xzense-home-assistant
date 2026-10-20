# Xzense Alpha

Experimental Home Assistant custom integration for **Exodraft Xzense** over Bluetooth LE.

Current integration version: **0.5.6 Alpha**. This release continues from the preserved **0.5.5 Alpha** source package; the discarded 0.5.4 regression build is not used as source.

> The Home Assistant domain remains `xzense_full_preview` for compatibility with existing installations. The user-facing name remains **Xzense Alpha**.

## Working now

- BLE discovery and connection to the Xzense control panel
- Xzense PIN/session authentication
- Temporary **Release Bluetooth to app** helper
- Live operating state and state timer
- Chimney, inside and outside temperatures
- Air pressure
- Actual fan speed
- Firmware version from CONNECT ACK (`410` -> `4.10`)
- Power source (`0x05`: Battery / External power)
- Boost on/off (`0x08`) — live verified
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

## New in 0.5.6 — firing and fan-mode controls

Static analysis of the controller firmware bundled with the official Xzense app established the control paths used by the Xzense UI. These controls are now exposed in Home Assistant while retaining controller-side ACK/NACK validation:

| Home Assistant control | Wire action | Availability / meaning |
|---|---|---|
| **Start lighting** | BOOST `0x08`, `start=1` | Only when state `2 = Ready for lighting` |
| **Refuel** | BOOST `0x08`, `start=1` | Only when state `4 = Operation` |
| **Stop firing** | BOOST `0x08`, `start=0` | In state `3 = Boosting` or `5 = Refueling` |
| **Stop firing** | GLOBAL `0x19 = 6` | In state `4 = Operation`; starts Afterrun |
| **Finish firing** | GLOBAL `0x19 = 6` | Explicit Operation -> Afterrun action |
| **Ventilation** | VENTILATION `0x09`, `start=0/1` | Firmware-derived; first live write on this controller still pending |
| **System control** | GLOBAL `0x56` | `0=Manual`, `1=eXotelligence`, `2=Pressure controlled` |

BOOST remains the same packet that was already physically verified. The new Refuel and Start-lighting actions deliberately reuse the firmware's state-dependent BOOST command instead of inventing new packet IDs.

The BLE connection/reconnect/session-acquisition methods are regression-locked to the tested 0.5.5 implementation. 0.5.6 changes application-level control handling only.

## 0.5.5 live mapping correction retained

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

States 3 and 6 are live verified. States 2, 4 and 5 follow the Xzense operating sequence and firmware/UI behavior; they remain less strongly evidenced than the two live-verified states.

## Setting ranges and scaling

The GLOBAL ID/scaling map comes from live controller correlation. Home Assistant ranges for Sound, Contrast, Brightness, Start/Stop temperature, Boost/Afterrun time, Boost speed, chimney draught and minimum fan voltage follow the published Xzense manual. Temperatures are converted from tenths of a degree and timer values from seconds to minutes.

Boost-stop temperature is live-correlated (`600 = 60.0 °C`), but the manual does not publish an explicit adjustment range; Alpha 0.5.6 therefore uses a conservative HA UI bound while leaving the controller to validate the write.

## Still locked / pending

Temperature sensor `0x57`, External start `0x58`, the `0x59`-`0x5B` candidates, and unidentified `0x35`, `0x36`, `0x50`, `0x51`, `0x55` remain non-writable. Destructive packet types such as factory reset are intentionally not exposed.

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

This is an unofficial reverse-engineered integration and is not affiliated with or endorsed by Exodraft. Controller ACK/NACK remains authoritative for state-dependent commands. Destructive operations such as factory reset and network reset are intentionally not exposed.
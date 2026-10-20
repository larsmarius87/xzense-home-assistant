# Xzense Alpha

Experimental Home Assistant custom integration for **Exodraft Xzense** over Bluetooth LE.

Current integration version: **0.5.7 Alpha**. This release is built directly from the tested **0.5.6 Alpha** source, which itself continues the preserved 0.5.5/0.5.3 line. The discarded 0.5.4 regression build is not used as source.

> The Home Assistant domain remains `xzense_full_preview` for compatibility with existing installations. The user-facing name remains **Xzense Alpha**.

## 0.5.7 source-of-truth update

The official **Xzense 5.0.5** app contains controller firmware `assets/flutter_assets/assets/fw/exodraft.gbl`. The image identifies itself as **v4.10_RC2**, matching the 4.10 generation reported by the user's controller. Direct UI/controller-code bindings from that firmware are used together with live 4.10 observations.

The firmware also contains an older debug-name lookup whose GLOBAL labels are shifted for several setup values. Alpha 0.5.7 therefore does **not** use that debug table alone as authoritative evidence.

## Working / mapped controls

| Home Assistant control | Xzense mapping | Confidence / gate |
|---|---|---|
| Boost on/off | packet `0x08`, start `1/0` + inside temperature | **Live verified** |
| Start lighting | packet `0x08`, start `1` | Firmware-derived; only state `2` |
| Refuel | packet `0x08`, start `1` | v4.10_RC2-derived; only state `5 = Burnout` |
| Stop firing | packet `0x08`, start `0` | states `3 = Boosting` and `7 = Refueling/Reheating` |
| Stop/finish firing | GLOBAL `0x19 = 6` | states `4 = Operation` and `5 = Burnout`; enters Afterrun |
| Ventilation | packet `0x09`, start `1/0` | Firmware-derived; first live write pending |
| Operation fan speed | GLOBAL `0x50`, direct % | Firmware + earlier physical write evidence; HA control only in state `4` |
| System control | GLOBAL `0x55` | Firmware-derived enum: `0=Manual`, `1=eXotelligence`, `2=Pressure controlled` |

The BLE discovery/reconnect/session-acquisition and **Release Bluetooth to app** methods remain regression-locked to the tested 0.5.5 implementation.

## Current GLOBAL map

| GLOBAL | Meaning | Encoding | Evidence |
|---:|---|---|---|
| `0x05` | Power source | `2=Battery`, `3=External power` | Live A/B verified |
| `0x19` | Device state | enum | Live + firmware |
| `0x1A` | Time in current state | seconds | Live verified |
| `0x1B` | Air pressure | hPa | Live verified |
| `0x1C` | Inside temperature | raw / 10 °C | Strong live mapping |
| `0x1D` | Outside temperature | raw / 10 °C | Strong live mapping |
| `0x1E` | Chimney temperature | raw / 10 °C | Live verified |
| `0x1F` | Actual fan speed | % | Live verified |
| `0x32` | Sound | direct % | Live A/B + v4.10 code |
| `0x33` | Contrast | direct % | Live + v4.10 code |
| `0x34` | Brightness | direct % | Live + v4.10 code |
| `0x4B` | Start temperature | raw / 10 °C | Live + v4.10 code |
| `0x4C` | Stop temperature | raw / 10 °C | Live + v4.10 code |
| `0x4D` | Boost time | seconds | Live + v4.10 code |
| `0x4E` | Afterrun time | seconds | Live + v4.10 code |
| `0x4F` | Boost speed | % | Live + v4.10 code |
| `0x50` | Operation/User fan speed | direct % | v4.10 UI + earlier physical probe |
| `0x51` | Actual draught | raw, scaling pending | v4.10 firmware; read-only |
| `0x52` | Boost stop temperature | raw / 10 °C | Live + v4.10 code |
| `0x53` | Chimney draught setpoint | Pa | Live + v4.10 code |
| `0x54` | Minimum fan voltage | V | Live + v4.10 code |
| `0x55` | System control | enum 0/1/2 | v4.10 direct UI binding |
| `0x56` | Temperature sensor | enum pending | v4.10 direct UI binding; read-only |
| `0x57` | External start | coding pending | v4.10 code; read-only |
| `0x58` | Alarm setpoint | scaling pending | v4.10 direct UI binding; read-only |
| `0x59` | Reboost/refire time | raw | v4.10 ID known/read-only |
| `0x5A` | External fan speed | raw | v4.10 external-start path; read-only |
| `0x5B` | Burnout timeout | raw | v4.10 ID known/read-only |

`0x35`, `0x36` and `0x20` remain unidentified. Candidate/service fields are deliberately not writable until their value coding and safe ranges are established.

## Operating states — v4.10

The v4.10_RC2 firmware contains the state-name table in this order, including the inserted `AFTERRUN` state:

| Raw | State |
|---:|---|
| `0` | Offline |
| `1` | Setup |
| `2` | Ready for lighting / firmware `IDLE` |
| `3` | Boosting |
| `4` | Operation |
| `5` | Burnout |
| `6` | Afterrun |
| `7` | Refueling / firmware `REHEATING` |
| `8` | Ventilation |
| `9` | Error |
| `10` | Upgrading |

States `3` and `6` are additionally live verified on the user's controller. The 0.5.6 assumption that state `5` was Refueling is superseded by the v4.10 firmware: state `5` is **Burnout**, while Refueling/Reheating is state `7`.

## Packet types

Known controller packet types include `0x02 CONNECT`, `0x06 GLOBAL`, `0x07 STATUS`, `0x08 BOOST`, `0x09 VENTILATION`, `0x0A RANGETEST`, `0x0B FACTORY_RESET`, `0x0C FILE_TRANSFER`, `0x0D TIMESYNC` and `0x0E CONNECTED_PEERS`. Destructive/service operations are intentionally not exposed.

## Installation

Copy `custom_components/xzense_full_preview/` into `/config/custom_components/xzense_full_preview/`, restart Home Assistant and reload/add **Xzense Alpha**.

## Repository notes

- `PROTOCOL_NOTES.md` documents evidence and chronology.
- `PROTOCOL_MANIFEST.md` is the current ID/packet source of truth.
- `FEATURE_MATRIX.md` tracks Home Assistant exposure and confidence.
- `tests/` contains protocol and regression tests that do not require a live Xzense device.

## Safety / scope

This is an unofficial reverse-engineered integration and is not affiliated with or endorsed by Exodraft. Controller ACK/NACK remains authoritative for state-dependent commands. The new v4.10-derived controls still require live validation where explicitly noted.
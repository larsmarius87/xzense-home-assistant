# Xzense Alpha

## Alpha 0.5.15 – Bluetooth proxy selection and disconnect diagnostics (22 October 2026)

**Download:** [xzense-alpha-0.5.15-source.zip](xzense-alpha-0.5.15-source.zip) – complete source code, dashboard, and tests.

- Collect fresh advertisements for 3 seconds before selecting a Bluetooth proxy, and choose using RSSI with a bounded preference for previously successful sources.
- Record the active proxy, connection RSSI, session duration, last STATUS request/response, and last 20 disconnect events.
- Separate local shutdown/setup cleanup from unexpected BLE callback; the callback does NOT tell us whether the panel, proxy, or RF path caused a disconnect.
- Keep the same PIN, Xzense commands, 10-second STATUS polling, prior entity IDs and 0.5.14 dashboard.
- 94 local tests passed, but these BLE changes are not verified with the physical device yet.
- Read [INSTALLASJON_0.5.15.md](INSTALLASJON_0.5.15.md) to verify the active custom_components folder and domain before installing.

## Alpha 0.5.14 – dashboard og temperatursensor (22. oktober 2026)

**Nedlasting:** [xzense-alpha-0.5.14-source.zip](xzense-alpha-0.5.14-source.zip) (komplett kildekode, tester og dashboard).

- Refueling («Legg på ved») tilgjengelig i Operation (state 4) og Burnout (state 5), videreført fra 0.5.12b.
- Temperaturprobe som eksperimentell På/Av-bryter via GLOBAL 0x56; mapping 0/1 er ikke fysisk bekreftet. Ikke endre under aktiv fyring.
- Dashboardkort med fem norske faner, visuell entitetsvelger og egne visningsnavn.
- Diagnostikksensorer avkorter teksttilstander til 255 tegn for å unngå Home Assistant-feilmeldinger.
- BLE-oppkobling, PIN og GATT er uendret fra 0.5.13.

**Slik installeres kortet når integrasjonsmappen heter `xzense`:** Kopier [www/xzense-card.js](www/xzense-card.js) til `/config/www/xzense-card.js`, registrer `/local/xzense-card.js?v=0514` som JavaScript-modul under **Innstillinger → Dashboard → Ressurser**, og legg til manuelt kort med `type: custom:xzense-card`. Se [dashboard/INSTALLASJON.md](dashboard/INSTALLASJON.md).

**OBS:** ZIP-arkivet er utviklingsintegrasjonen `xzense_full_preview` (domenet i manifestet). Dersom den installerte integrasjonen faktisk heter `xzense`, skal du ikke endre mappenavn eller erstatte den med `xzense_full_preview` uten å kontrollere domenet. Det separate Lovelace-kortet fungerer uavhengig av hvilket av disse domenene som brukes, ved at du velger entiteter i redigeringen.

Testet lokalt med 84 Python-tester og dashboardets JavaScript-smoketest; ikke testet på fysisk Xzense-panel.

## Alpha 0.5.13: compatibility correction to 0.5.12b

- Normalized the integration's `manifest.json` version to numeric SemVer `0.5.13` and synchronized `const.py` so Home Assistant and version checks see one release.
- No changes to BLE protocol, PIN authentication, device controls, entity IDs or runtime behavior compared with 0.5.12b.
- Retains **Refuel** availability in Operation (state 4) and Burnout (state 5), plus raw **0x05 status** / **0x18 status** sensor names.
- If Home Assistant reports the integration missing, copy the **whole** `custom_components/xzense_full_preview/` directory into `/config/custom_components/xzense_full_preview/`, replacing the previous files, then restart Home Assistant. Do not delete the existing integration/config entry. Review Settings → System → Logs if it still fails.


Experimental Home Assistant custom integration for **Exodraft Xzense** over Bluetooth LE.

Current integration version: **0.5.13 Alpha**, a small revision of **0.5.12**.

> The Home Assistant domain remains `xzense_full_preview` for compatibility with existing installations. The user-facing name remains **Xzense Alpha**.

## 0.5.12b — Refuel in Operating and raw GLOBAL status names

- **Refuel** is available in **Operating / Operation (state 4)** as well as **Burnout (state 5)**, when the existing Boost command is available. It still sends the same `BOOST/REQ 0x08 start=1` command; the result in state 4 has **not yet been physically verified**.
- The existing sensor with unique ID suffix `battery` is renamed **0x05 status** and displays the **raw integer** (e.g. `2` / `3`), without claiming it means battery or external power.
- The existing sensor with unique ID suffix `signal_strength` is renamed **0x18 status** and still displays the raw `GLOBAL 0x18` integer, without interpreting its units.
- Sensor unique IDs, BLE transport/authentication, all other controls and diagnostics remain unchanged. Home Assistant may preserve a manually customized entity name until the user resets that customization.

## 0.5.10 fan-speed availability in Ventilation (no wire-protocol change)

The live 2026-10-21 Ventilation (state 8) capture shows GLOBAL `0x50` rising from 10 to 16 in 1% steps; subsequent STATUS reported 16%. The same setpoint is used in Operation (state 4). The Home Assistant number is now named **Fan speed** and available only in state `4` or `8`, with a write-time check for the same states. The separate `0x1F` read-only sensor is now named **Actual fan speed**. Existing feature keys, unique IDs, minimum 10% and maximum 100%, and the GLOBAL write format remain unchanged. Writes in Ventilation from HA have not yet been physically tested.

## 0.5.9 deferred external controls (no wire-protocol change)

External start (GLOBAL `0x57`) and External fan speed (GLOBAL `0x5A`) have been removed from the active feature registry and HA entity exposure at the user's request. The registry cleanup from 0.5.8 still removes any old entities with these IDs. To preserve reverse-engineering evidence, both values remain in raw diagnostic GLOBAL captures and in protocol documentation. The unresolved **Power source (?)** sensor (`0x05`) stays, showing raw values as unknown until verified. Boost, Ventilation, BLE connection and all other controls are unchanged.

## 0.5.8 cleanup (no wire-protocol change)

Removed empty Burn count, Operation time and Error log entities, unmapped Language and Download log placeholders and the duplicate raw GLOBAL 0x51 entity. Candidate settings without verified writing semantics remain documented in the feature matrix and available in diagnostic GLOBAL dumps, but are no longer instantiated as unusable controls. GLOBAL 0x00-0x04 now appear as UNKNOWN rather than misleading legacy firmware debug labels. No BLE connection or control commands changed.

## 0.5.12 — configuration, source ambiguity and ChimneyLog research

- **System control** moved to Configuration. **Alarm temperature** (`0x58`) is a Configuration number with 150–400 °C range and raw-tenths scaling.
- **Refire / Reboost time** (`0x59`) and **Burnout timeout** (`0x5B`) are now editable Configuration numbers after user confirmation of panel editing. Raw seconds convert to minutes. Home Assistant exposes 0–546.1 minutes in 0.1-minute steps, using only the signed-16-bit GLOBAL transport bound; **these are not verified controller-safe limits**. HA-initiated writes await physical verification.
- Old read-only sensor entries for `0x59`/`0x5B` are removed on migration. Existing numeric settings retain their feature keys/unique IDs.
- **Actual chimney draught (raw)** sensor hidden/removed; raw `0x51` retained in the full diagnostics.
- **Power source (?)** preserves the existing sensor key (`battery`), but reports `Unknown (2)` / `Unknown (3)` instead of asserting Battery/External. The physical controller was wired while sending different raw values in consecutive diagnostics; the precise enum has not been proven. Raw remains present in diagnostics.
- [ChimneyLog investigation](CHIMNEYLOG_RESEARCH.md): confirms firmware filenames and app-side indicators but no safe request/record layout. No `FILE_TRANSFER` test commands or firmware writes are added.


## 0.5.7 source-of-truth update

The official **Xzense 5.0.5** app contains controller firmware `assets/flutter_assets/assets/fw/exodraft.gbl`. The image identifies itself as **v4.10_RC2**, matching the 4.10 generation reported by the user's controller. Direct UI/controller-code bindings from that firmware are used together with live 4.10 observations.

The firmware also contains an older debug-name lookup whose GLOBAL labels are shifted for several setup values. Alpha 0.5.7 therefore does **not** use that debug table alone as authoritative evidence.

## Working / mapped controls

| Home Assistant control | Xzense mapping | Confidence / gate |
|---|---|---|
| Boost switch | packet `0x08`, start `1/0` + inside temperature | Command live-verified, status from STATUS |
| Start lighting | packet `0x08`, start `1` | Firmware-derived; only state `2` |
| Refuel | packet `0x08`, start `1` | v4.10_RC2-derived; only state `5 = Burnout` |
| Stop firing | packet `0x08`, start `0` | states `3 = Boosting` and `7 = Refueling/Reheating` |
| Stop firing (Afterrun branch) | GLOBAL `0x19 = 6` | states `4 = Operation` and `5 = Burnout`; enters Afterrun |
| Ventilation switch | packet `0x09`, start `1/0` | Live tested; status from STATUS state 8 |
| Fan speed (setpoint) | GLOBAL `0x50`, direct 10–100 % | Observed in Operation and Ventilation; HA control available in all connected states |
| System control | GLOBAL `0x55` | Firmware-derived enum: `0=Manual`, `1=eXotelligence`, `2=Pressure controlled` |

The BLE discovery/reconnect/session-acquisition methods are preserved; the nonfunctional **Release Bluetooth to app** feature was removed in 0.5.11.

## Current GLOBAL map

| GLOBAL | Meaning | Encoding | Evidence |
|---:|---|---|---|
| `0x05` | Power source (?) | raw 2 / raw 3, meaning unverified | Contradictory readings on a wired installation |
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
| `0x50` | Fan speed setpoint (Operation + Ventilation) | direct % | v4.10 UI + live 10→16% Ventilation capture |
| `0x51` | Actual draught | raw, scaling pending | v4.10 firmware; read-only |
| `0x52` | Boost stop temperature | raw / 10 °C | Live + v4.10 code |
| `0x53` | Chimney draught setpoint | Pa | Live + v4.10 code |
| `0x54` | Minimum fan voltage | V | Live + v4.10 code |
| `0x55` | System control | enum 0/1/2 | v4.10 direct UI binding |
| `0x56` | Temperature sensor | enum pending | v4.10 direct UI binding; read-only |
| `0x58` | Alarm setpoint | scaling pending | v4.10 direct UI binding; read-only |
| `0x59` | Reboost/refire time | raw | v4.10 ID known/read-only |
| `0x5B` | Burnout timeout | raw | v4.10 ID known/read-only |

`0x57` and `0x5A` are intentionally deferred and visible only in diagnostic raw data and protocol notes. `0x00`–`0x04`, `0x20`, `0x35` and `0x36` remain unidentified. Candidate/service fields are deliberately not writable until their value coding and safe ranges are established.

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

## Alpha 0.5.11 update (2026-10-21)

- Removed non-functional Bluetooth release-to-app button, timer and associated BLE pause logic.
- Combined Boost on/off into one Boost switch; removed redundant Finish firing button. Stop firing retains its Afterrun transition through GLOBAL 0x19=6.
- Boost and Ventilation switches follow authenticated STATUS state (Boost state 3; Ventilation state 8). Boost state 7 is unresolved and retains last known value.
- Switch state is restored across HA restarts and retained across BLE reconnects until the first valid fresh STATUS frame. CONNECT/ACK immediately triggers the existing STATUS polling loop; command ACK alone does not determine switch state.
- Fan speed GLOBAL 0x50 is available in all connected states; firmware may still enforce its own restrictions.
- Controls are normal entities, configuration settings categorized CONFIG; device-page display ordering remains Home Assistant controlled.
- GitHub release source zip built from this tree; local tests do not substitute for on-device validation.
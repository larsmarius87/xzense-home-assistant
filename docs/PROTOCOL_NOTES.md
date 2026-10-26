# Xzense protocol notes — Alpha 0.5.7

## 0.5.7: direct Xzense v4.10_RC2 controller-firmware analysis

The official **Xzense 5.0.5 APK/XAPK** supplied for analysis contains:

`assets/flutter_assets/assets/fw/exodraft.gbl`

The GBL is 455,488 bytes, SHA-256 `42fafc7b51f8811f48c80a4290a83fd7823c747c12855ba3884bdf17b74b2bd6`, and identifies the controller application as **v4.10_RC2**. The user's controller reports raw CONNECT version `410`, rendered by the integration as `4.10`.

### Important: stale debug-name table

The firmware still carries a legacy GLOBAL debug-name lookup with several pre-shift labels. It is useful as historical evidence, but it conflicts with both live 4.10 observations and direct current UI bindings. Alpha 0.5.7 therefore uses this evidence order:

1. physical live A/B correlation / successful write;
2. direct v4.10_RC2 UI/controller-code binding;
3. legacy debug-name table only as supporting evidence.

Direct v4.10 code bindings include:

- `0x32` Sound
- `0x33` Contrast
- `0x34` Brightness
- `0x4F` Boost speed
- `0x50` Fan-speed setpoint (Operation + Ventilation)
- `0x52` Boost stop temperature
- `0x53` Chimney draught setpoint
- `0x54` Minimum fan voltage
- `0x55` System control
- `0x56` Temperature sensor
- `0x57` External start control path
- `0x58` Alarm setpoint
- `0x59` Reboost/refire time
- `0x5A` External fan-speed companion in the External-start path
- `0x5B` Burnout timeout

The `0x55`/`0x56` distinction is particularly important: **0x55 is System control; 0x56 is Temperature sensor**. This supersedes the 0.5.6 assumption.

### v4.10 state table

Repeated firmware state-name arrays explicitly contain the following ordered entries:

`OFFLINE, SETUP, IDLE, BOOSTING, OPERATING, BURNOUT, AFTERRUN, REHEATING, VENTILATING, ERROR_STATE, UPGRADING, UNKNOWN_STATE`

Therefore the 4.10 runtime states are:

- 0 Offline
- 1 Setup
- 2 IDLE / Ready for lighting
- 3 Boosting
- 4 Operation
- 5 Burnout
- 6 Afterrun
- 7 Reheating / user-facing Refueling
- 8 Ventilation
- 9 Error
- 10 Upgrading

State 3 Boosting and state 6 Afterrun are additionally live verified. This directly fixes the 0.5.6 state error: state 5 is **Burnout**, not Refueling; Refueling/Reheating is state 7.

### Refuel / stop / Afterrun control paths

BOOST request remains:

`08 0B | session_id_le32 | start_u8 | inside_temp_i16_le`

v4.10_RC2 reuses it by state:

- Ready/IDLE state 2 + `start=1` -> Start lighting / Boosting.
- Burnout state 5 + `start=1` -> Refueling/Reheating state 7.
- Boosting state 3 + `start=0` -> stop Boost.
- Reheating state 7 + `start=0` -> stop Reheat.

The firmware contains the user prompt `Would you like to refuel now?`, plus explicit `START Reheating`, `STOP Reheat`, `STOP Boost` and `START Afterrun` paths. The negative/finish path transitions to Afterrun with GLOBAL state 6:

`06 0B | session_id_le32 | 19 | 06 00`

Alpha 0.5.7 exposes **Finish firing** in states 4 and 5, and makes **Stop firing** context-aware.

### Fan speed setpoint

Direct v4.10 Fan Control UI code binds GLOBAL `0x50`. On 2026-10-21 in Ventilation (state 8), GLOBAL `0x50` was observed stepping 10→11→12→13→14→15→16 while the STATUS frame reported 16% fan speed; this independently confirms that the setpoint is used in Ventilation as well as Operation. Since Alpha 0.5.10, the HA **Fan speed** number is available in states 4 (Operation) and 8 (Ventilation), with the same GLOBAL write encoding and an additional write-time state check. Actual speed is read from STATUS or GLOBAL `0x1F` and labelled **Actual fan speed**. A HA-initiated write in Ventilation still requires physical testing.

This is not Boost speed. Boost speed is independently live-correlated and directly bound to GLOBAL `0x4F`.

### System control

Direct v4.10 `SystemManager` UI code binds the mode to GLOBAL `0x55`. The recovered options are:

- `0 = Manual`
- `1 = eXotelligence`
- `2 = Pressure controlled`

The write path is firmware-derived and awaits first deliberate live validation on this controller.

### Ventilation

Packet `0x09` is VENTILATION. Request payload:

`09 0B | session_id_le32 | start_u8`

where 1=start and 0=stop. The controller applies its own state checks and ACK/NACK response. Alpha 0.5.7 uses the ACK-confirmed last command as the HA switch state because an independent live ventilation-state field has not yet been mapped.

## Retained live 4.10 correlations

Physical-panel/live diagnostics established:

- `0x05`: power source **unverified**. Raw 2 and 3 were observed despite a reportedly hardwired controller; previous Battery/External interpretation is no longer treated as conclusive.
- `0x19`: device state; state 3 Boosting and state 6 Afterrun live verified.
- `0x1A`: state timer seconds.
- `0x1B`: air pressure hPa.
- `0x1C`: inside temperature /10 °C.
- `0x1D`: outside temperature /10 °C.
- `0x1E`: chimney temperature /10 °C.
- `0x1F`: actual fan speed %.
- `0x32`: Sound, direct; intentional panel 12 -> 24 produced raw 12 -> 24.
- `0x33`: Contrast; panel 75 matched raw 75.
- `0x34`: Brightness; panel 68 matched raw 68.
- `0x4B`: Start temperature; 502 = 50.2 °C.
- `0x4C`: Stop temperature; 398 = 39.8 °C.
- `0x4D`: Boost time; 900 s = 15 min.
- `0x4E`: Afterrun time; 1800 s = 30 min.
- `0x4F`: Boost speed; 100 = 100 %.
- `0x52`: Boost stop temperature; 600 = 60.0 °C.
- `0x53`: chimney draught setpoint; 26 = 26 Pa.
- `0x54`: minimum fan voltage; observed at 80 V and 105 V.

Latest known tail values included `0x50=10`, `0x51=0`, `0x55=0`, `0x56=1`, `0x57=1`, `0x58=2500`, `0x59=180`, `0x5A=0`, `0x5B=300`. The direct v4.10 bindings make several of these IDs clearer. GLOBAL 0x56-0x5B remain write-locked; System control is the separate write-ready GLOBAL 0x55.

## STATUS layout

14-byte STATUS application payload:

`u8 state | i16 state_timer_s | i16 fan_% | i16 chimney_temp_x10 | i16 outside_temp_x10 | i16 inside_temp_x10 | i16 air_pressure_hPa | u8 flags`

## GLOBAL write envelope

Verified request form:

`06 0B | session_id_le32 | global_id_u8 | value_i16_le`

Only features marked `write_ready` may use it. Candidate/service fields are deliberately locked.

## Connection-code boundary

0.5.7 does not alter BLE discovery, source selection, reconnect behavior, PIN/session acquisition, BLE-release timing, status polling or GATT framing. Regression tests hash those methods against the tested 0.5.5 implementation.

## Historical corrections

- 0.5.6 incorrectly used `0x56` for System control; v4.10 direct code shows `0x55=System control` and `0x56=Temperature sensor`.
- 0.5.6 labelled state 5 Refueling; v4.10 state arrays show `5=Burnout`, `6=Afterrun`, `7=Reheating/Refueling`.
- 0.5.5 conservatively locked 0x50 after the broad settings shift was discovered. v4.10 direct Fan Control code plus the earlier successful physical probe now re-establishes `0x50` as Operation/User fan speed.
- Historical pre-0.5.5 labels for 0x32-0x55 that came from the stale firmware debug table must not override current live/direct-code evidence.

## 0.5.10 — fan speed in Ventilation

Captured GLOBAL `0x50` stepping 10→16 while state `0x19=8` (Ventilation); STATUS fan speed=16%. Removed HA-only state-4 restriction and replaced it with state 4 or 8. GLOBAL `0x50` remains the single setpoint. GLOBAL `0x1F` remains the separate actual fan-speed sensor.

## 0.5.9 — deferred external fields

GLOBAL `0x57` (External start) and `0x5A` (External fan speed) are deliberately deferred: they no longer appear in the active feature registry or as Home Assistant controls. These IDs and their raw values remain in GLOBAL diagnostics and protocol documentation for later study. GLOBAL `0x05` remains a separate sensor with unresolved semantics, and Ventilation packet `0x09` is unaffected.

## Alpha 0.5.11 update (2026-10-21)

- Removed non-functional Bluetooth release-to-app button, timer and associated BLE pause logic.
- Combined Boost on/off into one Boost switch; removed redundant Finish firing button. Stop firing retains its Afterrun transition through GLOBAL 0x19=6.
- Boost and Ventilation switches follow authenticated STATUS state (Boost state 3; Ventilation state 8). Boost state 7 is unresolved and retains last known value.
- Switch state is restored across HA restarts and retained across BLE reconnects until the first valid fresh STATUS frame. CONNECT/ACK immediately triggers the existing STATUS polling loop; command ACK alone does not determine switch state.
- Fan speed GLOBAL 0x50 is available in all connected states; firmware may still enforce its own restrictions.
- Controls are normal entities, configuration settings categorized CONFIG; device-page display ordering remains Home Assistant controlled.
- GitHub release source zip built from this tree; local tests do not substitute for on-device validation.

## Alpha 0.5.12 research

Alarm temperature `0x58`: manual 150–400 °C; raw `2500` is 250.0 °C. Promoted to CONFIG number, physical write/readback pending. Refire `0x59=180` and Burnout `0x5B=300` displayed provisionally as 3 and 5 minutes in DIAGNOSTIC only; no writes. See `CHIMNEYLOG_RESEARCH.md` for extracted firmware/Flutter symbols and remaining FILE_TRANSFER uncertainties.

## 0.5.14 experimental 0x56 switch

v4.10 directly maps the panel menu "Temperature sensor" to GLOBAL `0x56`. Official manual describes On/Off. Alpha 0.5.14 exposes a deliberately labeled *experimental* HA switch; `0=Off`, `1=On` remains a hypothesis until confirmed by physical-panel A/B comparison. Disabling stops automatic temperature-based start and stop. Do not infer the coding from the old shifted debug labels. All prior raw snapshots remain as collected.
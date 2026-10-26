# Xzense Alpha 0.5.12b — feature matrix

| Feature | Status | Mapping / notes |
|---|---|---|
| BLE connect + PIN session | Working | DSPS BLE service + Xzense CONNECT; connection methods unchanged from 0.5.5 |
| Temporary BLE release to app | Removed in 0.5.11 | Former test helper no longer exposed |
| Live status polling | Working | STATUS `0x07` |
| Device state | Verified read / v4.10 mapped | GLOBAL `0x19`; 0 Offline, 1 Setup, 2 Ready/IDLE, 3 Boosting, 4 Operation, 5 Burnout, 6 Afterrun, 7 Refueling/Reheating, 8 Ventilation, 9 Error, 10 Upgrading |
| State timer | Verified read | GLOBAL `0x1A`, seconds |
| Air pressure | Verified read | GLOBAL `0x1B`, hPa |
| Inside temperature | Strong read mapping | GLOBAL `0x1C`, tenths °C |
| Outside temperature | Strong read mapping | GLOBAL `0x1D`, tenths °C |
| Chimney temperature | Verified read | GLOBAL `0x1E`, tenths °C |
| Actual fan speed | Verified read | GLOBAL `0x1F`, % |
| 0x05 status | Raw, semantics unresolved | GLOBAL `0x05`; integers `2` and `3` observed during continuous USB power |
| Firmware version | Verified read | CONNECT ACK; `410` -> `4.10` |
| Boost switch | Commands tested; state derived | packet `0x08`, start 1/0 + inside temperature; STATUS state 3 |
| Start lighting | Firmware-derived / write-ready | state 2 -> BOOST `0x08`, start=1 |
| Refuel | Test write-ready | states 4 Operation and 5 Burnout -> BOOST `0x08`, start=1; state-4 outcome unverified |
| Stop firing | v4.10 firmware-derived / write-ready | state 3/7 -> BOOST start=0; state 4/5 -> GLOBAL `0x19=6` |
| Finish firing | Removed in 0.5.11 | Stop firing still performs the Afterrun action |
| Ventilation switch | Live tested | packet `0x09` on/off; STATUS state 8 determines switch state |
| Fan speed (setpoint) | Live read / write-ready | GLOBAL `0x50`, direct 10–100%; exposed in all connected states; other-state write behavior unverified |
| System control | v4.10 firmware-derived / write-ready | GLOBAL `0x55`; `0=Manual`, `1=eXotelligence`, `2=Pressure controlled` |
| Sound | Live-correlated / write-ready | GLOBAL `0x32`, direct % |
| Contrast | Live-correlated / write-ready | GLOBAL `0x33`, direct % |
| Brightness | Live-correlated / write-ready | GLOBAL `0x34`, direct % |
| Start temperature | Live-correlated / write-ready | GLOBAL `0x4B`, raw / 10 °C |
| Stop temperature | Live-correlated / write-ready | GLOBAL `0x4C`, raw / 10 °C |
| Boost time | Live-correlated / write-ready | GLOBAL `0x4D`, wire seconds / HA minutes |
| Afterrun time | Live-correlated / write-ready | GLOBAL `0x4E`, wire seconds / HA minutes |
| Boost speed | Live-correlated / write-ready | GLOBAL `0x4F`, direct % |
| Actual draught | No HA sensor | GLOBAL `0x51` raw is retained only in diagnostics |
| Boost stop temperature | Live-correlated / write-ready | GLOBAL `0x52`, raw / 10 °C |
| Chimney draught setpoint | Live-correlated / write-ready | GLOBAL `0x53`, direct Pa |
| Minimum fan voltage | Live-correlated / write-ready | GLOBAL `0x54`, direct V |
| Temperature probe | **EXPERIMENTAL / write-enabled** | GLOBAL `0x56`; On=1, Off=0 assumed; confirm physically before use. Off disables temperature-based start/stop |
| Alarm temperature | CONFIG / write-ready | GLOBAL `0x58` raw tenths °C; 150–400 °C manual range |
| Reboost/refire time | CONFIG / write-ready | GLOBAL `0x59` in seconds, shown as minutes; freely adjustable within signed wire range (controller safety limits unknown) |
| Burnout timeout | CONFIG / write-ready | GLOBAL `0x5B` in seconds, shown as minutes; freely adjustable within signed wire range (controller safety limits unknown) |
| GLOBAL `0x20` / `0x35` / `0x36` | Unknown / diagnostic | Raw read only |

The Home Assistant domain remains `xzense_full_preview` for registry compatibility. The user-facing integration name is **Xzense Alpha**.

## 0.5.10 entity exposure and deferred features

Only features marked `write_ready` create Home Assistant button/number/select/switch controls; candidate settings are diagnostics-only until their write semantics are confirmed. Previous `Burn count`, `Operation time`, `Error log`, `Download log`, `Language` and virtual `History` scaffolds were removed because they offered no data or working action. `Burn count`, `Operation time` and `Error log` remain **planned protocol research** under `FILE_TRANSFER 0x0C` / `ChimneyLog`; no decoded response is available yet. The raw GLOBAL payload and full diagnostic snapshots remain available for analysis.

External start (`0x57`) and External fan speed (`0x5A`) are **deferred at user request**. They are not represented as features/HA entities, but both continue to appear in full diagnostic raw GLOBAL dumps so no investigation data is lost. GLOBAL `0x05` is retained as an unresolved raw sensor, separate from external start/speed.

## Alpha 0.5.11 update (2026-10-21)

- Removed non-functional Bluetooth release-to-app button, timer and associated BLE pause logic.
- Combined Boost on/off into one Boost switch; removed redundant Finish firing button. Stop firing retains its Afterrun transition through GLOBAL 0x19=6.
- Boost and Ventilation switches follow authenticated STATUS state (Boost state 3; Ventilation state 8). Boost state 7 is unresolved and retains last known value.
- Switch state is restored across HA restarts and retained across BLE reconnects until the first valid fresh STATUS frame. CONNECT/ACK immediately triggers the existing STATUS polling loop; command ACK alone does not determine switch state.
- Fan speed GLOBAL 0x50 is available in all connected states; firmware may still enforce its own restrictions.
- Controls are normal entities, configuration settings categorized CONFIG; device-page display ordering remains Home Assistant controlled.
- GitHub release source zip built from this tree; local tests do not substitute for on-device validation.

## Alpha 0.5.12 updates

| Feature | Exposure | Confidence |
|---|---|---|
| Alarm temperature / GLOBAL `0x58` | CONFIG number 150–400 °C | Firmware ID + manual range + raw 2500=250.0°C; physical HA write not yet tested |
| Refire/Reboost / GLOBAL `0x59` | Read-only DIAGNOSTIC in minutes (candidate) | `180` observed; no firmware write limits verified |
| Burnout time / GLOBAL `0x5B` | Read-only DIAGNOSTIC in minutes (candidate) | `300` observed; no firmware write limits verified |
| System control / GLOBAL `0x55` | CONFIG select | Existing mode mapping, unchanged |
| Actual chimney draught / GLOBAL `0x51` | Removed standalone entity; retained raw GLOBAL | Scaling still unknown |
| ChimneyLog / FILE_TRANSFER `0x0C` | Research only | Log exists but safe request and record schema unknown; see CHIMNEYLOG_RESEARCH.md |
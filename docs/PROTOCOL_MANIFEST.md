# Xzense BLE protocol manifest — Alpha 0.5.25

Current source of truth for the 4.10 controller. **Verified** = confirmed on live hardware/captured working write. **Live-correlated** = physical controller setting matched to GLOBAL value. **Firmware-derived** = directly recovered from the official Xzense 5.0.5 bundled controller firmware (`v4.10_RC2`). **Candidate** = read-only until semantics/scaling are independently confirmed.

The v4.10_RC2 image contains a stale legacy GLOBAL debug-name table. Current IDs below therefore use direct UI/controller-code bindings plus live 4.10 correlations, not the legacy name table alone.

| ID | Current meaning | Encoding / unit | Access | Status | Evidence / notes |
|---:|---|---|---|---|---|
| `0x00`–`0x03` | Ukjente controllerfelter | int16 | diagnostikk | Ukjent | Lesbare i full GLOBAL-dump og samlet rådiagnostikk |
| `0x04` | Batteri på kontrollpanel | prosent, tentativt direkte | sensor | **Live-korrelert kandidat** | Endret rå 100→90 samtidig med batteriikon; eksakt kalibrering ikke fastslått |
| `0x05` | Signalstyrke panel ↔ kraftenhet | rå 0–3 (antatt) | sensor | **Firmware-hint / kandidat** | 2/3 observert; ikke Bluetooth-RSSI og ikke strømforsyningskilde |
| `0x18` | MY_STATE | rå integer | rådiagnostikk | Ukjent | Tidligere feilaktig tolket som signalstyrke; kan aktiveres som råsensor |
| `0x19` | Device state | enum | read + selected state action | Verified read / Firmware-derived write | State 3/6 live verified; Afterrun action writes value 6 |
| `0x1A` | State timer | seconds | read | **Verified** | Advances approximately once per second |
| `0x1B` | Air pressure | hPa | read | **Verified** | e.g. live 1011 = 1011 hPa |
| `0x1C` | Inside temperature | /10 °C | read | Strong | Corroborates STATUS |
| `0x1D` | Outside temperature | /10 °C | read | Strong | Corroborates STATUS |
| `0x1E` | Chimney temperature | /10 °C | read | **Verified** | Live calibrated |
| `0x1F` | Actual fan speed | % | read | **Verified** | Live at 10 % and 100 % |
| `0x20` | XTP-relatert / uavklart | int16 | kun full dump | Ukjent | Ingen montert XTP. Ikke opprettet som aktiv sensor |
| `0x32` | Sound | % | read/write | **Live-correlated + firmware** | 12→24 A/B; direct v4.10 UI binding |
| `0x33` | Contrast | % | read/write | **Live-correlated + firmware** | 75 matched panel |
| `0x34` | Brightness | % | read/write | **Live-correlated + firmware** | 68 matched panel |
| `0x35` | Unknown | int16 | rådiagnostikk | Ukjent | observert 1 |
| `0x36` | Unknown | int16 | rådiagnostikk | Ukjent | observert 0 |
| `0x4B` | Start temperature | /10 °C | read/write | **Live-correlated + firmware** | 502 = 50.2 °C |
| `0x4C` | Stop temperature | /10 °C | read/write | **Live-correlated + firmware** | 398 = 39.8 °C |
| `0x4D` | Boost time | seconds | read/write | **Live-correlated + firmware** | 900 = 15 min |
| `0x4E` | Afterrun time | seconds | read/write | **Live-correlated + firmware** | 1800 = 30 min |
| `0x4F` | Boost speed | % | read/write | **Live-correlated + firmware** | 100 = 100 % |
| `0x50` | Fan speed setpoint | % | read/write | **Live Ventilation A/B + firmware** | Operation (4) and Ventilation (8): 10→16 steps observed in Ventilation, STATUS fan=16%; HA control gated to states 4 and 8 |
| `0x51` | XTP actual draught | raw | kun full dump | Firmware-derived | Mangler XTP-sensor; ingen aktiv entitet |
| `0x52` | Boost stop temperature | /10 °C | read/write | **Live-correlated + firmware** | 600 = 60.0 °C |
| `0x53` | **Pipetrekk** (lagret installasjonsverdi) | Pa | read/write | **Live-correlated + firmware** | 26 = 26 Pa; ikke en sanntidsmåling uten XTP |
| `0x54` | Minimum fan voltage | V | read/write | **Live-correlated + firmware** | 80–120 V; HA-lokal RS009-41-bryter begrenser skriveområdet til 100–120 V |
| `0x55` | System control | enum | read/write kun 0/1 | **v4.10 firmware-derived** | 0 Manual, 1 eXotelligence; 2 Pressure controlled ikke vist uten XTP |
| `0x56` | Temperature probe | experimental enum (0/1) | read/write experimental | **v4.10 ID known** | assumed 0=Off,1=On; needs live confirmation |
| `0x57` | External start | raw/enum | diagnostic only (deferred) | Firmware-derived | removed from active feature registry; raw capture retained |
| `0x58` | Alarm setpoint | /10 °C | read/write | Firmware-derived | 150–500 °C, manual 150–400 °C |
| `0x59` | Reboost/refire time | seconds | read/write | Firmware-derived | 0–45 min, observed 180s=3min |
| `0x5A` | External fan speed | raw | diagnostic only (deferred) | Firmware-derived candidate | removed from active feature registry; raw capture retained |
| `0x5B` | Burnout timeout | seconds | read/write | Firmware-derived | 1–200 min, observed 300s=5min |

## Firmwaregrenser og referanseverdier for 0.5.25

Alle tallene under er vist som brukerrettede verdier; registerets rå verdi er hele grader ×10 eller minutter ×60 der det er oppgitt. Grensene ble funnet i 4.10_RC2-firmwarens oppsettsbeskrivelser og kan avvike fra den trykte manualen. **Endring av integrasjonen overskriver aldri kontrollpanelets eksisterende konfigurasjon.**

| GLOBAL | Innstilling | Firmware minimum | Firmware maksimum | Fabrikk-/brukerreferanse | Lokal tilleggssperre |
|---|---|---:|---:|---:|---|
| `0x4B` | Starttemperatur | 5 °C | 205 °C | 40 °C | Må være minst 6 °C over stopp |
| `0x4C` | Stopptemperatur | 0 °C | 200 °C | 35 °C | Må være minst 6 °C under start |
| `0x4D` | Boost-tid | 0 min | 45 min | 10 min | – |
| `0x4E` | Ettergangstid | 1 min | 200 min | 30 min | – |
| `0x52` | Boost-stopptemperatur | 30 °C | 250 °C | **60 °C brukerønske**; manual 150 °C | – |
| `0x53` | Pipetrekk | 8 Pa | 150 Pa | 20 Pa | Ikke XTP-sanntid |
| `0x54` | Minimum viftespenning | 80 V | 120 V | 100 V (manual) | RS009-41 PÅ: 100–120 V |
| `0x58` | Alarmtemperatur | 150 °C | 500 °C | 250 °C | – |
| `0x59` | Gjenfyringstid | 0 min | 45 min | 3 min | – |
| `0x5B` | Utbrenningstid | 1 min | 200 min | 5 min | – |

## Alle øvrige registre i HA-diagnostikk

`sensor.*unused_global_values` viser hvert mottatt, ellers ubrukt GLOBAL-register og dets råverdi under attributtet `registers`. Dette omfatter også eventuelle nye, ennå ikke navngitte ID-er. Registerbeskrivelsene ovenfor er **ikke** en påstand om at en ubrukt verdi støttes av fysisk utstyr. Kjente ubrukte ID-er (`0x00`–`0x03`, `0x18`, `0x35`, `0x36`, `0x57`, `0x5A` osv.) har dessuten separate diagnostikkentiteter som er **deaktivert som standard** for å redusere antall løpende HA-tilstandsoppdateringer. XTP-feltene `0x20` og `0x51` holdes utenfor de nye diagnostikkentitetene, men finnes fortsatt i fullstendig diagnostikkeksport.

## v4.10 state table

The firmware state-name arrays contain: `OFFLINE`, `SETUP`, `IDLE`, `BOOSTING`, `OPERATING`, `BURNOUT`, inserted `AFTERRUN`, `REHEATING`, `VENTILATING`, `ERROR_STATE`, `UPGRADING`, `UNKNOWN_STATE`.

| Raw | Meaning |
|---:|---|
| `0` | Offline |
| `1` | Setup |
| `2` | Ready for lighting / IDLE |
| `3` | Boosting |
| `4` | Operation |
| `5` | Burnout |
| `6` | Afterrun |
| `7` | Refueling / Reheating |
| `8` | Ventilation |
| `9` | Error |
| `10` | Upgrading |

## Packet types

| Packet | Meaning | Status |
|---:|---|---|
| `0x02` | CONNECT | Verified |
| `0x06` | GLOBAL | Verified read/write envelope |
| `0x07` | STATUS | Verified |
| `0x08` | BOOST | Live verified on/off; v4.10 state-dependent Start lighting / Refuel paths |
| `0x09` | VENTILATION | Firmware-derived start/stop; live write pending |
| `0x0A` | RANGETEST | Firmware-derived, not exposed |
| `0x0B` | FACTORY_RESET | Firmware-derived, intentionally not exposed |
| `0x0C` | FILE_TRANSFER | Firmware-derived, not exposed |
| `0x0D` | TIMESYNC | Firmware-derived, not exposed |
| `0x0E` | CONNECTED_PEERS | Firmware-derived, not exposed |

## Action semantics in 0.5.7

- state `2` + BOOST `start=1` -> Start lighting.
- state `5` Burnout + BOOST `start=1` -> Refuel/Reheating (`state 7`).
- state `3` or `7` + BOOST `start=0` -> stop the active Boost/Reheat phase.
- state `4` Operation or `5` Burnout + GLOBAL `0x19=6` -> Finish firing / Afterrun.
- VENTILATION request: `09 0B | session_id_le32 | start_u8`.
- System control: GLOBAL `0x55`, values `0/1/2` as above.
- Fan speed setpoint: GLOBAL `0x50`, direct %, exposed 10-100 % and HA-gated to states `4` Operation or `8` Ventilation.

Controller ACK/NACK remains authoritative for state-dependent requests.

## Alpha 0.5.11 update (2026-10-21)

- Removed non-functional Bluetooth release-to-app button, timer and associated BLE pause logic.
- Combined Boost on/off into one Boost switch; removed redundant Finish firing button. Stop firing retains its Afterrun transition through GLOBAL 0x19=6.
- Boost and Ventilation switches follow authenticated STATUS state (Boost state 3; Ventilation state 8). Boost state 7 is unresolved and retains last known value.
- Switch state is restored across HA restarts and retained across BLE reconnects until the first valid fresh STATUS frame. CONNECT/ACK immediately triggers the existing STATUS polling loop; command ACK alone does not determine switch state.
- Fan speed GLOBAL 0x50 is available in all connected states; firmware may still enforce its own restrictions.
- Controls are normal entities, configuration settings categorized CONFIG; device-page display ordering remains Home Assistant controlled.
- GitHub release source zip built from this tree; local tests do not substitute for on-device validation.

## 0.5.12 exposure supplement (supersedes read-only row labels above)

- GLOBAL `0x58`: Alarm temperature, CONFIG write-enabled in HA, 150–400 °C, 0.1 °C steps, raw tenths. Firmware/official-manual-derived; physical HA write pending.
- GLOBAL `0x59` and `0x5B`: read-only DIAGNOSTIC display; 180/60 = 3, 300/60 = 5 minutes are still provisional. Raw GLOBAL values retained, no write controls.
- GLOBAL `0x51`: visible actual-draft raw entity removed; diagnostics still includes the raw value.
- FILE_TRANSFER `0x0C`: research only. No active log/firmware transfer implemented; see `CHIMNEYLOG_RESEARCH.md`.

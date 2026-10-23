# Xzense Alpha

Uoffisiell, eksperimentell Home Assistant-integrasjon for **Exodraft Xzense** over Bluetooth LE. Integrasjonsdomenet er `xzense_full_preview` og skal ikke endres ved oppgradering.

**Nyeste pakke: Alpha 0.5.19.3 (23. oktober 2026)** · [Last ned komplett kildekode og dokumentasjon](xzense-alpha-0.5.19.3-slider-seconds-source.zip) · Installasjonsfilen `INSTALLASJON_0.5.19.3.md` ligger i ZIP-arkivet.

## Kort om gjeldende versjon

| Funksjon | Gjeldende oppførsel |
|---|---|
| Bluetooth i Ready (hvile) | Slider **0–120 minutter**, standard 5 min. `0` betyr kontinuerlig tilkobling. |
| Bluetooth under aktiv drift | Slider **0–600 sekunder**, standard `0` (kontinuerlig). Omfatter Boosting, Operation, Afterrun og Ventilation. |
| Styringskommandoer | Tilkobling ved behov, kommandokø og normalt 15 sekunders holdetid etter handling. |
| Sensorverdier uten Bluetooth | Siste kjente verdier beholdes, men kan være utdaterte. **Sist oppdatert (Bluetooth)** viser siste mottatte gyldige data. |
| Fyringsvarighet | Ny økt fra observert Ready; tilbakeberegning med `Time in State` når plausibel. Start fra Afterrun **fortsetter samme økt**, uten nullstilling. |
| Start fra Afterrun | Støttes via eksisterende startkommando; Afterrun → Boosting/Operation er observert i diagnostikk. |

### Viktig om sikkerhet og stabilitet

**Ikke bruk Alpha 0.5.15 eller 0.5.16.** En bekreftet busy-loop i BLE-gjentilkoblingen kunne fryse Home Assistant. 0.5.17 rettet denne feilbanen; nyere versjoner bygger videre på beskyttelsen. 0.5.19.3 har bestått lokale regresjonstester, men den nyeste kombinasjonen av modusbytter og fysisk Bluetooth-forbindelse må fortsatt prøves på anlegget.

Dette er ikke en sikkerhetskontroller. Når Bluetooth er frakoblet, kan både driftstilstand og temperatur være eldre enn de ser ut. Ikke bruk lagrede verdier som bekreftet sanntidsstatus.

### Installere eller oppgradere

1. Ta backup av `/config/custom_components/xzense_full_preview/`.
2. Pakk ut `custom_components/xzense_full_preview/` fra ZIP-en og erstatt hele den eksisterende mappen; behold den eksisterende konfigurasjonsoppføringen.
3. Start Home Assistant på nytt og kontroller versjon **0.5.19.3**.
4. Bruker du det separate dashboardkortet, kopier `www/xzense-card.js` til `/config/www/` og oppdater ressursen til `/local/xzense-card.js?v=05193b`. Se installasjonsfilen i arkivet for andre oppsett.

De to Bluetooth-intervallene er `number`-entiteter med `NumberMode.SLIDER`. Home Assistant kan fortsatt vise kompakte tallfelter i enkelte lister; åpne entitetsdialogen eller legg entiteten i et Tile-kort for en faktisk slider. Ved oppgradering fra 0.5.19.2 konverteres aktivt intervall fra minutter til sekunder (f.eks. 1 min → 60 sek).

## Versjonshistorikk (nyeste først)

## Alpha 0.5.19.3 – Bluetooth-slidere i HA og sekunder under aktiv drift

- Hovedskjermen viser også **Sist oppdatert** fra eksisterende `last_data_at`-sensor, som gir tidspunkt og alder på mottatte Bluetooth-data selv når kontrollpanelet er frakoblet. Sensoren heter nå «Sist oppdatert (Bluetooth)» og beholder samme unique ID.

- Rettet konflikt med Home Assistants reserverte `mode`-attributt på begge `number`-entitetene. Enhetene har nå bare egendefinert `bluetooth_connection_mode` og presenterer `NumberMode.SLIDER` til HA.
- Aktiv drift: **0–600 sekunder**, trinn 1 sekund, standard **0 = kontinuerlig**. Hvile/Ready: **0–120 minutter**, standard 5 min.
- Ved oppgradering oversettes gammel innstilling fra 0.5.19.2, for eksempel 1 minutt til 60 sekunder. Når du endrer aktiv slider lagres den videre som `active_update_interval_seconds`.
- Kontinuerlig drift, BLE-protokoll, styringskommandoer, kommandokø, sensorkache og fyringstid beholdes.
- Begge dashboardkopiene er oppdatert til 0.5.19.3. Se `INSTALLASJON_0.5.19.3.md`.

## Alpha 0.5.19.2 – hybrid Bluetooth og fyringstid

Historisk versjon: **0.5.19.2**. Bygger på 0.5.19.1 med Afterrun-start støttet.

- **Bluetooth i hvile (Ready):** lineær slider 0–120 minutter, standard 5.
- **Bluetooth under aktiv drift (Boosting/Operation/Afterrun/Ventilation):** slider 0–10 minutter, standard 0 = kontinuerlig.
- **Knappetrykk:** start forbindelse ved behov, send én kommando med fersk STATUS, behold forbindelse i 15 sekunder etter handling. Sist kjente verdier beholdes ved frakobling.
- **Fyringsvarighet:** ny økt kun ved forrige observerte Ready og ny aktiv status; Afterrun → Boosting/Operation fortsetter eksisterende økt. `Time in State` brukes til å tilbakedatere Ready → Boosting når plausibel; Ready → Operation er et estimat for Operations start. Fra HA Start opptenning i Ready brukes knappetrykk som foreløpig referanse inntil STATUS bekrefter aktiv tilstand. Afterrun → Ready markerer avsluttet økt.
- Byttende driftsprofiler kan ikke oppdages mens Bluetooth er frakoblet; endringen trer i kraft ved første nye STATUS. Tidligere feilførte økter fra eldre versjoner kan ikke rekonstrueres automatisk.
- **Testutgave:** test med tilsyn på Xzense-kontrollpanelet før du tar i bruk automatiseringer. Fyringsvarigheten er diagnostikk, ikke en sikkerhetssensor.

Se `INSTALLASJON_0.5.19.2.md` for oppgradering og tilbakeføring.

## Alpha 0.5.19.1 – Start ny fyring i Afterrun

- `Start lighting` kan trykkes i Ready (2) og Afterrun (6). Ved Afterrun bruker den samme BOOST/REQ start=1 som tidligere; panelet bestemmer om kommandoen blir akseptert.
- **Historisk oppførsel i 0.5.19.1:** En ny økt ble registrert ved Afterrun → Boosting/Operation/Reheating. **Dette ble endret i 0.5.19.2:** Start fra Afterrun fortsetter nåværende fyringsøkt uten nullstilling.
- Periodisk BLE, kommandokø, slider og beholdte sensorverdier er identiske med 0.5.19.
- Testversjon: test forsiktig på det fysiske panelet. Ikke anta at utestet restart i Afterrun fungerer.

## Alpha 0.5.19 — periodisk og behovsstyrt Bluetooth (testversjon)

- Ny lineær slider **Bluetooth update interval**, 0–120 minutter. 0 = kontinuerlig 0.5.17-sesjon; standard 5 minutter.
- Periodisk modus: koble til, vent på autentisert STATUS, hent DATA, koble fra kontrollert, neste oppdatering etter valgt intervall.
- Ved trykk på styring: hurtigvei via egnet per-scanner BLE-cache (RSSI >= −85 dBm); fallback til den opprinnelige skanningen. Kommandokø, fersk STATUS før skriving, 15 sekunder BLE holdetid etter siste handling.
- Siste kjente status og GLOBAL-verdier overlever frakobling og HA-omstart; entiteter viser attributtene `last_data_at` og `stale`. Driftsstatus og verdier er **ikke sanntid** under frakobling.
- Kontrollpanelets normale kommunikasjonsrammer er uendret. Aktiv fyring gir ikke automatisk hyppigere polling; velg 0 min hvis sanntid er viktig.
- Innebygd dashboardkort viser intervallet i **Konfigurasjon**, og oppdateringstidspunkter i **Diagnostikk**.
- Rent lokalt 117 tester og JS-smoke; **ikke validert mot fysisk Exodraft Xzense**. Ta backup av 0.5.17 før testing.

## Alpha 0.5.18 — eksperimentell STATUS-polling (historisk)

- Testet justerbar STATUS-polling, inkludert av, 10, 60 og 300 sekunder.
- Flere sesjoner ble brutt etter omtrent 30–40 sekunder. Årsaken er ikke endelig fastslått, og denne varianten anbefales ikke som stabil referanse.
- Hybridversjonene 0.5.19 og nyere ble i stedet videreutviklet fra 0.5.17 sin kjente kommunikasjonsflyt.

## Alpha 0.5.17 — Event loop hotfix

- Ved BLE-reconnect kan `_wake` allerede være satt. 0.5.15/0.5.16 løp da videre uten `await`, slik at asyncio og alle andre HA-oppgaver stanset.
- 0.5.17 konsumerer wake-signalet og går til asynkron venting med en ekstra tilkoblingskontroll, fremfor å spinne.
- 0.5.16 sine proxy-/timerfunksjoner er beholdt uendret og må fortsatt testes fysisk.
- Regresjonstest simulerer dette konkret, i tillegg til eksisterende testsett.

## Alpha 0.5.16 – Strongest BLE proxy + fire timers (22 October 2026)

**Download:** [xzense-alpha-0.5.16-source.zip](xzense-alpha-0.5.16-source.zip) · [Installation](INSTALLASJON_0.5.16.md) · [Next-chat handoff](OVERLEVERING_NESTE_CHAT_0.5.16.md)

- Compare BLE discoveries **per proxy** using `async_register_advertisement_callback` and `async_scanner_devices_by_address`. Rank by actual RSSI; no last-success/failure score, and fall back to other candidates on connection failure.
- Capture candidate sources and origin (`fresh_raw_advertisement` or `per_scanner_cache`) in diagnostics. RSSI is sampled, not continuously measured, and a cached value may be stale.
- Existing **Time in current state** sensor now reports `HH:MM:SS`, correcting the signed 16-bit display and 65,536-second rollover. Unique ID stays `state_timer`; raw seconds, rollover count and continuity are attributes.
- New **Fire duration** sensor measures an observed fire cycle from Boosting/Operation/Refueling/Burnout/Afterrun until Ready; Ventilation does not start a cycle. Unknown starting times are conservatively flagged and **never presented as exact**.
- Store timer checkpoints across HA restarts with the Home Assistant storage helper. Prolonged BLE outages can conceal state changes, so elapsed reconstruction and fire duration have uncertainty indicators.
- Updated Lovelace card 0.5.16 displays both timers (Norwegian labels), with all device entities still English. Existing commands and 10-second STATUS polling are unchanged.
- Automated unit/regression tests and JS smoke test pass locally; **physical Bluetooth/controller validation remains outstanding**.

## Alpha 0.5.15 — proxyvalg og BLE-sesjonsdiagnostikk (2026-10-22)

- Samler ferske Bluetooth-annonseringer fra flere proxyer i et **3-sekunders vindu** og prioriterer signalstyrke, moderat bonus for sist vellykkede proxy og kortvarig straff etter feil. Ingen MAC-adresse er hardkodet.
- Logger siste **20 BLE-frakoblinger** med tilkoblet proxy, RSSI ved oppkobling, sesjonsvarighet, tilkoblingsstatus og tid for siste STATUS-forespørsel/-svar.
- Skiller lokal opprydding fra uventet BLE-callback. **En uventet callback identifiserer ikke hvem som koblet fra.**
- Beskytter ny tilkobling mot forsinkede callbacks fra eldre klienter og mot en mistet frakoblingshendelse under CONNECT.
- PIN/CONNECT, STATUS hvert 10. sekund, GLOBAL/BOOST/Ventilation og øvrige kontrollkommandoer er uendret.
- Dashboard er uendret fra 0.5.14 og bruker `/local/xzense-card.js?v=0514`.
- Hele integrasjonen leveres fortsatt med domenet `xzense_full_preview`. Verifiser gjeldende integrasjonsdomene før du erstatter en installert mappe med navnet `xzense`.

## Alpha 0.5.14 — nytt Lovelace-dashboard og temperaturprobe

Denne versjonen inkluderer dashboardkortet både i `www/xzense-card.js` (anbefalt: kopier til `/config/www/` og bruk ressursen `/local/xzense-card.js?v=0514`) og under `custom_components/xzense_full_preview/www/xzense-card.js`.
Kortet har **egen visuell redigerer** for å velge riktige HA-entiteter og valgfritt eget visningsnavn per felt. Se [dashboard/INSTALLASJON.md](dashboard/INSTALLASJON.md) for full oppdatering og ressursregistrering. Ikke gi en eksisterende integrasjonsmappe ved navn `xzense` nytt navn uten å kontrollere integrasjonsdomenet. Fem faner: Hovedskjerm, Driftsinnstillinger, Konfigurasjon, Kontrollpanel og Diagnostikk.

- `Temperature probe` er nå en **eksperimentell På/Av-bryter** for GLOBAL `0x56`. Verdiene `0=Av`, `1=På` må bekreftes på panelet ved første forsiktige test; kontrollen deaktiverer automatisk temperaturbasert start/stopp når den er av. Ikke test under aktiv fyring.
- Overlange diagnostikk-sensortilstander begrenses til 255 tegn; komplett GLOBAL-oppsett og Bluetooth-feiltekst bevares i attributter og diagnostikk.
- Alpha 0.5.14: ingen endring i BLE/PIN/STATUS-transport eller kildevalg.
- Inneholder alt fra 0.5.12b og 0.5.13, inkludert Refuel i tilstand 4 og 5.

## Alpha 0.5.13: compatibility correction to 0.5.12b

- Normalized the integration's `manifest.json` version to numeric SemVer `0.5.13` and synchronized `const.py` so Home Assistant and version checks see one release.
- No changes to BLE protocol, PIN authentication, device controls, entity IDs or runtime behavior compared with 0.5.12b.
- Retains **Refuel** availability in Operation (state 4) and Burnout (state 5), plus raw **0x05 status** / **0x18 status** sensor names.
- If Home Assistant reports the integration missing, copy the **whole** `custom_components/xzense_full_preview/` directory into `/config/custom_components/xzense_full_preview/`, replacing the previous files, then restart Home Assistant. Do not delete the existing integration/config entry. Review Settings → System → Logs if it still fails.

## 0.5.12b — Refuel in Operating and raw GLOBAL status names

- **Refuel** is available in **Operating / Operation (state 4)** as well as **Burnout (state 5)**, when the existing Boost command is available. It still sends the same `BOOST/REQ 0x08 start=1` command; the result in state 4 has **not yet been physically verified**.
- The existing sensor with unique ID suffix `battery` is renamed **0x05 status** and displays the **raw integer** (e.g. `2` / `3`), without claiming it means battery or external power.
- The existing sensor with unique ID suffix `signal_strength` is renamed **0x18 status** and still displays the raw `GLOBAL 0x18` integer, without interpreting its units.
- Sensor unique IDs, BLE transport/authentication, all other controls and diagnostics remain unchanged. Home Assistant may preserve a manually customized entity name until the user resets that customization.

## 0.5.12 — configuration, source ambiguity and ChimneyLog research

- **System control** moved to Configuration. **Alarm temperature** (`0x58`) is a Configuration number with 150–400 °C range and raw-tenths scaling.
- **Refire / Reboost time** (`0x59`) and **Burnout timeout** (`0x5B`) are now editable Configuration numbers after user confirmation of panel editing. Raw seconds convert to minutes. Home Assistant exposes 0–546.1 minutes in 0.1-minute steps, using only the signed-16-bit GLOBAL transport bound; **these are not verified controller-safe limits**. HA-initiated writes await physical verification.
- Old read-only sensor entries for `0x59`/`0x5B` are removed on migration. Existing numeric settings retain their feature keys/unique IDs.
- **Actual chimney draught (raw)** sensor hidden/removed; raw `0x51` retained in the full diagnostics.
- **Power source (?)** preserves the existing sensor key (`battery`), but reports `Unknown (2)` / `Unknown (3)` instead of asserting Battery/External. The physical controller was wired while sending different raw values in consecutive diagnostics; the precise enum has not been proven. Raw remains present in diagnostics.
- [ChimneyLog investigation](CHIMNEYLOG_RESEARCH.md): confirms firmware filenames and app-side indicators but no safe request/record layout. No `FILE_TRANSFER` test commands or firmware writes are added.

## Alpha 0.5.11 update (2026-10-21)

- Removed non-functional Bluetooth release-to-app button, timer and associated BLE pause logic.
- Combined Boost on/off into one Boost switch; removed redundant Finish firing button. Stop firing retains its Afterrun transition through GLOBAL 0x19=6.
- Boost and Ventilation switches follow authenticated STATUS state (Boost state 3; Ventilation state 8). Boost state 7 is unresolved and retains last known value.
- Switch state is restored across HA restarts and retained across BLE reconnects until the first valid fresh STATUS frame. CONNECT/ACK immediately triggers the existing STATUS polling loop; command ACK alone does not determine switch state.
- Fan speed GLOBAL 0x50 is available in all connected states; firmware may still enforce its own restrictions.
- Controls are normal entities, configuration settings categorized CONFIG; device-page display ordering remains Home Assistant controlled.
- GitHub release source zip built from this tree; local tests do not substitute for on-device validation.

## 0.5.10 fan-speed availability in Ventilation (no wire-protocol change)

The live 2026-10-21 Ventilation (state 8) capture shows GLOBAL `0x50` rising from 10 to 16 in 1% steps; subsequent STATUS reported 16%. The same setpoint is used in Operation (state 4). The Home Assistant number is now named **Fan speed** and available only in state `4` or `8`, with a write-time check for the same states. The separate `0x1F` read-only sensor is now named **Actual fan speed**. Existing feature keys, unique IDs, minimum 10% and maximum 100%, and the GLOBAL write format remain unchanged. Writes in Ventilation from HA have not yet been physically tested.

## 0.5.9 deferred external controls (no wire-protocol change)

External start (GLOBAL `0x57`) and External fan speed (GLOBAL `0x5A`) have been removed from the active feature registry and HA entity exposure at the user's request. The registry cleanup from 0.5.8 still removes any old entities with these IDs. To preserve reverse-engineering evidence, both values remain in raw diagnostic GLOBAL captures and in protocol documentation. The unresolved **Power source (?)** sensor (`0x05`) stays, showing raw values as unknown until verified. Boost, Ventilation, BLE connection and all other controls are unchanged.

## 0.5.8 cleanup (no wire-protocol change)

Removed empty Burn count, Operation time and Error log entities, unmapped Language and Download log placeholders and the duplicate raw GLOBAL 0x51 entity. Candidate settings without verified writing semantics remain documented in the feature matrix and available in diagnostic GLOBAL dumps, but are no longer instantiated as unusable controls. GLOBAL 0x00-0x04 now appear as UNKNOWN rather than misleading legacy firmware debug labels. No BLE connection or control commands changed.

## 0.5.7 source-of-truth update

The official **Xzense 5.0.5** app contains controller firmware `assets/flutter_assets/assets/fw/exodraft.gbl`. The image identifies itself as **v4.10_RC2**, matching the 4.10 generation reported by the user's controller. Direct UI/controller-code bindings from that firmware are used together with live 4.10 observations.

The firmware also contains an older debug-name lookup whose GLOBAL labels are shifted for several setup values. Alpha 0.5.7 therefore does **not** use that debug table alone as authoritative evidence.

## Protokollreferanse


Følgende tabeller oppsummerer identifiserte GLOBAL-felt, driftstilstander og kontrollkommandoer. `PROTOCOL_NOTES.md`, `PROTOCOL_MANIFEST.md`, `FEATURE_MATRIX.md` og tester følger med i kildekodearkivet.


## Working / mapped controls

| Home Assistant control | Xzense mapping | Confidence / gate |
|---|---|---|
| Boost switch | packet `0x08`, start `1/0` + inside temperature | Command live-verified, status from STATUS |
| Start lighting | packet `0x08`, start `1` | Firmware-derived; only state `2` |
| Refuel | packet `0x08`, start `1` | v4.10_RC2-derived; states `4 = Operation` and `5 = Burnout` |
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
| `0x56` | Temperature probe | experimental On/Off (`0/1`, unverified) | v4.10 direct UI binding; write mapping awaits physical confirmation |
| `0x58` | Alarm setpoint | raw / 10 °C | 150–400 °C number; physical write unverified |
| `0x59` | Reboost/refire time | seconds → HA minutes | experimental writable configuration |
| `0x5B` | Burnout timeout | seconds → HA minutes | experimental writable configuration |

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

## Safety / scope

This is an unofficial reverse-engineered integration and is not affiliated with or endorsed by Exodraft. Controller ACK/NACK remains authoritative for state-dependent commands. The new v4.10-derived controls still require live validation where explicitly noted.

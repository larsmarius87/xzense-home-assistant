# Xzense Alpha – komplett endringslogg

## 0.5.26 – testversjon (03.11.2026)

- Basert på 0.5.25-rc1. Bluetooth-transport og multi-proxy er uendret.
- Refueling bare i Burnout (state 5), firmware velger 0x59-timer og state 7. Operation state 4 gir ordinær Boost med 0x4D, ikke Refueling.
- Sensorikon med sikker fallback fra Final Fix1.
- Forbedret dashboard og sensorvisning. Se [installasjonsnotat](INSTALLASJON_0.5.26.md).
- Må verifiseres i drift før den regnes som stabil.

**Nyeste testpakke: 0.5.26 (3. november 2026), ennå ikke fysisk verifisert. Sist bekreftet fungerende versjon: 0.5.25 RC1.** Alle tilgjengelige komplette arkiver er listet i [REVISJONER.md](REVISJONER.md). Se også [README](README.md). Original endringslogg før opprydding er bevart i [docs/CHANGELOG_OPPRINNELIG_TIL_0.5.24.md](arkiv/dokumenter/CHANGELOG_OPPRINNELIG_TIL_0.5.24.md).

> **IKKE INSTALLER 0.5.15 eller 0.5.16:** Begge inneholder en dokumentert busy-loop som kan fryse Home Assistant. 0.5.17 rettet denne konkrete feilen.

**Implementert i 0.5.25:** Sensor med sist vellykkede STATUS-oppdatering i norsk dato-/tidsformat, flertelefonvarsling og ryddigere diagnostikk.

## Verifiserte observasjoner (skilt fra kodeendringer)

### Verifisering på fysisk Xzense – 26.10.2026 (0.5.24)

- 8 av 8 vellykkede applikasjonsautentiseringer; 8 av 8 STATUS-svar; 2 av 2 GLOBAL-skrivinger kvittert med ACK.
- 0 CRC-feil, 0 ugyldige rammer og 0 STATUS-NACK i aktuell diagnostikk.
- Multi-proxy fungerte med den nye Stue-proxyen (`90:15:06:FA:DF:FA`, typisk −65 dBm) samt gammel Stue (`8C:D0:B2:A9:21:22`, −78 dBm); det ble logget 3 fallback-hendelser.
- `connected: false` er forventet mellom økter når Bluetooth er i periodisk hvilepolling (5 min i den aktuelle diagnostikken). Registrerte frakoblinger var `local_periodic_poll`.
- Dette bekrefter oppkobling, autentisering, lesing og noen globale skrive-ACK-er, **ikke** at alle kontrollkommandoer eller døgnlang stabilitet er ferdig verifisert.

### Verifisert i eldre samtaler (historiske observasjoner)

- **0.4.5 / 19.10.2026:** Boost ON og OFF bekreftet på fysisk Xzense. Boost ON sendte `0x08` start=1; svar `ACK:01`, status 3 (Boosting), vifte 100 %. Dette er ikke en generell bekreftelse av alle styringskommandoer.
- **0.5.17 / 22.–23.10.2026:** En målt autentisert BLE-økt varte 27 min 17 s via Stue, med 191 STATUS-forespørsler og uten STATUS-NACK eller CRC-feil. Bekreftet videre `10 s` polling; kontrollpanelets timeout og ALIVE-rammer ble fortsatt undersøkt.
- **0.5.19.1 / 23.10.2026:** Etterfølgende fysisk test bekreftet `Afterrun → Boosting → Operation` ved «Start ny fyring», med BOOST-ACK etter ca. 217 ms og ingen uventede disconnects i testen. Opprinnelige kodenotater sa «ikke fysisk bekreftet» før denne testen og må leses i tidsrekkefølge.
- **0.5.15–0.5.16:** Bekreftet asyncio busy-loop som kunne fryse hele HA. **Må ikke anbefales for installasjon.** Hotfix kom i 0.5.17.

---

---

---

## Versjonsendringer (nyeste først)

## 0.5.25 – 2026-10-28 – siste Alpha etter RC1

- Ferdig versjon `0.5.25` med bevarte innstillinger og uendret BLE fra 0.5.24. RC1-ZIP beholdt separat i arkivet.
- `mdi:turbine` for Boost, `mdi:engine-outline` for Viftetype RS009-41, `mdi:fan` for viftehastighet.
- Radio-link `0x05` tolkes foreløpig 0–3 signalstreker, panelbatteri `0x04` foreløpig prosent. `0x18` fortsatt ukjent. Pipetrekk `0x53` lagret installasjonsparameter.
- Flertelefonvalg i varslingsinnstillinger, automatisk lesing av tidligere ett-telefonvalg. Varselteksten «Xzense: Legg i mer ved» ved fersk Drift (4) → Utbrenning (5), og ingen varsel ved oppstart.
- Tidligere utilgjengelige, eksperimentelle probe- og rådiagnostikkentiteter ryddes fra registeret. Råverdiene ligger fortsatt i nedlastbar integrasjonsdiagnostikk.
- 0x54 minimum viftespenning 80–120 V, eller 100–120 V når Viftetype RS009-41 er på, uten automatisk skriving.
- 184 av 184 lokale Python-testtilfeller og fem dashbord-smoketester bestått. Fysisk BLE- og push-test gjenstår.

## 0.5.25-rc1 – 2026-10-27 – arkivert testkandidat

- Oppsettgrenser fra firmware 4.10_RC2, start-/stoppdifferanse minst 6 °C, råregistersamling og nye sensorverdier. Se [installasjon av RC1](INSTALLASJON_0.5.25-rc1.md).

## 0.5.24 – 2026-10-26 – automatisk multi-proxy med cache-fallback

- Fjernet eksklusiv lås til tidligere Stue-proxy (`8C:D0:B2:A9:21:22`). Oppdager automatisk alle tilgjengelige Home Assistant Bluetooth-kilder, inkludert ny ESPHome-proxy, uten forhåndskonfigurert MAC.
- Rangering etter faktisk RSSI. Ferske annonseringer overstyrer cache fra samme adapter; ingen låst prioritert proxy. Også manuelt utløst tilkobling henter kandidater på nytt, slik at ny proxy ikke overses til fordel for gammel cache.
- Beholder 0.5.23 sin mindre strenge logikk: etter inntil tre sekunder uten ny annonsering kan integrasjonen forsøke kildebestemte BLEDevice-oppføringer fra HA-cache. Cachetilkobling fra én adapter faller tilbake til neste ved feil.
- 120 sekunders karantene for mislykkede cachetilkoblinger; ferske annonseringer kan gjenåpne en kilde ved senere skannerunder.
- Maksimalt seks ulike Bluetooth-kilder per oppkoblingsrunde, ett Bleak-forsøk per kilde. Ingen rekursive reskanninger som kan skape aggressive løkker.
- Beholder øvrige funksjoner, PIN og entitets-ID-er. Diagnostikk rapporterer `source_lock_active=false` og alle kandidatene.
- Fallback håndterer tilkoblings-/GATT-oppsettfeil. Manglende applikasjons-ACK/STATUS etter etablert BLE behandles fortsatt av neste oppkoblingsrunde, ikke direkte fallback i samme runde.

## 0.5.23 – 2026-10-26 – Stue-only, avslappet annonseringskrav (TEST)

- Stue er fortsatt eneste tillatte Bluetooth-kilde: `8C:D0:B2:A9:21:22`. Ingen fallback til Gang eller USB.
- Etter 3 sekunder uten ny Xzense-annonsering tillates én BLE-tilkobling med Home Assistants **Stue-spesifikke** cache, hvis den finnes.
- På manuelt utløst tilkobling tillates den samme Stue-cachen uten en kunstig RSSI-grense på −85 dBm.
- Mislykkede cachetilkoblinger får 120 sekunders sperre før cache kan brukes på nytt; ferske annonseringer håndteres fortsatt som før.
- Hvis Stue aldri har oppdaget Xzense og ingen Stue-spesifikk BLEDevice finnes, kan integrasjonen fortsatt ikke koble til. Ingen oppdiktede BLEDevice-håndtak opprettes.
- Nye diagnostikkfelt for å skille cache-fallback fra ferske annonseringer. Mindre hyppige nye forsøk i kontinuerlig modus.
- Uendret protokoll, PIN, STATUS og kontrollkommandoer.

## 0.5.22 – 2026-10-25 – Stue-only låst proxy (historisk TEST)

- Låste BLE-kandidater til gammel Stue-kilde `8C:D0:B2:A9:21:22`. Ingen fallback til Gang, USB eller annen proxy.
- Forutsatte ferske annonseringer fra Stue. Hvis Stue ikke observerte Xzense, kom ingen BLE-opprettelse i gang (`locked_source_not_available`).
- Nye diagnostikkfelter `source_lock_active` og `locked_bluetooth_source`. Variasjonen var kun ment for feilisolering, ikke permanent oppsett.
- Fysisk diagnostikk viste at Stue skannet og observerte andre BLE-enheter, men ingen nylig Xzense-annonsering. Denne testen ledet til den mindre strenge 0.5.23 og multi-proxy 0.5.24.

## 0.5.21 – 2026-10-24 – valgfri pushvarsling ved utbrenning

- Ny **Konfigurer**-meny i Xzense-integrasjonen: slå pushvarsling ved utbrenning av/på, og velg telefon.
- Bruker Home Assistants `notify`-entiteter fra Companion-appen (`notify.send_message`), med fallback til eksplisitt valgt eldre `notify.mobile_app_*`-handling.
- Varsling skjer bare etter observerte, dekodede STATUS-meldinger som viser **Operation (4) → Burnout (5)**. Ingen varsel ved oppstart, gjenopprettet cache, andre overganger eller gjentatte Burnout-svar.
- Varslingsoppgave kjøres uavhengig av Bluetooth-dataflyten. Feil ved sending logges som advarsel og avbryter ikke BLE.
- Av som standard; eksisterende tidsinnstillinger og entitets-ID-er beholdes.
- Bluetooth-proxyvalg, PIN, polling, styringskommandoer og dashboard er uendret bortsett fra et minimalt STATUS-observatørkall.
- 170 automatiserte Python-tester inkl. nye overgangs-, varslings- og API-tester. Fysisk sending til telefon må testes i Home Assistant.

## 0.5.20.2 (2026-10-23)

- La til oversettbar enum-sensor for driftstilstand uten å endre gamle statusverdier.
- La til norsk lokalisering av status på dashboardkortet; behold engelsk protokoll internt.
- Beholdt brukerens entitetsnavn «Ettergangstid» og «Gjenfyrings-tid».

## 0.5.20.1 – Norwegian entity translations

- Translate every existing entity name through `translation_key` and `strings.json` / `translations/nb.json`.
- Preserve existing entity unique IDs and raw STATUS/SELECT values. No changes to BLE, controls or dashboard.
- English translation remains available in `translations/en.json`.

## 0.5.20 – 2026-10-23 – diagnostic slim + adaptive proxy fast window

- Reduce enabled HA diagnostic entities to 12; keep full diagnostics export unchanged and preserve unique IDs for rollback.
- Automatically disable legacy excess diagnostic entities in registry; preserve core dashboard-linked diagnostic entities.
- Avoid entity-state rewrites on every raw BLE advertisement; candidates are published after scan.
- Shorten candidate collection from 3.0s to 0.8s only for fresh, strong, previously successful source (RSSI >= −75 dBm, no recent failure); default 3.0s otherwise.
- One-time fallback to full 3.0s scan if all short-window sources fail.
- Dashboard last-data timestamp fallback via live sensor attributes; JavaScript resource cache version 0520.
- No change to CONNECT, PIN, STATUS, control requests or 0.5.17 asyncio wake guard.
- Local regression tests only; device verification outstanding.

## Alpha 0.5.19.3 – slider-fiks og sekunder for aktiv drift (2026-10-23)

- Eksisterende `last_data_at`-sensor vises som **Sist oppdatert (Bluetooth)**. Dashboardets hovedskjerm viser nå lokalt klokkeslett og hvor lenge siden siste gyldige STATUS/GLOBAL-data ble mottatt; diagnostikkfanen viser samme informasjon. Ingen duplikatsensor, endret unique_id eller BLE-protokollendring.

- Home Assistant viste de to Bluetooth `number`-entitetene som tallfelt fordi vår egendefinerte ekstraattributt `mode` kolliderte med `NumberMode.SLIDER`. Attributten er endret til `bluetooth_connection_mode` for begge entitetene.
- Aktiv Bluetooth-intervall lagres i **sekunder**, 0–600 s / trinn 1 s / standard 0 s. Hvilemodus er uendret, 0–120 min.
- Tidligere aktiv intervallverdi i minutter migreres ved innlasting (eksempel 1 min → 60 s). Entitetenes unique_id-er beholdes; ny verdi skrives som `active_update_interval_seconds` ved justering.
- Scheduler bruker heltallssekunder, og diagnostikken viser både nytt sekundintervall og bakoverkompatibel minuttrapportering. Begge dashboard-kopier er synkronisert.
- Ingen endringer i BLE-pakker, CONNECT/PIN, STATUS-kommandoer, fyringslogikk eller kontrollskriving.

## Alpha 0.5.19.2 – to Bluetooth-intervaller og sammenhengende fyringsøkt (2026-10-23)

- To justerbare HA NumberEntity-slidere: Ready/hvile **0–120 minutter** (standard 5), Boosting/Operation/Afterrun/Ventilation **0–10 minutter** (standard 0 = kontinuerlig). Aktiv profil inkluderer tilstandene 3, 4, 5, 6, 7 og 8. Kontinuerlig drift sender STATUS hvert 10. sekund.
- Eksisterende entitet `bluetooth_update_interval` og lagret 0.5.19.1-intervall beholdes som hvile-slider. Ny `bluetooth_active_update_interval` legges til. Automatisk profilbytte ved ny STATUS; tilstandsendringer uten BLE oppdages ved neste tilkobling.
- Periodisk polling i Ready og kontinuerlig oppkobling under aktiv drift etter standardverdiene, med CPU-yield under transportmodusbytte. Hurtigtilkobling på knappetrykk, 15 sekunders holdetid og offline cache beholdes.
- **Afterrun → Boosting/Operation/Refuel fortsetter samme fyringsøkt**, og sletter ikke starttidspunkt/historikk. Avslutt ved Ready.
- Ved sist observerte Ready → Boosting beregnes starttid fra `Time in State`, også over et femminutters gap når tidsverdien er plausibel. Ready → Operation/Reheating bruker tilgjengelig stadietimer som estimat; Boosting-tiden kan ha blitt oversett.
- Knappen Start opptenning fra Ready lagrer et *foreløpig* tidspunkt, brukt ved senere bekreftet aktiv STATUS når den er mer informativ enn stadietimer. En avvist/mislykket sendelse forkaster dette tidspunktet. Start fra Afterrun nullstiller ikke perioden.
- Ingen endringer i Xzense-pakkeformatet eller BLE-protokollbyggere. Ikke testet mot fysisk enhet.

## Alpha 0.5.19.1 – ny fyring fra Afterrun (2026-10-23)

- Engangsversjon basert på 0.5.19. `Start lighting` er nå tilgjengelig i både Ready (2) og Afterrun (6).
- Bruker uendret firmwareavledet `BOOST/REQ start=1`; ved trykk gjennom periodisk BLE kobler integrasjonen til, henter fersk STATUS og sjekker tillatt tilstand før skriving. Xzense avgjør om kommandoen godtas.
- Regnskap over fyringsøkter splittes **først når STATUS bekrefter en overgang** fra Afterrun (6) til Boosting/Operation/Reheating (3/4/7). Tidligere økt lagres som `last_fire_duration`; ny økt får egen starttid og varighet. Lange observasjonsgap merkes som usikre.
- Innebygd kort viser «Start ny fyring» i Afterrun så lenge ingen egendefinert knappetekst overstyrer.
- Ingen endringer i Bluetooth-transport, polling, proxyvalg, løkke eller protokollrammer.
- Overgangen er **ikke fysisk bekreftet**. Ingen garantert ACK eller vellykket overgang fra panelet før den er testet.

## 0.5.19 Alpha — behovsstyrt Bluetooth og offline cache (2026-10-23)

- **0–120 minutter** som justerbar HA NumberEntity (slider) og Xzense-kortet (Konfigurasjon). `0` betyr samme kontinuerlige 10 sekunders STATUS polling som i 0.5.17; standard `5` minutter.
- Periodisk sesjon henter en fersk STATUS, venter 2 sekunder på tilleggsdata, og kobler fra. 15 sekunders oppkoblingsvindu etter styring.
- Styring kan utføres når Bluetooth er frakoblet. Ved behov: koble til → autentiser → hent fersk STATUS → valider handling → send kommando én gang. Kortere oppkobling via adapter-cache når signalet er godt; ellers full skanning.
- Sensor-cache lagres av Home Assistant og innlastes ved oppstart. Eldre sensorverdier blir værende; `stale`/`last_data_at` viser at de ikke er oppdaterte. Fortløpende timere blir ikke estimert fra eldre status.
- Diagnostikk registrerer intervall, hyppighet, planlagte frakoblinger, hurtigtilkoblingsforsøk, kommandokø og sist/neste dataoppdatering.
- Aldri automatisk gjentakelse av kontrollskriving ved uklart kvitteringssvar.
- Lokale tester (117) og JavaScript syntax/smoke; BLE-adferd ikke målt på fysisk panel.

## 0.5.18 Alpha – 2026-10-22 – justerbar STATUS-polling

- Periodisk STATUS/REQ ble **avslått som standard**; etter autentisert oppkobling ble én STATUS/REQ sendt.
- Valgbart intervall via «Konfigurer»: Av / 10 sek / 60 sek / 5 minutter. Kommandoer kunne også utløse STATUS.
- `last_observed_at`, `sample_age_seconds` og `sample_stale` for sentrale sensorer; etter 120 sekunder uten nye målinger ble data markert som gamle. Passive GLOBAL-meldinger ble fortsatt lest.
- BLE-proxyvalg, PIN og tidligere styringsfunksjoner ble beholdt. **Ikke fysisk verifisert i denne versjonen.** Se [installasjonsnotatet](arkiv/installasjon/INSTALLASJON_0.5.18.md).

## 0.5.17 Alpha — CRITICAL asyncio event-loop hotfix (2026-10-22)

- 0.5.15 and 0.5.16 affected: `_connection_loop` could enter a tight, non-yielding loop when `_wake.is_set()` remained true after a successful Bluetooth reconnect. This blocks the HA asyncio event loop and can make all HA appear crashed.
- Remove the bad immediate `continue`, consume pending event and asynchronously wait, preserving the connection-state safety check.
- Regression test exercises a pre-set wake and proves the background event loop remains responsive.
- 0.5.16 timers, BLE proxy RSSI selection and wire protocol remain otherwise unchanged.
- No physical device/HA runtime validation; 0.5.14 is advised for safest rollback.

## Alpha 0.5.16 — RSSI proxy selection, continuous timers and handoff (2026-10-22)

- Fixed 0.5.15's blind spot: ordinary `async_register_callback` drops unchanged/per-scanner suppressed advertisements, so a stronger proxy could be missing from its candidate list.
- Use `async_register_advertisement_callback` per-packet stream and `async_scanner_devices_by_address` to include every HA-known connectable scanner, with a three-second fresh collection window and direct per-adapter BLEDevice handles.
- Strictly rank by actual RSSI, without a preferred-source or recent-failure scoring bonus. The next strongest candidate remains fallback on failed connection attempts.
- Diagnostic `candidate_details` distinguishes fresh raw observations and scanner cache records; cached RSSI can be older than a current reading.
- Preserve 0.5.15's BLE-session diagnostics and disconnect safeguards, PIN and GATT command encoding. Unverified on hardware.
- `Time in current state` retains its **existing unique ID** (`state_timer`) but now returns `HH:MM:SS` instead of signed seconds. `0x1A` is interpreted as unsigned 16-bit and modulo-65536 rollover is accumulated when consistent with wall time; raw seconds, rollover count and continuity are sensor attributes and diagnostics.
- Add `Fire duration` sensor (`fire_duration`) for Boosting, Operation, Burnout, Afterrun and Refueling until returning to Ready. Starts are exact to the observed STATUS cadence when the transition is seen; an already-running fire is only counted from first observation and labelled `partial_observation`.
- Persist latest timing checkpoints, last fire duration and session start in HA `.storage` across restarts (subject to a possible short checkpoint gap if HA stops abruptly); mark ambiguity after extended Bluetooth gaps. Ventilation does not start a fire cycle.
- Update Lovelace card to display `Fyringsvarighet` and `Tid i driftstilstand` together; URL cache-busting version `v=0516` if using `/local`.
- Add dedicated synthetic rollover, lifecycle and restart tests; retain PIN and ten-second STATUS polling.

## Alpha 0.5.15 — BLE proxy ranking and disconnect tracking (2026-10-22)

- Collect fresh HA Bluetooth advertisements for 3 seconds and rank available proxy candidates using RSSI, bounded successful-source preference, and temporary failed-source penalty. Fallback to other fresh candidates remains supported.
- Track active BLE session's source and RSSI, previous successful source and up to 20 disconnect events including elapsed duration, most recent STATUS request/response, authentication status, and classification.
- Separate deliberate local shutdown/setup cleanup from unexpected BLE disconnected callbacks. The callback does not prove that Exodraft initiated a disconnect.
- Guard delayed disconnect callbacks from older BLE clients and lost wake-up events while CONNECT was in progress.
- Preserve HA entity IDs, protocol encoding, control commands, PIN exchange, and 10-second STATUS interval. Unchanged dashboard file from 0.5.14.
- Runtime on the user's physical controller remains unverified pending next diagnostic after installation.

## Alpha 0.5.14 — Temperaturprobe, diagnostikk og dashboard

- Viderefører samtlige endringer i 0.5.12b/0.5.13 (Refuel i Operation og Burnout, statusetiketter og gyldig manifest-versjon).
- Eksperimentell På/Av-bryter for Temperature probe via GLOBAL 0x56 (0=Av / 1=På). Skriveverdiene må verifiseres fysisk. Av deaktiverer automatisk temperaturbasert start/stopp; vis forsiktighet.
- Begrenser diagnostikksensorenes tilstand til 255 tegn. Global values eksponerer alle felter via attributter og fortsatt gjennom HA-diagnostikken; full Bluetooth-feiltekst ligger i attributten full_value.
- Eget dashboardkort `www/xzense-card.js` med norsk panel-lignende visning, funksjonsstyring og visuell entitetskobling i Lovelace-kortredigeringen.
- Endrer IKKE Bluetooth-tilkobling, avlesningsintervall, PIN- eller GATT-protokoll.

## Alpha 0.5.13 (manifest compatibility fix)

- Version string changed from `0.5.12b` to standards-compliant numeric `0.5.13` in `manifest.json`, and synchronized with `const.py`.
- Otherwise byte-identical integration runtime code to Alpha 0.5.12b. All previous controls and diagnostics retained.

## 0.5.12b Alpha — minor Refuel and raw-status label revision

- Refuel button available in state 4 **Operation** and state 5 **Burnout**. Sends the same BOOST/REQ start=1; state-4 controller behavior is not yet live-verified.
- Renamed display titles: `Power source (?)` -> `0x05 status` and `Signal strength` -> `0x18 status`.
- `0x05 status` now returns only the raw integer (not an assumed power-source enum or `Unknown (x)` text).
- Preserved existing Home Assistant unique IDs (`battery`, `signal_strength`) and all BLE communication/session logic.
- No changes to GLOBAL transport, STATUS polling, ChimneyLog research or other controls.

## 0.5.12 — alarm temperature configuration and ChimneyLog research

- Added writable Alarm temperature number (GLOBAL `0x58`, 150–400 °C in 0.1 °C steps, value/10), with on-device confirmation pending.
- System control selector moved into HA Configuration via entity category.
- Added non-writable diagnostic Refire / Reboost time (`0x59`) and Burnout time (`0x5B`); `/60` minutes **candidate** display, raw diagnostics retained. Unknown writing bounds prevent safe exposure as CONFIG number fields.
- Removed visible Actual chimney draught (raw) and redundant Burnout raw sensor; raw globals unchanged in diagnostic JSON.
- Documented firmware / Flutter ChimneyLog evidence (log filenames, fan/temperature/pressure debug format, `burnCount`, `operationTime`, BLE file transfer details). No FILE_TRANSFER writes were added.

### Supplerende originalnotater for 0.5.12

- New CONFIG number entities: Alarm temperature (`0x58`, 150–400 °C), Refire/Reboost time (`0x59`, seconds shown as minutes), Burnout timeout (`0x5B`, seconds shown as minutes); panel editability of both timers reported by the user, but HA writes unverified.
- Two time-setting limits are signed 16-bit transport bounds (0–546.1 min, 0.1-min step), not controller-safe recommended ranges.
- Moved System control to Configuration; removed duplicate Actual chimney draught raw sensor while preserving raw protocol values.
- Replaced misleading `0x05=2` Battery / `0x05=3` External power assertions with `Unknown (raw)` until exact enum/power-detection behavior is verified on the hardwired installation.
- Documented ChimneyLog/ErrLog static firmware and app evidence; did not add experimental FILE_TRANSFER requests.

## Alpha 0.5.11 update (2026-10-21)

- Removed non-functional Bluetooth release-to-app button, timer and associated BLE pause logic.
- Combined Boost on/off into one Boost switch; removed redundant Finish firing button. Stop firing retains its Afterrun transition through GLOBAL 0x19=6.
- Boost and Ventilation switches follow authenticated STATUS state (Boost state 3; Ventilation state 8). Boost state 7 is unresolved and retains last known value.
- Switch state is restored across HA restarts and retained across BLE reconnects until the first valid fresh STATUS frame. CONNECT/ACK immediately triggers the existing STATUS polling loop; command ACK alone does not determine switch state.
- Fan speed GLOBAL 0x50 is available in all connected states; firmware may still enforce its own restrictions.
- Controls are normal entities, configuration settings categorized CONFIG; device-page display ordering remains Home Assistant controlled.
- GitHub release source zip built from this tree; local tests do not substitute for on-device validation.

## 0.5.10 Alpha — fan-speed setpoint enabled in Ventilation (2026-10-21)

- Verified from live Ventilation (state 8) diagnostics that GLOBAL `0x50` was raised 10→16 in 1% increments; STATUS reported 16% actual fan speed.
- Renamed the existing `user_fan_speed` HA number to **Fan speed** and allowed it in states 4 (Operation) and 8 (Ventilation); a write-time state recheck prevents writes outside these states.
- Renamed the separate `0x1F` read-only sensor to **Actual fan speed**. Both entity feature keys and unique IDs remain stable.
- Preserved 10–100% bounds, GLOBAL wire payload encoding, Bluetooth connection/authentication, Ventilation packet `0x09`, Boost and all other controls. Actual HA speed write while in Ventilation remains to be physically tested.

## 0.5.9 Alpha — defer external start/speed settings (2026-10-21)

- Removed `external_start` (GLOBAL `0x57`) and `external_fan_speed` (GLOBAL `0x5A`) from the active feature registry and feature matrix at user request.
- Kept 0.5.8's entity-registry cleanup for any old copies of those controls; they were already non-exposed in 0.5.8.
- Retained the raw GLOBAL values and labels in protocol diagnostics and the archival protocol manifest for future reverse engineering.
- Preserved the verified Power source sensor (GLOBAL `0x05`), the Ventilation switch (packet `0x09`), and all BLE/controller command behavior unchanged.
- Added regression tests enforcing the deliberate exclusion while retaining raw diagnostic data.

## 0.5.8 Alpha — housekeeping over 0.5.7 (2026-10-21)

- No changes to BLE connection, authentication, polling or confirmed write-frame logic.
- Removed unavailable/never-functional UI entities: Burn count, Operation time, Error log, Language, Download log and duplicate GLOBAL 0x51 raw.
- Candidate setting controls (0x56-0x5A) remain in feature registry and full diagnostics but are no longer created as permanently unavailable HA entities.
- Reclassified legacy debug labels for GLOBAL 0x00-0x04 to UNKNOWN. Removed unobserved 0xFF legacy Burnout alias. All raw numeric GLOBAL data remains intact.
- Dropped the unused shadow PLATFORMS constant with nonexistent update platform.
- Added precise entity-registry cleanup for the nonfunctional placeholders; preserved current working entity IDs and legacy compatibility domain.
- Kept protocol history in CHANGELOG and PROTOCOL_NOTES for reference instead of exposing unimplemented placeholders.

## 0.5.7 Alpha

- Built directly from the tested 0.5.6 source package; BLE discovery/reconnect/PIN/session/BLE-release methods remain hash-locked to the 0.5.5 implementation.
- Re-analysed the controller firmware bundled with official Xzense 5.0.5; the image identifies itself as **v4.10_RC2**.
- Corrected the v4.10 state map: `1=Setup`, `2=Ready/IDLE`, `3=Boosting`, `4=Operation`, `5=Burnout`, `6=Afterrun`, `7=Refueling/Reheating`, `8=Ventilation`, `9=Error`, `10=Upgrading`.
- Corrected **Refuel** gating: state 5 Burnout sends BOOST `0x08 start=1`; Reheating/Refueling is state 7.
- Corrected **Stop firing**: state 3/7 sends BOOST `start=0`; state 4/5 transitions to Afterrun with GLOBAL `0x19=6`.
- Corrected **System control** from the 0.5.6 provisional `0x56` mapping to v4.10 direct binding **GLOBAL `0x55`**. GLOBAL `0x56` is Temperature sensor and remains write-locked.
- Restored **Operation fan speed** as GLOBAL `0x50`, direct 10-100 %, based on direct v4.10 Fan Control UI code plus the earlier physical write probe. The HA number is available only in state 4 Operation.
- Shifted the remaining v4.10 service candidates: `0x57` External start, `0x58` Alarm setpoint, `0x59` Reboost/refire time, `0x5A` External fan speed, `0x5B` Burnout timeout; these remain read-only.
- Reclassified GLOBAL `0x51` as firmware-derived Actual draught but leave it raw/read-only until scaling is live-confirmed.
- Documented that the v4.10 image contains a stale legacy GLOBAL debug-name table; direct v4.10 UI bindings and live correlations take precedence.

## 0.5.6 Alpha

- Built directly from the tested 0.5.5 source package.
- Preserved the complete BLE discovery/reconnect/session-acquisition and **Release Bluetooth to app** method implementations byte-for-byte at method level; regression hashes enforce this.
- Promoted **Start lighting** to a state-gated control: state 2 uses BOOST `0x08`, `start=1`.
- Promoted **Refuel** to a state-gated control: state 4 uses the same BOOST `0x08`, `start=1`, matching the controller firmware's Reheating path.
- Added context-aware **Stop firing**: state 3/5 sends BOOST `start=0`; state 4 transitions to Afterrun with GLOBAL `0x19=6`.
- Added explicit **Finish firing** button for Operation -> Afterrun via GLOBAL `0x19=6`.
- Added **Ventilation** switch using firmware-derived packet `0x09` with a one-byte start/stop flag; ACK/NACK diagnostics and last ACK-confirmed switch state are recorded.
- Promoted **System control** GLOBAL `0x56` to a writable select with firmware-derived enum `0=Manual`, `1=eXotelligence`, `2=Pressure controlled`.
- Added protocol/regression tests for Ventilation payloads, System control enum and the 0.5.5 connection-code boundary.
- No writes were enabled for unidentified `0x35`, `0x36`, `0x50`, `0x51`, `0x55` or candidate `0x57`-`0x5B` fields.

## 0.5.5 Alpha

- Built from the preserved 0.5.3 Alpha source baseline; the discarded 0.5.4 regression build is not used.
- Preserved the 0.5.3 BLE connection strategy and **Release Bluetooth to app** helper unchanged.
- Added live-correlated `0x32=Sound`, `0x33=Contrast` and `0x34=Brightness`.
- Corrected the setup block: `0x4B` Start temperature, `0x4C` Stop temperature, `0x4D` Boost time, `0x4E` Afterrun time and `0x4F` Boost speed.
- Corrected `0x52` Boost stop temperature, `0x53` chimney draught setpoint and `0x54` minimum fan voltage.
- Added native HA scaling: tenths °C -> °C and wire seconds -> minutes.
- Added manual-backed UI ranges for the settings whose ranges are published by Exodraft.
- Added verified power-source decoding: `0x05=2` Battery and `0x05=3` External power.
- Preserved firmware formatting from 0.5.3: CONNECT ACK `410` is shown as `4.10`.
- Removed all write access from unidentified `0x35`, `0x36`, `0x50`, `0x51`, `0x55` and from unverified `0x58`-`0x5B` candidates.
- Added disabled raw diagnostic sensors for `0x35`, `0x36`, `0x50`, `0x51` and `0x55`.

## 0.5.4 – forkastet feilbygg (historisk)

- Denne revisjonen er dokumentert som **feilbygg fra 0.4.6** og skal ikke installeres. Ingen verifisert komplett original ZIP finnes i repoet.

## 0.5.3 Alpha

- Added **Release Bluetooth to app** button. It disconnects Home Assistant from the Xzense control panel without sending any Xzense control command.
- Added local **Bluetooth app release time** number entity, adjustable from 1 to 600 seconds (default 60 seconds) for test use.
- While released, the integration suppresses its reconnect loop; when the timer expires it automatically resumes the existing fresh-advertisement connection strategy.
- Added BLE release state/counters to diagnostics.

## 0.5.2 — Xzense Alpha

- Renamed the user-facing integration from **Xzense Full Preview** to **Xzense Alpha** while retaining the `xzense_full_preview` domain for compatibility.
- Corrected GLOBAL `0x50` to **Fan speed setpoint** after a successful physical write test; values are direct percent.
- Rejected the previous `0x52` manual/user fan-speed mapping and returned it to unknown/read-only status.
- Corrected GLOBAL `0x54` to **Minimum fan voltage** after live observations at 80 V and 105 V.
- Returned `0x55` to unknown/read-only status.
- Bounded the verified fan-speed setpoint to 10-100 % and minimum fan-voltage test control to the documented 80-120 V service range.
- Updated protocol labels, feature matrix and tests to match the current live evidence.

## 0.5.1

- Corrected the interface-setting test mappings from a live panel cross-check.
- GLOBAL `0x34` is now treated as **Contrast** with a 0-100 % Home Assistant number control; panel contrast around 70 matched raw `68`.
- GLOBAL `0x33` is no longer labelled Volume and is no longer writable; panel sound was `0` while raw `0x33` was `75`, disproving the previous direct-volume mapping.
- Other experimental numeric GLOBAL controls remain raw signed-int16 until individually calibrated.
- No change to verified BOOST on/off behavior.

## 0.5.0 — experimental raw-write branch

- Branched from 0.4.7; 0.4.7 remains the stable test package.
- Enabled direct signed-int16 GLOBAL writes for selected recovered numeric setting IDs.
- Added raw write entities for Volume `0x33`, Contrast `0x34`, Brightness `0x35`, and Language `0x4B`.
- Opened existing numeric setting globals `0x4C-0x50`, `0x52-0x55`, and `0x59-0x5B` for raw writes.
- Removed guessed percentage scaling from experimental number entities; displayed values are the exact raw wire values.
- Added GLOBAL write request diagnostics (request count, ID, raw value, request/response timestamps).
- Kept System control `0x56`, Temperature sensor `0x57`, External start `0x58`, Ventilation `0x09`, BLE enable `0x36`, runtime/status values and Actual draft `0x51` write-locked.
- Boost On/Off remains separately live-verified.

## 0.4.7

- Firmware version is now read from `connect_ack_version`; observed raw `410` is exposed as `4.10`.
- Renamed device state `2` from `Standby` to `Ready for lighting` based on the Xzense operating sequence.
- Added manual-supported state labels `4 = Operation` and `5 = Refueling`; live verification is still pending for these two states.
- Removed the obsolete `Weather station` binary-sensor placeholder. The manual's Weather page is a presentation of outside temperature, chimney temperature and air pressure, which are already exposed separately.
- Removed the obsolete firmware-update scaffold; the integration now exposes the known firmware value as a read-only sensor.
- Added registry cleanup for stale `Chimney state`, `Weather station` and old `Firmware` placeholder entities from earlier preview builds.
- Kept `0x51 Actual draft` unchanged; raw zero is not hard-coded as “XTP not connected”.
- No new write commands were enabled. Boost On/Off remain the only write-ready controls.
- Retains the Xzense icon assets added in 0.4.6.

## 0.4.6

- Added bundled Xzense icon assets (`icon.png`, `logo.png`, and integration-local `custom_components/xzense_full_preview/icon.png`).
- No functional protocol or control changes from 0.4.5.

## 0.4.5

- Removed the global write lock by setting `CONTROL_WRITES_ENABLED = True`.
- Write access is still limited to features explicitly marked `write_ready`; unknown mappings remain unavailable.
- Added the first state-2 label (`Standby` at the time; corrected to `Ready for lighting` in 0.4.7).
- Kept Boost packet handling enabled.

## 0.4.4

- Removed the v0.4.3 experimental volume/fan write probes and their Afterrun gates.
- Added dedicated **Boost on** and **Boost off** buttons.
- Statically verified controller packet type `0x08` as `BOOST` from the bundled firmware.
- BOOST request uses active session ID + start/stop byte + current raw inside temperature.
- Added BOOST ACK/NACK/request diagnostics and immediate STATUS refresh after a command.
- All non-Boost control writes remain disabled.

## 0.4.3

- Confirms device state `6` as **Afterrun** from a synchronized live capture.
- Reclassifies GLOBAL/STATUS `0x1A` as **time in current state**; the value reset at the state transition and advanced about once per second.
- Confirms GLOBAL/STATUS `0x1B` as **air pressure in hPa**; user confirmed raw `1011` = **1011 hPa**.
- Corrects the 14-byte STATUS layout accordingly.
- Keeps state `3` = **Boosting**, `0x1E` = chimney temperature `/10`, and `0x1F` = actual fan speed `%`.
- Keeps all normal control writes disabled.
- Adds two explicit experimental write-probe buttons:
  - volume no-op: writes the existing `0x33` value back unchanged;
  - fan candidate probe: only in Afterrun below 60 °C with actual fan <=20 %, temporarily changes GLOBAL `0x50` by +10 (max 30), samples STATUS for about five seconds, then restores the original value.
- Records GLOBAL ACK/NACK and probe results in diagnostics.

## 0.4.2

- Calibrated chimney temperature and actual fan speed from synchronized live values.
- Corrected temperature scaling and left GLOBAL `0x20` unidentified.

## Tidlige prototyper 0.1.0–0.4.1 (2026)

De tidlige filene stammer fra de første Xzense-samtalene. Arkivene og revisjonsetikettene er dokumentert i [REVISJONER.md](REVISJONER.md), med originalfiler under [historisk/](arkiv/tidlige-versjoner/README.md).

- **0.1.0:** Første lesende BLE-diagnostikk uten styringskommandoer.
- **0.2.0–0.2.8:** PIN-konfigurasjon, forskjellige GATT-/pairing-forsøk, ferske annonseringer og deretter CONNECT/ACK.
- **0.3.0:** STATUS/REQ og de første live-sensorene. Separat lab- og preview-variant for protokolltesting.
- **0.3.1 / 0.3.2:** Eksperimentelle hardkodet-PIN-/no-auth-tester i `historisk/IKKE_INSTALLER/`. **Skal ikke installeres.**
- **0.4.0:** Full Preview-domene og funksjonsskjelett, skrivekommandoer sperret.
- **0.4.1:** 14-byte STATUS/ACK fra fysisk panel kartlagt.

Dette er dokumenterte historiske utgaver, ikke anbefalte installasjoner.

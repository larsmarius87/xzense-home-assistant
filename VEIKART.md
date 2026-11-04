# Xzense development roadmap / Veikart

**Current HACS development version / Gjeldende HACS-versjon: 0.5.28**

This page describes future work; it is not a list of completed features. / Denne siden beskriver planlagt arbeid, ikke ferdige funksjoner.

## English

### Available in the 0.5.28 HACS test

- Integration name and domain: **Xzense / `xzense`**
- HACS repository layout and automated syntax/structure checks
- Native entity icons for Start, Stop, Refuel, Boost and RS009-41 motor type
- Norwegian last successful Bluetooth synchronization sensor label: **Sist BT-synk**
- Existing BLE controls and multi-proxy fallback from corrected 0.5.27

### Priorities

1. Validate long-term BLE stability and physical operation of 0.5.28.
2. Review and verify advanced write commands and status-dependent controls before describing them as fully tested.
3. Check translations, icons, entity naming and diagnostic availability for regressions.
4. Continue to improve tests and release notes for HACS installations.

### Planned later

- **Home Assistant firing-session log:** Count and summarize firing sessions, durations, phases, refueling actions and temperatures. A session ends only when the controller returns to **Ready for lighting (state 2)**. Preserve active sessions across HA restarts and temporary BLE disconnections.
- **Deferred:** Exodraft internal log-file decoding, `FILE_TRANSFER 0x0C`, ChimneyLog, burn count and operation time from firmware history.

## Norsk

### På plass i HACS-testen 0.5.28

- Integrasjonsnavn og domene: **Xzense / `xzense`**
- HACS-mappestruktur og automatiske kontroller av syntaks og struktur
- Egne entitetsikoner for Start fyring, Avslutt fyring, Legg inn ved, Boost og Viftetype RS009-41
- Kortere norsk sensornavn: **Sist BT-synk**
- Eksisterende Bluetooth-styring og automatisk proxy-reservevalg fra korrigert 0.5.27

### Prioritert videre arbeid

1. Teste Bluetooth-stabilitet og funksjoner over tid på fysisk enhet.
2. Verifisere avanserte skrivekommandoer og tilstandsavhengig styring før de omtales som ferdig testet.
3. Kontrollere oversettelser, ikoner, entitetsnavn og diagnostikk mot tidligere rettelser.
4. Forbedre automatiske tester og versjonsinformasjon for HACS.

### Senere

- **Egen fyringslogg i Home Assistant:** Registrere og oppsummere fyringsøkter, varighet, driftsfaser, vedpåfyllinger og temperaturer. En økt avsluttes først når kontrolleren kommer tilbake til **Klar for fyring (tilstand 2)**. Bevare pågående økter gjennom HA-omstart og midlertidige BLE-avbrudd.
- **Utsatt:** Dekoding av Exodrafts interne loggfiler, `FILE_TRANSFER 0x0C`, ChimneyLog, burn count og operation time fra kontrollpanelets interne historikk.

## Verified protocol observations / Bekreftede protokollfunn

- GLOBAL `0x04`: control-panel battery / batterinivå kontrollpanel
- GLOBAL `0x05`: radio link between panel and power unit (0–3) / radiolink mellom panel og kraftenhet (0–3)
- Refueling in the correct controller state has been physically tested / vedpåfylling ved riktig driftstilstand er testet på fysisk panel

See the [README](README.md) and [protocol notes](docs/PROTOCOL_MANIFEST.md) for context. / Se [README](README.md) og [protokolloversikten](docs/PROTOCOL_MANIFEST.md) for detaljer.

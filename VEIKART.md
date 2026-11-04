# Xzense – planlagt videre arbeid

Oppdatert 4. november 2026. Dette er **planer**, ikke funksjoner som er ferdig implementert i 0.5.27.

## Neste bygg (foreløpig 0.5.28)

- Fjerne «Alpha» fra visningsnavnet og rydde opp i historiske navn.
- Forberede distribusjon via GitHub og HACS med en ryddig release-struktur. HACS-installasjon må testes før den annonseres som støttet.
- Vurdere å endre integrasjonsdomene og mappe fra `xzense_full_preview` til `xzense`. **Dette krever migreringsdesign og testing** slik at eksisterende config entries, PIN, options, enheter og entitets-ID-er ikke går tapt. Ikke bare gi mappen nytt navn.
- Egne ikoner på knappentitetene i integrasjonen: «Start fyring» = `mdi:fire`, «Avslutt fyring» = `mdi:fire-off` (finn faktisk entitetsnavn før endringen).
- Kontrollere ikon-, navn- og oversettelsesregresjoner mot 0.5.25 final og korrigert 0.5.27.
- Oppdatere faktisk README, changelog og release-instruksjoner sammen med koden.

## Bekreftet protokollfunn (dokumentasjon)

- GLOBAL `0x04`: batterinivå på panelet bekreftet.
- GLOBAL `0x05`: radiolink panel ↔ kraftenhet bekreftet (nivå 0–3).
- Refueling ved riktig tilstand er fysisk testet og fungerer.

## Senere, når integrasjonen er stabil

**Egen fyringslogg i Home Assistant**: Én økt starter ved overgang fra «Klar for fyring» (tilstand 2) til fyring og avsluttes først når panelet er tilbake til «Klar for fyring». Boost, Drift, Utbrenning, Vedpåfylling og Ettergang inngår i samme økt. Registrer tidspunkt, varighet, tilstandsvarighet, antall påfyllinger/Boost, temperatur og viftedata. Bevar pågående økter over HA-omstart og periodiske BLE-avbrudd. Logg egne øktoppsummeringer uavhengig av Recorder-opprydding.

**Satt på vent**: Dekoding av interne Exodraft-loggfiler, `FILE_TRANSFER 0x0C`, ChimneyLog, Burn count og Operation time fra panelets interne historikk. Ingen eksperimentell logguthenting skal inn i neste bygg.

## Kvalitetssikring

- Bygg på korrigert 0.5.27, ikke på en ufullstendig tidligere RC.
- Behold tester for fyringsstyring, BLE-hvile/aktiv drift, proxy-fallback og ikon-/oversettelsesregresjoner.
- Ingen firmwareendringer, uverifiserte GLOBAL-skriveoperasjoner eller utilsiktet registermigrering.

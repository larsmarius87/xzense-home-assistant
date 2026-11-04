# Xzense for Home Assistant

Uoffisiell integrasjon for **Exodraft Xzense**. Lar Home Assistant lese status og styre utvalgte funksjoner på kontrollpanelet via Bluetooth Low Energy (BLE).

**Nyeste testversjon: 0.5.27 (korrigert)** · Kontrollerfirmware testet: 4.10_RC2

> Prosjektet er under utvikling. Den korrigerte 0.5.27-pakken er tilgjengelig, men er ikke fullstendig langtidsverifisert. 0.5.25 RC1 er tidligere bekreftet fungerende og beholdes som tilbakefallsversjon.

## Last ned

**[Last ned Xzense 0.5.27 (ZIP)](https://github.com/larsmarius87/xzense-home-assistant/blob/main/xzense-alpha-0.5.27-source.zip)**

- [Installasjonsveiledning](https://github.com/larsmarius87/xzense-home-assistant/blob/main/INSTALLASJON_0.5.27.md)
- [Endringslogg](https://github.com/larsmarius87/xzense-home-assistant/blob/main/CHANGELOG.md)
- [Alle revisjoner og eldre versjoner](https://github.com/larsmarius87/xzense-home-assistant/blob/main/REVISJONER.md)

**0.5.27 ligger nå på hovedgrenen `main`.** HACS-installasjon er ikke tilgjengelig ennå.

## Funksjoner

- **Status:** Driftstilstand, skorsteinstemperatur, inne- og utetemperatur, lufttrykk, faktisk viftehastighet, batterinivå og radiolink mellom panel og kraftenhet.
- **Styring:** Start fyring, avslutt fyring, Boost, ventilasjon og vedpåfylling. Vedpåfylling er avhengig av riktig driftstilstand i kontrolleren.
- **Innstillinger:** Blant annet temperaturgrenser, Boost-tid, ettergangstid, viftehastighet og kontrollpanelinnstillinger.
- **Bluetooth:** Bruker Home Assistants Bluetooth-adaptere og ESPHome-proxyer, med automatisk kildevalg og fallback. Separate oppdateringsintervaller for hvile og aktiv drift.
- **Varsling:** Valgfri melding til én eller flere telefoner når Xzense går fra Drift til Utbrenning.
- **Dashboard:** Eget Xzense-kort med norsk tekst, status og relevante kontroller.

## Installere eller oppdatere

1. Ta backup av Home Assistant og den eksisterende Xzense-mappen.
2. Pakk ut [ZIP-filen](https://github.com/larsmarius87/xzense-home-assistant/blob/main/xzense-alpha-0.5.27-source.zip) og kopier `custom_components/xzense_full_preview` til `/config/custom_components/`.
3. Kopier `www/xzense-card.js` til `/config/www/` dersom du bruker dashboardkortet. Kontroller ressursadressen `/local/xzense-card.js?v=0527`.
4. Start Home Assistant på nytt og sjekk tilkobling, status, entiteter og kontrollfunksjoner.

**Viktig:** I 0.5.27 er integrasjonsdomenet fortsatt `xzense_full_preview`. Ikke gi mappen nytt navn eller slett den eksisterende integrasjonen. Se [installasjonsveiledningen](https://github.com/larsmarius87/xzense-home-assistant/blob/main/INSTALLASJON_0.5.27.md) for detaljer og tilbakefall.

## Neste steg

Til neste større oppdatering planlegges:

- Kortere integrasjonsnavn **Xzense**, uten «Alpha».
- Tilrettelegging for installasjon og oppdateringer gjennom **HACS**.
- Sikker migrering fra `xzense_full_preview` til `xzense`, hvis eksisterende konfigurasjon og entiteter kan bevares.
- Egne ikoner på knappene for å starte og avslutte fyring.

En egen **fyringslogg i Home Assistant** er planlagt senere. En fyringsøkt avsluttes først når kontrolleren returnerer til «Klar for fyring». Arbeid med Exodrafts interne loggfiler er satt på vent.

Se [veikartet](https://github.com/larsmarius87/xzense-home-assistant/blob/main/VEIKART.md) for mer informasjon.

## Dokumentasjon

| Dokument | Innhold |
|---|---|
| [CHANGELOG](https://github.com/larsmarius87/xzense-home-assistant/blob/main/CHANGELOG.md) | Alle registrerte endringer og korrigeringer |
| [REVISJONER](https://github.com/larsmarius87/xzense-home-assistant/blob/main/REVISJONER.md) | Versjonsarkiv og tidligere ZIP-pakker |
| [Protokolloversikt](https://github.com/larsmarius87/xzense-home-assistant/blob/main/docs/PROTOCOL_MANIFEST.md) | Kartlagte BLE-/GLOBAL-verdier og verifiseringsstatus |
| [Funksjonsmatrise](https://github.com/larsmarius87/xzense-home-assistant/blob/main/docs/FEATURE_MATRIX.md) | Oversikt over implementerte funksjoner |
| [VEIKART](https://github.com/larsmarius87/xzense-home-assistant/blob/main/VEIKART.md) | Avtalte planer og utsatte oppgaver |

## Sikkerhet

Dette er en uoffisiell integrasjon, ikke et produkt fra Exodraft. Home Assistant skal ikke erstatte kontrollpanelets lokale betjening, alarmer eller sikkerhetsfunksjoner. Styringskommandoer og eksperimentelle innstillinger må testes forsvarlig.

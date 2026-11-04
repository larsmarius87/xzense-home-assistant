# Exodraft Xzense – Home Assistant

Eksperimentell, lokal Home Assistant-integrasjon via BLE. Dette er et **uoffisielt testprosjekt**.

> **Nyeste testpakke: 0.5.27 (korrigert).** [Last ned ZIP](xzense-alpha-0.5.27-source.zip) · [Installasjon](INSTALLASJON_0.5.27.md) · [Endringslogg](CHANGELOG.md) · [Alle revisjoner](REVISJONER.md).
>
> 0.5.25 RC1 er siste versjon som var bekreftet stabil over tid. Refueling er senere testet på fysisk panel, men hele 0.5.27 er ikke fullstendig langtidsverifisert. **Versjonsnavnet Alpha finnes fortsatt i manifestet; fjerning og sikker domenemigrering er planlagt for 0.5.28.**

## Installere 0.5.27

1. Ta backup av Home Assistant og `/config/custom_components/xzense_full_preview/`.
2. Pakk ut [0.5.27-kildepakken](xzense-alpha-0.5.27-source.zip). Kopier `custom_components/xzense_full_preview/` til `/config/custom_components/xzense_full_preview/`.
3. Kopier `www/xzense-card.js` til `/config/www/xzense-card.js`, og bruk ressursen `/local/xzense-card.js?v=0527`.
4. Start Home Assistant på nytt og kontroller sensorer, PIN, Bluetooth og knapper. Behold det eksisterende integrasjonsdomenet `xzense_full_preview`.

**HACS er ikke klart ennå.** ZIP er fortsatt installasjonsmetoden. Automatisk oppdatering fra GitHub og mulig migrering til domenet `xzense` utredes for neste versjon. Ikke slett den gamle integrasjonen manuelt før migrering er testet.

## Nytt siden 0.5.25 RC1

- 0.5.26: Firmwarebasert Refueling bare i Utbrenning (status 5); status 7 er «Vedpåfylling».
- 0.5.26.1: Flervalg for telefonvarslinger og kompatibilitet med tidligere enkeltvalg.
- 0.5.27: «Legg inn ved», gjenopprettet Radiolink og Viftetype RS009-41, rettelser for oversettelser og dashboard.
- Korrigert 0.5.27: Boost `mdi:turbine`, viftetype `mdi:engine-outline`, varslingsteksten «Xzense: Legg i mer ved» og avgrenset opprydding av gamle diagnostikkentiteter.

**Bekreftet på fysisk panel:** Refueling virker ved riktig driftstilstand. Batteri `0x04` og radiolink `0x05` er bekreftet. Alle andre funksjoner må vurderes etter individuell teststatus.

## Hva integrasjonen gjør

- Leser tilstand, skorsteinstemperatur, inne-/utetemperatur, viftehastighet, lufttrykk og en rekke globale innstillinger.
- Bruker kontrollpanelets BLE/PIN/CONNECT-protokoll og STATUS/GLOBAL-meldinger.
- Har kontroller for blant annet Boost, Ventilation, oppstart/gjenfyring og flere innstillinger. Enkelte skrivefunksjoner er fortsatt **eksperimentelle**; ikke alle er fysisk testet.
- Støtter behovsstyrt/periodisk Bluetooth-oppkobling, separate oppdateringsintervaller for hvile og aktiv drift, og beholdte sensordata mellom økter.
- Inneholder norsk språkpakke og et panelinspirert Lovelace-kort.
- Kan valgfritt sende pushvarsel ved observert overgang **Operation (4) → Burnout (5)**; dette er av som standard.

Se [funksjonsmatrisen](docs/FEATURE_MATRIX.md), [protokollnotatene](docs/PROTOCOL_NOTES.md) og [dashboardveiledningen](dashboard/INSTALLASJON.md) for detaljer og begrensninger.

## Bluetooth i 0.5.24

- Velger automatisk blant Home Assistants tilgjengelige Bluetooth-adaptere og ESPHome-proxyer, med rangering etter RSSI.
- Bruker kildebestemte BLE-observasjoner i Home Assistant-cache dersom fersk annonsering mangler.
- Prøver neste kilde ved feil under BLE/GATT-oppkobling, med **ett forsøk per kilde og opptil seks kilder per runde**.
- Har **120 sekunders pause etter mislykkede cachetilkoblinger** for å unngå aggressive forsøk.
- Bytter ikke proxy midt i samme runde dersom BLE allerede er opprettet, men Xzense-applikasjonens ACK/STATUS senere uteblir.

Ved periodisk oppdatering er `connected: false` **normalt mellom vellykkede pollinger**. Bruk `last_status_response_at`, `selected_source`, `source_fallbacks` og `last_error` i diagnostikken ved feilsøking.

### Fysisk status 26. oktober 2026

Testen med ny Stue-proxy (M5Stack ATOM Lite) og gammel Stue viste **8/8 applikasjonsautentiseringer, 8/8 STATUS-svar, 2/2 GLOBAL-skrive-ACK-er og 0 CRC-feil**. Det var samtidig **3 kildefallbacks**. Dette bekrefter fungerende kommunikasjon i testperioden, ikke bevist døgnlang stabilitet.

## Versjoner, historikk og dokumentasjon

| Ressurs | Innhold |
|---|---|
| **[Endringslogg](CHANGELOG.md)** | Kronologiske endringer og verifiserte funn |
| **[Alle revisjoner og ZIP-arkiver](REVISJONER.md)** | Tilgjengelige utgaver fra tidlige 0.1-prototyper til 0.5.27, med nedlastingslenker |
| [Historiske prototyper](arkiv/tidlige-versjoner/README.md) | Opprinnelige 0.1–0.4-arkiver, inkludert isolerte testbygg |
| [Tidligere README](arkiv/dokumenter/README_HISTORISK_TIL_0.5.24.md) | Arkivert dokumentasjon før opprydding |
| [Tidligere CHANGELOG](arkiv/dokumenter/CHANGELOG_OPPRINNELIG_TIL_0.5.24.md) | Original endringslogg bevart for sammenligning |
| [Installasjon 0.5.24](INSTALLASJON_0.5.24_MULTI_PROXY.md) | Oppdatering og diagnose av ny multi-proxy-strategi |

**Viktig om historiske versjoner:** 0.5.15 og 0.5.16 har en dokumentert asyncio busy-loop som kan fryse Home Assistant. Ikke installer disse i et fungerende system. Versjon 0.5.22 og 0.5.23 var midlertidige **Stue-only**-tester, mens 0.5.24 støtter flere proxyer.

Noen mellomversjoner har dokumenterte endringer, men ingen verifisert original ZIP i repoet. Dette er merket særskilt i [revisjonsoversikten](REVISJONER.md); manglende kildepakker er ikke funnet på.

## Planlagt, ikke implementert

Se [VEIKART.md](VEIKART.md). Blant annet: HACS, sikker migrering til domenet `xzense`, integrasjonsnavn uten «Alpha» og knappeikoner for «Start fyring» / «Avslutt fyring». Home Assistant-basert fyringslogg er planlagt senere; interne Exodraft-loggfiler er satt på vent.

## Sikkerhet og teststatus

Xzense styrer en fysisk skorsteinsvifte. Home Assistant-integrasjonen er ikke en sikkerhetsfunksjon og skal ikke erstatte lokal betjening, kontrollpanelets alarmer eller sikker overvåkning. Test skrivekommandoer bare under trygge forhold. Ukjent GLOBAL-semantikk skal behandles som uverifisert, ikke som dokumenterte enhetsverdier.

Ingen firmwareoppdatering, reflash eller automatisk kontrollpanelendring følger av å installere denne HA-integrasjonen.

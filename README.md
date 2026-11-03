# Exodraft Xzense – Home Assistant (Alpha)

> **0.5.26 er tilgjengelig som testversjon i en egen gren/PR.** Den er basert på sist bekreftede stabile 0.5.25-rc1, med firmwarebasert Refueling og feilretting for sensorikon. [Les installasjonsveiledningen](INSTALLASJON_0.5.26.md) og [last ned kildepakken](xzense-alpha-0.5.26-source.zip). Behold RC1 som sikker tilbakefallsversjon.

Eksperimentell, lokal Home Assistant-integrasjon for **Exodraft Xzense** via Bluetooth Low Energy (BLE), med PIN-autentisering, statusavlesning, konfigurering og utvalgte styringskommandoer.

> **Gjeldende prosjektversjon: 0.5.25 Alpha (28. oktober 2026).** Dette er en utviklingsversjon, ikke en offisiell Exodraft-integrasjon. Den er testet med et fysisk kontrollpanel, men langvarig stabilitet og alle styringskommandoer er ikke fullstendig verifisert.

## Last ned og installer

**[Last ned Xzense 0.5.25 – komplett kildepakke (ZIP)](xzense-alpha-0.5.25-source.zip)**

1. Ta backup av eksisterende `/config/custom_components/xzense_full_preview/`.
2. Pakk ut ZIP-filen og kopier **hele** mappen `custom_components/xzense_full_preview/` inn i `/config/custom_components/`; erstatt filene i eksisterende mappe.
3. Start Home Assistant på nytt. Behold eksisterende konfigurasjonsoppføring, PIN og integrasjonsdomene `xzense_full_preview`.
4. Kontroller versjon **0.5.25** under integrasjonens diagnostikk, og sjekk at det kommer et nytt STATUS-svar.

Se [full installasjonsveiledning for 0.5.25](INSTALLASJON_0.5.25.md).

## Nytt i 0.5.25

- En eller flere mobiler kan motta «Xzense: Legg i mer ved» når STATUS går fra Drift til Utbrenning. Varsling er av som standard; tidligere valg av én mobil beholdes.
- «Viftetype RS009-41» begrenser minimum viftespenning til 100–120 V ved ny justering, mot 80–120 V ellers. Den skriver ikke til kontrollpanelet automatisk.
- Radiolink (0x05) vises som 0–3 signalstreker, og panelbatteri (0x04) forsøksvis i prosent. Begge tolkes foreløpig og er ikke fullstendig kalibrert.
- Boost bruker `mdi:turbine`, viftetype `mdi:engine-outline`. Gammel utilgjengelig diagnose-teststøy ryddes fra entitetsregisteret, mens rådata bevares.
- Protokolloversikt med samtlige identifiserte **0x-registre og sikkerhetsgrad** finnes i [protokollmanifestet](docs/PROTOCOL_MANIFEST.md).
- Bluetooth-transport og automatisk valg av proxy er identisk med 0.5.24.

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
| **[Alle revisjoner og ZIP-arkiver](REVISJONER.md)** | Tilgjengelige utgaver fra tidlige 0.1-prototyper til 0.5.25, med nedlastingslenker |
| [Historiske prototyper](arkiv/tidlige-versjoner/README.md) | Opprinnelige 0.1–0.4-arkiver, inkludert isolerte testbygg |
| [Tidligere README](arkiv/dokumenter/README_HISTORISK_TIL_0.5.24.md) | Arkivert dokumentasjon før opprydding |
| [Tidligere CHANGELOG](arkiv/dokumenter/CHANGELOG_OPPRINNELIG_TIL_0.5.24.md) | Original endringslogg bevart for sammenligning |
| [Installasjon 0.5.24](INSTALLASJON_0.5.24_MULTI_PROXY.md) | Oppdatering og diagnose av ny multi-proxy-strategi |

**Viktig om historiske versjoner:** 0.5.15 og 0.5.16 har en dokumentert asyncio busy-loop som kan fryse Home Assistant. Ikke installer disse i et fungerende system. Versjon 0.5.22 og 0.5.23 var midlertidige **Stue-only**-tester, mens 0.5.24 støtter flere proxyer.

Noen mellomversjoner har dokumenterte endringer, men ingen verifisert original ZIP i repoet. Dette er merket særskilt i [revisjonsoversikten](REVISJONER.md); manglende kildepakker er ikke funnet på.

## Planlagt, men ikke implementert

I **neste** revisjon er det ønsket en egen automatisk aktivert sensor for **sist vellykkede Bluetooth/STATUS-oppdatering**, vist som norsk dato og klokkeslett (for eksempel `26.10.2026 kl. 10:32:48`). Dette er **ikke** en del av 0.5.24. Eksisterende diagnostikk har `last_status_response_at`.

## Sikkerhet og teststatus

Xzense styrer en fysisk skorsteinsvifte. Home Assistant-integrasjonen er ikke en sikkerhetsfunksjon og skal ikke erstatte lokal betjening, kontrollpanelets alarmer eller sikker overvåkning. Test skrivekommandoer bare under trygge forhold. Ukjent GLOBAL-semantikk skal behandles som uverifisert, ikke som dokumenterte enhetsverdier.

Ingen firmwareoppdatering, reflash eller automatisk kontrollpanelendring følger av å installere denne HA-integrasjonen.

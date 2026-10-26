# Xzense Alpha – Home Assistant-integrasjon for Exodraft Xzense

Eksperimentell, lokal **Bluetooth Low Energy (BLE)**-integrasjon for Exodraft Xzense-kontrollpanelet. Prosjektet ble utviklet og testet gjennom samtalene *Exodraft Xzense styring* 1–3, med analyse av kontrollerdiagnostikk, app og firmware. **Nåværende kildeversjon: 0.5.24 Alpha (26. oktober 2026).**

> **Dette er ikke en offisiell Exodraft-integrasjon.** Den påvirker et fysisk peis-/skorsteinsystem. Ikke la Home Assistant være eneste sikkerhetsmekanisme, og kontroller alltid kritiske endringer på det fysiske panelet.

## Last ned og dokumentasjon

- **[Komplett kildepakke – 0.5.24](xzense-alpha-0.5.24-multi-proxy-relaxed-source.zip)**
- **[Installasjon av 0.5.24](INSTALLASJON_0.5.24_MULTI_PROXY.md)**
- **[Full endringslogg fra 0.1.0 til 0.5.24](CHANGELOG.md)**
- **[Alle dokumenterte revisjoner og kildearkiver](REVISJONER.md)**
- **[Historisk README med tekniske detaljer og GLOBAL-kart](docs/README_HISTORISK_TIL_0.5.24.md)**
- **[Firmware-/protokollnotater](CHIMNEYLOG_RESEARCH.md)** og [funksjonsmatrise](FEATURE_MATRIX.md)
- **[Dashboardkort og installasjon](dashboard/INSTALLASJON.md)**

Ingen automatisk oppdateringsmekanisme eller sikkerhetsgaranti er etablert; dette er foreløpig testbygg.

## Hva fungerer i 0.5.24?

| Område | Status |
|---|---|
| BLE via Home Assistant / ESPHome Bluetooth-proxyer | Fungerer i faktisk test |
| PIN / CONNECT / autentisert Xzense-sesjon | Bekreftet |
| STATUS, GLOBAL, temperaturer, lufttrykk, enhetstilstand og vifte | Bekreftet avlesning |
| Boost, start/stopp, refuel, Ventilation og konfigurasjonskontroller | Implementert, varierer i grad av fysisk verifikasjon |
| Periodisk Bluetooth i hvile / eget intervall under drift | Implementert |
| Lokale sensorverdier mellom BLE-oppdateringer | Implementert med tids-/stale-attributter |
| Fyringstid og tid i driftsstatus | Implementert, kan estimeres ved lange frakoblinger |
| Norsk entitets- og tilstandsoversettelse | Implementert |
| Valgfri pushvarsling ved overgang Operation → Burnout | Implementert, må aktiveres |
| Lovelace-kort som etterligner Xzense-display | Inkludert i kildepakken |
| Automatisk bytte mellom Bluetooth-proxyer | Implementert i 0.5.24 |

**Faktiske testdata 26.10.2026:** Diagnostikken viste 8/8 vellykkede Xzense-autentiseringer, 8/8 STATUS-svar, 2/2 kvitterte GLOBAL-skrivinger, ingen CRC-feil og vellykkede sesjoner gjennom både ny og eldre stue-proxy. Dette demonstrerer reell kommunikasjon, **ikke** dokumentert døgnstabilitet eller verifisering av alle mulige styringskommandoer.

## Bluetooth og proxyvalg i 0.5.24

Integrasjonen henter Xzense-observasjoner fra Home Assistants Bluetooth-kilder, rangerer tilgjengelige kilder etter målt **RSSI** og forsøker tilkobling. Ved feil under BLE-/GATT-oppsett forsøkes neste kilde innenfor begrensede rammer.

- Inntil **6 ulike kilder per oppkoblingsrunde**, høyst **ett BLE-forsøk per kilde**.
- Hvis ingen fersk annonsering oppdages, kan den etter 3 sekunder bruke **kildebestemte** tidligere BLE-observasjoner fra Home Assistant.
- Mislykkede cacheforsøk får 120 sekunders pause per kilde.
- Ingen hardkodet adresse eller Stue-lås.
- Fallback ved manglende *applikasjons*-CONNECT/ACK eller STATUS **etter** etablert GATT blir ikke nødvendigvis prøvd i samme runde.

**Periodisk drift:** `connected: false` mellom polling-sykluser er normalt. `local_periodic_poll` i `disconnect_history` viser planlagt frakobling. Det er feil, timeout, autentiseringssvikt eller manglende STATUS som må undersøkes – ikke bare at BLE er frakoblet i hvile.

## Installering / oppgradering

1. Ta backup av eksisterende `/config/custom_components/xzense_full_preview/` og gjerne Home Assistant-konfigurasjonen.
2. Last ned [0.5.24-kildepakken](xzense-alpha-0.5.24-multi-proxy-relaxed-source.zip).
3. Pakk ut ZIP og erstatt **hele** mappen `custom_components/xzense_full_preview/` i Home Assistant.
4. Start Home Assistant på nytt. Ikke slett integrasjonsoppføringen for å oppgradere.
5. Kontroller i nedlastet Xzense-diagnostikk at både `custom_components.xzense_full_preview.version` og `integration_manifest.version` viser `0.5.24`.
6. Se at PIN-autentisering og STATUS svarer, og sammenlign fysisk panel med HA. Kontroller eventuelle styrekommandoer forsiktig.

**Kompatibilitet:** Integrasjonsdomenet må fortsatt hete `xzense_full_preview` selv om visningsnavnet er **Xzense Alpha**. Ikke kopier eldre `custom_components/xzense` eller `xzense_preview` over dagens mappe uten migrering.

## Konfigurering og dashboard

- I **Innstillinger → Enheter og tjenester → Xzense Alpha → Konfigurer** ligger blant annet valgfri utbrenningsvarsling.
- Under Xzense-enhetens tallentiteter finner du BLE-intervaller for hvile og aktiv drift. Standard er normalt 5 minutter i hvile og kontinuerlig kommunikasjon ved aktiv drift, avhengig av lagrede innstillinger.
- Dashboardkortet leveres i kildearkivet og kan brukes som `/api/xzense_full_preview/xzense-card.js` eller ved manuell kopi til `/config/www/xzense-card.js`, avhengig av oppsett. Se [kortets installasjon](dashboard/INSTALLASJON.md).
- Full diagnostikk er tilgjengelig fra **Last ned diagnostikk** i Home Assistant selv om de fleste diagnostikk-entitetene er deaktivert.

## Diagnostikk

Ved Bluetooth-problemer er disse feltene mest relevante:

| Diagnostikkfelt | Betydning |
|---|---|
| `candidate_sources` / `candidate_details` | Alle kilder Xzense er observert fra og eventuell lagret RSSI |
| `selected_source` | Hvilken kilde som ble valgt i siste forsøk |
| `source_fallbacks` / `last_failed_source` | Om og hvor fallback ble nødvendig |
| `application_auth_success_count` | Vellykkede PIN/CONNECT-autentiseringer |
| `status_request_count` / `status_response_count` | Om STATUS-forespørsler faktisk får svar |
| `disconnect_history` | Årsaksklassifisering, varighet og om STATUS var mottatt |
| `crc_errors` / `invalid_frames` | Mulige protokollfeil |
| `last_status_response_at` / `last_data_at` | Når siste godkjente telemetri ble mottatt |

**Ønsket til senere revisjon (ikke i 0.5.24):** Egen, automatisk aktivert HA-sensor som viser siste **vellykkede STATUS-oppdatering** som norsk lokal dato og klokkeslett, også når periodisk BLE er frakoblet. Dette er kun planlagt; ingen kodeendring er inkludert her.

## Versjonshistorikk og sikkerhet

**[REVISJONER.md](REVISJONER.md)** har en versjon-for-versjon-oversikt og lenker til tilgjengelige source-ZIP-er. **[CHANGELOG.md](CHANGELOG.md)** inneholder detaljert historikk, inkludert tidlige BLE-eksperimenter fra 0.1-/0.2-/0.3-seriene, korreksjoner i GLOBAL-kartet og BLE-optimalisering gjennom 0.5.24.

**Ikke installer 0.5.15 eller 0.5.16.** En bekreftet busy-loop kan blokkere Home Assistants asyncio-eventløkke. **Ikke installer 0.5.4**, som var feilbygd fra eldre grunnlag. De tidlige 0.3.1-/0.3.2-pakkene er spesialiserte auth-/no-auth-prober, ikke daglige driftsversjoner.

Firmware-/protokollkartleggingen er eksperimentell. Ikke utled sikre driftstemperaturer eller fysisk sikkerhet fra rå 16-bit globale verdier. Gjør ikke endringer under aktiv fyring hvis det kan redusere trekk eller skape røykfare.

## Om repoet

Dette repoet er et **historisk kildearkiv**, ikke et ferdig vedlikeholdt HACS-produkt. Noen eldre versjoner har andre domener/filstrukturer, og et kildearkiv kan inneholde filer som kun var beregnet for den historiske prototypen. Test mot riktig HA-versjon og ta backup før eventuell tilbakerulling.

# FOR NESTE: Xzense Alpha 0.5.25

**Oppdatert:** 27. oktober 2026  
**Status:** Planlagt. **Ingenting i dette dokumentet er implementert eller publisert som 0.5.25.**  
**Gjeldende testversjon:** 0.5.24 Multi-proxy Relaxed, med fungerende M5Stack ATOM Lite (stue2).  
**Formål:** Samle beslutninger, protokollfunn og åpne verifikasjoner til neste byggeøkt.

## 1. Avtalte endringer for 0.5.25

- [ ] **Temperaturgrenser:** Oppdater min/maks for justerbare temperaturer etter de mest presise funnene i firmware og manual. Dokumenter grensene per register før koden endres; ikke anta at rå signed-int16-grense er en sikker brukergrense.
- [ ] **Start-/stopptemperatur:** Håndhev minimum **6,0 °C** avstand, også med desimaler. Starttemperatur må være minst stopptemperatur + 6 °C. Dynamiske grenser begge veier og sikker avvisning ved skriving. Behold eksisterende verdi hvis den allerede er gyldig.
- [ ] **Boost-stopptemperatur (GLOBAL 0x52):** Bruk **60 °C som vår oppgitte standard-/referanseverdi**, med min/maks fra firmwaren. Ikke tving eksisterende installasjon til 60 °C ved oppdatering.
- [ ] **Fabrikkverdier:** Vis produsentens dokumenterte fabrikkoppsett som informasjon (for eksempel beskrivelse/attributter/hjelpetekst). Skill mellom fabrikkstandard, vår valgte standard (60 °C) og panelverdiene som er lagret hos brukeren. Ikke legg inn automatisk fabrikkreset.
- [ ] **Batteri (GLOBAL 0x04):** Vis en ordinær sensor i prosent. Firmware-tabellen kaller feltet BATTERY; verdi 100 og senere 90 samsvarer med fall i batteriikonet. Ingen batterivarsling. Verifiser kilde og identitetsmigrering fordi eldre integrasjoner har brukt et misvisende batteri-/status-entitetsnavn for GLOBAL 0x05.
- [ ] **Signalstyrke (GLOBAL 0x05):** Vis signalstyrke **mellom kontrollpanel og Power Unit**, ikke RSSI for BLE-proxy/HA. Firmware-koden kaller feltet SIGNAL_STRENGTH. Mest sannsynlig skala **0–3**, men valider tersklene mot faktiske panelvisninger før brukerrettet skala låses.
- [ ] **Driftstilstand:** Behold kun én vanlig driftstilstandssensor på norsk. Flytt engelsk driftstilstand og numerisk tilstandskode til diagnostikk. Behold interne koder og eksisterende entitets-ID-er så langt mulig.
- [ ] **Visningsnavn:** Endre «Normal drift» til **«Drift»** hvis endringen ikke allerede ligger i 0.5.24. Endre «Start opptenning» til **«Start fyring»** i norsk integrasjon/dashboard uten å endre handlingen.
- [ ] **Sist Bluetooth-oppdatering:** Vis **siste vellykkede STATUS-svar** med full norsk dato og klokkeslett, eksempel 27.10.2026 kl. 08:32:45, lokal tid Europe/Oslo. Behold maskinlesbar timestamp for automatisering. 0.5.24 har allerede last_data_at / «Sist oppdatert (Bluetooth)», så gjenbruk/forbedre eksisterende løsning og unngå unødvendig duplikatsensor.
- [ ] **GLOBAL 0x53:** Vis bare navnet **«Pipetrekk»** under Konfigurasjon, i Pa. Brukerens verdi er **26 Pa**. Dette er en innstilling/setpunkt, **ikke en løpende fysisk måling**. Den brukes ikke aktivt i brukerens oppsett uten XTP.
- [ ] **XTP-opprydding:** Ikke eksponer levende trekkmåling (0x20), XTP-relatert 0x51 eller trykkstyrt alternativ (2) av SYSTEM_CONTROL 0x55 som aktive funksjoner. Råfeltene kan beholdes i full diagnostikk. Behold 0x55=0 Manuell og 0x55=1 eXotelligence, og behold 0x1B atmosfærisk lufttrykk (hPa), som **ikke** er XTP-trekkmåling.
- [ ] **Øvrige tids-/konfigurasjonsgrenser:** Oppdater relevante min/maks i grensesnittet etter verifiserte firmwarefunn, blant annet alarm, gjenfyringstid og utbrenningstid. Ikke åpne nye uprøvde skrivekommandoer bare fordi registeret finnes.

## 2. Skal bevares / bevisst utsettes

- **Ikke endre Bluetooth-strategi fra 0.5.24:** automatisk proxyvalg etter RSSI, kildebestemt HA-cache, inntil seks kilder per runde, eksisterende fallback ved BLE/GATT-feil, 120 sekunders cache-karantene, nåværende hvile-/aktivintervall og vern mot event-loop-spinn.
- **Ny fallback etter vellykket BLE men manglende Xzense CONNECT-ACK/STATUS:** utsettes til vi har mer langtidserfaring med 0.5.24. Ikke fjern den eksisterende BLE/GATT-fallbacken.
- **Ekstern start 0x57 og ekstern viftehastighet 0x5A:** fortsatt utelatt fra aktive funksjoner; behold rådata i diagnostikk.
- **XTP-trykksensor:** ikke installert. Ingen trykkstyring, trykkbaserte varsler eller falske målte trekkverdier.
- **Firmwareoppgradering fra HA:** droppet. Ingen GBL/FILE_TRANSFER-skriving.
- **Ingen nye batterivarsler.** Eksisterende valgfri varsling om overgang Drift → Utbrenning i 0.5.21+ skal ikke endres.
- **Bevar** domenet xzense_full_preview, konfigurasjonsoppføringen, PIN-flyt, eksisterende entity unique IDs, STATUS- og kontrollrammer, dashboardets funksjoner og norske oversettelser.
- **Lever komplett pakke først når bygg bestilles**, med korrekt versjon, tester, oppdatert README, CHANGELOG og REVISJONER. Ikke omdøp 0.5.24 til 0.5.25 i dokumentasjon før ny kode faktisk er bygget/testet.

---

# Protokollmanifest: hva 0x-verdiene betyr / kan bety

**Avgrensning:** Dette er et **foreløpig arbeidsmanifest per 27.10.2026**, basert på dokumentasjon, fysiske korrelasjoner, diagnostikk og analyse av Exodraft 5.0.5 APKs **exodraft.gbl**, kontrollpanel-firmware **4.10_RC2**. Ikke alle ID-er har kjent funksjon eller trygg skriveadgang.

**Viktig:** Pakkekommandokoden 0x05 (ALIVE) er **ikke** det samme som GLOBAL-registeret 0x05 (SIGNAL_STRENGTH). Dette er to forskjellige navnerom.

**Kildehierarki:** (1) fysisk testet avlesning/ACK eller A/B-endring, (2) direkte kodespor i 4.10_RC2, (3) firmware enum-/strengtabell, (4) hypotese fra råverdier. Eldre debug-etiketter kan ha vært forskjøvet og må ikke trumfe nyere observasjoner.

## A. Pakkekommandoer (BLE-applikasjonsprotokoll)

| Kode | Navn i firmware | Beskrivelse | Sikkerhet / dokumentasjon |
|---|---|---|---|
| 0x00 | DISCOVER | Oppdagelse av enheter | Firmware-identifisert, full dataform ikke verifisert |
| 0x01 | EXT_DISCOVER | Utvidet oppdagelse | Firmware-identifisert, ikke testet |
| 0x02 | CONNECT | Applikasjonstilkobling/PIN | **Fysisk bekreftet** |
| 0x03 | EXT_CONNECT | Utvidet tilkobling | Firmware-identifisert, ikke testet |
| 0x04 | DISCONNECT | Avslutte sesjon | Firmware-identifisert, ikke egen skriveprøve |
| 0x05 | ALIVE | Mulig keepalive | Identifisert i firmware; wireformat og effekt ikke bekreftet. Må ikke forveksles med GLOBAL 0x05 |
| 0x06 | GLOBAL | Lese/skrive globale parametre | **Leseprotokoll og utvalgte skriver/ACK fysisk bekreftet** |
| 0x07 | STATUS | Hente driftstilstand/status | **Fysisk bekreftet** |
| 0x08 | BOOST | Start/stopp Boost; tilstandsbetinget opptenning/gjenfyring | **Fysisk testet Boost på/av**, øvrige tilstandsoverganger delvis firmware-avledet |
| 0x09 | VENTILATION | Ventilasjon på/av | **Fysisk testet**, STATUS state 8 |
| 0x0A | RANGETEST | Radiotest mot Power Unit | Firmware-identifisert; ikke implementert |
| 0x0B | FACTORY_RESET | Fabrikktilbakestilling | **Destruktiv kommando, skal ikke eksponeres** |
| 0x0C | FILE_TRANSFER | Fil-/firmwareoverføring, mulig ChimneyLog og ErrLog | Ikke trygt dekodet, ikke send ukjente subkommandoer |
| 0x0D | TIMESYNC | Tidssynkronisering | Firmware-identifisert, format ukjent |
| 0x0E | CONNECTED_PEERS | Oversikt over tilknyttede enheter | Identifisert, enkelte råpayloads finnes; innhold udekodet |

## B. GLOBAL-registere og andre globale felt

**Statusforklaringer:** «Bekreftet» betyr fysisk observert/testet. «Firmware» betyr statisk kode-/strengfunn uten full fysisk verifikasjon. «Foreløpig» betyr at skala, betydning eller sammenheng ennå må testes.

| ID | Navn / betydning | Format / eksempel | Status og merknad |
|---|---|---|---|
| 0x00 | NONE / intern visningsverdi | Råverdi 1 observert | Firmware-navn; **betydning uavklart** |
| 0x01 | ANIMATE | Råverdi observert | Firmware-navn; bruksområde uavklart |
| 0x02 | SECONDS | Rå teller (kan rulle over signed 16-bit) | Firmware-navn; **ikke forveksle med driftstilstandstimer 0x1A** |
| 0x03 | KEYBOARD | Råverdi 0 observert | Firmware-navn; innhold uavklart |
| **0x04** | **BATTERY** | 100 → 90, antatt 0–100 % | **Firmware + fysisk korrelasjon** til panelikon; sensor planlagt |
| **0x05** | **SIGNAL_STRENGTH** | Rå 2/3; **antatt 0–3** | **Direkte firmwarekode** kobler feltet til panelvisning; Power Unit-radio, ikke BLE-RSSI. Skala ennå ikke endelig bekreftet |
| 0x18 | MY_STATE | Rå 2 observert | Firmware-navn; semantikk **ikke verifisert**, ikke signalstyrke |
| **0x19** | **CHIMNEY_STATE** | Enum 0–10 | **Bekreftet driftstilstand**, se tilstandstabell |
| **0x1A** | **STATE_TIMER** | Sekunder, observerte rollover | **Bekreftet** tid i gjeldende tilstand |
| **0x1B** | **PRESSURE** | For eksempel 981/1011 hPa | **Bekreftet atmosfærisk lufttrykk**, ikke XTP |
| 0x1C | INSIDE_TEMP | Tideler °C | Sterk korrelasjon med STATUS |
| 0x1D | OUTSIDE_TEMP | Tideler °C | Sterk korrelasjon med STATUS |
| **0x1E** | **CHIMNEY_TEMP** | Tideler °C | **Fysisk bekreftet** skorsteinstemperatur |
| **0x1F** | **FAN_SPEED** | % | **Fysisk bekreftet** faktisk viftehastighet |
| 0x20 | ACTUAL_DRAFT | Rå 10 observert | Firmware-navn; **krever trolig XTP**, skala/måling ikke validert i brukerens oppsett; ingen aktiv sensor |
| **0x32** | **VOLUME / lyd** | % | **Bekreftet A/B**, 12 → 24 |
| **0x33** | **CONTRAST / kontrast** | % | **Bekreftet**, eksempel 75 |
| **0x34** | **BRIGHTNESS / lysstyrke** | % | **Bekreftet**, eksempel 68 |
| 0x35 | BLE_ENABLED | Rå 1 | Firmware-navn; ikke skriv, kan påvirke tilkobling |
| 0x36 | LANGUAGE | Rå 0 | Firmware-navn; koding ukjent, språkfeil på panel kjent; ikke skriv |
| **0x4B** | **AUTO_START_TEMP** | /10 °C, f.eks. 502 = 50,2 °C | **Bekreftet korrelasjon**, grenser skal revideres |
| **0x4C** | **AUTO_STOP_TEMP** | /10 °C, f.eks. 398 = 39,8 °C | **Bekreftet korrelasjon**, minst 6 °C under start i HA |
| **0x4D** | **BOOST_TIME** | Sekunder, f.eks. 900 = 15 min | **Bekreftet**, HA-skrive-ACK observert |
| **0x4E** | **AFTERRUN_TIME** | Sekunder, f.eks. 1800 = 30 min | **Bekreftet korrelasjon** |
| **0x4F** | **BOOST_FAN_SPEED** | % | **Firmware + korrelasjon**, boosthastighet |
| **0x50** | **USER_FAN_SPEED** | 10–100 % | **Fysisk bekreftet** brukerviftehastighet, også korrelert i ventilasjon |
| 0x51 | DRAFT_FAN_SPEED | Rå 0 observert | Firmware-tabellen navngir trekkrelatert viftehastighet; eldre dokument kalte det «Actual draught». **XTP-relatert/ikke aktivt**, semantikk skal ikke overtolkes |
| **0x52** | **BOOST_STOP_TEMP** | /10 °C, 600 = 60,0 °C | **Bekreftet**; vårt valgte standardreferansepunkt 60 °C, grenser fra firmware |
| **0x53** | **WANTED_DRAFT / Pipetrekk** | Pa, brukerens **26 Pa** | **Bekreftet** innstilling/setpunkt i menyen, **ikke målt trekk** |
| **0x54** | **MIN_FAN_VOLTAGE** | V, 80 → 105 V testet | **Fysisk bekreftet** |
| **0x55** | **SYSTEM_CONTROL** | 0 Manuell; 1 eXotelligence; 2 trykkstyrt | **Direkte firmwarebinding**; skjul alternativ 2 uten XTP |
| 0x56 | TEMPERATURE_SENSOR | Rå 1, antatt 0 Av / 1 På | **Firmware-ID bekreftet, 0/1-skriving eksperimentell** |
| 0x57 | EXTERN_START | Rå 0/1 observert | **Firmware**, bevisst utsatt fra aktive funksjoner |
| **0x58** | **ALARM_SETPOINT** | /10 °C, 2500 = 250 °C | **Firmware + manual**; 150–400 °C i tidligere dokumentasjon |
| 0x59 | REBOOST_TIME | 180 sek = 3 min observert | **Firmware**, separat fra Boosttid, kontroller grenser før UI-endring |
| 0x5A | EXTERN_FAN_SPEED | Rå 0 | **Firmware**, bevisst utsatt fra aktive funksjoner |
| 0x5B | BURNOUT_TIMEOUT | 300 sek = 5 min observert | **Firmware**, kontroller sikre min/maks før UI-endring |

**Ikke listet:** Ukjente/manglende register-ID-er i hex-intervallene betyr ikke at de er ledige eller trygge å skrive til. Dokumentet dekker alle **identifiserte** felt, ikke alle 256 mulige ID-er.

## C. Driftstilstand (GLOBAL 0x19 og STATUS)

| Råverdi | Intern status | Brukervendt norsk betegnelse |
|---|---|---|
| 0 | OFFLINE | Frakoblet |
| 1 | SETUP | Oppsett |
| 2 | IDLE / Ready for lighting | Klar for fyring |
| 3 | BOOSTING | Boost |
| 4 | OPERATING | **Drift** (ikke «Normal drift») |
| 5 | BURNOUT | Utbrenning |
| 6 | AFTERRUN | Ettergang |
| 7 | REHEATING | Gjenfyring |
| 8 | VENTILATING | Ventilasjon |
| 9 | ERROR_STATE | Feil |
| 10 | UPGRADING | Oppdatering |

Tilstandsmappingen 0–10 kommer fra firmware-tabellen. Ikke tolk 0x18 (MY_STATE) som 0x19 (CHIMNEY_STATE).

## D. Forskjellen på avlest, bekreftet og skrivbar

- Et navn i firmwaren viser at programmet kjenner feltet, men **beviser ikke** at det er aktivt på akkurat dette kontrollpanelet, eller at lesefelt kan skrives.
- En råverdi som matcher brukerens menyinnstilling er god korrelasjon; trygg skriveadgang krever ekstra vurdering og eventuell fysisk test.
- Skrivepakke for validerte GLOBAL-innstillinger: kommando 0x06 + aktiv sesjons-ID + register-ID + signert 16-bit verdi (little endian). Ingen generell vilkårlig råskrivefunksjon i HA.
- DATA fra STATUS kan være ferske eller cachet. Planlagte norske sensorer må ikke vise cache som sanntidsmåling.

## E. Åpne spørsmål og dokumentasjonsforbehold

1. Sjekk faktisk 0.5.24-kode før endringer: hvilke visningsnavn/sensorer er allerede endret, og hvilke unique IDs brukes. Unngå duplikater og entity registry-konflikter.
2. 0x05: Skalaen antas 0–3, men må sammenlignes med indikator/diagnose. Oppgi ikke BLE-RSSI i dBm som denne verdien.
3. 0x04: Battery 0–100 % virker sannsynlig ved 100 → 90, men eksakt oppdaterings-/avrundingslogikk i panelet er ikke fullstendig verifisert.
4. 0x20 og 0x51 kan forbli i rå diagnostikk; XTP-målinger skal ikke fremstå som gyldige uten XTP.
5. Start-/stopp-/boost-/alarm-/tidsgrenser må kontrolleres mot koden før implementasjon. Brukerens verdier skal ikke overskrives.
6. 0x0C FILE_TRANSFER (ChimneyLog/ErrLog), 0x0D TIMESYNC, 0x0E CONNECTED_PEERS og 0x05 ALIVE er **ikke** automatisk sikre for nye live-anrop.
7. Bevar historiske korrigeringer: eldre 0.5.5–0.5.10-notater hadde enkelte forskjøvne GLOBAL-navn. Dette dokumentet fører nyere analyse uten å slette de originale notatene.

## Eksisterende kildedokumentasjon

- [Gjeldende installasjon og versjon](README.md)
- [Endringshistorikk](CHANGELOG.md)
- [Revisjonshistorikk og kildearkiver](REVISJONER.md)
- [Tidligere protokollmanifest](docs/PROTOCOL_MANIFEST.md) (inneholder eldre uavklarte felt; må samordnes ved neste bygg)
- [Protokollnotater](docs/PROTOCOL_NOTES.md)
- [ChimneyLog-forskning](docs/CHIMNEYLOG_RESEARCH.md)

**Neste handling:** Ingen kodeendring før Lars Marius uttrykkelig ber om bygging av 0.5.25.

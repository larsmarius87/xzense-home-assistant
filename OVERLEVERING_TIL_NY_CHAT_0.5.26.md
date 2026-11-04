# Xzense, overlevering til ny ChatGPT-samtale
**Oppdatert:** 3. november 2026

## Oppdrag for neste samtale
Fortsett utviklingen av Home Assistant-integrasjonen for Exodraft Xzense. Ikke start på nytt. Begynn med å kontrollere kildekoden og GitHub-grenen for **0.5.26**, teste pakken, og rette eventuelle avvik. Bevar sist bekreftet fungerende **0.5.25 RC1** som sikker tilbakefallsversjon.

## GitHub og filer
- Privat repo: https://github.com/larsmarius87/xzense-home-assistant
- Siste testpakke: https://github.com/larsmarius87/xzense-home-assistant/blob/xzense-0.5.26-refueling-test/xzense-alpha-0.5.26-source.zip
- Gren: `xzense-0.5.26-refueling-test`
- Draft PR: https://github.com/larsmarius87/xzense-home-assistant/pull/1
- Dokumentasjon: `INSTALLASJON_0.5.26.md` og `CHANGELOG.md` på samme gren.
- **Main er ikke oppdatert med 0.5.26.** PR står som kladd inntil verifisering.
- Eldre komplette ZIP-er: `xzense-alpha-0.5.25-rc1-source.zip`, `xzense-alpha-0.5.25-source.zip` og historiske pakker.
- Integrasjonsdomene: `xzense_full_preview`. Mappen er `custom_components/xzense_full_preview`. Dashboard JS: `/config/www/xzense-card.js`, ressurs `/local/xzense-card.js?v=0526`.

## Versjonshistorikk som må respekteres
| Versjon | Status |
|---|---|
| 0.5.25 RC1 | **Sist bekreftet fungerende** hos Lars. |
| 0.5.25 Final | Ga utilgjengelige sensorer og navneproblemer. |
| 0.5.25 Final Fix1 | Kun en endring fra Final: `sensor.py` returnerte `getattr(self, "_attr_icon", None)` i stedet for `self._attr_icon`, slik at sensorer uten egendefinert ikon ikke utløste `AttributeError`. Ingen fysisk verifisering. |
| 0.5.26 | Ny **testversjon** på egen GitHub-gren. Bygget fra RC1-kilde, utvalgte ikon/diagnostikkfikser, firmwarebasert Refueling-gating og dashboardendringer. Ikke ennå installert/testet fysisk i denne samtalen. |

I 0.5.25 RC1, Final og Final Fix1 var Bluetooth-transportkoden identisk. 0.5.26 bevarer denne.

## De viktigste firmwarefunnene
Lars har Xzense A809-kontrollpanel med firmware **4.10_RC2**. Originalapp APK **5.0.5** og oppdateringsfil `exodraft.gbl` ble analysert i tidligere samtale, inkludert Cortex Thumb-2-maskinkode.

Eksterne tilstander (STATUS/GLOBAL `0x19`):
`0` Offline, `1` Setup, `2` Ready/Klar for fyring, `3` Boosting, `4` Operating/Drift, `5` Burnout/Utbrenning, `6` Afterrun, `7` Refueling, `8` Ventilating, `9` Error, `10` Upgrading.

**Refueling, bekreftet av firmwareanalysen:**
- I firmware rundt `0x8FD4–0x900C` utløses Burnout når temperaturføler er aktiv, pipetemperaturen tidligere var over starttemperaturen (ca. 50,2 °C) og nå synker under stopptemperaturen (for tiden ca. 35 °C).
- I koden rundt `0x8B90–0x8BD0` har `BOOST/REQ start=1` to ulike forløp:
  - **Burnout**, intern tilstand 11 / ekstern 5: starter `Refueling`, ekstern tilstand **7**, med varighet fra **GLOBAL 0x59** (hos Lars ca. **180 sekunder / 3 min**).
  - **Operation**, ekstern tilstand 4: starter vanlig **Boosting**, ekstern tilstand **3**, med varighet fra **GLOBAL 0x4D** (hos Lars ca. 900 sekunder / 15 min).
- Dermed er det **ikke nødvendig å midlertidig endre Boost-tid** for å gi 3 minutters Refueling.
- `0x5B` er Burnout-timeout fram til Afterrun, ikke selve Refueling-knappen.
- Panelets firmware viser varselet «It is time to refuel. Would you like to refuel now?» i Burnout, og ja-knappen sender den relevante startkommandoen.
- I 0.5.26 er `button.refuel` og `client.async_control_feature('refuel')` begrenset til ekstern tilstand **5**. Selve kommandoen er fortsatt `async_set_boost(True)`.

**Ikke anta at normal Boost og Refueling er samme modus.** Det er samme startkommando, men *firmwaren* velger ulik modus/timer etter gjeldende tilstand.

## Andre kartlagte GLOBAL-felt
- `0x50`: operativ viftehastighet i prosent.
- `0x54`: minimum viftespenning 80–120 V, med lokal RS009-41-bryter som begrenser skriving til 100–120 V. Lars bruker ca. 105 V.
- `0x05`: radiolink mellom panel og kraftenhet, 0–3 streker. **Ikke Bluetooth RSSI.**
- `0x04`: batteri kontrollpanel (prosent).
- `0x55`: systemstyring; 1=eXotelligence.
- `0x59`: refire/reboost/Refueling-varighet.
- `0x5B`: Burnout-timeout.
- Peistrykk/lufttrykk 1011 er bekreftet som lufttrykk; pipetrekk er installasjonssettpunkt, ikke målt trykk på dette anlegget.
- 0x56 temperaturprobe er testet og fungerer. Det gamle røde «eksperimentell»-varselet på kortet skulle fjernes.

## Oppsett og Bluetooth-erfaring
- Home Assistant kjører på en Proxmox-server. ESP32/ESPHome Bluetooth-proxyer brukes i flere rom, særlig Stue og ny M2 Atom.
- Kontrolleren har hatt feil `133`, `0x85`, autentiseringsfeil, timeout og periodiske frakoblinger. Nærhet alene var ikke alltid tilstrekkelig; ny M2 Atom fungerte bedre.
- Serverens integrerte Bluetooth-radio i kjeller ble i en test ikke autentisert; oppkoblingen fungerte igjen når panelet var nær den tidligere proxyen i etasjen over. Ingen sikker konklusjon om radioen er ubrukelig.
- Tidligere forsøk på låsing til kun én proxy fungerte dårlig; multi-proxy ble gjenopprettet.
- Unngå endringer i stabil BLE-transport uten tydelig datagrunnlag. Versjon 0.5.15/0.5.16 hadde tidligere busy-loop/CPU-problemer; senere versjon rettet det.

## Dashboardendringer inkludert i 0.5.26
- Bevar norsk kontrollpanel med standard Home Assistant-farger.
- Batteriindikator oppe i hjørnet, uten egen statistikkboks.
- Z-Wave-symbol og **tre streker for panel/kraftenhet-radio** på motsatt side av Bluetooth-oppdateringslinjen.
- Refuel/ved: `mdi:forest`. Boost: `mdi:turbine` (ikke rakett).
- Første rad: Pipetemperatur, faktisk viftehastighet og fyringsvarighet. Andre rad: Innetemperatur, Utetemperatur og Lufttrykk.
- «Tid i nåværende modus» fjernet fra hovedkortet; sensor er beholdt i integrasjonen.
- Ingen firmware `4.10_RC2`-suffiks bak hver standardreferanse.
- Gammelt rødt varsel om temperaturføler fjernet.
- Toppknapper for Start fyring, Legg på ved, Avslutt fyring, Boost og Ventilasjon; faner for driftsinnstillinger, konfigurasjon, kontrollpanel og diagnostikk.
- Funksjonelle HA-entiteter må være riktig koblet; ikke hardkod unike entity-id-er.

## Viktige åpne oppgaver
1. **Test 0.5.26-pakken før merge:** verifiser ZIP-integritet (`unzip -t`), kjør `python run_tests_0525.py`/pytest og sjekk manifest/const.js-versjoner.
2. Installer på Home Assistant bare når Lars ønsker det, helst med backup av RC1. Bekreft at ingen sensorer blir utilgjengelige og at BLE fortsatte å fungere.
3. Verifiser fysisk under naturlig Burnout: «Legg på ved» blir tilgjengelig i state 5, kommandoen gir state 7 / Refueling i ca. 3 min, går tilbake korrekt. Bekreft at normal Boost har egen 15 min varighet.
4. Test dashboard på mobil/panel, inkludert korrekte ikoner og sensorfelt.
5. Når bekreftet stabil: vurder å merke PR ready og merge til `main`; oppdater revisjonsoversikt. **Ikke gjør dette før brukeren ønsker det.**
6. Øvrige ønsker: sist vellykket BT dato/tid, sist brukte proxy-MAC, forbedrede varslinger for flere mobiler og eventuelle egne ikoner som distribueres med integrasjonen.

## Viktig arbeidsmiljøforhold
Den aktuelle ChatGPT-økten fikk **read-only** lokalt filsystem og kunne ikke levere lokalt ZIP-vedlegg. GitHub-tilkoblingen hadde likevel `push`-rettigheter, så 0.5.26-ZIP ble bygget i minnet og lagt direkte i GitHub på en separat gren. Dette er ingen dokumentert generell begrensning for ChatGPT Plus. Nye samtaler kan ha andre tillatelser; test tilgang før arbeid med lokale filer.

## Brukerpreferanser
Brukeren heter Lars, er elektriker og teknisk kyndig. Svar på norsk, uten overdreven bruk av tankestreker. **Verifiser før du konkluderer**, og forklar hva som er testet kontra utledet. Ved kodeleveranser ønsker han komplette konfigurasjoner/ZIP og full changelog. Ikke lag en ny «final» uten å ha kontroll på RC1, Final, Fix1 og testresultatene.

# Xzense for Home Assistant

Uoffisiell integrasjon for **Exodraft Xzense**. Leser status fra Xzense-kontrollpanelet og gir tilgang til utvalgte styringsfunksjoner i Home Assistant via Bluetooth Low Energy (BLE).

> **Gjeldende HACS-test: 0.5.28** · Integrasjonsnavn: **Xzense** · Mappe og domene: `xzense`
>
> Dette er en **testutgave**, ikke en ferdig migreringsutgivelse. HACS-struktur og Python-syntaks er kontrollert i GitHub Actions, men oppgradering fra tidligere installasjoner er **ikke verifisert på et eksisterende Home Assistant-oppsett**. Ta backup før testing.

## Funksjoner

- **Status og sensorer:** Driftstilstand, skorsteinstemperatur, inne- og utetemperatur, lufttrykk, viftehastighet, batterinivå og radiolink mellom kontrollpanel og kraftenhet.
- **Styring:** Start og avslutt fyring, Boost, ventilasjon og vedpåfylling når kontrollerens driftstilstand tillater det.
- **Innstillinger:** Temperaturgrenser, Boost og ettergang, vifteparametere samt lyd, kontrast og lysstyrke for panelet.
- **Bluetooth:** Home Assistants Bluetooth-adaptere og ESPHome Bluetooth-proxyer, med automatisk kildevalg, fallback og justerbare oppdateringsintervaller.
- **Varsling:** Valgfritt varsel til én eller flere telefoner ved observert overgang fra Drift til Utbrenning.
- **Dashboard:** Et separat Xzense-kort med norsk tekst og kontrollfunksjoner.

## Installering via HACS – testversjon

Pakkelager: [`larsmarius87/xzense-home-assistant`](https://github.com/larsmarius87/xzense-home-assistant)

1. Åpne **HACS → menyen (⋮) → Egendefinerte pakkelagre**.
2. Legg til `https://github.com/larsmarius87/xzense-home-assistant` med kategorien **Integration**.
3. Velg **Xzense** i HACS, installer og start Home Assistant på nytt.
4. Legg deretter til integrasjonen under **Innstillinger → Enheter og tjenester**, dersom dette er en ny installasjon.

HACS installerer Python-integrasjonen fra `custom_components/xzense/`. Filen `hacs.json` ligger i repositoryets rot. Denne testversjonen er publisert på **`HACS`-grenen**, som for øyeblikket er repositoryets standardgren. Den kan endres senere; HACS bruker normalt standardgrenen når et egendefinert repository legges til.

**Dashboardkortet:** `www/xzense-card.js` distribueres foreløpig separat. Kopier det til `/config/www/xzense-card.js` og kontroller at Lovelace har ressursen `/local/xzense-card.js`. HACS-integrasjonsinstallasjonen håndterer ikke dette kortet som en egen frontend-pakke.

## Viktig ved oppgradering fra tidligere Xzense

Tidligere pakker brukte integrasjonsdomenet `xzense_full_preview`. I 0.5.28 er domenet endret til `xzense`.

Det er **ikke nok å endre mappenavnet** for å migrere en eksisterende integrasjon: Home Assistant kan fortsatt ha en konfigurasjonsoppføring og entitetsregistrering knyttet til det gamle domenet.

- **Ikke slett** den gamle Xzense-integrasjonen eller konfigurasjonsoppføringen for å «rydde opp».
- Ta **full backup** av Home Assistant, inkludert konfigurasjon, `.storage` og Recorder-databasen.
- Eksisterende PIN, innstillinger, entitets-ID-er, dashboardreferanser og historikk er ment å bevares, men **automatisk migrering er ennå ikke ferdig implementert og testet**.
- For en eksisterende installasjon bør du **vente med å oppgradere** til en sikker migreringsprosedyre er verifisert. En test i et separat Home Assistant-miljø er tryggere.

**0.5.27 korrigert** ligger fortsatt tilgjengelig på [`main`](https://github.com/larsmarius87/xzense-home-assistant/tree/main) som eldre ZIP-basert utgave. Det er ikke samme installasjonsopplegg som 0.5.28 i HACS.

## Status for 0.5.28

| Område | Status |
|---|---|
| HACS-mappestruktur | Bygget og validert |
| Navn og domene `xzense` | Implementert i testbygget |
| Eksisterende Xzense-ikon | Inkludert i `custom_components/xzense/brand/icon.png` |
| Bluetooth og styringsfunksjoner | Basert på korrigert 0.5.27, ikke fullstendig fysisk retestet i 0.5.28 |
| Automatisk migrering av gammel HA-konfigurasjon | **Ikke ferdig / ikke verifisert** |
| Automatisk HACS-installering av dashboardkort | Ikke implementert |
| Egen fyringslogg i Home Assistant | Planlagt senere |

## Dokumentasjon og utvikling

- [Endringslogg](CHANGELOG.md) – historikk og tidligere rettelser
- [Revisjonsarkiv](REVISJONER.md) – eldre versjoner og ZIP-pakker
- [Protokollregister](docs/PROTOCOL_MANIFEST.md) – identifiserte registre og hva som er bekreftet
- [Veikart](VEIKART.md) – planlagte funksjoner og videre arbeid
- [`main`-grenen](https://github.com/larsmarius87/xzense-home-assistant/tree/main) – siste ordinære ZIP-baserte utviklingsversjon

Følgende protokollverdier er bekreftet på fysisk enhet: `0x04` batterinivå og `0x05` radiolink mellom kontrollpanel og kraftenhet. Vedpåfylling ved riktig driftstilstand er også fysisk testet. Arbeidet med Exodrafts interne loggfiler er satt på vent; en egen fyringslogg i Home Assistant er planlagt til senere.

## Sikkerhet

Dette er et uoffisielt prosjekt og ikke en integrasjon fra Exodraft. Home Assistant skal ikke erstatte kontrollpanelets sikkerhetsfunksjoner, varslinger eller lokale betjening. Vær særlig forsiktig ved testing av styringskommandoer og oppgraderinger som påvirker en eksisterende installasjon.

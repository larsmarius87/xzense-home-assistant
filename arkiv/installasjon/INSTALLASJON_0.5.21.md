# Xzense Alpha 0.5.21 – telefonvarsel ved utbrenning

## Oppdatere

1. Ta backup av den fungerende Xzense-installasjonen (0.5.20.2).
2. Pakk ut hele `custom_components/xzense_full_preview/`-innholdet fra ZIP-en og kopier **filene** til den eksisterende integrasjonsmappen i `/config/custom_components/`. **Ikke endre navnet på din eksisterende Xzense-mappe eller integrasjonsdomenet.**
3. Start Home Assistant på nytt og kontroller at Xzense Alpha rapporterer versjon `0.5.21`.
4. Gå til **Innstillinger → Enheter og tjenester → Xzense Alpha → Konfigurer**.
5. Slå på **Send varsel ved utbrenning**, og velg **Telefon som skal varsles**.
6. Lagre. Innstillingen er aktiv uten ny Bluetooth-omstart. Gamle Bluetooth-intervallvalg beholdes.

## Forutsetning

Telefonen må være registrert i **Home Assistant Companion** og ha tillatt varslinger.
Avsender er Home Assistant, ikke en selvstendig SMS-tjeneste; ingen telefonnummer brukes.

## Hva utløser et varsel?

Bare en **ny, gyldig STATUS-overgang fra Operation (`4`) til Burnout (`5`)**.
For eksempel:
- STATUS 4 → STATUS 4 → STATUS 5: **ett** varsel.
- STATUS 5 → STATUS 5: **ingen nye** varsler.
- Home Assistant starter når panelet allerede er i Burnout: **ingen** varsel.
- Etter HA-omstart må Operation først observeres før neste overgang kan varsles.

Melding: «Xzense har gått fra normal drift til utbrenning.»

**Merk:** BLE-søvntid og brudd kan forsinke varselet. Hvis integrasjonen ikke observerer overgangen (for eksempel fordi hele utbrenningen skjer mellom to tilkoblinger), kan varslet utebli. Funksjonen er en bekvemmelighet, ikke en kritisk sikkerhetsalarm.

## Hvis telefonen ikke vises

Kontroller Companion-registrering under **Innstillinger → Enheter og tjenester → Mobile App**, og at telefonens varselentitet ikke er deaktivert. Eldre mobilapp-handlinger listes opp som «mobilapp-tjeneste». Valg av mottaker er eksplisitt – aldri send til alle telefoner automatisk.

## Test push uten å vente på utbrenning

Under **Utviklerverktøy → Handlinger** kan du velge «Send en varslingsmelding» (`notify.send_message`) og angi samme telefon som mottaker. For eldre oppsett kan handlingen være `notify.mobile_app_telefonnavn`.

## Tilbakeføring

Gjenopprett 0.5.20.2-filene og start Home Assistant på nytt. Varslingsinnstillingene ligger i `entry.options`, påvirker ingen eksisterende entitets-ID-er og kan trygt ignoreres av eldre versjon.
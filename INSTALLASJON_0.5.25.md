# Xzense 0.5.25 Alpha – installasjon og kontroll

Dato: 28. oktober 2026. Basert på 0.5.25-rc1. Dette er den endelige 0.5.25 Alpha, ikke en RC.

1. Ta en kopi av mappen med fungerende Xzense-integrasjon før oppdatering.
2. Pakk ut `xzense-alpha-0.5.25-source.zip`. Kopier `custom_components/xzense_full_preview` over eksisterende mappe med **samme navn**. Ikke endre domenet eller legg til en annen Xzense-instans.
3. Start Home Assistant på nytt. Sjekk at versjonen i `manifest.json` er `0.5.25`.
4. Bruk Lovelace-ressurs `/api/xzense_full_preview/xzense-card.js?v=0525`. Dersom du selv kopierer kortet til `/config/www/`, oppdater filen og bruk `/local/xzense-card.js?v=0525`.
5. Under Xzense → **Konfigurer** kan du slå på varsel ved utbrenning og velge en eller flere mobiler. Varsling er deaktivert til du selv slår den på.
6. Sjekk at «Viftetype RS009-41» har riktig lokal innstilling, og at den viste minimumsviftespenningen er fornuftig. Bryteren begrenser bare fremtidige skriverettede justeringer; den endrer ikke fysisk verdi automatisk.
7. Kontroller «Pipetrekk» (lagret installasjonsverdi), «Radiolink – signalstyrke» (0–3), batteri og de norske statusnavnene. Batteriprosenten er foreløpig en uverifisert kalibrering.
8. Tidligere utilgjengelige diagnostikkentiteter fjernes ved oppstart, men rådata skal fortsatt være i **Last ned diagnostikk** og «Ubrukte GLOBAL-verdier».

**Viktig:** De lokale testene er kjørt uten en fysisk Xzense. Bekreft Boost, statusoverganger og mobilvarsling i ditt eget oppsett. Ikke gjennomfør unødvendige skriverettede tester på en aktiv peis. Bluetooth-motoren fra 0.5.24 er ikke endret i denne versjonen.

Se også [Endringslogg](CHANGELOG.md) og [Protokollmanifest](PROTOCOL_MANIFEST.md).

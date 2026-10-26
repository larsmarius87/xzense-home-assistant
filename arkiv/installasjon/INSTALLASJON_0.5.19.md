# Xzense Alpha 0.5.19 – Hybrid Bluetooth (eksperimentell)

**Bygget direkte fra Alpha 0.5.17.** Domenet er fortsatt `xzense_full_preview`; behold eksisterende konfigurasjonsoppføring og PIN. Installer **ikke** en parallell integrasjon med samme Bluetooth-adresse.

## Installere

1. Ta backup av den fungerende 0.5.17-integrasjonen og eventuelt hele Home Assistant.
2. Finn den **aktive** custom-components-mappen og dens `manifest.json`. Dersom den aktive mappen er `/config/custom_components/xzense_full_preview/`, erstatt den med **hele** mappen `custom_components/xzense_full_preview/` i ZIP-filen (inkludert `www/`). Ikke opprett en ny mappe med et annet domenenavn.
3. Start Home Assistant på nytt. Bekreft at Xzense-diagnostikken viser **0.5.19**.
4. Gå til **Innstillinger → Enheter og tjenester → Xzense → Entiteter** og finn `Bluetooth update interval` (en `number`-entitet). Slideren finnes også i Xzense-kortet under **Konfigurasjon** hvis du bruker det innebygde kortet og oppdaterer nettleseren.
5. Første oppstart bruker **5 minutter** (ny standard). Sett slideren til **0 minutter** dersom du først vil kontrollere at tradisjonell kontinuerlig modus fungerer som før.
6. Test periodisk modus med for eksempel **1 minutt**. Sjekk sensorene `Last data update`, `Next Bluetooth update`, BLE link og `Connection` og den nye diagnostikken. Ved periodisk polling skal BLE være avslått mellom øktene og siste sensorverdier beholdes.

## Virkemåte

- **0** = kontinuerlig tilkobling, STATUS hvert 10. sekund.
- **1–120** = ett øyeblikksbilde per intervall; neste intervall regnes etter at forrige økt er ferdig.
- **Ved knappetrykk** forsøker integrasjonen å bruke en sterk Bluetooth-proxy i HA-cache. Hvis det mislykkes, går den tilbake til vanlig 3-sekunders innsamling av annonseringer. Ved svak/no proxy kan dette ta vesentlig lengre tid.
- **Skrivekommandoer sendes først etter en fersk STATUS i ny sesjon.** Flere påfølgende kommandoer køes. BLE beholdes i cirka 15 sekunder etter siste håndtering.
- **Sensordata beholdes**, men markeres med `stale` og `last_data_at` når de ikke er ferske. Et tidligere «Vifte av» beviser ikke at viften fremdeles står stille. Selv ved tilkoblet sesjon kan en verdi være gammel inntil ny STATUS er mottatt.
- Ingen automatisk bytting til kontinuerlig tilkobling under fyring i denne testen. Velg `0` dersom du trenger løpende tilsyn.
- Kontroller alltid kritiske handlinger på det fysiske panelet; `write-without-response` garanterer ikke kvittering.

## Rull tilbake

Stans/deaktiver integrasjonen, erstatt filene med fungerende **0.5.17**, og start HA på nytt. Den nye `number`-entiteten for Bluetooth intervallet kan bli utilgjengelig med gammel versjon; den opprinnelige funksjonaliteten beholder eksisterende entitets-ID-er. Ikke installer Alpha 0.5.15/0.5.16, som hadde risiko for å blokkere HAs hendelsesløkke.

## Teststatus

Kodekompilering, Python-testsuite og dashboardets JS-smoke er kjørt lokalt. Ingen tilgang til fysisk Xzense/Bluetooth-proxy under bygging. Test derfor først når viften ikke er i en kritisk driftssituasjon.
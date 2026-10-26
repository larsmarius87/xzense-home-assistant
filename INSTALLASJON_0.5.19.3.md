# Xzense Alpha 0.5.19.3 – installasjon

**Endringer:** Bluetooth-intervallene er NumberEntity-slidere (kolliderende `mode`-attributt er fjernet). Hovedskjermen viser «Sist oppdatert», og den eksisterende diagnostikksensoren heter nå «Sist oppdatert (Bluetooth)». Ready: 0–120 minutter. Aktiv drift: 0–600 sekunder. 0 = kontinuerlig i begge profiler.

1. Ta backup av eksisterende `/config/custom_components/xzense_full_preview/` (0.5.19.2).
2. Erstatt hele mappen med `custom_components/xzense_full_preview/` fra ZIP-en, uten å slette eller legge til Xzense-konfigurasjonen på nytt.
3. Start Home Assistant på nytt og bekreft **0.5.19.3** under integrasjonsdiagnostikken.
4. Finn begge Xzense-konfigurasjonsentitetene: `Bluetooth update interval` (Ready, 0–120 min) og `Bluetooth active update interval` (aktiv, 0–600 s). De har uendrede unique ID-er. Begge skal eksponere `mode: slider` i HA sin entitetstilstand, samt `bluetooth_connection_mode` som egen attributt. **Merk:** HA kan likevel velge kompakt tallvisning i enkelte lister; åpne entitetsdialogen eller legg `number`-entiteten i et Tile-kort for å teste slideren.
5. Var aktiv verdi tidligere satt til 1 minutt, vil den nye entiteten vise 60 sekunder. Standard når ingen gammel verdi er valgt: 0 sekunder (kontinuerlig).
6. **Sist oppdatert** viser tidspunktet for sist mottatte gyldige STATUS/GLOBAL-data, ikke sist forsøkte Bluetooth-oppkobling. Verdien kan være gammel ved frakobling. Den eksisterende diagnostikksensoren beholder sin unique ID og eventuelle gamle entitets-ID.
7. Bruker du det medfølgende Xzense-kortet via `/local/xzense-card.js`, oppdater den med `www/xzense-card.js` i ZIP-en og endre ressurs-URL til `/local/xzense-card.js?v=05193b`. Hvis kortet er registrert med `/api/xzense_full_preview/xzense-card.js`, tøm nettleserbuffer/restart HA ved behov.
8. Test med fysisk tilsyn, særlig på overgang fra Ready til Operation, og se etter `bluetooth_update_interval_seconds` i diagnostikk. En oppdatering kan ta lenger tid enn angitt intervall på grunn av Bluetooth-oppkobling og 2 s etterventing.

**Tilbakeføring:** legg tilbake 0.5.19.2-mappen og start HA på nytt. Den gamle `active_update_interval_minutes`-innstillingen vil fremdeles ligge i konfigurasjonen. Justeringer du har gjort i sekunder i 0.5.19.3 kan ikke automatisk oversettes tilbake til 0.5.19.2, så kontroller aktivt intervall manuelt ved tilbakeføring.

**Begrensning:** Testene verifiserer lokal kode og simulert tilstand, ikke Bluetooth mot kontrollpanelet. Bruk ikke cachet status som en fersk sikkerhetstilstand.
# Xzense Alpha 0.5.19.2 – installasjon

1. Ta backup av nåværende `custom_components/xzense_full_preview` (spesielt den fungerende 0.5.19.1-versjonen) og noter kortets ressursadresse.
2. Erstatt **hele** mappen `/config/custom_components/xzense_full_preview` med den tilsvarende mappen i ZIP. Ikke slett eksisterende config entry, så beholdes PIN og innstillinger.
3. Start Home Assistant på nytt. Kontroller versjon **0.5.19.2** på integrasjonen og i diagnostikken.
4. Under Xzense-entitetene: kontroller `Bluetooth update interval` (gammelt entitets-ID, nå hvile/Ready, 0–120 min) og `Bluetooth active update interval` (ny, 0–10 min). De er som standard 5 min og 0 min, men 0.5.19.1-hvileintervallet bevares fra tidligere innstillinger.
5. Bruker du tilpasset dashboardkort? Kopier `www/xzense-card.js` til `/config/www/xzense-card.js`, og oppdater cache-parametret på Lovelace-ressursen, eksempelvis `/local/xzense-card.js?v=05192`. Det tilpassede kortet viser begge sliderne under «Konfigurasjon».
6. Test først med fysisk tilsyn: 5-minutters Ready-polling, overgang til kontinuerlig under Operation, Afterrun → ny fyring uten reset og kontrollert frakobling når status blir Ready. En kjent tilstandsendring fra panelet mens Bluetooth er nede kan bare oppdages ved neste planlagte avlesning.

**Tilbakeføring:** kopier den lagrede 0.5.19.1-mappen tilbake og start HA på nytt. Den gamle idle-slideren bruker samme unique_id som før; den nye aktive slideren blir utilgjengelig når du går tilbake. Lagrede timingdata fra 0.5.19.2 kan fortsatt ligge i HA `.storage`.

**Viktig:** Ikke stol på gammel, cachet `Ready`/`Operation` som bekreftet aktuell tilstand. Xzense styrer en fysisk vifte; testskriving må overvåkes. Ikke testet på kontrollpanelet i dette bygget.
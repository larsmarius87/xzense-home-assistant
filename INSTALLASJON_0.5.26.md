# Installasjon av Xzense Alpha 0.5.26 (testversjon)

Bygger på den sist **bekreftet fungerende** versjonen 0.5.25-rc1, med utvalgte
feilrettinger fra 0.5.25-final-fix1. Bluetooth-transport og proxyvalg er
uendret.

## Endringer

- Refueling: «Legg på ved» kan aktiveres kun når kontrollpanelet er i
  **Burnout (tilstand 5)**. Kommandoen er BOOST/REQ start=1 (samme kommando
  som Boost). Firmware velger Refueling (tilstand 7) og varighet fra
  GLOBAL 0x59, typisk 180 sekunder. Fra Operation (tilstand 4) ville samme
  kommando ha startet vanlig Boost med GLOBAL 0x4D, så knappene skilles.
- Retter `AttributeError` i sensor-ikon ved at ikonoppslag har sikker fallback.
- Oppdaterer radiolink-etikett og 0–3 signalstyrke-ikon. Rå entiteter som
  ikke trengs, skjules fra ny eksponering; eksisterende brukerdata fjernes ikke.
- Dashboard: batteri i øvre hjørne, Z-Wave-merke og tre radiolink-stolper
  på Bluetooth-linjen, ikon `mdi:forest` for ved og `mdi:turbine` for Boost.
  Fyringsvarighet ligger med de primære feltene; innetemperatur, utetemperatur
  og lufttrykk er på neste linje. Tid i nåværende modus er borte fra hovedkortet.
- Tar bort utdatert rødt varsel for fungerende temperaturføler og firmware-
  versjonstekst ved standardreferanser.

## Oppgradering

1. Behold en kopi av 0.5.25-rc1 som tilbakefallsversjon.
2. Kopier mappen `custom_components/xzense_full_preview` til
   `/config/custom_components/xzense_full_preview` på Home Assistant.
3. Kopier `www/xzense-card.js` til `/config/www/xzense-card.js`.
4. Endre ressurs-URL i dashboardet til `/local/xzense-card.js?v=0526`
   for å unngå gammel nettleser-cache.
5. Start Home Assistant på nytt, kontroller sensorer og driftsstatus.
6. Prøv «Legg på ved» bare når det er trygt og kontrollpanelet faktisk står
   i Burnout. Ved uventet oppførsel, rull tilbake til 0.5.25-rc1.

**Viktig:** Firmwareanalysen viser tilstandsbetingelsene, men 0.5.26 er ennå
ikke verifisert i drift på brukerens Xzense. Dette er derfor en testversjon.

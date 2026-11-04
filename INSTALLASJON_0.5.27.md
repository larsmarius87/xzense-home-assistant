# Installere korrigert Xzense 0.5.27

**Status:** Testutgave for eksisterende integrasjon. Refueling er bekreftet fungerende på fysisk panel ved riktig driftstatus, men full oppdatering er ikke langtidsverifisert.

## Oppdatering fra en eksisterende versjon

1. Ta en full Home Assistant-backup og behold en kopi av `/config/custom_components/xzense_full_preview/`.
2. Last ned [0.5.27 ZIP](xzense-alpha-0.5.27-source.zip), pakk den ut og kopier **hele** `custom_components/xzense_full_preview/` til `/config/custom_components/xzense_full_preview/`.
3. Kopier `www/xzense-card.js` til `/config/www/xzense-card.js`. Kontroller at dashboardressursen bruker `/local/xzense-card.js?v=0527` for å unngå gammel nettlesercache.
4. Start Home Assistant på nytt. Kontroller at eksisterende integrasjonsoppføring og PIN er bevart, og at temperaturer, radiolink, status, knapper og varsling oppfører seg som før.
5. Hvis noe ikke virker: gjenopprett forrige mappe/backup. 0.5.25 RC1 er siste versjon som tidligere var bekreftet stabil over tid.

**Ikke** bytt mappenavn til `xzense` eller fjern den gamle integrasjonsoppføringen ved denne oppdateringen. Domet er fortsatt `xzense_full_preview`. HACS-støtte og sikker migrering er planlagt, ikke implementert.

## Dette inneholder korrigert 0.5.27

- `Refueling`: Fra Utbrenning (status 5), knapp «Legg inn ved», status 7 «Vedpåfylling».
- Navnene «Radiolink – signalstyrke» og «Viftetype RS009-41», samt reviderte oversettelser.
- Varsling til flere valgte telefoner ved Drift (4) → Utbrenning (5); tittel «Xzense: Legg i mer ved».
- Ikonene `mdi:turbine` for Boost og `mdi:engine-outline` for Viftetype.
- Forsiktig registeropprydding begrenset til eksplisitt listede foreldede diagnostikk-/testentiteter. Rådiagnostikk beholdes.
- Samme BLE-protokoll og multi-proxy-strategi som tidligere. HACS er ikke lagt til.

**Kjente begrensninger:** HA kan bevare gamle egendefinerte entitetsnavn i sitt register. «Start fyring» / «Avslutt fyring» får egne integrasjonsikoner først i neste bygg. Fyringslogg i HA er fortsatt bare planlagt.

Integrasjonen styrer en fysisk skorsteinsvifte og skal ikke brukes som eneste sikkerhetsmekanisme.

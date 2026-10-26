# Xzense Alpha 0.5.20 – installasjon og rollback

Dette er en ny **testversjon** basert på din fungerende 0.5.19.3. Ingen fysisk Bluetooth-test er gjennomført.

1. Ta sikkerhetskopi av hele den installerte Xzense-integrasjonsmappen, **uansett om den hos deg heter `xzense`** eller `xzense_full_preview`. **Ikke endre mappenavn** eller domenet i `manifest.json` som ledd i denne oppgraderingen.
2. Åpne ZIP-arkivet og kopier **innholdet i** `custom_components/xzense_full_preview/` over filene i din **eksisterende** installerte integrasjonsmappe. Sjekk at `manifest.json` nå viser `0.5.20`. Ikke slett HA-konfigurasjonsoppføringen.
3. Restart Home Assistant. Kontroller at temperatur, STATUS og styrekommandoene vises som før. Følg med på CPU og Bluetooth-feil ved første oppstart.
4. Dashboardkort fra integrasjonsmappen: ressursen er `/api/xzense_full_preview/xzense-card.js?v=0520`, JavaScript-modul. **Dette er rutens navn fra kildekoden, ikke mappenavnet.** Hvis du bruker `/local/xzense-card.js`, må filen i `www/` i pakken kopieres til `/config/www/` og URL-en endres til `/local/xzense-card.js?v=0520`.
5. «Sist oppdatert» på kortet bruker nå eksisterende diagnostikksensor eller `last_data_at`-attributt på den tilordnede pipetemperatursensoren. `last_data_at` er blant de 12 fortsatt aktive diagnostikkentitetene.
6. De overflødige diagnostikkentitetene fra tidligere versjoner settes til **deaktivert av integrasjonen**, ikke slettet. Fullstendig rådiagnostikk kan fortsatt lastes ned fra Home Assistant-integrasjonen. De 12 operative diagnostikkentitetene forblir tilgjengelige.
7. Ved sterke, ferske signaler fra en tidligere fungerende proxy kan skannevinduet bli **0,8 sekunder**. Ellers beholdes **3,0 sekunder**. En mislykket rask runde gjentas én gang med fullt skannevindu.

**Tilbakeføring:** Kopier tilbake din 0.5.19.3-backup og start HA på nytt. 0.5.19.3-koden aktiverer igjen de diagnostikkentitetene som ble deaktivert av 0.5.20. Bruk dashboardressursens forrige cacheversjon `?v=05193b` ved behov. Eksisterende intervallinnstillinger forblir uendret.

**Merk:** Tidligere diagnostikkhistorikk fra Recorder er ikke slettet. Ingen tidsstyring, PIN eller Xzense-skrivekommandoer er endret. Versjonen må testes fysisk før den bør regnes som stabil.
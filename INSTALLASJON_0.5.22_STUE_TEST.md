# Xzense 0.5.22 – Stue-only Bluetooth test

**Begrenset diagnostikkbygg basert direkte på 0.5.21.** Ingen andre
funksjoner, kommandoer, skriveregler, pollingintervaller eller BLE-tidsgrenser
er endret. Dette er ikke en generell stabilitetsrettelse.

## Låst adapter

- Stue: `8C:D0:B2:A9:21:22` (eneste tillatte kilde).
- Gang: `E8:9F:6D:E8:66:86` (ikke brukt).
- Serverens USB: `A4:6B:40:5B:08:C9` (ikke brukt).
- Ingen adapter-fallback eller gjentatt kortskanning ved mislykket
  Stue-tilkobling i samme forsøk. Polling skjer fortsatt etter integrasjonens
  eksisterende intervallvalg.
- Når Stue ikke sender annonse innen den eksisterende 45-sekundersgrensen,
  vil tilkoblingen mislykkes. Ingen annen adapter prøves.

## Installasjon

1. Ta backup av eksisterende `custom_components/xzense_full_preview/`.
2. Pakk ut og kopier hele `custom_components/xzense_full_preview/` fra ZIP-en
   over eksisterende filer i `/config/custom_components/xzense_full_preview/`.
   Ikke lag en ny integrasjon og ikke endre config entry eller PIN.
3. Start Home Assistant på nytt. Integrasjonen skal vise versjon `0.5.22`.
4. I Xzense-diagnostikken: se etter `source_lock_active: true`,
   `locked_bluetooth_source: 8C:D0:B2:A9:21:22`, og at
   `selected_source`/`disconnect_history` for nye økter bare bruker Stue.
5. Observer antall vellykkede sesjoner, mottatte STATUS, feil og
   `source_fallbacks` (skal forbli 0 siden restart).

**Sikkerhet:** Start/stopp-/BOOST- og konfigurasjonskommandoer følger
fortsatt 0.5.21s eksisterende krav om ny status. En kommando kan fremdeles
feile hvis Bluetooth eller STATUS ikke virker. Bruk det fysiske Xzense-panelet
ved behov. Ikke trykk Start gjentatte ganger uten å verifisere driftstilstand.

## Tilbakeføring

Kopier tilbake 0.5.21 fra originalpakke eller backup og start HA på nytt.
Da er ordinært RSSI-basert adaptervalg og fallback tilbake.
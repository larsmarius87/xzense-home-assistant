# KRITISK oppdatering fra 0.5.16

0.5.15 og 0.5.16 har en hendelsesløkke-feil i `XzenseClient._connection_loop`:

```python
if self._wake.is_set():
    continue
```

Dette kan skape en uendelig busy-loop uten `await` når disconnect-signalet er aktivt men klienten fortsatt er tilkoblet, og dermed fryse hele HA. Denne feilbanen er rettet i Alpha 0.5.17. Det er en logisk/teknisk verifisert svakhet, men vi har ikke HA core dump fra bruker og kan dermed ikke bevise at den alene forårsaket den observerte frysingen. **IKKE installer 0.5.15 eller 0.5.16.** Ved problemer: deaktiver integrasjonen eller rull tilbake til 0.5.14. 0.5.17 må valideres på virkelig HA før den betegnes stabil.

---

# Xzense – overlevering til neste ChatGPT-chat

**Dato:** 22. oktober 2026  
**Siste bygg:** Alpha 0.5.16  
**Repository:** https://github.com/larsmarius87/xzense-home-assistant  
**Last ned:** https://github.com/larsmarius87/xzense-home-assistant/blob/main/xzense-alpha-0.5.16-source.zip

## Brukerens prioriteringer og arbeidsform

- Home Assistant, Exodraft Xzense BLE, firmware 4.10 (`CONNECT ACK version=410`), med PIN-basert app-autentisering. Dashboardet skal være på norsk; entitetsnavn på **engelsk frem til Beta**.
- Komplett integrasjonspakke ved hver Alpha-release, ikke løse kodebiter. Ikke lag YAML med mindre brukeren ber om det. Bevar eksisterende entitets-ID-er/unique-ID-er der mulig.
- Viktigste uløste problem akkurat nå: **Bluetooth-frakoblinger**, og at HA tidligere valgte feil ESPHome-proxy.
- Publiser source-ZIP og dokumentasjon til privat GitHub-repo. Ikke anta at klientens runtime mappe er lik manifest-domenet uten å verifisere.

## Miljø og adaptere

- Home Assistant OS i Proxmox-VM, Home Assistant 2026.10.2 i siste diagnostikk; timezone `Europe/Oslo`.
- Xzense Bluetooth-adresse `84:8B:CD:50:36:29`.
- Beste fysisk plasserte proxy **`bluetooth proxy stue` = `8C:D0:B2:A9:21:22`**, ESP32-C3. Bekreftet fungerende på −64 dBm ved oppkobling.
- Tidligere BLE-kilder `A4:6B:40:5B:08:C9` (−94 til −100 dBm) og `E8:9F:6D:E8:66:86` (rundt −91/−94 dBm).
- KONTROLLPANELET gikk fortsatt på **batteri** da `0x05` endret seg `3→2`, derfor er `0x05` **ikke bekreftet strømforsyningskode**. Ikke påstå `2 = nett` eller `3 = batteri`.

## Diagnoser og etterforskning av brudd

- 22.10 kl. 17:34: diagnostikk 0.5.14, forbindelse via `A4:6B:40:5B:08:C9`, RSSI −100 dBm, connection_attempts 258, disconnect_count 222.
- 22.10 kl. 17:43: diagnostikk 0.5.14, forbindelse via stue `8C:D0:B2:A9:21:22`, RSSI −64 dBm, connection_attempts 268, disconnect_count 231. Status ACK, PIN/CONNECT ACK fungerende.
- Senere HA-logger registrerte nye BLE-brudd; enkelte STATUS/REQ manglet svar ca. 3–4 sekunder før disconnected callback. **Callback forteller ikke om panelet, proxyen eller radioforbindelsen initierte bruddet.** Det er ikke bevist at stue-proxyen sto for alle senere brudd pga. hull i logghistorikken.
- 0.5.15 innførte `disconnect_history` med 20 siste brudd, klassifisering `local_shutdown`/`local_setup_failure_cleanup`/`unexpected_ble_callback`, session source/RSSI, tid, auth, og siste STATUS. En callback fra gammel klient skal ikke kunne påvirke en ny forbindelse.

## Alpha 0.5.16 – nye tekniske endringer

### Valg av Bluetooth-kilde

- 0.5.15 samlet bare vanlige HA BLE-callbacks i 3 sekunder. HA filtrerer identiske / ikke-valgte annonseringer; det førte til at stue-proxyen ikke alltid fantes i kandidatlisten.
- 0.5.16 bruker **`bluetooth.async_register_advertisement_callback`** (per-packet, per scanner) og **`bluetooth.async_scanner_devices_by_address(hass,address,connectable=True)`** (per-scanner-cache). Begge er dokumentert i offisielle HA Bluetooth API-er.
- Samler annonseringer i 3 sekunder etter første ferske, supplerer med HA cache, **sorterer strengt på RSSI**, og prøver neste ved oppkoblingsfeil. Ikke hardkodet MAC-adresse, ingen bonus for tidligere godkjent kilde.
- Nye diagnostikkfelt: `candidate_details`, `source_discovery_method`, `fresh_scanner_count`, `cached_scanner_count`, `selected_source`, `active_session_source`, RSSI og `disconnect_history`. Cached RSSI kan være eldre enn fersk måling. Bekreft reell proxy ved neste test.

### Tid i tilstand (`0x1A`)

- Enheten sender **16-biters teller** som eldre parser tolket signed, med -32768-jump og senere wrap 65535→0 etter **18 t 12 min 16 sek**.
- `Time in current state`: **eksisterende unique ID `state_timer` bevart**. Fra numeriske sekunder til `HH:MM:SS`; rå teller `raw & 0xffff`, antall fullstendige rundganger akkumulert ved konsistens mot veggklokke. Viser kontinuitet/usikkerhet som attributter.
- `status_state_timer` i diagnostikken beholder rå signed verdi; full diagnostikk viser nye korrigerte tidsfelt. Dette er **ikke** verifisert ved fysisk 65536-rollover i 0.5.16, men er testet syntetisk.

### Fire duration

- Ny sensor `Fire duration` / intern unique-ID-suffiks `fire_duration`.
- Teller en fyringsøkt gjennom state 3 Boosting, 4 Operation, 5 Burnout, 6 Afterrun, 7 Refueling frem til 2 Ready for lighting. State 8 Ventilation utløser ikke ny økt.
- Dersom HA ser Ready→Boosting, estimeres start ved mottatt rå state-timer og UTC. Dersom første observasjon allerede er under fyring: start ved første observert tidspunkt og `fire_quality=partial_observation` i stedet for å oppgi falskt nøyaktig full syklus.
- Ved lengre BLE-gap markeres varighet `estimated_after_gap`, og ved avslutning `estimated_end_after_gap`; kan ikke rekonstruere komplette skjulte sykluser.
- Etter fyring viser sensoren `00:00:00`, sist målte varighet ligger i attributtet `last_fire_duration_seconds`.
- Tidscache lagres av HA `Store` i `.storage/xzense_full_preview.timing_<entry_id>`, throttlet under normal drift + forsøkes ved unload. Etter uventet HA-stopp kan en kort periode mangle, men videreføres ved nye STATUS.
- Begge tidsensorer oppdateres ved STATUS vanligvis **hvert 10. sekund**, ikke hvert sekund.
- Dashbordet har nytt felt `Fyringsvarighet`, og ressurs-URL må versjonsoppdateres til `v=0516` hvis bruker kjører `/local`.

## Kjente protocol mappings

- `0x19` = device state; `0x1A` = state timer; `0x1B` = air pressure; `0x1C` inside temp; `0x1D` outside temp; `0x1E` chimney temp; `0x1F` fan speed; `0x20` unknown.
- Settings: `0x32` Sound, `0x33` Contrast, `0x34` Brightness (panel 68 %), `0x4B` Start temp, `0x4C` Stop temp, `0x4D` Boost time, `0x4E` Afterrun time, `0x4F` Boost speed, `0x50` Fan speed, `0x55` System control (0 manual), `0x56` temperature probe experimental, `0x58` alarm temp, `0x59` Refire time, `0x5B` Burnout timeout.
- Ukjente felter: `0x00`–`0x05` (inkl `0x05`!), `0x18`, `0x20`, `0x35`, `0x36`, og status bits. `0x02` økte omtrent sekund-for-sekund i flere prøver, men betydningen er ikke bekreftet.
- CONNECT/PIN/GATT/protokollkoder er bevart. STATUS polling hvert 10. sekund. Endre ikke skrivekommandoene uten egen eksplisitt test.

## Installasjonsadvarsel

- Manifest `domain=xzense_full_preview`, mens eldre runtime-logg viste `/config/custom_components/xzense/client.py`. Finn **aktiv mappe**, sjekk `manifest.json` før du kopierer. Ikke start to klienter til samme BLE-periferi.
- `www/xzense-card.js` i pakken eller `custom_components/xzense_full_preview/www/xzense-card.js` som innebygget ressurs.

## Validering og neste steg

1. Lokale tester er syntetiske, og BLE-endringene er **ikke testet på fysisk Xzense**. Les ny diagnostikk etter installasjon av 0.5.16.
2. Se om `candidate_details` inneholder stue, om `selected_source`/`active_session_source` faktisk velger stue med bedre RSSI, og følg `disconnect_history` over tid. Skill mellom scan, GATT, app-auth og status-timeout.
3. Test `Time in current state` ved signert 32768-grense og etter 65536-modulo; bekreft `HH:MM:SS`, `rollovers`, kontinuitet.
4. Test én full fyringssyklus. Bekreft overgang, summerte stadier, restart/persistens, og flagg ved Bluetooth-brudd.
5. Ikke gå videre til Beta før fysisk bekreftelse av de kritiske BLE- og timingfunksjonene.

**Start ny chat ved å laste opp denne Markdown-filen og diagnostikken fra 0.5.16.**
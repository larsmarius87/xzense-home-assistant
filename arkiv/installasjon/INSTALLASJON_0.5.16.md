# Xzense Alpha 0.5.16 – installasjon og test

## Innhold

Komplett kildekode, tester og oppdatert dashboard er inkludert i `xzense-alpha-0.5.16-source.zip`.

**Sikkerhet ved oppdatering:** Kontroller den faktisk aktive mappen under `/config/custom_components/`. Manifestet rapporterer domenet `xzense_full_preview`, mens en tidligere HA-kjøretidslogg viste `/config/custom_components/xzense/client.py`. Ikke opprett to parallelle Xzense-integrasjoner; sikkerhetskopier før du bytter ut filer. Erstatt hele innholdet i den aktive integrasjonsmappen med alle filene fra arkivets `custom_components/xzense_full_preview/` etter at du har bekreftet domenet i manifestet. Start Home Assistant på nytt.

## Bluetooth-valg

0.5.16 samler ferske Xzense-annonseringer fra alle connectable proxyer i 3 sekunder, legger til kilder som Home Assistant fortsatt har i per-scanner-cache, sorterer etter **høyeste RSSI**, og prøver øvrige kandidater ved feil. En cached RSSI kan være eldre enn en ny annonsering. Det er ikke noen tvungen MAC-lås.

Forventet sterk kandidat ved tidligere målinger: **stue `8C:D0:B2:A9:21:22`** (−64 dBm), mot eldre proxyer på −94 til −100 dBm. Dette må bekreftes på nytt etter installasjon.

I ny integrasjonsdiagnostikk: `source_discovery_method`, `candidate_details`, `selected_source`, `active_session_source`, `selected_source_rssi`, `disconnect_history`, `last_disconnect_kind`, `last_disconnect_session_seconds`. Bare en `unexpected_ble_callback` er ikke bevis for at Xzense tok initiativet til bruddet.

## Tidsfunksjoner

- **Time in current state**: beholdt eksisterende unike entitetsidentifikator `state_timer` og engelsk navn; nå formatet `HH:MM:SS` i stedet for numeriske sekunder. Underliggende `0x1A` er 16-biters, signert i gammel parser men korrigert til unsigned; full modulo-rundgang er 65 536 sekunder. Råverdien, antall rundganger og kontinuitet ligger i attributter. Historikk fra den gamle numeriske sensoren og den nye tekstsensoren er ikke direkte sammenlignbare.
- **Fire duration**: ny sensor med engelsk navn, men norsk merkelapp `Fyringsvarighet` på dashboardet. Teller gjennom Boosting, Operation, Refueling, Burnout og Afterrun til systemet kommer tilbake til Ready for lighting. Ventilation alene teller ikke som fyring. Etter avslutning vises 00:00:00 og sist varighet ligger i attributter.
- Begge oppdateres når integrasjonen mottar STATUS, normalt hvert 10. sekund; de er ikke klokker som oppdateres hvert sekund i HA.
- Beregningen lagres i HA `.storage` og forsøkes gjenopprettet etter restart. Start som ikke er observert markeres `partial_observation`; brudd på mer enn 40 sekunder kan gi `estimated_after_gap`; tid som ikke stemmer med motteken teller markeres `timer_reset_or_missed_transition`. Ved brudd kan hele sykluser ha skjedd mens HA var frakoblet, og de kan ikke rekonstrueres sikkert.

## Dashboard

Oppdatert versjon finnes både i `www/xzense-card.js` og `custom_components/xzense_full_preview/www/xzense-card.js`. Hvis du bruker `/config/www/xzense-card.js`, kopier den nye filen og oppdater Lovelace-ressursen til `/local/xzense-card.js?v=0516`. Hvis du bruker integrasjonens innebygde ressurs, er banen `/api/xzense_full_preview/xzense-card.js?v=0516`. Les `dashboard/INSTALLASJON.md` ved behov.

## Kontroll etter oppdatering

1. Diagnostikken skal vise `custom_components.xzense_full_preview.version: 0.5.16`.
2. Bekreft at `source_selection` viser `raw_per_scanner_plus_cache_strict_rssi_then_fallback`.
3. Verifiser at stue-proxyen faktisk finnes i `candidate_details` ved ny oppkobling, og se om `disconnect_count` stabiliserer seg.
4. Kontrollér Time in current state, Fire duration og attributtene; ikke bruk usikre fyringsvarigheter som eksakte logger.

**Kun lokal kode- og syntakstesting er gjort ved bygging.** Endringer i BLE og timer er ikke fysisk bekreftet mot Xzense-panelet.
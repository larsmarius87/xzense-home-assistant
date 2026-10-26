# Xzense 0.5.23 – Stue-only, mindre streng BLE-test

Installer ved å sikkerhetskopiere eksisterende `/config/custom_components/xzense_full_preview/`, erstatte hele mappen med `custom_components/xzense_full_preview/` fra ZIP-filen og starte Home Assistant på nytt. Behold eksisterende integrasjon, PIN og dashbord.

## Hva er endret?

1. Stue `8C:D0:B2:A9:21:22` forblir **eneste** tillatte BLE-kilde.
2. Hvis HA har et BLEDevice-håndtak fra *Stue selv*, kan det brukes selv uten en nylig annonsering fra Xzense. Integrasjonen venter 3 sekunder på en fersk Stue-annonse først.
3. Det gjøres aldri mer enn ett faktisk BLE-tilkoblingsforsøk i samme forsøk. Ved mislykket cacheforsøk er cache sperret i 120 sekunder, slik at feil ikke gir en rask tilkoblingssløyfe.
4. I Xzense-diagnostikken: `source_lock_active=true`; `source_selection=locked_stue_cache_permitted_no_fallback_test`; `cached_stue_without_fresh_count` teller cache-fallbacks. `candidate_sources` viser `per_scanner_cache` eller `fresh_raw_advertisement`.

**Viktig begrensning:** Hvis Stue ikke har oppdaget Xzense i det hele tatt, og det ikke finnes noen Stue-spesifikk BLEDevice i Home Assistant, kan denne endringen ikke tvinge frem en tilkobling. Da viser diagnostikken `locked_source_not_available`/`advertisement_timeout` i stedet for å bruke en annen adapter. Det er meningen.

Bruk fysisk kontrollpanel for sikker styring under testing. Ikke send gjentatte startkommandoer uten fersk, verifisert STATUS.

### Tilbakeføring

Installer 0.5.22-pakken på samme måte og start Home Assistant på nytt.
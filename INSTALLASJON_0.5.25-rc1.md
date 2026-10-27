# Xzense Alpha 0.5.25-rc1 – oppdatering og test

**Dato:** 27. oktober 2026. Bygget fra komplett 0.5.24 multi-proxy-kildepakke.

1. Lagre den fungerende 0.5.24-pakken og last ned en HA-backup.
2. Oppdater innholdet i den **eksisterende** `custom_components/xzense_full_preview/`-mappen med hele mappen fra 0.5.25-rc1. Ikke endre domene, filnavn for integrasjonen eller enhetens MAC.
3. Start Home Assistant på nytt. Åpne **Innstillinger → Enheter og tjenester → Xzense Alpha**.
4. Kontroller at temperaturer og viftehastighet samsvarer med det fysiske panelet. Prøv **ikke** nye skrivegrenser uten å verifisere at motor og pipe tåler dem.
5. Kontroller sensoren «Batteri kontrollpanel» (GLOBAL 0x04) og «Signalstyrke til kraftenhet» (GLOBAL 0x05). De er foreløpige identifikasjoner, ikke kalibrerte presisjonsmålinger.
6. Ved RS009-41-motor, aktiver **«RS009-41 motor»** under konfigurasjonsentitetene. Dette endrer bare minste tillatte *nye* innstilling fra 80 til 100 V. Er gjeldende verdi lavere enn 100 V, vises en advarsel; velg selv ny verdi på «Minste viftespenning», og trykk Lagre når dette er fysisk forsvarlig.
7. Følg Bluetooth-kilde og status under diagnostikk som i 0.5.24. Den nye «Ubrukte GLOBAL-verdier (0x)» viser et registerkart i attributtene. Enkelt-ID-er kan aktiveres i entitetsregisteret ved forskning.
8. Dersom du bruker det innebygde dashboardkortet, legg til/oppdater ressursen til `/api/xzense_full_preview/xzense-card.js?v=0525rc1` og tøm nettlesercachen om du fortsatt ser gammel tekst. Bruk `device_state_localized` i stedet for den eldre engelske statusen i eventuell manuell kortkobling.

**Viktig om områdegrenser:** Firmware 4.10_RC2 tillater enkelte langt videre intervaller enn den trykte manualen. HA bruker nå firmwarens min/maks etter avtale. Det betyr **ikke** at alle slike verdier er anbefalte for din installasjon. Seksgradersregelen og RS009-41-valget er ekstra lokale sperrer. Full automatisk firmwareoppdatering eller aktiv XTP-styring er ikke lagt til.

**Fabrikkreferanser:** start 40 °C, stopp 35 °C, boosttid 10 min, ettergang 30 min, pipetrekk 20 Pa, alarm 250 °C, min. spenning 100 V (manual). Boost-stopptemperatur 60 °C er brukerens valgte referanse og er forskjellig fra eldre manualreferanse 150 °C. Alle er informasjon; oppdateringen overskriver ikke kontrollpanelets eksisterende verdier.

**Tilbakerulling:** Legg tilbake din komplette 0.5.24-mappe og start HA på nytt. Det lokale `rs009_41_motor`-valget i config-entry options er ufarlig for gammel kode, som ignorerer det.

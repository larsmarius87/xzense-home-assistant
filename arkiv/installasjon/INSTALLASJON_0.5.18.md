# Xzense Alpha 0.5.18 – installasjon

Komplett kildekodepakke videreført fra Alpha 0.5.17. Integrasjonsdomenet er fortsatt `xzense_full_preview`.

## Endringer
- **Periodisk STATUS/REQ er av som standard.** Etter hver vellykket PIN/CONNECT-ACK sendes én STATUS/REQ ved tilkobling.
- Status sendes fortsatt kort tid etter Boost- og Ventilation-kommandoer.
- Under **Innstillinger → Enheter og tjenester → Xzense Alpha → Konfigurer** kan du velge Av, hvert 10. sekund, hvert 60. sekund eller hvert 5. minutt. Lagrede endringer laster integrasjonen på nytt.
- Passive `GLOBAL/DATA`-varsler mottas fortsatt. For sentrale sensorer velges den ferskeste prøven fra STATUS eller GLOBAL.
- Temperatur, viftehastighet, lufttrykk og driftstilstand får attributtene `last_observed_at`, `sample_age_seconds` og `sample_stale`. Etter 120 sekunder uten ny prøve merkes verdien som gammel. Home Assistant oppdaterer sensorattributtene lokalt omtrent hvert minutt når polling er av.
- Fire duration og Time in current state baseres fortsatt på faktiske meldinger og kan ikke garanteres oppdatert ved langvarig fravær av telemetri.
- Eksisterende BLE-proxyvalg, PIN, sesjonslogikk, tidslagring, kontroller, dashboard og diagnostikk videreføres.

## Installasjon
1. Kontroller at **bare én Xzense-integrasjon** er aktiv.
2. Ta en sikkerhetskopi av eksisterende `/config/custom_components/xzense_full_preview/`.
3. Last ned `xzense-alpha-0.5.18-source.zip` fra dette repoet.
4. Pakk ut ZIP-en og kopier **hele** mappen `custom_components/xzense_full_preview` til samme sted i Home Assistant. Ikke installer kildemappens toppnivå som integrasjon.
5. Start Home Assistant på nytt.
6. Kontroller versjon **0.5.18** under integrasjonen og at diagnostikken viser `status_poll_interval_seconds: 0`.
7. Når Bluetooth er slått på på kontrollpanelet igjen, sjekk at første STATUS mottas, og sammenlign `disconnect_history` med 0.5.17.

## Verifikasjon og begrensninger
- GitHub Actions verifiserer ZIP-struktur, Python-kompilering og `tests/test_status_polling_0518.py`.
- Dette er en **Alpha som ikke er verifisert mot fysisk Xzense**.
- Når polling er avslått, kan enkelte verdier i dashboardet bli stående på siste mottatte måling. Bruk `sample_stale` eller velg et lengre intervall om oppdatering trengs.
- Hvis testversjonen har problemer, velg polling hvert 10. sekund eller rull tilbake til 0.5.17.

**Sikkerhet:** Ikke test kontrollkommandoer med brennende ild dersom en slik test kan skape utrygge trekk- eller røykforhold.

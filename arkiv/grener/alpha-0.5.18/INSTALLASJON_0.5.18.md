# Xzense Alpha 0.5.18 – valgfri STATUS-polling

**Testbygg basert på Alpha 0.5.17.** BLE proxyvalg, autentisering og eksisterende skrivekommandoer er beholdt.

- STATUS/REQ sendes én gang ved oppkobling og etter Boost/Ventilation.
- Periodisk polling er av som standard; valg: Av, 10 sekunder, 60 sekunder eller 5 minutter.
- Passive GLOBAL/DATA behandles. Siste observerte sample prioriteres.
- Sensorattributter viser tidspunkt, målingsalder og stale etter 120 sekunder.
- Tidsensorene oppdateres ikke kontinuerlig uten innkommende data.
- Når kontrollpanelets Bluetooth igjen aktiveres, test dette separat fra fyringssyklus.

## Installasjon
1. Kontroller at bare én Xzense-integrasjon er aktiv.
2. Verifiser at aktiv HA-mappe er `custom_components/xzense_full_preview` og manifest domain samsvarer.
3. Pakk ut og erstatt **hele** integrasjonsmappen fra ZIP.
4. Start HA på nytt, bekreft manifestversjon 0.5.18.
5. Under **Innstillinger → Enheter og tjenester → Xzense Alpha → Konfigurer** velger du ønsket STATUS-frekvens. Standard er Av.
6. Bekreft i diagnostikken at `status_poll_interval_seconds=0`.

**Alpha / eksperimentell:** Syntetisk kildekodeverifikasjon, ikke fysisk Xzense-test. Ved behov kan du velge 10 sekunders polling eller rulle tilbake til 0.5.17.

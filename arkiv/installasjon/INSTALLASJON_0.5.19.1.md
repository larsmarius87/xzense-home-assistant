# Xzense Alpha 0.5.19.1 – Afterrun-oppstart

Engangsversjon fra 0.5.19 med én funksjonell endring: Start opptenning også i tilstand 6 (Afterrun).

1. Ta backup av fungerende installasjon, helst 0.5.17/0.5.19.
2. Erstatt hele `/config/custom_components/xzense_full_preview/` med `custom_components/xzense_full_preview/` fra ZIP. Ikke bytt domenenavn eller slett PIN-konfigurasjonen.
3. Start Home Assistant på nytt. Kontroller `manifest.json`/Diagnostikk for versjon 0.5.19.1.
4. Hvis du bruker den innebygde dashboardressursen, oppdater nettlesercachen (eventuelt legg til `?v=05191` i ressurssiden dersom nødvendig) for å få «Start ny fyring»-etiketten i Afterrun.
5. Test ved Afterrun med kontroll på det fysiske panelet: trykk «Start ny fyring» én gang, og kontroller om panelet sender BOOST/ACK eller BOOST/NACK og om STATUS faktisk skifter til Boosting/Operation/Reheating.

**Ikke en bekreftet maskinvarefunksjon:** Firmware har en BOOST start=1-kommando, men vi har ikke fysisk bekreftet aksept i Afterrun. At HA-servicekallet returnerer, betyr ikke at start er bekreftet. Dersom tilstanden forblir Afterrun, regnes ikke ny økt.

**Sikkerhet:** Ikke bruk eksperimentell styring uten tilsyn ved varm peis.

For øvrige installasjons- og tilbakeføringsdetaljer, se `INSTALLASJON_0.5.19.md`.
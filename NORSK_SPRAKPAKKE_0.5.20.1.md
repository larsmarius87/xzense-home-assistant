# Norsk språkpakke – Xzense Alpha 0.5.20.1

Denne oppdateringen baseres på **0.5.20**, og oversetter navnene på alle 136 registrerte entiteter
(inkludert de 85 diagnostikksensorene som normalt er deaktivert), ved hjelp av Home Assistants
innbygde oversettelsessystem.

Språk:
- `strings.json`: engelske kildestrenger, inkludert entitetsnavn
- `translations/en.json`: engelske oversettelser
- `translations/nb.json`: norske bokmålsoversettelser

**Viktig:** HA bruker språket i **Home Assistant-serverens** oppsett når standardnavn for entiteter
opprettes. Grensesnittspråk for den enkelte brukeren overstyrer ikke nødvendigvis eksisterende
entitetsnavn. Navn du tidligere har tilpasset manuelt, beholdes.

### Installere

1. Ta backup av den fungerende 0.5.20.
2. Kopier hele innholdet av `custom_components/xzense_full_preview/` i ZIP-en over innholdet i
   **din eksisterende integrasjonsmappe**; du trenger ikke bytte mappenavn.
3. Start Home Assistant på nytt.
4. Kontroller versjon `0.5.20.1` og språk. Ikke slett integrasjonen eller entitetene.

Merk: Dersom de gamle engelske standardnavnene er lagret i HA-registeret, er det ikke garantert
at de endres automatisk. De kan da tilbakestilles på entitetens innstillinger uten å endre
entitets-ID-en. Eksisterende automatiseringer blir ikke omskrevet.

### Hva er ikke endret?

- Bluetooth-proxyvalg, autentisering, hurtigskanning, tilkoblingsintervaller og timerlogikk.
- Unike entitets-ID-er, registry keys og protokollkart.
- Verdiene fra STATUS, GLOBAL og selve styringskommandoene.
- System control-alternativenes interne engelske tekst (for å bevare stabil skrivemapping).
- Kortets ressursadresse fra 0.5.20: `/api/xzense_full_preview/xzense-card.js?v=0520`.

### Kjent begrensning

Dette er en oversettelse av **entitetsnavn**, ikke alle råverdier. Driftstilstandene som
`Operation` og `Afterrun` leveres fremdeles fra protokolltolkeren på engelsk, slik at
dashboards og automasjoner som sammenligner disse tekstene ikke påvirkes. Norsk lokalisering
av statusverdiene kan legges til separat når hele verdikjeden er verifisert.
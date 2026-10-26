# Xzense Alpha 0.5.20.2 – norsk oversettelse av driftstilstander

Basert på 0.5.20.1 med brukerens egne navn «Ettergangstid» og «Gjenfyrings-tid».

## Driftstilstander

I `custom_components/xzense_full_preview/translations/nb.json` finner du:

`entity → sensor → device_state_localized → state`

Her kan alle de 11 statusnavnene redigeres, blant annet `ready_for_lighting` → «Klar for fyring».

- Den **opprinnelige** sensoren `device_state` beholder engelske råtilstander, `unique_id` og entity_id for at eksisterende automasjoner og historikk ikke skal endres.
- En **ny** `device_state_localized`-sensor bruker Home Assistants innebygde enum-oversettelser. I Home Assistant vises statusen på norsk når visningsspråket er bokmål; intern sensorverdi er en stabil kode som `ready_for_lighting`.
- Det egne Xzense-dashboardkortet viser norsk status fra samme oversettelsesnøkler via `hass.localize` når de er tilgjengelige, ellers den inkluderte norske reserveoversettelsen.
- STATUS-pakker, GLOBAL-protokoll, Bluetooth og skriving til kontrollpanelet er uendret.
- Entitetsnavnene «Ettergangstid» og «Gjenfyrings-tid» fra brukerens reviderte språkfil er bevart.

## Installering

1. Ta backup av eksisterende integrasjonsmappe.
2. Kopier **innholdet** av `custom_components/xzense_full_preview/` i ZIP-en til din nåværende installasjonsmappe. Den kan fortsatt hete `xzense`; ikke endre mappenavnet for dette.
3. Restart Home Assistant og kontroller versjon `0.5.20.2`.
4. For Xzense-kortet registrert via integrasjonen: bruk `/api/xzense_full_preview/xzense-card.js?v=05202` som JavaScript-modul. Ved `/local/` må den nye `www/xzense-card.js` kopieres til `/config/www/`.
5. Når du har redigert `nb.json` manuelt, restart Home Assistant (og eventuelt oppdater nettleseren) for å laste språkfilen på nytt.

**Merk:** Custom card bruker innebygd norsk reserveoversettelse hvis frontend ikke leverer `hass.localize`; denne reserven endres ikke bare ved å redigere `nb.json`. Den nye lokaliserte sensoren bruker derimot HA-oversettelsene. Om du ønsker andre tekster også i reservevisningen på kortet, kan vi synkronisere disse ved neste bygg.

## Tilbakeføring

0.5.20.1-pakken kan legges tilbake uten endring av gamle entitets-ID-er. Den nye lokaliserte sensoren blir ikke lenger oppdatert av den eldre versjonen.

Statuskodene ligger isolert i `state_localization.py`; `protocol.py` er byte-for-byte uendret fra 0.5.20.1.
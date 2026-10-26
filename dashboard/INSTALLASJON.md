# Xzense Alpha 0.5.14 – Dashboardinstallasjon

## Anbefalt: kortet som separat Lovelace-ressurs

1. Last ned [xzense-alpha-0.5.14-source.zip](../arkiv/versjoner/xzense-alpha-0.5.14-source.zip) og pakk den ut.
2. Kopier `www/xzense-card.js` til `/config/www/xzense-card.js` i Home Assistant. Opprett `www` om nødvendig.
3. Gå til **Innstillinger → Dashboard → Ressurser** og registrer URL `/local/xzense-card.js?v=0514` med typen **JavaScript-modul**.
4. Fjern eventuelle gamle ressurser som `/api/xzense_full_preview/xzense-card.js?v=0514` for å unngå dobbeltregistrering.
5. Oppdater dashbordet hardt i nettleseren, og legg til et **Manuelt** kort:

```yaml
type: custom:xzense-card
title: Xzense
entities: {}
```

6. Rediger kortet. Den visuelle redigeringen lar deg velge riktig Home Assistant-entitet og visningsnavn for hver funksjon.

**Viktig:** `/local/xzense-card.js` hentes fra `/config/www/xzense-card.js` og fungerer uansett om integrasjonsmappen heter `xzense` eller `xzense_full_preview`. Ikke endre integrasjonens mappenavn uten å sjekke at det samsvarer med `domain` i `manifest.json`.

## Integrasjonsversjonen

ZIP-filen inneholder kildekode for `custom_components/xzense_full_preview`, med eget integrasjonsdomene. Den skal bare installeres/oppdateres som denne utviklingsintegrasjonen. Ikke erstatt en eksisterende `custom_components/xzense` direkte med denne mappen.

## Verifisering

84 Python-tester og JavaScript-smoketest passert. Temperaturprobe På/Av (`0x56`) er eksperimentell, med ikke fysisk verifisert 0/1-mapping. Ingen endring av BLE-protokoll fra 0.5.13.

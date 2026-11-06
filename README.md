# Xzense for Home Assistant

**English** · [Norsk](#norsk)

An unofficial Home Assistant integration for **Exodraft Xzense**, providing extensive monitoring, control and configuration over Bluetooth Low Energy (BLE). Alongside the functions available in the official app, it exposes additional settings, sensors and diagnostics directly in Home Assistant.

**Current HACS test version: 0.5.28.3** · Integration name: **Xzense** · Domain and folder: `xzense`

> **Development release:** This integration is under active development. Some controls are based on firmware analysis and have not been fully verified on a physical controller. It is not affiliated with or supported by Exodraft.

## English

### Features

| Area | Functionality |
|---|---|
| Monitoring | Operating state, chimney temperature, indoor/outdoor temperature, air pressure, fan speed and control-panel battery |
| Radio link | Signal strength (0–3) between the Xzense control panel and power unit; distinct from Home Assistant's BLE RSSI |
| Fireplace control | Start firing, stop firing, Boost, ventilation and refueling in supported controller states |
| Settings | Temperature thresholds, fan settings, Boost/afterrun durations, panel brightness, contrast and sound |
| Bluetooth | Local BLE connection through Home Assistant Bluetooth adapters or ESPHome Bluetooth proxies; configurable polling intervals and proxy fallback |
| Notifications | Optional notifications to one or more phones when the controller moves from Operation to Burnout |
| Diagnostics | BLE connection diagnostics, firmware information and additional read-only values |

**Refueling:** The Refuel action is available in **Burnout (state 5)**. The controller can enter **Refueling (state 7)** for the configured refire time. This behavior has been tested on a physical controller.

**Entity icons:** Start firing `mdi:fire`, stop firing `mdi:fire-off`, refuel `mdi:forest`, Boost `mdi:turbine` and RS009-41 motor type `mdi:engine-outline`. The Norwegian sensor label for the last successful Bluetooth synchronization is **Sist BT-synk**.

### Installation with HACS

1. Open **HACS** in Home Assistant.
2. From the menu, select **Custom repositories**.
3. Enter `https://github.com/larsmarius87/xzense-home-assistant` and select **Integration**.
4. Find **Xzense** in HACS and download it.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration**, search for **Xzense**, and complete the setup using your controller's Bluetooth address and PIN as requested.

This repository currently publishes the HACS test integration from its **`HACS` branch**, with code installed to `custom_components/xzense/`. For a fresh installation you do not need to rename any folders or manually copy integration Python files.

**Optional dashboard card:** The bundled Xzense card **automatically discovers its sensors and controls through the Home Assistant entity and device registries**, even after entity renaming. With multiple Xzense devices, select the target device in the card editor; manual entity overrides remain available. Add a card using `type: custom:xzense-card`. The dashboard resource must be registered separately (the HACS integration is not an independent frontend plugin). The bundled JavaScript is served at `/api/xzense_full_preview/xzense-card.js` for manually configured dashboard resources. The historical path is retained for compatibility; it does **not** indicate the integration's current domain.

**Dashboard buttons:** Start firing, refuel and stop firing now work when Home Assistant reports a button state of `unknown` before its first use. Truly unavailable buttons remain disabled.

**Battery display:** The panel battery sensor is capped at 100% in Home Assistant. Raw GLOBAL `0x04` values remain available in diagnostic exports.

### Current status and limitations

- Version **0.5.28.3** is intended for HACS testing. The HACS layout and Python syntax are checked automatically.
- The main features are based on the corrected **0.5.27** codebase, with native entity icon fixes and the shorter integration name.
- Some Bluetooth writes and advanced controller settings still require live testing.
- A Home Assistant firing-session history is planned, not implemented.
- The controller's internal historical log transfer is not implemented.

For stability and safety, make a Home Assistant backup before experimental updates. Avoid running two copies of Xzense against the same Bluetooth controller.

### Documentation

[Changelog](CHANGELOG.md) · [Version history](REVISJONER.md) · [BLE protocol notes](docs/PROTOCOL_MANIFEST.md) · [Feature matrix](docs/FEATURE_MATRIX.md) · [Development roadmap](VEIKART.md) · [Legacy ZIP releases on main](https://github.com/larsmarius87/xzense-home-assistant/tree/main)

---

## Norsk

En uoffisiell Home Assistant-integrasjon for **Exodraft Xzense** med omfattende overvåking, styring og konfigurasjon via Bluetooth Low Energy (BLE). I tillegg til funksjonene fra originalappen gir den tilgang til flere innstillinger, sensorer og diagnostikk direkte i Home Assistant.

**Gjeldende HACS-testversjon: 0.5.28.3** · Integrasjonsnavn: **Xzense** · Domene og mappe: `xzense`

> **Utviklingsversjon:** Integrasjonen er under aktiv utvikling. Enkelte kontroller er basert på analyse av fastvaren og er ikke ferdig testet på fysisk enhet. Prosjektet er ikke tilknyttet eller støttet av Exodraft.

### Funksjoner

| Område | Funksjonalitet |
|---|---|
| Overvåking | Driftstilstand, pipetemperatur, inne-/utetemperatur, lufttrykk, viftehastighet og batterinivå på panelet |
| Radiolink | Signalstyrke (0–3) mellom kontrollpanel og kraftenhet, ikke Bluetooth-signalstyrken mot Home Assistant |
| Fyringsstyring | Start fyring, avslutt fyring, Boost, ventilasjon og vedpåfylling i relevante driftstilstander |
| Innstillinger | Temperaturgrenser, vifteinnstillinger, Boost-/ettergangstid, lysstyrke, kontrast og lyd |
| Bluetooth | Lokal BLE via Home Assistants Bluetooth-adaptere eller ESPHome Bluetooth-proxyer, med justerbare intervaller og automatisk reservevalg |
| Varsling | Valgfritt varsel til én eller flere telefoner når kontrolleren går fra Drift til Utbrenning |
| Diagnostikk | Bluetooth-diagnostikk, fastvareinformasjon og ytterligere skrivebeskyttede verdier |

**Vedpåfylling:** Knappen **Legg inn ved** er tilgjengelig ved **Utbrenning (tilstand 5)**. Panelet kan da gå til **Vedpåfylling (tilstand 7)** i den innstilte påfyllingstiden. Denne funksjonen er testet på fysisk panel.

**Entitetsikoner:** Start fyring `mdi:fire`, avslutt fyring `mdi:fire-off`, legg inn ved `mdi:forest`, Boost `mdi:turbine` og Viftetype RS009-41 `mdi:engine-outline`. Sensoren for siste vellykkede Bluetooth-synkronisering heter **Sist BT-synk**.

### Installering med HACS

1. Åpne **HACS** i Home Assistant.
2. Velg **Egendefinerte pakkelagre** i menyen.
3. Legg til `https://github.com/larsmarius87/xzense-home-assistant` og velg kategorien **Integration**.
4. Finn **Xzense** i HACS og last ned integrasjonen.
5. Start Home Assistant på nytt.
6. Gå til **Innstillinger → Enheter og tjenester → Legg til integrasjon**, søk etter **Xzense**, og fullfør oppsettet med Bluetooth-adresse og PIN når du blir bedt om det.

Integrasjonen publiseres foreløpig fra **`HACS`-grenen** og installeres i `custom_components/xzense/`. Ved nyinstallasjon trenger du ikke endre mappenavn eller kopiere Python-filer manuelt.

**Valgfritt dashboardkort:** Xzense-kortet **finner sensorer og kontroller automatisk via Home Assistants enhets- og entitetsregister**, også når entitetene har fått egne navn. Har du flere Xzense-enheter, velger du riktig enhet i kortredigeringen. Manuell overstyring er fortsatt mulig. Legg til kortet med `type: custom:xzense-card`. Dashboardressursen må registreres separat (HACS-integrasjonen er ikke en egen frontendutvidelse). Det innebygde JavaScript-kortet serveres på `/api/xzense_full_preview/xzense-card.js` for manuell registrering av dashboardressurs. Den gamle URL-en er beholdt av kompatibilitetshensyn og betyr **ikke** at integrasjonen bruker det gamle domenet.

**Dashboardknapper:** Start fyring, Legg inn ved og Avslutt fyring fungerer nå også når Home Assistant viser `unknown` før knappen har vært brukt. Faktisk utilgjengelige knapper er fortsatt deaktivert.

**Batterivisning:** Batterisensoren viser maksimalt 100 % i Home Assistant. Råverdien fra GLOBAL `0x04` beholdes i diagnostikkeksporten.

### Status og begrensninger

- **0.5.28.3** er en HACS-testversjon. Mappestruktur og Python-syntaks blir kontrollert automatisk.
- Funksjonaliteten bygger på korrigert **0.5.27**, med oppdaterte integrasjonsikoner og kortere integrasjonsnavn.
- Enkelte Bluetooth-skrivekommandoer og avanserte innstillinger trenger fortsatt fysisk testing.
- Egen fyringslogg i Home Assistant er planlagt, men ikke implementert.
- Overføring og dekoding av historiske logger fra kontrollpanelet er ikke implementert.

Ta backup av Home Assistant før eksperimentelle oppdateringer. Unngå å kjøre to Xzense-integrasjoner mot samme Bluetooth-kontroller samtidig.

### Dokumentasjon

[Endringslogg](CHANGELOG.md) · [Revisjonsarkiv](REVISJONER.md) · [BLE-protokoll](docs/PROTOCOL_MANIFEST.md) · [Funksjonsmatrise](docs/FEATURE_MATRIX.md) · [Veikart](VEIKART.md) · [Eldre ZIP-versjoner på main](https://github.com/larsmarius87/xzense-home-assistant/tree/main)

---

## Safety / Sikkerhet

**EN:** This is a community-developed integration and not an official Exodraft product. Home Assistant must not replace the Xzense panel's safety controls, alarms or local operation.

**NO:** Dette er en uoffisiell integrasjon og ikke et produkt fra Exodraft. Home Assistant må ikke erstatte kontrollpanelets sikkerhetsfunksjoner, alarmer eller lokale betjening.

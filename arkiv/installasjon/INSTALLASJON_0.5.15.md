# Xzense Alpha 0.5.15 – Bluetooth-oppdatering

**[Last ned ZIP](xzense-alpha-0.5.15-source.zip)**

## Integrasjonsmappe

Arkivet har fortsatt Home Assistant-domain xzense_full_preview og kildekoden under custom_components/xzense_full_preview/.
Ikke gi integrasjonsmappen nytt navn uten å kontrollere domain i manifest.json.

En tidligere kjøretidslogg viste /config/custom_components/xzense/client.py, mens HA-diagnostikken rapporterte domain xzense_full_preview.
Ta derfor sikkerhetskopi og kontroller fysisk plassering av den aktive integrasjonen før du erstatter noe.

Normalt: erstatt hele mappen /config/custom_components/xzense_full_preview/ med komplett mappe fra ZIP, og restart Home Assistant.
Hvis den aktive mappen faktisk heter /config/custom_components/xzense/, verifiser manifest/domain før du velger hvilke filer som skal byttes. Unngå å opprette to parallelle integrasjoner.

## Dashboard

Dashboardkortet er uendret fra 0.5.14. Ressursen fra /config/www/xzense-card.js bruker fortsatt /local/xzense-card.js?v=0514.

## Diagnostikk

Etter restart, bekreft manifest 0.5.15 og adapter_collection_window_seconds = 3.0.
Sjekk selected_source, active_session_source, preferred_source, last_disconnect_kind og disconnect_history.
unexpected_ble_callback betyr bare at denne integrasjonen ikke initierte disconnect. Det betyr ikke at Xzense-kontrolleren med sikkerhet avsluttet forbindelsen.

**Revision 0.5.15 (95 tests):** Guards delayed callbacks from a previously closed BLE client so they cannot reset a replacement connection. Also protects against a lost disconnect wake-up during application handshake. No change to the physical Xzense packet encoding.

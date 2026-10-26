# Xzense Alpha 0.5.24 – Flere proxyer igjen

## Installasjon
1. Ta backup av `config/custom_components/xzense_full_preview`.
2. Pakk ut ZIP. Erstatt hele `custom_components/xzense_full_preview` med mappen fra pakken.
3. Start Home Assistant på nytt og kontroller at integrasjonen viser `0.5.24`.
4. Ny stue-proxy må være registrert og tilgjengelig i Home Assistant Bluetooth/ESPHome. Ingen MAC-adresse skal legges inn i Xzense.

## Tilkoblingsstrategi
- Finner alle adaptere som har observert Xzense; ny stue-proxy blir brukt automatisk når den har annonsert enheten. Dette gjelder også ved manuelt utløst tilkobling.
- Rangerer BLE-observasjoner etter RSSI. Ved mislykket Bleak-tilkobling eller GATT-oppsett fortsetter den til neste kandidat i samme runde.
- Hvis det ikke kommer fersk annonsering, prøver den etter 3 sekunder HA sin kildebestemte cache fra alle proxyer (120 s karantene etter cachefeil).
- Ett BLE-tilkoblingsforsøk per proxy og opptil seks per runde. Ingen rekursive forsøksløkker.
- En BLE-tilkobling som lykkes, men mangler senere Xzense CONNECT ACK / STATUS, blir ikke byttet i samme runde. Ny oppkoblingsrunde håndterer videre testing.

## Diagnose
Se `source_lock_active=false`, `source_selection=multi_proxy_rssi_per_scanner_cache_and_fresh_fallback`, `candidate_details`, `selected_source`, `active_session_source`, `last_failed_source` og `source_fallbacks`.

*Kan ikke verifisere den nye proxyens radio eller firmware på avstand. Backup og kontroll av at Xzense har lokal betjening anbefales før test.*
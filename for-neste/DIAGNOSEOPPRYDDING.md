# For neste versjon: utgåtte diagnoseentiteter som fortsatt står som utilgjengelige

Rapportert etter 0.5.25: Legacy-sensorene **GLOBAL 0x5B raw**, **GLOBAL 0x35/0x50/0x55 raw**, **Experimental write probes**, **Fan probe ...**, **Last write probe ...**, **Status auxiliary raw**, **Status flag**, **Status polling interval** og **Status state selector** står fortsatt i Home Assistant.

Sannsynlig årsak: Oppryddingen i 0.5.25 bruker eksakt `unique_id = address_suffix`. Historiske Alpha-builds kan ha registrert samme suffix med andre prefikser, slik at oppføringen ikke matcher.

Tiltak i `0.5.26-registry-cleanup.patch`:
- Behold eksakt liste over kjente utgåtte suffixer.
- Match også `_suffix` på slutten av `unique_id`, uavhengig av eldre prefiks og store/små bokstaver.
- Søk **kun** i entitetsregisteroppføringer for den aktuelle Xzense-konfigurasjonsoppføringen.
- Unngå å fjerne aktive kontroller og sensorer.
- Ingen endringer i Bluetooth, kontrollkommandoer, diagnostikkens rådata eller dashboardkort.

Test: 185 automatiske tester passert. Må fortsatt valideres etter oppdatering i faktisk Home Assistant, siden registerinnholdet ikke følger med diagnostikkfilene. Endringer er kun klargjort, ingen ny ZIP/release publisert.

# For neste versjon: ikoner under «Kontroller»

Forberedt fra kildepakkens `0.5.25`-filer. **Ikke en ny release, og ikke del av den publiserte 0.5.25 ZIP-en.**

| HA-entitet | Ikon | Endring |
|---|---|---|
| Start fyring | `mdi:fire` | Nytt |
| Legg på ved | `mdi:fireplace` | Nytt |
| Avslutt fyring | `mdi:fire-off` | Nytt |
| Boost | `mdi:turbine` | Beholdt |
| Ventilasjon | `mdi:fan` | Beholdt |
| Viftehastighet | `mdi:fan-chevron-up` | Nytt |

Omfang: HA-integrasjonen, ikke Lovelace-/dashboardkortet. Endringer kun i `button.py` og `number.py`. Ingen Bluetooth- eller styringslogikk endret.

`for-neste/0.5.26-kontroller-ikoner.patch` er en unified diff mot `xzense-alpha-0.5.25-source.zip` (på rotnivå inne i ZIP).

Teststatus i arbeidskopien: `run_tests_0525.py` → 184 passed, 0 failed. Ikonene er verifisert som eksisterende MDI-navn, men fysisk Home Assistant UI er ikke testet.

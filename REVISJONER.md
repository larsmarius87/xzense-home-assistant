# Xzense – versjonsarkiv og revisjonsoversikt

Oppdatert 26. oktober 2026. **Nyeste tilgjengelige bygg: 0.5.24 Alpha.**

Dette er en historisk oversikt over **eksisterende ZIP-filer i GitHub-repoet**, ikke en liste over generelt støttede eller anbefalte installasjoner. ZIP-ene er kildearkiver som inneholder komplette integrasjonsfiler for aktuell revisjon. Se også [README](README.md), [CHANGELOG](CHANGELOG.md) og [installasjon for 0.5.24](INSTALLASJON_0.5.24_MULTI_PROXY.md).

> **Advarsel:** 0.5.15 og 0.5.16 har en kjent asyncio busy-loop som kan fryse Home Assistant. Versjonene beholdes kun som historikk. 0.5.17 rettet denne konkrete feilen.

## Tilgjengelige kildepakker

| Revisjon | Komplett kilde-ZIP | Viktigste endring | Dokumentasjon |
|---|---|---|---|
| 0.5.2 | [Last ned](xzense-alpha-0.5.2-source.zip) | Tidlig BLE-integrasjon | – |
| 0.5.5 | [Last ned](xzense-alpha-0.5.5-source.zip) | Tidlig utvidelse av Xzense-kontroller | – |
| 0.5.6 | [Last ned](xzense-alpha-0.5.6-source.zip) | Protokollutvikling og diagnose | – |
| 0.5.7 | [Last ned](xzense-alpha-0.5.7-source.zip) | Firmwarebasert mapping av v4.10-kontroller | – |
| 0.5.11 | [Last ned](xzense-alpha-0.5.11-source.zip) | Styringsopprydding, Boost/Ventilation | – |
| 0.5.12 | [Last ned](xzense-alpha-0.5.12-source.zip) | Alarmtemperatur, konfigurering og ChimneyLog-undersøkelse | – |
| 0.5.12b | [Last ned](xzense-alpha-0.5.12b-source.zip) | Refuel i Operation/Burnout og råstatus 0x05/0x18 | – |
| 0.5.13 | [Last ned](xzense-alpha-0.5.13-source.zip) | SemVer- og manifestkorrigering | – |
| 0.5.14 | [Last ned](xzense-alpha-0.5.14-source.zip) | Dashboardkort, temperaturprobe, diagnostikk | – |
| 0.5.15 | [Last ned](xzense-alpha-0.5.15-source.zip) | Proxyvalg og frakoblingshistorikk — **ikke bruk: kjent busy-loop** | [INSTALLASJON_0.5.15.md](INSTALLASJON_0.5.15.md) |
| 0.5.16 | [Last ned](xzense-alpha-0.5.16-source.zip) | Per-proxy RSSI og fyringstimere — **ikke bruk: kjent busy-loop** | [INSTALLASJON_0.5.16.md](INSTALLASJON_0.5.16.md) |
| 0.5.17 | [Last ned](xzense-alpha-0.5.17-source.zip) | Reparasjonsversjon for asyncio busy-loop | [INSTALLASJON_0.5.17.md](INSTALLASJON_0.5.17.md) |
| 0.5.18 | [Last ned](xzense-alpha-0.5.18-source.zip) | Polling-eksperiment | [INSTALLASJON_0.5.18.md](INSTALLASJON_0.5.18.md) |
| 0.5.19 | [Last ned](xzense-alpha-0.5.19-hybrid-source.zip) | Periodisk BLE, behovsstyrt tilkobling og lagrede sensorverdier | [INSTALLASJON_0.5.19.md](INSTALLASJON_0.5.19.md) |
| 0.5.19.1 | [Last ned](xzense-alpha-0.5.19.1-afterrun-source.zip) | Start ny fyring fra Afterrun | [INSTALLASJON_0.5.19.1.md](INSTALLASJON_0.5.19.1.md) |
| 0.5.19.2 | [Last ned](xzense-alpha-0.5.19.2-dual-interval-source.zip) | Separate intervaller for hvile/aktiv drift | [INSTALLASJON_0.5.19.2.md](INSTALLASJON_0.5.19.2.md) |
| 0.5.19.3 | [Last ned](xzense-alpha-0.5.19.3-slider-seconds-source.zip) | Sekundbasert aktivt intervall og sliderfiks | [INSTALLASJON_0.5.19.3.md](INSTALLASJON_0.5.19.3.md) |
| 0.5.20 | [Last ned](xzense-alpha-0.5.20-adaptive-ble-source.zip) | Redusert diagnostikk og adaptivt skannevindu | [INSTALLASJON_0.5.20.md](INSTALLASJON_0.5.20.md) |
| 0.5.20.1 | [Last ned](xzense-alpha-0.5.20.1-norsk-sprakpakke-source.zip) | Norske entitetsnavn | [NORSK_SPRAKPAKKE_0.5.20.1.md](NORSK_SPRAKPAKKE_0.5.20.1.md) |
| 0.5.20.1 (revidert) | [Last ned](xzense-alpha-0.5.20.1-norsk-sprakpakke-revidert-source.zip) | Revidert språkpakke (samme manifestversjon) | [NORSK_SPRAKPAKKE_0.5.20.1.md](NORSK_SPRAKPAKKE_0.5.20.1.md) |
| 0.5.20.2 | [Last ned](xzense-alpha-0.5.20.2-norske-driftstilstander-source.zip) | Norske driftstilstander | [NORSKE_DRIFTSTILSTANDER_0.5.20.2.md](NORSKE_DRIFTSTILSTANDER_0.5.20.2.md) |
| 0.5.21 | [Last ned](xzense-alpha-0.5.21-burnout-notifications-source.zip) | Valgfrie pushvarsler ved Operation → Burnout | [INSTALLASJON_0.5.21.md](INSTALLASJON_0.5.21.md) |
| 0.5.22 | [Last ned](xzense-alpha-0.5.22-stue-only-test-source.zip) | Låst Bluetooth-kilde: gammel Stue (test) | [INSTALLASJON_0.5.22_STUE_TEST.md](INSTALLASJON_0.5.22_STUE_TEST.md) |
| 0.5.23 | [Last ned](xzense-alpha-0.5.23-stue-only-relaxed-source.zip) | Låst Stue med kildebestemt cache-fallback (test) | [INSTALLASJON_0.5.23_STUE_RELAXED.md](INSTALLASJON_0.5.23_STUE_RELAXED.md) |
| 0.5.24 | [Last ned](xzense-alpha-0.5.24-multi-proxy-relaxed-source.zip) | Automatisk multi-proxy, RSSI-sortering og cache-fallback | [INSTALLASJON_0.5.24_MULTI_PROXY.md](INSTALLASJON_0.5.24_MULTI_PROXY.md) |

## Tilleggspakker (ikke komplette installasjoner)

Disse brukes bare til å sammenligne eller hente enkeltfiler. For vanlig installasjon brukes **komplett kilde-ZIP** over.

- [0.5.20.1 språkpakke – tillegg](xzense-alpha-0.5.20.1-norsk-sprakpakke-tillegg.zip)
- [0.5.20.1 revidert språkpakke – tillegg](xzense-alpha-0.5.20.1-norsk-sprakpakke-revidert-tillegg.zip)
- [0.5.20.2 norske driftstilstander – tillegg](xzense-alpha-0.5.20.2-norske-driftstilstander-tillegg.zip)
- [0.5.21 varslinger – tillegg](xzense-alpha-0.5.21-burnout-notifications-tillegg.zip)

## Dokumenterte endringer uten eget arkiv

README og eldre protokolldokumentasjon beskriver blant annet revisjonene **0.5.8, 0.5.9 og 0.5.10**. De har **ikke separate kilde-ZIP-er i repoet** per denne oversikten. Vi viser derfor ikke oppdiktede nedlastingslenker. Heller ikke 0.5.3 eller 0.5.4 finnes som egne ZIP-er i det gjennomgåtte repoet.

## Installasjon, kompatibilitet og sikkerhet

1. Ta backup av gjeldende integrasjonsmappe og konfigurasjon.
2. Bruk komplett ZIP for ønsket revisjon, og erstatt mappen `/config/custom_components/xzense_full_preview/`.
3. Start Home Assistant på nytt, og kontroller versjonen i integrasjonens diagnostikk.
4. Behold domenet `xzense_full_preview` og eksisterende oppføring slik at entity-ID-er og innstillinger ikke går tapt.

**0.5.24-kontroll:** Diagnostikk fra 26.10.2026 bekreftet 8 vellykkede applikasjonsautentiseringer, 8 STATUS-svar og 2 skrive-ACK-er med flere Bluetooth-proxyer. Dette beviser oppkobling og avlesning, men ikke langvarig stabilitet eller alle kontrollkommandoer.

Dette er en eksperimentell integrasjon for et fysisk peis-/skorsteinssystem. Ikke bruk automatisering som eneste sikkerhetsmekanisme; kontroller med det fysiske Xzense-panelet. 

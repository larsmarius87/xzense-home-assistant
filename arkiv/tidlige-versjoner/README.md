# Historiske Xzense-kildearkiver (0.1–0.4)

Dette er originale ZIP-filer fra Xzense-utviklingen. **De fleste er eksperimentelle og ikke kompatible med dagens integrasjonsdomene `xzense_full_preview`. Ikke installer på et produksjonssystem.**

- `kildearkiver/` har autentiske eldre versjoner av Xzense HA-integrasjonen, samt en separat lab-versjon.
- `IKKE_INSTALLER/` inneholder bevisst isolerte autentiseringstester. `0.3.1` inneholder en hardkodet test-PIN i kildekoden. Den er bevart **kun for historikk i dette private repoet**.
- Dette er **originale binære ZIP-filer**. Filene ble kopiert uten endring, og Git blob-SHA er kontrollert mot lokale originaler.

Nåværende brukervennlig versjon er 0.5.24; se [README](../../README.md), [CHANGELOG](../../CHANGELOG.md) og [revisjonsoversikt](../../REVISJONER.md). 0.5.15 og 0.5.16 er kjente farlige busy-loop-versjoner i hovedarkivet.

## Historiske GitHub-arbeidsflyter

- [`arbeidsflyter/publish-xzense-0518.yml.txt`](arbeidsflyter/publish-xzense-0518.yml.txt) er en ren tekstkopi av den tidligere automatiseringen for 0.5.18. Den er **ikke aktiv** under `.github/workflows/`.
- Arkivgjenoppretting gjennom `.github/workflows/backfill-xzense-archives.yml` kan fortsatt kjøres **manuelt** om originalarkivene må kontrolleres eller gjenopprettes; den startes ikke automatisk ved push.

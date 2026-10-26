# Xzense Alpha 0.5.17 — kritisk hendelsesløkke-rettelse

**0.5.15 og 0.5.16 skal ikke installeres eller brukes videre:** Begge inneholder en synkron `continue` ved aktivt `_wake` i `_connection_loop`, som kan låse Home Assistants asyncio-hendelsesløkke under BLE-gjentilkobling.

**Tryggeste valg ved ustabil HA:** Deaktiver integrasjonen eller gå tilbake til 0.5.14 (sist brukt uten denne spesifikke feilen). Sikker modus i HA OS kan startes via VM-konsollen: `ha core restart --safe-mode`. Sikkermodus laster ikke inn egendefinerte integrasjoner; deaktiver Xzense før en normal omstart. Ta gjerne backup før endringer.

**Hva 0.5.17 retter:** Fjerner den blokkerende busy-loop-grenen. Når en BLE-sesjon er tilkoblet, blir et allerede aktivt wake-signal konsumert før et ekte asynkront ventepunkt. Tilkoblingstilstand sjekkes rett før ventingen. Det finnes en faktisk regresjonstest mot funksjonen.

**Videreføring:** Inkluderer 0.5.16 sin RSSI-basert proxyvalg og begge tidsfunksjonene, men disse er ikke fysisk verifisert på panelet.

**Installasjon:** Verifiser fysisk aktiv integrasjonsmappe før oppdatering. Domenet i manifestet er `xzense_full_preview`, men tidligere logg viste `/config/custom_components/xzense/client.py`; IKKE opprett duplikatmapper. Erstatt alle filene i aktiv mappe med kildefilene fra `custom_components/xzense_full_preview/`, og start HA på nytt. Verifiser at diagnostikk viser `0.5.17`.

**Testing:** Lokale tester og en isolert asyncio-regresjonstest kan vise at den konkrete frysingen er fjernet, men dette er fortsatt ikke en full integrasjonstest av Home Assistant og fysisk Xzense. Hold HA-backup og 0.5.14 tilgjengelig.

**Hvis HA fortsatt krasjer:** Ta HA-kjernelogger og Supervisor-logg (`ha core logs`, `ha supervisor logs`) fra VM-konsollen, og se om containeren faktisk restartes eller bare blir utilgjengelig.
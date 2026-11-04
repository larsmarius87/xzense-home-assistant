from pathlib import Path
import json, zipfile
root=Path("_build_0527")
app=root/"custom_components"/"xzense_full_preview"
p=app/"translations"/"en.json"
d=json.loads(p.read_text())
d["entity"]["sensor"]["signal_strength"]["name"]="Radio link signal strength"
d["options"]["step"]["init"]["data"]["burnout_notification_target"]="Phones to notify"
d["options"]["error"]["target_required"]="Select at least one phone before enabling notifications."
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
p=app/"strings.json"
s=json.loads(p.read_text())
s["entity"]=d["entity"]
s["options"]=d["options"]
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
p=root/"tests"/"test_release_0527_naming.py"
t=p.read_text().replace("    assert en['entity']['sensor']['last_data_at']['name']","    assert en['entity']['sensor']['signal_strength']['name']=='Radio link signal strength'\n    assert en['options']['step']['init']['data']['burnout_notification_target']=='Phones to notify'\n    assert en['entity']['sensor']['last_data_at']['name']")
p.write_text(t)
p=root/"tests"/"test_release_0514.py"
t=p.read_text().replace('"0.5.25-rc1", "0.5.27"', '"0.5.25-rc1", "0.5.26", "0.5.27"')
p.write_text(t)
# Preserve version 0.5.27; adjust only the requested Norwegian button label.
for rel in [
    "custom_components/xzense_full_preview/translations/nb.json",
    "custom_components/xzense_full_preview/www/xzense-card.js",
    "www/xzense-card.js",
    "tests/test_release_0527_naming.py",
    "CHANGELOG.md",
]:
    file = root / rel
    text = file.read_text()
    file.write_text(text.replace("Legg i ved", "Legg inn ved"))

# Restore agreed 0.5.25 final UI and cleanup without reverting 0.5.27 BLE/refueling.
p=app/"switch.py"
s=p.read_text().replace('_attr_icon = "mdi:engine"','_attr_icon = "mdi:engine-outline"').replace('"boost": "mdi:fire"','"boost": "mdi:turbine"')
p.write_text(s)
p=app/"burnout_notifications.py"
s=p.read_text().replace('NOTIFY_TITLE = "Xzense – utbrenning"','NOTIFY_TITLE = "Xzense: Legg i mer ved"').replace('NOTIFY_MESSAGE = "Xzense har gått fra normal drift til utbrenning."','NOTIFY_MESSAGE = "Legg i mer ved."')
p.write_text(s)
p=app/"__init__.py"
s=p.read_text()
anchor='        "boost_on", "boost_off", "start_afterrun",\n'
assert s.count(anchor)==1
extra='''        # 0.5.25 final: retired diagnostic/test entities only.
        "raw_global_35", "raw_global_50", "raw_global_55",
        "global_0x35_raw", "global_0x50_raw", "global_0x55_raw",
        "experimental_write_probes", "fan_probe_baseline_raw",
        "fan_probe_observed_fan_speed", "fan_probe_restored_fan_speed",
        "fan_probe_target_raw", "last_write_probe",
        "last_write_probe_result", "status_auxiliary_raw",
        "status_flag", "status_flags", "status_polling_interval",
        "status_state_selector",
'''
s=s.replace(anchor,anchor+extra)
p.write_text(s)
p=root/"tests"/"test_release_0527_regressions.py"
p.write_text('''"""Regression tests: approved 0.5.25 final fixes in 0.5.27."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"custom_components"/"xzense_full_preview"

def test_025_icons_restored():
    s=(ROOT/"switch.py").read_text()
    assert '_attr_icon = "mdi:engine-outline"' in s
    assert '"boost": "mdi:turbine"' in s
    assert '"boost": "mdi:fire"' not in s

def test_025_notification_message_multi_phone_preserved():
    s=(ROOT/"burnout_notifications.py").read_text()
    assert 'NOTIFY_TITLE = "Xzense: Legg i mer ved"' in s
    assert 'NOTIFY_MESSAGE = "Legg i mer ved."' in s
    assert 'for target in valid:' in s
    assert 'previous != 4 or state != 5' in s
    assert 'multiple=True' in (ROOT/"config_flow.py").read_text()

def test_025_registry_cleanup_exact_old_test_ids():
    s=(ROOT/"__init__.py").read_text()
    for suffix in ("raw_global_35","raw_global_50","raw_global_55",
                   "experimental_write_probes", "status_flags", "last_write_probe"):
        assert '"'+suffix+'"' in s
    assert 'entity_entry.unique_id in obsolete_unique_ids' in s
    assert 'er.async_entries_for_config_entry(registry, entry.entry_id)' in s
    assert 'reduced_diagnostics' in s

def test_027_refuel_restrictions_preserved():
    s=(ROOT/"button.py").read_text()
    assert 'return self.client.controls_available and state == 5' in s
    assert 'return getattr(self, "_attr_icon", None)' in (ROOT/"sensor.py").read_text()
''')
p=root/"CHANGELOG.md"
p.write_text('''### 0.5.27 – korrigert testpakke (samme versjonsnummer)
- Gjenopprettet ikonene mdi:turbine (Boost) og mdi:engine-outline (RS009-41) fra 0.5.25 final.
- Gjenopprettet utbrenningsvarslet «Xzense: Legg i mer ved», beholdt flervalg av telefoner.
- Gjeninnført avgrenset opprydding av foreldede test- og råverdi-entiteter fra 0.5.25 final.
- Beholdt 0.5.27 sin egen Refueling-styring, BLE-kode og trygg sensorikon-fallback.
- Lagt til regresjonstester for tilbakefallene.

'''+p.read_text())
p=root/"INSTALLASJON_0.5.27.md"
p.write_text(p.read_text()+'''
### Korrigert 0.5.27
Gjenoppretter historiske ikoner, varslingstekst og registeropprydding.
Ta backup før oppdatering. Oppryddingen fjerner kun eksplisitt navngitte
foreldede entiteter i Xzense-integrasjonen. Egendefinerte entitetsnavn i
Home Assistant kan måtte tilbakestilles manuelt.
''')

out=Path("xzense-alpha-0.5.27-source.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for f in sorted(root.rglob("*")):
        if f.is_file() and not any(x in f.parts for x in ("__pycache__",".pytest_cache")) and not f.name.endswith(".pyc"):
            z.write(f,f.relative_to(root))

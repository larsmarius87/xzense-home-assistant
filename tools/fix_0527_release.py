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

out=Path("xzense-alpha-0.5.27-source.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for f in sorted(root.rglob("*")):
        if f.is_file() and not any(x in f.parts for x in ("__pycache__",".pytest_cache")) and not f.name.endswith(".pyc"):
            z.write(f,f.relative_to(root))

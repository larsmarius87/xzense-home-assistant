from pathlib import Path
import json, zipfile, shutil, re
ROOT=Path.cwd()
SRC=ROOT/'xzense-alpha-0.5.26-source.zip'
OUT=ROOT/'_build_0527'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
with zipfile.ZipFile(SRC) as z:z.extractall(OUT)
APP=OUT/'custom_components/xzense_full_preview'
p=APP/'config_flow.py';s=p.read_text()
s=s.replace('from homeassistant.core import callback','from homeassistant.core import callback\nfrom homeassistant.helpers import selector')
start=s.index('class XzenseOptionsFlow(OptionsFlow):')
s=s[:start]+'''class XzenseOptionsFlow(OptionsFlow):
    """Select multiple mobile phones for burnout notifications."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure multiple Companion notify entities or mobile_app services."""
        current = self.config_entry.options
        choices = mobile_notification_targets(self.hass)
        choices.pop(NO_NOTIFY_TARGET, None)
        stored = current.get(CONF_BURNOUT_NOTIFY_TARGET, [])
        if isinstance(stored, str):
            selected = [] if stored in ("", NO_NOTIFY_TARGET) else [stored]
        elif isinstance(stored, list):
            selected = [value for value in stored if isinstance(value, str) and value != NO_NOTIFY_TARGET]
        else:
            selected = []
        for value in selected:
            if value not in choices:
                choices[value] = f"Tidligere valgt telefon ({value})"

        errors: dict[str, str] = {}
        if user_input is not None:
            enabled = bool(user_input.get(CONF_BURNOUT_NOTIFY_ENABLED, False))
            targets = user_input.get(CONF_BURNOUT_NOTIFY_TARGET, [])
            if not isinstance(targets, list) or any(
                not isinstance(target, str) or target not in choices for target in targets
            ):
                errors["base"] = "invalid_target"
            elif enabled and not targets:
                errors["base"] = "target_required"
            else:
                return self.async_create_entry(
                    data={**current,
                          CONF_BURNOUT_NOTIFY_ENABLED: enabled,
                          CONF_BURNOUT_NOTIFY_TARGET: list(dict.fromkeys(targets))}
                )

        schema = vol.Schema({
            vol.Required(
                CONF_BURNOUT_NOTIFY_ENABLED,
                default=current.get(CONF_BURNOUT_NOTIFY_ENABLED, False)
            ): bool,
            vol.Required(
                CONF_BURNOUT_NOTIFY_TARGET,
                default=selected,
            ): selector.SelectSelector(selector.SelectSelectorConfig(
                options=[selector.SelectOptionDict(value=value, label=label)
                         for value, label in choices.items()],
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )),
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
'''
p.write_text(s)
p=APP/'burnout_notifications.py';s=p.read_text()
start=s.index('        target = opts.get(CONF_BURNOUT_NOTIFY_TARGET, "")')
end=s.index('\n    async def _async_send',start)
s=s[:start]+'''        stored = opts.get(CONF_BURNOUT_NOTIFY_TARGET, [])
        if isinstance(stored, str):
            targets = [stored]
        elif isinstance(stored, list):
            targets = stored
        else:
            targets = []
        valid = list(dict.fromkeys(
            target for target in targets
            if isinstance(target, str) and (
                target.startswith("entity:notify.")
                or target.startswith("service:mobile_app_")
            )
        ))
        if not valid:
            _LOGGER.warning("Xzense burnout notification enabled but no valid phone is selected")
            return
        for target in valid:
            self.entry.async_create_background_task(
                self.hass,
                self._async_send(target),
                f"xzense-burnout-notification-{self.entry.entry_id}",
            )
'''+s[end:]
p.write_text(s)
# Copy exact approved labels from the historical 0.5.25 final package.
hist=ROOT/'xzense-alpha-0.5.25-source.zip'
with zipfile.ZipFile(hist) as z:
    for locale in ['nb','en']:
        path=f'custom_components/xzense_full_preview/translations/{locale}.json'
        before=json.loads((APP/'translations'/f'{locale}.json').read_text())
        approved=json.loads(z.read(path))
        for kind,key in [('sensor','signal_strength'),('switch','rs009_41_motor')]:
            if kind in approved.get('entity',{}) and key in approved['entity'][kind]:
                before['entity'][kind]['name']=before['entity'][kind].get('name') if False else before['entity'][kind].get('name')
                before['entity'][kind][key]['name']=approved['entity'][kind][key]['name']
        if locale=='nb':
            before['entity']['button']['refuel']['name']='Legg i ved'
            before['entity']['sensor']['device_state_localized']['state']['refueling']='Vedpåfylling'
            before['options']['step']['init']['description']='Velg én eller flere telefoner som skal varsles når Xzense går fra Drift til Utbrenning. Krever Home Assistant Companion med varsler aktivert. Ingen varsling ved oppstart eller gjentatte statusmeldinger.'
            before['options']['step']['init']['data']['burnout_notification_target']='Mobiler som skal varsles'
            before['options']['error']['invalid_target']='En av de valgte mobilene er ikke tilgjengelig.'
            before['options']['error']['target_required']='Velg minst én mobil før du aktiverer varsling.'
        else:
            before['entity']['sensor']['last_data_at']['name']='Last updated (Bluetooth)'
            before['options']['error']['invalid_target']='One of the selected phones is unavailable.'
            before['options']['step']['init']['description']='Send a push notification to one or more selected phones on Operation to Burnout. Requires Home Assistant Companion with notifications enabled. Startup and repeated STATUS messages do not notify.'
        (APP/'translations'/f'{locale}.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
p=APP/'strings.json';d=json.loads(p.read_text());en=json.loads((APP/'translations/en.json').read_text());d['entity']=en['entity'];d['options']=en['options'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for p in [APP/'manifest.json',APP/'const.py']:
    p.write_text(p.read_text().replace('0.5.26','0.5.27'))
for p in [APP/'www/xzense-card.js',OUT/'www/xzense-card.js']:
    s=p.read_text().replace('Xzense panel card 0.5.26.','Xzense panel card 0.5.27.').replace('Xzense Dashboard 0.5.26','Xzense Dashboard 0.5.27').replace('Xzense-kort 0.5.26','Xzense-kort 0.5.27')
    s=s.replace("{key:'refuel',name:'Legg på ved'","{key:'refuel',name:'Legg i ved'").replace('"refueling":"Påfylling av ved"','"refueling":"Vedpåfylling"')
    p.write_text(s)
for p in (OUT/'tests').glob('test_*.py'):
    s=p.read_text().replace('0.5.26.2','0.5.27').replace("assert 'Xzense Dashboard 0.5.26'","assert 'Xzense Dashboard 0.5.27'").replace('assert "Xzense-kort 0.5.26"','assert "Xzense-kort 0.5.27"').replace('assert "0.5.26" in card','assert "0.5.27" in card')
    p.write_text(s)
(OUT/'tests/test_release_0527_naming.py').write_text("""import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'custom_components'/'xzense_full_preview'
def test_027_titles():
    nb=json.loads((APP/'translations'/'nb.json').read_text())
    en=json.loads((APP/'translations'/'en.json').read_text())
    assert nb['entity']['sensor']['signal_strength']['name']=='Radiolink – signalstyrke'
    assert nb['entity']['switch']['rs009_41_motor']['name']=='Viftetype RS009-41'
    assert nb['entity']['button']['refuel']['name']=='Legg i ved'
    assert nb['entity']['sensor']['device_state_localized']['state']['refueling']=='Vedpåfylling'
    assert en['entity']['sensor']['last_data_at']['name']=='Last updated (Bluetooth)'
def test_027_mobile():
    assert 'multiple=True' in (APP/'config_flow.py').read_text()
    assert 'for target in valid:' in (APP/'burnout_notifications.py').read_text()
""")
(OUT/'INSTALLASJON_0.5.27.md').write_text("""# Xzense Alpha 0.5.27
Oppgrader ved å erstatte /config/custom_components/xzense_full_preview med katalogen i ZIP.
Kopier www/xzense-card.js til /config/www/xzense-card.js og bruk /local/xzense-card.js?v=0527.
Start Home Assistant på nytt. Test radiolink, viftetype, flervalgsvarsling og driftstatus 7.
0.5.25 RC1 er siste bekreftet fungerende test mot fysisk panel.
Eksisterende egendefinerte entitetsnavn i HA må eventuelt tilbakestilles manuelt.
""")
p=OUT/'CHANGELOG.md';p.write_text("""## 0.5.27 (2026-11-03)
- Radiolink – signalstyrke og Viftetype RS009-41, historiske navn gjenopprettet.
- Refueling = Vedpåfylling, knapp = Legg i ved.
- Mobilvarsling til flere telefoner; historiske valg migreres.
- Oversettelser og visningskort oppdatert uten endringer i BLE-transport.

"""+p.read_text())
p=OUT/'README.md';s=p.read_text().replace('Xzense Alpha 0.5.26 –','Xzense Alpha 0.5.27 –').replace('(INSTALLASJON_0.5.26.md)','(INSTALLASJON_0.5.27.md)');p.write_text(s)
archive=ROOT/'xzense-alpha-0.5.27-source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for f in OUT.rglob('*'):
        if f.is_file() and '__pycache__' not in f.parts and not f.name.endswith('.pyc'):
            z.write(f,f.relative_to(OUT))
print("built",archive,archive.stat().st_size)

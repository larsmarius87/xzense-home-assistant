"""Build Xzense 0.5.28.3 HACS integration from corrected 0.5.27.

Only HACS development branch. No changes to the original ZIP or to main.
"""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "xzense-alpha-0.5.27-source.zip"
OLD_DOMAIN = "xzense_full_preview"
NEW_DOMAIN = "xzense"
APP = ROOT / "custom_components" / NEW_DOMAIN
VERSION = "0.5.28.3"


def build():
    if not ARCHIVE.is_file():
        raise RuntimeError("Missing corrected 0.5.27 source ZIP")
    old = ROOT / "custom_components" / OLD_DOMAIN
    if old.exists():
        shutil.rmtree(old)
    if APP.exists():
        shutil.rmtree(APP)
    APP.mkdir(parents=True)
    prefix = f"custom_components/{OLD_DOMAIN}/"
    with zipfile.ZipFile(ARCHIVE) as z:
        for name in sorted(z.namelist()):
            if not name.startswith(prefix) or name.endswith("/"):
                continue
            rel = Path(name[len(prefix):])
            if rel.is_absolute() or ".." in rel.parts:
                raise RuntimeError(f"Unsafe ZIP entry: {name}")
            target = APP / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
    for expected in ("__init__.py", "manifest.json", "const.py", "config_flow.py", "client.py"):
        if not (APP / expected).is_file():
            raise RuntimeError(f"Missing {expected}")

    manifest_path = APP / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("domain") != OLD_DOMAIN:
        raise RuntimeError(f"Wrong source domain {manifest.get('domain')}")
    manifest.update({
        "domain": NEW_DOMAIN,
        "name": "Xzense",
        "version": VERSION,
        "documentation": "https://github.com/larsmarius87/xzense-home-assistant",
        "issue_tracker": "https://github.com/larsmarius87/xzense-home-assistant/issues",
        "codeowners": ["@larsmarius87"],
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    const_path = APP / "const.py"
    c = const_path.read_text()
    if 'DOMAIN = "xzense_full_preview"' not in c:
        raise RuntimeError("Source domain constant changed: stop build")
    c = c.replace('DOMAIN = "xzense_full_preview"', 'DOMAIN = "xzense"')
    c = c.replace('"0.5.27"', f'"{VERSION}"').replace("'0.5.27'", f"'{VERSION}'")
    const_path.write_text(c)

    init = APP / "__init__.py"
    s = init.read_text()
    # Existing dashboards keep their old resource URL, while new installs use /api/xzense.
    s = s.replace(
        'StaticPathConfig(\n                "/api/xzense_full_preview/xzense-card.js",',
        'StaticPathConfig(\n                "/api/xzense_full_preview/xzense-card.js",'
    )
    # In 0.5.28 DOMAIN is xzense. The old side-by-side guard checks
    # hass.data["xzense"], which is the current integration itself.
    # Only the old domains count as competing integrations.
    self_guard = 'hass.data.get("xzense") or hass.data.get("xzense_preview")'
    if self_guard not in s:
        raise RuntimeError("Self-blocking guard not found in source; review required")
    s = s.replace(self_guard, 'hass.data.get("xzense_full_preview") or hass.data.get("xzense_preview")')
    if self_guard in s:
        raise RuntimeError("Self-blocking guard not fixed")
    init.write_text(s.replace('Xzense Alpha', 'Xzense'))

    # Keep the 0.5.27 entity icons, and apply the two agreed native button
    # icons. These are integration entity icons, not just dashboard artwork.
    switches = APP / "switch.py"
    sw = switches.read_text()
    if '"boost": "mdi:turbine"' not in sw or '_attr_icon = "mdi:engine-outline"' not in sw:
        raise RuntimeError("0.5.27 Boost / motor-type icons are missing")
    buttons = APP / "button.py"
    b = buttons.read_text()
    needle = "        super().__init__(client, feature)\n"
    replacement = (
        "        super().__init__(client, feature)\n"
        "        self._attr_icon = {\n"
        '            "start_fire": "mdi:fire",\n'
        '            "stop_fire": "mdi:fire-off",\n'
        '            "refuel": "mdi:forest",\n'
        '        }.get(feature.key, "mdi:gesture-tap-button")\n'
    )
    if needle not in b:
        raise RuntimeError("Xzense button constructor changed")
    buttons.write_text(b.replace(needle, replacement, 1))

    # Bluetooth interval entities use direct number input in HA Devices & Services.
    # Do not change dashboard card controls or any other numeric entities.
    number_path = APP / "number.py"
    number_source = number_path.read_text(encoding="utf-8")
    for class_name in ("XzenseUpdateInterval", "XzenseActiveUpdateInterval"):
        class_start = number_source.find(f"class {class_name}(")
        if class_start < 0:
            raise RuntimeError(f"Missing {class_name} in number.py")
        mode_start = number_source.find("_attr_mode = NumberMode.SLIDER", class_start)
        next_class = number_source.find("\\nclass ", class_start + 1)
        if mode_start < 0 or (next_class >= 0 and mode_start > next_class):
            raise RuntimeError(f"Expected slider in {class_name}; review source")
        number_source = (
            number_source[:mode_start]
            + "_attr_mode = NumberMode.BOX"
            + number_source[mode_start + len("_attr_mode = NumberMode.SLIDER"):]
        )
    if number_source.count("_attr_mode = NumberMode.BOX") < 3:
        raise RuntimeError("Bluetooth number input replacement incomplete")
    number_path.write_text(number_source, encoding="utf-8")


    for p in APP.rglob("*.py"):
        if p.name not in ("client.py", "__init__.py"):
            s = p.read_text()
            s = s.replace("Xzense Alpha", "Xzense")
            p.write_text(s)
    # The dashboard card is authored separately from the source ZIP, and its
    # registry-based auto-linking must never be lost during rebuilding.
    source_card = ROOT / "tools" / "xzense_card_05281.js"
    if not source_card.is_file():
        raise RuntimeError("Missing 0.5.28.1 dashboard card")
    js = source_card.read_text(encoding="utf-8")
    for required in ("config/entity_registry/list", "config/device_registry/list",
                     "unique_id.endsWith('_'+key)", "xz-device"):
        if required not in js:
            raise RuntimeError(f"Dashboard auto-link check failed: {required}")
    (APP / "www" / "xzense-card.js").write_text(js, encoding="utf-8")

    # Keep OLD_DOMAIN storage namespaces in client.py to preserve saved state and fire durations.
    if f"{OLD_DOMAIN}.timing_" not in (APP / "client.py").read_text():
        raise RuntimeError("Stored timing namespace changed unexpectedly")
    if f"{OLD_DOMAIN}.cache_" not in (APP / "client.py").read_text():
        raise RuntimeError("Stored sensor cache namespace changed unexpectedly")

    # Clamp the exposed battery sensor only; keep raw GLOBAL 0x04 unchanged.
    sensor_path = APP / "sensor.py"
    sensor_source = sensor_path.read_text(encoding="utf-8")
    battery_line = 'SensorDescription("battery", "Panel battery", lambda s: s.globals.get(0x04),'
    new_battery_line = (
        'SensorDescription("battery", "Panel battery", '
        'lambda s: min(100, s.globals[0x04]) if 0x04 in s.globals else None,'
    )
    if sensor_source.count(battery_line) != 1:
        raise RuntimeError("Battery sensor definition changed; review clamp")
    sensor_path.write_text(sensor_source.replace(battery_line, new_battery_line), encoding="utf-8")

    # Short Norwegian label for last successful Bluetooth status synchronization.
    nb_path = APP / "translations" / "nb.json"
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    bt_label = nb["entity"]["sensor"]["last_successful_bt_status"]
    bt_label["name"] = "Sist BT-synk"
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Home Assistant 2026.3+ reads custom integration branding from brand/.
    # Preserve the existing Xzense artwork byte-for-byte.
    icon = APP / "icon.png"
    if not icon.is_file():
        raise RuntimeError("Missing existing Xzense icon.png in source ZIP")
    brand = APP / "brand"
    brand.mkdir(exist_ok=True)
    shutil.copy2(icon, brand / "icon.png")

    (ROOT / "hacs.json").write_text(
        json.dumps({"name": "Xzense", "render_readme": True}, indent=2) + "\n"
    )
    assert manifest["domain"] == APP.name
    assert manifest["version"] == VERSION
    assert not old.exists()
    print("Built Xzense 0.5.28.3 as HACS custom_components/xzense")
    print("HACS integration + automatic registry-linked dashboard card ready for testing.")


if __name__ == "__main__":
    build()

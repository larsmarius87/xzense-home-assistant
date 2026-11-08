"""Build Xzense 0.5.28.6 HACS integration from corrected 0.5.27.

Only HACS development branch. No changes to the original ZIP or to main.
"""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "xzense-alpha-0.5.27-source.zip"
NEW_DOMAIN = "xzense"
APP = ROOT / "custom_components" / NEW_DOMAIN
VERSION = "0.5.28.6"


def build():
    if not ARCHIVE.is_file():
        raise RuntimeError("Missing corrected 0.5.27 source ZIP")
    if APP.exists():
        shutil.rmtree(APP)
    APP.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        # Identify the 0.5.27 source folder without retaining its retired
        # integration domain as a constant or in generated code.
        source_domains = {
            name.split("/")[1] for name in z.namelist()
            if name.startswith("custom_components/") and name.count("/") >= 2
        }
        if len(source_domains) != 1:
            raise RuntimeError(f"Expected one source integration, got {source_domains}")
        source_domain = next(iter(source_domains))
        prefix = f"custom_components/{source_domain}/"
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
    if manifest.get("domain") != source_domain:
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
    original_domain_line = f'DOMAIN = "{source_domain}"'
    if original_domain_line not in c:
        raise RuntimeError("Source domain constant changed: stop build")
    c = c.replace(original_domain_line, f'DOMAIN = "{NEW_DOMAIN}"')
    c = c.replace('"0.5.27"', f'"{VERSION}"').replace("'0.5.27'", f"'{VERSION}'")
    const_path.write_text(c)

    init = APP / "__init__.py"
    s = init.read_text()
    old_path = f"/api/{source_domain}/xzense-card.js"
    new_path = f"/api/{NEW_DOMAIN}/xzense-card.js"
    if old_path not in s:
        raise RuntimeError("Source dashboard static path not found")
    s = s.replace(old_path, new_path)
    # Remove the obsolete side-by-side compatibility guard entirely.
    guard_begin = s.find("    # This is a side-by-side development integration.")
    guard_end = s.find("    await client.async_initialize_timing()", guard_begin)
    if guard_begin == -1 or guard_end == -1:
        raise RuntimeError("Legacy integration guard location changed")
    s = s[:guard_begin] + s[guard_end:]
    init.write_text(s.replace("Xzense Alpha", "Xzense"))

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

    # The DSPS service UUID is shared with unrelated BLE products.
    # Only advertisements carrying a recognizable Xzense name may trigger
    # an automatic config flow; preserve the explicit address + PIN flow.
    bluetooth_entries = manifest.get("bluetooth", [])
    if not any(entry.get("local_name") == "Xzense*" for entry in bluetooth_entries):
        raise RuntimeError("Expected named Xzense Bluetooth discovery entry")
    manifest["bluetooth"] = [{"local_name": "Xzense*", "connectable": True}]
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    flow_path = APP / "config_flow.py"
    flow_source = flow_path.read_text(encoding="utf-8")
    old_filter = (
        '    name = (info.name or "").lower()\n'
        '    return "xzense" in name or SERVICE_UUID.lower() in {\n'
        '        uuid.lower() for uuid in info.service_uuids\n'
        '    }'
    )
    new_filter = (
        '    name = (info.name or "").strip().lower()\n'
        '    return name.startswith("xzense")'
    )
    if flow_source.count(old_filter) != 1:
        raise RuntimeError("Expected Xzense discovery filter not found")
    flow_source = flow_source.replace(old_filter, new_filter)
    if "    SERVICE_UUID,\n" not in flow_source:
        raise RuntimeError("Expected legacy shared DSPS import not found")
    flow_source = flow_source.replace("    SERVICE_UUID,\n", "")
    flow_path.write_text(flow_source, encoding="utf-8")

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
        s = p.read_text()
        s = s.replace("Xzense Alpha", "Xzense")
        if source_domain in s and p.name != "client.py":
            raise RuntimeError(f"Legacy domain remains in {p.name}")
        p.write_text(s)
    # The dashboard card is authored separately from the source ZIP, and its
    # registry-based auto-linking must never be lost during rebuilding.
    source_card = ROOT / "tools" / "xzense_card_05281.js"
    if not source_card.is_file():
        raise RuntimeError("Missing dashboard card source")
    js = source_card.read_text(encoding="utf-8")
    for required in ("config/entity_registry/list", "config/device_registry/list",
                     "unique_id.endsWith('_'+key)", "xz-device"):
        if required not in js:
            raise RuntimeError(f"Dashboard auto-link check failed: {required}")
    (APP / "www" / "xzense-card.js").write_text(js, encoding="utf-8")

    # Retire legacy storage namespaces and use only the current integration
    # domain. Previous fire-duration history and cached values are not migrated.
    client_path = APP / "client.py"
    client_source = client_path.read_text()
    for suffix in ("timing_", "cache_"):
        old_namespace = f"{source_domain}.{suffix}"
        if old_namespace not in client_source:
            raise RuntimeError(f"Expected storage key missing: {suffix}")
        client_source = client_source.replace(old_namespace, f"{NEW_DOMAIN}.{suffix}")
    client_path.write_text(client_source)

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
    assert source_domain not in (APP / "__init__.py").read_text()
    assert source_domain not in (APP / "client.py").read_text()
    print("Built Xzense 0.5.28.6 as HACS custom_components/xzense")
    print("HACS integration + automatic registry-linked dashboard card ready for testing.")


if __name__ == "__main__":
    build()

"""Build Xzense 0.5.28 full domain-migration HACS test from corrected 0.5.27.

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
VERSION = "0.5.28"


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
    c = c.replace('"0.5.27"', '"0.5.28"').replace("'0.5.27'", "'0.5.28'")
    const_path.write_text(c)

    init = APP / "__init__.py"
    s = init.read_text()
    # Existing dashboards keep their old resource URL, while new installs use /api/xzense.
    s = s.replace(
        'StaticPathConfig(\n                "/api/xzense_full_preview/xzense-card.js",',
        'StaticPathConfig(\n                "/api/xzense_full_preview/xzense-card.js",'
    )
    init.write_text(s.replace('Xzense Alpha', 'Xzense'))

    card = APP / "www" / "xzense-card.js"
    if card.exists():
        card.write_text(card.read_text().replace(
            "component.xzense_full_preview.entity.", "component.xzense.entity."
        ).replace("Xzense Alpha", "Xzense"))
    for p in APP.rglob("*.py"):
        if p.name not in ("client.py", "__init__.py"):
            s = p.read_text()
            s = s.replace("Xzense Alpha", "Xzense")
            p.write_text(s)
    # Keep OLD_DOMAIN storage namespaces in client.py to preserve saved state and fire durations.
    if f"{OLD_DOMAIN}.timing_" not in (APP / "client.py").read_text():
        raise RuntimeError("Stored timing namespace changed unexpectedly")
    if f"{OLD_DOMAIN}.cache_" not in (APP / "client.py").read_text():
        raise RuntimeError("Stored sensor cache namespace changed unexpectedly")

    (ROOT / "hacs.json").write_text(
        json.dumps({"name": "Xzense", "render_readme": True}, indent=2) + "\n"
    )
    assert manifest["domain"] == APP.name
    assert manifest["version"] == VERSION
    assert not old.exists()
    print("Built Xzense 0.5.28 as HACS custom_components/xzense")
    print("IMPORTANT: Existing HA installations require offline migration before reboot.")


if __name__ == "__main__":
    build()

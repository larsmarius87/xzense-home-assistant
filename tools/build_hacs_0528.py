"""Prepare HACS-compatible Xzense 0.5.28 test tree from the audited 0.5.27 ZIP.

The legacy integration domain stays unchanged on purpose for safe testing.
"""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "xzense-alpha-0.5.27-source.zip"
DOMAIN = "xzense_full_preview"
PREFIX = f"custom_components/{DOMAIN}/"
TARGET = ROOT / "custom_components" / DOMAIN
EXPECTED = {"__init__.py", "manifest.json", "config_flow.py", "const.py"}
VERSION = "0.5.28"


def build() -> None:
    if not ARCHIVE.is_file():
        raise RuntimeError(f"Missing source archive: {ARCHIVE}")
    if TARGET.exists():
        raise RuntimeError(f"Refusing to overwrite existing integration: {TARGET}")
    TARGET.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        names = set(z.namelist())
        members = [name for name in names if name.startswith(PREFIX) and not name.endswith("/")]
        if not members:
            raise RuntimeError(f"No {PREFIX} files found in source package")
        for name in sorted(members):
            relative = Path(name[len(PREFIX):])
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe archive path: {name}")
            dest = TARGET / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(name))
        missing = EXPECTED - {p.name for p in TARGET.iterdir() if p.is_file()}
        if missing:
            raise RuntimeError(f"Missing essential integration files: {sorted(missing)}")

    manifest_path = TARGET / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("domain") != DOMAIN:
        raise RuntimeError(f"Unexpected domain: {manifest.get('domain')!r}")
    manifest["version"] = VERSION
    manifest.setdefault("documentation", "https://github.com/larsmarius87/xzense-home-assistant")
    manifest.setdefault("issue_tracker", "https://github.com/larsmarius87/xzense-home-assistant/issues")
    manifest.setdefault("codeowners", ["@larsmarius87"])
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    const_file = TARGET / "const.py"
    original = const_file.read_text(encoding="utf-8")
    updated = original.replace('"0.5.27"', '"0.5.28"').replace("'0.5.27'", "'0.5.28'")
    if updated != original:
        const_file.write_text(updated, encoding="utf-8")

    (ROOT / "hacs.json").write_text(
        json.dumps({"name": "Xzense (0.5.28 HACS test)", "render_readme": True}, indent=2) + "\n",
        encoding="utf-8",
    )
    for mandatory in ("domain", "documentation", "issue_tracker", "codeowners", "name", "version"):
        if not manifest.get(mandatory):
            raise RuntimeError(f"Missing required manifest key {mandatory}")
    print(f"Built {DOMAIN} version {VERSION}; {len(members)} files")
    print("Manifest:", json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    build()

"""Regress false-positive Bluetooth auto-discovery without importing Home Assistant.

Checks the actual filter function extracted from the built integration.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace

root = Path(__file__).resolve().parents[1]
app = root / "custom_components" / "xzense"
flow = (app / "config_flow.py").read_text()
module = ast.parse(flow)
func = next((n for n in module.body if isinstance(n, ast.FunctionDef)
             and n.name == "_looks_like_xzense"), None)
assert func is not None
filter_module = ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[]))
namespace = {}
exec(compile(filter_module, "<discovery filter>", "exec"), namespace)
matches = namespace["_looks_like_xzense"]
DSPS = "0783b03e-8535-b5a0-7140-a304d2495cb7"

for name in ("Xzense", "Xzense A809", "XZENSE-123", " xzense-controller "):
    assert matches(SimpleNamespace(name=name, service_uuids=[])), name
for name in (None, "", "ESPHome Bluetooth Proxy", "Renesas DSPS",
             "NotXzense", "Other Xzense device", "Nixie Clock"):
    assert not matches(SimpleNamespace(name=name, service_uuids=[DSPS])), name
manifest = json.loads((app / "manifest.json").read_text())
assert manifest["bluetooth"] == [{"local_name": "Xzense*", "connectable": True}]
assert "async_discovered_service_info" in flow
assert "CONF_ADDRESS" in flow and "CONF_PIN" in flow
print("Bluetooth discovery tests passed: Xzense names accepted, unrelated DSPS rejected.")

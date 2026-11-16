"""Regression checks: no duplicate automatic Xzense flows for an installed panel.

Exercise the exact helpers extracted from the generated integration without
importing Home Assistant (CI runner does not install HA).
"""
from __future__ import annotations

import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace

source = (Path(__file__).resolve().parents[1] / "custom_components/xzense/config_flow.py").read_text()
module = ast.parse(source)
helpers = [node for node in module.body if isinstance(node, ast.FunctionDef) and
           node.name in ("_normalized_panel_name", "_matches_configured_panel")]
assert {node.name for node in helpers} == {"_normalized_panel_name", "_matches_configured_panel"}
ns = {"ConfigEntry": object, "CONF_ADDRESS": "address", "CONF_NAME": "name"}
exec(compile(ast.fix_missing_locations(ast.Module(body=helpers, type_ignores=[])),
             "<Xzense discovery helpers>", "exec"), ns)
matches = ns["_matches_configured_panel"]

def entry(name: str, address: str, title: str | None = None):
    return SimpleNamespace(data={"name": name, "address": address}, title=title or name)

saved = [entry("Xzense (A809)", "84:8B:CD:50:36:29", "Min peis")]
assert matches("Xzense (A809)", "AA:11:22:33:44:55", saved)
assert matches("   xZeNsE   (A809)  ", "BB:11:22:33:44:55", saved)
assert matches("Other name", "84:8b:cd:50:36:29", saved)
assert not matches("Xzense (A810)", "CC:11:22:33:44:55", saved)
assert not matches("Xzense (A809)", "AA:11:22:33:44:55", [])
assert not matches(None, "DD:11:22:33:44:55", saved)

flow = next(node for node in module.body if isinstance(node, ast.ClassDef)
            and node.name == "XzenseConfigFlow")
bluetooth = next(node for node in flow.body if isinstance(node, ast.AsyncFunctionDef)
                 and node.name == "async_step_bluetooth")
confirm = next(node for node in flow.body if isinstance(node, ast.AsyncFunctionDef)
               and node.name == "async_step_bluetooth_confirm")
manual = next(node for node in flow.body if isinstance(node, ast.AsyncFunctionDef)
              and node.name == "async_step_user")
bluetooth_code, confirm_code, manual_code = (ast.unparse(x) for x in (bluetooth, confirm, manual))
assert "_matches_configured_panel(" in bluetooth_code
assert 'reason=\'already_configured\'' in bluetooth_code
assert "_matches_configured_panel(" in confirm_code
assert "_matches_configured_panel(" not in manual_code
assert "_abort_if_unique_id_configured()" in manual_code

class FlowAbort(Exception):
    pass

# Execute the actual automatic Bluetooth flow with fake HA plumbing.
scope = {"BluetoothServiceInfoBleak": object, "ConfigFlowResult": object, "DEFAULT_NAME": "Xzense",
         "_looks_like_xzense": lambda info: info.name.lower().startswith("xzense"),
         "_matches_configured_panel": matches,
         "_LOGGER": SimpleNamespace(debug=lambda *args: None)}
exec(compile(ast.fix_missing_locations(ast.Module(body=[bluetooth], type_ignores=[])),
             "<Xzense automatic discovery>", "exec"), scope)
run_discovery = scope["async_step_bluetooth"]

class FakeFlow:
    def __init__(self, entries):
        self.entries = entries
        self.id_set = None
        self._discovery = None
        self.context = {}
    def _async_current_entries(self):
        return self.entries
    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}
    async def async_set_unique_id(self, value):
        self.id_set = value
    def _abort_if_unique_id_configured(self):
        return None
    async def async_step_bluetooth_confirm(self):
        return {"type": "form"}

async def test():
    repeated = FakeFlow(saved)
    result = await run_discovery(repeated, SimpleNamespace(name="Xzense (A809)", address="AA:11:22:33:44:55"))
    assert result == {"type": "abort", "reason": "already_configured"}
    assert repeated.id_set is None
    legitimate = FakeFlow(saved)
    result = await run_discovery(legitimate, SimpleNamespace(name="Xzense (A810)", address="BB:11:22:33:44:55"))
    assert result == {"type": "form"}
    assert legitimate.id_set == "BB:11:22:33:44:55"
    print("Xzense duplicate discovery regression tests passed.")

asyncio.run(test())

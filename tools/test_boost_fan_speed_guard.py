"""Behavioral tests for the generated controller-side fan-speed write interlock."""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace

source=(Path(__file__).resolve().parents[1]/"custom_components/xzense/client.py").read_text()
tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="XzenseClient")
method=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=="_async_check_fan_speed_write_allowed")
class HomeAssistantError(Exception):pass
import time
ns={"HomeAssistantError":HomeAssistantError,"time":time,"asyncio":asyncio,"SNAPSHOT_WAIT_SECONDS":0.10}
exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),"<fan-speed interlock>","exec"),ns)
check=ns[method.name]
async def case(state, response=True, connected=True):
    class Fake:
        def __init__(self):
            self._client=SimpleNamespace(is_connected=connected)
            self.state=SimpleNamespace(session_id=123,status_response_count=4,status=SimpleNamespace(device_state=2))
            self.requests=0
        async def _send_status_request(self, client, session):
            self.requests+=1
            if response:
                self.state.status=SimpleNamespace(device_state=state)
                self.state.status_response_count+=1
    fake=Fake()
    try:
        await check(fake)
        outcome="allowed"
    except HomeAssistantError:
        outcome="blocked"
    return outcome,fake.requests
async def main():
    assert await case(3)==("blocked",1)
    assert await case(4)==("allowed",1)
    assert await case(2)==("allowed",1)
    assert await case(3,response=False)==("blocked",1)
    assert await case(4,connected=False)==("blocked",0)
    # The physical Boost control dispatch is separate from the GLOBAL 0x50 guard.
    control=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=="async_control_feature")
    control_text=ast.unparse(control)
    assert 'feature_key == "boost"' in control_text
    assert 'await self.async_set_boost(bool(value))' in control_text
    writer=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=="async_execute_feature")
    writer_text=ast.unparse(writer)
    assert 'feature_key == "user_fan_speed"' in writer_text
    assert 'await self._async_check_fan_speed_write_allowed()' in writer_text
    print("Boost fan-speed guard tests passed (boost blocked, normal allowed, stale/disconnected blocked, Boost switch independent).")
asyncio.run(main())

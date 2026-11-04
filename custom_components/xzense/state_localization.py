"""Stable state codes for Home Assistant translations, without changing the wire protocol.

The legacy device_state sensor continues to use protocol.device_state_name.
"""

from __future__ import annotations

# Stable language-independent codes for native Home Assistant enum translations.
# Do not replace DEVICE_STATE_NAMES: historical sensor states and automations
# intentionally continue to use the original English protocol labels.
DEVICE_STATE_CODES: dict[int, str] = {
    0: "offline",
    1: "setup",
    2: "ready_for_lighting",
    3: "boosting",
    4: "operation",
    5: "burnout",
    6: "afterrun",
    7: "refueling",
    8: "ventilation",
    9: "error",
    10: "upgrading",
}


def device_state_code(value: int | None) -> str | None:
    """Get a stable enum code without translating the underlying wire state."""
    if value is None:
        return None
    return DEVICE_STATE_CODES.get(value, "unknown_state")


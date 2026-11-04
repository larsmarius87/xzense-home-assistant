"""Xzense 4.10_RC2 GLOBAL scaling and firmware setting bounds.

Ranges come from the firmware's individual GLOBAL setup descriptors. They can
be wider than the limits published in the user manual. Factory references are
informational only: they are never written into the installed controller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Scale = Literal["direct", "tenths", "seconds_to_minutes"]
UnitKind = Literal["percent", "celsius", "minutes", "pascal", "volt", "none"]


@dataclass(frozen=True, slots=True)
class SettingRule:
    minimum: float
    maximum: float
    step: float
    unit: UnitKind
    scale: Scale = "direct"
    factory_default: float | None = None
    reference_note: str = "Firmware 4.10_RC2"


# Extra local safety margin requested by the user. The application firmware
# uses a smaller threshold internally, but 6°C tolerates decimal rounding.
TEMPERATURE_GAP_C = 6.0
RS009_41_MIN_VOLTAGE = 100.0


SETTING_RULES: dict[str, SettingRule] = {
    # Manual: Interface settings 0-100 %.
    "volume_raw": SettingRule(0, 100, 1, "percent", factory_default=100),
    "contrast_raw": SettingRule(0, 100, 1, "percent", factory_default=50),
    "brightness_raw": SettingRule(0, 100, 1, "percent", factory_default=100),
    "auto_start_temperature": SettingRule(5, 205, 0.1, "celsius", "tenths", 40),
    "auto_stop_temperature": SettingRule(0, 200, 0.1, "celsius", "tenths", 35),
    "boost_time": SettingRule(0, 45, 1, "minutes", "seconds_to_minutes", 10),
    "afterrun_time": SettingRule(1, 200, 1, "minutes", "seconds_to_minutes", 30),
    "boost_fan_speed": SettingRule(40, 100, 1, "percent", factory_default=100),
    # 4.10 RC2 Fan Control slider + earlier physical 0x50 write test: direct %.
    "user_fan_speed": SettingRule(10, 100, 1, "percent"),
    "wanted_draft": SettingRule(8, 150, 1, "pascal", factory_default=20),
    "minimum_fan_voltage": SettingRule(80, 120, 1, "volt", factory_default=100,
                                       reference_note="Manual reference: 100 V; RS009-41 requires >=100 V"),
    "boost_stop_temperature": SettingRule(30, 250, 0.1, "celsius", "tenths", 60,
                                          "User-selected reference: 60°C; manual documents 150°C"),
    "alarm_setpoint": SettingRule(150, 500, 0.1, "celsius", "tenths", 250),
    "refire_time": SettingRule(0, 45, 0.1, "minutes", "seconds_to_minutes", 3),
    "burnout_time": SettingRule(1, 200, 0.1, "minutes", "seconds_to_minutes", 5),
}


def effective_bounds(key: str, globals_: dict[int, int], *, rs009_41: bool) -> tuple[float, float]:
    """Return physical firmware limits narrowed by confirmed local constraints."""
    rule = SETTING_RULES[key]
    lower, upper = rule.minimum, rule.maximum
    if key == "minimum_fan_voltage" and rs009_41:
        lower = max(lower, RS009_41_MIN_VOLTAGE)
    if key == "auto_start_temperature" and 0x4C in globals_:
        lower = max(lower, globals_[0x4C] / 10 + TEMPERATURE_GAP_C)
    if key == "auto_stop_temperature" and 0x4B in globals_:
        upper = min(upper, globals_[0x4B] / 10 - TEMPERATURE_GAP_C)
    return (round(lower, 1), round(upper, 1))


def validate_raw_setting(key: str, raw: int, globals_: dict[int, int], *, rs009_41: bool) -> None:
    """Block invalid GLOBAL writes before they can reach the BLE transport."""
    if key not in SETTING_RULES:
        return
    native = raw_to_native(key, raw)
    lower, upper = effective_bounds(key, globals_, rs009_41=rs009_41)
    if key in {"auto_start_temperature", "auto_stop_temperature"}:
        counterpart = 0x4C if key == "auto_start_temperature" else 0x4B
        if counterpart not in globals_:
            raise ValueError("Read both start and stop temperatures before changing either")
    if not lower <= native <= upper:
        raise ValueError(f"{key} must be between {lower} and {upper} (requested {native})")


def raw_to_native(key: str, raw: int) -> float:
    """Convert a signed-int16 GLOBAL value to its HA-facing value."""
    rule = SETTING_RULES.get(key)
    if rule is None or rule.scale == "direct":
        return float(raw)
    if rule.scale == "tenths":
        return raw / 10.0
    if rule.scale == "seconds_to_minutes":
        return raw / 60.0
    raise ValueError(f"Unsupported scale for {key}: {rule.scale}")


def native_to_raw(key: str, value: float) -> int:
    """Convert an HA-facing number back to the signed-int16 GLOBAL value."""
    rule = SETTING_RULES.get(key)
    if rule is not None and not (rule.minimum <= value <= rule.maximum):
        raise ValueError(f"{key} must be between {rule.minimum} and {rule.maximum}")
    if rule is None or rule.scale == "direct":
        return int(round(value))
    if rule.scale == "tenths":
        return int(round(value * 10.0))
    if rule.scale == "seconds_to_minutes":
        return int(round(value * 60.0))
    raise ValueError(f"Unsupported scale for {key}: {rule.scale}")

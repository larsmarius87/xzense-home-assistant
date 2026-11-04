"""Number controls for verified Xzense settings and local test helpers."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import XzenseClient
from .const import DOMAIN
from .entity import XzenseEntity, XzenseFeatureEntity
from .features import FEATURES, FeatureSpec
from .settings import SETTING_RULES, effective_bounds, native_to_raw, raw_to_native, validate_raw_setting

NUMBER_FEATURES = tuple(f for f in FEATURES if f.kind == "number" and f.state == "write_ready")

_UNIT_BY_KIND = {
    "percent": PERCENTAGE,
    "celsius": UnitOfTemperature.CELSIUS,
    "minutes": UnitOfTime.MINUTES,
    "pascal": UnitOfPressure.PA,
    "volt": UnitOfElectricPotential.VOLT,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([*(XzenseNumber(client, feature) for feature in NUMBER_FEATURES),
                        XzenseUpdateInterval(client), XzenseActiveUpdateInterval(client)])


class XzenseNumber(XzenseFeatureEntity, NumberEntity):
    """A numeric Xzense setting backed by a GLOBAL value."""

    _attr_mode = NumberMode.BOX

    def __init__(self, client: XzenseClient, feature: FeatureSpec) -> None:
        super().__init__(client, feature)
        if feature.key != "user_fan_speed":
            self._attr_entity_category = EntityCategory.CONFIG
        rule = SETTING_RULES.get(feature.key)
        if rule is None:
            raise ValueError(f"Missing verified setting rule for {feature.key}")

        self._attr_native_min_value = rule.minimum
        self._attr_native_max_value = rule.maximum
        self._attr_native_step = rule.step
        unit = _UNIT_BY_KIND.get(rule.unit)
        if unit is not None:
            self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        if self.feature.global_id is None:
            return None
        raw = self.client.state.globals.get(self.feature.global_id)
        return None if raw is None else raw_to_native(self.feature.key, raw)

    @property
    def native_min_value(self) -> float:
        return effective_bounds(self.feature.key, self.client.state.globals,
                                rs009_41=self.client.rs009_41_motor)[0]

    @property
    def native_max_value(self) -> float:
        return effective_bounds(self.feature.key, self.client.state.globals,
                                rs009_41=self.client.rs009_41_motor)[1]

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        attrs = super().extra_state_attributes
        rule = SETTING_RULES[self.feature.key]
        attrs.update({"factory_reference": rule.factory_default,
                      "factory_reference_note": rule.reference_note,
                      "firmware_range": f"{rule.minimum}–{rule.maximum}"})
        if self.feature.key == "minimum_fan_voltage":
            attrs["rs009_41_motor"] = self.client.rs009_41_motor
            attrs["under_motor_minimum"] = bool(self.client.rs009_41_motor
                and self.native_value is not None and self.native_value < 100)
        if self.feature.key in {"auto_start_temperature", "auto_stop_temperature"}:
            attrs["minimum_temperature_separation_c"] = 6
        return attrs

    async def async_set_native_value(self, value: float) -> None:
        raw = native_to_raw(self.feature.key, value)
        validate_raw_setting(self.feature.key, raw, self.client.state.globals,
                             rs009_41=self.client.rs009_41_motor)
        await self.client.async_control_feature(self.feature.key, raw)


class XzenseUpdateInterval(XzenseEntity, NumberEntity):
    """Idle/Ready refresh interval: 0 continuous, 1–120 min periodic."""

    _attr_translation_key = "bluetooth_update_interval"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 120
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:bluetooth-connect"

    def __init__(self, client: XzenseClient) -> None:
        super().__init__(client)
        self._attr_unique_id = f"{client.address}_bluetooth_update_interval"

    @property
    def native_value(self) -> float:
        return float(self.client.idle_interval_minutes)

    async def async_set_native_value(self, value: float) -> None:
        await self.client.async_set_interval(int(value), active=False)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"profile": "Ready", "bluetooth_connection_mode": "continuous" if self.client.idle_interval_minutes == 0 else "periodic"}


class XzenseActiveUpdateInterval(XzenseEntity, NumberEntity):
    """Active states (incl. ventilation): 0 continuous, 1–600 seconds periodic."""

    _attr_translation_key = "bluetooth_active_update_interval"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:bluetooth-connect"

    def __init__(self, client: XzenseClient) -> None:
        super().__init__(client)
        self._attr_unique_id = f"{client.address}_bluetooth_active_update_interval"

    @property
    def native_value(self) -> float:
        return float(self.client.active_interval_seconds)

    async def async_set_native_value(self, value: float) -> None:
        await self.client.async_set_interval(int(value), active=True)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"profile": "Boosting / Operation / Afterrun / Ventilation",
                "bluetooth_connection_mode": "continuous" if self.client.active_interval_seconds == 0 else "periodic"}

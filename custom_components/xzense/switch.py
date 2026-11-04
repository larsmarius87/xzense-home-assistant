"""Switches for app-visible Xzense controls."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import XzenseClient
from .const import DOMAIN
from .entity import XzenseEntity, XzenseFeatureEntity
from .features import FEATURES, FeatureSpec

SWITCH_FEATURES = tuple(f for f in FEATURES if f.kind == "switch" and f.state == "write_ready")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([*(XzenseSwitch(client, feature) for feature in SWITCH_FEATURES),
                        XzenseRS00941Switch(client)])


class XzenseRS00941Switch(XzenseEntity, SwitchEntity):
    """Persist the installed motor type as a local, non-BLE configuration."""

    _attr_translation_key = "rs009_41_motor"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:engine-outline"

    def __init__(self, client: XzenseClient) -> None:
        super().__init__(client)
        self._attr_unique_id = f"{client.address}_rs009_41_motor"

    @property
    def is_on(self) -> bool:
        return self.client.rs009_41_motor

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        current = self.client.state.globals.get(0x54)
        return {"minimum_voltage_when_enabled": 100,
                "minimum_voltage_when_disabled": 80,
                "maximum_voltage": 120,
                "current_voltage": current,
                "voltage_below_rs009_41_limit": bool(
                    self.is_on and current is not None and current < 100),
                "scope": "Home Assistant UI and write validation only; no automatic BLE write"}

    async def async_turn_on(self, **kwargs) -> None:
        await self.client.async_set_rs009_41_motor(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.client.async_set_rs009_41_motor(False)


class XzenseSwitch(XzenseFeatureEntity, SwitchEntity, RestoreEntity):
    """Xzense controls with status-derived, restorable state."""

    def __init__(self, client: XzenseClient, feature: FeatureSpec) -> None:
        super().__init__(client, feature)
        self._attr_icon = {
            "boost": "mdi:turbine",
            "ventilation": "mdi:fan",
            "temperature_sensor": "mdi:thermometer",
        }.get(feature.key, "mdi:toggle-switch")
        if feature.key == "temperature_sensor":
            from homeassistant.const import EntityCategory
            self._attr_entity_category = EntityCategory.CONFIG

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Restore prior value on HA restart only if live STATUS has not arrived.
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state in (STATE_ON, STATE_OFF):
            value = last_state.state == STATE_ON
            if self.feature.key == "boost" and self.client.state.boost_is_on is None:
                self.client.state.boost_is_on = value
            elif self.feature.key == "ventilation" and self.client.state.ventilation_is_on is None:
                self.client.state.ventilation_is_on = value
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        if self.feature.key == "boost":
            return self.client.controls_available and (
                self.client.interval_minutes > 0 or self.client.boost_available()
            )
        if self.feature.key == "ventilation":
            return self.client.controls_available and (
                self.client.interval_minutes > 0 or self.client.ventilation_available()
            )
        return super().available

    @property
    def is_on(self) -> bool | None:
        if self.feature.key == "boost":
            return self.client.state.boost_is_on
        if self.feature.key == "ventilation":
            return self.client.state.ventilation_is_on
        if self.feature.key == "temperature_sensor":
            raw = self.client.state.globals.get(0x56)
            return bool(raw) if raw in (0, 1) else None
        if self.feature.global_id is not None:
            value = self.client.state.globals.get(self.feature.global_id)
            return None if value is None else bool(value)
        return None

    async def async_turn_on(self, **kwargs) -> None:
        await self.client.async_control_feature(
            self.feature.key, 1 if self.feature.key == "temperature_sensor" else True
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.client.async_control_feature(
            self.feature.key, 0 if self.feature.key == "temperature_sensor" else False
        )

"""Buttons for app-visible Xzense actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import XzenseClient
from .const import DOMAIN
from .entity import XzenseFeatureEntity
from .features import FEATURES, FeatureSpec

BUTTON_FEATURES = tuple(f for f in FEATURES if f.kind == "button" and f.state == "write_ready")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(XzenseButton(client, feature) for feature in BUTTON_FEATURES)


class XzenseButton(XzenseFeatureEntity, ButtonEntity):
    """An Xzense action button."""

    def __init__(self, client: XzenseClient, feature: FeatureSpec) -> None:
        super().__init__(client, feature)
        self._attr_icon = {
            "start_fire": "mdi:fire",
            "stop_fire": "mdi:fire-off",
            "refuel": "mdi:forest",
        }.get(feature.key, "mdi:gesture-tap-button")

    @property
    def available(self) -> bool:
        state = self.client.current_device_state()
        if self.feature.key == "start_fire":
            return self.client.controls_available and state in {2, 6}
        if self.feature.key == "refuel":
            return self.client.controls_available and state == 5
        if self.feature.key == "stop_fire":
            if state in {3, 7}:
                return self.client.controls_available
            return super().available and state in {4, 5}
        return super().available

    async def async_press(self) -> None:
        await self.client.async_control_feature(self.feature.key)

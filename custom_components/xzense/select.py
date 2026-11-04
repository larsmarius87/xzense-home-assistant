"""Select controls for Xzense operating modes/settings."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import XzenseClient
from .const import DOMAIN
from .entity import XzenseFeatureEntity
from .features import FEATURES, FeatureSpec
from .protocol import SYSTEM_CONTROL_NAME_TO_VALUE, SYSTEM_CONTROL_VALUE_TO_NAME

SELECT_FEATURES = tuple(f for f in FEATURES if f.kind == "select" and f.state == "write_ready")

OPTIONS = {
    "system_control": ["Manual", "eXotelligence"],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(XzenseSelect(client, feature) for feature in SELECT_FEATURES)


class XzenseSelect(XzenseFeatureEntity, SelectEntity):
    """A scaffolded Xzense select."""

    def __init__(self, client: XzenseClient, feature: FeatureSpec) -> None:
        super().__init__(client, feature)
        self._attr_options = OPTIONS[feature.key]
        if feature.key == "system_control":
            self._attr_entity_category = EntityCategory.CONFIG

    @property
    def current_option(self) -> str | None:
        if self.feature.key == "system_control" and self.feature.global_id is not None:
            raw = self.client.state.globals.get(self.feature.global_id)
            current = SYSTEM_CONTROL_VALUE_TO_NAME.get(raw) if raw is not None else None
            return current if current in self.options else None
        return None

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            return
        if self.feature.key == "system_control":
            await self.client.async_control_feature(
                self.feature.key, SYSTEM_CONTROL_NAME_TO_VALUE[option]
            )
            return
        await self.client.async_control_feature(self.feature.key, option)

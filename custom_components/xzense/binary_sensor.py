"""Binary sensors for Xzense."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import XzenseClient
from .const import DOMAIN
from .entity import XzenseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            XzenseApplicationConnectionBinarySensor(client),
            XzenseBleConnectionBinarySensor(client),
        ]
    )


class XzenseApplicationConnectionBinarySensor(XzenseEntity, BinarySensorEntity):
    """Authenticated Xzense application-session status."""

    _attr_translation_key = "connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, client: XzenseClient) -> None:
        super().__init__(client)
        self._attr_unique_id = f"{client.address}_connection"

    @property
    def is_on(self) -> bool:
        return (
            self.client.state.connected
            and self.client.state.notifications_active
            and self.client.state.application_auth_state == "connected"
        )


class XzenseBleConnectionBinarySensor(XzenseEntity, BinarySensorEntity):
    """Low-level BLE link status."""

    _attr_translation_key = "ble_connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, client: XzenseClient) -> None:
        super().__init__(client)
        self._attr_unique_id = f"{client.address}_ble_connection"

    @property
    def is_on(self) -> bool:
        return self.client.state.ble_link_connected


"""Shared entity bases for Xzense Alpha."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import Entity

from .client import XzenseClient
from .const import CONTROL_WRITES_ENABLED, DOMAIN
from .features import FeatureSpec


class XzenseEntity(Entity):
    """Base entity backed by a XzenseClient."""

    _attr_has_entity_name = True

    def __init__(self, client: XzenseClient) -> None:
        self.client = client
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, client.address)},
            name=client.name,
            manufacturer="Exodraft",
            model="Xzense",
            connections={(CONNECTION_BLUETOOTH, client.address)},
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.client.async_add_listener(self.async_write_ha_state))


class XzenseFeatureEntity(XzenseEntity):
    """Base for identified Xzense settings and actions."""

    def __init__(self, client: XzenseClient, feature: FeatureSpec) -> None:
        super().__init__(client)
        self.feature = feature
        self._attr_translation_key = feature.key
        self._attr_unique_id = f"{client.address}_{feature.key}"

    @property
    def available(self) -> bool:
        return (
            CONTROL_WRITES_ENABLED
            and self.feature.state == "write_ready"
            and self.client.controls_available
        )

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        attrs: dict[str, object] = {
            "protocol_readiness": self.feature.state,
            "control_writes_enabled": CONTROL_WRITES_ENABLED,
        }
        if self.feature.global_id is not None:
            attrs["global_id"] = f"0x{self.feature.global_id:02X}"
        if self.feature.packet_type is not None:
            attrs["packet_type"] = f"0x{self.feature.packet_type:02X}"
        if self.feature.notes:
            attrs["notes"] = self.feature.notes
        return attrs

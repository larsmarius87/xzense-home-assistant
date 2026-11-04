"""Sensors for Exodraft Xzense."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfPressure, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .client import STATUS_POLL_INTERVAL, XzenseClient, XzenseState
from .const import DOMAIN
from .features import FEATURES
from .protocol import GLOBAL_NAMES, device_state_name
from .state_localization import DEVICE_STATE_CODES, device_state_code
from .entity import XzenseEntity
from .version import format_firmware_version


def _status_or_global(state: XzenseState, attr: str, global_id: int) -> int | None:
    """Prefer a verified STATUS value, falling back to passive GLOBAL/DATA."""
    if state.status is not None:
        value = getattr(state.status, attr, None)
        if value is not None:
            return value
    return state.globals.get(global_id)


def _temperature_status_or_global(
    state: XzenseState, raw_attr: str, global_id: int
) -> float | None:
    """Return a calibrated temperature in degrees Celsius."""
    if state.status is not None:
        raw = getattr(state.status, raw_attr, None)
        if raw is not None:
            return raw / 10.0
    raw = state.globals.get(global_id)
    return None if raw is None else raw / 10.0


def _operating_state(state: XzenseState) -> str | None:
    raw = _status_or_global(state, "device_state", 0x19)
    return device_state_name(raw)


def _operating_state_localized_code(state: XzenseState) -> str | None:
    """Return an enum code; Home Assistant localizes its presentation."""
    raw = _status_or_global(state, "device_state", 0x19)
    return device_state_code(raw)


def _local_status_time(state: XzenseState) -> str | None:
    """Last *successful STATUS/ACK* as ordinary Oslo wall-clock text."""
    if not state.last_status_response_at:
        return None
    try:
        stamp = datetime.fromisoformat(state.last_status_response_at.replace("Z", "+00:00"))
        return stamp.astimezone(ZoneInfo("Europe/Oslo")).strftime("%d.%m.%Y kl. %H:%M:%S")
    except ValueError:
        return None


def _global_dump(state: XzenseState) -> str | None:
    """Keep the sensor state short; full values live in attributes/diagnostics."""
    if not state.globals:
        return None
    return f"{len(state.globals)} GLOBAL-felt"


# All firmware/protocol-discovered GLOBAL IDs not used by other entities are
# available in one live diagnostic summary. Keep XTP-only fields in the full
# download, but do not create XTP entities for a system without the sensor.
_ACTIVE_GLOBAL_IDS = frozenset(
    feature.global_id for feature in FEATURES if feature.global_id is not None
)
_UNUSED_GLOBAL_IDS = frozenset(GLOBAL_NAMES) - _ACTIVE_GLOBAL_IDS - {0x20, 0x51}


def _unused_global_values(state: XzenseState) -> dict[str, int]:
    return {f"0x{key:02X} ({GLOBAL_NAMES.get(key, 'UNMAPPED')})": value
            for key, value in sorted(state.globals.items())
            if key not in _ACTIVE_GLOBAL_IDS and key not in {0x20, 0x51}}


def _unused_global_count(state: XzenseState) -> str:
    return f"{len(_unused_global_values(state))} GLOBAL-felt"


@dataclass(frozen=True, slots=True)
class SensorDescription:
    key: str
    name: str
    value_fn: Callable[[XzenseState], Any]
    diagnostic: bool = True
    native_unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    enabled_default: bool = True
    options: tuple[str, ...] | None = None


# Live mappings calibrated against synchronized panel readings on 2026-10-19.
# Temperature globals are tenths of a degree Celsius. Fan speed is direct %.
LIVE_SENSORS = (
    SensorDescription(
        "chimney_temperature",
        "Chimney temperature",
        lambda s: _temperature_status_or_global(s, "chimney_temperature_raw", 0x1E),
        diagnostic=False,
        native_unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        "inside_temperature",
        "Inside temperature",
        lambda s: _temperature_status_or_global(s, "inside_temperature_raw", 0x1C),
        diagnostic=False,
        native_unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        "outside_temperature",
        "Outside temperature",
        lambda s: _temperature_status_or_global(s, "outside_temperature_raw", 0x1D),
        diagnostic=False,
        native_unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        "fan_speed",
        "Actual fan speed",
        lambda s: _status_or_global(s, "fan_speed", 0x1F),
        diagnostic=False,
        native_unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

# Additional app/firmware-visible reads. IDs are recovered, but scaling/semantics
# beyond their names are deliberately left raw until verified on the wire.
APP_READ_SENSORS = (
    SensorDescription(
        "pressure",
        "Air pressure",
        lambda s: _status_or_global(s, "air_pressure_hpa", 0x1B),
        diagnostic=False,
        native_unit=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        "state_timer",
        "Time in current state",
        lambda s: s.state_timer_display,
        diagnostic=False,
    ),
    SensorDescription(
        "fire_duration",
        "Fire duration",
        lambda s: s.fire_duration_display,
        diagnostic=False,
    ),
    SensorDescription("device_state", "Device state (English)", _operating_state),
    # Keep the existing unique ID for the Norwegian normal-state sensor.
    SensorDescription(
        "device_state_localized", "Localized device state", _operating_state_localized_code,
        diagnostic=False,
        device_class=SensorDeviceClass.ENUM,
        options=tuple(DEVICE_STATE_CODES.values()) + ("unknown_state",),
    ),
    SensorDescription("signal_strength", "Radio link signal strength", lambda s: s.globals.get(0x05), diagnostic=False),
    SensorDescription("battery", "Panel battery", lambda s: s.globals.get(0x04),
                      diagnostic=False, native_unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT),
    SensorDescription("last_successful_bt_status", "Last successful Bluetooth update", _local_status_time,
                      diagnostic=False),
    SensorDescription(
        "firmware_version",
        "Firmware version",
        lambda s: format_firmware_version(s.connect_ack_version),
        diagnostic=False,
    ),
)

# Unresolved values remain accessible in the full diagnostics GLOBAL snapshot.
# Do not expose a redundant actual-draught or burnout-time raw entity.
RAW_UNKNOWN_SENSORS = (
    SensorDescription("raw_global_18", "GLOBAL 0x18 MY_STATE (raw)", lambda s: s.globals.get(0x18), enabled_default=False),
    SensorDescription("raw_global_36", "GLOBAL 0x36 (raw)", lambda s: s.globals.get(0x36), enabled_default=False),
) + tuple(
    SensorDescription(f"raw_global_{global_id:02x}",
                      f"GLOBAL 0x{global_id:02X} ({GLOBAL_NAMES[global_id]})",
                      lambda state, gid=global_id: state.globals.get(gid),
                      enabled_default=False)
    for global_id in sorted(_UNUSED_GLOBAL_IDS - {0x18, 0x35, 0x36, 0x50, 0x55, 0x5B})
)

# Keep the fields the bundled dashboard and everyday troubleshooting require.
# All other descriptions remain registered with their original unique IDs, but
# disabled at the HA entity-registry level. Full raw diagnostics are unchanged.
CORE_DIAGNOSTIC_KEYS = frozenset({
    "last_data_at", "next_poll_at", "phase", "ble_link_connected",
    "last_advertisement_rssi", "selected_source", "last_error",
    "crc_errors", "status_nack_count", "source_fallbacks",
    "fast_connect_attempts", "fast_connect_fallbacks",
    "status_device_state",
    "unused_global_values",
})

_ALL_DIAGNOSTIC_SENSORS = (
    SensorDescription("unused_global_values", "Unused GLOBAL register values", _unused_global_count),
    SensorDescription("last_data_at", "Sist oppdatert (Bluetooth)", lambda s: s.last_data_at),
    SensorDescription("next_poll_at", "Next Bluetooth update", lambda s: s.next_poll_at),
    SensorDescription("phase", "Bluetooth setup phase", lambda s: s.phase),
    SensorDescription("ble_link_connected", "BLE link connected", lambda s: s.ble_link_connected),
    SensorDescription("notifications_active", "BLE notifications active", lambda s: s.notifications_active),
    SensorDescription("packet_count", "Valid protocol frames", lambda s: s.packet_count),
    SensorDescription("last_payload", "Last protocol payload", lambda s: s.last_frame.payload_hex if s.last_frame else None),
    SensorDescription("last_frame", "Last protocol frame", lambda s: s.last_frame.hex if s.last_frame else None),
    SensorDescription("last_notification", "Last BLE notification", lambda s: s.last_notification.hex() if s.last_notification else None),
    SensorDescription("last_notification_at", "Last BLE notification time", lambda s: s.last_notification_at),
    SensorDescription("notification_count", "BLE notifications", lambda s: s.notification_count),
    SensorDescription("discarded_bytes", "Discarded protocol bytes", lambda s: s.discarded_bytes),
    SensorDescription("invalid_frames", "Invalid protocol frames", lambda s: s.invalid_frames),
    SensorDescription("crc_errors", "Protocol CRC errors", lambda s: s.crc_errors),
    SensorDescription("connection_attempts", "Bluetooth connection attempts", lambda s: s.connection_attempts),
    SensorDescription("disconnect_count", "Bluetooth disconnects", lambda s: s.disconnect_count),
    SensorDescription("advertisement_count", "Fresh BLE advertisements", lambda s: s.advertisement_count),
    SensorDescription("advertisement_waits", "Advertisement waits", lambda s: s.advertisement_waits),
    SensorDescription("advertisement_timeouts", "Advertisement wait timeouts", lambda s: s.advertisement_timeouts),
    SensorDescription("last_advertisement_at", "Last fresh advertisement time", lambda s: s.last_advertisement_at),
    SensorDescription("last_advertisement_rssi", "Last advertisement RSSI", lambda s: s.last_advertisement_rssi),
    SensorDescription("last_advertisement_source", "Last advertisement adapter", lambda s: s.last_advertisement_source),
    SensorDescription("last_advertisement_name", "Last advertisement name", lambda s: s.last_advertisement_name),
    SensorDescription("last_advertisement_connectable", "Last advertisement connectable", lambda s: s.last_advertisement_connectable),
    SensorDescription("candidate_source_count", "Bluetooth candidate sources", lambda s: s.candidate_source_count),
    SensorDescription("candidate_sources", "Bluetooth source candidates", lambda s: s.candidate_sources or None),
    SensorDescription("selected_source", "Selected Bluetooth source", lambda s: s.selected_source),
    SensorDescription("selected_source_rssi", "Selected Bluetooth source RSSI", lambda s: s.selected_source_rssi),
    SensorDescription("source_connection_attempts", "Bluetooth source connection attempts", lambda s: s.source_connection_attempts),
    SensorDescription("source_fallbacks", "Bluetooth source fallbacks", lambda s: s.source_fallbacks),
    SensorDescription("last_failed_source", "Last failed Bluetooth source", lambda s: s.last_failed_source),
    SensorDescription("active_session_source", "Active Bluetooth proxy", lambda s: s.active_session_source),
    SensorDescription("preferred_source", "Preferred Bluetooth proxy", lambda s: s.preferred_source),
    SensorDescription("last_disconnect_source", "Last disconnected proxy", lambda s: s.last_disconnect_source),
    SensorDescription("last_disconnect_kind", "Last BLE disconnect classification", lambda s: s.last_disconnect_kind),
    SensorDescription("last_disconnect_session_seconds", "Last BLE session duration", lambda s: s.last_disconnect_session_seconds),
    SensorDescription("pairing_attempts", "Bluetooth pairing attempts", lambda s: s.pairing_attempts),
    SensorDescription("pairing_success", "Bluetooth pairing succeeded", lambda s: s.pairing_success),
    SensorDescription("pairing_last_error", "Last Bluetooth pairing error", lambda s: s.pairing_last_error),
    SensorDescription("authorization_retries", "GATT authorization retries", lambda s: s.authorization_retries),
    SensorDescription("tx_count", "Application TX frames", lambda s: s.tx_count),
    SensorDescription("tx_chunk_count", "Application TX chunks", lambda s: s.tx_chunk_count),
    SensorDescription("last_tx", "Last application TX", lambda s: "<redacted CONNECT/REQ>" if s.last_tx_kind == "CONNECT/REQ" else (s.last_tx.hex() if s.last_tx else None)),
    SensorDescription("last_tx_kind", "Last application TX type", lambda s: s.last_tx_kind),
    SensorDescription("last_tx_at", "Last application TX time", lambda s: s.last_tx_at),
    SensorDescription("tx_write_mode", "Application TX write mode", lambda s: s.tx_write_mode),
    SensorDescription("tx_chunk_size", "Application TX chunk size", lambda s: s.tx_chunk_size),
    SensorDescription("application_auth_state", "Application authentication state", lambda s: s.application_auth_state),
    SensorDescription("application_connect_attempts", "Application CONNECT attempts", lambda s: s.application_connect_attempts),
    SensorDescription("application_auth_success_count", "Application authentication successes", lambda s: s.application_auth_success_count),
    SensorDescription("handshake_sent_at", "Application handshake sent time", lambda s: s.handshake_sent_at),
    SensorDescription("handshake_response_at", "Application handshake response time", lambda s: s.handshake_response_at),
    SensorDescription("handshake_last_error", "Application handshake error", lambda s: s.handshake_last_error),
    SensorDescription("session_id", "Application session ID", lambda s: f"0x{s.session_id:08X}" if s.session_id is not None else None),
    SensorDescription("connect_ack_version", "CONNECT ACK version", lambda s: s.connect_ack_version),
    SensorDescription("connect_ack_flag", "CONNECT ACK flag", lambda s: s.connect_ack_flag),
    SensorDescription("status_polling_active", "Status polling active", lambda s: s.status_polling_active),
    SensorDescription("status_request_count", "Status requests", lambda s: s.status_request_count),
    SensorDescription("status_response_count", "Status responses", lambda s: s.status_response_count),
    SensorDescription("status_nack_count", "Status NACKs", lambda s: s.status_nack_count),
    SensorDescription("status_request_errors", "Status request errors", lambda s: s.status_request_errors),
    SensorDescription("last_status_request_at", "Last status request time", lambda s: s.last_status_request_at),
    SensorDescription("last_status_response_at", "Last status response time", lambda s: s.last_status_response_at),
    SensorDescription("last_status_payload", "Last status payload", lambda s: s.last_status_payload.hex() if s.last_status_payload else None),
    SensorDescription("status_device_state", "Status device state", lambda s: s.status.device_state if s.status else None),
    SensorDescription("status_state_timer", "Status time in current state", lambda s: s.status.state_timer if s.status else None),
    SensorDescription("status_fan_speed", "Status fan speed", lambda s: s.status.fan_speed if s.status else None),
    SensorDescription("status_chimney_temperature_raw", "Status chimney temperature raw", lambda s: s.status.chimney_temperature_raw if s.status else None),
    SensorDescription("status_outside_temperature_raw", "Status outside temperature raw", lambda s: s.status.outside_temperature_raw if s.status else None),
    SensorDescription("status_inside_temperature_raw", "Status inside temperature raw", lambda s: s.status.inside_temperature_raw if s.status else None),
    SensorDescription("global_0x20_raw", "GLOBAL 0x20 raw", lambda s: s.globals.get(0x20)),
    SensorDescription("status_air_pressure_hpa", "Status air pressure", lambda s: s.status.air_pressure_hpa if s.status else None),
    SensorDescription("global_write_request_count", "GLOBAL write requests", lambda s: s.global_write_request_count),
    SensorDescription("global_write_ack_count", "GLOBAL write ACKs", lambda s: s.global_write_ack_count),
    SensorDescription("global_write_nack_count", "GLOBAL write NACKs", lambda s: s.global_write_nack_count),
    SensorDescription("last_global_write_id", "Last GLOBAL write ID", lambda s: f"0x{s.last_global_write_id:02X}" if s.last_global_write_id is not None else None),
    SensorDescription("last_global_write_value", "Last GLOBAL write value", lambda s: s.last_global_write_value),
    SensorDescription("last_global_write_request_at", "Last GLOBAL write request time", lambda s: s.last_global_write_request_at),
    SensorDescription("last_global_write_response", "Last GLOBAL write response", lambda s: s.last_global_write_response),
    SensorDescription("last_global_write_response_at", "Last GLOBAL write response time", lambda s: s.last_global_write_response_at),
    SensorDescription("boost_request_count", "Boost requests", lambda s: s.boost_request_count),
    SensorDescription("boost_ack_count", "Boost ACKs", lambda s: s.boost_ack_count),
    SensorDescription("boost_nack_count", "Boost NACKs", lambda s: s.boost_nack_count),
    SensorDescription("last_boost_action", "Last Boost action", lambda s: s.last_boost_action),
    SensorDescription("last_boost_request_at", "Last Boost request time", lambda s: s.last_boost_request_at),
    SensorDescription("last_boost_response", "Last Boost response", lambda s: s.last_boost_response),
    SensorDescription("last_boost_response_at", "Last Boost response time", lambda s: s.last_boost_response_at),
    SensorDescription("global_update_count", "Global updates", lambda s: s.global_update_count),
    SensorDescription("last_global_id", "Last global ID", lambda s: f"0x{s.last_global_id:02X}" if s.last_global_id is not None else None),
    SensorDescription("last_global_name", "Last global name", lambda s: s.last_global_name),
    SensorDescription("last_global_value", "Last global value", lambda s: s.last_global_value),
    SensorDescription("last_global_at", "Last global update time", lambda s: s.last_global_at),
    SensorDescription("global_values", "Global values", _global_dump),
    SensorDescription("last_packet_type", "Last application packet type", lambda s: s.last_frame.packet_type_name if s.last_frame else None),
    SensorDescription("last_protocol_type", "Last application protocol type", lambda s: s.last_frame.protocol_type_name if s.last_frame else None),
    SensorDescription("last_error", "Last Bluetooth error", lambda s: s.last_error),
)

DIAGNOSTIC_SENSORS = tuple(
    replace(description, enabled_default=description.key in CORE_DIAGNOSTIC_KEYS)
    for description in _ALL_DIAGNOSTIC_SENSORS
)

# 0x59 and 0x5B are now editable configuration numbers; their original raw
# values remain in the protocol GLOBAL diagnostics snapshot.
SENSORS = LIVE_SENSORS + APP_READ_SENSORS + RAW_UNKNOWN_SENSORS + DIAGNOSTIC_SENSORS

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(XzenseSensor(client, description) for description in SENSORS)


class XzenseSensor(XzenseEntity, SensorEntity):
    """A live or diagnostic Xzense value."""

    def __init__(self, client: XzenseClient, description: SensorDescription) -> None:
        super().__init__(client)
        self.description = description
        self._attr_translation_key = description.key
        self._attr_unique_id = f"{client.address}_{description.key}"
        self._attr_entity_registry_enabled_default = description.enabled_default
        if description.diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if description.native_unit is not None:
            self._attr_native_unit_of_measurement = description.native_unit
        if description.device_class is not None:
            self._attr_device_class = description.device_class
        if description.state_class is not None:
            self._attr_state_class = description.state_class
        if description.options is not None:
            self._attr_options = list(description.options)
        if description.key == "fan_speed":
            self._attr_icon = "mdi:fan"
        elif description.key == "signal_strength":
            self._attr_icon = "mdi:signal-cellular-outline"

    @property
    def icon(self) -> str | None:
        """Show the verified 0–3 radio-link bars, with a safe default."""
        if self.description.key == "signal_strength":
            raw = self.native_value
            if isinstance(raw, int) and 1 <= raw <= 3:
                return f"mdi:signal-cellular-{raw}"
            return "mdi:signal-cellular-outline"
        return getattr(self, "_attr_icon", None)

    @property
    def native_value(self) -> Any:
        value = self.description.value_fn(self.client.state)
        # HA rejects sensor states longer than 255 characters. Preserve the
        # unabridged value below in attributes and diagnostic downloads.
        if isinstance(value, str) and len(value) > 255:
            return value[:252] + "..."
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.description.key == "unused_global_values":
            return {"registers": _unused_global_values(self.client.state),
                    "known_registers": [f"0x{key:02X}" for key in sorted(_UNUSED_GLOBAL_IDS)],
                    "scope": "read-only; excludes XTP-only 0x20 and 0x51"}
        if self.description.key == "last_successful_bt_status":
            return {"timestamp_iso": self.client.state.last_status_response_at,
                    "time_zone": "Europe/Oslo",
                    "source": "successful STATUS/ACK (not BLE advertisement)"}
        if self.description.key == "signal_strength":
            return {"global_id": "0x05", "value_range_inferred": "0–3",
                    "link": "control panel to power unit; not HA Bluetooth RSSI"}
        if self.description.key == "battery":
            return {"global_id": "0x04", "calibration": "inferred from panel battery icon",
                    "last_data_at": self.client.state.last_data_at}
        if not self.description.diagnostic and self.description.key not in {"state_timer", "fire_duration"}:
            return {
                "last_data_at": self.client.state.last_data_at,
                "stale": not self.client._fresh_status_event.is_set(),
            }
        if self.description.key == "state_timer":
            state = self.client.state
            return {
                "raw_unsigned_seconds": state.state_timer_unsigned_raw,
                "elapsed_seconds": state.state_timer_elapsed_seconds,
                "rollovers": state.state_timer_rollovers,
                "continuity": state.state_timer_continuity,
                "observed_at": state.state_timer_observed_at,
                "stale": not self.client._fresh_status_event.is_set(),
            }
        if self.description.key == "fire_duration":
            state = self.client.state
            return {
                "elapsed_seconds": state.fire_duration_seconds,
                "started_at": state.fire_started_at,
                "quality": state.fire_quality,
                "last_fire_duration_seconds": state.last_fire_duration_seconds,
                "last_fire_quality": state.last_fire_quality,
                "stale": not self.client._fresh_status_event.is_set(),
            }
        if self.description.key == "global_values":
            return {"values": {f"0x{k:02X}": v for k, v in sorted(self.client.state.globals.items())}}
        value = self.description.value_fn(self.client.state)
        if isinstance(value, str) and len(value) > 255:
            return {"full_value": value}
        return None

    @property
    def available(self) -> bool:
        if self.description.diagnostic:
            return True
        return self.native_value is not None

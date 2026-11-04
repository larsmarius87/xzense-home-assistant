"""Exodraft Xzense Home Assistant integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import entity_registry as er

from .burnout_notifications import BurnoutNotificationManager
from .client import XzenseClient
from .const import CONF_NAME, CONF_PIN, DEFAULT_NAME, DOMAIN
from .sensor import DIAGNOSTIC_SENSORS, CORE_DIAGNOSTIC_KEYS

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xzense from a config entry."""
    if not entry.data.get(CONF_PIN):
        raise ConfigEntryAuthFailed("Xzense PIN is required")

    hass.data.setdefault(DOMAIN, {})

    # The Lovelace card is bundled with the integration and served from
    # a stable static URL. Users only need to register this JS module once
    # in Settings > Dashboards > Resources (no copy into /config/www).
    if not hass.data[DOMAIN].get("_frontend_registered"):
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                "/api/xzense_full_preview/xzense-card.js",
                str(Path(__file__).parent / "www" / "xzense-card.js"),
                False,
            )
        ])
        hass.data[DOMAIN]["_frontend_registered"] = True

    client = XzenseClient(
        hass,
        entry,
        entry.data[CONF_ADDRESS],
        entry.data.get(CONF_NAME, entry.title or DEFAULT_NAME),
        entry.data[CONF_PIN],
    )
    hass.data[DOMAIN][entry.entry_id] = client

    registry = er.async_get(hass)
    # Remove obsolete entities and former non-functional scaffolds from the
    # entity registry. Verified controls, their unique IDs and diagnostic raw
    # data are deliberately preserved.
    obsolete_suffixes = (
        "chimney_state", "weather_station", "firmware",
        "language_raw", "download_log",
        "burn_count", "operation_time", "error_log",
        "external_start",
        "external_fan_speed", "raw_global_51", "actual_draft", "raw_global_5b",
        "ble_release_seconds", "release_ble_to_app",
        "boost_on", "boost_off", "start_afterrun",
        # 0.5.25 final: retired diagnostic/test entities only.
        "raw_global_35", "raw_global_50", "raw_global_55",
        "global_0x35_raw", "global_0x50_raw", "global_0x55_raw",
        "experimental_write_probes", "fan_probe_baseline_raw",
        "fan_probe_observed_fan_speed", "fan_probe_restored_fan_speed",
        "fan_probe_target_raw", "last_write_probe",
        "last_write_probe_result", "status_auxiliary_raw",
        "status_flag", "status_flags", "status_polling_interval",
        "status_state_selector",
    )
    obsolete_unique_ids = {
        f"{entry.data[CONF_ADDRESS]}_{suffix}" for suffix in obsolete_suffixes
    }
    # 0x59/0x5B were read-only sensors in the pre-release 0.5.12 build.
    # When upgraded to configuration numbers, remove any old sensor entities.
    promoted_time_unique_ids = {
        f"{entry.data[CONF_ADDRESS]}_{key}" for key in ("refire_time", "burnout_time")
    }
    reduced_diagnostics = {
        f"{entry.data[CONF_ADDRESS]}_{description.key}"
        for description in DIAGNOSTIC_SENSORS
        if description.key not in CORE_DIAGNOSTIC_KEYS
    }
    for entity_entry in list(er.async_entries_for_config_entry(registry, entry.entry_id)):
        if (entity_entry.domain == "select" and
                entity_entry.unique_id == f"{entry.data[CONF_ADDRESS]}_temperature_sensor"):
            registry.async_remove(entity_entry.entity_id)
            continue
        if (
            entity_entry.domain == "sensor"
            and entity_entry.unique_id in promoted_time_unique_ids
        ):
            registry.async_remove(entity_entry.entity_id)
            continue
        if entity_entry.unique_id in obsolete_unique_ids or (
            entity_entry.domain == "button"
            and entity_entry.unique_id == f"{entry.data[CONF_ADDRESS]}_boost"
        ):
            registry.async_remove(entity_entry.entity_id)
            continue
        if entity_entry.domain == "sensor" and entity_entry.unique_id in reduced_diagnostics:
            # Existing 0.5.19.3 installations already registered all sensors.
            # Disable unneeded diagnostic state writers, not their registry IDs.
            if entity_entry.disabled_by is None:
                registry.async_update_entity(
                    entity_entry.entity_id, disabled_by=er.RegistryEntryDisabler.INTEGRATION
                )
        elif entity_entry.disabled_by == er.RegistryEntryDisabler.INTEGRATION:
            # Retain old upgrade behavior for controls/core diagnostics. The
            # 0.5.19.3 rollback re-enables all integration-disabled entities.
            registry.async_update_entity(entity_entry.entity_id, disabled_by=None)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # This is a side-by-side development integration. Avoid two clients fighting
    # for the same Xzense BLE peripheral.
    if hass.data.get("xzense") or hass.data.get("xzense_preview"):
        client.state.phase = "blocked_by_other_xzense_integration"
        client.state.last_error = (
            "Another Xzense integration is loaded. Disable/unload it, then reload "
            "Xzense; only one client may own the BLE session."
        )
        client._notify_listeners()
        return True

    await client.async_initialize_timing()
    await client.async_initialize_cache()
    notifier = BurnoutNotificationManager(hass, entry)
    remove_observer = client.async_add_status_listener(notifier.observe)
    hass.data[DOMAIN][f"_burnout_notifier_{entry.entry_id}"] = (notifier, remove_observer)
    await client.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Xzense."""
    client: XzenseClient = hass.data[DOMAIN][entry.entry_id]
    manager = hass.data[DOMAIN].pop(f"_burnout_notifier_{entry.entry_id}", None)
    if manager:
        notifier, remove_observer = manager
        remove_observer()
        notifier.stop()
    await client.async_stop()

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded

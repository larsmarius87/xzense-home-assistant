"""Optional mobile notification on an observed Xzense Operation -> Burnout edge.

Only fresh, decoded STATUS frames may call observe(). Cached/restored values must
never be used to synthesize a transition on Home Assistant startup.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er

from .const import CONF_BURNOUT_NOTIFY_ENABLED, CONF_BURNOUT_NOTIFY_TARGET

_LOGGER = logging.getLogger(__name__)

NOTIFY_TITLE = "Xzense: Legg i mer ved"
NOTIFY_MESSAGE = "Legg i mer ved."
NO_NOTIFY_TARGET = "none"


def mobile_notification_targets(hass: HomeAssistant) -> dict[str, str]:
    """Return selectable Companion phones, both notify entities and legacy actions.

    Entity registry platform filtering prevents accidental sends to arbitrary
    notify services. Never fall back to notify.notify (could target everyone).
    """
    choices: dict[str, str] = {NO_NOTIFY_TARGET: "Ingen telefon"}
    registry = er.async_get(hass)
    for entity in registry.entities.values():
        if entity.domain != "notify" or entity.platform != "mobile_app" or entity.disabled_by is not None:
            continue
        name = entity.name or entity.original_name or entity.entity_id
        choices[f"entity:{entity.entity_id}"] = f"{name} ({entity.entity_id})"

    for service in hass.services.async_services().get("notify", {}):
        if service.startswith("mobile_app_"):
            choices[f"service:{service}"] = f"{service.removeprefix('mobile_app_').replace('_', ' ')} (mobilapp-tjeneste)"
    return choices


class BurnoutNotificationManager:
    """One notification per fresh observed 4 -> 5 edge, off by default."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._last_fresh_state: int | None = None
        self._closed = False

    def stop(self) -> None:
        """Detach on entry unload; in-flight HA tasks finish independently."""
        self._closed = True

    def observe(self, state: int) -> None:
        """Called synchronously for valid live STATUS only, never cache restores."""
        if self._closed:
            return
        previous = self._last_fresh_state
        self._last_fresh_state = state
        if previous != 4 or state != 5:
            return

        # Read options at every transition: changing settings needs no BLE reload.
        opts = self.entry.options
        if not opts.get(CONF_BURNOUT_NOTIFY_ENABLED, False):
            return
        stored = opts.get(CONF_BURNOUT_NOTIFY_TARGET, [])
        if isinstance(stored, str):
            targets = [stored]
        elif isinstance(stored, list):
            targets = stored
        else:
            targets = []
        valid = list(dict.fromkeys(
            target for target in targets
            if isinstance(target, str) and (
                target.startswith("entity:notify.")
                or target.startswith("service:mobile_app_")
            )
        ))
        if not valid:
            _LOGGER.warning("Xzense burnout notification enabled but no valid phone is selected")
            return
        for target in valid:
            self.entry.async_create_background_task(
                self.hass,
                self._async_send(target),
                f"xzense-burnout-notification-{self.entry.entry_id}",
            )

    async def _async_send(self, target: str) -> None:
        """Send outside the Bluetooth receive callback; never block STATUS parsing."""
        try:
            if target.startswith("entity:"):
                entity_id = target.removeprefix("entity:")
                if self.hass.states.get(entity_id) is None:
                    _LOGGER.warning("Xzense notification phone %s is not available", entity_id)
                    return
                await self.hass.services.async_call(
                    "notify", "send_message",
                    {"title": NOTIFY_TITLE, "message": NOTIFY_MESSAGE},
                    target={"entity_id": entity_id},
                    blocking=True,
                )
            else:
                service = target.removeprefix("service:")
                if not self.hass.services.has_service("notify", service):
                    _LOGGER.warning("Xzense notification action notify.%s was not found", service)
                    return
                await self.hass.services.async_call(
                    "notify", service,
                    {"title": NOTIFY_TITLE, "message": NOTIFY_MESSAGE},
                    blocking=True,
                )
            _LOGGER.info("Xzense burnout notification sent to %s", target)
        except Exception:
            # Notification failures must never interrupt the BLE receive path.
            _LOGGER.warning("Failed to send Xzense burnout notification to %s", target, exc_info=True)

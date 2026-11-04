"""Config flow for Xzense Alpha."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback
from homeassistant.helpers import selector

from .burnout_notifications import NO_NOTIFY_TARGET, mobile_notification_targets

from .const import (
    CONF_NAME,
    CONF_PIN,
    CONF_BURNOUT_NOTIFY_ENABLED,
    CONF_BURNOUT_NOTIFY_TARGET,
    DEFAULT_NAME,
    DOMAIN,
    SERVICE_UUID,
    normalize_pin,
)


def _looks_like_xzense(info: BluetoothServiceInfoBleak) -> bool:
    name = (info.name or "").lower()
    return "xzense" in name or SERVICE_UUID.lower() in {
        uuid.lower() for uuid in info.service_uuids
    }


class XzenseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle Xzense Alpha setup."""

    VERSION = 2

    def __init__(self) -> None:
        self._discovery: BluetoothServiceInfoBleak | None = None
        self._discovered: dict[str, BluetoothServiceInfoBleak] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> XzenseOptionsFlow:
        """Offer an optional phone notification on Operation -> Burnout."""
        return XzenseOptionsFlow()

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle automatic Bluetooth discovery."""
        if not _looks_like_xzense(discovery_info):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery = discovery_info
        self.context["title_placeholders"] = {
            "name": discovery_info.name or DEFAULT_NAME
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a discovered Xzense device and collect its PIN."""
        if self._discovery is None:
            return self.async_abort(reason="no_devices_found")

        errors: dict[str, str] = {}
        if user_input is not None:
            pin = normalize_pin(user_input[CONF_PIN])
            if pin is None:
                errors[CONF_PIN] = "invalid_pin"
            else:
                return self.async_create_entry(
                    title=self._discovery.name or DEFAULT_NAME,
                    data={
                        CONF_ADDRESS: self._discovery.address,
                        CONF_NAME: self._discovery.name or DEFAULT_NAME,
                        CONF_PIN: pin,
                    },
                )

        schema = vol.Schema({vol.Required(CONF_PIN): str})
        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user choose a discovered Xzense or enter an address manually."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip()
            pin = normalize_pin(user_input[CONF_PIN])
            if pin is None:
                errors[CONF_PIN] = "invalid_pin"
            else:
                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                info = self._discovered.get(address)
                title = (info.name if info else None) or DEFAULT_NAME
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ADDRESS: address,
                        CONF_NAME: title,
                        CONF_PIN: pin,
                    },
                )

        self._discovered = {
            info.address: info
            for info in async_discovered_service_info(self.hass, connectable=True)
            if _looks_like_xzense(info)
        }

        if self._discovered:
            labels = {
                address: f"{(info.name or DEFAULT_NAME)} ({address})"
                for address, info in self._discovered.items()
            }
            schema = vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(labels),
                    vol.Required(CONF_PIN): str,
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                    vol.Required(CONF_PIN): str,
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Ask for the PIN when upgrading an entry created by v0.1.x."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Store a new PIN for an existing Xzense config entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            pin = normalize_pin(user_input[CONF_PIN])
            if pin is None:
                errors[CONF_PIN] = "invalid_pin"
            else:
                entry = self._get_reauth_entry()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_PIN: pin},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PIN): str}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow the Xzense PIN to be changed later."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            pin = normalize_pin(user_input[CONF_PIN])
            if pin is None:
                errors[CONF_PIN] = "invalid_pin"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_PIN: pin},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_PIN): str}
            ),
            errors=errors,
        )


class XzenseOptionsFlow(OptionsFlow):
    """Select multiple mobile phones for burnout notifications."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure multiple Companion notify entities or mobile_app services."""
        current = self.config_entry.options
        choices = mobile_notification_targets(self.hass)
        choices.pop(NO_NOTIFY_TARGET, None)
        stored = current.get(CONF_BURNOUT_NOTIFY_TARGET, [])
        if isinstance(stored, str):
            selected = [] if stored in ("", NO_NOTIFY_TARGET) else [stored]
        elif isinstance(stored, list):
            selected = [value for value in stored if isinstance(value, str) and value != NO_NOTIFY_TARGET]
        else:
            selected = []
        for value in selected:
            if value not in choices:
                choices[value] = f"Tidligere valgt telefon ({value})"

        errors: dict[str, str] = {}
        if user_input is not None:
            enabled = bool(user_input.get(CONF_BURNOUT_NOTIFY_ENABLED, False))
            targets = user_input.get(CONF_BURNOUT_NOTIFY_TARGET, [])
            if not isinstance(targets, list) or any(
                not isinstance(target, str) or target not in choices for target in targets
            ):
                errors["base"] = "invalid_target"
            elif enabled and not targets:
                errors["base"] = "target_required"
            else:
                return self.async_create_entry(
                    data={**current,
                          CONF_BURNOUT_NOTIFY_ENABLED: enabled,
                          CONF_BURNOUT_NOTIFY_TARGET: list(dict.fromkeys(targets))}
                )

        schema = vol.Schema({
            vol.Required(
                CONF_BURNOUT_NOTIFY_ENABLED,
                default=current.get(CONF_BURNOUT_NOTIFY_ENABLED, False)
            ): bool,
            vol.Required(
                CONF_BURNOUT_NOTIFY_TARGET,
                default=selected,
            ): selector.SelectSelector(selector.SelectSelectorConfig(
                options=[selector.SelectOptionDict(value=value, label=label)
                         for value, label in choices.items()],
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )),
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)

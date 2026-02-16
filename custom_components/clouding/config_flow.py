"""Config flow for the .io integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_UPDATE_INTERVAL, DOMAIN, MIN_TIME_BETWEEN_UPDATES
from .pythonclouding import (
    Clouding,
    CloudingAuthenticationError,
    CloudingError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.helpers.service_info.hassio import HassioServiceInfo

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Clouding.io"): str,
        vol.Required(CONF_API_KEY, default=""): str,
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY, default=""): str,
    },
)


async def validate_connection(hass: HomeAssistant, api_key: str | None) -> dict[str, str]:
    """Validate Clouding.io connectivity."""

    errors: dict[str, str] = {}
    session = async_get_clientsession(hass)
    clouding = Clouding(session, api_key)

    try:
        await clouding.get_servers()
    except CloudingAuthenticationError:
        errors["base"] = "invalid_auth"
    except CloudingError:
        errors["base"] = "cannot_connect"
    except Exception:  # pylint: disable=broad-exception-caught
        _LOGGER.exception("Unexpected exception")
        errors["base"] = "unknown"
    return errors


class CloudingConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Clouding.io."""

    _hassio_discovery: HassioServiceInfo | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match({"name": user_input[CONF_NAME]})

            if not (
                errors := await validate_connection(
                    self.hass,
                    user_input[CONF_API_KEY],
                )
            ):
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={**user_input},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=STEP_USER_DATA_SCHEMA, suggested_values=user_input
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:  # pylint: disable=unused-argument
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Confirm reauthentication dialog."""
        errors: dict[str, str] = {}

        entry = self._get_reauth_entry()

        if user_input is not None and not (
            errors := await validate_connection(
                self.hass,
                user_input[CONF_API_KEY],
            )
        ):
            return self.async_update_reload_and_abort(
                entry,
                data_updates=user_input,
            )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=STEP_REAUTH_DATA_SCHEMA, suggested_values="user_input"
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reconfigure flow."""
        errors: dict[str, str] = {}

        entry = self._get_reconfigure_entry()

        if user_input is not None:
            self._async_abort_entries_match({"name": user_input[CONF_API_KEY]})

            if not (
                errors := await validate_connection(
                    self.hass,
                    user_input[CONF_API_KEY],
                )
            ):
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={**user_input},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=STEP_REAUTH_DATA_SCHEMA,
                suggested_values=user_input,
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowHandler:  # noqa: ARG004 # pylint: disable=unused-argument
        """Get the options flow for this handler."""
        return OptionsFlowHandler()


async def _async_validate_input(
    hass: HomeAssistant,  # noqa: ARG001 # pylint: disable=unused-argument
    user_input: dict[str, Any],
) -> Any:
    if user_input[CONF_UPDATE_INTERVAL] == 1:
        return {CONF_UPDATE_INTERVAL: "invalid_update_interval"}

    return {}


def _get_data_option_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_UPDATE_INTERVAL,
            ): vol.All(
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=15,
                        max=3600,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Coerce(int),
            )
        }
    )


class OptionsFlowHandler(OptionsFlow):
    """Options flow used to change configuration (options) of existing instance of integration."""

    async def async_step_init(self, user_input=None) -> ConfigFlowResult:  # pylint: disable=unused-argument  # noqa: ANN001
        """..."""
        if user_input is not None:  # we asked to validate values entered by user
            errors = await _async_validate_input(self.hass, user_input)

            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={**self.config_entry.data, **user_input}
                )
                return self.async_create_entry(title="", data={})
            return self.async_show_form(
                step_id="init",
                data_schema=self.add_suggested_values_to_schema(
                    _get_data_option_schema(),
                    user_input,
                ),
                errors=dict(errors),
            )

        update_interval = self.config_entry.data.get(CONF_UPDATE_INTERVAL, None)

        if update_interval is None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    CONF_UPDATE_INTERVAL: MIN_TIME_BETWEEN_UPDATES.seconds,
                },
            )

        # we asked to provide default values for the form
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                _get_data_option_schema(),
                self.config_entry.data,
            ),
        )

"""Service platform for the Clouding.io integration."""

from __future__ import annotations

import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr

from custom_components.clouding.pythonclouding import (
    CloudingBadRequestException,
)

from .const import DOMAIN
from .coordinator import (
    CloudingDataUpdateCoordinator,
)

_LOGGER = logging.getLogger(__name__)


async def _async_service(service_call: ServiceCall, data: Any, action: str) -> None:
    """..."""

    device_id = service_call.data[CONF_DEVICE_ID]

    # Get the device based on the given device ID.
    device = dr.async_get(service_call.hass).devices.get(device_id)

    if device is None:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="invalid_device_id")

    clouding_current_config_entry: ConfigEntry | None = None

    for config_entry_id in device.config_entries:
        config_entry = service_call.hass.config_entries.async_get_entry(config_entry_id)
        if not config_entry or config_entry.domain != DOMAIN:
            # Not the blue_current config entry.
            continue

        if config_entry.state is not ConfigEntryState.LOADED:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="config_entry_not_loaded")

        clouding_current_config_entry = config_entry
        break

    if not clouding_current_config_entry:
        # The device is not connected to a valid blue_current config entry.
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_config_entry")

    coordinator: CloudingDataUpdateCoordinator = clouding_current_config_entry.runtime_data

    # response = await coordinator.api.get_servers()
    _LOGGER.error(
        f"Action '{action}' forn '{device.name}' from '{clouding_current_config_entry.title}' will be performed."
    )

    mapping: Dict[str, str] = {
        "archive_server": "archive",
        "unarchive_server": "unarchive",
        "start_server": "start",
        "stop_server": "stop",
        "reboot_server": "reboot",
        "hard_reboot_server": "hard-reboot",
    }

    try:
        await coordinator.api.call_action_server(mapping[action], device.serial_number)
    except CloudingBadRequestException as _:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="action_cannot_be_performed",
            translation_placeholders={"action_name": mapping[action]},
        )

    await coordinator.async_update_data()
    await coordinator._async_refresh()


async def async_archive_server(service_call: ServiceCall, data: Any) -> None:
    """..."""
    await _async_service(service_call, data, "archive_server")


async def async_unarchive_server(service_call: ServiceCall, data: Any) -> None:
    """..."""
    await _async_service(service_call, data, "unarchive_server")


async def async_hard_reboot_server(service_call: ServiceCall, data: Any) -> None:
    """..."""
    await _async_service(service_call, data, "hard_reboot_server")


async def async_reboot_server(service_call: ServiceCall, data: Any) -> None:
    """..."""
    await _async_service(service_call, data, "reboot_server")


async def async_start_server(service_call: ServiceCall, data: Any) -> None:
    """..."""
    await _async_service(service_call, data, "start_server")


async def async_stop_server(service_call: ServiceCall, data: Any) -> None:
    """..."""
    await _async_service(service_call, data, "stop_server")

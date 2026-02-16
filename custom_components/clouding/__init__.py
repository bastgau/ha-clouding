"""The Clouding.io integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from homeassistant.const import Platform

from .const import (
    CONF_UPDATE_INTERVAL,
    DOMAIN,
    MIN_TIME_BETWEEN_UPDATES,
    SERVICE_ARCHIVE_SERVER,
    SERVICE_HARD_REBOOT_SERVER,
    SERVICE_REBOOT_SERVER,
    SERVICE_START_SERVER,
    SERVICE_STOP_SERVER,
    SERVICE_UNARCHIVE_SERVER,
)
from .coordinator import (
    CloudingConfigEntry,
    CloudingDataUpdateCoordinator,
)
from .helpers import purge_entities
from .services import (
    async_archive_server,
    async_hard_reboot_server,
    async_reboot_server,
    async_start_server,
    async_stop_server,
    async_unarchive_server,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

_SERVICE_MAP = {
    SERVICE_ARCHIVE_SERVER: async_archive_server,
    SERVICE_UNARCHIVE_SERVER: async_unarchive_server,
    SERVICE_HARD_REBOOT_SERVER: async_hard_reboot_server,
    SERVICE_REBOOT_SERVER: async_reboot_server,
    SERVICE_START_SERVER: async_start_server,
    SERVICE_STOP_SERVER: async_stop_server,
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: CloudingConfigEntry) -> bool:
    """Set up Clouding.io from a config entry."""

    conf_update_interval: int | None = config_entry.data.get(CONF_UPDATE_INTERVAL)

    if conf_update_interval is None:
        update_interval = MIN_TIME_BETWEEN_UPDATES
    else:
        update_interval = timedelta(seconds=conf_update_interval)

    coordinator = CloudingDataUpdateCoordinator(
        hass,
        config_entry=config_entry,
        update_interval=update_interval,
    )

    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Register services to hass
    async def execute_service(call: ServiceCall) -> None:
        """Execute a service to Clouding.io."""

        function_call = _SERVICE_MAP[call.service]
        await function_call(call, call.data)

    for service in _SERVICE_MAP:
        hass.services.async_register(DOMAIN, service, execute_service)

    purge_entities(config_entry, hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: CloudingConfigEntry) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

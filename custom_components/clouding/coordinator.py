"""Coordinator for the Clouding.io integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .pythonclouding import (
    Clouding,
    CloudingAuthenticationError,
    CloudingError,
    CloudingServer,
)

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

type CloudingConfigEntry = ConfigEntry[CloudingDataUpdateCoordinator]


class CloudingDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Update coordinator for Clouding."""

    config_entry: CloudingConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: CloudingConfigEntry, update_interval: timedelta) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance.
            config_entry: The config entry associated with this coordinator.
            update_interval: The interval in seconds between data updates.

        """

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=update_interval,
        )
        session = async_get_clientsession(hass)
        self.api = Clouding(session, config_entry.data[CONF_API_KEY])

    async def async_update_data(self) -> dict[str, CloudingServer]:
        """Fetch the latest data from Clouding.io.

        Returns:
            A dictionary mapping server IDs to their CloudingServer instances.

        Raises:
            ConfigEntryAuthFailed: If the API key is invalid or authentication fails.
            UpdateFailed: If the API request fails for any other reason.

        """
        return await self._async_update_data()

    async def _async_update_data(self) -> dict[str, CloudingServer]:
        """Fetch the latest data from Clouding.io.

        Returns:
            A dictionary mapping server IDs to their CloudingServer instances.

        Raises:
            ConfigEntryAuthFailed: If the API key is invalid or authentication fails.
            UpdateFailed: If the API request fails for any other reason.

        """

        try:
            servers: dict[str, CloudingServer] = await self.api.get_servers()
        except CloudingAuthenticationError as e:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="auth_failed_exception",
            ) from e
        except CloudingError as e:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="request_failed_exception",
            ) from e

        return servers

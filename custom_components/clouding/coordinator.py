"""Coordinator for the Clouding.io integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.clouding.pythonclouding import (
    Clouding,
    CloudingAuthenticationException,
    CloudingException,
    CloudingServer,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL_UPDATES = timedelta(hours=3)

type CloudingConfigEntry = ConfigEntry[CloudingDataUpdateCoordinator]


class CloudingDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Update coordinator for Clouding."""

    config_entry: CloudingConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: CloudingConfigEntry, update_interval: int) -> None:
        """Initialize the coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=update_interval,
        )
        session = async_get_clientsession(hass)
        self.api = Clouding(session, config_entry.data[CONF_API_KEY])

    async def async_update_data(self) -> Dict[str, CloudingServer]:
        """..."""
        self._async_update_data()

    async def _async_update_data(self) -> Dict[str, CloudingServer]:
        """Fetch the latest data from Clouding.io"""

        try:
            servers: Dict[str, CloudingServer] = await self.api.get_servers()
        except CloudingAuthenticationException as e:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="auth_failed_exception",
            ) from e
        except CloudingException as e:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="request_failed_exception",
            ) from e

        return servers

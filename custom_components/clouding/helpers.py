"""Helpers for the Clouding.io integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceRegistry

    from .coordinator import CloudingConfigEntry


def purge_entities(config_entry: CloudingConfigEntry, hass: HomeAssistant) -> None:
    """Remove devices from the registry that no longer exist in Clouding.io.

    Compares the list of servers currently returned by the coordinator against
    all devices registered under this config entry. Any device whose server ID
    is no longer present in the coordinator data is removed from the device registry.

    Args:
        config_entry (CloudingConfigEntry): The active Clouding.io config entry.
        hass (HomeAssistant): The Home Assistant instance.

    Returns:
        None.

    """

    existing_servers: list[str] = [server_id.upper() for server_id in config_entry.runtime_data.data]
    entities_to_remove: list[str] = []

    config_entry_id: str = config_entry.runtime_data.config_entry.entry_id
    device_registry: DeviceRegistry = dr.async_get(hass)

    for device_attributes in device_registry.devices.data.values():
        try:
            current_domain: str = next(iter(device_attributes.identifiers))[0]

            if current_domain != DOMAIN:
                continue

            current_entry_id: str = next(iter(device_attributes.config_entries))
            current_server_id: str = next(iter(device_attributes.identifiers))[1].rsplit("_", 1)[1]

        except IndexError:
            continue

        if current_entry_id == config_entry_id and current_server_id.upper() not in existing_servers:
            entities_to_remove.append(device_attributes.id)

    for entity_id in entities_to_remove:
        device_registry.async_remove_device(entity_id)

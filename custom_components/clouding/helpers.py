"""Helpers for the Clouding.io integration."""

from __future__ import annotations


from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import CloudingConfigEntry


def purge_entities(config_entry: CloudingConfigEntry, hass: HomeAssistant) -> None:
    """..."""

    existing_servers: list[str] = [server_id.upper() for server_id in config_entry.runtime_data.data.keys()]
    entities_to_remove: list[str] = []

    config_entry_id: str = config_entry.runtime_data.config_entry.entry_id
    device_registry = dr.async_get(hass)

    for device_attributes in dr.async_get(hass).devices.data.values():
        try:
            current_domain: str = list(device_attributes.identifiers)[0][0]

            if current_domain != DOMAIN:
                continue

            current_entry_id = list(device_attributes.config_entries)[0]
            current_server_id = list(device_attributes.identifiers)[0][1].rsplit("_", 1)[1]

        except IndexError as _:
            continue

        entities_to_remove.append(
            device_attributes.id
        ) if current_entry_id == config_entry_id and current_server_id.upper() not in existing_servers else None

    [device_registry.async_remove_device(id) for id in entities_to_remove]

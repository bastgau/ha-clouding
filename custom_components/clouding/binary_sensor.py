"""Binary sensor platform for the Clouding.io integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util, slugify

from .const import ATTRIBUTION
from .coordinator import CloudingConfigEntry, CloudingDataUpdateCoordinator
from .device_info import CloudingDeviceInfo

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
    from pythonclouding import CloudingServer

PARALLEL_UPDATES = 0


class EnumCloudingBinarySensor(StrEnum):
    """Clouding sensors."""

    SERVER_RUNNING = "is_running"


@dataclass(frozen=True, kw_only=True)
class CloudingBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe Clouding.io sensor entity."""

    name_suffix: str


BINARY_SENSOR_ATTRIBUTES: tuple[CloudingBinarySensorEntityDescription, ...] = (
    CloudingBinarySensorEntityDescription(
        key=EnumCloudingBinarySensor.SERVER_RUNNING,
        translation_key=EnumCloudingBinarySensor.SERVER_RUNNING,
        name_suffix="Power State",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
)


class CloudingBinarySensor(CoordinatorEntity[CloudingDataUpdateCoordinator], BinarySensorEntity):  # pylint: disable=too-many-instance-attributes
    """A Clouding.io binary sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CloudingDataUpdateCoordinator,
        server_id: str,
        description: CloudingBinarySensorEntityDescription,
        device_name: str,
    ) -> None:
        """Initialize Clouding.io binary sensors."""

        super().__init__(coordinator)

        server: CloudingServer = coordinator.api.servers[server_id]

        part_entity_id: str = slugify(f"{device_name} {server.attr_id} {description.name_suffix}")
        self.entity_id = f"{BINARY_SENSOR_DOMAIN}.{part_entity_id}"
        self.entity_description = description

        self._device_name = device_name

        self._model_name = server.attr_image.attr_name
        self._server_name = server.attr_name
        self._server_unique_id = server.attr_id

        self._attr_unique_id = slugify(f"{device_name} {server.attr_id} {description.key}")

        self._attr_device_info = CloudingDeviceInfo(
            device_name,
            self._model_name,
            self._server_name,
            self._server_unique_id,
        ).device_info

        self._attr_extra_state_attributes = {}

        self._update_attr()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""

        self._update_attr()
        super()._handle_coordinator_update()

    @property
    def is_on(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return if the service is on."""

        return getattr(self.coordinator.api.servers[self._server_unique_id], "attr_" + self.entity_description.key)

    @callback
    def _update_attr(self) -> None:
        """Update attributes for binary sensor."""

        try:
            if self.entity_description.key == EnumCloudingBinarySensor.SERVER_RUNNING:
                self._attr_extra_state_attributes = {
                    "Value": self.coordinator.api.servers[self._server_unique_id].attr_power_state,
                    "Last Refresh": dt_util.utcnow(),
                }

            self._attr_native_value = getattr(
                self.coordinator.api.servers[self._server_unique_id], "attr_" + self.entity_description.key
            )

        except KeyError:
            self._attr_native_value = None


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 # pylint: disable=unused-argument
    config_entry: CloudingConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize a Clouding.io binary sensor."""

    coordinator = config_entry.runtime_data
    device_name = config_entry.data[CONF_NAME]

    entities = [
        CloudingBinarySensor(coordinator, server, description, device_name)
        for server in coordinator.api.servers
        for description in BINARY_SENSOR_ATTRIBUTES
    ]

    async_add_entities(entities)

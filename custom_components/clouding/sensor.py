"""Sensor platform for the Clouding.io integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import CONF_NAME, UnitOfInformation
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION
from .coordinator import CloudingConfigEntry, CloudingDataUpdateCoordinator
from .device_info import CloudingDeviceInfo

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
    from pythonclouding import CloudingServer

PARALLEL_UPDATES = 0


class EnumCloudingSensor(StrEnum):
    """Clouding.io sensors."""

    SERVER_FLAVOR = "flavor"
    SERVER_HOSTNAME = "hostname"
    SERVER_PRIVATE_ID = "private_ip"
    SERVER_RAM_GB = "ram_gb"
    SERVER_CREATED_AT = "created_at"
    SERVER_DNS_ADDRESS = "dns_address"
    SERVER_NAME = "name"
    SERVER_POWER_STATE = "power_state"
    SERVER_PUBLIC_IP = "public_ip"
    SERVER_STATUS = "status"
    SERVER_VCORES = "vcores"
    SERVER_VOLUME_SIZE_GB = "volume_size_gb"


@dataclass(frozen=True, kw_only=True)
class CloudingSensorEntityDescription(SensorEntityDescription):
    """Describe Clouding.io sensor entity.

    Attributes:
        name_suffix: The suffix appended to the device name to build the entity name.

    """

    name_suffix: str


SENSOR_ATTRIBUTES: tuple[CloudingSensorEntityDescription, ...] = (
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_FLAVOR, translation_key=EnumCloudingSensor.SERVER_FLAVOR, name_suffix="Flavor"
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_HOSTNAME,
        translation_key=EnumCloudingSensor.SERVER_HOSTNAME,
        name_suffix="Hostname",
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_RAM_GB,
        translation_key=EnumCloudingSensor.SERVER_RAM_GB,
        name_suffix="RAM Gb",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_display_precision=0,
        device_class=SensorDeviceClass.DATA_SIZE,
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_CREATED_AT,
        translation_key=EnumCloudingSensor.SERVER_CREATED_AT,
        name_suffix="Created At",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_DNS_ADDRESS,
        translation_key=EnumCloudingSensor.SERVER_DNS_ADDRESS,
        name_suffix="DNS Address",
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_NAME,
        translation_key=EnumCloudingSensor.SERVER_NAME,
        name_suffix="Name",
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_PUBLIC_IP,
        translation_key=EnumCloudingSensor.SERVER_PUBLIC_IP,
        name_suffix="Public IP",
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_STATUS,
        translation_key=EnumCloudingSensor.SERVER_STATUS,
        name_suffix="Status",
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_VCORES,
        translation_key=EnumCloudingSensor.SERVER_VCORES,
        name_suffix="VCores",
    ),
    CloudingSensorEntityDescription(
        key=EnumCloudingSensor.SERVER_VOLUME_SIZE_GB,
        translation_key=EnumCloudingSensor.SERVER_VOLUME_SIZE_GB,
        name_suffix="Volume Size GB",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
        suggested_display_precision=0,
        device_class=SensorDeviceClass.DATA_SIZE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 # pylint: disable=unused-argument
    config_entry: CloudingConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize a Clouding sensor.

    Args:
        hass: The Home Assistant instance (unused).
        config_entry: The Clouding.io config entry.
        async_add_entities: Callback to register new entities.

    Returns:
        None.

    """

    coordinator = config_entry.runtime_data
    device_name = config_entry.data[CONF_NAME]

    entities = [
        CloudingSensor(coordinator, server, description, device_name)
        for server in coordinator.api.servers
        for description in SENSOR_ATTRIBUTES
    ]

    async_add_entities(entities)


class CloudingSensor(CoordinatorEntity[CloudingDataUpdateCoordinator], SensorEntity, CloudingDeviceInfo):  # pyright: ignore[reportIncompatibleVariableOverride] # pylint: disable=too-many-instance-attributes
    """A Clouding.io sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CloudingDataUpdateCoordinator,
        server_id: str,
        description: CloudingSensorEntityDescription,
        device_name: str,
    ) -> None:
        """Initialize Clouding sensors.

        Args:
            coordinator: The data update coordinator.
            server_id: The unique identifier of the server.
            description: The entity description for this sensor.
            device_name: The name of the device as configured.

        """

        super().__init__(coordinator)

        server: CloudingServer = coordinator.api.servers[server_id]

        part_entity_id: str = slugify(f"{device_name} {server.attr_id} {description.name_suffix}")
        self.entity_id = f"{SENSOR_DOMAIN}.{part_entity_id}"
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

        self._update_attr()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update.

        Returns:
            None.

        """
        self._update_attr()
        super()._handle_coordinator_update()

    @callback
    def _update_attr(self) -> None:
        """Update attributes for sensor.

        Returns:
            None.

        """
        try:
            self._attr_native_value = getattr(
                self.coordinator.api.servers[self._server_unique_id], "attr_" + self.entity_description.key
            )

            if self.entity_description.key == EnumCloudingSensor.SERVER_STATUS:
                value: str = str(self._attr_native_value).lower()

                if value == "archived":
                    self._attr_icon = "mdi:archive-check-outline"
                elif value in ["unarchiving", "archiving"]:
                    self._attr_icon = "mdi:archive-clock-outline"
                elif value == "stopped":
                    self._attr_icon = "mdi:close-circle-outline"
                elif value in ["starting", "stopping"]:
                    self._attr_icon = "mdi:refresh-circle"
                else:
                    self._attr_icon = "mdi:check-circle-outline"

        except KeyError:
            self._attr_native_value = None

"""Python API wrapper for Clouding.io."""

# ruff: noqa: N815
# pylint: disable=invalid-name

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TC003
from zoneinfo import ZoneInfo

from mashumaro import DataClassDictMixin


@dataclass
class CloudingBaseModel(DataClassDictMixin):
    """Base model for Clouding.io API resources.

    Attributes:
        id: The unique identifier of the resource.

    """

    id: str | None = None

    @property
    def attr_id(self) -> str:
        """Return the unique identifier of the resource.

        Returns:
            The resource ID as a string.

        """
        return str(self.id)


@dataclass(kw_only=True)
class CloudingServerImage(CloudingBaseModel):
    """Server Image model for Clouding.io."""

    name: str | None = None

    @property
    def attr_name(self) -> str:
        """Return the name of the server image.

        Returns:
            The image name as a string.

        """
        return str(self.name)


@dataclass(kw_only=True)
class CloudingPublicPorts(CloudingBaseModel):
    """Public ports model for a Clouding.io server.

    Attributes:
        ipAddress: The public IP address associated with the port.
        macAddress: The MAC address associated with the port.

    """

    ipAddress: str | None = None
    macAddress: str | None = None


@dataclass(kw_only=True)
class CloudingServer(CloudingBaseModel):  # pylint: disable=too-many-instance-attributes
    """Server model for Clouding.io.

    Attributes:
        createdAt: The datetime when the server was created.
        dnsAddress: The DNS address of the server.
        flavor: The flavor (instance type) of the server.
        hostname: The hostname of the server.
        image: The image associated with the server.
        name: The display name of the server.
        powerState: The current power state of the server.
        privateIp: The private IP address of the server, if any.
        publicIp: The public IP address of the server.
        publicPorts: The list of public ports associated with the server.
        ramGb: The amount of RAM allocated to the server in gigabytes.
        status: The current status of the server.
        vCores: The number of virtual CPU cores allocated to the server.
        volumeSizeGb: The volume size of the server in gigabytes.

    """

    createdAt: datetime
    dnsAddress: str
    flavor: str
    hostname: str
    image: CloudingServerImage
    name: str
    powerState: str
    privateIp: str | None = None
    publicIp: str
    publicPorts: list[CloudingPublicPorts]
    ramGb: int
    status: str
    vCores: int
    volumeSizeGb: int

    @property
    def attr_created_at(self) -> datetime:
        """Return the server creation date with Paris timezone.

        Returns:
            A timezone-aware datetime object set to Europe/Paris.

        """
        return self.createdAt.replace(tzinfo=ZoneInfo("Europe/Paris"))

    @property
    def attr_dns_address(self) -> str:
        """Return the DNS address of the server.

        Returns:
            The DNS address as a string.

        """
        return self.dnsAddress

    @property
    def attr_flavor(self) -> str:
        """Return the flavor (instance type) of the server.

        Returns:
            The flavor identifier as a string.

        """
        return self.flavor

    @property
    def attr_hostname(self) -> str:
        """Return the hostname of the server.

        Returns:
            The hostname as a string.

        """
        return self.hostname

    @property
    def attr_image(self) -> CloudingServerImage:
        """Return the image associated with the server.

        Returns:
            A CloudingServerImage instance.

        """
        return self.image

    @property
    def attr_name(self) -> str:
        """Return the display name of the server.

        Returns:
            The server name as a string.

        """
        return self.name

    @property
    def attr_power_state(self) -> str:
        """Return the current power state of the server.

        Returns:
            The power state as a string (e.g. 'running', 'shutdown').

        """
        return self.powerState

    @property
    def attr_public_ip(self) -> str:
        """Return the public IP address of the server.

        Returns:
            The public IP address as a string.

        """
        return self.publicIp

    @property
    def attr_status(self) -> str:
        """Return the current status of the server.

        Returns:
            The status as a string (e.g. 'active', 'archived', 'stopped').

        """
        return self.status

    @property
    def attr_ram_gb(self) -> int:
        """Return the amount of RAM allocated to the server in gigabytes.

        Returns:
            The RAM size as an integer.

        """
        return self.ramGb

    @property
    def attr_vcores(self) -> int:
        """Return the number of virtual CPU cores allocated to the server.

        Returns:
            The vCores count as an integer.

        """
        return self.vCores

    @property
    def attr_volume_size_gb(self) -> int:
        """Return the volume size of the server in gigabytes.

        Returns:
            The volume size as an integer.

        """
        return self.volumeSizeGb

    @property
    def attr_is_running(self) -> bool:
        """Return whether the server is currently running.

        Returns:
            True if the power state is not 'shutdown', False otherwise.

        """
        return self.powerState.lower() != "shutdown"

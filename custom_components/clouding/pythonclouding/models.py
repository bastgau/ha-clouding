"""Python API wrapper for Clouding.io"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from mashumaro import DataClassDictMixin


@dataclass
class CloudingBaseModel(DataClassDictMixin):
    """CloudingBaseModel."""

    id: str | None = None

    @property
    def attr_id(self) -> str:
        return self.id


@dataclass(kw_only=True)
class CloudingServerImage(CloudingBaseModel):
    """Server Image model for Clouding.io"""

    name: str | None = None

    @property
    def attr_name(self) -> str:
        return self.name


@dataclass(kw_only=True)
class CloudingPublicPorts(CloudingBaseModel):
    """Server Image model for Clouding.io"""

    ipAddress: str | None = None
    macAddress: str | None = None


@dataclass(kw_only=True)
class CloudingServer(CloudingBaseModel):
    """Server model for Clouding.io"""

    createdAt: datetime
    dnsAddress: str
    flavor: str
    hostname: str
    image: CloudingServerImage
    name: str
    powerState: str
    privateIp: str | None = None
    publicIp: str
    publicPorts: List[CloudingPublicPorts]
    ramGb: int
    status: str
    vCores: int
    volumeSizeGb: int

    @property
    def attr_created_at(self) -> datetime:
        return self.createdAt.replace(tzinfo=ZoneInfo("Europe/Paris"))

    @property
    def attr_dns_address(self) -> str:
        return self.dnsAddress

    @property
    def attr_flavor(self) -> str:
        return self.flavor

    @property
    def attr_hostname(self) -> str:
        return self.hostname

    @property
    def attr_image(self) -> CloudingServerImage:
        return self.image

    @property
    def attr_name(self) -> str:
        return self.name

    @property
    def attr_power_state(self) -> str:
        return self.powerState

    @property
    def attr_public_ip(self) -> str:
        return self.publicIp

    @property
    def attr_status(self) -> str:
        return self.status

    @property
    def attr_ram_gb(self) -> int:
        return self.ramGb

    @property
    def attr_vcores(self) -> int:
        return self.vCores

    @property
    def attr_volume_size_gb(self) -> int:
        return self.volumeSizeGb

    @property
    def attr_is_running(self) -> bool:
        return self.powerState.lower() != "shutdown"

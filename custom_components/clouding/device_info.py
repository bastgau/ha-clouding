"""Device platform for the Clouding.io integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import slugify

from .const import DOMAIN, MANUFACTURER_NAME, PORTAL_URL


class CloudingDeviceInfo:  # pylint: disable=too-few-public-methods
    """Provide device information for a Clouding.io server entity.

    Attributes:
        _device_name: The integration instance name configured by the user.
        _model_name: The server image/model name.
        _server_name: The display name of the server.
        _server_unique_id: The unique identifier of the server.

    """

    _device_name: str
    _model_name: str
    _server_name: str
    _server_unique_id: str

    def __init__(self, device_name: str, model_name: str, server_name: str, server_unique_id: str) -> None:
        """Initialize CloudingDeviceInfo.

        Args:
            device_name: The integration instance name configured by the user.
            model_name: The server image/model name.
            server_name: The display name of the server.
            server_unique_id: The unique identifier of the server.

        """

        self._device_name = device_name
        self._model_name = model_name
        self._server_name = server_name
        self._server_unique_id = server_unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information of the entity.

        Returns:
            A DeviceInfo instance populated with Clouding.io server metadata.

        """

        return DeviceInfo(
            identifiers={(DOMAIN, slugify(f"{self._device_name} {self._server_unique_id}"))},
            name=self._server_name,
            manufacturer=MANUFACTURER_NAME,
            configuration_url=PORTAL_URL,
            model=self._model_name,
            serial_number=self._server_unique_id,
        )

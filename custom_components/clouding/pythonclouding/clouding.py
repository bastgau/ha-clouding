"""Python API wrapper for Clouding.io"""

from http import HTTPStatus
from typing import Any

from aiohttp import ClientError, ClientResponse, ClientResponseError, ClientSession, ClientTimeout
from yarl import URL

from .const import CLOUDING_BASE_URL
from .exceptions import (
    CloudingAuthenticationException,
    CloudingBadRequestException,
    CloudingConnectionException,
    CloudingInvalidAPIResponseException,
)
from .models import CloudingServer


class Clouding:
    """Clouding.io client."""

    _base_url: str
    _headers: dict[str, str]
    _timeout: ClientTimeout
    _session: ClientSession
    _servers: dict[str, CloudingServer]

    def __init__(self, session: ClientSession, api_key: str | None = None, timeout: float = 10) -> None:
        """Initialize the Clouding.io client."""

        self._base_url = CLOUDING_BASE_URL if isinstance(CLOUDING_BASE_URL, URL) else URL(CLOUDING_BASE_URL)
        self._headers = {"X-API-KEY": api_key}
        self._timeout = ClientTimeout(total=timeout)
        self._session = session

    @property
    def servers(self) -> dict[str, CloudingServer]:
        """..."""
        return self._servers

    async def get_servers(self) -> dict[str, CloudingServer]:
        """Retrieve servers from Clouding.io"""

        url = self._base_url / "servers"
        request: ClientResponse = await self._call(url, headers=self._headers, timeout=self._timeout, method="get")
        return await self._prepare_server_results(request)

    async def call_action_server(self, action: str, id: str) -> None:
        """..."""

        url = self._base_url / "servers" / id / action
        request: ClientResponse = await self._call(url, headers=self._headers, timeout=self._timeout, method="post")
        return request.json

    async def _call(self, url, headers: dict[str, Any], timeout: float, method: str) -> ClientResponse:
        """..."""

        exception_msg: str = ""

        try:
            if method == "post":
                request: ClientResponse = await self._session.post(url, headers=headers, timeout=timeout)
            else:
                request: ClientResponse = await self._session.get(url, headers=headers, timeout=timeout)
            request.raise_for_status()
        except ClientResponseError as e:
            if e.status == HTTPStatus.UNAUTHORIZED:
                exception_msg = f"Authentication failed for {url!s}"
                raise CloudingAuthenticationException(exception_msg) from e
            if e.status == HTTPStatus.BAD_REQUEST:
                exception_msg = f"Bad request for {url!s}"
                raise CloudingBadRequestException(exception_msg) from e
            exception_msg = f"Request for {url!s} failed with status code {e.status}"
            raise CloudingConnectionException(exception_msg) from e
        except TimeoutError as e:
            exception_msg = f"Request timeout for {url!s}"
            raise CloudingConnectionException(exception_msg) from e
        except ClientError as e:
            raise CloudingConnectionException from e

        return request

    async def _prepare_server_results(self, request: ClientResponse) -> dict[str, CloudingServer]:
        """..."""

        results: dict[str, Any] = await request.json()

        if "servers" not in results:
            raise CloudingInvalidAPIResponseException

        dict_results: dict[str, Any] = {result["id"]: result for result in results["servers"]}
        self._servers = {key: CloudingServer.from_dict(value) for key, value in dict_results.items()}

        return self._servers

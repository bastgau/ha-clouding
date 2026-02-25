"""Python API wrapper for Clouding.io."""

from http import HTTPStatus
from typing import Any, Literal

from aiohttp import ClientError, ClientResponse, ClientResponseError, ClientSession, ClientTimeout
from yarl import URL

from .const import CLOUDING_BASE_URL
from .exceptions import (
    CloudingAuthenticationError,
    CloudingBadRequestError,
    CloudingConnectionError,
    CloudingInvalidAPIResponseError,
)
from .models import CloudingServer


class Clouding:
    """Clouding.io client."""

    def __init__(self, session: ClientSession, api_key: str | None = None, timeout: float = 10) -> None:
        """Initialize the Clouding.io client.

        Args:
            session (ClientSession): The aiohttp client session to use for requests.
            api_key (str | None): The Clouding.io API key for authentication.
            timeout (float): The request timeout in seconds.

        """

        self._base_url: URL = CLOUDING_BASE_URL if isinstance(CLOUDING_BASE_URL, URL) else URL(CLOUDING_BASE_URL)
        self._headers: dict[str, str] = {"X-API-KEY": str(api_key)}
        self._timeout: ClientTimeout = ClientTimeout(total=timeout)
        self._session: ClientSession = session

        self._servers: dict[str, CloudingServer] = {}

    @property
    def servers(self) -> dict[str, CloudingServer]:
        """Return the cached dictionary of CloudingServer instances.

        Returns:
            dict[str, CloudingServer]: A dictionary mapping server IDs to their CloudingServer instances.

        """
        return self._servers

    async def get_servers(self) -> dict[str, CloudingServer]:
        """Retrieve servers from Clouding.io.

        Returns:
            dict[str, CloudingServer]: A dictionary mapping server IDs to their CloudingServer instances.

        Raises:
            CloudingAuthenticationError: If the API key is invalid or authentication fails.
            CloudingBadRequestError: If the request is malformed.
            CloudingConnectionError: If the request fails or times out.
            CloudingInvalidAPIResponseError: If the response does not contain a 'servers' key.

        """

        url = self._base_url / "servers"
        request: ClientResponse = await self._call(url, headers=self._headers, req_timeout=self._timeout, method="get")
        return await self._prepare_server_results(request)

    async def call_action_server(self, action: str, server_id: str) -> dict[str, Any]:
        """Send an action request to a specific Clouding.io server.

        Args:
            action (str): The action to perform (e.g. 'start', 'stop', 'reboot', 'hard-reboot').
            server_id (str): The unique identifier of the target server.

        Returns:
            dict[str, Any]: A dictionary containing JSON response from the API.

        Raises:
            CloudingAuthenticationError: If authentication fails.
            CloudingBadRequestError: If the action is not valid for the current server state.
            CloudingConnectionError: If the request fails or times out.

        """

        url = self._base_url / "servers" / server_id / action
        request: ClientResponse = await self._call(url, headers=self._headers, req_timeout=self._timeout, method="post")
        return await request.json()

    async def _call(
        self, url: URL, headers: dict[str, str], req_timeout: ClientTimeout, method: Literal["get", "post"]
    ) -> ClientResponse:
        """Perform an HTTP request to the Clouding.io API.

        Args:
            url (URL): The target URL for the request.
            headers (dict[str, str]): HTTP headers to include in the request.
            req_timeout (ClientTimeout): The aiohttp ClientTimeout object controlling the request timeout.
            method (Literal["get", "post"]): HTTP method to use ('get' or 'post').

        Returns:
            ClientResponse: The aiohttp ClientResponse object.

        Raises:
            KeyError: if the method is not supported.
            CloudingAuthenticationError: If the response status is 401 Unauthorized.
            CloudingBadRequestError: If the response status is 400 Bad Request.
            CloudingConnectionError: If the request fails, times out, or returns another error status.

        """

        if method not in ["get", "post"]:
            msg: str = f"The method with the value '{method}' is unknown"
            raise KeyError(msg)

        exception_msg: str = ""

        response: ClientResponse | None = None

        try:
            if method == "post":
                response = await self._session.post(url, headers=headers, timeout=req_timeout)
            elif method == "get":
                response = await self._session.get(url, headers=headers, timeout=req_timeout)

            response.raise_for_status()
        except ClientResponseError as e:
            if e.status == HTTPStatus.UNAUTHORIZED:
                exception_msg = f"Authentication failed for {url!s}"
                raise CloudingAuthenticationError(exception_msg) from e
            if e.status == HTTPStatus.BAD_REQUEST:
                exception_msg = f"Bad request for {url!s}"
                raise CloudingBadRequestError(exception_msg) from e
            exception_msg = f"Request for {url!s} failed with status code {e.status}"
            raise CloudingConnectionError(exception_msg) from e
        except TimeoutError as e:
            exception_msg = f"Request timeout for {url!s}"
            raise CloudingConnectionError(exception_msg) from e
        except ClientError as e:
            raise CloudingConnectionError from e

        return response

    async def _prepare_server_results(self, request: ClientResponse) -> dict[str, CloudingServer]:
        """Parse the API response and populate the internal servers dictionary.

        Args:
            request (ClientResponse): The aiohttp ClientResponse from the servers endpoint.

        Returns:
            dict[str, CloudingServer]: A dictionary mapping server IDs to their CloudingServer instances.

        Raises:
            CloudingInvalidAPIResponseError: If the response does not contain a 'servers' key.

        """

        results: dict[str, Any] = await request.json()

        if "servers" not in results:
            raise CloudingInvalidAPIResponseError

        dict_results: dict[str, Any] = {result["id"]: result for result in results["servers"]}
        self._servers = {key: CloudingServer.from_dict(value) for key, value in dict_results.items()}  # pyright: ignore[reportUnknownMemberType]

        return self._servers

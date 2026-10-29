"""Check how the Clouding.io client turns HTTP failures and malformed answers into its own exceptions."""

from unittest.mock import AsyncMock, Mock

from aiohttp import ClientConnectionError, ClientResponseError
from custom_components.clouding.pythonclouding import (
    Clouding,
    CloudingAuthenticationError,
    CloudingBadRequestError,
    CloudingError,
)
from custom_components.clouding.pythonclouding.exceptions import (
    CloudingConnectionError,
    CloudingInvalidAPIResponseError,
)
import pytest


def _session(*, get_error: Exception | None = None, payload: dict[str, object] | None = None) -> Mock:
    """Build a fake aiohttp session that fails with get_error or answers payload."""
    response = Mock()
    response.json = AsyncMock(return_value=payload or {})
    if get_error is not None:
        response.raise_for_status = Mock(side_effect=get_error)
    session = Mock()
    session.get = AsyncMock(return_value=response)
    session.post = AsyncMock(return_value=response)
    return session


def _http_error(status: int) -> ClientResponseError:
    """Return the error aiohttp raises for an HTTP status."""
    return ClientResponseError(request_info=Mock(), history=(), status=status)


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        pytest.param(_http_error(401), CloudingAuthenticationError, id="unauthorized"),
        pytest.param(_http_error(400), CloudingBadRequestError, id="bad-request"),
        pytest.param(_http_error(500), CloudingConnectionError, id="other-status"),
        pytest.param(TimeoutError(), CloudingConnectionError, id="timeout"),
        pytest.param(ClientConnectionError(), CloudingConnectionError, id="connection"),
    ],
)
async def test_get_servers_translates_request_failures(error: Exception, expected: type[CloudingError]) -> None:
    """Every request failure comes out as the matching Clouding exception, never as an aiohttp one."""
    client = Clouding(_session(get_error=error), api_key="secret")

    with pytest.raises(expected):
        await client.get_servers()


async def test_get_servers_rejects_an_answer_without_servers() -> None:
    """An answer that has no servers key is an invalid API response, not an empty list."""
    client = Clouding(_session(payload={"unexpected": []}), api_key="secret")

    with pytest.raises(CloudingInvalidAPIResponseError):
        await client.get_servers()


async def test_get_servers_of_an_empty_list_caches_nothing() -> None:
    """An answer with an empty servers list gives an empty dictionary, kept by the client."""
    client = Clouding(_session(payload={"servers": []}), api_key="secret")

    assert await client.get_servers() == {}
    assert client.servers == {}


async def test_call_action_server_posts_to_the_server_action_url() -> None:
    """The action is posted to servers/<id>/<action>, with the API key header, and the JSON answer is returned."""
    session = _session(payload={"status": "ok"})
    client = Clouding(session, api_key="secret")

    assert await client.call_action_server("start", "abc") == {"status": "ok"}

    assert str(session.post.await_args.args[0]) == "https://api.clouding.io/v1/servers/abc/start"
    assert session.post.await_args.kwargs["headers"] == {"X-API-KEY": "secret"}

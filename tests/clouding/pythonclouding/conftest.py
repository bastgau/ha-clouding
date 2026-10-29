"""Fixtures for the bundled client's own tests.

These tests cover `custom_components/clouding/pythonclouding/`, which knows nothing about Home Assistant. The
`client` job of the test workflow installs no Home Assistant test plugin, and this file keeps these tests
independent of it.
"""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations() -> None:
    """Neutralize the root conftest's Home Assistant fixture for this package.

    `tests/conftest.py` declares an autouse fixture that pulls in `enable_custom_integrations`, which only exists
    once pytest-homeassistant-custom-component is installed. A fixture defined in a nested conftest shadows its
    parent's, so overriding it here drops that dependency for the client tests, which never load a Home Assistant
    instance.

    """

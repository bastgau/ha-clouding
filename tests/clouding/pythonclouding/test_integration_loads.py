"""Check that the Clouding.io API client package can be imported.

A first test to start from, seeded once by the template: the repository owns it, edit it or delete it.
"""

import importlib


def test_client_loads() -> None:
    """The client package imports, without Home Assistant being started."""
    module = importlib.import_module("custom_components.clouding.pythonclouding")

    assert module.__name__ == "custom_components.clouding.pythonclouding"

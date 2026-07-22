"""Fixtures for HA-integration tests (config flow, entities, etc.).

Deliberately does NOT declare `pytest_plugins = "pytest_homeassistant_custom_component"`
here: pytest only allows that string-based plugin registration in a *top-level*
conftest.py, and the top-level tests/conftest.py is a shared ancestor of
tests/scheduling/ too (whose whole point is running without homeassistant
installed at all -- see tests/scheduling/'s docstring and pytest.ini). So this
suite is invoked with the plugin loaded via the CLI instead:

    pytest tests/components -p pytest_homeassistant_custom_component

(requirements_test.txt has the pinned version). tests/scheduling/ never needs
that flag and never touches homeassistant.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make custom_components/ discoverable by Home Assistant's loader in tests."""
    yield

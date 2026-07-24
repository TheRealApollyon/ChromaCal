"""Tests for the ChromaCal sensor platform: one entity per configured light.

Complements the manual container-restart verification with an automated
check that setting up a real config entry actually creates the sensor with
a sensible state and attributes -- exercising the same
custom_components.chromacal -> coordinator -> sensor path, just without a
browser or a running HA UI.
"""

from __future__ import annotations

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import DOMAIN

ENTRY_DATA = {
    "region": "us",
    "categories": {"federal": True},
    "lights": [
        {
            "name": "Front Porch",
            "zone": "",
            "entity": "light.front_porch",
            "start_type": "sunset",
            "start_time": "19:00",
            "end_type": "time",
            "end_time": "23:00",
            "fade_in": 30,
            "fade_out": 120,
            "warmwhite_time": "22:00",
            "warmwhite_enabled": True,
        }
    ],
}


async def test_sensor_created_for_configured_light(hass):
    """Setting up a config entry creates a schedule sensor with real data."""
    hass.states.async_set(
        "sun.sun",
        "above_horizon",
        {"next_setting": "2026-12-25T20:00:00+00:00"},
    )

    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_entry")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, "test_entry_light.front_porch_schedule"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state not in (None, "unknown", "unavailable")
    assert state.attributes["light_entity"] == "light.front_porch"
    assert "segments" in state.attributes
    assert len(state.attributes["segments"]) >= 1


async def test_sensor_falls_back_gracefully_without_sun_entity(hass):
    """No sun.sun entity -> setup still succeeds, sensor still gets a value."""
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_entry_2")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, "test_entry_2_light.front_porch_schedule"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state not in (None, "unknown", "unavailable")

"""Tests for House View: coordinator state/persistence, the
chromacal.set_house_view / add_house_marker / assign_house_marker /
remove_house_marker services, and the sensor that exposes all of it to
the panel.

Mirrors test_tonight_pick_and_color_override.py's structure -- House View
is persisted to config entry OPTIONS the same way, mutated via services
the same way, and exposed to the frontend via a sensor's
extra_state_attributes the same way.
"""

from __future__ import annotations

import pytest
import voluptuous as vol
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import (
    ATTR_LIGHT_ENTITY,
    ATTR_MARKER_ID,
    ATTR_MODE,
    ATTR_PATH,
    ATTR_X,
    ATTR_Y,
    ATTR_Z,
    CONF_HOUSE_VIEW_MARKERS,
    CONF_HOUSE_VIEW_MODE,
    CONF_HOUSE_VIEW_PATH,
    DOMAIN,
    SERVICE_ADD_HOUSE_MARKER,
    SERVICE_ASSIGN_HOUSE_MARKER,
    SERVICE_REMOVE_HOUSE_MARKER,
    SERVICE_SET_HOUSE_VIEW,
)

LIGHT_ENTITY = "light.front_porch"

ENTRY_DATA = {
    "region": "us",
    "categories": {"federal": True},
    "lights": [
        {
            "name": "Front Porch",
            "zone": "",
            "entity": LIGHT_ENTITY,
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


async def _setup_entry(hass, entry_id: str) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id=entry_id)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_defaults_before_any_configuration(hass):
    entry = await _setup_entry(hass, "test_house_view_defaults")
    coordinator = entry.runtime_data

    assert coordinator.house_view_mode == "2d"
    assert coordinator.house_view_path == ""
    assert coordinator.house_view_markers == []


async def test_set_house_view_persists_mode_and_path(hass):
    entry = await _setup_entry(hass, "test_house_view_set")
    coordinator = entry.runtime_data

    await coordinator.async_set_house_view("3d", "/local/myhouse.glb")
    assert coordinator.house_view_mode == "3d"
    assert coordinator.house_view_path == "/local/myhouse.glb"

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert live_entry.options[CONF_HOUSE_VIEW_MODE] == "3d"
    assert live_entry.options[CONF_HOUSE_VIEW_PATH] == "/local/myhouse.glb"


async def test_add_assign_remove_marker(hass):
    entry = await _setup_entry(hass, "test_house_view_marker_lifecycle")
    coordinator = entry.runtime_data

    await coordinator.async_add_house_marker("2d", 0.25, 0.5, None)
    assert len(coordinator.house_view_markers) == 1
    marker = coordinator.house_view_markers[0]
    assert marker["mode"] == "2d"
    assert marker["x"] == 0.25
    assert marker["y"] == 0.5
    assert marker["z"] is None
    assert marker["light_entity"] is None
    # A generated id, not list position -- see CONF_HOUSE_VIEW_MARKERS.
    marker_id = marker["id"]
    assert isinstance(marker_id, str) and marker_id

    await coordinator.async_assign_house_marker(marker_id, LIGHT_ENTITY)
    assert coordinator.house_view_markers[0]["light_entity"] == LIGHT_ENTITY

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert live_entry.options[CONF_HOUSE_VIEW_MARKERS][0]["light_entity"] == LIGHT_ENTITY

    await coordinator.async_remove_house_marker(marker_id)
    assert coordinator.house_view_markers == []
    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert live_entry.options[CONF_HOUSE_VIEW_MARKERS] == []


async def test_assign_unknown_marker_id_is_a_silent_no_op(hass):
    """Same idiom as async_reset_color_override's pop(..., None) -- a
    stale/racing marker_id doesn't raise."""
    entry = await _setup_entry(hass, "test_house_view_unknown_marker")
    coordinator = entry.runtime_data

    await coordinator.async_assign_house_marker("does-not-exist", LIGHT_ENTITY)
    assert coordinator.house_view_markers == []

    await coordinator.async_remove_house_marker("does-not-exist")
    assert coordinator.house_view_markers == []


async def test_assign_house_marker_rejects_non_light_entity(hass):
    """Security-review finding: assign_house_marker's light_entity used to
    accept any syntactically-valid entity_id in the instance (cv.entity_id
    alone doesn't check domain), even though a marker only ever means
    "one of ChromaCal's own configured lights" and the UI picker already
    only ever offers those. Now constrained with cv.entity_domain("light")."""
    entry = await _setup_entry(hass, "test_house_view_wrong_domain")
    coordinator = entry.runtime_data
    await coordinator.async_add_house_marker("2d", 0.1, 0.2, None)
    marker_id = coordinator.house_view_markers[0]["id"]

    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ASSIGN_HOUSE_MARKER,
            {ATTR_MARKER_ID: marker_id, ATTR_LIGHT_ENTITY: "switch.chromacal_emergency_mode"},
            blocking=True,
        )

    # A real light entity is still accepted.
    await hass.services.async_call(
        DOMAIN,
        SERVICE_ASSIGN_HOUSE_MARKER,
        {ATTR_MARKER_ID: marker_id, ATTR_LIGHT_ENTITY: LIGHT_ENTITY},
        blocking=True,
    )
    assert coordinator.house_view_markers[0]["light_entity"] == LIGHT_ENTITY


async def test_house_view_survives_reload(hass):
    entry = await _setup_entry(hass, "test_house_view_reload")
    coordinator = entry.runtime_data

    await coordinator.async_set_house_view("2d", "/local/myhouse.png")
    await coordinator.async_add_house_marker("2d", 0.1, 0.2, None)
    marker_id = coordinator.house_view_markers[0]["id"]
    await coordinator.async_assign_house_marker(marker_id, LIGHT_ENTITY)

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    reloaded_coordinator = live_entry.runtime_data
    assert reloaded_coordinator.house_view_mode == "2d"
    assert reloaded_coordinator.house_view_path == "/local/myhouse.png"
    assert len(reloaded_coordinator.house_view_markers) == 1
    assert reloaded_coordinator.house_view_markers[0]["light_entity"] == LIGHT_ENTITY


async def test_services_are_registered_and_mutate_coordinator_state(hass):
    entry = await _setup_entry(hass, "test_house_view_services")
    coordinator = entry.runtime_data

    assert hass.services.has_service(DOMAIN, SERVICE_SET_HOUSE_VIEW)
    assert hass.services.has_service(DOMAIN, SERVICE_ADD_HOUSE_MARKER)
    assert hass.services.has_service(DOMAIN, SERVICE_ASSIGN_HOUSE_MARKER)
    assert hass.services.has_service(DOMAIN, SERVICE_REMOVE_HOUSE_MARKER)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_HOUSE_VIEW,
        {ATTR_MODE: "3d", ATTR_PATH: "/local/myhouse.glb"},
        blocking=True,
    )
    assert coordinator.house_view_mode == "3d"

    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_HOUSE_MARKER,
        {ATTR_MODE: "3d", ATTR_X: 1.0, ATTR_Y: 2.0, ATTR_Z: 3.0},
        blocking=True,
    )
    assert len(coordinator.house_view_markers) == 1
    marker_id = coordinator.house_view_markers[0]["id"]
    assert coordinator.house_view_markers[0]["z"] == 3.0

    await hass.services.async_call(
        DOMAIN,
        SERVICE_ASSIGN_HOUSE_MARKER,
        {ATTR_MARKER_ID: marker_id, ATTR_LIGHT_ENTITY: LIGHT_ENTITY},
        blocking=True,
    )
    assert coordinator.house_view_markers[0]["light_entity"] == LIGHT_ENTITY

    await hass.services.async_call(
        DOMAIN, SERVICE_REMOVE_HOUSE_MARKER, {ATTR_MARKER_ID: marker_id}, blocking=True
    )
    assert coordinator.house_view_markers == []


async def test_services_removed_on_unload(hass):
    entry = await _setup_entry(hass, "test_house_view_services_unload")

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_SET_HOUSE_VIEW)
    assert not hass.services.has_service(DOMAIN, SERVICE_ADD_HOUSE_MARKER)
    assert not hass.services.has_service(DOMAIN, SERVICE_ASSIGN_HOUSE_MARKER)
    assert not hass.services.has_service(DOMAIN, SERVICE_REMOVE_HOUSE_MARKER)


async def test_house_view_sensor_exposes_config_to_the_panel(hass):
    """The panel's entire House View data model comes from this sensor's
    attributes (mirrors how the Upcoming Events sensor feeds the
    Tonight's Pick/Color Override UI) -- not from the coordinator
    directly, since the panel only ever reads HA entity states."""
    entry = await _setup_entry(hass, "test_house_view_sensor")
    coordinator = entry.runtime_data

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, "test_house_view_sensor_house_view")
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state.state == "0"
    assert state.attributes["role"] == "house_view"
    assert state.attributes["mode"] == "2d"
    assert state.attributes["path"] == ""
    assert state.attributes["markers"] == []

    await coordinator.async_set_house_view("3d", "/local/myhouse.glb")
    await coordinator.async_add_house_marker("3d", 1.0, 2.0, 3.0)
    marker_id = coordinator.house_view_markers[0]["id"]
    await coordinator.async_assign_house_marker(marker_id, LIGHT_ENTITY)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state.state == "1"
    assert state.attributes["mode"] == "3d"
    assert state.attributes["path"] == "/local/myhouse.glb"
    assert state.attributes["markers"] == [
        {
            "id": marker_id,
            "mode": "3d",
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
            "light_entity": LIGHT_ENTITY,
        }
    ]

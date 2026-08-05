"""Tests for the light Config Subentry flow (Phase 8): add, edit, and the
real gap found while building this -- removing a light via HA's own
generic subentry-delete path (no reload involved) must still stop that
light from being scheduled on the very next refresh cycle.
"""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import (
    CONF_END_TYPE,
    CONF_ENTITY,
    CONF_FADE_IN,
    CONF_FADE_OUT,
    CONF_NAME,
    CONF_START_TYPE,
    CONF_WARMWHITE_ENABLED,
    DOMAIN,
    LIGHT_SUBENTRY_TYPE,
)

FRONT_PORCH_ENTITY = "light.front_porch"
BACK_YARD_ENTITY = "light.back_yard"

FRONT_PORCH_LIGHT_DATA = {
    "name": "Front Porch",
    "zone": "",
    "entity": FRONT_PORCH_ENTITY,
    "start_type": "sunset",
    "start_time": "19:00",
    "end_type": "time",
    "end_time": "23:00",
    "fade_in": 30,
    "fade_out": 120,
    "warmwhite_time": "22:00",
    "warmwhite_enabled": True,
}

FRESH_ENTRY_DATA = {"region": "us", "categories": {"federal": True}}
FRESH_SUBENTRY = {
    "subentry_type": LIGHT_SUBENTRY_TYPE,
    "title": "Front Porch",
    "unique_id": None,
    "data": FRONT_PORCH_LIGHT_DATA,
}


async def _setup_entry(hass, entry_id: str) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=FRESH_ENTRY_DATA,
        entry_id=entry_id,
        version=2,
        subentries_data=[FRESH_SUBENTRY],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_add_light_creates_a_new_subentry_and_entities(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_add_light")
    assert len(entry.subentries) == 1

    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, LIGHT_SUBENTRY_TYPE),
        context={"source": config_entries.SOURCE_USER},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Back Yard",
            CONF_ENTITY: BACK_YARD_ENTITY,
            CONF_START_TYPE: "sunset",
            CONF_END_TYPE: "time",
            CONF_FADE_IN: "30",
            CONF_FADE_OUT: "120",
            CONF_WARMWHITE_ENABLED: True,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    # Adding a subentry has no built-in reload-and-abort helper (unlike
    # editing) -- the flow schedules its own reload afterward so the new
    # light actually gets sensor/button entities, not just a subentry.
    # Wait for that scheduled reload to finish, not just the flow's own
    # immediate side effects.
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    lights = [s for s in live_entry.subentries.values() if s.subentry_type == LIGHT_SUBENTRY_TYPE]
    assert len(lights) == 2
    names = {s.data[CONF_NAME] for s in lights}
    assert names == {"Front Porch", "Back Yard"}

    # A real entity exists for the new light too, not just the subentry.
    coordinator = live_entry.runtime_data
    assert BACK_YARD_ENTITY in coordinator.data


async def test_edit_light_updates_its_subentry_data(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_edit_light")
    subentry_id = next(iter(entry.subentries))

    result = await entry.start_subentry_reconfigure_flow(hass, subentry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Front Porch Renamed",
            CONF_ENTITY: FRONT_PORCH_ENTITY,
            CONF_START_TYPE: "sunset",
            CONF_END_TYPE: "time",
            CONF_FADE_IN: "60",
            CONF_FADE_OUT: "120",
            CONF_WARMWHITE_ENABLED: True,
        },
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    subentry = live_entry.subentries[subentry_id]
    assert subentry.data[CONF_NAME] == "Front Porch Renamed"
    assert subentry.data[CONF_FADE_IN] == 60
    assert subentry.title == "Front Porch Renamed"
    # Editing does NOT create a second subentry -- same subentry_id.
    assert len(live_entry.subentries) == 1


async def test_removing_a_light_stops_it_being_scheduled_without_a_reload(hass, freezer):
    """The real gap found building this phase: HA's generic subentry-
    delete websocket command (config_entries/subentries/delete, what the
    actual "remove this light" UI action calls) only mutates
    entry.subentries -- it does not reload the config entry. Confirms
    coordinator.lights (a live property reading entry.subentries fresh,
    not a __init__-time snapshot) reflects the removal on the very next
    refresh with no reload involved at all.
    """
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_remove_light")
    coordinator = entry.runtime_data
    subentry_id = next(iter(entry.subentries))

    assert FRONT_PORCH_ENTITY in coordinator.data
    assert len(coordinator.lights) == 1

    registry = er.async_get(hass)
    sensor_entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{subentry_id}_schedule"
    )
    assert sensor_entity_id is not None

    # The exact call the real "delete" UI action makes -- no reload.
    hass.config_entries.async_remove_subentry(entry, subentry_id)

    # No reload anywhere in this test -- proving the live property alone
    # is what makes the next refresh correct.
    assert len(coordinator.lights) == 0

    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert FRONT_PORCH_ENTITY not in coordinator.data

    # The entity itself is gone too (HA's generic subentry cleanup, not
    # anything this integration has to implement).
    assert registry.async_get(sensor_entity_id) is None
    assert hass.states.get(sensor_entity_id) is None

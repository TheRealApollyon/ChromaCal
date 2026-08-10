"""Tests for Tonight's Pick and Color Override: coordinator state/
persistence, the chromacal.set_tonight_pick / set_color_override /
reset_color_override services, and how picking/overriding actually
changes a real awareness-tier collision's resolved schedule.

Real collision used throughout: "Native American Heritage Month"
(category=heritage) and "Movember + Alzheimer's Awareness"
(category=awareness) both run the whole month of November -- with both
categories enabled, every November day is a real, reliable two-event
awareness-tier collision, not a synthetic HolidayEvent. Same collision
used for this phase's live verification (see the plan discussion).
"""

from __future__ import annotations

import homeassistant.util.dt as dt_util
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import (
    ATTR_COLORS,
    ATTR_EVENT_NAME,
    CONF_COLOR_OVERRIDES,
    DOMAIN,
    SERVICE_RESET_COLOR_OVERRIDE,
    SERVICE_SET_COLOR_OVERRIDE,
    SERVICE_SET_TONIGHT_PICK,
)

LIGHT_ENTITY = "light.front_porch"
EVENT_A = "Native American Heritage Month"
EVENT_B = "Movember + Alzheimer's Awareness"

ENTRY_DATA = {
    "region": "us",
    "categories": {"heritage": True, "awareness": True},
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


async def test_tonight_pick_toggles_and_resolves_the_collision(hass, freezer):
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_pick_toggle")
    coordinator = entry.runtime_data

    # Before any pick: real split across both colliding events.
    schedule = coordinator.data[LIGHT_ENTITY]
    assert {s.event.name for s in schedule.segments} == {EVENT_A, EVENT_B}
    assert all(not s.is_pick for s in schedule.segments)

    await coordinator.async_set_tonight_pick(EVENT_B)
    assert coordinator.tonight_pick == EVENT_B
    schedule = coordinator.data[LIGHT_ENTITY]
    assert len(schedule.segments) == 1
    assert schedule.segments[0].event.name == EVENT_B
    assert schedule.segments[0].is_pick is True

    # Same event again -- v1's exact ★-click toggle behavior -- clears it.
    await coordinator.async_set_tonight_pick(EVENT_B)
    assert coordinator.tonight_pick is None
    schedule = coordinator.data[LIGHT_ENTITY]
    assert {s.event.name for s in schedule.segments} == {EVENT_A, EVENT_B}


async def test_tonight_pick_applies_to_every_configured_light(hass, freezer):
    """all-lights, not per-light in the panel UI (per the plan decision) --
    but the underlying ScheduleConfig.tonight_pick dict this feeds still
    has to carry a real per-light entry for each configured light, not
    just one, or a second/third light wouldn't see the pick at all."""
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "region": "us",
            "categories": {"heritage": True, "awareness": True},
            "lights": [
                ENTRY_DATA["lights"][0],
                {**ENTRY_DATA["lights"][0], "name": "Back Yard", "entity": "light.back_yard"},
            ],
        },
        entry_id="test_pick_all_lights",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    coordinator = entry.runtime_data

    await coordinator.async_set_tonight_pick(EVENT_A)
    picked = coordinator._tonight_pick_for_lights()
    assert picked == {"Front Porch": EVENT_A, "Back Yard": EVENT_A}
    assert coordinator.data["light.front_porch"].segments[0].event.name == EVENT_A
    assert coordinator.data["light.back_yard"].segments[0].event.name == EVENT_A


async def test_tonight_pick_resets_at_local_midnight(hass, freezer):
    freezer.move_to("2026-11-10 23:59:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_pick_midnight_reset")
    coordinator = entry.runtime_data

    await coordinator.async_set_tonight_pick(EVENT_A)
    assert coordinator.tonight_pick == EVENT_A

    freezer.move_to("2026-11-11 00:00:01-06:00")
    coordinator.ensure_today_candidates(dt_util.now())
    assert coordinator.tonight_pick is None


async def test_color_override_persists_and_applies(hass, freezer):
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_color_override")
    coordinator = entry.runtime_data

    await coordinator.async_set_color_override(EVENT_A, ["#111111", "#222222"])
    assert coordinator.color_overrides[EVENT_A] == ("#111111", "#222222")

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert live_entry.options[CONF_COLOR_OVERRIDES][EVENT_A] == ["#111111", "#222222"]

    schedule = coordinator.data[LIGHT_ENTITY]
    overridden = next(s for s in schedule.segments if s.event.name == EVENT_A)
    assert overridden.event.colors == ("#111111", "#222222")

    await coordinator.async_reset_color_override(EVENT_A)
    assert EVENT_A not in coordinator.color_overrides
    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert EVENT_A not in live_entry.options.get(CONF_COLOR_OVERRIDES, {})


async def test_color_override_survives_reload(hass, freezer):
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_color_override_reload")
    coordinator = entry.runtime_data
    await coordinator.async_set_color_override(EVENT_B, ["#ABCDEF"])

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    reloaded_coordinator = live_entry.runtime_data
    assert reloaded_coordinator.color_overrides[EVENT_B] == ("#ABCDEF",)


async def test_services_are_registered_and_mutate_coordinator_state(hass, freezer):
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_services")
    coordinator = entry.runtime_data

    assert hass.services.has_service(DOMAIN, SERVICE_SET_TONIGHT_PICK)
    assert hass.services.has_service(DOMAIN, SERVICE_SET_COLOR_OVERRIDE)
    assert hass.services.has_service(DOMAIN, SERVICE_RESET_COLOR_OVERRIDE)

    await hass.services.async_call(
        DOMAIN, SERVICE_SET_TONIGHT_PICK, {ATTR_EVENT_NAME: EVENT_A}, blocking=True
    )
    assert coordinator.tonight_pick == EVENT_A

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR_OVERRIDE,
        {ATTR_EVENT_NAME: EVENT_B, ATTR_COLORS: ["#123456"]},
        blocking=True,
    )
    assert coordinator.color_overrides[EVENT_B] == ("#123456",)

    await hass.services.async_call(
        DOMAIN, SERVICE_RESET_COLOR_OVERRIDE, {ATTR_EVENT_NAME: EVENT_B}, blocking=True
    )
    assert EVENT_B not in coordinator.color_overrides


async def test_upcoming_events_sensor_exposes_pick_and_overrides(hass, freezer):
    """The panel's entire data model for these two buttons comes from
    this sensor's attributes (see grouping.ts's RawUpcomingAttrs) -- not
    from the coordinator directly, since the panel only ever reads HA
    entity states. Confirms the wire shape it actually depends on."""
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_sensor_attrs")
    coordinator = entry.runtime_data

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, "test_sensor_attrs_upcoming_events")
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state.attributes["tonight_pick"] is None
    assert state.attributes["color_overrides"] == {}

    await coordinator.async_set_tonight_pick(EVENT_A)
    await coordinator.async_set_color_override(EVENT_B, ["#654321"])
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state.attributes["tonight_pick"] == EVENT_A
    assert state.attributes["color_overrides"] == {EVENT_B: ["#654321"]}


async def test_services_removed_on_unload(hass, freezer):
    freezer.move_to("2026-11-10 12:00:00-06:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_services_unload")

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_SET_TONIGHT_PICK)
    assert not hass.services.has_service(DOMAIN, SERVICE_SET_COLOR_OVERRIDE)
    assert not hass.services.has_service(DOMAIN, SERVICE_RESET_COLOR_OVERRIDE)

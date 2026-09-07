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

    # Migration (version 1 -> 2, Phase 8) turned the one light in
    # ENTRY_DATA's old-shape "lights" list into a real subentry -- the
    # unique_id is keyed on its HA-generated subentry_id, not
    # light_entity, so it can only be known after setup, not hardcoded.
    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    subentry = next(iter(live_entry.subentries.values()))
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"test_entry_{subentry.subentry_id}_schedule"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state not in (None, "unknown", "unavailable")
    assert state.attributes["light_entity"] == "light.front_porch"
    assert "segments" in state.attributes
    assert len(state.attributes["segments"]) >= 1
    # schedule_end_time: the light's configured off-time, exposed for the
    # panel's OFF/DAWN timeline marker -- see coordinator.py's LightSchedule.
    assert state.attributes["schedule_end_time"] == "23:00"
    assert state.attributes["light_name"] == "Front Porch"


async def test_sensor_exposes_light_config_and_override_state(hass):
    """Tonight's Schedule (Plan B) needs the light's own configured values,
    not just their effect on the resolved schedule -- and needs to know
    when a manual override currently owns the light."""
    hass.states.async_set(
        "sun.sun",
        "above_horizon",
        {"next_setting": "2026-12-25T20:00:00+00:00"},
    )
    hass.states.async_set("light.front_porch", "off")

    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_config_attrs")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    subentry = next(iter(live_entry.subentries.values()))
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"test_config_attrs_{subentry.subentry_id}_schedule"
    )
    state = hass.states.get(entity_id)

    assert state.attributes["fade_in"] == 30
    assert state.attributes["fade_out"] == 120
    assert state.attributes["warmwhite_time"] == "22:00"
    assert state.attributes["warmwhite_enabled"] is True
    assert state.attributes["verify_enabled"] is True
    assert state.attributes["verify_off_enabled"] is False  # ENTRY_DATA never set it -- real default
    assert state.attributes["override_source"] is None  # nothing overriding yet

    coordinator = live_entry.runtime_data
    await coordinator.async_fire_force_white("light.front_porch")
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state.attributes["override_source"] == "force_white"


async def test_light_name_attribute_is_the_configured_name_not_the_entity_friendly_name(hass):
    """Regression test for a real bug found live during Phase 10's compact
    card verification: the panel/card used to read the light entity's own
    friendly_name for display, which silently showed the wrong name for
    any light configured with a different name than its underlying
    entity's own name. light_name must reflect what the user actually
    typed into ChromaCal's config, not whatever the light's own
    integration happens to call it."""
    hass.states.async_set(
        "sun.sun",
        "above_horizon",
        {"next_setting": "2026-12-25T20:00:00+00:00"},
    )
    # The entity's own name deliberately differs from ChromaCal's
    # configured name for it -- the exact mismatch that exposed the bug.
    hass.states.async_set("light.kitchen_lights", "off", {"friendly_name": "Kitchen Lights"})

    entry_data = {
        "region": "us",
        "categories": {"federal": True},
        "lights": [
            {
                "name": "Living Room Overhead Lights",
                "zone": "",
                "entity": "light.kitchen_lights",
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
    entry = MockConfigEntry(domain=DOMAIN, data=entry_data, entry_id="test_name_mismatch")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    subentry = next(iter(live_entry.subentries.values()))
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"test_name_mismatch_{subentry.subentry_id}_schedule"
    )
    state = hass.states.get(entity_id)

    assert state.attributes["light_name"] == "Living Room Overhead Lights"


async def test_sensor_falls_back_gracefully_without_sun_entity(hass):
    """No sun.sun entity -> setup still succeeds, sensor still gets a value."""
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_entry_2")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    subentry = next(iter(live_entry.subentries.values()))
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"test_entry_2_{subentry.subentry_id}_schedule"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state not in (None, "unknown", "unavailable")


# ── Upcoming Events (global, not per-light) ──────────────────────────────


async def test_upcoming_events_sensor_created_once_not_per_light(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_upcoming")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, "test_upcoming_upcoming_events")
    assert entity_id is not None
    # Not entity-per-light: only one Upcoming Events sensor exists even
    # though ENTRY_DATA configures one light -- confirmed by construction
    # (unique_id has no light_entity segment), asserted here as behavior.
    assert (
        registry.async_get_entity_id(
            "sensor", DOMAIN, "test_upcoming_light.front_porch_upcoming_events"
        )
        is None
    )


async def test_upcoming_events_sensor_lists_independence_day(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_upcoming_list")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, "test_upcoming_list_upcoming_events")
    state = hass.states.get(entity_id)
    assert state is not None

    assert state.attributes["role"] == "upcoming_events"
    events = state.attributes["events"]
    assert len(events) >= 1

    july4 = next(e for e in events if e["name"] == "Independence Day")
    assert july4["date"] == "2026-07-04"
    assert july4["is_today"] is True
    assert july4["category"] == "federal"
    assert "colors" in july4 and isinstance(july4["colors"], list)

    # Native value: the nearest event's name -- today's, since it's first.
    assert state.state == events[0]["name"]


async def test_upcoming_events_sensor_updates_when_a_permanent_skip_is_set(hass, freezer):
    """Not filtered by skip status -- matches get_upcoming_events()'s own
    contract (an already-skipped event must still appear so there's
    something to build an un-skip control from)."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id="test_upcoming_skip")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = entry.runtime_data
    await coordinator.async_set_permanent_skip("Independence Day", True)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, "test_upcoming_skip_upcoming_events")
    events = hass.states.get(entity_id).attributes["events"]
    assert any(e["name"] == "Independence Day" for e in events)

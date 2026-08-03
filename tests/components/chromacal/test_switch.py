"""Tests for the skip-system switches: permanent skip (static, all enabled
events) and skip-tonight (dynamic, today's candidates only).
"""

from __future__ import annotations

import homeassistant.util.dt as dt_util
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.chromacal.const import CONF_EMERGENCY_WAS_ACTIVE, DOMAIN

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


def _permanent_id(registry, entry_id: str, name: str) -> str | None:
    return registry.async_get_entity_id("switch", DOMAIN, f"{entry_id}_skip_{name}")


def _tonight_id(registry, entry_id: str, name: str) -> str | None:
    return registry.async_get_entity_id("switch", DOMAIN, f"{entry_id}_skip_tonight_{name}")


async def test_permanent_skip_switch_created_for_every_enabled_event(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_permanent_all")

    registry = er.async_get(hass)
    entity_id = _permanent_id(registry, entry.entry_id, "Independence Day")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "off"  # not skipped by default


async def test_toggling_permanent_skip_on_suppresses_the_event(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")  # inside Independence Day's window
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )

    entry = await _setup_entry(hass, "test_permanent_toggle")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.data[LIGHT_ENTITY].current_segment.event.name == "Independence Day"

    registry = er.async_get(hass)
    entity_id = _permanent_id(registry, entry.entry_id, "Independence Day")
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    assert "Independence Day" in coordinator.skipped_events
    assert hass.states.get(entity_id).state == "on"
    assert coordinator.data[LIGHT_ENTITY].current_segment.event.name != "Independence Day"


async def test_permanent_skip_is_reversible(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_permanent_reversible")
    coordinator = entry.runtime_data

    registry = er.async_get(hass)
    entity_id = _permanent_id(registry, entry.entry_id, "Independence Day")

    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert "Independence Day" in coordinator.skipped_events

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert "Independence Day" not in coordinator.skipped_events
    assert hass.states.get(entity_id).state == "off"


async def test_permanent_skip_persists_to_config_entry_options(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_permanent_persist")

    registry = er.async_get(hass)
    entity_id = _permanent_id(registry, entry.entry_id, "Independence Day")
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    assert entry.options.get("skipped_events") == ["Independence Day"]


async def test_permanent_skip_switch_exposes_role_scope_and_event_name(hass, freezer):
    """Regression coverage for the Phase 6 panel work: the frontend groups
    switches by these attributes instead of parsing display names (which a
    user could rename in the UI)."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_permanent_attrs")

    registry = er.async_get(hass)
    entity_id = _permanent_id(registry, entry.entry_id, "Independence Day")
    attrs = hass.states.get(entity_id).attributes
    assert attrs["role"] == "skip"
    assert attrs["scope"] == "permanent"
    assert attrs["event_name"] == "Independence Day"


async def test_tonight_skip_switch_only_exists_for_todays_candidates(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_tonight_scope")

    registry = er.async_get(hass)
    assert _tonight_id(registry, entry.entry_id, "Independence Day") is not None
    assert _tonight_id(registry, entry.entry_id, "Veterans Day") is None  # a different date


async def test_tonight_skip_switch_survives_a_same_day_reload(hass, freezer):
    """Real bug, caught live in the disposable container (2026-08-01, a
    real HA restart + config-entry reload, not a hypothetical): a tonight-
    skip switch's entity-registry entry persists across a reload/restart
    regardless of whether the entity is currently live. The old seeding
    logic treated "already in the registry" as "already added this
    session," so a still-valid candidate that happened to already have a
    registry entry from before the reload never got handed to
    async_add_entities() again -- it silently never came back as a real
    entity, even though the registry still remembered its entity_id.
    """
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_tonight_reload")

    registry = er.async_get(hass)
    entity_id = _tonight_id(registry, entry.entry_id, "Independence Day")
    assert entity_id is not None
    assert hass.states.get(entity_id) is not None  # live before the reload

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    # Same day, same candidate -- must come back as a real, live entity.
    # The broken version doesn't make the entity vanish -- hass.states
    # still returns something for it, just an "unavailable, restored=True"
    # placeholder with none of the switch's own attributes, which reads as
    # a broken entity in the HA UI rather than a cleanly-missing one. Check
    # the actual state and a real attribute, not just "is this None".
    entity_id_after = _tonight_id(registry, entry.entry_id, "Independence Day")
    assert entity_id_after is not None
    state_after = hass.states.get(entity_id_after)
    assert state_after is not None
    assert state_after.state != "unavailable"
    assert state_after.attributes.get("event_name") == "Independence Day"


async def test_tonight_skip_switch_exposes_role_scope_and_event_name(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_tonight_attrs")

    registry = er.async_get(hass)
    entity_id = _tonight_id(registry, entry.entry_id, "Independence Day")
    attrs = hass.states.get(entity_id).attributes
    assert attrs["role"] == "skip"
    assert attrs["scope"] == "tonight"
    assert attrs["event_name"] == "Independence Day"


async def test_toggling_tonight_skip_suppresses_only_tonight_not_permanently(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    entry = await _setup_entry(hass, "test_tonight_toggle")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = _tonight_id(registry, entry.entry_id, "Independence Day")
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    assert "Independence Day" in coordinator.tonight_skips
    assert "Independence Day" not in coordinator.skipped_events  # the permanent list, untouched
    assert coordinator.data[LIGHT_ENTITY].current_segment.event.name != "Independence Day"


async def test_ensure_today_candidates_resets_tonight_skips_on_new_day(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_midnight_reset")
    coordinator = entry.runtime_data
    coordinator.tonight_skips = {"Independence Day"}

    coordinator.ensure_today_candidates(dt_util.now())  # same day -- date guard, no-op
    assert "Independence Day" in coordinator.tonight_skips

    freezer.move_to("2026-07-05 00:01:00-05:00")
    coordinator.ensure_today_candidates(dt_util.now())
    assert coordinator.tonight_skips == set()


async def test_ensure_today_candidates_adds_and_removes_tonight_switches_across_days(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_midnight_switches")
    coordinator = entry.runtime_data

    registry = er.async_get(hass)
    july4_entity = _tonight_id(registry, entry.entry_id, "Independence Day")
    assert july4_entity is not None
    assert hass.states.get(july4_entity) is not None

    freezer.move_to("2026-07-05 00:01:00-05:00")
    coordinator.ensure_today_candidates(dt_util.now())
    await hass.async_block_till_done()

    assert _tonight_id(registry, entry.entry_id, "Independence Day") is None
    assert hass.states.get(july4_entity) is None


# ── Emergency Mode ───────────────────────────────────────────────────


def _emergency_id(registry, entry_id: str) -> str | None:
    return registry.async_get_entity_id("switch", DOMAIN, f"{entry_id}_emergency_mode")


async def test_emergency_switch_is_off_by_default(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_emergency_off_default")

    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    assert entity_id is not None
    assert hass.states.get(entity_id).state == "off"


async def test_emergency_switch_exposes_role(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_emergency_role_attr")

    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    assert hass.states.get(entity_id).attributes["role"] == "emergency_mode"


async def test_turning_on_emergency_fires_immediately_and_reports_on(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_emergency_turn_on")
    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)

    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "on"
    assert entry.runtime_data.emergency_active is True
    assert len(turn_on_calls) == 1  # fired immediately on activation, matching v1
    assert turn_on_calls[0].data["rgb_color"] == [255, 0, 0]  # red-blue pattern, first color

    # Clean up the running interval before the test ends.
    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()


async def test_turning_off_emergency_stops_and_resumes_the_schedule(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_emergency_turn_off")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()  # establishes event:Independence Day
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "off"
    assert coordinator.emergency_active is False
    assert LIGHT_ENTITY not in coordinator._manual_override
    # Last call resumes the real schedule -- back to Independence Day, not
    # left on whatever emergency color happened to fire last.
    assert turn_on_calls[-1].data["rgb_color"] == [220, 20, 60]


async def test_emergency_suppresses_autofire_while_active(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    entry = await _setup_entry(hass, "test_emergency_override")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()

    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    assert coordinator._is_overridden(LIGHT_ENTITY) is True

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert coordinator._is_overridden(LIGHT_ENTITY) is False


async def test_emergency_breadcrumb_flag_tracks_start_and_clean_stop(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_emergency_breadcrumb")
    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)

    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options.get(CONF_EMERGENCY_WAS_ACTIVE) is True

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert entry.options.get(CONF_EMERGENCY_WAS_ACTIVE) is False

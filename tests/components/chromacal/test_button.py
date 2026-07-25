"""Tests for the quick-control button entities: 21 Gun Salute,
Catch Up/Sync, and per-light Force White.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import homeassistant.util.dt as dt_util
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.chromacal.const import DOMAIN

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


def _button_id(registry, entry_id: str, suffix: str) -> str | None:
    return registry.async_get_entity_id("button", DOMAIN, f"{entry_id}{suffix}")


async def test_salute_catchup_stop_and_force_white_buttons_are_created(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_buttons_created")

    registry = er.async_get(hass)
    assert _button_id(registry, entry.entry_id, "_salute") is not None
    assert _button_id(registry, entry.entry_id, "_catch_up_sync") is not None
    assert _button_id(registry, entry.entry_id, "_stop") is not None
    assert _button_id(registry, entry.entry_id, f"_{LIGHT_ENTITY}_force_white") is not None


async def test_global_and_force_white_buttons_expose_role_for_frontend_grouping(hass, freezer):
    """Regression coverage for the Phase 6 panel work: the frontend tells
    the three global buttons apart, and identifies a Force White button's
    light, from these attributes instead of parsing display names."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_button_role_attrs")
    registry = er.async_get(hass)

    salute_id = _button_id(registry, entry.entry_id, "_salute")
    assert hass.states.get(salute_id).attributes["role"] == "salute"

    catch_up_id = _button_id(registry, entry.entry_id, "_catch_up_sync")
    assert hass.states.get(catch_up_id).attributes["role"] == "catch_up_sync"

    stop_id = _button_id(registry, entry.entry_id, "_stop")
    assert hass.states.get(stop_id).attributes["role"] == "stop"

    force_white_id = _button_id(registry, entry.entry_id, f"_{LIGHT_ENTITY}_force_white")
    force_white_attrs = hass.states.get(force_white_id).attributes
    assert force_white_attrs["role"] == "force_white"
    assert force_white_attrs["light_entity"] == LIGHT_ENTITY


# ── Catch Up / Sync ─────────────────────────────────────────────────


async def test_catch_up_bypasses_the_gate_that_normally_blocks_a_redundant_fire(hass, freezer):
    """The core Phase 5b finding: async_refresh() alone does NOT re-fire
    once desired_key already matches _last_fire_key. Catch Up/Sync must.
    """
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_catchup_bypass")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()  # establishes event:Independence Day
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 1

    # Baseline: a plain refresh with nothing changed does NOT refire.
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 1

    # Catch Up/Sync does, even though the gate would otherwise block it.
    await coordinator.async_catch_up()
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 2
    assert turn_on_calls[1].data["entity_id"] == LIGHT_ENTITY
    assert turn_on_calls[1].data["rgb_color"] == [220, 20, 60]  # Independence Day, index 0


async def test_catch_up_button_press_delegates_to_the_coordinator(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_catchup_press")
    registry = er.async_get(hass)
    entity_id = _button_id(registry, entry.entry_id, "_catch_up_sync")

    with patch.object(
        entry.runtime_data, "async_catch_up", new=AsyncMock()
    ) as mock_catch_up:
        await hass.services.async_call("button", "press", {"entity_id": entity_id}, blocking=True)
        await hass.async_block_till_done()

    mock_catch_up.assert_called_once()


# ── Force White ──────────────────────────────────────────────────────


async def test_force_white_uses_the_lights_own_configured_kelvin(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_force_white_kelvin")
    await entry.runtime_data.async_fire_force_white(LIGHT_ENTITY)
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 1
    call = turn_on_calls[0]
    assert call.data["entity_id"] == LIGHT_ENTITY
    assert call.data["color_temp_kelvin"] == 4000  # default warmwhite_kelvin_mireds=250 -> 4000K
    assert call.data["brightness_pct"] == 100


async def test_force_white_suppresses_autofire_for_thirty_minutes(hass, freezer):
    # Start close to warmwhite_time (22:00) so a 15-minute jump both stays
    # inside the 30-minute override window (21:50 + 30m = 22:20) AND crosses
    # a real transition the schedule would otherwise want to fire.
    freezer.move_to("2026-07-04 21:50:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_force_white_suppress")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()  # establishes event:Independence Day
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 1

    await coordinator.async_fire_force_white(LIGHT_ENTITY)
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 2  # the Force White command itself

    # 15 minutes later -- still inside the 30-minute override window, but
    # past warmwhite_time (22:00), so the real schedule would otherwise want
    # to fire warmwhite here; the override must still block it.
    freezer.move_to("2026-07-04 22:05:00-05:00")
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 2  # unchanged -- auto-fire stood down


async def test_force_white_sets_a_thirty_minute_expiry_on_the_override(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = await _setup_entry(hass, "test_force_white_expiry")
    coordinator = entry.runtime_data
    await coordinator.async_fire_force_white(LIGHT_ENTITY)
    await hass.async_block_till_done()

    override = coordinator._manual_override[LIGHT_ENTITY]
    assert override.source == "force_white"
    assert (override.expires_at - dt_util.now()).total_seconds() == 30 * 60


async def test_force_white_resumes_the_real_schedule_when_override_is_cleared(hass, freezer):
    """Doesn't wait on the real 30-minute timer (impractical in a unit
    test, and this project's existing tests don't exercise real timer
    firing elsewhere either -- see async_recheck_color_cycle's tests,
    which call the method directly instead). Simulates what the
    async_call_later callback does -- clear the override, force-fire --
    to verify the resume mechanism itself works.
    """
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_force_white_resume")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()  # event:Independence Day established
    await hass.async_block_till_done()

    await coordinator.async_fire_force_white(LIGHT_ENTITY)
    await hass.async_block_till_done()
    calls_after_force_white = len(turn_on_calls)

    coordinator._manual_override.pop(LIGHT_ENTITY, None)
    await coordinator.async_force_fire([LIGHT_ENTITY])
    await hass.async_block_till_done()

    assert len(turn_on_calls) == calls_after_force_white + 1
    resumed_call = turn_on_calls[-1]
    assert resumed_call.data["rgb_color"] == [220, 20, 60]  # back to Independence Day

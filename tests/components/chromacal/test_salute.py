"""Tests for the 21 Gun Salute sequence.

Patches asyncio.sleep so the ~40-60 real-second sequence completes near-
instantly -- the step *data* (colors, ordering, pace timing) is already
covered Docker-free in tests/scheduling/test_actions.py; what's left to
verify here is coordinator behavior: the re-entry guard, the manual
override lifecycle, and that the schedule actually resumes afterward.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

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


async def test_salute_fires_all_steps_then_resumes_the_schedule(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    turn_off_calls = async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_salute_full_sequence")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()  # establishes event:Independence Day, seeds the gate
    await hass.async_block_till_done()
    turn_on_before = len(turn_on_calls)

    with patch("custom_components.chromacal.coordinator.asyncio.sleep", return_value=None):
        await coordinator.async_fire_salute("standard")
    await hass.async_block_till_done()

    # 3 volleys x (flash + afterglow) + taps = 7 turn_on during the sequence,
    # plus 1 more resuming the real schedule at the end = 8.
    assert len(turn_on_calls) == turn_on_before + 8
    # 2 pauses (between volleys) + 1 fade-out = 3 turn_off.
    assert len(turn_off_calls) == 3

    first_flash = turn_on_calls[turn_on_before]
    assert first_flash.data["rgb_color"] == [255, 255, 255]
    assert first_flash.data["brightness_pct"] == 100

    taps_call = turn_on_calls[turn_on_before + 6]
    assert taps_call.data["rgb_color"] == [255, 147, 41]

    # The very last call is the resume, back to the actual active event.
    resume_call = turn_on_calls[-1]
    assert resume_call.data["rgb_color"] == [220, 20, 60]  # Independence Day, index 0

    # Guard and override both cleaned up afterward.
    assert coordinator.salute_active is False
    assert LIGHT_ENTITY not in coordinator._manual_override


async def test_salute_suppresses_autofire_while_in_progress(hass, freezer):
    """A coordinator refresh landing mid-Salute must not fight it -- this
    is what the manual override set for the whole sequence's duration
    protects against.
    """
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    entry = await _setup_entry(hass, "test_salute_override")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    async def _fake_sleep(_seconds):
        # While "mid-sequence," the light is overridden.
        assert coordinator._is_overridden(LIGHT_ENTITY) is True

    with patch("custom_components.chromacal.coordinator.asyncio.sleep", new=_fake_sleep):
        await coordinator.async_fire_salute("standard")

    # And no longer overridden once the sequence (and its resume) is done.
    assert coordinator._is_overridden(LIGHT_ENTITY) is False


async def test_salute_button_running_attribute_tracks_state(hass, freezer):
    """Regression test: async_fire_salute() mutated salute_active without
    ever calling async_update_listeners(), so the button's `running`
    attribute (which reads salute_active) never actually got re-published
    to HA's state machine. Caught during the Phase 5b listener-
    notification audit, not by the original test suite. The button is no
    longer marked unavailable while running (see the multi-source cancel/
    Stop plan discussion -- a second press is now meaningful, not
    something to grey out), so this checks the attribute instead.
    """
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = await _setup_entry(hass, "test_salute_button_running_attr")
    coordinator = entry.runtime_data
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_salute")

    assert hass.states.get(entity_id).attributes["running"] is False

    async def _fake_sleep(_seconds):
        assert hass.states.get(entity_id).attributes["running"] is True

    with patch("custom_components.chromacal.coordinator.asyncio.sleep", new=_fake_sleep):
        await coordinator.async_fire_salute("standard")
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).attributes["running"] is False


async def test_toggle_salute_button_press_delegates_to_the_coordinator(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_salute_button_press")
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_salute")

    with patch.object(
        entry.runtime_data, "async_toggle_salute", new=AsyncMock()
    ) as mock_toggle:
        await hass.services.async_call("button", "press", {"entity_id": entity_id}, blocking=True)
        await hass.async_block_till_done()

    mock_toggle.assert_called_once()

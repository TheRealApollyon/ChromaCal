"""Tests for the coordinator's auto-fire behavior: does it actually call
light.turn_on/turn_off when the desired state changes?

Uses frozen time (the `freezer` fixture from pytest-freezer, bundled with
pytest-homeassistant-custom-component) so desired-key transitions are
deterministic instead of depending on real wall-clock time passing between
assertions.
"""

from __future__ import annotations

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


async def test_first_refresh_observes_without_firing(hass, freezer):
    """First-update guard: the very first coordinator refresh never fires."""
    freezer.move_to("2026-07-23 12:00:00-05:00")  # midday -- clearly 'pre'
    # pytest-homeassistant-custom-component's default test hass isn't
    # America/Chicago (observed Pacific in an earlier failed run) -- pin it
    # explicitly so the "-05:00" in frozen times above lands where the test
    # actually intends, not wherever the harness defaults to.
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    turn_off_calls = async_mock_service(hass, "light", "turn_off")

    await _setup_entry(hass, "test_observe_only")

    assert len(turn_on_calls) == 0
    assert len(turn_off_calls) == 0


async def test_auto_fire_transitions_from_pre_to_off(hass, freezer):
    """A real pre -> off transition across two refreshes fires turn_off
    with the light's configured fade_out transition."""
    freezer.move_to("2026-07-23 12:00:00-05:00")  # 'pre' -- seeds observing
    await hass.config.async_set_time_zone("America/Chicago")
    turn_off_calls = async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_pre_to_off")
    assert len(turn_off_calls) == 0

    freezer.move_to("2026-07-23 23:30:00-05:00")  # past end_time (23:00) -> 'off'
    coordinator = entry.runtime_data
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert len(turn_off_calls) == 1
    call = turn_off_calls[0]
    assert call.data["entity_id"] == LIGHT_ENTITY
    assert call.data["transition"] == 120  # fade_out


async def test_auto_fire_sends_the_correct_event_color_command(hass, freezer):
    """A stable 'event:X' key still fires once, with the right color/
    brightness/transition, on the refresh after the observing one -- the
    sentinel '__init__' seeded on first refresh never equals a real key.
    """
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_event_color")
    assert len(turn_on_calls) == 0  # first refresh: observe only

    # Pin sun.sun to a controlled value now that setup has settled (chromacal
    # depends on "sun", so during setup the real sun component computes and
    # writes its own astronomical value for whatever lat/long the test
    # harness defaults to -- setting the override any earlier just gets
    # clobbered). Also reset the coordinator's own once-per-day cache fields
    # directly, since otherwise they'd keep whatever the first refresh
    # already cached rather than re-reading this override. next_setting =
    # tomorrow 20:00 CDT: hoursUntil from 21:00 today is ~23h (>2), so
    # resolve_sunset_hour() uses it directly -> sunset_hour = 20.0 exactly,
    # hand-verified below.
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 1
    call = turn_on_calls[0]
    assert call.data["entity_id"] == LIGHT_ENTITY
    # Independence Day's first color, #DC143C -> (220, 20, 60)
    assert call.data["rgb_color"] == [220, 20, 60]
    assert call.data["brightness"] == 255
    assert call.data["transition"] == 30  # fade_in

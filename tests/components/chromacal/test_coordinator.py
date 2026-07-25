"""Tests for the coordinator's auto-fire behavior: does it actually call
light.turn_on/turn_off when the desired state changes?

Uses frozen time (the `freezer` fixture from pytest-freezer, bundled with
pytest-homeassistant-custom-component) so desired-key transitions are
deterministic instead of depending on real wall-clock time passing between
assertions.
"""

from __future__ import annotations

import logging
from unittest.mock import patch

import homeassistant.util.dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.chromacal.const import DOMAIN
from custom_components.chromacal.scheduling.fire import build_fire_command as real_build_fire_command

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


async def test_color_cycle_advances_on_recheck_after_a_minute_boundary(hass, freezer):
    """The ~60s color-cycle recheck re-fires with the next color once
    elapsed time crosses a new minute-of-cycle, without needing the coarse
    key itself to change (that's the Phase 4c gap this closes)."""
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_color_cycle_advance")
    assert len(turn_on_calls) == 0  # first refresh: observe only

    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None

    await coordinator.async_refresh()  # establishes event:Independence Day, fires index 0
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 1
    assert turn_on_calls[0].data["rgb_color"] == [220, 20, 60]  # #DC143C, index 0

    # Segment starts at sunset_hour=20.0. A 1-minute jump is enough: at
    # 21:01:30, elapsed = 61.5 minutes -> int(61.5) % 3 = 61 % 3 = 1 ->
    # second color, #FFFFFF -> (255, 255, 255). Deliberately NOT a large
    # jump -- crossing into warmwhite_time (22:00) would trip the coarse
    # gate's own transition instead of (or in addition to) this recheck,
    # which is a different code path than what this test is isolating.
    # Also deliberately NOT exactly 21:01:00 (61.0 minutes on the nose) --
    # that lands on the same float-precision boundary flagged in
    # test_fire.py (1/60*3600 can round to 59.999...), which would make
    # this test flake on the exact same class of bug, not a real one.
    freezer.move_to("2026-07-04 21:01:30-05:00")
    await coordinator.async_recheck_color_cycle(dt_util.now())
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 2
    call = turn_on_calls[1]
    assert call.data["entity_id"] == LIGHT_ENTITY
    assert call.data["rgb_color"] == [255, 255, 255]
    assert call.data["brightness"] == 255
    assert call.data["transition"] == 30


async def test_color_cycle_recheck_does_not_refire_the_same_color(hass, freezer):
    """Calling the recheck again with no elapsed-time change fires nothing
    extra -- this is what stops it from refiring on every coordinator tick
    regardless of whether the color actually changed."""
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_color_cycle_no_advance")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None

    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert len(turn_on_calls) == 1

    # Same frozen "now" as the fire above -- same color index.
    await coordinator.async_recheck_color_cycle(dt_util.now())
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 1


# ── async_force_fire per-light exception isolation ──────────────────

_TWO_LIGHT_ENTRY_DATA = {
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
        },
        {
            "name": "Back Yard",
            "zone": "",
            "entity": "light.back_yard",
            "start_type": "sunset",
            "start_time": "19:00",
            "end_type": "time",
            "end_time": "23:00",
            "fade_in": 30,
            "fade_out": 120,
            "warmwhite_time": "22:00",
            "warmwhite_enabled": True,
        },
    ],
}


def _broken_build_fire_command(key, light, segments, now):
    """Simulates a real resolution failure for exactly one light, so the
    other light's resolution/fire path can be observed independently."""
    if light.name == "Back Yard":
        raise RuntimeError("boom -- simulated resolution failure")
    return real_build_fire_command(key, light, segments, now)


async def test_force_fire_one_lights_failure_does_not_block_the_others(hass, freezer, caplog):
    """Regression test for a real gap found during the Phase 5b cancel/
    Stop bug investigation: async_force_fire's per-light loop had no
    exception isolation, so a failure resolving ANY one light silently
    aborted the fire for every other configured light too.
    """
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = MockConfigEntry(domain=DOMAIN, data=_TWO_LIGHT_ENTRY_DATA, entry_id="test_force_fire_isolation")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None

    with (
        patch(
            "custom_components.chromacal.coordinator.build_fire_command",
            side_effect=_broken_build_fire_command,
        ),
        caplog.at_level(logging.ERROR),
    ):
        await coordinator.async_force_fire()

    # Front Porch still got its real fire -- one light's failure didn't
    # block the other.
    fired_entities = {call.data["entity_id"] for call in turn_on_calls}
    assert "light.front_porch" in fired_entities
    assert "light.back_yard" not in fired_entities

    # And the failure was logged loudly, not silently -- mentions the
    # specific light that failed.
    error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("light.back_yard" in r.getMessage() for r in error_records)
    assert any("force-fire failed" in r.getMessage() for r in error_records)

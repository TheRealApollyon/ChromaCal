"""Tests for sunset-synced fade-in: does the coordinator actually fire the
warm-white ramp sunset_fade_offset_min minutes before sunset when a light
opts in, and leave every other light's behavior completely unaffected when
it doesn't?

Real finding while writing these: bridge.py's build_light_config() always
hardcodes start_offset=0 (not collected by any config flow yet), which
means color_start_h == approx_sunset_h for every real, coordinator-driven
light today -- the old 'warmup' key's window ([sunset, color_start_h)) is
therefore ALWAYS EMPTY in practice, never actually reachable through the
real setup path (only via engine.py's own unit tests, which construct
LightConfig directly with a nonzero start_offset). sunset_fade's window
([sunset - offset, color_start_h) == [sunset - offset, sunset)) is NOT
empty even at start_offset=0, so it's a genuinely new firing window for
every real light, not something that only kicks in alongside start_offset.
"""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.chromacal.const import DOMAIN

FRONT_ENTITY = "light.front_porch"

BASE_LIGHT = {
    "name": "Front Porch",
    "zone": "",
    "entity": FRONT_ENTITY,
    "start_type": "sunset",
    "start_time": "19:00",
    "end_type": "time",
    "end_time": "23:00",
    "fade_in": 30,
    "fade_out": 120,
    "warmwhite_time": "22:00",
    "warmwhite_enabled": True,
}


async def _setup_entry(hass, entry_id: str, light_overrides: dict) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "region": "us",
            "categories": {"federal": True},
            "lights": [{**BASE_LIGHT, **light_overrides}],
        },
        entry_id=entry_id,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _pin_sunset_to_20h(hass, coordinator) -> None:
    """next_setting -> sunset_hour = 20.0 exactly -- same derivation
    test_coordinator.py's own event-color test hand-verifies (America/
    Chicago, hours_until > 2 so resolve_sunset_hour uses next_setting
    directly)."""
    hass.states.async_set("sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"})
    coordinator.sunset_hour = None
    coordinator.sunset_date = None


async def test_sunset_fade_disabled_fires_nothing_before_sunset(hass, freezer):
    """Regression guard: a light that never opts in does exactly what it
    always has in the (previously always-empty, now still-empty-for-it)
    pre-sunset window -- no fire, same as before this feature existed."""
    freezer.move_to("2026-07-04 12:00:00-05:00")  # 'pre' -- seeds observing
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_sunset_fade_disabled", {})
    coordinator = entry.runtime_data
    _pin_sunset_to_20h(hass, coordinator)

    freezer.move_to("2026-07-04 19:45:00-05:00")  # 15 min before sunset
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 0


async def test_sunset_fade_enabled_fires_the_ramp_before_sunset(hass, freezer):
    """The real replacement behavior: fires sunset_fade_offset_min minutes
    before sunset, with the configured duration as the transition."""
    freezer.move_to("2026-07-04 12:00:00-05:00")  # 'pre' -- seeds observing
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(
        hass,
        "test_sunset_fade_enabled",
        {
            "sunset_fade_enabled": True,
            "sunset_fade_offset_min": 30,
            "sunset_fade_duration_sec": 1800,
        },
    )
    coordinator = entry.runtime_data
    _pin_sunset_to_20h(hass, coordinator)

    freezer.move_to("2026-07-04 19:45:00-05:00")  # 15 min into the 19:30 fade window
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 1
    call = turn_on_calls[0]
    assert call.data["entity_id"] == FRONT_ENTITY
    assert call.data["color_temp_kelvin"] == 4000  # default 250 mireds
    assert call.data["brightness"] == 255
    assert call.data["transition"] == 1800  # the configured duration, not fade_in


async def test_sunset_fade_enabled_still_fires_nothing_before_its_own_window(hass, freezer):
    """A light with sunset_fade_enabled still observes 'pre' correctly
    before (sunset - offset) -- the feature narrows the no-op window, it
    doesn't eliminate it."""
    freezer.move_to("2026-07-04 12:00:00-05:00")  # 'pre' -- seeds observing
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(
        hass,
        "test_sunset_fade_still_pre",
        {"sunset_fade_enabled": True, "sunset_fade_offset_min": 30},
    )
    coordinator = entry.runtime_data
    _pin_sunset_to_20h(hass, coordinator)

    freezer.move_to("2026-07-04 19:15:00-05:00")  # 15 min before the 19:30 fade window
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert len(turn_on_calls) == 0

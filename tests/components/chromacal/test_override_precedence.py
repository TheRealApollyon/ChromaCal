"""Tests spanning more than one override source -- Salute, Emergency Mode,
and Force White -- that don't belong neatly in any single feature's own
test file: precedence between sources, the ownership-tracking fix that
prevents one source's cleanup from clearing a different source's still-
active override, and the global Stop button that cancels whichever of the
three is currently active.
"""

from __future__ import annotations

import asyncio
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


def _emergency_id(registry, entry_id: str) -> str | None:
    return registry.async_get_entity_id("switch", DOMAIN, f"{entry_id}_emergency_mode")


# Captured before any patching -- patching
# "custom_components.chromacal.coordinator.asyncio.sleep" patches the
# asyncio module's `sleep` attribute itself (coordinator.py's `import
# asyncio` and this file's are the same shared module object), so calling
# asyncio.sleep from inside the replacement function would recurse into
# itself. This alias sidesteps that.
_real_sleep = asyncio.sleep


async def _real_short_sleep(_seconds: float) -> None:
    # Used in place of asyncio.sleep inside a running Salute so it
    # genuinely suspends and resumes on the test's real event loop --
    # needed here (unlike test_salute.py's return_value=None patches)
    # because these tests need the task to still be mid-sequence when a
    # second, concurrent action (cancel, Emergency starting) happens.
    #
    # delay=0, not a real nonzero duration: freezegun's `freezer` fixture
    # defaults real_asyncio=False (confirmed in freezegun's own source),
    # which freezes the event loop's own monotonic clock along with
    # wall-clock time -- any asyncio.sleep(n>0) would schedule a
    # loop.call_later() callback that never fires, hanging forever, not
    # just here but for real production timers too if this were ever
    # copied elsewhere. asyncio.sleep(0) is a genuinely different code
    # path (a bare yield, not a clock-scheduled callback -- confirmed in
    # asyncio's own source), so it still suspends and resumes the task
    # for real without touching the clock at all.
    await _real_sleep(0)


async def _yield_to_event_loop(times: int = 20) -> None:
    """Let a concurrently-running task (e.g. a just-started Salute)
    advance for a bit before the test proceeds. Not hass.async_block_
    till_done() -- that would wait for the task to fully *finish*, which
    defeats testing "mid-sequence" behavior entirely. Plain repeated
    zero-delay yields instead, for the same frozen-clock reason
    _real_short_sleep uses delay=0.
    """
    for _ in range(times):
        await _real_sleep(0)


# ── Emergency vs. Salute precedence ─────────────────────────────────


async def test_emergency_starting_cancels_a_running_salute(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    async_mock_service(hass, "light", "turn_on")
    async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_emergency_cancels_salute")
    coordinator = entry.runtime_data

    with patch("custom_components.chromacal.coordinator.asyncio.sleep", new=_real_short_sleep):
        await coordinator.async_toggle_salute("standard")
        assert coordinator.salute_active is True
        await _yield_to_event_loop()  # let it get partway through the sequence

        registry = er.async_get(hass)
        entity_id = _emergency_id(registry, entry.entry_id)
        await hass.services.async_call(
            "switch", "turn_on", {"entity_id": entity_id}, blocking=True
        )
        await hass.async_block_till_done()

    assert coordinator.salute_active is False  # Emergency preempted it
    assert coordinator.emergency_active is True
    assert coordinator._manual_override[LIGHT_ENTITY].source == "emergency"

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()


async def test_salute_declines_while_emergency_is_active(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_salute_declines_emergency")
    coordinator = entry.runtime_data
    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    calls_before = len(turn_on_calls)

    await coordinator.async_toggle_salute("standard")
    await hass.async_block_till_done()

    assert coordinator.salute_active is False  # declined, never started
    assert len(turn_on_calls) == calls_before  # no salute sequence fired

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()


# ── Ownership regression ────────────────────────────────────────────


async def test_force_white_resume_does_not_clear_emergencys_override(hass, freezer):
    """The bug this phase's ownership fix closes: a source's own cleanup
    must not clear a DIFFERENT source's override if that source took over
    the same light in the meantime. Confirmed as a real, reachable gap
    before this fix, not hypothetical -- see the plan discussion.
    """
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_on")
    async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_ownership_regression")
    coordinator = entry.runtime_data

    await coordinator.async_fire_force_white(LIGHT_ENTITY)
    await hass.async_block_till_done()
    assert coordinator._manual_override[LIGHT_ENTITY].source == "force_white"

    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert coordinator._manual_override[LIGHT_ENTITY].source == "emergency"

    # Force White's own resume timer firing now (simulated directly --
    # same reasoning as test_button.py's Force White resume test: waiting
    # on the real 30-minute async_call_later isn't practical).
    coordinator._clear_override_if_owned(LIGHT_ENTITY, "force_white")

    # Emergency's override must survive this -- the actual regression.
    assert coordinator._manual_override[LIGHT_ENTITY].source == "emergency"
    assert coordinator.emergency_active is True

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()


# ── Stop button ──────────────────────────────────────────────────────


async def test_stop_cancels_a_running_salute(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_stop_cancels_salute")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    with patch("custom_components.chromacal.coordinator.asyncio.sleep", new=_real_short_sleep):
        await coordinator.async_toggle_salute("standard")
        assert coordinator.salute_active is True
        await _yield_to_event_loop()

        await coordinator.async_stop_all_overrides()

    assert coordinator.salute_active is False
    assert LIGHT_ENTITY not in coordinator._manual_override
    assert turn_on_calls[-1].data["rgb_color"] == [220, 20, 60]  # resumed


async def test_stop_cancels_active_emergency_mode(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_stop_cancels_emergency")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)
    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert coordinator.emergency_active is True

    await coordinator.async_stop_all_overrides()
    await hass.async_block_till_done()

    assert coordinator.emergency_active is False
    assert hass.states.get(entity_id).state == "off"
    assert LIGHT_ENTITY not in coordinator._manual_override
    assert turn_on_calls[-1].data["rgb_color"] == [220, 20, 60]


async def test_stop_clears_an_active_force_white_override(hass, freezer):
    freezer.move_to("2026-07-04 21:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    hass.states.async_set(
        "sun.sun", "below_horizon", {"next_setting": "2026-07-06T01:00:00+00:00"}
    )
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_stop_clears_force_white")
    coordinator = entry.runtime_data
    coordinator.sunset_hour = None
    coordinator.sunset_date = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    await coordinator.async_fire_force_white(LIGHT_ENTITY)
    await hass.async_block_till_done()
    assert LIGHT_ENTITY in coordinator._manual_override

    await coordinator.async_stop_all_overrides()
    await hass.async_block_till_done()

    assert LIGHT_ENTITY not in coordinator._manual_override
    assert turn_on_calls[-1].data["rgb_color"] == [220, 20, 60]


async def test_stop_is_a_true_noop_when_nothing_is_overridden(hass, freezer):
    """Directly proves the safe-no-op requirement: zero light service
    calls actually reached HA's service execution layer, not just "no
    exception raised". async_mock_service registers the real interception
    point HA's ServiceRegistry dispatches through -- patching
    hass.services.async_call directly isn't possible (it's a read-only
    attribute on ServiceRegistry), so this is the correct tool, not a
    weaker substitute for it.
    """
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    turn_off_calls = async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_stop_noop")
    coordinator = entry.runtime_data
    assert coordinator.salute_active is False
    assert coordinator.emergency_active is False
    assert coordinator._manual_override == {}

    await coordinator.async_stop_all_overrides()
    await hass.async_block_till_done()

    assert turn_on_calls == []
    assert turn_off_calls == []


async def test_stop_button_entity_delegates_to_the_coordinator(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_stop_button_press")
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_stop")
    assert entity_id is not None

    with patch.object(
        entry.runtime_data, "async_stop_all_overrides", new=AsyncMock()
    ) as mock_stop:
        await hass.services.async_call("button", "press", {"entity_id": entity_id}, blocking=True)
        await hass.async_block_till_done()

    mock_stop.assert_called_once()


# ── Entity state vs. physical light during 'pre'/'warmup' ───────────
#
# Deliberate decision, not a bug: cancelling during 'pre'/'warmup' leaves
# the physical light on the override's last state, since 'pre' means "do
# nothing, an existing automation handles this phase" -- see ROADMAP.md.
# What actually matters is that the *entity* state (the button's `running`
# attribute, the switch's `is_on`) still flips to stopped/off correctly
# and immediately, regardless of whether the resume produces a visible
# light change. These tests prove that specifically, at a frozen 'pre'
# time (noon), where async_force_fire's resume is a guaranteed no-op.


async def test_salute_button_running_flips_false_even_when_resume_is_a_noop(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")  # noon -- guaranteed 'pre'
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")
    turn_off_calls = async_mock_service(hass, "light", "turn_off")

    entry = await _setup_entry(hass, "test_salute_running_flips_during_pre")
    coordinator = entry.runtime_data
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_salute")

    with patch("custom_components.chromacal.coordinator.asyncio.sleep", new=_real_short_sleep):
        await coordinator.async_toggle_salute("standard")
        assert coordinator.salute_active is True
        assert hass.states.get(entity_id).attributes["running"] is True
        await _yield_to_event_loop()

        # The Salute's own in-sequence colors DID fire (it bypasses 'pre'
        # gating by design) -- confirms this isn't a no-op test by accident.
        calls_during_sequence = len(turn_on_calls) + len(turn_off_calls)
        assert calls_during_sequence > 0

        await coordinator.async_toggle_salute("standard")  # cancel

    # Entity state flipped correctly...
    assert coordinator.salute_active is False
    assert hass.states.get(entity_id).attributes["running"] is False
    # ...even though the resume itself was a guaranteed no-op: no NEW
    # light call beyond what the Salute sequence itself already fired.
    assert len(turn_on_calls) + len(turn_off_calls) == calls_during_sequence


async def test_emergency_switch_is_on_flips_false_even_when_resume_is_a_noop(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")  # noon -- guaranteed 'pre'
    await hass.config.async_set_time_zone("America/Chicago")
    turn_on_calls = async_mock_service(hass, "light", "turn_on")

    entry = await _setup_entry(hass, "test_emergency_off_flips_during_pre")
    coordinator = entry.runtime_data
    registry = er.async_get(hass)
    entity_id = _emergency_id(registry, entry.entry_id)

    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "on"
    calls_during_emergency = len(turn_on_calls)
    assert calls_during_emergency > 0  # Emergency's own colors fired, bypassing 'pre' too

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    await hass.async_block_till_done()

    # Entity state flipped correctly...
    assert coordinator.emergency_active is False
    assert hass.states.get(entity_id).state == "off"
    # ...even though the resume itself was a guaranteed no-op.
    assert len(turn_on_calls) == calls_during_emergency

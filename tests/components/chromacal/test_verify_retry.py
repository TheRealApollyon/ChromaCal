"""Tests for verify-and-retry (Plan A): after firing a real on/off
transition, does the coordinator actually confirm the light reports the
intended state, retry on a mismatch, and notify if it never resolves?

Follows this project's own established convention for timer-based logic
(see test_button.py's test_force_white_resumes_the_real_schedule_when_
override_is_cleared): doesn't wait on real async_call_later delays --
calls the underlying methods (_call_fire_command_verified, _run_verify_
check) directly to test the mechanism itself, the same way Force White's
own resume timer is tested.
"""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.chromacal.const import DOMAIN
from custom_components.chromacal.scheduling.fire import FireCommand

FRONT_ENTITY = "light.front_porch"
BACK_ENTITY = "light.back_yard"

ENTRY_DATA = {
    "region": "us",
    "categories": {"federal": True},
    "lights": [
        {
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
            "verify_enabled": True,
            "verify_retry_count": 2,
            "verify_check_delay": 180,
        },
        {
            "name": "Back Yard",
            "zone": "",
            "entity": BACK_ENTITY,
            "start_type": "sunset",
            "start_time": "19:00",
            "end_type": "time",
            "end_time": "23:00",
            "fade_in": 30,
            "fade_out": 120,
            "warmwhite_time": "22:00",
            "warmwhite_enabled": True,
            "verify_enabled": True,
            "verify_retry_count": 2,
            "verify_check_delay": 180,
        },
    ],
}

OFF_COMMAND = FireCommand("light", "turn_off", {"transition": 120})


async def _setup_entry(hass, entry_id: str) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id=entry_id)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_verify_disabled_never_schedules_a_check(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_disabled")
    coordinator = entry.runtime_data

    light = replace(coordinator.light_config_for(FRONT_ENTITY), verify_enabled=False)

    await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "off", OFF_COMMAND)

    assert coordinator.verify_state_for(FRONT_ENTITY) is None
    assert FRONT_ENTITY not in coordinator._verify_pending_unsub


async def test_verify_enabled_records_pending_immediately_after_firing(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_pending")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)

    await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "off", OFF_COMMAND)

    state = coordinator.verify_state_for(FRONT_ENTITY)
    assert state is not None
    assert state.result == "pending"
    assert FRONT_ENTITY in coordinator._verify_pending_unsub


async def test_matching_state_records_ok_and_dismisses_notification(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_verify_ok")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    hass.states.async_set(FRONT_ENTITY, "off")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_dismiss"
    ) as mock_dismiss:
        await coordinator._run_verify_check(FRONT_ENTITY, light, OFF_COMMAND, attempts_left=2)

    mock_dismiss.assert_called_once_with(hass, f"{DOMAIN}_verify_{FRONT_ENTITY}")
    state = coordinator.verify_state_for(FRONT_ENTITY)
    assert state.result == "ok"
    assert state.attempts_used == 0


async def test_mismatch_with_attempts_left_retries_with_short_transition(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    turn_off_calls = async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_retry")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    hass.states.async_set(FRONT_ENTITY, "on")  # still on -- doesn't match the off command

    await coordinator._run_verify_check(FRONT_ENTITY, light, OFF_COMMAND, attempts_left=2)

    # Retried with the short transition, not the original 120s fade.
    assert len(turn_off_calls) == 1
    assert turn_off_calls[0].data["transition"] == 5

    state = coordinator.verify_state_for(FRONT_ENTITY)
    assert state.result == "pending"  # not resolved yet -- another check is scheduled
    assert FRONT_ENTITY in coordinator._verify_pending_unsub


async def test_mismatch_with_no_attempts_left_notifies_and_records_failed(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_failed")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    hass.states.async_set(FRONT_ENTITY, "on")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_check(FRONT_ENTITY, light, OFF_COMMAND, attempts_left=0)

    mock_notify.assert_called_once()
    kwargs = mock_notify.call_args.kwargs
    message = mock_notify.call_args.args[1]
    assert "Front Porch" in message
    assert "off" in message
    assert kwargs["notification_id"] == f"{DOMAIN}_verify_{FRONT_ENTITY}"

    state = coordinator.verify_state_for(FRONT_ENTITY)
    assert state.result == "failed"


async def test_two_lights_verify_state_never_collides(hass, freezer):
    """Real concern with multiple configured lights: one light's verify
    outcome must never leak into or overwrite another's."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_two_lights")
    coordinator = entry.runtime_data
    front_light = coordinator.light_config_for(FRONT_ENTITY)
    back_light = coordinator.light_config_for(BACK_ENTITY)

    hass.states.async_set(FRONT_ENTITY, "off")  # matches -- will be "ok"
    hass.states.async_set(BACK_ENTITY, "on")  # mismatch -- will stay "pending"

    await coordinator._run_verify_check(FRONT_ENTITY, front_light, OFF_COMMAND, attempts_left=2)
    await coordinator._run_verify_check(BACK_ENTITY, back_light, OFF_COMMAND, attempts_left=2)

    front_state = coordinator.verify_state_for(FRONT_ENTITY)
    back_state = coordinator.verify_state_for(BACK_ENTITY)
    assert front_state.result == "ok"
    assert back_state.result == "pending"
    assert FRONT_ENTITY not in coordinator._verify_pending_unsub  # resolved, nothing pending
    assert BACK_ENTITY in coordinator._verify_pending_unsub  # still retrying


async def test_a_new_fire_cancels_a_still_pending_verify_chain_for_the_same_light(hass, freezer):
    """If a later schedule transition fires for this light before its
    previous verify chain finished, only the newest chain should stay
    live -- otherwise two overlapping chains could double-retry and one
    could report a stale result over the other's."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_cancel_pending")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)

    with patch("custom_components.chromacal.coordinator.async_call_later") as mock_call_later:
        first_unsub = MagicMock()
        mock_call_later.return_value = first_unsub
        await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "off", OFF_COMMAND)
        first_unsub.assert_not_called()

        second_unsub = MagicMock()
        mock_call_later.return_value = second_unsub
        await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "off", OFF_COMMAND)

    first_unsub.assert_called_once()
    second_unsub.assert_not_called()
    assert coordinator._verify_pending_unsub[FRONT_ENTITY] is second_unsub


async def test_auto_fire_actually_schedules_verification(hass, freezer):
    """Confirms the real call-site wiring, not just the wrapper in
    isolation -- a genuine schedule-driven off transition through
    _auto_fire ends up with a pending verify check, the same as calling
    _call_fire_command_verified directly."""
    freezer.move_to("2026-07-23 12:00:00-05:00")  # 'pre' -- seeds observing
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_via_auto_fire")
    coordinator = entry.runtime_data

    freezer.move_to("2026-07-23 23:30:00-05:00")  # past end_time -> 'off'
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    state = coordinator.verify_state_for(FRONT_ENTITY)
    assert state is not None
    assert state.result == "pending"

"""Tests for Verify Off (a fixed clock-time check-and-notify, distinct
from Plan A's verify-and-retry): does the coordinator actually schedule
the check at schedule_end_time + 30 minutes, read the light's real state,
notify on both outcomes (not just failure), skip cleanly when a manual
override owns the light, and cancel a stale pending check on a new fire?

Same convention as test_verify_retry.py: doesn't wait on real
async_call_later delays -- calls the underlying methods directly.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from unittest.mock import MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.chromacal.const import DOMAIN
from custom_components.chromacal.coordinator import ManualOverride
from custom_components.chromacal.scheduling.fire import FireCommand

FRONT_ENTITY = "light.front_porch"

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
            "verify_enabled": False,  # isolates Verify Off's own scheduling
            "verify_off_enabled": True,
        }
    ],
}

OFF_COMMAND = FireCommand("light", "turn_off", {"transition": 120})


async def _setup_entry(hass, entry_id: str) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id=entry_id)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_verify_off_disabled_never_schedules_a_check(hass, freezer):
    freezer.move_to("2026-07-04 23:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_off_disabled")
    coordinator = entry.runtime_data
    light = replace(coordinator.light_config_for(FRONT_ENTITY), verify_off_enabled=False)

    await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "off", OFF_COMMAND)

    assert FRONT_ENTITY not in coordinator._verify_off_pending_unsub


async def test_verify_off_only_schedules_on_the_off_key(hass, freezer):
    """A non-'off' fire (e.g. warmwhite) must not arm a Verify Off check --
    it's a fixed off-time check, not a generic post-fire one."""
    freezer.move_to("2026-07-04 22:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_on")
    entry = await _setup_entry(hass, "test_verify_off_wrong_key")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    warmwhite_command = FireCommand("light", "turn_on", {"color_temp_kelvin": 4000, "brightness": 255})

    await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "warmwhite", warmwhite_command)

    assert FRONT_ENTITY not in coordinator._verify_off_pending_unsub


async def test_off_fire_schedules_a_check_thirty_minutes_after_schedule_end(hass, freezer):
    freezer.move_to("2026-07-04 23:00:00-05:00")  # exactly the light's configured end_time
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_off_delay")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)

    with patch(
        "custom_components.chromacal.coordinator.async_call_later"
    ) as mock_call_later:
        mock_call_later.return_value = MagicMock()
        await coordinator._call_fire_command_verified(FRONT_ENTITY, light, "off", OFF_COMMAND)

    mock_call_later.assert_called_once()
    delay = mock_call_later.call_args.args[1]
    assert delay == timedelta(minutes=30).total_seconds()
    assert FRONT_ENTITY in coordinator._verify_off_pending_unsub


async def test_check_confirms_off_sends_success_notification(hass, freezer):
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_verify_off_success")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    hass.states.async_set(FRONT_ENTITY, "off")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_called_once()
    message = mock_notify.call_args.args[1]
    kwargs = mock_notify.call_args.kwargs
    assert "Front Porch" in message
    assert "confirmed off" in message
    assert kwargs["notification_id"] == f"{DOMAIN}_verify_off_{FRONT_ENTITY}"
    assert "Confirmed Off" in kwargs["title"]


async def test_success_notifies_by_default_matching_todays_real_behavior(hass, freezer):
    """verify_off_notify_on_success defaults to True -- explicit regression
    guard that today's real behavior (both outcomes notify) doesn't change
    for a light that never touches this new field."""
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_verify_off_success_default_unchanged")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    assert light.verify_off_notify_on_success is True  # the default itself
    hass.states.async_set(FRONT_ENTITY, "off")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_called_once()


async def test_success_is_silent_when_notify_on_success_is_false(hass, freezer):
    """The new toggle's actual gate: persistent_notification and any
    configured notify service both stay silent on a successful check --
    no "all clear" noise anywhere, dashboard or phone."""
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    notify_calls = async_mock_service(hass, "notify", "mobile_app_test_phone")
    entry = await _setup_entry(hass, "test_verify_off_success_silenced")
    coordinator = entry.runtime_data
    light = replace(
        coordinator.light_config_for(FRONT_ENTITY),
        verify_off_notify_on_success=False,
        verify_off_notify_service="notify.mobile_app_test_phone",
    )
    hass.states.async_set(FRONT_ENTITY, "off")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_not_called()
    assert len(notify_calls) == 0


async def test_failure_still_notifies_even_when_notify_on_success_is_false(hass, freezer):
    """The toggle only ever gates the success path -- a failure must
    always get through, regardless of this setting."""
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_verify_off_failure_ignores_toggle")
    coordinator = entry.runtime_data
    light = replace(coordinator.light_config_for(FRONT_ENTITY), verify_off_notify_on_success=False)
    hass.states.async_set(FRONT_ENTITY, "on")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_called_once()


async def test_check_finds_still_on_sends_failure_notification_and_notify_service(hass, freezer):
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    notify_calls = async_mock_service(hass, "notify", "mobile_app_test_phone")
    entry = await _setup_entry(hass, "test_verify_off_failure")
    coordinator = entry.runtime_data
    light = replace(
        coordinator.light_config_for(FRONT_ENTITY),
        verify_off_notify_service="notify.mobile_app_test_phone",
    )
    hass.states.async_set(FRONT_ENTITY, "on")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_called_once()
    message = mock_notify.call_args.args[1]
    assert "Front Porch" in message
    assert "on" in message

    assert len(notify_calls) == 1
    assert notify_calls[0].data["message"] == message


async def test_verify_off_notify_service_blank_only_uses_persistent_notification(hass, freezer):
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_verify_off_blank_service")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)  # verify_off_notify_service defaults to ""
    hass.states.async_set(FRONT_ENTITY, "on")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_called_once()  # no exception, no attempted service call


async def test_manual_override_at_check_time_skips_notification_entirely(hass, freezer):
    freezer.move_to("2026-07-04 23:30:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_verify_off_overridden")
    coordinator = entry.runtime_data
    light = coordinator.light_config_for(FRONT_ENTITY)
    hass.states.async_set(FRONT_ENTITY, "on")  # would otherwise be a real failure
    coordinator._manual_override[FRONT_ENTITY] = ManualOverride(source="force_white")

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        await coordinator._run_verify_off_check(FRONT_ENTITY, light)

    mock_notify.assert_not_called()


async def test_a_new_fire_cancels_a_still_pending_verify_off_check(hass, freezer):
    """Mirrors test_verify_retry.py's own equivalent test for Plan A's
    verify chain -- Verify Off needs the same cancel-on-new-fire guarantee,
    via its own independent pending-timer map."""
    freezer.move_to("2026-07-04 23:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    async_mock_service(hass, "light", "turn_off")
    entry = await _setup_entry(hass, "test_verify_off_cancel_pending")
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
    assert coordinator._verify_off_pending_unsub[FRONT_ENTITY] is second_unsub

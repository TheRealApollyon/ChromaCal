"""Tests for the Emergency Mode restart breadcrumb: if
CONF_EMERGENCY_WAS_ACTIVE is still True when the coordinator starts up, HA
went down mid-broadcast without ever reaching the normal stop path. This
should surface to a human (log warning + persistent_notification, not just
a log line -- see the Phase 5b plan discussion for why), then clear itself
so it doesn't refire on a later, unrelated restart.
"""

from __future__ import annotations

from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import CONF_EMERGENCY_WAS_ACTIVE, DOMAIN

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


async def test_breadcrumb_left_true_raises_a_notification_and_clears_itself(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=ENTRY_DATA,
        entry_id="test_breadcrumb_left_true",
        options={CONF_EMERGENCY_WAS_ACTIVE: True},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    mock_notify.assert_called_once()
    _, kwargs = mock_notify.call_args
    call_args = mock_notify.call_args.args
    # message is the 2nd positional arg, title/notification_id may be kwargs
    assert "no longer running" in call_args[1]
    assert entry.options.get(CONF_EMERGENCY_WAS_ACTIVE) is False

    # Emergency Mode's own runtime state is fresh, never resumed from the
    # breadcrumb -- confirms this really is a one-shot notice, not resumed
    # state that would leave the broadcast silently running again.
    assert entry.runtime_data.emergency_active is False


async def test_breadcrumb_left_false_does_not_notify(hass, freezer):
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=ENTRY_DATA,
        entry_id="test_breadcrumb_left_false",
        options={CONF_EMERGENCY_WAS_ACTIVE: False},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.chromacal.coordinator.persistent_notification.async_create"
    ) as mock_notify:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    mock_notify.assert_not_called()

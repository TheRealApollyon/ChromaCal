"""Tests for verify-and-retry's pure logic: does a light's real state
match what a FireCommand asked for, and what should a retry send?
"""

from __future__ import annotations

from scheduling.fire import FireCommand
from scheduling.verify import (
    RETRY_TRANSITION_SECONDS,
    build_retry_command,
    is_verifiable,
    state_matches,
)

OFF_COMMAND = FireCommand("light", "turn_off", {"transition": 120})
ON_COMMAND_NO_BRIGHTNESS = FireCommand("light", "turn_on", {"rgb_color": [255, 0, 0]})
ON_COMMAND_WITH_BRIGHTNESS = FireCommand(
    "light", "turn_on", {"color_temp_kelvin": 4000, "brightness": 200, "transition": 30}
)


def test_off_command_matches_only_actual_off():
    assert state_matches(OFF_COMMAND, "off", None) is True
    assert state_matches(OFF_COMMAND, "on", None) is False
    assert state_matches(OFF_COMMAND, None, None) is False


def test_on_command_without_commanded_brightness_ignores_actual_brightness():
    assert state_matches(ON_COMMAND_NO_BRIGHTNESS, "on", None) is True
    assert state_matches(ON_COMMAND_NO_BRIGHTNESS, "on", 1) is True
    assert state_matches(ON_COMMAND_NO_BRIGHTNESS, "off", None) is False


def test_on_command_with_brightness_but_entity_reports_none_passes_on_state_alone():
    # Real bug caught live in the disposable multi-light container: an
    # onoff-only light (or any switch entity -- config_flow.py's
    # EntitySelector allows both domains) can never report a brightness
    # attribute at all, so a command that sets one must not treat a
    # missing actual_brightness as an automatic failure -- there's
    # nothing to compare, not a mismatch. The on/off state is the only
    # real signal such an entity can ever give.
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", None) is True


def test_on_command_brightness_within_tolerance_passes():
    # Commanded 200, tolerance is 10% = 20.
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", 200) is True
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", 190) is True
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", 220) is True


def test_on_command_brightness_outside_tolerance_fails():
    # Stuck-at-low-brightness is exactly the real failure mode this exists
    # to catch (v1's own BRIGHTNESS_THRESHOLD precedent).
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", 5) is False
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", 179) is False


def test_no_fixed_near_max_floor_unlike_v1():
    # v1 used a fixed BRIGHTNESS_THRESHOLD = 253 (near Zigbee max) because
    # it always commanded near-max brightness. v2's "default" tier
    # deliberately commands 200, not max -- a fixed near-max floor would
    # wrongly fail this every time. Confirms the check is relative to what
    # was actually commanded, not an absolute near-max floor.
    near_max_command = FireCommand(
        "light", "turn_on", {"color_temp_kelvin": 4000, "brightness": 255}
    )
    assert state_matches(near_max_command, "on", 200) is False  # genuinely low for THIS command
    assert state_matches(ON_COMMAND_WITH_BRIGHTNESS, "on", 200) is True  # exact match for a lower-brightness command


def test_brightness_pct_commands_normalize_onto_the_0_255_scale():
    # Force White (build_force_white_command) uses brightness_pct, not
    # brightness -- 100% should compare the same as a 255 brightness
    # command, not be treated as "no brightness commanded" (which would
    # skip the check entirely and silently miss a stuck-low bulb).
    force_white_command = FireCommand(
        "light", "turn_on", {"color_temp_kelvin": 2700, "brightness_pct": 100, "transition": 3}
    )
    assert state_matches(force_white_command, "on", 255) is True
    assert state_matches(force_white_command, "on", 250) is True  # within 10% tolerance
    assert state_matches(force_white_command, "on", 5) is False  # stuck low


def test_is_verifiable_only_true_for_real_on_off_commands():
    assert is_verifiable(OFF_COMMAND) is True
    assert is_verifiable(ON_COMMAND_WITH_BRIGHTNESS) is True
    assert is_verifiable(None) is False


def test_build_retry_command_swaps_transition_only():
    retry = build_retry_command(ON_COMMAND_WITH_BRIGHTNESS)
    assert retry.service_data["transition"] == RETRY_TRANSITION_SECONDS
    # Everything else about the command is untouched.
    assert retry.domain == ON_COMMAND_WITH_BRIGHTNESS.domain
    assert retry.service == ON_COMMAND_WITH_BRIGHTNESS.service
    assert retry.service_data["brightness"] == 200
    assert retry.service_data["color_temp_kelvin"] == 4000
    # Original command is untouched -- FireCommand is frozen, but confirm
    # the retry didn't mutate the shared service_data dict in place either.
    assert ON_COMMAND_WITH_BRIGHTNESS.service_data["transition"] == 30


def test_build_retry_command_with_no_transition_key_is_a_no_op():
    command = FireCommand("light", "turn_on", {"brightness": 255})
    assert build_retry_command(command) == command

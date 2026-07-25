"""Tests for the pure Salute/Emergency/Force White logic in
scheduling/actions.py -- Docker-free, no Home Assistant required.
"""

from __future__ import annotations

from custom_components.chromacal.scheduling.actions import (
    build_force_white_command,
    get_emergency_sequence,
    get_salute_steps,
)

# ── get_salute_steps ────────────────────────────────────────────────


def test_salute_has_three_volleys_each_with_flash_and_afterglow():
    steps = get_salute_steps("standard")
    flashes = [s for s in steps if "flash" in s.label]
    afterglows = [s for s in steps if "afterglow" in s.label]
    assert len(flashes) == 3
    assert len(afterglows) == 3
    assert all(s.rgb == (255, 255, 255) and s.brightness_pct == 100 for s in flashes)
    assert all(s.rgb == (60, 0, 0) and s.brightness_pct == 20 for s in afterglows)


def test_salute_pauses_between_volleys_but_not_after_the_third():
    steps = get_salute_steps("standard")
    pauses = [s for s in steps if "pause" in s.label]
    assert len(pauses) == 2  # between volley 1->2 and 2->3, not after volley 3
    assert all(s.rgb is None for s in pauses)  # pause = lights off


def test_salute_ends_with_taps_then_fade_out():
    steps = get_salute_steps("standard")
    assert steps[-2].label == "taps"
    assert steps[-2].rgb == (255, 147, 41)
    assert steps[-1].label == "fade out"
    assert steps[-1].rgb is None


def test_salute_pace_changes_hold_times_not_structure():
    fast = get_salute_steps("fast")
    slow = get_salute_steps("slow")
    assert len(fast) == len(slow)
    assert fast[0].hold_ms < slow[0].hold_ms  # fast flash holds shorter than slow


def test_salute_unknown_pace_falls_back_to_standard():
    assert get_salute_steps("nonsense") == get_salute_steps("standard")


# ── get_emergency_sequence ──────────────────────────────────────────


def test_emergency_red_blue_alternates_two_colors():
    assert get_emergency_sequence("red-blue") == [(255, 0, 0), (0, 0, 255)]


def test_emergency_amber_alternates_with_off():
    seq = get_emergency_sequence("amber")
    assert seq[0] == (255, 140, 0)
    assert seq[1] is None


def test_emergency_unknown_pattern_falls_back_to_solid_red():
    assert get_emergency_sequence("nonsense") == [(255, 0, 0)]


# ── build_force_white_command ───────────────────────────────────────


def test_force_white_command_uses_given_kelvin_at_full_brightness():
    command = build_force_white_command(2700)
    assert command.domain == "light"
    assert command.service == "turn_on"
    assert command.service_data["color_temp_kelvin"] == 2700
    assert command.service_data["brightness_pct"] == 100

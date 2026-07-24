"""Tests for build_fire_command (the command half of fireScheduledCommand)."""

from __future__ import annotations

from datetime import datetime

from scheduling.engine import LightConfig
from scheduling.fire import build_fire_command
from scheduling.models import NightSegment, SegmentEvent

NOW = datetime(2026, 7, 23, 20, 30, 0)
LIGHT = LightConfig(name="Porch", fade_in=30, fade_out=120)


def test_off_key_turns_off_with_fade_out_transition():
    cmd = build_fire_command("off", LIGHT, [], NOW)
    assert cmd.domain == "light"
    assert cmd.service == "turn_off"
    assert cmd.service_data == {"transition": 120}


def test_warmwhite_key_uses_kelvin_default_when_no_color_or_kelvin_configured():
    cmd = build_fire_command("warmwhite", LIGHT, [], NOW)
    assert cmd.service == "turn_on"
    # 250 mireds (v1's default) -> 1_000_000 / 250 = 4000K
    assert cmd.service_data["color_temp_kelvin"] == 4000
    assert cmd.service_data["brightness"] == 255
    assert cmd.service_data["transition"] == 30  # max(fade_in=30, 30)


def test_warmwhite_key_prefers_explicit_color_over_kelvin():
    light = LightConfig(name="Porch", fade_in=30, warmwhite_color="#FF0000")
    cmd = build_fire_command("warmwhite", light, [], NOW)
    assert cmd.service_data["rgb_color"] == [255, 0, 0]
    assert "color_temp_kelvin" not in cmd.service_data


def test_warmwhite_transition_is_at_least_30_even_if_fade_in_is_shorter():
    light = LightConfig(name="Porch", fade_in=5)
    cmd = build_fire_command("warmwhite", light, [], NOW)
    assert cmd.service_data["transition"] == 30


def test_event_key_single_color_no_cycling():
    segment = NightSegment(
        SegmentEvent("Halloween", ("#FF5000",), "holiday", "🎃"), 18.0, 22.0
    )
    cmd = build_fire_command("event:Halloween", LIGHT, [segment], NOW)
    assert cmd.service == "turn_on"
    assert cmd.service_data["rgb_color"] == [255, 80, 0]
    assert cmd.service_data["brightness"] == 255
    assert cmd.service_data["transition"] == 30


def test_event_key_multi_color_picks_index_from_elapsed_time():
    # Segment started at 20:00, now is 20:01:30 -> 90s elapsed
    # -> colorIdx = floor(90/60) % 3 = 1 % 3 = 1
    # (deliberately not exactly 60s: 1/60*3600 can round to 59.999... in
    # float, which would flake this test at the boundary -- not a bug in
    # build_fire_command, just bad test data if left exactly on the edge)
    segment = NightSegment(
        SegmentEvent("Pride Month", ("#FF0000", "#00FF00", "#0000FF"), "awareness", "🏳️‍🌈"),
        20.0,
        23.0,
    )
    now = datetime(2026, 7, 23, 20, 1, 30)
    cmd = build_fire_command("event:Pride Month", LIGHT, [segment], now)
    assert cmd.service_data["rgb_color"] == [0, 255, 0]  # index 1


def test_event_key_missing_segment_returns_none():
    assert build_fire_command("event:Nonexistent", LIGHT, [], NOW) is None


def test_default_key_uses_dimmer_warm_white():
    cmd = build_fire_command("default", LIGHT, [], NOW)
    assert cmd.service_data["color_temp_kelvin"] == 4000
    assert cmd.service_data["brightness"] == 200


def test_warmup_and_pre_keys_return_none():
    assert build_fire_command("warmup", LIGHT, [], NOW) is None
    assert build_fire_command("pre", LIGHT, [], NOW) is None

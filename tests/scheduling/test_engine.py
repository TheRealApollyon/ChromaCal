"""Tests for get_enabled_holidays, resolve_tier_winner, and get_night_segments."""

from __future__ import annotations

from datetime import datetime

import pytest

from scheduling.engine import (
    LightConfig,
    PersonalEvent,
    ScheduleConfig,
    get_current_segment,
    get_enabled_holidays,
    get_night_segments,
    resolve_tier_winner,
)
from scheduling.models import HolidayEvent, NightSegment, SegmentEvent

# ── get_enabled_holidays ─────────────────────────────────────────────────────


def test_category_filter_excludes_disabled_categories():
    config = ScheduleConfig(region="us", categories={"federal": True})
    holidays = get_enabled_holidays(config, 2026)
    assert all(h.category == "federal" for h in holidays)
    assert any(h.name == "Independence Day" for h in holidays)
    assert not any(h.name == "Halloween" for h in holidays)  # cultural, disabled


def test_no_categories_enabled_returns_nothing():
    config = ScheduleConfig(region="us", categories={})
    assert get_enabled_holidays(config, 2026) == []


def test_floating_dates_are_resolved_not_hardcoded():
    config = ScheduleConfig(region="us", categories={"federal": True})
    holidays = get_enabled_holidays(config, 2026)
    thanksgiving = next(h for h in holidays if h.name == "Thanksgiving")
    # 4th Thursday of Nov 2026 = the 26th (independently verified in test_dates.py)
    assert (thanksgiving.month, thanksgiving.day_start) == (11, 26)


def test_non_us_region_uses_its_own_calendar():
    config = ScheduleConfig(region="ca", categories={"federal": True})
    holidays = get_enabled_holidays(config, 2026)
    names = {h.name for h in holidays}
    assert "Canada Day" in names
    assert "Independence Day" not in names  # US-only


def test_color_override_replaces_default_colors():
    config = ScheduleConfig(
        region="us",
        categories={"federal": True},
        color_overrides={"Christmas Day": ("#111111",)},
    )
    holidays = get_enabled_holidays(config, 2026)
    christmas = next(h for h in holidays if h.name == "Christmas Day")
    assert christmas.colors == ("#111111",)


# ── resolve_tier_winner ───────────────────────────────────────────────────────

EVENT_A = HolidayEvent(10, 31, 31, "Samhain", "pagan", "🍂", ("#000000",), "holiday")
EVENT_B = HolidayEvent(10, 31, 31, "Halloween", "cultural", "🎃", ("#FF5000",), "holiday")


def test_single_candidate_returned_directly():
    assert resolve_tier_winner([EVENT_A], "Porch", ScheduleConfig()) is EVENT_A


def test_no_candidates_returns_none():
    assert resolve_tier_winner([], "Porch", ScheduleConfig()) is None


def test_no_preference_falls_back_to_array_order():
    winner = resolve_tier_winner([EVENT_A, EVENT_B], "Porch", ScheduleConfig())
    assert winner is EVENT_A


def test_saved_collision_preference_wins():
    pair_key = " vs ".join(sorted([EVENT_A.name, EVENT_B.name]))
    config = ScheduleConfig(collision_preferences={pair_key: "Halloween"})
    winner = resolve_tier_winner([EVENT_A, EVENT_B], "Porch", config)
    assert winner is EVENT_B


def test_tonights_pick_wins_when_no_saved_preference():
    config = ScheduleConfig(tonight_pick={"Porch": "Halloween"})
    winner = resolve_tier_winner([EVENT_A, EVENT_B], "Porch", config)
    assert winner is EVENT_B


def test_saved_preference_beats_tonights_pick():
    pair_key = " vs ".join(sorted([EVENT_A.name, EVENT_B.name]))
    config = ScheduleConfig(
        collision_preferences={pair_key: "Samhain"},
        tonight_pick={"Porch": "Halloween"},
    )
    winner = resolve_tier_winner([EVENT_A, EVENT_B], "Porch", config)
    assert winner is EVENT_A


# ── get_night_segments ────────────────────────────────────────────────────────

LIGHT = LightConfig(name="Porch", end_type="time", end_time="23:00", warmwhite_time=None, warmwhite_enabled=False)
NOW = datetime(2026, 11, 10, 19, 0)  # Nov 10, sunset hour supplied explicitly below


def test_sacred_tier_wins_and_runs_to_1am():
    sacred = HolidayEvent(11, 10, 10, "USMC Birthday", "military", "🎂", ("#FF2400",), "sacred")
    segments = get_night_segments(NOW, LIGHT, ScheduleConfig(), [sacred], sunset_hour=18.0)
    assert len(segments) == 1
    assert segments[0].event.name == "USMC Birthday"
    assert segments[0].is_sacred is True
    assert segments[0].end_hour == 25


def test_vigil_tier_used_when_no_sacred():
    vigil = HolidayEvent(11, 10, 10, "Some Vigil", "military", "🕯️", ("#000000",), "vigil")
    segments = get_night_segments(NOW, LIGHT, ScheduleConfig(), [vigil], sunset_hour=18.0)
    assert len(segments) == 1
    assert segments[0].event.name == "Some Vigil"
    assert segments[0].end_hour == 23


def test_holiday_tier_used_when_no_sacred_or_vigil():
    holiday = HolidayEvent(11, 10, 10, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")
    segments = get_night_segments(NOW, LIGHT, ScheduleConfig(), [holiday], sunset_hour=18.0)
    assert segments[0].event.name == "Some Holiday"


def test_awareness_events_split_the_window_equally():
    aware1 = HolidayEvent(11, 1, 30, "Awareness One", "awareness", "💙", ("#111111",), "awareness")
    aware2 = HolidayEvent(11, 1, 30, "Awareness Two", "awareness", "💙", ("#222222",), "awareness")
    segments = get_night_segments(NOW, LIGHT, ScheduleConfig(), [aware1, aware2], sunset_hour=18.0)
    assert len(segments) == 2
    assert segments[0].event.name == "Awareness One"
    assert segments[1].event.name == "Awareness Two"
    # window is 18:00-23:00 (5 hours), split evenly across 2 events
    assert segments[0].start_hour == pytest.approx(18.0)
    assert segments[0].end_hour == pytest.approx(20.5)
    assert segments[1].start_hour == pytest.approx(20.5)
    assert segments[1].end_hour == pytest.approx(23.0)


def test_tonights_pick_overrides_awareness_split():
    aware1 = HolidayEvent(11, 1, 30, "Awareness One", "awareness", "💙", ("#111111",), "awareness")
    aware2 = HolidayEvent(11, 1, 30, "Awareness Two", "awareness", "💙", ("#222222",), "awareness")
    config = ScheduleConfig(tonight_pick={"Porch": "Awareness Two"})
    segments = get_night_segments(NOW, LIGHT, config, [aware1, aware2], sunset_hour=18.0)
    assert len(segments) == 1
    assert segments[0].event.name == "Awareness Two"
    assert segments[0].is_pick is True
    assert segments[0].end_hour == pytest.approx(23.0)


def test_personal_event_used_when_no_holidays_match():
    config = ScheduleConfig(
        personal_events=(PersonalEvent(month=11, day=10, name="My Birthday", colors=("#ff00ff",)),)
    )
    segments = get_night_segments(NOW, LIGHT, config, [], sunset_hour=18.0)
    assert segments[0].event.name == "My Birthday"
    assert segments[0].event.icon == "🎂"


def test_default_fallback_when_nothing_matches():
    segments = get_night_segments(NOW, LIGHT, ScheduleConfig(), [], sunset_hour=18.0)
    assert segments[0].event.name == "Default"
    assert segments[0].event.event_type == "default"


def test_skipped_event_is_excluded():
    holiday = HolidayEvent(11, 10, 10, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")
    config = ScheduleConfig(skipped_events=frozenset({"Some Holiday"}))
    segments = get_night_segments(NOW, LIGHT, config, [holiday], sunset_hour=18.0)
    assert segments[0].event.name == "Default"


def test_pagan_solstice_is_sacred_only_when_extended_nights_enabled():
    solstice = HolidayEvent(11, 10, 10, "Some Sabbat", "pagan", "🌲", ("#000000",), "pagan_solstice")

    config_off = ScheduleConfig(pagan_extended_nights=False)
    segments_off = get_night_segments(NOW, LIGHT, config_off, [solstice], sunset_hour=18.0)
    assert segments_off[0].is_sacred is False
    assert segments_off[0].end_hour == 23  # holiday-tier window, not sacred's 25

    config_on = ScheduleConfig(pagan_extended_nights=True)
    segments_on = get_night_segments(NOW, LIGHT, config_on, [solstice], sunset_hour=18.0)
    assert segments_on[0].is_sacred is True
    assert segments_on[0].end_hour == 25


def test_warmwhite_cutoff_shortens_color_window_before_end_time():
    light = LightConfig(name="Porch", end_type="time", end_time="23:00", warmwhite_enabled=True, warmwhite_time="20:00")
    holiday = HolidayEvent(11, 10, 10, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")
    segments = get_night_segments(NOW, light, ScheduleConfig(), [holiday], sunset_hour=18.0)
    assert segments[0].end_hour == 20.0  # warm-white cutoff, earlier than the 23:00 end time


def test_start_offset_delays_color_start_after_sunset():
    light = LightConfig(name="Porch", end_type="time", end_time="23:00", warmwhite_enabled=False, start_offset=30)
    holiday = HolidayEvent(11, 10, 10, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")
    segments = get_night_segments(NOW, light, ScheduleConfig(), [holiday], sunset_hour=18.0)
    assert segments[0].start_hour == pytest.approx(18.5)  # 18:00 sunset + 30min offset


# ── get_current_segment ──────────────────────────────────────────────────────

EVENT_ONE = SegmentEvent("One", ("#111111",), "awareness", "💙")
EVENT_TWO = SegmentEvent("Two", ("#222222",), "awareness", "💙")
EVENT_THREE = SegmentEvent("Three", ("#333333",), "awareness", "💙")
SPLIT_SEGMENTS = [
    NightSegment(EVENT_ONE, 18.0, 19.5),
    NightSegment(EVENT_TWO, 19.5, 21.0),
    NightSegment(EVENT_THREE, 21.0, 22.5),
]


def test_current_segment_picks_the_one_matching_now_hour():
    assert get_current_segment(SPLIT_SEGMENTS, 20.0).event.name == "Two"


def test_current_segment_start_boundary_is_inclusive():
    assert get_current_segment(SPLIT_SEGMENTS, 21.0).event.name == "Three"


def test_current_segment_end_boundary_is_exclusive():
    assert get_current_segment(SPLIT_SEGMENTS, 19.5).event.name == "Two"


def test_current_segment_falls_back_to_first_when_before_window():
    assert get_current_segment(SPLIT_SEGMENTS, 10.0).event.name == "One"


def test_current_segment_falls_back_to_first_when_after_window():
    assert get_current_segment(SPLIT_SEGMENTS, 23.0).event.name == "One"


def test_current_segment_none_for_empty_list():
    assert get_current_segment([], 20.0) is None

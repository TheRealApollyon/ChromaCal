"""Tests for get_enabled_holidays, resolve_tier_winner, and get_night_segments."""

from __future__ import annotations

from datetime import datetime

import pytest

from scheduling.engine import (
    LightConfig,
    PersonalEvent,
    ScheduleConfig,
    all_event_names,
    get_candidates_for_date,
    get_current_segment,
    get_desired_fire_key,
    get_enabled_holidays,
    get_night_segments,
    get_upcoming_events,
    resolve_cfg_end_hour,
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


def test_warmwhite_time_with_seconds_does_not_crash_and_parses_the_same():
    """Real regression, 2026-09-03: HA's TimeSelector submitted "22:00:00"
    instead of "22:00" for a real Pi's stored warmwhite_time, crashing
    every coordinator refresh with `too many values to unpack` out of
    _parse_hour's bare 2-value unpack. "HH:MM:SS" must parse identically
    to the equivalent "HH:MM", not just avoid crashing.
    """
    holiday = HolidayEvent(11, 10, 10, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")

    clean = LightConfig(name="Porch", end_type="time", end_time="23:00", warmwhite_enabled=True, warmwhite_time="20:00")
    with_seconds = LightConfig(name="Porch", end_type="time", end_time="23:00", warmwhite_enabled=True, warmwhite_time="20:00:00")

    clean_segments = get_night_segments(NOW, clean, ScheduleConfig(), [holiday], sunset_hour=18.0)
    seconds_segments = get_night_segments(NOW, with_seconds, ScheduleConfig(), [holiday], sunset_hour=18.0)

    assert seconds_segments[0].end_hour == clean_segments[0].end_hour == 20.0


def test_resolve_cfg_end_hour_with_seconds_does_not_crash_and_parses_the_same():
    clean = LightConfig(end_type="time", end_time="23:00")
    with_seconds = LightConfig(end_type="time", end_time="23:00:00")
    assert resolve_cfg_end_hour(with_seconds) == resolve_cfg_end_hour(clean) == 23


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


# ── get_desired_fire_key ──────────────────────────────────────────────────────

FIRE_LIGHT = LightConfig(name="Porch", end_type="time", end_time="23:00", warmwhite_enabled=True, warmwhite_time="22:00")
FIRE_EVENT = HolidayEvent(7, 1, 31, "Some Awareness Month", "awareness", "💙", ("#111111",), "awareness")


def test_desired_key_off_after_end_time():
    now = datetime(2026, 7, 23, 23, 0)
    segments = get_night_segments(now, FIRE_LIGHT, ScheduleConfig(), [FIRE_EVENT], sunset_hour=18.0)
    assert get_desired_fire_key(now, FIRE_LIGHT, segments, 18.0) == "off"


def test_desired_key_warmwhite_after_warmwhite_time():
    now = datetime(2026, 7, 23, 22, 30)
    segments = get_night_segments(now, FIRE_LIGHT, ScheduleConfig(), [FIRE_EVENT], sunset_hour=18.0)
    assert get_desired_fire_key(now, FIRE_LIGHT, segments, 18.0) == "warmwhite"


def test_desired_key_event_during_color_window():
    now = datetime(2026, 7, 23, 20, 0)
    segments = get_night_segments(now, FIRE_LIGHT, ScheduleConfig(), [FIRE_EVENT], sunset_hour=18.0)
    assert get_desired_fire_key(now, FIRE_LIGHT, segments, 18.0) == "event:Some Awareness Month"


def test_desired_key_warmup_between_sunset_and_color_start():
    # start_offset delays color start past sunset -- the gap in between is 'warmup'
    light = LightConfig(name="Porch", end_type="time", end_time="23:00", start_offset=30)
    now = datetime(2026, 7, 23, 18, 10)
    segments = get_night_segments(now, light, ScheduleConfig(), [FIRE_EVENT], sunset_hour=18.0)
    assert get_desired_fire_key(now, light, segments, 18.0) == "warmup"


def test_desired_key_pre_before_sunset():
    now = datetime(2026, 7, 23, 12, 0)
    segments = get_night_segments(now, FIRE_LIGHT, ScheduleConfig(), [FIRE_EVENT], sunset_hour=18.0)
    assert get_desired_fire_key(now, FIRE_LIGHT, segments, 18.0) == "pre"


def test_desired_key_uses_its_own_20h_fallback_when_sunset_is_none():
    # Unlike get_night_segments (falls back to "now"), getDesiredFireKey
    # falls back to a hardcoded 20.0 when sunset_hour is None -- ported
    # faithfully as a real v1 inconsistency, not unified.
    now = datetime(2026, 7, 23, 19, 0)
    segments = get_night_segments(now, FIRE_LIGHT, ScheduleConfig(), [FIRE_EVENT], sunset_hour=None)
    assert get_desired_fire_key(now, FIRE_LIGHT, segments, None) == "pre"  # 19:00 < 20.0 fallback


# ── resolve_cfg_end_hour ──────────────────────────────────────────────────────


def test_resolve_cfg_end_hour_parses_a_plain_time():
    light = LightConfig(name="Porch", end_type="time", end_time="23:00")
    assert resolve_cfg_end_hour(light) == 23


def test_resolve_cfg_end_hour_defaults_to_23_for_non_time_end_types():
    light = LightConfig(name="Porch", end_type="sunrise", end_time=None)
    assert resolve_cfg_end_hour(light) == 23


def test_resolve_cfg_end_hour_defaults_to_23_on_unparseable_end_time():
    light = LightConfig(name="Porch", end_type="time", end_time="not-a-time")
    assert resolve_cfg_end_hour(light) == 23


def test_resolve_cfg_end_hour_truncates_minutes_matching_v1_behavior():
    # Ported faithfully from v1's own int(hh) truncation, not "fixed" to
    # round to the nearest hour -- see get_night_segments/get_desired_fire_key.
    light = LightConfig(name="Porch", end_type="time", end_time="23:45")
    assert resolve_cfg_end_hour(light) == 23


# ── get_candidates_for_date / all_event_names ────────────────────────────────

SACRED_EVENT = HolidayEvent(11, 10, 10, "USMC Birthday", "military", "🎂", ("#FF2400",), "sacred")
VIGIL_EVENT = HolidayEvent(11, 10, 10, "Some Vigil", "military", "🕯️", ("#000000",), "vigil")
HOLIDAY_EVENT = HolidayEvent(11, 10, 10, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")
OTHER_DAY_EVENT = HolidayEvent(11, 11, 11, "Veterans Day", "military", "🎖️", ("#000000",), "holiday")
MULTI_DAY_EVENT = HolidayEvent(11, 1, 30, "Native American Heritage Month", "heritage", "🪶", ("#000000",), "awareness")
ALL_CANDIDATE_EVENTS = [SACRED_EVENT, VIGIL_EVENT, HOLIDAY_EVENT, OTHER_DAY_EVENT, MULTI_DAY_EVENT]


def test_get_candidates_for_date_returns_every_tier_matching_the_date():
    candidates = get_candidates_for_date(ALL_CANDIDATE_EVENTS, 11, 10)
    names = {c.name for c in candidates}
    assert names == {"USMC Birthday", "Some Vigil", "Some Holiday", "Native American Heritage Month"}


def test_get_candidates_for_date_excludes_events_on_other_dates():
    candidates = get_candidates_for_date(ALL_CANDIDATE_EVENTS, 11, 10)
    assert "Veterans Day" not in {c.name for c in candidates}


def test_get_candidates_for_date_includes_multi_day_events_throughout_their_range():
    # Native American Heritage Month runs Nov 1-30 -- should match on day 1,
    # mid-range, and day 30, not just its start date.
    for day in (1, 15, 30):
        candidates = get_candidates_for_date(ALL_CANDIDATE_EVENTS, 11, day)
        assert "Native American Heritage Month" in {c.name for c in candidates}


def test_get_candidates_for_date_does_not_filter_by_skip_status():
    # No skip parameter exists on this function at all -- confirmed by
    # construction (it only takes holidays/month/day), but assert the
    # actual returned set includes everything regardless of what a caller
    # might separately consider "skipped".
    candidates = get_candidates_for_date(ALL_CANDIDATE_EVENTS, 11, 10)
    assert len(candidates) == 4


def test_all_event_names_deduplicates_and_sorts():
    duplicate = HolidayEvent(1, 1, 1, "Some Holiday", "federal", "🎆", ("#000000",), "holiday")
    names = all_event_names([SACRED_EVENT, VIGIL_EVENT, HOLIDAY_EVENT, duplicate])
    assert names == sorted({"USMC Birthday", "Some Vigil", "Some Holiday"})


# ── get_upcoming_events ───────────────────────────────────────────────────────

SINGLE_DAY_TODAY = HolidayEvent(7, 4, 4, "Independence Day", "federal", "🎆", ("#DC143C",), "holiday")
SINGLE_DAY_FUTURE = HolidayEvent(7, 20, 20, "Some Future Day", "federal", "🎉", ("#000000",), "holiday")
MULTI_DAY_FUTURE_START = HolidayEvent(8, 1, 31, "Some Awareness Month", "awareness", "💙", ("#000000",), "awareness")
MULTI_DAY_IN_PROGRESS = HolidayEvent(7, 1, 10, "Mid-Range Month", "awareness", "💚", ("#000000",), "awareness")
OUTSIDE_WINDOW = HolidayEvent(9, 1, 1, "Too Far Out", "federal", "🎈", ("#000000",), "holiday")


def test_today_event_is_included_and_flagged_is_today():
    events = get_upcoming_events(datetime(2026, 7, 4), [SINGLE_DAY_TODAY])
    assert len(events) == 1
    assert events[0].name == "Independence Day"
    assert events[0].date == datetime(2026, 7, 4).date()
    assert events[0].is_today is True


def test_future_single_day_event_included_not_flagged_today():
    events = get_upcoming_events(datetime(2026, 7, 4), [SINGLE_DAY_FUTURE])
    assert len(events) == 1
    assert events[0].date == datetime(2026, 7, 20).date()
    assert events[0].is_today is False


def test_event_beyond_the_window_is_excluded():
    events = get_upcoming_events(datetime(2026, 7, 4), [OUTSIDE_WINDOW], days=45)
    assert events == []


def test_event_exactly_at_the_window_boundary_is_included():
    # July 4 + 45 days = August 18 -- inclusive boundary (v1's `i <= days`).
    boundary_event = HolidayEvent(8, 18, 18, "Boundary Day", "federal", "🎯", ("#000000",), "holiday")
    events = get_upcoming_events(datetime(2026, 7, 4), [boundary_event], days=45)
    assert len(events) == 1
    assert events[0].date == datetime(2026, 8, 18).date()


def test_multi_day_event_starting_in_the_future_appears_once_on_its_start_day():
    events = get_upcoming_events(datetime(2026, 7, 4), [MULTI_DAY_FUTURE_START])
    assert len(events) == 1
    assert events[0].date == datetime(2026, 8, 1).date()


def test_multi_day_event_already_in_progress_today_still_shows_today():
    # Real v1 quirk: today (July 4) falls mid-range (July 1-10), not on the
    # start day -- still included today rather than silently disappearing.
    events = get_upcoming_events(datetime(2026, 7, 4), [MULTI_DAY_IN_PROGRESS])
    assert len(events) == 1
    assert events[0].date == datetime(2026, 7, 4).date()
    assert events[0].is_today is True


def test_personal_single_day_event_behaves_like_a_normal_event():
    personal = PersonalEvent(month=7, day=4, name="Birthday", colors=("#FFC0CB",))
    events = get_upcoming_events(datetime(2026, 7, 4), [], personal_events=(personal,))
    assert len(events) == 1
    assert events[0].category == "personal"
    assert events[0].icon == "🎂"
    assert events[0].is_personal_range is False


def test_personal_range_event_appears_once_per_night_not_deduplicated():
    personal = PersonalEvent(month=7, day=4, day_end=6, name="Anniversary Trip", colors=("#FF00FF",))
    events = get_upcoming_events(datetime(2026, 7, 4), [], personal_events=(personal,))
    dates = sorted(e.date for e in events)
    assert dates == [datetime(2026, 7, d).date() for d in (4, 5, 6)]
    assert all(e.is_personal_range for e in events)


def test_upcoming_events_does_not_filter_by_skip_status():
    # No skip parameter exists on this function at all, by construction --
    # same contract as get_candidates_for_date, confirmed the same way.
    events = get_upcoming_events(datetime(2026, 7, 4), [SINGLE_DAY_TODAY])
    assert len(events) == 1


def test_upcoming_events_dedup_keeps_only_the_first_future_occurrence():
    first = HolidayEvent(7, 20, 20, "Duplicate Name", "federal", "🎆", ("#000000",), "holiday")
    second = HolidayEvent(7, 25, 25, "Duplicate Name", "federal", "🎆", ("#000000",), "holiday")
    events = get_upcoming_events(datetime(2026, 7, 4), [first, second])
    assert len(events) == 1
    assert events[0].date == datetime(2026, 7, 20).date()


def test_upcoming_events_dedup_does_not_apply_across_two_today_occurrences():
    # Real v1 quirk, ported faithfully rather than "fixed": the dedup guard
    # is `seen.has(key) && !e.isToday` -- it only drops a duplicate that
    # ISN'T today, so two same-named entries that both land on today both
    # survive. Doesn't come up with real calendar data (no two enabled
    # entries share a name), but this locks in that the port matches v1's
    # actual behavior rather than a "cleaner" dedup nobody asked for.
    duplicate = HolidayEvent(7, 4, 4, "Independence Day", "federal", "🎆", ("#DC143C",), "holiday")
    events = get_upcoming_events(datetime(2026, 7, 4), [SINGLE_DAY_TODAY, duplicate])
    assert len(events) == 2

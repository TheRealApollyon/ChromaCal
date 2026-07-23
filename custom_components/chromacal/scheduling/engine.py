"""The scheduling brain: get_enabled_holidays, resolve_tier_winner, get_night_segments.

Ported from chromacal.html. No global CFG/_floatCache — everything a v1
function used to read off CFG is an explicit parameter here (see
ScheduleConfig), and floating-date resolution is the caller's concern (call
build_floating_dates() once per year and pass the result in, or just call
get_enabled_holidays fresh — it's cheap, no caching needed at this scale).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import replace as dc_replace
from datetime import datetime

from .calendars import GLOBAL_FLOATING, REGION_CALENDARS, US_HOLIDAYS
from .dates import build_floating_dates, get_pagan_solstice_events
from .models import HolidayEvent, NightSegment, SegmentEvent

_PERSONAL_ICONS = {
    "tribute": "🎖️",
    "memorial": "🕯️",
    "celebration": "🎉",
    "personal": "🎂",
}


@dataclass(frozen=True)
class PersonalEvent:
    """A user-defined personal event (birthday, anniversary, etc.)."""

    month: int
    day: int
    name: str
    colors: tuple[str, ...]
    event_type: str = "personal"
    day_end: int | None = None


@dataclass
class ScheduleConfig:
    """Everything get_enabled_holidays/resolve_tier_winner/get_night_segments
    used to read from v1's global CFG, made explicit."""

    region: str = "us"
    categories: dict[str, bool] = field(default_factory=dict)
    pagan_extended_nights: bool = False
    skipped_events: frozenset[str] = field(default_factory=frozenset)
    tonight_skips: frozenset[str] = field(default_factory=frozenset)
    collision_preferences: dict[str, str] = field(default_factory=dict)
    tonight_pick: dict[str, str] = field(default_factory=dict)
    color_overrides: dict[str, tuple[str, ...]] = field(default_factory=dict)
    personal_events: tuple[PersonalEvent, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LightConfig:
    """The subset of a light's config that get_night_segments needs."""

    name: str = ""
    end_type: str = "time"
    end_time: str | None = "23:00"
    start_offset: int = 0
    warmwhite_enabled: bool = True
    warmwhite_time: str | None = "22:00"


def get_enabled_holidays(config: ScheduleConfig, year: int) -> list[HolidayEvent]:
    """Regional calendar (with floating dates resolved) + GLOBAL_FLOATING +
    this year's pagan solstice/equinox events, filtered to enabled categories,
    with any user color overrides applied last."""
    floating = build_floating_dates(year)
    overrides = floating.get(config.region.upper(), {})
    base = REGION_CALENDARS.get(config.region) or US_HOLIDAYS

    def apply_date_override(h: HolidayEvent) -> HolidayEvent:
        override = overrides.get(h.name)
        if override is None:
            return h
        return dc_replace(h, month=override.month, day_start=override.day_start, day_end=override.day_end)

    resolved = [apply_date_override(h) for h in base]
    merged = [*resolved, *GLOBAL_FLOATING, *get_pagan_solstice_events(year)]
    merged = [h for h in merged if config.categories.get(h.category)]

    def apply_color_override(h: HolidayEvent) -> HolidayEvent:
        override = config.color_overrides.get(h.name)
        return dc_replace(h, colors=override) if override else h

    return [apply_color_override(h) for h in merged]


def resolve_tier_winner(
    candidates: list[HolidayEvent], light_name: str, config: ScheduleConfig
) -> HolidayEvent | None:
    """Same-tier collision resolution, in priority order:
    1. A saved preference for this exact pair (permanent, e.g. Samhain vs Halloween).
    2. Tonight's Pick for this light (one-off, e.g. a single year's Father's Day/Litha collision).
    3. Array order (first candidate wins), same as v1's original fallback behavior.
    """
    if len(candidates) <= 1:
        return candidates[0] if candidates else None

    pair_key = " vs ".join(sorted(c.name for c in candidates))
    saved_pref = config.collision_preferences.get(pair_key)
    if saved_pref:
        preferred = next((c for c in candidates if c.name == saved_pref), None)
        if preferred:
            return preferred

    pick = config.tonight_pick.get(light_name)
    if pick:
        picked = next((c for c in candidates if c.name == pick), None)
        if picked:
            return picked

    return candidates[0]


def _to_segment_event(h: HolidayEvent) -> SegmentEvent:
    return SegmentEvent(h.name, h.colors, h.event_type, h.icon)


def _parse_hour(time_str: str) -> float:
    hh, mm = time_str.split(":")
    return int(hh) + int(mm) / 60


def get_night_segments(
    now: datetime,
    light: LightConfig,
    config: ScheduleConfig,
    holidays: list[HolidayEvent],
    sunset_hour: float | None = None,
) -> list[NightSegment]:
    """Tonight's schedule for one light: sacred > vigil > holiday > awareness
    (split equally, or Tonight's Pick) > personal > default. Sacred/vigil/holiday
    are single-winner tiers resolved via resolve_tier_winner; awareness is the
    only tier that splits its window across multiple simultaneous events.
    """
    month, day = now.month, now.day
    skipped = config.skipped_events
    tonight_only_skips = config.tonight_skips

    def not_skipped(h: HolidayEvent) -> bool:
        return h.name not in skipped and h.name not in tonight_only_skips

    def in_window(h: HolidayEvent) -> bool:
        return h.month == month and h.day_start <= day <= h.day_end

    cfg_end = 23
    if light.end_type == "time" and light.end_time:
        try:
            cfg_end = int(light.end_time.split(":")[0])
        except ValueError:
            cfg_end = 23

    light_name = light.name or ""
    start_offset_min = light.start_offset or 0
    approx_sunset_h = sunset_hour if sunset_hour is not None else (now.hour + now.minute / 60)
    color_start_h = approx_sunset_h + start_offset_min / 60

    ww_h = None
    if light.warmwhite_enabled and light.warmwhite_time:
        ww_h = _parse_hour(light.warmwhite_time)
    color_end_h = ww_h if (ww_h is not None and ww_h < cfg_end) else cfg_end

    tonight_pick = config.tonight_pick.get(light_name)

    sacred_candidates = [
        h for h in holidays
        if (h.event_type == "sacred" or (h.event_type == "pagan_solstice" and config.pagan_extended_nights))
        and in_window(h) and not_skipped(h)
    ]
    sacred = resolve_tier_winner(sacred_candidates, light_name, config)
    if sacred:
        return [NightSegment(_to_segment_event(sacred), color_start_h, 25, is_sacred=True)]

    vigil_candidates = [h for h in holidays if h.event_type == "vigil" and in_window(h) and not_skipped(h)]
    vigil = resolve_tier_winner(vigil_candidates, light_name, config)
    if vigil:
        return [NightSegment(_to_segment_event(vigil), color_start_h, color_end_h)]

    holiday_candidates = [
        h for h in holidays
        if h.event_type in ("holiday", "pagan_solstice") and in_window(h) and not_skipped(h)
    ]
    holiday = resolve_tier_winner(holiday_candidates, light_name, config)
    if holiday:
        return [NightSegment(_to_segment_event(holiday), color_start_h, color_end_h)]

    awares = [h for h in holidays if h.event_type == "awareness" and in_window(h) and not_skipped(h)]

    if not awares:
        personal = next(
            (
                p for p in config.personal_events
                if p.month == month and day >= p.day and day <= (p.day_end or p.day) and p.name not in skipped
            ),
            None,
        )
        if personal:
            icon = _PERSONAL_ICONS.get(personal.event_type, "🎂")
            return [NightSegment(
                SegmentEvent(personal.name, personal.colors, personal.event_type, icon),
                color_start_h, color_end_h,
            )]
        return [NightSegment(SegmentEvent("Default", ("#FFC97A",), "default", "💡"), color_start_h, color_end_h)]

    if tonight_pick:
        picked = next((h for h in awares if h.name == tonight_pick), None)
        if picked:
            return [NightSegment(_to_segment_event(picked), color_start_h, color_end_h, is_pick=True)]

    total_h = max(color_end_h - color_start_h, 0)
    per_h = total_h / len(awares) if awares else total_h
    return [
        NightSegment(_to_segment_event(h), color_start_h + i * per_h, color_start_h + (i + 1) * per_h)
        for i, h in enumerate(awares)
    ]


def get_current_segment(segments: list[NightSegment], now_hour: float) -> NightSegment | None:
    """Which of tonight's segments is active right now?

    Ports getCurrentSegment() from chromacal.html. Falls back to the first
    segment if none match (e.g. now_hour is before the window starts or
    after the last segment ends) -- get_night_segments() always returns at
    least one segment, so this only returns None for an empty list.
    """
    for segment in segments:
        if segment.start_hour <= now_hour < segment.end_hour:
            return segment
    return segments[0] if segments else None

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
from datetime import datetime, timedelta

from .calendars import GLOBAL_FLOATING, REGION_CALENDARS, US_HOLIDAYS
from .dates import build_floating_dates, get_pagan_solstice_events
from .models import HolidayEvent, NightSegment, SegmentEvent, UpcomingEvent

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
    """The subset of a light's config that get_night_segments/
    get_desired_fire_key/build_fire_command need -- plus, since Plan A,
    a few fields (verify_*) that only the coordinator's fire-verification
    path needs, not those three functions. Kept on this same dataclass
    anyway rather than a second one: it's still the one shape
    build_light_config() produces from a light's raw config dict, and
    every caller that needs "this light's resolved config" already reads
    from here (sensor.py included, for display -- see verify_off_enabled).

    warmwhite_kelvin_mireds and warmwhite_color aren't collected by any
    config flow yet (Phase 1's wizard doesn't ask for them) -- they exist
    here so build_fire_command() has an honest, named dependency instead of
    a magic number buried in command-construction logic, matching v1's
    warmwhiteKelvin/warmwhiteColor fields and their same defaults.
    """

    name: str = ""
    end_type: str = "time"
    end_time: str | None = "23:00"
    start_offset: int = 0
    warmwhite_enabled: bool = True
    warmwhite_time: str | None = "22:00"
    fade_in: int = 30
    fade_out: int = 120
    warmwhite_kelvin_mireds: int = 250
    warmwhite_color: str | None = None
    verify_enabled: bool = True
    verify_retry_count: int = 2
    verify_check_delay: int = 180
    # Fixed clock-time off-verification (distinct from verify_enabled
    # above) -- this pass only displays it (Tonight's Schedule), no check
    # logic reads it yet. See const.py's CONF_VERIFY_OFF_ENABLED.
    verify_off_enabled: bool = False


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


def get_candidates_for_date(holidays: list[HolidayEvent], month: int, day: int) -> list[HolidayEvent]:
    """Every enabled calendar entry whose date range includes month/day,
    across all tiers, regardless of current skip state or which tier would
    win a collision.

    Used to determine which events are skippable "tonight" -- deliberately
    does NOT filter by skip status itself (that's ScheduleConfig's job
    inside get_night_segments). Filtering it out here too would mean an
    already-skipped event has no candidate left to build an un-skip switch
    from, which would violate skip state always being reversible.
    """
    return [h for h in holidays if h.month == month and h.day_start <= day <= h.day_end]


def all_event_names(holidays: list[HolidayEvent]) -> list[str]:
    """Every distinct event name in an enabled calendar, sorted.

    Used to build the static, always-present permanent-skip switches --
    one per name, for the whole enabled region+categories calendar, not
    scoped to any particular date.
    """
    return sorted({h.name for h in holidays})


@dataclass(frozen=True)
class _UpcomingCandidate:
    """Internal unification of HolidayEvent and PersonalEvent -- v1's
    getUpcomingEvents() builds one throwaway ad-hoc object shape for both;
    this is the same idea with real field names, not a public type."""

    month: int
    day_start: int
    day_end: int
    name: str
    category: str
    event_type: str
    icon: str
    colors: tuple[str, ...]
    is_personal_range: bool


def get_upcoming_events(
    now: datetime,
    holidays: list[HolidayEvent],
    personal_events: tuple[PersonalEvent, ...] = (),
    days: int = 45,
) -> list[UpcomingEvent]:
    """Every enabled holiday/personal event landing in the next `days` days.

    Ports getUpcomingEvents() from chromacal.html faithfully, including two
    real quirks worth knowing rather than "fixing":

    - A multi-day built-in event (e.g. Pride Month) appears once, on its
      start day, not once per day of its range -- EXCEPT one already in
      progress today, which still shows up today even though today isn't
      its start day. Only *future* continuation days get skipped.
    - A personal event with a real date range (day_end != day) is the one
      exception to "once per event": every night in the range appears
      individually, since the whole point of giving it a range is to let
      the user skip or customize individual nights within it.

    Like get_candidates_for_date, deliberately does NOT filter by skip
    status -- see UpcomingEvent's own docstring for why.
    """
    candidates = [
        _UpcomingCandidate(
            month=h.month,
            day_start=h.day_start,
            day_end=h.day_end,
            name=h.name,
            category=h.category,
            event_type=h.event_type,
            icon=h.icon,
            colors=h.colors,
            is_personal_range=False,
        )
        for h in holidays
    ] + [
        _UpcomingCandidate(
            month=p.month,
            day_start=p.day,
            day_end=p.day_end if p.day_end is not None else p.day,
            name=p.name,
            category="personal",
            event_type=p.event_type,
            icon=_PERSONAL_ICONS.get(p.event_type, "🎂"),
            colors=p.colors,
            is_personal_range=p.day_end is not None and p.day_end != p.day,
        )
        for p in personal_events
    ]

    today = now.date()
    events: list[UpcomingEvent] = []
    for i in range(days + 1):
        d = today + timedelta(days=i)
        for c in candidates:
            if c.month != d.month or not (c.day_start <= d.day <= c.day_end):
                continue
            is_multi_day = c.day_start != c.day_end
            if is_multi_day and d.day > c.day_start and i > 0 and not c.is_personal_range:
                continue
            events.append(
                UpcomingEvent(
                    date=d,
                    name=c.name,
                    category=c.category,
                    event_type=c.event_type,
                    icon=c.icon,
                    colors=c.colors,
                    is_today=(i == 0),
                    is_personal_range=c.is_personal_range,
                )
            )

    seen: set[str] = set()
    result: list[UpcomingEvent] = []
    for e in events:
        key = f"{e.name}:{e.date.isoformat()}" if e.is_personal_range else e.name
        if key in seen and not e.is_today:
            continue
        seen.add(key)
        result.append(e)
    return result


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
    """"HH:MM" -> decimal hour. Only the hour and minute are ever used --
    `split(":")[:2]`, not a bare 2-value unpack, because HA's own
    TimeSelector has been observed submitting "HH:MM:SS" instead of
    "HH:MM" (confirmed live, 2026-09-03: a real Pi's stored
    warmwhite_time of "22:00:00" crashed every coordinator refresh with
    `too many values to unpack`, from a plain `hh, mm = time_str.split(":")`
    here -- this is the only place in the whole integration that parses a
    configured time string into hour math, so this one fix covers every
    caller, not just warmwhite_time's).
    """
    hh, mm = time_str.split(":")[:2]
    return int(hh) + int(mm) / 60


def resolve_cfg_end_hour(light: LightConfig) -> float:
    """The light's configured off-time as a decimal hour, defaulting to 23
    for any end_type other than a plain time (or an unparseable end_time).

    Was duplicated verbatim inside get_night_segments and
    get_desired_fire_key; extracted so sensor.py can also expose it (as
    schedule_end_time) without a third copy of the same four lines.
    Routed through _parse_hour (truncated to an int) rather than its own
    parsing, so it gets the same "HH:MM:SS" tolerance for free instead of
    being a second, independently-fragile place to fix later.
    """
    if light.end_type == "time" and light.end_time:
        try:
            return int(_parse_hour(light.end_time))
        except ValueError:
            return 23
    return 23


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

    cfg_end = resolve_cfg_end_hour(light)

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


def get_desired_fire_key(
    now: datetime,
    light: LightConfig,
    segments: list[NightSegment],
    sunset_hour: float | None,
) -> str:
    """What SHOULD be happening right now for this light?

    Ports getDesiredFireKey() from chromacal.html. Returns one of:
    'off' | 'warmwhite' | f'event:{name}' | 'default' | 'warmup' | 'pre'.
    'warmup' and 'pre' mean "do nothing" -- an existing sunset/sunrise
    automation is assumed to handle that phase, matching v1.

    Deliberately uses its own fallback (20.0) when sunset_hour is None,
    NOT get_night_segments' fallback (the current hour) -- that mismatch
    exists in v1 itself (getDesiredFireKey and getNightSegments read
    different sunsetH defaults), so it's preserved here rather than
    quietly unified.
    """
    now_hour = now.hour + now.minute / 60
    cfg_end = resolve_cfg_end_hour(light)
    start_offset_min = light.start_offset or 0
    approx_sunset_h = sunset_hour if sunset_hour is not None else 20.0
    color_start_h = approx_sunset_h + start_offset_min / 60
    ww_h = None
    if light.warmwhite_enabled and light.warmwhite_time:
        ww_h = _parse_hour(light.warmwhite_time)

    if now_hour >= cfg_end:
        return "off"
    if ww_h is not None and now_hour >= ww_h:
        return "warmwhite"
    if now_hour >= color_start_h:
        current = get_current_segment(segments, now_hour)
        return f"event:{current.event.name}" if current else "default"
    if now_hour >= approx_sunset_h:
        return "warmup"
    return "pre"

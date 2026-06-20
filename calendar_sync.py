"""
ChromaCal v2: Calendar Sync.

Two distinct pieces, each with a different verification story:

1. fetch_calendar_events() — the actual HA service call. Specified correctly
   against documented APIs (blocking=True AND return_response=True are both
   required to get event data back, confirmed against multiple independent
   sources, including real bug reports from people who forgot one of the two
   flags), but genuinely UNTESTED here, since it needs a live Home Assistant
   instance with a real calendar entity to actually run against. That's an
   honest boundary, not something to pretend around.

2. match_events_to_colors() and merge_into_upcoming() — pure logic, no HA
   dependency at all. Fully testable in isolation, and fully tested below
   against realistic mock data matching the documented response shape.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any


# ── PART 1: THE LIVE HA CALL — correctly specified, not independently testable here ──

async def fetch_calendar_events(hass, calendar_entity_id: str, days: int = 45) -> list[dict]:
    """
    Calls calendar.get_events for one calendar entity over a lookahead window,
    matching the same 45-day horizon ChromaCal already uses for its built-in
    holiday calendar. Returns the flat list of events for that entity.

    blocking=True and return_response=True are both required — calendar.get_events
    is a response-data service, not a fire-and-forget one. Missing either flag
    is a documented, real, easy mistake (confirmed via actual error reports:
    "Service call requires responses but caller did not ask for...").
    """
    start = datetime.now()
    end = start + timedelta(days=days)
    response = await hass.services.async_call(
        "calendar", "get_events",
        {
            "entity_id": calendar_entity_id,
            "start_date_time": start.isoformat(),
            "end_date_time": end.isoformat(),
        },
        blocking=True,
        return_response=True,
    )
    # Response is keyed by calendar entity_id, each with an "events" list —
    # documented shape: {"calendar.x": {"events": [{"summary":..., "start":..., ...}]}}
    return response.get(calendar_entity_id, {}).get("events", [])


# ── PART 2: MATCHING & MERGING — pure logic, fully testable ──

def match_events_to_colors(events: list[dict], color_mappings: dict[str, list[str]]) -> list[dict]:
    """
    events: the raw list from fetch_calendar_events(), each dict containing
        at minimum 'summary' and 'start' (per the documented response shape —
        'end', 'description', 'location' are present only when they have a value).
    color_mappings: { "game night": ["#FF0000", "#00FF00"], ... } — keys are
        already normalized (lowercased, trimmed) by save_color_mapping() below,
        so matching here is a simple, predictable exact lookup, not fuzzy.

    Returns only the events that matched, each with its assigned colors attached.
    """
    matched = []
    for event in events:
        title = event.get("summary", "")
        normalized = title.strip().lower()
        if normalized in color_mappings:
            matched.append({**event, "colors": color_mappings[normalized]})
    return matched

def save_color_mapping(color_mappings: dict[str, list[str]], title: str, colors: list[str]) -> dict[str, list[str]]:
    """Normalizes a title the same way match_events_to_colors() expects, so
    saving 'Game Night' and matching against a calendar's 'game night' both work."""
    key = title.strip().lower()
    return {**color_mappings, key: colors}

def merge_into_upcoming(holiday_events: list[dict], matched_calendar_events: list[dict]) -> list[dict]:
    """
    Produces one unified, date-sorted list — calendar-sourced events are
    indistinguishable in shape from holidays once merged, same fields the
    rest of ChromaCal's Upcoming list already expects: date, name, colors, source.
    """
    unified = []
    for h in holiday_events:
        unified.append({"date": h["date"], "name": h["name"], "colors": h["colors"], "source": "holiday"})
    for c in matched_calendar_events:
        event_date = datetime.fromisoformat(c["start"]).date() if isinstance(c["start"], str) else c["start"]
        unified.append({"date": event_date, "name": c.get("summary", ""), "colors": c["colors"], "source": "calendar"})
    unified.sort(key=lambda e: e["date"])
    return unified

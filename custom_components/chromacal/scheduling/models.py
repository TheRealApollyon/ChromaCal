"""Data shapes for the scheduling brain.

Field names are spelled out (month/day_start/day_end/category/event_type)
rather than v1's terse m/d1/d2/cat/type — a readability improvement with no
behavior change, since these are pure data carriers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HolidayEvent:
    """One entry from a regional calendar, GLOBAL_FLOATING, or a pagan solstice/equinox.

    event_type is one of: holiday | vigil | sacred | awareness | pagan_solstice
    (matches v1's tier system used by resolve_tier_winner/get_night_segments).
    """

    month: int
    day_start: int
    day_end: int
    name: str
    category: str
    icon: str
    colors: tuple[str, ...]
    event_type: str
    note: str | None = None


@dataclass(frozen=True)
class SegmentEvent:
    """The event payload embedded in a NightSegment — name/colors/type/icon only.

    Mirrors what v1's getNightSegments() actually returns for personal/default
    events (which have no month/day/category), so this is deliberately a
    smaller shape than HolidayEvent rather than reusing it.
    """

    name: str
    colors: tuple[str, ...]
    event_type: str
    icon: str


@dataclass(frozen=True)
class NightSegment:
    """One scheduled window for a light tonight: [start_hour, end_hour) showing event."""

    event: SegmentEvent
    start_hour: float
    end_hour: float
    is_sacred: bool = False
    is_pick: bool = False

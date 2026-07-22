"""Date algorithms ported from chromacal.html: Easter, solstice/equinox table,
nth-weekday-of-month, and the floating-date override builder.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta

from .models import HolidayEvent

# ── EASTER (Anonymous Gregorian / Meeus-Jones-Butcher algorithm) ───────────
# Ported 1:1 from getEasterDate() in chromacal.html. Valid for the Gregorian
# calendar generally, not just the 2024-2031 window checked in tests.


def get_easter_date(year: int) -> date:
    """Return the Gregorian-calendar date of Easter Sunday for `year`."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


# ── SOLSTICE / EQUINOX TABLE ─────────────────────────────────────────────────
# Ported verbatim from chromacal.html's SOLSTICE_EQUINOX_TABLE. Format per year:
# (march_equinox_day, june_solstice_day, sept_equinox_day, dec_solstice_day),
# all UTC day-of-month. Independently cross-checked against real UTC
# equinox/solstice timestamps for all 8 years 2024-2031 during this port, not
# just against v1's own claimed verification of the same range.
SOLSTICE_EQUINOX_TABLE: dict[int, tuple[int, int, int, int]] = {
    2024: (20, 20, 22, 21),
    2025: (20, 21, 22, 21),
    2026: (20, 21, 23, 21),
    2027: (20, 21, 23, 22),
    2028: (20, 20, 22, 21),
    2029: (20, 21, 22, 21),
    2030: (20, 21, 22, 21),
    2031: (20, 21, 23, 22),
}
# Falls back to the most common date of the years actually checked, for any
# year outside the verified table above.
SOLSTICE_EQUINOX_FALLBACK: tuple[int, int, int, int] = (20, 21, 22, 21)


def get_solstice_equinox_days(year: int) -> tuple[int, int, int, int]:
    """Return (march_equinox, june_solstice, sept_equinox, dec_solstice) day-of-month."""
    return SOLSTICE_EQUINOX_TABLE.get(year, SOLSTICE_EQUINOX_FALLBACK)


def get_pagan_solstice_events(year: int) -> list[HolidayEvent]:
    """The 4 solstice/equinox pagan sabbats for `year`, with resolved dates.

    event_type is 'pagan_solstice' (not 'holiday') so get_night_segments' sacred
    tier check can find these specifically and gate them on pagan_extended_nights.
    """
    mar_d, jun_d, sep_d, dec_d = get_solstice_equinox_days(year)
    return [
        HolidayEvent(
            3, mar_d, mar_d, "Ostara (Spring Equinox)", "pagan", "🌱",
            ("#FFF4B0", "#A8D8A8", "#FFD1DC"), "pagan_solstice",
            "Balance of day and night, renewal",
        ),
        HolidayEvent(
            6, jun_d, jun_d, "Litha (Summer Solstice)", "pagan", "☀️",
            ("#FFD700", "#FFA500"), "pagan_solstice",
            "Longest day, the sun at its peak",
        ),
        HolidayEvent(
            9, sep_d, sep_d, "Mabon (Fall Equinox)", "pagan", "🍁",
            ("#CC6B2C", "#8B5A2B", "#A0522D"), "pagan_solstice",
            "Second harvest, balance, gratitude",
        ),
        HolidayEvent(
            12, dec_d, dec_d, "Yule (Winter Solstice)", "pagan", "🌲",
            ("#0B6E4F", "#A4243B", "#D4AF37"), "pagan_solstice",
            "Longest night, the return of the light",
        ),
    ]


def nth_weekday(year: int, month: int, weekday: int, n: int) -> int:
    """Day-of-month of the nth occurrence of `weekday` in `year`/`month`.

    weekday: 0=Sun 1=Mon 2=Tue 3=Wed 4=Thu 5=Fri 6=Sat (matches v1's JS
    Date.getDay() convention, not Python's date.weekday()).
    n: 1=first 2=second 3=third 4=fourth  -1=last.
    e.g. nth_weekday(2026, 11, 4, 4) == 26 (4th Thursday of Nov 2026 = Thanksgiving).
    """
    first_py_dow, days_in_month = calendar.monthrange(year, month)  # Mon=0..Sun=6
    first_dow = (first_py_dow + 1) % 7  # convert to Sun=0..Sat=6
    if n > 0:
        return 1 + (weekday - first_dow + 7) % 7 + (n - 1) * 7
    last_day = days_in_month
    last_py_dow = calendar.weekday(year, month, last_day)
    last_dow = (last_py_dow + 1) % 7
    return last_day - (last_dow - weekday + 7) % 7


def shift_date(month: int, day: int, year: int, days: int) -> tuple[int, int]:
    """Add `days` to a (month, day) pair in `year`, correctly crossing month boundaries."""
    shifted = date(year, month, day) + timedelta(days=days)
    return shifted.month, shifted.day


@dataclass(frozen=True)
class DateOverride:
    """A resolved floating date for one named holiday: (month, day_start, day_end)."""

    month: int
    day_start: int
    day_end: int


def build_floating_dates(year: int) -> dict[str, dict[str, DateOverride]]:
    """Build the per-region floating-date override map for `year`.

    Pattern: region key (US/CA/UK/AU/EU) -> holiday name -> resolved DateOverride.
    Regions not listed here (APAC/LATAM/GLOBAL) have no floating dates to
    resolve — their calendars are either all-fixed-date or already
    approximate (GLOBAL_FLOATING), matching v1.
    """
    easter = get_easter_date(year)

    def off(days: int) -> DateOverride:
        m, d = shift_date(easter.month, easter.day, year, days)
        return DateOverride(m, d, d)

    # Victoria Day = last Monday in May, on or before May 24
    vic_day_d = nth_weekday(year, 5, 1, -1)
    if vic_day_d > 24:
        vic_day_d -= 7
    vic_day = DateOverride(5, vic_day_d, vic_day_d)

    return {
        "US": {
            "MLK Day": DateOverride(1, nth_weekday(year, 1, 1, 3), nth_weekday(year, 1, 1, 3)),
            "Presidents' Day": DateOverride(2, nth_weekday(year, 2, 1, 3), nth_weekday(year, 2, 1, 3)),
            "Mardi Gras / Fat Tuesday": off(-47),
            "Ash Wednesday": off(-46),
            "Good Friday": off(-2),
            "Easter Sunday": DateOverride(easter.month, easter.day, easter.day),
            "Mother's Day": DateOverride(5, nth_weekday(year, 5, 0, 2), nth_weekday(year, 5, 0, 2)),
            "Memorial Day": DateOverride(5, nth_weekday(year, 5, 1, -1), nth_weekday(year, 5, 1, -1)),
            "Armed Forces Day": DateOverride(5, nth_weekday(year, 5, 6, 3), nth_weekday(year, 5, 6, 3)),
            "Father's Day": DateOverride(6, nth_weekday(year, 6, 0, 3), nth_weekday(year, 6, 0, 3)),
            "Labor Day": DateOverride(9, nth_weekday(year, 9, 1, 1), nth_weekday(year, 9, 1, 1)),
            "POW·MIA Recognition Day": DateOverride(9, nth_weekday(year, 9, 5, 3), nth_weekday(year, 9, 5, 3)),
            "Gold Star Mother's and Family's Day": DateOverride(9, nth_weekday(year, 9, 0, -1), nth_weekday(year, 9, 0, -1)),
            "Indigenous Peoples Day": DateOverride(10, nth_weekday(year, 10, 1, 2), nth_weekday(year, 10, 1, 2)),
            "Thanksgiving": DateOverride(11, nth_weekday(year, 11, 4, 4), nth_weekday(year, 11, 4, 4)),
        },
        "CA": {
            "Good Friday": off(-2),
            "Easter Monday": off(1),
            "Victoria Day": vic_day,
            "Labour Day": DateOverride(9, nth_weekday(year, 9, 1, 1), nth_weekday(year, 9, 1, 1)),
            "Thanksgiving (Canada)": DateOverride(10, nth_weekday(year, 10, 1, 2), nth_weekday(year, 10, 1, 2)),
        },
        "UK": {
            "Good Friday": off(-2),
            "Easter Monday": off(1),
            "Early May Bank Holiday": DateOverride(5, nth_weekday(year, 5, 1, 1), nth_weekday(year, 5, 1, 1)),
            "Spring Bank Holiday": DateOverride(5, nth_weekday(year, 5, 1, -1), nth_weekday(year, 5, 1, -1)),
            "Summer Bank Holiday": DateOverride(8, nth_weekday(year, 8, 1, -1), nth_weekday(year, 8, 1, -1)),
        },
        "AU": {
            "Good Friday": off(-2),
            "Easter Saturday": off(-1),
            "Easter Sunday": DateOverride(easter.month, easter.day, easter.day),
            "Easter Monday": off(1),
        },
        "EU": {
            "Good Friday": off(-2),
            "Easter Monday": off(1),
            "Ascension Day": off(39),
            "Pentecost Monday / Whit Monday": off(50),
            "Carnival / Mardi Gras": off(-47),
        },
    }

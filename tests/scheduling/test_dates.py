"""Date-math tests for the scheduling brain.

Easter and solstice/equinox dates here are checked against independent
sources (Wikipedia's "List of dates for Easter", qppstudio.net, and UTC
equinox/solstice timestamps), not just against chromacal.html's own output —
the point is confirming real-world correctness, not just JS parity.
"""

from __future__ import annotations

from datetime import date

import pytest

from scheduling.dates import (
    build_floating_dates,
    get_easter_date,
    get_pagan_solstice_events,
    get_solstice_equinox_days,
    nth_weekday,
    shift_date,
)

# Source: https://en.wikipedia.org/wiki/List_of_dates_for_Easter
EASTER_DATES_2024_2031 = {
    2024: date(2024, 3, 31),
    2025: date(2025, 4, 20),
    2026: date(2026, 4, 5),
    2027: date(2027, 3, 28),
    2028: date(2028, 4, 16),
    2029: date(2029, 4, 1),
    2030: date(2030, 4, 21),
    2031: date(2031, 4, 13),
}

# A couple of years outside the "verified 2024-2031" window, to confirm the
# algorithm itself generalizes rather than happening to fit only that range.
EASTER_DATES_OTHER_YEARS = {
    2000: date(2000, 4, 23),
    2016: date(2016, 3, 27),
}


@pytest.mark.parametrize("year,expected", sorted(EASTER_DATES_2024_2031.items()))
def test_easter_matches_v1_verified_window(year, expected):
    assert get_easter_date(year) == expected


@pytest.mark.parametrize("year,expected", sorted(EASTER_DATES_OTHER_YEARS.items()))
def test_easter_generalizes_outside_verified_window(year, expected):
    assert get_easter_date(year) == expected


# Source: UTC equinox/solstice timestamps for all 8 years (worldclocktools.com,
# universaltimedate.com, earthsky.org, timeanddate.com), independently checked
# against chromacal.html's own SOLSTICE_EQUINOX_TABLE for every year it claims
# "verified 2024-2031" — not a sample.
@pytest.mark.parametrize(
    "year,expected",
    [
        (2024, (20, 20, 22, 21)),
        (2025, (20, 21, 22, 21)),
        (2026, (20, 21, 23, 21)),
        (2027, (20, 21, 23, 22)),
        (2028, (20, 20, 22, 21)),
        (2029, (20, 21, 22, 21)),
        (2030, (20, 21, 22, 21)),
        (2031, (20, 21, 23, 22)),
    ],
)
def test_solstice_equinox_days_match_utc_data(year, expected):
    assert get_solstice_equinox_days(year) == expected


def test_solstice_equinox_fallback_for_unlisted_year():
    assert get_solstice_equinox_days(1999) == (20, 21, 22, 21)


def test_pagan_solstice_events_use_resolved_dates():
    events = get_pagan_solstice_events(2026)
    assert [e.name for e in events] == [
        "Ostara (Spring Equinox)",
        "Litha (Summer Solstice)",
        "Mabon (Fall Equinox)",
        "Yule (Winter Solstice)",
    ]
    assert (events[0].month, events[0].day_start) == (3, 20)
    assert (events[1].month, events[1].day_start) == (6, 21)
    assert (events[2].month, events[2].day_start) == (9, 23)
    assert (events[3].month, events[3].day_start) == (12, 21)
    assert all(e.event_type == "pagan_solstice" for e in events)


@pytest.mark.parametrize(
    "year,month,weekday,n,expected_day",
    [
        (2026, 11, 4, 4, 26),  # Thanksgiving: 4th Thursday of Nov 2026
        (2026, 1, 1, 3, 19),  # MLK Day: 3rd Monday of Jan 2026
        (2026, 5, 1, -1, 25),  # Memorial Day: last Monday of May 2026
        (2026, 9, 1, 1, 7),  # Labor Day: 1st Monday of Sep 2026
    ],
)
def test_nth_weekday_matches_known_us_holidays(year, month, weekday, n, expected_day):
    assert nth_weekday(year, month, weekday, n) == expected_day


def test_shift_date_crosses_month_boundary():
    # Easter 2026 is April 5; Ash Wednesday is 46 days before it (Feb 18).
    assert shift_date(4, 5, 2026, -46) == (2, 18)


def test_shift_date_crosses_year_boundary():
    assert shift_date(1, 5, 2026, -10) == (12, 26)


def test_build_floating_dates_thanksgiving_2026():
    floating = build_floating_dates(2026)
    assert floating["US"]["Thanksgiving"].month == 11
    assert floating["US"]["Thanksgiving"].day_start == 26


def test_build_floating_dates_victoria_day_subtracts_week_when_past_24th():
    # nth_weekday(2026, 5, 1, -1) is a date past the 24th in some years;
    # Victoria Day must always land on or before the 24th.
    floating = build_floating_dates(2026)
    assert floating["CA"]["Victoria Day"].day_start <= 24

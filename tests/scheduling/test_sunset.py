"""Tests for the ported fetchSunset() hour-extraction logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from scheduling.sunset import resolve_sunset_hour

# A fixed local offset stands in for "local time" here -- the function only
# cares about hour/minute extraction and a hoursUntil comparison, neither of
# which needs real IANA tzdata to exercise both branches faithfully.
LOCAL = timezone(timedelta(hours=-5))


def test_sunset_still_ahead_today_uses_next_setting_directly():
    now = datetime(2026, 7, 22, 15, 0, tzinfo=LOCAL)  # 3pm
    next_setting = datetime(2026, 7, 22, 20, 19, tzinfo=LOCAL)  # 8:19pm, same day
    assert resolve_sunset_hour(now, next_setting) == pytest.approx(20 + 19 / 60)


def test_sunset_already_passed_still_resolves_to_same_hour_minute():
    # Checking well after today's sunset: next_setting is tomorrow's, but
    # hoursUntil is ~21h (always > 2h in this case), so the branch takes the
    # same "use directly" path -- see the Phase 2c discussion for why.
    now = datetime(2026, 7, 22, 23, 0, tzinfo=LOCAL)  # 11pm, 2h41m after sunset
    next_setting = datetime(2026, 7, 23, 20, 19, tzinfo=LOCAL)  # tomorrow, 8:19pm
    assert resolve_sunset_hour(now, next_setting) == pytest.approx(20 + 19 / 60)


def test_within_2_hours_before_sunset_takes_the_subtract_branch():
    # hoursUntil <= 2h: next_setting is already today's own upcoming sunset,
    # so subtracting 24h and re-extracting hour/minute must still land on the
    # same value (no DST in this fixed-offset test).
    now = datetime(2026, 7, 22, 19, 0, tzinfo=LOCAL)  # 7pm, sunset in 1h19m
    next_setting = datetime(2026, 7, 22, 20, 19, tzinfo=LOCAL)
    assert resolve_sunset_hour(now, next_setting) == pytest.approx(20 + 19 / 60)


def test_exactly_2_hours_out_is_the_subtract_branchs_boundary():
    # hours_until == 2.0 exactly: `> 2` is false, so this is the smallest gap
    # that still takes the subtract-24h path, not the largest gap that takes
    # the direct path. Value is identical either way absent DST.
    now = datetime(2026, 7, 22, 18, 19, tzinfo=LOCAL)  # exactly 2h before sunset
    next_setting = datetime(2026, 7, 22, 20, 19, tzinfo=LOCAL)
    assert resolve_sunset_hour(now, next_setting) == pytest.approx(20 + 19 / 60)


def test_just_over_2_hours_out_uses_next_setting_directly():
    now = datetime(2026, 7, 22, 18, 18, tzinfo=LOCAL)  # 2h1m before sunset
    next_setting = datetime(2026, 7, 22, 20, 19, tzinfo=LOCAL)
    assert resolve_sunset_hour(now, next_setting) == pytest.approx(20 + 19 / 60)

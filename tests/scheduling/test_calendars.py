"""Structural sanity checks for the ported regional calendars."""

from __future__ import annotations

from scheduling.calendars import (
    AU_HOLIDAYS,
    CA_HOLIDAYS,
    EU_HOLIDAYS,
    GLOBAL_FLOATING,
    APAC_HOLIDAYS,
    LATAM_HOLIDAYS,
    REGION_CALENDARS,
    UK_HOLIDAYS,
    US_HOLIDAYS,
)

ALL_REGION_ARRAYS = {
    "us": US_HOLIDAYS,
    "ca": CA_HOLIDAYS,
    "uk": UK_HOLIDAYS,
    "au": AU_HOLIDAYS,
    "eu": EU_HOLIDAYS,
    "apac": APAC_HOLIDAYS,
    "latam": LATAM_HOLIDAYS,
    "global": GLOBAL_FLOATING,
}

VALID_EVENT_TYPES = {"holiday", "vigil", "sacred", "awareness", "pagan_solstice"}


def test_region_calendars_keys_match_the_8_wizard_regions():
    assert set(REGION_CALENDARS) == {"us", "ca", "uk", "au", "eu", "apac", "latam", "global"}


def test_us_is_the_only_region_that_falls_back_to_us_holidays():
    assert REGION_CALENDARS["us"] is None
    for region, calendar in REGION_CALENDARS.items():
        if region != "us":
            assert calendar is not None


def test_every_event_has_a_valid_month_and_day_range():
    for region, holidays in ALL_REGION_ARRAYS.items():
        for h in holidays:
            assert 1 <= h.month <= 12, f"{region}/{h.name}: bad month {h.month}"
            assert 1 <= h.day_start <= 31, f"{region}/{h.name}: bad day_start {h.day_start}"
            assert h.day_start <= h.day_end <= 31, f"{region}/{h.name}: bad day_end {h.day_end}"


def test_every_event_has_a_known_type():
    for region, holidays in ALL_REGION_ARRAYS.items():
        for h in holidays:
            assert h.event_type in VALID_EVENT_TYPES, f"{region}/{h.name}: unknown type {h.event_type}"


def test_every_event_has_at_least_one_color():
    for region, holidays in ALL_REGION_ARRAYS.items():
        for h in holidays:
            assert len(h.colors) >= 1, f"{region}/{h.name}: no colors"


def test_usmc_birthday_is_the_only_sacred_event():
    sacred = [h.name for h in US_HOLIDAYS if h.event_type == "sacred"]
    assert sacred == ["USMC Birthday"]


def test_global_floating_includes_all_4_pagan_cross_quarter_days():
    pagan_names = {h.name for h in GLOBAL_FLOATING if h.category == "pagan"}
    assert pagan_names == {"Imbolc", "Beltane", "Lughnasadh", "Samhain"}

"""Tests for the pure-Python config-entry-dict -> scheduling-dataclass adapters.

Imported the same way as tests/scheduling/'s other tests (via the
`custom_components/chromacal` pythonpath entry in pytest.ini) so this stays
Docker-free too — scheduling/bridge.py has zero HA imports itself.
"""

from __future__ import annotations

from scheduling.bridge import build_light_config, build_schedule_config


def test_build_schedule_config_copies_region_and_categories():
    config = build_schedule_config("ca", {"federal": True, "cultural": False})
    assert config.region == "ca"
    assert config.categories == {"federal": True, "cultural": False}


def test_build_schedule_config_defaults_are_empty():
    config = build_schedule_config("us", {})
    assert config.pagan_extended_nights is False
    assert config.skipped_events == frozenset()
    assert config.tonight_skips == frozenset()
    assert config.collision_preferences == {}
    assert config.tonight_pick == {}
    assert config.color_overrides == {}


def test_build_schedule_config_accepts_optional_extras():
    config = build_schedule_config(
        "us",
        {"federal": True},
        pagan_extended_nights=True,
        skipped_events=frozenset({"Halloween"}),
        tonight_pick={"Porch": "Litha"},
    )
    assert config.pagan_extended_nights is True
    assert config.skipped_events == frozenset({"Halloween"})
    assert config.tonight_pick == {"Porch": "Litha"}


def test_build_light_config_reads_expected_keys():
    light_data = {
        "name": "Front Porch",
        "entity": "light.front_porch",
        "end_type": "time",
        "end_time": "23:00",
        "warmwhite_enabled": True,
        "warmwhite_time": "22:00",
    }
    light = build_light_config(light_data)
    assert light.name == "Front Porch"
    assert light.end_type == "time"
    assert light.end_time == "23:00"
    assert light.warmwhite_enabled is True
    assert light.warmwhite_time == "22:00"
    assert light.start_offset == 0


def test_build_light_config_falls_back_to_defaults_for_missing_keys():
    light = build_light_config({})
    assert light.name == ""
    assert light.end_type == "time"
    assert light.end_time is None
    assert light.warmwhite_enabled is True
    assert light.warmwhite_time is None

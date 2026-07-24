"""Adapts a ChromaCal config entry's plain dicts into this package's
dataclasses. Pure Python, zero Home Assistant imports.

Deliberately uses the light-config dict's literal string keys ("name",
"end_type", etc.) rather than importing const.py's CONF_* aliases for them:
const.py lives one level up in custom_components/chromacal/, and reaching it
would need a `..const` relative import — which breaks the "scheduling/ is
importable as its own top-level package" trick tests/scheduling/ relies on
to stay Docker-free (see pytest.ini's pythonpath entry). These keys are
config_flow.py's own CONF_* values; keep them in sync if those ever change.
"""

from __future__ import annotations

from typing import Any

from .engine import LightConfig, ScheduleConfig


def build_schedule_config(
    region: str,
    categories: dict[str, bool],
    *,
    pagan_extended_nights: bool = False,
    skipped_events: frozenset[str] = frozenset(),
    tonight_skips: frozenset[str] = frozenset(),
    collision_preferences: dict[str, str] | None = None,
    tonight_pick: dict[str, str] | None = None,
    color_overrides: dict[str, tuple[str, ...]] | None = None,
) -> ScheduleConfig:
    """Build a ScheduleConfig from a config entry's stored region/categories.

    The keyword-only extras (skips, collision preferences, tonight's pick,
    color overrides) aren't collected by the Phase 1 config flow yet — those
    arrive as switch/button entities and an options flow in a later phase —
    so they default to empty here.
    """
    return ScheduleConfig(
        region=region,
        categories=dict(categories),
        pagan_extended_nights=pagan_extended_nights,
        skipped_events=frozenset(skipped_events),
        tonight_skips=frozenset(tonight_skips),
        collision_preferences=dict(collision_preferences or {}),
        tonight_pick=dict(tonight_pick or {}),
        color_overrides=dict(color_overrides or {}),
    )


def build_light_config(light_data: dict[str, Any]) -> LightConfig:
    """Build a LightConfig from one entry in a config entry's `lights` list.

    start_offset, warmwhite_kelvin_mireds, and warmwhite_color aren't
    collected by the Phase 1 wizard (advanced fields deferred to a later
    options flow), so they default rather than reading config keys that
    don't exist yet. fade_in/fade_out ARE collected by the wizard and read
    here for real.
    """
    return LightConfig(
        name=light_data.get("name", ""),
        end_type=light_data.get("end_type", "time"),
        end_time=light_data.get("end_time"),
        start_offset=0,
        warmwhite_enabled=light_data.get("warmwhite_enabled", True),
        warmwhite_time=light_data.get("warmwhite_time"),
        fade_in=light_data.get("fade_in", 30),
        fade_out=light_data.get("fade_out", 120),
    )

"""The ChromaCal integration.

Runtime state lives on ConfigEntry.runtime_data (the current documented
pattern as of the 2026 HA releases — see
https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/),
rather than the older hass.data[DOMAIN] convention. Storing it there gives
the entry's own typed alias instead of a shared, untyped dict keyed by
DOMAIN, and it's cleaned up automatically with the entry — no manual
hass.data teardown needed in async_unload_entry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_CATEGORIES, CONF_ENTITY, CONF_LIGHTS, CONF_REGION
from .scheduling.bridge import build_light_config, build_schedule_config
from .scheduling.engine import get_enabled_holidays, get_night_segments
from .scheduling.sunset import resolve_sunset_hour

_LOGGER = logging.getLogger(__name__)

# Scheduling entities (sensor/switch/button) land in a later phase.
PLATFORMS: list[str] = []

type ChromaCalConfigEntry = ConfigEntry[ChromaCalData]


@dataclass
class ChromaCalData:
    """Runtime state for one ChromaCal config entry."""

    region: str
    categories: dict[str, bool]
    lights: list[dict[str, Any]]
    # Once-per-day sunset cache, matching v1's sunsetH/sunsetFetchDay -- kept
    # on the entry's own runtime_data rather than a bare module-level global.
    sunset_hour: float | None = None
    sunset_date: date | None = None


def _resolve_sunset(hass: HomeAssistant, data: ChromaCalData) -> float | None:
    """Return today's sunset as a decimal hour, fetched from sun.sun and
    cached once per day on `data`.

    Reads sun.sun's next_setting attribute (not the lower-level astral
    helpers) to match v1's fetchSunset(), which called HA's REST API for
    that same entity. Returns None if sun.sun isn't available for any
    reason -- get_night_segments already falls back to a current-hour
    approximation in that case, matching v1's silent-continue behavior
    rather than crashing setup over a diagnostic feature.
    """
    now = dt_util.now()
    today = now.date()
    if data.sunset_date == today and data.sunset_hour is not None:
        return data.sunset_hour

    sun_state = hass.states.get("sun.sun")
    if sun_state is None:
        _LOGGER.warning("ChromaCal: sun.sun not found, using current-hour fallback for sunset")
        return None

    next_setting_raw = sun_state.attributes.get("next_setting")
    next_setting = dt_util.parse_datetime(next_setting_raw) if next_setting_raw else None
    if next_setting is None:
        _LOGGER.warning(
            "ChromaCal: sun.sun has no next_setting attribute, using current-hour fallback for sunset"
        )
        return None

    sunset_hour = resolve_sunset_hour(now, dt_util.as_local(next_setting))
    data.sunset_hour = sunset_hour
    data.sunset_date = today
    return sunset_hour


def _log_resolved_schedule(hass: HomeAssistant, data: ChromaCalData) -> None:
    """Log tonight's resolved schedule for every configured light.

    Startup-only diagnostic logging — concrete, human-checkable proof that
    the scheduling brain runs through the real custom_components.chromacal
    import path inside HA, not just in isolated tests. No recurring loop and
    no light.turn_on/turn_off calls here; that's the auto-fire state machine,
    a later phase.
    """
    now = dt_util.now()
    sunset_hour = _resolve_sunset(hass, data)
    config = build_schedule_config(data.region, data.categories)
    holidays = get_enabled_holidays(config, now.year)

    for light_data in data.lights:
        light = build_light_config(light_data)
        light_label = light.name or light_data.get(CONF_ENTITY, "unnamed light")
        segments = get_night_segments(now, light, config, holidays, sunset_hour=sunset_hour)
        for segment in segments:
            _LOGGER.info(
                "ChromaCal: %s -> %s (%s tier, %.2fh-%.2fh)",
                light_label,
                segment.event.name,
                segment.event.event_type,
                segment.start_hour,
                segment.end_hour,
            )


async def async_setup_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Set up ChromaCal from a config entry."""
    entry.runtime_data = ChromaCalData(
        region=entry.data[CONF_REGION],
        categories=entry.data[CONF_CATEGORIES],
        lights=entry.data[CONF_LIGHTS],
    )

    _log_resolved_schedule(hass, entry.runtime_data)

    if PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Unload a ChromaCal config entry."""
    if PLATFORMS:
        return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return True

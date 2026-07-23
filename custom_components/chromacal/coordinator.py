"""The DataUpdateCoordinator for ChromaCal.

Recomputes tonight's resolved schedule for every configured light every 5
minutes -- frequent enough that the "currently active segment" tracks
reality across an awareness-split night, infrequent enough to be obviously
not wasteful for data that changes at most a few times a night. Chosen over
bare polling specifically because CLAUDE.md's entity list already commits
to a Catch Up/Sync button (Phase 5+) whose entire job is
`coordinator.async_request_refresh()` -- building the coordinator now means
that button, and any switch/button entities that share this same resolved
schedule, are nearly free later instead of requiring a refactor then.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_ENTITY, DOMAIN
from .scheduling.bridge import build_light_config, build_schedule_config
from .scheduling.engine import get_current_segment, get_enabled_holidays, get_night_segments
from .scheduling.models import NightSegment
from .scheduling.sunset import resolve_sunset_hour

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


@dataclass
class LightSchedule:
    """Tonight's resolved schedule for one configured light."""

    light_entity: str
    light_name: str
    segments: list[NightSegment]
    current_segment: NightSegment | None
    sunset_hour: float | None


class ChromaCalCoordinator(DataUpdateCoordinator[dict[str, LightSchedule]]):
    """Fetches sunset (cached once/day) and recomputes tonight's schedule."""

    def __init__(
        self,
        hass: HomeAssistant,
        region: str,
        categories: dict[str, bool],
        lights: list[dict[str, Any]],
    ) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.region = region
        self.categories = categories
        self.lights = lights
        # Once-per-day sunset cache, matching v1's sunsetH/sunsetFetchDay --
        # lives on this long-lived coordinator instance, not a bare module
        # global, and not recomputed just because _async_update_data() runs
        # more often than once a day (see the Phase 3 plan discussion).
        self.sunset_hour: float | None = None
        self.sunset_date: date | None = None

    def _resolve_sunset(self) -> float | None:
        """Return today's sunset as a decimal hour, cached once per day.

        Reads sun.sun's next_setting attribute (not the lower-level astral
        helpers) to match v1's fetchSunset(), which called HA's REST API
        for that same entity. Returns None if sun.sun isn't available for
        any reason -- get_night_segments() already falls back to a
        current-hour approximation in that case, matching v1's
        silent-continue behavior rather than crashing setup over this.
        """
        now = dt_util.now()
        today = now.date()
        if self.sunset_date == today and self.sunset_hour is not None:
            return self.sunset_hour

        sun_state = self.hass.states.get("sun.sun")
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
        self.sunset_hour = sunset_hour
        self.sunset_date = today
        return sunset_hour

    async def _async_update_data(self) -> dict[str, LightSchedule]:
        now = dt_util.now()
        now_hour = now.hour + now.minute / 60
        sunset_hour = self._resolve_sunset()
        config = build_schedule_config(self.region, self.categories)
        holidays = get_enabled_holidays(config, now.year)

        result: dict[str, LightSchedule] = {}
        for light_data in self.lights:
            light = build_light_config(light_data)
            light_entity = light_data.get(CONF_ENTITY, "")
            segments = get_night_segments(now, light, config, holidays, sunset_hour=sunset_hour)
            current = get_current_segment(segments, now_hour)
            result[light_entity] = LightSchedule(
                light_entity=light_entity,
                light_name=light.name or light_entity,
                segments=segments,
                current_segment=current,
                sunset_hour=sunset_hour,
            )
            if current is not None:
                _LOGGER.info(
                    "ChromaCal: %s -> %s (%s tier, %.2fh-%.2fh)",
                    light.name or light_entity,
                    current.event.name,
                    current.event.event_type,
                    current.start_hour,
                    current.end_hour,
                )

        return result

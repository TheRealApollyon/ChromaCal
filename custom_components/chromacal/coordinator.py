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

Multi-color event cycling (the gap flagged in Phase 4) runs on a separate,
faster ~60s interval -- see async_recheck_color_cycle() and __init__.py's
registration of it -- since it's designed to advance roughly once a minute
and this coordinator's own 5-minute cadence would only sample a fraction
of the cycle, not restore it.

The skip system (Phase 5a) splits similarly by cadence: permanent skip
(self.skipped_events) is a standing setting persisted to the config entry's
options, checked on every refresh like region/categories. Skip-tonight
(self.tonight_skips) resets at exactly local midnight via
ensure_today_candidates(), driven by __init__.py's async_track_time_change
callback rather than this coordinator's own 5-minute cycle -- see the Phase
5a plan discussion for why a scheduled exact-time callback beats polling
for a reset that has one precisely-known trigger instant per day.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_ENTITY, CONF_SKIPPED_EVENTS, DOMAIN
from .scheduling.bridge import build_light_config, build_schedule_config
from .scheduling.engine import (
    LightConfig,
    all_event_names,
    get_candidates_for_date,
    get_current_segment,
    get_desired_fire_key,
    get_enabled_holidays,
    get_night_segments,
)
from .scheduling.fire import FireCommand, build_fire_command
from .scheduling.models import NightSegment
from .scheduling.sunset import resolve_sunset_hour

# Desired-fire-keys that mean "do nothing" -- an existing sunset/sunrise
# automation is assumed to handle these phases, matching v1.
_NO_FIRE_KEYS = ("pre", "warmup")

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
        entry: ConfigEntry,
        region: str,
        categories: dict[str, bool],
        lights: list[dict[str, Any]],
    ) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self._entry = entry
        self.region = region
        self.categories = categories
        self.lights = lights
        # Once-per-day sunset cache, matching v1's sunsetH/sunsetFetchDay --
        # lives on this long-lived coordinator instance, not a bare module
        # global, and not recomputed just because _async_update_data() runs
        # more often than once a day (see the Phase 3 plan discussion).
        self.sunset_hour: float | None = None
        self.sunset_date: date | None = None
        # Last desired-fire-key actually fired per light, matching v1's
        # _lastFireKey -- lives here, not a bare module global, same
        # discipline as the sunset cache above. Keyed by light_entity, the
        # same key used everywhere else on this coordinator (coordinator.data,
        # the sensor's unique_id), not v1's "name || entity" fallback.
        self._last_fire_key: dict[str, str] = {}
        # Last color actually fired for a stable multi-color 'event:X' key,
        # keyed by light_entity -- lets the color-cycle recheck (see
        # async_recheck_color_cycle) detect "has the color-in-cycle advanced"
        # independently of the coarse key-change gate above. Always read with
        # .get(), never [] -- "not yet seeded" (a light's first-ever fire) is
        # a real, expected state, not a bug.
        self._last_fired_rgb_color: dict[str, list[int]] = {}
        # Permanent skip: matches v1's CFG.skippedEvents (global, per-event
        # name, not per-light). Seeded from config entry OPTIONS (not the
        # switch entity's own RestoreEntity storage) because these switches
        # are static -- see the Phase 5a plan discussion for why options is
        # still the right home even though nothing here gets recreated.
        self.skipped_events: set[str] = set(entry.options.get(CONF_SKIPPED_EVENTS, []))
        # Skip-tonight: matches v1's CFG.tonightSkips, but flattened to a
        # single in-memory set + a date guard (the coordinator only ever
        # cares about *today's* key) rather than v1's date-keyed dict of
        # every day that ever had a skip. Deliberately NOT persisted to
        # config entry options like skipped_events above -- if HA restarts
        # while a tonight-skip is active, it resets and the suppressed event
        # resumes. Accepted as-designed: HA restarts are rare and deliberate
        # (an update, a reboot), unlike v1's browser tab, which reloaded
        # constantly just from normal use -- the persistence v1 needed to
        # survive *that* churn doesn't apply here. Reset precisely at local
        # midnight via ensure_today_candidates(), not just whenever the
        # 5-minute cycle happens to notice (see __init__.py's
        # async_track_time_change registration).
        self.tonight_skips: set[str] = set()
        self.tonight_skips_date: date | None = None
        # Which event names are skippable *tonight* -- drives the dynamic
        # tonight-skip switches (see switch.py). Recomputed alongside the
        # tonight_skips reset above, same date guard.
        self.todays_candidate_names: set[str] = set()

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

    def ensure_today_candidates(self, now: datetime) -> None:
        """Reset tonight_skips and recompute today's skippable candidates
        if the date has changed.

        Called from two places: __init__.py's async_track_time_change
        callback, pinned to exactly local midnight -- the precise,
        near-zero-lag path this exists for -- and defensively from
        _async_update_data()'s own 5-minute cycle, which only matters
        right after HA startup (before that callback has had a chance to
        fire) or if a callback were somehow missed. The date guard makes
        calling this from both places safe and cheap: the second call on
        any given day is just an equality check.
        """
        today = now.date()
        if self.tonight_skips_date == today:
            return
        self.tonight_skips = set()
        self.tonight_skips_date = today
        config = build_schedule_config(
            self.region, self.categories, skipped_events=frozenset(self.skipped_events)
        )
        holidays = get_enabled_holidays(config, now.year)
        candidates = get_candidates_for_date(holidays, now.month, now.day)
        self.todays_candidate_names = {c.name for c in candidates}
        self.async_update_listeners()  # lets switch.py add/remove tonight-skip entities

    def get_all_event_names(self) -> list[str]:
        """Every event name in the enabled region+categories calendar --
        drives the static, always-present permanent-skip switches."""
        config = build_schedule_config(self.region, self.categories)
        holidays = get_enabled_holidays(config, dt_util.now().year)
        return all_event_names(holidays)

    async def async_set_permanent_skip(self, event_name: str, skipped: bool) -> None:
        """Skip (or restore) an event permanently. Always reversible --
        this is the same set either direction, per CLAUDE.md's hard rule;
        there is no separate one-way "permanent" code path.
        """
        if skipped:
            self.skipped_events.add(event_name)
        else:
            self.skipped_events.discard(event_name)
        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_SKIPPED_EVENTS: sorted(self.skipped_events)},
        )
        # async_refresh(), not async_request_refresh() -- the latter is
        # debounced (meant for coalescing rapid automatic triggers), which
        # left the switch's own reported state stale immediately after a
        # toggle in testing. A direct user action should update
        # deterministically and immediately, not wait out a debounce window.
        await self.async_refresh()

    async def async_set_tonight_skip(self, event_name: str, skipped: bool) -> None:
        """Skip (or restore) an event for tonight only. In-memory only --
        see tonight_skips' field docstring for why, and
        ensure_today_candidates() for how/when it resets.
        """
        if skipped:
            self.tonight_skips.add(event_name)
        else:
            self.tonight_skips.discard(event_name)
        await self.async_refresh()  # same reasoning as async_set_permanent_skip above

    async def _async_update_data(self) -> dict[str, LightSchedule]:
        now = dt_util.now()
        now_hour = now.hour + now.minute / 60
        self.ensure_today_candidates(now)
        sunset_hour = self._resolve_sunset()
        config = build_schedule_config(
            self.region,
            self.categories,
            skipped_events=frozenset(self.skipped_events),
            tonight_skips=frozenset(self.tonight_skips),
        )
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

            await self._auto_fire(light_entity, light, segments, sunset_hour, now)

        return result

    async def _auto_fire(
        self,
        light_entity: str,
        light: LightConfig,
        segments: list[NightSegment],
        sunset_hour: float | None,
        now: datetime,
    ) -> None:
        """Fire a light.turn_on/turn_off when the desired state (the coarse
        tier/event key) has changed.

        Ports getDesiredFireKey()/fireScheduledCommand()'s firing decision
        from chromacal.html. Only owns key transitions -- advancing the
        active color within a stable multi-color key is
        async_recheck_color_cycle()'s job, not this method's (see
        scheduling/fire.py's module docstring for why fireScheduledCommand
        alone never produced that in v1 either).
        """
        if not light_entity:
            return

        desired_key = get_desired_fire_key(now, light, segments, sunset_hour)

        if light_entity not in self._last_fire_key:
            # First-update guard, ported faithfully: observe what SHOULD be
            # happening without firing, so a fresh coordinator (HA startup)
            # doesn't immediately re-fire a command that's probably already
            # correct. Matches v1's page-load behavior exactly.
            self._last_fire_key[light_entity] = (
                desired_key if desired_key in _NO_FIRE_KEYS else "__init__"
            )
            _LOGGER.info(
                "ChromaCal: %s auto-fire initialized, observing (no fire on first load)",
                light.name or light_entity,
            )
            return

        if desired_key in _NO_FIRE_KEYS or desired_key == self._last_fire_key[light_entity]:
            return

        command = build_fire_command(desired_key, light, segments, now)

        # All state mutation happens here, synchronously, before the await
        # below -- not after. None of these statements themselves await, so
        # asyncio can't interleave another callback (e.g. the 60s color-cycle
        # recheck) partway through them: by the time control could possibly
        # yield to another coroutine, _last_fire_key and _last_fired_rgb_color
        # are already mutually consistent. Seeding after the await would
        # leave a real window where a key transition was visible but its
        # color wasn't yet recorded -- see the Phase 4c plan discussion.
        self._last_fire_key[light_entity] = desired_key
        if command is not None and "rgb_color" in command.service_data:
            self._last_fired_rgb_color[light_entity] = command.service_data["rgb_color"]
        else:
            self._last_fired_rgb_color.pop(light_entity, None)

        if command is None:
            return

        await self._call_fire_command(light_entity, light, desired_key, command)

    async def _call_fire_command(
        self, light_entity: str, light: LightConfig, key: str, command: FireCommand
    ) -> None:
        """Issue the actual service call and log the result or failure."""
        try:
            await self.hass.services.async_call(
                command.domain,
                command.service,
                {"entity_id": light_entity, **command.service_data},
                blocking=True,
            )
            _LOGGER.info(
                "ChromaCal: fired %s.%s on %s (%s) -> %s",
                command.domain,
                command.service,
                light.name or light_entity,
                key,
                command.service_data,
            )
        except HomeAssistantError as err:
            # Mirrors v1's catch(e) around fireScheduledCommand -- a failed
            # service call (entity unavailable, etc.) shouldn't crash the
            # whole coordinator update. Deliberately narrower than v1's bare
            # catch: an unexpected error in this method's own logic (not a
            # service-call failure) should still surface loudly rather than
            # being swallowed, per CLAUDE.md's known-failure-pattern note.
            _LOGGER.error(
                "ChromaCal: auto-fire error for %s: %s", light.name or light_entity, err
            )

    async def async_recheck_color_cycle(self, now: datetime) -> None:
        """Re-fire a stable multi-color 'event:X' key when its active color
        has advanced since it was last sent.

        Runs on its own ~60s interval (see __init__.py), decoupled from this
        coordinator's own 5-minute refresh: v1's real cadence for color
        cycling (inherited from the Blueprint automation it relied on) was
        ~60s, and checking only every 5 minutes would skip most of a cycle
        rather than step through it. Reuses self.data (already computed by
        the 5-minute refresh) instead of recomputing holidays/segments here
        -- only the cheap "has the color changed" check runs fine-grained.

        Only acts on a light whose coarse key is already an established
        'event:X' matching what self.data currently shows -- if the schedule
        has moved on since the key was set (a real transition mid-flight),
        that mismatch is caught below and this is a safe no-op; the coarse
        gate in _auto_fire owns transitions, this only owns color-within-key.
        """
        for light_entity, schedule in self.data.items():
            last_key = self._last_fire_key.get(light_entity)
            if not last_key or not last_key.startswith("event:"):
                continue  # not currently driving a stable event window

            current = schedule.current_segment
            if current is None or f"event:{current.event.name}" != last_key:
                continue  # stale relative to a transition in progress elsewhere; skip

            light_data = next(
                (l for l in self.lights if l.get(CONF_ENTITY) == light_entity), None
            )
            if light_data is None:
                continue
            light = build_light_config(light_data)

            command = build_fire_command(last_key, light, schedule.segments, now)
            if command is None or "rgb_color" not in command.service_data:
                continue  # single-color event, or key no longer resolves -- nothing to cycle

            if self._last_fired_rgb_color.get(light_entity) == command.service_data["rgb_color"]:
                continue  # same color as last time -- nothing changed, don't refire

            # Seed before the await, same reasoning as _auto_fire above.
            self._last_fired_rgb_color[light_entity] = command.service_data["rgb_color"]
            await self._call_fire_command(light_entity, light, last_key, command)

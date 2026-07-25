"""The DataUpdateCoordinator for ChromaCal.

Recomputes tonight's resolved schedule for every configured light every 5
minutes -- frequent enough that the "currently active segment" tracks
reality across an awareness-split night, infrequent enough to be obviously
not wasteful for data that changes at most a few times a night. Chosen over
bare polling specifically because CLAUDE.md's entity list already commits
to switch/button entities that share this same resolved schedule, which
are nearly free to add on top of a coordinator instead of requiring a
refactor later.

Quick-control actions (Phase 5b): 21 Gun Salute, Force White, Emergency
Mode, and Catch Up/Sync all needed a shared primitive this module didn't
have yet -- async_force_fire() recomputes and unconditionally re-issues
the current desired command, bypassing the _last_fire_key/
_last_fired_rgb_color gate that _auto_fire normally uses to avoid
redundant firing. (Catch Up/Sync is NOT just coordinator.async_refresh()
-- that was this docstring's original assumption, checked and found wrong
during the Phase 5b plan: refresh() recomputes self.data for the sensors
but leaves the fire gate untouched, so a light that's drifted out of sync
with what the coordinator last told it wouldn't get re-fired at all.)
Salute, Force White, and Emergency Mode also needed something v1 had and
this coordinator didn't: _manual_override, a per-light suppression map so
auto-fire (and the color-cycle recheck) stand down while one of these is
active, ported from v1's _schedOverride.

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

import asyncio
import contextlib
import logging
from collections.abc import Callable, Coroutine, Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_EMERGENCY_WAS_ACTIVE, CONF_ENTITY, CONF_SKIPPED_EVENTS, DOMAIN
from .scheduling.actions import (
    EMERGENCY_TRANSITION,
    build_force_white_command,
    get_emergency_sequence,
    get_salute_steps,
)
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
FORCE_WHITE_OVERRIDE_MINUTES = 30  # matches v1's OVERRIDE_MINS -- real-world tuned, not arbitrary
EMERGENCY_FIRE_INTERVAL = timedelta(seconds=5)  # matches v1's default CFG.emergencyInterval

# _manual_override source tags -- which mechanism currently owns a light's
# override, so cleanup only ever clears an entry it still owns (see
# ManualOverride and _clear_override_if_owned). Precedence, highest first:
# emergency > salute > force_white. The only place that matters operationally
# is async_start_emergency(), which cancels a running Salute before taking
# over; everything else (Force White vs. either) is handled for free by
# ownership-aware overwriting/clearing, no extra guard needed.
_OVERRIDE_SOURCE_FORCE_WHITE = "force_white"
_OVERRIDE_SOURCE_SALUTE = "salute"
_OVERRIDE_SOURCE_EMERGENCY = "emergency"


@dataclass(frozen=True)
class ManualOverride:
    """One light's current override: who owns it, and until when.

    expires_at=None means indefinite -- suppressed until whoever set it
    (Salute, Emergency Mode) explicitly clears it. A real datetime means
    bounded (Force White's 30-minute window); self-expiry past that point
    is the caller's job via async_call_later, not this dataclass's.

    Added in the multi-source cancel/Stop phase after a real bug: with a
    bare `datetime | None` and no owner tag, one source's cleanup could
    silently clear a *different* source's still-active override on the
    same light (e.g. Salute finishing while Emergency Mode had since taken
    over the same light) -- see _clear_override_if_owned().
    """

    source: str
    expires_at: datetime | None = None


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
        # Manual override: suppresses auto-fire and the color-cycle recheck
        # for a light, ported from v1's _schedOverride. See ManualOverride
        # for the source/expiry shape. In-memory only, like tonight_skips
        # above -- losing an active override on an HA restart is an
        # accepted tradeoff for Force White and Salute (same reasoning as
        # tonight_skips: restarts are rare/deliberate). NOT accepted as-is
        # for Emergency Mode specifically -- silently losing an active
        # safety broadcast is a worse failure than a decorative override
        # resetting early, so that one gets its own narrow persisted
        # breadcrumb (CONF_EMERGENCY_WAS_ACTIVE) purely to warn a human it
        # happened, not to resume the broadcast -- see
        # async_check_emergency_breadcrumb().
        self._manual_override: dict[str, ManualOverride] = {}
        # Re-entry guard for the Salute sequence -- checked and set
        # synchronously, before any await, so two rapid button presses
        # can't both pass the guard. Same atomicity discipline as the
        # Phase 4c auto-fire race-condition fix.
        self.salute_active: bool = False
        # The running Salute task, so a second button press (or Emergency
        # Mode preempting it) can actually cancel it -- see
        # async_cancel_salute(). None whenever salute_active is False.
        self._salute_task: asyncio.Task[None] | None = None
        # Emergency Mode's live state. Always starts fresh/False on a new
        # coordinator -- never restored from CONF_EMERGENCY_WAS_ACTIVE,
        # which is a one-shot breadcrumb, not resumable state.
        self.emergency_active: bool = False
        self._emergency_unsub: Callable[[], None] | None = None

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

    def _is_overridden(self, light_entity: str) -> bool:
        """True if auto-fire and color-cycling should stand down for this
        light right now. Ported from v1's isOverridden gate. Absent from
        _manual_override means no override; see ManualOverride for what
        an entry's source/expires_at mean.
        """
        override = self._manual_override.get(light_entity)
        if override is None:
            return False
        return override.expires_at is None or dt_util.now() < override.expires_at

    def _clear_override_if_owned(self, light_entity: str, source: str) -> None:
        """Clear light_entity's override only if `source` still owns it.

        The ownership-aware alternative to a blind .pop() -- without this,
        one source's cleanup (Force White's resume timer, Salute's finally
        block, Emergency's stop) can clear a *different* source's still-
        active override on the same light, if that source took over in
        the meantime. Every cleanup path uses this instead of popping
        directly; async_stop_all_overrides() is the one deliberate
        exception, since an unconditional clear is exactly what "stop
        everything" means.
        """
        current = self._manual_override.get(light_entity)
        if current is not None and current.source == source:
            self._manual_override.pop(light_entity, None)

    def _light_config_for(self, light_entity: str) -> LightConfig | None:
        """Look up and build the LightConfig for one configured light by
        entity id. None if it's no longer configured (defensive; shouldn't
        happen for a light_entity sourced from self.lights itself)."""
        light_data = next(
            (l for l in self.lights if l.get(CONF_ENTITY) == light_entity), None
        )
        return build_light_config(light_data) if light_data is not None else None

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

        if self._is_overridden(light_entity):
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
            if self._is_overridden(light_entity):
                continue  # Force White / Salute / Emergency Mode owns this light right now

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

    async def async_force_fire(self, light_entities: Iterable[str] | None = None) -> None:
        """Recompute and unconditionally re-issue the current desired
        command for the given lights (or every configured light),
        bypassing the _last_fire_key/_last_fired_rgb_color gate that
        _auto_fire normally uses to avoid redundant firing.

        This is the real Catch Up/Sync primitive -- confirmed against what
        chromacal.html's forceSyncAllBridges() actually needed to
        accomplish, not its literal implementation (which republished to a
        bridge helper entity that no longer exists in v2). The functional
        need it served -- make the physical light reflect what SHOULD be
        showing right now, even if this coordinator's own bookkeeping
        thinks nothing changed -- maps onto bypassing the fire gate, not
        onto coordinator.async_refresh(): refresh() recomputes self.data
        for the sensors but leaves the gate untouched, so a light that's
        drifted out of sync with what the coordinator last told it
        wouldn't get re-fired at all.

        Also the shared "resume the real schedule right now" primitive for
        when Salute finishes, Force White's window expires, and Emergency
        Mode is cancelled. v1 resumed by deleting _lastFireKey and calling
        update() -- that doesn't translate here: this coordinator's
        first-update guard would just re-observe and defer the actual fire
        by a full 5-minute cycle instead of firing immediately, which is
        worse than doing nothing.
        """
        now = dt_util.now()
        now_hour = now.hour + now.minute / 60
        sunset_hour = self._resolve_sunset()
        config = build_schedule_config(
            self.region,
            self.categories,
            skipped_events=frozenset(self.skipped_events),
            tonight_skips=frozenset(self.tonight_skips),
        )
        holidays = get_enabled_holidays(config, now.year)
        targets = set(light_entities) if light_entities is not None else None

        for light_data in self.lights:
            light_entity = light_data.get(CONF_ENTITY, "")
            if not light_entity or (targets is not None and light_entity not in targets):
                continue
            light = build_light_config(light_data)
            segments = get_night_segments(now, light, config, holidays, sunset_hour=sunset_hour)
            desired_key = get_desired_fire_key(now, light, segments, sunset_hour)
            if desired_key in _NO_FIRE_KEYS:
                continue

            command = build_fire_command(desired_key, light, segments, now)

            # Reseed the gate before the await, same reasoning as _auto_fire.
            self._last_fire_key[light_entity] = desired_key
            if command is not None and "rgb_color" in command.service_data:
                self._last_fired_rgb_color[light_entity] = command.service_data["rgb_color"]
            else:
                self._last_fired_rgb_color.pop(light_entity, None)

            if command is None:
                continue
            await self._call_fire_command(light_entity, light, desired_key, command)

    def async_fire_and_forget(
        self, coro: Coroutine[Any, Any, None], name: str
    ) -> asyncio.Task[None]:
        """Schedule a coroutine to run without the caller awaiting it,
        tied to this config entry's lifecycle -- used by button.py so a
        button press (Salute, Catch Up/Sync, Force White) returns
        immediately instead of blocking the frontend/automation caller for
        however long the underlying action takes. Returns the Task so
        callers that need to cancel it later (async_toggle_salute) can.

        entry.async_create_task(), not hass.async_create_task(): the
        latter's own docstring says it's intended for HA core internal use
        only and integrations should use the config-entry-scoped methods
        instead -- caught during the Phase 5b callback-dispatch audit.
        The practical difference: HA actually waits for entry-tracked
        tasks during this config entry's own unload, not just global
        shutdown, so unloading ChromaCal mid-Salute is handled correctly.
        """
        return self._entry.async_create_task(self.hass, coro, name=name)

    async def async_catch_up(self) -> None:
        """Catch Up/Sync button: force every configured light to match
        what the schedule says right now, regardless of whether this
        coordinator thinks anything has changed."""
        await self.async_force_fire()

    async def async_toggle_salute(self, pace: str = "standard") -> None:
        """21 Gun Salute button's actual entry point: press to start,
        press again while running to cancel. A single method so button.py
        never has to know which action applies -- it just calls this.

        Declines (logs, no-ops) if Emergency Mode is active: Emergency
        outranks Salute (see async_start_emergency(), which is the
        reverse direction -- it cancels a running Salute automatically
        rather than declining, since Emergency starting is the one place
        a higher-precedence source needs to actively preempt a lower one
        instead of just naturally overwriting its override entry).
        """
        if self.salute_active:
            await self.async_cancel_salute()
            return
        if self.emergency_active:
            _LOGGER.warning("ChromaCal: Emergency Mode is active, ignoring Salute press")
            return
        self._salute_task = self.async_fire_and_forget(
            self.async_fire_salute(pace), name="chromacal_salute"
        )

    async def async_cancel_salute(self) -> None:
        """Cancel a running Salute and resume the real schedule
        immediately. Only meaningful while salute_active is True.

        The actual cleanup (clearing owned overrides, resetting
        salute_active, notifying listeners, force-firing the resume)
        lives entirely in async_fire_salute()'s own finally block --
        Python runs finally on a cancelled task exactly the same as on
        normal completion, so there's nothing extra to do here beyond
        triggering the cancellation and waiting for that unwind to land.
        """
        if self._salute_task is None:
            return
        self._salute_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._salute_task
        self._salute_task = None

    async def async_fire_salute(self, pace: str = "standard") -> None:
        """21 Gun Salute: 3 volleys + Taps + fade-out, broadcast across
        every configured light (no per-light participation opt-out yet --
        see CLAUDE.md's deferred-decisions note; all lights participate
        for now), then resumes the real schedule immediately via
        async_force_fire().

        Not called directly by button.py -- see async_toggle_salute(),
        which owns the start-vs-cancel decision and re-entry guarding.
        """
        self.salute_active = True
        # Without this, ChromaCalSaluteButton's `running` attribute (reads
        # coordinator.salute_active) never actually gets re-published to
        # HA's state machine -- caught during the Phase 5b listener-
        # notification audit, same bug class as the Emergency switch fix
        # above, a third occurrence of the same oversight.
        self.async_update_listeners()

        lights_by_entity = {
            light_data[CONF_ENTITY]: build_light_config(light_data)
            for light_data in self.lights
            if light_data.get(CONF_ENTITY)
        }
        for light_entity in lights_by_entity:
            self._manual_override[light_entity] = ManualOverride(source=_OVERRIDE_SOURCE_SALUTE)

        _LOGGER.info(
            "ChromaCal: 21 Gun Salute commencing -- 3 volleys, %d light(s)", len(lights_by_entity)
        )
        try:
            for step in get_salute_steps(pace):
                if step.rgb is None:
                    command = FireCommand("light", "turn_off", {"transition": step.transition})
                else:
                    r, g, b = step.rgb
                    command = FireCommand(
                        "light",
                        "turn_on",
                        {
                            "rgb_color": [r, g, b],
                            "brightness_pct": step.brightness_pct,
                            "transition": step.transition,
                        },
                    )
                await asyncio.gather(
                    *(
                        self._call_fire_command(light_entity, light, step.label, command)
                        for light_entity, light in lights_by_entity.items()
                    )
                )
                await asyncio.sleep(step.hold_ms / 1000)
            _LOGGER.info("ChromaCal: 21 Gun Salute complete -- resuming schedule")
        finally:
            # Runs identically whether the loop above finished normally or
            # was interrupted by cancellation (async_cancel_salute) --
            # Python guarantees finally executes on both exit paths.
            for light_entity in lights_by_entity:
                self._clear_override_if_owned(light_entity, _OVERRIDE_SOURCE_SALUTE)
            self.salute_active = False
            self.async_update_listeners()  # same reasoning as above, the reverse transition
            await self.async_force_fire(lights_by_entity.keys())

    async def async_start_emergency(self, pattern: str = "red-blue") -> None:
        """Emergency Mode: broadcast an alternating color pattern across
        every configured light until async_stop_emergency() is called.
        Backing entity is a switch, not a button -- this is genuinely
        start/stop with a real running state, not a fire-once trigger (see
        the Phase 5b plan discussion for why that's a deliberate deviation
        from CLAUDE.md's literal "button" wording for this one action).

        Emergency outranks Salute: starting Emergency while a Salute is
        running cancels it first, rather than letting both loops fight
        over the same light on independent cadences (confirmed as a real,
        observable conflict before this fix -- see the multi-source
        cancel/Stop plan discussion). This is the one place precedence
        needs an active preempt; Force White vs. either is handled for
        free by ownership-aware override overwriting, no guard needed.
        """
        if self.emergency_active:
            return
        if self.salute_active:
            await self.async_cancel_salute()
        self.emergency_active = True

        lights_by_entity = {
            light_data[CONF_ENTITY]: build_light_config(light_data)
            for light_data in self.lights
            if light_data.get(CONF_ENTITY)
        }
        for light_entity in lights_by_entity:
            # Indefinite, until async_stop_emergency. Unconditional
            # overwrite -- if Force White owned this light's override,
            # Emergency simply takes over; Force White's own resume timer
            # will no-op later since it checks ownership before clearing.
            self._manual_override[light_entity] = ManualOverride(source=_OVERRIDE_SOURCE_EMERGENCY)

        # Breadcrumb only -- not resumed from on restart, see
        # async_check_emergency_breadcrumb() and this flag's own docstring
        # in const.py.
        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_EMERGENCY_WAS_ACTIVE: True},
        )
        _LOGGER.error(
            "ChromaCal: EMERGENCY MODE ACTIVATED -- %d light(s), pattern=%s",
            len(lights_by_entity),
            pattern,
        )

        sequence = get_emergency_sequence(pattern)
        cycle_index = {"value": 0}

        async def _fire(_now: datetime) -> None:
            color = sequence[cycle_index["value"] % len(sequence)]
            cycle_index["value"] += 1
            if color is None:
                command = FireCommand("light", "turn_off", {"transition": EMERGENCY_TRANSITION})
            else:
                r, g, b = color
                command = FireCommand(
                    "light",
                    "turn_on",
                    {"rgb_color": [r, g, b], "brightness_pct": 100, "transition": EMERGENCY_TRANSITION},
                )
            await asyncio.gather(
                *(
                    self._call_fire_command(light_entity, light, "emergency", command)
                    for light_entity, light in lights_by_entity.items()
                )
            )

        await _fire(dt_util.utcnow())  # fire immediately on activation, matching v1
        self._emergency_unsub = async_track_time_interval(
            self.hass, _fire, EMERGENCY_FIRE_INTERVAL, name="chromacal_emergency"
        )
        # Also tied to entry unload (e.g. the integration is removed/reloaded
        # while HA keeps running) -- calling an already-cancelled unsub from
        # async_stop_emergency later is a safe no-op, same pattern already
        # used for switch.py's dynamic tonight-skip listener.
        self._entry.async_on_unload(self._emergency_unsub)

        # Without this, the switch's own is_on keeps reporting stale ('off')
        # until some unrelated coordinator update happens to fire next --
        # same bug already caught and fixed once for the skip switches in
        # Phase 5a. async_update_listeners() (not a full async_refresh())
        # is the right-sized tool: just tell CoordinatorEntity listeners to
        # re-read state and write it, without re-running _async_update_data.
        self.async_update_listeners()

    async def async_stop_emergency(self) -> None:
        """Cancel Emergency Mode and resume the real schedule immediately."""
        if not self.emergency_active:
            return
        self.emergency_active = False
        self.async_update_listeners()  # same reasoning as async_start_emergency above
        if self._emergency_unsub is not None:
            self._emergency_unsub()
            self._emergency_unsub = None

        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_EMERGENCY_WAS_ACTIVE: False},
        )
        _LOGGER.warning("ChromaCal: Emergency Mode cancelled -- resuming schedule")

        light_entities = [ld[CONF_ENTITY] for ld in self.lights if ld.get(CONF_ENTITY)]
        for light_entity in light_entities:
            self._clear_override_if_owned(light_entity, _OVERRIDE_SOURCE_EMERGENCY)
        await self.async_force_fire(light_entities)

    async def async_fire_force_white(self, light_entity: str) -> None:
        """Force White: immediately set one light to its own configured
        warm-white Kelvin at full brightness, then suppress auto-fire for
        that light for FORCE_WHITE_OVERRIDE_MINUTES before automatically
        resuming the real schedule -- matches v1's OVERRIDE_MINS exactly,
        a real-world-tuned value, not an arbitrary one to relitigate here.

        Uses the light's own warmwhite_kelvin_mireds (option (a) from the
        Phase 5b plan discussion) rather than a paired Kelvin-picker
        entity -- matches where the options-flow phase is already headed
        for per-light config.
        """
        light = self._light_config_for(light_entity)
        if light is None:
            return

        kelvin = round(1_000_000 / (light.warmwhite_kelvin_mireds or 250))
        command = build_force_white_command(kelvin)
        self._manual_override[light_entity] = ManualOverride(
            source=_OVERRIDE_SOURCE_FORCE_WHITE,
            expires_at=dt_util.now() + timedelta(minutes=FORCE_WHITE_OVERRIDE_MINUTES),
        )
        await self._call_fire_command(light_entity, light, "force_white", command)

        async def _resume(_now: datetime) -> None:
            # Ownership-aware: if Salute or Emergency took over this light
            # since this timer was scheduled, this must NOT clear their
            # override -- see _clear_override_if_owned() and the
            # multi-source cancel/Stop plan discussion for the bug this
            # closes.
            self._clear_override_if_owned(light_entity, _OVERRIDE_SOURCE_FORCE_WHITE)
            await self.async_force_fire([light_entity])

        async_call_later(
            self.hass, timedelta(minutes=FORCE_WHITE_OVERRIDE_MINUTES), _resume
        )

    async def async_stop_all_overrides(self) -> None:
        """button.chromacal_stop: cancel whatever override is currently
        active -- a running Salute, Emergency Mode, or any light's Force
        White window -- across every configured light, then resolve and
        push the real current schedule. A third, simpler entry point into
        the same cancel-and-resume action as Salute's own press-again
        (async_toggle_salute) and the Emergency switch's turn_off -- both
        of those stay as they are; this is for someone who just wants
        "make it normal again" without knowing what's currently wrong.

        Must be a safe no-op if nothing is overridden: each branch below
        is itself a no-op when its condition is false, and the final
        force-fire only runs if there was actually a Force White entry (or
        anything else) left to resolve -- so with nothing active, this
        issues zero service calls.
        """
        if self.salute_active:
            await self.async_cancel_salute()
        if self.emergency_active:
            await self.async_stop_emergency()
        if self._manual_override:
            # Whatever's left at this point can only be Force White
            # entries (Salute/Emergency's own cleanup above already
            # cleared theirs) -- an unconditional clear, not ownership-
            # checked, since "stop everything" is exactly what this button
            # means; no other source's cleanup should be racing with it.
            light_entities = list(self._manual_override)
            self._manual_override.clear()
            await self.async_force_fire(light_entities)

    async def async_check_emergency_breadcrumb(self) -> None:
        """Called once from __init__.py right after coordinator setup. If
        CONF_EMERGENCY_WAS_ACTIVE is still True, HA went down while
        Emergency Mode was actively broadcasting -- log a warning and
        raise a persistent_notification so a human actually sees it (a log
        line alone isn't enough given what Emergency Mode is for -- see
        the Phase 5b plan discussion), then clear the flag so it doesn't
        refire on a later, unrelated restart. Emergency Mode's own runtime
        state is never resumed from this -- it's already fresh/False from
        __init__, by design.
        """
        if not self._entry.options.get(CONF_EMERGENCY_WAS_ACTIVE, False):
            return

        _LOGGER.warning(
            "ChromaCal: Emergency Mode was active before restart and is no longer running"
        )
        persistent_notification.async_create(
            self.hass,
            (
                "Emergency Mode was active before Home Assistant restarted and "
                "is **no longer running**. If you still need it, turn "
                "`switch.chromacal_emergency_mode` back on."
            ),
            title="ChromaCal: Emergency Mode stopped",
            notification_id=f"{DOMAIN}_emergency_was_active",
        )
        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_EMERGENCY_WAS_ACTIVE: False},
        )

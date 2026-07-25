"""The ChromaCal integration.

Runtime state lives on ConfigEntry.runtime_data (the current documented
pattern as of the 2026 HA releases — see
https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/),
rather than the older hass.data[DOMAIN] convention. As of Phase 3,
runtime_data *is* the ChromaCalCoordinator itself (holding region/
categories/lights plus the once-per-day sunset cache) — the modern
convention for integrations built around a DataUpdateCoordinator, and it's
cleaned up automatically with the entry — no manual hass.data teardown
needed in async_unload_entry.
"""

from __future__ import annotations

from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval

from .const import CONF_CATEGORIES, CONF_LIGHTS, CONF_REGION
from .coordinator import ChromaCalCoordinator

PLATFORMS: list[str] = ["sensor", "switch", "button"]

# v1's real cadence for multi-color cycling, inherited from the Blueprint
# automation it relied on (see coordinator.py's async_recheck_color_cycle).
# Deliberately separate from the coordinator's own 5-minute UPDATE_INTERVAL.
COLOR_CYCLE_INTERVAL = timedelta(seconds=60)

type ChromaCalConfigEntry = ConfigEntry[ChromaCalCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Set up ChromaCal from a config entry."""
    coordinator = ChromaCalCoordinator(
        hass,
        entry,
        region=entry.data[CONF_REGION],
        categories=entry.data[CONF_CATEGORIES],
        lights=entry.data[CONF_LIGHTS],
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # One-shot check: did HA go down while Emergency Mode was actively
    # broadcasting? Logs + raises a persistent_notification if so, then
    # clears the breadcrumb. Emergency Mode's own runtime state is never
    # resumed by this -- see coordinator.py's async_check_emergency_breadcrumb().
    await coordinator.async_check_emergency_breadcrumb()

    async def _recheck_color_cycle(_now) -> None:
        await coordinator.async_recheck_color_cycle(dt_util.now())

    entry.async_on_unload(
        async_track_time_interval(hass, _recheck_color_cycle, COLOR_CYCLE_INTERVAL)
    )

    @callback
    def _midnight_rollover(_now) -> None:
        # Exact local-midnight trigger, not a poll: resets tonight-only
        # skips and recomputes which events are skippable "tonight" with
        # near-zero lag, rather than waiting on the 5-minute cycle to
        # notice the date changed (see the Phase 5a plan discussion for
        # why this beat a faster polling interval for this specific job).
        #
        # @callback is required, not decorative: without it, HA's job-type
        # detection (get_hassjob_callable_job_type) treats a plain sync def
        # as potentially blocking and runs it in the executor thread pool,
        # not the event loop. ensure_today_candidates() calls
        # async_update_listeners() internally, which is event-loop-only --
        # running it from a worker thread raised a real
        # "calls async_write_ha_state from a thread other than the event
        # loop" RuntimeError, caught live in the disposable test container
        # during Phase 5b verification (2026-07-25 05:00:00, a real
        # midnight rollover, not a hypothetical).
        coordinator.ensure_today_candidates(dt_util.now())

    entry.async_on_unload(
        async_track_time_change(hass, _midnight_rollover, hour=0, minute=0, second=0)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Unload a ChromaCal config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

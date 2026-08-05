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

import logging
from datetime import timedelta
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval

from .const import (
    CONF_CATEGORIES,
    CONF_ENTITY,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_REGION,
    CONF_SUBENTRY_ID,
    DOMAIN,
    LIGHT_SUBENTRY_TYPE,
)
from .coordinator import ChromaCalCoordinator
from .frontend import async_register_frontend, async_unregister_frontend

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "switch", "button"]

# v1's real cadence for multi-color cycling, inherited from the Blueprint
# automation it relied on (see coordinator.py's async_recheck_color_cycle).
# Deliberately separate from the coordinator's own 5-minute UPDATE_INTERVAL.
COLOR_CYCLE_INTERVAL = timedelta(seconds=60)

type ChromaCalConfigEntry = ConfigEntry[ChromaCalCoordinator]


async def async_migrate_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Version 1 -> 2: move entry.data[CONF_LIGHTS] into real Config
    Subentries (Phase 8), one per light, each getting an HA-generated
    stable subentry_id -- and repoint each light's already-live sensor/
    button entities from their old light_entity-keyed unique_id to a
    subentry_id-keyed one, so already-configured installs don't lose
    those entities' entity_id, history, or any customization.

    Closes the deferred design decision CLAUDE.md has carried since the
    Phase 5a orphaned-sensor investigation: unique_id was keyed on a
    light's `entity` string, which silently orphaned the old entity the
    moment that string ever changed. Called automatically by HA's own
    config-entry setup machinery before async_setup_entry, exactly once,
    gated on entry.version -- see config_entries.py's own
    `hasattr(component, "async_migrate_entry")` check.
    """
    if entry.version > 1:
        return True

    registry = er.async_get(hass)
    old_lights: list[dict[str, Any]] = entry.data.get(CONF_LIGHTS, [])

    for light_data in old_lights:
        light_entity = light_data.get(CONF_ENTITY, "")
        subentry = ConfigSubentry(
            data=light_data,
            subentry_type=LIGHT_SUBENTRY_TYPE,
            title=light_data.get(CONF_NAME) or light_entity or "Light",
            unique_id=None,
        )
        hass.config_entries.async_add_subentry(entry, subentry)

        for domain, suffix in (("sensor", "schedule"), ("button", "force_white")):
            old_unique_id = f"{entry.entry_id}_{light_entity}_{suffix}"
            entity_id = registry.async_get_entity_id(domain, DOMAIN, old_unique_id)
            if entity_id is None:
                continue
            new_unique_id = f"{entry.entry_id}_{subentry.subentry_id}_{suffix}"
            registry.async_update_entity(
                entity_id,
                new_unique_id=new_unique_id,
                config_subentry_id=subentry.subentry_id,
            )
            _LOGGER.info(
                "ChromaCal: migrated %s unique_id for %s -- entity_id unchanged",
                domain,
                entity_id,
            )

    new_data = {key: value for key, value in entry.data.items() if key != CONF_LIGHTS}
    hass.config_entries.async_update_entry(entry, data=new_data, version=2)
    return True


def _lights_from_subentries(entry: ChromaCalConfigEntry) -> list[dict[str, Any]]:
    """Every configured light's data, sourced from the entry's Config
    Subentries (Phase 8) instead of the old CONF_LIGHTS list."""
    return [
        {**subentry.data, CONF_SUBENTRY_ID: subentry.subentry_id}
        for subentry in entry.subentries.values()
        if subentry.subentry_type == LIGHT_SUBENTRY_TYPE
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Set up ChromaCal from a config entry."""
    coordinator = ChromaCalCoordinator(
        hass,
        entry,
        region=entry.data[CONF_REGION],
        categories=entry.data[CONF_CATEGORIES],
        lights=_lights_from_subentries(entry),
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
    await async_register_frontend(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Unload a ChromaCal config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        async_unregister_frontend(hass)
    return unloaded

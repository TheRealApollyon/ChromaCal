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

import voluptuous as vol

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval

from .const import (
    ATTR_COLORS,
    ATTR_EVENT_NAME,
    ATTR_LIGHT_ENTITY,
    ATTR_MARKER_ID,
    ATTR_MODE,
    ATTR_PATH,
    ATTR_X,
    ATTR_Y,
    ATTR_Z,
    CONF_CATEGORIES,
    CONF_ENTITY,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_REGION,
    DOMAIN,
    LIGHT_SUBENTRY_TYPE,
    MAX_COLOR_OVERRIDE_COLORS,
    SERVICE_ADD_HOUSE_MARKER,
    SERVICE_ASSIGN_HOUSE_MARKER,
    SERVICE_REMOVE_HOUSE_MARKER,
    SERVICE_RESET_COLOR_OVERRIDE,
    SERVICE_SET_COLOR_OVERRIDE,
    SERVICE_SET_HOUSE_VIEW,
    SERVICE_SET_TONIGHT_PICK,
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

# Tonight's Pick / Color Override are services, not entities -- neither
# maps to a stable, addressable thing (a collision's candidates change
# nightly and are often empty; an override is a variable-length color
# list, not a fixed option set). See the plan discussion for the
# dev-docs/source research behind that call.
_HEX_COLOR = vol.Match(r"^#[0-9A-Fa-f]{6}$")

SET_TONIGHT_PICK_SCHEMA = vol.Schema({vol.Required(ATTR_EVENT_NAME): cv.string})

SET_COLOR_OVERRIDE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_EVENT_NAME): cv.string,
        vol.Required(ATTR_COLORS): vol.All(
            cv.ensure_list,
            [_HEX_COLOR],
            vol.Length(min=1, max=MAX_COLOR_OVERRIDE_COLORS),
        ),
    }
)

RESET_COLOR_OVERRIDE_SCHEMA = vol.Schema({vol.Required(ATTR_EVENT_NAME): cv.string})

_HOUSE_VIEW_MODE = vol.In(["2d", "3d"])

SET_HOUSE_VIEW_SCHEMA = vol.Schema(
    {vol.Required(ATTR_MODE): _HOUSE_VIEW_MODE, vol.Required(ATTR_PATH): cv.string}
)

ADD_HOUSE_MARKER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MODE): _HOUSE_VIEW_MODE,
        vol.Required(ATTR_X): vol.Coerce(float),
        vol.Required(ATTR_Y): vol.Coerce(float),
        vol.Optional(ATTR_Z): vol.Coerce(float),
    }
)

ASSIGN_HOUSE_MARKER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MARKER_ID): cv.string,
        # cv.entity_domain("light"), not the looser cv.entity_id -- a
        # marker's whole purpose is representing one of ChromaCal's own
        # configured lights, and the picker in the UI already only ever
        # offers those. cv.entity_id alone accepted any entity_id in the
        # instance regardless of domain (confirmed against real HA core
        # source during the security review this closes: entity_domain()
        # still validates entity_id shape via entities_domain() ->
        # entity_ids(), then additionally rejects anything outside the
        # given domain).
        vol.Optional(ATTR_LIGHT_ENTITY, default=None): vol.Any(
            cv.entity_domain("light"), None
        ),
    }
)

REMOVE_HOUSE_MARKER_SCHEMA = vol.Schema({vol.Required(ATTR_MARKER_ID): cv.string})


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


async def async_setup_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Set up ChromaCal from a config entry."""
    coordinator = ChromaCalCoordinator(
        hass,
        entry,
        region=entry.data[CONF_REGION],
        categories=entry.data[CONF_CATEGORIES],
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

    async def _async_set_tonight_pick(call: ServiceCall) -> None:
        await coordinator.async_set_tonight_pick(call.data[ATTR_EVENT_NAME])

    async def _async_set_color_override(call: ServiceCall) -> None:
        await coordinator.async_set_color_override(
            call.data[ATTR_EVENT_NAME], call.data[ATTR_COLORS]
        )

    async def _async_reset_color_override(call: ServiceCall) -> None:
        await coordinator.async_reset_color_override(call.data[ATTR_EVENT_NAME])

    async def _async_set_house_view(call: ServiceCall) -> None:
        await coordinator.async_set_house_view(call.data[ATTR_MODE], call.data[ATTR_PATH])

    async def _async_add_house_marker(call: ServiceCall) -> None:
        await coordinator.async_add_house_marker(
            call.data[ATTR_MODE], call.data[ATTR_X], call.data[ATTR_Y], call.data.get(ATTR_Z)
        )

    async def _async_assign_house_marker(call: ServiceCall) -> None:
        await coordinator.async_assign_house_marker(
            call.data[ATTR_MARKER_ID], call.data[ATTR_LIGHT_ENTITY]
        )

    async def _async_remove_house_marker(call: ServiceCall) -> None:
        await coordinator.async_remove_house_marker(call.data[ATTR_MARKER_ID])

    # Registered here, not async_setup, and guarded with has_service --
    # single_instance_allowed means there's only ever one entry to close
    # over, so there's no target/device_id resolution needed the way a
    # multi-instance integration would require (confirmed against
    # rainmachine's real async_setup_entry-registered services, which use
    # this same has_service guard for exactly this reason).
    for service_name, schema, handler in (
        (SERVICE_SET_TONIGHT_PICK, SET_TONIGHT_PICK_SCHEMA, _async_set_tonight_pick),
        (SERVICE_SET_COLOR_OVERRIDE, SET_COLOR_OVERRIDE_SCHEMA, _async_set_color_override),
        (SERVICE_RESET_COLOR_OVERRIDE, RESET_COLOR_OVERRIDE_SCHEMA, _async_reset_color_override),
        (SERVICE_SET_HOUSE_VIEW, SET_HOUSE_VIEW_SCHEMA, _async_set_house_view),
        (SERVICE_ADD_HOUSE_MARKER, ADD_HOUSE_MARKER_SCHEMA, _async_add_house_marker),
        (SERVICE_ASSIGN_HOUSE_MARKER, ASSIGN_HOUSE_MARKER_SCHEMA, _async_assign_house_marker),
        (SERVICE_REMOVE_HOUSE_MARKER, REMOVE_HOUSE_MARKER_SCHEMA, _async_remove_house_marker),
    ):
        if hass.services.has_service(DOMAIN, service_name):
            continue
        hass.services.async_register(DOMAIN, service_name, handler, schema=schema)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_frontend(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Unload a ChromaCal config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        async_unregister_frontend(hass)
        for service_name in (
            SERVICE_SET_TONIGHT_PICK,
            SERVICE_SET_COLOR_OVERRIDE,
            SERVICE_RESET_COLOR_OVERRIDE,
            SERVICE_SET_HOUSE_VIEW,
            SERVICE_ADD_HOUSE_MARKER,
            SERVICE_ASSIGN_HOUSE_MARKER,
            SERVICE_REMOVE_HOUSE_MARKER,
        ):
            hass.services.async_remove(DOMAIN, service_name)
    return unloaded

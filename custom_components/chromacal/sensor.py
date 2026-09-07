"""Sensor platform for ChromaCal -- one entity per configured light showing
tonight's resolved, currently-active schedule.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChromaCalCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ChromaCalCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one schedule sensor per configured light, plus one global
    Upcoming Events sensor (not per-light -- the list depends on region/
    categories/personal events, none of which are light-specific).

    Each light's sensor is added in its own async_add_entities() call with
    config_subentry_id set (Phase 8) -- that parameter is per-call, not
    per-entity, so a light with multiple entities can't share one bulk
    call with entities belonging to a different light or to the parent
    entry (the global Upcoming Events sensor gets no subentry at all).
    """
    coordinator: ChromaCalCoordinator = entry.runtime_data
    for light_entity, schedule in coordinator.data.items():
        async_add_entities(
            [ChromaCalScheduleSensor(coordinator, entry.entry_id, light_entity)],
            config_subentry_id=schedule.subentry_id,
        )
    async_add_entities(
        [
            ChromaCalUpcomingEventsSensor(coordinator, entry.entry_id),
            ChromaCalHouseViewSensor(coordinator, entry.entry_id),
        ]
    )


def _format_hour(hour: float) -> str:
    """Decimal hour (e.g. 20.32, or 25.0 for a sacred-tier midnight-crossing
    segment) -> HH:MM, wrapping past midnight."""
    total_minutes = round(hour * 60) % (24 * 60)
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


class ChromaCalScheduleSensor(CoordinatorEntity[ChromaCalCoordinator], SensorEntity):
    """Tonight's currently-active resolved event for one configured light."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: ChromaCalCoordinator, entry_id: str, light_entity: str
    ) -> None:
        super().__init__(coordinator)
        self._light_entity = light_entity
        schedule = coordinator.data[light_entity]
        self._attr_name = "Schedule"
        # Keyed on the light's stable subentry_id (Phase 8), not
        # light_entity -- see __init__.py's async_migrate_entry for why
        # that matters and how already-configured lights got moved over
        # without losing this entity's identity.
        self._attr_unique_id = f"{entry_id}_{schedule.subentry_id}_schedule"
        # Own device per light, identified by subentry_id, NOT the shared
        # (DOMAIN, entry_id) hub identifier every global entity uses --
        # a device can only belong to one config_subentry_id at a time,
        # and this entity IS added with config_subentry_id=schedule.
        # subentry_id (see async_setup_entry below). Sharing the hub's
        # identifier here caused HA to silently reassign that one shared
        # device between the hub and whichever light's entities were set
        # up last, on every restart -- confirmed live 2026-08-28, real
        # Pi trial: only the last-loaded per-light entity (button.py's
        # Force White, since PLATFORMS loads button.py last) ended up
        # visible; every other sensor/switch/button silently vanished.
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, schedule.subentry_id)},
            name=schedule.light_name,
        )

    @property
    def native_value(self) -> str | None:
        schedule = self.coordinator.data.get(self._light_entity)
        if schedule is None or schedule.current_segment is None:
            return None
        return schedule.current_segment.event.name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        schedule = self.coordinator.data.get(self._light_entity)
        if schedule is None:
            return {}

        attrs: dict[str, Any] = {
            # role lets the frontend panel tell this sensor apart from the
            # global Upcoming Events sensor below by data, not by parsing
            # display names -- same reasoning as switch.py/button.py's
            # role/scope attributes.
            "role": "schedule",
            "light_entity": schedule.light_entity,
            # ChromaCal's own configured name for this light -- NOT the
            # same thing as the underlying light entity's own
            # friendly_name (that's whatever the light's own integration
            # calls it, e.g. "Kitchen Lights", and can freely differ from
            # what the user named it here). Only reachable before this
            # otherwise via this entity's own composed name
            # (f"{light_name} Schedule", has_entity_name-prefixed by the
            # device name too) -- fragile to parse back out, so exposed
            # directly instead. The panel/card were reading the light
            # entity's friendly_name as a stand-in, which silently showed
            # the wrong name for any light renamed away from its entity's
            # own name -- found live while visually verifying Phase 10's
            # compact card against a light named differently from its
            # entity.
            "light_name": schedule.light_name,
            "sunset_hour": schedule.sunset_hour,
            "schedule_end_time": _format_hour(schedule.schedule_end_hour),
            "segments": [
                {
                    "name": segment.event.name,
                    "event_type": segment.event.event_type,
                    "colors": list(segment.event.colors),
                    "icon": segment.event.icon,
                    "start_time": _format_hour(segment.start_hour),
                    "end_time": _format_hour(segment.end_hour),
                }
                for segment in schedule.segments
            ],
        }

        # Tonight's Schedule (Plan B) -- the light's own configured
        # values, not just their effect on the resolved schedule above.
        # warmwhite_time in particular: only its effect (the last segment
        # capped early) was visible before this; the frontend shouldn't
        # have to reverse-engineer the boundary from segment math when
        # the source value is right here on LightConfig.
        light = self.coordinator.light_config_for(self._light_entity)
        if light is not None:
            attrs["fade_in"] = light.fade_in
            attrs["fade_out"] = light.fade_out
            attrs["warmwhite_time"] = light.warmwhite_time
            attrs["warmwhite_enabled"] = light.warmwhite_enabled
            attrs["verify_enabled"] = light.verify_enabled
            attrs["verify_off_enabled"] = light.verify_off_enabled

        # Manual override (Salute/Force White/Emergency) -- so Tonight's
        # Schedule can show when something else currently owns the light,
        # instead of silently rendering the normal schedule as if it were
        # still in charge.
        override = self.coordinator.override_for(self._light_entity)
        attrs["override_source"] = override.source if override is not None else None

        # Verify-and-retry (Plan A) -- real state for a future panel
        # surface to bind to, not a placeholder. None until the first
        # on/off transition after this coordinator started, same as
        # segments/current_segment above being empty before the first
        # refresh -- not a bug, just nothing to report yet.
        verify = self.coordinator.verify_state_for(self._light_entity)
        if verify is not None:
            attrs["verify_result"] = verify.result
            attrs["verify_checked_at"] = (
                verify.checked_at.isoformat() if verify.checked_at else None
            )
            attrs["verify_attempts_used"] = verify.attempts_used

        current = schedule.current_segment
        if current is not None:
            attrs["event_type"] = current.event.event_type
            attrs["colors"] = list(current.event.colors)
            attrs["icon"] = current.event.icon
            attrs["start_time"] = _format_hour(current.start_hour)
            attrs["end_time"] = _format_hour(current.end_hour)

        return attrs


class ChromaCalUpcomingEventsSensor(CoordinatorEntity[ChromaCalCoordinator], SensorEntity):
    """The next 45 days of enabled holiday/personal events -- global, not
    per-light, since the list depends only on region/categories/personal
    events. Native value is the nearest event's name (something legible
    at a glance in HA's own entity list); the full list lives in
    extra_state_attributes for the panel's Upcoming Events card.

    Not filtered by skip state, same as get_upcoming_events() itself --
    the panel is responsible for showing skip status (via the existing
    skip switches) and dimming skipped rows, not this sensor.
    """

    _attr_has_entity_name = True
    _attr_name = "Upcoming Events"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_upcoming_events"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def native_value(self) -> str | None:
        events = self.coordinator.upcoming_events
        return events[0].name if events else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "role": "upcoming_events",
            "events": [
                {
                    "date": event.date.isoformat(),
                    "name": event.name,
                    "category": event.category,
                    "event_type": event.event_type,
                    "icon": event.icon,
                    "colors": list(event.colors),
                    "is_today": event.is_today,
                    "is_personal_range": event.is_personal_range,
                }
                for event in self.coordinator.upcoming_events
            ],
            # Tonight's Pick / Color Override (all-lights, not per-event
            # attributes -- see coordinator.py's field docstrings) -- the
            # panel compares an event's own name against these to decide
            # whether its ☆/🎨 buttons show as active.
            "tonight_pick": self.coordinator.tonight_pick,
            "color_overrides": {
                name: list(colors) for name, colors in self.coordinator.color_overrides.items()
            },
        }


class ChromaCalHouseViewSensor(CoordinatorEntity[ChromaCalCoordinator], SensorEntity):
    """House View's config -- global, not per-light, same reasoning as
    ChromaCalUpcomingEventsSensor above: one 2D image or 3D model with
    markers on it applies across every configured light, not one per
    light. Native value is the marker count (something legible at a
    glance); the mode/path/full marker list live in extra_state_attributes
    for the panel's House View section.
    """

    _attr_has_entity_name = True
    _attr_name = "House View"
    _attr_icon = "mdi:floor-plan"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_house_view"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.house_view_markers)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "role": "house_view",
            "mode": self.coordinator.house_view_mode,
            "path": self.coordinator.house_view_path,
            "markers": list(self.coordinator.house_view_markers),
        }

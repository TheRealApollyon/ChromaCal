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
    """Set up one schedule sensor per configured light."""
    coordinator: ChromaCalCoordinator = entry.runtime_data
    async_add_entities(
        ChromaCalScheduleSensor(coordinator, entry.entry_id, light_entity)
        for light_entity in coordinator.data
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
        light_name = coordinator.data[light_entity].light_name
        self._attr_name = f"{light_name} Schedule"
        self._attr_unique_id = f"{entry_id}_{light_entity}_schedule"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="ChromaCal",
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
            "light_entity": schedule.light_entity,
            "sunset_hour": schedule.sunset_hour,
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

        current = schedule.current_segment
        if current is not None:
            attrs["event_type"] = current.event.event_type
            attrs["colors"] = list(current.event.colors)
            attrs["icon"] = current.event.icon
            attrs["start_time"] = _format_hour(current.start_hour)
            attrs["end_time"] = _format_hour(current.end_hour)

        return attrs

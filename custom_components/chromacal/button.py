"""Button platform for ChromaCal's one-shot quick-control actions: 21 Gun
Salute, Catch Up/Sync (both global, one entity total), and Force White
(per configured light -- v1 scoped this to whichever light was selected in
its single-page-app tab, and HA has no equivalent "currently active light"
concept for backend entities, so it becomes one button per light instead).

Emergency Mode is deliberately NOT here -- it's a switch (see switch.py),
since it's genuinely start/stop with a real running state, not a fire-once
trigger. See the Phase 5b plan discussion for that reasoning.

All three buttons fire their coordinator method via
coordinator.async_fire_and_forget() rather than awaiting it directly from
async_press(): Salute runs ~50-60 real seconds of sequenced service calls,
and awaiting that from async_press() would stall the entity-service-call
caller (frontend spinner, or any automation's button.press action) for the
whole duration. v1's own onclick handler never awaited its async function
either. Catch Up/Sync and Force White are fast in practice but get the
same treatment for consistency and because there's no reason for a button
press to ever block its caller here. async_fire_and_forget() wraps
entry.async_create_task(), not the bare hass.async_create_task() this
originally used -- see that method's docstring for why (caught during the
Phase 5b callback-dispatch audit).
"""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up the Salute, Catch Up/Sync, and per-light Force White buttons.

    All static, like the sensor and permanent-skip switch platforms -- none
    of these come or go based on date or config the way tonight-skip
    switches do.
    """
    coordinator = entry.runtime_data

    entities: list[ButtonEntity] = [
        ChromaCalSaluteButton(coordinator, entry.entry_id),
        ChromaCalCatchUpButton(coordinator, entry.entry_id),
    ]
    entities.extend(
        ChromaCalForceWhiteButton(coordinator, entry.entry_id, light_entity)
        for light_entity in coordinator.data
    )
    async_add_entities(entities)


class ChromaCalSaluteButton(CoordinatorEntity[ChromaCalCoordinator], ButtonEntity):
    """21 Gun Salute -- 3 volleys + Taps across every configured light."""

    _attr_has_entity_name = True
    _attr_name = "21 Gun Salute"
    _attr_icon = "mdi:flag"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_salute"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def available(self) -> bool:
        # Greyed out while a Salute is already running -- the coordinator's
        # own re-entry guard is the authoritative protection (a second
        # press could still reach async_press() via an automation calling
        # button.press directly); this is just honest UI feedback on top.
        return super().available and not self.coordinator.salute_active

    async def async_press(self) -> None:
        self.coordinator.async_fire_and_forget(
            self.coordinator.async_fire_salute(), name="chromacal_salute"
        )


class ChromaCalCatchUpButton(CoordinatorEntity[ChromaCalCoordinator], ButtonEntity):
    """Force-recompute and re-push the correct state to every configured
    light -- for when a light has drifted out of sync with what ChromaCal
    last told it (a dropped Zigbee command, a manual change elsewhere)."""

    _attr_has_entity_name = True
    _attr_name = "Catch Up / Sync"
    _attr_icon = "mdi:sync"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_catch_up_sync"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    async def async_press(self) -> None:
        self.coordinator.async_fire_and_forget(
            self.coordinator.async_catch_up(), name="chromacal_catch_up_sync"
        )


class ChromaCalForceWhiteButton(CoordinatorEntity[ChromaCalCoordinator], ButtonEntity):
    """Immediately set one light to its own configured warm-white Kelvin,
    suppressing auto-fire for that light for 30 minutes before the real
    schedule resumes on its own."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:lightbulb-on-outline"

    def __init__(
        self, coordinator: ChromaCalCoordinator, entry_id: str, light_entity: str
    ) -> None:
        super().__init__(coordinator)
        self._light_entity = light_entity
        light_name = coordinator.data[light_entity].light_name
        self._attr_name = f"{light_name} Force White"
        self._attr_unique_id = f"{entry_id}_{light_entity}_force_white"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    async def async_press(self) -> None:
        # Fast/single service call, but fire-and-forget for the same
        # reason as the other two buttons: a press should never block its
        # caller, and this keeps the three entities' behavior consistent.
        self.coordinator.async_fire_and_forget(
            self.coordinator.async_fire_force_white(self._light_entity),
            name="chromacal_force_white",
        )

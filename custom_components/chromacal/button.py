"""Button platform for ChromaCal's one-shot quick-control actions: 21 Gun
Salute, Catch Up/Sync, Stop (all global, one entity each), and Force White
(per configured light -- v1 scoped this to whichever light was selected in
its single-page-app tab, and HA has no equivalent "currently active light"
concept for backend entities, so it becomes one button per light instead).

Emergency Mode is deliberately NOT here -- it's a switch (see switch.py),
since it's genuinely start/stop with a real running state, not a fire-once
trigger. See the Phase 5b plan discussion for that reasoning.

Catch Up/Sync and Force White fire their coordinator method via
coordinator.async_fire_and_forget() rather than awaiting it directly from
async_press(): a press should never block its caller (frontend spinner,
or any automation's button.press action), even though these two are fast
in practice. async_fire_and_forget() wraps entry.async_create_task(), not
the bare hass.async_create_task() this originally used -- see that
method's docstring for why (caught during the Phase 5b callback-dispatch
audit).

Salute is different: async_press() calls coordinator.async_toggle_salute()
directly and awaits it, since that method itself decides whether to start
(fire-and-forget, same reasoning as above) or cancel a running Salute
(fast -- a task cancellation plus quick cleanup, not worth a separate
fire-and-forget path). Stop (button.chromacal_stop) is the same shape:
awaits coordinator.async_stop_all_overrides() directly, since cancelling
whatever's active is comparably fast.
"""

from __future__ import annotations

from typing import Any

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

    async_add_entities(
        [
            ChromaCalSaluteButton(coordinator, entry.entry_id),
            ChromaCalCatchUpButton(coordinator, entry.entry_id),
            ChromaCalStopButton(coordinator, entry.entry_id),
        ]
    )
    # Force White is per-light, so each gets its own async_add_entities()
    # call with config_subentry_id set (Phase 8) -- see sensor.py's
    # async_setup_entry for why that can't be one bulk call.
    for light_entity, schedule in coordinator.data.items():
        async_add_entities(
            [ChromaCalForceWhiteButton(coordinator, entry.entry_id, light_entity)],
            config_subentry_id=schedule.subentry_id,
        )


class ChromaCalSaluteButton(CoordinatorEntity[ChromaCalCoordinator], ButtonEntity):
    """21 Gun Salute -- 3 volleys + Taps across every configured light.

    Press again while running to cancel: Salute can also start on its own
    from an auto-fired event (Memorial Day, POW/MIA, a Memorial-type
    personal event), not just a button press, so it needs the same
    interrupt capability Emergency Mode already has via its switch's
    turn_off. Deliberately NOT marked unavailable while running (that was
    the original design) -- a second press is a real, meaningful action
    now, not something to grey out. The `running` attribute is how the UI
    shows current state instead.
    """

    _attr_has_entity_name = True
    _attr_name = "21 Gun Salute"
    _attr_icon = "mdi:flag"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_salute"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        # role lets the frontend panel identify this specific global button
        # by data instead of parsing its display name -- same reasoning as
        # the switch.py role/scope attributes.
        return {"role": "salute", "running": self.coordinator.salute_active}

    async def async_press(self) -> None:
        # Not fire-and-forget at this layer: async_toggle_salute() itself
        # decides whether to start (fire-and-forget internally) or cancel
        # a running Salute (fast), so awaiting it here never blocks long.
        await self.coordinator.async_toggle_salute()


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

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"role": "catch_up_sync"}

    async def async_press(self) -> None:
        self.coordinator.async_fire_and_forget(
            self.coordinator.async_catch_up(), name="chromacal_catch_up_sync"
        )


class ChromaCalStopButton(CoordinatorEntity[ChromaCalCoordinator], ButtonEntity):
    """Cancel whatever override is currently active -- a running Salute,
    Emergency Mode, or any light's Force White window -- across every
    configured light, and resume the real schedule immediately.

    A third, simpler entry point into the same cancel-and-resume action
    as Salute's own press-again-to-cancel and the Emergency switch's
    turn_off (both of those stay as they are) -- for someone who just
    wants "make it normal again" without knowing what's currently
    overridden. Safe no-op if nothing is: see
    coordinator.async_stop_all_overrides()'s own docstring.
    """

    _attr_has_entity_name = True
    _attr_name = "Stop"
    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_stop"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"role": "stop"}

    async def async_press(self) -> None:
        await self.coordinator.async_stop_all_overrides()


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
        schedule = coordinator.data[light_entity]
        self._attr_name = "Force White"
        # Keyed on subentry_id (Phase 8) -- see sensor.py's identical
        # change and __init__.py's async_migrate_entry.
        self._attr_unique_id = f"{entry_id}_{schedule.subentry_id}_force_white"
        # Own device per light, scoped by subentry_id -- see sensor.py's
        # ChromaCalScheduleSensor for the full explanation of why sharing
        # the hub's (DOMAIN, entry_id) identifier here caused entities to
        # silently vanish on real hardware (2026-08-28 trial).
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, schedule.subentry_id)},
            name=schedule.light_name,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"role": "force_white", "light_entity": self._light_entity}

    async def async_press(self) -> None:
        # Fast/single service call, but fire-and-forget for the same
        # reason as the other two buttons: a press should never block its
        # caller, and this keeps the three entities' behavior consistent.
        self.coordinator.async_fire_and_forget(
            self.coordinator.async_fire_force_white(self._light_entity),
            name="chromacal_force_white",
        )

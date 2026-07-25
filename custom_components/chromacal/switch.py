"""Switch platform for ChromaCal: the skip system, plus Emergency Mode.

Skip system -- two switch types, deliberately scoped and persisted
differently -- see the Phase 5a plan discussion for the full reasoning:

- Permanent skip: one switch per event in the whole enabled region+
  categories calendar, created once (static, like the sensor platform).
  Persisted in the config entry's OPTIONS, not the switch's own state, so
  it survives independently of any particular entity's lifecycle.
- Skip-tonight: one switch per event that's actually a candidate for
  *today* -- typically 0-3 entities, occasionally more. Added and removed
  dynamically as that set changes at local midnight (see coordinator.py's
  ensure_today_candidates()), which is why this is the first entity type
  in this integration that isn't created once and left alone.

Emergency Mode (Phase 5b) is here too, not in button.py, despite CLAUDE.md
listing it alongside the other quick-control buttons -- it's genuinely
start/stop with a real running state (an alternating color broadcast that
continues until explicitly cancelled), not a fire-once trigger. A button
entity has no persisted on/off state to show "is this currently active"
without bolting on a separate sensor; a switch's is_on gives that for
free. Same reasoning that made the skip system a switch in the first
place.

All switches here are always reversible by construction (CLAUDE.md's hard
rule) -- a switch has both an on and off state, there's no separate
one-way action.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChromaCalCoordinator

_PERMANENT_PREFIX = "_skip_"
_TONIGHT_PREFIX = "_skip_tonight_"


def _permanent_unique_id(entry_id: str, event_name: str) -> str:
    return f"{entry_id}{_PERMANENT_PREFIX}{event_name}"


def _tonight_unique_id(entry_id: str, event_name: str) -> str:
    return f"{entry_id}{_TONIGHT_PREFIX}{event_name}"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ChromaCalCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the static permanent-skip switches and start tracking the
    dynamic tonight-skip switches."""
    coordinator = entry.runtime_data

    async_add_entities(
        ChromaCalPermanentSkipSwitch(coordinator, entry.entry_id, name)
        for name in coordinator.get_all_event_names()
    )
    async_add_entities([ChromaCalEmergencySwitch(coordinator, entry.entry_id)])

    # Reconcile against whatever the entity registry already has for THIS
    # entry, not an empty set -- otherwise a tonight-skip switch that was
    # already stale before an HA restart (the day rolled over while HA was
    # down, say) would never get cleaned up: this session's own diffing
    # only ever sees names it added itself unless seeded from what's real.
    registry = er.async_get(hass)
    known_tonight_names: set[str] = {
        reg_entry.unique_id[len(entry.entry_id) + len(_TONIGHT_PREFIX) :]
        for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id)
        if reg_entry.domain == Platform.SWITCH
        and reg_entry.unique_id.startswith(f"{entry.entry_id}{_TONIGHT_PREFIX}")
    }

    def _sync_tonight_switches() -> None:
        current = coordinator.todays_candidate_names
        new_names = current - known_tonight_names
        stale_names = known_tonight_names - current

        if new_names:
            known_tonight_names.update(new_names)
            async_add_entities(
                ChromaCalTonightSkipSwitch(coordinator, entry.entry_id, name)
                for name in new_names
            )

        for name in stale_names:
            known_tonight_names.discard(name)
            entity_id = registry.async_get_entity_id(
                Platform.SWITCH, DOMAIN, _tonight_unique_id(entry.entry_id, name)
            )
            if entity_id:
                registry.async_remove(entity_id)

    # Reconcile once against the current (already-computed, from the
    # coordinator's first refresh) candidate set before wiring the ongoing
    # listener -- covers both "brand new switches for today" and "clean up
    # anything stale from before this restart" in the same pass.
    _sync_tonight_switches()
    entry.async_on_unload(coordinator.async_add_listener(_sync_tonight_switches))


class ChromaCalPermanentSkipSwitch(CoordinatorEntity[ChromaCalCoordinator], SwitchEntity):
    """Permanently skip (or restore) one calendar event, across all lights."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-remove-outline"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str, event_name: str) -> None:
        super().__init__(coordinator)
        self._event_name = event_name
        self._attr_name = f"{event_name} Skip"
        self._attr_unique_id = _permanent_unique_id(entry_id, event_name)
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def is_on(self) -> bool:
        return self._event_name in self.coordinator.skipped_events

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_permanent_skip(self._event_name, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_permanent_skip(self._event_name, False)


class ChromaCalTonightSkipSwitch(CoordinatorEntity[ChromaCalCoordinator], SwitchEntity):
    """Skip (or restore) one event for tonight only.

    Only exists while its event is one of coordinator.todays_candidate_names
    -- added/removed by async_setup_entry's coordinator listener, not
    created once like the permanent switches above.
    """

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-minus-outline"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str, event_name: str) -> None:
        super().__init__(coordinator)
        self._event_name = event_name
        self._attr_name = f"{event_name} Skip Tonight"
        self._attr_unique_id = _tonight_unique_id(entry_id, event_name)
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def is_on(self) -> bool:
        return self._event_name in self.coordinator.tonight_skips

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_tonight_skip(self._event_name, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_tonight_skip(self._event_name, False)


class ChromaCalEmergencySwitch(CoordinatorEntity[ChromaCalCoordinator], SwitchEntity):
    """Broadcast an alternating emergency color pattern across every
    configured light until turned back off. See this module's docstring
    for why this is a switch, not a button.
    """

    _attr_has_entity_name = True
    _attr_name = "Emergency Mode"
    _attr_icon = "mdi:alert-octagon"

    def __init__(self, coordinator: ChromaCalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_emergency_mode"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="ChromaCal")

    @property
    def is_on(self) -> bool:
        return self.coordinator.emergency_active

    async def async_turn_on(self, **kwargs: Any) -> None:
        # Fast to complete (fires once, registers a repeating interval, and
        # returns) unlike Salute, so a direct await is fine here -- no need
        # for the fire-and-forget task pattern button.py uses.
        await self.coordinator.async_start_emergency()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_stop_emergency()

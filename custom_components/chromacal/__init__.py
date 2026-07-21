"""The ChromaCal integration.

Runtime state lives on ConfigEntry.runtime_data (the current documented
pattern as of the 2026 HA releases — see
https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/),
rather than the older hass.data[DOMAIN] convention. Storing it there gives
the entry's own typed alias instead of a shared, untyped dict keyed by
DOMAIN, and it's cleaned up automatically with the entry — no manual
hass.data teardown needed in async_unload_entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_CATEGORIES, CONF_LIGHTS, CONF_REGION

# Scheduling entities (sensor/switch/button) land in a later phase.
PLATFORMS: list[str] = []

type ChromaCalConfigEntry = ConfigEntry[ChromaCalData]


@dataclass
class ChromaCalData:
    """Runtime state for one ChromaCal config entry."""

    region: str
    categories: dict[str, bool]
    lights: list[dict[str, Any]]


async def async_setup_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Set up ChromaCal from a config entry."""
    entry.runtime_data = ChromaCalData(
        region=entry.data[CONF_REGION],
        categories=entry.data[CONF_CATEGORIES],
        lights=entry.data[CONF_LIGHTS],
    )

    if PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Unload a ChromaCal config entry."""
    if PLATFORMS:
        return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return True

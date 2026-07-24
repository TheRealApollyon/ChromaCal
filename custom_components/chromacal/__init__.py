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

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_CATEGORIES, CONF_LIGHTS, CONF_REGION
from .coordinator import ChromaCalCoordinator

PLATFORMS: list[str] = ["sensor"]

type ChromaCalConfigEntry = ConfigEntry[ChromaCalCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Set up ChromaCal from a config entry."""
    coordinator = ChromaCalCoordinator(
        hass,
        region=entry.data[CONF_REGION],
        categories=entry.data[CONF_CATEGORIES],
        lights=entry.data[CONF_LIGHTS],
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ChromaCalConfigEntry) -> bool:
    """Unload a ChromaCal config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

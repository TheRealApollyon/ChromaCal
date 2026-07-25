"""Tests for the sidebar panel registration in frontend.py.

Verifies the actual registered Panel object's fields directly (via
frontend.DATA_PANELS) rather than just asserting "setup didn't raise" --
require_admin/embed_iframe/module_url are real product decisions (see the
Phase 6 plan discussion), not implementation details safe to drift on.
"""

from __future__ import annotations

from homeassistant.components import frontend
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import DOMAIN, PANEL_STATIC_URL_BASE, PANEL_URL_PATH

ENTRY_DATA = {
    "region": "us",
    "categories": {"federal": True},
    "lights": [
        {
            "name": "Front Porch",
            "zone": "",
            "entity": "light.front_porch",
            "start_type": "sunset",
            "start_time": "19:00",
            "end_type": "time",
            "end_time": "23:00",
            "fade_in": 30,
            "fade_out": 120,
            "warmwhite_time": "22:00",
            "warmwhite_enabled": True,
        }
    ],
}


async def _setup_entry(hass, entry_id: str) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, entry_id=entry_id)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_panel_registered_on_setup(hass, freezer):
    freezer.move_to("2026-07-25 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    await _setup_entry(hass, "test_panel_registered")

    assert frontend.async_panel_exists(hass, PANEL_URL_PATH)
    panel = hass.data[frontend.DATA_PANELS][PANEL_URL_PATH]

    assert panel.sidebar_title == "ChromaCal"
    assert panel.require_admin is False
    assert panel.config is not None
    custom = panel.config["_panel_custom"]
    assert custom["name"] == "chromacal-panel"
    assert custom["embed_iframe"] is False
    assert custom["trust_external"] is False
    assert custom["module_url"].startswith(f"{PANEL_STATIC_URL_BASE}/chromacal-panel.js?v=")


async def test_panel_registration_is_idempotent_across_setups(hass, freezer):
    """A second config entry (or a reload) must not raise "Overwriting
    panel" -- the async_panel_exists guard in frontend.py exists precisely
    for this."""
    freezer.move_to("2026-07-25 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    await _setup_entry(hass, "test_panel_first")

    # A second entry setup must not raise, and must not replace the panel
    # with a duplicate registration attempt.
    await _setup_entry(hass, "test_panel_second")
    assert frontend.async_panel_exists(hass, PANEL_URL_PATH)


async def test_panel_removed_on_unload(hass, freezer):
    freezer.move_to("2026-07-25 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")
    entry = await _setup_entry(hass, "test_panel_unload")
    assert frontend.async_panel_exists(hass, PANEL_URL_PATH)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not frontend.async_panel_exists(hass, PANEL_URL_PATH)

"""Registers ChromaCal's sidebar panel -- a single Lit web component built
from frontend/src/ (see frontend/README.md for the rebuild command),
served straight out of this integration's own directory so nothing
requires the user to touch /www/ or add a Lovelace resource by hand.

Mechanism confirmed directly against the installed HA 2026.7.2 source
(homeassistant.components.frontend / .panel_custom) and cross-checked
against HACS's own production frontend.py, which registers its panel the
same way. One deliberate deviation from HACS's example: embed_iframe is
False here, not True -- CSS custom properties (which the theme-native
requirement depends on) don't cross an iframe boundary, and HACS's own
reason for iframing (isolating a large pre-existing SPA) doesn't apply to
a small panel built to inherit HA's theme in the first place.

ChromaCal is a single-instance integration in practice (see the rest of
this codebase -- Emergency Mode's breadcrumb, the shared "ChromaCal"
device, etc. all assume one config entry), so this panel is registered/
removed at the HA-instance level, guarded against double-registration by
`frontend.async_panel_exists` rather than tracked per-entry.
"""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN, PANEL_STATIC_URL_BASE, PANEL_URL_PATH, PANEL_WEBCOMPONENT_NAME

PANEL_DIST_DIR = Path(__file__).parent / "panel_dist"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve panel_dist/ and register the sidebar panel, once per HA instance."""
    if frontend.async_panel_exists(hass, PANEL_URL_PATH):
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_STATIC_URL_BASE, str(PANEL_DIST_DIR), False)]
    )

    # Cache-busts the module URL on every integration version bump -- same
    # trick HACS uses (its own `?hacstag=` query param) -- so a browser
    # that already cached the old bundle picks up a new one after upgrade.
    integration = await async_get_integration(hass, DOMAIN)

    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="ChromaCal",
        sidebar_icon="mdi:string-lights",
        frontend_url_path=PANEL_URL_PATH,
        require_admin=False,
        config={
            "_panel_custom": {
                "name": PANEL_WEBCOMPONENT_NAME,
                "embed_iframe": False,
                "trust_external": False,
                "module_url": f"{PANEL_STATIC_URL_BASE}/chromacal-panel.js?v={integration.version}",
            }
        },
    )


def async_unregister_frontend(hass: HomeAssistant) -> None:
    """Remove the sidebar panel on unload."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)

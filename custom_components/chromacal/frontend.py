"""Registers ChromaCal's sidebar panel and compact Lovelace card -- both
built from the same frontend/src/ Lit component (see frontend/README.md
for the rebuild command) and served out of this integration's own
directory, so nothing requires the user to touch /www/ or add a Lovelace
resource by hand.

Panel mechanism confirmed directly against the installed HA 2026.7.2
source (homeassistant.components.frontend / .panel_custom) and
cross-checked against HACS's own production frontend.py, which registers
its panel the same way. One deliberate deviation from HACS's example:
embed_iframe is False here, not True -- CSS custom properties (which the
theme-native requirement depends on) don't cross an iframe boundary, and
HACS's own reason for iframing (isolating a large pre-existing SPA)
doesn't apply to a small panel built to inherit HA's theme in the first
place.

The card needs a different registration path than the panel: a panel's
module only loads when its own sidebar route is active (panel_custom's
own lazy resolver), but the card must be available in Lovelace's card
picker on *any* dashboard. `frontend.add_extra_js_url` (confirmed against
the same installed source) is what makes a module load on every frontend
page -- pointed at the exact same URL as the panel's own module_url, so
the browser's module cache serves one shared instance either way, not a
second load.

ChromaCal is a single-instance integration in practice (see the rest of
this codebase -- Emergency Mode's breadcrumb, the shared "ChromaCal"
device, etc. all assume one config entry), so both are registered/
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


def _module_url(version: str) -> str:
    """The one bundle both the panel and the card load from -- cache-busted
    on every integration version bump (same trick HACS uses with its own
    `?hacstag=` param), so a browser that already cached an old bundle
    picks up a new one after upgrade."""
    return f"{PANEL_STATIC_URL_BASE}/chromacal-panel.js?v={version}"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve panel_dist/, register the sidebar panel, and make the compact
    card's module available dashboard-wide -- once per HA instance."""
    if frontend.async_panel_exists(hass, PANEL_URL_PATH):
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_STATIC_URL_BASE, str(PANEL_DIST_DIR), False)]
    )

    integration = await async_get_integration(hass, DOMAIN)
    module_url = _module_url(integration.version)

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
                "module_url": module_url,
            }
        },
    )

    frontend.add_extra_js_url(hass, module_url)


def async_unregister_frontend(hass: HomeAssistant) -> None:
    """Remove the sidebar panel and the card's dashboard-wide module on
    unload."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
    # Prefix-match rather than reconstruct the exact ?v=... URL -- getting
    # the integration's version needs async_get_integration, an async
    # call, and this function isn't async (matches how it's already
    # called, unawaited, from async_unload_entry).
    url_manager = hass.data.get(frontend.DATA_EXTRA_MODULE_URL)
    registered_urls = url_manager.urls if url_manager is not None else ()
    for url in list(registered_urls):
        if url.startswith(f"{PANEL_STATIC_URL_BASE}/chromacal-panel.js"):
            frontend.remove_extra_js_url(hass, url)

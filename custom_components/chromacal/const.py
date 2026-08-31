"""Constants for the ChromaCal integration."""

DOMAIN = "chromacal"

# ── Config entry data keys ─────────────────────────────────────────
CONF_REGION = "region"
CONF_CATEGORIES = "categories"
CONF_LIGHTS = "lights"

# ── Config entry OPTIONS keys — mutable post-setup settings, not part of
# the original wizard (unlike CONF_REGION/CONF_CATEGORIES/CONF_LIGHTS
# above). Permanent-skip state lives here (see coordinator.py) so it
# survives restarts independently of any particular switch entity's
# lifecycle.
CONF_SKIPPED_EVENTS = "skipped_events"

# Per-event color override -- dict[event_name, list[hex]], matching v1's
# CFG.colorOverrides shape byte-for-byte. Persisted like skipped_events
# above (survives restarts, until explicitly changed/reset), unlike
# tonight_pick below which is deliberately NOT persisted.
CONF_COLOR_OVERRIDES = "color_overrides"

# One-shot breadcrumb, not live state: True the instant Emergency Mode
# starts, False the instant it stops cleanly. If the coordinator finds this
# True on startup, HA went down mid-broadcast without ever reaching the
# normal stop path -- see coordinator.py's startup check, which logs a
# warning, fires a persistent_notification, and immediately clears this
# back to False. Emergency Mode's actual runtime state is never restored
# from this -- it stays fresh/in-memory, same reasoning as tonight_skips.
CONF_EMERGENCY_WAS_ACTIVE = "emergency_was_active"

# ── Lights are Config Subentries (Phase 8), not a data list ─────────
# Stable subentry_id (HA-generated, a ULID) replaces light_entity as the
# identity unique_ids are keyed on -- see the Phase 8 plan discussion and
# __init__.py's async_migrate_entry for the migration this closes.
LIGHT_SUBENTRY_TYPE = "light"

# Synthetic key injected onto each light dict in coordinator.lights,
# sourced from the owning ConfigSubentry's subentry_id. Not a real
# per-light config field and never written by config_flow's own forms --
# purely a convenience so sensor.py/button.py can read it off the same
# plain dict shape as every other light field, without threading a
# parallel subentry_id argument through every call site that already
# takes a light dict.
CONF_SUBENTRY_ID = "_subentry_id"

# ── Per-light config keys (mirrors the v1 saveLight() object shape) ─
CONF_NAME = "name"
CONF_ZONE = "zone"
CONF_ENTITY = "entity"
CONF_START_TYPE = "start_type"
CONF_START_TIME = "start_time"
CONF_END_TYPE = "end_type"
CONF_END_TIME = "end_time"
CONF_FADE_IN = "fade_in"
CONF_FADE_OUT = "fade_out"
CONF_WARMWHITE_TIME = "warmwhite_time"
CONF_WARMWHITE_ENABLED = "warmwhite_enabled"

# Verify-and-retry (Plan A): after firing a real on/off transition, confirm
# the light actually reports the intended state instead of just trusting
# the service call landed -- see coordinator.py's _call_fire_command_verified
# docstring. Defaults sourced from Shane's own "Outside Lights - Late Night
# Off" automation (real hardware-proven values, not invented) -- see
# CLAUDE.md's root-cause writeup for the light flip-back investigation this
# feature exists to catch.
CONF_VERIFY_ENABLED = "verify_enabled"
CONF_VERIFY_RETRY_COUNT = "verify_retry_count"
CONF_VERIFY_CHECK_DELAY = "verify_check_delay"

# ── Regions — matches the 8 wizard region tiles in chromacal.html ──
REGIONS = {
    "us": "United States",
    "ca": "Canada",
    "uk": "United Kingdom",
    "au": "Australia / NZ",
    "eu": "Europe",
    "apac": "Asia-Pacific",
    "latam": "Latin America",
    "global": "Global / Other",
}

# ── Categories — matches CATEGORIES in chromacal.html ──────────────
CATEGORIES = {
    "federal": "Federal & National Holidays",
    "cultural": "Cultural Celebrations",
    "military": "Military & Veterans",
    "heritage": "Heritage & Cultural Months",
    "pride": "Pride & LGBTQ+ Events",
    "awareness": "Health & Awareness Months",
    "religious": "Religious Observances",
    "pagan": "Pagan & Wiccan Observances (Beta)",
    "personal": "Personal Events",
}

START_TYPES = ["sunset", "sunrise", "time"]
END_TYPES = ["time", "sunrise", "civil_dawn", "never"]

# Matches the <select> options in the v1 wizard's Step 5 (fade in/out dropdowns)
FADE_IN_OPTIONS = [0, 15, 30, 60, 120]
FADE_OUT_OPTIONS = [0, 30, 60, 120]

# Verify-and-retry dropdowns -- 0 retries is a valid choice (check once,
# notify immediately on mismatch, no re-fire).
VERIFY_RETRY_COUNT_OPTIONS = [0, 1, 2, 3]
VERIFY_CHECK_DELAY_OPTIONS = [60, 120, 180, 300]

# ── Sidebar panel (Phase 6) ──────────────────────────────────────
PANEL_URL_PATH = "chromacal"
PANEL_STATIC_URL_BASE = "/chromacal_static"
PANEL_WEBCOMPONENT_NAME = "chromacal-panel"

# ── Tonight's Pick / Color Override services ─────────────────────
# Services, not entities -- neither maps to a stable, addressable thing:
# Tonight's Pick's candidates change nightly (often empty), and Color
# Override needs a variable-length list of colors, not a fixed option
# set. See the plan discussion for the dev-docs/source research behind
# this call.
SERVICE_SET_TONIGHT_PICK = "set_tonight_pick"
SERVICE_SET_COLOR_OVERRIDE = "set_color_override"
SERVICE_RESET_COLOR_OVERRIDE = "reset_color_override"

ATTR_EVENT_NAME = "event_name"
ATTR_COLORS = "colors"

# Matches v1's chip-list cap in the color-override modal.
MAX_COLOR_OVERRIDE_COLORS = 6

# ── House View (Phase 11) ─────────────────────────────────────────
# A 2D image or 3D model with light markers on it, matching v1's House
# View. Persisted the same way as CONF_COLOR_OVERRIDES above -- a user's
# house image/model path and marker layout are configuration they set once
# and expect to survive restarts, not per-session runtime state.
CONF_HOUSE_VIEW_MODE = "house_view_mode"
CONF_HOUSE_VIEW_PATH = "house_view_path"
# list[dict] shape: {id, mode, x, y, z, light_entity}. Keyed by a generated
# id and light_entity, NOT list position like v1's CFG.houseView.markers --
# v1's browser-local single-client model made index-splicing safe; v2's
# WebSocket-synced, potentially-multi-client model doesn't have that
# guarantee, and the light_name attribute bug already showed positional/
# name-based joins drift where entity-id joins don't.
CONF_HOUSE_VIEW_MARKERS = "house_view_markers"

SERVICE_SET_HOUSE_VIEW = "set_house_view"
SERVICE_ADD_HOUSE_MARKER = "add_house_marker"
SERVICE_ASSIGN_HOUSE_MARKER = "assign_house_marker"
SERVICE_REMOVE_HOUSE_MARKER = "remove_house_marker"

ATTR_MODE = "mode"
ATTR_PATH = "path"
ATTR_X = "x"
ATTR_Y = "y"
ATTR_Z = "z"
ATTR_MARKER_ID = "marker_id"
ATTR_LIGHT_ENTITY = "light_entity"

DEFAULT_START_TIME = "19:00"
DEFAULT_END_TIME = "23:00"
DEFAULT_FADE_IN = 30
DEFAULT_FADE_OUT = 120
DEFAULT_WARMWHITE_TIME = "22:00"
DEFAULT_VERIFY_RETRY_COUNT = 2
DEFAULT_VERIFY_CHECK_DELAY = 180

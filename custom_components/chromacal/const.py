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

DEFAULT_START_TIME = "19:00"
DEFAULT_END_TIME = "23:00"
DEFAULT_FADE_IN = 30
DEFAULT_FADE_OUT = 120
DEFAULT_WARMWHITE_TIME = "22:00"

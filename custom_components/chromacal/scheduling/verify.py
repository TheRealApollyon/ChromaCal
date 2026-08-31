"""Pure logic for verify-and-retry (Plan A): does a light's real reported
state match what a FireCommand asked for, and what should a retry attempt
actually send?

Kept separate from coordinator.py the same way fire.py already is -- the
real async I/O (sleeping, reading hass.states, re-issuing the service call,
notifying) lives in the coordinator; this module is pure and testable
without Home Assistant installed at all (see tests/scheduling/'s
docstring and pytest.ini).

All constants here are real, hardware-proven values from Shane's own
"Outside Lights - Late Night Off" automation, not invented -- see
CLAUDE.md's root-cause writeup for the light flip-back investigation this
feature exists to catch, and for why that automation's retry passes use a
short transition instead of replaying the full fade.
"""

from __future__ import annotations

from dataclasses import replace

from .fire import FireCommand

# Between-retries delay. The initial post-fire delay before the first check
# is per-light configurable (LightConfig.verify_check_delay); this one
# isn't exposed as a config field -- it's a fixed value matching the proven
# automation, keeping the config surface to the three fields that were
# actually asked for instead of growing a fourth knob.
VERIFY_RETRY_INTERVAL_SECONDS = 60

# A retry re-fires the same command, but with this short transition instead
# of replaying the original (possibly 120s) fade -- matches the proven
# automation's own retry passes exactly.
RETRY_TRANSITION_SECONDS = 5

# Relative, not absolute: v1 used a fixed near-Zigbee-max floor
# (BRIGHTNESS_THRESHOLD = 253 out of 254) because it always commanded
# near-max brightness. v2's "default" tier deliberately commands
# brightness: 200, not max, so a fixed floor would misfire on every normal
# Default-tier check -- this compares against what was actually commanded
# instead.
BRIGHTNESS_TOLERANCE_FRACTION = 0.10


def expects_on(command: FireCommand) -> bool:
    """Does this command's own service imply the light should end up on?"""
    return command.service == "turn_on"


def is_verifiable(command: FireCommand | None) -> bool:
    """Only real on/off transitions are worth verifying -- a command with
    neither service is a defensive case build_fire_command never actually
    produces, and None means nothing fired at all (a 'pre'/'warmup' no-op)."""
    return command is not None and command.service in ("turn_on", "turn_off")


def _commanded_brightness_0_255(command: FireCommand) -> float | None:
    """Normalize whichever brightness key a command used onto HA's own
    0-255 `brightness` attribute scale. build_fire_command's on-commands
    all use `brightness` (0-255); build_force_white_command uses
    `brightness_pct` (0-100) instead -- both need to compare against the
    same real reported value."""
    if "brightness" in command.service_data:
        return command.service_data["brightness"]
    if "brightness_pct" in command.service_data:
        return command.service_data["brightness_pct"] * 255 / 100
    return None


def state_matches(
    command: FireCommand, actual_state: str | None, actual_brightness: int | None
) -> bool:
    """Does the light's real reported state satisfy what `command` asked
    for? Off is an exact match. On requires state == "on", plus -- only if
    the command itself set a brightness AND the entity actually reports one
    back -- the reported brightness landing within
    BRIGHTNESS_TOLERANCE_FRACTION of what was commanded, not an exact byte
    match: `light.shane_office_dongle_outside_lights_zha`, the entity this
    whole feature was built to protect, is itself a 4-bulb ZHA group, and
    group-reported brightness is an aggregate, not a byte-exact echo of the
    commanded value.

    actual_brightness is None either way for an onoff-only light or a
    `switch` entity (config_flow.py's EntitySelector allows both domains,
    not just dimmable lights) -- confirmed live in the disposable
    multi-light container: an onoff-only template light was failing verify
    on every single check, forever, because it can structurally never
    report a brightness back. Nothing to compare against means nothing to
    fail on -- the on/off state is the only real signal such an entity can
    ever give, so that alone has to be enough.
    """
    if not expects_on(command):
        return actual_state == "off"

    if actual_state != "on":
        return False

    commanded_brightness = _commanded_brightness_0_255(command)
    if commanded_brightness is None or actual_brightness is None:
        return True
    tolerance = commanded_brightness * BRIGHTNESS_TOLERANCE_FRACTION
    return abs(actual_brightness - commanded_brightness) <= tolerance


def build_retry_command(command: FireCommand) -> FireCommand:
    """Same command, but with a short transition instead of replaying the
    original fade -- matches the proven automation's own retry passes
    (`transition: 5`, not another 120s), so a retry corrects the state
    quickly rather than repeating a two-minute fade that may itself be
    part of what needs correcting.
    """
    if "transition" not in command.service_data:
        return command
    return replace(
        command,
        service_data={**command.service_data, "transition": RETRY_TRANSITION_SECONDS},
    )

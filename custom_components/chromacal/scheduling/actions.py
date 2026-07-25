"""Pure, Docker-free logic for the one-shot/quick-control actions:
21 Gun Salute, Emergency Mode, and Force White.

Everything here is data -- what steps a Salute goes through, what colors an
Emergency pattern alternates between, what command Force White issues.
The actual asyncio sequencing (awaiting between steps, issuing the real
service calls, the repeating Emergency interval) lives in coordinator.py;
none of that is testable without Home Assistant, so it stays out of here,
same split as scheduling/fire.py's build_fire_command().

Ported from chromacal.html's fire21GunSalute()/startEmergency()/
forceWhiteCustom() (see those functions for the pace/pattern research and
reasoning already documented there -- not repeated here).
"""

from __future__ import annotations

from dataclasses import dataclass

from .fire import FireCommand

RGB = tuple[int, int, int]


@dataclass(frozen=True)
class SaluteStep:
    """One step of the Salute sequence: set a color/brightness (or turn off),
    then hold for hold_ms before the next step."""

    label: str
    rgb: RGB | None  # None means turn_off, not "no color data"
    brightness_pct: int
    transition: float
    hold_ms: int


# Timing per pace, matching v1's SALUTE_PACES exactly -- these values came
# from real hardware testing (see chromacal.html's 21 GUN SALUTE comment
# block), not arbitrary choices to relitigate here.
_SALUTE_PACES = {
    "fast": {"flash_on": 1200, "afterglow": 1800, "pause": 1200, "taps_hold": 25000, "fade_out": 4000},
    "standard": {"flash_on": 1800, "afterglow": 2500, "pause": 1800, "taps_hold": 35000, "fade_out": 6000},
    "slow": {"flash_on": 2200, "afterglow": 3200, "pause": 2500, "taps_hold": 45000, "fade_out": 8000},
}

_CMD_TRANSITION = 1.0  # seconds -- matches v1's fixed 1.0s transition for volley/afterglow/pause steps


def get_salute_steps(pace: str = "standard") -> list[SaluteStep]:
    """The full ordered Salute sequence for one light: 3 volleys (white flash,
    red afterglow, pause -- except no pause after the third), then Taps, then
    a fade-out. hold_ms on the final fade-out step is the transition time
    itself (there's nothing to hold afterward), matching v1's structure of
    firing lightOff with pace.fadeOut as the transition and then waiting that
    same duration before considering the sequence complete.
    """
    pace_cfg = _SALUTE_PACES.get(pace, _SALUTE_PACES["standard"])
    steps: list[SaluteStep] = []

    for volley in range(1, 4):
        steps.append(
            SaluteStep(f"volley {volley} flash", (255, 255, 255), 100, _CMD_TRANSITION, pace_cfg["flash_on"])
        )
        steps.append(
            SaluteStep(f"volley {volley} afterglow", (60, 0, 0), 20, _CMD_TRANSITION, pace_cfg["afterglow"])
        )
        if volley < 3:
            steps.append(SaluteStep(f"volley {volley} pause", None, 0, _CMD_TRANSITION, pace_cfg["pause"]))

    steps.append(SaluteStep("taps", (255, 147, 41), 35, _CMD_TRANSITION, pace_cfg["taps_hold"]))
    fade_out_s = pace_cfg["fade_out"] / 1000
    steps.append(SaluteStep("fade out", None, 0, fade_out_s, pace_cfg["fade_out"]))

    return steps


# Emergency pattern sequences, matching v1's startEmergency() exactly.
# None means turn_off (used by the "amber" pattern's alternation with dark,
# matching the real roadway/construction emergency convention of a single
# pulsing light rather than two alternating colors).
_EMERGENCY_PATTERNS: dict[str, list[RGB | None]] = {
    "red-blue": [(255, 0, 0), (0, 0, 255)],
    "blue": [(0, 0, 255), (255, 255, 255)],
    "amber": [(255, 140, 0), None],
    "red-white": [(255, 0, 0), (255, 255, 255)],
}

EMERGENCY_TRANSITION = 0.1  # seconds -- matches v1's EMG_TRANSITION


def get_emergency_sequence(pattern: str) -> list[RGB | None]:
    """The alternating color sequence for an Emergency pattern. Falls back to
    solid red for an unrecognized pattern name, matching v1's `else
    sequence = ['#FF0000']`.
    """
    return _EMERGENCY_PATTERNS.get(pattern, [(255, 0, 0)])


def build_force_white_command(kelvin: int) -> FireCommand:
    """The service call Force White issues: a fixed-Kelvin warm white at full
    brightness. Matches v1's forceWhiteCustom() minus the Kelvin picker --
    kelvin here is the light's own configured warmwhite Kelvin (see the
    Phase 5b plan discussion for why a fixed per-light value was chosen over
    a paired selector entity).
    """
    return FireCommand(
        "light",
        "turn_on",
        {"color_temp_kelvin": kelvin, "brightness_pct": 100, "transition": 3},
    )

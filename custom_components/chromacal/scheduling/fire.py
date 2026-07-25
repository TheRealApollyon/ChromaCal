"""Ports the command-construction half of fireScheduledCommand() from
chromacal.html -- what service call SHOULD fire for a given desired-state
key. The actual hass.services.async_call() happens in the coordinator;
everything here is pure and testable without Home Assistant.

Not ported: applyIntensity()'s saturation/brightness adjustment. No config
flow collects CFG.lightingStyle or a per-light intensityOverride yet, so
v1's real-world effective value is always 'balanced' (satMul=1, briMul=1,
a no-op) -- skipping it here produces identical output to porting it and
always hitting that no-op branch. Add it when that config surface exists.

Ongoing multi-color cycling: v1 got that from its bridge/Blueprint pub-sub
path, not from repeated fireScheduledCommand calls (that function only ever
fired once per key transition). This module's build_fire_command() still
only computes one color-index snapshot per call; the ~60s re-check that
detects "has the index advanced" and re-invokes this to get the next color
lives in coordinator.py's async_recheck_color_cycle(), not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .engine import LightConfig
from .models import NightSegment


@dataclass(frozen=True)
class FireCommand:
    """A service call to make: domain.service(entity_id=..., **service_data)."""

    domain: str
    service: str
    service_data: dict[str, Any]


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def build_fire_command(
    key: str, light: LightConfig, segments: list[NightSegment], now: datetime
) -> FireCommand | None:
    """What service call corresponds to desired-state `key`?

    Returns None for 'warmup'/'pre' (do nothing, matching v1) and for an
    'event:X' key whose segment can't be found (defensive, mirrors v1's
    early return there).
    """
    now_hour = now.hour + now.minute / 60 + now.second / 3600
    fade_in = light.fade_in or 30
    fade_out = light.fade_out or 120

    if key == "off":
        return FireCommand("light", "turn_off", {"transition": fade_out})

    if key == "warmwhite":
        if light.warmwhite_color:
            r, g, b = _hex_to_rgb(light.warmwhite_color)
            color_data: dict[str, Any] = {"rgb_color": [r, g, b]}
        else:
            kelvin = round(1_000_000 / (light.warmwhite_kelvin_mireds or 250))
            color_data = {"color_temp_kelvin": kelvin}
        return FireCommand(
            "light",
            "turn_on",
            {**color_data, "brightness": 255, "transition": max(fade_in, 30)},
        )

    if key.startswith("event:"):
        event_name = key[len("event:") :]
        segment = next((s for s in segments if s.event.name == event_name), None)
        if segment is None:
            return None
        colors = segment.event.colors or ("#FFC97A",)
        rgbs = [_hex_to_rgb(h) for h in colors]
        # Elapsed-time-based color index: stateless, matches v1, but only
        # ever evaluated once per key transition here -- see module
        # docstring on why this doesn't yet produce ongoing cycling.
        elapsed_sec = max(0.0, (now_hour - segment.start_hour) * 3600)
        color_idx = int(elapsed_sec // 60) % len(rgbs) if len(rgbs) > 1 else 0
        r, g, b = rgbs[color_idx]
        return FireCommand(
            "light",
            "turn_on",
            {"rgb_color": [r, g, b], "brightness": 255, "transition": fade_in},
        )

    if key == "default":
        kelvin = round(1_000_000 / (light.warmwhite_kelvin_mireds or 250))
        return FireCommand(
            "light",
            "turn_on",
            {"color_temp_kelvin": kelvin, "brightness": 200, "transition": fade_in},
        )

    return None  # 'warmup' and 'pre': do nothing

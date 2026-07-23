"""Ports v1's fetchSunset() hour-extraction logic from chromacal.html.

sun.sun's `next_setting` attribute is always the next chronological sunset
event: if today's hasn't happened yet, it *is* today's; if today's already
passed, it's tomorrow's. hoursUntil > 2 picks between using it directly vs.
subtracting 24h and re-deriving the local hour/minute from that adjusted
instant. In practice this only changes anything right at a DST boundary
(see the Phase 2c plan discussion) — ported faithfully anyway, per v1.
"""

from __future__ import annotations

from datetime import datetime, timedelta


def resolve_sunset_hour(now: datetime, next_setting: datetime) -> float:
    """Return today's approximate sunset as a decimal hour (e.g. 20.32 = 20:19).

    now/next_setting must both be timezone-aware, in the same local zone.
    """
    hours_until = (next_setting - now).total_seconds() / 3600
    target = next_setting if hours_until > 2 else next_setting - timedelta(hours=24)
    return target.hour + target.minute / 60

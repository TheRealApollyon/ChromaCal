import type { LightCardModel } from "./grouping";

/** 16:00 today through 08:00 tomorrow -- the window every night-schedule
 * segment chromacal produces should fall inside (see get_night_segments). */
export const WINDOW_START_MIN = 16 * 60;
export const WINDOW_SPAN_MIN = 16 * 60;

export function hhmmToMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

/** Wraps a raw minutes-of-day value (0-1439) into the fixed night window's
 * basis, so anything before 16:00 is treated as "the next day" -- this is
 * what lets a segment or marker crossing midnight compare/position
 * correctly against ones that don't. */
function toWindowMinutes(rawMinutes: number): number {
  return rawMinutes >= WINDOW_START_MIN ? rawMinutes : rawMinutes + 24 * 60;
}

/** Exported alongside hhmmToWindowMinutes below so callers outside this
 * module (Tonight's Schedule's phase-list done/active comparisons) use
 * the same midnight-wrapping semantics as the timeline marks themselves,
 * instead of a second, potentially-inconsistent HH:MM comparison. */
export function hourToWindowMinutes(hour: number): number {
  return toWindowMinutes(Math.round(hour * 60));
}

export function hhmmToWindowMinutes(hhmm: string): number {
  return toWindowMinutes(hhmmToMinutes(hhmm));
}

function windowMinutesToPct(windowMinutes: number): number {
  return Math.max(0, Math.min(100, ((windowMinutes - WINDOW_START_MIN) / WINDOW_SPAN_MIN) * 100));
}

/** Positions a HH:MM-HH:MM segment inside the fixed night window, wrapping
 * anything before 16:00 to "the next day" so a segment crossing midnight
 * still renders as one continuous span. */
export function segmentPosition(startTime: string, endTime: string): { leftPct: number; widthPct: number } {
  const leftPct = windowMinutesToPct(hhmmToWindowMinutes(startTime));
  const rightPct = windowMinutesToPct(hhmmToWindowMinutes(endTime));
  return { leftPct, widthPct: Math.max(0, rightPct - leftPct) };
}

export function formatHour(hour: number): string {
  const totalMinutes = Math.round(hour * 60) % (24 * 60);
  const h = Math.floor(totalMinutes / 60);
  const m = totalMinutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

/** "Xh Xm until 22:00"-style countdown, for Tonight's Schedule's two
 * countdown lines above the phase list. null if there's no target (the
 * relevant toggle is off) or it's already passed for tonight -- callers
 * render nothing in either case, not a stale/negative countdown. */
export function formatCountdown(nowHour: number, targetHHMM: string | null): string | null {
  if (targetHHMM === null) return null;
  const diffMin = hhmmToWindowMinutes(targetHHMM) - hourToWindowMinutes(nowHour);
  if (diffMin <= 0) return null;
  const h = Math.floor(diffMin / 60);
  const m = diffMin % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

/** A "HH:MM" time plus some minutes, wrapping past midnight -- e.g.
 * Verify Off's fixed off-time + 30 minutes. Pure clock math, not
 * night-window-relative like the timeline helpers above (those compare
 * two points; this computes a new one from a single starting point). */
export function addMinutesToHHMM(hhmm: string, minutes: number): string {
  const wrapped = (((hhmmToMinutes(hhmm) + minutes) % (24 * 60)) + 24 * 60) % (24 * 60);
  const h = Math.floor(wrapped / 60);
  const m = wrapped % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export interface TimelineMark {
  label: string;
  time: string;
  windowMinutes: number;
  leftPct: number;
  emphasize: boolean;
  /** Set during collision resolution -- render the tick line only, no label. */
  bare: boolean;
}

/**
 * Ports v1's mkr()/markers array: WARM/OFF (whichever applies), NOW,
 * SUNSET/COLORS (only shown if still ahead of now). FADE IN is
 * deliberately not ported -- it needs fade_in/start_offset data the
 * sensor doesn't expose yet, and wasn't part of the explicit
 * NOW/COLORS/WARM/OFF ask this was scoped against.
 *
 * schedule_end_time (light.scheduleEndTime) is what makes WARM vs OFF
 * distinguishable: get_night_segments caps a light's last segment at
 * warm-white's start whenever warm-white is enabled and earlier than the
 * light's real off-time, so "last segment end < schedule end" is exactly
 * "warm-white is active before off" -- see engine.py's resolve_cfg_end_hour.
 *
 * Collision resolution is priority-based, not time-order-based -- a real
 * live bug found 2026-09: a default light's WARM (warmwhite_time) and OFF
 * (schedule end) sit only ~6.25% of the window apart by default (e.g.
 * 22:00/23:00), inside the 9% LABEL_MIN_GAP_PCT radius, so the old
 * single left-to-right pass would silently blank whichever of WARM/OFF
 * lost the tie -- and when NOW also landed nearby, all three could go
 * label-less at once. WARM/OFF are the two marks that actually matter
 * operationally, so they're processed first and never suppressed, no
 * matter how close together they land; NOW only yields to WARM/OFF;
 * SUNSET/COLORS (pure context) yield to whatever's already been
 * accepted. Left-to-right position on the timeline stays pure time --
 * only which labels are allowed to render changes.
 */
type RawMark = {
  label: string;
  time: string;
  windowMinutes: number;
  emphasize: boolean;
  priority: number; // 0 = WARM/OFF, 1 = NOW, 2 = SUNSET/COLORS
};

export function buildTimelineMarks(light: LightCardModel, nowHour: number): TimelineMark[] {
  const nowWindowMin = hourToWindowMinutes(nowHour);
  const raw: RawMark[] = [];

  const lastSegment = light.segments[light.segments.length - 1];
  if (lastSegment) {
    const lastEndWindowMin = hhmmToWindowMinutes(lastSegment.endTime);
    const scheduleEndWindowMin =
      light.scheduleEndTime !== null ? hhmmToWindowMinutes(light.scheduleEndTime) : null;

    if (scheduleEndWindowMin !== null && lastEndWindowMin < scheduleEndWindowMin) {
      raw.push({ label: "WARM", time: lastSegment.endTime, windowMinutes: lastEndWindowMin, emphasize: false, priority: 0 });
      raw.push({
        label: "OFF",
        time: light.scheduleEndTime as string,
        windowMinutes: scheduleEndWindowMin,
        emphasize: true,
        priority: 0,
      });
    } else {
      raw.push({ label: "OFF", time: lastSegment.endTime, windowMinutes: lastEndWindowMin, emphasize: true, priority: 0 });
    }
  }

  raw.push({ label: "NOW", time: formatHour(nowHour), windowMinutes: nowWindowMin, emphasize: false, priority: 1 });

  if (light.sunsetHour !== null) {
    const sunsetWindowMin = hourToWindowMinutes(light.sunsetHour);
    if (sunsetWindowMin > nowWindowMin) {
      raw.push({ label: "SUNSET", time: formatHour(light.sunsetHour), windowMinutes: sunsetWindowMin, emphasize: false, priority: 2 });
    }
  }

  const firstSegment = light.segments[0];
  if (firstSegment) {
    const colorsWindowMin = hhmmToWindowMinutes(firstSegment.startTime);
    if (colorsWindowMin > nowWindowMin) {
      raw.push({ label: "COLORS", time: firstSegment.startTime, windowMinutes: colorsWindowMin, emphasize: false, priority: 2 });
    }
  }

  const LABEL_MIN_GAP_PCT = 9;
  const withPct = raw.map((mark) => ({ ...mark, leftPct: windowMinutesToPct(mark.windowMinutes) }));
  const byPriority = [...withPct].sort((a, b) => a.priority - b.priority || a.windowMinutes - b.windowMinutes);

  const acceptedPcts: number[] = [];
  const bareByMark = new Map<(typeof withPct)[number], boolean>();
  for (const mark of byPriority) {
    const collides =
      mark.priority > 0 && acceptedPcts.some((pct) => Math.abs(mark.leftPct - pct) < LABEL_MIN_GAP_PCT);
    bareByMark.set(mark, collides);
    if (!collides) acceptedPcts.push(mark.leftPct);
  }

  return withPct
    .sort((a, b) => a.windowMinutes - b.windowMinutes)
    .map((mark) => ({
      label: mark.label,
      time: mark.time,
      windowMinutes: mark.windowMinutes,
      leftPct: mark.leftPct,
      emphasize: mark.emphasize,
      bare: bareByMark.get(mark) ?? false,
    }));
}

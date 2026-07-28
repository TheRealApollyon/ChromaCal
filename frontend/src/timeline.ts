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

function hourToWindowMinutes(hour: number): number {
  return toWindowMinutes(Math.round(hour * 60));
}

function hhmmToWindowMinutes(hhmm: string): number {
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

function formatHour(hour: number): string {
  const totalMinutes = Math.round(hour * 60) % (24 * 60);
  const h = Math.floor(totalMinutes / 60);
  const m = totalMinutes % 60;
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
 * Ports v1's mkr()/markers array: NOW always first, then SUNSET/COLORS
 * (only shown if still ahead of now), then whichever of WARM/OFF actually
 * applies. FADE IN is deliberately not ported -- it needs fade_in/
 * start_offset data the sensor doesn't expose yet, and wasn't part of the
 * explicit NOW/COLORS/WARM/OFF ask this was scoped against.
 *
 * schedule_end_time (light.scheduleEndTime) is what makes WARM vs OFF
 * distinguishable: get_night_segments caps a light's last segment at
 * warm-white's start whenever warm-white is enabled and earlier than the
 * light's real off-time, so "last segment end < schedule end" is exactly
 * "warm-white is active before off" -- see engine.py's resolve_cfg_end_hour.
 */
export function buildTimelineMarks(light: LightCardModel, nowHour: number): TimelineMark[] {
  const nowWindowMin = hourToWindowMinutes(nowHour);
  const raw: Omit<TimelineMark, "leftPct" | "bare">[] = [
    { label: "NOW", time: formatHour(nowHour), windowMinutes: nowWindowMin, emphasize: false },
  ];

  if (light.sunsetHour !== null) {
    const sunsetWindowMin = hourToWindowMinutes(light.sunsetHour);
    if (sunsetWindowMin > nowWindowMin) {
      raw.push({
        label: "SUNSET",
        time: formatHour(light.sunsetHour),
        windowMinutes: sunsetWindowMin,
        emphasize: false,
      });
    }
  }

  const firstSegment = light.segments[0];
  if (firstSegment) {
    const colorsWindowMin = hhmmToWindowMinutes(firstSegment.startTime);
    if (colorsWindowMin > nowWindowMin) {
      raw.push({
        label: "COLORS",
        time: firstSegment.startTime,
        windowMinutes: colorsWindowMin,
        emphasize: false,
      });
    }
  }

  const lastSegment = light.segments[light.segments.length - 1];
  if (lastSegment) {
    const lastEndWindowMin = hhmmToWindowMinutes(lastSegment.endTime);
    const scheduleEndWindowMin =
      light.scheduleEndTime !== null ? hhmmToWindowMinutes(light.scheduleEndTime) : null;

    if (scheduleEndWindowMin !== null && lastEndWindowMin < scheduleEndWindowMin) {
      raw.push({ label: "WARM", time: lastSegment.endTime, windowMinutes: lastEndWindowMin, emphasize: false });
      raw.push({
        label: "OFF",
        time: light.scheduleEndTime as string,
        windowMinutes: scheduleEndWindowMin,
        emphasize: true,
      });
    } else {
      raw.push({ label: "OFF", time: lastSegment.endTime, windowMinutes: lastEndWindowMin, emphasize: true });
    }
  }

  // Collision pass, ported from v1: hide a label (keep its tick line) if
  // it'd land within ~9% of the window's width from the last shown label.
  const LABEL_MIN_GAP_PCT = 9;
  let lastShownPct = -999;
  return raw
    .sort((a, b) => a.windowMinutes - b.windowMinutes)
    .map((mark) => {
      const leftPct = windowMinutesToPct(mark.windowMinutes);
      const bare = leftPct - lastShownPct < LABEL_MIN_GAP_PCT;
      if (!bare) lastShownPct = leftPct;
      return { ...mark, leftPct, bare };
    });
}

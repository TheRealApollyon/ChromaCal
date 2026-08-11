import type { HomeAssistant } from "./types";

/**
 * Translates ChromaCal's entity set into a view model for rendering,
 * grouping by the role/scope/light_entity attributes the backend exposes
 * (see switch.py/button.py/sensor.py) rather than by parsing display
 * names -- a user renaming an entity in the HA UI must not break this.
 */

export interface SegmentModel {
  name: string;
  eventType: string;
  colors: string[];
  icon: string;
  startTime: string;
  endTime: string;
}

/** The wire shape sensor.py actually emits (see its extra_state_attributes)
 * -- snake_case, straight out of Python. Kept distinct from SegmentModel
 * (camelCase, used everywhere else in this component) so the one place
 * that translates between them is obvious and can't silently drift. */
interface RawSegment {
  name: string;
  event_type: string;
  colors: string[];
  icon: string;
  start_time: string;
  end_time: string;
}

function mapSegment(raw: RawSegment): SegmentModel {
  return {
    name: raw.name,
    eventType: raw.event_type,
    colors: raw.colors,
    icon: raw.icon,
    startTime: raw.start_time,
    endTime: raw.end_time,
  };
}

export interface LightCardModel {
  lightEntity: string;
  lightName: string;
  scheduleEntityId: string;
  forceWhiteEntityId: string | null;
  currentEventName: string | null;
  currentEventType: string | null;
  currentColors: string[];
  currentIcon: string | null;
  currentStart: string | null;
  currentEnd: string | null;
  segments: SegmentModel[];
  sunsetHour: number | null;
  /** The light's configured off-time ("HH:MM"), for the OFF/DAWN timeline
   * marker -- see engine.py's resolve_cfg_end_hour and sensor.py. */
  scheduleEndTime: string | null;
}

export interface SkipModel {
  entityId: string;
  eventName: string;
  isOn: boolean;
}

export interface UpcomingEventModel {
  date: string;
  name: string;
  category: string;
  eventType: string;
  icon: string;
  colors: string[];
  isToday: boolean;
  isPersonalRange: boolean;
  permanentSkip: SkipModel | null;
  /** Only set for today's events with a real tonight-skip switch --
   * "tonight" has no meaning for a future date, same restriction the
   * backend itself already enforces (tonight-skip switches only exist
   * for today's candidates). */
  tonightSkip: SkipModel | null;
  /** True if this is today's event AND it's the one currently picked
   * (all-lights -- see coordinator.py's tonight_pick field docstring).
   * Only meaningful for today, same restriction as tonightSkip above. */
  isPicked: boolean;
  /** This event's current color override, or null if it's running its
   * built-in default colors. Present regardless of date (v1's 🎨 button
   * works on any day, not just today -- see chromacal-panel.ts). */
  overrideColors: string[] | null;
}

/** The wire shape of one entry in the Upcoming Events sensor's `events`
 * attribute -- see sensor.py's ChromaCalUpcomingEventsSensor. */
interface RawUpcomingEvent {
  date: string;
  name: string;
  category: string;
  event_type: string;
  icon: string;
  colors: string[];
  is_today: boolean;
  is_personal_range: boolean;
}

/** Wire shape of the Upcoming Events sensor's own top-level attributes
 * (siblings of `events`, not per-event) -- see sensor.py. */
interface RawUpcomingAttrs {
  events?: RawUpcomingEvent[];
  tonight_pick?: string | null;
  color_overrides?: Record<string, string[]>;
}

export interface GlobalControlsModel {
  saluteEntityId: string | null;
  saluteRunning: boolean;
  catchUpEntityId: string | null;
  stopEntityId: string | null;
  emergencyEntityId: string | null;
  emergencyOn: boolean;
}

export interface PanelViewModel {
  globals: GlobalControlsModel;
  lights: LightCardModel[];
  tonightSkips: SkipModel[];
  permanentSkips: SkipModel[];
  upcomingEvents: UpcomingEventModel[];
}

function ownEntityIds(hass: HomeAssistant): string[] {
  return Object.values(hass.entities)
    .filter((entry) => entry.platform === "chromacal")
    .map((entry) => entry.entity_id);
}

function domainOf(entityId: string): string {
  return entityId.split(".", 1)[0];
}

export function buildViewModel(hass: HomeAssistant): PanelViewModel {
  const ids = ownEntityIds(hass);

  const globals: GlobalControlsModel = {
    saluteEntityId: null,
    saluteRunning: false,
    catchUpEntityId: null,
    stopEntityId: null,
    emergencyEntityId: null,
    emergencyOn: false,
  };

  const scheduleByLight = new Map<string, string>();
  const forceWhiteByLight = new Map<string, string>();
  const tonightSkips: SkipModel[] = [];
  const permanentSkips: SkipModel[] = [];
  let upcomingEventsEntityId: string | null = null;

  for (const entityId of ids) {
    const state = hass.states[entityId];
    if (!state) continue;
    const attrs = state.attributes;
    const domain = domainOf(entityId);

    if (domain === "button") {
      const role = attrs.role as string | undefined;
      if (role === "salute") {
        globals.saluteEntityId = entityId;
        globals.saluteRunning = Boolean(attrs.running);
      } else if (role === "catch_up_sync") {
        globals.catchUpEntityId = entityId;
      } else if (role === "stop") {
        globals.stopEntityId = entityId;
      } else if (role === "force_white" && typeof attrs.light_entity === "string") {
        forceWhiteByLight.set(attrs.light_entity, entityId);
      }
      continue;
    }

    if (domain === "switch") {
      const role = attrs.role as string | undefined;
      if (role === "emergency_mode") {
        globals.emergencyEntityId = entityId;
        globals.emergencyOn = state.state === "on";
      } else if (role === "skip" && typeof attrs.event_name === "string") {
        const skip: SkipModel = {
          entityId,
          eventName: attrs.event_name,
          isOn: state.state === "on",
        };
        if (attrs.scope === "tonight") tonightSkips.push(skip);
        else permanentSkips.push(skip);
      }
      continue;
    }

    if (domain === "sensor") {
      if (attrs.role === "upcoming_events") {
        upcomingEventsEntityId = entityId;
      } else if (typeof attrs.light_entity === "string") {
        scheduleByLight.set(attrs.light_entity, entityId);
      }
    }
  }

  const lights: LightCardModel[] = [];
  for (const [lightEntity, scheduleEntityId] of scheduleByLight) {
    const scheduleState = hass.states[scheduleEntityId];
    const scheduleAttrs = scheduleState?.attributes ?? {};
    // ChromaCal's own configured name (sensor.py's light_name attribute),
    // NOT the underlying light entity's own friendly_name -- those can
    // freely differ (e.g. a light named "Kitchen Lights" by its own
    // integration, configured in ChromaCal as "Living Room Overhead
    // Lights"). Reading the entity's friendly_name here silently showed
    // the wrong name for any light renamed away from its entity's own
    // name -- found live while visually verifying Phase 10's compact
    // card. Falls back to the entity id only if the sensor hasn't
    // reported yet, same as every other scheduleAttrs read below.
    const lightName = (scheduleAttrs.light_name as string | undefined) ?? lightEntity;

    lights.push({
      lightEntity,
      lightName,
      scheduleEntityId,
      forceWhiteEntityId: forceWhiteByLight.get(lightEntity) ?? null,
      currentEventName: (scheduleState?.state as string) || null,
      currentEventType: (scheduleAttrs.event_type as string) ?? null,
      currentColors: (scheduleAttrs.colors as string[]) ?? [],
      currentIcon: (scheduleAttrs.icon as string) ?? null,
      currentStart: (scheduleAttrs.start_time as string) ?? null,
      currentEnd: (scheduleAttrs.end_time as string) ?? null,
      segments: ((scheduleAttrs.segments as RawSegment[] | undefined) ?? []).map(mapSegment),
      sunsetHour: (scheduleAttrs.sunset_hour as number) ?? null,
      scheduleEndTime: (scheduleAttrs.schedule_end_time as string) ?? null,
    });
  }
  lights.sort((a, b) => a.lightName.localeCompare(b.lightName));

  tonightSkips.sort((a, b) => a.eventName.localeCompare(b.eventName));
  permanentSkips.sort((a, b) => a.eventName.localeCompare(b.eventName));

  const permanentSkipByName = new Map(permanentSkips.map((s) => [s.eventName, s]));
  const tonightSkipByName = new Map(tonightSkips.map((s) => [s.eventName, s]));
  const upcomingAttrs = (upcomingEventsEntityId
    ? hass.states[upcomingEventsEntityId]?.attributes
    : undefined) as RawUpcomingAttrs | undefined;
  const rawEvents = upcomingAttrs?.events ?? [];
  const tonightPick = upcomingAttrs?.tonight_pick ?? null;
  const colorOverrides = upcomingAttrs?.color_overrides ?? {};
  const upcomingEvents: UpcomingEventModel[] = rawEvents.map((e) => ({
    date: e.date,
    name: e.name,
    category: e.category,
    eventType: e.event_type,
    icon: e.icon,
    colors: e.colors,
    isToday: e.is_today,
    isPersonalRange: e.is_personal_range,
    permanentSkip: permanentSkipByName.get(e.name) ?? null,
    tonightSkip: e.is_today ? (tonightSkipByName.get(e.name) ?? null) : null,
    isPicked: e.is_today && tonightPick === e.name,
    overrideColors: colorOverrides[e.name] ?? null,
  }));

  return { globals, lights, tonightSkips, permanentSkips, upcomingEvents };
}

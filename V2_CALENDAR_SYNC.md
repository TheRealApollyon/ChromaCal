# ChromaCal v2: Calendar Sync

Your idea originally, and a particularly good fit for v2 specifically, not just generically nice to have.

## Foundation

Home Assistant exposes calendar entities, Google Calendar, CalDAV, a local calendar, whatever someone's already connected, through a documented action, `calendar.get_events`. Point it at a calendar entity and a date range, get back a list of events, each with a title, start, end, and optionally a description and location.

Two real findings worth designing around rather than discovering later:

Recurring events are already expanded before ChromaCal would ever see them. A weekly "Game Night" doesn't come back as one event with a repeat rule attached, it comes back as a separate entry for every individual Friday in the requested range. Nothing about recurrence needs to be built here at all.

The calendar entity's own state isn't reliable for this. It only ever tracks one upcoming event and breaks down with overlapping events or same-time events. The real mechanism has to be calling `calendar.get_events` directly over a date range, the same way ChromaCal already pulls its 45-day holiday lookahead today. Calendar sync isn't really a new mechanism, it's a second source feeding the one that already exists.

## The design

Pick a calendar entity once, in settings. ChromaCal queries it over the same lookahead window it already uses for everything else, today through 45 days out. Every returned event gets checked against a saved list of title-to-colors mappings, plain exact match, case-insensitive, nothing fuzzy. A match becomes a real entry in the existing Upcoming list, same row style, same 🎨 customize button already built for holidays tonight, just sourced from a calendar instead of the built-in catalog.

Creating a new mapping in the first place is a small, separate UI piece, name a title, like "Game Night," pick colors, save. Functionally close to how Personal Events already work today, reused rather than reinvented.

## A deliberate scope boundary, not an oversight

A matched calendar event gets treated exactly like any other date-based ChromaCal event, sunset to late night, same as a holiday. It does not fire at the event's own specific start time, a 2pm birthday party doesn't make lights come on at 2pm.

That's a real, deliberate line, not a missing feature. Reacting to a calendar event's actual clock time, not just its date, is a genuinely different trigger model than anything currently in ChromaCal, and it overlaps directly with the custom timeline builder already flagged as its own dedicated piece of work, not something to fold in here. Calendar sync's job is supplying a new source of dates. Deciding what happens at exactly what time of day is the other project's territory.

## Open, not yet decided

**Multiple calendars at once.** `calendar.get_events` already supports targeting more than one calendar entity in a single call, so nothing technical blocks this. Starting with one calendar is the simpler default, worth deciding deliberately whether multi-calendar support is a real v1-of-this-feature requirement or a later addition.

**All-day versus timed events.** Given the date-based design above, this mostly doesn't matter, an all-day event and a timed event both just mean "this day," but worth confirming that holds cleanly once this is actually built rather than assumed.

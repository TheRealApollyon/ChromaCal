# ChromaCal: What This Actually Is

Written because the project's gotten big enough that the shape of it stopped being obvious from the feature list alone. This isn't a roadmap and it isn't a feature spec, it's the thing to come back to when a new idea shows up and the question is "does this even belong here, and if so, where."

## The actual job

Strip away everything else and ChromaCal does one thing: it translates "something is happening" into "the lights should look like this." Every feature, the built-in calendar, Personal Events, Calendar Sync, WLED support, the whole scheduling engine, exists in service of that one translation. Nothing about ChromaCal is actually about calendars, or about lights, on their own. It's the bridge between the two.

## Three sources, not one, because three real situations exist

**The built-in catalog** is the original pitch and still the core of the thing: 130-plus holidays, observances, and awareness months that ChromaCal already knows about, computed algorithmically so they're correct forever without anyone touching them again. This exists for the broadly-shared stuff, the things enough people would want that it makes sense to ship them rather than ask everyone to enter Easter's date themselves. Zero setup is the whole point here. You toggle categories on or off, not individual dates.

**Personal Events** is ChromaCal's own lightweight way of saying "I have one specific thing, and it's not going to be on anyone else's calendar, and I don't want to connect an entire external account just to tell you about it." A birthday, an anniversary, a one-off. Type a name, pick a date, pick colors. Lives entirely inside ChromaCal, nothing external involved, nothing to sync.

**Calendar Sync** exists for the opposite situation: someone who already keeps their actual life in a real calendar app, Google, CalDAV, whatever, and shouldn't have to duplicate-enter things into ChromaCal that already exist somewhere else. It reads from a connected calendar and lets colors get assigned to events by title. Read-only, deliberately. A color mapping is meaningless data outside ChromaCal, your calendar app has no use for knowing "Game Night" means red and green, so writing anything back would just be clutter for no real benefit. The calendar entry was never the point. What color the lights show is.

These aren't competing approaches to the same problem. They're three different real situations, "I want it to just work," "I have one specific thing," and "I already track this elsewhere," each solved the way that actually fits, not forced through one mechanism that's good at none of them.

## A separate axis: what happens once something fires

Everything above is about *what triggers* a color change. WLED support is a different axis entirely, *how the lights respond* once something has. A plain RGB bulb gets a color. A WLED-backed light can optionally run an actual effect, a chase, a twinkle, something built once in WLED's own app and selected by name. This isn't a fourth source competing with the other three, it's available to any of them. A built-in holiday, a Personal Event, a Calendar Sync match, any of them can point at a WLED preset if the light supports it. Source and behavior are independent questions.

## What this means when something new comes up

A new feature idea almost always belongs to one of these buckets, or reveals a genuine need for a new one. If it's "ChromaCal should already know about X without anyone asking," that's a catalog question. If it's "I want to tell ChromaCal about one specific thing of my own," that's Personal Events. If it's "I already have this somewhere else," that's Calendar Sync. If it's about how the lights actually look once triggered, rather than what triggers them, that's the WLED axis, not a new source at all.

The collision-handling work this same night is a good example of staying inside this frame rather than inventing a fourth thing: two real events from the existing sources happened to land on the same day. The fix is about resolving a conflict between sources that already exist, not about creating a new kind of event.

When something genuinely doesn't fit any of this, that's worth treating as a real, deliberate decision, not a quiet addition. The same way every other real fork tonight got an actual conversation instead of a silent pick.

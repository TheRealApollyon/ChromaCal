# ChromaCal: Generalized Same-Tier Collision Handling

Grew out of a real bug, not a hypothetical. Litha and Father's Day land on the same calendar day in 2026, and the existing priority logic silently picked one without ever surfacing that a second event existed at all.

## The real data this is grounded in

Computed across all 8 years the solstice/equinox table currently covers, 2024 through 2031, checking every pagan event against every other single-winner-tier event (holiday, vigil, sacred, not awareness, since those already coexist) using the actual date-resolution algorithms already in the app:

- **Litha vs Father's Day**: collides exactly once in the 8-year window, 2026 only. A genuine coincidence, not a pattern.
- **Samhain vs Halloween**: collides every single year, all 8, zero exceptions, because both are fixed to October 31st permanently. Not a coincidence, a structural certainty for as long as both categories are ever enabled together.

That split matters. A permanent, guaranteed collision and a one-in-eight-years coincidence are genuinely different problems and probably deserve genuinely different answers.

## What was actually broken

Every single-winner tier, sacred, vigil, holiday, used `.find()` against the full event list for the day, returning the first match in array order and stopping. No detection that a second candidate existed, no visibility, the losing event didn't just lose, it disappeared entirely, not shown anywhere, not even in the Upcoming list. That's the more immediate problem, independent of how a real resolution mechanism eventually works.

The Upcoming list had the same issue for a different reason: it deliberately stopped at the first match per future day to avoid a month-long awareness event repeating across 30 rows. Correct behavior for that case, but it accidentally also silenced a real same-day collision between two single-day events.

## The actual design, now implemented

**Detection first.** Each single-winner tier switches from `.find()` to `.filter()`, so the system knows when more than one candidate exists for the same day. The Upcoming list fix removes the early break for single-day events while keeping the multi-day repetition protection that was always correct.

**Two resolution paths, matched to the two real shapes of collision.**

For the rare, coincidental kind (Litha/Father's Day): Tonight's Pick is the right tool, just not currently reachable here. It's already built, already understood, already matches the "this is a today-specific decision" character of something that won't repeat next year. The fix is making it reachable from any same-tier collision via `resolveTierWinner()`.

For the permanent, structural kind (Samhain/Halloween): a saved preference keyed by event pair, set once in Settings, remembered going forward. The data structure exists in `CFG.collisionPreferences`. The Settings UI to actually set it does not exist yet, that's the one real open piece.

**Deliberately not touching the cross-tier hierarchy.** Sacred still always beats vigil still always beats holiday. Everything here is scoped to collisions within the same tier.

## What ships in v1.1.0

`resolveTierWinner(candidates, lightName)`, a real top-level function, not nested inside the scheduling loop. Resolution order: saved preference for the pair, Tonight's Pick if active, array order as explicit fallback. The Upcoming list now shows both colliding events on future days so you can actually see and pick.

## Still open

The Settings UI for permanent collision preferences. The Samhain/Halloween collision happens every year, October 31st, every year, permanently. Right now the default behavior (array order) picks Halloween. If you have Pagan & Wiccan enabled and want Samhain to win every year without using Tonight's Pick, that preference screen is what you'd need. Building it is well-defined work, just not done yet.

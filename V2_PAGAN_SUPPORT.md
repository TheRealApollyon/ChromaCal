# ChromaCal v2: Pagan/Wiccan Support

Picks up where the v1 beta left off. The four fixed cross-quarter days, Imbolc, Beltane, Lughnasadh, Samhain, and the sacred-night toggle for the solstices and equinoxes both carry over unchanged, those were already correct, dependency-free designs. What changes in v2 is how the four solstices and equinoxes get their dates.

## Why this needed revisiting

The v1 beta used a hardcoded lookup table, correct, verified against Wikipedia and the US Naval Observatory, but only through 2031, with an acknowledged need to extend it manually at some point. That was the right call for v1, a single self-contained HTML file with no room for a real dependency. It's not the right call for v2, a real Python Integration with no such constraint.

Two real alternatives got weighed honestly before landing here. A third-party Home Assistant integration exists for exactly this (Solstice Season, by moerk-o), genuinely well-built, actively maintained, but still an external dependency on a small, single-maintainer project. And `astral`, the mature library Home Assistant's own `sun` integration already trusts, turns out not to actually calculate solstices or equinoxes at all, just sunrise, sunset, and related sun-position data, so it wasn't a fit despite being the obvious first guess.

What this settles on instead: implement the real calculation directly. Specifically, Jean Meeus's published periodic-term method, the same general mathematical lineage as the Meeus/Jones/Butcher Easter algorithm ChromaCal already trusts and uses in v1 right now. No table to extend, no third-party package to depend on, permanently correct for any year.

## The actual implementation

`solstice_calc.py`, included alongside this document. A mean-position polynomial per event (March equinox, June solstice, September equinox, December solstice), corrected by a 24-term periodic series accounting for the real perturbations in Earth's position, then converted from Julian Day to a UTC datetime. Standard, published astronomical method, not something invented for this project.

## Verified, not just trusted

The formula's reputation is well-established, but that's not the same as checking it, so it got checked properly:

- **Calendar-day accuracy**: tested against the full 16-year reference table already built and verified earlier this project (2016-2031, cross-validated against Wikipedia and the USNO). 64 out of 64 checks passed exactly.
- **Time-of-day precision**: tested against an independent, separately-sourced minute-precision reference table (2016-2027, 48 events). Zero calendar-day mismatches, worst-case deviation of 1.8 minutes from the published authoritative time, consistent with this formula's well-documented precision characteristics.
- **Generalization beyond the original table**: confirmed for years well outside 2016-2031, including 1900 through 2100, producing correctly-ordered, plausible dates throughout with no special-casing anywhere in the code.

Worth being honest about the one real limit rather than overstating this as flawless across all of time: precision is very slightly reduced toward the far edges of that broader range, a known, documented characteristic of this formula, and practically irrelevant to anything ChromaCal would ever actually schedule against.

## How this plugs into the rest of the event system

`pagan_solstice_dates(year)` returns the four events in the same simple `(month, day)` shape every other event type in ChromaCal already uses. The scheduling engine doesn't need to know or care that these four dates come from real calculation instead of a table, it gets exactly the same shape back either way. Ostara, Litha, Mabon, and Yule slot into the existing event list precisely the way the v1 beta already designed, same names, same category, same sacred-night toggle behavior, only the source of the date itself has changed.

## What this means for the v1 beta branch

`pagan-wiccan-beta` still has real, independent value as a record of the original design work, the category, the toggle, the four fixed days, the original verified table. Nothing here invalidates that work, it just gives v2 a permanent answer to the one piece that was always going to need revisiting eventually.

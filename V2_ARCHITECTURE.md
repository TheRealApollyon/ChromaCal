# ChromaCal v2: Architecture Scoping

This document exists to turn "split it into an Integration and a card" into something concrete enough to actually estimate and build against, rather than a single line in a roadmap. Nothing here is final. The point is to surface the real shape of the work and the real decisions that need making before any code gets written, the same way the Pagan/Wiccan section of ROADMAP.md flagged an open question instead of quietly picking an answer.

## Why this exists

v1 works, but it has one structural limitation baked into its design: ChromaCal is a static HTML file running entirely in a browser tab, and the companion Blueprint only receives fresh values while that tab is open and actively publishing. Close the tab, and the schedule stops advancing past whatever it last published. The README already documents this honestly rather than hiding it, and recommends keeping a spare device or kiosk display running as the workaround.

v2's actual goal is to remove the need for that workaround entirely, by moving the scheduling brain into Home Assistant itself, where it runs server-side regardless of whether any browser is open.

## What the codebase actually looks like right now

Worth grounding this in real numbers rather than a general sense of "it's a big file." The current `dist/chromacal.html` is 5,508 lines and 143 top-level functions. Breaking those down by what they actually do:

- **~17 functions are pure scheduling and calendar logic:** `getEasterDate`, `buildFloatingDates`, `getEnabledHolidays`, `getNightSegments`, `getCurrentSegment`, `getTonightSchedule`, `applyIntensity`, color math helpers, and similar. This is the actual "brain": given a date and a light's config, what should be on right now. No DOM, no HA calls, just computation. This is the part that's genuinely portable to Python with a fairly direct translation.

- **~22 functions are HA I/O:** `fireScheduledCommand`, `syncBridgeHelper`, `haFetch`, `lightOn`/`lightOff`, the Quick Controls actions, Emergency Mode. Right now these go through REST calls authenticated with a long-lived token, because a browser tab has no other way to reach Home Assistant. Inside a real Integration, this layer gets *simpler*, not just translated, since the integration runs inside HA and can call services directly through the internal service-call API instead of authenticating over HTTP at all.

- **~3 functions are config/persistence:** loading and saving settings, currently to browser localStorage. This becomes a `ConfigEntry` plus an options flow.

- **The remaining ~101 functions, roughly 70% of the total, are DOM rendering, modal handling, form wiring, and House View's 2D/3D viewer.** This is the real headline number for scoping purposes: most of this codebase isn't scheduling logic at all, it's UI. None of it ports to Python, because Python isn't running in a browser. It has to be substantially rebuilt as a Lovelace card, in JavaScript, using a completely different rendering approach (LitElement Web Components, not direct DOM manipulation).

So this isn't "port 5,000 lines to Python." It's closer to "extract roughly 1,500 lines of real logic into Python, and rebuild roughly 4,000 lines of UI as a proper card." Different shape of effort than the line count alone suggests, and useful to know going in.

## Target architecture

Two separate pieces, matching current Home Assistant convention for this kind of split:

### 1. The Integration (`custom_components/chromacal/`)

Verified against current (2026.4+) HA custom integration scaffolding. Standard shape:

```
custom_components/chromacal/
├── __init__.py          # setup and entry point
├── config_flow.py       # replaces the in-app "enter your HA URL and token" wizard
├── const.py
├── manifest.json
├── diagnostics.py       # structured troubleshooting data
├── repairs.py           # surfaces fixable issues to the user in HA's UI
├── services.yaml        # service definitions
├── coordinator/
│   ├── __init__.py
│   ├── base.py          # the DataUpdateCoordinator — replaces the 30s setInterval loop
│   └── scheduling.py     # the ported brain: getEnabledHolidays, getNightSegments, etc.
└── entity/
    └── ...               # the entities described below
```

**The 30-second `pollTimer = setInterval(update, 30000)` loop becomes a `DataUpdateCoordinator`.** This is the same pattern HA already uses for hundreds of integrations and is genuinely a good fit, it's built exactly for "periodically recompute state and notify listeners," which is what ChromaCal's loop already does, just inside a browser tab instead of inside HA's own event loop.

**Config flow replaces the token-and-URL setup screen entirely**, and removes a real limitation along with it: right now ChromaCal needs a long-lived access token because it's an external page talking to HA over HTTP. An Integration runs *inside* HA's process, with direct access to the `hass` object. No token. No URL. No auth surface to leak via `/local/` at all, which closes the unauthenticated-static-file concern the README currently has to document as a known characteristic.

**What entities would this expose?** Worth deciding deliberately rather than guessing, but a reasonable starting shape: a sensor entity per configured light showing the current event/phase (replacing the `input_text.chromacal_*` bridge helper), and the existing Quick Controls (Test Tonight's Color, Force White, Emergency Mode, 21 Gun Salute, skip/pick actions) become real HA *services*, callable from automations, scripts, or voice assistants, not just UI buttons. That's a genuine capability upgrade over v1, not just a rebuild, since right now none of that is automatable from the rest of someone's HA setup.

### 2. The Lovelace Card (separate HACS frontend repo, or a `www/` bundle within this one)

Verified against current HA frontend custom-card conventions: a LitElement-based Web Component implementing `setConfig()` and a `hass` property setter, registered via `window.customCards`, distributed through HACS as a "Plugin" rather than the current "dashboard panel" style `content_in_root: false` distribution ChromaCal uses today.

This is where the ~101 UI-layer functions get rebuilt, Active State, Tonight's Schedule, Upcoming Events with its skip/pick/customize-color buttons, Settings, House View. The card becomes a thin display-and-control layer reading entity state and calling services, not the brain. That's the real architectural shift: today the brain and the UI are the same file; in v2 they're decoupled, and the brain keeps running whether or not the card is ever opened.

## What doesn't change at all

The actual holiday calendar, names, dates, colors, categories, is just data. It's portable regardless of language, copy-paste with light reformatting, not a rewrite. Same goes for the verified solstice/equinox table and the Easter algorithm, those are correct math, not browser-dependent code.

## Real open questions, not yet decided

- **Coexistence during transition.** Should v1 and v2 be able to run side by side for existing users, or is this a clean cutover once v2 reaches parity? Affects whether the Integration needs any migration tooling at all.
- **Where the Lovelace card lives.** Same repo as the Integration, or a genuinely separate HACS entry the way many HA add-ons split "integration" and "card" repos? Affects discoverability and how updates get versioned against each other.
- **Phase 1 scope.** The single highest-value, lowest-risk slice is probably just the coordinator plus entity/service exposure, with *no* card at all yet, since that alone solves the actual headless problem this whole effort exists for. A user could control everything through HA's native UI and automations in the meantime. Worth confirming that's actually the right Phase 1 rather than trying to ship coordinator and card together.
- **HACS quality scale.** HA's integration quality tiers (Bronze/Silver/Gold/Platinum) bring real requirements, strict typing, diagnostics, reconfigure flow, stale-device handling. Worth deciding up front how much of that to target for v1 of the integration versus treating it as later polish.

## What this document is not

It's not a timeline. None of this has been built yet, and estimating effort on unbuilt server-side Python work, in an ecosystem with real conventions to learn and follow correctly, isn't something to guess at just to have a number. Once Phase 1 scope is actually agreed on from the open questions above, that piece specifically is small enough to scope honestly.

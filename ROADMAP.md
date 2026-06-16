# ChromaCal v2 Roadmap

*Consolidated from the "ChromaCal integration question" conversation and the June 15-16 debugging session. This is a planning document, not a build log, nothing here is built yet.*

---

## Where v1 stands right now

Live, working, and not at risk from anything in this document. Standalone `chromacal.html` in HA's `/www/` folder, REST API calls authenticated with a long-lived token, a companion Blueprint (`chromacal_sync.yaml`) watching a pub/sub `input_text` bridge entity for resilience when the tab closes. The `color_temp_kelvin` breaking change from HA 2026.3 is fixed across every code path. This stays exactly as-is and keeps running while v2 gets designed and built. Nothing below blocks or risks it.

---

## The core decision: two decoupled pieces, not one

This morning's conversation left an open question about converting the dashboard into a proper `custom:chromacal-card` Lovelace element instead of an iframe page. Tonight's debugging surfaced a second, separate problem: the entire scheduling brain currently lives in browser JavaScript, which means nothing runs unless a tab stays open. These turned out to be two different problems with two different fixes, not one.

**Backend** (`custom_components/chromacal/`): a real HACS Integration, written in Python, loaded directly into Home Assistant's own process. This is where the scheduling brain moves to, the 130+ holiday calendar, the floating-date math, split-night logic, skip system, color style transforms. It runs as long as HA itself runs, with zero dependency on any browser or tab.

**Frontend** (`custom:chromacal-card`): a true Lovelace custom card using HA's native `hass` object, replacing the current standalone page. Becomes a control and configuration surface that reads state from the backend's entities, not the thing keeping the schedule alive.

**Why Integration and not Add-on:** Add-ons require Home Assistant's Supervisor, which only exists on Home Assistant OS or Supervised installs. Pi4-Services runs HA straight through Docker Compose, the Container install method, which has no Supervisor at all and never will without changing how HA itself is installed. An Add-on built for ChromaCal would be a dead end on your own setup and on every other Docker Compose user's setup too, a meaningfully sized chunk of the exact homelab audience this project is aimed at. Adaptive Lighting, the closest comparable project in the entire ecosystem, proves the Integration path alone is enough for serious adoption: HACS install, one config entry, Add Integration wizard, done, no Supervisor required anywhere in that flow.

**The token problem solves itself for free.** A custom_component's code runs inside HA's own Python process. It calls `hass.services.async_call("light", "turn_on", {...})` directly, in-process, no HTTP round trip, no token of any kind. This was something this morning's conversation hadn't resolved yet, full token elimination, and it turns out to not even need Ingress or Supervisor machinery to get there.

---

## Decided

**Both panel and card, one shared component.** A Lovelace custom element can serve as a compact card embedded in a normal dashboard and as full-screen panel content, the same underlying code, two entry points. Build a compact summary view, today's event, status dot, quick toggles, for the card form, with a button that opens the full experience as a panel. Bubble Card's popup pattern is direct community precedent for exactly this shape.

**Theme-native by default, fully brandable on request.** The card reads Home Assistant's own theme variables out of the box, so it automatically matches whatever theme each person has installed and looks native sitting next to Mushroom-style cards rather than clashing. The current rainbow CHROMACAL identity, Twilight, Sci-Fi, Mono, becomes an opt-in style choice layered on top, not the forced default. Built to play nicely with card-mod so anyone can go further without needing the maintainer to build a bespoke theming system. Gets the adoption benefit of looking native and the full customization benefit at the same time, not a tradeoff between them.

**Skip state is always reversible, no exceptions.** Already true in v1, the permanent skip toggle restores on a second click same as it sets on the first. This is a hard rule for v2 too: nothing in the skip system is ever a one-way action, regardless of what it's labeled. Moving skips to real HA switch entities in Phase 3 makes this structurally guaranteed for free, a switch entity always has both an on and an off state by definition.

**What entities does the backend actually expose?** An entity is Home Assistant's unit of tracked state, the same kind of thing as `light.shane_office_dongle_outside_lights_zha`. Right now ChromaCal's only footprint inside HA's actual state machine is the one `input_text` bridge helper, everything else lives invisibly in the browser. The backend integration creates real entities the same way ZHA creates light entities: a sensor per configured light showing the current event and phase, switch entities for permanent and tonight-only skip per event, button entities for one-shot actions like the 21 Gun Salute or Force White. Once these exist, any dashboard, automation, or voice command can read and control ChromaCal's state without its own UI ever being open. Exact entity list gets finalized once Phase 2 starts.

---

## Lessons from tonight worth carrying into the build

The `color_temp_kelvin` bug existed because the parameter name was a hand-typed string in five separate places, with no single source of truth. HA's own Python light component exposes constants for exactly this (`ATTR_COLOR_TEMP_KELVIN` and friends), which a real integration should use instead of string literals. When HA deprecates or renames something again, code using HA's own constants tends to get caught by static analysis or simply continues working through the compatibility shims HA provides internally, instead of silently 400ing in production until someone notices.

The skip-system date-keying bug taught a more general lesson, isolate state by the dimension that actually varies (calendar date, in that case) rather than relying on cleanup functions running at the right moment. Worth keeping in mind in Python too.

The kiosk watchdog failure tonight was caused by a script with zero error handling around its one critical operation, a single uncaught exception silently killed the entire loop with no trace. Anything in the v2 backend that runs as a persistent background task (which is the whole point of moving to an Integration) needs the same discipline, wrap the recurring work, log failures, never let one bad iteration take down the whole coordinator.

---

## How this gets built, stated plainly

This was a major topic in this morning's conversation and deserves to live somewhere permanent, not just in chat history. The code in this project has been written with extensive AI assistance, and that's going to remain true through v2 as well. Pretending otherwise would be dishonest, and it's not how this gets represented to the community when it ships.

What stays human, every time: the feature set and what ChromaCal actually does, every architectural decision including the ones in this document, all testing against real hardware, real Zigbee mesh behavior, real bugs found by actually using it, and final judgment on what ships and what doesn't. AI writes a large share of the actual implementation, helps debug issues found during real testing, and helps research how the wider community handles comparable problems, the Adaptive Lighting comparison that shaped the backend architecture decision above came directly out of that.

This gets stated the same way in the README, not buried, not hedged. People can weigh the project accordingly, that's their call to make, and they should get to make it with the real picture.

---

**Phase 1, skeleton.** Minimal `custom_components/chromacal/` that HACS can install and HA can load: `manifest.json`, `__init__.py`, `config_flow.py` with a basic Add Integration wizard, one placeholder sensor entity. No scheduling logic yet. Goal is purely proving the packaging and loading mechanics work end to end before porting anything real into it.

**Phase 2, port the brain.** Move the holiday calendar (Easter, Islamic estimates, nth-weekday US holidays, the rest), split-night logic, and color style transforms from JavaScript into Python. Wire it to a `DataUpdateCoordinator` that recomputes the current phase on an interval and fires `light.turn_on`/`light.turn_off` directly, no REST, no token.

**Phase 3, skip system and overrides as real entities.** Switches and services exposed through HA's own state machine, so skip toggles work from any dashboard, any voice assistant, any automation, not just from inside ChromaCal's own UI.

**Phase 4, the Lovelace card.** Build `custom:chromacal-card` against the entities Phase 2 and 3 created. This is also where the full-panel-vs-card and visual-identity decisions actually get implemented, once they're made.

**Phase 5, packaging for real distribution.** HACS validation requirements, manifest correctness, translations/strings.json for the config flow, possibly a brands repo submission for a proper icon.

**Phase 6, release.** The Reddit announcement template already sitting in the v1 test checklist gets dusted off and updated for the real architecture.

---

*This file is meant to be updated as decisions get made and phases complete, not treated as fixed in stone.*

# ChromaCal v2: WLED Support

First real feature slice of the v2 architecture, chosen deliberately as the lowest-risk place to start.

## Foundation

Home Assistant already ships a mature, built-in WLED integration. It auto-discovers devices on the network and creates a full set of entities per segment, including a `light` entity with color and effect control, plus dedicated selector entities for presets, playlists, and color palettes. Each segment shows up as its own separate light entity, and all of WLED's built-in effects are selectable from a dropdown.

That matters for scope: plain RGB control of a WLED segment already works today, in v1, with zero WLED-specific code, since a segment is just a normal `light.*` entity taking `rgb_color`. What's actually new here is everything that makes WLED specifically interesting, its effects and presets.

## Detection

This needed to be precise, not just "checks the device registry," since that's not actually a mechanism, it's a description of one. The real, concrete steps, using standard Home Assistant helpers, nothing custom or fragile:

1. Look the light entity up in the entity registry. Every registered entity carries a `config_entry_id`, the ID of whichever integration's setup created it.
2. Resolve that config entry and check its `domain`. If it's literally `"wled"`, this light came from WLED. If not, treat it as a normal light, exactly like today.
3. The same registry entry also carries a `device_id`, the physical device this entity belongs to. A single WLED controller can expose several entities, the segment's light entity, plus separate selector entities for presets, playlists, and palettes, all sharing that one device_id.
4. Pull every entity that shares that device_id using Home Assistant's own `entity_registry.async_entries_for_device()` helper, the same mechanism the `device_entities()` template function uses under the hood. Filter that list for the one in the `select.` domain that represents presets.

A real wrinkle worth specifying precisely rather than leaving implicit: WLED's integration translates entity names into whatever language Home Assistant is running in, so matching against the visible entity_id or friendly name isn't locale-safe, "preset" won't appear in the string on a non-English install. What does stay stable across languages is the `unique_id` suffix each select entity carries internally, `_preset`, `_playlist`, `_live_override`. That's the correct thing to match against, confirmed directly from a real WLED-integration bug report showing this exact suffix structure held steady even when the surrounding entity_id and friendly name were fully localized into Slovak.

That's the whole detection chain, and every step is a documented, standard HA helper, not a workaround. Nothing about this is WLED-specific plumbing ChromaCal has to invent and maintain, it's the normal way any Home Assistant integration discovers sibling entities on the same device.

When a light gets added in ChromaCal-v2, this check runs automatically and the light quietly gets WLED-aware behavior if it qualifies. No manual toggle, no separate setup step.

## Per-event preset assignment

Extends the color-customization modal already shipped in v1 tonight. For a WLED-detected light specifically, the modal swaps the color swatch picker for a dropdown listing that device's actual current presets, sourced from the preset `select` entity found above. The list is read fresh every time the modal opens, never cached on ChromaCal's side.

Worth being honest about what "fresh" actually guarantees, though. There's a real, currently open bug in Home Assistant's own WLED integration: it loads the preset list once, when it starts up, and doesn't refresh it afterward, so a preset just added in WLED's own app won't show up in Home Assistant until that integration gets manually reloaded. ChromaCal asking for the current state every time genuinely has no caching of its own, but that's not the same guarantee as reflecting a change made seconds ago in WLED, since that gap sits one layer up, in HA's integration, not somewhere ChromaCal can route around.

## Fallback behavior

If a WLED light doesn't have a preset assigned for a given event, it just uses that event's normal color array, identical to any other light. Nothing goes dark, nothing errors, nothing requires special-casing elsewhere in the app.

## Firing mechanism

When a preset is assigned, ChromaCal calls `select.select_option` against the device's preset-select entity, not `light.turn_on`. Worth being precise about this from the start: real-world Home Assistant community threads show people repeatedly tripped up trying to set a preset through `light.turn_on`'s data fields directly, which doesn't reliably work. Using the correct service from day one avoids a documented, common mistake.

## A real, honest trade-off

`select.select_option` has no `transition` parameter, unlike `light.turn_on`. So a WLED preset switch will snap rather than fade. Any smoothness depends entirely on WLED's own device-side transition-time setting, not anything ChromaCal controls per event. Plain-color lights keep their full fade-in control exactly as they have it today; WLED preset lights trade that control for genuinely richer effects. Worth stating plainly in user-facing documentation rather than letting someone discover it as a surprise.

## Turning off

Ordinary `light.turn_off` works regardless of whatever preset was last active on a segment. No WLED-specific handling needed for the end of the night.

## Preset creation, two paths, both real

ChromaCal does not build presets live, on the fly, every time an event fires. That was considered and deliberately rejected, it would mean ChromaCal owning a fragile, constantly-exercised code path duplicating WLED's own effects engine, exercised every single night rather than occasionally.

What's actually worth building is a one-time, opt-in convenience, not a runtime dependency:

- **Capture what's currently showing.** Dial in the exact look in WLED's own app, then a ChromaCal action calls WLED's native `psave` command to capture whatever's currently live on the device into a named preset. Requires no pre-designed content from ChromaCal at all, and sidesteps the segment-portability and effect-version concerns below almost entirely, since the person tuning it already has it working on their own real hardware.
- **Pick from a curated starter pack.** ChromaCal ships a small number of pre-designed looks, Christmas Twinkle, Halloween Spooky, a Police/Emergency flash, installable with one tap via the same `psave` mechanism. Real value, but genuinely needs actual WLED hardware to design and test against first. Not something to ship sight-unseen. Deferred until that hardware exists.

Both are worth building eventually. "Capture what's showing" is the practical near-term target.

## Known wrinkles, worth having on record

- **Segment geometry isn't portable.** A preset built for one physical strip layout doesn't necessarily translate cleanly to a different segment configuration. The WLED community has real, documented interest in "universal" presets designed to work across different setups, worth borrowing that approach whenever the curated starter pack gets built.
- **Community validation is real, not assumed.** Calendar-triggered WLED preset switching is something people already hand-build with raw Home Assistant automations and Node-RED flows, often with real friction, confused threads, broken templates, even official HA documentation recommending manual workarounds for picking presets cleanly from a basic light card. A polished, purpose-built version of this is solving a problem people already have, not inventing one.

## Open, not yet decided

A new category of trigger came up alongside this conversation, worth recording even though it's not WLED-specific: live sports score changes (via the existing Team Tracker integration) are attribute-level changes on an indeterminate timeline, not date-anchored the way every other ChromaCal event currently is. That's a genuinely different trigger shape than anything scoped so far, and deliberately set aside for later rather than folded in here.

# ChromaCal v2 — HACS Integration Migration

## What this project is

ChromaCal is a Home Assistant holiday/awareness-lighting scheduler: a 130+ event
calendar (US/CA/UK/AU/EU/APAC/LATAM + global floating observances + Pagan/Wiccan
sabbats) that drives Zigbee lights through sunset warm-up, color windows, warm
white curfew, and lights-off, with collision handling when two events land on
the same night.

**v1** is a single ~4,500-line `chromacal.html` file living in HA's `/www/`
folder, deployed at `pi@<ha-host>:/mnt/data/homeassistant/www/chromacal.html`
(SSH port 16752). It's Repo: `github.com/TheRealApollyon/chromacal`. Local
working copy: `C:\chromacal-release`. Current version: v1.1.0.

**This session's job is v2**: porting the scheduling brain out of browser
JavaScript into a real Python HACS Integration, so it runs inside Home
Assistant's own process instead of depending on a browser tab staying open.

Read the existing `chromacal.html` in this repo before writing anything — it's
the authoritative source for every rule below (holiday calendar data, collision
logic, bridge helper, auto-fire scheduling). Don't reinvent logic that already
works; port it faithfully, then improve the parts that were only ever
workarounds for living in a browser tab.

## The problem being solved

Two real, separate problems, with one architecture that fixes both:

1. **Tab dependency.** The entire scheduling engine — `update()`, the auto-fire
   logic, the holiday calendar math — only runs while a browser tab has
   `chromacal.html` open. Close the tab, nothing fires. A JS error anywhere in
   that loop (we've hit this twice now — see "Known failure pattern" below)
   silently kills the whole engine with no server-side fallback.
2. **Token security.** v1 authenticates to HA's REST API using a long-lived
   access token pasted into the page. This is a real risk once remote access
   (Nabu Casa) is involved, since the token then sits in an internet-reachable
   static file.

## Architecture — already decided, do not relitigate

**Two decoupled pieces:**

- **Backend**: `custom_components/chromacal/` — a real HACS Integration,
  written in Python, running inside HA's own process. This is where the
  scheduling brain lives: the holiday calendar, floating-date math, split-night
  segment logic, collision resolution (`resolveTierWinner` equivalent), skip
  system, color/style transforms. Runs continuously as long as HA runs — zero
  dependency on any browser or tab.
- **Frontend**: `custom:chromacal-card` — a Lovelace custom element using HA's
  native `hass` object. Reads state from backend entities; does not itself
  hold any scheduling logic or auth token.

**Integration, not Add-on.** Pi4-Services runs HA via Docker Compose (Container
install method) — there is no Supervisor, so Add-ons are a dead end here and
for a meaningful share of the Docker Compose HA audience generally. Adaptive
Lighting is the existing proof this Integration-only path is enough for real
adoption: HACS install → Add Integration wizard → done, no Supervisor anywhere
in that flow.

**Token problem solves itself for free.** A `custom_component` runs inside HA's
own Python process. It calls `hass.services.async_call("light", "turn_on", {...})`
directly, in-process — no HTTP round trip, no token of any kind, anywhere.

**Both panel and card, one shared component.** A single Lovelace custom element
can serve as a compact embedded card AND as full-screen panel content — same
underlying code, two entry points (Bubble Card's popup pattern is direct
precedent for this shape). **Build the full panel first this session** — it's
the direct replacement for what exists today and is what actually kills the tab
dependency. The compact card view comes after, reusing the same component.

**Theme-native by default, fully brandable on request.** The card reads Home
Assistant's own theme CSS variables out of the box, so it automatically matches
whatever theme the user already has installed (sits naturally next to Mushroom
cards instead of clashing). The current ChromaCal identity — rainbow wordmark,
Twilight/Sci-Fi/Mono themes — becomes an **opt-in style preset layered on top**,
not the forced default. ChromaCal's existing CSS custom-property theme system
(`--bg`, `--s1`, `--cyan`, etc.) is the right foundation for this — it's a
remapping exercise, not a rebuild. Build it to play nicely with card-mod too.

**Entities the backend exposes** (finalize exact naming during Phase 2, but the
shape is decided):
- A `sensor` per configured light showing current event name + phase
- `switch` entities for permanent-skip and tonight-only-skip, per event
- `button` entities for one-shot actions: 21 Gun Salute, Force White, Color
  Override, Emergency Mode, Catch Up/Sync

**Skip state is always reversible — hard rule, no exceptions.** Nothing in the
skip system is ever a one-way action regardless of what it's labeled — a
"permanent" skip toggle must restore on a second click, same as it sets on the
first. Modeling skips as real `switch` entities makes this structurally
guaranteed for free (a switch always has both an on and off state).

## AI transparency — a permanent project value, not a footnote

This codebase has been built with extensive AI assistance, and that continues
to be true through v2. This gets stated plainly in the README and code
comments — not hidden, not hedged, not spun as "look what I built" when that
isn't the full picture. The person's actual role: designing the solution,
making the architectural calls, troubleshooting against real hardware,
iterating on what the AI produced. That framing is accurate and should be
preserved verbatim in any docs this session touches or writes.

## Known failure pattern — watch for this specifically

v1 has broken from the *same category* of bug twice: a variable declared
inside one `{ }` block gets referenced from a sibling block that already
closed, so it's out of scope. First occurrence: `nowHours` declared but `nowH`
referenced in the Verify-Off check. Second: `desiredKey`/`lightKey` declared
inside the auto-fire `if` block, referenced later in the Brightness
Verification block after that scope had already closed. Both times the bug
silently took down the whole engine (caught by a `catch(e)` that just flips
the UI to OFFLINE) rather than crashing loudly.

When porting to Python: Python doesn't have JS's block-scoping quirks, but the
underlying mistake — a new feature block written on the assumption that it can
see a variable from a sibling block above it — is a general risk any time
logic gets appended incrementally. Write this scheduling logic with clear
function boundaries and explicit parameters/return values rather than shared
mutable state across long functions, and add basic unit tests around the
schedule-resolution functions (segment selection, collision resolution,
fire-key computation) so a similar silent failure gets caught by a test
instead of by the OFFLINE badge in production.

## Deferred design decisions — resolved in Phase 8

**Per-light stable identity, not just `entity`.** RESOLVED in Phase 8. Lights
are now Config Subentries (`ConfigSubentryFlow`, one per light), each getting
an HA-generated stable `subentry_id` (a ULID) that `sensor.py`/`button.py` key
`unique_id` on instead of the light's `entity` string. `async_migrate_entry`
in `__init__.py` moves any pre-Phase-8 install's `entry.data["lights"]` list
into real subentries and repoints existing sensor/button entities' `unique_id`
(via `entity_registry.async_update_entity(new_unique_id=..., config_subentry_id=...)`)
without touching their `entity_id` — closing the exact orphaned-sensor gap
from the Phase 5a incident described below. Proven both by
`tests/components/chromacal/test_migration.py` (seeds the old shape, asserts
survival) and by live verification against a genuinely pre-Phase-8 entry in a
disposable container.

Original problem, kept for context: `sensor.py`'s schedule sensor used to
derive its `unique_id` directly from a light's `entity` string
(`f"{entry_id}_{light_entity}_schedule"`). That's harmless while `entity` is
write-once, but the moment a user could repoint an existing light at a
different HA entity, this bit every time: to HA's registry, `unique_id` *is*
identity, so changing the string that feeds it creates a brand-new entity and
silently orphans the old one (`unavailable`, `restored: true`, forever, until
someone notices and removes it by hand). Hit exactly this in Phase 5a from a
manual light-entity swap in config entry data (`switch.decorative_lights` ->
`light.bed_light`); cleaned the orphan up via a direct entity-registry edit
at the time, but that was cleanup, not a fix.

## Current branch state

- `main` — v1.1.0, stable, keep running untouched during this migration
- Four v2 scoping branches exist: `v2-ha-integration` (this work),
  `v2-wled-support`, `v2-pagan-support`, `v2-calendar-sync`
- Work this migration on `v2-ha-integration`

## Testing safety — read before touching the real Pi

There is no separate dev/staging Home Assistant instance in this setup — the
only HA that exists is production, on `pi@<ha-host>`, controlling real
lights in a real house. This matters more here than it did for v1: a bug in
`chromacal.html` just crashes a browser tab. A bug in a `custom_component`
crashes inside HA's own Python process — it can take down Home Assistant
entirely, not just ChromaCal.

**Do not load this integration into the production HA instance until it has
been verified clean in a disposable instance first.** Spin up a second,
throwaway HA container (same image/version as production, no real devices
attached) purely for loading and iterating on the integration. Confirm the
integration loads without error, the config flow completes, and the entities
appear correctly there before it ever touches the real Pi. Once it's stable
there, move to the real instance — and even then, keep v1 (`chromacal.html`)
running untouched in parallel as a fallback until v2 has proven itself over a
few real nights of scheduling.

## Browser tool gotcha — stale preview session breaks screenshots, not DOM checks

Symptom: `mcp__Claude_Browser__computer` screenshot/zoom calls time out with
"the Browser pane is not displayed, so the page is not compositing frames",
while `javascript_tool`/`read_page`/`get_page_text` against the same tab keep
working fine. This happened across a multi-day gap in Phase 7 — the
underlying browser process's on-screen compositor had gone stale (window no
longer actively rendering) while the CDP/JS channel stayed alive, since JS
execution doesn't require actual screen compositing but a real screenshot
does. New tabs (`tabs_create`) inside the *same* stale preview session did
not fix it. `preview_stop` on the stale `serverId` followed by a fresh
`preview_start` did.

If DOM/computed-style checks succeed but screenshots keep failing with that
exact message, restart the whole preview session first, not just the tab —
and don't treat DOM introspection as a substitute for an actual visual check
in the meantime; they catch different classes of bug (see the truncation/
dead-space fixes in Phase 7, both invisible to DOM math until a real
screenshot showed them).

## Disposable-container gotcha — "hung" HA may just be waiting on onboarding

Symptom: a fresh disposable HA container logs its earliest startup lines
(the "custom integration ... not tested" loader warning, maybe a `rich`
SyntaxWarning) and then goes completely idle -- 0% CPU, no further log
output, no errors, seemingly forever. Every diagnostic points to a real
hang: the process is alive but blocked in `do_epoll_wait` with nothing
scheduled, disk/memory/DNS all check out fine, and it reproduces even on a
completely bare `home-assistant` image with zero bind mounts or
customization.

It isn't a hang. A never-onboarded HA instance stops at onboarding's
location-picker step, which needs a human to actually click/set a
location in the browser -- there's no further log output because HA is
correctly waiting on user input, not stuck. Confirmed in Phase 7 after a
long, thorough (and ultimately unnecessary) investigation that ruled out
Docker Desktop, host resources, and the container's own code before the
real cause turned up: nobody had completed onboarding on that instance.

Check this FIRST, before concluding a Docker/host-level fault: open the
container's URL in a browser and see whether it's actually sitting on the
onboarding flow. Only chase infrastructure theories once onboarding is
confirmed complete and the hang persists.

## Windows Git Bash gotcha — `docker run -v`/`docker exec` paths get silently mangled

Symptom: a container built with `docker run -v "/c/path/on/host:/config" ...`
comes up, HTTP responds, onboarding even works — but a custom component
mounted via a second `-v` never actually appears inside the container
(`ls /config/custom_components/chromacal` -> "No such file or directory"),
and `docker inspect --format '{{.Mounts}}'` shows garbled source/destination
paths like `...;D -> \Git\config` instead of the real POSIX paths. Also seen
as `docker exec ... cat /config/x` failing with a path like
`D:/Git/config/x: can't find mount point` even though the same path works
fine via `docker exec ... sh -c 'cat /config/x'`.

Cause: Git Bash (MSYS2) auto-converts POSIX-looking arguments to Windows
paths before they ever reach `docker`, including inside `-v` flags and
`docker exec` command arguments — silently, with no warning. This corrupted
an entire container's custom-component mount for hours in Phase 8 before the
missing directory was noticed; the container looked healthy the whole time
(root `/config` mount happened to still work, so onboarding/config edits via
`docker exec ... cat/write /config/configuration.yaml` succeeded and masked
the problem).

Fix: prefix every `docker run`/`docker exec`/`docker inspect` invocation that
touches a `/`-style path with `MSYS_NO_PATHCONV=1`, and after creating any
container with bind mounts, immediately verify with
`docker inspect <name> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'`
that the paths look right — don't just trust that the container booted
cleanly.

## Sandbox gotcha — YAML `demo:` integration hangs boot here; config-entry Demo does not

Symptom: a disposable HA container's log stops dead right after "The legacy
device tracker platform demo.device_tracker is being set up" — 0% CPU,
no further output, no error, indefinitely. Reproduced identically across
multiple fresh containers in Phase 8, ruling out container-specific
corruption; a container with `light: platform: demo` also fails immediately
(that specific YAML platform form isn't supported in current HA — "does not
support platform setup").

This is specific to the **YAML** `demo:` integration's legacy
`device_tracker` platform setup in this sandboxed environment (likely a
blocking call with no working DNS/network here) — it is not a general HA
startup problem. The **config-entry-based** Demo integration (the one HA's
own onboarding flow adds automatically, or `Settings > Add Integration >
Demo` where supported) sets up the same 58-ish demo devices/entities without
touching that code path, and boots cleanly.

For live-verification containers that just need throwaway light entities to
attach ChromaCal lights to: prefer a `template:` light (fully virtual, zero
network dependency) or rely on the config-entry Demo integration. Avoid
`demo:` in `configuration.yaml`.

## Custom-component gotcha — `translations/en.json` needs literal text, not `[%key:...%]` refs

Symptom: a config/subentry flow's abort dialog (e.g. after a successful
reconfigure) shows the raw string `[%key:common::config_flow::abort::reconfigure_successful%]`
in the real HA UI instead of resolved text, even though `strings.json` and
`translations/en.json` both look correct and match the exact pattern real
core integrations use (`ollama`, `mqtt`, `anthropic`, etc. all reference
`abort.reconfigure_successful` the same way).

Cause: `[%key:...%]` is a *source-format* shorthand. For core HA
integrations, `script/translations` (part of HA's own build pipeline)
resolves every `[%key:%]` reference in `strings.json` into literal text before
it ships in `translations/<lang>.json`. Custom components never run that
pipeline — whatever is physically in `translations/en.json` is what the
frontend renders, unresolved references included. Phase 8 hit this after
copying `strings.json` to `translations/en.json` verbatim (`cp`), assuming
the two should always be byte-identical; that assumption is only safe for
keys that don't use `[%key:%]` shorthand.

Fix: `strings.json` may keep `[%key:...%]` references (it's the correct
source format, useful if this ever becomes a HACS-published integration that
runs through proper tooling), but `translations/en.json` must contain the
final literal resolved text for every string, looked up from HA's own
`homeassistant/strings.json` (`common.config_flow.abort.<key>`, etc.) if
unsure of the exact wording. Also note: HA caches parsed translations
in-process — a fix to the file needs a container restart (not just a
browser reload) before it's visible in the UI, which can make the fix look
like it didn't work if you only reload the page.

## Suggested first session shape

1. Read `chromacal.html` in full; inventory what needs porting (holiday
   calendar arrays, `getNightSegments`/`resolveTierWinner` logic, auto-fire
   state machine, bridge helper) before writing any Python.
2. Scaffold `custom_components/chromacal/` — `manifest.json`, `__init__.py`,
   `config_flow.py` for the setup wizard (region, categories, lights).
3. Stand up the disposable test HA container described above; confirm the
   scaffolded integration loads cleanly there before writing scheduling logic.
4. Port the scheduling brain to Python — this is what actually removes the
   tab dependency, before any frontend work starts. Test it against the
   disposable instance, not production.
5. Stand up the entities listed above so state is visible/controllable from
   any dashboard or automation, not just ChromaCal's own UI.
6. Only after the backend is verified stable in the disposable instance:
   build the Lovelace panel component, theme-native by default per the
   styling decision above, then move the whole thing to the real Pi.

# ChromaCal

**Automated holiday lighting for Home Assistant. One file. No YAML config. No integrations.**

ChromaCal is a single HTML dashboard that lives in your HA `/www/` folder. It knows about 130+ holidays, awareness months, and cultural observances across US, Canada, UK, Australia, EU, and globally, and automatically cycles your lights through the right colors every night, year after year, without maintenance.

> *"The whole world celebrates with light. Now you can too."*

---

## How this was built

The code in this repo was written with extensive AI assistance (Claude, Anthropic). Saying otherwise would be dishonest, so this isn't buried in a footnote.

What's actually mine: the entire feature set and how it behaves, every architectural decision (the holiday calendar scope, the skip system rules, the scheduling model, the Pub/Sub bridge that keeps lights running when the dashboard's closed), the visual design direction, and every bit of testing against my own real ZHA lights and Zigbee mesh. Bugs that AI-written code introduced got found by me actually using the thing, not by code review. What ships and what doesn't is my call.

What AI did: wrote the bulk of the actual JavaScript, YAML, and documentation implementing those decisions, helped debug issues I found through real testing, and helped research how the wider Home Assistant community handles comparable problems.

If that changes how you weigh this project, that's a completely fair call to make. I'd rather you make it with the real picture than a curated one.

---

## ✨ What it does

- **Zero maintenance** — Easter, Thanksgiving, Mardi Gras, Islamic dates, Jewish holidays, all computed algorithmically forever
- **130+ events** — Federal, Military, Cultural, Heritage, Pride, Awareness, Religious, Personal categories
- **Split-night scheduling** — Multiple June awareness months (Pride, Men's Health, Caribbean Heritage) automatically split the color window equally
- **Pub/Sub bridge** — Companion Blueprint keeps lights running server-side even when the browser is closed
- **Tonight's Schedule** — Full visual timeline with countdown, phase list, feature toggles
- **Quick Controls** — Test colors, Color Override, Force White (with Kelvin picker), Emergency Mode (US/EU/Amber/Red-White), 21 Gun Salute for military tribute events
- **Skip system** — Permanent skip (⊘) or Skip Tonight only (🌙, auto-resets at midnight), both always reversible
- **Tonight's Pick** — Force one event to own the full window (⭐)
- **Warm White** — Security lighting at a configurable Kelvin (2700K → 6500K) before lights-off
- **Fade-In control** — 30s to 10min crossfade when colors fire
- **5 themes** — Daylight, Twilight (Catppuccin Mocha), Sci-Fi, Mono, Custom

---

## 📦 Installation

### Method 1: HACS Custom Repository (Recommended)

1. Open Home Assistant and navigate to **HACS → Frontend**
2. Click the **three dots** in the top right → **Custom repositories**
3. Paste: `https://github.com/TheRealApollyon/ChromaCal`
4. Select **Plugin** as the category → **Add**
5. Click **Download** on the ChromaCal card that appears
6. Access at: `http://your-ha-ip:8123/local/chromacal.html`

### Method 2: Manual

Copy `dist/chromacal.html` to your HA `/config/www/` folder:

```bash
# Via SCP (adjust path/port)
scp -P 22 chromacal.html user@ha-host:/config/www/chromacal.html
```

Or use the HA File Editor / Studio Code Server.

Access at: `http://your-ha-ip:8123/local/chromacal.html`

---

### Import the Blueprint

Click the badge to import the automation engine directly into your Home Assistant:

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FTheRealApollyon%2FChromaCal%2Fmain%2Fblueprints%2Fautomation%2Fchromacal%2Fchromacal_sync.yaml)

*Manual fallback:* Copy `blueprints/automation/chromacal/chromacal_sync.yaml` to `/config/blueprints/automation/chromacal/` on your HA instance.

Requires HA 2025.4.0 or newer (uses `color_temp_kelvin`, since HA 2026.3 fully removed the older mireds-based `color_temp` parameter).

---

### First Launch

1. Open ChromaCal in your browser
2. Enter your HA URL and a Long-Lived Access Token (Profile → Security)
3. Add your light entity (auto-detects from HA)
4. Configure your schedule (start offset, warm white, fade-in duration)
5. Create an automation from the Blueprint: Settings → Automations → Create from Blueprint → ChromaCal Sync Engine

---

## ⚙️ Light Configuration

### Color Start Offset
How many minutes **after sunset** ChromaCal waits before firing colors. Set this to match when your existing warm-up automation finishes.

Example: If your "Sunset Fade In" starts 30 min before sunset and takes 45 min total, it finishes at sunset + 15 min. Set offset to **+15** for colors right after, or **+30** for a 15-min warm white buffer first.

### Color Fade-In
How long the crossfade takes when holiday colors first fire:
- **30 sec** — quick snap
- **1 min** — smooth (default)
- **5 min** — very gradual, barely perceptible
- **10 min** — ultra slow melt into color

Single Zigbee `transition` parameter — no additional commands needed.

### Warm White
Security lighting before lights-off. Configurable Kelvin:
- 🕯️ Candle (1800K) — very warm amber
- Warm (2700K) — classic incandescent
- Neutral (4000K) — clean white (default)
- Daylight (5000K) — bright
- ✨ Jesus Lights (6500K) — max white-blue intensity

---

## 🗓️ Calendar Coverage

**US:** Federal holidays, Military observances (POW/MIA, USMC Birthday, Armed Forces Day), cultural months, awareness months, pride events, religious observances

**International:** Canada, UK, Australia, EU, APAC, Latin America, global Islamic/Jewish/Hindu/Lunar floating calendar

**All floating dates computed algorithmically** — Easter (Meeus/Jones/Butcher), US nthWeekday holidays, Islamic calendar estimates, Jewish calendar. Verified correct 2024–2030.

---

## 🔗 The Bridge (Blueprint)

ChromaCal publishes its schedule to `input_text.chromacal_[lightname]` in HA's state machine every 30 seconds. The companion Blueprint watches this entity and fires physical light commands, so lights change color even when ChromaCal's browser tab is closed.

**Worth knowing:** the bridge only gets fresh values while ChromaCal's tab is open and active, since that's what's doing the publishing. If you need the schedule to run through a phase transition (color window into warm white into off) with the tab fully closed all evening, keep a tab open somewhere, a spare device or kiosk display works well. A fully headless backend that doesn't need a browser at all is the explicit goal of the next major version, see the roadmap.

**Hardened against HA restarts:** Uses `state_attr()` reads (not trigger context) and triggers on `homeassistant: start` and `automation_reloaded` events, so it recovers correctly after any interruption.

---

## 🚨 Emergency Mode

Alternating emergency lighting patterns using Zigbee-safe 3-second intervals:

- 🔴🔵 **Red/Blue (US)** — Police/Fire simulation
- 🔵 **Blue (EU)** — EU emergency standard with pulse
- 🟡 **Amber** — Roadway/construction
- 🔴⚪ **Red/White** — Fire truck pattern

Click again to cancel and resume the schedule.

---

## 🎖️ Military Tribute & Memorial Events

Personal events support dedicated types beyond birthdays: Military Tribute auto-loads official US Flag Code colors for honoring a veteran, Memorial uses warm candlelight tones for remembrance. Quick Controls also includes a 21 Gun Salute, three volleys of seven white flashes with a dimmed red glow between volleys, for nights that call for it.

---

## 🛠️ Compatibility

Works with **any HA `light.*` entity** that supports `rgb_color`:
- Zigbee via ZHA (Innr, IKEA, Sengled, etc.)
- Philips Hue (local API)
- LIFX
- Z-Wave color bulbs
- ESPHome RGBW
- Tuya / Local Tuya
- Shelly RGBW

For color-temp-only lights (no RGB), warm white and Force White work; event colors will be approximated by the bulb.

---

## 📋 File Structure

```
chromacal/
├── README.md
├── ROADMAP.md
├── hacs.json
├── LICENSE
├── dist/
│   └── chromacal.html          ← the entire app
└── blueprints/
    └── automation/
        └── chromacal/
            └── chromacal_sync.yaml
```

---

## 🔒 Privacy

ChromaCal stores your HA URL and token in browser `localStorage` only. Nothing is sent anywhere except directly to your own Home Assistant instance. No cloud, no analytics, no ads.

**Worth knowing if you use Nabu Casa or any other remote access method:** files served from HA's `/local/` URL (the `www` folder, where this dashboard lives) aren't protected by HA's own authentication. This is true for anything anyone puts in `www`, not specific to ChromaCal, and it's a long-standing, documented characteristic of how HA serves static files, not a bug, browser-loaded resources like images don't carry auth headers, so HA made `/local/` deliberately unauthenticated to keep dashboard images and similar resources working. It applies the same way through a Nabu Casa URL as it does locally.

Practically, since ChromaCal never writes your token or your settings into the file itself, anyone who finds the URL without already having your token sees an empty setup screen, not your actual lights, schedule, or configuration. Still genuinely worth knowing before you install, especially with remote access configured, since it's true of this file the same as any other file you've ever placed in `www`.

---

## 🗺️ What's Next

A major architecture change is planned, splitting ChromaCal into a real Home Assistant Integration (the scheduling brain, running server-side with zero browser dependency) and a proper Lovelace custom card (the control surface). See `ROADMAP.md` for the full plan and reasoning.

---

## 🤝 Contributing

Issues and PRs welcome. Use **Settings → Feedback → Report a Bug** inside ChromaCal to open a pre-filled GitHub Issue with your version and setup info automatically included.

---

## 📄 License

MIT — do whatever you want, attribution appreciated.

*ChromaCal v1.0.0 — Honor your heritage. Light your home.*

# ChromaCal 🎨

**Automated holiday lighting for Home Assistant. One file. No YAML config. No integrations.**

ChromaCal is a single HTML dashboard that lives in your HA `/www/` folder. It knows about 130+ holidays, awareness months, and cultural observances across US, Canada, UK, Australia, EU, and globally — and automatically cycles your lights through the right colors every night, year after year, without maintenance.

> *"The whole world celebrates with light. Now you can too."*

---

## ✨ What it does

- **Zero maintenance** — Easter, Thanksgiving, Mardi Gras, Islamic dates, Jewish holidays, all computed algorithmically forever
- **130+ events** — Federal, Military, Cultural, Heritage, Pride, Awareness, Religious, Personal categories
- **Split-night scheduling** — Multiple June awareness months (Pride, Men's Health, Caribbean Heritage) automatically split the color window equally
- **Pub/Sub bridge** — Companion Blueprint keeps lights running server-side even when the browser is closed
- **Tonight's Schedule** — Full visual timeline with countdown, phase list, feature toggles
- **Quick Controls** — Test colors, Color Override, Force White (with Kelvin picker), Emergency Mode (US/EU/Amber/Red-White)
- **Skip system** — Permanent skip (⊘) or Skip Tonight only (🌙, auto-resets at midnight)
- **Tonight's Pick** — Force one event to own the full window (⭐)
- **Warm White** — Security lighting at a configurable Kelvin (2700K → 6500K) before lights-off
- **Fade-In control** — 30s to 10min crossfade when colors fire
- **5 themes** — Daylight, Twilight (Catppuccin Mocha), Sci-Fi, Mono, Custom

---

## 📦 Installation

### 1. Add to Home Assistant

Copy `chromacal.html` to your HA `/config/www/` folder:

```bash
# Via SCP (adjust path/port)
scp -P 22 chromacal.html user@ha-host:/config/www/chromacal.html
```

Or use the HA File Editor / Studio Code Server.

Access at: `http://your-ha-ip:8123/local/chromacal.html`

### 2. Import the Blueprint

Copy `blueprints/automation/chromacal/chromacal_sync.yaml` to:
```
/config/blueprints/automation/chromacal/chromacal_sync.yaml
```

Or import via URL in HA → Settings → Automations & Scenes → Blueprints → Import.

### 3. First launch

1. Open ChromaCal in your browser
2. Enter your HA URL and a Long-Lived Access Token (Profile → Security)
3. Add your light entity (auto-detects from HA)
4. Configure your schedule (start offset, warm white, fade-in duration)
5. Create a Blueprint automation: Settings → Automations → Create from Blueprint → ChromaCal Sync Engine

---

## ⚙️ Light Configuration

### Color Start Offset
How many minutes **after sunset** ChromaCal waits before firing colors. Set this to match when your existing warm-up automation finishes.

Example: If your "Sunset Fade In" starts 30 min before sunset and takes 45 min total, it finishes at sunset + 15 min. Set offset to **+15** for colors to fire right after, or **+30** for a 15-min warm white buffer.

### Warm-Up Automation Start
How many minutes **before sunset** your existing warm-up automation starts. This affects only the timeline display — ChromaCal doesn't control the warm-up, your HA automation does.

### Color Fade-In
How long the crossfade takes when holiday colors first fire:
- **30 sec** — quick snap
- **1 min** — smooth (default)
- **5 min** — very gradual, barely perceptible transition
- **10 min** — ultra slow melt into color

This is a single Zigbee `transition` parameter — no additional commands needed.

### Warm White
Security lighting before lights-off. Choose your preferred Kelvin:
- 🕯️ Candle (1800K) — very warm amber
- Warm (2700K) — classic incandescent
- Neutral (4000K) — clean white (default)
- Daylight (5000K) — bright
- ✨ Jesus Lights (6500K) — max white-blue intensity

---

## 🗓️ Calendar Coverage

**US:** Federal holidays, Military observances (including POW/MIA, USMC Birthday), cultural months, awareness months, pride events, religious observances

**International:** Canada, UK, Australia, EU, APAC, Latin America, and global Islamic/Jewish/Hindu/Lunar floating calendar

**All floating dates computed algorithmically** — Easter (Meeus/Jones/Butcher), US nthWeekday holidays, Islamic calendar estimates, Jewish calendar, and more. Verified correct 2024–2030.

---

## 🔗 The Bridge (Blueprint)

ChromaCal publishes its schedule to `input_text.chromacal_[lightname]` in HA's state machine every 30 seconds. The companion Blueprint watches this entity and fires physical light commands — so lights change color even when ChromaCal's browser tab is closed.

**Hardened against HA restarts:** The Blueprint uses `state_attr()` reads (not trigger context) and triggers on `homeassistant: start` and `automation_reloaded` events, so it recovers correctly after any interruption.

---

## 🚨 Emergency Mode

Activates alternating emergency lighting patterns using Zigbee-safe 3-second intervals:

- 🔴🔵 **Red/Blue (US)** — Police/Fire simulation
- 🔵 **Blue (EU)** — EU emergency standard with pulse
- 🟡 **Amber** — Roadway/construction
- 🔴⚪ **Red/White** — Fire truck pattern

Click the button again to cancel and resume schedule.

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

For color-temp-only lights (no RGB), warm white and the Force White feature work; event colors will be approximated by the bulb.

---

## 📋 File Structure

```
chromacal/
├── README.md
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

---

## 🤝 Contributing

Issues and PRs welcome at [github.com/TheRealApollyon/chromacal](https://github.com/TheRealApollyon/chromacal)

Use **Settings → Feedback → Report a Bug** in ChromaCal to open a pre-filled GitHub Issue with your version and setup info.

---

## 📄 License

MIT — do whatever you want, attribution appreciated.

*ChromaCal v1.0.0 — Honor your heritage. Light your home.*

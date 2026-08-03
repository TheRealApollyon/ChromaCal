import { LitElement, html, css, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";

import type { HomeAssistant, PanelInfo } from "./types";
import { buildViewModel, type LightCardModel, type SkipModel, type UpcomingEventModel } from "./grouping";
import { nativeThemeVars, presetThemeVars, PRESET_IDS, PRESET_LABELS, type PresetId } from "./theme";
import { buildTimelineMarks, segmentPosition } from "./timeline";

const THEME_STORAGE_KEY = "chromacal-panel-theme-preset";

/** Multi-color cycling events get the same "spinning" glow pulse v1 used
 * for its color orb -- ported at the same threshold v1 hardcoded. */
const SPINNING_COLOR_THRESHOLD = 5;

function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.replace("#", "");
  const value = parseInt(clean, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

@customElement("chromacal-panel")
export class ChromaCalPanel extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: Boolean }) narrow = false;
  @property({ attribute: false }) panel?: PanelInfo;

  @state() private _themePreset: PresetId = "native";
  @state() private _skipFilter = "";
  @state() private _manageSkipsOpen = false;
  @state() private _controlsOpen = false;

  connectedCallback(): void {
    super.connectedCallback();
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored && (PRESET_IDS as readonly string[]).includes(stored)) {
      this._themePreset = stored as PresetId;
    }
    this._applyThemeAttribute();
  }

  private _applyThemeAttribute(): void {
    if (this._themePreset === "native") {
      this.removeAttribute("data-theme");
    } else {
      this.setAttribute("data-theme", this._themePreset);
    }
  }

  private _onThemeChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value as PresetId;
    this._themePreset = value;
    localStorage.setItem(THEME_STORAGE_KEY, value);
    this._applyThemeAttribute();
  }

  private _callService(
    domain: string,
    service: string,
    entityId: string | null,
  ): void {
    if (!entityId) return;
    this.hass.callService(domain, service, { entity_id: entityId });
  }

  private _pressButton(entityId: string | null): void {
    this._callService("button", "press", entityId);
  }

  private _toggleSwitch(entityId: string | null, isOn: boolean): void {
    this._callService("switch", isOn ? "turn_off" : "turn_on", entityId);
  }

  render() {
    if (!this.hass) return nothing;
    const model = buildViewModel(this.hass);

    return html`
      <div class="root">
        <header>
          <h1>ChromaCal</h1>
          <div class="header-right">
            <button
              class="emergency-toggle ${model.globals.emergencyOn ? "active" : ""}"
              ?disabled=${!model.globals.emergencyEntityId}
              @click=${() =>
                this._toggleSwitch(model.globals.emergencyEntityId, model.globals.emergencyOn)}
              title="Emergency Mode -- broadcasts an alternating alert pattern until turned off"
            >
              Emergency Mode ${model.globals.emergencyOn ? "(Active)" : ""}
            </button>
            <label class="theme-picker">
              <span class="visually-hidden">Panel theme</span>
              <select @change=${this._onThemeChange} .value=${this._themePreset}>
                ${PRESET_IDS.map(
                  (id) => html`<option value=${id} ?selected=${id === this._themePreset}>
                    ${PRESET_LABELS[id]}
                  </option>`,
                )}
              </select>
            </label>
          </div>
        </header>

        <div class="page-grid ${this.narrow ? "narrow" : ""}">
          <main class="main-col">
            ${model.lights.length === 0
              ? html`<div class="empty-state">
                  <p>No lights configured yet.</p>
                  <p class="muted">Add a light from ChromaCal's settings to see it here.</p>
                </div>`
              : html`<section class="light-grid ${this.narrow ? "narrow" : ""}">
                  ${model.lights.map((light) => this._renderLightCard(light))}
                </section>`}

            <section class="upcoming-section">
              <h2>Upcoming Events</h2>
              ${model.upcomingEvents.length === 0
                ? html`<p class="muted">No events in the next 45 days for your selected categories.</p>`
                : html`<div class="upcoming-list">
                    ${model.upcomingEvents.map((event) => this._renderUpcomingRow(event))}
                  </div>`}
            </section>
          </main>

          <aside class="side-col">
            <section class="skip-section">
              <h2>Tonight's Skips</h2>
              ${model.tonightSkips.length === 0
                ? html`<p class="muted">Nothing skipped tonight.</p>`
                : html`<div class="chip-row">
                    ${model.tonightSkips.map((skip) => this._renderSkipChip(skip))}
                  </div>`}
            </section>

            <details
              class="collapsible-section"
              ?open=${this._controlsOpen}
              @toggle=${(e: Event) => (this._controlsOpen = (e.target as HTMLDetailsElement).open)}
            >
              <summary>Controls</summary>
              <div class="controls-bar">
                <button
                  class="control-btn"
                  ?disabled=${!model.globals.saluteEntityId}
                  @click=${() => this._pressButton(model.globals.saluteEntityId)}
                >
                  ${model.globals.saluteRunning ? "Cancel Salute" : "21 Gun Salute"}
                </button>
                <button
                  class="control-btn"
                  ?disabled=${!model.globals.catchUpEntityId}
                  @click=${() => this._pressButton(model.globals.catchUpEntityId)}
                >
                  Catch Up / Sync
                </button>
                <button
                  class="control-btn"
                  ?disabled=${!model.globals.stopEntityId}
                  @click=${() => this._pressButton(model.globals.stopEntityId)}
                >
                  Stop
                </button>
              </div>
            </details>

            <details
              class="collapsible-section"
              ?open=${this._manageSkipsOpen}
              @toggle=${(e: Event) => (this._manageSkipsOpen = (e.target as HTMLDetailsElement).open)}
            >
              <summary>Manage Skips (${model.permanentSkips.length} events)</summary>
              <input
                type="search"
                placeholder="Filter events..."
                .value=${this._skipFilter}
                @input=${(e: Event) => (this._skipFilter = (e.target as HTMLInputElement).value)}
              />
              <div class="chip-row">
                ${model.permanentSkips
                  .filter((skip) =>
                    skip.eventName.toLowerCase().includes(this._skipFilter.toLowerCase()),
                  )
                  .map((skip) => this._renderSkipChip(skip))}
              </div>
            </details>
          </aside>
        </div>
      </div>
    `;
  }

  private _formatEventDate(isoDate: string): string {
    // "T00:00:00" avoids the UTC-midnight-rolls-back-a-day trap of parsing
    // a bare YYYY-MM-DD string, which JS treats as UTC while
    // toLocaleDateString renders in the browser's local zone.
    return new Date(`${isoDate}T00:00:00`).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  }

  private _renderUpcomingRow(event: UpcomingEventModel) {
    const permSkip = event.permanentSkip;
    const nightSkip = event.tonightSkip;
    return html`
      <div class="upcoming-row ${event.isToday ? "today" : ""} ${permSkip?.isOn ? "skipped" : ""}">
        <span class="up-date">${event.isToday ? "TODAY" : this._formatEventDate(event.date)}</span>
        <span class="up-icon">${event.icon}</span>
        <span class="up-name">${event.name}</span>
        <span class="up-badge">${event.category}</span>
        <span class="up-chips">
          ${event.colors.map((c) => html`<span class="up-chip" style="background:${c}"></span>`)}
        </span>
        <button
          class="up-action-btn"
          disabled
          title="Tonight's Pick -- not wired up yet, coming in a follow-up"
        >
          ☆
        </button>
        <button
          class="up-action-btn"
          disabled
          title="Customize colors -- not wired up yet, coming in a follow-up"
        >
          🎨
        </button>
        ${nightSkip
          ? html`<button
              class="up-action-btn ${nightSkip.isOn ? "active" : ""}"
              @click=${() => this._toggleSwitch(nightSkip.entityId, nightSkip.isOn)}
              title=${nightSkip.isOn
                ? "Skipped tonight -- click to restore"
                : "Skip for tonight only (resets at midnight)"}
            >
              🌙
            </button>`
          : nothing}
        ${permSkip
          ? html`<button
              class="up-action-btn ${permSkip.isOn ? "active" : ""}"
              @click=${() => this._toggleSwitch(permSkip.entityId, permSkip.isOn)}
              title=${permSkip.isOn
                ? "Re-enable -- this event will run again"
                : "Permanently skip this event"}
            >
              ${permSkip.isOn ? "⊘" : "○"}
            </button>`
          : nothing}
      </div>
    `;
  }

  private _renderSkipChip(skip: SkipModel) {
    return html`
      <button
        class="chip ${skip.isOn ? "skipped" : ""}"
        @click=${() => this._toggleSwitch(skip.entityId, skip.isOn)}
        title=${skip.isOn ? "Skipped -- click to restore" : "Click to skip"}
      >
        ${skip.eventName}
      </button>
    `;
  }

  /** Orb style: an *active* color (a real segment color) always wins and
   * is rendered as-is -- that's live data, not decoration. With no active
   * color, the orb falls back to a neutral fill with a themed ring driven
   * by --cc-accent (HA's --primary-color by default), never a hardcoded
   * hue -- see the Phase 7 plan discussion for why that split matters. */
  private _renderOrb(light: LightCardModel, size: "full" | "compact") {
    const activeColor = light.currentColors[0];
    const spinning = light.currentColors.length >= SPINNING_COLOR_THRESHOLD;
    // Highlight opacity and glow alpha/blur values are pulled directly from
    // v1's own setOrb() (dist/chromacal.html), scaled down from its 84px
    // orb to this component's 64px/32px sizes -- real rendered ground
    // truth, not a guessed approximation.
    const style = activeColor
      ? `background: radial-gradient(circle at 38% 30%, rgba(255,255,255,.45) 0%, ${activeColor} 45%, rgba(0,0,0,.5) 100%); box-shadow: 0 0 ${
          size === "full" ? "24px" : "12px"
        } ${hexToRgba(activeColor, 0.627)}, 0 0 ${size === "full" ? "46px" : "23px"} ${hexToRgba(
          activeColor,
          0.208,
        )};`
      : "";
    return html`<div class="orb ${size} ${spinning ? "spinning" : ""}" style=${style}></div>`;
  }

  private _renderLightCard(light: LightCardModel) {
    if (this.narrow) {
      return html`
        <div class="light-card compact">
          ${this._renderOrb(light, "compact")}
          <div class="compact-info">
            <span class="light-name-eyebrow">${light.lightName}</span>
            <span class="event-name-headline compact">${light.currentEventName ?? "—"}</span>
          </div>
        </div>
      `;
    }

    const marks = buildTimelineMarks(light, new Date().getHours() + new Date().getMinutes() / 60);

    return html`
      <div class="light-card">
        <div class="card-top">
          ${this._renderOrb(light, "full")}
          <div class="card-info">
            <span class="light-name-eyebrow">${light.lightName}</span>
            <span class="event-name-headline">${light.currentEventName ?? "No active event"}</span>
            ${light.currentStart && light.currentEnd
              ? html`<span class="event-time-range"
                  >${light.currentStart}&ndash;${light.currentEnd}</span
                >`
              : nothing}
          </div>
          ${light.forceWhiteEntityId
            ? html`<button
                class="force-white-btn"
                @click=${() => this._pressButton(light.forceWhiteEntityId)}
              >
                Force White
              </button>`
            : nothing}
        </div>
        ${light.segments.length > 0
          ? html`<div class="timeline-wrapper">
              <div class="timeline">
                ${light.segments.map((segment) => {
                  const { leftPct, widthPct } = segmentPosition(segment.startTime, segment.endTime);
                  const isCurrent = segment.name === light.currentEventName;
                  return html`<div
                    class="timeline-seg ${isCurrent ? "current" : ""}"
                    style="left:${leftPct}%; width:${widthPct}%; background:${segment.colors[0] ??
                    "var(--cc-s2)"}"
                    title="${segment.name} (${segment.startTime}–${segment.endTime})"
                  ></div>`;
                })}
              </div>
              <div class="timeline-marks">
                ${marks.map(
                  (mark) => html`
                    <div class="tl-mark" style="left:${mark.leftPct}%">
                      <div class="tl-mark-line"></div>
                      ${!mark.bare
                        ? html`<span class="tl-mark-lbl ${mark.emphasize ? "hl" : ""}"
                              >${mark.label}</span
                            ><span class="tl-mark-lbl ${mark.emphasize ? "hl" : ""}">${mark.time}</span>`
                        : nothing}
                    </div>
                  `,
                )}
              </div>
            </div>`
          : nothing}
      </div>
    `;
  }

  static styles = [
    nativeThemeVars,
    presetThemeVars,
    css`
      :host {
        display: block;
        font-family: var(--cc-font);
        color: var(--cc-text);
        background: var(--cc-bg);
        padding: 16px;
        box-sizing: border-box;
      }

      * {
        box-sizing: border-box;
      }

      .visually-hidden {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        clip: rect(0 0 0 0);
      }

      header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
      }

      .header-right {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      h1 {
        font-size: 22px;
        margin: 0;
        color: var(--cc-accent);
      }

      .emergency-toggle {
        background: var(--cc-s1);
        border: 1px solid var(--cc-red);
        color: var(--cc-red);
        font-weight: 600;
        border-radius: var(--cc-radius);
        padding: 6px 14px;
        font-family: inherit;
        font-size: 13px;
        cursor: pointer;
      }

      .emergency-toggle:disabled {
        opacity: 0.5;
        cursor: default;
      }

      .emergency-toggle.active {
        background: var(--cc-red);
        color: var(--cc-s1);
      }

      h2 {
        font-size: 16px;
        margin: 0 0 8px;
      }

      select,
      input[type="search"] {
        background: var(--cc-s2);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-radius: 6px;
        padding: 6px 10px;
        font-family: inherit;
      }

      .muted {
        color: var(--cc-muted);
        font-size: 13px;
      }

      /* ── Page composition: main content wide/left, secondary controls
         narrow/right -- the same "primary destination first" tiering the
         backend design already follows, reinforced spatially here. ── */
      .page-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(260px, 320px);
        gap: 20px;
        align-items: start;
      }

      .page-grid.narrow {
        grid-template-columns: 1fr;
      }

      .main-col {
        min-width: 0;
      }

      .side-col {
        min-width: 0;
      }

      .controls-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
      }

      .control-btn {
        background: var(--cc-s1);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 10px 16px;
        font-family: inherit;
        font-size: 14px;
        cursor: pointer;
      }

      .control-btn:hover:not(:disabled) {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
      }

      .control-btn:disabled {
        opacity: 0.5;
        cursor: default;
      }

      .empty-state {
        background: var(--cc-s1);
        border: 1px dashed var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 32px;
        text-align: center;
        margin-bottom: 20px;
      }

      .light-grid {
        display: grid;
        /* auto-fit, not auto-fill: auto-fill reserves a full track's worth
           of width for every track the container COULD hold, even ones
           with no card in them, leaving real cards squeezed into a
           fraction of the row with dead space beside them. auto-fit
           collapses those empty tracks so populated ones actually expand
           to fill the row. */
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 14px;
      }

      .light-grid.narrow {
        grid-template-columns: 1fr;
      }

      .light-card {
        background: var(--cc-s1);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 16px;
      }

      .light-card.compact {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
      }

      .card-top {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 14px;
      }

      .card-info {
        flex: 1;
        min-width: 0;
      }

      .compact-info {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
      }

      /* ── Hierarchy: the light's own name is the quiet label; the current
         event is the loud headline -- inverted from the original layout,
         which had it backwards. ── */
      .light-name-eyebrow {
        display: block;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--cc-muted);
        margin-bottom: 4px;
      }

      .event-name-headline {
        display: block;
        font-size: 19px;
        font-weight: 700;
        color: var(--cc-accent);
        text-shadow: 0 0 12px color-mix(in srgb, var(--cc-accent) 45%, transparent);
        line-height: 1.25;
        /* Never truncate -- this is the single most important text on the
           card, so it wraps onto a second line instead of clipping. */
        white-space: normal;
        overflow-wrap: break-word;
      }

      .event-name-headline.compact {
        font-size: 15px;
      }

      .event-time-range {
        display: block;
        color: var(--cc-muted);
        font-size: 12px;
        margin-top: 4px;
      }

      .force-white-btn {
        background: var(--cc-s2);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
        cursor: pointer;
        font-family: inherit;
        align-self: flex-start;
        flex-shrink: 0;
      }

      .force-white-btn:hover {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
      }

      /* ── Signature orb -- see _renderOrb()'s comment for the real-color-
         vs-themed-idle-glow split. ── */
      .orb {
        border-radius: 50%;
        background: var(--cc-s2);
        flex-shrink: 0;
        transition: background 0.8s, box-shadow 0.8s;
        box-shadow: 0 0 0 2px var(--cc-accent) inset;
      }

      .orb.full {
        width: 64px;
        height: 64px;
      }

      .orb.compact {
        width: 32px;
        height: 32px;
        box-shadow: 0 0 0 1.5px var(--cc-accent) inset;
      }

      .orb.spinning {
        animation: orb-pulse 3s ease-in-out infinite alternate;
      }

      @keyframes orb-pulse {
        from {
          filter: brightness(1);
        }
        to {
          filter: brightness(1.3);
        }
      }

      .timeline-wrapper {
        position: relative;
        padding-bottom: 34px;
      }

      .timeline {
        /* Height/radius scaled up from an earlier 10px pass to match v1's
           actual rendered bar (dist/chromacal.html's #phase-rows), which
           reads as noticeably more present/legible at this size. */
        position: relative;
        height: 16px;
        background: var(--cc-s2);
        border-radius: 8px;
        overflow: hidden;
      }

      .timeline-seg {
        position: absolute;
        top: 0;
        bottom: 0;
        opacity: 0.65;
      }

      .timeline-seg.current {
        opacity: 1;
        box-shadow: 0 0 0 1px var(--cc-accent) inset;
      }

      .timeline-marks {
        position: absolute;
        left: 0;
        right: 0;
        top: 20px;
      }

      .tl-mark {
        position: absolute;
        transform: translateX(-50%);
        text-align: center;
        white-space: nowrap;
      }

      .tl-mark-line {
        width: 1.5px;
        height: 7px;
        background: var(--cc-border);
        margin: 0 auto 4px;
      }

      .tl-mark-lbl {
        font-size: 10px;
        color: var(--cc-muted);
        line-height: 1.4;
        display: block;
      }

      .tl-mark-lbl.hl {
        color: var(--cc-text);
        font-weight: 700;
        font-size: 11px;
      }

      .upcoming-section {
        margin-top: 20px;
      }

      .upcoming-list {
        display: flex;
        flex-direction: column;
        gap: 1px;
        background: var(--cc-border);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        overflow: hidden;
      }

      .upcoming-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: var(--cc-s1);
        font-size: 13px;
      }

      .upcoming-row.today {
        background: var(--cc-s2);
      }

      .upcoming-row.skipped {
        opacity: 0.5;
      }

      .up-date {
        width: 78px;
        flex-shrink: 0;
        color: var(--cc-muted);
        font-size: 12px;
      }

      .upcoming-row.today .up-date {
        color: var(--cc-accent);
        font-weight: 700;
      }

      .up-icon {
        flex-shrink: 0;
      }

      .up-name {
        flex: 1;
        min-width: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .up-badge {
        flex-shrink: 0;
        background: var(--cc-s2);
        color: var(--cc-muted);
        border-radius: 999px;
        padding: 2px 8px;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .up-chips {
        display: flex;
        gap: 2px;
        flex-shrink: 0;
      }

      .up-chip {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        border: 1px solid var(--cc-border);
      }

      .up-action-btn {
        flex-shrink: 0;
        background: none;
        border: 1px solid var(--cc-border);
        border-radius: 6px;
        width: 26px;
        height: 26px;
        color: var(--cc-muted);
        cursor: pointer;
        font-size: 13px;
        line-height: 1;
      }

      .up-action-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }

      .up-action-btn:hover:not(:disabled) {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
      }

      .up-action-btn.active {
        background: var(--cc-accent2);
        color: var(--cc-s1);
        border-color: var(--cc-accent2);
      }

      .skip-section {
        margin-bottom: 16px;
      }

      .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
      }

      .chip {
        background: var(--cc-s2);
        color: var(--cc-muted);
        border: 1px solid var(--cc-border);
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 12px;
        cursor: pointer;
        font-family: inherit;
      }

      .chip:hover {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
      }

      .chip.skipped {
        background: var(--cc-accent2);
        color: var(--cc-s1);
        border-color: var(--cc-accent2);
      }

      /* Giving a direct child its own display:flex/block here defeats the
       * browser's native closed-<details> hiding (author styles beat the UA
       * stylesheet regardless of specificity) -- add a matching
       * :not([open]) override below whenever a new child gets one. */
      .collapsible-section {
        background: var(--cc-s1);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 12px 14px;
        margin-bottom: 12px;
      }

      .collapsible-section summary {
        cursor: pointer;
        font-weight: 600;
      }

      .collapsible-section[open] summary {
        margin-bottom: 8px;
      }

      .collapsible-section .controls-bar {
        margin-bottom: 0;
      }

      .collapsible-section input[type="search"] {
        display: block;
        width: 100%;
        margin: 10px 0;
      }

      /* Author-origin display rules (flex/block above) otherwise defeat the
       * browser's own "hide contents while closed" UA rule for <details> --
       * origin beats specificity in the cascade, so author styles win over
       * the UA stylesheet regardless of selector weight. Restore the
       * closed-state hiding explicitly rather than relying on the default. */
      .collapsible-section:not([open]) .controls-bar,
      .collapsible-section:not([open]) .chip-row,
      .collapsible-section:not([open]) input[type="search"] {
        display: none;
      }
    `,
  ];
}

declare global {
  interface HTMLElementTagNameMap {
    "chromacal-panel": ChromaCalPanel;
  }
}

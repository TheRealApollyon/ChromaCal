import { LitElement, html, css, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";

import type { HomeAssistant, PanelInfo } from "./types";
import { buildViewModel, type LightCardModel, type SkipModel } from "./grouping";
import { nativeThemeVars, presetThemeVars, PRESET_IDS, PRESET_LABELS, type PresetId } from "./theme";

const THEME_STORAGE_KEY = "chromacal-panel-theme-preset";

/** 16:00 today through 08:00 tomorrow -- the window every night-schedule
 * segment chromacal produces should fall inside (see get_night_segments). */
const WINDOW_START_MIN = 16 * 60;
const WINDOW_SPAN_MIN = 16 * 60;

function hhmmToMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

/** Positions a HH:MM-HH:MM segment inside the fixed night window above,
 * wrapping anything before 16:00 to "the next day" so a segment crossing
 * midnight still renders as one continuous span. */
function segmentPosition(startTime: string, endTime: string): { leftPct: number; widthPct: number } {
  const rawStart = hhmmToMinutes(startTime);
  const rawEnd = hhmmToMinutes(endTime);
  const start = rawStart >= WINDOW_START_MIN ? rawStart : rawStart + 24 * 60;
  const end = rawEnd >= WINDOW_START_MIN ? rawEnd : rawEnd + 24 * 60;
  const leftPct = Math.max(0, Math.min(100, ((start - WINDOW_START_MIN) / WINDOW_SPAN_MIN) * 100));
  const rightPct = Math.max(0, Math.min(100, ((end - WINDOW_START_MIN) / WINDOW_SPAN_MIN) * 100));
  return { leftPct, widthPct: Math.max(0, rightPct - leftPct) };
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

        ${model.lights.length === 0
          ? html`<div class="empty-state">
              <p>No lights configured yet.</p>
              <p class="muted">Add a light from ChromaCal's settings to see it here.</p>
            </div>`
          : html`<section class="light-grid ${this.narrow ? "narrow" : ""}">
              ${model.lights.map((light) => this._renderLightCard(light))}
            </section>`}

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

  private _renderLightCard(light: LightCardModel) {
    if (this.narrow) {
      return html`
        <div class="light-card compact">
          <span class="light-name">${light.lightName}</span>
          <span class="event-name">${light.currentEventName ?? "—"}</span>
          ${light.currentColors[0]
            ? html`<span class="swatch" style="background:${light.currentColors[0]}"></span>`
            : nothing}
        </div>
      `;
    }

    return html`
      <div class="light-card">
        <div class="light-card-header">
          <span class="light-name">${light.lightName}</span>
          ${light.forceWhiteEntityId
            ? html`<button
                class="force-white-btn"
                @click=${() => this._pressButton(light.forceWhiteEntityId)}
              >
                Force White
              </button>`
            : nothing}
        </div>
        <div class="current-event">
          ${light.currentColors[0]
            ? html`<span class="swatch" style="background:${light.currentColors[0]}"></span>`
            : nothing}
          <span class="event-name">${light.currentEventName ?? "No active event"}</span>
          ${light.currentStart && light.currentEnd
            ? html`<span class="muted"
                >${light.currentStart}&ndash;${light.currentEnd}</span
              >`
            : nothing}
        </div>
        ${light.segments.length > 0
          ? html`<div class="timeline">
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
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 12px;
        margin-bottom: 24px;
      }

      .light-grid.narrow {
        grid-template-columns: 1fr;
      }

      .light-card {
        background: var(--cc-s1);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 14px;
      }

      .light-card.compact {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
      }

      .light-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
      }

      .light-name {
        font-weight: 600;
      }

      .compact .light-name {
        flex: 1;
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
      }

      .force-white-btn:hover {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
      }

      .current-event {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
      }

      .swatch {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 1px solid var(--cc-border);
        flex-shrink: 0;
      }

      .event-name {
        font-size: 14px;
      }

      .timeline {
        position: relative;
        height: 10px;
        background: var(--cc-s2);
        border-radius: 5px;
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

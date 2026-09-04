import{a as _,b as s,c as b,d as z,e as C,f as E,g as f}from"./chunk-5VH4SVWE.js";import{a as u}from"./chunk-JFKSI6I7.js";function Y(r){return{name:r.name,eventType:r.event_type,colors:r.colors,icon:r.icon,startTime:r.start_time,endTime:r.end_time}}function K(r){return Object.values(r.entities).filter(c=>c.platform==="chromacal").map(c=>c.entity_id)}function J(r){return r.split(".",1)[0]}function k(r){let c=K(r),e={saluteEntityId:null,saluteRunning:!1,catchUpEntityId:null,stopEntityId:null,emergencyEntityId:null,emergencyOn:!1},t=new Map,o=new Map,a=[],m=[],y=null,x=null;for(let i of c){let h=r.states[i];if(!h)continue;let p=h.attributes,g=J(i);if(g==="button"){let v=p.role;v==="salute"?(e.saluteEntityId=i,e.saluteRunning=!!p.running):v==="catch_up_sync"?e.catchUpEntityId=i:v==="stop"?e.stopEntityId=i:v==="force_white"&&typeof p.light_entity=="string"&&o.set(p.light_entity,i);continue}if(g==="switch"){let v=p.role;if(v==="emergency_mode")e.emergencyEntityId=i,e.emergencyOn=h.state==="on";else if(v==="skip"&&typeof p.event_name=="string"){let R={entityId:i,eventName:p.event_name,isOn:h.state==="on"};p.scope==="tonight"?a.push(R):m.push(R)}continue}g==="sensor"&&(p.role==="upcoming_events"?y=i:p.role==="house_view"?x=i:typeof p.light_entity=="string"&&t.set(p.light_entity,i))}let w=[];for(let[i,h]of t){let p=r.states[h],g=p?.attributes??{},v=g.light_name??i;w.push({lightEntity:i,lightName:v,scheduleEntityId:h,forceWhiteEntityId:o.get(i)??null,currentEventName:p?.state||null,currentEventType:g.event_type??null,currentColors:g.colors??[],currentIcon:g.icon??null,currentStart:g.start_time??null,currentEnd:g.end_time??null,segments:(g.segments??[]).map(Y),sunsetHour:g.sunset_hour??null,scheduleEndTime:g.schedule_end_time??null})}w.sort((i,h)=>i.lightName.localeCompare(h.lightName)),a.sort((i,h)=>i.eventName.localeCompare(h.eventName)),m.sort((i,h)=>i.eventName.localeCompare(h.eventName));let $=new Map(m.map(i=>[i.eventName,i])),n=new Map(a.map(i=>[i.eventName,i])),d=y?r.states[y]?.attributes:void 0,T=d?.events??[],G=d?.tonight_pick??null,j=d?.color_overrides??{},X=T.map(i=>({date:i.date,name:i.name,category:i.category,eventType:i.event_type,icon:i.icon,colors:i.colors,isToday:i.is_today,isPersonalRange:i.is_personal_range,permanentSkip:$.get(i.name)??null,tonightSkip:i.is_today?n.get(i.name)??null:null,isPicked:i.is_today&&G===i.name,overrideColors:j[i.name]??null})),O=x?r.states[x]?.attributes:void 0,q={mode:O?.mode??"2d",path:O?.path??"",markers:(O?.markers??[]).map(i=>({id:i.id,mode:i.mode,x:i.x,y:i.y,z:i.z,lightEntity:i.light_entity}))};return{globals:e,lights:w,tonightSkips:a,permanentSkips:m,upcomingEvents:X,houseView:q}}var L=_`
  :host {
    --cc-bg: var(--primary-background-color, #fafafa);
    --cc-s1: var(--card-background-color, #fff);
    --cc-s2: var(--secondary-background-color, var(--divider-color, #eee));
    --cc-border: var(--divider-color, #e0e0e0);
    --cc-accent: var(--primary-color, #03a9f4);
    --cc-accent2: var(--accent-color, var(--primary-color, #ff9800));
    --cc-green: var(--success-color, #4caf50);
    --cc-red: var(--error-color, #db4437);
    --cc-text: var(--primary-text-color, #212121);
    --cc-muted: var(--secondary-text-color, #727272);
    --cc-font: inherit;
    --cc-radius: var(--ha-card-border-radius, 12px);
  }
`,I=["native","daylight","twilight","scifi","mono"],P={native:"Match dashboard theme",daylight:"Daylight",twilight:"Twilight",scifi:"Sci-Fi",mono:"Mono"},A=_`
  :host([data-theme="daylight"]) {
    --cc-bg: #f0f2f8;
    --cc-s1: #ffffff;
    --cc-s2: #e8ecf5;
    --cc-border: #c8d0e4;
    --cc-accent: #1d4ed8;
    --cc-accent2: #b45309;
    --cc-green: #15803d;
    --cc-red: #b91c1c;
    --cc-text: #0f172a;
    --cc-muted: #64748b;
    --cc-font: "Orbitron", monospace;
  }

  :host([data-theme="twilight"]) {
    --cc-bg: #11111b;
    --cc-s1: #1e1e2e;
    --cc-s2: #313244;
    --cc-border: #585b70;
    --cc-accent: #89dceb;
    --cc-accent2: #f9e2af;
    --cc-green: #a6e3a1;
    --cc-red: #f38ba8;
    --cc-text: #cdd6f4;
    --cc-muted: #7f849c;
    --cc-font: "Orbitron", monospace;
  }

  :host([data-theme="scifi"]) {
    --cc-bg: #060810;
    --cc-s1: #0e1b2e;
    --cc-s2: #132338;
    --cc-border: #1f3758;
    --cc-accent: #00c8e8;
    --cc-accent2: #f59e0b;
    --cc-green: #22c55e;
    --cc-red: #f43f5e;
    --cc-text: #d6e4f0;
    --cc-muted: #516882;
    --cc-font: "Orbitron", monospace;
  }

  :host([data-theme="mono"]) {
    --cc-bg: #000000;
    --cc-s1: #111111;
    --cc-s2: #1c1c1c;
    --cc-border: #383838;
    --cc-accent: #ffffff;
    --cc-accent2: #ffd43b;
    --cc-green: #6bcf7f;
    --cc-red: #ff6b6b;
    --cc-text: #ffffff;
    --cc-muted: #aaaaaa;
    --cc-font: "Orbitron", monospace;
  }
`;function Q(r){let[c,e]=r.split(":").map(Number);return c*60+e}function W(r){return r>=960?r:r+1440}function H(r){return W(Math.round(r*60))}function M(r){return W(Q(r))}function N(r){return Math.max(0,Math.min(100,(r-960)/960*100))}function U(r,c){let e=N(M(r)),t=N(M(c));return{leftPct:e,widthPct:Math.max(0,t-e)}}function V(r){let c=Math.round(r*60)%1440,e=Math.floor(c/60),t=c%60;return`${String(e).padStart(2,"0")}:${String(t).padStart(2,"0")}`}function D(r,c){let e=H(c),t=[],o=r.segments[r.segments.length-1];if(o){let n=M(o.endTime),d=r.scheduleEndTime!==null?M(r.scheduleEndTime):null;d!==null&&n<d?(t.push({label:"WARM",time:o.endTime,windowMinutes:n,emphasize:!1,priority:0}),t.push({label:"OFF",time:r.scheduleEndTime,windowMinutes:d,emphasize:!0,priority:0})):t.push({label:"OFF",time:o.endTime,windowMinutes:n,emphasize:!0,priority:0})}if(t.push({label:"NOW",time:V(c),windowMinutes:e,emphasize:!1,priority:1}),r.sunsetHour!==null){let n=H(r.sunsetHour);n>e&&t.push({label:"SUNSET",time:V(r.sunsetHour),windowMinutes:n,emphasize:!1,priority:2})}let a=r.segments[0];if(a){let n=M(a.startTime);n>e&&t.push({label:"COLORS",time:a.startTime,windowMinutes:n,emphasize:!1,priority:2})}let m=9,y=t.map(n=>({...n,leftPct:N(n.windowMinutes)})),x=[...y].sort((n,d)=>n.priority-d.priority||n.windowMinutes-d.windowMinutes),w=[],$=new Map;for(let n of x){let d=n.priority>0&&w.some(T=>Math.abs(n.leftPct-T)<m);$.set(n,d),d||w.push(n.leftPct)}return y.sort((n,d)=>n.windowMinutes-d.windowMinutes).map(n=>({label:n.label,time:n.time,windowMinutes:n.windowMinutes,leftPct:n.leftPct,emphasize:n.emphasize,bare:$.get(n)??!1}))}var B="chromacal-panel-theme-preset",Z=5;function F(r,c){let e=r.replace("#",""),t=parseInt(e,16),o=t>>16&255,a=t>>8&255,m=t&255;return`rgba(${o}, ${a}, ${m}, ${c})`}var l=class extends z{constructor(){super(...arguments);this.narrow=!1;this._themePreset="native";this._skipFilter="";this._manageSkipsOpen=!1;this._controlsOpen=!1;this._houseViewOpen=!1;this._colorModalEvent=null;this._colorModalColors=[];this._colorModalPickerValue="#ffffff"}connectedCallback(){super.connectedCallback();let e=localStorage.getItem(B);e&&I.includes(e)&&(this._themePreset=e),this._applyThemeAttribute()}_applyThemeAttribute(){this._themePreset==="native"?this.removeAttribute("data-theme"):this.setAttribute("data-theme",this._themePreset)}_onThemeChange(e){let t=e.target.value;this._themePreset=t,localStorage.setItem(B,t),this._applyThemeAttribute()}_callService(e,t,o){o&&this.hass.callService(e,t,{entity_id:o})}_pressButton(e){this._callService("button","press",e)}_toggleSwitch(e,t){this._callService("switch",t?"turn_off":"turn_on",e)}_onHouseViewToggle(e){let t=e.target.open;this._houseViewOpen=t,t&&import("./house-view-BW6Y22GU.js")}_setTonightPick(e){this.hass.callService("chromacal","set_tonight_pick",{event_name:e})}_openColorModal(e){this._colorModalEvent=e.name,this._colorModalColors=[...e.overrideColors??e.colors]}_closeColorModal(){this._colorModalEvent=null,this._colorModalColors=[]}_addColorModalColor(){this._colorModalColors.length>=l.MAX_COLORS||(this._colorModalColors=[...this._colorModalColors,this._colorModalPickerValue])}_removeColorModalColor(e){this._colorModalColors=this._colorModalColors.filter((t,o)=>o!==e)}_moveColorModalColor(e,t){let o=e+t;if(o<0||o>=this._colorModalColors.length)return;let a=[...this._colorModalColors];[a[e],a[o]]=[a[o],a[e]],this._colorModalColors=a}_saveColorOverride(){!this._colorModalEvent||this._colorModalColors.length===0||(this.hass.callService("chromacal","set_color_override",{event_name:this._colorModalEvent,colors:this._colorModalColors}),this._closeColorModal())}_resetColorOverride(){this._colorModalEvent&&(this.hass.callService("chromacal","reset_color_override",{event_name:this._colorModalEvent}),this._closeColorModal())}render(){if(!this.hass)return b;let e=k(this.hass);return s`
      <div class="root">
        <header>
          <h1>ChromaCal</h1>
          <div class="header-right">
            <a
              class="settings-link"
              href="/config/integrations/integration/chromacal"
              title="Manage lights, categories, and region in Settings"
            >
              Manage Lights &amp; Categories
            </a>
            <button
              class="control-btn"
              ?disabled=${!e.globals.catchUpEntityId}
              @click=${()=>this._pressButton(e.globals.catchUpEntityId)}
            >
              Catch Up / Sync
            </button>
            <button
              class="control-btn"
              ?disabled=${!e.globals.stopEntityId}
              @click=${()=>this._pressButton(e.globals.stopEntityId)}
            >
              Stop
            </button>
            <button
              class="emergency-toggle ${e.globals.emergencyOn?"active":""}"
              ?disabled=${!e.globals.emergencyEntityId}
              @click=${()=>this._toggleSwitch(e.globals.emergencyEntityId,e.globals.emergencyOn)}
              title="Emergency Mode -- broadcasts an alternating alert pattern until turned off"
            >
              Emergency Mode ${e.globals.emergencyOn?"(Active)":""}
            </button>
            <label class="theme-picker">
              <span class="visually-hidden">Panel theme</span>
              <select @change=${this._onThemeChange} .value=${this._themePreset}>
                ${I.map(t=>s`<option value=${t} ?selected=${t===this._themePreset}>
                    ${P[t]}
                  </option>`)}
              </select>
            </label>
          </div>
        </header>

        <div class="page-grid ${this.narrow?"narrow":""}">
          <main class="main-col">
            ${this._renderLightGrid(e)}

            <section class="upcoming-section">
              <h2>Upcoming Events</h2>
              ${e.upcomingEvents.length===0?s`<p class="muted">No events in the next 45 days for your selected categories.</p>`:s`<div class="upcoming-list">
                    ${e.upcomingEvents.map(t=>this._renderUpcomingRow(t))}
                  </div>`}
            </section>

            <details
              class="collapsible-section house-view-section"
              ?open=${this._houseViewOpen}
              @toggle=${this._onHouseViewToggle}
            >
              <summary>House View</summary>
              ${this._houseViewOpen?s`<chromacal-house-view
                    .hass=${this.hass}
                    .model=${e.houseView}
                    .lights=${e.lights}
                  ></chromacal-house-view>`:b}
            </details>
          </main>

          <aside class="side-col">
            <section class="skip-section">
              <h2>Tonight's Skips</h2>
              ${e.tonightSkips.length===0?s`<p class="muted">Nothing skipped tonight.</p>`:s`<div class="chip-row">
                    ${e.tonightSkips.map(t=>this._renderSkipChip(t))}
                  </div>`}
            </section>

            <details
              class="collapsible-section"
              ?open=${this._controlsOpen}
              @toggle=${t=>this._controlsOpen=t.target.open}
            >
              <summary>Controls</summary>
              <div class="controls-bar">
                <button
                  class="control-btn"
                  ?disabled=${!e.globals.saluteEntityId}
                  @click=${()=>this._pressButton(e.globals.saluteEntityId)}
                >
                  ${e.globals.saluteRunning?"Cancel Salute":"21 Gun Salute"}
                </button>
              </div>
            </details>

            <details
              class="collapsible-section"
              ?open=${this._manageSkipsOpen}
              @toggle=${t=>this._manageSkipsOpen=t.target.open}
            >
              <summary>Manage Skips (${e.permanentSkips.length} events)</summary>
              <input
                type="search"
                placeholder="Filter events..."
                .value=${this._skipFilter}
                @input=${t=>this._skipFilter=t.target.value}
              />
              <div class="chip-row">
                ${e.permanentSkips.filter(t=>t.eventName.toLowerCase().includes(this._skipFilter.toLowerCase())).map(t=>this._renderSkipChip(t))}
              </div>
            </details>
          </aside>
        </div>

        ${this._colorModalEvent?this._renderColorModal():b}
      </div>
    `}_renderColorModal(){let e=this._colorModalEvent,t=this._colorModalColors;return s`
      <div class="modal-overlay" @click=${this._closeColorModal}>
        <div class="modal-dialog" @click=${o=>o.stopPropagation()}>
          <h3>Customize colors</h3>
          <p class="modal-event-name">${e}</p>

          <div class="modal-chip-row">
            ${t.length===0?s`<p class="muted">No colors -- add at least one below.</p>`:t.map((o,a)=>s`
                    <div class="modal-chip-item">
                      <span class="modal-chip" style="background:${o}" title=${o}></span>
                      <div class="modal-chip-btns">
                        <button
                          class="chip-move-btn"
                          ?disabled=${a===0}
                          @click=${()=>this._moveColorModalColor(a,-1)}
                          title="Move left"
                        >
                          ‹
                        </button>
                        <button
                          class="chip-move-btn chip-remove-btn"
                          @click=${()=>this._removeColorModalColor(a)}
                          title="Remove"
                        >
                          ×
                        </button>
                        <button
                          class="chip-move-btn"
                          ?disabled=${a===t.length-1}
                          @click=${()=>this._moveColorModalColor(a,1)}
                          title="Move right"
                        >
                          ›
                        </button>
                      </div>
                    </div>
                  `)}
          </div>

          <div class="modal-add-row">
            <input
              type="color"
              .value=${this._colorModalPickerValue}
              @input=${o=>this._colorModalPickerValue=o.target.value}
            />
            <button
              class="control-btn"
              ?disabled=${t.length>=l.MAX_COLORS}
              @click=${this._addColorModalColor}
            >
              Add color
            </button>
          </div>

          <div class="modal-actions">
            <button class="control-btn" @click=${this._resetColorOverride}>Reset to default</button>
            <div class="modal-actions-right">
              <button class="control-btn" @click=${this._closeColorModal}>Cancel</button>
              <button
                class="control-btn control-btn-primary"
                ?disabled=${t.length===0}
                @click=${this._saveColorOverride}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    `}_formatEventDate(e){return new Date(`${e}T00:00:00`).toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"})}_renderUpcomingRow(e){let t=e.permanentSkip,o=e.tonightSkip;return s`
      <div class="upcoming-row ${e.isToday?"today":""} ${t?.isOn?"skipped":""}">
        <span class="up-date">${e.isToday?"TODAY":this._formatEventDate(e.date)}</span>
        <span class="up-icon">${e.icon}</span>
        <span class="up-name">${e.name}</span>
        <span class="up-badge">${e.category}</span>
        <span class="up-chips">
          ${e.colors.map(a=>s`<span class="up-chip" style="background:${a}"></span>`)}
        </span>
        ${e.isToday&&!t?.isOn&&!o?.isOn?s`<button
              class="up-action-btn ${e.isPicked?"active":""}"
              @click=${()=>this._setTonightPick(e.name)}
              title=${e.isPicked?"Clear -- resume split":"Pick this event tonight"}
            >
              ${e.isPicked?"\u2605":"\u2606"}
            </button>`:b}
        <button
          class="up-action-btn ${e.overrideColors?"active":""}"
          @click=${()=>this._openColorModal(e)}
          title=${e.overrideColors?"Customized -- click to edit":"Customize colors for this event"}
        >
          🎨
        </button>
        ${o?s`<button
              class="up-action-btn ${o.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(o.entityId,o.isOn)}
              title=${o.isOn?"Skipped tonight -- click to restore":"Skip for tonight only (resets at midnight)"}
            >
              🌙
            </button>`:b}
        ${t?s`<button
              class="up-action-btn ${t.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(t.entityId,t.isOn)}
              title=${t.isOn?"Re-enable -- this event will run again":"Permanently skip this event"}
            >
              ${t.isOn?"\u2298":"\u25CB"}
            </button>`:b}
      </div>
    `}_renderSkipChip(e){return s`
      <button
        class="chip ${e.isOn?"skipped":""}"
        @click=${()=>this._toggleSwitch(e.entityId,e.isOn)}
        title=${e.isOn?"Skipped -- click to restore":"Click to skip"}
      >
        ${e.eventName}
      </button>
    `}_renderOrb(e,t){let o=e.currentColors[0],a=e.currentColors.length>=Z,m=o?`background: radial-gradient(circle at 38% 30%, rgba(255,255,255,.45) 0%, ${o} 45%, rgba(0,0,0,.5) 100%); box-shadow: 0 0 ${t==="full"?"24px":"12px"} ${F(o,.627)}, 0 0 ${t==="full"?"46px":"23px"} ${F(o,.208)};`:"";return s`<div class="orb ${t} ${a?"spinning":""}" style=${m}></div>`}_renderLightGrid(e){return e.lights.length===0?s`<div class="empty-state">
        <p>No lights configured yet.</p>
        <p class="muted">Add a light from ChromaCal's settings to see it here.</p>
      </div>`:s`<section class="light-grid ${this.narrow?"narrow":""}">
      ${e.lights.map(t=>this._renderLightCard(t))}
    </section>`}_renderLightCard(e){if(this.narrow)return s`
        <div class="light-card compact">
          ${this._renderOrb(e,"compact")}
          <div class="compact-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline compact">${e.currentEventName??"\u2014"}</span>
          </div>
        </div>
      `;let t=D(e,new Date().getHours()+new Date().getMinutes()/60);return s`
      <div class="light-card">
        <div class="card-top">
          ${this._renderOrb(e,"full")}
          <div class="card-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline">${e.currentEventName??"No active event"}</span>
            ${e.currentStart&&e.currentEnd?s`<span class="event-time-range"
                  >${e.currentStart}&ndash;${e.currentEnd}</span
                >`:b}
          </div>
          ${e.forceWhiteEntityId?s`<button
                class="force-white-btn"
                @click=${()=>this._pressButton(e.forceWhiteEntityId)}
              >
                Force White
              </button>`:b}
        </div>
        ${e.segments.length>0?s`<div class="timeline-wrapper">
              <div class="timeline">
                ${e.segments.map(o=>{let{leftPct:a,widthPct:m}=U(o.startTime,o.endTime),y=o.name===e.currentEventName;return s`<div
                    class="timeline-seg ${y?"current":""}"
                    style="left:${a}%; width:${m}%; background:${o.colors[0]??"var(--cc-s2)"}"
                    title="${o.name} (${o.startTime}–${o.endTime})"
                  ></div>`})}
              </div>
              <div class="timeline-marks">
                ${t.map(o=>s`
                    <div class="tl-mark" style="left:${o.leftPct}%">
                      <div class="tl-mark-line"></div>
                      ${o.bare?b:s`<span class="tl-mark-lbl ${o.emphasize?"hl":""}"
                              >${o.label}</span
                            ><span class="tl-mark-lbl ${o.emphasize?"hl":""}">${o.time}</span>`}
                    </div>
                  `)}
              </div>
            </div>`:b}
      </div>
    `}};l.MAX_COLORS=6,l.styles=[L,A,_`
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

      /* Link out to Settings > Devices & Services > ChromaCal -- not a
         new settings surface, just discoverability for the Reconfigure/
         subentry flows that live there (see the Phase 8 plan). */
      .settings-link {
        color: var(--cc-muted);
        font-size: 13px;
        text-decoration: none;
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 6px 12px;
      }

      .settings-link:hover {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
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
        /* Unlike .event-name-headline, this one truncates instead of
           wrapping -- it's the quiet label, not the thing worth a second
           line. Found live in a real Sections-view dashboard column
           (narrower than the light-grid's own 300px minmax): a longer
           light name wrapped to two lines here, making that row visibly
           taller than its neighbors instead of staying a compact single
           line -- exactly the readability check a DOM-only pass wouldn't
           have caught. */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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

      .control-btn-primary {
        background: var(--cc-accent);
        color: var(--cc-s1);
        border-color: var(--cc-accent);
      }

      .control-btn-primary:hover:not(:disabled) {
        color: var(--cc-s1);
        opacity: 0.9;
      }

      .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }

      .modal-dialog {
        background: var(--cc-bg);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius);
        padding: 20px;
        width: min(420px, 90vw);
        max-height: 85vh;
        overflow-y: auto;
      }

      .modal-dialog h3 {
        margin: 0 0 4px;
      }

      .modal-event-name {
        color: var(--cc-muted);
        margin: 0 0 16px;
      }

      .modal-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        min-height: 32px;
        margin-bottom: 16px;
      }

      .modal-chip-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
      }

      .modal-chip {
        display: block;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 1px solid var(--cc-border);
      }

      .modal-chip-btns {
        display: flex;
        gap: 2px;
      }

      .chip-move-btn {
        background: none;
        border: 1px solid var(--cc-border);
        border-radius: 4px;
        color: var(--cc-muted);
        cursor: pointer;
        font-size: 11px;
        line-height: 1;
        width: 20px;
        height: 20px;
      }

      .chip-move-btn:hover:not(:disabled) {
        border-color: var(--cc-accent);
        color: var(--cc-accent);
      }

      .chip-move-btn:disabled {
        opacity: 0.35;
        cursor: default;
      }

      .chip-remove-btn:hover:not(:disabled) {
        border-color: var(--cc-red);
        color: var(--cc-red);
      }

      .modal-add-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
      }

      .modal-add-row input[type="color"] {
        width: 40px;
        height: 36px;
        padding: 0;
        border: 1px solid var(--cc-border);
        border-radius: 6px;
        background: none;
        cursor: pointer;
      }

      .modal-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
      }

      .modal-actions-right {
        display: flex;
        gap: 10px;
      }

      /* ── Compact card mode (ChromaCalCard) -- <ha-card> supplies the
         chrome (background/border/radius/elevation), just needs its own
         content padding; .light-grid/.light-card.compact are unchanged
         from the panel's own narrow-mode styles above. ── */
      .card-content {
        padding: 0 16px 16px;
      }
    `],u([E({attribute:!1})],l.prototype,"hass",2),u([E({type:Boolean})],l.prototype,"narrow",2),u([E({attribute:!1})],l.prototype,"panel",2),u([f()],l.prototype,"_themePreset",2),u([f()],l.prototype,"_skipFilter",2),u([f()],l.prototype,"_manageSkipsOpen",2),u([f()],l.prototype,"_controlsOpen",2),u([f()],l.prototype,"_houseViewOpen",2),u([f()],l.prototype,"_colorModalEvent",2),u([f()],l.prototype,"_colorModalColors",2),u([f()],l.prototype,"_colorModalPickerValue",2),l=u([C("chromacal-panel")],l);var S=class extends l{constructor(){super(),this.narrow=!0}setConfig(c){}static getStubConfig(){return{}}getCardSize(){return this.hass?Math.max(1,k(this.hass).lights.length):1}getGridOptions(){return{rows:this.hass?Math.max(1,k(this.hass).lights.length):1,columns:6,min_rows:1}}render(){if(!this.hass)return b;let c=k(this.hass);return s`
      <ha-card header="ChromaCal">
        <div class="card-content">${this._renderLightGrid(c)}</div>
      </ha-card>
    `}};S=u([C("chromacal-card")],S);window.customCards=window.customCards||[];window.customCards.push({type:"chromacal-card",name:"ChromaCal",description:"Compact status for your ChromaCal lights."});export{S as ChromaCalCard,l as ChromaCalPanel};

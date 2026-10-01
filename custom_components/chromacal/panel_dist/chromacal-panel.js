import{a as M,b as s,c as u,d as W,e as z,f as T,g as y}from"./chunk-5VH4SVWE.js";import{a as f}from"./chunk-JFKSI6I7.js";function Z(o){return{name:o.name,eventType:o.event_type,colors:o.colors,icon:o.icon,startTime:o.start_time,endTime:o.end_time}}function ee(o){return Object.values(o.entities).filter(c=>c.platform==="chromacal").map(c=>c.entity_id)}function te(o){return o.split(".",1)[0]}function $(o){let c=ee(o),e={saluteEntityId:null,saluteRunning:!1,catchUpEntityId:null,stopEntityId:null,emergencyEntityId:null,emergencyOn:!1},t=new Map,n=new Map,i=[],d=[],v=null,w=null;for(let r of c){let b=o.states[r];if(!b)continue;let g=b.attributes,l=te(r);if(l==="button"){let _=g.role;_==="salute"?(e.saluteEntityId=r,e.saluteRunning=!!g.running):_==="catch_up_sync"?e.catchUpEntityId=r:_==="stop"?e.stopEntityId=r:_==="force_white"&&typeof g.light_entity=="string"&&n.set(g.light_entity,r);continue}if(l==="switch"){let _=g.role;if(_==="emergency_mode")e.emergencyEntityId=r,e.emergencyOn=b.state==="on";else if(_==="skip"&&typeof g.event_name=="string"){let H={entityId:r,eventName:g.event_name,isOn:b.state==="on"};g.scope==="tonight"?i.push(H):d.push(H)}continue}l==="sensor"&&(g.role==="upcoming_events"?v=r:g.role==="house_view"?w=r:typeof g.light_entity=="string"&&t.set(g.light_entity,r))}let x=[];for(let[r,b]of t){let g=o.states[b],l=g?.attributes??{},_=l.light_name??r;x.push({lightEntity:r,lightName:_,scheduleEntityId:b,forceWhiteEntityId:n.get(r)??null,currentEventName:g?.state||null,currentEventType:l.event_type??null,currentColors:l.colors??[],currentIcon:l.icon??null,currentStart:l.start_time??null,currentEnd:l.end_time??null,segments:(l.segments??[]).map(Z),sunsetHour:l.sunset_hour??null,scheduleEndTime:l.schedule_end_time??null,fadeIn:l.fade_in??null,fadeOut:l.fade_out??null,warmwhiteTime:l.warmwhite_time??null,warmwhiteEnabled:l.warmwhite_enabled??!1,verifyEnabled:l.verify_enabled??!1,verifyOffEnabled:l.verify_off_enabled??!1,sunsetFadeEnabled:l.sunset_fade_enabled??!1,sunsetFadeOffsetMin:l.sunset_fade_offset_min??null,overrideSource:l.override_source??null,verifyResult:l.verify_result??null,verifyCheckedAt:l.verify_checked_at??null,verifyAttemptsUsed:l.verify_attempts_used??null})}x.sort((r,b)=>r.lightName.localeCompare(b.lightName)),i.sort((r,b)=>r.eventName.localeCompare(b.eventName)),d.sort((r,b)=>r.eventName.localeCompare(b.eventName));let m=new Map(d.map(r=>[r.eventName,r])),a=new Map(i.map(r=>[r.eventName,r])),h=v?o.states[v]?.attributes:void 0,I=h?.events??[],Y=h?.tonight_pick??null,K=h?.color_overrides??{},J=I.map(r=>({date:r.date,name:r.name,category:r.category,eventType:r.event_type,icon:r.icon,colors:r.colors,isToday:r.is_today,isPersonalRange:r.is_personal_range,permanentSkip:m.get(r.name)??null,tonightSkip:r.is_today?a.get(r.name)??null:null,isPicked:r.is_today&&Y===r.name,overrideColors:K[r.name]??null})),R=w?o.states[w]?.attributes:void 0,Q={mode:R?.mode??"2d",path:R?.path??"",markers:(R?.markers??[]).map(r=>({id:r.id,mode:r.mode,x:r.x,y:r.y,z:r.z,lightEntity:r.light_entity}))};return{globals:e,lights:x,tonightSkips:i,permanentSkips:d,upcomingEvents:J,houseView:Q}}var P=M`
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
`,L=["native","daylight","twilight","scifi","mono"],V={native:"Match dashboard theme",daylight:"Daylight",twilight:"Twilight",scifi:"Sci-Fi",mono:"Mono"},F=M`
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
`;function U(o){let[c,e]=o.split(":").map(Number);return c*60+e}function D(o){return o>=960?o:o+1440}function E(o){return D(Math.round(o*60))}function k(o){return D(U(o))}function N(o){return Math.max(0,Math.min(100,(o-960)/960*100))}function B(o,c){let e=N(k(o)),t=N(k(c));return{leftPct:e,widthPct:Math.max(0,t-e)}}function S(o){let c=Math.round(o*60)%1440,e=Math.floor(c/60),t=c%60;return`${String(e).padStart(2,"0")}:${String(t).padStart(2,"0")}`}function A(o,c){if(c===null)return null;let e=k(c)-E(o);if(e<=0)return null;let t=Math.floor(e/60),n=e%60;return t>0?`${t}h ${n}m`:`${n}m`}function G(o,c){let e=((U(o)+c)%1440+1440)%1440,t=Math.floor(e/60),n=e%60;return`${String(t).padStart(2,"0")}:${String(n).padStart(2,"0")}`}function O(o){if(o<=0)return"0s";let c=Math.floor(o/60),e=o%60;return c>0?`${c}m${e>0?` ${e}s`:""}`:`${e}s`}function j(o,c){let e=E(c),t=[],n=o.segments[o.segments.length-1];if(n){let a=k(n.endTime),h=o.scheduleEndTime!==null?k(o.scheduleEndTime):null;h!==null&&a<h?(t.push({label:"WARM",time:n.endTime,windowMinutes:a,emphasize:!1,priority:0}),t.push({label:"OFF",time:o.scheduleEndTime,windowMinutes:h,emphasize:!0,priority:0})):t.push({label:"OFF",time:n.endTime,windowMinutes:a,emphasize:!0,priority:0})}if(t.push({label:"NOW",time:S(c),windowMinutes:e,emphasize:!1,priority:1}),o.sunsetHour!==null){let a=E(o.sunsetHour);a>e&&t.push({label:"SUNSET",time:S(o.sunsetHour),windowMinutes:a,emphasize:!1,priority:2})}let i=o.segments[0];if(i){let a=k(i.startTime);a>e&&t.push({label:"COLORS",time:i.startTime,windowMinutes:a,emphasize:!1,priority:2})}let d=9,v=t.map(a=>({...a,leftPct:N(a.windowMinutes)})),w=[...v].sort((a,h)=>a.priority-h.priority||a.windowMinutes-h.windowMinutes),x=[],m=new Map;for(let a of w){let h=a.priority>0&&x.some(I=>Math.abs(a.leftPct-I)<d);m.set(a,h),h||x.push(a.leftPct)}return v.sort((a,h)=>a.windowMinutes-h.windowMinutes).map(a=>({label:a.label,time:a.time,windowMinutes:a.windowMinutes,leftPct:a.leftPct,emphasize:a.emphasize,bare:m.get(a)??!1}))}var X="chromacal-panel-theme-preset",oe=5,ne={force_white:"Force White",salute:"21 Gun Salute",emergency:"Emergency Mode"};function q(o,c){let e=o.replace("#",""),t=parseInt(e,16),n=t>>16&255,i=t>>8&255,d=t&255;return`rgba(${n}, ${i}, ${d}, ${c})`}var p=class extends W{constructor(){super(...arguments);this.narrow=!1;this._themePreset="native";this._skipFilter="";this._manageSkipsOpen=!1;this._controlsOpen=!1;this._houseViewOpen=!1;this._colorModalEvent=null;this._colorModalColors=[];this._colorModalPickerValue="#ffffff";this._clockText=""}connectedCallback(){super.connectedCallback();let e=localStorage.getItem(X);e&&L.includes(e)&&(this._themePreset=e),this._applyThemeAttribute(),this._clockText=new Date().toLocaleTimeString(),this._clockInterval=setInterval(()=>{this._clockText=new Date().toLocaleTimeString()},1e3)}disconnectedCallback(){super.disconnectedCallback(),clearInterval(this._clockInterval)}_panelVersion(){let t=this.panel?.config?._panel_custom?.module_url;if(!t)return"";try{return new URL(t,window.location.origin).searchParams.get("v")??""}catch{return""}}_applyThemeAttribute(){this._themePreset==="native"?this.removeAttribute("data-theme"):this.setAttribute("data-theme",this._themePreset)}_onThemeChange(e){let t=e.target.value;this._themePreset=t,localStorage.setItem(X,t),this._applyThemeAttribute()}_callService(e,t,n){n&&this.hass.callService(e,t,{entity_id:n})}_pressButton(e){this._callService("button","press",e)}_toggleSwitch(e,t){this._callService("switch",t?"turn_off":"turn_on",e)}_onHouseViewToggle(e){let t=e.target.open;this._houseViewOpen=t,t&&import("./house-view-BW6Y22GU.js")}_setTonightPick(e){this.hass.callService("chromacal","set_tonight_pick",{event_name:e})}_openColorModal(e){this._colorModalEvent=e.name,this._colorModalColors=[...e.overrideColors??e.colors]}_closeColorModal(){this._colorModalEvent=null,this._colorModalColors=[]}_addColorModalColor(){this._colorModalColors.length>=p.MAX_COLORS||(this._colorModalColors=[...this._colorModalColors,this._colorModalPickerValue])}_removeColorModalColor(e){this._colorModalColors=this._colorModalColors.filter((t,n)=>n!==e)}_moveColorModalColor(e,t){let n=e+t;if(n<0||n>=this._colorModalColors.length)return;let i=[...this._colorModalColors];[i[e],i[n]]=[i[n],i[e]],this._colorModalColors=i}_saveColorOverride(){!this._colorModalEvent||this._colorModalColors.length===0||(this.hass.callService("chromacal","set_color_override",{event_name:this._colorModalEvent,colors:this._colorModalColors}),this._closeColorModal())}_resetColorOverride(){this._colorModalEvent&&(this.hass.callService("chromacal","reset_color_override",{event_name:this._colorModalEvent}),this._closeColorModal())}render(){if(!this.hass)return u;let e=$(this.hass);return s`
      <div class="root">
        <div class="hero">
          <h1 class="hero-brand">
            <img class="hero-logo" src="/chromacal_static/brand/icon.png" alt="" />
            <span class="logo-c" style="color:#2563EB">C</span
            ><span class="logo-c" style="color:#CC2200">H</span
            ><span class="logo-c" style="color:#D4750A">R</span
            ><span class="logo-c" style="color:#2ECC71">O</span
            ><span class="logo-c" style="color:#CC44FF">M</span
            ><span class="logo-c" style="color:#007E88">A</span
            ><span class="logo-c" style="color:#E8B84B">C</span
            ><span class="logo-c" style="color:#CC3377">A</span
            ><span class="logo-c" style="color:#00C8E8">L</span>
          </h1>
          <div class="hero-line1">The whole world celebrates with light.</div>
          <div class="hero-line2">Now you can too.</div>
        </div>

        <header>
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
                ${L.map(t=>s`<option value=${t} ?selected=${t===this._themePreset}>
                    ${V[t]}
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
                  ></chromacal-house-view>`:u}
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

        ${this._colorModalEvent?this._renderColorModal():u}

        <footer>
          <strong>Honor your heritage. Light your home.</strong> ·
          ChromaCal <span>v${this._panelVersion()}</span> ·
          <a href="https://github.com/TheRealApollyon/chromacal" target="_blank" rel="noopener">GitHub</a> ·
          <span>${this._clockText}</span>
        </footer>
      </div>
    `}_renderColorModal(){let e=this._colorModalEvent,t=this._colorModalColors;return s`
      <div class="modal-overlay" @click=${this._closeColorModal}>
        <div class="modal-dialog" @click=${n=>n.stopPropagation()}>
          <h3>Customize colors</h3>
          <p class="modal-event-name">${e}</p>

          <div class="modal-chip-row">
            ${t.length===0?s`<p class="muted">No colors -- add at least one below.</p>`:t.map((n,i)=>s`
                    <div class="modal-chip-item">
                      <span class="modal-chip" style="background:${n}" title=${n}></span>
                      <div class="modal-chip-btns">
                        <button
                          class="chip-move-btn"
                          ?disabled=${i===0}
                          @click=${()=>this._moveColorModalColor(i,-1)}
                          title="Move left"
                        >
                          ‹
                        </button>
                        <button
                          class="chip-move-btn chip-remove-btn"
                          @click=${()=>this._removeColorModalColor(i)}
                          title="Remove"
                        >
                          ×
                        </button>
                        <button
                          class="chip-move-btn"
                          ?disabled=${i===t.length-1}
                          @click=${()=>this._moveColorModalColor(i,1)}
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
              @input=${n=>this._colorModalPickerValue=n.target.value}
            />
            <button
              class="control-btn"
              ?disabled=${t.length>=p.MAX_COLORS}
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
    `}_formatEventDate(e){return new Date(`${e}T00:00:00`).toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"})}_renderUpcomingRow(e){let t=e.permanentSkip,n=e.tonightSkip;return s`
      <div class="upcoming-row ${e.isToday?"today":""} ${t?.isOn?"skipped":""}">
        <span class="up-date">${e.isToday?"TODAY":this._formatEventDate(e.date)}</span>
        <span class="up-icon">${e.icon}</span>
        <span class="up-name">${e.name}</span>
        <span class="up-badge">${e.category}</span>
        <span class="up-chips">
          ${e.colors.map(i=>s`<span class="up-chip" style="background:${i}"></span>`)}
        </span>
        ${e.isToday&&!t?.isOn&&!n?.isOn?s`<button
              class="up-action-btn ${e.isPicked?"active":""}"
              @click=${()=>this._setTonightPick(e.name)}
              title=${e.isPicked?"Clear -- resume split":"Pick this event tonight"}
            >
              ${e.isPicked?"\u2605":"\u2606"}
            </button>`:u}
        <button
          class="up-action-btn ${e.overrideColors?"active":""}"
          @click=${()=>this._openColorModal(e)}
          title=${e.overrideColors?"Customized -- click to edit":"Customize colors for this event"}
        >
          🎨
        </button>
        ${n?s`<button
              class="up-action-btn ${n.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(n.entityId,n.isOn)}
              title=${n.isOn?"Skipped tonight -- click to restore":"Skip for tonight only (resets at midnight)"}
            >
              🌙
            </button>`:u}
        ${t?s`<button
              class="up-action-btn ${t.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(t.entityId,t.isOn)}
              title=${t.isOn?"Re-enable -- this event will run again":"Permanently skip this event"}
            >
              ${t.isOn?"\u2298":"\u25CB"}
            </button>`:u}
      </div>
    `}_renderSkipChip(e){return s`
      <button
        class="chip ${e.isOn?"skipped":""}"
        @click=${()=>this._toggleSwitch(e.entityId,e.isOn)}
        title=${e.isOn?"Skipped -- click to restore":"Click to skip"}
      >
        ${e.eventName}
      </button>
    `}_renderOrb(e,t){let n=e.currentColors[0],i=e.currentColors.length>=oe,d=n?`background: radial-gradient(circle at 38% 30%, rgba(255,255,255,.45) 0%, ${n} 45%, rgba(0,0,0,.5) 100%); box-shadow: 0 0 ${t==="full"?"24px":"12px"} ${q(n,.627)}, 0 0 ${t==="full"?"46px":"23px"} ${q(n,.208)};`:"";return s`<div class="orb ${t} ${i?"spinning":""}" style=${d}></div>`}_renderLightGrid(e){return e.lights.length===0?s`<div class="empty-state">
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
      `;let t=new Date().getHours()+new Date().getMinutes()/60,n=j(e,t);return s`
      <div class="light-card">
        <div class="card-top">
          ${this._renderOrb(e,"full")}
          <div class="card-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline">${e.currentEventName??"No active event"}</span>
            ${e.currentStart&&e.currentEnd?s`<span class="event-time-range"
                  >${e.currentStart}&ndash;${e.currentEnd}</span
                >`:u}
          </div>
          ${e.forceWhiteEntityId?s`<button
                class="force-white-btn"
                @click=${()=>this._pressButton(e.forceWhiteEntityId)}
              >
                Force White
              </button>`:u}
        </div>
        ${e.segments.length>0?s`<div class="timeline-wrapper">
              <div class="timeline">
                ${e.segments.map(i=>{let{leftPct:d,widthPct:v}=B(i.startTime,i.endTime),w=i.name===e.currentEventName;return s`<div
                    class="timeline-seg ${w?"current":""}"
                    style="left:${d}%; width:${v}%; background:${i.colors[0]??"var(--cc-s2)"}"
                    title="${i.name} (${i.startTime}–${i.endTime})"
                  ></div>`})}
              </div>
              <div class="timeline-marks">
                ${n.map(i=>s`
                    <div class="tl-mark" style="left:${i.leftPct}%">
                      <div class="tl-mark-line"></div>
                      ${i.bare?u:s`<span class="tl-mark-lbl ${i.emphasize?"hl":""}"
                              >${i.label}</span
                            ><span class="tl-mark-lbl ${i.emphasize?"hl":""}">${i.time}</span>`}
                    </div>
                  `)}
              </div>
            </div>
            ${e.fadeOut!==null&&e.fadeOut>0?s`<div class="tl-fade-row">
                  <span class="tl-fi-in"></span>
                  <span class="tl-fi-out" title="Lights dim to off over this duration"
                    >◂ ${O(e.fadeOut)} dim out</span
                  >
                </div>`:u}`:u}
        ${this._renderScheduleList(e,t)}
      </div>
    `}_renderScheduleList(e,t){let n=E(t),i=(m,a)=>({kind:"point",label:m,time:a,done:n>=k(a)}),d=[];e.sunsetHour!==null&&d.push(i("Lights On",S(e.sunsetHour))),e.sunsetFadeEnabled&&e.sunsetHour!==null&&e.sunsetFadeOffsetMin!==null&&d.push(i("HA Fade-In Starts",S(e.sunsetHour-e.sunsetFadeOffsetMin/60)));let v=e.segments[0];v&&d.push(i("ChromaCal Colors Fire",v.startTime)),e.fadeIn!==null&&d.push({kind:"feature",label:"Color Fade-In",value:O(e.fadeIn),isOn:e.fadeIn>0});for(let m of e.segments){let a=k(m.startTime),h=k(m.endTime);d.push({kind:"segment",label:m.name,time:`${m.startTime}\u2013${m.endTime}`,done:n>=h,active:n>=a&&n<h,color:m.colors[0]??null})}e.warmwhiteEnabled&&e.warmwhiteTime!==null&&d.push(i("Warm White",e.warmwhiteTime)),d.push({kind:"feature",label:"Warm White",value:e.warmwhiteTime??"\u2014",isOn:e.warmwhiteEnabled}),e.fadeOut!==null&&d.push({kind:"feature",label:"Dim Out",value:O(e.fadeOut),isOn:e.fadeOut>0}),e.scheduleEndTime!==null&&d.push(i("Lights Off",e.scheduleEndTime)),d.push({kind:"feature",label:"Verify Off",value:e.scheduleEndTime!==null?G(e.scheduleEndTime,30):"\u2014",isOn:e.verifyOffEnabled});let w=e.warmwhiteEnabled?A(t,e.warmwhiteTime):null,x=A(t,e.scheduleEndTime);return s`
      <div class="schedule-list">
        ${e.overrideSource?s`<div class="schedule-override-banner">
              ${ne[e.overrideSource]??e.overrideSource} active — overriding
              the schedule below
            </div>`:u}
        ${w||x?s`<div class="schedule-countdowns">
              ${w?s`<span>${w} until ${e.warmwhiteTime}</span>`:u}
              ${x?s`<span>${x} until ${e.scheduleEndTime}</span>`:u}
            </div>`:u}
        ${d.map(m=>this._renderScheduleRow(m))}
      </div>
    `}_renderScheduleRow(e){if(e.kind==="feature")return s`<div class="sched-row sched-feat">
        <span class="sched-sep">──</span>
        <span class="sched-feat-lbl">${e.label}</span>
        <span class="sched-feat-val">${e.value}</span>
        <span class="feat-tog ${e.isOn?"on":""}">${e.isOn?"ON":"OFF"}</span>
      </div>`;let t=e.kind==="segment"&&e.active,n=e.done?"\u2705":t?"\u25B6":"\u25CB";return s`<div class="sched-row ${t?"active":""}">
      <span class="sched-row-icon">${n}</span>
      ${e.kind==="segment"&&e.color?s`<span class="sched-row-swatch" style="background:${e.color}"></span>`:u}
      <span class="sched-row-label">${e.label}</span>
      <span class="sched-row-time">${e.time}</span>
      ${t?s`<span class="sched-now">◀ NOW</span>`:u}
    </div>`}};p.MAX_COLORS=6,p.styles=[P,F,M`
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

      /* ── Hero (v1.1.0's real logo/wordmark/tagline, ported verbatim --
         see dist/chromacal.html's .hero/.hero-brand/.logo-c/.hero-line1/2
         at the v1.1.0 tag) -- full-bleed within the panel's own padded
         bounds via negative margins, matching v1's edge-to-edge look. */
      .hero {
        text-align: center;
        padding: 20px 16px 14px;
        margin: -16px -16px 16px;
        border-bottom: 1.5px solid var(--cc-border);
        background: var(--cc-s1);
      }

      .hero-logo {
        height: 36px;
        width: 36px;
        vertical-align: middle;
        margin-right: 8px;
      }

      .hero-brand {
        font-family: var(--cc-font);
        font-size: clamp(22px, 5vw, 42px);
        font-weight: 900;
        letter-spacing: 6px;
      }

      .logo-c {
        display: inline-block;
        transition: opacity 0.3s;
        text-shadow: 0 0 16px currentColor;
      }

      .hero-brand:hover .logo-c {
        opacity: 0.8;
      }

      .hero-line1 {
        font-family: var(--cc-font);
        font-size: clamp(13px, 2.8vw, 20px);
        font-weight: 700;
        letter-spacing: 0.5px;
        color: var(--cc-text);
        line-height: 1.3;
      }

      .hero-line2 {
        font-family: var(--cc-font);
        font-size: clamp(12px, 2.4vw, 17px);
        font-weight: 600;
        color: var(--cc-accent);
        margin-top: 3px;
      }

      footer {
        text-align: center;
        padding: 14px 16px;
        color: var(--cc-muted);
        font-size: 13px;
        border-top: 1.5px solid var(--cc-border);
        margin: 16px -16px -16px;
      }

      footer a {
        color: var(--cc-text);
        text-decoration: none;
        font-weight: 700;
        border-bottom: 1.5px solid var(--cc-border);
        padding-bottom: 1px;
        transition: color 0.2s, border-color 0.2s;
      }

      footer a:hover {
        color: var(--cc-accent);
        border-color: var(--cc-accent);
      }

      header {
        display: flex;
        align-items: center;
        /* Right-aligned, not space-between -- the old <h1>ChromaCal</h1>
           that used to occupy the other flex slot moved into .hero above;
           the toolbar itself is unchanged, still exactly where it was. */
        justify-content: flex-end;
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

      /* ── Tonight's Schedule (Plan B) -- countdown lines + phase list,
         below the timeline bar above. ── */
      .schedule-list {
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid var(--cc-border);
      }

      .schedule-override-banner {
        background: color-mix(in srgb, var(--cc-red) 15%, transparent);
        border: 1px solid var(--cc-red);
        color: var(--cc-red);
        border-radius: var(--cc-radius);
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
      }

      .schedule-countdowns {
        display: flex;
        gap: 16px;
        color: var(--cc-muted);
        font-size: 12px;
        margin-bottom: 10px;
      }

      .sched-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 5px 0;
        font-size: 13px;
      }

      .sched-row.active {
        color: var(--cc-accent);
        font-weight: 600;
      }

      .sched-row-icon {
        width: 16px;
        flex-shrink: 0;
        text-align: center;
        color: var(--cc-muted);
      }

      .sched-row.active .sched-row-icon {
        color: var(--cc-accent);
      }

      .sched-row-swatch {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .sched-row-label {
        flex: 1;
        min-width: 0;
      }

      .sched-row-time {
        color: var(--cc-muted);
        font-size: 12px;
        flex-shrink: 0;
      }

      .sched-row.active .sched-row-time {
        color: inherit;
      }

      /* "◀ NOW" tag on whichever row is currently active -- v1's
         .sched-now, same green/weight/letter-spacing. */
      .sched-now {
        font-size: 10px;
        color: var(--cc-green);
        font-weight: 700;
        letter-spacing: 0.3px;
        flex-shrink: 0;
      }

      /* Feature-toggle rows (Color Fade-In, Warm White, Dim Out, Verify
         Off) -- v1's .sched-feat/.sched-sep/.sched-feat-lbl/.sched-feat-val/
         .feat-tog, adapted onto --cc-* tokens. The pill is a static span,
         not a button -- see ScheduleRow's docstring for why it isn't
         clickable here. */
      .sched-feat {
        background: var(--cc-s2);
        border-top: none !important;
        padding: 4px 6px;
      }

      .sched-sep {
        font-size: 11px;
        color: var(--cc-muted);
        width: 16px;
        flex-shrink: 0;
        text-align: center;
      }

      .sched-feat-lbl {
        flex: 1;
        color: var(--cc-muted);
        font-size: 12px;
        font-weight: 400;
      }

      .sched-feat-val {
        font-size: 11px;
        color: var(--cc-text);
        font-family: monospace;
        flex-shrink: 0;
        opacity: 0.65;
      }

      .feat-tog {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 3px 10px;
        border-radius: 10px;
        flex-shrink: 0;
        border: 1.5px solid var(--cc-border);
        background: transparent;
        color: var(--cc-muted);
        min-width: 40px;
        text-align: center;
      }

      .feat-tog.on {
        border-color: var(--cc-green);
        color: var(--cc-green);
        background: color-mix(in srgb, var(--cc-green) 10%, transparent);
      }

      /* Dim-out annotation below the timeline bar -- v1's .tl-fade-row,
         a plain two-column flex row (the empty .tl-fi-in slot is kept for
         the same space-between layout v1 uses, even though v1 itself
         never populates it either). */
      .tl-fade-row {
        display: flex;
        justify-content: space-between;
        margin-top: 6px;
        min-height: 20px;
      }

      .tl-fi-out {
        font-size: 12px;
        color: var(--cc-accent2);
        font-weight: 500;
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
    `],f([T({attribute:!1})],p.prototype,"hass",2),f([T({type:Boolean})],p.prototype,"narrow",2),f([T({attribute:!1})],p.prototype,"panel",2),f([y()],p.prototype,"_themePreset",2),f([y()],p.prototype,"_skipFilter",2),f([y()],p.prototype,"_manageSkipsOpen",2),f([y()],p.prototype,"_controlsOpen",2),f([y()],p.prototype,"_houseViewOpen",2),f([y()],p.prototype,"_colorModalEvent",2),f([y()],p.prototype,"_colorModalColors",2),f([y()],p.prototype,"_colorModalPickerValue",2),f([y()],p.prototype,"_clockText",2),p=f([z("chromacal-panel")],p);var C=class extends p{constructor(){super(),this.narrow=!0}setConfig(c){}static getStubConfig(){return{}}getCardSize(){return this.hass?Math.max(1,$(this.hass).lights.length):1}getGridOptions(){return{rows:this.hass?Math.max(1,$(this.hass).lights.length):1,columns:6,min_rows:1}}render(){if(!this.hass)return u;let c=$(this.hass);return s`
      <ha-card header="ChromaCal">
        <div class="card-content">${this._renderLightGrid(c)}</div>
      </ha-card>
    `}};C=f([z("chromacal-card")],C);window.customCards=window.customCards||[];window.customCards.push({type:"chromacal-card",name:"ChromaCal",description:"Compact status for your ChromaCal lights."});export{C as ChromaCalCard,p as ChromaCalPanel};

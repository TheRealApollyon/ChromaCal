/**
 * House View: a 2D image or 3D model with light markers on it, ported
 * from v1's chromacal.html (its `#house-view` section, `initHouseView()`
 * onward). Real, non-cosmetic differences from that port, not silent
 * changes:
 *
 * - Three.js is current (0.185.x via npm/ESM, `three/addons/...`), not
 *   v1's classic-global r128 loaded via CDN <script> tags. Real breaking
 *   API surface since r128: `renderer.outputColorSpace`/
 *   `THREE.SRGBColorSpace` replaced `.outputEncoding`/`sRGBEncoding`, and
 *   `ColorManagement.enabled` now defaults to true -- confirmed against
 *   the real npm registry metadata and threejs.org's migration notes, not
 *   assumed from memory of the old API.
 * - This is its own custom element, dynamically import()-ed from
 *   chromacal-panel.ts only when House View is actually opened (see the
 *   esbuild.config.mjs comment) -- so Three.js's weight never ships to
 *   every dashboard page the way the always-loaded panel/card bundle
 *   does. It gets mounted/unmounted by the parent's own conditional
 *   render (not just CSS-hidden), so disconnectedCallback() below is a
 *   real cleanup boundary, not a nicety -- entered every time the user
 *   collapses the section, same as leaving the page. Skipping proper
 *   WebGL disposal here would leak a GPU context on every open/close
 *   cycle (browsers cap concurrent WebGL contexts at roughly 8-16), per
 *   three.js's own "How to dispose of objects" guidance.
 * - Markers sync from `hass`'s own reactive updates (Lit's normal render
 *   cycle already re-runs whenever hass changes), not v1's 10-second REST
 *   poll -- there's nothing to poll, hass already pushes this live. Also
 *   reads the light entity's own actual live state (on/off + rgb_color),
 *   not the schedule sensor's resolved event color -- those can diverge
 *   (Force White, Emergency Mode, a manually-toggled light), and "what
 *   does my house actually look like right now" is the entire point of
 *   this feature.
 * - Markers are keyed by a generated id + light_entity (assigned via
 *   services), not v1's list-position lightIndex -- see coordinator.py's
 *   CONF_HOUSE_VIEW_MARKERS docstring for why.
 */

import { LitElement, html, css, nothing, type PropertyValues } from "lit";
import { customElement, property, state, query } from "lit/decorators.js";

import type { HomeAssistant } from "./types";
import type { HouseViewMarker, HouseViewModel, LightCardModel } from "./grouping";

// Type-only -- erased at compile time, so this costs nothing at runtime
// and doesn't defeat the point of the dynamic import() below. The actual
// runtime module only loads when _ensureThree() actually runs.
import type * as THREE from "three";
import type { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import type { OrbitControls } from "three/addons/controls/OrbitControls.js";

const DOMAIN = "chromacal";
const DRAG_THRESHOLD_PX = 5; // matches v1's onViewerClick3D drag-vs-click distinction

function liveMarkerColor(hass: HomeAssistant, lightEntity: string | null): { color: string; isOn: boolean } {
  if (!lightEntity) return { color: "#888888", isOn: false };
  const state = hass.states[lightEntity];
  if (!state) return { color: "#888888", isOn: false };
  const isOn = state.state === "on";
  if (!isOn) return { color: "#333333", isOn: false };
  const rgb = state.attributes.rgb_color as number[] | undefined;
  return { color: rgb ? `rgb(${rgb.join(",")})` : "#f59e0b", isOn: true };
}

@customElement("chromacal-house-view")
export class ChromaCalHouseView extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ attribute: false }) model!: HouseViewModel;
  @property({ attribute: false }) lights: LightCardModel[] = [];

  @state() private _pathInput = "";
  @state() private _loadError: string | null = null;
  @state() private _loading = false;

  @query("#viewer-3d-host") private _viewer3dHost?: HTMLDivElement;

  // Three.js refs -- plain instance fields, not reactive @state: the
  // imperative scene graph/render loop must not be torn down and rebuilt
  // by Lit's own re-render cycle just because an unrelated property (like
  // a light turning on) changed. Same reasoning v1 had for keeping this
  // off its framework-free page's own re-render logic, just scoped to
  // this element instance instead of a module global now that this is a
  // real, potentially-multiply-instantiated custom element.
  private _threeMod: typeof THREE | null = null;
  private _GLTFLoaderCtor: typeof GLTFLoader | null = null;
  private _OrbitControlsCtor: typeof OrbitControls | null = null;
  private _scene: THREE.Scene | null = null;
  private _camera: THREE.PerspectiveCamera | null = null;
  private _renderer: THREE.WebGLRenderer | null = null;
  private _controls: OrbitControls | null = null;
  private _raycaster: THREE.Raycaster | null = null;
  private _model3d: THREE.Object3D | null = null;
  private _markerMeshes = new Map<string, THREE.Mesh>();
  private _animId: number | null = null;
  private _resizeObserver: ResizeObserver | null = null;
  private _pointerDownPos: { x: number; y: number } | null = null;
  private _loaded3dPath: string | null = null; // which path the current 3D scene was built from

  connectedCallback(): void {
    super.connectedCallback();
    this._pathInput = this.model?.path ?? "";
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this._disposeScene();
  }

  protected willUpdate(changed: PropertyValues<this>): void {
    if (changed.has("model") && this.model && !changed.get("model")) {
      // First time `model` arrives -- seed the path input from it.
      this._pathInput = this.model.path;
    }

    const previousModel = changed.get("model");
    if (previousModel && this.model && previousModel.mode !== this.model.mode) {
      // _loadError has no mode of its own -- there's one shared error
      // slot, matching the one shared path/mode this component already
      // has. Without this, a failed 3D load's error banner stays visible
      // above a since-successfully-loaded 2D image after switching tabs
      // (or vice versa) -- confirmed live: the error text is real, but
      // its *scope* wasn't, so it outlived the mode it was actually
      // about. Cleared here (reactively, whenever mode actually changes)
      // rather than only on the next load attempt, since a mode switch
      // with no load attempt yet (e.g. the path hasn't been re-entered)
      // must not still show the previous mode's stale failure.
      this._loadError = null;
    }
  }

  protected updated(changed: PropertyValues<this>): void {
    if (this.model?.mode === "3d" && this.model.path) {
      if (this._loaded3dPath !== this.model.path) {
        this._loadModel(this.model.path);
      } else if (changed.has("model")) {
        this._syncMarkerMeshes();
      }
    }
    if (changed.has("hass") && this.model?.mode === "3d") {
      this._updateLiveMarkerColors3d();
    }
  }

  private _callService(service: string, data: Record<string, unknown>): void {
    this.hass.callService(DOMAIN, service, data);
  }

  private _setHouseView(mode: "2d" | "3d", path: string): void {
    // Optimistic clear, ahead of the round trip through hass -- the
    // reactive clear in willUpdate() is the authoritative fix (also
    // covers a mode change arriving from outside this click, e.g.
    // another browser tab), but waiting for it here would leave the
    // previous mode's stale error banner flashing on screen for the
    // length of a full service-call/state-update round trip.
    if (this.model && mode !== this.model.mode) this._loadError = null;
    // Every explicit user action that can point 3D mode at a (possibly
    // unchanged) path -- the mode toggle and the Load button both funnel
    // through here -- forces exactly one fresh load attempt by clearing
    // the reload guard. This is the ONLY place that clears it after a
    // failure; _loadModel's own catch block deliberately does not (see
    // its comment), so a persistently-broken path fails once per user
    // click, never in an automatic unbounded loop.
    this._loaded3dPath = null;
    this._callService("set_house_view", { mode, path });
  }

  private _addMarker(mode: "2d" | "3d", x: number, y: number, z: number | null): void {
    this._callService("add_house_marker", { mode, x, y, z: z ?? undefined });
  }

  private _assignMarker(markerId: string, lightEntity: string): void {
    this._callService("assign_house_marker", {
      marker_id: markerId,
      light_entity: lightEntity || undefined,
    });
  }

  private _removeMarker(markerId: string): void {
    this._callService("remove_house_marker", { marker_id: markerId });
  }

  // ── 2D mode ─────────────────────────────────────────────────────
  private _onImageClick(e: MouseEvent): void {
    const img = e.currentTarget as HTMLImageElement;
    const rect = img.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    if (x < 0 || x > 1 || y < 0 || y > 1) return; // clicked the letterboxed area
    this._addMarker("2d", x, y, null);
  }

  private _onImageError(): void {
    this._loadError = `Could not load ${this.model.path} -- check the path and that the file is in your HA /www/ folder.`;
  }

  private _onImageLoad(): void {
    this._loadError = null;
  }

  // ── 3D mode ─────────────────────────────────────────────────────
  private async _ensureThree(): Promise<void> {
    if (this._threeMod) return;
    const [threeMod, gltfMod, controlsMod] = await Promise.all([
      import("three"),
      import("three/addons/loaders/GLTFLoader.js"),
      import("three/addons/controls/OrbitControls.js"),
    ]);
    this._threeMod = threeMod;
    this._GLTFLoaderCtor = gltfMod.GLTFLoader;
    this._OrbitControlsCtor = controlsMod.OrbitControls;
  }

  private async _loadModel(path: string): Promise<void> {
    this._loaded3dPath = path; // set eagerly -- guards against a second updated() re-entering mid-load
    this._loading = true;
    this._loadError = null;
    try {
      await this._ensureThree();
      const host = this._viewer3dHost;
      if (!host) return;
      this._initScene(host);
      await this._loadGltf(path);
      this._syncMarkerMeshes();
    } catch (e) {
      this._loadError = e instanceof Error ? e.message : "3D engine failed to load.";
      // Deliberately NOT resetting _loaded3dPath here. It's tempting --
      // otherwise clicking Load again with the exact same (now-fixed)
      // path looks like a no-op, since updated()'s reload check only
      // fires on an actual path change. But resetting it on every failure
      // makes updated() re-trigger this same failing load on the very
      // next unrelated reactive update (a hass tick, a marker sync) --
      // confirmed live: a genuinely-broken path fetched in an unbounded
      // loop, not just once. The retry-with-same-path case is instead
      // handled explicitly in _setHouseView() below, which is the single
      // chokepoint both the Load button and the mode toggle already funnel
      // through -- so a retry only ever happens in response to a real
      // user action, never automatically.
    } finally {
      this._loading = false;
    }
  }

  private _initScene(host: HTMLDivElement): void {
    this._disposeScene();
    const THREE = this._threeMod!;
    const w = host.clientWidth || 1;
    const h = host.clientHeight || 1;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0d1624);
    const camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 2000);
    camera.position.set(5, 5, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    // Explicit, not just relying on the current default -- three.js's
    // color-managed output defaults to sRGB as of the version this
    // targets, but v1's r128-era code predates that default entirely and
    // getting this wrong silently washes out marker/scene colors, not a
    // loud failure -- worth pinning explicitly rather than trusting an
    // upstream default to stay put.
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setSize(w, h);
    host.replaceChildren(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dir = new THREE.DirectionalLight(0xffffff, 0.7);
    dir.position.set(5, 10, 7);
    scene.add(dir);

    const controls = new this._OrbitControlsCtor!(camera, renderer.domElement);
    controls.enableDamping = true;

    renderer.domElement.addEventListener("pointerdown", (e) => {
      this._pointerDownPos = { x: e.clientX, y: e.clientY };
    });
    renderer.domElement.addEventListener("pointerup", (e) => {
      const down = this._pointerDownPos;
      this._pointerDownPos = null;
      if (down && Math.hypot(e.clientX - down.x, e.clientY - down.y) < DRAG_THRESHOLD_PX) {
        this._onCanvasClick(e);
      }
    });

    this._scene = scene;
    this._camera = camera;
    this._renderer = renderer;
    this._controls = controls;
    this._raycaster = new THREE.Raycaster();
    this._markerMeshes.clear();

    this._resizeObserver = new ResizeObserver(() => this._onResize());
    this._resizeObserver.observe(host);

    this._animate();
  }

  private _animate = (): void => {
    this._animId = requestAnimationFrame(this._animate);
    this._controls?.update();
    if (this._renderer && this._scene && this._camera) {
      this._renderer.render(this._scene, this._camera);
    }
  };

  private _onResize(): void {
    const host = this._viewer3dHost;
    if (!host || !this._renderer || !this._camera) return;
    const w = host.clientWidth || 1;
    const h = host.clientHeight || 1;
    this._camera.aspect = w / h;
    this._camera.updateProjectionMatrix();
    this._renderer.setSize(w, h);
  }

  private _loadGltf(path: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const loader = new this._GLTFLoaderCtor!();
      loader.load(
        path,
        (gltf) => {
          const THREE = this._threeMod!;
          if (this._model3d) this._scene?.remove(this._model3d);
          this._model3d = gltf.scene;
          this._scene?.add(this._model3d);

          const box = new THREE.Box3().setFromObject(this._model3d);
          const size = box.getSize(new THREE.Vector3());
          const center = box.getCenter(new THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z, 1);
          if (this._camera) {
            this._camera.position.set(center.x + maxDim, center.y + maxDim * 0.8, center.z + maxDim);
            this._camera.far = maxDim * 20;
            this._camera.updateProjectionMatrix();
          }
          if (this._controls) {
            this._controls.target.copy(center);
            this._controls.update();
          }
          resolve();
        },
        undefined,
        (err) => reject(err instanceof Error ? err : new Error("Could not load the 3D model.")),
      );
    });
  }

  private _onCanvasClick(e: PointerEvent): void {
    if (!this._model3d || !this._renderer || !this._raycaster || !this._camera || !this._threeMod) return;
    const rect = this._renderer.domElement.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    this._raycaster.setFromCamera(new this._threeMod.Vector2(x, y), this._camera);
    const hits = this._raycaster.intersectObject(this._model3d, true);
    if (!hits.length) return;
    const p = hits[0].point;
    this._addMarker("3d", p.x, p.y, p.z);
  }

  /** Reconciles marker meshes against `this.model.markers` -- called
   * after a (re)load and whenever the marker list itself changes (add/
   * remove/assign all come back through `model` via hass's own reactive
   * update, not a direct mutation here). */
  private _syncMarkerMeshes(): void {
    const THREE = this._threeMod;
    if (!THREE || !this._scene) return;
    const markers3d = (this.model?.markers ?? []).filter((m) => m.mode === "3d");
    const liveIds = new Set(markers3d.map((m) => m.id));

    for (const [id, mesh] of this._markerMeshes) {
      if (!liveIds.has(id)) {
        this._scene.remove(mesh);
        mesh.geometry.dispose();
        (mesh.material as THREE.Material).dispose();
        this._markerMeshes.delete(id);
      }
    }

    for (const marker of markers3d) {
      let mesh = this._markerMeshes.get(marker.id);
      if (!mesh) {
        const geo = new THREE.SphereGeometry(0.12, 16, 16);
        const mat = new THREE.MeshStandardMaterial({
          color: 0x888888,
          emissive: 0x444444,
          emissiveIntensity: 0.3,
        });
        mesh = new THREE.Mesh(geo, mat);
        this._scene.add(mesh);
        this._markerMeshes.set(marker.id, mesh);
      }
      mesh.position.set(marker.x, marker.y, marker.z ?? 0);
    }
    this._updateLiveMarkerColors3d();
  }

  private _updateLiveMarkerColors3d(): void {
    const THREE = this._threeMod;
    if (!THREE || !this.hass) return;
    for (const marker of this.model?.markers ?? []) {
      if (marker.mode !== "3d") continue;
      const mesh = this._markerMeshes.get(marker.id);
      if (!mesh) continue;
      const { color, isOn } = liveMarkerColor(this.hass, marker.lightEntity);
      const c = new THREE.Color();
      c.setStyle(color);
      const mat = mesh.material as THREE.MeshStandardMaterial;
      mat.color.copy(c);
      mat.emissive.copy(c);
      mat.emissiveIntensity = isOn ? 0.8 : 0.15;
    }
  }

  private _disposeScene(): void {
    if (this._animId !== null) {
      cancelAnimationFrame(this._animId);
      this._animId = null;
    }
    this._resizeObserver?.disconnect();
    this._resizeObserver = null;

    const THREE = this._threeMod;
    if (THREE && this._scene) {
      this._scene.traverse((obj) => {
        const mesh = obj as THREE.Mesh;
        if (!mesh.isMesh) return;
        mesh.geometry?.dispose();
        const mat = mesh.material;
        if (Array.isArray(mat)) mat.forEach((m) => m.dispose());
        else mat?.dispose();
      });
    }
    this._markerMeshes.clear();
    this._model3d = null;
    this._controls?.dispose();
    this._controls = null;
    this._renderer?.dispose();
    this._renderer = null;
    this._scene = null;
    this._camera = null;
    this._raycaster = null;
  }

  // ── Shared marker list + controls ──────────────────────────────
  private _renderMarkerList() {
    const markers = this.model?.markers ?? [];
    if (!markers.length) return nothing;
    return html`
      <div class="hv-list">
        ${markers.map((marker) => this._renderMarkerRow(marker))}
      </div>
    `;
  }

  private _renderMarkerRow(marker: HouseViewMarker) {
    const { color } = liveMarkerColor(this.hass, marker.lightEntity);
    return html`
      <div class="hv-marker-item">
        <div class="hv-marker-dot" style="background:${color}"></div>
        <select
          @change=${(e: Event) => this._assignMarker(marker.id, (e.target as HTMLSelectElement).value)}
        >
          <option value="" ?selected=${marker.lightEntity === null}>-- Select light --</option>
          ${this.lights.map(
            (light) => html`
              <option value=${light.lightEntity} ?selected=${marker.lightEntity === light.lightEntity}>
                ${light.lightName}
              </option>
            `,
          )}
        </select>
        <button class="control-btn" @click=${() => this._removeMarker(marker.id)}>Remove</button>
      </div>
    `;
  }

  private _renderViewer() {
    if (this.model.mode === "3d") {
      // #viewer-3d-host is deliberately Lit-opaque: an unconditional,
      // always-empty child. Three.js's own renderer.domElement gets
      // mounted into it imperatively (see _initScene's replaceChildren)
      // -- that DOM write is invisible to Lit, so this div must never
      // also own a templated ${...} child of its own, or Lit's next
      // re-render tries to patch marker nodes that replaceChildren()
      // already wiped out and throws deep in its own diffing internals
      // ("Cannot read properties of null (reading 'nextSibling')"),
      // caught live in the disposable container during this phase's
      // verification. The placeholder/loading overlays are declarative
      // siblings, absolutely positioned over the host instead.
      return html`
        <div class="hv-viewer">
          <div id="viewer-3d-host"></div>
          ${!this.model.path
            ? html`<div class="hv-placeholder">
                No file loaded yet.<br />
                <code>.glb</code> or <code>.gltf</code> -- exports from Blender, Sweet Home 3D, or
                floor3d-card.<br /><br />
                Enter a path below (relative to your HA <code>/www/</code> folder) and click Load.
              </div>`
            : nothing}
          ${this._loading ? html`<div class="hv-loading">LOADING&hellip;</div>` : nothing}
        </div>
      `;
    }

    return html`
      <div class="hv-viewer">
        ${!this.model.path
          ? html`<div class="hv-placeholder">
              No file loaded yet.<br />
              Any image -- <code>.png</code> <code>.jpg</code> <code>.svg</code> -- a floor plan, a
              photo of your house, anything.<br /><br />
              Enter a path below (relative to your HA <code>/www/</code> folder) and click Load.
            </div>`
          : html`
              <img
                src=${this.model.path}
                alt="House"
                @click=${this._onImageClick}
                @load=${this._onImageLoad}
                @error=${this._onImageError}
              />
              ${this.model.markers
                .filter((m) => m.mode === "2d")
                .map((marker) => {
                  const { color } = liveMarkerColor(this.hass, marker.lightEntity);
                  return html`
                    <div
                      class="hv-marker ${marker.lightEntity === null ? "unassigned" : ""}"
                      style="left:${marker.x * 100}%;top:${marker.y * 100}%;background:${color};color:${color}"
                    ></div>
                  `;
                })}
            `}
      </div>
    `;
  }

  render() {
    if (!this.model) return nothing;
    return html`
      <div class="hv-controls">
        <div class="hv-mode-toggle">
          <button
            class="hv-mode-btn ${this.model.mode === "2d" ? "active" : ""}"
            @click=${() => this._setHouseView("2d", this.model.path)}
          >
            🖼️ 2D Image
          </button>
          <button
            class="hv-mode-btn ${this.model.mode === "3d" ? "active" : ""}"
            @click=${() => this._setHouseView("3d", this.model.path)}
          >
            📦 3D Model
          </button>
        </div>
        <input
          type="text"
          class="hv-path-input"
          .value=${this._pathInput}
          @input=${(e: Event) => (this._pathInput = (e.target as HTMLInputElement).value)}
          placeholder="/local/myhouse.png or /local/myhouse.glb"
        />
        <button
          class="control-btn control-btn-primary"
          @click=${() => this._setHouseView(this.model.mode, this._pathInput.trim())}
        >
          Load
        </button>
      </div>

      ${this._loadError ? html`<p class="hv-error">${this._loadError}</p>` : nothing}

      ${this._renderViewer()}
      ${this.model.path
        ? html`<p class="hv-hint">
            💡 Click anywhere on the image/model above to drop a marker, then pick which light it
            represents below. Markers glow with that light's live color.
          </p>`
        : nothing}
      ${this._renderMarkerList()}
    `;
  }

  static styles = css`
    :host {
      display: block;
    }

    .hv-controls {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .hv-mode-toggle {
      display: flex;
      gap: 6px;
    }

    .hv-mode-btn {
      padding: 8px 14px;
      border-radius: var(--cc-radius, 8px);
      border: 1px solid var(--cc-border);
      background: var(--cc-s2);
      color: var(--cc-muted);
      font-size: 11px;
      letter-spacing: 1px;
      cursor: pointer;
      transition:
        border-color 0.2s,
        color 0.2s;
    }

    .hv-mode-btn.active {
      border-color: var(--cc-accent);
      color: var(--cc-accent);
    }

    .hv-path-input {
      flex: 1;
      min-width: 180px;
      padding: 8px 10px;
      border-radius: var(--cc-radius, 8px);
      border: 1px solid var(--cc-border);
      background: var(--cc-s2);
      color: var(--cc-text);
    }

    .hv-viewer {
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: var(--cc-s2);
      border: 1px solid var(--cc-border);
      border-radius: var(--cc-radius, 8px);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: crosshair;
    }

    #viewer-3d-host {
      position: absolute;
      inset: 0;
    }

    .hv-viewer img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      user-select: none;
    }

    .hv-viewer canvas {
      width: 100% !important;
      height: 100% !important;
      display: block;
    }

    .hv-placeholder {
      text-align: center;
      color: var(--cc-muted);
      font-size: 12px;
      padding: 20px;
      line-height: 1.8;
    }

    .hv-placeholder code {
      background: var(--cc-s1);
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--cc-accent);
    }

    .hv-loading {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--cc-muted);
      background: rgba(0, 0, 0, 0.35);
      letter-spacing: 2px;
      font-size: 12px;
    }

    .hv-error {
      color: var(--cc-red);
      font-size: 12px;
      margin: 0 0 8px;
    }

    .hv-hint {
      font-size: 11px;
      color: var(--cc-muted);
      margin: 8px 0;
    }

    .hv-marker {
      position: absolute;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      border: 2px solid #fff;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 12px currentColor;
      pointer-events: none;
    }

    .hv-marker.unassigned {
      background: var(--cc-muted) !important;
      border-style: dashed;
    }

    .hv-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 12px;
    }

    .hv-marker-item {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .hv-marker-dot {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .hv-marker-item select {
      flex: 1;
      padding: 6px 8px;
      border-radius: var(--cc-radius, 8px);
      border: 1px solid var(--cc-border);
      background: var(--cc-s2);
      color: var(--cc-text);
    }

    .control-btn {
      padding: 6px 12px;
      border-radius: var(--cc-radius, 8px);
      border: 1px solid var(--cc-border);
      background: var(--cc-s2);
      color: var(--cc-text);
      cursor: pointer;
      font-size: 12px;
    }

    .control-btn:hover {
      opacity: 0.85;
    }

    .control-btn-primary {
      background: var(--cc-accent);
      color: var(--cc-s1);
      border-color: var(--cc-accent);
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "chromacal-house-view": ChromaCalHouseView;
  }
}

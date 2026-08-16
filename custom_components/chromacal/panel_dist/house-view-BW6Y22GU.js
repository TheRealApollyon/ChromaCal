import{a as y,b as a,c as p,d as x,e as w,f as v,g as u,h as k}from"./chunk-5VH4SVWE.js";import{a as c}from"./chunk-JFKSI6I7.js";var E="chromacal",M=5;function f(b,_){if(!_)return{color:"#888888",isOn:!1};let e=b.states[_];if(!e)return{color:"#888888",isOn:!1};if(!(e.state==="on"))return{color:"#333333",isOn:!1};let r=e.attributes.rgb_color;return{color:r?`rgb(${r.join(",")})`:"#f59e0b",isOn:!0}}var l=class extends x{constructor(){super(...arguments);this.lights=[];this._pathInput="";this._loadError=null;this._loading=!1;this._threeMod=null;this._GLTFLoaderCtor=null;this._OrbitControlsCtor=null;this._scene=null;this._camera=null;this._renderer=null;this._controls=null;this._raycaster=null;this._model3d=null;this._markerMeshes=new Map;this._animId=null;this._resizeObserver=null;this._pointerDownPos=null;this._loaded3dPath=null;this._animate=()=>{this._animId=requestAnimationFrame(this._animate),this._controls?.update(),this._renderer&&this._scene&&this._camera&&this._renderer.render(this._scene,this._camera)}}connectedCallback(){super.connectedCallback(),this._pathInput=this.model?.path??""}disconnectedCallback(){super.disconnectedCallback(),this._disposeScene()}willUpdate(e){e.has("model")&&this.model&&!e.get("model")&&(this._pathInput=this.model.path);let t=e.get("model");t&&this.model&&t.mode!==this.model.mode&&(this._loadError=null)}updated(e){this.model?.mode==="3d"&&this.model.path&&(this._loaded3dPath!==this.model.path?this._loadModel(this.model.path):e.has("model")&&this._syncMarkerMeshes()),e.has("hass")&&this.model?.mode==="3d"&&this._updateLiveMarkerColors3d()}_callService(e,t){this.hass.callService(E,e,t)}_setHouseView(e,t){this.model&&e!==this.model.mode&&(this._loadError=null),this._loaded3dPath=null,this._callService("set_house_view",{mode:e,path:t})}_addMarker(e,t,r,i){this._callService("add_house_marker",{mode:e,x:t,y:r,z:i??void 0})}_assignMarker(e,t){this._callService("assign_house_marker",{marker_id:e,light_entity:t||void 0})}_removeMarker(e){this._callService("remove_house_marker",{marker_id:e})}_onImageClick(e){let r=e.currentTarget.getBoundingClientRect(),i=(e.clientX-r.left)/r.width,o=(e.clientY-r.top)/r.height;i<0||i>1||o<0||o>1||this._addMarker("2d",i,o,null)}_onImageError(){this._loadError=`Could not load ${this.model.path} -- check the path and that the file is in your HA /www/ folder.`}_onImageLoad(){this._loadError=null}async _ensureThree(){if(this._threeMod)return;let[e,t,r]=await Promise.all([import("./three.module-E477GN6O.js"),import("./GLTFLoader-QCACB6RL.js"),import("./OrbitControls-VLDYU42X.js")]);this._threeMod=e,this._GLTFLoaderCtor=t.GLTFLoader,this._OrbitControlsCtor=r.OrbitControls}async _loadModel(e){this._loaded3dPath=e,this._loading=!0,this._loadError=null;try{await this._ensureThree();let t=this._viewer3dHost;if(!t)return;this._initScene(t),await this._loadGltf(e),this._syncMarkerMeshes()}catch(t){this._loadError=t instanceof Error?t.message:"3D engine failed to load."}finally{this._loading=!1}}_initScene(e){this._disposeScene();let t=this._threeMod,r=e.clientWidth||1,i=e.clientHeight||1,o=new t.Scene;o.background=new t.Color(857636);let s=new t.PerspectiveCamera(50,r/i,.1,2e3);s.position.set(5,5,5);let n=new t.WebGLRenderer({antialias:!0});n.outputColorSpace=t.SRGBColorSpace,n.setSize(r,i),e.replaceChildren(n.domElement),o.add(new t.AmbientLight(16777215,.7));let m=new t.DirectionalLight(16777215,.7);m.position.set(5,10,7),o.add(m);let h=new this._OrbitControlsCtor(s,n.domElement);h.enableDamping=!0,n.domElement.addEventListener("pointerdown",d=>{this._pointerDownPos={x:d.clientX,y:d.clientY}}),n.domElement.addEventListener("pointerup",d=>{let g=this._pointerDownPos;this._pointerDownPos=null,g&&Math.hypot(d.clientX-g.x,d.clientY-g.y)<M&&this._onCanvasClick(d)}),this._scene=o,this._camera=s,this._renderer=n,this._controls=h,this._raycaster=new t.Raycaster,this._markerMeshes.clear(),this._resizeObserver=new ResizeObserver(()=>this._onResize()),this._resizeObserver.observe(e),this._animate()}_onResize(){let e=this._viewer3dHost;if(!e||!this._renderer||!this._camera)return;let t=e.clientWidth||1,r=e.clientHeight||1;this._camera.aspect=t/r,this._camera.updateProjectionMatrix(),this._renderer.setSize(t,r)}_loadGltf(e){return new Promise((t,r)=>{new this._GLTFLoaderCtor().load(e,o=>{let s=this._threeMod;this._model3d&&this._scene?.remove(this._model3d),this._model3d=o.scene,this._scene?.add(this._model3d);let n=new s.Box3().setFromObject(this._model3d),m=n.getSize(new s.Vector3),h=n.getCenter(new s.Vector3),d=Math.max(m.x,m.y,m.z,1);this._camera&&(this._camera.position.set(h.x+d,h.y+d*.8,h.z+d),this._camera.far=d*20,this._camera.updateProjectionMatrix()),this._controls&&(this._controls.target.copy(h),this._controls.update()),t()},void 0,o=>r(o instanceof Error?o:new Error("Could not load the 3D model.")))})}_onCanvasClick(e){if(!this._model3d||!this._renderer||!this._raycaster||!this._camera||!this._threeMod)return;let t=this._renderer.domElement.getBoundingClientRect(),r=(e.clientX-t.left)/t.width*2-1,i=-((e.clientY-t.top)/t.height)*2+1;this._raycaster.setFromCamera(new this._threeMod.Vector2(r,i),this._camera);let o=this._raycaster.intersectObject(this._model3d,!0);if(!o.length)return;let s=o[0].point;this._addMarker("3d",s.x,s.y,s.z)}_syncMarkerMeshes(){let e=this._threeMod;if(!e||!this._scene)return;let t=(this.model?.markers??[]).filter(i=>i.mode==="3d"),r=new Set(t.map(i=>i.id));for(let[i,o]of this._markerMeshes)r.has(i)||(this._scene.remove(o),o.geometry.dispose(),o.material.dispose(),this._markerMeshes.delete(i));for(let i of t){let o=this._markerMeshes.get(i.id);if(!o){let s=new e.SphereGeometry(.12,16,16),n=new e.MeshStandardMaterial({color:8947848,emissive:4473924,emissiveIntensity:.3});o=new e.Mesh(s,n),this._scene.add(o),this._markerMeshes.set(i.id,o)}o.position.set(i.x,i.y,i.z??0)}this._updateLiveMarkerColors3d()}_updateLiveMarkerColors3d(){let e=this._threeMod;if(!(!e||!this.hass))for(let t of this.model?.markers??[]){if(t.mode!=="3d")continue;let r=this._markerMeshes.get(t.id);if(!r)continue;let{color:i,isOn:o}=f(this.hass,t.lightEntity),s=new e.Color;s.setStyle(i);let n=r.material;n.color.copy(s),n.emissive.copy(s),n.emissiveIntensity=o?.8:.15}}_disposeScene(){this._animId!==null&&(cancelAnimationFrame(this._animId),this._animId=null),this._resizeObserver?.disconnect(),this._resizeObserver=null,this._threeMod&&this._scene&&this._scene.traverse(t=>{let r=t;if(!r.isMesh)return;r.geometry?.dispose();let i=r.material;Array.isArray(i)?i.forEach(o=>o.dispose()):i?.dispose()}),this._markerMeshes.clear(),this._model3d=null,this._controls?.dispose(),this._controls=null,this._renderer?.dispose(),this._renderer=null,this._scene=null,this._camera=null,this._raycaster=null}_renderMarkerList(){let e=this.model?.markers??[];return e.length?a`
      <div class="hv-list">
        ${e.map(t=>this._renderMarkerRow(t))}
      </div>
    `:p}_renderMarkerRow(e){let{color:t}=f(this.hass,e.lightEntity);return a`
      <div class="hv-marker-item">
        <div class="hv-marker-dot" style="background:${t}"></div>
        <select
          @change=${r=>this._assignMarker(e.id,r.target.value)}
        >
          <option value="" ?selected=${e.lightEntity===null}>-- Select light --</option>
          ${this.lights.map(r=>a`
              <option value=${r.lightEntity} ?selected=${e.lightEntity===r.lightEntity}>
                ${r.lightName}
              </option>
            `)}
        </select>
        <button class="control-btn" @click=${()=>this._removeMarker(e.id)}>Remove</button>
      </div>
    `}_renderViewer(){return this.model.mode==="3d"?a`
        <div class="hv-viewer">
          <div id="viewer-3d-host"></div>
          ${this.model.path?p:a`<div class="hv-placeholder">
                No file loaded yet.<br />
                <code>.glb</code> or <code>.gltf</code> -- exports from Blender, Sweet Home 3D, or
                floor3d-card.<br /><br />
                Enter a path below (relative to your HA <code>/www/</code> folder) and click Load.
              </div>`}
          ${this._loading?a`<div class="hv-loading">LOADING&hellip;</div>`:p}
        </div>
      `:a`
      <div class="hv-viewer">
        ${this.model.path?a`
              <img
                src=${this.model.path}
                alt="House"
                @click=${this._onImageClick}
                @load=${this._onImageLoad}
                @error=${this._onImageError}
              />
              ${this.model.markers.filter(e=>e.mode==="2d").map(e=>{let{color:t}=f(this.hass,e.lightEntity);return a`
                    <div
                      class="hv-marker ${e.lightEntity===null?"unassigned":""}"
                      style="left:${e.x*100}%;top:${e.y*100}%;background:${t};color:${t}"
                    ></div>
                  `})}
            `:a`<div class="hv-placeholder">
              No file loaded yet.<br />
              Any image -- <code>.png</code> <code>.jpg</code> <code>.svg</code> -- a floor plan, a
              photo of your house, anything.<br /><br />
              Enter a path below (relative to your HA <code>/www/</code> folder) and click Load.
            </div>`}
      </div>
    `}render(){return this.model?a`
      <div class="hv-controls">
        <div class="hv-mode-toggle">
          <button
            class="hv-mode-btn ${this.model.mode==="2d"?"active":""}"
            @click=${()=>this._setHouseView("2d",this.model.path)}
          >
            🖼️ 2D Image
          </button>
          <button
            class="hv-mode-btn ${this.model.mode==="3d"?"active":""}"
            @click=${()=>this._setHouseView("3d",this.model.path)}
          >
            📦 3D Model
          </button>
        </div>
        <input
          type="text"
          class="hv-path-input"
          .value=${this._pathInput}
          @input=${e=>this._pathInput=e.target.value}
          placeholder="/local/myhouse.png or /local/myhouse.glb"
        />
        <button
          class="control-btn control-btn-primary"
          @click=${()=>this._setHouseView(this.model.mode,this._pathInput.trim())}
        >
          Load
        </button>
      </div>

      ${this._loadError?a`<p class="hv-error">${this._loadError}</p>`:p}

      ${this._renderViewer()}
      ${this.model.path?a`<p class="hv-hint">
            💡 Click anywhere on the image/model above to drop a marker, then pick which light it
            represents below. Markers glow with that light's live color.
          </p>`:p}
      ${this._renderMarkerList()}
    `:p}};l.styles=y`
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
  `,c([v({attribute:!1})],l.prototype,"hass",2),c([v({attribute:!1})],l.prototype,"model",2),c([v({attribute:!1})],l.prototype,"lights",2),c([u()],l.prototype,"_pathInput",2),c([u()],l.prototype,"_loadError",2),c([u()],l.prototype,"_loading",2),c([k("#viewer-3d-host")],l.prototype,"_viewer3dHost",2),l=c([w("chromacal-house-view")],l);export{l as ChromaCalHouseView};

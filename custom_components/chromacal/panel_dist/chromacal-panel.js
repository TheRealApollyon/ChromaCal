var Rt=Object.defineProperty;var Ut=Object.getOwnPropertyDescriptor;var b=(i,t,e,s)=>{for(var r=s>1?void 0:s?Ut(t,e):t,n=i.length-1,o;n>=0;n--)(o=i[n])&&(r=(s?o(t,e,r):o(r))||r);return s&&r&&Rt(t,e,r),r};var D=globalThis,W=D.ShadowRoot&&(D.ShadyCSS===void 0||D.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,F=Symbol(),ot=new WeakMap,T=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==F)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(W&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=ot.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&ot.set(e,t))}return t}toString(){return this.cssText}},at=i=>new T(typeof i=="string"?i:i+"",void 0,F),E=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((s,r,n)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+i[n+1],i[0]);return new T(e,i,F)},ct=(i,t)=>{if(W)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=D.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,i.appendChild(s)}},G=W?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return at(e)})(i):i;var{is:Ht,defineProperty:Lt,getOwnPropertyDescriptor:zt,getOwnPropertyNames:Dt,getOwnPropertySymbols:Wt,getPrototypeOf:Bt}=Object,B=globalThis,lt=B.trustedTypes,jt=lt?lt.emptyScript:"",qt=B.reactiveElementPolyfillSupport,C=(i,t)=>i,P={toAttribute(i,t){switch(t){case Boolean:i=i?jt:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},j=(i,t)=>!Ht(i,t),dt={attribute:!0,type:String,converter:P,reflect:!1,useDefault:!1,hasChanged:j};Symbol.metadata??=Symbol("metadata"),B.litPropertyMetadata??=new WeakMap;var v=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=dt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&Lt(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:n}=zt(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:r,set(o){let l=r?.call(this);n?.call(this,o),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??dt}static _$Ei(){if(this.hasOwnProperty(C("elementProperties")))return;let t=Bt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(C("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(C("properties"))){let e=this.properties,s=[...Dt(e),...Wt(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(G(r))}else t!==void 0&&e.push(G(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ct(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:P).toAttribute(e,s.type);this._$Em=t,n==null?this.removeAttribute(r):this.setAttribute(r,n),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let n=s.getPropertyOptions(r),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:P;this._$Em=r;let l=o.fromAttribute(e,n.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,s,r=!1,n){if(t!==void 0){let o=this.constructor;if(r===!1&&(n=this[t]),s??=o.getPropertyOptions(t),!((s.hasChanged??j)(n,e)||s.useDefault&&s.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:n},o){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),n!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,n]of this._$Ep)this[r]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,n]of s){let{wrapped:o}=n,l=this[r];o!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,n,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};v.elementStyles=[],v.shadowRootOptions={mode:"open"},v[C("elementProperties")]=new Map,v[C("finalized")]=new Map,qt?.({ReactiveElement:v}),(B.reactiveElementVersions??=[]).push("2.1.2");var tt=globalThis,ht=i=>i,q=tt.trustedTypes,pt=q?q.createPolicy("lit-html",{createHTML:i=>i}):void 0,vt="$lit$",y=`lit$${Math.random().toFixed(9).slice(2)}$`,yt="?"+y,Vt=`<${yt}>`,w=document,N=()=>w.createComment(""),I=i=>i===null||typeof i!="object"&&typeof i!="function",et=Array.isArray,Ft=i=>et(i)||typeof i?.[Symbol.iterator]=="function",K=`[ 	
\f\r]`,O=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ut=/-->/g,mt=/>/g,_=RegExp(`>|${K}(?:([^\\s"'>=/]+)(${K}*=${K}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),gt=/'/g,ft=/"/g,$t=/^(?:script|style|textarea|title)$/i,st=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),m=st(1),ce=st(2),le=st(3),S=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),bt=new WeakMap,x=w.createTreeWalker(w,129);function _t(i,t){if(!et(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return pt!==void 0?pt.createHTML(t):t}var Gt=(i,t)=>{let e=i.length-1,s=[],r,n=t===2?"<svg>":t===3?"<math>":"",o=O;for(let l=0;l<e;l++){let a=i[l],c,h,d=-1,u=0;for(;u<a.length&&(o.lastIndex=u,h=o.exec(a),h!==null);)u=o.lastIndex,o===O?h[1]==="!--"?o=ut:h[1]!==void 0?o=mt:h[2]!==void 0?($t.test(h[2])&&(r=RegExp("</"+h[2],"g")),o=_):h[3]!==void 0&&(o=_):o===_?h[0]===">"?(o=r??O,d=-1):h[1]===void 0?d=-2:(d=o.lastIndex-h[2].length,c=h[1],o=h[3]===void 0?_:h[3]==='"'?ft:gt):o===ft||o===gt?o=_:o===ut||o===mt?o=O:(o=_,r=void 0);let g=o===_&&i[l+1].startsWith("/>")?" ":"";n+=o===O?a+Vt:d>=0?(s.push(c),a.slice(0,d)+vt+a.slice(d)+y+g):a+y+(d===-2?l:g)}return[_t(i,n+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},R=class i{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let n=0,o=0,l=t.length-1,a=this.parts,[c,h]=Gt(t,e);if(this.el=i.createElement(c,s),x.currentNode=this.el.content,e===2||e===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(r=x.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let d of r.getAttributeNames())if(d.endsWith(vt)){let u=h[o++],g=r.getAttribute(d).split(y),z=/([.?@])?(.*)/.exec(u);a.push({type:1,index:n,name:z[2],strings:g,ctor:z[1]==="."?X:z[1]==="?"?Y:z[1]==="@"?Z:M}),r.removeAttribute(d)}else d.startsWith(y)&&(a.push({type:6,index:n}),r.removeAttribute(d));if($t.test(r.tagName)){let d=r.textContent.split(y),u=d.length-1;if(u>0){r.textContent=q?q.emptyScript:"";for(let g=0;g<u;g++)r.append(d[g],N()),x.nextNode(),a.push({type:2,index:++n});r.append(d[u],N())}}}else if(r.nodeType===8)if(r.data===yt)a.push({type:2,index:n});else{let d=-1;for(;(d=r.data.indexOf(y,d+1))!==-1;)a.push({type:7,index:n}),d+=y.length-1}n++}}static createElement(t,e){let s=w.createElement("template");return s.innerHTML=t,s}};function A(i,t,e=i,s){if(t===S)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,n=I(t)?void 0:t._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),n===void 0?r=void 0:(r=new n(i),r._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=A(i,r._$AS(i,t.values),r,s)),t}var J=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??w).importNode(e,!0);x.currentNode=r;let n=x.nextNode(),o=0,l=0,a=s[0];for(;a!==void 0;){if(o===a.index){let c;a.type===2?c=new U(n,n.nextSibling,this,t):a.type===1?c=new a.ctor(n,a.name,a.strings,this,t):a.type===6&&(c=new Q(n,this,t)),this._$AV.push(c),a=s[++l]}o!==a?.index&&(n=x.nextNode(),o++)}return x.currentNode=w,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},U=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=A(this,t,e),I(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==S&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Ft(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&I(this._$AH)?this._$AA.nextSibling.data=t:this.T(w.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=R.createElement(_t(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let n=new J(r,this),o=n.u(this.options);n.p(e),this.T(o),this._$AH=n}}_$AC(t){let e=bt.get(t.strings);return e===void 0&&bt.set(t.strings,e=new R(t)),e}k(t){et(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let n of t)r===e.length?e.push(s=new i(this.O(N()),this.O(N()),this,this.options)):s=e[r],s._$AI(n),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=ht(t).nextSibling;ht(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},M=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,n){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=p}_$AI(t,e=this,s,r){let n=this.strings,o=!1;if(n===void 0)t=A(this,t,e,0),o=!I(t)||t!==this._$AH&&t!==S,o&&(this._$AH=t);else{let l=t,a,c;for(t=n[0],a=0;a<n.length-1;a++)c=A(this,l[s+a],e,a),c===S&&(c=this._$AH[a]),o||=!I(c)||c!==this._$AH[a],c===p?t=p:t!==p&&(t+=(c??"")+n[a+1]),this._$AH[a]=c}o&&!r&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},X=class extends M{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}},Y=class extends M{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}},Z=class extends M{constructor(t,e,s,r,n){super(t,e,s,r,n),this.type=5}_$AI(t,e=this){if((t=A(this,t,e,0)??p)===S)return;let s=this._$AH,r=t===p&&s!==p||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==p&&(s===p||r);r&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},Q=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){A(this,t)}};var Kt=tt.litHtmlPolyfillSupport;Kt?.(R,U),(tt.litHtmlVersions??=[]).push("3.3.3");var xt=(i,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let n=e?.renderBefore??null;s._$litPart$=r=new U(t.insertBefore(N(),n),n,void 0,e??{})}return r._$AI(i),r};var rt=globalThis,$=class extends v{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=xt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return S}};$._$litElement$=!0,$.finalized=!0,rt.litElementHydrateSupport?.({LitElement:$});var Jt=rt.litElementPolyfillSupport;Jt?.({LitElement:$});(rt.litElementVersions??=[]).push("4.2.2");var wt=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)};var Xt={attribute:!0,type:String,converter:P,reflect:!1,hasChanged:j},Yt=(i=Xt,t,e)=>{let{kind:s,metadata:r}=e,n=globalThis.litPropertyMetadata.get(r);if(n===void 0&&globalThis.litPropertyMetadata.set(r,n=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),n.set(e.name,i),s==="accessor"){let{name:o}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(o,a,i,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,i,l),l}}}if(s==="setter"){let{name:o}=e;return function(l){let a=this[o];t.call(this,l),this.requestUpdate(o,a,i,!0,l)}}throw Error("Unsupported decorator location: "+s)};function k(i){return(t,e)=>typeof e=="object"?Yt(i,t,e):((s,r,n)=>{let o=r.hasOwnProperty(n);return r.constructor.createProperty(n,s),o?Object.getOwnPropertyDescriptor(r,n):void 0})(i,t,e)}function H(i){return k({...i,state:!0,attribute:!1})}function Zt(i){return{name:i.name,eventType:i.event_type,colors:i.colors,icon:i.icon,startTime:i.start_time,endTime:i.end_time}}function Qt(i){return Object.values(i.entities).filter(t=>t.platform==="chromacal").map(t=>t.entity_id)}function te(i){return i.split(".",1)[0]}function St(i){let t=Qt(i),e={saluteEntityId:null,saluteRunning:!1,catchUpEntityId:null,stopEntityId:null,emergencyEntityId:null,emergencyOn:!1},s=new Map,r=new Map,n=[],o=[];for(let a of t){let c=i.states[a];if(!c)continue;let h=c.attributes,d=te(a);if(d==="button"){let u=h.role;u==="salute"?(e.saluteEntityId=a,e.saluteRunning=!!h.running):u==="catch_up_sync"?e.catchUpEntityId=a:u==="stop"?e.stopEntityId=a:u==="force_white"&&typeof h.light_entity=="string"&&r.set(h.light_entity,a);continue}if(d==="switch"){let u=h.role;if(u==="emergency_mode")e.emergencyEntityId=a,e.emergencyOn=c.state==="on";else if(u==="skip"&&typeof h.event_name=="string"){let g={entityId:a,eventName:h.event_name,isOn:c.state==="on"};h.scope==="tonight"?n.push(g):o.push(g)}continue}d==="sensor"&&typeof h.light_entity=="string"&&s.set(h.light_entity,a)}let l=[];for(let[a,c]of s){let h=i.states[c],d=h?.attributes??{},g=i.states[a]?.attributes.friendly_name??a;l.push({lightEntity:a,lightName:g,scheduleEntityId:c,forceWhiteEntityId:r.get(a)??null,currentEventName:h?.state||null,currentEventType:d.event_type??null,currentColors:d.colors??[],currentIcon:d.icon??null,currentStart:d.start_time??null,currentEnd:d.end_time??null,segments:(d.segments??[]).map(Zt),sunsetHour:d.sunset_hour??null,scheduleEndTime:d.schedule_end_time??null})}return l.sort((a,c)=>a.lightName.localeCompare(c.lightName)),n.sort((a,c)=>a.eventName.localeCompare(c.eventName)),o.sort((a,c)=>a.eventName.localeCompare(c.eventName)),{globals:e,lights:l,tonightSkips:n,permanentSkips:o}}var Et=E`
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
`,it=["native","daylight","twilight","scifi","mono"],At={native:"Match dashboard theme",daylight:"Daylight",twilight:"Twilight",scifi:"Sci-Fi",mono:"Mono"},Mt=E`
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
`;function ee(i){let[t,e]=i.split(":").map(Number);return t*60+e}function Ct(i){return i>=960?i:i+24*60}function kt(i){return Ct(Math.round(i*60))}function L(i){return Ct(ee(i))}function nt(i){return Math.max(0,Math.min(100,(i-960)/960*100))}function Pt(i,t){let e=nt(L(i)),s=nt(L(t));return{leftPct:e,widthPct:Math.max(0,s-e)}}function Tt(i){let t=Math.round(i*60)%1440,e=Math.floor(t/60),s=t%60;return`${String(e).padStart(2,"0")}:${String(s).padStart(2,"0")}`}function Ot(i,t){let e=kt(t),s=[{label:"NOW",time:Tt(t),windowMinutes:e,emphasize:!1}];if(i.sunsetHour!==null){let a=kt(i.sunsetHour);a>e&&s.push({label:"SUNSET",time:Tt(i.sunsetHour),windowMinutes:a,emphasize:!1})}let r=i.segments[0];if(r){let a=L(r.startTime);a>e&&s.push({label:"COLORS",time:r.startTime,windowMinutes:a,emphasize:!1})}let n=i.segments[i.segments.length-1];if(n){let a=L(n.endTime),c=i.scheduleEndTime!==null?L(i.scheduleEndTime):null;c!==null&&a<c?(s.push({label:"WARM",time:n.endTime,windowMinutes:a,emphasize:!1}),s.push({label:"OFF",time:i.scheduleEndTime,windowMinutes:c,emphasize:!0})):s.push({label:"OFF",time:n.endTime,windowMinutes:a,emphasize:!0})}let o=9,l=-999;return s.sort((a,c)=>a.windowMinutes-c.windowMinutes).map(a=>{let c=nt(a.windowMinutes),h=c-l<o;return h||(l=c),{...a,leftPct:c,bare:h}})}var Nt="chromacal-panel-theme-preset",se=5;function It(i,t){let e=i.replace("#",""),s=parseInt(e,16),r=s>>16&255,n=s>>8&255,o=s&255;return`rgba(${r}, ${n}, ${o}, ${t})`}var f=class extends ${constructor(){super(...arguments);this.narrow=!1;this._themePreset="native";this._skipFilter="";this._manageSkipsOpen=!1;this._controlsOpen=!1}connectedCallback(){super.connectedCallback();let e=localStorage.getItem(Nt);e&&it.includes(e)&&(this._themePreset=e),this._applyThemeAttribute()}_applyThemeAttribute(){this._themePreset==="native"?this.removeAttribute("data-theme"):this.setAttribute("data-theme",this._themePreset)}_onThemeChange(e){let s=e.target.value;this._themePreset=s,localStorage.setItem(Nt,s),this._applyThemeAttribute()}_callService(e,s,r){r&&this.hass.callService(e,s,{entity_id:r})}_pressButton(e){this._callService("button","press",e)}_toggleSwitch(e,s){this._callService("switch",s?"turn_off":"turn_on",e)}render(){if(!this.hass)return p;let e=St(this.hass);return m`
      <div class="root">
        <header>
          <h1>ChromaCal</h1>
          <div class="header-right">
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
                ${it.map(s=>m`<option value=${s} ?selected=${s===this._themePreset}>
                    ${At[s]}
                  </option>`)}
              </select>
            </label>
          </div>
        </header>

        <div class="page-grid ${this.narrow?"narrow":""}">
          <main class="main-col">
            ${e.lights.length===0?m`<div class="empty-state">
                  <p>No lights configured yet.</p>
                  <p class="muted">Add a light from ChromaCal's settings to see it here.</p>
                </div>`:m`<section class="light-grid ${this.narrow?"narrow":""}">
                  ${e.lights.map(s=>this._renderLightCard(s))}
                </section>`}
          </main>

          <aside class="side-col">
            <section class="skip-section">
              <h2>Tonight's Skips</h2>
              ${e.tonightSkips.length===0?m`<p class="muted">Nothing skipped tonight.</p>`:m`<div class="chip-row">
                    ${e.tonightSkips.map(s=>this._renderSkipChip(s))}
                  </div>`}
            </section>

            <details
              class="collapsible-section"
              ?open=${this._controlsOpen}
              @toggle=${s=>this._controlsOpen=s.target.open}
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
              </div>
            </details>

            <details
              class="collapsible-section"
              ?open=${this._manageSkipsOpen}
              @toggle=${s=>this._manageSkipsOpen=s.target.open}
            >
              <summary>Manage Skips (${e.permanentSkips.length} events)</summary>
              <input
                type="search"
                placeholder="Filter events..."
                .value=${this._skipFilter}
                @input=${s=>this._skipFilter=s.target.value}
              />
              <div class="chip-row">
                ${e.permanentSkips.filter(s=>s.eventName.toLowerCase().includes(this._skipFilter.toLowerCase())).map(s=>this._renderSkipChip(s))}
              </div>
            </details>
          </aside>
        </div>
      </div>
    `}_renderSkipChip(e){return m`
      <button
        class="chip ${e.isOn?"skipped":""}"
        @click=${()=>this._toggleSwitch(e.entityId,e.isOn)}
        title=${e.isOn?"Skipped -- click to restore":"Click to skip"}
      >
        ${e.eventName}
      </button>
    `}_renderOrb(e,s){let r=e.currentColors[0],n=e.currentColors.length>=se,o=r?`background: radial-gradient(circle at 38% 30%, rgba(255,255,255,.45) 0%, ${r} 45%, rgba(0,0,0,.5) 100%); box-shadow: 0 0 ${s==="full"?"24px":"12px"} ${It(r,.627)}, 0 0 ${s==="full"?"46px":"23px"} ${It(r,.208)};`:"";return m`<div class="orb ${s} ${n?"spinning":""}" style=${o}></div>`}_renderLightCard(e){if(this.narrow)return m`
        <div class="light-card compact">
          ${this._renderOrb(e,"compact")}
          <div class="compact-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline compact">${e.currentEventName??"\u2014"}</span>
          </div>
        </div>
      `;let s=Ot(e,new Date().getHours()+new Date().getMinutes()/60);return m`
      <div class="light-card">
        <div class="card-top">
          ${this._renderOrb(e,"full")}
          <div class="card-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline">${e.currentEventName??"No active event"}</span>
            ${e.currentStart&&e.currentEnd?m`<span class="event-time-range"
                  >${e.currentStart}&ndash;${e.currentEnd}</span
                >`:p}
          </div>
          ${e.forceWhiteEntityId?m`<button
                class="force-white-btn"
                @click=${()=>this._pressButton(e.forceWhiteEntityId)}
              >
                Force White
              </button>`:p}
        </div>
        ${e.segments.length>0?m`<div class="timeline-wrapper">
              <div class="timeline">
                ${e.segments.map(r=>{let{leftPct:n,widthPct:o}=Pt(r.startTime,r.endTime),l=r.name===e.currentEventName;return m`<div
                    class="timeline-seg ${l?"current":""}"
                    style="left:${n}%; width:${o}%; background:${r.colors[0]??"var(--cc-s2)"}"
                    title="${r.name} (${r.startTime}–${r.endTime})"
                  ></div>`})}
              </div>
              <div class="timeline-marks">
                ${s.map(r=>m`
                    <div class="tl-mark" style="left:${r.leftPct}%">
                      <div class="tl-mark-line"></div>
                      ${r.bare?p:m`<span class="tl-mark-lbl ${r.emphasize?"hl":""}"
                              >${r.label}</span
                            ><span class="tl-mark-lbl ${r.emphasize?"hl":""}">${r.time}</span>`}
                    </div>
                  `)}
              </div>
            </div>`:p}
      </div>
    `}};f.styles=[Et,Mt,E`
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
    `],b([k({attribute:!1})],f.prototype,"hass",2),b([k({type:Boolean})],f.prototype,"narrow",2),b([k({attribute:!1})],f.prototype,"panel",2),b([H()],f.prototype,"_themePreset",2),b([H()],f.prototype,"_skipFilter",2),b([H()],f.prototype,"_manageSkipsOpen",2),b([H()],f.prototype,"_controlsOpen",2),f=b([wt("chromacal-panel")],f);export{f as ChromaCalPanel};

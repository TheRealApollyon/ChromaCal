var Pt=Object.defineProperty;var Tt=Object.getOwnPropertyDescriptor;var y=(i,t,e,s)=>{for(var r=s>1?void 0:s?Tt(t,e):t,n=i.length-1,o;n>=0;n--)(o=i[n])&&(r=(s?o(t,e,r):o(r))||r);return s&&r&&Pt(t,e,r),r};var D=globalThis,j=D.ShadowRoot&&(D.ShadyCSS===void 0||D.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,F=Symbol(),nt=new WeakMap,M=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==F)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(j&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=nt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&nt.set(e,t))}return t}toString(){return this.cssText}},ot=i=>new M(typeof i=="string"?i:i+"",void 0,F),E=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((s,r,n)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+i[n+1],i[0]);return new M(e,i,F)},at=(i,t)=>{if(j)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=D.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,i.appendChild(s)}},G=j?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return ot(e)})(i):i;var{is:Ot,defineProperty:Nt,getOwnPropertyDescriptor:It,getOwnPropertyNames:Ut,getOwnPropertySymbols:Rt,getPrototypeOf:Ht}=Object,B=globalThis,ct=B.trustedTypes,Lt=ct?ct.emptyScript:"",Dt=B.reactiveElementPolyfillSupport,P=(i,t)=>i,T={toAttribute(i,t){switch(t){case Boolean:i=i?Lt:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},z=(i,t)=>!Ot(i,t),lt={attribute:!0,type:String,converter:T,reflect:!1,useDefault:!1,hasChanged:z};Symbol.metadata??=Symbol("metadata"),B.litPropertyMetadata??=new WeakMap;var b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=lt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&Nt(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:n}=It(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:r,set(o){let l=r?.call(this);n?.call(this,o),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??lt}static _$Ei(){if(this.hasOwnProperty(P("elementProperties")))return;let t=Ht(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(P("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(P("properties"))){let e=this.properties,s=[...Ut(e),...Rt(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(G(r))}else t!==void 0&&e.push(G(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return at(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:T).toAttribute(e,s.type);this._$Em=t,n==null?this.removeAttribute(r):this.setAttribute(r,n),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let n=s.getPropertyOptions(r),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:T;this._$Em=r;let l=o.fromAttribute(e,n.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,s,r=!1,n){if(t!==void 0){let o=this.constructor;if(r===!1&&(n=this[t]),s??=o.getPropertyOptions(t),!((s.hasChanged??z)(n,e)||s.useDefault&&s.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:n},o){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),n!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,n]of this._$Ep)this[r]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,n]of s){let{wrapped:o}=n,l=this[r];o!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,n,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[P("elementProperties")]=new Map,b[P("finalized")]=new Map,Dt?.({ReactiveElement:b}),(B.reactiveElementVersions??=[]).push("2.1.2");var tt=globalThis,dt=i=>i,q=tt.trustedTypes,ht=q?q.createPolicy("lit-html",{createHTML:i=>i}):void 0,yt="$lit$",v=`lit$${Math.random().toFixed(9).slice(2)}$`,bt="?"+v,jt=`<${bt}>`,S=document,N=()=>S.createComment(""),I=i=>i===null||typeof i!="object"&&typeof i!="function",et=Array.isArray,Bt=i=>et(i)||typeof i?.[Symbol.iterator]=="function",K=`[ 	
\f\r]`,O=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,pt=/-->/g,ut=/>/g,_=RegExp(`>|${K}(?:([^\\s"'>=/]+)(${K}*=${K}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),mt=/'/g,gt=/"/g,vt=/^(?:script|style|textarea|title)$/i,st=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),m=st(1),se=st(2),re=st(3),A=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),ft=new WeakMap,x=S.createTreeWalker(S,129);function $t(i,t){if(!et(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ht!==void 0?ht.createHTML(t):t}var zt=(i,t)=>{let e=i.length-1,s=[],r,n=t===2?"<svg>":t===3?"<math>":"",o=O;for(let l=0;l<e;l++){let a=i[l],d,h,c=-1,u=0;for(;u<a.length&&(o.lastIndex=u,h=o.exec(a),h!==null);)u=o.lastIndex,o===O?h[1]==="!--"?o=pt:h[1]!==void 0?o=ut:h[2]!==void 0?(vt.test(h[2])&&(r=RegExp("</"+h[2],"g")),o=_):h[3]!==void 0&&(o=_):o===_?h[0]===">"?(o=r??O,c=-1):h[1]===void 0?c=-2:(c=o.lastIndex-h[2].length,d=h[1],o=h[3]===void 0?_:h[3]==='"'?gt:mt):o===gt||o===mt?o=_:o===pt||o===ut?o=O:(o=_,r=void 0);let g=o===_&&i[l+1].startsWith("/>")?" ":"";n+=o===O?a+jt:c>=0?(s.push(d),a.slice(0,c)+yt+a.slice(c)+v+g):a+v+(c===-2?l:g)}return[$t(i,n+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},U=class i{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let n=0,o=0,l=t.length-1,a=this.parts,[d,h]=zt(t,e);if(this.el=i.createElement(d,s),x.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(r=x.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let c of r.getAttributeNames())if(c.endsWith(yt)){let u=h[o++],g=r.getAttribute(c).split(v),L=/([.?@])?(.*)/.exec(u);a.push({type:1,index:n,name:L[2],strings:g,ctor:L[1]==="."?Y:L[1]==="?"?Z:L[1]==="@"?Q:C}),r.removeAttribute(c)}else c.startsWith(v)&&(a.push({type:6,index:n}),r.removeAttribute(c));if(vt.test(r.tagName)){let c=r.textContent.split(v),u=c.length-1;if(u>0){r.textContent=q?q.emptyScript:"";for(let g=0;g<u;g++)r.append(c[g],N()),x.nextNode(),a.push({type:2,index:++n});r.append(c[u],N())}}}else if(r.nodeType===8)if(r.data===bt)a.push({type:2,index:n});else{let c=-1;for(;(c=r.data.indexOf(v,c+1))!==-1;)a.push({type:7,index:n}),c+=v.length-1}n++}}static createElement(t,e){let s=S.createElement("template");return s.innerHTML=t,s}};function w(i,t,e=i,s){if(t===A)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,n=I(t)?void 0:t._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),n===void 0?r=void 0:(r=new n(i),r._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=w(i,r._$AS(i,t.values),r,s)),t}var J=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??S).importNode(e,!0);x.currentNode=r;let n=x.nextNode(),o=0,l=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new R(n,n.nextSibling,this,t):a.type===1?d=new a.ctor(n,a.name,a.strings,this,t):a.type===6&&(d=new X(n,this,t)),this._$AV.push(d),a=s[++l]}o!==a?.index&&(n=x.nextNode(),o++)}return x.currentNode=S,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},R=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=w(this,t,e),I(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==A&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Bt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&I(this._$AH)?this._$AA.nextSibling.data=t:this.T(S.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=U.createElement($t(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let n=new J(r,this),o=n.u(this.options);n.p(e),this.T(o),this._$AH=n}}_$AC(t){let e=ft.get(t.strings);return e===void 0&&ft.set(t.strings,e=new U(t)),e}k(t){et(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let n of t)r===e.length?e.push(s=new i(this.O(N()),this.O(N()),this,this.options)):s=e[r],s._$AI(n),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=dt(t).nextSibling;dt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},C=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,n){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=p}_$AI(t,e=this,s,r){let n=this.strings,o=!1;if(n===void 0)t=w(this,t,e,0),o=!I(t)||t!==this._$AH&&t!==A,o&&(this._$AH=t);else{let l=t,a,d;for(t=n[0],a=0;a<n.length-1;a++)d=w(this,l[s+a],e,a),d===A&&(d=this._$AH[a]),o||=!I(d)||d!==this._$AH[a],d===p?t=p:t!==p&&(t+=(d??"")+n[a+1]),this._$AH[a]=d}o&&!r&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},Y=class extends C{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}},Z=class extends C{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}},Q=class extends C{constructor(t,e,s,r,n){super(t,e,s,r,n),this.type=5}_$AI(t,e=this){if((t=w(this,t,e,0)??p)===A)return;let s=this._$AH,r=t===p&&s!==p||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==p&&(s===p||r);r&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},X=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){w(this,t)}};var qt=tt.litHtmlPolyfillSupport;qt?.(U,R),(tt.litHtmlVersions??=[]).push("3.3.3");var _t=(i,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let n=e?.renderBefore??null;s._$litPart$=r=new R(t.insertBefore(N(),n),n,void 0,e??{})}return r._$AI(i),r};var rt=globalThis,$=class extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=_t(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return A}};$._$litElement$=!0,$.finalized=!0,rt.litElementHydrateSupport?.({LitElement:$});var Wt=rt.litElementPolyfillSupport;Wt?.({LitElement:$});(rt.litElementVersions??=[]).push("4.2.2");var xt=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)};var Vt={attribute:!0,type:String,converter:T,reflect:!1,hasChanged:z},Ft=(i=Vt,t,e)=>{let{kind:s,metadata:r}=e,n=globalThis.litPropertyMetadata.get(r);if(n===void 0&&globalThis.litPropertyMetadata.set(r,n=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),n.set(e.name,i),s==="accessor"){let{name:o}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(o,a,i,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,i,l),l}}}if(s==="setter"){let{name:o}=e;return function(l){let a=this[o];t.call(this,l),this.requestUpdate(o,a,i,!0,l)}}throw Error("Unsupported decorator location: "+s)};function k(i){return(t,e)=>typeof e=="object"?Ft(i,t,e):((s,r,n)=>{let o=r.hasOwnProperty(n);return r.constructor.createProperty(n,s),o?Object.getOwnPropertyDescriptor(r,n):void 0})(i,t,e)}function H(i){return k({...i,state:!0,attribute:!1})}function Gt(i){return{name:i.name,eventType:i.event_type,colors:i.colors,icon:i.icon,startTime:i.start_time,endTime:i.end_time}}function Kt(i){return Object.values(i.entities).filter(t=>t.platform==="chromacal").map(t=>t.entity_id)}function Jt(i){return i.split(".",1)[0]}function St(i){let t=Kt(i),e={saluteEntityId:null,saluteRunning:!1,catchUpEntityId:null,stopEntityId:null,emergencyEntityId:null,emergencyOn:!1},s=new Map,r=new Map,n=[],o=[];for(let a of t){let d=i.states[a];if(!d)continue;let h=d.attributes,c=Jt(a);if(c==="button"){let u=h.role;u==="salute"?(e.saluteEntityId=a,e.saluteRunning=!!h.running):u==="catch_up_sync"?e.catchUpEntityId=a:u==="stop"?e.stopEntityId=a:u==="force_white"&&typeof h.light_entity=="string"&&r.set(h.light_entity,a);continue}if(c==="switch"){let u=h.role;if(u==="emergency_mode")e.emergencyEntityId=a,e.emergencyOn=d.state==="on";else if(u==="skip"&&typeof h.event_name=="string"){let g={entityId:a,eventName:h.event_name,isOn:d.state==="on"};h.scope==="tonight"?n.push(g):o.push(g)}continue}c==="sensor"&&typeof h.light_entity=="string"&&s.set(h.light_entity,a)}let l=[];for(let[a,d]of s){let h=i.states[d],c=h?.attributes??{},g=i.states[a]?.attributes.friendly_name??a;l.push({lightEntity:a,lightName:g,scheduleEntityId:d,forceWhiteEntityId:r.get(a)??null,currentEventName:h?.state||null,currentEventType:c.event_type??null,currentColors:c.colors??[],currentIcon:c.icon??null,currentStart:c.start_time??null,currentEnd:c.end_time??null,segments:(c.segments??[]).map(Gt),sunsetHour:c.sunset_hour??null})}return l.sort((a,d)=>a.lightName.localeCompare(d.lightName)),n.sort((a,d)=>a.eventName.localeCompare(d.eventName)),o.sort((a,d)=>a.eventName.localeCompare(d.eventName)),{globals:e,lights:l,tonightSkips:n,permanentSkips:o}}var At=E`
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
`,it=["native","daylight","twilight","scifi","mono"],Et={native:"Match dashboard theme",daylight:"Daylight",twilight:"Twilight",scifi:"Sci-Fi",mono:"Mono"},wt=E`
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
`;var Ct="chromacal-panel-theme-preset",V=16*60,kt=16*60;function Mt(i){let[t,e]=i.split(":").map(Number);return t*60+e}function Yt(i,t){let e=Mt(i),s=Mt(t),r=e>=V?e:e+24*60,n=s>=V?s:s+24*60,o=Math.max(0,Math.min(100,(r-V)/kt*100)),l=Math.max(0,Math.min(100,(n-V)/kt*100));return{leftPct:o,widthPct:Math.max(0,l-o)}}var f=class extends ${constructor(){super(...arguments);this.narrow=!1;this._themePreset="native";this._skipFilter="";this._manageSkipsOpen=!1;this._controlsOpen=!1}connectedCallback(){super.connectedCallback();let e=localStorage.getItem(Ct);e&&it.includes(e)&&(this._themePreset=e),this._applyThemeAttribute()}_applyThemeAttribute(){this._themePreset==="native"?this.removeAttribute("data-theme"):this.setAttribute("data-theme",this._themePreset)}_onThemeChange(e){let s=e.target.value;this._themePreset=s,localStorage.setItem(Ct,s),this._applyThemeAttribute()}_callService(e,s,r){r&&this.hass.callService(e,s,{entity_id:r})}_pressButton(e){this._callService("button","press",e)}_toggleSwitch(e,s){this._callService("switch",s?"turn_off":"turn_on",e)}render(){if(!this.hass)return p;let e=St(this.hass);return m`
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
                    ${Et[s]}
                  </option>`)}
              </select>
            </label>
          </div>
        </header>

        ${e.lights.length===0?m`<div class="empty-state">
              <p>No lights configured yet.</p>
              <p class="muted">Add a light from ChromaCal's settings to see it here.</p>
            </div>`:m`<section class="light-grid ${this.narrow?"narrow":""}">
              ${e.lights.map(s=>this._renderLightCard(s))}
            </section>`}

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
      </div>
    `}_renderSkipChip(e){return m`
      <button
        class="chip ${e.isOn?"skipped":""}"
        @click=${()=>this._toggleSwitch(e.entityId,e.isOn)}
        title=${e.isOn?"Skipped -- click to restore":"Click to skip"}
      >
        ${e.eventName}
      </button>
    `}_renderLightCard(e){return this.narrow?m`
        <div class="light-card compact">
          <span class="light-name">${e.lightName}</span>
          <span class="event-name">${e.currentEventName??"\u2014"}</span>
          ${e.currentColors[0]?m`<span class="swatch" style="background:${e.currentColors[0]}"></span>`:p}
        </div>
      `:m`
      <div class="light-card">
        <div class="light-card-header">
          <span class="light-name">${e.lightName}</span>
          ${e.forceWhiteEntityId?m`<button
                class="force-white-btn"
                @click=${()=>this._pressButton(e.forceWhiteEntityId)}
              >
                Force White
              </button>`:p}
        </div>
        <div class="current-event">
          ${e.currentColors[0]?m`<span class="swatch" style="background:${e.currentColors[0]}"></span>`:p}
          <span class="event-name">${e.currentEventName??"No active event"}</span>
          ${e.currentStart&&e.currentEnd?m`<span class="muted"
                >${e.currentStart}&ndash;${e.currentEnd}</span
              >`:p}
        </div>
        ${e.segments.length>0?m`<div class="timeline">
              ${e.segments.map(s=>{let{leftPct:r,widthPct:n}=Yt(s.startTime,s.endTime),o=s.name===e.currentEventName;return m`<div
                  class="timeline-seg ${o?"current":""}"
                  style="left:${r}%; width:${n}%; background:${s.colors[0]??"var(--cc-s2)"}"
                  title="${s.name} (${s.startTime}–${s.endTime})"
                ></div>`})}
            </div>`:p}
      </div>
    `}};f.styles=[At,wt,E`
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
    `],y([k({attribute:!1})],f.prototype,"hass",2),y([k({type:Boolean})],f.prototype,"narrow",2),y([k({attribute:!1})],f.prototype,"panel",2),y([H()],f.prototype,"_themePreset",2),y([H()],f.prototype,"_skipFilter",2),y([H()],f.prototype,"_manageSkipsOpen",2),y([H()],f.prototype,"_controlsOpen",2),f=y([xt("chromacal-panel")],f);export{f as ChromaCalPanel};

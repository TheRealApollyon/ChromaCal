var Bt=Object.defineProperty;var jt=Object.getOwnPropertyDescriptor;var y=(s,t,e,o)=>{for(var i=o>1?void 0:o?jt(t,e):t,r=s.length-1,n;r>=0;r--)(n=s[r])&&(i=(o?n(t,e,i):n(i))||i);return o&&i&&Bt(t,e,i),i};var F=globalThis,G=F.ShadowRoot&&(F.ShadyCSS===void 0||F.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),ht=new WeakMap,U=class{constructor(t,e,o){if(this._$cssResult$=!0,o!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(G&&t===void 0){let o=e!==void 0&&e.length===1;o&&(t=ht.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),o&&ht.set(e,t))}return t}toString(){return this.cssText}},ut=s=>new U(typeof s=="string"?s:s+"",void 0,Z),P=(s,...t)=>{let e=s.length===1?s[0]:t.reduce((o,i,r)=>o+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+s[r+1],s[0]);return new U(e,s,Z)},mt=(s,t)=>{if(G)s.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let o=document.createElement("style"),i=F.litNonce;i!==void 0&&o.setAttribute("nonce",i),o.textContent=e.cssText,s.appendChild(o)}},Q=G?s=>s:s=>s instanceof CSSStyleSheet?(t=>{let e="";for(let o of t.cssRules)e+=o.cssText;return ut(e)})(s):s;var{is:qt,defineProperty:Vt,getOwnPropertyDescriptor:Ft,getOwnPropertyNames:Gt,getOwnPropertySymbols:Kt,getPrototypeOf:Xt}=Object,K=globalThis,gt=K.trustedTypes,Jt=gt?gt.emptyScript:"",Yt=K.reactiveElementPolyfillSupport,H=(s,t)=>s,L={toAttribute(s,t){switch(t){case Boolean:s=s?Jt:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,t){let e=s;switch(t){case Boolean:e=s!==null;break;case Number:e=s===null?null:Number(s);break;case Object:case Array:try{e=JSON.parse(s)}catch{e=null}}return e}},X=(s,t)=>!qt(s,t),ft={attribute:!0,type:String,converter:L,reflect:!1,useDefault:!1,hasChanged:X};Symbol.metadata??=Symbol("metadata"),K.litPropertyMetadata??=new WeakMap;var x=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ft){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let o=Symbol(),i=this.getPropertyDescriptor(t,o,e);i!==void 0&&Vt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,o){let{get:i,set:r}=Ft(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:i,set(n){let l=i?.call(this);r?.call(this,n),this.requestUpdate(t,l,o)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ft}static _$Ei(){if(this.hasOwnProperty(H("elementProperties")))return;let t=Xt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(H("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(H("properties"))){let e=this.properties,o=[...Gt(e),...Kt(e)];for(let i of o)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[o,i]of e)this.elementProperties.set(o,i)}this._$Eh=new Map;for(let[e,o]of this.elementProperties){let i=this._$Eu(e,o);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let o=new Set(t.flat(1/0).reverse());for(let i of o)e.unshift(Q(i))}else t!==void 0&&e.push(Q(t));return e}static _$Eu(t,e){let o=e.attribute;return o===!1?void 0:typeof o=="string"?o:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let o of e.keys())this.hasOwnProperty(o)&&(t.set(o,this[o]),delete this[o]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return mt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,o){this._$AK(t,o)}_$ET(t,e){let o=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,o);if(i!==void 0&&o.reflect===!0){let r=(o.converter?.toAttribute!==void 0?o.converter:L).toAttribute(e,o.type);this._$Em=t,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(t,e){let o=this.constructor,i=o._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let r=o.getPropertyOptions(i),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:L;this._$Em=i;let l=n.fromAttribute(e,r.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(t,e,o,i=!1,r){if(t!==void 0){let n=this.constructor;if(i===!1&&(r=this[t]),o??=n.getPropertyOptions(t),!((o.hasChanged??X)(r,e)||o.useDefault&&o.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,o))))return;this.C(t,e,o)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:o,reflect:i,wrapped:r},n){o&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),r!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||o||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let o=this.constructor.elementProperties;if(o.size>0)for(let[i,r]of o){let{wrapped:n}=r,l=this[i];n!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,r,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(o=>o.hostUpdate?.()),this.update(e)):this._$EM()}catch(o){throw t=!1,this._$EM(),o}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[H("elementProperties")]=new Map,x[H("finalized")]=new Map,Yt?.({ReactiveElement:x}),(K.reactiveElementVersions??=[]).push("2.1.2");var nt=globalThis,vt=s=>s,J=nt.trustedTypes,bt=J?J.createPolicy("lit-html",{createHTML:s=>s}):void 0,St="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,Et="?"+S,Zt=`<${Et}>`,C=document,D=()=>C.createComment(""),W=s=>s===null||typeof s!="object"&&typeof s!="function",at=Array.isArray,Qt=s=>at(s)||typeof s?.[Symbol.iterator]=="function",tt=`[ 	
\f\r]`,z=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,yt=/-->/g,_t=/>/g,k=RegExp(`>|${tt}(?:([^\\s"'>=/]+)(${tt}*=${tt}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$t=/'/g,xt=/"/g,At=/^(?:script|style|textarea|title)$/i,ct=s=>(t,...e)=>({_$litType$:s,strings:t,values:e}),u=ct(1),ge=ct(2),fe=ct(3),T=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),wt=new WeakMap,M=C.createTreeWalker(C,129);function kt(s,t){if(!at(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return bt!==void 0?bt.createHTML(t):t}var te=(s,t)=>{let e=s.length-1,o=[],i,r=t===2?"<svg>":t===3?"<math>":"",n=z;for(let l=0;l<e;l++){let a=s[l],d,m,p=-1,_=0;for(;_<a.length&&(n.lastIndex=_,m=n.exec(a),m!==null);)_=n.lastIndex,n===z?m[1]==="!--"?n=yt:m[1]!==void 0?n=_t:m[2]!==void 0?(At.test(m[2])&&(i=RegExp("</"+m[2],"g")),n=k):m[3]!==void 0&&(n=k):n===k?m[0]===">"?(n=i??z,p=-1):m[1]===void 0?p=-2:(p=n.lastIndex-m[2].length,d=m[1],n=m[3]===void 0?k:m[3]==='"'?xt:$t):n===xt||n===$t?n=k:n===yt||n===_t?n=z:(n=k,i=void 0);let $=n===k&&s[l+1].startsWith("/>")?" ":"";r+=n===z?a+Zt:p>=0?(o.push(d),a.slice(0,p)+St+a.slice(p)+S+$):a+S+(p===-2?l:$)}return[kt(s,r+(s[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),o]},B=class s{constructor({strings:t,_$litType$:e},o){let i;this.parts=[];let r=0,n=0,l=t.length-1,a=this.parts,[d,m]=te(t,e);if(this.el=s.createElement(d,o),M.currentNode=this.el.content,e===2||e===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(i=M.nextNode())!==null&&a.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let p of i.getAttributeNames())if(p.endsWith(St)){let _=m[n++],$=i.getAttribute(p).split(S),O=/([.?@])?(.*)/.exec(_);a.push({type:1,index:r,name:O[2],strings:$,ctor:O[1]==="."?ot:O[1]==="?"?it:O[1]==="@"?st:R}),i.removeAttribute(p)}else p.startsWith(S)&&(a.push({type:6,index:r}),i.removeAttribute(p));if(At.test(i.tagName)){let p=i.textContent.split(S),_=p.length-1;if(_>0){i.textContent=J?J.emptyScript:"";for(let $=0;$<_;$++)i.append(p[$],D()),M.nextNode(),a.push({type:2,index:++r});i.append(p[_],D())}}}else if(i.nodeType===8)if(i.data===Et)a.push({type:2,index:r});else{let p=-1;for(;(p=i.data.indexOf(S,p+1))!==-1;)a.push({type:7,index:r}),p+=S.length-1}r++}}static createElement(t,e){let o=C.createElement("template");return o.innerHTML=t,o}};function N(s,t,e=s,o){if(t===T)return t;let i=o!==void 0?e._$Co?.[o]:e._$Cl,r=W(t)?void 0:t._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(s),i._$AT(s,e,o)),o!==void 0?(e._$Co??=[])[o]=i:e._$Cl=i),i!==void 0&&(t=N(s,i._$AS(s,t.values),i,o)),t}var et=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:o}=this._$AD,i=(t?.creationScope??C).importNode(e,!0);M.currentNode=i;let r=M.nextNode(),n=0,l=0,a=o[0];for(;a!==void 0;){if(n===a.index){let d;a.type===2?d=new j(r,r.nextSibling,this,t):a.type===1?d=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(d=new rt(r,this,t)),this._$AV.push(d),a=o[++l]}n!==a?.index&&(r=M.nextNode(),n++)}return M.currentNode=C,i}p(t){let e=0;for(let o of this._$AV)o!==void 0&&(o.strings!==void 0?(o._$AI(t,o,e),e+=o.strings.length-2):o._$AI(t[e])),e++}},j=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,o,i){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=o,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=N(this,t,e),W(t)?t===h||t==null||t===""?(this._$AH!==h&&this._$AR(),this._$AH=h):t!==this._$AH&&t!==T&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Qt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==h&&W(this._$AH)?this._$AA.nextSibling.data=t:this.T(C.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:o}=t,i=typeof o=="number"?this._$AC(t):(o.el===void 0&&(o.el=B.createElement(kt(o.h,o.h[0]),this.options)),o);if(this._$AH?._$AD===i)this._$AH.p(e);else{let r=new et(i,this),n=r.u(this.options);r.p(e),this.T(n),this._$AH=r}}_$AC(t){let e=wt.get(t.strings);return e===void 0&&wt.set(t.strings,e=new B(t)),e}k(t){at(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,o,i=0;for(let r of t)i===e.length?e.push(o=new s(this.O(D()),this.O(D()),this,this.options)):o=e[i],o._$AI(r),i++;i<e.length&&(this._$AR(o&&o._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let o=vt(t).nextSibling;vt(t).remove(),t=o}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},R=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,o,i,r){this.type=1,this._$AH=h,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,o.length>2||o[0]!==""||o[1]!==""?(this._$AH=Array(o.length-1).fill(new String),this.strings=o):this._$AH=h}_$AI(t,e=this,o,i){let r=this.strings,n=!1;if(r===void 0)t=N(this,t,e,0),n=!W(t)||t!==this._$AH&&t!==T,n&&(this._$AH=t);else{let l=t,a,d;for(t=r[0],a=0;a<r.length-1;a++)d=N(this,l[o+a],e,a),d===T&&(d=this._$AH[a]),n||=!W(d)||d!==this._$AH[a],d===h?t=h:t!==h&&(t+=(d??"")+r[a+1]),this._$AH[a]=d}n&&!i&&this.j(t)}j(t){t===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},ot=class extends R{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===h?void 0:t}},it=class extends R{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==h)}},st=class extends R{constructor(t,e,o,i,r){super(t,e,o,i,r),this.type=5}_$AI(t,e=this){if((t=N(this,t,e,0)??h)===T)return;let o=this._$AH,i=t===h&&o!==h||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==h&&(o===h||i);i&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},rt=class{constructor(t,e,o){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=o}get _$AU(){return this._$AM._$AU}_$AI(t){N(this,t)}};var ee=nt.litHtmlPolyfillSupport;ee?.(B,j),(nt.litHtmlVersions??=[]).push("3.3.3");var Mt=(s,t,e)=>{let o=e?.renderBefore??t,i=o._$litPart$;if(i===void 0){let r=e?.renderBefore??null;o._$litPart$=i=new j(t.insertBefore(D(),r),r,void 0,e??{})}return i._$AI(s),i};var lt=globalThis,E=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Mt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return T}};E._$litElement$=!0,E.finalized=!0,lt.litElementHydrateSupport?.({LitElement:E});var oe=lt.litElementPolyfillSupport;oe?.({LitElement:E});(lt.litElementVersions??=[]).push("4.2.2");var Ct=s=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(s,t)}):customElements.define(s,t)};var ie={attribute:!0,type:String,converter:L,reflect:!1,hasChanged:X},se=(s=ie,t,e)=>{let{kind:o,metadata:i}=e,r=globalThis.litPropertyMetadata.get(i);if(r===void 0&&globalThis.litPropertyMetadata.set(i,r=new Map),o==="setter"&&((s=Object.create(s)).wrapped=!0),r.set(e.name,s),o==="accessor"){let{name:n}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(n,a,s,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,s,l),l}}}if(o==="setter"){let{name:n}=e;return function(l){let a=this[n];t.call(this,l),this.requestUpdate(n,a,s,!0,l)}}throw Error("Unsupported decorator location: "+o)};function I(s){return(t,e)=>typeof e=="object"?se(s,t,e):((o,i,r)=>{let n=i.hasOwnProperty(r);return i.constructor.createProperty(r,o),n?Object.getOwnPropertyDescriptor(i,r):void 0})(s,t,e)}function A(s){return I({...s,state:!0,attribute:!1})}function re(s){return{name:s.name,eventType:s.event_type,colors:s.colors,icon:s.icon,startTime:s.start_time,endTime:s.end_time}}function ne(s){return Object.values(s.entities).filter(t=>t.platform==="chromacal").map(t=>t.entity_id)}function ae(s){return s.split(".",1)[0]}function Tt(s){let t=ne(s),e={saluteEntityId:null,saluteRunning:!1,catchUpEntityId:null,stopEntityId:null,emergencyEntityId:null,emergencyOn:!1},o=new Map,i=new Map,r=[],n=[],l=null;for(let c of t){let v=s.states[c];if(!v)continue;let f=v.attributes,b=ae(c);if(b==="button"){let w=f.role;w==="salute"?(e.saluteEntityId=c,e.saluteRunning=!!f.running):w==="catch_up_sync"?e.catchUpEntityId=c:w==="stop"?e.stopEntityId=c:w==="force_white"&&typeof f.light_entity=="string"&&i.set(f.light_entity,c);continue}if(b==="switch"){let w=f.role;if(w==="emergency_mode")e.emergencyEntityId=c,e.emergencyOn=v.state==="on";else if(w==="skip"&&typeof f.event_name=="string"){let V={entityId:c,eventName:f.event_name,isOn:v.state==="on"};f.scope==="tonight"?r.push(V):n.push(V)}continue}b==="sensor"&&(f.role==="upcoming_events"?l=c:typeof f.light_entity=="string"&&o.set(f.light_entity,c))}let a=[];for(let[c,v]of o){let f=s.states[v],b=f?.attributes??{},V=s.states[c]?.attributes.friendly_name??c;a.push({lightEntity:c,lightName:V,scheduleEntityId:v,forceWhiteEntityId:i.get(c)??null,currentEventName:f?.state||null,currentEventType:b.event_type??null,currentColors:b.colors??[],currentIcon:b.icon??null,currentStart:b.start_time??null,currentEnd:b.end_time??null,segments:(b.segments??[]).map(re),sunsetHour:b.sunset_hour??null,scheduleEndTime:b.schedule_end_time??null})}a.sort((c,v)=>c.lightName.localeCompare(v.lightName)),r.sort((c,v)=>c.eventName.localeCompare(v.eventName)),n.sort((c,v)=>c.eventName.localeCompare(v.eventName));let d=new Map(n.map(c=>[c.eventName,c])),m=new Map(r.map(c=>[c.eventName,c])),p=l?s.states[l]?.attributes:void 0,_=p?.events??[],$=p?.tonight_pick??null,O=p?.color_overrides??{},Wt=_.map(c=>({date:c.date,name:c.name,category:c.category,eventType:c.event_type,icon:c.icon,colors:c.colors,isToday:c.is_today,isPersonalRange:c.is_personal_range,permanentSkip:d.get(c.name)??null,tonightSkip:c.is_today?m.get(c.name)??null:null,isPicked:c.is_today&&$===c.name,overrideColors:O[c.name]??null}));return{globals:e,lights:a,tonightSkips:r,permanentSkips:n,upcomingEvents:Wt}}var Ot=P`
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
`,dt=["native","daylight","twilight","scifi","mono"],Pt={native:"Match dashboard theme",daylight:"Daylight",twilight:"Twilight",scifi:"Sci-Fi",mono:"Mono"},Nt=P`
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
`;function ce(s){let[t,e]=s.split(":").map(Number);return t*60+e}function Ut(s){return s>=960?s:s+24*60}function Rt(s){return Ut(Math.round(s*60))}function q(s){return Ut(ce(s))}function pt(s){return Math.max(0,Math.min(100,(s-960)/960*100))}function Ht(s,t){let e=pt(q(s)),o=pt(q(t));return{leftPct:e,widthPct:Math.max(0,o-e)}}function It(s){let t=Math.round(s*60)%1440,e=Math.floor(t/60),o=t%60;return`${String(e).padStart(2,"0")}:${String(o).padStart(2,"0")}`}function Lt(s,t){let e=Rt(t),o=[{label:"NOW",time:It(t),windowMinutes:e,emphasize:!1}];if(s.sunsetHour!==null){let a=Rt(s.sunsetHour);a>e&&o.push({label:"SUNSET",time:It(s.sunsetHour),windowMinutes:a,emphasize:!1})}let i=s.segments[0];if(i){let a=q(i.startTime);a>e&&o.push({label:"COLORS",time:i.startTime,windowMinutes:a,emphasize:!1})}let r=s.segments[s.segments.length-1];if(r){let a=q(r.endTime),d=s.scheduleEndTime!==null?q(s.scheduleEndTime):null;d!==null&&a<d?(o.push({label:"WARM",time:r.endTime,windowMinutes:a,emphasize:!1}),o.push({label:"OFF",time:s.scheduleEndTime,windowMinutes:d,emphasize:!0})):o.push({label:"OFF",time:r.endTime,windowMinutes:a,emphasize:!0})}let n=9,l=-999;return o.sort((a,d)=>a.windowMinutes-d.windowMinutes).map(a=>{let d=pt(a.windowMinutes),m=d-l<n;return m||(l=d),{...a,leftPct:d,bare:m}})}var zt="chromacal-panel-theme-preset",le=5;function Dt(s,t){let e=s.replace("#",""),o=parseInt(e,16),i=o>>16&255,r=o>>8&255,n=o&255;return`rgba(${i}, ${r}, ${n}, ${t})`}var g=class extends E{constructor(){super(...arguments);this.narrow=!1;this._themePreset="native";this._skipFilter="";this._manageSkipsOpen=!1;this._controlsOpen=!1;this._colorModalEvent=null;this._colorModalColors=[];this._colorModalPickerValue="#ffffff"}connectedCallback(){super.connectedCallback();let e=localStorage.getItem(zt);e&&dt.includes(e)&&(this._themePreset=e),this._applyThemeAttribute()}_applyThemeAttribute(){this._themePreset==="native"?this.removeAttribute("data-theme"):this.setAttribute("data-theme",this._themePreset)}_onThemeChange(e){let o=e.target.value;this._themePreset=o,localStorage.setItem(zt,o),this._applyThemeAttribute()}_callService(e,o,i){i&&this.hass.callService(e,o,{entity_id:i})}_pressButton(e){this._callService("button","press",e)}_toggleSwitch(e,o){this._callService("switch",o?"turn_off":"turn_on",e)}_setTonightPick(e){this.hass.callService("chromacal","set_tonight_pick",{event_name:e})}_openColorModal(e){this._colorModalEvent=e.name,this._colorModalColors=[...e.overrideColors??e.colors]}_closeColorModal(){this._colorModalEvent=null,this._colorModalColors=[]}_addColorModalColor(){this._colorModalColors.length>=g.MAX_COLORS||(this._colorModalColors=[...this._colorModalColors,this._colorModalPickerValue])}_removeColorModalColor(e){this._colorModalColors=this._colorModalColors.filter((o,i)=>i!==e)}_moveColorModalColor(e,o){let i=e+o;if(i<0||i>=this._colorModalColors.length)return;let r=[...this._colorModalColors];[r[e],r[i]]=[r[i],r[e]],this._colorModalColors=r}_saveColorOverride(){!this._colorModalEvent||this._colorModalColors.length===0||(this.hass.callService("chromacal","set_color_override",{event_name:this._colorModalEvent,colors:this._colorModalColors}),this._closeColorModal())}_resetColorOverride(){this._colorModalEvent&&(this.hass.callService("chromacal","reset_color_override",{event_name:this._colorModalEvent}),this._closeColorModal())}render(){if(!this.hass)return h;let e=Tt(this.hass);return u`
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
                ${dt.map(o=>u`<option value=${o} ?selected=${o===this._themePreset}>
                    ${Pt[o]}
                  </option>`)}
              </select>
            </label>
          </div>
        </header>

        <div class="page-grid ${this.narrow?"narrow":""}">
          <main class="main-col">
            ${e.lights.length===0?u`<div class="empty-state">
                  <p>No lights configured yet.</p>
                  <p class="muted">Add a light from ChromaCal's settings to see it here.</p>
                </div>`:u`<section class="light-grid ${this.narrow?"narrow":""}">
                  ${e.lights.map(o=>this._renderLightCard(o))}
                </section>`}

            <section class="upcoming-section">
              <h2>Upcoming Events</h2>
              ${e.upcomingEvents.length===0?u`<p class="muted">No events in the next 45 days for your selected categories.</p>`:u`<div class="upcoming-list">
                    ${e.upcomingEvents.map(o=>this._renderUpcomingRow(o))}
                  </div>`}
            </section>
          </main>

          <aside class="side-col">
            <section class="skip-section">
              <h2>Tonight's Skips</h2>
              ${e.tonightSkips.length===0?u`<p class="muted">Nothing skipped tonight.</p>`:u`<div class="chip-row">
                    ${e.tonightSkips.map(o=>this._renderSkipChip(o))}
                  </div>`}
            </section>

            <details
              class="collapsible-section"
              ?open=${this._controlsOpen}
              @toggle=${o=>this._controlsOpen=o.target.open}
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
              @toggle=${o=>this._manageSkipsOpen=o.target.open}
            >
              <summary>Manage Skips (${e.permanentSkips.length} events)</summary>
              <input
                type="search"
                placeholder="Filter events..."
                .value=${this._skipFilter}
                @input=${o=>this._skipFilter=o.target.value}
              />
              <div class="chip-row">
                ${e.permanentSkips.filter(o=>o.eventName.toLowerCase().includes(this._skipFilter.toLowerCase())).map(o=>this._renderSkipChip(o))}
              </div>
            </details>
          </aside>
        </div>

        ${this._colorModalEvent?this._renderColorModal():h}
      </div>
    `}_renderColorModal(){let e=this._colorModalEvent,o=this._colorModalColors;return u`
      <div class="modal-overlay" @click=${this._closeColorModal}>
        <div class="modal-dialog" @click=${i=>i.stopPropagation()}>
          <h3>Customize colors</h3>
          <p class="modal-event-name">${e}</p>

          <div class="modal-chip-row">
            ${o.length===0?u`<p class="muted">No colors -- add at least one below.</p>`:o.map((i,r)=>u`
                    <div class="modal-chip-item">
                      <span class="modal-chip" style="background:${i}" title=${i}></span>
                      <div class="modal-chip-btns">
                        <button
                          class="chip-move-btn"
                          ?disabled=${r===0}
                          @click=${()=>this._moveColorModalColor(r,-1)}
                          title="Move left"
                        >
                          ‹
                        </button>
                        <button
                          class="chip-move-btn chip-remove-btn"
                          @click=${()=>this._removeColorModalColor(r)}
                          title="Remove"
                        >
                          ×
                        </button>
                        <button
                          class="chip-move-btn"
                          ?disabled=${r===o.length-1}
                          @click=${()=>this._moveColorModalColor(r,1)}
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
              @input=${i=>this._colorModalPickerValue=i.target.value}
            />
            <button
              class="control-btn"
              ?disabled=${o.length>=g.MAX_COLORS}
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
                ?disabled=${o.length===0}
                @click=${this._saveColorOverride}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    `}_formatEventDate(e){return new Date(`${e}T00:00:00`).toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"})}_renderUpcomingRow(e){let o=e.permanentSkip,i=e.tonightSkip;return u`
      <div class="upcoming-row ${e.isToday?"today":""} ${o?.isOn?"skipped":""}">
        <span class="up-date">${e.isToday?"TODAY":this._formatEventDate(e.date)}</span>
        <span class="up-icon">${e.icon}</span>
        <span class="up-name">${e.name}</span>
        <span class="up-badge">${e.category}</span>
        <span class="up-chips">
          ${e.colors.map(r=>u`<span class="up-chip" style="background:${r}"></span>`)}
        </span>
        ${e.isToday&&!o?.isOn&&!i?.isOn?u`<button
              class="up-action-btn ${e.isPicked?"active":""}"
              @click=${()=>this._setTonightPick(e.name)}
              title=${e.isPicked?"Clear -- resume split":"Pick this event tonight"}
            >
              ${e.isPicked?"\u2605":"\u2606"}
            </button>`:h}
        <button
          class="up-action-btn ${e.overrideColors?"active":""}"
          @click=${()=>this._openColorModal(e)}
          title=${e.overrideColors?"Customized -- click to edit":"Customize colors for this event"}
        >
          🎨
        </button>
        ${i?u`<button
              class="up-action-btn ${i.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(i.entityId,i.isOn)}
              title=${i.isOn?"Skipped tonight -- click to restore":"Skip for tonight only (resets at midnight)"}
            >
              🌙
            </button>`:h}
        ${o?u`<button
              class="up-action-btn ${o.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(o.entityId,o.isOn)}
              title=${o.isOn?"Re-enable -- this event will run again":"Permanently skip this event"}
            >
              ${o.isOn?"\u2298":"\u25CB"}
            </button>`:h}
      </div>
    `}_renderSkipChip(e){return u`
      <button
        class="chip ${e.isOn?"skipped":""}"
        @click=${()=>this._toggleSwitch(e.entityId,e.isOn)}
        title=${e.isOn?"Skipped -- click to restore":"Click to skip"}
      >
        ${e.eventName}
      </button>
    `}_renderOrb(e,o){let i=e.currentColors[0],r=e.currentColors.length>=le,n=i?`background: radial-gradient(circle at 38% 30%, rgba(255,255,255,.45) 0%, ${i} 45%, rgba(0,0,0,.5) 100%); box-shadow: 0 0 ${o==="full"?"24px":"12px"} ${Dt(i,.627)}, 0 0 ${o==="full"?"46px":"23px"} ${Dt(i,.208)};`:"";return u`<div class="orb ${o} ${r?"spinning":""}" style=${n}></div>`}_renderLightCard(e){if(this.narrow)return u`
        <div class="light-card compact">
          ${this._renderOrb(e,"compact")}
          <div class="compact-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline compact">${e.currentEventName??"\u2014"}</span>
          </div>
        </div>
      `;let o=Lt(e,new Date().getHours()+new Date().getMinutes()/60);return u`
      <div class="light-card">
        <div class="card-top">
          ${this._renderOrb(e,"full")}
          <div class="card-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline">${e.currentEventName??"No active event"}</span>
            ${e.currentStart&&e.currentEnd?u`<span class="event-time-range"
                  >${e.currentStart}&ndash;${e.currentEnd}</span
                >`:h}
          </div>
          ${e.forceWhiteEntityId?u`<button
                class="force-white-btn"
                @click=${()=>this._pressButton(e.forceWhiteEntityId)}
              >
                Force White
              </button>`:h}
        </div>
        ${e.segments.length>0?u`<div class="timeline-wrapper">
              <div class="timeline">
                ${e.segments.map(i=>{let{leftPct:r,widthPct:n}=Ht(i.startTime,i.endTime),l=i.name===e.currentEventName;return u`<div
                    class="timeline-seg ${l?"current":""}"
                    style="left:${r}%; width:${n}%; background:${i.colors[0]??"var(--cc-s2)"}"
                    title="${i.name} (${i.startTime}–${i.endTime})"
                  ></div>`})}
              </div>
              <div class="timeline-marks">
                ${o.map(i=>u`
                    <div class="tl-mark" style="left:${i.leftPct}%">
                      <div class="tl-mark-line"></div>
                      ${i.bare?h:u`<span class="tl-mark-lbl ${i.emphasize?"hl":""}"
                              >${i.label}</span
                            ><span class="tl-mark-lbl ${i.emphasize?"hl":""}">${i.time}</span>`}
                    </div>
                  `)}
              </div>
            </div>`:h}
      </div>
    `}};g.MAX_COLORS=6,g.styles=[Ot,Nt,P`
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
    `],y([I({attribute:!1})],g.prototype,"hass",2),y([I({type:Boolean})],g.prototype,"narrow",2),y([I({attribute:!1})],g.prototype,"panel",2),y([A()],g.prototype,"_themePreset",2),y([A()],g.prototype,"_skipFilter",2),y([A()],g.prototype,"_manageSkipsOpen",2),y([A()],g.prototype,"_controlsOpen",2),y([A()],g.prototype,"_colorModalEvent",2),y([A()],g.prototype,"_colorModalColors",2),y([A()],g.prototype,"_colorModalPickerValue",2),g=y([Ct("chromacal-panel")],g);export{g as ChromaCalPanel};

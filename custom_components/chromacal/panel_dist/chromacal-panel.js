var Dt=Object.defineProperty;var Wt=Object.getOwnPropertyDescriptor;var _=(i,t,e,s)=>{for(var n=s>1?void 0:s?Wt(t,e):t,r=i.length-1,o;r>=0;r--)(o=i[r])&&(n=(s?o(t,e,n):o(n))||n);return s&&n&&Dt(t,e,n),n};var V=globalThis,F=V.ShadowRoot&&(V.ShadyCSS===void 0||V.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,X=Symbol(),pt=new WeakMap,I=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==X)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(F&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=pt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&pt.set(e,t))}return t}toString(){return this.cssText}},ht=i=>new I(typeof i=="string"?i:i+"",void 0,X),O=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((s,n,r)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+i[r+1],i[0]);return new I(e,i,X)},ut=(i,t)=>{if(F)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),n=V.litNonce;n!==void 0&&s.setAttribute("nonce",n),s.textContent=e.cssText,i.appendChild(s)}},Z=F?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return ht(e)})(i):i;var{is:Bt,defineProperty:jt,getOwnPropertyDescriptor:qt,getOwnPropertyNames:Vt,getOwnPropertySymbols:Ft,getPrototypeOf:Gt}=Object,G=globalThis,mt=G.trustedTypes,Kt=mt?mt.emptyScript:"",Jt=G.reactiveElementPolyfillSupport,R=(i,t)=>i,U={toAttribute(i,t){switch(t){case Boolean:i=i?Kt:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},K=(i,t)=>!Bt(i,t),gt={attribute:!0,type:String,converter:U,reflect:!1,useDefault:!1,hasChanged:K};Symbol.metadata??=Symbol("metadata"),G.litPropertyMetadata??=new WeakMap;var x=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=gt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),n=this.getPropertyDescriptor(t,s,e);n!==void 0&&jt(this.prototype,t,n)}}static getPropertyDescriptor(t,e,s){let{get:n,set:r}=qt(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:n,set(o){let l=n?.call(this);r?.call(this,o),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??gt}static _$Ei(){if(this.hasOwnProperty(R("elementProperties")))return;let t=Gt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(R("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(R("properties"))){let e=this.properties,s=[...Vt(e),...Ft(e)];for(let n of s)this.createProperty(n,e[n])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,n]of e)this.elementProperties.set(s,n)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let n=this._$Eu(e,s);n!==void 0&&this._$Eh.set(n,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let n of s)e.unshift(Z(n))}else t!==void 0&&e.push(Z(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ut(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),n=this.constructor._$Eu(t,s);if(n!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:U).toAttribute(e,s.type);this._$Em=t,r==null?this.removeAttribute(n):this.setAttribute(n,r),this._$Em=null}}_$AK(t,e){let s=this.constructor,n=s._$Eh.get(t);if(n!==void 0&&this._$Em!==n){let r=s.getPropertyOptions(n),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:U;this._$Em=n;let l=o.fromAttribute(e,r.type);this[n]=l??this._$Ej?.get(n)??l,this._$Em=null}}requestUpdate(t,e,s,n=!1,r){if(t!==void 0){let o=this.constructor;if(n===!1&&(r=this[t]),s??=o.getPropertyOptions(t),!((s.hasChanged??K)(r,e)||s.useDefault&&s.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:n,wrapped:r},o){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),r!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),n===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[n,r]of this._$Ep)this[n]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[n,r]of s){let{wrapped:o}=r,l=this[n];o!==!0||this._$AL.has(n)||l===void 0||this.C(n,void 0,r,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[R("elementProperties")]=new Map,x[R("finalized")]=new Map,Jt?.({ReactiveElement:x}),(G.reactiveElementVersions??=[]).push("2.1.2");var rt=globalThis,ft=i=>i,J=rt.trustedTypes,bt=J?J.createPolicy("lit-html",{createHTML:i=>i}):void 0,wt="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,St="?"+S,Yt=`<${St}>`,M=document,L=()=>M.createComment(""),z=i=>i===null||typeof i!="object"&&typeof i!="function",ot=Array.isArray,Xt=i=>ot(i)||typeof i?.[Symbol.iterator]=="function",Q=`[ 	
\f\r]`,H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,vt=/-->/g,yt=/>/g,A=RegExp(`>|${Q}(?:([^\\s"'>=/]+)(${Q}*=${Q}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$t=/'/g,_t=/"/g,Et=/^(?:script|style|textarea|title)$/i,at=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),u=at(1),ue=at(2),me=at(3),T=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),xt=new WeakMap,k=M.createTreeWalker(M,129);function At(i,t){if(!ot(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return bt!==void 0?bt.createHTML(t):t}var Zt=(i,t)=>{let e=i.length-1,s=[],n,r=t===2?"<svg>":t===3?"<math>":"",o=H;for(let l=0;l<e;l++){let a=i[l],d,m,h=-1,y=0;for(;y<a.length&&(o.lastIndex=y,m=o.exec(a),m!==null);)y=o.lastIndex,o===H?m[1]==="!--"?o=vt:m[1]!==void 0?o=yt:m[2]!==void 0?(Et.test(m[2])&&(n=RegExp("</"+m[2],"g")),o=A):m[3]!==void 0&&(o=A):o===A?m[0]===">"?(o=n??H,h=-1):m[1]===void 0?h=-2:(h=o.lastIndex-m[2].length,d=m[1],o=m[3]===void 0?A:m[3]==='"'?_t:$t):o===_t||o===$t?o=A:o===vt||o===yt?o=H:(o=A,n=void 0);let $=o===A&&i[l+1].startsWith("/>")?" ":"";r+=o===H?a+Yt:h>=0?(s.push(d),a.slice(0,h)+wt+a.slice(h)+S+$):a+S+(h===-2?l:$)}return[At(i,r+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},D=class i{constructor({strings:t,_$litType$:e},s){let n;this.parts=[];let r=0,o=0,l=t.length-1,a=this.parts,[d,m]=Zt(t,e);if(this.el=i.createElement(d,s),k.currentNode=this.el.content,e===2||e===3){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(n=k.nextNode())!==null&&a.length<l;){if(n.nodeType===1){if(n.hasAttributes())for(let h of n.getAttributeNames())if(h.endsWith(wt)){let y=m[o++],$=n.getAttribute(h).split(S),c=/([.?@])?(.*)/.exec(y);a.push({type:1,index:r,name:c[2],strings:$,ctor:c[1]==="."?et:c[1]==="?"?st:c[1]==="@"?nt:C}),n.removeAttribute(h)}else h.startsWith(S)&&(a.push({type:6,index:r}),n.removeAttribute(h));if(Et.test(n.tagName)){let h=n.textContent.split(S),y=h.length-1;if(y>0){n.textContent=J?J.emptyScript:"";for(let $=0;$<y;$++)n.append(h[$],L()),k.nextNode(),a.push({type:2,index:++r});n.append(h[y],L())}}}else if(n.nodeType===8)if(n.data===St)a.push({type:2,index:r});else{let h=-1;for(;(h=n.data.indexOf(S,h+1))!==-1;)a.push({type:7,index:r}),h+=S.length-1}r++}}static createElement(t,e){let s=M.createElement("template");return s.innerHTML=t,s}};function P(i,t,e=i,s){if(t===T)return t;let n=s!==void 0?e._$Co?.[s]:e._$Cl,r=z(t)?void 0:t._$litDirective$;return n?.constructor!==r&&(n?._$AO?.(!1),r===void 0?n=void 0:(n=new r(i),n._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=n:e._$Cl=n),n!==void 0&&(t=P(i,n._$AS(i,t.values),n,s)),t}var tt=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,n=(t?.creationScope??M).importNode(e,!0);k.currentNode=n;let r=k.nextNode(),o=0,l=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new W(r,r.nextSibling,this,t):a.type===1?d=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(d=new it(r,this,t)),this._$AV.push(d),a=s[++l]}o!==a?.index&&(r=k.nextNode(),o++)}return k.currentNode=M,n}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},W=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,n){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=P(this,t,e),z(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==T&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Xt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&z(this._$AH)?this._$AA.nextSibling.data=t:this.T(M.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,n=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=D.createElement(At(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===n)this._$AH.p(e);else{let r=new tt(n,this),o=r.u(this.options);r.p(e),this.T(o),this._$AH=r}}_$AC(t){let e=xt.get(t.strings);return e===void 0&&xt.set(t.strings,e=new D(t)),e}k(t){ot(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,n=0;for(let r of t)n===e.length?e.push(s=new i(this.O(L()),this.O(L()),this,this.options)):s=e[n],s._$AI(r),n++;n<e.length&&(this._$AR(s&&s._$AB.nextSibling,n),e.length=n)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=ft(t).nextSibling;ft(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},C=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,n,r){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=n,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=p}_$AI(t,e=this,s,n){let r=this.strings,o=!1;if(r===void 0)t=P(this,t,e,0),o=!z(t)||t!==this._$AH&&t!==T,o&&(this._$AH=t);else{let l=t,a,d;for(t=r[0],a=0;a<r.length-1;a++)d=P(this,l[s+a],e,a),d===T&&(d=this._$AH[a]),o||=!z(d)||d!==this._$AH[a],d===p?t=p:t!==p&&(t+=(d??"")+r[a+1]),this._$AH[a]=d}o&&!n&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},et=class extends C{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}},st=class extends C{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}},nt=class extends C{constructor(t,e,s,n,r){super(t,e,s,n,r),this.type=5}_$AI(t,e=this){if((t=P(this,t,e,0)??p)===T)return;let s=this._$AH,n=t===p&&s!==p||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==p&&(s===p||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},it=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){P(this,t)}};var Qt=rt.litHtmlPolyfillSupport;Qt?.(D,W),(rt.litHtmlVersions??=[]).push("3.3.3");var kt=(i,t,e)=>{let s=e?.renderBefore??t,n=s._$litPart$;if(n===void 0){let r=e?.renderBefore??null;s._$litPart$=n=new W(t.insertBefore(L(),r),r,void 0,e??{})}return n._$AI(i),n};var ct=globalThis,E=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=kt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return T}};E._$litElement$=!0,E.finalized=!0,ct.litElementHydrateSupport?.({LitElement:E});var te=ct.litElementPolyfillSupport;te?.({LitElement:E});(ct.litElementVersions??=[]).push("4.2.2");var Mt=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)};var ee={attribute:!0,type:String,converter:U,reflect:!1,hasChanged:K},se=(i=ee,t,e)=>{let{kind:s,metadata:n}=e,r=globalThis.litPropertyMetadata.get(n);if(r===void 0&&globalThis.litPropertyMetadata.set(n,r=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),r.set(e.name,i),s==="accessor"){let{name:o}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(o,a,i,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,i,l),l}}}if(s==="setter"){let{name:o}=e;return function(l){let a=this[o];t.call(this,l),this.requestUpdate(o,a,i,!0,l)}}throw Error("Unsupported decorator location: "+s)};function N(i){return(t,e)=>typeof e=="object"?se(i,t,e):((s,n,r)=>{let o=n.hasOwnProperty(r);return n.constructor.createProperty(r,s),o?Object.getOwnPropertyDescriptor(n,r):void 0})(i,t,e)}function B(i){return N({...i,state:!0,attribute:!1})}function ne(i){return{name:i.name,eventType:i.event_type,colors:i.colors,icon:i.icon,startTime:i.start_time,endTime:i.end_time}}function ie(i){return Object.values(i.entities).filter(t=>t.platform==="chromacal").map(t=>t.entity_id)}function re(i){return i.split(".",1)[0]}function Tt(i){let t=ie(i),e={saluteEntityId:null,saluteRunning:!1,catchUpEntityId:null,stopEntityId:null,emergencyEntityId:null,emergencyOn:!1},s=new Map,n=new Map,r=[],o=[],l=null;for(let c of t){let f=i.states[c];if(!f)continue;let g=f.attributes,b=re(c);if(b==="button"){let w=g.role;w==="salute"?(e.saluteEntityId=c,e.saluteRunning=!!g.running):w==="catch_up_sync"?e.catchUpEntityId=c:w==="stop"?e.stopEntityId=c:w==="force_white"&&typeof g.light_entity=="string"&&n.set(g.light_entity,c);continue}if(b==="switch"){let w=g.role;if(w==="emergency_mode")e.emergencyEntityId=c,e.emergencyOn=f.state==="on";else if(w==="skip"&&typeof g.event_name=="string"){let q={entityId:c,eventName:g.event_name,isOn:f.state==="on"};g.scope==="tonight"?r.push(q):o.push(q)}continue}b==="sensor"&&(g.role==="upcoming_events"?l=c:typeof g.light_entity=="string"&&s.set(g.light_entity,c))}let a=[];for(let[c,f]of s){let g=i.states[f],b=g?.attributes??{},q=i.states[c]?.attributes.friendly_name??c;a.push({lightEntity:c,lightName:q,scheduleEntityId:f,forceWhiteEntityId:n.get(c)??null,currentEventName:g?.state||null,currentEventType:b.event_type??null,currentColors:b.colors??[],currentIcon:b.icon??null,currentStart:b.start_time??null,currentEnd:b.end_time??null,segments:(b.segments??[]).map(ne),sunsetHour:b.sunset_hour??null,scheduleEndTime:b.schedule_end_time??null})}a.sort((c,f)=>c.lightName.localeCompare(f.lightName)),r.sort((c,f)=>c.eventName.localeCompare(f.eventName)),o.sort((c,f)=>c.eventName.localeCompare(f.eventName));let d=new Map(o.map(c=>[c.eventName,c])),m=new Map(r.map(c=>[c.eventName,c])),$=((l?i.states[l]:void 0)?.attributes.events??[]).map(c=>({date:c.date,name:c.name,category:c.category,eventType:c.event_type,icon:c.icon,colors:c.colors,isToday:c.is_today,isPersonalRange:c.is_personal_range,permanentSkip:d.get(c.name)??null,tonightSkip:c.is_today?m.get(c.name)??null:null}));return{globals:e,lights:a,tonightSkips:r,permanentSkips:o,upcomingEvents:$}}var Ot=O`
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
`,lt=["native","daylight","twilight","scifi","mono"],Pt={native:"Match dashboard theme",daylight:"Daylight",twilight:"Twilight",scifi:"Sci-Fi",mono:"Mono"},Ct=O`
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
`;function oe(i){let[t,e]=i.split(":").map(Number);return t*60+e}function Rt(i){return i>=960?i:i+24*60}function Nt(i){return Rt(Math.round(i*60))}function j(i){return Rt(oe(i))}function dt(i){return Math.max(0,Math.min(100,(i-960)/960*100))}function Ut(i,t){let e=dt(j(i)),s=dt(j(t));return{leftPct:e,widthPct:Math.max(0,s-e)}}function It(i){let t=Math.round(i*60)%1440,e=Math.floor(t/60),s=t%60;return`${String(e).padStart(2,"0")}:${String(s).padStart(2,"0")}`}function Ht(i,t){let e=Nt(t),s=[{label:"NOW",time:It(t),windowMinutes:e,emphasize:!1}];if(i.sunsetHour!==null){let a=Nt(i.sunsetHour);a>e&&s.push({label:"SUNSET",time:It(i.sunsetHour),windowMinutes:a,emphasize:!1})}let n=i.segments[0];if(n){let a=j(n.startTime);a>e&&s.push({label:"COLORS",time:n.startTime,windowMinutes:a,emphasize:!1})}let r=i.segments[i.segments.length-1];if(r){let a=j(r.endTime),d=i.scheduleEndTime!==null?j(i.scheduleEndTime):null;d!==null&&a<d?(s.push({label:"WARM",time:r.endTime,windowMinutes:a,emphasize:!1}),s.push({label:"OFF",time:i.scheduleEndTime,windowMinutes:d,emphasize:!0})):s.push({label:"OFF",time:r.endTime,windowMinutes:a,emphasize:!0})}let o=9,l=-999;return s.sort((a,d)=>a.windowMinutes-d.windowMinutes).map(a=>{let d=dt(a.windowMinutes),m=d-l<o;return m||(l=d),{...a,leftPct:d,bare:m}})}var Lt="chromacal-panel-theme-preset",ae=5;function zt(i,t){let e=i.replace("#",""),s=parseInt(e,16),n=s>>16&255,r=s>>8&255,o=s&255;return`rgba(${n}, ${r}, ${o}, ${t})`}var v=class extends E{constructor(){super(...arguments);this.narrow=!1;this._themePreset="native";this._skipFilter="";this._manageSkipsOpen=!1;this._controlsOpen=!1}connectedCallback(){super.connectedCallback();let e=localStorage.getItem(Lt);e&&lt.includes(e)&&(this._themePreset=e),this._applyThemeAttribute()}_applyThemeAttribute(){this._themePreset==="native"?this.removeAttribute("data-theme"):this.setAttribute("data-theme",this._themePreset)}_onThemeChange(e){let s=e.target.value;this._themePreset=s,localStorage.setItem(Lt,s),this._applyThemeAttribute()}_callService(e,s,n){n&&this.hass.callService(e,s,{entity_id:n})}_pressButton(e){this._callService("button","press",e)}_toggleSwitch(e,s){this._callService("switch",s?"turn_off":"turn_on",e)}render(){if(!this.hass)return p;let e=Tt(this.hass);return u`
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
                ${lt.map(s=>u`<option value=${s} ?selected=${s===this._themePreset}>
                    ${Pt[s]}
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
                  ${e.lights.map(s=>this._renderLightCard(s))}
                </section>`}

            <section class="upcoming-section">
              <h2>Upcoming Events</h2>
              ${e.upcomingEvents.length===0?u`<p class="muted">No events in the next 45 days for your selected categories.</p>`:u`<div class="upcoming-list">
                    ${e.upcomingEvents.map(s=>this._renderUpcomingRow(s))}
                  </div>`}
            </section>
          </main>

          <aside class="side-col">
            <section class="skip-section">
              <h2>Tonight's Skips</h2>
              ${e.tonightSkips.length===0?u`<p class="muted">Nothing skipped tonight.</p>`:u`<div class="chip-row">
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
    `}_formatEventDate(e){return new Date(`${e}T00:00:00`).toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"})}_renderUpcomingRow(e){let s=e.permanentSkip,n=e.tonightSkip;return u`
      <div class="upcoming-row ${e.isToday?"today":""} ${s?.isOn?"skipped":""}">
        <span class="up-date">${e.isToday?"TODAY":this._formatEventDate(e.date)}</span>
        <span class="up-icon">${e.icon}</span>
        <span class="up-name">${e.name}</span>
        <span class="up-badge">${e.category}</span>
        <span class="up-chips">
          ${e.colors.map(r=>u`<span class="up-chip" style="background:${r}"></span>`)}
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
        ${n?u`<button
              class="up-action-btn ${n.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(n.entityId,n.isOn)}
              title=${n.isOn?"Skipped tonight -- click to restore":"Skip for tonight only (resets at midnight)"}
            >
              🌙
            </button>`:p}
        ${s?u`<button
              class="up-action-btn ${s.isOn?"active":""}"
              @click=${()=>this._toggleSwitch(s.entityId,s.isOn)}
              title=${s.isOn?"Re-enable -- this event will run again":"Permanently skip this event"}
            >
              ${s.isOn?"\u2298":"\u25CB"}
            </button>`:p}
      </div>
    `}_renderSkipChip(e){return u`
      <button
        class="chip ${e.isOn?"skipped":""}"
        @click=${()=>this._toggleSwitch(e.entityId,e.isOn)}
        title=${e.isOn?"Skipped -- click to restore":"Click to skip"}
      >
        ${e.eventName}
      </button>
    `}_renderOrb(e,s){let n=e.currentColors[0],r=e.currentColors.length>=ae,o=n?`background: radial-gradient(circle at 38% 30%, rgba(255,255,255,.45) 0%, ${n} 45%, rgba(0,0,0,.5) 100%); box-shadow: 0 0 ${s==="full"?"24px":"12px"} ${zt(n,.627)}, 0 0 ${s==="full"?"46px":"23px"} ${zt(n,.208)};`:"";return u`<div class="orb ${s} ${r?"spinning":""}" style=${o}></div>`}_renderLightCard(e){if(this.narrow)return u`
        <div class="light-card compact">
          ${this._renderOrb(e,"compact")}
          <div class="compact-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline compact">${e.currentEventName??"\u2014"}</span>
          </div>
        </div>
      `;let s=Ht(e,new Date().getHours()+new Date().getMinutes()/60);return u`
      <div class="light-card">
        <div class="card-top">
          ${this._renderOrb(e,"full")}
          <div class="card-info">
            <span class="light-name-eyebrow">${e.lightName}</span>
            <span class="event-name-headline">${e.currentEventName??"No active event"}</span>
            ${e.currentStart&&e.currentEnd?u`<span class="event-time-range"
                  >${e.currentStart}&ndash;${e.currentEnd}</span
                >`:p}
          </div>
          ${e.forceWhiteEntityId?u`<button
                class="force-white-btn"
                @click=${()=>this._pressButton(e.forceWhiteEntityId)}
              >
                Force White
              </button>`:p}
        </div>
        ${e.segments.length>0?u`<div class="timeline-wrapper">
              <div class="timeline">
                ${e.segments.map(n=>{let{leftPct:r,widthPct:o}=Ut(n.startTime,n.endTime),l=n.name===e.currentEventName;return u`<div
                    class="timeline-seg ${l?"current":""}"
                    style="left:${r}%; width:${o}%; background:${n.colors[0]??"var(--cc-s2)"}"
                    title="${n.name} (${n.startTime}–${n.endTime})"
                  ></div>`})}
              </div>
              <div class="timeline-marks">
                ${s.map(n=>u`
                    <div class="tl-mark" style="left:${n.leftPct}%">
                      <div class="tl-mark-line"></div>
                      ${n.bare?p:u`<span class="tl-mark-lbl ${n.emphasize?"hl":""}"
                              >${n.label}</span
                            ><span class="tl-mark-lbl ${n.emphasize?"hl":""}">${n.time}</span>`}
                    </div>
                  `)}
              </div>
            </div>`:p}
      </div>
    `}};v.styles=[Ot,Ct,O`
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
    `],_([N({attribute:!1})],v.prototype,"hass",2),_([N({type:Boolean})],v.prototype,"narrow",2),_([N({attribute:!1})],v.prototype,"panel",2),_([B()],v.prototype,"_themePreset",2),_([B()],v.prototype,"_skipFilter",2),_([B()],v.prototype,"_manageSkipsOpen",2),_([B()],v.prototype,"_controlsOpen",2),v=_([Mt("chromacal-panel")],v);export{v as ChromaCalPanel};

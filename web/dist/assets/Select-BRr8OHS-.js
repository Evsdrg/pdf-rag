import{$ as e,A as t,An as n,Bt as r,C as i,Cn as a,Ct as o,D as s,Dn as c,Et as l,F as u,Ft as d,Gt as f,H as p,Ht as m,It as h,J as g,Ln as _,Lt as v,Nt as y,O as b,On as x,P as S,Pn as C,R as w,Rt as T,S as E,T as D,Tt as O,U as k,Ut as A,V as j,Vt as M,Wt as N,Yt as P,Zt as F,_t as I,at as L,bn as R,bt as z,ct as ee,dn as te,dt as B,et as V,f as H,fn as U,gn as W,gt as G,hn as ne,it as K,lt as re,mn as q,pn as J,rn as Y,rt as X,s as Z,st as ie,tn as Q,tt as ae,un as $,v as oe,vn as se,vt as ce,w as le,xt as ue,yn as de,yt as fe}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{A as pe,O as me,j as he,k as ge}from"./api-GVzHhqB2.js";import{C as _e,D as ve,E as ye,I as be,L as xe,N as Se,S as Ce,T as we,m as Te,w as Ee,y as De}from"./index-BgAh03Vf.js";function Oe(e){return e&-e}var ke=class{constructor(e,t){this.l=e,this.min=t;let n=Array(e+1);for(let t=0;t<e+1;++t)n[t]=0;this.ft=n}add(e,t){if(t===0)return;let{l:n,ft:r}=this;for(e+=1;e<=n;)r[e]+=t,e+=Oe(e)}get(e){return this.sum(e+1)-this.sum(e)}sum(e){if(e===void 0&&(e=this.l),e<=0)return 0;let{ft:t,min:n,l:r}=this;if(e>r)throw Error("[FinweckTree.sum]: `i` is larger than length.");let i=e*n;for(;e>0;)i+=t[e],e-=Oe(e);return i}getBound(e){let t=0,n=this.l;for(;n>t;){let r=Math.floor((t+n)/2),i=this.sum(r);if(i>e){n=r;continue}if(i<e){if(t===r)return this.sum(t+1)<=e?t+1:r;t=r}else return r}return t}},Ae;function je(){return typeof document>`u`?!1:(Ae===void 0&&(Ae=`matchMedia`in window&&window.matchMedia(`(pointer:coarse)`).matches),Ae)}var Me;function Ne(){return typeof document>`u`?1:(Me===void 0&&(Me=`chrome`in window?window.devicePixelRatio:1),Me)}var Pe=`VVirtualListXScroll`;function Fe({columnsRef:e,renderColRef:t,renderItemWithColsRef:n}){let r=C(0),i=C(0),s=Y(()=>{let t=e.value;if(t.length===0)return null;let n=new ke(t.length,0);return t.forEach((e,t)=>{n.add(t,e.width)}),n}),c=o(()=>{let e=s.value;return e===null?0:Math.max(e.getBound(i.value)-1,0)}),l=e=>{let t=s.value;return t===null?0:t.sum(e)},u=o(()=>{let t=s.value;return t===null?0:Math.min(t.getBound(i.value+r.value)+1,e.value.length-1)});return a(Pe,{startIndexRef:c,endIndexRef:u,columnsRef:e,renderColRef:t,renderItemWithColsRef:n,getLeft:l}),{listWidthRef:r,scrollLeftRef:i}}var Ie=$({name:`VirtualListRow`,props:{index:{type:Number,required:!0},item:{type:Object,required:!0}},setup(){let{startIndexRef:e,endIndexRef:t,columnsRef:n,getLeft:r,renderColRef:i,renderItemWithColsRef:a}=J(Pe);return{startIndex:e,endIndex:t,columns:n,renderCol:i,renderItemWithCols:a,getLeft:r}},render(){let{startIndex:e,endIndex:t,columns:n,renderCol:r,renderItemWithCols:i,getLeft:a,item:o}=this;if(i!=null)return i({itemIndex:this.index,startColIndex:e,endColIndex:t,allColumns:n,item:o,getLeft:a});if(r!=null){let i=[];for(let s=e;s<=t;++s){let e=n[s];i.push(r({column:e,left:a(s),item:o}))}return i}return null}}),Le=X(`.v-vl`,{maxHeight:`inherit`,height:`100%`,overflow:`auto`,minWidth:`1px`},[X(`&:not(.v-vl--show-scrollbar)`,{scrollbarWidth:`none`},[X(`&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb`,{width:0,height:0,display:`none`})])]),Re=$({name:`VirtualList`,inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},columns:{type:Array,default:()=>[]},renderCol:Function,renderItemWithCols:Function,items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:`div`},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:`key`},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(e){let t=L();Le.mount({id:`vueuc/virtual-list`,head:!0,anchorMetaName:K,ssr:t}),R(()=>{let{defaultScrollIndex:t,defaultScrollKey:n}=e;t==null?n!=null&&b({key:n}):b({index:t})});let n=!1,r=!1;W(()=>{if(n=!1,!r){r=!0;return}b({top:m.value,left:s.value})}),de(()=>{n=!0,r||=!0});let i=o(()=>{if(e.renderCol==null&&e.renderItemWithCols==null||e.columns.length===0)return;let t=0;return e.columns.forEach(e=>{t+=e.width}),t}),a=Y(()=>{let t=new Map,{keyField:n}=e;return e.items.forEach((e,r)=>{t.set(e[n],r)}),t}),{scrollLeftRef:s,listWidthRef:c}=Fe({columnsRef:_(e,`columns`),renderColRef:_(e,`renderCol`),renderItemWithColsRef:_(e,`renderItemWithCols`)}),l=C(null),u=C(void 0),d=new Map,f=Y(()=>{let{items:t,itemSize:n,keyField:r}=e,i=new ke(t.length,n);return t.forEach((e,t)=>{let n=e[r],a=d.get(n);a!==void 0&&i.add(t,a)}),i}),p=C(0),m=C(0),g=o(()=>Math.max(f.value.getBound(m.value-y(e.paddingTop))-1,0)),v=Y(()=>{let{value:t}=u;if(t===void 0)return[];let{items:n,itemSize:r}=e,i=g.value,a=Math.min(i+Math.ceil(t/r+1),n.length-1),o=[];for(let e=i;e<=a;++e)o.push(n[e]);return o}),b=(e,t)=>{if(typeof e==`number`){E(e,t,`auto`);return}let{left:n,top:r,index:i,key:o,position:s,behavior:c,debounce:l=!0}=e;if(n!==void 0||r!==void 0)E(n,r,c);else if(i!==void 0)w(i,c,l);else if(o!==void 0){let e=a.value.get(o);e!==void 0&&w(e,c,l)}else s===`bottom`?E(0,2**53-1,c):s===`top`&&E(0,0,c)},x,S=null;function w(t,n,r){let{value:i}=f,a=i.sum(t)+y(e.paddingTop);if(!r)l.value.scrollTo({left:0,top:a,behavior:n});else{x=t,S!==null&&window.clearTimeout(S),S=window.setTimeout(()=>{x=void 0,S=null},16);let{scrollTop:e,offsetHeight:r}=l.value;if(a>e){let o=i.get(t);a+o<=e+r||l.value.scrollTo({left:0,top:a+o-r,behavior:n})}else l.value.scrollTo({left:0,top:a,behavior:n})}}function E(e,t,n){l.value.scrollTo({left:e,top:t,behavior:n})}function D(t,r){if(n||e.ignoreItemResize||P(r.target))return;let{value:i}=f,o=a.value.get(t),s=i.get(o),c=r.borderBoxSize?.[0]?.blockSize??r.contentRect.height;if(c===s)return;c-e.itemSize===0?d.delete(t):d.set(t,c-e.itemSize);let u=c-s;if(u===0)return;i.add(o,u);let m=l.value;if(m!=null){if(x===void 0){let e=i.sum(o);m.scrollTop>e&&m.scrollBy(0,u)}else(o<x||o===x&&c+i.sum(o)>m.scrollTop+m.offsetHeight)&&m.scrollBy(0,u);N()}p.value++}let O=!je(),k=!1;function A(t){var n;(n=e.onScroll)==null||n.call(e,t),(!O||!k)&&N()}function j(t){var n;if((n=e.onWheel)==null||n.call(e,t),O){let e=l.value;if(e!=null){if(t.deltaX===0&&(e.scrollTop===0&&t.deltaY<=0||e.scrollTop+e.offsetHeight>=e.scrollHeight&&t.deltaY>=0))return;t.preventDefault(),e.scrollTop+=t.deltaY/Ne(),e.scrollLeft+=t.deltaX/Ne(),N(),k=!0,T(()=>{k=!1})}}}function M(t){if(n||P(t.target))return;if(e.renderCol==null&&e.renderItemWithCols==null){if(t.contentRect.height===u.value)return}else if(t.contentRect.height===u.value&&t.contentRect.width===c.value)return;u.value=t.contentRect.height,c.value=t.contentRect.width;let{onResize:r}=e;r!==void 0&&r(t)}function N(){let{value:e}=l;e!=null&&(m.value=e.scrollTop,s.value=e.scrollLeft)}function P(e){let t=e;for(;t!==null;){if(t.style.display===`none`)return!0;t=t.parentElement}return!1}return{listHeight:u,listStyle:{overflow:`auto`},keyToIndex:a,itemsStyle:Y(()=>{let{itemResizable:t}=e,n=h(f.value.sum());return p.value,[e.itemsStyle,{boxSizing:`content-box`,width:h(i.value),height:t?``:n,minHeight:t?n:``,paddingTop:h(e.paddingTop),paddingBottom:h(e.paddingBottom)}]}),visibleItemsStyle:Y(()=>(p.value,{transform:`translateY(${h(f.value.sum(g.value))})`})),viewportItems:v,listElRef:l,itemsElRef:C(null),scrollTo:b,handleListResize:M,handleListScroll:A,handleListWheel:j,handleItemResize:D}},render(){let{itemResizable:t,keyField:n,keyToIndex:r,visibleItemsTag:i}=this;return U(e,{onResize:this.handleListResize},{default:()=>{var a;return U(`div`,q(this.$attrs,{class:[`v-vl`,this.showScrollbar&&`v-vl--show-scrollbar`],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:`listElRef`}),[this.items.length===0?(a=this.$slots).empty?.call(a):U(`div`,{ref:`itemsElRef`,class:`v-vl-items`,style:this.itemsStyle},[U(i,Object.assign({class:`v-vl-visible-items`,style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>{let{renderCol:i,renderItemWithCols:a}=this;return this.viewportItems.map(o=>{let s=o[n],c=r.get(s),l=i==null?void 0:U(Ie,{index:c,item:o}),u=a==null?void 0:U(Ie,{index:c,item:o}),d=this.$slots.default({item:o,renderedCols:l,renderedItemWithCols:u,index:c})[0];return t?U(e,{key:s,onResize:e=>this.handleItemResize(s,e)},{default:()=>d}):(d.key=s,d)})}})])])}})}});function ze(e,t){t&&(R(()=>{let{value:n}=e;n&&V.registerHandler(n,t)}),c(e,(e,t)=>{t&&V.unregisterHandler(t)},{deep:!1}),se(()=>{let{value:t}=e;t&&V.unregisterHandler(t)}))}var Be=new WeakSet;function Ve(e){Be.add(e)}function He(e){return!Be.has(e)}function Ue(e){switch(typeof e){case`string`:return e||void 0;case`number`:return String(e);default:return}}function We(e){let t=e.filter(e=>e!==void 0);if(t.length!==0)return t.length===1?t[0]:t=>{e.forEach(e=>{e&&e(t)})}}var Ge=$({name:`Checkmark`,render(){return U(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 16 16`},U(`g`,{fill:`none`},U(`path`,{d:`M14.046 3.486a.75.75 0 0 1-.032 1.06l-7.93 7.474a.85.85 0 0 1-1.188-.022l-2.68-2.72a.75.75 0 1 1 1.068-1.053l2.234 2.267l7.468-7.038a.75.75 0 0 1 1.06.032z`,fill:`currentColor`})))}}),Ke=$({name:`ChevronDown`,render(){return U(`svg`,{viewBox:`0 0 16 16`,fill:`none`,xmlns:`http://www.w3.org/2000/svg`},U(`path`,{d:`M3.14645 5.64645C3.34171 5.45118 3.65829 5.45118 3.85355 5.64645L8 9.79289L12.1464 5.64645C12.3417 5.45118 12.6583 5.45118 12.8536 5.64645C13.0488 5.84171 13.0488 6.15829 12.8536 6.35355L8.35355 10.8536C8.15829 11.0488 7.84171 11.0488 7.64645 10.8536L3.14645 6.35355C2.95118 6.15829 2.95118 5.84171 3.14645 5.64645Z`,fill:`currentColor`}))}}),qe=i(`clear`,()=>U(`svg`,{viewBox:`0 0 16 16`,version:`1.1`,xmlns:`http://www.w3.org/2000/svg`},U(`g`,{stroke:`none`,"stroke-width":`1`,fill:`none`,"fill-rule":`evenodd`},U(`g`,{fill:`currentColor`,"fill-rule":`nonzero`},U(`path`,{d:`M8,2 C11.3137085,2 14,4.6862915 14,8 C14,11.3137085 11.3137085,14 8,14 C4.6862915,14 2,11.3137085 2,8 C2,4.6862915 4.6862915,2 8,2 Z M6.5343055,5.83859116 C6.33943736,5.70359511 6.07001296,5.72288026 5.89644661,5.89644661 L5.89644661,5.89644661 L5.83859116,5.9656945 C5.70359511,6.16056264 5.72288026,6.42998704 5.89644661,6.60355339 L5.89644661,6.60355339 L7.293,8 L5.89644661,9.39644661 L5.83859116,9.4656945 C5.70359511,9.66056264 5.72288026,9.92998704 5.89644661,10.1035534 L5.89644661,10.1035534 L5.9656945,10.1614088 C6.16056264,10.2964049 6.42998704,10.2771197 6.60355339,10.1035534 L6.60355339,10.1035534 L8,8.707 L9.39644661,10.1035534 L9.4656945,10.1614088 C9.66056264,10.2964049 9.92998704,10.2771197 10.1035534,10.1035534 L10.1035534,10.1035534 L10.1614088,10.0343055 C10.2964049,9.83943736 10.2771197,9.57001296 10.1035534,9.39644661 L10.1035534,9.39644661 L8.707,8 L10.1035534,6.60355339 L10.1614088,6.5343055 C10.2964049,6.33943736 10.2771197,6.07001296 10.1035534,5.89644661 L10.1035534,5.89644661 L10.0343055,5.83859116 C9.83943736,5.70359511 9.57001296,5.72288026 9.39644661,5.89644661 L9.39644661,5.89644661 L8,7.293 L6.60355339,5.89644661 Z`}))))),Je=$({name:`Empty`,render(){return U(`svg`,{viewBox:`0 0 28 28`,fill:`none`,xmlns:`http://www.w3.org/2000/svg`},U(`path`,{d:`M26 7.5C26 11.0899 23.0899 14 19.5 14C15.9101 14 13 11.0899 13 7.5C13 3.91015 15.9101 1 19.5 1C23.0899 1 26 3.91015 26 7.5ZM16.8536 4.14645C16.6583 3.95118 16.3417 3.95118 16.1464 4.14645C15.9512 4.34171 15.9512 4.65829 16.1464 4.85355L18.7929 7.5L16.1464 10.1464C15.9512 10.3417 15.9512 10.6583 16.1464 10.8536C16.3417 11.0488 16.6583 11.0488 16.8536 10.8536L19.5 8.20711L22.1464 10.8536C22.3417 11.0488 22.6583 11.0488 22.8536 10.8536C23.0488 10.6583 23.0488 10.3417 22.8536 10.1464L20.2071 7.5L22.8536 4.85355C23.0488 4.65829 23.0488 4.34171 22.8536 4.14645C22.6583 3.95118 22.3417 3.95118 22.1464 4.14645L19.5 6.79289L16.8536 4.14645Z`,fill:`currentColor`}),U(`path`,{d:`M25 22.75V12.5991C24.5572 13.0765 24.053 13.4961 23.5 13.8454V16H17.5L17.3982 16.0068C17.0322 16.0565 16.75 16.3703 16.75 16.75C16.75 18.2688 15.5188 19.5 14 19.5C12.4812 19.5 11.25 18.2688 11.25 16.75L11.2432 16.6482C11.1935 16.2822 10.8797 16 10.5 16H4.5V7.25C4.5 6.2835 5.2835 5.5 6.25 5.5H12.2696C12.4146 4.97463 12.6153 4.47237 12.865 4H6.25C4.45507 4 3 5.45507 3 7.25V22.75C3 24.5449 4.45507 26 6.25 26H21.75C23.5449 26 25 24.5449 25 22.75ZM4.5 22.75V17.5H9.81597L9.85751 17.7041C10.2905 19.5919 11.9808 21 14 21L14.215 20.9947C16.2095 20.8953 17.842 19.4209 18.184 17.5H23.5V22.75C23.5 23.7165 22.7165 24.5 21.75 24.5H6.25C5.2835 24.5 4.5 23.7165 4.5 22.75Z`,fill:`currentColor`}))}}),Ye=$({name:`Eye`,render(){return U(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 512 512`},U(`path`,{d:`M255.66 112c-77.94 0-157.89 45.11-220.83 135.33a16 16 0 0 0-.27 17.77C82.92 340.8 161.8 400 255.66 400c92.84 0 173.34-59.38 221.79-135.25a16.14 16.14 0 0 0 0-17.47C428.89 172.28 347.8 112 255.66 112z`,fill:`none`,stroke:`currentColor`,"stroke-linecap":`round`,"stroke-linejoin":`round`,"stroke-width":`32`}),U(`circle`,{cx:`256`,cy:`256`,r:`80`,fill:`none`,stroke:`currentColor`,"stroke-miterlimit":`10`,"stroke-width":`32`}))}}),Xe=$({name:`EyeOff`,render(){return U(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 512 512`},U(`path`,{d:`M432 448a15.92 15.92 0 0 1-11.31-4.69l-352-352a16 16 0 0 1 22.62-22.62l352 352A16 16 0 0 1 432 448z`,fill:`currentColor`}),U(`path`,{d:`M255.66 384c-41.49 0-81.5-12.28-118.92-36.5c-34.07-22-64.74-53.51-88.7-91v-.08c19.94-28.57 41.78-52.73 65.24-72.21a2 2 0 0 0 .14-2.94L93.5 161.38a2 2 0 0 0-2.71-.12c-24.92 21-48.05 46.76-69.08 76.92a31.92 31.92 0 0 0-.64 35.54c26.41 41.33 60.4 76.14 98.28 100.65C162 402 207.9 416 255.66 416a239.13 239.13 0 0 0 75.8-12.58a2 2 0 0 0 .77-3.31l-21.58-21.58a4 4 0 0 0-3.83-1a204.8 204.8 0 0 1-51.16 6.47z`,fill:`currentColor`}),U(`path`,{d:`M490.84 238.6c-26.46-40.92-60.79-75.68-99.27-100.53C349 110.55 302 96 255.66 96a227.34 227.34 0 0 0-74.89 12.83a2 2 0 0 0-.75 3.31l21.55 21.55a4 4 0 0 0 3.88 1a192.82 192.82 0 0 1 50.21-6.69c40.69 0 80.58 12.43 118.55 37c34.71 22.4 65.74 53.88 89.76 91a.13.13 0 0 1 0 .16a310.72 310.72 0 0 1-64.12 72.73a2 2 0 0 0-.15 2.95l19.9 19.89a2 2 0 0 0 2.7.13a343.49 343.49 0 0 0 68.64-78.48a32.2 32.2 0 0 0-.1-34.78z`,fill:`currentColor`}),U(`path`,{d:`M256 160a95.88 95.88 0 0 0-21.37 2.4a2 2 0 0 0-1 3.38l112.59 112.56a2 2 0 0 0 3.38-1A96 96 0 0 0 256 160z`,fill:`currentColor`}),U(`path`,{d:`M165.78 233.66a2 2 0 0 0-3.38 1a96 96 0 0 0 115 115a2 2 0 0 0 1-3.38z`,fill:`currentColor`}))}}),Ze=M(`base-clear`,`
 flex-shrink: 0;
 height: 1em;
 width: 1em;
 position: relative;
`,[r(`>`,[m(`clear`,`
 font-size: var(--n-clear-size);
 height: 1em;
 width: 1em;
 cursor: pointer;
 color: var(--n-clear-color);
 transition: color .3s var(--n-bezier);
 display: flex;
 `,[r(`&:hover`,`
 color: var(--n-clear-color-hover)!important;
 `),r(`&:active`,`
 color: var(--n-clear-color-pressed)!important;
 `)]),m(`placeholder`,`
 display: flex;
 `),m(`clear, placeholder`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 `,[E({originalTransform:`translateX(-50%) translateY(-50%)`,left:`50%`,top:`50%`})])])]),Qe=$({name:`BaseClear`,props:{clsPrefix:{type:String,required:!0},show:Boolean,onClear:Function},setup(e){return b(`-base-clear`,Ze,_(e,`clsPrefix`)),{handleMouseDown(e){e.preventDefault()}}},render(){let{clsPrefix:e}=this;return U(`div`,{class:`${e}-base-clear`},U(le,null,{default:()=>{var t;return this.show?U(`div`,{key:`dismiss`,class:`${e}-base-clear__clear`,onClick:this.onClear,onMousedown:this.handleMouseDown,"data-clear":!0},j(this.$slots.icon,()=>[U(D,{clsPrefix:e},{default:()=>U(qe,null)})])):U(`div`,{key:`icon`,class:`${e}-base-clear__placeholder`},(t=this.$slots).placeholder?.call(t))}}))}}),$e=$({props:{onFocus:Function,onBlur:Function},setup(e){return()=>U(`div`,{style:`width: 0; height: 0`,tabindex:0,onFocus:e.onFocus,onBlur:e.onBlur})}}),et=M(`empty`,`
 display: flex;
 flex-direction: column;
 align-items: center;
 font-size: var(--n-font-size);
`,[m(`icon`,`
 width: var(--n-icon-size);
 height: var(--n-icon-size);
 font-size: var(--n-icon-size);
 line-height: var(--n-icon-size);
 color: var(--n-icon-color);
 transition:
 color .3s var(--n-bezier);
 `,[r(`+`,[m(`description`,`
 margin-top: 8px;
 `)])]),m(`description`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),m(`extra`,`
 text-align: center;
 transition: color .3s var(--n-bezier);
 margin-top: 12px;
 color: var(--n-extra-text-color);
 `)]),tt=Object.assign(Object.assign({},s.props),{description:String,showDescription:{type:Boolean,default:!0},showIcon:{type:Boolean,default:!0},size:{type:String,default:`medium`},renderIcon:Function}),nt=$({name:`Empty`,props:tt,slots:Object,setup(e){let{mergedClsPrefixRef:t,inlineThemeDisabled:n,mergedComponentPropsRef:r}=u(e),i=s(`Empty`,`-empty`,et,we,e,t),{localeRef:a}=pe(`Empty`),o=Y(()=>e.description??r?.value?.Empty?.description),c=Y(()=>r?.value?.Empty?.renderIcon||(()=>U(Je,null))),l=Y(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{[f(`iconSize`,t)]:r,[f(`fontSize`,t)]:a,textColor:o,iconColor:s,extraTextColor:c}}=i.value;return{"--n-icon-size":r,"--n-font-size":a,"--n-bezier":n,"--n-text-color":o,"--n-icon-color":s,"--n-extra-text-color":c}}),d=n?S(`empty`,Y(()=>{let t=``,{size:n}=e;return t+=n[0],t}),l,e):void 0;return{mergedClsPrefix:t,mergedRenderIcon:c,localizedDescription:Y(()=>o.value||a.value.description),cssVars:n?void 0:l,themeClass:d?.themeClass,onRender:d?.onRender}},render(){let{$slots:e,mergedClsPrefix:t,onRender:n}=this;return n?.(),U(`div`,{class:[`${t}-empty`,this.themeClass],style:this.cssVars},this.showIcon?U(`div`,{class:`${t}-empty__icon`},e.icon?e.icon():U(D,{clsPrefix:t},{default:this.mergedRenderIcon})):null,this.showDescription?U(`div`,{class:`${t}-empty__description`},e.default?e.default():this.localizedDescription):null,e.extra?U(`div`,{class:`${t}-empty__extra`},e.extra()):null)}}),rt=$({name:`NBaseSelectGroupHeader`,props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(){let{renderLabelRef:e,renderOptionRef:t,labelFieldRef:n,nodePropsRef:r}=J(I);return{labelField:n,nodeProps:r,renderLabel:e,renderOption:t}},render(){let{clsPrefix:e,renderLabel:t,renderOption:n,nodeProps:r,tmNode:{rawNode:i}}=this,a=r?.(i),o=t?t(i,!1):Se(i[this.labelField],i,!1),s=U(`div`,Object.assign({},a,{class:[`${e}-base-select-group-header`,a?.class]}),o);return i.render?i.render({node:s,option:i}):n?n({node:s,option:i,selected:!1}):s}});function it(e,t){return U(P,{name:`fade-in-scale-up-transition`},{default:()=>e?U(D,{clsPrefix:t,class:`${t}-base-select-option__check`},{default:()=>U(Ge)}):null})}var at=$({name:`NBaseSelectOption`,props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(e){let{valueRef:t,pendingTmNodeRef:n,multipleRef:r,valueSetRef:i,renderLabelRef:a,renderOptionRef:s,labelFieldRef:c,valueFieldRef:l,showCheckmarkRef:u,nodePropsRef:d,handleOptionClick:f,handleOptionMouseEnter:p}=J(I),m=o(()=>{let{value:t}=n;return t?e.tmNode.key===t.key:!1});function h(t){let{tmNode:n}=e;n.disabled||f(t,n)}function g(t){let{tmNode:n}=e;n.disabled||p(t,n)}function _(t){let{tmNode:n}=e,{value:r}=m;n.disabled||r||p(t,n)}return{multiple:r,isGrouped:o(()=>{let{tmNode:t}=e,{parent:n}=t;return n&&n.rawNode.type===`group`}),showCheckmark:u,nodeProps:d,isPending:m,isSelected:o(()=>{let{value:n}=t,{value:a}=r;if(n===null)return!1;let o=e.tmNode.rawNode[l.value];if(a){let{value:e}=i;return e.has(o)}return n===o}),labelField:c,renderLabel:a,renderOption:s,handleMouseMove:_,handleMouseEnter:g,handleClick:h}},render(){let{clsPrefix:e,tmNode:{rawNode:t},isSelected:n,isPending:r,isGrouped:i,showCheckmark:a,nodeProps:o,renderOption:s,renderLabel:c,handleClick:l,handleMouseEnter:u,handleMouseMove:d}=this,f=it(n,e),p=c?[c(t,n),a&&f]:[Se(t[this.labelField],t,n),a&&f],m=o?.(t),h=U(`div`,Object.assign({},m,{class:[`${e}-base-select-option`,t.class,m?.class,{[`${e}-base-select-option--disabled`]:t.disabled,[`${e}-base-select-option--selected`]:n,[`${e}-base-select-option--grouped`]:i,[`${e}-base-select-option--pending`]:r,[`${e}-base-select-option--show-checkmark`]:a}],style:[m?.style||``,t.style||``],onClick:We([l,m?.onClick]),onMouseenter:We([u,m?.onMouseenter]),onMousemove:We([d,m?.onMousemove])}),U(`div`,{class:`${e}-base-select-option__content`},p));return t.render?t.render({node:h,option:t,selected:n}):s?s({node:h,option:t,selected:n}):h}}),ot=M(`base-select-menu`,`
 line-height: 1.5;
 outline: none;
 z-index: 0;
 position: relative;
 border-radius: var(--n-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-color);
`,[M(`scrollbar`,`
 max-height: var(--n-height);
 `),M(`virtual-list`,`
 max-height: var(--n-height);
 `),M(`base-select-option`,`
 min-height: var(--n-option-height);
 font-size: var(--n-option-font-size);
 display: flex;
 align-items: center;
 `,[m(`content`,`
 z-index: 1;
 white-space: nowrap;
 text-overflow: ellipsis;
 overflow: hidden;
 `)]),M(`base-select-group-header`,`
 min-height: var(--n-option-height);
 font-size: .93em;
 display: flex;
 align-items: center;
 `),M(`base-select-menu-option-wrapper`,`
 position: relative;
 width: 100%;
 `),m(`loading, empty`,`
 display: flex;
 padding: 12px 32px;
 flex: 1;
 justify-content: center;
 `),m(`loading`,`
 color: var(--n-loading-color);
 font-size: var(--n-loading-size);
 `),m(`header`,`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),m(`action`,`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-top: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),M(`base-select-group-header`,`
 position: relative;
 cursor: default;
 padding: var(--n-option-padding);
 color: var(--n-group-header-text-color);
 `),M(`base-select-option`,`
 cursor: pointer;
 position: relative;
 padding: var(--n-option-padding);
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 box-sizing: border-box;
 color: var(--n-option-text-color);
 opacity: 1;
 `,[A(`show-checkmark`,`
 padding-right: calc(var(--n-option-padding-right) + 20px);
 `),r(`&::before`,`
 content: "";
 position: absolute;
 left: 4px;
 right: 4px;
 top: 0;
 bottom: 0;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),r(`&:active`,`
 color: var(--n-option-text-color-pressed);
 `),A(`grouped`,`
 padding-left: calc(var(--n-option-padding-left) * 1.5);
 `),A(`pending`,[r(`&::before`,`
 background-color: var(--n-option-color-pending);
 `)]),A(`selected`,`
 color: var(--n-option-text-color-active);
 `,[r(`&::before`,`
 background-color: var(--n-option-color-active);
 `),A(`pending`,[r(`&::before`,`
 background-color: var(--n-option-color-active-pending);
 `)])]),A(`disabled`,`
 cursor: not-allowed;
 `,[N(`selected`,`
 color: var(--n-option-text-color-disabled);
 `),A(`selected`,`
 opacity: var(--n-option-opacity-disabled);
 `)]),m(`check`,`
 font-size: 16px;
 position: absolute;
 right: calc(var(--n-option-padding-right) - 4px);
 top: calc(50% - 7px);
 color: var(--n-option-check-color);
 transition: color .3s var(--n-bezier);
 `,[_e({enterScale:`0.5`})])])]),st=$({name:`InternalSelectMenu`,props:Object.assign(Object.assign({},s.props),{clsPrefix:{type:String,required:!0},scrollable:{type:Boolean,default:!0},treeMate:{type:Object,required:!0},multiple:Boolean,size:{type:String,default:`medium`},value:{type:[String,Number,Array],default:null},autoPending:Boolean,virtualScroll:{type:Boolean,default:!0},show:{type:Boolean,default:!0},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},loading:Boolean,focusable:Boolean,renderLabel:Function,renderOption:Function,nodeProps:Function,showCheckmark:{type:Boolean,default:!0},onMousedown:Function,onScroll:Function,onFocus:Function,onBlur:Function,onKeyup:Function,onKeydown:Function,onTabOut:Function,onMouseenter:Function,onMouseleave:Function,onResize:Function,resetMenuOnOptionsChange:{type:Boolean,default:!0},inlineThemeDisabled:Boolean,scrollbarProps:Object,onToggle:Function}),setup(e){let{mergedClsPrefixRef:n,mergedRtlRef:r,mergedComponentPropsRef:i}=u(e),o=t(`InternalSelectMenu`,r,n),l=s(`InternalSelectMenu`,`-internal-select-menu`,ot,Ee,e,_(e,`clsPrefix`)),p=C(null),m=C(null),h=C(null),g=Y(()=>e.treeMate.getFlattenedNodes()),v=Y(()=>ve(g.value)),b=C(null);function x(){let{treeMate:t}=e,n=null,{value:r}=e;r===null?n=t.getFirstAvailableNode():(n=e.multiple?t.getNode((r||[])[(r||[]).length-1]):t.getNode(r),(!n||n.disabled)&&(n=t.getFirstAvailableNode())),U(n||null)}function w(){let{value:t}=b;t&&!e.treeMate.getNode(t.key)&&(b.value=null)}let T;c(()=>e.show,t=>{t?T=c(()=>e.treeMate,()=>{e.resetMenuOnOptionsChange?(e.autoPending?x():w(),ne(W)):w()},{immediate:!0}):T?.()},{immediate:!0}),se(()=>{T?.()});let E=Y(()=>y(l.value.self[f(`optionHeight`,e.size)])),D=Y(()=>d(l.value.self[f(`padding`,e.size)])),O=Y(()=>e.multiple&&Array.isArray(e.value)?new Set(e.value):new Set),k=Y(()=>{let e=g.value;return e&&e.length===0}),A=Y(()=>i?.value?.Select?.renderEmpty);function j(t){let{onToggle:n}=e;n&&n(t)}function M(t){let{onScroll:n}=e;n&&n(t)}function N(e){var t;(t=h.value)==null||t.sync(),M(e)}function P(){var e;(e=h.value)==null||e.sync()}function F(){let{value:e}=b;return e||null}function L(e,t){t.disabled||U(t,!1)}function z(e,t){t.disabled||j(t)}function ee(t){var n;xe(t,`action`)||(n=e.onKeyup)==null||n.call(e,t)}function te(t){var n;xe(t,`action`)||(n=e.onKeydown)==null||n.call(e,t)}function B(t){var n;(n=e.onMousedown)==null||n.call(e,t),!e.focusable&&t.preventDefault()}function V(){let{value:e}=b;e&&U(e.getNext({loop:!0}),!0)}function H(){let{value:e}=b;e&&U(e.getPrev({loop:!0}),!0)}function U(e,t=!1){b.value=e,t&&W()}function W(){var t,n;let r=b.value;if(!r)return;let i=v.value(r.key);i!==null&&(e.virtualScroll?(t=m.value)==null||t.scrollTo({index:i}):(n=h.value)==null||n.scrollTo({index:i,elSize:E.value}))}function K(t){var n;p.value?.contains(t.target)&&((n=e.onFocus)==null||n.call(e,t))}function re(t){var n;p.value?.contains(t.relatedTarget)||(n=e.onBlur)==null||n.call(e,t)}a(I,{handleOptionMouseEnter:L,handleOptionClick:z,valueSetRef:O,pendingTmNodeRef:b,nodePropsRef:_(e,`nodeProps`),showCheckmarkRef:_(e,`showCheckmark`),multipleRef:_(e,`multiple`),valueRef:_(e,`value`),renderLabelRef:_(e,`renderLabel`),renderOptionRef:_(e,`renderOption`),labelFieldRef:_(e,`labelField`),valueFieldRef:_(e,`valueField`)}),a(G,p),R(()=>{let{value:e}=h;e&&e.sync()});let q=Y(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{height:r,borderRadius:i,color:a,groupHeaderTextColor:o,actionDividerColor:s,optionTextColorPressed:c,optionTextColor:u,optionTextColorDisabled:p,optionTextColorActive:m,optionOpacityDisabled:h,optionCheckColor:g,actionTextColor:_,optionColorPending:v,optionColorActive:y,loadingColor:b,loadingSize:x,optionColorActivePending:S,[f(`optionFontSize`,t)]:C,[f(`optionHeight`,t)]:w,[f(`optionPadding`,t)]:T}}=l.value;return{"--n-height":r,"--n-action-divider-color":s,"--n-action-text-color":_,"--n-bezier":n,"--n-border-radius":i,"--n-color":a,"--n-option-font-size":C,"--n-group-header-text-color":o,"--n-option-check-color":g,"--n-option-color-pending":v,"--n-option-color-active":y,"--n-option-color-active-pending":S,"--n-option-height":w,"--n-option-opacity-disabled":h,"--n-option-text-color":u,"--n-option-text-color-active":m,"--n-option-text-color-disabled":p,"--n-option-text-color-pressed":c,"--n-option-padding":T,"--n-option-padding-left":d(T,`left`),"--n-option-padding-right":d(T,`right`),"--n-loading-color":b,"--n-loading-size":x}}),{inlineThemeDisabled:J}=e,X=J?S(`internal-select-menu`,Y(()=>e.size[0]),q,e):void 0,Z={selfRef:p,next:V,prev:H,getPendingTmNode:F};return ze(p,e.onResize),Object.assign({mergedTheme:l,mergedClsPrefix:n,rtlEnabled:o,virtualListRef:m,scrollbarRef:h,itemSize:E,padding:D,flattenedNodes:g,empty:k,mergedRenderEmpty:A,virtualListContainer(){let{value:e}=m;return e?.listElRef},virtualListContent(){let{value:e}=m;return e?.itemsElRef},doScroll:M,handleFocusin:K,handleFocusout:re,handleKeyUp:ee,handleKeyDown:te,handleMouseDown:B,handleVirtualListResize:P,handleVirtualListScroll:N,cssVars:J?void 0:q,themeClass:X?.themeClass,onRender:X?.onRender},Z)},render(){let{$slots:e,virtualScroll:t,clsPrefix:n,mergedTheme:r,themeClass:i,onRender:a}=this;return a?.(),U(`div`,{ref:`selfRef`,tabindex:this.focusable?0:-1,class:[`${n}-base-select-menu`,`${n}-base-select-menu--${this.size}-size`,this.rtlEnabled&&`${n}-base-select-menu--rtl`,i,this.multiple&&`${n}-base-select-menu--multiple`],style:this.cssVars,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onKeyup:this.handleKeyUp,onKeydown:this.handleKeyDown,onMousedown:this.handleMouseDown,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},k(e.header,e=>e&&U(`div`,{class:`${n}-base-select-menu__header`,"data-header":!0,key:`header`},e)),this.loading?U(`div`,{class:`${n}-base-select-menu__loading`},U(oe,{clsPrefix:n,strokeWidth:20})):this.empty?U(`div`,{class:`${n}-base-select-menu__empty`,"data-empty":!0},j(e.empty,()=>[this.mergedRenderEmpty?.call(this)||U(nt,{theme:r.peers.Empty,themeOverrides:r.peerOverrides.Empty,size:this.size})])):U(H,Object.assign({ref:`scrollbarRef`,theme:r.peers.Scrollbar,themeOverrides:r.peerOverrides.Scrollbar,scrollable:this.scrollable,container:t?this.virtualListContainer:void 0,content:t?this.virtualListContent:void 0,onScroll:t?void 0:this.doScroll},this.scrollbarProps),{default:()=>t?U(Re,{ref:`virtualListRef`,class:`${n}-virtual-list`,items:this.flattenedNodes,itemSize:this.itemSize,showScrollbar:!1,paddingTop:this.padding.top,paddingBottom:this.padding.bottom,onResize:this.handleVirtualListResize,onScroll:this.handleVirtualListScroll,itemResizable:!0},{default:({item:e})=>e.isGroup?U(rt,{key:e.key,clsPrefix:n,tmNode:e}):e.ignored?null:U(at,{clsPrefix:n,key:e.key,tmNode:e})}):U(`div`,{class:`${n}-base-select-menu-option-wrapper`,style:{paddingTop:this.padding.top,paddingBottom:this.padding.bottom}},this.flattenedNodes.map(e=>e.isGroup?U(rt,{key:e.key,clsPrefix:n,tmNode:e}):U(at,{clsPrefix:n,key:e.key,tmNode:e})))}),k(e.action,e=>e&&[U(`div`,{class:`${n}-base-select-menu__action`,"data-action":!0,key:`action`},e),U($e,{onFocus:this.onTabOut,key:`focus-detector`})]))}}),ct=$({name:`InternalSelectionSuffix`,props:{clsPrefix:{type:String,required:!0},showArrow:{type:Boolean,default:void 0},showClear:{type:Boolean,default:void 0},loading:{type:Boolean,default:!1},onClear:Function},setup(e,{slots:t}){return()=>{let{clsPrefix:n}=e;return U(oe,{clsPrefix:n,class:`${n}-base-suffix`,strokeWidth:24,scale:.85,show:e.loading},{default:()=>e.showArrow?U(Qe,{clsPrefix:n,show:e.showClear,onClear:e.onClear},{placeholder:()=>U(D,{clsPrefix:n,class:`${n}-base-suffix__arrow`},{default:()=>j(t.default,()=>[U(Ke,null)])})}):null})}}}),lt=r([M(`base-selection`,`
 --n-padding-single: var(--n-padding-single-top) var(--n-padding-single-right) var(--n-padding-single-bottom) var(--n-padding-single-left);
 --n-padding-multiple: var(--n-padding-multiple-top) var(--n-padding-multiple-right) var(--n-padding-multiple-bottom) var(--n-padding-multiple-left);
 position: relative;
 z-index: auto;
 box-shadow: none;
 width: 100%;
 max-width: 100%;
 display: inline-block;
 vertical-align: bottom;
 border-radius: var(--n-border-radius);
 min-height: var(--n-height);
 line-height: 1.5;
 font-size: var(--n-font-size);
 `,[M(`base-loading`,`
 color: var(--n-loading-color);
 `),M(`base-selection-tags`,`min-height: var(--n-height);`),m(`border, state-border`,`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border: var(--n-border);
 border-radius: inherit;
 transition:
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `),m(`state-border`,`
 z-index: 1;
 border-color: #0000;
 `),M(`base-suffix`,`
 cursor: pointer;
 position: absolute;
 top: 50%;
 transform: translateY(-50%);
 right: 10px;
 `,[m(`arrow`,`
 font-size: var(--n-arrow-size);
 color: var(--n-arrow-color);
 transition: color .3s var(--n-bezier);
 `)]),M(`base-selection-overlay`,`
 display: flex;
 align-items: center;
 white-space: nowrap;
 pointer-events: none;
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 left: 0;
 padding: var(--n-padding-single);
 transition: color .3s var(--n-bezier);
 `,[m(`wrapper`,`
 flex-basis: 0;
 flex-grow: 1;
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),M(`base-selection-placeholder`,`
 color: var(--n-placeholder-color);
 `,[m(`inner`,`
 max-width: 100%;
 overflow: hidden;
 `)]),M(`base-selection-tags`,`
 cursor: pointer;
 outline: none;
 box-sizing: border-box;
 position: relative;
 z-index: auto;
 display: flex;
 padding: var(--n-padding-multiple);
 flex-wrap: wrap;
 align-items: center;
 width: 100%;
 vertical-align: bottom;
 background-color: var(--n-color);
 border-radius: inherit;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),M(`base-selection-label`,`
 height: var(--n-height);
 display: inline-flex;
 width: 100%;
 vertical-align: bottom;
 cursor: pointer;
 outline: none;
 z-index: auto;
 box-sizing: border-box;
 position: relative;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 border-radius: inherit;
 background-color: var(--n-color);
 align-items: center;
 `,[M(`base-selection-input`,`
 font-size: inherit;
 line-height: inherit;
 outline: none;
 cursor: pointer;
 box-sizing: border-box;
 border:none;
 width: 100%;
 padding: var(--n-padding-single);
 background-color: #0000;
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 caret-color: var(--n-caret-color);
 `,[m(`content`,`
 text-overflow: ellipsis;
 overflow: hidden;
 white-space: nowrap; 
 `)]),m(`render-label`,`
 color: var(--n-text-color);
 `)]),N(`disabled`,[r(`&:hover`,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-hover);
 border: var(--n-border-hover);
 `)]),A(`focus`,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-focus);
 border: var(--n-border-focus);
 `)]),A(`active`,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-active);
 border: var(--n-border-active);
 `),M(`base-selection-label`,`background-color: var(--n-color-active);`),M(`base-selection-tags`,`background-color: var(--n-color-active);`)])]),A(`disabled`,`cursor: not-allowed;`,[m(`arrow`,`
 color: var(--n-arrow-color-disabled);
 `),M(`base-selection-label`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[M(`base-selection-input`,`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 `),m(`render-label`,`
 color: var(--n-text-color-disabled);
 `)]),M(`base-selection-tags`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `),M(`base-selection-placeholder`,`
 cursor: not-allowed;
 color: var(--n-placeholder-color-disabled);
 `)]),M(`base-selection-input-tag`,`
 height: calc(var(--n-height) - 6px);
 line-height: calc(var(--n-height) - 6px);
 outline: none;
 display: none;
 position: relative;
 margin-bottom: 3px;
 max-width: 100%;
 vertical-align: bottom;
 `,[m(`input`,`
 font-size: inherit;
 font-family: inherit;
 min-width: 1px;
 padding: 0;
 background-color: #0000;
 outline: none;
 border: none;
 max-width: 100%;
 overflow: hidden;
 width: 1em;
 line-height: inherit;
 cursor: pointer;
 color: var(--n-text-color);
 caret-color: var(--n-caret-color);
 `),m(`mirror`,`
 position: absolute;
 left: 0;
 top: 0;
 white-space: pre;
 visibility: hidden;
 user-select: none;
 -webkit-user-select: none;
 opacity: 0;
 `)]),[`warning`,`error`].map(e=>A(`${e}-status`,[m(`state-border`,`border: var(--n-border-${e});`),N(`disabled`,[r(`&:hover`,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-hover-${e});
 border: var(--n-border-hover-${e});
 `)]),A(`active`,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-active-${e});
 border: var(--n-border-active-${e});
 `),M(`base-selection-label`,`background-color: var(--n-color-active-${e});`),M(`base-selection-tags`,`background-color: var(--n-color-active-${e});`)]),A(`focus`,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),M(`base-selection-popover`,`
 margin-bottom: -3px;
 display: flex;
 flex-wrap: wrap;
 margin-right: -8px;
 `),M(`base-selection-tag-wrapper`,`
 max-width: 100%;
 display: inline-flex;
 padding: 0 7px 3px 0;
 `,[r(`&:last-child`,`padding-right: 0;`),M(`tag`,`
 font-size: 14px;
 max-width: 100%;
 `,[m(`content`,`
 line-height: 1.25;
 text-overflow: ellipsis;
 overflow: hidden;
 `)])])]),ut=$({name:`InternalSelection`,props:Object.assign(Object.assign({},s.props),{clsPrefix:{type:String,required:!0},bordered:{type:Boolean,default:void 0},active:Boolean,pattern:{type:String,default:``},placeholder:String,selectedOption:{type:Object,default:null},selectedOptions:{type:Array,default:null},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},multiple:Boolean,filterable:Boolean,clearable:Boolean,disabled:Boolean,size:{type:String,default:`medium`},loading:Boolean,autofocus:Boolean,showArrow:{type:Boolean,default:!0},inputProps:Object,focused:Boolean,renderTag:Function,onKeydown:Function,onClick:Function,onBlur:Function,onFocus:Function,onDeleteOption:Function,maxTagCount:[String,Number],ellipsisTagPopoverProps:Object,onClear:Function,onPatternInput:Function,onPatternFocus:Function,onPatternBlur:Function,renderLabel:Function,status:String,inlineThemeDisabled:Boolean,ignoreComposition:{type:Boolean,default:!0},onResize:Function}),setup(e){let{mergedClsPrefixRef:n,mergedRtlRef:r}=u(e),i=t(`InternalSelection`,r,n),a=C(null),o=C(null),l=C(null),p=C(null),m=C(null),h=C(null),g=C(null),v=C(null),y=C(null),b=C(null),w=C(!1),T=C(!1),E=C(!1),D=s(`InternalSelection`,`-internal-selection`,lt,Ce,e,_(e,`clsPrefix`)),O=Y(()=>e.clearable&&!e.disabled&&(E.value||e.active)),k=Y(()=>e.selectedOption?e.renderTag?e.renderTag({option:e.selectedOption,handleClose:()=>{}}):e.renderLabel?e.renderLabel(e.selectedOption,!0):Se(e.selectedOption[e.labelField],e.selectedOption,!0):e.placeholder),A=Y(()=>{let t=e.selectedOption;if(t)return t[e.labelField]}),j=Y(()=>e.multiple?!!(Array.isArray(e.selectedOptions)&&e.selectedOptions.length):e.selectedOption!==null);function M(){var t;let{value:n}=a;if(n){let{value:r}=o;r&&(r.style.width=`${n.offsetWidth}px`,e.maxTagCount!==`responsive`&&((t=y.value)==null||t.sync({showAllItemsBeforeCalculate:!1})))}}function N(){let{value:e}=b;e&&(e.style.display=`none`)}function P(){let{value:e}=b;e&&(e.style.display=`inline-block`)}c(_(e,`active`),e=>{e||N()}),c(_(e,`pattern`),()=>{e.multiple&&ne(M)});function F(t){let{onFocus:n}=e;n&&n(t)}function I(t){let{onBlur:n}=e;n&&n(t)}function L(t){let{onDeleteOption:n}=e;n&&n(t)}function z(t){let{onClear:n}=e;n&&n(t)}function ee(t){let{onPatternInput:n}=e;n&&n(t)}function te(e){(!e.relatedTarget||!l.value?.contains(e.relatedTarget))&&F(e)}function B(e){l.value?.contains(e.relatedTarget)||I(e)}function V(e){z(e)}function H(){E.value=!0}function U(){E.value=!1}function W(t){!e.active||!e.filterable||t.target!==o.value&&t.preventDefault()}function G(e){L(e)}let K=C(!1);function re(t){if(t.key===`Backspace`&&!K.value&&!e.pattern.length){let{selectedOptions:t}=e;t?.length&&G(t[t.length-1])}}let q=null;function J(t){let{value:n}=a;n&&(n.textContent=t.target.value,M()),e.ignoreComposition&&K.value?q=t:ee(t)}function X(){K.value=!0}function Z(){K.value=!1,e.ignoreComposition&&ee(q),q=null}function ie(t){var n;T.value=!0,(n=e.onPatternFocus)==null||n.call(e,t)}function Q(t){var n;T.value=!1,(n=e.onPatternBlur)==null||n.call(e,t)}function ae(){var t,n;if(e.filterable)T.value=!1,(t=h.value)==null||t.blur(),(n=o.value)==null||n.blur();else if(e.multiple){let{value:e}=p;e?.blur()}else{let{value:e}=m;e?.blur()}}function $(){var t,n,r;e.filterable?(T.value=!1,(t=h.value)==null||t.focus()):e.multiple?(n=p.value)==null||n.focus():(r=m.value)==null||r.focus()}function oe(){let{value:e}=o;e&&(P(),e.focus())}function se(){let{value:e}=o;e&&e.blur()}function ce(e){let{value:t}=g;t&&t.setTextContent(`+${e}`)}function le(){let{value:e}=v;return e}function ue(){return o.value}let de=null;function fe(){de!==null&&window.clearTimeout(de)}function pe(){e.active||(fe(),de=window.setTimeout(()=>{j.value&&(w.value=!0)},100))}function me(){fe()}function he(e){e||(fe(),w.value=!1)}c(j,e=>{e||(w.value=!1)}),R(()=>{x(()=>{let t=h.value;t&&(e.disabled?t.removeAttribute(`tabindex`):t.tabIndex=T.value?-1:0)})}),ze(l,e.onResize);let{inlineThemeDisabled:ge}=e,_e=Y(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontWeight:r,borderRadius:i,color:a,placeholderColor:o,textColor:s,paddingSingle:c,paddingMultiple:l,caretColor:u,colorDisabled:p,textColorDisabled:m,placeholderColorDisabled:h,colorActive:g,boxShadowFocus:_,boxShadowActive:v,boxShadowHover:y,border:b,borderFocus:x,borderHover:S,borderActive:C,arrowColor:w,arrowColorDisabled:T,loadingColor:E,colorActiveWarning:O,boxShadowFocusWarning:k,boxShadowActiveWarning:A,boxShadowHoverWarning:j,borderWarning:M,borderFocusWarning:N,borderHoverWarning:P,borderActiveWarning:F,colorActiveError:I,boxShadowFocusError:L,boxShadowActiveError:R,boxShadowHoverError:z,borderError:ee,borderFocusError:te,borderHoverError:B,borderActiveError:V,clearColor:H,clearColorHover:U,clearColorPressed:W,clearSize:G,arrowSize:ne,[f(`height`,t)]:K,[f(`fontSize`,t)]:re}}=D.value,q=d(c),J=d(l);return{"--n-bezier":n,"--n-border":b,"--n-border-active":C,"--n-border-focus":x,"--n-border-hover":S,"--n-border-radius":i,"--n-box-shadow-active":v,"--n-box-shadow-focus":_,"--n-box-shadow-hover":y,"--n-caret-color":u,"--n-color":a,"--n-color-active":g,"--n-color-disabled":p,"--n-font-size":re,"--n-height":K,"--n-padding-single-top":q.top,"--n-padding-multiple-top":J.top,"--n-padding-single-right":q.right,"--n-padding-multiple-right":J.right,"--n-padding-single-left":q.left,"--n-padding-multiple-left":J.left,"--n-padding-single-bottom":q.bottom,"--n-padding-multiple-bottom":J.bottom,"--n-placeholder-color":o,"--n-placeholder-color-disabled":h,"--n-text-color":s,"--n-text-color-disabled":m,"--n-arrow-color":w,"--n-arrow-color-disabled":T,"--n-loading-color":E,"--n-color-active-warning":O,"--n-box-shadow-focus-warning":k,"--n-box-shadow-active-warning":A,"--n-box-shadow-hover-warning":j,"--n-border-warning":M,"--n-border-focus-warning":N,"--n-border-hover-warning":P,"--n-border-active-warning":F,"--n-color-active-error":I,"--n-box-shadow-focus-error":L,"--n-box-shadow-active-error":R,"--n-box-shadow-hover-error":z,"--n-border-error":ee,"--n-border-focus-error":te,"--n-border-hover-error":B,"--n-border-active-error":V,"--n-clear-size":G,"--n-clear-color":H,"--n-clear-color-hover":U,"--n-clear-color-pressed":W,"--n-arrow-size":ne,"--n-font-weight":r}}),ve=ge?S(`internal-selection`,Y(()=>e.size[0]),_e,e):void 0;return{mergedTheme:D,mergedClearable:O,mergedClsPrefix:n,rtlEnabled:i,patternInputFocused:T,filterablePlaceholder:k,label:A,selected:j,showTagsPanel:w,isComposing:K,counterRef:g,counterWrapperRef:v,patternInputMirrorRef:a,patternInputRef:o,selfRef:l,multipleElRef:p,singleElRef:m,patternInputWrapperRef:h,overflowRef:y,inputTagElRef:b,handleMouseDown:W,handleFocusin:te,handleClear:V,handleMouseEnter:H,handleMouseLeave:U,handleDeleteOption:G,handlePatternKeyDown:re,handlePatternInputInput:J,handlePatternInputBlur:Q,handlePatternInputFocus:ie,handleMouseEnterCounter:pe,handleMouseLeaveCounter:me,handleFocusout:B,handleCompositionEnd:Z,handleCompositionStart:X,onPopoverUpdateShow:he,focus:$,focusInput:oe,blur:ae,blurInput:se,updateCounter:ce,getCounter:le,getTail:ue,renderLabel:e.renderLabel,cssVars:ge?void 0:_e,themeClass:ve?.themeClass,onRender:ve?.onRender}},render(){let{status:e,multiple:t,size:n,disabled:r,filterable:i,maxTagCount:a,bordered:o,clsPrefix:s,ellipsisTagPopoverProps:c,onRender:l,renderTag:u,renderLabel:d}=this;l?.();let f=a===`responsive`,p=typeof a==`number`,m=f||p,h=U(w,null,{default:()=>U(ct,{clsPrefix:s,loading:this.loading,showArrow:this.showArrow,showClear:this.mergedClearable&&this.selected,onClear:this.handleClear},{default:()=>{var e;return(e=this.$slots).arrow?.call(e)}})}),g;if(t){let{labelField:e}=this,t=t=>U(`div`,{class:`${s}-base-selection-tag-wrapper`,key:t.value},u?u({option:t,handleClose:()=>{this.handleDeleteOption(t)}}):U(ge,{size:n,closable:!t.disabled,disabled:r,onClose:()=>{this.handleDeleteOption(t)},internalCloseIsButtonTag:!1,internalCloseFocusable:!1},{default:()=>d?d(t,!0):Se(t[e],t,!0)})),o=()=>(p?this.selectedOptions.slice(0,a):this.selectedOptions).map(t),l=i?U(`div`,{class:`${s}-base-selection-input-tag`,ref:`inputTagElRef`,key:`__input-tag__`},U(`input`,Object.assign({},this.inputProps,{ref:`patternInputRef`,tabindex:-1,disabled:r,value:this.pattern,autofocus:this.autofocus,class:`${s}-base-selection-input-tag__input`,onBlur:this.handlePatternInputBlur,onFocus:this.handlePatternInputFocus,onKeydown:this.handlePatternKeyDown,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),U(`span`,{ref:`patternInputMirrorRef`,class:`${s}-base-selection-input-tag__mirror`},this.pattern)):null,_=f?()=>U(`div`,{class:`${s}-base-selection-tag-wrapper`,ref:`counterWrapperRef`},U(ge,{size:n,ref:`counterRef`,onMouseenter:this.handleMouseEnterCounter,onMouseleave:this.handleMouseLeaveCounter,disabled:r})):void 0,v;if(p){let e=this.selectedOptions.length-a;e>0&&(v=U(`div`,{class:`${s}-base-selection-tag-wrapper`,key:`__counter__`},U(ge,{size:n,ref:`counterRef`,onMouseenter:this.handleMouseEnterCounter,disabled:r},{default:()=>`+${e}`})))}let y=f?i?U(be,{ref:`overflowRef`,updateCounter:this.updateCounter,getCounter:this.getCounter,getTail:this.getTail,style:{width:`100%`,display:`flex`,overflow:`hidden`}},{default:o,counter:_,tail:()=>l}):U(be,{ref:`overflowRef`,updateCounter:this.updateCounter,getCounter:this.getCounter,style:{width:`100%`,display:`flex`,overflow:`hidden`}},{default:o,counter:_}):p&&v?o().concat(v):o(),b=m?()=>U(`div`,{class:`${s}-base-selection-popover`},f?o():this.selectedOptions.map(t)):void 0,x=m?Object.assign({show:this.showTagsPanel,trigger:`hover`,overlap:!0,placement:`top`,width:`trigger`,onUpdateShow:this.onPopoverUpdateShow,theme:this.mergedTheme.peers.Popover,themeOverrides:this.mergedTheme.peerOverrides.Popover},c):null,S=!this.selected&&(!this.active||!this.pattern&&!this.isComposing)?U(`div`,{class:`${s}-base-selection-placeholder ${s}-base-selection-overlay`},U(`div`,{class:`${s}-base-selection-placeholder__inner`},this.placeholder)):null,C=i?U(`div`,{ref:`patternInputWrapperRef`,class:`${s}-base-selection-tags`},y,f?null:l,h):U(`div`,{ref:`multipleElRef`,class:`${s}-base-selection-tags`,tabindex:r?void 0:0},y,h);g=U(Q,null,m?U(Z,Object.assign({},x,{scrollable:!0,style:`max-height: calc(var(--v-target-height) * 6.6);`}),{trigger:()=>C,default:b}):C,S)}else if(i){let e=this.pattern||this.isComposing,t=this.active?!e:!this.selected,n=!this.active&&this.selected;g=U(`div`,{ref:`patternInputWrapperRef`,class:`${s}-base-selection-label`,title:this.patternInputFocused?void 0:Ue(this.label)},U(`input`,Object.assign({},this.inputProps,{ref:`patternInputRef`,class:`${s}-base-selection-input`,value:this.active?this.pattern:``,placeholder:``,readonly:r,disabled:r,tabindex:-1,autofocus:this.autofocus,onFocus:this.handlePatternInputFocus,onBlur:this.handlePatternInputBlur,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),n?U(`div`,{class:`${s}-base-selection-label__render-label ${s}-base-selection-overlay`,key:`input`},U(`div`,{class:`${s}-base-selection-overlay__wrapper`},u?u({option:this.selectedOption,handleClose:()=>{}}):d?d(this.selectedOption,!0):Se(this.label,this.selectedOption,!0))):null,t?U(`div`,{class:`${s}-base-selection-placeholder ${s}-base-selection-overlay`,key:`placeholder`},U(`div`,{class:`${s}-base-selection-overlay__wrapper`},this.filterablePlaceholder)):null,h)}else g=U(`div`,{ref:`singleElRef`,class:`${s}-base-selection-label`,tabindex:this.disabled?void 0:0},this.label===void 0?U(`div`,{class:`${s}-base-selection-placeholder ${s}-base-selection-overlay`,key:`placeholder`},U(`div`,{class:`${s}-base-selection-placeholder__inner`},this.placeholder)):U(`div`,{class:`${s}-base-selection-input`,title:Ue(this.label),key:`input`},U(`div`,{class:`${s}-base-selection-input__content`},u?u({option:this.selectedOption,handleClose:()=>{}}):d?d(this.selectedOption,!0):Se(this.label,this.selectedOption,!0))),h);return U(`div`,{ref:`selfRef`,class:[`${s}-base-selection`,this.rtlEnabled&&`${s}-base-selection--rtl`,this.themeClass,e&&`${s}-base-selection--${e}-status`,{[`${s}-base-selection--active`]:this.active,[`${s}-base-selection--selected`]:this.selected||this.active&&this.pattern,[`${s}-base-selection--disabled`]:this.disabled,[`${s}-base-selection--multiple`]:this.multiple,[`${s}-base-selection--focus`]:this.focused}],style:this.cssVars,onClick:this.onClick,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onKeydown:this.onKeydown,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onMousedown:this.handleMouseDown},g,o?U(`div`,{class:`${s}-base-selection__border`}):null,o?U(`div`,{class:`${s}-base-selection__state-border`}):null)}}),dt=ce(`n-input`),ft=M(`input`,`
 max-width: 100%;
 cursor: text;
 line-height: 1.5;
 z-index: auto;
 outline: none;
 box-sizing: border-box;
 position: relative;
 display: inline-flex;
 border-radius: var(--n-border-radius);
 background-color: var(--n-color);
 transition: background-color .3s var(--n-bezier);
 font-size: var(--n-font-size);
 font-weight: var(--n-font-weight);
 --n-padding-vertical: calc((var(--n-height) - 1.5 * var(--n-font-size)) / 2);
`,[m(`input, textarea`,`
 overflow: hidden;
 flex-grow: 1;
 position: relative;
 `),m(`input-el, textarea-el, input-mirror, textarea-mirror, separator, placeholder`,`
 box-sizing: border-box;
 font-size: inherit;
 line-height: 1.5;
 font-family: inherit;
 border: none;
 outline: none;
 background-color: #0000;
 text-align: inherit;
 transition:
 -webkit-text-fill-color .3s var(--n-bezier),
 caret-color .3s var(--n-bezier),
 color .3s var(--n-bezier),
 text-decoration-color .3s var(--n-bezier);
 `),m(`input-el, textarea-el`,`
 -webkit-appearance: none;
 scrollbar-width: none;
 width: 100%;
 min-width: 0;
 text-decoration-color: var(--n-text-decoration-color);
 color: var(--n-text-color);
 caret-color: var(--n-caret-color);
 background-color: transparent;
 `,[r(`&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb`,`
 width: 0;
 height: 0;
 display: none;
 `),r(`&::placeholder`,`
 color: #0000;
 -webkit-text-fill-color: transparent !important;
 `),r(`&:-webkit-autofill ~`,[m(`placeholder`,`display: none;`)])]),A(`round`,[N(`textarea`,`border-radius: calc(var(--n-height) / 2);`)]),m(`placeholder`,`
 pointer-events: none;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 overflow: hidden;
 color: var(--n-placeholder-color);
 `,[r(`span`,`
 width: 100%;
 display: inline-block;
 `)]),A(`textarea`,[m(`placeholder`,`overflow: visible;`)]),N(`autosize`,`width: 100%;`),A(`autosize`,[m(`textarea-el, input-el`,`
 position: absolute;
 top: 0;
 left: 0;
 height: 100%;
 `)]),M(`input-wrapper`,`
 overflow: hidden;
 display: inline-flex;
 flex-grow: 1;
 position: relative;
 padding-left: var(--n-padding-left);
 padding-right: var(--n-padding-right);
 `),m(`input-mirror`,`
 padding: 0;
 height: var(--n-height);
 line-height: var(--n-height);
 overflow: hidden;
 visibility: hidden;
 position: static;
 white-space: pre;
 pointer-events: none;
 `),m(`input-el`,`
 padding: 0;
 height: var(--n-height);
 line-height: var(--n-height);
 `,[r(`&[type=password]::-ms-reveal`,`display: none;`),r(`+`,[m(`placeholder`,`
 display: flex;
 align-items: center; 
 `)])]),N(`textarea`,[m(`placeholder`,`white-space: nowrap;`)]),m(`eye`,`
 display: flex;
 align-items: center;
 justify-content: center;
 transition: color .3s var(--n-bezier);
 `),A(`textarea`,`width: 100%;`,[M(`input-word-count`,`
 position: absolute;
 right: var(--n-padding-right);
 bottom: var(--n-padding-vertical);
 `),A(`resizable`,[M(`input-wrapper`,`
 resize: vertical;
 min-height: var(--n-height);
 `)]),m(`textarea-el, textarea-mirror, placeholder`,`
 height: 100%;
 padding-left: 0;
 padding-right: 0;
 padding-top: var(--n-padding-vertical);
 padding-bottom: var(--n-padding-vertical);
 word-break: break-word;
 display: inline-block;
 vertical-align: bottom;
 box-sizing: border-box;
 line-height: var(--n-line-height-textarea);
 margin: 0;
 resize: none;
 white-space: pre-wrap;
 scroll-padding-block-end: var(--n-padding-vertical);
 `),m(`textarea-mirror`,`
 width: 100%;
 pointer-events: none;
 overflow: hidden;
 visibility: hidden;
 position: static;
 white-space: pre-wrap;
 overflow-wrap: break-word;
 `)]),A(`pair`,[m(`input-el, placeholder`,`text-align: center;`),m(`separator`,`
 display: flex;
 align-items: center;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 white-space: nowrap;
 `,[M(`icon`,`
 color: var(--n-icon-color);
 `),M(`base-icon`,`
 color: var(--n-icon-color);
 `)])]),A(`disabled`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[m(`border`,`border: var(--n-border-disabled);`),m(`input-el, textarea-el`,`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 text-decoration-color: var(--n-text-color-disabled);
 `),m(`placeholder`,`color: var(--n-placeholder-color-disabled);`),m(`separator`,`color: var(--n-text-color-disabled);`,[M(`icon`,`
 color: var(--n-icon-color-disabled);
 `),M(`base-icon`,`
 color: var(--n-icon-color-disabled);
 `)]),M(`input-word-count`,`
 color: var(--n-count-text-color-disabled);
 `),m(`suffix, prefix`,`color: var(--n-text-color-disabled);`,[M(`icon`,`
 color: var(--n-icon-color-disabled);
 `),M(`internal-icon`,`
 color: var(--n-icon-color-disabled);
 `)])]),N(`disabled`,[m(`eye`,`
 color: var(--n-icon-color);
 cursor: pointer;
 `,[r(`&:hover`,`
 color: var(--n-icon-color-hover);
 `),r(`&:active`,`
 color: var(--n-icon-color-pressed);
 `)]),r(`&:hover`,[m(`state-border`,`border: var(--n-border-hover);`)]),A(`focus`,`background-color: var(--n-color-focus);`,[m(`state-border`,`
 border: var(--n-border-focus);
 box-shadow: var(--n-box-shadow-focus);
 `)])]),m(`border, state-border`,`
 box-sizing: border-box;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border-radius: inherit;
 border: var(--n-border);
 transition:
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `),m(`state-border`,`
 border-color: #0000;
 z-index: 1;
 `),m(`prefix`,`margin-right: 4px;`),m(`suffix`,`
 margin-left: 4px;
 `),m(`suffix, prefix`,`
 transition: color .3s var(--n-bezier);
 flex-wrap: nowrap;
 flex-shrink: 0;
 line-height: var(--n-height);
 white-space: nowrap;
 display: inline-flex;
 align-items: center;
 justify-content: center;
 color: var(--n-suffix-text-color);
 `,[M(`base-loading`,`
 font-size: var(--n-icon-size);
 margin: 0 2px;
 color: var(--n-loading-color);
 `),M(`base-clear`,`
 font-size: var(--n-icon-size);
 `,[m(`placeholder`,[M(`base-icon`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-icon-color);
 font-size: var(--n-icon-size);
 `)])]),r(`>`,[M(`icon`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-icon-color);
 font-size: var(--n-icon-size);
 `)]),M(`base-icon`,`
 font-size: var(--n-icon-size);
 `)]),M(`input-word-count`,`
 pointer-events: none;
 line-height: 1.5;
 font-size: .85em;
 color: var(--n-count-text-color);
 transition: color .3s var(--n-bezier);
 margin-left: 4px;
 font-variant: tabular-nums;
 `),[`warning`,`error`].map(e=>A(`${e}-status`,[N(`disabled`,[M(`base-loading`,`
 color: var(--n-loading-color-${e})
 `),m(`input-el, textarea-el`,`
 caret-color: var(--n-caret-color-${e});
 `),m(`state-border`,`
 border: var(--n-border-${e});
 `),r(`&:hover`,[m(`state-border`,`
 border: var(--n-border-hover-${e});
 `)]),r(`&:focus`,`
 background-color: var(--n-color-focus-${e});
 `,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)]),A(`focus`,`
 background-color: var(--n-color-focus-${e});
 `,[m(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),pt=M(`input`,[A(`disabled`,[m(`input-el, textarea-el`,`
 -webkit-text-fill-color: var(--n-text-color-disabled);
 `)])]);function mt(e){let t=0;for(let n of e)t++;return t}function ht(e){return e===``||e==null}function gt(e){let t=C(null);function n(){let{value:n}=e;if(!n?.focus){i();return}let{selectionStart:r,selectionEnd:a,value:o}=n;if(r==null||a==null){i();return}t.value={start:r,end:a,beforeText:o.slice(0,r),afterText:o.slice(a)}}function r(){var n;let{value:r}=t,{value:i}=e;if(!r||!i)return;let{value:a}=i,{start:o,beforeText:s,afterText:c}=r,l=a.length;if(a.endsWith(c))l=a.length-c.length;else if(a.startsWith(s))l=s.length;else{let e=s[o-1],t=a.indexOf(e,o-1);t!==-1&&(l=t+1)}(n=i.setSelectionRange)==null||n.call(i,l,l)}function i(){t.value=null}return c(e,i),{recordCursor:n,restoreCursor:r}}var _t=$({name:`InputWordCount`,setup(e,{slots:t}){let{mergedValueRef:n,maxlengthRef:r,mergedClsPrefixRef:i,countGraphemesRef:a}=J(dt),o=Y(()=>{let{value:e}=n;return e===null||Array.isArray(e)?0:(a.value||mt)(e)});return()=>{let{value:e}=r,{value:a}=n;return U(`span`,{class:`${i.value}-input-word-count`},p(t.default,{value:a===null||Array.isArray(a)?``:a},()=>[e===void 0?o.value:`${o.value} / ${e}`]))}}}),vt=Object.assign(Object.assign({},s.props),{bordered:{type:Boolean,default:void 0},type:{type:String,default:`text`},placeholder:[Array,String],defaultValue:{type:[String,Array],default:null},value:[String,Array],disabled:{type:Boolean,default:void 0},size:String,rows:{type:[Number,String],default:3},round:Boolean,minlength:[String,Number],maxlength:[String,Number],clearable:Boolean,autosize:{type:[Boolean,Object],default:!1},pair:Boolean,separator:String,readonly:{type:[String,Boolean],default:!1},passivelyActivated:Boolean,showPasswordOn:String,stateful:{type:Boolean,default:!0},autofocus:Boolean,inputProps:Object,resizable:{type:Boolean,default:!0},showCount:Boolean,loading:{type:Boolean,default:void 0},allowInput:Function,renderCount:Function,onMousedown:Function,onKeydown:Function,onKeyup:[Function,Array],onInput:[Function,Array],onFocus:[Function,Array],onBlur:[Function,Array],onClick:[Function,Array],onChange:[Function,Array],onClear:[Function,Array],countGraphemes:Function,status:String,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],textDecoration:[String,Array],attrSize:{type:Number,default:20},onInputBlur:[Function,Array],onInputFocus:[Function,Array],onDeactivate:[Function,Array],onActivate:[Function,Array],onWrapperFocus:[Function,Array],onWrapperBlur:[Function,Array],internalDeactivateOnEnter:Boolean,internalForceFocus:Boolean,internalLoadingBeforeSuffix:{type:Boolean,default:!0},showPasswordToggle:Boolean}),yt=$({name:`Input`,props:vt,slots:Object,setup(e){let{mergedClsPrefixRef:n,mergedBorderedRef:r,inlineThemeDisabled:i,mergedRtlRef:p,mergedComponentPropsRef:m}=u(e),h=s(`Input`,`-input`,ft,De,e,n);me&&b(`-input-safari`,pt,n);let v=C(null),y=C(null),w=C(null),T=C(null),E=C(null),D=C(null),k=C(null),A=gt(k),j=C(null),{localeRef:M}=pe(`Input`),N=C(e.defaultValue),P=_(e,`value`),F=ue(P,N),I=he(e,{mergedSize:t=>{let{size:n}=e;if(n)return n;let{mergedSize:r}=t||{};return r?.value?r.value:m?.value?.Input?.size||`medium`}}),{mergedSizeRef:L,mergedDisabledRef:z,mergedStatusRef:ee}=I,B=C(!1),V=C(!1),H=C(!1),U=C(!1),W=null,G=Y(()=>{let{placeholder:t,pair:n}=e;return n?Array.isArray(t)?t:t===void 0?[``,``]:[t,t]:t===void 0?[M.value.placeholder]:[t]}),K=Y(()=>{let{value:e}=H,{value:t}=F,{value:n}=G;return!e&&(ht(t)||Array.isArray(t)&&ht(t[0]))&&n[0]}),re=Y(()=>{let{value:e}=H,{value:t}=F,{value:n}=G;return!e&&n[1]&&(ht(t)||Array.isArray(t)&&ht(t[1]))}),q=o(()=>e.internalForceFocus||B.value),J=o(()=>{if(z.value||e.readonly||!e.clearable||!q.value&&!V.value)return!1;let{value:t}=F,{value:n}=q;return e.pair?!!(Array.isArray(t)&&(t[0]||t[1]))&&(V.value||n):!!t&&(V.value||n)}),X=Y(()=>{let{showPasswordOn:t}=e;if(t)return t;if(e.showPasswordToggle)return`click`}),Z=C(!1),ie=Y(()=>{let{textDecoration:t}=e;return t?Array.isArray(t)?t.map(e=>({textDecoration:e})):[{textDecoration:t}]:[``,``]}),Q=C(void 0),ae=()=>{if(e.type===`textarea`){let{autosize:t}=e;if(t&&(Q.value=j.value?.$el?.offsetWidth),!y.value||typeof t==`boolean`)return;let{paddingTop:n,paddingBottom:r,lineHeight:i}=window.getComputedStyle(y.value),a=Number(n.slice(0,-2)),o=Number(r.slice(0,-2)),s=Number(i.slice(0,-2)),{value:c}=w;if(!c)return;if(t.minRows){let e=Math.max(t.minRows,1),n=`${a+o+s*e}px`;c.style.minHeight=n}if(t.maxRows){let e=`${a+o+s*t.maxRows}px`;c.style.maxHeight=e}}},$=Y(()=>{let{maxlength:t}=e;return t===void 0?void 0:Number(t)});R(()=>{let{value:e}=F;Array.isArray(e)||Qe(e)});let oe=te().proxy;function se(t,n){let{onUpdateValue:r,"onUpdate:value":i,onInput:a}=e,{nTriggerFormInput:o}=I;r&&g(r,t,n),i&&g(i,t,n),a&&g(a,t,n),N.value=t,o()}function ce(t,n){let{onChange:r}=e,{nTriggerFormChange:i}=I;r&&g(r,t,n),N.value=t,i()}function le(t){let{onBlur:n}=e,{nTriggerFormBlur:r}=I;n&&g(n,t),r()}function de(t){let{onFocus:n}=e,{nTriggerFormFocus:r}=I;n&&g(n,t),r()}function fe(t){let{onClear:n}=e;n&&g(n,t)}function ge(t){let{onInputBlur:n}=e;n&&g(n,t)}function _e(t){let{onInputFocus:n}=e;n&&g(n,t)}function ve(){let{onDeactivate:t}=e;t&&g(t)}function ye(){let{onActivate:t}=e;t&&g(t)}function be(t){let{onClick:n}=e;n&&g(n,t)}function xe(t){let{onWrapperFocus:n}=e;n&&g(n,t)}function Se(t){let{onWrapperBlur:n}=e;n&&g(n,t)}function Ce(){H.value=!0}function we(e){H.value=!1,e.target===D.value?Te(e,1):Te(e,0)}function Te(t,n=0,r=`input`){let i=t.target.value;if(Qe(i),t instanceof InputEvent&&!t.isComposing&&(H.value=!1),e.type===`textarea`){let{value:e}=j;e&&e.syncUnifiedContainer()}if(W=i,H.value)return;A.recordCursor();let a=Ee(i);if(a)if(!e.pair)r===`input`?se(i,{source:n}):ce(i,{source:n});else{let{value:e}=F;e=Array.isArray(e)?[e[0],e[1]]:[``,``],e[n]=i,r===`input`?se(e,{source:n}):ce(e,{source:n})}oe.$forceUpdate(),a||ne(A.restoreCursor)}function Ee(t){let{countGraphemes:n,maxlength:r,minlength:i}=e;if(n){let e;if(r!==void 0&&(e===void 0&&(e=n(t)),e>Number(r))||i!==void 0&&(e===void 0&&(e=n(t)),e<Number(r)))return!1}let{allowInput:a}=e;return typeof a!=`function`||a(t)}function Oe(e){ge(e),e.relatedTarget===v.value&&ve(),(e.relatedTarget===null||e.relatedTarget!==E.value&&e.relatedTarget!==D.value&&e.relatedTarget!==y.value)&&(U.value=!1),Me(e,`blur`),k.value=null}function ke(e,t){_e(e),B.value=!0,U.value=!0,ye(),Me(e,`focus`),t===0?k.value=E.value:t===1?k.value=D.value:t===2&&(k.value=y.value)}function Ae(t){e.passivelyActivated&&(Se(t),Me(t,`blur`))}function je(t){e.passivelyActivated&&(B.value=!0,xe(t),Me(t,`focus`))}function Me(e,t){e.relatedTarget!==null&&(e.relatedTarget===E.value||e.relatedTarget===D.value||e.relatedTarget===y.value||e.relatedTarget===v.value)||(t===`focus`?(de(e),B.value=!0):t===`blur`&&(le(e),B.value=!1))}function Ne(e,t){Te(e,t,`change`)}function Pe(e){be(e)}function Fe(e){fe(e),Ie()}function Ie(){e.pair?(se([``,``],{source:`clear`}),ce([``,``],{source:`clear`})):(se(``,{source:`clear`}),ce(``,{source:`clear`}))}function Le(t){let{onMousedown:n}=e;n&&n(t);let{tagName:r}=t.target;if(r!==`INPUT`&&r!==`TEXTAREA`){if(e.resizable){let{value:e}=v;if(e){let{left:n,top:r,width:i,height:a}=e.getBoundingClientRect();if(n+i-14<t.clientX&&t.clientX<n+i&&r+a-14<t.clientY&&t.clientY<r+a)return}}t.preventDefault(),B.value||Ke()}}function Re(){var t;V.value=!0,e.type===`textarea`&&((t=j.value)==null||t.handleMouseEnterWrapper())}function ze(){var t;V.value=!1,e.type===`textarea`&&((t=j.value)==null||t.handleMouseLeaveWrapper())}function Be(){z.value||X.value===`click`&&(Z.value=!Z.value)}function Ve(e){if(z.value)return;e.preventDefault();let t=e=>{e.preventDefault(),O(`mouseup`,document,t)};if(l(`mouseup`,document,t),X.value!==`mousedown`)return;Z.value=!0;let n=()=>{Z.value=!1,O(`mouseup`,document,n)};l(`mouseup`,document,n)}function He(t){e.onKeyup&&g(e.onKeyup,t)}function Ue(t){switch(e.onKeydown&&g(e.onKeydown,t),t.key){case`Escape`:Ge();break;case`Enter`:We(t)}}function We(t){var n,r;if(e.passivelyActivated){let{value:i}=U;if(i){e.internalDeactivateOnEnter&&Ge();return}t.preventDefault(),e.type===`textarea`?(n=y.value)==null||n.focus():(r=E.value)==null||r.focus()}}function Ge(){e.passivelyActivated&&(U.value=!1,ne(()=>{var e;(e=v.value)==null||e.focus()}))}function Ke(){var t,n,r;z.value||(e.passivelyActivated?(t=v.value)==null||t.focus():((n=y.value)==null||n.focus(),(r=E.value)==null||r.focus()))}function qe(){v.value?.contains(document.activeElement)&&document.activeElement.blur()}function Je(){var e,t;(e=y.value)==null||e.select(),(t=E.value)==null||t.select()}function Ye(){z.value||(y.value?y.value.focus():E.value&&E.value.focus())}function Xe(){let{value:e}=v;e?.contains(document.activeElement)&&e!==document.activeElement&&Ge()}function Ze(t){if(e.type===`textarea`){let{value:e}=y;e?.scrollTo(t)}else{let{value:e}=E;e?.scrollTo(t)}}function Qe(t){let{type:n,pair:r,autosize:i}=e;if(!r&&i)if(n===`textarea`){let{value:e}=w;e&&(e.textContent=`${t??``}\r\n`)}else{let{value:e}=T;e&&(t?e.textContent=t:e.innerHTML=`&nbsp;`)}}function $e(){ae()}let et=C({top:`0`});function tt(e){var t;let{scrollTop:n}=e.target;et.value.top=`${-n}px`,(t=j.value)==null||t.syncUnifiedContainer()}let nt=null;x(()=>{let{autosize:t,type:n}=e;t&&n===`textarea`?nt=c(F,e=>{!Array.isArray(e)&&e!==W&&Qe(e)}):nt?.()});let rt=null;x(()=>{e.type===`textarea`?rt=c(F,e=>{var t;!Array.isArray(e)&&e!==W&&((t=j.value)==null||t.syncUnifiedContainer())}):rt?.()}),a(dt,{mergedValueRef:F,maxlengthRef:$,mergedClsPrefixRef:n,countGraphemesRef:_(e,`countGraphemes`)});let it={wrapperElRef:v,inputElRef:E,textareaElRef:y,isCompositing:H,clear:Ie,focus:Ke,blur:qe,select:Je,deactivate:Xe,activate:Ye,scrollTo:Ze},at=t(`Input`,p,n),ot=Y(()=>{let{value:e}=L,{common:{cubicBezierEaseInOut:t},self:{color:n,borderRadius:r,textColor:i,caretColor:a,caretColorError:o,caretColorWarning:s,textDecorationColor:c,border:l,borderDisabled:u,borderHover:p,borderFocus:m,placeholderColor:g,placeholderColorDisabled:_,lineHeightTextarea:v,colorDisabled:y,colorFocus:b,textColorDisabled:x,boxShadowFocus:S,iconSize:C,colorFocusWarning:w,boxShadowFocusWarning:T,borderWarning:E,borderFocusWarning:D,borderHoverWarning:O,colorFocusError:k,boxShadowFocusError:A,borderError:j,borderFocusError:M,borderHoverError:N,clearSize:P,clearColor:F,clearColorHover:I,clearColorPressed:R,iconColor:z,iconColorDisabled:ee,suffixTextColor:te,countTextColor:B,countTextColorDisabled:V,iconColorHover:H,iconColorPressed:U,loadingColor:W,loadingColorError:G,loadingColorWarning:ne,fontWeight:K,[f(`padding`,e)]:re,[f(`fontSize`,e)]:q,[f(`height`,e)]:J}}=h.value,{left:Y,right:X}=d(re);return{"--n-bezier":t,"--n-count-text-color":B,"--n-count-text-color-disabled":V,"--n-color":n,"--n-font-size":q,"--n-font-weight":K,"--n-border-radius":r,"--n-height":J,"--n-padding-left":Y,"--n-padding-right":X,"--n-text-color":i,"--n-caret-color":a,"--n-text-decoration-color":c,"--n-border":l,"--n-border-disabled":u,"--n-border-hover":p,"--n-border-focus":m,"--n-placeholder-color":g,"--n-placeholder-color-disabled":_,"--n-icon-size":C,"--n-line-height-textarea":v,"--n-color-disabled":y,"--n-color-focus":b,"--n-text-color-disabled":x,"--n-box-shadow-focus":S,"--n-loading-color":W,"--n-caret-color-warning":s,"--n-color-focus-warning":w,"--n-box-shadow-focus-warning":T,"--n-border-warning":E,"--n-border-focus-warning":D,"--n-border-hover-warning":O,"--n-loading-color-warning":ne,"--n-caret-color-error":o,"--n-color-focus-error":k,"--n-box-shadow-focus-error":A,"--n-border-error":j,"--n-border-focus-error":M,"--n-border-hover-error":N,"--n-loading-color-error":G,"--n-clear-color":F,"--n-clear-size":P,"--n-clear-color-hover":I,"--n-clear-color-pressed":R,"--n-icon-color":z,"--n-icon-color-hover":H,"--n-icon-color-pressed":U,"--n-icon-color-disabled":ee,"--n-suffix-text-color":te}}),st=i?S(`input`,Y(()=>{let{value:e}=L;return e[0]}),ot,e):void 0;return Object.assign(Object.assign({},it),{wrapperElRef:v,inputElRef:E,inputMirrorElRef:T,inputEl2Ref:D,textareaElRef:y,textareaMirrorElRef:w,textareaScrollbarInstRef:j,rtlEnabled:at,uncontrolledValue:N,mergedValue:F,passwordVisible:Z,mergedPlaceholder:G,showPlaceholder1:K,showPlaceholder2:re,mergedFocus:q,isComposing:H,activated:U,showClearButton:J,mergedSize:L,mergedDisabled:z,textDecorationStyle:ie,mergedClsPrefix:n,mergedBordered:r,mergedShowPasswordOn:X,placeholderStyle:et,mergedStatus:ee,textAreaScrollContainerWidth:Q,handleTextAreaScroll:tt,handleCompositionStart:Ce,handleCompositionEnd:we,handleInput:Te,handleInputBlur:Oe,handleInputFocus:ke,handleWrapperBlur:Ae,handleWrapperFocus:je,handleMouseEnter:Re,handleMouseLeave:ze,handleMouseDown:Le,handleChange:Ne,handleClick:Pe,handleClear:Fe,handlePasswordToggleClick:Be,handlePasswordToggleMousedown:Ve,handleWrapperKeydown:Ue,handleWrapperKeyup:He,handleTextAreaMirrorResize:$e,getTextareaScrollContainer:()=>y.value,mergedTheme:h,cssVars:i?void 0:ot,themeClass:st?.themeClass,onRender:st?.onRender})},render(){let{mergedClsPrefix:t,mergedStatus:n,themeClass:r,type:i,countGraphemes:a,onRender:o}=this,s=this.$slots;return o?.(),U(`div`,{ref:`wrapperElRef`,class:[`${t}-input`,`${t}-input--${this.mergedSize}-size`,r,n&&`${t}-input--${n}-status`,{[`${t}-input--rtl`]:this.rtlEnabled,[`${t}-input--disabled`]:this.mergedDisabled,[`${t}-input--textarea`]:i===`textarea`,[`${t}-input--resizable`]:this.resizable&&!this.autosize,[`${t}-input--autosize`]:this.autosize,[`${t}-input--round`]:this.round&&i!==`textarea`,[`${t}-input--pair`]:this.pair,[`${t}-input--focus`]:this.mergedFocus,[`${t}-input--stateful`]:this.stateful}],style:this.cssVars,tabindex:!this.mergedDisabled&&this.passivelyActivated&&!this.activated?0:void 0,onFocus:this.handleWrapperFocus,onBlur:this.handleWrapperBlur,onClick:this.handleClick,onMousedown:this.handleMouseDown,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd,onKeyup:this.handleWrapperKeyup,onKeydown:this.handleWrapperKeydown},U(`div`,{class:`${t}-input-wrapper`},k(s.prefix,e=>e&&U(`div`,{class:`${t}-input__prefix`},e)),i===`textarea`?U(H,{ref:`textareaScrollbarInstRef`,class:`${t}-input__textarea`,container:this.getTextareaScrollContainer,theme:this.theme?.peers?.Scrollbar,themeOverrides:this.themeOverrides?.peers?.Scrollbar,triggerDisplayManually:!0,useUnifiedContainer:!0,internalHoistYRail:!0},{default:()=>{let{textAreaScrollContainerWidth:n}=this,r={width:this.autosize&&n&&`${n}px`};return U(Q,null,U(`textarea`,Object.assign({},this.inputProps,{ref:`textareaElRef`,class:[`${t}-input__textarea-el`,this.inputProps?.class],autofocus:this.autofocus,rows:Number(this.rows),placeholder:this.placeholder,value:this.mergedValue,disabled:this.mergedDisabled,maxlength:a?void 0:this.maxlength,minlength:a?void 0:this.minlength,readonly:this.readonly,tabindex:this.passivelyActivated&&!this.activated?-1:void 0,style:[this.textDecorationStyle[0],this.inputProps?.style,r],onBlur:this.handleInputBlur,onFocus:e=>{this.handleInputFocus(e,2)},onInput:this.handleInput,onChange:this.handleChange,onScroll:this.handleTextAreaScroll})),this.showPlaceholder1?U(`div`,{class:`${t}-input__placeholder`,style:[this.placeholderStyle,r],key:`placeholder`},this.mergedPlaceholder[0]):null,this.autosize?U(e,{onResize:this.handleTextAreaMirrorResize},{default:()=>U(`div`,{ref:`textareaMirrorElRef`,class:`${t}-input__textarea-mirror`,key:`mirror`})}):null)}}):U(`div`,{class:`${t}-input__input`},U(`input`,Object.assign({type:i===`password`&&this.mergedShowPasswordOn&&this.passwordVisible?`text`:i},this.inputProps,{ref:`inputElRef`,class:[`${t}-input__input-el`,this.inputProps?.class],style:[this.textDecorationStyle[0],this.inputProps?.style],tabindex:this.passivelyActivated&&!this.activated?-1:this.inputProps?.tabindex,placeholder:this.mergedPlaceholder[0],disabled:this.mergedDisabled,maxlength:a?void 0:this.maxlength,minlength:a?void 0:this.minlength,value:Array.isArray(this.mergedValue)?this.mergedValue[0]:this.mergedValue,readonly:this.readonly,autofocus:this.autofocus,size:this.attrSize,onBlur:this.handleInputBlur,onFocus:e=>{this.handleInputFocus(e,0)},onInput:e=>{this.handleInput(e,0)},onChange:e=>{this.handleChange(e,0)}})),this.showPlaceholder1?U(`div`,{class:`${t}-input__placeholder`},U(`span`,null,this.mergedPlaceholder[0])):null,this.autosize?U(`div`,{class:`${t}-input__input-mirror`,key:`mirror`,ref:`inputMirrorElRef`},`\xA0`):null),!this.pair&&k(s.suffix,e=>e||this.clearable||this.showCount||this.mergedShowPasswordOn||this.loading!==void 0?U(`div`,{class:`${t}-input__suffix`},[k(s[`clear-icon-placeholder`],e=>(this.clearable||e)&&U(Qe,{clsPrefix:t,show:this.showClearButton,onClear:this.handleClear},{placeholder:()=>e,icon:()=>{var e;return(e=this.$slots)[`clear-icon`]?.call(e)}})),this.internalLoadingBeforeSuffix?null:e,this.loading===void 0?null:U(ct,{clsPrefix:t,loading:this.loading,showArrow:!1,showClear:!1,style:this.cssVars}),this.internalLoadingBeforeSuffix?e:null,this.showCount&&this.type!==`textarea`?U(_t,null,{default:e=>{let{renderCount:t}=this;return t?t(e):s.count?.call(s,e)}}):null,this.mergedShowPasswordOn&&this.type===`password`?U(`div`,{class:`${t}-input__eye`,onMousedown:this.handlePasswordToggleMousedown,onClick:this.handlePasswordToggleClick},this.passwordVisible?j(s[`password-visible-icon`],()=>[U(D,{clsPrefix:t},{default:()=>U(Ye,null)})]):j(s[`password-invisible-icon`],()=>[U(D,{clsPrefix:t},{default:()=>U(Xe,null)})])):null]):null)),this.pair?U(`span`,{class:`${t}-input__separator`},j(s.separator,()=>[this.separator])):null,this.pair?U(`div`,{class:`${t}-input-wrapper`},U(`div`,{class:`${t}-input__input`},U(`input`,{ref:`inputEl2Ref`,type:this.type,class:`${t}-input__input-el`,tabindex:this.passivelyActivated&&!this.activated?-1:void 0,placeholder:this.mergedPlaceholder[1],disabled:this.mergedDisabled,maxlength:a?void 0:this.maxlength,minlength:a?void 0:this.minlength,value:Array.isArray(this.mergedValue)?this.mergedValue[1]:void 0,readonly:this.readonly,style:this.textDecorationStyle[1],onBlur:this.handleInputBlur,onFocus:e=>{this.handleInputFocus(e,1)},onInput:e=>{this.handleInput(e,1)},onChange:e=>{this.handleChange(e,1)}}),this.showPlaceholder2?U(`div`,{class:`${t}-input__placeholder`},U(`span`,null,this.mergedPlaceholder[1])):null),k(s.suffix,e=>(this.clearable||e)&&U(`div`,{class:`${t}-input__suffix`},[this.clearable&&U(Qe,{clsPrefix:t,show:this.showClearButton,onClear:this.handleClear},{icon:()=>s[`clear-icon`]?.call(s),placeholder:()=>s[`clear-icon-placeholder`]?.call(s)}),e]))):null,this.mergedBordered?U(`div`,{class:`${t}-input__border`}):null,this.mergedBordered?U(`div`,{class:`${t}-input__state-border`}):null,this.showCount&&i===`textarea`?U(_t,null,{default:e=>{let{renderCount:t}=this;return t?t(e):s.count?.call(s,e)}}):null)}});function bt(e){return e.type===`group`}function xt(e){return e.type===`ignored`}function St(e,t){try{return!!(1+t.toString().toLowerCase().indexOf(e.trim().toLowerCase()))}catch{return!1}}function Ct(e,t){return{getIsGroup:bt,getIgnored:xt,getKey(t){return bt(t)?t.name||t.key||`key-required`:t[e]},getChildren(e){return e[t]}}}function wt(e,t,n,r){if(!t)return e;function i(e){if(!Array.isArray(e))return[];let a=[];for(let o of e)if(bt(o)){let e=i(o[r]);e.length&&a.push(Object.assign({},o,{[r]:e}))}else if(xt(o))continue;else t(n,o)&&a.push(o);return a}return i(e)}function Tt(e,t,n){let r=new Map;return e.forEach(e=>{bt(e)?e[n].forEach(e=>{r.set(e[t],e)}):r.set(e[t],e)}),r}var Et=r([M(`select`,`
 z-index: auto;
 outline: none;
 width: 100%;
 position: relative;
 font-weight: var(--n-font-weight);
 `),M(`select-menu`,`
 margin: 4px 0;
 box-shadow: var(--n-menu-box-shadow);
 `,[_e({originalTransition:`background-color .3s var(--n-bezier), box-shadow .3s var(--n-bezier)`})])]),Dt=Object.assign(Object.assign({},s.props),{to:B.propTo,bordered:{type:Boolean,default:void 0},clearable:Boolean,clearCreatedOptionsOnClear:{type:Boolean,default:!0},clearFilterAfterSelect:{type:Boolean,default:!0},options:{type:Array,default:()=>[]},defaultValue:{type:[String,Number,Array],default:null},keyboard:{type:Boolean,default:!0},value:[String,Number,Array],placeholder:String,menuProps:Object,multiple:Boolean,size:String,menuSize:{type:String},filterable:Boolean,disabled:{type:Boolean,default:void 0},remote:Boolean,loading:Boolean,filter:Function,placement:{type:String,default:`bottom-start`},widthMode:{type:String,default:`trigger`},tag:Boolean,onCreate:Function,fallbackOption:{type:[Function,Boolean],default:void 0},show:{type:Boolean,default:void 0},showArrow:{type:Boolean,default:!0},maxTagCount:[Number,String],ellipsisTagPopoverProps:Object,consistentMenuWidth:{type:Boolean,default:!0},virtualScroll:{type:Boolean,default:!0},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},childrenField:{type:String,default:`children`},renderLabel:Function,renderOption:Function,renderTag:Function,"onUpdate:value":[Function,Array],inputProps:Object,nodeProps:Function,ignoreComposition:{type:Boolean,default:!0},showOnFocus:Boolean,onUpdateValue:[Function,Array],onBlur:[Function,Array],onClear:[Function,Array],onFocus:[Function,Array],onScroll:[Function,Array],onSearch:[Function,Array],onUpdateShow:[Function,Array],"onUpdate:show":[Function,Array],displayDirective:{type:String,default:`show`},resetMenuOnOptionsChange:{type:Boolean,default:!0},status:String,showCheckmark:{type:Boolean,default:!0},scrollbarProps:Object,onChange:[Function,Array],items:Array}),Ot=$({name:`Select`,props:Dt,slots:Object,setup(e){let{mergedClsPrefixRef:t,mergedBorderedRef:n,namespaceRef:r,inlineThemeDisabled:i,mergedComponentPropsRef:a}=u(e),o=s(`Select`,`-select`,Et,Te,e,t),l=C(e.defaultValue),d=_(e,`value`),f=ue(d,l),p=C(!1),m=C(``),h=fe(e,[`items`,`options`]),y=C([]),b=C([]),x=Y(()=>b.value.concat(y.value).concat(h.value)),w=Y(()=>{let{filter:t}=e;if(t)return t;let{labelField:n,valueField:r}=e;return(e,t)=>{if(!t)return!1;let i=t[n];if(typeof i==`string`)return St(e,i);let a=t[r];return typeof a==`string`?St(e,a):typeof a==`number`&&St(e,String(a))}}),T=Y(()=>{if(e.remote)return h.value;{let{value:t}=x,{value:n}=m;return!n.length||!e.filterable?t:wt(t,w.value,n,e.childrenField)}}),E=Y(()=>{let{valueField:t,childrenField:n}=e,r=Ct(t,n);return ye(T.value,r)}),D=Y(()=>Tt(x.value,e.valueField,e.childrenField)),O=C(!1),k=ue(_(e,`show`),O),A=C(null),j=C(null),M=C(null),{localeRef:N}=pe(`Select`),P=Y(()=>e.placeholder??N.value.placeholder),F=[],I=C(new Map),L=Y(()=>{let{fallbackOption:t}=e;if(t===void 0){let{labelField:t,valueField:n}=e;return e=>({[t]:String(e),[n]:e})}return t===!1?!1:e=>Object.assign(t(e),{value:e})});function R(t){let n=e.remote,{value:r}=I,{value:i}=D,{value:a}=L,o=[];return t.forEach(e=>{if(i.has(e))o.push(i.get(e));else if(n&&r.has(e))o.push(r.get(e));else if(a){let t=a(e);t&&o.push(t)}}),o}let ee=Y(()=>{if(e.multiple){let{value:e}=f;return Array.isArray(e)?R(e):[]}return null}),te=Y(()=>{let{value:t}=f;return!e.multiple&&!Array.isArray(t)?t===null?null:R([t])[0]||null:null}),V=he(e,{mergedSize:t=>{let{size:n}=e;if(n)return n;let{mergedSize:r}=t||{};return r?.value?r.value:a?.value?.Select?.size||`medium`}}),{mergedSizeRef:H,mergedDisabledRef:U,mergedStatusRef:W}=V;function G(t,n){let{onChange:r,"onUpdate:value":i,onUpdateValue:a}=e,{nTriggerFormChange:o,nTriggerFormInput:s}=V;r&&g(r,t,n),a&&g(a,t,n),i&&g(i,t,n),l.value=t,o(),s()}function ne(t){let{onBlur:n}=e,{nTriggerFormBlur:r}=V;n&&g(n,t),r()}function K(){let{onClear:t}=e;t&&g(t)}function re(t){let{onFocus:n,showOnFocus:r}=e,{nTriggerFormFocus:i}=V;n&&g(n,t),i(),r&&ie()}function q(t){let{onSearch:n}=e;n&&g(n,t)}function J(t){let{onScroll:n}=e;n&&g(n,t)}function X(){var t;let{remote:n,multiple:r}=e;if(n){let{value:n}=I;if(r){let{valueField:r}=e;(t=ee.value)==null||t.forEach(e=>{n.set(e[r],e)})}else{let t=te.value;t&&n.set(t[e.valueField],t)}}}function Z(t){let{onUpdateShow:n,"onUpdate:show":r}=e;n&&g(n,t),r&&g(r,t),O.value=t}function ie(){U.value||(Z(!0),O.value=!0,e.filterable&&Me())}function Q(){Z(!1)}function ae(){m.value=``,b.value=F}let $=C(!1);function oe(){e.filterable&&($.value=!0)}function se(){e.filterable&&($.value=!1,k.value||ae())}function ce(){U.value||(k.value?e.filterable?Me():Q():ie())}function le(e){(M.value?.selfRef)?.contains(e.relatedTarget)||(p.value=!1,ne(e),Q())}function de(e){re(e),p.value=!0}function me(){p.value=!0}function ge(e){A.value?.$el.contains(e.relatedTarget)||(p.value=!1,ne(e),Q())}function _e(){var e;(e=A.value)==null||e.focus(),Q()}function ve(e){k.value&&(A.value?.$el.contains(v(e))||Q())}function be(t){if(!Array.isArray(t))return[];if(L.value)return Array.from(t);{let{remote:n}=e,{value:r}=D;if(n){let{value:e}=I;return t.filter(t=>r.has(t)||e.has(t))}return t.filter(e=>r.has(e))}}function Se(e){Ce(e.rawNode)}function Ce(t){if(U.value)return;let{tag:n,remote:r,clearFilterAfterSelect:i,valueField:a}=e;if(n&&!r){let{value:e}=b,t=e[0]||null;if(t){let e=y.value;e.length?e.push(t):y.value=[t],b.value=F}}if(r&&I.value.set(t[a],t),e.multiple){let e=be(f.value),o=e.findIndex(e=>e===t[a]);if(~o){if(e.splice(o,1),n&&!r){let e=we(t[a]);~e&&(y.value.splice(e,1),i&&(m.value=``))}}else e.push(t[a]),i&&(m.value=``);G(e,R(e))}else{if(n&&!r){let e=we(t[a]);~e?y.value=[y.value[e]]:y.value=F}je(),Q(),G(t[a],t)}}function we(t){return y.value.findIndex(n=>n[e.valueField]===t)}function Ee(t){k.value||ie();let{value:n}=t.target;m.value=n;let{tag:r,remote:i}=e;if(q(n),r&&!i){if(!n){b.value=F;return}let{onCreate:t}=e,r=t?t(n):{[e.labelField]:n,[e.valueField]:n},{valueField:i,labelField:a}=e;h.value.some(e=>e[i]===r[i]||e[a]===r[a])||y.value.some(e=>e[i]===r[i]||e[a]===r[a])?b.value=F:b.value=[r]}}function De(t){t.stopPropagation();let{multiple:n,tag:r,remote:i,clearCreatedOptionsOnClear:a}=e;!n&&e.filterable&&Q(),r&&!i&&a&&(y.value=F),K(),n?G([],[]):G(null,null)}function Oe(e){!xe(e,`action`)&&!xe(e,`empty`)&&!xe(e,`header`)&&e.preventDefault()}function ke(e){J(e)}function Ae(t){var n,r,i;if(!e.keyboard){t.preventDefault();return}switch(t.key){case` `:if(e.filterable)break;t.preventDefault();case`Enter`:if(!A.value?.isComposing){if(k.value){let t=M.value?.getPendingTmNode();t?Se(t):e.filterable||(Q(),je())}else if(ie(),e.tag&&$.value){let t=b.value[0];if(t){let n=t[e.valueField],{value:r}=f;e.multiple&&Array.isArray(r)&&r.includes(n)||Ce(t)}}}t.preventDefault();break;case`ArrowUp`:if(t.preventDefault(),e.loading)return;k.value&&((n=M.value)==null||n.prev());break;case`ArrowDown`:if(t.preventDefault(),e.loading)return;k.value?(r=M.value)==null||r.next():ie();break;case`Escape`:k.value&&(Ve(t),Q()),(i=A.value)==null||i.focus()}}function je(){var e;(e=A.value)==null||e.focus()}function Me(){var e;(e=A.value)==null||e.focusInput()}function Ne(){var e;k.value&&((e=j.value)==null||e.syncPosition())}X(),c(_(e,`options`),X);let Pe={focus:()=>{var e;(e=A.value)==null||e.focus()},focusInput:()=>{var e;(e=A.value)==null||e.focusInput()},blur:()=>{var e;(e=A.value)==null||e.blur()},blurInput:()=>{var e;(e=A.value)==null||e.blurInput()}},Fe=Y(()=>{let{self:{menuBoxShadow:e}}=o.value;return{"--n-menu-box-shadow":e}}),Ie=i?S(`select`,void 0,Fe,e):void 0;return Object.assign(Object.assign({},Pe),{mergedStatus:W,mergedClsPrefix:t,mergedBordered:n,namespace:r,treeMate:E,isMounted:z(),triggerRef:A,menuRef:M,pattern:m,uncontrolledShow:O,mergedShow:k,adjustedTo:B(e),uncontrolledValue:l,mergedValue:f,followerRef:j,localizedPlaceholder:P,selectedOption:te,selectedOptions:ee,mergedSize:H,mergedDisabled:U,focused:p,activeWithoutMenuOpen:$,inlineThemeDisabled:i,onTriggerInputFocus:oe,onTriggerInputBlur:se,handleTriggerOrMenuResize:Ne,handleMenuFocus:me,handleMenuBlur:ge,handleMenuTabOut:_e,handleTriggerClick:ce,handleToggle:Se,handleDeleteOption:Ce,handlePatternInput:Ee,handleClear:De,handleTriggerBlur:le,handleTriggerFocus:de,handleKeydown:Ae,handleMenuAfterLeave:ae,handleMenuClickOutside:ve,handleMenuScroll:ke,handleMenuKeydown:Ae,handleMenuMousedown:Oe,mergedTheme:o,cssVars:i?void 0:Fe,themeClass:Ie?.themeClass,onRender:Ie?.onRender})},render(){return U(`div`,{class:`${this.mergedClsPrefix}-select`},U(re,null,{default:()=>[U(ee,null,{default:()=>U(ut,{ref:`triggerRef`,inlineThemeDisabled:this.inlineThemeDisabled,status:this.mergedStatus,inputProps:this.inputProps,clsPrefix:this.mergedClsPrefix,showArrow:this.showArrow,maxTagCount:this.maxTagCount,ellipsisTagPopoverProps:this.ellipsisTagPopoverProps,bordered:this.mergedBordered,active:this.activeWithoutMenuOpen||this.mergedShow,pattern:this.pattern,placeholder:this.localizedPlaceholder,selectedOption:this.selectedOption,selectedOptions:this.selectedOptions,multiple:this.multiple,renderTag:this.renderTag,renderLabel:this.renderLabel,filterable:this.filterable,clearable:this.clearable,disabled:this.mergedDisabled,size:this.mergedSize,theme:this.mergedTheme.peers.InternalSelection,labelField:this.labelField,valueField:this.valueField,themeOverrides:this.mergedTheme.peerOverrides.InternalSelection,loading:this.loading,focused:this.focused,onClick:this.handleTriggerClick,onDeleteOption:this.handleDeleteOption,onPatternInput:this.handlePatternInput,onClear:this.handleClear,onBlur:this.handleTriggerBlur,onFocus:this.handleTriggerFocus,onKeydown:this.handleKeydown,onPatternBlur:this.onTriggerInputBlur,onPatternFocus:this.onTriggerInputFocus,onResize:this.handleTriggerOrMenuResize,ignoreComposition:this.ignoreComposition},{arrow:()=>{var e;return[(e=this.$slots).arrow?.call(e)]}})}),U(ae,{ref:`followerRef`,show:this.mergedShow,to:this.adjustedTo,teleportDisabled:this.adjustedTo===B.tdkey,containerClass:this.namespace,width:this.consistentMenuWidth?`target`:void 0,minWidth:`target`,placement:this.placement},{default:()=>U(P,{name:`fade-in-scale-up-transition`,appear:this.isMounted,onAfterLeave:this.handleMenuAfterLeave},{default:()=>{var e;return this.mergedShow||this.displayDirective===`show`?((e=this.onRender)==null||e.call(this),n(U(st,Object.assign({},this.menuProps,{ref:`menuRef`,onResize:this.handleTriggerOrMenuResize,inlineThemeDisabled:this.inlineThemeDisabled,virtualScroll:this.consistentMenuWidth&&this.virtualScroll,class:[`${this.mergedClsPrefix}-select-menu`,this.themeClass,this.menuProps?.class],clsPrefix:this.mergedClsPrefix,focusable:!0,labelField:this.labelField,valueField:this.valueField,autoPending:!0,nodeProps:this.nodeProps,theme:this.mergedTheme.peers.InternalSelectMenu,themeOverrides:this.mergedTheme.peerOverrides.InternalSelectMenu,treeMate:this.treeMate,multiple:this.multiple,size:this.menuSize,renderOption:this.renderOption,renderLabel:this.renderLabel,value:this.mergedValue,style:[this.menuProps?.style,this.cssVars],onToggle:this.handleToggle,onScroll:this.handleMenuScroll,onFocus:this.handleMenuFocus,onBlur:this.handleMenuBlur,onKeydown:this.handleMenuKeydown,onTabOut:this.handleMenuTabOut,onMousedown:this.handleMenuMousedown,show:this.mergedShow,showCheckmark:this.showCheckmark,resetMenuOnOptionsChange:this.resetMenuOnOptionsChange,scrollbarProps:this.scrollbarProps}),{empty:()=>{var e;return[(e=this.$slots).empty?.call(e)]},header:()=>{var e;return[(e=this.$slots).header?.call(e)]},action:()=>{var e;return[(e=this.$slots).action?.call(e)]}}),this.displayDirective===`show`?[[F,this.mergedShow],[ie,this.handleMenuClickOutside,void 0,{capture:!0}]]:[[ie,this.handleMenuClickOutside,void 0,{capture:!0}]])):null}})})]}))}});export{nt as a,He as c,st as i,Re as l,Ct as n,Ke as o,yt as r,We as s,Ot as t};
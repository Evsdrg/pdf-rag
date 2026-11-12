import{$t as e,A as t,An as n,B as r,Bt as i,Ct as a,D as o,Dt as s,E as c,Ft as l,G as u,Gt as d,Ht as f,I as p,In as m,Kt as h,L as g,Lt as _,M as v,Mn as y,Ot as b,Rt as x,Sn as S,St as C,T as w,Tn as T,Tt as E,U as D,Ut as O,W as k,Wt as A,X as j,Zt as ee,_n as M,an as N,at as P,b as F,bn as I,bt as L,dt as te,fn as R,gn as z,hn as B,k as V,kn as H,lt as U,m as W,mn as G,nt as K,ot as ne,pn as q,pt as J,qt as Y,rn as re,rt as ie,s as X,st as Z,tt as ae,ut as oe,vn as se,vt as ce,w as le,xn as ue,xt as de,yt as fe,zn as Q,zt as pe}from"./_plugin-vue_export-helper-BL3uulyl.js";import{A as me,M as he,N as ge,P as _e,j as ve}from"./api-CSoYMIuI.js";import{C as ye,E as be,F as xe,I as Se,M as $,S as Ce,T as we,m as Te,w as Ee,y as De}from"./index-DFXqAcyu.js";function Oe(e){return e&-e}var ke=class{constructor(e,t){this.l=e,this.min=t;let n=Array(e+1);for(let t=0;t<e+1;++t)n[t]=0;this.ft=n}add(e,t){if(t===0)return;let{l:n,ft:r}=this;for(e+=1;e<=n;)r[e]+=t,e+=Oe(e)}get(e){return this.sum(e+1)-this.sum(e)}sum(e){if(e===void 0&&(e=this.l),e<=0)return 0;let{ft:t,min:n,l:r}=this;if(e>r)throw Error("[FinweckTree.sum]: `i` is larger than length.");let i=e*n;for(;e>0;)i+=t[e],e-=Oe(e);return i}getBound(e){let t=0,n=this.l;for(;n>t;){let r=Math.floor((t+n)/2),i=this.sum(r);if(i>e){n=r;continue}if(i<e){if(t===r)return this.sum(t+1)<=e?t+1:r;t=r}else return r}return t}},Ae;function je(){return typeof document>`u`?!1:(Ae===void 0&&(Ae=`matchMedia`in window&&window.matchMedia(`(pointer:coarse)`).matches),Ae)}var Me;function Ne(){return typeof document>`u`?1:(Me===void 0&&(Me=`chrome`in window?window.devicePixelRatio:1),Me)}var Pe=`VVirtualListXScroll`;function Fe({columnsRef:e,renderColRef:t,renderItemWithColsRef:n}){let r=m(0),i=m(0),a=N(()=>{let t=e.value;if(t.length===0)return null;let n=new ke(t.length,0);return t.forEach((e,t)=>{n.add(t,e.width)}),n}),o=E(()=>{let e=a.value;return e===null?0:Math.max(e.getBound(i.value)-1,0)}),s=e=>{let t=a.value;return t===null?0:t.sum(e)},c=E(()=>{let t=a.value;return t===null?0:Math.min(t.getBound(i.value+r.value)+1,e.value.length-1)});return T(Pe,{startIndexRef:o,endIndexRef:c,columnsRef:e,renderColRef:t,renderItemWithColsRef:n,getLeft:s}),{listWidthRef:r,scrollLeftRef:i}}var Ie=R({name:`VirtualListRow`,props:{index:{type:Number,required:!0},item:{type:Object,required:!0}},setup(){let{startIndexRef:e,endIndexRef:t,columnsRef:n,getLeft:r,renderColRef:i,renderItemWithColsRef:a}=B(Pe);return{startIndex:e,endIndex:t,columns:n,renderCol:i,renderItemWithCols:a,getLeft:r}},render(){let{startIndex:e,endIndex:t,columns:n,renderCol:r,renderItemWithCols:i,getLeft:a,item:o}=this;if(i!=null)return i({itemIndex:this.index,startColIndex:e,endColIndex:t,allColumns:n,item:o,getLeft:a});if(r!=null){let i=[];for(let s=e;s<=t;++s){let e=n[s];i.push(r({column:e,left:a(s),item:o}))}return i}return null}}),Le=P(`.v-vl`,{maxHeight:`inherit`,height:`100%`,overflow:`auto`,minWidth:`1px`},[P(`&:not(.v-vl--show-scrollbar)`,{scrollbarWidth:`none`},[P(`&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb`,{width:0,height:0,display:`none`})])]),Re=R({name:`VirtualList`,inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},columns:{type:Array,default:()=>[]},renderCol:Function,renderItemWithCols:Function,items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:`div`},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:`key`},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(e){let t=Z();Le.mount({id:`vueuc/virtual-list`,head:!0,anchorMetaName:ne,ssr:t}),S(()=>{let{defaultScrollIndex:t,defaultScrollKey:n}=e;t==null?n!=null&&y({key:n}):y({index:t})});let n=!1,r=!1;se(()=>{if(n=!1,!r){r=!0;return}y({top:g.value,left:s.value})}),ue(()=>{n=!0,r||=!0});let a=E(()=>{if(e.renderCol==null&&e.renderItemWithCols==null||e.columns.length===0)return;let t=0;return e.columns.forEach(e=>{t+=e.width}),t}),o=N(()=>{let t=new Map,{keyField:n}=e;return e.items.forEach((e,r)=>{t.set(e[n],r)}),t}),{scrollLeftRef:s,listWidthRef:c}=Fe({columnsRef:Q(e,`columns`),renderColRef:Q(e,`renderCol`),renderItemWithColsRef:Q(e,`renderItemWithCols`)}),u=m(null),d=m(void 0),f=new Map,p=N(()=>{let{items:t,itemSize:n,keyField:r}=e,i=new ke(t.length,n);return t.forEach((e,t)=>{let n=e[r],a=f.get(n);a!==void 0&&i.add(t,a)}),i}),h=m(0),g=m(0),_=E(()=>Math.max(p.value.getBound(g.value-l(e.paddingTop))-1,0)),v=N(()=>{let{value:t}=d;if(t===void 0)return[];let{items:n,itemSize:r}=e,i=_.value,a=Math.min(i+Math.ceil(t/r+1),n.length-1),o=[];for(let e=i;e<=a;++e)o.push(n[e]);return o}),y=(e,t)=>{if(typeof e==`number`){T(e,t,`auto`);return}let{left:n,top:r,index:i,key:a,position:s,behavior:c,debounce:l=!0}=e;if(n!==void 0||r!==void 0)T(n,r,c);else if(i!==void 0)w(i,c,l);else if(a!==void 0){let e=o.value.get(a);e!==void 0&&w(e,c,l)}else s===`bottom`?T(0,2**53-1,c):s===`top`&&T(0,0,c)},b,C=null;function w(t,n,r){let{value:i}=p,a=i.sum(t)+l(e.paddingTop);if(!r)u.value.scrollTo({left:0,top:a,behavior:n});else{b=t,C!==null&&window.clearTimeout(C),C=window.setTimeout(()=>{b=void 0,C=null},16);let{scrollTop:e,offsetHeight:r}=u.value;if(a>e){let o=i.get(t);a+o<=e+r||u.value.scrollTo({left:0,top:a+o-r,behavior:n})}else u.value.scrollTo({left:0,top:a,behavior:n})}}function T(e,t,n){u.value.scrollTo({left:e,top:t,behavior:n})}function D(t,r){if(n||e.ignoreItemResize||P(r.target))return;let{value:i}=p,a=o.value.get(t),s=i.get(a),c=r.borderBoxSize?.[0]?.blockSize??r.contentRect.height;if(c===s)return;c-e.itemSize===0?f.delete(t):f.set(t,c-e.itemSize);let l=c-s;if(l===0)return;i.add(a,l);let d=u.value;if(d!=null){if(b===void 0){let e=i.sum(a);d.scrollTop>e&&d.scrollBy(0,l)}else(a<b||a===b&&c+i.sum(a)>d.scrollTop+d.offsetHeight)&&d.scrollBy(0,l);M()}h.value++}let O=!je(),k=!1;function A(t){var n;(n=e.onScroll)==null||n.call(e,t),(!O||!k)&&M()}function j(t){var n;if((n=e.onWheel)==null||n.call(e,t),O){let e=u.value;if(e!=null){if(t.deltaX===0&&(e.scrollTop===0&&t.deltaY<=0||e.scrollTop+e.offsetHeight>=e.scrollHeight&&t.deltaY>=0))return;t.preventDefault(),e.scrollTop+=t.deltaY/Ne(),e.scrollLeft+=t.deltaX/Ne(),M(),k=!0,i(()=>{k=!1})}}}function ee(t){if(n||P(t.target))return;if(e.renderCol==null&&e.renderItemWithCols==null){if(t.contentRect.height===d.value)return}else if(t.contentRect.height===d.value&&t.contentRect.width===c.value)return;d.value=t.contentRect.height,c.value=t.contentRect.width;let{onResize:r}=e;r!==void 0&&r(t)}function M(){let{value:e}=u;e!=null&&(g.value=e.scrollTop,s.value=e.scrollLeft)}function P(e){let t=e;for(;t!==null;){if(t.style.display===`none`)return!0;t=t.parentElement}return!1}return{listHeight:d,listStyle:{overflow:`auto`},keyToIndex:o,itemsStyle:N(()=>{let{itemResizable:t}=e,n=x(p.value.sum());return h.value,[e.itemsStyle,{boxSizing:`content-box`,width:x(a.value),height:t?``:n,minHeight:t?n:``,paddingTop:x(e.paddingTop),paddingBottom:x(e.paddingBottom)}]}),visibleItemsStyle:N(()=>(h.value,{transform:`translateY(${x(p.value.sum(_.value))})`})),viewportItems:v,listElRef:u,itemsElRef:m(null),scrollTo:y,handleListResize:ee,handleListScroll:A,handleListWheel:j,handleItemResize:D}},render(){let{itemResizable:e,keyField:t,keyToIndex:n,visibleItemsTag:r}=this;return G(ae,{onResize:this.handleListResize},{default:()=>{var i;return G(`div`,z(this.$attrs,{class:[`v-vl`,this.showScrollbar&&`v-vl--show-scrollbar`],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:`listElRef`}),[this.items.length===0?(i=this.$slots).empty?.call(i):G(`div`,{ref:`itemsElRef`,class:`v-vl-items`,style:this.itemsStyle},[G(r,Object.assign({class:`v-vl-visible-items`,style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>{let{renderCol:r,renderItemWithCols:i}=this;return this.viewportItems.map(a=>{let o=a[t],s=n.get(o),c=r==null?void 0:G(Ie,{index:s,item:a}),l=i==null?void 0:G(Ie,{index:s,item:a}),u=this.$slots.default({item:a,renderedCols:c,renderedItemWithCols:l,index:s})[0];return e?G(ae,{key:o,onResize:e=>this.handleItemResize(o,e)},{default:()=>u}):(u.key=o,u)})}})])])}})}});function ze(e,t){t&&(S(()=>{let{value:n}=e;n&&K.registerHandler(n,t)}),H(e,(e,t)=>{t&&K.unregisterHandler(t)},{deep:!1}),I(()=>{let{value:t}=e;t&&K.unregisterHandler(t)}))}var Be=new WeakSet;function Ve(e){Be.add(e)}function He(e){return!Be.has(e)}function Ue(e){switch(typeof e){case`string`:return e||void 0;case`number`:return String(e);default:return}}function We(e){let t=e.filter(e=>e!==void 0);if(t.length!==0)return t.length===1?t[0]:t=>{e.forEach(e=>{e&&e(t)})}}var Ge=R({name:`Checkmark`,render(){return G(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 16 16`},G(`g`,{fill:`none`},G(`path`,{d:`M14.046 3.486a.75.75 0 0 1-.032 1.06l-7.93 7.474a.85.85 0 0 1-1.188-.022l-2.68-2.72a.75.75 0 1 1 1.068-1.053l2.234 2.267l7.468-7.038a.75.75 0 0 1 1.06.032z`,fill:`currentColor`})))}}),Ke=R({name:`ChevronDown`,render(){return G(`svg`,{viewBox:`0 0 16 16`,fill:`none`,xmlns:`http://www.w3.org/2000/svg`},G(`path`,{d:`M3.14645 5.64645C3.34171 5.45118 3.65829 5.45118 3.85355 5.64645L8 9.79289L12.1464 5.64645C12.3417 5.45118 12.6583 5.45118 12.8536 5.64645C13.0488 5.84171 13.0488 6.15829 12.8536 6.35355L8.35355 10.8536C8.15829 11.0488 7.84171 11.0488 7.64645 10.8536L3.14645 6.35355C2.95118 6.15829 2.95118 5.84171 3.14645 5.64645Z`,fill:`currentColor`}))}}),qe=w(`clear`,()=>G(`svg`,{viewBox:`0 0 16 16`,version:`1.1`,xmlns:`http://www.w3.org/2000/svg`},G(`g`,{stroke:`none`,"stroke-width":`1`,fill:`none`,"fill-rule":`evenodd`},G(`g`,{fill:`currentColor`,"fill-rule":`nonzero`},G(`path`,{d:`M8,2 C11.3137085,2 14,4.6862915 14,8 C14,11.3137085 11.3137085,14 8,14 C4.6862915,14 2,11.3137085 2,8 C2,4.6862915 4.6862915,2 8,2 Z M6.5343055,5.83859116 C6.33943736,5.70359511 6.07001296,5.72288026 5.89644661,5.89644661 L5.89644661,5.89644661 L5.83859116,5.9656945 C5.70359511,6.16056264 5.72288026,6.42998704 5.89644661,6.60355339 L5.89644661,6.60355339 L7.293,8 L5.89644661,9.39644661 L5.83859116,9.4656945 C5.70359511,9.66056264 5.72288026,9.92998704 5.89644661,10.1035534 L5.89644661,10.1035534 L5.9656945,10.1614088 C6.16056264,10.2964049 6.42998704,10.2771197 6.60355339,10.1035534 L6.60355339,10.1035534 L8,8.707 L9.39644661,10.1035534 L9.4656945,10.1614088 C9.66056264,10.2964049 9.92998704,10.2771197 10.1035534,10.1035534 L10.1035534,10.1035534 L10.1614088,10.0343055 C10.2964049,9.83943736 10.2771197,9.57001296 10.1035534,9.39644661 L10.1035534,9.39644661 L8.707,8 L10.1035534,6.60355339 L10.1614088,6.5343055 C10.2964049,6.33943736 10.2771197,6.07001296 10.1035534,5.89644661 L10.1035534,5.89644661 L10.0343055,5.83859116 C9.83943736,5.70359511 9.57001296,5.72288026 9.39644661,5.89644661 L9.39644661,5.89644661 L8,7.293 L6.60355339,5.89644661 Z`}))))),Je=R({name:`Eye`,render(){return G(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 512 512`},G(`path`,{d:`M255.66 112c-77.94 0-157.89 45.11-220.83 135.33a16 16 0 0 0-.27 17.77C82.92 340.8 161.8 400 255.66 400c92.84 0 173.34-59.38 221.79-135.25a16.14 16.14 0 0 0 0-17.47C428.89 172.28 347.8 112 255.66 112z`,fill:`none`,stroke:`currentColor`,"stroke-linecap":`round`,"stroke-linejoin":`round`,"stroke-width":`32`}),G(`circle`,{cx:`256`,cy:`256`,r:`80`,fill:`none`,stroke:`currentColor`,"stroke-miterlimit":`10`,"stroke-width":`32`}))}}),Ye=R({name:`EyeOff`,render(){return G(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 512 512`},G(`path`,{d:`M432 448a15.92 15.92 0 0 1-11.31-4.69l-352-352a16 16 0 0 1 22.62-22.62l352 352A16 16 0 0 1 432 448z`,fill:`currentColor`}),G(`path`,{d:`M255.66 384c-41.49 0-81.5-12.28-118.92-36.5c-34.07-22-64.74-53.51-88.7-91v-.08c19.94-28.57 41.78-52.73 65.24-72.21a2 2 0 0 0 .14-2.94L93.5 161.38a2 2 0 0 0-2.71-.12c-24.92 21-48.05 46.76-69.08 76.92a31.92 31.92 0 0 0-.64 35.54c26.41 41.33 60.4 76.14 98.28 100.65C162 402 207.9 416 255.66 416a239.13 239.13 0 0 0 75.8-12.58a2 2 0 0 0 .77-3.31l-21.58-21.58a4 4 0 0 0-3.83-1a204.8 204.8 0 0 1-51.16 6.47z`,fill:`currentColor`}),G(`path`,{d:`M490.84 238.6c-26.46-40.92-60.79-75.68-99.27-100.53C349 110.55 302 96 255.66 96a227.34 227.34 0 0 0-74.89 12.83a2 2 0 0 0-.75 3.31l21.55 21.55a4 4 0 0 0 3.88 1a192.82 192.82 0 0 1 50.21-6.69c40.69 0 80.58 12.43 118.55 37c34.71 22.4 65.74 53.88 89.76 91a.13.13 0 0 1 0 .16a310.72 310.72 0 0 1-64.12 72.73a2 2 0 0 0-.15 2.95l19.9 19.89a2 2 0 0 0 2.7.13a343.49 343.49 0 0 0 68.64-78.48a32.2 32.2 0 0 0-.1-34.78z`,fill:`currentColor`}),G(`path`,{d:`M256 160a95.88 95.88 0 0 0-21.37 2.4a2 2 0 0 0-1 3.38l112.59 112.56a2 2 0 0 0 3.38-1A96 96 0 0 0 256 160z`,fill:`currentColor`}),G(`path`,{d:`M165.78 233.66a2 2 0 0 0-3.38 1a96 96 0 0 0 115 115a2 2 0 0 0 1-3.38z`,fill:`currentColor`}))}}),Xe=O(`base-clear`,`
 flex-shrink: 0;
 height: 1em;
 width: 1em;
 position: relative;
`,[f(`>`,[A(`clear`,`
 font-size: var(--n-clear-size);
 height: 1em;
 width: 1em;
 cursor: pointer;
 color: var(--n-clear-color);
 transition: color .3s var(--n-bezier);
 display: flex;
 `,[f(`&:hover`,`
 color: var(--n-clear-color-hover)!important;
 `),f(`&:active`,`
 color: var(--n-clear-color-pressed)!important;
 `)]),A(`placeholder`,`
 display: flex;
 `),A(`clear, placeholder`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 `,[le({originalTransform:`translateX(-50%) translateY(-50%)`,left:`50%`,top:`50%`})])])]),Ze=R({name:`BaseClear`,props:{clsPrefix:{type:String,required:!0},show:Boolean,onClear:Function},setup(e){return t(`-base-clear`,Xe,Q(e,`clsPrefix`)),{handleMouseDown(e){e.preventDefault()}}},render(){let{clsPrefix:e}=this;return G(`div`,{class:`${e}-base-clear`},G(c,null,{default:()=>{var t;return this.show?G(`div`,{key:`dismiss`,class:`${e}-base-clear__clear`,onClick:this.onClear,onMousedown:this.handleMouseDown,"data-clear":!0},D(this.$slots.icon,()=>[G(o,{clsPrefix:e},{default:()=>G(qe,null)})])):G(`div`,{key:`icon`,class:`${e}-base-clear__placeholder`},(t=this.$slots).placeholder?.call(t))}}))}}),Qe=R({props:{onFocus:Function,onBlur:Function},setup(e){return()=>G(`div`,{style:`width: 0; height: 0`,tabindex:0,onFocus:e.onFocus,onBlur:e.onBlur})}}),$e=R({name:`NBaseSelectGroupHeader`,props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(){let{renderLabelRef:e,renderOptionRef:t,labelFieldRef:n,nodePropsRef:r}=B(fe);return{labelField:n,nodeProps:r,renderLabel:e,renderOption:t}},render(){let{clsPrefix:e,renderLabel:t,renderOption:n,nodeProps:r,tmNode:{rawNode:i}}=this,a=r?.(i),o=t?t(i,!1):$(i[this.labelField],i,!1),s=G(`div`,Object.assign({},a,{class:[`${e}-base-select-group-header`,a?.class]}),o);return i.render?i.render({node:s,option:i}):n?n({node:s,option:i,selected:!1}):s}});function et(e,t){return G(ee,{name:`fade-in-scale-up-transition`},{default:()=>e?G(o,{clsPrefix:t,class:`${t}-base-select-option__check`},{default:()=>G(Ge)}):null})}var tt=R({name:`NBaseSelectOption`,props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(e){let{valueRef:t,pendingTmNodeRef:n,multipleRef:r,valueSetRef:i,renderLabelRef:a,renderOptionRef:o,labelFieldRef:s,valueFieldRef:c,showCheckmarkRef:l,nodePropsRef:u,handleOptionClick:d,handleOptionMouseEnter:f}=B(fe),p=E(()=>{let{value:t}=n;return t?e.tmNode.key===t.key:!1});function m(t){let{tmNode:n}=e;n.disabled||d(t,n)}function h(t){let{tmNode:n}=e;n.disabled||f(t,n)}function g(t){let{tmNode:n}=e,{value:r}=p;n.disabled||r||f(t,n)}return{multiple:r,isGrouped:E(()=>{let{tmNode:t}=e,{parent:n}=t;return n&&n.rawNode.type===`group`}),showCheckmark:l,nodeProps:u,isPending:p,isSelected:E(()=>{let{value:n}=t,{value:a}=r;if(n===null)return!1;let o=e.tmNode.rawNode[c.value];if(a){let{value:e}=i;return e.has(o)}return n===o}),labelField:s,renderLabel:a,renderOption:o,handleMouseMove:g,handleMouseEnter:h,handleClick:m}},render(){let{clsPrefix:e,tmNode:{rawNode:t},isSelected:n,isPending:r,isGrouped:i,showCheckmark:a,nodeProps:o,renderOption:s,renderLabel:c,handleClick:l,handleMouseEnter:u,handleMouseMove:d}=this,f=et(n,e),p=c?[c(t,n),a&&f]:[$(t[this.labelField],t,n),a&&f],m=o?.(t),h=G(`div`,Object.assign({},m,{class:[`${e}-base-select-option`,t.class,m?.class,{[`${e}-base-select-option--disabled`]:t.disabled,[`${e}-base-select-option--selected`]:n,[`${e}-base-select-option--grouped`]:i,[`${e}-base-select-option--pending`]:r,[`${e}-base-select-option--show-checkmark`]:a}],style:[m?.style||``,t.style||``],onClick:We([l,m?.onClick]),onMouseenter:We([u,m?.onMouseenter]),onMousemove:We([d,m?.onMousemove])}),G(`div`,{class:`${e}-base-select-option__content`},p));return t.render?t.render({node:h,option:t,selected:n}):s?s({node:h,option:t,selected:n}):h}}),nt=O(`base-select-menu`,`
 line-height: 1.5;
 outline: none;
 z-index: 0;
 position: relative;
 border-radius: var(--n-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-color);
`,[O(`scrollbar`,`
 max-height: var(--n-height);
 `),O(`virtual-list`,`
 max-height: var(--n-height);
 `),O(`base-select-option`,`
 min-height: var(--n-option-height);
 font-size: var(--n-option-font-size);
 display: flex;
 align-items: center;
 `,[A(`content`,`
 z-index: 1;
 white-space: nowrap;
 text-overflow: ellipsis;
 overflow: hidden;
 `)]),O(`base-select-group-header`,`
 min-height: var(--n-option-height);
 font-size: .93em;
 display: flex;
 align-items: center;
 `),O(`base-select-menu-option-wrapper`,`
 position: relative;
 width: 100%;
 `),A(`loading, empty`,`
 display: flex;
 padding: 12px 32px;
 flex: 1;
 justify-content: center;
 `),A(`loading`,`
 color: var(--n-loading-color);
 font-size: var(--n-loading-size);
 `),A(`header`,`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),A(`action`,`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-top: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),O(`base-select-group-header`,`
 position: relative;
 cursor: default;
 padding: var(--n-option-padding);
 color: var(--n-group-header-text-color);
 `),O(`base-select-option`,`
 cursor: pointer;
 position: relative;
 padding: var(--n-option-padding);
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 box-sizing: border-box;
 color: var(--n-option-text-color);
 opacity: 1;
 `,[d(`show-checkmark`,`
 padding-right: calc(var(--n-option-padding-right) + 20px);
 `),f(`&::before`,`
 content: "";
 position: absolute;
 left: 4px;
 right: 4px;
 top: 0;
 bottom: 0;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),f(`&:active`,`
 color: var(--n-option-text-color-pressed);
 `),d(`grouped`,`
 padding-left: calc(var(--n-option-padding-left) * 1.5);
 `),d(`pending`,[f(`&::before`,`
 background-color: var(--n-option-color-pending);
 `)]),d(`selected`,`
 color: var(--n-option-text-color-active);
 `,[f(`&::before`,`
 background-color: var(--n-option-color-active);
 `),d(`pending`,[f(`&::before`,`
 background-color: var(--n-option-color-active-pending);
 `)])]),d(`disabled`,`
 cursor: not-allowed;
 `,[h(`selected`,`
 color: var(--n-option-text-color-disabled);
 `),d(`selected`,`
 opacity: var(--n-option-opacity-disabled);
 `)]),A(`check`,`
 font-size: 16px;
 position: absolute;
 right: calc(var(--n-option-padding-right) - 4px);
 top: calc(50% - 7px);
 color: var(--n-option-check-color);
 transition: color .3s var(--n-bezier);
 `,[ye({enterScale:`0.5`})])])]),rt=R({name:`InternalSelectMenu`,props:Object.assign(Object.assign({},V.props),{clsPrefix:{type:String,required:!0},scrollable:{type:Boolean,default:!0},treeMate:{type:Object,required:!0},multiple:Boolean,size:{type:String,default:`medium`},value:{type:[String,Number,Array],default:null},autoPending:Boolean,virtualScroll:{type:Boolean,default:!0},show:{type:Boolean,default:!0},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},loading:Boolean,focusable:Boolean,renderLabel:Function,renderOption:Function,nodeProps:Function,showCheckmark:{type:Boolean,default:!0},onMousedown:Function,onScroll:Function,onFocus:Function,onBlur:Function,onKeyup:Function,onKeydown:Function,onTabOut:Function,onMouseenter:Function,onMouseleave:Function,onResize:Function,resetMenuOnOptionsChange:{type:Boolean,default:!0},inlineThemeDisabled:Boolean,scrollbarProps:Object,onToggle:Function}),setup(e){let{mergedClsPrefixRef:t,mergedRtlRef:n,mergedComponentPropsRef:r}=g(e),i=v(`InternalSelectMenu`,n,t),a=V(`InternalSelectMenu`,`-internal-select-menu`,nt,Ee,e,Q(e,`clsPrefix`)),o=m(null),s=m(null),c=m(null),u=N(()=>e.treeMate.getFlattenedNodes()),d=N(()=>be(u.value)),f=m(null);function h(){let{treeMate:t}=e,n=null,{value:r}=e;r===null?n=t.getFirstAvailableNode():(n=e.multiple?t.getNode((r||[])[(r||[]).length-1]):t.getNode(r),(!n||n.disabled)&&(n=t.getFirstAvailableNode())),U(n||null)}function y(){let{value:t}=f;t&&!e.treeMate.getNode(t.key)&&(f.value=null)}let b;H(()=>e.show,t=>{t?b=H(()=>e.treeMate,()=>{e.resetMenuOnOptionsChange?(e.autoPending?h():y(),M(W)):y()},{immediate:!0}):b?.()},{immediate:!0}),I(()=>{b?.()});let x=N(()=>l(a.value.self[Y(`optionHeight`,e.size)])),C=N(()=>_(a.value.self[Y(`padding`,e.size)])),w=N(()=>e.multiple&&Array.isArray(e.value)?new Set(e.value):new Set),E=N(()=>{let e=u.value;return e&&e.length===0}),D=N(()=>r?.value?.Select?.renderEmpty);function O(t){let{onToggle:n}=e;n&&n(t)}function k(t){let{onScroll:n}=e;n&&n(t)}function A(e){var t;(t=c.value)==null||t.sync(),k(e)}function j(){var e;(e=c.value)==null||e.sync()}function ee(){let{value:e}=f;return e||null}function P(e,t){t.disabled||U(t,!1)}function F(e,t){t.disabled||O(t)}function L(t){var n;Se(t,`action`)||(n=e.onKeyup)==null||n.call(e,t)}function te(t){var n;Se(t,`action`)||(n=e.onKeydown)==null||n.call(e,t)}function R(t){var n;(n=e.onMousedown)==null||n.call(e,t),!e.focusable&&t.preventDefault()}function z(){let{value:e}=f;e&&U(e.getNext({loop:!0}),!0)}function B(){let{value:e}=f;e&&U(e.getPrev({loop:!0}),!0)}function U(e,t=!1){f.value=e,t&&W()}function W(){var t,n;let r=f.value;if(!r)return;let i=d.value(r.key);i!==null&&(e.virtualScroll?(t=s.value)==null||t.scrollTo({index:i}):(n=c.value)==null||n.scrollTo({index:i,elSize:x.value}))}function G(t){var n;o.value?.contains(t.target)&&((n=e.onFocus)==null||n.call(e,t))}function K(t){var n;o.value?.contains(t.relatedTarget)||(n=e.onBlur)==null||n.call(e,t)}T(fe,{handleOptionMouseEnter:P,handleOptionClick:F,valueSetRef:w,pendingTmNodeRef:f,nodePropsRef:Q(e,`nodeProps`),showCheckmarkRef:Q(e,`showCheckmark`),multipleRef:Q(e,`multiple`),valueRef:Q(e,`value`),renderLabelRef:Q(e,`renderLabel`),renderOptionRef:Q(e,`renderOption`),labelFieldRef:Q(e,`labelField`),valueFieldRef:Q(e,`valueField`)}),T(ce,o),S(()=>{let{value:e}=c;e&&e.sync()});let ne=N(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{height:r,borderRadius:i,color:o,groupHeaderTextColor:s,actionDividerColor:c,optionTextColorPressed:l,optionTextColor:u,optionTextColorDisabled:d,optionTextColorActive:f,optionOpacityDisabled:p,optionCheckColor:m,actionTextColor:h,optionColorPending:g,optionColorActive:v,loadingColor:y,loadingSize:b,optionColorActivePending:x,[Y(`optionFontSize`,t)]:S,[Y(`optionHeight`,t)]:C,[Y(`optionPadding`,t)]:w}}=a.value;return{"--n-height":r,"--n-action-divider-color":c,"--n-action-text-color":h,"--n-bezier":n,"--n-border-radius":i,"--n-color":o,"--n-option-font-size":S,"--n-group-header-text-color":s,"--n-option-check-color":m,"--n-option-color-pending":g,"--n-option-color-active":v,"--n-option-color-active-pending":x,"--n-option-height":C,"--n-option-opacity-disabled":p,"--n-option-text-color":u,"--n-option-text-color-active":f,"--n-option-text-color-disabled":d,"--n-option-text-color-pressed":l,"--n-option-padding":w,"--n-option-padding-left":_(w,`left`),"--n-option-padding-right":_(w,`right`),"--n-loading-color":y,"--n-loading-size":b}}),{inlineThemeDisabled:q}=e,J=q?p(`internal-select-menu`,N(()=>e.size[0]),ne,e):void 0,re={selfRef:o,next:z,prev:B,getPendingTmNode:ee};return ze(o,e.onResize),Object.assign({mergedTheme:a,mergedClsPrefix:t,rtlEnabled:i,virtualListRef:s,scrollbarRef:c,itemSize:x,padding:C,flattenedNodes:u,empty:E,mergedRenderEmpty:D,virtualListContainer(){let{value:e}=s;return e?.listElRef},virtualListContent(){let{value:e}=s;return e?.itemsElRef},doScroll:k,handleFocusin:G,handleFocusout:K,handleKeyUp:L,handleKeyDown:te,handleMouseDown:R,handleVirtualListResize:j,handleVirtualListScroll:A,cssVars:q?void 0:ne,themeClass:J?.themeClass,onRender:J?.onRender},re)},render(){let{$slots:e,virtualScroll:t,clsPrefix:n,mergedTheme:r,themeClass:i,onRender:a}=this;return a?.(),G(`div`,{ref:`selfRef`,tabindex:this.focusable?0:-1,class:[`${n}-base-select-menu`,`${n}-base-select-menu--${this.size}-size`,this.rtlEnabled&&`${n}-base-select-menu--rtl`,i,this.multiple&&`${n}-base-select-menu--multiple`],style:this.cssVars,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onKeyup:this.handleKeyUp,onKeydown:this.handleKeyDown,onMousedown:this.handleMouseDown,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},u(e.header,e=>e&&G(`div`,{class:`${n}-base-select-menu__header`,"data-header":!0,key:`header`},e)),this.loading?G(`div`,{class:`${n}-base-select-menu__loading`},G(F,{clsPrefix:n,strokeWidth:20})):this.empty?G(`div`,{class:`${n}-base-select-menu__empty`,"data-empty":!0},D(e.empty,()=>[this.mergedRenderEmpty?.call(this)||G(he,{theme:r.peers.Empty,themeOverrides:r.peerOverrides.Empty,size:this.size})])):G(W,Object.assign({ref:`scrollbarRef`,theme:r.peers.Scrollbar,themeOverrides:r.peerOverrides.Scrollbar,scrollable:this.scrollable,container:t?this.virtualListContainer:void 0,content:t?this.virtualListContent:void 0,onScroll:t?void 0:this.doScroll},this.scrollbarProps),{default:()=>t?G(Re,{ref:`virtualListRef`,class:`${n}-virtual-list`,items:this.flattenedNodes,itemSize:this.itemSize,showScrollbar:!1,paddingTop:this.padding.top,paddingBottom:this.padding.bottom,onResize:this.handleVirtualListResize,onScroll:this.handleVirtualListScroll,itemResizable:!0},{default:({item:e})=>e.isGroup?G($e,{key:e.key,clsPrefix:n,tmNode:e}):e.ignored?null:G(tt,{clsPrefix:n,key:e.key,tmNode:e})}):G(`div`,{class:`${n}-base-select-menu-option-wrapper`,style:{paddingTop:this.padding.top,paddingBottom:this.padding.bottom}},this.flattenedNodes.map(e=>e.isGroup?G($e,{key:e.key,clsPrefix:n,tmNode:e}):G(tt,{clsPrefix:n,key:e.key,tmNode:e})))}),u(e.action,e=>e&&[G(`div`,{class:`${n}-base-select-menu__action`,"data-action":!0,key:`action`},e),G(Qe,{onFocus:this.onTabOut,key:`focus-detector`})]))}}),it=R({name:`InternalSelectionSuffix`,props:{clsPrefix:{type:String,required:!0},showArrow:{type:Boolean,default:void 0},showClear:{type:Boolean,default:void 0},loading:{type:Boolean,default:!1},onClear:Function},setup(e,{slots:t}){return()=>{let{clsPrefix:n}=e;return G(F,{clsPrefix:n,class:`${n}-base-suffix`,strokeWidth:24,scale:.85,show:e.loading},{default:()=>e.showArrow?G(Ze,{clsPrefix:n,show:e.showClear,onClear:e.onClear},{placeholder:()=>G(o,{clsPrefix:n,class:`${n}-base-suffix__arrow`},{default:()=>D(t.default,()=>[G(Ke,null)])})}):null})}}}),at=f([O(`base-selection`,`
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
 `,[O(`base-loading`,`
 color: var(--n-loading-color);
 `),O(`base-selection-tags`,`min-height: var(--n-height);`),A(`border, state-border`,`
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
 `),A(`state-border`,`
 z-index: 1;
 border-color: #0000;
 `),O(`base-suffix`,`
 cursor: pointer;
 position: absolute;
 top: 50%;
 transform: translateY(-50%);
 right: 10px;
 `,[A(`arrow`,`
 font-size: var(--n-arrow-size);
 color: var(--n-arrow-color);
 transition: color .3s var(--n-bezier);
 `)]),O(`base-selection-overlay`,`
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
 `,[A(`wrapper`,`
 flex-basis: 0;
 flex-grow: 1;
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),O(`base-selection-placeholder`,`
 color: var(--n-placeholder-color);
 `,[A(`inner`,`
 max-width: 100%;
 overflow: hidden;
 `)]),O(`base-selection-tags`,`
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
 `),O(`base-selection-label`,`
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
 `,[O(`base-selection-input`,`
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
 `,[A(`content`,`
 text-overflow: ellipsis;
 overflow: hidden;
 white-space: nowrap; 
 `)]),A(`render-label`,`
 color: var(--n-text-color);
 `)]),h(`disabled`,[f(`&:hover`,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-hover);
 border: var(--n-border-hover);
 `)]),d(`focus`,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-focus);
 border: var(--n-border-focus);
 `)]),d(`active`,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-active);
 border: var(--n-border-active);
 `),O(`base-selection-label`,`background-color: var(--n-color-active);`),O(`base-selection-tags`,`background-color: var(--n-color-active);`)])]),d(`disabled`,`cursor: not-allowed;`,[A(`arrow`,`
 color: var(--n-arrow-color-disabled);
 `),O(`base-selection-label`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[O(`base-selection-input`,`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 `),A(`render-label`,`
 color: var(--n-text-color-disabled);
 `)]),O(`base-selection-tags`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `),O(`base-selection-placeholder`,`
 cursor: not-allowed;
 color: var(--n-placeholder-color-disabled);
 `)]),O(`base-selection-input-tag`,`
 height: calc(var(--n-height) - 6px);
 line-height: calc(var(--n-height) - 6px);
 outline: none;
 display: none;
 position: relative;
 margin-bottom: 3px;
 max-width: 100%;
 vertical-align: bottom;
 `,[A(`input`,`
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
 `),A(`mirror`,`
 position: absolute;
 left: 0;
 top: 0;
 white-space: pre;
 visibility: hidden;
 user-select: none;
 -webkit-user-select: none;
 opacity: 0;
 `)]),[`warning`,`error`].map(e=>d(`${e}-status`,[A(`state-border`,`border: var(--n-border-${e});`),h(`disabled`,[f(`&:hover`,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-hover-${e});
 border: var(--n-border-hover-${e});
 `)]),d(`active`,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-active-${e});
 border: var(--n-border-active-${e});
 `),O(`base-selection-label`,`background-color: var(--n-color-active-${e});`),O(`base-selection-tags`,`background-color: var(--n-color-active-${e});`)]),d(`focus`,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),O(`base-selection-popover`,`
 margin-bottom: -3px;
 display: flex;
 flex-wrap: wrap;
 margin-right: -8px;
 `),O(`base-selection-tag-wrapper`,`
 max-width: 100%;
 display: inline-flex;
 padding: 0 7px 3px 0;
 `,[f(`&:last-child`,`padding-right: 0;`),O(`tag`,`
 font-size: 14px;
 max-width: 100%;
 `,[A(`content`,`
 line-height: 1.25;
 text-overflow: ellipsis;
 overflow: hidden;
 `)])])]),ot=R({name:`InternalSelection`,props:Object.assign(Object.assign({},V.props),{clsPrefix:{type:String,required:!0},bordered:{type:Boolean,default:void 0},active:Boolean,pattern:{type:String,default:``},placeholder:String,selectedOption:{type:Object,default:null},selectedOptions:{type:Array,default:null},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},multiple:Boolean,filterable:Boolean,clearable:Boolean,disabled:Boolean,size:{type:String,default:`medium`},loading:Boolean,autofocus:Boolean,showArrow:{type:Boolean,default:!0},inputProps:Object,focused:Boolean,renderTag:Function,onKeydown:Function,onClick:Function,onBlur:Function,onFocus:Function,onDeleteOption:Function,maxTagCount:[String,Number],ellipsisTagPopoverProps:Object,onClear:Function,onPatternInput:Function,onPatternFocus:Function,onPatternBlur:Function,renderLabel:Function,status:String,inlineThemeDisabled:Boolean,ignoreComposition:{type:Boolean,default:!0},onResize:Function}),setup(e){let{mergedClsPrefixRef:t,mergedRtlRef:r}=g(e),i=v(`InternalSelection`,r,t),a=m(null),o=m(null),s=m(null),c=m(null),l=m(null),u=m(null),d=m(null),f=m(null),h=m(null),y=m(null),b=m(!1),x=m(!1),C=m(!1),w=V(`InternalSelection`,`-internal-selection`,at,Ce,e,Q(e,`clsPrefix`)),T=N(()=>e.clearable&&!e.disabled&&(C.value||e.active)),E=N(()=>e.selectedOption?e.renderTag?e.renderTag({option:e.selectedOption,handleClose:()=>{}}):e.renderLabel?e.renderLabel(e.selectedOption,!0):$(e.selectedOption[e.labelField],e.selectedOption,!0):e.placeholder),D=N(()=>{let t=e.selectedOption;if(t)return t[e.labelField]}),O=N(()=>e.multiple?!!(Array.isArray(e.selectedOptions)&&e.selectedOptions.length):e.selectedOption!==null);function k(){var t;let{value:n}=a;if(n){let{value:r}=o;r&&(r.style.width=`${n.offsetWidth}px`,e.maxTagCount!==`responsive`&&((t=h.value)==null||t.sync({showAllItemsBeforeCalculate:!1})))}}function A(){let{value:e}=y;e&&(e.style.display=`none`)}function j(){let{value:e}=y;e&&(e.style.display=`inline-block`)}H(Q(e,`active`),e=>{e||A()}),H(Q(e,`pattern`),()=>{e.multiple&&M(k)});function ee(t){let{onFocus:n}=e;n&&n(t)}function P(t){let{onBlur:n}=e;n&&n(t)}function F(t){let{onDeleteOption:n}=e;n&&n(t)}function I(t){let{onClear:n}=e;n&&n(t)}function L(t){let{onPatternInput:n}=e;n&&n(t)}function te(e){(!e.relatedTarget||!s.value?.contains(e.relatedTarget))&&ee(e)}function R(e){s.value?.contains(e.relatedTarget)||P(e)}function z(e){I(e)}function B(){C.value=!0}function U(){C.value=!1}function W(t){!e.active||!e.filterable||t.target!==o.value&&t.preventDefault()}function G(e){F(e)}let K=m(!1);function ne(t){if(t.key===`Backspace`&&!K.value&&!e.pattern.length){let{selectedOptions:t}=e;t?.length&&G(t[t.length-1])}}let q=null;function J(t){let{value:n}=a;n&&(n.textContent=t.target.value,k()),e.ignoreComposition&&K.value?q=t:L(t)}function re(){K.value=!0}function ie(){K.value=!1,e.ignoreComposition&&L(q),q=null}function X(t){var n;x.value=!0,(n=e.onPatternFocus)==null||n.call(e,t)}function Z(t){var n;x.value=!1,(n=e.onPatternBlur)==null||n.call(e,t)}function ae(){var t,n;if(e.filterable)x.value=!1,(t=u.value)==null||t.blur(),(n=o.value)==null||n.blur();else if(e.multiple){let{value:e}=c;e?.blur()}else{let{value:e}=l;e?.blur()}}function oe(){var t,n,r;e.filterable?(x.value=!1,(t=u.value)==null||t.focus()):e.multiple?(n=c.value)==null||n.focus():(r=l.value)==null||r.focus()}function se(){let{value:e}=o;e&&(j(),e.focus())}function ce(){let{value:e}=o;e&&e.blur()}function le(e){let{value:t}=d;t&&t.setTextContent(`+${e}`)}function ue(){let{value:e}=f;return e}function de(){return o.value}let fe=null;function pe(){fe!==null&&window.clearTimeout(fe)}function me(){e.active||(pe(),fe=window.setTimeout(()=>{O.value&&(b.value=!0)},100))}function he(){pe()}function ge(e){e||(pe(),b.value=!1)}H(O,e=>{e||(b.value=!1)}),S(()=>{n(()=>{let t=u.value;t&&(e.disabled?t.removeAttribute(`tabindex`):t.tabIndex=x.value?-1:0)})}),ze(s,e.onResize);let{inlineThemeDisabled:_e}=e,ve=N(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontWeight:r,borderRadius:i,color:a,placeholderColor:o,textColor:s,paddingSingle:c,paddingMultiple:l,caretColor:u,colorDisabled:d,textColorDisabled:f,placeholderColorDisabled:p,colorActive:m,boxShadowFocus:h,boxShadowActive:g,boxShadowHover:v,border:y,borderFocus:b,borderHover:x,borderActive:S,arrowColor:C,arrowColorDisabled:T,loadingColor:E,colorActiveWarning:D,boxShadowFocusWarning:O,boxShadowActiveWarning:k,boxShadowHoverWarning:A,borderWarning:j,borderFocusWarning:ee,borderHoverWarning:M,borderActiveWarning:N,colorActiveError:P,boxShadowFocusError:F,boxShadowActiveError:I,boxShadowHoverError:L,borderError:te,borderFocusError:R,borderHoverError:z,borderActiveError:B,clearColor:V,clearColorHover:H,clearColorPressed:U,clearSize:W,arrowSize:G,[Y(`height`,t)]:K,[Y(`fontSize`,t)]:ne}}=w.value,q=_(c),J=_(l);return{"--n-bezier":n,"--n-border":y,"--n-border-active":S,"--n-border-focus":b,"--n-border-hover":x,"--n-border-radius":i,"--n-box-shadow-active":g,"--n-box-shadow-focus":h,"--n-box-shadow-hover":v,"--n-caret-color":u,"--n-color":a,"--n-color-active":m,"--n-color-disabled":d,"--n-font-size":ne,"--n-height":K,"--n-padding-single-top":q.top,"--n-padding-multiple-top":J.top,"--n-padding-single-right":q.right,"--n-padding-multiple-right":J.right,"--n-padding-single-left":q.left,"--n-padding-multiple-left":J.left,"--n-padding-single-bottom":q.bottom,"--n-padding-multiple-bottom":J.bottom,"--n-placeholder-color":o,"--n-placeholder-color-disabled":p,"--n-text-color":s,"--n-text-color-disabled":f,"--n-arrow-color":C,"--n-arrow-color-disabled":T,"--n-loading-color":E,"--n-color-active-warning":D,"--n-box-shadow-focus-warning":O,"--n-box-shadow-active-warning":k,"--n-box-shadow-hover-warning":A,"--n-border-warning":j,"--n-border-focus-warning":ee,"--n-border-hover-warning":M,"--n-border-active-warning":N,"--n-color-active-error":P,"--n-box-shadow-focus-error":F,"--n-box-shadow-active-error":I,"--n-box-shadow-hover-error":L,"--n-border-error":te,"--n-border-focus-error":R,"--n-border-hover-error":z,"--n-border-active-error":B,"--n-clear-size":W,"--n-clear-color":V,"--n-clear-color-hover":H,"--n-clear-color-pressed":U,"--n-arrow-size":G,"--n-font-weight":r}}),ye=_e?p(`internal-selection`,N(()=>e.size[0]),ve,e):void 0;return{mergedTheme:w,mergedClearable:T,mergedClsPrefix:t,rtlEnabled:i,patternInputFocused:x,filterablePlaceholder:E,label:D,selected:O,showTagsPanel:b,isComposing:K,counterRef:d,counterWrapperRef:f,patternInputMirrorRef:a,patternInputRef:o,selfRef:s,multipleElRef:c,singleElRef:l,patternInputWrapperRef:u,overflowRef:h,inputTagElRef:y,handleMouseDown:W,handleFocusin:te,handleClear:z,handleMouseEnter:B,handleMouseLeave:U,handleDeleteOption:G,handlePatternKeyDown:ne,handlePatternInputInput:J,handlePatternInputBlur:Z,handlePatternInputFocus:X,handleMouseEnterCounter:me,handleMouseLeaveCounter:he,handleFocusout:R,handleCompositionEnd:ie,handleCompositionStart:re,onPopoverUpdateShow:ge,focus:oe,focusInput:se,blur:ae,blurInput:ce,updateCounter:le,getCounter:ue,getTail:de,renderLabel:e.renderLabel,cssVars:_e?void 0:ve,themeClass:ye?.themeClass,onRender:ye?.onRender}},render(){let{status:e,multiple:t,size:n,disabled:i,filterable:a,maxTagCount:o,bordered:s,clsPrefix:c,ellipsisTagPopoverProps:l,onRender:u,renderTag:d,renderLabel:f}=this;u?.();let p=o===`responsive`,m=typeof o==`number`,h=p||m,g=G(r,null,{default:()=>G(it,{clsPrefix:c,loading:this.loading,showArrow:this.showArrow,showClear:this.mergedClearable&&this.selected,onClear:this.handleClear},{default:()=>{var e;return(e=this.$slots).arrow?.call(e)}})}),_;if(t){let{labelField:e}=this,t=t=>G(`div`,{class:`${c}-base-selection-tag-wrapper`,key:t.value},d?d({option:t,handleClose:()=>{this.handleDeleteOption(t)}}):G(ve,{size:n,closable:!t.disabled,disabled:i,onClose:()=>{this.handleDeleteOption(t)},internalCloseIsButtonTag:!1,internalCloseFocusable:!1},{default:()=>f?f(t,!0):$(t[e],t,!0)})),r=()=>(m?this.selectedOptions.slice(0,o):this.selectedOptions).map(t),s=a?G(`div`,{class:`${c}-base-selection-input-tag`,ref:`inputTagElRef`,key:`__input-tag__`},G(`input`,Object.assign({},this.inputProps,{ref:`patternInputRef`,tabindex:-1,disabled:i,value:this.pattern,autofocus:this.autofocus,class:`${c}-base-selection-input-tag__input`,onBlur:this.handlePatternInputBlur,onFocus:this.handlePatternInputFocus,onKeydown:this.handlePatternKeyDown,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),G(`span`,{ref:`patternInputMirrorRef`,class:`${c}-base-selection-input-tag__mirror`},this.pattern)):null,u=p?()=>G(`div`,{class:`${c}-base-selection-tag-wrapper`,ref:`counterWrapperRef`},G(ve,{size:n,ref:`counterRef`,onMouseenter:this.handleMouseEnterCounter,onMouseleave:this.handleMouseLeaveCounter,disabled:i})):void 0,v;if(m){let e=this.selectedOptions.length-o;e>0&&(v=G(`div`,{class:`${c}-base-selection-tag-wrapper`,key:`__counter__`},G(ve,{size:n,ref:`counterRef`,onMouseenter:this.handleMouseEnterCounter,disabled:i},{default:()=>`+${e}`})))}let y=p?a?G(xe,{ref:`overflowRef`,updateCounter:this.updateCounter,getCounter:this.getCounter,getTail:this.getTail,style:{width:`100%`,display:`flex`,overflow:`hidden`}},{default:r,counter:u,tail:()=>s}):G(xe,{ref:`overflowRef`,updateCounter:this.updateCounter,getCounter:this.getCounter,style:{width:`100%`,display:`flex`,overflow:`hidden`}},{default:r,counter:u}):m&&v?r().concat(v):r(),b=h?()=>G(`div`,{class:`${c}-base-selection-popover`},p?r():this.selectedOptions.map(t)):void 0,x=h?Object.assign({show:this.showTagsPanel,trigger:`hover`,overlap:!0,placement:`top`,width:`trigger`,onUpdateShow:this.onPopoverUpdateShow,theme:this.mergedTheme.peers.Popover,themeOverrides:this.mergedTheme.peerOverrides.Popover},l):null,S=!this.selected&&(!this.active||!this.pattern&&!this.isComposing)?G(`div`,{class:`${c}-base-selection-placeholder ${c}-base-selection-overlay`},G(`div`,{class:`${c}-base-selection-placeholder__inner`},this.placeholder)):null,C=a?G(`div`,{ref:`patternInputWrapperRef`,class:`${c}-base-selection-tags`},y,p?null:s,g):G(`div`,{ref:`multipleElRef`,class:`${c}-base-selection-tags`,tabindex:i?void 0:0},y,g);_=G(re,null,h?G(X,Object.assign({},x,{scrollable:!0,style:`max-height: calc(var(--v-target-height) * 6.6);`}),{trigger:()=>C,default:b}):C,S)}else if(a){let e=this.pattern||this.isComposing,t=this.active?!e:!this.selected,n=!this.active&&this.selected;_=G(`div`,{ref:`patternInputWrapperRef`,class:`${c}-base-selection-label`,title:this.patternInputFocused?void 0:Ue(this.label)},G(`input`,Object.assign({},this.inputProps,{ref:`patternInputRef`,class:`${c}-base-selection-input`,value:this.active?this.pattern:``,placeholder:``,readonly:i,disabled:i,tabindex:-1,autofocus:this.autofocus,onFocus:this.handlePatternInputFocus,onBlur:this.handlePatternInputBlur,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),n?G(`div`,{class:`${c}-base-selection-label__render-label ${c}-base-selection-overlay`,key:`input`},G(`div`,{class:`${c}-base-selection-overlay__wrapper`},d?d({option:this.selectedOption,handleClose:()=>{}}):f?f(this.selectedOption,!0):$(this.label,this.selectedOption,!0))):null,t?G(`div`,{class:`${c}-base-selection-placeholder ${c}-base-selection-overlay`,key:`placeholder`},G(`div`,{class:`${c}-base-selection-overlay__wrapper`},this.filterablePlaceholder)):null,g)}else _=G(`div`,{ref:`singleElRef`,class:`${c}-base-selection-label`,tabindex:this.disabled?void 0:0},this.label===void 0?G(`div`,{class:`${c}-base-selection-placeholder ${c}-base-selection-overlay`,key:`placeholder`},G(`div`,{class:`${c}-base-selection-placeholder__inner`},this.placeholder)):G(`div`,{class:`${c}-base-selection-input`,title:Ue(this.label),key:`input`},G(`div`,{class:`${c}-base-selection-input__content`},d?d({option:this.selectedOption,handleClose:()=>{}}):f?f(this.selectedOption,!0):$(this.label,this.selectedOption,!0))),g);return G(`div`,{ref:`selfRef`,class:[`${c}-base-selection`,this.rtlEnabled&&`${c}-base-selection--rtl`,this.themeClass,e&&`${c}-base-selection--${e}-status`,{[`${c}-base-selection--active`]:this.active,[`${c}-base-selection--selected`]:this.selected||this.active&&this.pattern,[`${c}-base-selection--disabled`]:this.disabled,[`${c}-base-selection--multiple`]:this.multiple,[`${c}-base-selection--focus`]:this.focused}],style:this.cssVars,onClick:this.onClick,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onKeydown:this.onKeydown,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onMousedown:this.handleMouseDown},_,s?G(`div`,{class:`${c}-base-selection__border`}):null,s?G(`div`,{class:`${c}-base-selection__state-border`}):null)}}),st=L(`n-input`),ct=O(`input`,`
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
`,[A(`input, textarea`,`
 overflow: hidden;
 flex-grow: 1;
 position: relative;
 `),A(`input-el, textarea-el, input-mirror, textarea-mirror, separator, placeholder`,`
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
 `),A(`input-el, textarea-el`,`
 -webkit-appearance: none;
 scrollbar-width: none;
 width: 100%;
 min-width: 0;
 text-decoration-color: var(--n-text-decoration-color);
 color: var(--n-text-color);
 caret-color: var(--n-caret-color);
 background-color: transparent;
 `,[f(`&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb`,`
 width: 0;
 height: 0;
 display: none;
 `),f(`&::placeholder`,`
 color: #0000;
 -webkit-text-fill-color: transparent !important;
 `),f(`&:-webkit-autofill ~`,[A(`placeholder`,`display: none;`)])]),d(`round`,[h(`textarea`,`border-radius: calc(var(--n-height) / 2);`)]),A(`placeholder`,`
 pointer-events: none;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 overflow: hidden;
 color: var(--n-placeholder-color);
 `,[f(`span`,`
 width: 100%;
 display: inline-block;
 `)]),d(`textarea`,[A(`placeholder`,`overflow: visible;`)]),h(`autosize`,`width: 100%;`),d(`autosize`,[A(`textarea-el, input-el`,`
 position: absolute;
 top: 0;
 left: 0;
 height: 100%;
 `)]),O(`input-wrapper`,`
 overflow: hidden;
 display: inline-flex;
 flex-grow: 1;
 position: relative;
 padding-left: var(--n-padding-left);
 padding-right: var(--n-padding-right);
 `),A(`input-mirror`,`
 padding: 0;
 height: var(--n-height);
 line-height: var(--n-height);
 overflow: hidden;
 visibility: hidden;
 position: static;
 white-space: pre;
 pointer-events: none;
 `),A(`input-el`,`
 padding: 0;
 height: var(--n-height);
 line-height: var(--n-height);
 `,[f(`&[type=password]::-ms-reveal`,`display: none;`),f(`+`,[A(`placeholder`,`
 display: flex;
 align-items: center; 
 `)])]),h(`textarea`,[A(`placeholder`,`white-space: nowrap;`)]),A(`eye`,`
 display: flex;
 align-items: center;
 justify-content: center;
 transition: color .3s var(--n-bezier);
 `),d(`textarea`,`width: 100%;`,[O(`input-word-count`,`
 position: absolute;
 right: var(--n-padding-right);
 bottom: var(--n-padding-vertical);
 `),d(`resizable`,[O(`input-wrapper`,`
 resize: vertical;
 min-height: var(--n-height);
 `)]),A(`textarea-el, textarea-mirror, placeholder`,`
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
 `),A(`textarea-mirror`,`
 width: 100%;
 pointer-events: none;
 overflow: hidden;
 visibility: hidden;
 position: static;
 white-space: pre-wrap;
 overflow-wrap: break-word;
 `)]),d(`pair`,[A(`input-el, placeholder`,`text-align: center;`),A(`separator`,`
 display: flex;
 align-items: center;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 white-space: nowrap;
 `,[O(`icon`,`
 color: var(--n-icon-color);
 `),O(`base-icon`,`
 color: var(--n-icon-color);
 `)])]),d(`disabled`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[A(`border`,`border: var(--n-border-disabled);`),A(`input-el, textarea-el`,`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 text-decoration-color: var(--n-text-color-disabled);
 `),A(`placeholder`,`color: var(--n-placeholder-color-disabled);`),A(`separator`,`color: var(--n-text-color-disabled);`,[O(`icon`,`
 color: var(--n-icon-color-disabled);
 `),O(`base-icon`,`
 color: var(--n-icon-color-disabled);
 `)]),O(`input-word-count`,`
 color: var(--n-count-text-color-disabled);
 `),A(`suffix, prefix`,`color: var(--n-text-color-disabled);`,[O(`icon`,`
 color: var(--n-icon-color-disabled);
 `),O(`internal-icon`,`
 color: var(--n-icon-color-disabled);
 `)])]),h(`disabled`,[A(`eye`,`
 color: var(--n-icon-color);
 cursor: pointer;
 `,[f(`&:hover`,`
 color: var(--n-icon-color-hover);
 `),f(`&:active`,`
 color: var(--n-icon-color-pressed);
 `)]),f(`&:hover`,[A(`state-border`,`border: var(--n-border-hover);`)]),d(`focus`,`background-color: var(--n-color-focus);`,[A(`state-border`,`
 border: var(--n-border-focus);
 box-shadow: var(--n-box-shadow-focus);
 `)])]),A(`border, state-border`,`
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
 `),A(`state-border`,`
 border-color: #0000;
 z-index: 1;
 `),A(`prefix`,`margin-right: 4px;`),A(`suffix`,`
 margin-left: 4px;
 `),A(`suffix, prefix`,`
 transition: color .3s var(--n-bezier);
 flex-wrap: nowrap;
 flex-shrink: 0;
 line-height: var(--n-height);
 white-space: nowrap;
 display: inline-flex;
 align-items: center;
 justify-content: center;
 color: var(--n-suffix-text-color);
 `,[O(`base-loading`,`
 font-size: var(--n-icon-size);
 margin: 0 2px;
 color: var(--n-loading-color);
 `),O(`base-clear`,`
 font-size: var(--n-icon-size);
 `,[A(`placeholder`,[O(`base-icon`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-icon-color);
 font-size: var(--n-icon-size);
 `)])]),f(`>`,[O(`icon`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-icon-color);
 font-size: var(--n-icon-size);
 `)]),O(`base-icon`,`
 font-size: var(--n-icon-size);
 `)]),O(`input-word-count`,`
 pointer-events: none;
 line-height: 1.5;
 font-size: .85em;
 color: var(--n-count-text-color);
 transition: color .3s var(--n-bezier);
 margin-left: 4px;
 font-variant: tabular-nums;
 `),[`warning`,`error`].map(e=>d(`${e}-status`,[h(`disabled`,[O(`base-loading`,`
 color: var(--n-loading-color-${e})
 `),A(`input-el, textarea-el`,`
 caret-color: var(--n-caret-color-${e});
 `),A(`state-border`,`
 border: var(--n-border-${e});
 `),f(`&:hover`,[A(`state-border`,`
 border: var(--n-border-hover-${e});
 `)]),f(`&:focus`,`
 background-color: var(--n-color-focus-${e});
 `,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)]),d(`focus`,`
 background-color: var(--n-color-focus-${e});
 `,[A(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),lt=O(`input`,[d(`disabled`,[A(`input-el, textarea-el`,`
 -webkit-text-fill-color: var(--n-text-color-disabled);
 `)])]);function ut(e){let t=0;for(let n of e)t++;return t}function dt(e){return e===``||e==null}function ft(e){let t=m(null);function n(){let{value:n}=e;if(!n?.focus){i();return}let{selectionStart:r,selectionEnd:a,value:o}=n;if(r==null||a==null){i();return}t.value={start:r,end:a,beforeText:o.slice(0,r),afterText:o.slice(a)}}function r(){var n;let{value:r}=t,{value:i}=e;if(!r||!i)return;let{value:a}=i,{start:o,beforeText:s,afterText:c}=r,l=a.length;if(a.endsWith(c))l=a.length-c.length;else if(a.startsWith(s))l=s.length;else{let e=s[o-1],t=a.indexOf(e,o-1);t!==-1&&(l=t+1)}(n=i.setSelectionRange)==null||n.call(i,l,l)}function i(){t.value=null}return H(e,i),{recordCursor:n,restoreCursor:r}}var pt=R({name:`InputWordCount`,setup(e,{slots:t}){let{mergedValueRef:n,maxlengthRef:r,mergedClsPrefixRef:i,countGraphemesRef:a}=B(st),o=N(()=>{let{value:e}=n;return e===null||Array.isArray(e)?0:(a.value||ut)(e)});return()=>{let{value:e}=r,{value:a}=n;return G(`span`,{class:`${i.value}-input-word-count`},k(t.default,{value:a===null||Array.isArray(a)?``:a},()=>[e===void 0?o.value:`${o.value} / ${e}`]))}}}),mt=Object.assign(Object.assign({},V.props),{bordered:{type:Boolean,default:void 0},type:{type:String,default:`text`},placeholder:[Array,String],defaultValue:{type:[String,Array],default:null},value:[String,Array],disabled:{type:Boolean,default:void 0},size:String,rows:{type:[Number,String],default:3},round:Boolean,minlength:[String,Number],maxlength:[String,Number],clearable:Boolean,autosize:{type:[Boolean,Object],default:!1},pair:Boolean,separator:String,readonly:{type:[String,Boolean],default:!1},passivelyActivated:Boolean,showPasswordOn:String,stateful:{type:Boolean,default:!0},autofocus:Boolean,inputProps:Object,resizable:{type:Boolean,default:!0},showCount:Boolean,loading:{type:Boolean,default:void 0},allowInput:Function,renderCount:Function,onMousedown:Function,onKeydown:Function,onKeyup:[Function,Array],onInput:[Function,Array],onFocus:[Function,Array],onBlur:[Function,Array],onClick:[Function,Array],onChange:[Function,Array],onClear:[Function,Array],countGraphemes:Function,status:String,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],textDecoration:[String,Array],attrSize:{type:Number,default:20},onInputBlur:[Function,Array],onInputFocus:[Function,Array],onDeactivate:[Function,Array],onActivate:[Function,Array],onWrapperFocus:[Function,Array],onWrapperBlur:[Function,Array],internalDeactivateOnEnter:Boolean,internalForceFocus:Boolean,internalLoadingBeforeSuffix:{type:Boolean,default:!0},showPasswordToggle:Boolean}),ht=R({name:`Input`,props:mt,slots:Object,setup(e){let{mergedClsPrefixRef:r,mergedBorderedRef:i,inlineThemeDisabled:o,mergedRtlRef:c,mergedComponentPropsRef:l}=g(e),u=V(`Input`,`-input`,ct,De,e,r);me&&t(`-input-safari`,lt,r);let d=m(null),f=m(null),h=m(null),y=m(null),x=m(null),C=m(null),w=m(null),D=ft(w),O=m(null),{localeRef:k}=ge(`Input`),A=m(e.defaultValue),ee=Q(e,`value`),P=a(ee,A),F=_e(e,{mergedSize:t=>{let{size:n}=e;if(n)return n;let{mergedSize:r}=t||{};return r?.value?r.value:l?.value?.Input?.size||`medium`}}),{mergedSizeRef:I,mergedDisabledRef:L,mergedStatusRef:te}=F,R=m(!1),z=m(!1),B=m(!1),U=m(!1),W=null,G=N(()=>{let{placeholder:t,pair:n}=e;return n?Array.isArray(t)?t:t===void 0?[``,``]:[t,t]:t===void 0?[k.value.placeholder]:[t]}),K=N(()=>{let{value:e}=B,{value:t}=P,{value:n}=G;return!e&&(dt(t)||Array.isArray(t)&&dt(t[0]))&&n[0]}),ne=N(()=>{let{value:e}=B,{value:t}=P,{value:n}=G;return!e&&n[1]&&(dt(t)||Array.isArray(t)&&dt(t[1]))}),J=E(()=>e.internalForceFocus||R.value),re=E(()=>{if(L.value||e.readonly||!e.clearable||!J.value&&!z.value)return!1;let{value:t}=P,{value:n}=J;return e.pair?!!(Array.isArray(t)&&(t[0]||t[1]))&&(z.value||n):!!t&&(z.value||n)}),ie=N(()=>{let{showPasswordOn:t}=e;if(t)return t;if(e.showPasswordToggle)return`click`}),X=m(!1),Z=N(()=>{let{textDecoration:t}=e;return t?Array.isArray(t)?t.map(e=>({textDecoration:e})):[{textDecoration:t}]:[``,``]}),ae=m(void 0),oe=()=>{if(e.type===`textarea`){let{autosize:t}=e;if(t&&(ae.value=O.value?.$el?.offsetWidth),!f.value||typeof t==`boolean`)return;let{paddingTop:n,paddingBottom:r,lineHeight:i}=window.getComputedStyle(f.value),a=Number(n.slice(0,-2)),o=Number(r.slice(0,-2)),s=Number(i.slice(0,-2)),{value:c}=h;if(!c)return;if(t.minRows){let e=Math.max(t.minRows,1),n=`${a+o+s*e}px`;c.style.minHeight=n}if(t.maxRows){let e=`${a+o+s*t.maxRows}px`;c.style.maxHeight=e}}},se=N(()=>{let{maxlength:t}=e;return t===void 0?void 0:Number(t)});S(()=>{let{value:e}=P;Array.isArray(e)||Qe(e)});let ce=q().proxy;function le(t,n){let{onUpdateValue:r,"onUpdate:value":i,onInput:a}=e,{nTriggerFormInput:o}=F;r&&j(r,t,n),i&&j(i,t,n),a&&j(a,t,n),A.value=t,o()}function ue(t,n){let{onChange:r}=e,{nTriggerFormChange:i}=F;r&&j(r,t,n),A.value=t,i()}function de(t){let{onBlur:n}=e,{nTriggerFormBlur:r}=F;n&&j(n,t),r()}function fe(t){let{onFocus:n}=e,{nTriggerFormFocus:r}=F;n&&j(n,t),r()}function pe(t){let{onClear:n}=e;n&&j(n,t)}function he(t){let{onInputBlur:n}=e;n&&j(n,t)}function ve(t){let{onInputFocus:n}=e;n&&j(n,t)}function ye(){let{onDeactivate:t}=e;t&&j(t)}function be(){let{onActivate:t}=e;t&&j(t)}function xe(t){let{onClick:n}=e;n&&j(n,t)}function Se(t){let{onWrapperFocus:n}=e;n&&j(n,t)}function $(t){let{onWrapperBlur:n}=e;n&&j(n,t)}function Ce(){B.value=!0}function we(e){B.value=!1,e.target===C.value?Te(e,1):Te(e,0)}function Te(t,n=0,r=`input`){let i=t.target.value;if(Qe(i),t instanceof InputEvent&&!t.isComposing&&(B.value=!1),e.type===`textarea`){let{value:e}=O;e&&e.syncUnifiedContainer()}if(W=i,B.value)return;D.recordCursor();let a=Ee(i);if(a)if(!e.pair)r===`input`?le(i,{source:n}):ue(i,{source:n});else{let{value:e}=P;e=Array.isArray(e)?[e[0],e[1]]:[``,``],e[n]=i,r===`input`?le(e,{source:n}):ue(e,{source:n})}ce.$forceUpdate(),a||M(D.restoreCursor)}function Ee(t){let{countGraphemes:n,maxlength:r,minlength:i}=e;if(n){let e;if(r!==void 0&&(e===void 0&&(e=n(t)),e>Number(r))||i!==void 0&&(e===void 0&&(e=n(t)),e<Number(r)))return!1}let{allowInput:a}=e;return typeof a!=`function`||a(t)}function Oe(e){he(e),e.relatedTarget===d.value&&ye(),(e.relatedTarget===null||e.relatedTarget!==x.value&&e.relatedTarget!==C.value&&e.relatedTarget!==f.value)&&(U.value=!1),Me(e,`blur`),w.value=null}function ke(e,t){ve(e),R.value=!0,U.value=!0,be(),Me(e,`focus`),t===0?w.value=x.value:t===1?w.value=C.value:t===2&&(w.value=f.value)}function Ae(t){e.passivelyActivated&&($(t),Me(t,`blur`))}function je(t){e.passivelyActivated&&(R.value=!0,Se(t),Me(t,`focus`))}function Me(e,t){e.relatedTarget!==null&&(e.relatedTarget===x.value||e.relatedTarget===C.value||e.relatedTarget===f.value||e.relatedTarget===d.value)||(t===`focus`?(fe(e),R.value=!0):t===`blur`&&(de(e),R.value=!1))}function Ne(e,t){Te(e,t,`change`)}function Pe(e){xe(e)}function Fe(e){pe(e),Ie()}function Ie(){e.pair?(le([``,``],{source:`clear`}),ue([``,``],{source:`clear`})):(le(``,{source:`clear`}),ue(``,{source:`clear`}))}function Le(t){let{onMousedown:n}=e;n&&n(t);let{tagName:r}=t.target;if(r!==`INPUT`&&r!==`TEXTAREA`){if(e.resizable){let{value:e}=d;if(e){let{left:n,top:r,width:i,height:a}=e.getBoundingClientRect();if(n+i-14<t.clientX&&t.clientX<n+i&&r+a-14<t.clientY&&t.clientY<r+a)return}}t.preventDefault(),R.value||Ke()}}function Re(){var t;z.value=!0,e.type===`textarea`&&((t=O.value)==null||t.handleMouseEnterWrapper())}function ze(){var t;z.value=!1,e.type===`textarea`&&((t=O.value)==null||t.handleMouseLeaveWrapper())}function Be(){L.value||ie.value===`click`&&(X.value=!X.value)}function Ve(e){if(L.value)return;e.preventDefault();let t=e=>{e.preventDefault(),s(`mouseup`,document,t)};if(b(`mouseup`,document,t),ie.value!==`mousedown`)return;X.value=!0;let n=()=>{X.value=!1,s(`mouseup`,document,n)};b(`mouseup`,document,n)}function He(t){e.onKeyup&&j(e.onKeyup,t)}function Ue(t){switch(e.onKeydown&&j(e.onKeydown,t),t.key){case`Escape`:Ge();break;case`Enter`:We(t)}}function We(t){var n,r;if(e.passivelyActivated){let{value:i}=U;if(i){e.internalDeactivateOnEnter&&Ge();return}t.preventDefault(),e.type===`textarea`?(n=f.value)==null||n.focus():(r=x.value)==null||r.focus()}}function Ge(){e.passivelyActivated&&(U.value=!1,M(()=>{var e;(e=d.value)==null||e.focus()}))}function Ke(){var t,n,r;L.value||(e.passivelyActivated?(t=d.value)==null||t.focus():((n=f.value)==null||n.focus(),(r=x.value)==null||r.focus()))}function qe(){d.value?.contains(document.activeElement)&&document.activeElement.blur()}function Je(){var e,t;(e=f.value)==null||e.select(),(t=x.value)==null||t.select()}function Ye(){L.value||(f.value?f.value.focus():x.value&&x.value.focus())}function Xe(){let{value:e}=d;e?.contains(document.activeElement)&&e!==document.activeElement&&Ge()}function Ze(t){if(e.type===`textarea`){let{value:e}=f;e?.scrollTo(t)}else{let{value:e}=x;e?.scrollTo(t)}}function Qe(t){let{type:n,pair:r,autosize:i}=e;if(!r&&i)if(n===`textarea`){let{value:e}=h;e&&(e.textContent=`${t??``}\r\n`)}else{let{value:e}=y;e&&(t?e.textContent=t:e.innerHTML=`&nbsp;`)}}function $e(){oe()}let et=m({top:`0`});function tt(e){var t;let{scrollTop:n}=e.target;et.value.top=`${-n}px`,(t=O.value)==null||t.syncUnifiedContainer()}let nt=null;n(()=>{let{autosize:t,type:n}=e;t&&n===`textarea`?nt=H(P,e=>{!Array.isArray(e)&&e!==W&&Qe(e)}):nt?.()});let rt=null;n(()=>{e.type===`textarea`?rt=H(P,e=>{var t;!Array.isArray(e)&&e!==W&&((t=O.value)==null||t.syncUnifiedContainer())}):rt?.()}),T(st,{mergedValueRef:P,maxlengthRef:se,mergedClsPrefixRef:r,countGraphemesRef:Q(e,`countGraphemes`)});let it={wrapperElRef:d,inputElRef:x,textareaElRef:f,isCompositing:B,clear:Ie,focus:Ke,blur:qe,select:Je,deactivate:Xe,activate:Ye,scrollTo:Ze},at=v(`Input`,c,r),ot=N(()=>{let{value:e}=I,{common:{cubicBezierEaseInOut:t},self:{color:n,borderRadius:r,textColor:i,caretColor:a,caretColorError:o,caretColorWarning:s,textDecorationColor:c,border:l,borderDisabled:d,borderHover:f,borderFocus:p,placeholderColor:m,placeholderColorDisabled:h,lineHeightTextarea:g,colorDisabled:v,colorFocus:y,textColorDisabled:b,boxShadowFocus:x,iconSize:S,colorFocusWarning:C,boxShadowFocusWarning:w,borderWarning:T,borderFocusWarning:E,borderHoverWarning:D,colorFocusError:O,boxShadowFocusError:k,borderError:A,borderFocusError:j,borderHoverError:ee,clearSize:M,clearColor:N,clearColorHover:P,clearColorPressed:F,iconColor:L,iconColorDisabled:te,suffixTextColor:R,countTextColor:z,countTextColorDisabled:B,iconColorHover:V,iconColorPressed:H,loadingColor:U,loadingColorError:W,loadingColorWarning:G,fontWeight:K,[Y(`padding`,e)]:ne,[Y(`fontSize`,e)]:q,[Y(`height`,e)]:J}}=u.value,{left:re,right:ie}=_(ne);return{"--n-bezier":t,"--n-count-text-color":z,"--n-count-text-color-disabled":B,"--n-color":n,"--n-font-size":q,"--n-font-weight":K,"--n-border-radius":r,"--n-height":J,"--n-padding-left":re,"--n-padding-right":ie,"--n-text-color":i,"--n-caret-color":a,"--n-text-decoration-color":c,"--n-border":l,"--n-border-disabled":d,"--n-border-hover":f,"--n-border-focus":p,"--n-placeholder-color":m,"--n-placeholder-color-disabled":h,"--n-icon-size":S,"--n-line-height-textarea":g,"--n-color-disabled":v,"--n-color-focus":y,"--n-text-color-disabled":b,"--n-box-shadow-focus":x,"--n-loading-color":U,"--n-caret-color-warning":s,"--n-color-focus-warning":C,"--n-box-shadow-focus-warning":w,"--n-border-warning":T,"--n-border-focus-warning":E,"--n-border-hover-warning":D,"--n-loading-color-warning":G,"--n-caret-color-error":o,"--n-color-focus-error":O,"--n-box-shadow-focus-error":k,"--n-border-error":A,"--n-border-focus-error":j,"--n-border-hover-error":ee,"--n-loading-color-error":W,"--n-clear-color":N,"--n-clear-size":M,"--n-clear-color-hover":P,"--n-clear-color-pressed":F,"--n-icon-color":L,"--n-icon-color-hover":V,"--n-icon-color-pressed":H,"--n-icon-color-disabled":te,"--n-suffix-text-color":R}}),ut=o?p(`input`,N(()=>{let{value:e}=I;return e[0]}),ot,e):void 0;return Object.assign(Object.assign({},it),{wrapperElRef:d,inputElRef:x,inputMirrorElRef:y,inputEl2Ref:C,textareaElRef:f,textareaMirrorElRef:h,textareaScrollbarInstRef:O,rtlEnabled:at,uncontrolledValue:A,mergedValue:P,passwordVisible:X,mergedPlaceholder:G,showPlaceholder1:K,showPlaceholder2:ne,mergedFocus:J,isComposing:B,activated:U,showClearButton:re,mergedSize:I,mergedDisabled:L,textDecorationStyle:Z,mergedClsPrefix:r,mergedBordered:i,mergedShowPasswordOn:ie,placeholderStyle:et,mergedStatus:te,textAreaScrollContainerWidth:ae,handleTextAreaScroll:tt,handleCompositionStart:Ce,handleCompositionEnd:we,handleInput:Te,handleInputBlur:Oe,handleInputFocus:ke,handleWrapperBlur:Ae,handleWrapperFocus:je,handleMouseEnter:Re,handleMouseLeave:ze,handleMouseDown:Le,handleChange:Ne,handleClick:Pe,handleClear:Fe,handlePasswordToggleClick:Be,handlePasswordToggleMousedown:Ve,handleWrapperKeydown:Ue,handleWrapperKeyup:He,handleTextAreaMirrorResize:$e,getTextareaScrollContainer:()=>f.value,mergedTheme:u,cssVars:o?void 0:ot,themeClass:ut?.themeClass,onRender:ut?.onRender})},render(){let{mergedClsPrefix:e,mergedStatus:t,themeClass:n,type:r,countGraphemes:i,onRender:a}=this,s=this.$slots;return a?.(),G(`div`,{ref:`wrapperElRef`,class:[`${e}-input`,`${e}-input--${this.mergedSize}-size`,n,t&&`${e}-input--${t}-status`,{[`${e}-input--rtl`]:this.rtlEnabled,[`${e}-input--disabled`]:this.mergedDisabled,[`${e}-input--textarea`]:r===`textarea`,[`${e}-input--resizable`]:this.resizable&&!this.autosize,[`${e}-input--autosize`]:this.autosize,[`${e}-input--round`]:this.round&&r!==`textarea`,[`${e}-input--pair`]:this.pair,[`${e}-input--focus`]:this.mergedFocus,[`${e}-input--stateful`]:this.stateful}],style:this.cssVars,tabindex:!this.mergedDisabled&&this.passivelyActivated&&!this.activated?0:void 0,onFocus:this.handleWrapperFocus,onBlur:this.handleWrapperBlur,onClick:this.handleClick,onMousedown:this.handleMouseDown,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd,onKeyup:this.handleWrapperKeyup,onKeydown:this.handleWrapperKeydown},G(`div`,{class:`${e}-input-wrapper`},u(s.prefix,t=>t&&G(`div`,{class:`${e}-input__prefix`},t)),r===`textarea`?G(W,{ref:`textareaScrollbarInstRef`,class:`${e}-input__textarea`,container:this.getTextareaScrollContainer,theme:this.theme?.peers?.Scrollbar,themeOverrides:this.themeOverrides?.peers?.Scrollbar,triggerDisplayManually:!0,useUnifiedContainer:!0,internalHoistYRail:!0},{default:()=>{let{textAreaScrollContainerWidth:t}=this,n={width:this.autosize&&t&&`${t}px`};return G(re,null,G(`textarea`,Object.assign({},this.inputProps,{ref:`textareaElRef`,class:[`${e}-input__textarea-el`,this.inputProps?.class],autofocus:this.autofocus,rows:Number(this.rows),placeholder:this.placeholder,value:this.mergedValue,disabled:this.mergedDisabled,maxlength:i?void 0:this.maxlength,minlength:i?void 0:this.minlength,readonly:this.readonly,tabindex:this.passivelyActivated&&!this.activated?-1:void 0,style:[this.textDecorationStyle[0],this.inputProps?.style,n],onBlur:this.handleInputBlur,onFocus:e=>{this.handleInputFocus(e,2)},onInput:this.handleInput,onChange:this.handleChange,onScroll:this.handleTextAreaScroll})),this.showPlaceholder1?G(`div`,{class:`${e}-input__placeholder`,style:[this.placeholderStyle,n],key:`placeholder`},this.mergedPlaceholder[0]):null,this.autosize?G(ae,{onResize:this.handleTextAreaMirrorResize},{default:()=>G(`div`,{ref:`textareaMirrorElRef`,class:`${e}-input__textarea-mirror`,key:`mirror`})}):null)}}):G(`div`,{class:`${e}-input__input`},G(`input`,Object.assign({type:r===`password`&&this.mergedShowPasswordOn&&this.passwordVisible?`text`:r},this.inputProps,{ref:`inputElRef`,class:[`${e}-input__input-el`,this.inputProps?.class],style:[this.textDecorationStyle[0],this.inputProps?.style],tabindex:this.passivelyActivated&&!this.activated?-1:this.inputProps?.tabindex,placeholder:this.mergedPlaceholder[0],disabled:this.mergedDisabled,maxlength:i?void 0:this.maxlength,minlength:i?void 0:this.minlength,value:Array.isArray(this.mergedValue)?this.mergedValue[0]:this.mergedValue,readonly:this.readonly,autofocus:this.autofocus,size:this.attrSize,onBlur:this.handleInputBlur,onFocus:e=>{this.handleInputFocus(e,0)},onInput:e=>{this.handleInput(e,0)},onChange:e=>{this.handleChange(e,0)}})),this.showPlaceholder1?G(`div`,{class:`${e}-input__placeholder`},G(`span`,null,this.mergedPlaceholder[0])):null,this.autosize?G(`div`,{class:`${e}-input__input-mirror`,key:`mirror`,ref:`inputMirrorElRef`},`\xA0`):null),!this.pair&&u(s.suffix,t=>t||this.clearable||this.showCount||this.mergedShowPasswordOn||this.loading!==void 0?G(`div`,{class:`${e}-input__suffix`},[u(s[`clear-icon-placeholder`],t=>(this.clearable||t)&&G(Ze,{clsPrefix:e,show:this.showClearButton,onClear:this.handleClear},{placeholder:()=>t,icon:()=>{var e;return(e=this.$slots)[`clear-icon`]?.call(e)}})),this.internalLoadingBeforeSuffix?null:t,this.loading===void 0?null:G(it,{clsPrefix:e,loading:this.loading,showArrow:!1,showClear:!1,style:this.cssVars}),this.internalLoadingBeforeSuffix?t:null,this.showCount&&this.type!==`textarea`?G(pt,null,{default:e=>{let{renderCount:t}=this;return t?t(e):s.count?.call(s,e)}}):null,this.mergedShowPasswordOn&&this.type===`password`?G(`div`,{class:`${e}-input__eye`,onMousedown:this.handlePasswordToggleMousedown,onClick:this.handlePasswordToggleClick},this.passwordVisible?D(s[`password-visible-icon`],()=>[G(o,{clsPrefix:e},{default:()=>G(Je,null)})]):D(s[`password-invisible-icon`],()=>[G(o,{clsPrefix:e},{default:()=>G(Ye,null)})])):null]):null)),this.pair?G(`span`,{class:`${e}-input__separator`},D(s.separator,()=>[this.separator])):null,this.pair?G(`div`,{class:`${e}-input-wrapper`},G(`div`,{class:`${e}-input__input`},G(`input`,{ref:`inputEl2Ref`,type:this.type,class:`${e}-input__input-el`,tabindex:this.passivelyActivated&&!this.activated?-1:void 0,placeholder:this.mergedPlaceholder[1],disabled:this.mergedDisabled,maxlength:i?void 0:this.maxlength,minlength:i?void 0:this.minlength,value:Array.isArray(this.mergedValue)?this.mergedValue[1]:void 0,readonly:this.readonly,style:this.textDecorationStyle[1],onBlur:this.handleInputBlur,onFocus:e=>{this.handleInputFocus(e,1)},onInput:e=>{this.handleInput(e,1)},onChange:e=>{this.handleChange(e,1)}}),this.showPlaceholder2?G(`div`,{class:`${e}-input__placeholder`},G(`span`,null,this.mergedPlaceholder[1])):null),u(s.suffix,t=>(this.clearable||t)&&G(`div`,{class:`${e}-input__suffix`},[this.clearable&&G(Ze,{clsPrefix:e,show:this.showClearButton,onClear:this.handleClear},{icon:()=>s[`clear-icon`]?.call(s),placeholder:()=>s[`clear-icon-placeholder`]?.call(s)}),t]))):null,this.mergedBordered?G(`div`,{class:`${e}-input__border`}):null,this.mergedBordered?G(`div`,{class:`${e}-input__state-border`}):null,this.showCount&&r===`textarea`?G(pt,null,{default:e=>{let{renderCount:t}=this;return t?t(e):s.count?.call(s,e)}}):null)}});function gt(e){return e.type===`group`}function _t(e){return e.type===`ignored`}function vt(e,t){try{return!!(1+t.toString().toLowerCase().indexOf(e.trim().toLowerCase()))}catch{return!1}}function yt(e,t){return{getIsGroup:gt,getIgnored:_t,getKey(t){return gt(t)?t.name||t.key||`key-required`:t[e]},getChildren(e){return e[t]}}}function bt(e,t,n,r){if(!t)return e;function i(e){if(!Array.isArray(e))return[];let a=[];for(let o of e)if(gt(o)){let e=i(o[r]);e.length&&a.push(Object.assign({},o,{[r]:e}))}else if(_t(o))continue;else t(n,o)&&a.push(o);return a}return i(e)}function xt(e,t,n){let r=new Map;return e.forEach(e=>{gt(e)?e[n].forEach(e=>{r.set(e[t],e)}):r.set(e[t],e)}),r}var St=f([O(`select`,`
 z-index: auto;
 outline: none;
 width: 100%;
 position: relative;
 font-weight: var(--n-font-weight);
 `),O(`select-menu`,`
 margin: 4px 0;
 box-shadow: var(--n-menu-box-shadow);
 `,[ye({originalTransition:`background-color .3s var(--n-bezier), box-shadow .3s var(--n-bezier)`})])]),Ct=Object.assign(Object.assign({},V.props),{to:J.propTo,bordered:{type:Boolean,default:void 0},clearable:Boolean,clearCreatedOptionsOnClear:{type:Boolean,default:!0},clearFilterAfterSelect:{type:Boolean,default:!0},options:{type:Array,default:()=>[]},defaultValue:{type:[String,Number,Array],default:null},keyboard:{type:Boolean,default:!0},value:[String,Number,Array],placeholder:String,menuProps:Object,multiple:Boolean,size:String,menuSize:{type:String},filterable:Boolean,disabled:{type:Boolean,default:void 0},remote:Boolean,loading:Boolean,filter:Function,placement:{type:String,default:`bottom-start`},widthMode:{type:String,default:`trigger`},tag:Boolean,onCreate:Function,fallbackOption:{type:[Function,Boolean],default:void 0},show:{type:Boolean,default:void 0},showArrow:{type:Boolean,default:!0},maxTagCount:[Number,String],ellipsisTagPopoverProps:Object,consistentMenuWidth:{type:Boolean,default:!0},virtualScroll:{type:Boolean,default:!0},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},childrenField:{type:String,default:`children`},renderLabel:Function,renderOption:Function,renderTag:Function,"onUpdate:value":[Function,Array],inputProps:Object,nodeProps:Function,ignoreComposition:{type:Boolean,default:!0},showOnFocus:Boolean,onUpdateValue:[Function,Array],onBlur:[Function,Array],onClear:[Function,Array],onFocus:[Function,Array],onScroll:[Function,Array],onSearch:[Function,Array],onUpdateShow:[Function,Array],"onUpdate:show":[Function,Array],displayDirective:{type:String,default:`show`},resetMenuOnOptionsChange:{type:Boolean,default:!0},status:String,showCheckmark:{type:Boolean,default:!0},scrollbarProps:Object,onChange:[Function,Array],items:Array}),wt=R({name:`Select`,props:Ct,slots:Object,setup(e){let{mergedClsPrefixRef:t,mergedBorderedRef:n,namespaceRef:r,inlineThemeDisabled:i,mergedComponentPropsRef:o}=g(e),s=V(`Select`,`-select`,St,Te,e,t),c=m(e.defaultValue),l=Q(e,`value`),u=a(l,c),d=m(!1),f=m(``),h=de(e,[`items`,`options`]),_=m([]),v=m([]),y=N(()=>v.value.concat(_.value).concat(h.value)),b=N(()=>{let{filter:t}=e;if(t)return t;let{labelField:n,valueField:r}=e;return(e,t)=>{if(!t)return!1;let i=t[n];if(typeof i==`string`)return vt(e,i);let a=t[r];return typeof a==`string`?vt(e,a):typeof a==`number`&&vt(e,String(a))}}),x=N(()=>{if(e.remote)return h.value;{let{value:t}=y,{value:n}=f;return!n.length||!e.filterable?t:bt(t,b.value,n,e.childrenField)}}),S=N(()=>{let{valueField:t,childrenField:n}=e,r=yt(t,n);return we(x.value,r)}),w=N(()=>xt(y.value,e.valueField,e.childrenField)),T=m(!1),E=a(Q(e,`show`),T),D=m(null),O=m(null),k=m(null),{localeRef:A}=ge(`Select`),ee=N(()=>e.placeholder??A.value.placeholder),M=[],P=m(new Map),F=N(()=>{let{fallbackOption:t}=e;if(t===void 0){let{labelField:t,valueField:n}=e;return e=>({[t]:String(e),[n]:e})}return t===!1?!1:e=>Object.assign(t(e),{value:e})});function I(t){let n=e.remote,{value:r}=P,{value:i}=w,{value:a}=F,o=[];return t.forEach(e=>{if(i.has(e))o.push(i.get(e));else if(n&&r.has(e))o.push(r.get(e));else if(a){let t=a(e);t&&o.push(t)}}),o}let L=N(()=>{if(e.multiple){let{value:e}=u;return Array.isArray(e)?I(e):[]}return null}),te=N(()=>{let{value:t}=u;return!e.multiple&&!Array.isArray(t)?t===null?null:I([t])[0]||null:null}),R=_e(e,{mergedSize:t=>{let{size:n}=e;if(n)return n;let{mergedSize:r}=t||{};return r?.value?r.value:o?.value?.Select?.size||`medium`}}),{mergedSizeRef:z,mergedDisabledRef:B,mergedStatusRef:U}=R;function W(t,n){let{onChange:r,"onUpdate:value":i,onUpdateValue:a}=e,{nTriggerFormChange:o,nTriggerFormInput:s}=R;r&&j(r,t,n),a&&j(a,t,n),i&&j(i,t,n),c.value=t,o(),s()}function G(t){let{onBlur:n}=e,{nTriggerFormBlur:r}=R;n&&j(n,t),r()}function K(){let{onClear:t}=e;t&&j(t)}function ne(t){let{onFocus:n,showOnFocus:r}=e,{nTriggerFormFocus:i}=R;n&&j(n,t),i(),r&&X()}function q(t){let{onSearch:n}=e;n&&j(n,t)}function Y(t){let{onScroll:n}=e;n&&j(n,t)}function re(){var t;let{remote:n,multiple:r}=e;if(n){let{value:n}=P;if(r){let{valueField:r}=e;(t=L.value)==null||t.forEach(e=>{n.set(e[r],e)})}else{let t=te.value;t&&n.set(t[e.valueField],t)}}}function ie(t){let{onUpdateShow:n,"onUpdate:show":r}=e;n&&j(n,t),r&&j(r,t),T.value=t}function X(){B.value||(ie(!0),T.value=!0,e.filterable&&Me())}function Z(){ie(!1)}function ae(){f.value=``,v.value=M}let oe=m(!1);function se(){e.filterable&&(oe.value=!0)}function ce(){e.filterable&&(oe.value=!1,E.value||ae())}function le(){B.value||(E.value?e.filterable?Me():Z():X())}function ue(e){(k.value?.selfRef)?.contains(e.relatedTarget)||(d.value=!1,G(e),Z())}function fe(e){ne(e),d.value=!0}function me(){d.value=!0}function he(e){D.value?.$el.contains(e.relatedTarget)||(d.value=!1,G(e),Z())}function ve(){var e;(e=D.value)==null||e.focus(),Z()}function ye(e){E.value&&(D.value?.$el.contains(pe(e))||Z())}function be(t){if(!Array.isArray(t))return[];if(F.value)return Array.from(t);{let{remote:n}=e,{value:r}=w;if(n){let{value:e}=P;return t.filter(t=>r.has(t)||e.has(t))}return t.filter(e=>r.has(e))}}function xe(e){$(e.rawNode)}function $(t){if(B.value)return;let{tag:n,remote:r,clearFilterAfterSelect:i,valueField:a}=e;if(n&&!r){let{value:e}=v,t=e[0]||null;if(t){let e=_.value;e.length?e.push(t):_.value=[t],v.value=M}}if(r&&P.value.set(t[a],t),e.multiple){let e=be(u.value),o=e.findIndex(e=>e===t[a]);if(~o){if(e.splice(o,1),n&&!r){let e=Ce(t[a]);~e&&(_.value.splice(e,1),i&&(f.value=``))}}else e.push(t[a]),i&&(f.value=``);W(e,I(e))}else{if(n&&!r){let e=Ce(t[a]);~e?_.value=[_.value[e]]:_.value=M}je(),Z(),W(t[a],t)}}function Ce(t){return _.value.findIndex(n=>n[e.valueField]===t)}function Ee(t){E.value||X();let{value:n}=t.target;f.value=n;let{tag:r,remote:i}=e;if(q(n),r&&!i){if(!n){v.value=M;return}let{onCreate:t}=e,r=t?t(n):{[e.labelField]:n,[e.valueField]:n},{valueField:i,labelField:a}=e;h.value.some(e=>e[i]===r[i]||e[a]===r[a])||_.value.some(e=>e[i]===r[i]||e[a]===r[a])?v.value=M:v.value=[r]}}function De(t){t.stopPropagation();let{multiple:n,tag:r,remote:i,clearCreatedOptionsOnClear:a}=e;!n&&e.filterable&&Z(),r&&!i&&a&&(_.value=M),K(),n?W([],[]):W(null,null)}function Oe(e){!Se(e,`action`)&&!Se(e,`empty`)&&!Se(e,`header`)&&e.preventDefault()}function ke(e){Y(e)}function Ae(t){var n,r,i;if(!e.keyboard){t.preventDefault();return}switch(t.key){case` `:if(e.filterable)break;t.preventDefault();case`Enter`:if(!D.value?.isComposing){if(E.value){let t=k.value?.getPendingTmNode();t?xe(t):e.filterable||(Z(),je())}else if(X(),e.tag&&oe.value){let t=v.value[0];if(t){let n=t[e.valueField],{value:r}=u;e.multiple&&Array.isArray(r)&&r.includes(n)||$(t)}}}t.preventDefault();break;case`ArrowUp`:if(t.preventDefault(),e.loading)return;E.value&&((n=k.value)==null||n.prev());break;case`ArrowDown`:if(t.preventDefault(),e.loading)return;E.value?(r=k.value)==null||r.next():X();break;case`Escape`:E.value&&(Ve(t),Z()),(i=D.value)==null||i.focus()}}function je(){var e;(e=D.value)==null||e.focus()}function Me(){var e;(e=D.value)==null||e.focusInput()}function Ne(){var e;E.value&&((e=O.value)==null||e.syncPosition())}re(),H(Q(e,`options`),re);let Pe={focus:()=>{var e;(e=D.value)==null||e.focus()},focusInput:()=>{var e;(e=D.value)==null||e.focusInput()},blur:()=>{var e;(e=D.value)==null||e.blur()},blurInput:()=>{var e;(e=D.value)==null||e.blurInput()}},Fe=N(()=>{let{self:{menuBoxShadow:e}}=s.value;return{"--n-menu-box-shadow":e}}),Ie=i?p(`select`,void 0,Fe,e):void 0;return Object.assign(Object.assign({},Pe),{mergedStatus:U,mergedClsPrefix:t,mergedBordered:n,namespace:r,treeMate:S,isMounted:C(),triggerRef:D,menuRef:k,pattern:f,uncontrolledShow:T,mergedShow:E,adjustedTo:J(e),uncontrolledValue:c,mergedValue:u,followerRef:O,localizedPlaceholder:ee,selectedOption:te,selectedOptions:L,mergedSize:z,mergedDisabled:B,focused:d,activeWithoutMenuOpen:oe,inlineThemeDisabled:i,onTriggerInputFocus:se,onTriggerInputBlur:ce,handleTriggerOrMenuResize:Ne,handleMenuFocus:me,handleMenuBlur:he,handleMenuTabOut:ve,handleTriggerClick:le,handleToggle:xe,handleDeleteOption:$,handlePatternInput:Ee,handleClear:De,handleTriggerBlur:ue,handleTriggerFocus:fe,handleKeydown:Ae,handleMenuAfterLeave:ae,handleMenuClickOutside:ye,handleMenuScroll:ke,handleMenuKeydown:Ae,handleMenuMousedown:Oe,mergedTheme:s,cssVars:i?void 0:Fe,themeClass:Ie?.themeClass,onRender:Ie?.onRender})},render(){return G(`div`,{class:`${this.mergedClsPrefix}-select`},G(te,null,{default:()=>[G(oe,null,{default:()=>G(ot,{ref:`triggerRef`,inlineThemeDisabled:this.inlineThemeDisabled,status:this.mergedStatus,inputProps:this.inputProps,clsPrefix:this.mergedClsPrefix,showArrow:this.showArrow,maxTagCount:this.maxTagCount,ellipsisTagPopoverProps:this.ellipsisTagPopoverProps,bordered:this.mergedBordered,active:this.activeWithoutMenuOpen||this.mergedShow,pattern:this.pattern,placeholder:this.localizedPlaceholder,selectedOption:this.selectedOption,selectedOptions:this.selectedOptions,multiple:this.multiple,renderTag:this.renderTag,renderLabel:this.renderLabel,filterable:this.filterable,clearable:this.clearable,disabled:this.mergedDisabled,size:this.mergedSize,theme:this.mergedTheme.peers.InternalSelection,labelField:this.labelField,valueField:this.valueField,themeOverrides:this.mergedTheme.peerOverrides.InternalSelection,loading:this.loading,focused:this.focused,onClick:this.handleTriggerClick,onDeleteOption:this.handleDeleteOption,onPatternInput:this.handlePatternInput,onClear:this.handleClear,onBlur:this.handleTriggerBlur,onFocus:this.handleTriggerFocus,onKeydown:this.handleKeydown,onPatternBlur:this.onTriggerInputBlur,onPatternFocus:this.onTriggerInputFocus,onResize:this.handleTriggerOrMenuResize,ignoreComposition:this.ignoreComposition},{arrow:()=>{var e;return[(e=this.$slots).arrow?.call(e)]}})}),G(ie,{ref:`followerRef`,show:this.mergedShow,to:this.adjustedTo,teleportDisabled:this.adjustedTo===J.tdkey,containerClass:this.namespace,width:this.consistentMenuWidth?`target`:void 0,minWidth:`target`,placement:this.placement},{default:()=>G(ee,{name:`fade-in-scale-up-transition`,appear:this.isMounted,onAfterLeave:this.handleMenuAfterLeave},{default:()=>{var t;return this.mergedShow||this.displayDirective===`show`?((t=this.onRender)==null||t.call(this),y(G(rt,Object.assign({},this.menuProps,{ref:`menuRef`,onResize:this.handleTriggerOrMenuResize,inlineThemeDisabled:this.inlineThemeDisabled,virtualScroll:this.consistentMenuWidth&&this.virtualScroll,class:[`${this.mergedClsPrefix}-select-menu`,this.themeClass,this.menuProps?.class],clsPrefix:this.mergedClsPrefix,focusable:!0,labelField:this.labelField,valueField:this.valueField,autoPending:!0,nodeProps:this.nodeProps,theme:this.mergedTheme.peers.InternalSelectMenu,themeOverrides:this.mergedTheme.peerOverrides.InternalSelectMenu,treeMate:this.treeMate,multiple:this.multiple,size:this.menuSize,renderOption:this.renderOption,renderLabel:this.renderLabel,value:this.mergedValue,style:[this.menuProps?.style,this.cssVars],onToggle:this.handleToggle,onScroll:this.handleMenuScroll,onFocus:this.handleMenuFocus,onBlur:this.handleMenuBlur,onKeydown:this.handleMenuKeydown,onTabOut:this.handleMenuTabOut,onMousedown:this.handleMenuMousedown,show:this.mergedShow,showCheckmark:this.showCheckmark,resetMenuOnOptionsChange:this.resetMenuOnOptionsChange,scrollbarProps:this.scrollbarProps}),{empty:()=>{var e;return[(e=this.$slots).empty?.call(e)]},header:()=>{var e;return[(e=this.$slots).header?.call(e)]},action:()=>{var e;return[(e=this.$slots).action?.call(e)]}}),this.displayDirective===`show`?[[e,this.mergedShow],[U,this.handleMenuClickOutside,void 0,{capture:!0}]]:[[U,this.handleMenuClickOutside,void 0,{capture:!0}]])):null}})})]}))}});export{Ke as a,Re as c,rt as i,yt as n,We as o,ht as r,He as s,wt as t};
import{$ as e,A as t,Bt as n,D as r,Dn as i,En as a,F as o,Ft as s,Ht as c,In as l,It as u,Jt as d,Lt as f,Mt as p,Nn as m,P as h,Pt as g,Q as _,R as v,Sn as y,St as b,T as x,U as S,Ut as C,V as w,Vt as T,Wt as E,Xt as D,_n as O,bt as k,ct as A,dn as j,en as M,et as N,f as P,fn as F,gt as I,hn as ee,ht as te,it as L,kn as R,ln as z,mn as ne,nn as B,nt as V,ot as re,pn as H,q as U,rt as W,s as G,st as ie,ut as K,v as q,vn as ae,vt as oe,yn as J,yt as se,zt as Y}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{A as ce,j as le,k as X}from"./api-Bfr7BT7g.js";import{n as Z}from"./Input-DRobws3t.js";import{C as ue,D as de,E as fe,L as pe,N as Q,R as $,S as me,T as he,m as ge,w as _e}from"./index-Li7ENe2r.js";function ve(e){return e&-e}var ye=class{constructor(e,t){this.l=e,this.min=t;let n=Array(e+1);for(let t=0;t<e+1;++t)n[t]=0;this.ft=n}add(e,t){if(t===0)return;let{l:n,ft:r}=this;for(e+=1;e<=n;)r[e]+=t,e+=ve(e)}get(e){return this.sum(e+1)-this.sum(e)}sum(e){if(e===void 0&&(e=this.l),e<=0)return 0;let{ft:t,min:n,l:r}=this;if(e>r)throw Error("[FinweckTree.sum]: `i` is larger than length.");let i=e*n;for(;e>0;)i+=t[e],e-=ve(e);return i}getBound(e){let t=0,n=this.l;for(;n>t;){let r=Math.floor((t+n)/2),i=this.sum(r);if(i>e){n=r;continue}if(i<e){if(t===r)return this.sum(t+1)<=e?t+1:r;t=r}else return r}return t}},be;function xe(){return typeof document>`u`?!1:(be===void 0&&(be=`matchMedia`in window&&window.matchMedia(`(pointer:coarse)`).matches),be)}var Se;function Ce(){return typeof document>`u`?1:(Se===void 0&&(Se=`chrome`in window?window.devicePixelRatio:1),Se)}var we=`VVirtualListXScroll`;function Te({columnsRef:e,renderColRef:t,renderItemWithColsRef:n}){let r=m(0),i=m(0),a=B(()=>{let t=e.value;if(t.length===0)return null;let n=new ye(t.length,0);return t.forEach((e,t)=>{n.add(t,e.width)}),n}),o=b(()=>{let e=a.value;return e===null?0:Math.max(e.getBound(i.value)-1,0)}),s=e=>{let t=a.value;return t===null?0:t.sum(e)},c=b(()=>{let t=a.value;return t===null?0:Math.min(t.getBound(i.value+r.value)+1,e.value.length-1)});return y(we,{startIndexRef:o,endIndexRef:c,columnsRef:e,renderColRef:t,renderItemWithColsRef:n,getLeft:s}),{listWidthRef:r,scrollLeftRef:i}}var Ee=z({name:`VirtualListRow`,props:{index:{type:Number,required:!0},item:{type:Object,required:!0}},setup(){let{startIndexRef:e,endIndexRef:t,columnsRef:n,getLeft:r,renderColRef:i,renderItemWithColsRef:a}=F(we);return{startIndex:e,endIndex:t,columns:n,renderCol:i,renderItemWithCols:a,getLeft:r}},render(){let{startIndex:e,endIndex:t,columns:n,renderCol:r,renderItemWithCols:i,getLeft:a,item:o}=this;if(i!=null)return i({itemIndex:this.index,startColIndex:e,endColIndex:t,allColumns:n,item:o,getLeft:a});if(r!=null){let i=[];for(let s=e;s<=t;++s){let e=n[s];i.push(r({column:e,left:a(s),item:o}))}return i}return null}}),De=V(`.v-vl`,{maxHeight:`inherit`,height:`100%`,overflow:`auto`,minWidth:`1px`},[V(`&:not(.v-vl--show-scrollbar)`,{scrollbarWidth:`none`},[V(`&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb`,{width:0,height:0,display:`none`})])]),Oe=z({name:`VirtualList`,inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},columns:{type:Array,default:()=>[]},renderCol:Function,renderItemWithCols:Function,items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:`div`},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:`key`},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(e){let t=L();De.mount({id:`vueuc/virtual-list`,head:!0,anchorMetaName:W,ssr:t}),J(()=>{let{defaultScrollIndex:t,defaultScrollKey:n}=e;t==null?n!=null&&S({key:n}):S({index:t})});let n=!1,r=!1;ee(()=>{if(n=!1,!r){r=!0;return}S({top:v.value,left:o.value})}),ae(()=>{n=!0,r||=!0});let i=b(()=>{if(e.renderCol==null&&e.renderItemWithCols==null||e.columns.length===0)return;let t=0;return e.columns.forEach(e=>{t+=e.width}),t}),a=B(()=>{let t=new Map,{keyField:n}=e;return e.items.forEach((e,r)=>{t.set(e[n],r)}),t}),{scrollLeftRef:o,listWidthRef:c}=Te({columnsRef:l(e,`columns`),renderColRef:l(e,`renderCol`),renderItemWithColsRef:l(e,`renderItemWithCols`)}),u=m(null),d=m(void 0),h=new Map,g=B(()=>{let{items:t,itemSize:n,keyField:r}=e,i=new ye(t.length,n);return t.forEach((e,t)=>{let n=e[r],a=h.get(n);a!==void 0&&i.add(t,a)}),i}),_=m(0),v=m(0),y=b(()=>Math.max(g.value.getBound(v.value-p(e.paddingTop))-1,0)),x=B(()=>{let{value:t}=d;if(t===void 0)return[];let{items:n,itemSize:r}=e,i=y.value,a=Math.min(i+Math.ceil(t/r+1),n.length-1),o=[];for(let e=i;e<=a;++e)o.push(n[e]);return o}),S=(e,t)=>{if(typeof e==`number`){E(e,t,`auto`);return}let{left:n,top:r,index:i,key:o,position:s,behavior:c,debounce:l=!0}=e;if(n!==void 0||r!==void 0)E(n,r,c);else if(i!==void 0)T(i,c,l);else if(o!==void 0){let e=a.value.get(o);e!==void 0&&T(e,c,l)}else s===`bottom`?E(0,2**53-1,c):s===`top`&&E(0,0,c)},C,w=null;function T(t,n,r){let{value:i}=g,a=i.sum(t)+p(e.paddingTop);if(!r)u.value.scrollTo({left:0,top:a,behavior:n});else{C=t,w!==null&&window.clearTimeout(w),w=window.setTimeout(()=>{C=void 0,w=null},16);let{scrollTop:e,offsetHeight:r}=u.value;if(a>e){let o=i.get(t);a+o<=e+r||u.value.scrollTo({left:0,top:a+o-r,behavior:n})}else u.value.scrollTo({left:0,top:a,behavior:n})}}function E(e,t,n){u.value.scrollTo({left:e,top:t,behavior:n})}function D(t,r){if(n||e.ignoreItemResize||P(r.target))return;let{value:i}=g,o=a.value.get(t),s=i.get(o),c=r.borderBoxSize?.[0]?.blockSize??r.contentRect.height;if(c===s)return;c-e.itemSize===0?h.delete(t):h.set(t,c-e.itemSize);let l=c-s;if(l===0)return;i.add(o,l);let d=u.value;if(d!=null){if(C===void 0){let e=i.sum(o);d.scrollTop>e&&d.scrollBy(0,l)}else(o<C||o===C&&c+i.sum(o)>d.scrollTop+d.offsetHeight)&&d.scrollBy(0,l);N()}_.value++}let O=!xe(),k=!1;function A(t){var n;(n=e.onScroll)==null||n.call(e,t),(!O||!k)&&N()}function j(t){var n;if((n=e.onWheel)==null||n.call(e,t),O){let e=u.value;if(e!=null){if(t.deltaX===0&&(e.scrollTop===0&&t.deltaY<=0||e.scrollTop+e.offsetHeight>=e.scrollHeight&&t.deltaY>=0))return;t.preventDefault(),e.scrollTop+=t.deltaY/Ce(),e.scrollLeft+=t.deltaX/Ce(),N(),k=!0,f(()=>{k=!1})}}}function M(t){if(n||P(t.target))return;if(e.renderCol==null&&e.renderItemWithCols==null){if(t.contentRect.height===d.value)return}else if(t.contentRect.height===d.value&&t.contentRect.width===c.value)return;d.value=t.contentRect.height,c.value=t.contentRect.width;let{onResize:r}=e;r!==void 0&&r(t)}function N(){let{value:e}=u;e!=null&&(v.value=e.scrollTop,o.value=e.scrollLeft)}function P(e){let t=e;for(;t!==null;){if(t.style.display===`none`)return!0;t=t.parentElement}return!1}return{listHeight:d,listStyle:{overflow:`auto`},keyToIndex:a,itemsStyle:B(()=>{let{itemResizable:t}=e,n=s(g.value.sum());return _.value,[e.itemsStyle,{boxSizing:`content-box`,width:s(i.value),height:t?``:n,minHeight:t?n:``,paddingTop:s(e.paddingTop),paddingBottom:s(e.paddingBottom)}]}),visibleItemsStyle:B(()=>(_.value,{transform:`translateY(${s(g.value.sum(y.value))})`})),viewportItems:x,listElRef:u,itemsElRef:m(null),scrollTo:S,handleListResize:M,handleListScroll:A,handleListWheel:j,handleItemResize:D}},render(){let{itemResizable:e,keyField:t,keyToIndex:n,visibleItemsTag:r}=this;return j(_,{onResize:this.handleListResize},{default:()=>{var i;return j(`div`,H(this.$attrs,{class:[`v-vl`,this.showScrollbar&&`v-vl--show-scrollbar`],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:`listElRef`}),[this.items.length===0?(i=this.$slots).empty?.call(i):j(`div`,{ref:`itemsElRef`,class:`v-vl-items`,style:this.itemsStyle},[j(r,Object.assign({class:`v-vl-visible-items`,style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>{let{renderCol:r,renderItemWithCols:i}=this;return this.viewportItems.map(a=>{let o=a[t],s=n.get(o),c=r==null?void 0:j(Ee,{index:s,item:a}),l=i==null?void 0:j(Ee,{index:s,item:a}),u=this.$slots.default({item:a,renderedCols:c,renderedItemWithCols:l,index:s})[0];return e?j(_,{key:o,onResize:e=>this.handleItemResize(o,e)},{default:()=>u}):(u.key=o,u)})}})])])}})}});function ke(t,n){n&&(J(()=>{let{value:r}=t;r&&e.registerHandler(r,n)}),a(t,(t,n)=>{n&&e.unregisterHandler(n)},{deep:!1}),O(()=>{let{value:n}=t;n&&e.unregisterHandler(n)}))}var Ae=new WeakSet;function je(e){Ae.add(e)}function Me(e){return!Ae.has(e)}function Ne(e){switch(typeof e){case`string`:return e||void 0;case`number`:return String(e);default:return}}function Pe(e){let t=e.filter(e=>e!==void 0);if(t.length!==0)return t.length===1?t[0]:t=>{e.forEach(e=>{e&&e(t)})}}var Fe=z({name:`Checkmark`,render(){return j(`svg`,{xmlns:`http://www.w3.org/2000/svg`,viewBox:`0 0 16 16`},j(`g`,{fill:`none`},j(`path`,{d:`M14.046 3.486a.75.75 0 0 1-.032 1.06l-7.93 7.474a.85.85 0 0 1-1.188-.022l-2.68-2.72a.75.75 0 1 1 1.068-1.053l2.234 2.267l7.468-7.038a.75.75 0 0 1 1.06.032z`,fill:`currentColor`})))}}),Ie=z({name:`Empty`,render(){return j(`svg`,{viewBox:`0 0 28 28`,fill:`none`,xmlns:`http://www.w3.org/2000/svg`},j(`path`,{d:`M26 7.5C26 11.0899 23.0899 14 19.5 14C15.9101 14 13 11.0899 13 7.5C13 3.91015 15.9101 1 19.5 1C23.0899 1 26 3.91015 26 7.5ZM16.8536 4.14645C16.6583 3.95118 16.3417 3.95118 16.1464 4.14645C15.9512 4.34171 15.9512 4.65829 16.1464 4.85355L18.7929 7.5L16.1464 10.1464C15.9512 10.3417 15.9512 10.6583 16.1464 10.8536C16.3417 11.0488 16.6583 11.0488 16.8536 10.8536L19.5 8.20711L22.1464 10.8536C22.3417 11.0488 22.6583 11.0488 22.8536 10.8536C23.0488 10.6583 23.0488 10.3417 22.8536 10.1464L20.2071 7.5L22.8536 4.85355C23.0488 4.65829 23.0488 4.34171 22.8536 4.14645C22.6583 3.95118 22.3417 3.95118 22.1464 4.14645L19.5 6.79289L16.8536 4.14645Z`,fill:`currentColor`}),j(`path`,{d:`M25 22.75V12.5991C24.5572 13.0765 24.053 13.4961 23.5 13.8454V16H17.5L17.3982 16.0068C17.0322 16.0565 16.75 16.3703 16.75 16.75C16.75 18.2688 15.5188 19.5 14 19.5C12.4812 19.5 11.25 18.2688 11.25 16.75L11.2432 16.6482C11.1935 16.2822 10.8797 16 10.5 16H4.5V7.25C4.5 6.2835 5.2835 5.5 6.25 5.5H12.2696C12.4146 4.97463 12.6153 4.47237 12.865 4H6.25C4.45507 4 3 5.45507 3 7.25V22.75C3 24.5449 4.45507 26 6.25 26H21.75C23.5449 26 25 24.5449 25 22.75ZM4.5 22.75V17.5H9.81597L9.85751 17.7041C10.2905 19.5919 11.9808 21 14 21L14.215 20.9947C16.2095 20.8953 17.842 19.4209 18.184 17.5H23.5V22.75C23.5 23.7165 22.7165 24.5 21.75 24.5H6.25C5.2835 24.5 4.5 23.7165 4.5 22.75Z`,fill:`currentColor`}))}}),Le=z({props:{onFocus:Function,onBlur:Function},setup(e){return()=>j(`div`,{style:`width: 0; height: 0`,tabindex:0,onFocus:e.onFocus,onBlur:e.onBlur})}}),Re=n(`empty`,`
 display: flex;
 flex-direction: column;
 align-items: center;
 font-size: var(--n-font-size);
`,[T(`icon`,`
 width: var(--n-icon-size);
 height: var(--n-icon-size);
 font-size: var(--n-icon-size);
 line-height: var(--n-icon-size);
 color: var(--n-icon-color);
 transition:
 color .3s var(--n-bezier);
 `,[Y(`+`,[T(`description`,`
 margin-top: 8px;
 `)])]),T(`description`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),T(`extra`,`
 text-align: center;
 transition: color .3s var(--n-bezier);
 margin-top: 12px;
 color: var(--n-extra-text-color);
 `)]),ze=Object.assign(Object.assign({},r.props),{description:String,showDescription:{type:Boolean,default:!0},showIcon:{type:Boolean,default:!0},size:{type:String,default:`medium`},renderIcon:Function}),Be=z({name:`Empty`,props:ze,slots:Object,setup(e){let{mergedClsPrefixRef:t,inlineThemeDisabled:n,mergedComponentPropsRef:i}=o(e),a=r(`Empty`,`-empty`,Re,he,e,t),{localeRef:s}=ce(`Empty`),c=B(()=>e.description??i?.value?.Empty?.description),l=B(()=>i?.value?.Empty?.renderIcon||(()=>j(Ie,null))),u=B(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{[E(`iconSize`,t)]:r,[E(`fontSize`,t)]:i,textColor:o,iconColor:s,extraTextColor:c}}=a.value;return{"--n-icon-size":r,"--n-font-size":i,"--n-bezier":n,"--n-text-color":o,"--n-icon-color":s,"--n-extra-text-color":c}}),d=n?h(`empty`,B(()=>{let t=``,{size:n}=e;return t+=n[0],t}),u,e):void 0;return{mergedClsPrefix:t,mergedRenderIcon:l,localizedDescription:B(()=>c.value||s.value.description),cssVars:n?void 0:u,themeClass:d?.themeClass,onRender:d?.onRender}},render(){let{$slots:e,mergedClsPrefix:t,onRender:n}=this;return n?.(),j(`div`,{class:[`${t}-empty`,this.themeClass],style:this.cssVars},this.showIcon?j(`div`,{class:`${t}-empty__icon`},e.icon?e.icon():j(x,{clsPrefix:t},{default:this.mergedRenderIcon})):null,this.showDescription?j(`div`,{class:`${t}-empty__description`},e.default?e.default():this.localizedDescription):null,e.extra?j(`div`,{class:`${t}-empty__extra`},e.extra()):null)}}),Ve=z({name:`NBaseSelectGroupHeader`,props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(){let{renderLabelRef:e,renderOptionRef:t,labelFieldRef:n,nodePropsRef:r}=F(I);return{labelField:n,nodeProps:r,renderLabel:e,renderOption:t}},render(){let{clsPrefix:e,renderLabel:t,renderOption:n,nodeProps:r,tmNode:{rawNode:i}}=this,a=r?.(i),o=t?t(i,!1):Q(i[this.labelField],i,!1),s=j(`div`,Object.assign({},a,{class:[`${e}-base-select-group-header`,a?.class]}),o);return i.render?i.render({node:s,option:i}):n?n({node:s,option:i,selected:!1}):s}});function He(e,t){return j(d,{name:`fade-in-scale-up-transition`},{default:()=>e?j(x,{clsPrefix:t,class:`${t}-base-select-option__check`},{default:()=>j(Fe)}):null})}var Ue=z({name:`NBaseSelectOption`,props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(e){let{valueRef:t,pendingTmNodeRef:n,multipleRef:r,valueSetRef:i,renderLabelRef:a,renderOptionRef:o,labelFieldRef:s,valueFieldRef:c,showCheckmarkRef:l,nodePropsRef:u,handleOptionClick:d,handleOptionMouseEnter:f}=F(I),p=b(()=>{let{value:t}=n;return t?e.tmNode.key===t.key:!1});function m(t){let{tmNode:n}=e;n.disabled||d(t,n)}function h(t){let{tmNode:n}=e;n.disabled||f(t,n)}function g(t){let{tmNode:n}=e,{value:r}=p;n.disabled||r||f(t,n)}return{multiple:r,isGrouped:b(()=>{let{tmNode:t}=e,{parent:n}=t;return n&&n.rawNode.type===`group`}),showCheckmark:l,nodeProps:u,isPending:p,isSelected:b(()=>{let{value:n}=t,{value:a}=r;if(n===null)return!1;let o=e.tmNode.rawNode[c.value];if(a){let{value:e}=i;return e.has(o)}return n===o}),labelField:s,renderLabel:a,renderOption:o,handleMouseMove:g,handleMouseEnter:h,handleClick:m}},render(){let{clsPrefix:e,tmNode:{rawNode:t},isSelected:n,isPending:r,isGrouped:i,showCheckmark:a,nodeProps:o,renderOption:s,renderLabel:c,handleClick:l,handleMouseEnter:u,handleMouseMove:d}=this,f=He(n,e),p=c?[c(t,n),a&&f]:[Q(t[this.labelField],t,n),a&&f],m=o?.(t),h=j(`div`,Object.assign({},m,{class:[`${e}-base-select-option`,t.class,m?.class,{[`${e}-base-select-option--disabled`]:t.disabled,[`${e}-base-select-option--selected`]:n,[`${e}-base-select-option--grouped`]:i,[`${e}-base-select-option--pending`]:r,[`${e}-base-select-option--show-checkmark`]:a}],style:[m?.style||``,t.style||``],onClick:Pe([l,m?.onClick]),onMouseenter:Pe([u,m?.onMouseenter]),onMousemove:Pe([d,m?.onMousemove])}),j(`div`,{class:`${e}-base-select-option__content`},p));return t.render?t.render({node:h,option:t,selected:n}):s?s({node:h,option:t,selected:n}):h}}),We=n(`base-select-menu`,`
 line-height: 1.5;
 outline: none;
 z-index: 0;
 position: relative;
 border-radius: var(--n-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-color);
`,[n(`scrollbar`,`
 max-height: var(--n-height);
 `),n(`virtual-list`,`
 max-height: var(--n-height);
 `),n(`base-select-option`,`
 min-height: var(--n-option-height);
 font-size: var(--n-option-font-size);
 display: flex;
 align-items: center;
 `,[T(`content`,`
 z-index: 1;
 white-space: nowrap;
 text-overflow: ellipsis;
 overflow: hidden;
 `)]),n(`base-select-group-header`,`
 min-height: var(--n-option-height);
 font-size: .93em;
 display: flex;
 align-items: center;
 `),n(`base-select-menu-option-wrapper`,`
 position: relative;
 width: 100%;
 `),T(`loading, empty`,`
 display: flex;
 padding: 12px 32px;
 flex: 1;
 justify-content: center;
 `),T(`loading`,`
 color: var(--n-loading-color);
 font-size: var(--n-loading-size);
 `),T(`header`,`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),T(`action`,`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-top: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),n(`base-select-group-header`,`
 position: relative;
 cursor: default;
 padding: var(--n-option-padding);
 color: var(--n-group-header-text-color);
 `),n(`base-select-option`,`
 cursor: pointer;
 position: relative;
 padding: var(--n-option-padding);
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 box-sizing: border-box;
 color: var(--n-option-text-color);
 opacity: 1;
 `,[c(`show-checkmark`,`
 padding-right: calc(var(--n-option-padding-right) + 20px);
 `),Y(`&::before`,`
 content: "";
 position: absolute;
 left: 4px;
 right: 4px;
 top: 0;
 bottom: 0;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),Y(`&:active`,`
 color: var(--n-option-text-color-pressed);
 `),c(`grouped`,`
 padding-left: calc(var(--n-option-padding-left) * 1.5);
 `),c(`pending`,[Y(`&::before`,`
 background-color: var(--n-option-color-pending);
 `)]),c(`selected`,`
 color: var(--n-option-text-color-active);
 `,[Y(`&::before`,`
 background-color: var(--n-option-color-active);
 `),c(`pending`,[Y(`&::before`,`
 background-color: var(--n-option-color-active-pending);
 `)])]),c(`disabled`,`
 cursor: not-allowed;
 `,[C(`selected`,`
 color: var(--n-option-text-color-disabled);
 `),c(`selected`,`
 opacity: var(--n-option-opacity-disabled);
 `)]),T(`check`,`
 font-size: 16px;
 position: absolute;
 right: calc(var(--n-option-padding-right) - 4px);
 top: calc(50% - 7px);
 color: var(--n-option-check-color);
 transition: color .3s var(--n-bezier);
 `,[ue({enterScale:`0.5`})])])]),Ge=z({name:`InternalSelectMenu`,props:Object.assign(Object.assign({},r.props),{clsPrefix:{type:String,required:!0},scrollable:{type:Boolean,default:!0},treeMate:{type:Object,required:!0},multiple:Boolean,size:{type:String,default:`medium`},value:{type:[String,Number,Array],default:null},autoPending:Boolean,virtualScroll:{type:Boolean,default:!0},show:{type:Boolean,default:!0},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},loading:Boolean,focusable:Boolean,renderLabel:Function,renderOption:Function,nodeProps:Function,showCheckmark:{type:Boolean,default:!0},onMousedown:Function,onScroll:Function,onFocus:Function,onBlur:Function,onKeyup:Function,onKeydown:Function,onTabOut:Function,onMouseenter:Function,onMouseleave:Function,onResize:Function,resetMenuOnOptionsChange:{type:Boolean,default:!0},inlineThemeDisabled:Boolean,scrollbarProps:Object,onToggle:Function}),setup(e){let{mergedClsPrefixRef:n,mergedRtlRef:i,mergedComponentPropsRef:s}=o(e),c=t(`InternalSelectMenu`,i,n),u=r(`InternalSelectMenu`,`-internal-select-menu`,We,_e,e,l(e,`clsPrefix`)),d=m(null),f=m(null),_=m(null),v=B(()=>e.treeMate.getFlattenedNodes()),b=B(()=>de(v.value)),x=m(null);function S(){let{treeMate:t}=e,n=null,{value:r}=e;r===null?n=t.getFirstAvailableNode():(n=e.multiple?t.getNode((r||[])[(r||[]).length-1]):t.getNode(r),(!n||n.disabled)&&(n=t.getFirstAvailableNode())),W(n||null)}function C(){let{value:t}=x;t&&!e.treeMate.getNode(t.key)&&(x.value=null)}let w;a(()=>e.show,t=>{t?w=a(()=>e.treeMate,()=>{e.resetMenuOnOptionsChange?(e.autoPending?S():C(),ne(G)):C()},{immediate:!0}):w?.()},{immediate:!0}),O(()=>{w?.()});let T=B(()=>p(u.value.self[E(`optionHeight`,e.size)])),D=B(()=>g(u.value.self[E(`padding`,e.size)])),k=B(()=>e.multiple&&Array.isArray(e.value)?new Set(e.value):new Set),A=B(()=>{let e=v.value;return e&&e.length===0}),j=B(()=>s?.value?.Select?.renderEmpty);function M(t){let{onToggle:n}=e;n&&n(t)}function N(t){let{onScroll:n}=e;n&&n(t)}function P(e){var t;(t=_.value)==null||t.sync(),N(e)}function F(){var e;(e=_.value)==null||e.sync()}function ee(){let{value:e}=x;return e||null}function L(e,t){t.disabled||W(t,!1)}function R(e,t){t.disabled||M(t)}function z(t){var n;$(t,`action`)||(n=e.onKeyup)==null||n.call(e,t)}function V(t){var n;$(t,`action`)||(n=e.onKeydown)==null||n.call(e,t)}function re(t){var n;(n=e.onMousedown)==null||n.call(e,t),!e.focusable&&t.preventDefault()}function H(){let{value:e}=x;e&&W(e.getNext({loop:!0}),!0)}function U(){let{value:e}=x;e&&W(e.getPrev({loop:!0}),!0)}function W(e,t=!1){x.value=e,t&&G()}function G(){var t,n;let r=x.value;if(!r)return;let i=b.value(r.key);i!==null&&(e.virtualScroll?(t=f.value)==null||t.scrollTo({index:i}):(n=_.value)==null||n.scrollTo({index:i,elSize:T.value}))}function ie(t){var n;d.value?.contains(t.target)&&((n=e.onFocus)==null||n.call(e,t))}function K(t){var n;d.value?.contains(t.relatedTarget)||(n=e.onBlur)==null||n.call(e,t)}y(I,{handleOptionMouseEnter:L,handleOptionClick:R,valueSetRef:k,pendingTmNodeRef:x,nodePropsRef:l(e,`nodeProps`),showCheckmarkRef:l(e,`showCheckmark`),multipleRef:l(e,`multiple`),valueRef:l(e,`value`),renderLabelRef:l(e,`renderLabel`),renderOptionRef:l(e,`renderOption`),labelFieldRef:l(e,`labelField`),valueFieldRef:l(e,`valueField`)}),y(te,d),J(()=>{let{value:e}=_;e&&e.sync()});let q=B(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{height:r,borderRadius:i,color:a,groupHeaderTextColor:o,actionDividerColor:s,optionTextColorPressed:c,optionTextColor:l,optionTextColorDisabled:d,optionTextColorActive:f,optionOpacityDisabled:p,optionCheckColor:m,actionTextColor:h,optionColorPending:_,optionColorActive:v,loadingColor:y,loadingSize:b,optionColorActivePending:x,[E(`optionFontSize`,t)]:S,[E(`optionHeight`,t)]:C,[E(`optionPadding`,t)]:w}}=u.value;return{"--n-height":r,"--n-action-divider-color":s,"--n-action-text-color":h,"--n-bezier":n,"--n-border-radius":i,"--n-color":a,"--n-option-font-size":S,"--n-group-header-text-color":o,"--n-option-check-color":m,"--n-option-color-pending":_,"--n-option-color-active":v,"--n-option-color-active-pending":x,"--n-option-height":C,"--n-option-opacity-disabled":p,"--n-option-text-color":l,"--n-option-text-color-active":f,"--n-option-text-color-disabled":d,"--n-option-text-color-pressed":c,"--n-option-padding":w,"--n-option-padding-left":g(w,`left`),"--n-option-padding-right":g(w,`right`),"--n-loading-color":y,"--n-loading-size":b}}),{inlineThemeDisabled:ae}=e,oe=ae?h(`internal-select-menu`,B(()=>e.size[0]),q,e):void 0,se={selfRef:d,next:H,prev:U,getPendingTmNode:ee};return ke(d,e.onResize),Object.assign({mergedTheme:u,mergedClsPrefix:n,rtlEnabled:c,virtualListRef:f,scrollbarRef:_,itemSize:T,padding:D,flattenedNodes:v,empty:A,mergedRenderEmpty:j,virtualListContainer(){let{value:e}=f;return e?.listElRef},virtualListContent(){let{value:e}=f;return e?.itemsElRef},doScroll:N,handleFocusin:ie,handleFocusout:K,handleKeyUp:z,handleKeyDown:V,handleMouseDown:re,handleVirtualListResize:F,handleVirtualListScroll:P,cssVars:ae?void 0:q,themeClass:oe?.themeClass,onRender:oe?.onRender},se)},render(){let{$slots:e,virtualScroll:t,clsPrefix:n,mergedTheme:r,themeClass:i,onRender:a}=this;return a?.(),j(`div`,{ref:`selfRef`,tabindex:this.focusable?0:-1,class:[`${n}-base-select-menu`,`${n}-base-select-menu--${this.size}-size`,this.rtlEnabled&&`${n}-base-select-menu--rtl`,i,this.multiple&&`${n}-base-select-menu--multiple`],style:this.cssVars,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onKeyup:this.handleKeyUp,onKeydown:this.handleKeyDown,onMousedown:this.handleMouseDown,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},S(e.header,e=>e&&j(`div`,{class:`${n}-base-select-menu__header`,"data-header":!0,key:`header`},e)),this.loading?j(`div`,{class:`${n}-base-select-menu__loading`},j(q,{clsPrefix:n,strokeWidth:20})):this.empty?j(`div`,{class:`${n}-base-select-menu__empty`,"data-empty":!0},w(e.empty,()=>[this.mergedRenderEmpty?.call(this)||j(Be,{theme:r.peers.Empty,themeOverrides:r.peerOverrides.Empty,size:this.size})])):j(P,Object.assign({ref:`scrollbarRef`,theme:r.peers.Scrollbar,themeOverrides:r.peerOverrides.Scrollbar,scrollable:this.scrollable,container:t?this.virtualListContainer:void 0,content:t?this.virtualListContent:void 0,onScroll:t?void 0:this.doScroll},this.scrollbarProps),{default:()=>t?j(Oe,{ref:`virtualListRef`,class:`${n}-virtual-list`,items:this.flattenedNodes,itemSize:this.itemSize,showScrollbar:!1,paddingTop:this.padding.top,paddingBottom:this.padding.bottom,onResize:this.handleVirtualListResize,onScroll:this.handleVirtualListScroll,itemResizable:!0},{default:({item:e})=>e.isGroup?j(Ve,{key:e.key,clsPrefix:n,tmNode:e}):e.ignored?null:j(Ue,{clsPrefix:n,key:e.key,tmNode:e})}):j(`div`,{class:`${n}-base-select-menu-option-wrapper`,style:{paddingTop:this.padding.top,paddingBottom:this.padding.bottom}},this.flattenedNodes.map(e=>e.isGroup?j(Ve,{key:e.key,clsPrefix:n,tmNode:e}):j(Ue,{clsPrefix:n,key:e.key,tmNode:e})))}),S(e.action,e=>e&&[j(`div`,{class:`${n}-base-select-menu__action`,"data-action":!0,key:`action`},e),j(Le,{onFocus:this.onTabOut,key:`focus-detector`})]))}}),Ke=Y([n(`base-selection`,`
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
 `,[n(`base-loading`,`
 color: var(--n-loading-color);
 `),n(`base-selection-tags`,`min-height: var(--n-height);`),T(`border, state-border`,`
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
 `),T(`state-border`,`
 z-index: 1;
 border-color: #0000;
 `),n(`base-suffix`,`
 cursor: pointer;
 position: absolute;
 top: 50%;
 transform: translateY(-50%);
 right: 10px;
 `,[T(`arrow`,`
 font-size: var(--n-arrow-size);
 color: var(--n-arrow-color);
 transition: color .3s var(--n-bezier);
 `)]),n(`base-selection-overlay`,`
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
 `,[T(`wrapper`,`
 flex-basis: 0;
 flex-grow: 1;
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),n(`base-selection-placeholder`,`
 color: var(--n-placeholder-color);
 `,[T(`inner`,`
 max-width: 100%;
 overflow: hidden;
 `)]),n(`base-selection-tags`,`
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
 `),n(`base-selection-label`,`
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
 `,[n(`base-selection-input`,`
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
 `,[T(`content`,`
 text-overflow: ellipsis;
 overflow: hidden;
 white-space: nowrap; 
 `)]),T(`render-label`,`
 color: var(--n-text-color);
 `)]),C(`disabled`,[Y(`&:hover`,[T(`state-border`,`
 box-shadow: var(--n-box-shadow-hover);
 border: var(--n-border-hover);
 `)]),c(`focus`,[T(`state-border`,`
 box-shadow: var(--n-box-shadow-focus);
 border: var(--n-border-focus);
 `)]),c(`active`,[T(`state-border`,`
 box-shadow: var(--n-box-shadow-active);
 border: var(--n-border-active);
 `),n(`base-selection-label`,`background-color: var(--n-color-active);`),n(`base-selection-tags`,`background-color: var(--n-color-active);`)])]),c(`disabled`,`cursor: not-allowed;`,[T(`arrow`,`
 color: var(--n-arrow-color-disabled);
 `),n(`base-selection-label`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[n(`base-selection-input`,`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 `),T(`render-label`,`
 color: var(--n-text-color-disabled);
 `)]),n(`base-selection-tags`,`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `),n(`base-selection-placeholder`,`
 cursor: not-allowed;
 color: var(--n-placeholder-color-disabled);
 `)]),n(`base-selection-input-tag`,`
 height: calc(var(--n-height) - 6px);
 line-height: calc(var(--n-height) - 6px);
 outline: none;
 display: none;
 position: relative;
 margin-bottom: 3px;
 max-width: 100%;
 vertical-align: bottom;
 `,[T(`input`,`
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
 `),T(`mirror`,`
 position: absolute;
 left: 0;
 top: 0;
 white-space: pre;
 visibility: hidden;
 user-select: none;
 -webkit-user-select: none;
 opacity: 0;
 `)]),[`warning`,`error`].map(e=>c(`${e}-status`,[T(`state-border`,`border: var(--n-border-${e});`),C(`disabled`,[Y(`&:hover`,[T(`state-border`,`
 box-shadow: var(--n-box-shadow-hover-${e});
 border: var(--n-border-hover-${e});
 `)]),c(`active`,[T(`state-border`,`
 box-shadow: var(--n-box-shadow-active-${e});
 border: var(--n-border-active-${e});
 `),n(`base-selection-label`,`background-color: var(--n-color-active-${e});`),n(`base-selection-tags`,`background-color: var(--n-color-active-${e});`)]),c(`focus`,[T(`state-border`,`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),n(`base-selection-popover`,`
 margin-bottom: -3px;
 display: flex;
 flex-wrap: wrap;
 margin-right: -8px;
 `),n(`base-selection-tag-wrapper`,`
 max-width: 100%;
 display: inline-flex;
 padding: 0 7px 3px 0;
 `,[Y(`&:last-child`,`padding-right: 0;`),n(`tag`,`
 font-size: 14px;
 max-width: 100%;
 `,[T(`content`,`
 line-height: 1.25;
 text-overflow: ellipsis;
 overflow: hidden;
 `)])])]),qe=z({name:`InternalSelection`,props:Object.assign(Object.assign({},r.props),{clsPrefix:{type:String,required:!0},bordered:{type:Boolean,default:void 0},active:Boolean,pattern:{type:String,default:``},placeholder:String,selectedOption:{type:Object,default:null},selectedOptions:{type:Array,default:null},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},multiple:Boolean,filterable:Boolean,clearable:Boolean,disabled:Boolean,size:{type:String,default:`medium`},loading:Boolean,autofocus:Boolean,showArrow:{type:Boolean,default:!0},inputProps:Object,focused:Boolean,renderTag:Function,onKeydown:Function,onClick:Function,onBlur:Function,onFocus:Function,onDeleteOption:Function,maxTagCount:[String,Number],ellipsisTagPopoverProps:Object,onClear:Function,onPatternInput:Function,onPatternFocus:Function,onPatternBlur:Function,renderLabel:Function,status:String,inlineThemeDisabled:Boolean,ignoreComposition:{type:Boolean,default:!0},onResize:Function}),setup(e){let{mergedClsPrefixRef:n,mergedRtlRef:s}=o(e),c=t(`InternalSelection`,s,n),u=m(null),d=m(null),f=m(null),p=m(null),_=m(null),v=m(null),y=m(null),b=m(null),x=m(null),S=m(null),C=m(!1),w=m(!1),T=m(!1),D=r(`InternalSelection`,`-internal-selection`,Ke,me,e,l(e,`clsPrefix`)),O=B(()=>e.clearable&&!e.disabled&&(T.value||e.active)),k=B(()=>e.selectedOption?e.renderTag?e.renderTag({option:e.selectedOption,handleClose:()=>{}}):e.renderLabel?e.renderLabel(e.selectedOption,!0):Q(e.selectedOption[e.labelField],e.selectedOption,!0):e.placeholder),A=B(()=>{let t=e.selectedOption;if(t)return t[e.labelField]}),j=B(()=>e.multiple?!!(Array.isArray(e.selectedOptions)&&e.selectedOptions.length):e.selectedOption!==null);function M(){var t;let{value:n}=u;if(n){let{value:r}=d;r&&(r.style.width=`${n.offsetWidth}px`,e.maxTagCount!==`responsive`&&((t=x.value)==null||t.sync({showAllItemsBeforeCalculate:!1})))}}function N(){let{value:e}=S;e&&(e.style.display=`none`)}function P(){let{value:e}=S;e&&(e.style.display=`inline-block`)}a(l(e,`active`),e=>{e||N()}),a(l(e,`pattern`),()=>{e.multiple&&ne(M)});function F(t){let{onFocus:n}=e;n&&n(t)}function I(t){let{onBlur:n}=e;n&&n(t)}function ee(t){let{onDeleteOption:n}=e;n&&n(t)}function te(t){let{onClear:n}=e;n&&n(t)}function L(t){let{onPatternInput:n}=e;n&&n(t)}function R(e){(!e.relatedTarget||!f.value?.contains(e.relatedTarget))&&F(e)}function z(e){f.value?.contains(e.relatedTarget)||I(e)}function V(e){te(e)}function re(){T.value=!0}function H(){T.value=!1}function U(t){!e.active||!e.filterable||t.target!==d.value&&t.preventDefault()}function W(e){ee(e)}let G=m(!1);function ie(t){if(t.key===`Backspace`&&!G.value&&!e.pattern.length){let{selectedOptions:t}=e;t?.length&&W(t[t.length-1])}}let K=null;function q(t){let{value:n}=u;n&&(n.textContent=t.target.value,M()),e.ignoreComposition&&G.value?K=t:L(t)}function ae(){G.value=!0}function oe(){G.value=!1,e.ignoreComposition&&L(K),K=null}function se(t){var n;w.value=!0,(n=e.onPatternFocus)==null||n.call(e,t)}function Y(t){var n;w.value=!1,(n=e.onPatternBlur)==null||n.call(e,t)}function ce(){var t,n;if(e.filterable)w.value=!1,(t=v.value)==null||t.blur(),(n=d.value)==null||n.blur();else if(e.multiple){let{value:e}=p;e?.blur()}else{let{value:e}=_;e?.blur()}}function le(){var t,n,r;e.filterable?(w.value=!1,(t=v.value)==null||t.focus()):e.multiple?(n=p.value)==null||n.focus():(r=_.value)==null||r.focus()}function X(){let{value:e}=d;e&&(P(),e.focus())}function Z(){let{value:e}=d;e&&e.blur()}function ue(e){let{value:t}=y;t&&t.setTextContent(`+${e}`)}function de(){let{value:e}=b;return e}function fe(){return d.value}let pe=null;function $(){pe!==null&&window.clearTimeout(pe)}function he(){e.active||($(),pe=window.setTimeout(()=>{j.value&&(C.value=!0)},100))}function ge(){$()}function _e(e){e||($(),C.value=!1)}a(j,e=>{e||(C.value=!1)}),J(()=>{i(()=>{let t=v.value;t&&(e.disabled?t.removeAttribute(`tabindex`):t.tabIndex=w.value?-1:0)})}),ke(f,e.onResize);let{inlineThemeDisabled:ve}=e,ye=B(()=>{let{size:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontWeight:r,borderRadius:i,color:a,placeholderColor:o,textColor:s,paddingSingle:c,paddingMultiple:l,caretColor:u,colorDisabled:d,textColorDisabled:f,placeholderColorDisabled:p,colorActive:m,boxShadowFocus:h,boxShadowActive:_,boxShadowHover:v,border:y,borderFocus:b,borderHover:x,borderActive:S,arrowColor:C,arrowColorDisabled:w,loadingColor:T,colorActiveWarning:O,boxShadowFocusWarning:k,boxShadowActiveWarning:A,boxShadowHoverWarning:j,borderWarning:M,borderFocusWarning:N,borderHoverWarning:P,borderActiveWarning:F,colorActiveError:I,boxShadowFocusError:ee,boxShadowActiveError:te,boxShadowHoverError:L,borderError:R,borderFocusError:z,borderHoverError:ne,borderActiveError:B,clearColor:V,clearColorHover:re,clearColorPressed:H,clearSize:U,arrowSize:W,[E(`height`,t)]:G,[E(`fontSize`,t)]:ie}}=D.value,K=g(c),q=g(l);return{"--n-bezier":n,"--n-border":y,"--n-border-active":S,"--n-border-focus":b,"--n-border-hover":x,"--n-border-radius":i,"--n-box-shadow-active":_,"--n-box-shadow-focus":h,"--n-box-shadow-hover":v,"--n-caret-color":u,"--n-color":a,"--n-color-active":m,"--n-color-disabled":d,"--n-font-size":ie,"--n-height":G,"--n-padding-single-top":K.top,"--n-padding-multiple-top":q.top,"--n-padding-single-right":K.right,"--n-padding-multiple-right":q.right,"--n-padding-single-left":K.left,"--n-padding-multiple-left":q.left,"--n-padding-single-bottom":K.bottom,"--n-padding-multiple-bottom":q.bottom,"--n-placeholder-color":o,"--n-placeholder-color-disabled":p,"--n-text-color":s,"--n-text-color-disabled":f,"--n-arrow-color":C,"--n-arrow-color-disabled":w,"--n-loading-color":T,"--n-color-active-warning":O,"--n-box-shadow-focus-warning":k,"--n-box-shadow-active-warning":A,"--n-box-shadow-hover-warning":j,"--n-border-warning":M,"--n-border-focus-warning":N,"--n-border-hover-warning":P,"--n-border-active-warning":F,"--n-color-active-error":I,"--n-box-shadow-focus-error":ee,"--n-box-shadow-active-error":te,"--n-box-shadow-hover-error":L,"--n-border-error":R,"--n-border-focus-error":z,"--n-border-hover-error":ne,"--n-border-active-error":B,"--n-clear-size":U,"--n-clear-color":V,"--n-clear-color-hover":re,"--n-clear-color-pressed":H,"--n-arrow-size":W,"--n-font-weight":r}}),be=ve?h(`internal-selection`,B(()=>e.size[0]),ye,e):void 0;return{mergedTheme:D,mergedClearable:O,mergedClsPrefix:n,rtlEnabled:c,patternInputFocused:w,filterablePlaceholder:k,label:A,selected:j,showTagsPanel:C,isComposing:G,counterRef:y,counterWrapperRef:b,patternInputMirrorRef:u,patternInputRef:d,selfRef:f,multipleElRef:p,singleElRef:_,patternInputWrapperRef:v,overflowRef:x,inputTagElRef:S,handleMouseDown:U,handleFocusin:R,handleClear:V,handleMouseEnter:re,handleMouseLeave:H,handleDeleteOption:W,handlePatternKeyDown:ie,handlePatternInputInput:q,handlePatternInputBlur:Y,handlePatternInputFocus:se,handleMouseEnterCounter:he,handleMouseLeaveCounter:ge,handleFocusout:z,handleCompositionEnd:oe,handleCompositionStart:ae,onPopoverUpdateShow:_e,focus:le,focusInput:X,blur:ce,blurInput:Z,updateCounter:ue,getCounter:de,getTail:fe,renderLabel:e.renderLabel,cssVars:ve?void 0:ye,themeClass:be?.themeClass,onRender:be?.onRender}},render(){let{status:e,multiple:t,size:n,disabled:r,filterable:i,maxTagCount:a,bordered:o,clsPrefix:s,ellipsisTagPopoverProps:c,onRender:l,renderTag:u,renderLabel:d}=this;l?.();let f=a===`responsive`,p=typeof a==`number`,m=f||p,h=j(v,null,{default:()=>j(Z,{clsPrefix:s,loading:this.loading,showArrow:this.showArrow,showClear:this.mergedClearable&&this.selected,onClear:this.handleClear},{default:()=>{var e;return(e=this.$slots).arrow?.call(e)}})}),g;if(t){let{labelField:e}=this,t=t=>j(`div`,{class:`${s}-base-selection-tag-wrapper`,key:t.value},u?u({option:t,handleClose:()=>{this.handleDeleteOption(t)}}):j(X,{size:n,closable:!t.disabled,disabled:r,onClose:()=>{this.handleDeleteOption(t)},internalCloseIsButtonTag:!1,internalCloseFocusable:!1},{default:()=>d?d(t,!0):Q(t[e],t,!0)})),o=()=>(p?this.selectedOptions.slice(0,a):this.selectedOptions).map(t),l=i?j(`div`,{class:`${s}-base-selection-input-tag`,ref:`inputTagElRef`,key:`__input-tag__`},j(`input`,Object.assign({},this.inputProps,{ref:`patternInputRef`,tabindex:-1,disabled:r,value:this.pattern,autofocus:this.autofocus,class:`${s}-base-selection-input-tag__input`,onBlur:this.handlePatternInputBlur,onFocus:this.handlePatternInputFocus,onKeydown:this.handlePatternKeyDown,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),j(`span`,{ref:`patternInputMirrorRef`,class:`${s}-base-selection-input-tag__mirror`},this.pattern)):null,_=f?()=>j(`div`,{class:`${s}-base-selection-tag-wrapper`,ref:`counterWrapperRef`},j(X,{size:n,ref:`counterRef`,onMouseenter:this.handleMouseEnterCounter,onMouseleave:this.handleMouseLeaveCounter,disabled:r})):void 0,v;if(p){let e=this.selectedOptions.length-a;e>0&&(v=j(`div`,{class:`${s}-base-selection-tag-wrapper`,key:`__counter__`},j(X,{size:n,ref:`counterRef`,onMouseenter:this.handleMouseEnterCounter,disabled:r},{default:()=>`+${e}`})))}let y=f?i?j(pe,{ref:`overflowRef`,updateCounter:this.updateCounter,getCounter:this.getCounter,getTail:this.getTail,style:{width:`100%`,display:`flex`,overflow:`hidden`}},{default:o,counter:_,tail:()=>l}):j(pe,{ref:`overflowRef`,updateCounter:this.updateCounter,getCounter:this.getCounter,style:{width:`100%`,display:`flex`,overflow:`hidden`}},{default:o,counter:_}):p&&v?o().concat(v):o(),b=m?()=>j(`div`,{class:`${s}-base-selection-popover`},f?o():this.selectedOptions.map(t)):void 0,x=m?Object.assign({show:this.showTagsPanel,trigger:`hover`,overlap:!0,placement:`top`,width:`trigger`,onUpdateShow:this.onPopoverUpdateShow,theme:this.mergedTheme.peers.Popover,themeOverrides:this.mergedTheme.peerOverrides.Popover},c):null,S=!this.selected&&(!this.active||!this.pattern&&!this.isComposing)?j(`div`,{class:`${s}-base-selection-placeholder ${s}-base-selection-overlay`},j(`div`,{class:`${s}-base-selection-placeholder__inner`},this.placeholder)):null,C=i?j(`div`,{ref:`patternInputWrapperRef`,class:`${s}-base-selection-tags`},y,f?null:l,h):j(`div`,{ref:`multipleElRef`,class:`${s}-base-selection-tags`,tabindex:r?void 0:0},y,h);g=j(M,null,m?j(G,Object.assign({},x,{scrollable:!0,style:`max-height: calc(var(--v-target-height) * 6.6);`}),{trigger:()=>C,default:b}):C,S)}else if(i){let e=this.pattern||this.isComposing,t=this.active?!e:!this.selected,n=!this.active&&this.selected;g=j(`div`,{ref:`patternInputWrapperRef`,class:`${s}-base-selection-label`,title:this.patternInputFocused?void 0:Ne(this.label)},j(`input`,Object.assign({},this.inputProps,{ref:`patternInputRef`,class:`${s}-base-selection-input`,value:this.active?this.pattern:``,placeholder:``,readonly:r,disabled:r,tabindex:-1,autofocus:this.autofocus,onFocus:this.handlePatternInputFocus,onBlur:this.handlePatternInputBlur,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),n?j(`div`,{class:`${s}-base-selection-label__render-label ${s}-base-selection-overlay`,key:`input`},j(`div`,{class:`${s}-base-selection-overlay__wrapper`},u?u({option:this.selectedOption,handleClose:()=>{}}):d?d(this.selectedOption,!0):Q(this.label,this.selectedOption,!0))):null,t?j(`div`,{class:`${s}-base-selection-placeholder ${s}-base-selection-overlay`,key:`placeholder`},j(`div`,{class:`${s}-base-selection-overlay__wrapper`},this.filterablePlaceholder)):null,h)}else g=j(`div`,{ref:`singleElRef`,class:`${s}-base-selection-label`,tabindex:this.disabled?void 0:0},this.label===void 0?j(`div`,{class:`${s}-base-selection-placeholder ${s}-base-selection-overlay`,key:`placeholder`},j(`div`,{class:`${s}-base-selection-placeholder__inner`},this.placeholder)):j(`div`,{class:`${s}-base-selection-input`,title:Ne(this.label),key:`input`},j(`div`,{class:`${s}-base-selection-input__content`},u?u({option:this.selectedOption,handleClose:()=>{}}):d?d(this.selectedOption,!0):Q(this.label,this.selectedOption,!0))),h);return j(`div`,{ref:`selfRef`,class:[`${s}-base-selection`,this.rtlEnabled&&`${s}-base-selection--rtl`,this.themeClass,e&&`${s}-base-selection--${e}-status`,{[`${s}-base-selection--active`]:this.active,[`${s}-base-selection--selected`]:this.selected||this.active&&this.pattern,[`${s}-base-selection--disabled`]:this.disabled,[`${s}-base-selection--multiple`]:this.multiple,[`${s}-base-selection--focus`]:this.focused}],style:this.cssVars,onClick:this.onClick,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onKeydown:this.onKeydown,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onMousedown:this.handleMouseDown},g,o?j(`div`,{class:`${s}-base-selection__border`}):null,o?j(`div`,{class:`${s}-base-selection__state-border`}):null)}});function Je(e){return e.type===`group`}function Ye(e){return e.type===`ignored`}function Xe(e,t){try{return!!(1+t.toString().toLowerCase().indexOf(e.trim().toLowerCase()))}catch{return!1}}function Ze(e,t){return{getIsGroup:Je,getIgnored:Ye,getKey(t){return Je(t)?t.name||t.key||`key-required`:t[e]},getChildren(e){return e[t]}}}function Qe(e,t,n,r){if(!t)return e;function i(e){if(!Array.isArray(e))return[];let a=[];for(let o of e)if(Je(o)){let e=i(o[r]);e.length&&a.push(Object.assign({},o,{[r]:e}))}else if(Ye(o))continue;else t(n,o)&&a.push(o);return a}return i(e)}function $e(e,t,n){let r=new Map;return e.forEach(e=>{Je(e)?e[n].forEach(e=>{r.set(e[t],e)}):r.set(e[t],e)}),r}var et=Y([n(`select`,`
 z-index: auto;
 outline: none;
 width: 100%;
 position: relative;
 font-weight: var(--n-font-weight);
 `),n(`select-menu`,`
 margin: 4px 0;
 box-shadow: var(--n-menu-box-shadow);
 `,[ue({originalTransition:`background-color .3s var(--n-bezier), box-shadow .3s var(--n-bezier)`})])]),tt=Object.assign(Object.assign({},r.props),{to:K.propTo,bordered:{type:Boolean,default:void 0},clearable:Boolean,clearCreatedOptionsOnClear:{type:Boolean,default:!0},clearFilterAfterSelect:{type:Boolean,default:!0},options:{type:Array,default:()=>[]},defaultValue:{type:[String,Number,Array],default:null},keyboard:{type:Boolean,default:!0},value:[String,Number,Array],placeholder:String,menuProps:Object,multiple:Boolean,size:String,menuSize:{type:String},filterable:Boolean,disabled:{type:Boolean,default:void 0},remote:Boolean,loading:Boolean,filter:Function,placement:{type:String,default:`bottom-start`},widthMode:{type:String,default:`trigger`},tag:Boolean,onCreate:Function,fallbackOption:{type:[Function,Boolean],default:void 0},show:{type:Boolean,default:void 0},showArrow:{type:Boolean,default:!0},maxTagCount:[Number,String],ellipsisTagPopoverProps:Object,consistentMenuWidth:{type:Boolean,default:!0},virtualScroll:{type:Boolean,default:!0},labelField:{type:String,default:`label`},valueField:{type:String,default:`value`},childrenField:{type:String,default:`children`},renderLabel:Function,renderOption:Function,renderTag:Function,"onUpdate:value":[Function,Array],inputProps:Object,nodeProps:Function,ignoreComposition:{type:Boolean,default:!0},showOnFocus:Boolean,onUpdateValue:[Function,Array],onBlur:[Function,Array],onClear:[Function,Array],onFocus:[Function,Array],onScroll:[Function,Array],onSearch:[Function,Array],onUpdateShow:[Function,Array],"onUpdate:show":[Function,Array],displayDirective:{type:String,default:`show`},resetMenuOnOptionsChange:{type:Boolean,default:!0},status:String,showCheckmark:{type:Boolean,default:!0},scrollbarProps:Object,onChange:[Function,Array],items:Array}),nt=z({name:`Select`,props:tt,slots:Object,setup(e){let{mergedClsPrefixRef:t,mergedBorderedRef:n,namespaceRef:i,inlineThemeDisabled:s,mergedComponentPropsRef:c}=o(e),d=r(`Select`,`-select`,et,ge,e,t),f=m(e.defaultValue),p=l(e,`value`),g=k(p,f),_=m(!1),v=m(``),y=oe(e,[`items`,`options`]),b=m([]),x=m([]),S=B(()=>x.value.concat(b.value).concat(y.value)),C=B(()=>{let{filter:t}=e;if(t)return t;let{labelField:n,valueField:r}=e;return(e,t)=>{if(!t)return!1;let i=t[n];if(typeof i==`string`)return Xe(e,i);let a=t[r];return typeof a==`string`?Xe(e,a):typeof a==`number`&&Xe(e,String(a))}}),w=B(()=>{if(e.remote)return y.value;{let{value:t}=S,{value:n}=v;return!n.length||!e.filterable?t:Qe(t,C.value,n,e.childrenField)}}),T=B(()=>{let{valueField:t,childrenField:n}=e,r=Ze(t,n);return fe(w.value,r)}),E=B(()=>$e(S.value,e.valueField,e.childrenField)),D=m(!1),O=k(l(e,`show`),D),A=m(null),j=m(null),M=m(null),{localeRef:N}=ce(`Select`),P=B(()=>e.placeholder??N.value.placeholder),F=[],I=m(new Map),ee=B(()=>{let{fallbackOption:t}=e;if(t===void 0){let{labelField:t,valueField:n}=e;return e=>({[t]:String(e),[n]:e})}return t===!1?!1:e=>Object.assign(t(e),{value:e})});function te(t){let n=e.remote,{value:r}=I,{value:i}=E,{value:a}=ee,o=[];return t.forEach(e=>{if(i.has(e))o.push(i.get(e));else if(n&&r.has(e))o.push(r.get(e));else if(a){let t=a(e);t&&o.push(t)}}),o}let L=B(()=>{if(e.multiple){let{value:e}=g;return Array.isArray(e)?te(e):[]}return null}),R=B(()=>{let{value:t}=g;return!e.multiple&&!Array.isArray(t)?t===null?null:te([t])[0]||null:null}),z=le(e,{mergedSize:t=>{let{size:n}=e;if(n)return n;let{mergedSize:r}=t||{};return r?.value?r.value:c?.value?.Select?.size||`medium`}}),{mergedSizeRef:ne,mergedDisabledRef:V,mergedStatusRef:re}=z;function H(t,n){let{onChange:r,"onUpdate:value":i,onUpdateValue:a}=e,{nTriggerFormChange:o,nTriggerFormInput:s}=z;r&&U(r,t,n),a&&U(a,t,n),i&&U(i,t,n),f.value=t,o(),s()}function W(t){let{onBlur:n}=e,{nTriggerFormBlur:r}=z;n&&U(n,t),r()}function G(){let{onClear:t}=e;t&&U(t)}function ie(t){let{onFocus:n,showOnFocus:r}=e,{nTriggerFormFocus:i}=z;n&&U(n,t),i(),r&&X()}function q(t){let{onSearch:n}=e;n&&U(n,t)}function ae(t){let{onScroll:n}=e;n&&U(n,t)}function J(){var t;let{remote:n,multiple:r}=e;if(n){let{value:n}=I;if(r){let{valueField:r}=e;(t=L.value)==null||t.forEach(e=>{n.set(e[r],e)})}else{let t=R.value;t&&n.set(t[e.valueField],t)}}}function Y(t){let{onUpdateShow:n,"onUpdate:show":r}=e;n&&U(n,t),r&&U(r,t),D.value=t}function X(){V.value||(Y(!0),D.value=!0,e.filterable&&Ne())}function Z(){Y(!1)}function ue(){v.value=``,x.value=F}let de=m(!1);function pe(){e.filterable&&(de.value=!0)}function Q(){e.filterable&&(de.value=!1,O.value||ue())}function me(){V.value||(O.value?e.filterable?Ne():Z():X())}function he(e){(M.value?.selfRef)?.contains(e.relatedTarget)||(_.value=!1,W(e),Z())}function _e(e){ie(e),_.value=!0}function ve(){_.value=!0}function ye(e){A.value?.$el.contains(e.relatedTarget)||(_.value=!1,W(e),Z())}function be(){var e;(e=A.value)==null||e.focus(),Z()}function xe(e){O.value&&(A.value?.$el.contains(u(e))||Z())}function Se(t){if(!Array.isArray(t))return[];if(ee.value)return Array.from(t);{let{remote:n}=e,{value:r}=E;if(n){let{value:e}=I;return t.filter(t=>r.has(t)||e.has(t))}return t.filter(e=>r.has(e))}}function Ce(e){we(e.rawNode)}function we(t){if(V.value)return;let{tag:n,remote:r,clearFilterAfterSelect:i,valueField:a}=e;if(n&&!r){let{value:e}=x,t=e[0]||null;if(t){let e=b.value;e.length?e.push(t):b.value=[t],x.value=F}}if(r&&I.value.set(t[a],t),e.multiple){let e=Se(g.value),o=e.findIndex(e=>e===t[a]);if(~o){if(e.splice(o,1),n&&!r){let e=Te(t[a]);~e&&(b.value.splice(e,1),i&&(v.value=``))}}else e.push(t[a]),i&&(v.value=``);H(e,te(e))}else{if(n&&!r){let e=Te(t[a]);~e?b.value=[b.value[e]]:b.value=F}Me(),Z(),H(t[a],t)}}function Te(t){return b.value.findIndex(n=>n[e.valueField]===t)}function Ee(t){O.value||X();let{value:n}=t.target;v.value=n;let{tag:r,remote:i}=e;if(q(n),r&&!i){if(!n){x.value=F;return}let{onCreate:t}=e,r=t?t(n):{[e.labelField]:n,[e.valueField]:n},{valueField:i,labelField:a}=e;y.value.some(e=>e[i]===r[i]||e[a]===r[a])||b.value.some(e=>e[i]===r[i]||e[a]===r[a])?x.value=F:x.value=[r]}}function De(t){t.stopPropagation();let{multiple:n,tag:r,remote:i,clearCreatedOptionsOnClear:a}=e;!n&&e.filterable&&Z(),r&&!i&&a&&(b.value=F),G(),n?H([],[]):H(null,null)}function Oe(e){!$(e,`action`)&&!$(e,`empty`)&&!$(e,`header`)&&e.preventDefault()}function ke(e){ae(e)}function Ae(t){var n,r,i;if(!e.keyboard){t.preventDefault();return}switch(t.key){case` `:if(e.filterable)break;t.preventDefault();case`Enter`:if(!A.value?.isComposing){if(O.value){let t=M.value?.getPendingTmNode();t?Ce(t):e.filterable||(Z(),Me())}else if(X(),e.tag&&de.value){let t=x.value[0];if(t){let n=t[e.valueField],{value:r}=g;e.multiple&&Array.isArray(r)&&r.includes(n)||we(t)}}}t.preventDefault();break;case`ArrowUp`:if(t.preventDefault(),e.loading)return;O.value&&((n=M.value)==null||n.prev());break;case`ArrowDown`:if(t.preventDefault(),e.loading)return;O.value?(r=M.value)==null||r.next():X();break;case`Escape`:O.value&&(je(t),Z()),(i=A.value)==null||i.focus()}}function Me(){var e;(e=A.value)==null||e.focus()}function Ne(){var e;(e=A.value)==null||e.focusInput()}function Pe(){var e;O.value&&((e=j.value)==null||e.syncPosition())}J(),a(l(e,`options`),J);let Fe={focus:()=>{var e;(e=A.value)==null||e.focus()},focusInput:()=>{var e;(e=A.value)==null||e.focusInput()},blur:()=>{var e;(e=A.value)==null||e.blur()},blurInput:()=>{var e;(e=A.value)==null||e.blurInput()}},Ie=B(()=>{let{self:{menuBoxShadow:e}}=d.value;return{"--n-menu-box-shadow":e}}),Le=s?h(`select`,void 0,Ie,e):void 0;return Object.assign(Object.assign({},Fe),{mergedStatus:re,mergedClsPrefix:t,mergedBordered:n,namespace:i,treeMate:T,isMounted:se(),triggerRef:A,menuRef:M,pattern:v,uncontrolledShow:D,mergedShow:O,adjustedTo:K(e),uncontrolledValue:f,mergedValue:g,followerRef:j,localizedPlaceholder:P,selectedOption:R,selectedOptions:L,mergedSize:ne,mergedDisabled:V,focused:_,activeWithoutMenuOpen:de,inlineThemeDisabled:s,onTriggerInputFocus:pe,onTriggerInputBlur:Q,handleTriggerOrMenuResize:Pe,handleMenuFocus:ve,handleMenuBlur:ye,handleMenuTabOut:be,handleTriggerClick:me,handleToggle:Ce,handleDeleteOption:we,handlePatternInput:Ee,handleClear:De,handleTriggerBlur:he,handleTriggerFocus:_e,handleKeydown:Ae,handleMenuAfterLeave:ue,handleMenuClickOutside:xe,handleMenuScroll:ke,handleMenuKeydown:Ae,handleMenuMousedown:Oe,mergedTheme:d,cssVars:s?void 0:Ie,themeClass:Le?.themeClass,onRender:Le?.onRender})},render(){return j(`div`,{class:`${this.mergedClsPrefix}-select`},j(A,null,{default:()=>[j(ie,null,{default:()=>j(qe,{ref:`triggerRef`,inlineThemeDisabled:this.inlineThemeDisabled,status:this.mergedStatus,inputProps:this.inputProps,clsPrefix:this.mergedClsPrefix,showArrow:this.showArrow,maxTagCount:this.maxTagCount,ellipsisTagPopoverProps:this.ellipsisTagPopoverProps,bordered:this.mergedBordered,active:this.activeWithoutMenuOpen||this.mergedShow,pattern:this.pattern,placeholder:this.localizedPlaceholder,selectedOption:this.selectedOption,selectedOptions:this.selectedOptions,multiple:this.multiple,renderTag:this.renderTag,renderLabel:this.renderLabel,filterable:this.filterable,clearable:this.clearable,disabled:this.mergedDisabled,size:this.mergedSize,theme:this.mergedTheme.peers.InternalSelection,labelField:this.labelField,valueField:this.valueField,themeOverrides:this.mergedTheme.peerOverrides.InternalSelection,loading:this.loading,focused:this.focused,onClick:this.handleTriggerClick,onDeleteOption:this.handleDeleteOption,onPatternInput:this.handlePatternInput,onClear:this.handleClear,onBlur:this.handleTriggerBlur,onFocus:this.handleTriggerFocus,onKeydown:this.handleKeydown,onPatternBlur:this.onTriggerInputBlur,onPatternFocus:this.onTriggerInputFocus,onResize:this.handleTriggerOrMenuResize,ignoreComposition:this.ignoreComposition},{arrow:()=>{var e;return[(e=this.$slots).arrow?.call(e)]}})}),j(N,{ref:`followerRef`,show:this.mergedShow,to:this.adjustedTo,teleportDisabled:this.adjustedTo===K.tdkey,containerClass:this.namespace,width:this.consistentMenuWidth?`target`:void 0,minWidth:`target`,placement:this.placement},{default:()=>j(d,{name:`fade-in-scale-up-transition`,appear:this.isMounted,onAfterLeave:this.handleMenuAfterLeave},{default:()=>{var e;return this.mergedShow||this.displayDirective===`show`?((e=this.onRender)==null||e.call(this),R(j(Ge,Object.assign({},this.menuProps,{ref:`menuRef`,onResize:this.handleTriggerOrMenuResize,inlineThemeDisabled:this.inlineThemeDisabled,virtualScroll:this.consistentMenuWidth&&this.virtualScroll,class:[`${this.mergedClsPrefix}-select-menu`,this.themeClass,this.menuProps?.class],clsPrefix:this.mergedClsPrefix,focusable:!0,labelField:this.labelField,valueField:this.valueField,autoPending:!0,nodeProps:this.nodeProps,theme:this.mergedTheme.peers.InternalSelectMenu,themeOverrides:this.mergedTheme.peerOverrides.InternalSelectMenu,treeMate:this.treeMate,multiple:this.multiple,size:this.menuSize,renderOption:this.renderOption,renderLabel:this.renderLabel,value:this.mergedValue,style:[this.menuProps?.style,this.cssVars],onToggle:this.handleToggle,onScroll:this.handleMenuScroll,onFocus:this.handleMenuFocus,onBlur:this.handleMenuBlur,onKeydown:this.handleMenuKeydown,onTabOut:this.handleMenuTabOut,onMousedown:this.handleMenuMousedown,show:this.mergedShow,showCheckmark:this.showCheckmark,resetMenuOnOptionsChange:this.resetMenuOnOptionsChange,scrollbarProps:this.scrollbarProps}),{empty:()=>{var e;return[(e=this.$slots).empty?.call(e)]},header:()=>{var e;return[(e=this.$slots).header?.call(e)]},action:()=>{var e;return[(e=this.$slots).action?.call(e)]}}),this.displayDirective===`show`?[[D,this.mergedShow],[re,this.handleMenuClickOutside,void 0,{capture:!0}]]:[[re,this.handleMenuClickOutside,void 0,{capture:!0}]])):null}})})]}))}});export{Pe as a,Be as i,Ze as n,Me as o,Ge as r,Oe as s,nt as t};
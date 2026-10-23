import{A as e,An as t,Bt as n,Cn as r,D as i,Dn as a,F as o,Ht as s,J as c,Ln as l,On as u,P as d,Pn as f,Q as p,Rn as m,Sn as h,Ut as g,Vn as _,Vt as v,Y as y,Yt as b,Z as x,Zt as S,_ as C,_n as w,an as T,bn as E,bt as D,cn as O,f as k,fn as A,ft as ee,ht as j,in as M,k as N,kn as P,ln as F,mn as te,mt as ne,nt as re,on as I,ot as ie,pn as L,pt as ae,rn as R,st as oe,t as se,un as z,vn as B,x as ce,xt as V}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{E as H,M as le,k as ue,v as de,y as fe}from"./api-GVzHhqB2.js";import{c as pe}from"./Select-BRr8OHS-.js";import{t as me}from"./Space-CP8ci0tZ.js";import{a as he}from"./index-BgAh03Vf.js";var U=f(!1);function W(){U.value=!0}function G(){U.value=!1}var K=0;function ge(){return le&&(w(()=>{K||(window.addEventListener(`compositionstart`,W),window.addEventListener(`compositionend`,G)),K++}),B(()=>{K<=1?(window.removeEventListener(`compositionstart`,W),window.removeEventListener(`compositionend`,G),K=0):K--})),U}var q=0,J=``,Y=``,X=``,Z=``,Q=f(`0px`);function _e(e){if(typeof document>`u`)return;let t=document.documentElement,n,r=!1,i=()=>{t.style.marginRight=J,t.style.overflow=Y,t.style.overflowX=X,t.style.overflowY=Z,Q.value=`0px`};E(()=>{n=a(e,e=>{if(e){if(!q){let e=window.innerWidth-t.offsetWidth;e>0&&(J=t.style.marginRight,t.style.marginRight=`${e}px`,Q.value=`${e}px`),Y=t.style.overflow,X=t.style.overflowX,Z=t.style.overflowY,t.style.overflow=`hidden`,t.style.overflowX=`hidden`,t.style.overflowY=`hidden`}r=!0,q++}else q--,q||i(),r=!1},{immediate:!0})}),B(()=>{n?.(),r&&=(q--,q||i(),!1)})}var ve=z({name:`NDrawerContent`,inheritAttrs:!1,props:{blockScroll:Boolean,show:{type:Boolean,default:void 0},displayDirective:{type:String,required:!0},placement:{type:String,required:!0},contentClass:String,contentStyle:[Object,String],nativeScrollbar:{type:Boolean,required:!0},scrollbarProps:Object,trapFocus:{type:Boolean,default:!0},autoFocus:{type:Boolean,default:!0},showMask:{type:[Boolean,String],required:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,onClickoutside:Function,onAfterLeave:Function,onAfterEnter:Function,onEsc:Function},setup(t){let n=f(!!t.show),i=f(null),s=L(j),c=0,l=``,d=null,p=f(!1),m=f(!1),h=R(()=>t.placement===`top`||t.placement===`bottom`),{mergedClsPrefixRef:g,mergedRtlRef:_}=o(t),v=e(`Drawer`,_,g),y=k,b=e=>{m.value=!0,c=h.value?e.clientY:e.clientX,l=document.body.style.cursor,document.body.style.cursor=h.value?`ns-resize`:`ew-resize`,document.body.addEventListener(`mousemove`,O),document.body.addEventListener(`mouseleave`,y),document.body.addEventListener(`mouseup`,k)},x=()=>{d!==null&&(window.clearTimeout(d),d=null),m.value?p.value=!0:d=window.setTimeout(()=>{p.value=!0},300)},C=()=>{d!==null&&(window.clearTimeout(d),d=null),p.value=!1},{doUpdateHeight:w,doUpdateWidth:T}=s,E=e=>{let{maxWidth:n}=t;if(n&&e>n)return n;let{minWidth:r}=t;return r&&e<r?r:e},D=e=>{let{maxHeight:n}=t;if(n&&e>n)return n;let{minHeight:r}=t;return r&&e<r?r:e};function O(e){if(m.value)if(h.value){let n=i.value?.offsetHeight||0,r=c-e.clientY;n+=t.placement===`bottom`?r:-r,n=D(n),w(n),c=e.clientY}else{let n=i.value?.offsetWidth||0,r=c-e.clientX;n+=t.placement===`right`?r:-r,n=E(n),T(n),c=e.clientX}}function k(){m.value&&(c=0,m.value=!1,document.body.style.cursor=l,document.body.removeEventListener(`mousemove`,O),document.body.removeEventListener(`mouseup`,k),document.body.removeEventListener(`mouseleave`,y))}u(()=>{t.show&&(n.value=!0)}),a(()=>t.show,e=>{e||k()}),B(()=>{k()});let A=R(()=>{let{show:e}=t,n=[[S,e]];return t.showMask||n.push([oe,t.onClickoutside,void 0,{capture:!0}]),n});function M(){var e;n.value=!1,(e=t.onAfterLeave)==null||e.call(t)}return _e(R(()=>t.blockScroll&&n.value)),r(ne,i),r(ee,null),r(ae,null),{bodyRef:i,rtlEnabled:v,mergedClsPrefix:s.mergedClsPrefixRef,isMounted:s.isMountedRef,mergedTheme:s.mergedThemeRef,displayed:n,transitionName:R(()=>({right:`slide-in-from-right-transition`,left:`slide-in-from-left-transition`,top:`slide-in-from-top-transition`,bottom:`slide-in-from-bottom-transition`})[t.placement]),handleAfterLeave:M,bodyDirectives:A,handleMousedownResizeTrigger:b,handleMouseenterResizeTrigger:x,handleMouseleaveResizeTrigger:C,isDragging:m,isHoverOnResizeTrigger:p}},render(){let{$slots:e,mergedClsPrefix:n}=this;return this.displayDirective===`show`||this.displayed||this.show?t(A(`div`,{role:`none`},A(p,{disabled:!this.showMask||!this.trapFocus,active:this.show,autoFocus:this.autoFocus,onEsc:this.onEsc},{default:()=>A(b,{name:this.transitionName,appear:this.isMounted,onAfterEnter:this.onAfterEnter,onAfterLeave:this.handleAfterLeave},{default:()=>t(A(`div`,te(this.$attrs,{role:`dialog`,ref:`bodyRef`,"aria-modal":`true`,class:[`${n}-drawer`,this.rtlEnabled&&`${n}-drawer--rtl`,`${n}-drawer--${this.placement}-placement`,this.isDragging&&`${n}-drawer--unselectable`,this.nativeScrollbar&&`${n}-drawer--native-scrollbar`]}),[this.resizable?A(`div`,{class:[`${n}-drawer__resize-trigger`,(this.isDragging||this.isHoverOnResizeTrigger)&&`${n}-drawer__resize-trigger--hover`],onMouseenter:this.handleMouseenterResizeTrigger,onMouseleave:this.handleMouseleaveResizeTrigger,onMousedown:this.handleMousedownResizeTrigger}):null,this.nativeScrollbar?A(`div`,{class:[`${n}-drawer-content-wrapper`,this.contentClass],style:this.contentStyle,role:`none`},e):A(k,Object.assign({},this.scrollbarProps,{contentStyle:this.contentStyle,contentClass:[`${n}-drawer-content-wrapper`,this.contentClass],theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar}),e)]),this.bodyDirectives)})})),[[S,this.displayDirective===`if`||this.displayed||this.show]]):null}}),{cubicBezierEaseIn:ye,cubicBezierEaseOut:be}=N;function xe({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-bottom`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${ye}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${be}`}),n(`&.${r}-transition-enter-to`,{transform:`translateY(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateY(100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateY(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateY(100%)`})]}var{cubicBezierEaseIn:Se,cubicBezierEaseOut:Ce}=N;function we({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-left`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${Se}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${Ce}`}),n(`&.${r}-transition-enter-to`,{transform:`translateX(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateX(-100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateX(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateX(-100%)`})]}var{cubicBezierEaseIn:Te,cubicBezierEaseOut:$}=N;function Ee({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-right`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${Te}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${$}`}),n(`&.${r}-transition-enter-to`,{transform:`translateX(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateX(100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateX(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateX(100%)`})]}var{cubicBezierEaseIn:De,cubicBezierEaseOut:Oe}=N;function ke({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-top`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${De}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${Oe}`}),n(`&.${r}-transition-enter-to`,{transform:`translateY(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateY(-100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateY(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateY(-100%)`})]}var Ae=n([v(`drawer`,`
 word-break: break-word;
 line-height: var(--n-line-height);
 position: absolute;
 pointer-events: all;
 box-shadow: var(--n-box-shadow);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 background-color: var(--n-color);
 color: var(--n-text-color);
 box-sizing: border-box;
 `,[Ee(),we(),ke(),xe(),g(`unselectable`,`
 user-select: none; 
 -webkit-user-select: none;
 `),g(`native-scrollbar`,[v(`drawer-content-wrapper`,`
 overflow: auto;
 height: 100%;
 `)]),s(`resize-trigger`,`
 position: absolute;
 background-color: #0000;
 transition: background-color .3s var(--n-bezier);
 `,[g(`hover`,`
 background-color: var(--n-resize-trigger-color-hover);
 `)]),v(`drawer-content-wrapper`,`
 box-sizing: border-box;
 `),v(`drawer-content`,`
 height: 100%;
 display: flex;
 flex-direction: column;
 `,[g(`native-scrollbar`,[v(`drawer-body-content-wrapper`,`
 height: 100%;
 overflow: auto;
 `)]),v(`drawer-body`,`
 flex: 1 0 0;
 overflow: hidden;
 `),v(`drawer-body-content-wrapper`,`
 box-sizing: border-box;
 padding: var(--n-body-padding);
 `),v(`drawer-header`,`
 font-weight: var(--n-title-font-weight);
 line-height: 1;
 font-size: var(--n-title-font-size);
 color: var(--n-title-text-color);
 padding: var(--n-header-padding);
 transition: border .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-divider-color);
 border-bottom: var(--n-header-border-bottom);
 display: flex;
 justify-content: space-between;
 align-items: center;
 `,[s(`main`,`
 flex: 1;
 `),s(`close`,`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)]),v(`drawer-footer`,`
 display: flex;
 justify-content: flex-end;
 border-top: var(--n-footer-border-top);
 transition: border .3s var(--n-bezier);
 padding: var(--n-footer-padding);
 `)]),g(`right-placement`,`
 top: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-bottom-left-radius: var(--n-border-radius);
 `,[s(`resize-trigger`,`
 width: 3px;
 height: 100%;
 top: 0;
 left: 0;
 transform: translateX(-1.5px);
 cursor: ew-resize;
 `)]),g(`left-placement`,`
 top: 0;
 bottom: 0;
 left: 0;
 border-top-right-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[s(`resize-trigger`,`
 width: 3px;
 height: 100%;
 top: 0;
 right: 0;
 transform: translateX(1.5px);
 cursor: ew-resize;
 `)]),g(`top-placement`,`
 top: 0;
 left: 0;
 right: 0;
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[s(`resize-trigger`,`
 width: 100%;
 height: 3px;
 bottom: 0;
 left: 0;
 transform: translateY(1.5px);
 cursor: ns-resize;
 `)]),g(`bottom-placement`,`
 left: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-top-right-radius: var(--n-border-radius);
 `,[s(`resize-trigger`,`
 width: 100%;
 height: 3px;
 top: 0;
 left: 0;
 transform: translateY(-1.5px);
 cursor: ns-resize;
 `)])]),n(`body`,[n(`>`,[v(`drawer-container`,`
 position: fixed;
 `)])]),v(`drawer-container`,`
 position: relative;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 `,[n(`> *`,`
 pointer-events: all;
 `)]),v(`drawer-mask`,`
 background-color: rgba(0, 0, 0, .3);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `,[g(`invisible`,`
 background-color: rgba(0, 0, 0, 0)
 `),C({enterDuration:`0.2s`,leaveDuration:`0.2s`,enterCubicBezier:`var(--n-bezier-in)`,leaveCubicBezier:`var(--n-bezier-out)`})])]),je=Object.assign(Object.assign({},i.props),{show:Boolean,width:[Number,String],height:[Number,String],placement:{type:String,default:`right`},maskClosable:{type:Boolean,default:!0},showMask:{type:[Boolean,String],default:!0},to:[String,Object],displayDirective:{type:String,default:`if`},nativeScrollbar:{type:Boolean,default:!0},zIndex:Number,onMaskClick:Function,scrollbarProps:Object,contentClass:String,contentStyle:[Object,String],trapFocus:{type:Boolean,default:!0},onEsc:Function,autoFocus:{type:Boolean,default:!0},closeOnEsc:{type:Boolean,default:!0},blockScroll:{type:Boolean,default:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,defaultWidth:{type:[Number,String],default:251},defaultHeight:{type:[Number,String],default:251},onUpdateWidth:[Function,Array],onUpdateHeight:[Function,Array],"onUpdate:width":[Function,Array],"onUpdate:height":[Function,Array],"onUpdate:show":[Function,Array],onUpdateShow:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,drawerStyle:[String,Object],drawerClass:String,target:null,onShow:Function,onHide:Function}),Me=z({name:`Drawer`,inheritAttrs:!1,props:je,setup(e){let{mergedClsPrefixRef:t,namespaceRef:n,inlineThemeDisabled:a}=o(e),s=D(),u=i(`Drawer`,`-drawer`,Ae,he,e,t),p=f(e.defaultWidth),m=f(e.defaultHeight),h=V(l(e,`width`),p),g=V(l(e,`height`),m),_=R(()=>{let{placement:t}=e;return t===`top`||t===`bottom`?``:x(h.value)}),v=R(()=>{let{placement:t}=e;return t===`left`||t===`right`?``:x(g.value)}),y=t=>{let{onUpdateWidth:n,"onUpdate:width":r}=e;n&&c(n,t),r&&c(r,t),p.value=t},b=t=>{let{onUpdateHeight:n,"onUpdate:width":r}=e;n&&c(n,t),r&&c(r,t),m.value=t},S=R(()=>[{width:_.value,height:v.value},e.drawerStyle||``]);function C(t){let{onMaskClick:n,maskClosable:r}=e;r&&O(!1),n&&n(t)}function w(e){C(e)}let T=ge();function E(t){var n;(n=e.onEsc)==null||n.call(e),e.show&&e.closeOnEsc&&pe(t)&&(T.value||O(!1))}function O(t){let{onHide:n,onUpdateShow:r,"onUpdate:show":i}=e;r&&c(r,t),i&&c(i,t),n&&!t&&c(n,t)}r(j,{isMountedRef:s,mergedThemeRef:u,mergedClsPrefixRef:t,doUpdateShow:O,doUpdateHeight:b,doUpdateWidth:y});let k=R(()=>{let{common:{cubicBezierEaseInOut:e,cubicBezierEaseIn:t,cubicBezierEaseOut:n},self:{color:r,textColor:i,boxShadow:a,lineHeight:o,headerPadding:s,footerPadding:c,borderRadius:l,bodyPadding:d,titleFontSize:f,titleTextColor:p,titleFontWeight:m,headerBorderBottom:h,footerBorderTop:g,closeIconColor:_,closeIconColorHover:v,closeIconColorPressed:y,closeColorHover:b,closeColorPressed:x,closeIconSize:S,closeSize:C,closeBorderRadius:w,resizableTriggerColorHover:T}}=u.value;return{"--n-line-height":o,"--n-color":r,"--n-border-radius":l,"--n-text-color":i,"--n-box-shadow":a,"--n-bezier":e,"--n-bezier-out":n,"--n-bezier-in":t,"--n-header-padding":s,"--n-body-padding":d,"--n-footer-padding":c,"--n-title-text-color":p,"--n-title-font-size":f,"--n-title-font-weight":m,"--n-header-border-bottom":h,"--n-footer-border-top":g,"--n-close-icon-color":_,"--n-close-icon-color-hover":v,"--n-close-icon-color-pressed":y,"--n-close-size":C,"--n-close-color-hover":b,"--n-close-color-pressed":x,"--n-close-icon-size":S,"--n-close-border-radius":w,"--n-resize-trigger-color-hover":T}}),A=a?d(`drawer`,void 0,k,e):void 0;return{mergedClsPrefix:t,namespace:n,mergedBodyStyle:S,handleOutsideClick:w,handleMaskClick:C,handleEsc:E,mergedTheme:u,cssVars:a?void 0:k,themeClass:A?.themeClass,onRender:A?.onRender,isMounted:s}},render(){let{mergedClsPrefix:e}=this;return A(re,{to:this.to,show:this.show},{default:()=>{var n;return(n=this.onRender)==null||n.call(this),t(A(`div`,{class:[`${e}-drawer-container`,this.namespace,this.themeClass],style:this.cssVars,role:`none`},this.showMask?A(b,{name:`fade-in-transition`,appear:this.isMounted},{default:()=>this.show?A(`div`,{"aria-hidden":!0,class:[`${e}-drawer-mask`,this.showMask===`transparent`&&`${e}-drawer-mask--invisible`],onClick:this.handleMaskClick}):null}):null,A(ve,Object.assign({},this.$attrs,{class:[this.drawerClass,this.$attrs.class],style:[this.mergedBodyStyle,this.$attrs.style],blockScroll:this.blockScroll,contentStyle:this.contentStyle,contentClass:this.contentClass,placement:this.placement,scrollbarProps:this.scrollbarProps,show:this.show,displayDirective:this.displayDirective,nativeScrollbar:this.nativeScrollbar,onAfterEnter:this.onAfterEnter,onAfterLeave:this.onAfterLeave,trapFocus:this.trapFocus,autoFocus:this.autoFocus,resizable:this.resizable,maxHeight:this.maxHeight,minHeight:this.minHeight,maxWidth:this.maxWidth,minWidth:this.minWidth,showMask:this.showMask,onEsc:this.handleEsc,onClickoutside:this.handleOutsideClick}),this.$slots)),[[ie,{zIndex:this.zIndex,enabled:this.show}]])}})}}),Ne=z({name:`DrawerContent`,props:{title:String,headerClass:String,headerStyle:[Object,String],footerClass:String,footerStyle:[Object,String],bodyClass:String,bodyStyle:[Object,String],bodyContentClass:String,bodyContentStyle:[Object,String],nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,closable:Boolean},slots:Object,setup(){let e=L(j,null);e||y(`drawer-content`,"`n-drawer-content` must be placed inside `n-drawer`.");let{doUpdateShow:t}=e;function n(){t(!1)}return{handleCloseClick:n,mergedTheme:e.mergedThemeRef,mergedClsPrefix:e.mergedClsPrefixRef}},render(){let{title:e,mergedClsPrefix:t,nativeScrollbar:n,mergedTheme:r,bodyClass:i,bodyStyle:a,bodyContentClass:o,bodyContentStyle:s,headerClass:c,headerStyle:l,footerClass:u,footerStyle:d,scrollbarProps:f,closable:p,$slots:m}=this;return A(`div`,{role:`none`,class:[`${t}-drawer-content`,n&&`${t}-drawer-content--native-scrollbar`]},m.header||e||p?A(`div`,{class:[`${t}-drawer-header`,c],style:l,role:`none`},A(`div`,{class:`${t}-drawer-header__main`,role:`heading`,"aria-level":`1`},m.header===void 0?e:m.header()),p&&A(ce,{onClick:this.handleCloseClick,clsPrefix:t,class:`${t}-drawer-header__close`,absolute:!0})):null,n?A(`div`,{class:[`${t}-drawer-body`,i],style:a,role:`none`},A(`div`,{class:[`${t}-drawer-body-content-wrapper`,o],style:s,role:`none`},m)):A(k,Object.assign({themeOverrides:r.peerOverrides.Scrollbar,theme:r.peers.Scrollbar},f,{class:`${t}-drawer-body`,contentClass:[`${t}-drawer-body-content-wrapper`,o],contentStyle:s}),m),m.footer?A(`div`,{class:[`${t}-drawer-footer`,u],style:d,role:`none`},m.footer()):null)}}),Pe={class:`page-text`},Fe=se(z({__name:`PageDrawer`,props:{show:{type:Boolean},file:{default:``},page:{default:1},width:{default:740},ocrLabel:{default:`OCR 识别`}},emits:[`update:show`],setup(e,{emit:t}){let n=e,r=t,i=R({get:()=>n.show,set:e=>r(`update:show`,e)}),o=f(n.page),s=f(``),c=f(!1),l=f(!1),u=f(``);async function d(e,t){if(!(!e||t<1)){l.value=!0,u.value=``;try{let n=await fe(e,t);s.value=n.text||n.error||`(空)`,c.value=!!n.ocr}catch(e){s.value=``,u.value=`读取失败:${e.message}`}finally{l.value=!1}}}a(()=>[n.file,n.page],([,e])=>{o.value=e},{immediate:!0}),a(i,e=>{e&&(o.value=n.page,d(n.file,n.page))});function p(e){let t=o.value+e;t<1||(o.value=t,d(n.file,t))}return(t,n)=>(h(),T(m(Me),{show:i.value,"onUpdate:show":n[2]||=e=>i.value=e,width:e.width,placement:`right`},{default:P(()=>[e.file?(h(),T(m(Ne),{key:0,closable:``,title:`${e.file} 第${o.value}页`},{default:P(()=>[F(m(me),{class:`page-nav`,align:`center`},{default:P(()=>[F(m(H),{size:`small`,disabled:o.value<=1,loading:l.value,onClick:n[0]||=e=>p(-1)},{default:P(()=>[...n[3]||=[O(`上一页`,-1)]]),_:1},8,[`disabled`,`loading`]),M(`span`,null,`第 `+_(o.value)+` 页`,1),F(m(H),{size:`small`,loading:l.value,onClick:n[1]||=e=>p(1)},{default:P(()=>[...n[4]||=[O(`下一页`,-1)]]),_:1},8,[`loading`]),c.value?(h(),T(m(ue),{key:0,size:`small`,type:`warning`,round:``},{default:P(()=>[O(_(e.ocrLabel),1)]),_:1})):I(``,!0),F(m(H),{size:`small`,tag:`a`,href:m(de)(e.file,o.value),target:`_blank`},{default:P(()=>[...n[5]||=[O(`打开原文`,-1)]]),_:1},8,[`href`])]),_:1}),M(`pre`,Pe,_(u.value||s.value),1)]),_:1},8,[`title`])):I(``,!0)]),_:1},8,[`show`,`width`]))}}),[[`__scopeId`,`data-v-3d265eac`]]);export{Fe as t};
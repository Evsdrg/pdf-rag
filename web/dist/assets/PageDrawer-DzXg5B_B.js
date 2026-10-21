import{A as e,Bn as t,Bt as n,D as r,Dn as i,En as a,F as o,Ht as s,In as c,J as l,Jt as u,Ln as d,Nn as f,On as p,P as m,Sn as h,Vt as g,X as _,Xt as v,Z as y,_ as b,_n as x,an as S,at as C,bt as w,cn as T,dn as E,dt as D,f as O,fn as k,ft as ee,gn as A,in as j,k as M,kn as N,ln as P,mt as F,nn as I,ot as te,pn as ne,pt as re,q as L,rn as R,sn as z,t as ie,tt as ae,x as oe,xn as B,yn as se,yt as ce,zt as V}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{E as H,N as le,k as ue,v as de,y as fe}from"./api-Bfr7BT7g.js";import{o as pe}from"./Select-CL5-NE5w.js";import{t as me}from"./Space-ZYI01Owy.js";import{a as he}from"./index-Li7ENe2r.js";var U=f(!1);function W(){U.value=!0}function G(){U.value=!1}var K=0;function ge(){return le&&(A(()=>{K||(window.addEventListener(`compositionstart`,W),window.addEventListener(`compositionend`,G)),K++}),x(()=>{K<=1?(window.removeEventListener(`compositionstart`,W),window.removeEventListener(`compositionend`,G),K=0):K--})),U}var q=0,J=``,Y=``,X=``,Z=``,Q=f(`0px`);function _e(e){if(typeof document>`u`)return;let t=document.documentElement,n,r=!1,i=()=>{t.style.marginRight=J,t.style.overflow=Y,t.style.overflowX=X,t.style.overflowY=Z,Q.value=`0px`};se(()=>{n=a(e,e=>{if(e){if(!q){let e=window.innerWidth-t.offsetWidth;e>0&&(J=t.style.marginRight,t.style.marginRight=`${e}px`,Q.value=`${e}px`),Y=t.style.overflow,X=t.style.overflowX,Z=t.style.overflowY,t.style.overflow=`hidden`,t.style.overflowX=`hidden`,t.style.overflowY=`hidden`}r=!0,q++}else q--,q||i(),r=!1},{immediate:!0})}),x(()=>{n?.(),r&&=(q--,q||i(),!1)})}var ve=P({name:`NDrawerContent`,inheritAttrs:!1,props:{blockScroll:Boolean,show:{type:Boolean,default:void 0},displayDirective:{type:String,required:!0},placement:{type:String,required:!0},contentClass:String,contentStyle:[Object,String],nativeScrollbar:{type:Boolean,required:!0},scrollbarProps:Object,trapFocus:{type:Boolean,default:!0},autoFocus:{type:Boolean,default:!0},showMask:{type:[Boolean,String],required:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,onClickoutside:Function,onAfterLeave:Function,onAfterEnter:Function,onEsc:Function},setup(t){let n=f(!!t.show),r=f(null),s=k(F),c=0,l=``,u=null,d=f(!1),p=f(!1),m=I(()=>t.placement===`top`||t.placement===`bottom`),{mergedClsPrefixRef:g,mergedRtlRef:_}=o(t),y=e(`Drawer`,_,g),b=M,S=e=>{p.value=!0,c=m.value?e.clientY:e.clientX,l=document.body.style.cursor,document.body.style.cursor=m.value?`ns-resize`:`ew-resize`,document.body.addEventListener(`mousemove`,j),document.body.addEventListener(`mouseleave`,b),document.body.addEventListener(`mouseup`,M)},C=()=>{u!==null&&(window.clearTimeout(u),u=null),p.value?d.value=!0:u=window.setTimeout(()=>{d.value=!0},300)},w=()=>{u!==null&&(window.clearTimeout(u),u=null),d.value=!1},{doUpdateHeight:T,doUpdateWidth:E}=s,O=e=>{let{maxWidth:n}=t;if(n&&e>n)return n;let{minWidth:r}=t;return r&&e<r?r:e},A=e=>{let{maxHeight:n}=t;if(n&&e>n)return n;let{minHeight:r}=t;return r&&e<r?r:e};function j(e){if(p.value)if(m.value){let n=r.value?.offsetHeight||0,i=c-e.clientY;n+=t.placement===`bottom`?i:-i,n=A(n),T(n),c=e.clientY}else{let n=r.value?.offsetWidth||0,i=c-e.clientX;n+=t.placement===`right`?i:-i,n=O(n),E(n),c=e.clientX}}function M(){p.value&&(c=0,p.value=!1,document.body.style.cursor=l,document.body.removeEventListener(`mousemove`,j),document.body.removeEventListener(`mouseup`,M),document.body.removeEventListener(`mouseleave`,b))}i(()=>{t.show&&(n.value=!0)}),a(()=>t.show,e=>{e||M()}),x(()=>{M()});let N=I(()=>{let{show:e}=t,n=[[v,e]];return t.showMask||n.push([te,t.onClickoutside,void 0,{capture:!0}]),n});function P(){var e;n.value=!1,(e=t.onAfterLeave)==null||e.call(t)}return _e(I(()=>t.blockScroll&&n.value)),h(re,r),h(D,null),h(ee,null),{bodyRef:r,rtlEnabled:y,mergedClsPrefix:s.mergedClsPrefixRef,isMounted:s.isMountedRef,mergedTheme:s.mergedThemeRef,displayed:n,transitionName:I(()=>({right:`slide-in-from-right-transition`,left:`slide-in-from-left-transition`,top:`slide-in-from-top-transition`,bottom:`slide-in-from-bottom-transition`})[t.placement]),handleAfterLeave:P,bodyDirectives:N,handleMousedownResizeTrigger:S,handleMouseenterResizeTrigger:C,handleMouseleaveResizeTrigger:w,isDragging:p,isHoverOnResizeTrigger:d}},render(){let{$slots:e,mergedClsPrefix:t}=this;return this.displayDirective===`show`||this.displayed||this.show?N(E(`div`,{role:`none`},E(y,{disabled:!this.showMask||!this.trapFocus,active:this.show,autoFocus:this.autoFocus,onEsc:this.onEsc},{default:()=>E(u,{name:this.transitionName,appear:this.isMounted,onAfterEnter:this.onAfterEnter,onAfterLeave:this.handleAfterLeave},{default:()=>N(E(`div`,ne(this.$attrs,{role:`dialog`,ref:`bodyRef`,"aria-modal":`true`,class:[`${t}-drawer`,this.rtlEnabled&&`${t}-drawer--rtl`,`${t}-drawer--${this.placement}-placement`,this.isDragging&&`${t}-drawer--unselectable`,this.nativeScrollbar&&`${t}-drawer--native-scrollbar`]}),[this.resizable?E(`div`,{class:[`${t}-drawer__resize-trigger`,(this.isDragging||this.isHoverOnResizeTrigger)&&`${t}-drawer__resize-trigger--hover`],onMouseenter:this.handleMouseenterResizeTrigger,onMouseleave:this.handleMouseleaveResizeTrigger,onMousedown:this.handleMousedownResizeTrigger}):null,this.nativeScrollbar?E(`div`,{class:[`${t}-drawer-content-wrapper`,this.contentClass],style:this.contentStyle,role:`none`},e):E(O,Object.assign({},this.scrollbarProps,{contentStyle:this.contentStyle,contentClass:[`${t}-drawer-content-wrapper`,this.contentClass],theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar}),e)]),this.bodyDirectives)})})),[[v,this.displayDirective===`if`||this.displayed||this.show]]):null}}),{cubicBezierEaseIn:ye,cubicBezierEaseOut:be}=M;function xe({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-bottom`}={}){return[V(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${ye}`}),V(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${be}`}),V(`&.${n}-transition-enter-to`,{transform:`translateY(0)`}),V(`&.${n}-transition-enter-from`,{transform:`translateY(100%)`}),V(`&.${n}-transition-leave-from`,{transform:`translateY(0)`}),V(`&.${n}-transition-leave-to`,{transform:`translateY(100%)`})]}var{cubicBezierEaseIn:Se,cubicBezierEaseOut:Ce}=M;function we({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-left`}={}){return[V(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${Se}`}),V(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${Ce}`}),V(`&.${n}-transition-enter-to`,{transform:`translateX(0)`}),V(`&.${n}-transition-enter-from`,{transform:`translateX(-100%)`}),V(`&.${n}-transition-leave-from`,{transform:`translateX(0)`}),V(`&.${n}-transition-leave-to`,{transform:`translateX(-100%)`})]}var{cubicBezierEaseIn:Te,cubicBezierEaseOut:Ee}=M;function De({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-right`}={}){return[V(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${Te}`}),V(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${Ee}`}),V(`&.${n}-transition-enter-to`,{transform:`translateX(0)`}),V(`&.${n}-transition-enter-from`,{transform:`translateX(100%)`}),V(`&.${n}-transition-leave-from`,{transform:`translateX(0)`}),V(`&.${n}-transition-leave-to`,{transform:`translateX(100%)`})]}var{cubicBezierEaseIn:$,cubicBezierEaseOut:Oe}=M;function ke({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-top`}={}){return[V(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${$}`}),V(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${Oe}`}),V(`&.${n}-transition-enter-to`,{transform:`translateY(0)`}),V(`&.${n}-transition-enter-from`,{transform:`translateY(-100%)`}),V(`&.${n}-transition-leave-from`,{transform:`translateY(0)`}),V(`&.${n}-transition-leave-to`,{transform:`translateY(-100%)`})]}var Ae=V([n(`drawer`,`
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
 `,[De(),we(),ke(),xe(),s(`unselectable`,`
 user-select: none; 
 -webkit-user-select: none;
 `),s(`native-scrollbar`,[n(`drawer-content-wrapper`,`
 overflow: auto;
 height: 100%;
 `)]),g(`resize-trigger`,`
 position: absolute;
 background-color: #0000;
 transition: background-color .3s var(--n-bezier);
 `,[s(`hover`,`
 background-color: var(--n-resize-trigger-color-hover);
 `)]),n(`drawer-content-wrapper`,`
 box-sizing: border-box;
 `),n(`drawer-content`,`
 height: 100%;
 display: flex;
 flex-direction: column;
 `,[s(`native-scrollbar`,[n(`drawer-body-content-wrapper`,`
 height: 100%;
 overflow: auto;
 `)]),n(`drawer-body`,`
 flex: 1 0 0;
 overflow: hidden;
 `),n(`drawer-body-content-wrapper`,`
 box-sizing: border-box;
 padding: var(--n-body-padding);
 `),n(`drawer-header`,`
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
 `,[g(`main`,`
 flex: 1;
 `),g(`close`,`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)]),n(`drawer-footer`,`
 display: flex;
 justify-content: flex-end;
 border-top: var(--n-footer-border-top);
 transition: border .3s var(--n-bezier);
 padding: var(--n-footer-padding);
 `)]),s(`right-placement`,`
 top: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-bottom-left-radius: var(--n-border-radius);
 `,[g(`resize-trigger`,`
 width: 3px;
 height: 100%;
 top: 0;
 left: 0;
 transform: translateX(-1.5px);
 cursor: ew-resize;
 `)]),s(`left-placement`,`
 top: 0;
 bottom: 0;
 left: 0;
 border-top-right-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[g(`resize-trigger`,`
 width: 3px;
 height: 100%;
 top: 0;
 right: 0;
 transform: translateX(1.5px);
 cursor: ew-resize;
 `)]),s(`top-placement`,`
 top: 0;
 left: 0;
 right: 0;
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[g(`resize-trigger`,`
 width: 100%;
 height: 3px;
 bottom: 0;
 left: 0;
 transform: translateY(1.5px);
 cursor: ns-resize;
 `)]),s(`bottom-placement`,`
 left: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-top-right-radius: var(--n-border-radius);
 `,[g(`resize-trigger`,`
 width: 100%;
 height: 3px;
 top: 0;
 left: 0;
 transform: translateY(-1.5px);
 cursor: ns-resize;
 `)])]),V(`body`,[V(`>`,[n(`drawer-container`,`
 position: fixed;
 `)])]),n(`drawer-container`,`
 position: relative;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 `,[V(`> *`,`
 pointer-events: all;
 `)]),n(`drawer-mask`,`
 background-color: rgba(0, 0, 0, .3);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `,[s(`invisible`,`
 background-color: rgba(0, 0, 0, 0)
 `),b({enterDuration:`0.2s`,leaveDuration:`0.2s`,enterCubicBezier:`var(--n-bezier-in)`,leaveCubicBezier:`var(--n-bezier-out)`})])]),je=Object.assign(Object.assign({},r.props),{show:Boolean,width:[Number,String],height:[Number,String],placement:{type:String,default:`right`},maskClosable:{type:Boolean,default:!0},showMask:{type:[Boolean,String],default:!0},to:[String,Object],displayDirective:{type:String,default:`if`},nativeScrollbar:{type:Boolean,default:!0},zIndex:Number,onMaskClick:Function,scrollbarProps:Object,contentClass:String,contentStyle:[Object,String],trapFocus:{type:Boolean,default:!0},onEsc:Function,autoFocus:{type:Boolean,default:!0},closeOnEsc:{type:Boolean,default:!0},blockScroll:{type:Boolean,default:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,defaultWidth:{type:[Number,String],default:251},defaultHeight:{type:[Number,String],default:251},onUpdateWidth:[Function,Array],onUpdateHeight:[Function,Array],"onUpdate:width":[Function,Array],"onUpdate:height":[Function,Array],"onUpdate:show":[Function,Array],onUpdateShow:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,drawerStyle:[String,Object],drawerClass:String,target:null,onShow:Function,onHide:Function}),Me=P({name:`Drawer`,inheritAttrs:!1,props:je,setup(e){let{mergedClsPrefixRef:t,namespaceRef:n,inlineThemeDisabled:i}=o(e),a=ce(),s=r(`Drawer`,`-drawer`,Ae,he,e,t),l=f(e.defaultWidth),u=f(e.defaultHeight),d=w(c(e,`width`),l),p=w(c(e,`height`),u),g=I(()=>{let{placement:t}=e;return t===`top`||t===`bottom`?``:_(d.value)}),v=I(()=>{let{placement:t}=e;return t===`left`||t===`right`?``:_(p.value)}),y=t=>{let{onUpdateWidth:n,"onUpdate:width":r}=e;n&&L(n,t),r&&L(r,t),l.value=t},b=t=>{let{onUpdateHeight:n,"onUpdate:width":r}=e;n&&L(n,t),r&&L(r,t),u.value=t},x=I(()=>[{width:g.value,height:v.value},e.drawerStyle||``]);function S(t){let{onMaskClick:n,maskClosable:r}=e;r&&D(!1),n&&n(t)}function C(e){S(e)}let T=ge();function E(t){var n;(n=e.onEsc)==null||n.call(e),e.show&&e.closeOnEsc&&pe(t)&&(T.value||D(!1))}function D(t){let{onHide:n,onUpdateShow:r,"onUpdate:show":i}=e;r&&L(r,t),i&&L(i,t),n&&!t&&L(n,t)}h(F,{isMountedRef:a,mergedThemeRef:s,mergedClsPrefixRef:t,doUpdateShow:D,doUpdateHeight:b,doUpdateWidth:y});let O=I(()=>{let{common:{cubicBezierEaseInOut:e,cubicBezierEaseIn:t,cubicBezierEaseOut:n},self:{color:r,textColor:i,boxShadow:a,lineHeight:o,headerPadding:c,footerPadding:l,borderRadius:u,bodyPadding:d,titleFontSize:f,titleTextColor:p,titleFontWeight:m,headerBorderBottom:h,footerBorderTop:g,closeIconColor:_,closeIconColorHover:v,closeIconColorPressed:y,closeColorHover:b,closeColorPressed:x,closeIconSize:S,closeSize:C,closeBorderRadius:w,resizableTriggerColorHover:T}}=s.value;return{"--n-line-height":o,"--n-color":r,"--n-border-radius":u,"--n-text-color":i,"--n-box-shadow":a,"--n-bezier":e,"--n-bezier-out":n,"--n-bezier-in":t,"--n-header-padding":c,"--n-body-padding":d,"--n-footer-padding":l,"--n-title-text-color":p,"--n-title-font-size":f,"--n-title-font-weight":m,"--n-header-border-bottom":h,"--n-footer-border-top":g,"--n-close-icon-color":_,"--n-close-icon-color-hover":v,"--n-close-icon-color-pressed":y,"--n-close-size":C,"--n-close-color-hover":b,"--n-close-color-pressed":x,"--n-close-icon-size":S,"--n-close-border-radius":w,"--n-resize-trigger-color-hover":T}}),k=i?m(`drawer`,void 0,O,e):void 0;return{mergedClsPrefix:t,namespace:n,mergedBodyStyle:x,handleOutsideClick:C,handleMaskClick:S,handleEsc:E,mergedTheme:s,cssVars:i?void 0:O,themeClass:k?.themeClass,onRender:k?.onRender,isMounted:a}},render(){let{mergedClsPrefix:e}=this;return E(ae,{to:this.to,show:this.show},{default:()=>{var t;return(t=this.onRender)==null||t.call(this),N(E(`div`,{class:[`${e}-drawer-container`,this.namespace,this.themeClass],style:this.cssVars,role:`none`},this.showMask?E(u,{name:`fade-in-transition`,appear:this.isMounted},{default:()=>this.show?E(`div`,{"aria-hidden":!0,class:[`${e}-drawer-mask`,this.showMask===`transparent`&&`${e}-drawer-mask--invisible`],onClick:this.handleMaskClick}):null}):null,E(ve,Object.assign({},this.$attrs,{class:[this.drawerClass,this.$attrs.class],style:[this.mergedBodyStyle,this.$attrs.style],blockScroll:this.blockScroll,contentStyle:this.contentStyle,contentClass:this.contentClass,placement:this.placement,scrollbarProps:this.scrollbarProps,show:this.show,displayDirective:this.displayDirective,nativeScrollbar:this.nativeScrollbar,onAfterEnter:this.onAfterEnter,onAfterLeave:this.onAfterLeave,trapFocus:this.trapFocus,autoFocus:this.autoFocus,resizable:this.resizable,maxHeight:this.maxHeight,minHeight:this.minHeight,maxWidth:this.maxWidth,minWidth:this.minWidth,showMask:this.showMask,onEsc:this.handleEsc,onClickoutside:this.handleOutsideClick}),this.$slots)),[[C,{zIndex:this.zIndex,enabled:this.show}]])}})}}),Ne=P({name:`DrawerContent`,props:{title:String,headerClass:String,headerStyle:[Object,String],footerClass:String,footerStyle:[Object,String],bodyClass:String,bodyStyle:[Object,String],bodyContentClass:String,bodyContentStyle:[Object,String],nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,closable:Boolean},slots:Object,setup(){let e=k(F,null);e||l(`drawer-content`,"`n-drawer-content` must be placed inside `n-drawer`.");let{doUpdateShow:t}=e;function n(){t(!1)}return{handleCloseClick:n,mergedTheme:e.mergedThemeRef,mergedClsPrefix:e.mergedClsPrefixRef}},render(){let{title:e,mergedClsPrefix:t,nativeScrollbar:n,mergedTheme:r,bodyClass:i,bodyStyle:a,bodyContentClass:o,bodyContentStyle:s,headerClass:c,headerStyle:l,footerClass:u,footerStyle:d,scrollbarProps:f,closable:p,$slots:m}=this;return E(`div`,{role:`none`,class:[`${t}-drawer-content`,n&&`${t}-drawer-content--native-scrollbar`]},m.header||e||p?E(`div`,{class:[`${t}-drawer-header`,c],style:l,role:`none`},E(`div`,{class:`${t}-drawer-header__main`,role:`heading`,"aria-level":`1`},m.header===void 0?e:m.header()),p&&E(oe,{onClick:this.handleCloseClick,clsPrefix:t,class:`${t}-drawer-header__close`,absolute:!0})):null,n?E(`div`,{class:[`${t}-drawer-body`,i],style:a,role:`none`},E(`div`,{class:[`${t}-drawer-body-content-wrapper`,o],style:s,role:`none`},m)):E(O,Object.assign({themeOverrides:r.peerOverrides.Scrollbar,theme:r.peers.Scrollbar},f,{class:`${t}-drawer-body`,contentClass:[`${t}-drawer-body-content-wrapper`,o],contentStyle:s}),m),m.footer?E(`div`,{class:[`${t}-drawer-footer`,u],style:d,role:`none`},m.footer()):null)}}),Pe={class:`page-text`},Fe=ie(P({__name:`PageDrawer`,props:{show:{type:Boolean},file:{default:``},page:{default:1},width:{default:740},ocrLabel:{default:`OCR 识别`}},emits:[`update:show`],setup(e,{emit:n}){let r=e,i=n,o=I({get:()=>r.show,set:e=>i(`update:show`,e)}),s=f(r.page),c=f(``),l=f(!1),u=f(!1),m=f(``);async function h(e,t){if(!(!e||t<1)){u.value=!0,m.value=``;try{let n=await fe(e,t);c.value=n.text||n.error||`(空)`,l.value=!!n.ocr}catch(e){c.value=``,m.value=`读取失败:${e.message}`}finally{u.value=!1}}}a(()=>[r.file,r.page],([,e])=>{s.value=e},{immediate:!0}),a(o,e=>{e&&(s.value=r.page,h(r.file,r.page))});function g(e){let t=s.value+e;t<1||(s.value=t,h(r.file,t))}return(n,r)=>(B(),j(d(Me),{show:o.value,"onUpdate:show":r[2]||=e=>o.value=e,width:e.width,placement:`right`},{default:p(()=>[e.file?(B(),j(d(Ne),{key:0,closable:``,title:`${e.file} 第${s.value}页`},{default:p(()=>[T(d(me),{class:`page-nav`,align:`center`},{default:p(()=>[T(d(H),{size:`small`,disabled:s.value<=1,loading:u.value,onClick:r[0]||=e=>g(-1)},{default:p(()=>[...r[3]||=[z(`上一页`,-1)]]),_:1},8,[`disabled`,`loading`]),R(`span`,null,`第 `+t(s.value)+` 页`,1),T(d(H),{size:`small`,loading:u.value,onClick:r[1]||=e=>g(1)},{default:p(()=>[...r[4]||=[z(`下一页`,-1)]]),_:1},8,[`loading`]),l.value?(B(),j(d(ue),{key:0,size:`small`,type:`warning`,round:``},{default:p(()=>[z(t(e.ocrLabel),1)]),_:1})):S(``,!0),T(d(H),{size:`small`,tag:`a`,href:d(de)(e.file,s.value),target:`_blank`},{default:p(()=>[...r[5]||=[z(`打开原文`,-1)]]),_:1},8,[`href`])]),_:1}),R(`pre`,Pe,t(m.value||c.value),1)]),_:1},8,[`title`])):S(``,!0)]),_:1},8,[`show`,`width`]))}}),[[`__scopeId`,`data-v-3d265eac`]]);export{Fe as t};
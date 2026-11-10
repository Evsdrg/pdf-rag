import{$ as e,$t as t,An as n,Bn as r,C as i,Ct as a,Gt as o,Ht as s,I as c,In as l,L as u,M as d,Mn as f,Rn as p,Sn as m,St as h,Tn as g,Un as _,Ut as v,Wt as y,X as b,Z as x,Zt as S,_t as C,an as w,bn as T,cn as E,ct as D,dn as O,et as k,fn as A,gn as j,gt as ee,hn as M,ht as te,it as N,j as P,jn as F,k as I,kn as L,ln as ne,lt as re,m as R,mn as z,mt as ie,on as B,sn as V,t as ae,un as H,wn as U,y as oe,yn as se,zn as W}from"./_plugin-vue_export-helper-BL3uulyl.js";import{A as ce,D as G,P as le,b as ue,y as de}from"./api-Dd-BvpDC.js";import{s as fe}from"./Select-C7VrnrHM.js";import{t as pe}from"./Space-CL86OYWq.js";import{a as me}from"./index-D0nxnmu2.js";var K=l(!1);function q(){K.value=!0}function J(){K.value=!1}var Y=0;function he(){return le&&(se(()=>{Y||(window.addEventListener(`compositionstart`,q),window.addEventListener(`compositionend`,J)),Y++}),T(()=>{Y<=1?(window.removeEventListener(`compositionstart`,q),window.removeEventListener(`compositionend`,J),Y=0):Y--})),K}var X=0,Z=``,Q=``,$=``,ge=``,_e=l(`0px`);function ve(e){if(typeof document>`u`)return;let t=document.documentElement,n,r=!1,i=()=>{t.style.marginRight=Z,t.style.overflow=Q,t.style.overflowX=$,t.style.overflowY=ge,_e.value=`0px`};m(()=>{n=L(e,e=>{if(e){if(!X){let e=window.innerWidth-t.offsetWidth;e>0&&(Z=t.style.marginRight,t.style.marginRight=`${e}px`,_e.value=`${e}px`),Q=t.style.overflow,$=t.style.overflowX,ge=t.style.overflowY,t.style.overflow=`hidden`,t.style.overflowX=`hidden`,t.style.overflowY=`hidden`}r=!0,X++}else X--,X||i(),r=!1},{immediate:!0})}),T(()=>{n?.(),r&&=(X--,X||i(),!1)})}var ye=A({name:`NDrawerContent`,inheritAttrs:!1,props:{blockScroll:Boolean,show:{type:Boolean,default:void 0},displayDirective:{type:String,required:!0},placement:{type:String,required:!0},contentClass:String,contentStyle:[Object,String],nativeScrollbar:{type:Boolean,required:!0},scrollbarProps:Object,trapFocus:{type:Boolean,default:!0},autoFocus:{type:Boolean,default:!0},showMask:{type:[Boolean,String],required:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,onClickoutside:Function,onAfterLeave:Function,onAfterEnter:Function,onEsc:Function},setup(e){let r=l(!!e.show),i=l(null),a=M(C),o=0,s=``,c=null,f=l(!1),p=l(!1),m=w(()=>e.placement===`top`||e.placement===`bottom`),{mergedClsPrefixRef:h,mergedRtlRef:_}=u(e),v=d(`Drawer`,_,h),y=j,b=e=>{p.value=!0,o=m.value?e.clientY:e.clientX,s=document.body.style.cursor,document.body.style.cursor=m.value?`ns-resize`:`ew-resize`,document.body.addEventListener(`mousemove`,A),document.body.addEventListener(`mouseleave`,y),document.body.addEventListener(`mouseup`,j)},x=()=>{c!==null&&(window.clearTimeout(c),c=null),p.value?f.value=!0:c=window.setTimeout(()=>{f.value=!0},300)},S=()=>{c!==null&&(window.clearTimeout(c),c=null),f.value=!1},{doUpdateHeight:E,doUpdateWidth:D}=a,O=t=>{let{maxWidth:n}=e;if(n&&t>n)return n;let{minWidth:r}=e;return r&&t<r?r:t},k=t=>{let{maxHeight:n}=e;if(n&&t>n)return n;let{minHeight:r}=e;return r&&t<r?r:t};function A(t){if(p.value)if(m.value){let n=i.value?.offsetHeight||0,r=o-t.clientY;n+=e.placement===`bottom`?r:-r,n=k(n),E(n),o=t.clientY}else{let n=i.value?.offsetWidth||0,r=o-t.clientX;n+=e.placement===`right`?r:-r,n=O(n),D(n),o=t.clientX}}function j(){p.value&&(o=0,p.value=!1,document.body.style.cursor=s,document.body.removeEventListener(`mousemove`,A),document.body.removeEventListener(`mouseup`,j),document.body.removeEventListener(`mouseleave`,y))}n(()=>{e.show&&(r.value=!0)}),L(()=>e.show,e=>{e||j()}),T(()=>{j()});let N=w(()=>{let{show:n}=e,r=[[t,n]];return e.showMask||r.push([re,e.onClickoutside,void 0,{capture:!0}]),r});function P(){var t;r.value=!1,(t=e.onAfterLeave)==null||t.call(e)}return ve(w(()=>e.blockScroll&&r.value)),g(ee,i),g(ie,null),g(te,null),{bodyRef:i,rtlEnabled:v,mergedClsPrefix:a.mergedClsPrefixRef,isMounted:a.isMountedRef,mergedTheme:a.mergedThemeRef,displayed:r,transitionName:w(()=>({right:`slide-in-from-right-transition`,left:`slide-in-from-left-transition`,top:`slide-in-from-top-transition`,bottom:`slide-in-from-bottom-transition`})[e.placement]),handleAfterLeave:P,bodyDirectives:N,handleMousedownResizeTrigger:b,handleMouseenterResizeTrigger:x,handleMouseleaveResizeTrigger:S,isDragging:p,isHoverOnResizeTrigger:f}},render(){let{$slots:e,mergedClsPrefix:n}=this;return this.displayDirective===`show`||this.displayed||this.show?f(z(`div`,{role:`none`},z(k,{disabled:!this.showMask||!this.trapFocus,active:this.show,autoFocus:this.autoFocus,onEsc:this.onEsc},{default:()=>z(S,{name:this.transitionName,appear:this.isMounted,onAfterEnter:this.onAfterEnter,onAfterLeave:this.handleAfterLeave},{default:()=>f(z(`div`,j(this.$attrs,{role:`dialog`,ref:`bodyRef`,"aria-modal":`true`,class:[`${n}-drawer`,this.rtlEnabled&&`${n}-drawer--rtl`,`${n}-drawer--${this.placement}-placement`,this.isDragging&&`${n}-drawer--unselectable`,this.nativeScrollbar&&`${n}-drawer--native-scrollbar`]}),[this.resizable?z(`div`,{class:[`${n}-drawer__resize-trigger`,(this.isDragging||this.isHoverOnResizeTrigger)&&`${n}-drawer__resize-trigger--hover`],onMouseenter:this.handleMouseenterResizeTrigger,onMouseleave:this.handleMouseleaveResizeTrigger,onMousedown:this.handleMousedownResizeTrigger}):null,this.nativeScrollbar?z(`div`,{class:[`${n}-drawer-content-wrapper`,this.contentClass],style:this.contentStyle,role:`none`},e):z(R,Object.assign({},this.scrollbarProps,{contentStyle:this.contentStyle,contentClass:[`${n}-drawer-content-wrapper`,this.contentClass],theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar}),e)]),this.bodyDirectives)})})),[[t,this.displayDirective===`if`||this.displayed||this.show]]):null}}),{cubicBezierEaseIn:be,cubicBezierEaseOut:xe}=P;function Se({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-bottom`}={}){return[s(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${be}`}),s(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${xe}`}),s(`&.${n}-transition-enter-to`,{transform:`translateY(0)`}),s(`&.${n}-transition-enter-from`,{transform:`translateY(100%)`}),s(`&.${n}-transition-leave-from`,{transform:`translateY(0)`}),s(`&.${n}-transition-leave-to`,{transform:`translateY(100%)`})]}var{cubicBezierEaseIn:Ce,cubicBezierEaseOut:we}=P;function Te({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-left`}={}){return[s(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${Ce}`}),s(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${we}`}),s(`&.${n}-transition-enter-to`,{transform:`translateX(0)`}),s(`&.${n}-transition-enter-from`,{transform:`translateX(-100%)`}),s(`&.${n}-transition-leave-from`,{transform:`translateX(0)`}),s(`&.${n}-transition-leave-to`,{transform:`translateX(-100%)`})]}var{cubicBezierEaseIn:Ee,cubicBezierEaseOut:De}=P;function Oe({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-right`}={}){return[s(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${Ee}`}),s(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${De}`}),s(`&.${n}-transition-enter-to`,{transform:`translateX(0)`}),s(`&.${n}-transition-enter-from`,{transform:`translateX(100%)`}),s(`&.${n}-transition-leave-from`,{transform:`translateX(0)`}),s(`&.${n}-transition-leave-to`,{transform:`translateX(100%)`})]}var{cubicBezierEaseIn:ke,cubicBezierEaseOut:Ae}=P;function je({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:n=`slide-in-from-top`}={}){return[s(`&.${n}-transition-leave-active`,{transition:`transform ${t} ${ke}`}),s(`&.${n}-transition-enter-active`,{transition:`transform ${e} ${Ae}`}),s(`&.${n}-transition-enter-to`,{transform:`translateY(0)`}),s(`&.${n}-transition-enter-from`,{transform:`translateY(-100%)`}),s(`&.${n}-transition-leave-from`,{transform:`translateY(0)`}),s(`&.${n}-transition-leave-to`,{transform:`translateY(-100%)`})]}var Me=s([v(`drawer`,`
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
 `,[Oe(),Te(),je(),Se(),o(`unselectable`,`
 user-select: none; 
 -webkit-user-select: none;
 `),o(`native-scrollbar`,[v(`drawer-content-wrapper`,`
 overflow: auto;
 height: 100%;
 `)]),y(`resize-trigger`,`
 position: absolute;
 background-color: #0000;
 transition: background-color .3s var(--n-bezier);
 `,[o(`hover`,`
 background-color: var(--n-resize-trigger-color-hover);
 `)]),v(`drawer-content-wrapper`,`
 box-sizing: border-box;
 `),v(`drawer-content`,`
 height: 100%;
 display: flex;
 flex-direction: column;
 `,[o(`native-scrollbar`,[v(`drawer-body-content-wrapper`,`
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
 `,[y(`main`,`
 flex: 1;
 `),y(`close`,`
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
 `)]),o(`right-placement`,`
 top: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-bottom-left-radius: var(--n-border-radius);
 `,[y(`resize-trigger`,`
 width: 3px;
 height: 100%;
 top: 0;
 left: 0;
 transform: translateX(-1.5px);
 cursor: ew-resize;
 `)]),o(`left-placement`,`
 top: 0;
 bottom: 0;
 left: 0;
 border-top-right-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[y(`resize-trigger`,`
 width: 3px;
 height: 100%;
 top: 0;
 right: 0;
 transform: translateX(1.5px);
 cursor: ew-resize;
 `)]),o(`top-placement`,`
 top: 0;
 left: 0;
 right: 0;
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[y(`resize-trigger`,`
 width: 100%;
 height: 3px;
 bottom: 0;
 left: 0;
 transform: translateY(1.5px);
 cursor: ns-resize;
 `)]),o(`bottom-placement`,`
 left: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-top-right-radius: var(--n-border-radius);
 `,[y(`resize-trigger`,`
 width: 100%;
 height: 3px;
 top: 0;
 left: 0;
 transform: translateY(-1.5px);
 cursor: ns-resize;
 `)])]),s(`body`,[s(`>`,[v(`drawer-container`,`
 position: fixed;
 `)])]),v(`drawer-container`,`
 position: relative;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 `,[s(`> *`,`
 pointer-events: all;
 `)]),v(`drawer-mask`,`
 background-color: rgba(0, 0, 0, .3);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `,[o(`invisible`,`
 background-color: rgba(0, 0, 0, 0)
 `),oe({enterDuration:`0.2s`,leaveDuration:`0.2s`,enterCubicBezier:`var(--n-bezier-in)`,leaveCubicBezier:`var(--n-bezier-out)`})])]),Ne=Object.assign(Object.assign({},I.props),{show:Boolean,width:[Number,String],height:[Number,String],placement:{type:String,default:`right`},maskClosable:{type:Boolean,default:!0},showMask:{type:[Boolean,String],default:!0},to:[String,Object],displayDirective:{type:String,default:`if`},nativeScrollbar:{type:Boolean,default:!0},zIndex:Number,onMaskClick:Function,scrollbarProps:Object,contentClass:String,contentStyle:[Object,String],trapFocus:{type:Boolean,default:!0},onEsc:Function,autoFocus:{type:Boolean,default:!0},closeOnEsc:{type:Boolean,default:!0},blockScroll:{type:Boolean,default:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,defaultWidth:{type:[Number,String],default:251},defaultHeight:{type:[Number,String],default:251},onUpdateWidth:[Function,Array],onUpdateHeight:[Function,Array],"onUpdate:width":[Function,Array],"onUpdate:height":[Function,Array],"onUpdate:show":[Function,Array],onUpdateShow:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,drawerStyle:[String,Object],drawerClass:String,target:null,onShow:Function,onHide:Function}),Pe=A({name:`Drawer`,inheritAttrs:!1,props:Ne,setup(t){let{mergedClsPrefixRef:n,namespaceRef:r,inlineThemeDisabled:i}=u(t),o=h(),s=I(`Drawer`,`-drawer`,Me,me,t,n),d=l(t.defaultWidth),f=l(t.defaultHeight),p=a(W(t,`width`),d),m=a(W(t,`height`),f),_=w(()=>{let{placement:n}=t;return n===`top`||n===`bottom`?``:e(p.value)}),v=w(()=>{let{placement:n}=t;return n===`left`||n===`right`?``:e(m.value)}),y=e=>{let{onUpdateWidth:n,"onUpdate:width":r}=t;n&&b(n,e),r&&b(r,e),d.value=e},x=e=>{let{onUpdateHeight:n,"onUpdate:width":r}=t;n&&b(n,e),r&&b(r,e),f.value=e},S=w(()=>[{width:_.value,height:v.value},t.drawerStyle||``]);function T(e){let{onMaskClick:n,maskClosable:r}=t;r&&k(!1),n&&n(e)}function E(e){T(e)}let D=he();function O(e){var n;(n=t.onEsc)==null||n.call(t),t.show&&t.closeOnEsc&&fe(e)&&(D.value||k(!1))}function k(e){let{onHide:n,onUpdateShow:r,"onUpdate:show":i}=t;r&&b(r,e),i&&b(i,e),n&&!e&&b(n,e)}g(C,{isMountedRef:o,mergedThemeRef:s,mergedClsPrefixRef:n,doUpdateShow:k,doUpdateHeight:x,doUpdateWidth:y});let A=w(()=>{let{common:{cubicBezierEaseInOut:e,cubicBezierEaseIn:t,cubicBezierEaseOut:n},self:{color:r,textColor:i,boxShadow:a,lineHeight:o,headerPadding:c,footerPadding:l,borderRadius:u,bodyPadding:d,titleFontSize:f,titleTextColor:p,titleFontWeight:m,headerBorderBottom:h,footerBorderTop:g,closeIconColor:_,closeIconColorHover:v,closeIconColorPressed:y,closeColorHover:b,closeColorPressed:x,closeIconSize:S,closeSize:C,closeBorderRadius:w,resizableTriggerColorHover:T}}=s.value;return{"--n-line-height":o,"--n-color":r,"--n-border-radius":u,"--n-text-color":i,"--n-box-shadow":a,"--n-bezier":e,"--n-bezier-out":n,"--n-bezier-in":t,"--n-header-padding":c,"--n-body-padding":d,"--n-footer-padding":l,"--n-title-text-color":p,"--n-title-font-size":f,"--n-title-font-weight":m,"--n-header-border-bottom":h,"--n-footer-border-top":g,"--n-close-icon-color":_,"--n-close-icon-color-hover":v,"--n-close-icon-color-pressed":y,"--n-close-size":C,"--n-close-color-hover":b,"--n-close-color-pressed":x,"--n-close-icon-size":S,"--n-close-border-radius":w,"--n-resize-trigger-color-hover":T}}),j=i?c(`drawer`,void 0,A,t):void 0;return{mergedClsPrefix:n,namespace:r,mergedBodyStyle:S,handleOutsideClick:E,handleMaskClick:T,handleEsc:O,mergedTheme:s,cssVars:i?void 0:A,themeClass:j?.themeClass,onRender:j?.onRender,isMounted:o}},render(){let{mergedClsPrefix:e}=this;return z(N,{to:this.to,show:this.show},{default:()=>{var t;return(t=this.onRender)==null||t.call(this),f(z(`div`,{class:[`${e}-drawer-container`,this.namespace,this.themeClass],style:this.cssVars,role:`none`},this.showMask?z(S,{name:`fade-in-transition`,appear:this.isMounted},{default:()=>this.show?z(`div`,{"aria-hidden":!0,class:[`${e}-drawer-mask`,this.showMask===`transparent`&&`${e}-drawer-mask--invisible`],onClick:this.handleMaskClick}):null}):null,z(ye,Object.assign({},this.$attrs,{class:[this.drawerClass,this.$attrs.class],style:[this.mergedBodyStyle,this.$attrs.style],blockScroll:this.blockScroll,contentStyle:this.contentStyle,contentClass:this.contentClass,placement:this.placement,scrollbarProps:this.scrollbarProps,show:this.show,displayDirective:this.displayDirective,nativeScrollbar:this.nativeScrollbar,onAfterEnter:this.onAfterEnter,onAfterLeave:this.onAfterLeave,trapFocus:this.trapFocus,autoFocus:this.autoFocus,resizable:this.resizable,maxHeight:this.maxHeight,minHeight:this.minHeight,maxWidth:this.maxWidth,minWidth:this.minWidth,showMask:this.showMask,onEsc:this.handleEsc,onClickoutside:this.handleOutsideClick}),this.$slots)),[[D,{zIndex:this.zIndex,enabled:this.show}]])}})}}),Fe=A({name:`DrawerContent`,props:{title:String,headerClass:String,headerStyle:[Object,String],footerClass:String,footerStyle:[Object,String],bodyClass:String,bodyStyle:[Object,String],bodyContentClass:String,bodyContentStyle:[Object,String],nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,closable:Boolean},slots:Object,setup(){let e=M(C,null);e||x(`drawer-content`,"`n-drawer-content` must be placed inside `n-drawer`.");let{doUpdateShow:t}=e;function n(){t(!1)}return{handleCloseClick:n,mergedTheme:e.mergedThemeRef,mergedClsPrefix:e.mergedClsPrefixRef}},render(){let{title:e,mergedClsPrefix:t,nativeScrollbar:n,mergedTheme:r,bodyClass:a,bodyStyle:o,bodyContentClass:s,bodyContentStyle:c,headerClass:l,headerStyle:u,footerClass:d,footerStyle:f,scrollbarProps:p,closable:m,$slots:h}=this;return z(`div`,{role:`none`,class:[`${t}-drawer-content`,n&&`${t}-drawer-content--native-scrollbar`]},h.header||e||m?z(`div`,{class:[`${t}-drawer-header`,l],style:u,role:`none`},z(`div`,{class:`${t}-drawer-header__main`,role:`heading`,"aria-level":`1`},h.header===void 0?e:h.header()),m&&z(i,{onClick:this.handleCloseClick,clsPrefix:t,class:`${t}-drawer-header__close`,absolute:!0})):null,n?z(`div`,{class:[`${t}-drawer-body`,a],style:o,role:`none`},z(`div`,{class:[`${t}-drawer-body-content-wrapper`,s],style:c,role:`none`},h)):z(R,Object.assign({themeOverrides:r.peerOverrides.Scrollbar,theme:r.peers.Scrollbar},p,{class:`${t}-drawer-body`,contentClass:[`${t}-drawer-body-content-wrapper`,s],contentStyle:c}),h),h.footer?z(`div`,{class:[`${t}-drawer-footer`,d],style:f,role:`none`},h.footer()):null)}}),Ie={key:0,class:`page-warning`,role:`status`},Le={class:`page-text`},Re=ae(A({__name:`PageDrawer`,props:{show:{type:Boolean},file:{default:``},page:{default:1},width:{default:740},ocrLabel:{default:`OCR 识别`}},emits:[`update:show`],setup(e,{emit:t}){let n=e,i=t,a=w({get:()=>n.show,set:e=>i(`update:show`,e)}),o=p(n.page),s=p(``),c=p(!1),l=p(!1),u=p(``),d=p(``),f=p(null),m=p(0),h=null;async function g(e,t,n=!1){if(!e||t<1)return;h?.abort();let r=new AbortController;h=r,l.value=!0,u.value=``,n||(s.value=``,d.value=``,f.value=null);try{let i=await ue(e,t,r.signal,n?f.value??``:``);if(h!==r)return;s.value=n?s.value+i.text:i.text||`(空)`,c.value=i.ocr,d.value=i.warnings.map(e=>e.message).join(`；`),m.value=i.total_pages,f.value=i.next_cursor}catch(e){e.name!==`AbortError`&&(u.value=`读取失败:${e.message}`)}finally{h===r&&(l.value=!1,h=null)}}L(()=>[n.file,n.page],([,e])=>{o.value=e},{immediate:!0}),L(a,e=>{e?(o.value=n.page,g(n.file,n.page)):(h?.abort(),h=null,l.value=!1)});function v(e){let t=o.value+e;t<1||(o.value=t,g(n.file,t))}return(t,n)=>(U(),V(r(Pe),{show:a.value,"onUpdate:show":n[3]||=e=>a.value=e,width:e.width,placement:`right`},{default:F(()=>[e.file?(U(),V(r(Fe),{key:0,closable:``,title:`${e.file} 第${o.value}页`},{default:F(()=>[O(r(pe),{class:`page-nav`,align:`center`},{default:F(()=>[O(r(G),{size:`small`,disabled:o.value<=1,loading:l.value,onClick:n[0]||=e=>v(-1)},{default:F(()=>[...n[4]||=[H(`上一页`,-1)]]),_:1},8,[`disabled`,`loading`]),B(`span`,null,`第 `+_(o.value)+` 页`,1),O(r(G),{size:`small`,disabled:l.value||m.value>0&&o.value>=m.value,loading:l.value,onClick:n[1]||=e=>v(1)},{default:F(()=>[...n[5]||=[H(`下一页`,-1)]]),_:1},8,[`disabled`,`loading`]),c.value?(U(),V(r(ce),{key:0,size:`small`,type:`warning`,round:``},{default:F(()=>[H(_(e.ocrLabel),1)]),_:1})):E(``,!0),O(r(G),{size:`small`,tag:`a`,href:r(de)(e.file,o.value),target:`_blank`},{default:F(()=>[...n[6]||=[H(`打开原文`,-1)]]),_:1},8,[`href`])]),_:1}),d.value?(U(),ne(`p`,Ie,_(d.value),1)):E(``,!0),B(`pre`,Le,_(u.value||s.value),1),f.value?(U(),V(r(G),{key:1,size:`small`,loading:l.value,onClick:n[2]||=t=>g(e.file,o.value,!0)},{default:F(()=>[...n[7]||=[H(`继续读取本页`,-1)]]),_:1},8,[`loading`])):E(``,!0)]),_:1},8,[`title`])):E(``,!0)]),_:1},8,[`show`,`width`]))}}),[[`__scopeId`,`data-v-af7e76ab`]]);export{Re as t};
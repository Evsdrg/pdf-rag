import{A as e,An as t,Bt as n,Cn as r,D as i,Dn as a,F as o,Ht as s,In as c,J as l,Ln as u,On as d,P as f,Pn as p,Q as m,Rn as h,Sn as g,Ut as _,Vn as v,Vt as y,Y as b,Yt as x,Z as S,Zt as C,_ as w,_n as T,an as E,bn as D,bt as O,cn as k,f as A,fn as j,ft as ee,ht as M,in as N,k as P,kn as F,ln as I,mn as te,mt as ne,nt as re,on as L,ot as ie,pn as R,pt as ae,rn as z,sn as oe,st as se,t as ce,un as B,vn as V,x as le,xt as H}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{E as U,M as ue,k as de,v as fe,y as pe}from"./api-DSM5Qrv-.js";import{c as me}from"./Select-DjbSdqLG.js";import{t as he}from"./Space-DX9mpeUo.js";import{a as ge}from"./index-BMjX8OfM.js";var W=p(!1);function G(){W.value=!0}function K(){W.value=!1}var q=0;function _e(){return ue&&(T(()=>{q||(window.addEventListener(`compositionstart`,G),window.addEventListener(`compositionend`,K)),q++}),V(()=>{q<=1?(window.removeEventListener(`compositionstart`,G),window.removeEventListener(`compositionend`,K),q=0):q--})),W}var J=0,Y=``,X=``,Z=``,Q=``,$=p(`0px`);function ve(e){if(typeof document>`u`)return;let t=document.documentElement,n,r=!1,i=()=>{t.style.marginRight=Y,t.style.overflow=X,t.style.overflowX=Z,t.style.overflowY=Q,$.value=`0px`};D(()=>{n=a(e,e=>{if(e){if(!J){let e=window.innerWidth-t.offsetWidth;e>0&&(Y=t.style.marginRight,t.style.marginRight=`${e}px`,$.value=`${e}px`),X=t.style.overflow,Z=t.style.overflowX,Q=t.style.overflowY,t.style.overflow=`hidden`,t.style.overflowX=`hidden`,t.style.overflowY=`hidden`}r=!0,J++}else J--,J||i(),r=!1},{immediate:!0})}),V(()=>{n?.(),r&&=(J--,J||i(),!1)})}var ye=B({name:`NDrawerContent`,inheritAttrs:!1,props:{blockScroll:Boolean,show:{type:Boolean,default:void 0},displayDirective:{type:String,required:!0},placement:{type:String,required:!0},contentClass:String,contentStyle:[Object,String],nativeScrollbar:{type:Boolean,required:!0},scrollbarProps:Object,trapFocus:{type:Boolean,default:!0},autoFocus:{type:Boolean,default:!0},showMask:{type:[Boolean,String],required:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,onClickoutside:Function,onAfterLeave:Function,onAfterEnter:Function,onEsc:Function},setup(t){let n=p(!!t.show),i=p(null),s=R(M),c=0,l=``,u=null,f=p(!1),m=p(!1),h=z(()=>t.placement===`top`||t.placement===`bottom`),{mergedClsPrefixRef:g,mergedRtlRef:_}=o(t),v=e(`Drawer`,_,g),y=k,b=e=>{m.value=!0,c=h.value?e.clientY:e.clientX,l=document.body.style.cursor,document.body.style.cursor=h.value?`ns-resize`:`ew-resize`,document.body.addEventListener(`mousemove`,O),document.body.addEventListener(`mouseleave`,y),document.body.addEventListener(`mouseup`,k)},x=()=>{u!==null&&(window.clearTimeout(u),u=null),m.value?f.value=!0:u=window.setTimeout(()=>{f.value=!0},300)},S=()=>{u!==null&&(window.clearTimeout(u),u=null),f.value=!1},{doUpdateHeight:w,doUpdateWidth:T}=s,E=e=>{let{maxWidth:n}=t;if(n&&e>n)return n;let{minWidth:r}=t;return r&&e<r?r:e},D=e=>{let{maxHeight:n}=t;if(n&&e>n)return n;let{minHeight:r}=t;return r&&e<r?r:e};function O(e){if(m.value)if(h.value){let n=i.value?.offsetHeight||0,r=c-e.clientY;n+=t.placement===`bottom`?r:-r,n=D(n),w(n),c=e.clientY}else{let n=i.value?.offsetWidth||0,r=c-e.clientX;n+=t.placement===`right`?r:-r,n=E(n),T(n),c=e.clientX}}function k(){m.value&&(c=0,m.value=!1,document.body.style.cursor=l,document.body.removeEventListener(`mousemove`,O),document.body.removeEventListener(`mouseup`,k),document.body.removeEventListener(`mouseleave`,y))}d(()=>{t.show&&(n.value=!0)}),a(()=>t.show,e=>{e||k()}),V(()=>{k()});let A=z(()=>{let{show:e}=t,n=[[C,e]];return t.showMask||n.push([se,t.onClickoutside,void 0,{capture:!0}]),n});function j(){var e;n.value=!1,(e=t.onAfterLeave)==null||e.call(t)}return ve(z(()=>t.blockScroll&&n.value)),r(ne,i),r(ee,null),r(ae,null),{bodyRef:i,rtlEnabled:v,mergedClsPrefix:s.mergedClsPrefixRef,isMounted:s.isMountedRef,mergedTheme:s.mergedThemeRef,displayed:n,transitionName:z(()=>({right:`slide-in-from-right-transition`,left:`slide-in-from-left-transition`,top:`slide-in-from-top-transition`,bottom:`slide-in-from-bottom-transition`})[t.placement]),handleAfterLeave:j,bodyDirectives:A,handleMousedownResizeTrigger:b,handleMouseenterResizeTrigger:x,handleMouseleaveResizeTrigger:S,isDragging:m,isHoverOnResizeTrigger:f}},render(){let{$slots:e,mergedClsPrefix:n}=this;return this.displayDirective===`show`||this.displayed||this.show?t(j(`div`,{role:`none`},j(m,{disabled:!this.showMask||!this.trapFocus,active:this.show,autoFocus:this.autoFocus,onEsc:this.onEsc},{default:()=>j(x,{name:this.transitionName,appear:this.isMounted,onAfterEnter:this.onAfterEnter,onAfterLeave:this.handleAfterLeave},{default:()=>t(j(`div`,te(this.$attrs,{role:`dialog`,ref:`bodyRef`,"aria-modal":`true`,class:[`${n}-drawer`,this.rtlEnabled&&`${n}-drawer--rtl`,`${n}-drawer--${this.placement}-placement`,this.isDragging&&`${n}-drawer--unselectable`,this.nativeScrollbar&&`${n}-drawer--native-scrollbar`]}),[this.resizable?j(`div`,{class:[`${n}-drawer__resize-trigger`,(this.isDragging||this.isHoverOnResizeTrigger)&&`${n}-drawer__resize-trigger--hover`],onMouseenter:this.handleMouseenterResizeTrigger,onMouseleave:this.handleMouseleaveResizeTrigger,onMousedown:this.handleMousedownResizeTrigger}):null,this.nativeScrollbar?j(`div`,{class:[`${n}-drawer-content-wrapper`,this.contentClass],style:this.contentStyle,role:`none`},e):j(A,Object.assign({},this.scrollbarProps,{contentStyle:this.contentStyle,contentClass:[`${n}-drawer-content-wrapper`,this.contentClass],theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar}),e)]),this.bodyDirectives)})})),[[C,this.displayDirective===`if`||this.displayed||this.show]]):null}}),{cubicBezierEaseIn:be,cubicBezierEaseOut:xe}=P;function Se({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-bottom`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${be}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${xe}`}),n(`&.${r}-transition-enter-to`,{transform:`translateY(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateY(100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateY(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateY(100%)`})]}var{cubicBezierEaseIn:Ce,cubicBezierEaseOut:we}=P;function Te({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-left`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${Ce}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${we}`}),n(`&.${r}-transition-enter-to`,{transform:`translateX(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateX(-100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateX(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateX(-100%)`})]}var{cubicBezierEaseIn:Ee,cubicBezierEaseOut:De}=P;function Oe({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-right`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${Ee}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${De}`}),n(`&.${r}-transition-enter-to`,{transform:`translateX(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateX(100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateX(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateX(100%)`})]}var{cubicBezierEaseIn:ke,cubicBezierEaseOut:Ae}=P;function je({duration:e=`0.3s`,leaveDuration:t=`0.2s`,name:r=`slide-in-from-top`}={}){return[n(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${ke}`}),n(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${Ae}`}),n(`&.${r}-transition-enter-to`,{transform:`translateY(0)`}),n(`&.${r}-transition-enter-from`,{transform:`translateY(-100%)`}),n(`&.${r}-transition-leave-from`,{transform:`translateY(0)`}),n(`&.${r}-transition-leave-to`,{transform:`translateY(-100%)`})]}var Me=n([y(`drawer`,`
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
 `,[Oe(),Te(),je(),Se(),_(`unselectable`,`
 user-select: none; 
 -webkit-user-select: none;
 `),_(`native-scrollbar`,[y(`drawer-content-wrapper`,`
 overflow: auto;
 height: 100%;
 `)]),s(`resize-trigger`,`
 position: absolute;
 background-color: #0000;
 transition: background-color .3s var(--n-bezier);
 `,[_(`hover`,`
 background-color: var(--n-resize-trigger-color-hover);
 `)]),y(`drawer-content-wrapper`,`
 box-sizing: border-box;
 `),y(`drawer-content`,`
 height: 100%;
 display: flex;
 flex-direction: column;
 `,[_(`native-scrollbar`,[y(`drawer-body-content-wrapper`,`
 height: 100%;
 overflow: auto;
 `)]),y(`drawer-body`,`
 flex: 1 0 0;
 overflow: hidden;
 `),y(`drawer-body-content-wrapper`,`
 box-sizing: border-box;
 padding: var(--n-body-padding);
 `),y(`drawer-header`,`
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
 `)]),y(`drawer-footer`,`
 display: flex;
 justify-content: flex-end;
 border-top: var(--n-footer-border-top);
 transition: border .3s var(--n-bezier);
 padding: var(--n-footer-padding);
 `)]),_(`right-placement`,`
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
 `)]),_(`left-placement`,`
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
 `)]),_(`top-placement`,`
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
 `)]),_(`bottom-placement`,`
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
 `)])]),n(`body`,[n(`>`,[y(`drawer-container`,`
 position: fixed;
 `)])]),y(`drawer-container`,`
 position: relative;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 `,[n(`> *`,`
 pointer-events: all;
 `)]),y(`drawer-mask`,`
 background-color: rgba(0, 0, 0, .3);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `,[_(`invisible`,`
 background-color: rgba(0, 0, 0, 0)
 `),w({enterDuration:`0.2s`,leaveDuration:`0.2s`,enterCubicBezier:`var(--n-bezier-in)`,leaveCubicBezier:`var(--n-bezier-out)`})])]),Ne=Object.assign(Object.assign({},i.props),{show:Boolean,width:[Number,String],height:[Number,String],placement:{type:String,default:`right`},maskClosable:{type:Boolean,default:!0},showMask:{type:[Boolean,String],default:!0},to:[String,Object],displayDirective:{type:String,default:`if`},nativeScrollbar:{type:Boolean,default:!0},zIndex:Number,onMaskClick:Function,scrollbarProps:Object,contentClass:String,contentStyle:[Object,String],trapFocus:{type:Boolean,default:!0},onEsc:Function,autoFocus:{type:Boolean,default:!0},closeOnEsc:{type:Boolean,default:!0},blockScroll:{type:Boolean,default:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,defaultWidth:{type:[Number,String],default:251},defaultHeight:{type:[Number,String],default:251},onUpdateWidth:[Function,Array],onUpdateHeight:[Function,Array],"onUpdate:width":[Function,Array],"onUpdate:height":[Function,Array],"onUpdate:show":[Function,Array],onUpdateShow:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,drawerStyle:[String,Object],drawerClass:String,target:null,onShow:Function,onHide:Function}),Pe=B({name:`Drawer`,inheritAttrs:!1,props:Ne,setup(e){let{mergedClsPrefixRef:t,namespaceRef:n,inlineThemeDisabled:a}=o(e),s=O(),c=i(`Drawer`,`-drawer`,Me,ge,e,t),d=p(e.defaultWidth),m=p(e.defaultHeight),h=H(u(e,`width`),d),g=H(u(e,`height`),m),_=z(()=>{let{placement:t}=e;return t===`top`||t===`bottom`?``:S(h.value)}),v=z(()=>{let{placement:t}=e;return t===`left`||t===`right`?``:S(g.value)}),y=t=>{let{onUpdateWidth:n,"onUpdate:width":r}=e;n&&l(n,t),r&&l(r,t),d.value=t},b=t=>{let{onUpdateHeight:n,"onUpdate:width":r}=e;n&&l(n,t),r&&l(r,t),m.value=t},x=z(()=>[{width:_.value,height:v.value},e.drawerStyle||``]);function C(t){let{onMaskClick:n,maskClosable:r}=e;r&&D(!1),n&&n(t)}function w(e){C(e)}let T=_e();function E(t){var n;(n=e.onEsc)==null||n.call(e),e.show&&e.closeOnEsc&&me(t)&&(T.value||D(!1))}function D(t){let{onHide:n,onUpdateShow:r,"onUpdate:show":i}=e;r&&l(r,t),i&&l(i,t),n&&!t&&l(n,t)}r(M,{isMountedRef:s,mergedThemeRef:c,mergedClsPrefixRef:t,doUpdateShow:D,doUpdateHeight:b,doUpdateWidth:y});let k=z(()=>{let{common:{cubicBezierEaseInOut:e,cubicBezierEaseIn:t,cubicBezierEaseOut:n},self:{color:r,textColor:i,boxShadow:a,lineHeight:o,headerPadding:s,footerPadding:l,borderRadius:u,bodyPadding:d,titleFontSize:f,titleTextColor:p,titleFontWeight:m,headerBorderBottom:h,footerBorderTop:g,closeIconColor:_,closeIconColorHover:v,closeIconColorPressed:y,closeColorHover:b,closeColorPressed:x,closeIconSize:S,closeSize:C,closeBorderRadius:w,resizableTriggerColorHover:T}}=c.value;return{"--n-line-height":o,"--n-color":r,"--n-border-radius":u,"--n-text-color":i,"--n-box-shadow":a,"--n-bezier":e,"--n-bezier-out":n,"--n-bezier-in":t,"--n-header-padding":s,"--n-body-padding":d,"--n-footer-padding":l,"--n-title-text-color":p,"--n-title-font-size":f,"--n-title-font-weight":m,"--n-header-border-bottom":h,"--n-footer-border-top":g,"--n-close-icon-color":_,"--n-close-icon-color-hover":v,"--n-close-icon-color-pressed":y,"--n-close-size":C,"--n-close-color-hover":b,"--n-close-color-pressed":x,"--n-close-icon-size":S,"--n-close-border-radius":w,"--n-resize-trigger-color-hover":T}}),A=a?f(`drawer`,void 0,k,e):void 0;return{mergedClsPrefix:t,namespace:n,mergedBodyStyle:x,handleOutsideClick:w,handleMaskClick:C,handleEsc:E,mergedTheme:c,cssVars:a?void 0:k,themeClass:A?.themeClass,onRender:A?.onRender,isMounted:s}},render(){let{mergedClsPrefix:e}=this;return j(re,{to:this.to,show:this.show},{default:()=>{var n;return(n=this.onRender)==null||n.call(this),t(j(`div`,{class:[`${e}-drawer-container`,this.namespace,this.themeClass],style:this.cssVars,role:`none`},this.showMask?j(x,{name:`fade-in-transition`,appear:this.isMounted},{default:()=>this.show?j(`div`,{"aria-hidden":!0,class:[`${e}-drawer-mask`,this.showMask===`transparent`&&`${e}-drawer-mask--invisible`],onClick:this.handleMaskClick}):null}):null,j(ye,Object.assign({},this.$attrs,{class:[this.drawerClass,this.$attrs.class],style:[this.mergedBodyStyle,this.$attrs.style],blockScroll:this.blockScroll,contentStyle:this.contentStyle,contentClass:this.contentClass,placement:this.placement,scrollbarProps:this.scrollbarProps,show:this.show,displayDirective:this.displayDirective,nativeScrollbar:this.nativeScrollbar,onAfterEnter:this.onAfterEnter,onAfterLeave:this.onAfterLeave,trapFocus:this.trapFocus,autoFocus:this.autoFocus,resizable:this.resizable,maxHeight:this.maxHeight,minHeight:this.minHeight,maxWidth:this.maxWidth,minWidth:this.minWidth,showMask:this.showMask,onEsc:this.handleEsc,onClickoutside:this.handleOutsideClick}),this.$slots)),[[ie,{zIndex:this.zIndex,enabled:this.show}]])}})}}),Fe=B({name:`DrawerContent`,props:{title:String,headerClass:String,headerStyle:[Object,String],footerClass:String,footerStyle:[Object,String],bodyClass:String,bodyStyle:[Object,String],bodyContentClass:String,bodyContentStyle:[Object,String],nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,closable:Boolean},slots:Object,setup(){let e=R(M,null);e||b(`drawer-content`,"`n-drawer-content` must be placed inside `n-drawer`.");let{doUpdateShow:t}=e;function n(){t(!1)}return{handleCloseClick:n,mergedTheme:e.mergedThemeRef,mergedClsPrefix:e.mergedClsPrefixRef}},render(){let{title:e,mergedClsPrefix:t,nativeScrollbar:n,mergedTheme:r,bodyClass:i,bodyStyle:a,bodyContentClass:o,bodyContentStyle:s,headerClass:c,headerStyle:l,footerClass:u,footerStyle:d,scrollbarProps:f,closable:p,$slots:m}=this;return j(`div`,{role:`none`,class:[`${t}-drawer-content`,n&&`${t}-drawer-content--native-scrollbar`]},m.header||e||p?j(`div`,{class:[`${t}-drawer-header`,c],style:l,role:`none`},j(`div`,{class:`${t}-drawer-header__main`,role:`heading`,"aria-level":`1`},m.header===void 0?e:m.header()),p&&j(le,{onClick:this.handleCloseClick,clsPrefix:t,class:`${t}-drawer-header__close`,absolute:!0})):null,n?j(`div`,{class:[`${t}-drawer-body`,i],style:a,role:`none`},j(`div`,{class:[`${t}-drawer-body-content-wrapper`,o],style:s,role:`none`},m)):j(A,Object.assign({themeOverrides:r.peerOverrides.Scrollbar,theme:r.peers.Scrollbar},f,{class:`${t}-drawer-body`,contentClass:[`${t}-drawer-body-content-wrapper`,o],contentStyle:s}),m),m.footer?j(`div`,{class:[`${t}-drawer-footer`,u],style:d,role:`none`},m.footer()):null)}}),Ie={key:0,class:`page-warning`,role:`status`},Le={class:`page-text`},Re=ce(B({__name:`PageDrawer`,props:{show:{type:Boolean},file:{default:``},page:{default:1},width:{default:740},ocrLabel:{default:`OCR 识别`}},emits:[`update:show`],setup(e,{emit:t}){let n=e,r=t,i=z({get:()=>n.show,set:e=>r(`update:show`,e)}),o=c(n.page),s=c(``),l=c(!1),u=c(!1),d=c(``),f=c(``),p=c(null),m=c(0),_=null;async function y(e,t,n=!1){if(!e||t<1)return;_?.abort();let r=new AbortController;_=r,u.value=!0,d.value=``,n||(s.value=``,f.value=``,p.value=null);try{let i=await pe(e,t,r.signal,n?p.value??``:``);if(_!==r)return;s.value=n?s.value+i.text:i.text||`(空)`,l.value=i.ocr,f.value=i.warnings.map(e=>e.message).join(`；`),m.value=i.total_pages,p.value=i.next_cursor}catch(e){e.name!==`AbortError`&&(d.value=`读取失败:${e.message}`)}finally{_===r&&(u.value=!1,_=null)}}a(()=>[n.file,n.page],([,e])=>{o.value=e},{immediate:!0}),a(i,e=>{e?(o.value=n.page,y(n.file,n.page)):(_?.abort(),_=null,u.value=!1)});function b(e){let t=o.value+e;t<1||(o.value=t,y(n.file,t))}return(t,n)=>(g(),E(h(Pe),{show:i.value,"onUpdate:show":n[3]||=e=>i.value=e,width:e.width,placement:`right`},{default:F(()=>[e.file?(g(),E(h(Fe),{key:0,closable:``,title:`${e.file} 第${o.value}页`},{default:F(()=>[I(h(he),{class:`page-nav`,align:`center`},{default:F(()=>[I(h(U),{size:`small`,disabled:o.value<=1,loading:u.value,onClick:n[0]||=e=>b(-1)},{default:F(()=>[...n[4]||=[k(`上一页`,-1)]]),_:1},8,[`disabled`,`loading`]),N(`span`,null,`第 `+v(o.value)+` 页`,1),I(h(U),{size:`small`,disabled:u.value||m.value>0&&o.value>=m.value,loading:u.value,onClick:n[1]||=e=>b(1)},{default:F(()=>[...n[5]||=[k(`下一页`,-1)]]),_:1},8,[`disabled`,`loading`]),l.value?(g(),E(h(de),{key:0,size:`small`,type:`warning`,round:``},{default:F(()=>[k(v(e.ocrLabel),1)]),_:1})):L(``,!0),I(h(U),{size:`small`,tag:`a`,href:h(fe)(e.file,o.value),target:`_blank`},{default:F(()=>[...n[6]||=[k(`打开原文`,-1)]]),_:1},8,[`href`])]),_:1}),f.value?(g(),oe(`p`,Ie,v(f.value),1)):L(``,!0),N(`pre`,Le,v(d.value||s.value),1),p.value?(g(),E(h(U),{key:1,size:`small`,loading:u.value,onClick:n[2]||=t=>y(e.file,o.value,!0)},{default:F(()=>[...n[7]||=[k(`继续读取本页`,-1)]]),_:1},8,[`loading`])):L(``,!0)]),_:1},8,[`title`])):L(``,!0)]),_:1},8,[`show`,`width`]))}}),[[`__scopeId`,`data-v-af7e76ab`]]);export{Re as t};
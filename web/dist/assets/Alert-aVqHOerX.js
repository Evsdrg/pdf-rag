import{A as e,At as t,Bt as n,D as r,F as i,Ft as a,Gt as o,Ht as s,P as c,Pn as l,T as u,U as d,Ut as f,V as p,Vt as m,b as h,fn as g,g as _,kt as v,mn as y,rn as b,un as x,x as S}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{A as C,O as w,b as T,j as E,k as D,x as O}from"./index-BMjX8OfM.js";function k(e){let{lineHeight:n,borderRadius:r,fontWeightStrong:i,baseColor:a,dividerColor:o,actionColor:s,textColor1:c,textColor2:l,closeColorHover:u,closeColorPressed:d,closeIconColor:f,closeIconColorHover:p,closeIconColorPressed:m,infoColor:h,successColor:g,warningColor:_,errorColor:y,fontSize:b}=e;return Object.assign(Object.assign({},O),{fontSize:b,lineHeight:n,titleFontWeight:i,borderRadius:r,border:`1px solid ${o}`,color:s,titleTextColor:c,iconColor:l,contentTextColor:l,closeBorderRadius:r,closeColorHover:u,closeColorPressed:d,closeIconColor:f,closeIconColorHover:p,closeIconColorPressed:m,borderInfo:`1px solid ${t(a,v(h,{alpha:.25}))}`,colorInfo:t(a,v(h,{alpha:.08})),titleTextColorInfo:c,iconColorInfo:h,contentTextColorInfo:l,closeColorHoverInfo:u,closeColorPressedInfo:d,closeIconColorInfo:f,closeIconColorHoverInfo:p,closeIconColorPressedInfo:m,borderSuccess:`1px solid ${t(a,v(g,{alpha:.25}))}`,colorSuccess:t(a,v(g,{alpha:.08})),titleTextColorSuccess:c,iconColorSuccess:g,contentTextColorSuccess:l,closeColorHoverSuccess:u,closeColorPressedSuccess:d,closeIconColorSuccess:f,closeIconColorHoverSuccess:p,closeIconColorPressedSuccess:m,borderWarning:`1px solid ${t(a,v(_,{alpha:.33}))}`,colorWarning:t(a,v(_,{alpha:.08})),titleTextColorWarning:c,iconColorWarning:_,contentTextColorWarning:l,closeColorHoverWarning:u,closeColorPressedWarning:d,closeIconColorWarning:f,closeIconColorHoverWarning:p,closeIconColorPressedWarning:m,borderError:`1px solid ${t(a,v(y,{alpha:.25}))}`,colorError:t(a,v(y,{alpha:.08})),titleTextColorError:c,iconColorError:y,contentTextColorError:l,closeColorHoverError:u,closeColorPressedError:d,closeIconColorError:f,closeIconColorHoverError:p,closeIconColorPressedError:m})}var A={name:`Alert`,common:_,self:k},j=m(`alert`,`
 line-height: var(--n-line-height);
 border-radius: var(--n-border-radius);
 position: relative;
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-color);
 text-align: start;
 word-break: break-word;
`,[s(`border`,`
 border-radius: inherit;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 transition: border-color .3s var(--n-bezier);
 border: var(--n-border);
 pointer-events: none;
 `),f(`closable`,[m(`alert-body`,[s(`title`,`
 padding-right: 24px;
 `)])]),s(`icon`,{color:`var(--n-icon-color)`}),m(`alert-body`,{padding:`var(--n-padding)`},[s(`title`,{color:`var(--n-title-text-color)`}),s(`content`,{color:`var(--n-content-text-color)`})]),T({originalTransition:`transform .3s var(--n-bezier)`,enterToProps:{transform:`scale(1)`},leaveToProps:{transform:`scale(0.9)`}}),s(`icon`,`
 position: absolute;
 left: 0;
 top: 0;
 align-items: center;
 justify-content: center;
 display: flex;
 width: var(--n-icon-size);
 height: var(--n-icon-size);
 font-size: var(--n-icon-size);
 margin: var(--n-icon-margin);
 `),s(`close`,`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 position: absolute;
 right: 0;
 top: 0;
 margin: var(--n-close-margin);
 `),f(`show-icon`,[m(`alert-body`,{paddingLeft:`calc(var(--n-icon-margin-left) + var(--n-icon-size) + var(--n-icon-margin-right))`})]),f(`right-adjust`,[m(`alert-body`,{paddingRight:`calc(var(--n-close-size) + var(--n-padding) + 2px)`})]),m(`alert-body`,`
 border-radius: var(--n-border-radius);
 transition: border-color .3s var(--n-bezier);
 `,[s(`title`,`
 transition: color .3s var(--n-bezier);
 font-size: 16px;
 line-height: 19px;
 font-weight: var(--n-title-font-weight);
 `,[n(`& +`,[s(`content`,{marginTop:`9px`})])]),s(`content`,{transition:`color .3s var(--n-bezier)`,fontSize:`var(--n-font-size)`})]),s(`icon`,{transition:`color .3s var(--n-bezier)`})]),M=Object.assign(Object.assign({},r.props),{title:String,showIcon:{type:Boolean,default:!0},type:{type:String,default:`default`},bordered:{type:Boolean,default:!0},closable:Boolean,onClose:Function,onAfterLeave:Function,onAfterHide:Function}),N=x({name:`Alert`,inheritAttrs:!1,props:M,slots:Object,setup(t){let{mergedClsPrefixRef:n,mergedBorderedRef:s,inlineThemeDisabled:u,mergedRtlRef:d}=i(t),f=r(`Alert`,`-alert`,j,A,t,n),p=e(`Alert`,d,n),m=b(()=>{let{common:{cubicBezierEaseInOut:e},self:n}=f.value,{fontSize:r,borderRadius:i,titleFontWeight:s,lineHeight:c,iconSize:l,iconMargin:u,iconMarginRtl:d,closeIconSize:p,closeBorderRadius:m,closeSize:h,closeMargin:g,closeMarginRtl:_,padding:v}=n,{type:y}=t,{left:b,right:x}=a(u);return{"--n-bezier":e,"--n-color":n[o(`color`,y)],"--n-close-icon-size":p,"--n-close-border-radius":m,"--n-close-color-hover":n[o(`closeColorHover`,y)],"--n-close-color-pressed":n[o(`closeColorPressed`,y)],"--n-close-icon-color":n[o(`closeIconColor`,y)],"--n-close-icon-color-hover":n[o(`closeIconColorHover`,y)],"--n-close-icon-color-pressed":n[o(`closeIconColorPressed`,y)],"--n-icon-color":n[o(`iconColor`,y)],"--n-border":n[o(`border`,y)],"--n-title-text-color":n[o(`titleTextColor`,y)],"--n-content-text-color":n[o(`contentTextColor`,y)],"--n-line-height":c,"--n-border-radius":i,"--n-font-size":r,"--n-title-font-weight":s,"--n-icon-size":l,"--n-icon-margin":u,"--n-icon-margin-rtl":d,"--n-close-size":h,"--n-close-margin":g,"--n-close-margin-rtl":_,"--n-padding":v,"--n-icon-margin-left":b,"--n-icon-margin-right":x}}),h=u?c(`alert`,b(()=>t.type[0]),m,t):void 0,g=l(!0),_=()=>{let{onAfterLeave:e,onAfterHide:n}=t;e&&e(),n&&n()};return{rtlEnabled:p,mergedClsPrefix:n,mergedBordered:s,visible:g,handleCloseClick:()=>{Promise.resolve(t.onClose?.call(t)).then(e=>{e!==!1&&(g.value=!1)})},handleAfterLeave:()=>{_()},mergedTheme:f,cssVars:u?void 0:m,themeClass:h?.themeClass,onRender:h?.onRender}},render(){var e;return(e=this.onRender)==null||e.call(this),g(h,{onAfterLeave:this.handleAfterLeave},{default:()=>{let{mergedClsPrefix:e,$slots:t}=this,n={class:[`${e}-alert`,this.themeClass,this.closable&&`${e}-alert--closable`,this.showIcon&&`${e}-alert--show-icon`,!this.title&&this.closable&&`${e}-alert--right-adjust`,this.rtlEnabled&&`${e}-alert--rtl`],style:this.cssVars,role:`alert`};return this.visible?g(`div`,Object.assign({},y(this.$attrs,n)),this.closable&&g(S,{clsPrefix:e,class:`${e}-alert__close`,onClick:this.handleCloseClick}),this.bordered&&g(`div`,{class:`${e}-alert__border`}),this.showIcon&&g(`div`,{class:`${e}-alert__icon`,"aria-hidden":`true`},p(t.icon,()=>[g(u,{clsPrefix:e},{default:()=>{switch(this.type){case`success`:return g(D,null);case`info`:return g(C,null);case`warning`:return g(w,null);case`error`:return g(E,null);default:return null}}})])),g(`div`,{class:[`${e}-alert-body`,this.mergedBordered&&`${e}-alert-body--bordered`]},d(t.header,t=>{let n=t||this.title;return n?g(`div`,{class:`${e}-alert-body__title`},n):null}),t.default&&g(`div`,{class:`${e}-alert-body__content`},t))):null}})}});export{N as t};
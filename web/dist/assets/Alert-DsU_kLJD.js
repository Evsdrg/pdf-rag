import{A as e,Bt as t,D as n,F as r,Ht as i,Nn as a,Ot as o,P as s,Pt as c,T as l,U as u,V as d,Vt as f,Wt as p,b as m,dn as h,g,kt as _,ln as v,nn as y,pn as b,x,zt as S}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{A as C,O as w,b as T,j as E,k as D,x as O}from"./index-Li7ENe2r.js";function k(e){let{lineHeight:t,borderRadius:n,fontWeightStrong:r,baseColor:i,dividerColor:a,actionColor:s,textColor1:c,textColor2:l,closeColorHover:u,closeColorPressed:d,closeIconColor:f,closeIconColorHover:p,closeIconColorPressed:m,infoColor:h,successColor:g,warningColor:v,errorColor:y,fontSize:b}=e;return Object.assign(Object.assign({},O),{fontSize:b,lineHeight:t,titleFontWeight:r,borderRadius:n,border:`1px solid ${a}`,color:s,titleTextColor:c,iconColor:l,contentTextColor:l,closeBorderRadius:n,closeColorHover:u,closeColorPressed:d,closeIconColor:f,closeIconColorHover:p,closeIconColorPressed:m,borderInfo:`1px solid ${_(i,o(h,{alpha:.25}))}`,colorInfo:_(i,o(h,{alpha:.08})),titleTextColorInfo:c,iconColorInfo:h,contentTextColorInfo:l,closeColorHoverInfo:u,closeColorPressedInfo:d,closeIconColorInfo:f,closeIconColorHoverInfo:p,closeIconColorPressedInfo:m,borderSuccess:`1px solid ${_(i,o(g,{alpha:.25}))}`,colorSuccess:_(i,o(g,{alpha:.08})),titleTextColorSuccess:c,iconColorSuccess:g,contentTextColorSuccess:l,closeColorHoverSuccess:u,closeColorPressedSuccess:d,closeIconColorSuccess:f,closeIconColorHoverSuccess:p,closeIconColorPressedSuccess:m,borderWarning:`1px solid ${_(i,o(v,{alpha:.33}))}`,colorWarning:_(i,o(v,{alpha:.08})),titleTextColorWarning:c,iconColorWarning:v,contentTextColorWarning:l,closeColorHoverWarning:u,closeColorPressedWarning:d,closeIconColorWarning:f,closeIconColorHoverWarning:p,closeIconColorPressedWarning:m,borderError:`1px solid ${_(i,o(y,{alpha:.25}))}`,colorError:_(i,o(y,{alpha:.08})),titleTextColorError:c,iconColorError:y,contentTextColorError:l,closeColorHoverError:u,closeColorPressedError:d,closeIconColorError:f,closeIconColorHoverError:p,closeIconColorPressedError:m})}var A={name:`Alert`,common:g,self:k},j=t(`alert`,`
 line-height: var(--n-line-height);
 border-radius: var(--n-border-radius);
 position: relative;
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-color);
 text-align: start;
 word-break: break-word;
`,[f(`border`,`
 border-radius: inherit;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 transition: border-color .3s var(--n-bezier);
 border: var(--n-border);
 pointer-events: none;
 `),i(`closable`,[t(`alert-body`,[f(`title`,`
 padding-right: 24px;
 `)])]),f(`icon`,{color:`var(--n-icon-color)`}),t(`alert-body`,{padding:`var(--n-padding)`},[f(`title`,{color:`var(--n-title-text-color)`}),f(`content`,{color:`var(--n-content-text-color)`})]),T({originalTransition:`transform .3s var(--n-bezier)`,enterToProps:{transform:`scale(1)`},leaveToProps:{transform:`scale(0.9)`}}),f(`icon`,`
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
 `),f(`close`,`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 position: absolute;
 right: 0;
 top: 0;
 margin: var(--n-close-margin);
 `),i(`show-icon`,[t(`alert-body`,{paddingLeft:`calc(var(--n-icon-margin-left) + var(--n-icon-size) + var(--n-icon-margin-right))`})]),i(`right-adjust`,[t(`alert-body`,{paddingRight:`calc(var(--n-close-size) + var(--n-padding) + 2px)`})]),t(`alert-body`,`
 border-radius: var(--n-border-radius);
 transition: border-color .3s var(--n-bezier);
 `,[f(`title`,`
 transition: color .3s var(--n-bezier);
 font-size: 16px;
 line-height: 19px;
 font-weight: var(--n-title-font-weight);
 `,[S(`& +`,[f(`content`,{marginTop:`9px`})])]),f(`content`,{transition:`color .3s var(--n-bezier)`,fontSize:`var(--n-font-size)`})]),f(`icon`,{transition:`color .3s var(--n-bezier)`})]),M=Object.assign(Object.assign({},n.props),{title:String,showIcon:{type:Boolean,default:!0},type:{type:String,default:`default`},bordered:{type:Boolean,default:!0},closable:Boolean,onClose:Function,onAfterLeave:Function,onAfterHide:Function}),N=v({name:`Alert`,inheritAttrs:!1,props:M,slots:Object,setup(t){let{mergedClsPrefixRef:i,mergedBorderedRef:o,inlineThemeDisabled:l,mergedRtlRef:u}=r(t),d=n(`Alert`,`-alert`,j,A,t,i),f=e(`Alert`,u,i),m=y(()=>{let{common:{cubicBezierEaseInOut:e},self:n}=d.value,{fontSize:r,borderRadius:i,titleFontWeight:a,lineHeight:o,iconSize:s,iconMargin:l,iconMarginRtl:u,closeIconSize:f,closeBorderRadius:m,closeSize:h,closeMargin:g,closeMarginRtl:_,padding:v}=n,{type:y}=t,{left:b,right:x}=c(l);return{"--n-bezier":e,"--n-color":n[p(`color`,y)],"--n-close-icon-size":f,"--n-close-border-radius":m,"--n-close-color-hover":n[p(`closeColorHover`,y)],"--n-close-color-pressed":n[p(`closeColorPressed`,y)],"--n-close-icon-color":n[p(`closeIconColor`,y)],"--n-close-icon-color-hover":n[p(`closeIconColorHover`,y)],"--n-close-icon-color-pressed":n[p(`closeIconColorPressed`,y)],"--n-icon-color":n[p(`iconColor`,y)],"--n-border":n[p(`border`,y)],"--n-title-text-color":n[p(`titleTextColor`,y)],"--n-content-text-color":n[p(`contentTextColor`,y)],"--n-line-height":o,"--n-border-radius":i,"--n-font-size":r,"--n-title-font-weight":a,"--n-icon-size":s,"--n-icon-margin":l,"--n-icon-margin-rtl":u,"--n-close-size":h,"--n-close-margin":g,"--n-close-margin-rtl":_,"--n-padding":v,"--n-icon-margin-left":b,"--n-icon-margin-right":x}}),h=l?s(`alert`,y(()=>t.type[0]),m,t):void 0,g=a(!0),_=()=>{let{onAfterLeave:e,onAfterHide:n}=t;e&&e(),n&&n()};return{rtlEnabled:f,mergedClsPrefix:i,mergedBordered:o,visible:g,handleCloseClick:()=>{Promise.resolve(t.onClose?.call(t)).then(e=>{e!==!1&&(g.value=!1)})},handleAfterLeave:()=>{_()},mergedTheme:d,cssVars:l?void 0:m,themeClass:h?.themeClass,onRender:h?.onRender}},render(){var e;return(e=this.onRender)==null||e.call(this),h(m,{onAfterLeave:this.handleAfterLeave},{default:()=>{let{mergedClsPrefix:e,$slots:t}=this,n={class:[`${e}-alert`,this.themeClass,this.closable&&`${e}-alert--closable`,this.showIcon&&`${e}-alert--show-icon`,!this.title&&this.closable&&`${e}-alert--right-adjust`,this.rtlEnabled&&`${e}-alert--rtl`],style:this.cssVars,role:`alert`};return this.visible?h(`div`,Object.assign({},b(this.$attrs,n)),this.closable&&h(x,{clsPrefix:e,class:`${e}-alert__close`,onClick:this.handleCloseClick}),this.bordered&&h(`div`,{class:`${e}-alert__border`}),this.showIcon&&h(`div`,{class:`${e}-alert__icon`,"aria-hidden":`true`},d(t.icon,()=>[h(l,{clsPrefix:e},{default:()=>{switch(this.type){case`success`:return h(D,null);case`info`:return h(C,null);case`warning`:return h(w,null);case`error`:return h(E,null);default:return null}}})])),h(`div`,{class:[`${e}-alert-body`,this.mergedBordered&&`${e}-alert-body--bordered`]},u(t.header,t=>{let n=t||this.title;return n?h(`div`,{class:`${e}-alert-body__title`},n):null}),t.default&&h(`div`,{class:`${e}-alert-body__content`},t))):null}})}});export{N as t};
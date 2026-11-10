import{C as e,D as t,G as n,Gt as r,Ht as i,I as a,In as o,L as s,Lt as c,M as l,Mt as u,S as d,U as f,Ut as p,Wt as m,an as h,fn as g,gn as _,jt as v,k as y,mn as b,qt as x,v as S}from"./_plugin-vue_export-helper-BL3uulyl.js";import{A as C,D as w,O as T,b as E,k as D,x as O}from"./index-CzNorles.js";function k(e){let{lineHeight:t,borderRadius:n,fontWeightStrong:r,baseColor:i,dividerColor:a,actionColor:o,textColor1:s,textColor2:c,closeColorHover:l,closeColorPressed:d,closeIconColor:f,closeIconColorHover:p,closeIconColorPressed:m,infoColor:h,successColor:g,warningColor:_,errorColor:y,fontSize:b}=e;return Object.assign(Object.assign({},O),{fontSize:b,lineHeight:t,titleFontWeight:r,borderRadius:n,border:`1px solid ${a}`,color:o,titleTextColor:s,iconColor:c,contentTextColor:c,closeBorderRadius:n,closeColorHover:l,closeColorPressed:d,closeIconColor:f,closeIconColorHover:p,closeIconColorPressed:m,borderInfo:`1px solid ${u(i,v(h,{alpha:.25}))}`,colorInfo:u(i,v(h,{alpha:.08})),titleTextColorInfo:s,iconColorInfo:h,contentTextColorInfo:c,closeColorHoverInfo:l,closeColorPressedInfo:d,closeIconColorInfo:f,closeIconColorHoverInfo:p,closeIconColorPressedInfo:m,borderSuccess:`1px solid ${u(i,v(g,{alpha:.25}))}`,colorSuccess:u(i,v(g,{alpha:.08})),titleTextColorSuccess:s,iconColorSuccess:g,contentTextColorSuccess:c,closeColorHoverSuccess:l,closeColorPressedSuccess:d,closeIconColorSuccess:f,closeIconColorHoverSuccess:p,closeIconColorPressedSuccess:m,borderWarning:`1px solid ${u(i,v(_,{alpha:.33}))}`,colorWarning:u(i,v(_,{alpha:.08})),titleTextColorWarning:s,iconColorWarning:_,contentTextColorWarning:c,closeColorHoverWarning:l,closeColorPressedWarning:d,closeIconColorWarning:f,closeIconColorHoverWarning:p,closeIconColorPressedWarning:m,borderError:`1px solid ${u(i,v(y,{alpha:.25}))}`,colorError:u(i,v(y,{alpha:.08})),titleTextColorError:s,iconColorError:y,contentTextColorError:c,closeColorHoverError:l,closeColorPressedError:d,closeIconColorError:f,closeIconColorHoverError:p,closeIconColorPressedError:m})}var A={name:`Alert`,common:S,self:k},j=p(`alert`,`
 line-height: var(--n-line-height);
 border-radius: var(--n-border-radius);
 position: relative;
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-color);
 text-align: start;
 word-break: break-word;
`,[m(`border`,`
 border-radius: inherit;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 transition: border-color .3s var(--n-bezier);
 border: var(--n-border);
 pointer-events: none;
 `),r(`closable`,[p(`alert-body`,[m(`title`,`
 padding-right: 24px;
 `)])]),m(`icon`,{color:`var(--n-icon-color)`}),p(`alert-body`,{padding:`var(--n-padding)`},[m(`title`,{color:`var(--n-title-text-color)`}),m(`content`,{color:`var(--n-content-text-color)`})]),E({originalTransition:`transform .3s var(--n-bezier)`,enterToProps:{transform:`scale(1)`},leaveToProps:{transform:`scale(0.9)`}}),m(`icon`,`
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
 `),m(`close`,`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 position: absolute;
 right: 0;
 top: 0;
 margin: var(--n-close-margin);
 `),r(`show-icon`,[p(`alert-body`,{paddingLeft:`calc(var(--n-icon-margin-left) + var(--n-icon-size) + var(--n-icon-margin-right))`})]),r(`right-adjust`,[p(`alert-body`,{paddingRight:`calc(var(--n-close-size) + var(--n-padding) + 2px)`})]),p(`alert-body`,`
 border-radius: var(--n-border-radius);
 transition: border-color .3s var(--n-bezier);
 `,[m(`title`,`
 transition: color .3s var(--n-bezier);
 font-size: 16px;
 line-height: 19px;
 font-weight: var(--n-title-font-weight);
 `,[i(`& +`,[m(`content`,{marginTop:`9px`})])]),m(`content`,{transition:`color .3s var(--n-bezier)`,fontSize:`var(--n-font-size)`})]),m(`icon`,{transition:`color .3s var(--n-bezier)`})]),M=Object.assign(Object.assign({},y.props),{title:String,showIcon:{type:Boolean,default:!0},type:{type:String,default:`default`},bordered:{type:Boolean,default:!0},closable:Boolean,onClose:Function,onAfterLeave:Function,onAfterHide:Function}),N=g({name:`Alert`,inheritAttrs:!1,props:M,slots:Object,setup(e){let{mergedClsPrefixRef:t,mergedBorderedRef:n,inlineThemeDisabled:r,mergedRtlRef:i}=s(e),u=y(`Alert`,`-alert`,j,A,e,t),d=l(`Alert`,i,t),f=h(()=>{let{common:{cubicBezierEaseInOut:t},self:n}=u.value,{fontSize:r,borderRadius:i,titleFontWeight:a,lineHeight:o,iconSize:s,iconMargin:l,iconMarginRtl:d,closeIconSize:f,closeBorderRadius:p,closeSize:m,closeMargin:h,closeMarginRtl:g,padding:_}=n,{type:v}=e,{left:y,right:b}=c(l);return{"--n-bezier":t,"--n-color":n[x(`color`,v)],"--n-close-icon-size":f,"--n-close-border-radius":p,"--n-close-color-hover":n[x(`closeColorHover`,v)],"--n-close-color-pressed":n[x(`closeColorPressed`,v)],"--n-close-icon-color":n[x(`closeIconColor`,v)],"--n-close-icon-color-hover":n[x(`closeIconColorHover`,v)],"--n-close-icon-color-pressed":n[x(`closeIconColorPressed`,v)],"--n-icon-color":n[x(`iconColor`,v)],"--n-border":n[x(`border`,v)],"--n-title-text-color":n[x(`titleTextColor`,v)],"--n-content-text-color":n[x(`contentTextColor`,v)],"--n-line-height":o,"--n-border-radius":i,"--n-font-size":r,"--n-title-font-weight":a,"--n-icon-size":s,"--n-icon-margin":l,"--n-icon-margin-rtl":d,"--n-close-size":m,"--n-close-margin":h,"--n-close-margin-rtl":g,"--n-padding":_,"--n-icon-margin-left":y,"--n-icon-margin-right":b}}),p=r?a(`alert`,h(()=>e.type[0]),f,e):void 0,m=o(!0),g=()=>{let{onAfterLeave:t,onAfterHide:n}=e;t&&t(),n&&n()};return{rtlEnabled:d,mergedClsPrefix:t,mergedBordered:n,visible:m,handleCloseClick:()=>{Promise.resolve(e.onClose?.call(e)).then(e=>{e!==!1&&(m.value=!1)})},handleAfterLeave:()=>{g()},mergedTheme:u,cssVars:r?void 0:f,themeClass:p?.themeClass,onRender:p?.onRender}},render(){var r;return(r=this.onRender)==null||r.call(this),b(d,{onAfterLeave:this.handleAfterLeave},{default:()=>{let{mergedClsPrefix:r,$slots:i}=this,a={class:[`${r}-alert`,this.themeClass,this.closable&&`${r}-alert--closable`,this.showIcon&&`${r}-alert--show-icon`,!this.title&&this.closable&&`${r}-alert--right-adjust`,this.rtlEnabled&&`${r}-alert--rtl`],style:this.cssVars,role:`alert`};return this.visible?b(`div`,Object.assign({},_(this.$attrs,a)),this.closable&&b(e,{clsPrefix:r,class:`${r}-alert__close`,onClick:this.handleCloseClick}),this.bordered&&b(`div`,{class:`${r}-alert__border`}),this.showIcon&&b(`div`,{class:`${r}-alert__icon`,"aria-hidden":`true`},f(i.icon,()=>[b(t,{clsPrefix:r},{default:()=>{switch(this.type){case`success`:return b(T,null);case`info`:return b(D,null);case`warning`:return b(w,null);case`error`:return b(C,null);default:return null}}})])),b(`div`,{class:[`${r}-alert-body`,this.mergedBordered&&`${r}-alert-body--bordered`]},n(i.header,e=>{let t=e||this.title;return t?b(`div`,{class:`${r}-alert-body__title`},t):null}),i.default&&b(`div`,{class:`${r}-alert-body__content`},i))):null}})}});export{N as t};
import{A as e,Bt as t,D as n,F as r,Gt as i,Ht as a,Kt as o,P as s,Pt as c,Rt as l,U as u,Vt as d,Wt as f,dn as p,f as m,ln as h,nn as g,q as _,x as v,z as y,zt as b}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{P as x,_ as S}from"./index-BFmhv3ZW.js";var C=t(`card-content`,`
 flex: 1;
 min-width: 0;
 box-sizing: border-box;
 padding: 0 var(--n-padding-left) var(--n-padding-bottom) var(--n-padding-left);
 font-size: var(--n-font-size);
`),w=b([t(`card`,`
 font-size: var(--n-font-size);
 line-height: var(--n-line-height);
 display: flex;
 flex-direction: column;
 width: 100%;
 box-sizing: border-box;
 position: relative;
 border-radius: var(--n-border-radius);
 background-color: var(--n-color);
 color: var(--n-text-color);
 word-break: break-word;
 transition: 
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[l({background:`var(--n-color-modal)`}),a(`hoverable`,[b(`&:hover`,`box-shadow: var(--n-box-shadow);`)]),a(`content-segmented`,[b(`>`,[t(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `),d(`content-scrollbar`,[b(`>`,[t(`scrollbar-container`,[b(`>`,[t(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `)])])])])])]),a(`content-soft-segmented`,[b(`>`,[t(`card-content`,`
 margin: 0 var(--n-padding-left);
 padding: var(--n-padding-bottom) 0;
 `),d(`content-scrollbar`,[b(`>`,[t(`scrollbar-container`,[b(`>`,[t(`card-content`,`
 margin: 0 var(--n-padding-left);
 padding: var(--n-padding-bottom) 0;
 `)])])])])])]),a(`footer-segmented`,[b(`>`,[d(`footer`,`
 padding-top: var(--n-padding-bottom);
 `)])]),a(`footer-soft-segmented`,[b(`>`,[d(`footer`,`
 padding: var(--n-padding-bottom) 0;
 margin: 0 var(--n-padding-left);
 `)])]),b(`>`,[t(`card-header`,`
 box-sizing: border-box;
 display: flex;
 align-items: center;
 font-size: var(--n-title-font-size);
 padding:
 var(--n-padding-top)
 var(--n-padding-left)
 var(--n-padding-bottom)
 var(--n-padding-left);
 `,[d(`main`,`
 font-weight: var(--n-title-font-weight);
 transition: color .3s var(--n-bezier);
 flex: 1;
 min-width: 0;
 color: var(--n-title-text-color);
 `),d(`extra`,`
 display: flex;
 align-items: center;
 font-size: var(--n-font-size);
 font-weight: 400;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),d(`close`,`
 margin: 0 0 0 8px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)]),d(`action`,`
 box-sizing: border-box;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 background-clip: padding-box;
 background-color: var(--n-action-color);
 `),C,t(`card-content`,[b(`&:first-child`,`
 padding-top: var(--n-padding-bottom);
 `)]),d(`content-scrollbar`,`
 display: flex;
 flex-direction: column;
 `,[b(`>`,[t(`scrollbar-container`,[b(`>`,[C])])]),b(`&:first-child >`,[t(`scrollbar-container`,[b(`>`,[t(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `)])])])]),d(`footer`,`
 box-sizing: border-box;
 padding: 0 var(--n-padding-left) var(--n-padding-bottom) var(--n-padding-left);
 font-size: var(--n-font-size);
 `,[b(`&:first-child`,`
 padding-top: var(--n-padding-bottom);
 `)]),d(`action`,`
 background-color: var(--n-action-color);
 padding: var(--n-padding-bottom) var(--n-padding-left);
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `)]),t(`card-cover`,`
 overflow: hidden;
 width: 100%;
 border-radius: var(--n-border-radius) var(--n-border-radius) 0 0;
 `,[b(`img`,`
 display: block;
 width: 100%;
 `)]),a(`bordered`,`
 border: 1px solid var(--n-border-color);
 `,[b(`&:target`,`border-color: var(--n-color-target);`)]),a(`action-segmented`,[b(`>`,[d(`action`,[b(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),a(`content-segmented, content-soft-segmented`,[b(`>`,[t(`card-content`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[b(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)]),d(`content-scrollbar`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[b(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),a(`footer-segmented, footer-soft-segmented`,[b(`>`,[d(`footer`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[b(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),a(`embedded`,`
 background-color: var(--n-color-embedded);
 `)]),i(t(`card`,`
 background: var(--n-color-modal);
 `,[a(`embedded`,`
 background-color: var(--n-color-embedded-modal);
 `)])),o(t(`card`,`
 background: var(--n-color-popover);
 `,[a(`embedded`,`
 background-color: var(--n-color-embedded-popover);
 `)]))]),T={title:[String,Function],contentClass:String,contentStyle:[Object,String],contentScrollable:Boolean,headerClass:String,headerStyle:[Object,String],headerExtraClass:String,headerExtraStyle:[Object,String],footerClass:String,footerStyle:[Object,String],embedded:Boolean,segmented:{type:[Boolean,Object],default:!1},size:String,bordered:{type:Boolean,default:!0},closable:Boolean,hoverable:Boolean,role:String,onClose:[Function,Array],tag:{type:String,default:`div`},cover:Function,content:[String,Function],footer:Function,action:Function,headerExtra:Function,closeFocusable:Boolean};x(T);var E=Object.assign(Object.assign({},n.props),T),D=h({name:`Card`,props:E,slots:Object,setup(t){let i=()=>{let{onClose:e}=t;e&&_(e)},{inlineThemeDisabled:a,mergedClsPrefixRef:o,mergedRtlRef:l,mergedComponentPropsRef:u}=r(t),d=n(`Card`,`-card`,w,S,t,o),p=e(`Card`,l,o),m=g(()=>t.size||u?.value?.Card?.size||`medium`),h=g(()=>{let e=m.value,{self:{color:t,colorModal:n,colorTarget:r,textColor:i,titleTextColor:a,titleFontWeight:o,borderColor:s,actionColor:l,borderRadius:u,lineHeight:p,closeIconColor:h,closeIconColorHover:g,closeIconColorPressed:_,closeColorHover:v,closeColorPressed:y,closeBorderRadius:b,closeIconSize:x,closeSize:S,boxShadow:C,colorPopover:w,colorEmbedded:T,colorEmbeddedModal:E,colorEmbeddedPopover:D,[f(`padding`,e)]:O,[f(`fontSize`,e)]:k,[f(`titleFontSize`,e)]:A},common:{cubicBezierEaseInOut:j}}=d.value,{top:M,left:N,bottom:P}=c(O);return{"--n-bezier":j,"--n-border-radius":u,"--n-color":t,"--n-color-modal":n,"--n-color-popover":w,"--n-color-embedded":T,"--n-color-embedded-modal":E,"--n-color-embedded-popover":D,"--n-color-target":r,"--n-text-color":i,"--n-line-height":p,"--n-action-color":l,"--n-title-text-color":a,"--n-title-font-weight":o,"--n-close-icon-color":h,"--n-close-icon-color-hover":g,"--n-close-icon-color-pressed":_,"--n-close-color-hover":v,"--n-close-color-pressed":y,"--n-border-color":s,"--n-box-shadow":C,"--n-padding-top":M,"--n-padding-bottom":P,"--n-padding-left":N,"--n-font-size":k,"--n-title-font-size":A,"--n-close-size":S,"--n-close-icon-size":x,"--n-close-border-radius":b}}),v=a?s(`card`,g(()=>m.value[0]),h,t):void 0;return{rtlEnabled:p,mergedClsPrefix:o,mergedTheme:d,handleCloseClick:i,cssVars:a?void 0:h,themeClass:v?.themeClass,onRender:v?.onRender}},render(){let{segmented:e,bordered:t,hoverable:n,mergedClsPrefix:r,rtlEnabled:i,onRender:a,embedded:o,tag:s,$slots:c}=this;return a?.(),p(s,{class:[`${r}-card`,this.themeClass,o&&`${r}-card--embedded`,{[`${r}-card--rtl`]:i,[`${r}-card--content-scrollable`]:this.contentScrollable,[`${r}-card--content${typeof e!=`boolean`&&e.content===`soft`?`-soft`:``}-segmented`]:e===!0||e!==!1&&e.content,[`${r}-card--footer${typeof e!=`boolean`&&e.footer===`soft`?`-soft`:``}-segmented`]:e===!0||e!==!1&&e.footer,[`${r}-card--action-segmented`]:e===!0||e!==!1&&e.action,[`${r}-card--bordered`]:t,[`${r}-card--hoverable`]:n}],style:this.cssVars,role:this.role},u(c.cover,e=>{let t=this.cover?y([this.cover()]):e;return t&&p(`div`,{class:`${r}-card-cover`,role:`none`},t)}),u(c.header,e=>{let{title:t}=this,n=t?y(typeof t==`function`?[t()]:[t]):e;return n||this.closable?p(`div`,{class:[`${r}-card-header`,this.headerClass],style:this.headerStyle,role:`heading`},p(`div`,{class:`${r}-card-header__main`,role:`heading`},n),u(c[`header-extra`],e=>{let t=this.headerExtra?y([this.headerExtra()]):e;return t&&p(`div`,{class:[`${r}-card-header__extra`,this.headerExtraClass],style:this.headerExtraStyle},t)}),this.closable&&p(v,{clsPrefix:r,class:`${r}-card-header__close`,onClick:this.handleCloseClick,focusable:this.closeFocusable,absolute:!0})):null}),u(c.default,e=>{let{content:t}=this,n=t?y(typeof t==`function`?[t()]:[t]):e;return n?this.contentScrollable?p(m,{class:`${r}-card__content-scrollbar`,contentClass:[`${r}-card-content`,this.contentClass],contentStyle:this.contentStyle},n):p(`div`,{class:[`${r}-card-content`,this.contentClass],style:this.contentStyle,role:`none`},n):null}),u(c.footer,e=>{let t=this.footer?y([this.footer()]):e;return t&&p(`div`,{class:[`${r}-card__footer`,this.footerClass],style:this.footerStyle,role:`none`},t)}),u(c.action,e=>{let t=this.action?y([this.action()]):e;return t&&p(`div`,{class:`${r}-card__action`,role:`none`},t)}))}});export{D as t};
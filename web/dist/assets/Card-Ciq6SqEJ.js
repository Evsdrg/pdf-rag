import{A as e,Bt as t,D as n,F as r,Ft as i,G as a,Gt as o,Ht as s,J as c,Kt as l,P as u,U as d,Ut as f,Vt as p,f as m,fn as h,qt as g,rn as _,un as v,x as y,z as b,zt as x}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{v as S}from"./index-ejBjBNv_.js";function C(e,t=`default`,n=[]){let r=e.$slots[t];return r===void 0?n:r()}var w=p(`card-content`,`
 flex: 1;
 min-width: 0;
 box-sizing: border-box;
 padding: 0 var(--n-padding-left) var(--n-padding-bottom) var(--n-padding-left);
 font-size: var(--n-font-size);
`),T=t([p(`card`,`
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
 `,[x({background:`var(--n-color-modal)`}),f(`hoverable`,[t(`&:hover`,`box-shadow: var(--n-box-shadow);`)]),f(`content-segmented`,[t(`>`,[p(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `),s(`content-scrollbar`,[t(`>`,[p(`scrollbar-container`,[t(`>`,[p(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `)])])])])])]),f(`content-soft-segmented`,[t(`>`,[p(`card-content`,`
 margin: 0 var(--n-padding-left);
 padding: var(--n-padding-bottom) 0;
 `),s(`content-scrollbar`,[t(`>`,[p(`scrollbar-container`,[t(`>`,[p(`card-content`,`
 margin: 0 var(--n-padding-left);
 padding: var(--n-padding-bottom) 0;
 `)])])])])])]),f(`footer-segmented`,[t(`>`,[s(`footer`,`
 padding-top: var(--n-padding-bottom);
 `)])]),f(`footer-soft-segmented`,[t(`>`,[s(`footer`,`
 padding: var(--n-padding-bottom) 0;
 margin: 0 var(--n-padding-left);
 `)])]),t(`>`,[p(`card-header`,`
 box-sizing: border-box;
 display: flex;
 align-items: center;
 font-size: var(--n-title-font-size);
 padding:
 var(--n-padding-top)
 var(--n-padding-left)
 var(--n-padding-bottom)
 var(--n-padding-left);
 `,[s(`main`,`
 font-weight: var(--n-title-font-weight);
 transition: color .3s var(--n-bezier);
 flex: 1;
 min-width: 0;
 color: var(--n-title-text-color);
 `),s(`extra`,`
 display: flex;
 align-items: center;
 font-size: var(--n-font-size);
 font-weight: 400;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),s(`close`,`
 margin: 0 0 0 8px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)]),s(`action`,`
 box-sizing: border-box;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 background-clip: padding-box;
 background-color: var(--n-action-color);
 `),w,p(`card-content`,[t(`&:first-child`,`
 padding-top: var(--n-padding-bottom);
 `)]),s(`content-scrollbar`,`
 display: flex;
 flex-direction: column;
 `,[t(`>`,[p(`scrollbar-container`,[t(`>`,[w])])]),t(`&:first-child >`,[p(`scrollbar-container`,[t(`>`,[p(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `)])])])]),s(`footer`,`
 box-sizing: border-box;
 padding: 0 var(--n-padding-left) var(--n-padding-bottom) var(--n-padding-left);
 font-size: var(--n-font-size);
 `,[t(`&:first-child`,`
 padding-top: var(--n-padding-bottom);
 `)]),s(`action`,`
 background-color: var(--n-action-color);
 padding: var(--n-padding-bottom) var(--n-padding-left);
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `)]),p(`card-cover`,`
 overflow: hidden;
 width: 100%;
 border-radius: var(--n-border-radius) var(--n-border-radius) 0 0;
 `,[t(`img`,`
 display: block;
 width: 100%;
 `)]),f(`bordered`,`
 border: 1px solid var(--n-border-color);
 `,[t(`&:target`,`border-color: var(--n-color-target);`)]),f(`action-segmented`,[t(`>`,[s(`action`,[t(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),f(`content-segmented, content-soft-segmented`,[t(`>`,[p(`card-content`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[t(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)]),s(`content-scrollbar`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[t(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),f(`footer-segmented, footer-soft-segmented`,[t(`>`,[s(`footer`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[t(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),f(`embedded`,`
 background-color: var(--n-color-embedded);
 `)]),l(p(`card`,`
 background: var(--n-color-modal);
 `,[f(`embedded`,`
 background-color: var(--n-color-embedded-modal);
 `)])),g(p(`card`,`
 background: var(--n-color-popover);
 `,[f(`embedded`,`
 background-color: var(--n-color-embedded-popover);
 `)]))]),E={title:[String,Function],contentClass:String,contentStyle:[Object,String],contentScrollable:Boolean,headerClass:String,headerStyle:[Object,String],headerExtraClass:String,headerExtraStyle:[Object,String],footerClass:String,footerStyle:[Object,String],embedded:Boolean,segmented:{type:[Boolean,Object],default:!1},size:String,bordered:{type:Boolean,default:!0},closable:Boolean,hoverable:Boolean,role:String,onClose:[Function,Array],tag:{type:String,default:`div`},cover:Function,content:[String,Function],footer:Function,action:Function,headerExtra:Function,closeFocusable:Boolean};a(E);var D=Object.assign(Object.assign({},n.props),E),O=v({name:`Card`,props:D,slots:Object,setup(t){let a=()=>{let{onClose:e}=t;e&&c(e)},{inlineThemeDisabled:s,mergedClsPrefixRef:l,mergedRtlRef:d,mergedComponentPropsRef:f}=r(t),p=n(`Card`,`-card`,T,S,t,l),m=e(`Card`,d,l),h=_(()=>t.size||f?.value?.Card?.size||`medium`),g=_(()=>{let e=h.value,{self:{color:t,colorModal:n,colorTarget:r,textColor:a,titleTextColor:s,titleFontWeight:c,borderColor:l,actionColor:u,borderRadius:d,lineHeight:f,closeIconColor:m,closeIconColorHover:g,closeIconColorPressed:_,closeColorHover:v,closeColorPressed:y,closeBorderRadius:b,closeIconSize:x,closeSize:S,boxShadow:C,colorPopover:w,colorEmbedded:T,colorEmbeddedModal:E,colorEmbeddedPopover:D,[o(`padding`,e)]:O,[o(`fontSize`,e)]:k,[o(`titleFontSize`,e)]:A},common:{cubicBezierEaseInOut:j}}=p.value,{top:M,left:N,bottom:P}=i(O);return{"--n-bezier":j,"--n-border-radius":d,"--n-color":t,"--n-color-modal":n,"--n-color-popover":w,"--n-color-embedded":T,"--n-color-embedded-modal":E,"--n-color-embedded-popover":D,"--n-color-target":r,"--n-text-color":a,"--n-line-height":f,"--n-action-color":u,"--n-title-text-color":s,"--n-title-font-weight":c,"--n-close-icon-color":m,"--n-close-icon-color-hover":g,"--n-close-icon-color-pressed":_,"--n-close-color-hover":v,"--n-close-color-pressed":y,"--n-border-color":l,"--n-box-shadow":C,"--n-padding-top":M,"--n-padding-bottom":P,"--n-padding-left":N,"--n-font-size":k,"--n-title-font-size":A,"--n-close-size":S,"--n-close-icon-size":x,"--n-close-border-radius":b}}),v=s?u(`card`,_(()=>h.value[0]),g,t):void 0;return{rtlEnabled:m,mergedClsPrefix:l,mergedTheme:p,handleCloseClick:a,cssVars:s?void 0:g,themeClass:v?.themeClass,onRender:v?.onRender}},render(){let{segmented:e,bordered:t,hoverable:n,mergedClsPrefix:r,rtlEnabled:i,onRender:a,embedded:o,tag:s,$slots:c}=this;return a?.(),h(s,{class:[`${r}-card`,this.themeClass,o&&`${r}-card--embedded`,{[`${r}-card--rtl`]:i,[`${r}-card--content-scrollable`]:this.contentScrollable,[`${r}-card--content${typeof e!=`boolean`&&e.content===`soft`?`-soft`:``}-segmented`]:e===!0||e!==!1&&e.content,[`${r}-card--footer${typeof e!=`boolean`&&e.footer===`soft`?`-soft`:``}-segmented`]:e===!0||e!==!1&&e.footer,[`${r}-card--action-segmented`]:e===!0||e!==!1&&e.action,[`${r}-card--bordered`]:t,[`${r}-card--hoverable`]:n}],style:this.cssVars,role:this.role},d(c.cover,e=>{let t=this.cover?b([this.cover()]):e;return t&&h(`div`,{class:`${r}-card-cover`,role:`none`},t)}),d(c.header,e=>{let{title:t}=this,n=t?b(typeof t==`function`?[t()]:[t]):e;return n||this.closable?h(`div`,{class:[`${r}-card-header`,this.headerClass],style:this.headerStyle,role:`heading`},h(`div`,{class:`${r}-card-header__main`,role:`heading`},n),d(c[`header-extra`],e=>{let t=this.headerExtra?b([this.headerExtra()]):e;return t&&h(`div`,{class:[`${r}-card-header__extra`,this.headerExtraClass],style:this.headerExtraStyle},t)}),this.closable&&h(y,{clsPrefix:r,class:`${r}-card-header__close`,onClick:this.handleCloseClick,focusable:this.closeFocusable,absolute:!0})):null}),d(c.default,e=>{let{content:t}=this,n=t?b(typeof t==`function`?[t()]:[t]):e;return n?this.contentScrollable?h(m,{class:`${r}-card__content-scrollbar`,contentClass:[`${r}-card-content`,this.contentClass],contentStyle:this.contentStyle},n):h(`div`,{class:[`${r}-card-content`,this.contentClass],style:this.contentStyle,role:`none`},n):null}),d(c.footer,e=>{let t=this.footer?b([this.footer()]):e;return t&&h(`div`,{class:[`${r}-card__footer`,this.footerClass],style:this.footerStyle,role:`none`},t)}),d(c.action,e=>{let t=this.action?b([this.action()]):e;return t&&h(`div`,{class:`${r}-card__action`,role:`none`},t)}))}});export{C as n,O as t};
import{C as e,G as t,Gt as n,Ht as r,I as i,Jt as a,L as o,Lt as s,M as c,Ut as l,V as u,Vt as d,Wt as f,X as p,Yt as m,an as h,fn as g,k as _,m as v,mn as y,q as b,qt as x}from"./_plugin-vue_export-helper-BL3uulyl.js";import{v as S}from"./index-DFXqAcyu.js";function C(e,t=`default`,n=[]){let r=e.$slots[t];return r===void 0?n:r()}var w=l(`card-content`,`
 flex: 1;
 min-width: 0;
 box-sizing: border-box;
 padding: 0 var(--n-padding-left) var(--n-padding-bottom) var(--n-padding-left);
 font-size: var(--n-font-size);
`),T=r([l(`card`,`
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
 `,[d({background:`var(--n-color-modal)`}),n(`hoverable`,[r(`&:hover`,`box-shadow: var(--n-box-shadow);`)]),n(`content-segmented`,[r(`>`,[l(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `),f(`content-scrollbar`,[r(`>`,[l(`scrollbar-container`,[r(`>`,[l(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `)])])])])])]),n(`content-soft-segmented`,[r(`>`,[l(`card-content`,`
 margin: 0 var(--n-padding-left);
 padding: var(--n-padding-bottom) 0;
 `),f(`content-scrollbar`,[r(`>`,[l(`scrollbar-container`,[r(`>`,[l(`card-content`,`
 margin: 0 var(--n-padding-left);
 padding: var(--n-padding-bottom) 0;
 `)])])])])])]),n(`footer-segmented`,[r(`>`,[f(`footer`,`
 padding-top: var(--n-padding-bottom);
 `)])]),n(`footer-soft-segmented`,[r(`>`,[f(`footer`,`
 padding: var(--n-padding-bottom) 0;
 margin: 0 var(--n-padding-left);
 `)])]),r(`>`,[l(`card-header`,`
 box-sizing: border-box;
 display: flex;
 align-items: center;
 font-size: var(--n-title-font-size);
 padding:
 var(--n-padding-top)
 var(--n-padding-left)
 var(--n-padding-bottom)
 var(--n-padding-left);
 `,[f(`main`,`
 font-weight: var(--n-title-font-weight);
 transition: color .3s var(--n-bezier);
 flex: 1;
 min-width: 0;
 color: var(--n-title-text-color);
 `),f(`extra`,`
 display: flex;
 align-items: center;
 font-size: var(--n-font-size);
 font-weight: 400;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),f(`close`,`
 margin: 0 0 0 8px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)]),f(`action`,`
 box-sizing: border-box;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 background-clip: padding-box;
 background-color: var(--n-action-color);
 `),w,l(`card-content`,[r(`&:first-child`,`
 padding-top: var(--n-padding-bottom);
 `)]),f(`content-scrollbar`,`
 display: flex;
 flex-direction: column;
 `,[r(`>`,[l(`scrollbar-container`,[r(`>`,[w])])]),r(`&:first-child >`,[l(`scrollbar-container`,[r(`>`,[l(`card-content`,`
 padding-top: var(--n-padding-bottom);
 `)])])])]),f(`footer`,`
 box-sizing: border-box;
 padding: 0 var(--n-padding-left) var(--n-padding-bottom) var(--n-padding-left);
 font-size: var(--n-font-size);
 `,[r(`&:first-child`,`
 padding-top: var(--n-padding-bottom);
 `)]),f(`action`,`
 background-color: var(--n-action-color);
 padding: var(--n-padding-bottom) var(--n-padding-left);
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `)]),l(`card-cover`,`
 overflow: hidden;
 width: 100%;
 border-radius: var(--n-border-radius) var(--n-border-radius) 0 0;
 `,[r(`img`,`
 display: block;
 width: 100%;
 `)]),n(`bordered`,`
 border: 1px solid var(--n-border-color);
 `,[r(`&:target`,`border-color: var(--n-color-target);`)]),n(`action-segmented`,[r(`>`,[f(`action`,[r(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),n(`content-segmented, content-soft-segmented`,[r(`>`,[l(`card-content`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[r(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)]),f(`content-scrollbar`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[r(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),n(`footer-segmented, footer-soft-segmented`,[r(`>`,[f(`footer`,`
 transition: border-color 0.3s var(--n-bezier);
 `,[r(`&:not(:first-child)`,`
 border-top: 1px solid var(--n-border-color);
 `)])])]),n(`embedded`,`
 background-color: var(--n-color-embedded);
 `)]),a(l(`card`,`
 background: var(--n-color-modal);
 `,[n(`embedded`,`
 background-color: var(--n-color-embedded-modal);
 `)])),m(l(`card`,`
 background: var(--n-color-popover);
 `,[n(`embedded`,`
 background-color: var(--n-color-embedded-popover);
 `)]))]),E={title:[String,Function],contentClass:String,contentStyle:[Object,String],contentScrollable:Boolean,headerClass:String,headerStyle:[Object,String],headerExtraClass:String,headerExtraStyle:[Object,String],footerClass:String,footerStyle:[Object,String],embedded:Boolean,segmented:{type:[Boolean,Object],default:!1},size:String,bordered:{type:Boolean,default:!0},closable:Boolean,hoverable:Boolean,role:String,onClose:[Function,Array],tag:{type:String,default:`div`},cover:Function,content:[String,Function],footer:Function,action:Function,headerExtra:Function,closeFocusable:Boolean};b(E);var D=Object.assign(Object.assign({},_.props),E),O=g({name:`Card`,props:D,slots:Object,setup(e){let t=()=>{let{onClose:t}=e;t&&p(t)},{inlineThemeDisabled:n,mergedClsPrefixRef:r,mergedRtlRef:a,mergedComponentPropsRef:l}=o(e),u=_(`Card`,`-card`,T,S,e,r),d=c(`Card`,a,r),f=h(()=>e.size||l?.value?.Card?.size||`medium`),m=h(()=>{let e=f.value,{self:{color:t,colorModal:n,colorTarget:r,textColor:i,titleTextColor:a,titleFontWeight:o,borderColor:c,actionColor:l,borderRadius:d,lineHeight:p,closeIconColor:m,closeIconColorHover:h,closeIconColorPressed:g,closeColorHover:_,closeColorPressed:v,closeBorderRadius:y,closeIconSize:b,closeSize:S,boxShadow:C,colorPopover:w,colorEmbedded:T,colorEmbeddedModal:E,colorEmbeddedPopover:D,[x(`padding`,e)]:O,[x(`fontSize`,e)]:k,[x(`titleFontSize`,e)]:A},common:{cubicBezierEaseInOut:j}}=u.value,{top:M,left:N,bottom:P}=s(O);return{"--n-bezier":j,"--n-border-radius":d,"--n-color":t,"--n-color-modal":n,"--n-color-popover":w,"--n-color-embedded":T,"--n-color-embedded-modal":E,"--n-color-embedded-popover":D,"--n-color-target":r,"--n-text-color":i,"--n-line-height":p,"--n-action-color":l,"--n-title-text-color":a,"--n-title-font-weight":o,"--n-close-icon-color":m,"--n-close-icon-color-hover":h,"--n-close-icon-color-pressed":g,"--n-close-color-hover":_,"--n-close-color-pressed":v,"--n-border-color":c,"--n-box-shadow":C,"--n-padding-top":M,"--n-padding-bottom":P,"--n-padding-left":N,"--n-font-size":k,"--n-title-font-size":A,"--n-close-size":S,"--n-close-icon-size":b,"--n-close-border-radius":y}}),g=n?i(`card`,h(()=>f.value[0]),m,e):void 0;return{rtlEnabled:d,mergedClsPrefix:r,mergedTheme:u,handleCloseClick:t,cssVars:n?void 0:m,themeClass:g?.themeClass,onRender:g?.onRender}},render(){let{segmented:n,bordered:r,hoverable:i,mergedClsPrefix:a,rtlEnabled:o,onRender:s,embedded:c,tag:l,$slots:d}=this;return s?.(),y(l,{class:[`${a}-card`,this.themeClass,c&&`${a}-card--embedded`,{[`${a}-card--rtl`]:o,[`${a}-card--content-scrollable`]:this.contentScrollable,[`${a}-card--content${typeof n!=`boolean`&&n.content===`soft`?`-soft`:``}-segmented`]:n===!0||n!==!1&&n.content,[`${a}-card--footer${typeof n!=`boolean`&&n.footer===`soft`?`-soft`:``}-segmented`]:n===!0||n!==!1&&n.footer,[`${a}-card--action-segmented`]:n===!0||n!==!1&&n.action,[`${a}-card--bordered`]:r,[`${a}-card--hoverable`]:i}],style:this.cssVars,role:this.role},t(d.cover,e=>{let t=this.cover?u([this.cover()]):e;return t&&y(`div`,{class:`${a}-card-cover`,role:`none`},t)}),t(d.header,n=>{let{title:r}=this,i=r?u(typeof r==`function`?[r()]:[r]):n;return i||this.closable?y(`div`,{class:[`${a}-card-header`,this.headerClass],style:this.headerStyle,role:`heading`},y(`div`,{class:`${a}-card-header__main`,role:`heading`},i),t(d[`header-extra`],e=>{let t=this.headerExtra?u([this.headerExtra()]):e;return t&&y(`div`,{class:[`${a}-card-header__extra`,this.headerExtraClass],style:this.headerExtraStyle},t)}),this.closable&&y(e,{clsPrefix:a,class:`${a}-card-header__close`,onClick:this.handleCloseClick,focusable:this.closeFocusable,absolute:!0})):null}),t(d.default,e=>{let{content:t}=this,n=t?u(typeof t==`function`?[t()]:[t]):e;return n?this.contentScrollable?y(v,{class:`${a}-card__content-scrollbar`,contentClass:[`${a}-card-content`,this.contentClass],contentStyle:this.contentStyle},n):y(`div`,{class:[`${a}-card-content`,this.contentClass],style:this.contentStyle,role:`none`},n):null}),t(d.footer,e=>{let t=this.footer?u([this.footer()]):e;return t&&y(`div`,{class:[`${a}-card__footer`,this.footerClass],style:this.footerStyle,role:`none`},t)}),t(d.action,e=>{let t=this.action?u([this.action()]):e;return t&&y(`div`,{class:`${a}-card__action`,role:`none`},t)}))}});export{C as n,O as t};
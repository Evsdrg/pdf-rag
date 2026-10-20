import{B as e,Bt as t,D as n,F as r,Ft as i,Ht as a,In as o,Mt as s,Nn as c,Ot as l,P as u,S as d,U as f,Ut as p,Vt as m,Wt as h,bt as g,dn as _,g as v,ln as y,nn as b,q as x,v as S,w as C,zt as w}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{j as T}from"./api-Bfr7BT7g.js";import{t as E}from"./index-BFmhv3ZW.js";function D(e){let{primaryColor:t,opacityDisabled:n,borderRadius:r,textColor3:i}=e;return Object.assign(Object.assign({},E),{iconColor:i,textColor:`white`,loadingColor:t,opacityDisabled:n,railColor:`rgba(0, 0, 0, .14)`,railColorActive:t,buttonBoxShadow:`0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)`,buttonColor:`#FFF`,railBorderRadiusSmall:r,railBorderRadiusMedium:r,railBorderRadiusLarge:r,buttonBorderRadiusSmall:r,buttonBorderRadiusMedium:r,buttonBorderRadiusLarge:r,boxShadowFocus:`0 0 0 2px ${l(t,{alpha:.2})}`})}var O={name:`Switch`,common:v,self:D},k=t(`switch`,`
 height: var(--n-height);
 min-width: var(--n-width);
 vertical-align: middle;
 user-select: none;
 -webkit-user-select: none;
 display: inline-flex;
 outline: none;
 justify-content: center;
 align-items: center;
`,[m(`children-placeholder`,`
 height: var(--n-rail-height);
 display: flex;
 flex-direction: column;
 overflow: hidden;
 pointer-events: none;
 visibility: hidden;
 `),m(`rail-placeholder`,`
 display: flex;
 flex-wrap: none;
 `),m(`button-placeholder`,`
 width: calc(1.75 * var(--n-rail-height));
 height: var(--n-rail-height);
 `),t(`base-loading`,`
 position: absolute;
 top: 50%;
 left: 50%;
 transform: translateX(-50%) translateY(-50%);
 font-size: calc(var(--n-button-width) - 4px);
 color: var(--n-loading-color);
 transition: color .3s var(--n-bezier);
 `,[d({left:`50%`,top:`50%`,originalTransform:`translateX(-50%) translateY(-50%)`})]),m(`checked, unchecked`,`
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 box-sizing: border-box;
 position: absolute;
 white-space: nowrap;
 top: 0;
 bottom: 0;
 display: flex;
 align-items: center;
 line-height: 1;
 `),m(`checked`,`
 right: 0;
 padding-right: calc(1.25 * var(--n-rail-height) - var(--n-offset));
 `),m(`unchecked`,`
 left: 0;
 justify-content: flex-end;
 padding-left: calc(1.25 * var(--n-rail-height) - var(--n-offset));
 `),w(`&:focus`,[m(`rail`,`
 box-shadow: var(--n-box-shadow-focus);
 `)]),a(`round`,[m(`rail`,`border-radius: calc(var(--n-rail-height) / 2);`,[m(`button`,`border-radius: calc(var(--n-button-height) / 2);`)])]),p(`disabled`,[p(`icon`,[a(`rubber-band`,[a(`pressed`,[m(`rail`,[m(`button`,`max-width: var(--n-button-width-pressed);`)])]),m(`rail`,[w(`&:active`,[m(`button`,`max-width: var(--n-button-width-pressed);`)])]),a(`active`,[a(`pressed`,[m(`rail`,[m(`button`,`left: calc(100% - var(--n-offset) - var(--n-button-width-pressed));`)])]),m(`rail`,[w(`&:active`,[m(`button`,`left: calc(100% - var(--n-offset) - var(--n-button-width-pressed));`)])])])])])]),a(`active`,[m(`rail`,[m(`button`,`left: calc(100% - var(--n-button-width) - var(--n-offset))`)])]),m(`rail`,`
 overflow: hidden;
 height: var(--n-rail-height);
 min-width: var(--n-rail-width);
 border-radius: var(--n-rail-border-radius);
 cursor: pointer;
 position: relative;
 transition:
 opacity .3s var(--n-bezier),
 background .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-rail-color);
 `,[m(`button-icon`,`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 font-size: calc(var(--n-button-height) - 4px);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 display: flex;
 justify-content: center;
 align-items: center;
 line-height: 1;
 `,[d()]),m(`button`,`
 align-items: center; 
 top: var(--n-offset);
 left: var(--n-offset);
 height: var(--n-button-height);
 width: var(--n-button-width-pressed);
 max-width: var(--n-button-width);
 border-radius: var(--n-button-border-radius);
 background-color: var(--n-button-color);
 box-shadow: var(--n-button-box-shadow);
 box-sizing: border-box;
 cursor: inherit;
 content: "";
 position: absolute;
 transition:
 background-color .3s var(--n-bezier),
 left .3s var(--n-bezier),
 opacity .3s var(--n-bezier),
 max-width .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 `)]),a(`active`,[m(`rail`,`background-color: var(--n-rail-color-active);`)]),a(`loading`,[m(`rail`,`
 cursor: wait;
 `)]),a(`disabled`,[m(`rail`,`
 cursor: not-allowed;
 opacity: .5;
 `)])]),A=Object.assign(Object.assign({},n.props),{size:String,value:{type:[String,Number,Boolean],default:void 0},loading:Boolean,defaultValue:{type:[String,Number,Boolean],default:!1},disabled:{type:Boolean,default:void 0},round:{type:Boolean,default:!0},"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],checkedValue:{type:[String,Number,Boolean],default:!0},uncheckedValue:{type:[String,Number,Boolean],default:!1},railStyle:Function,rubberBand:{type:Boolean,default:!0},spinProps:Object,onChange:[Function,Array]}),j,M=y({name:`Switch`,props:A,slots:Object,setup(e){j===void 0&&(j=typeof CSS<`u`?CSS.supports!==void 0&&CSS.supports(`width`,`max(1px)`):!0);let{mergedClsPrefixRef:t,inlineThemeDisabled:a,mergedComponentPropsRef:l}=r(e),d=n(`Switch`,`-switch`,k,O,e,t),f=T(e,{mergedSize(t){return e.size===void 0?t?t.mergedSize.value:l?.value?.Switch?.size||`medium`:e.size}}),{mergedSizeRef:p,mergedDisabledRef:m}=f,_=c(e.defaultValue),v=o(e,`value`),y=g(v,_),S=b(()=>y.value===e.checkedValue),C=c(!1),w=c(!1),E=b(()=>{let{railStyle:t}=e;if(t)return t({focused:w.value,checked:S.value})});function D(t){let{"onUpdate:value":n,onChange:r,onUpdateValue:i}=e,{nTriggerFormInput:a,nTriggerFormChange:o}=f;n&&x(n,t),i&&x(i,t),r&&x(r,t),_.value=t,a(),o()}function A(){let{nTriggerFormFocus:e}=f;e()}function M(){let{nTriggerFormBlur:e}=f;e()}function N(){e.loading||m.value||(y.value===e.checkedValue?D(e.uncheckedValue):D(e.checkedValue))}function P(){w.value=!0,A()}function F(){w.value=!1,M(),C.value=!1}function I(t){e.loading||m.value||t.key===` `&&(y.value===e.checkedValue?D(e.uncheckedValue):D(e.checkedValue),C.value=!1)}function L(t){e.loading||m.value||t.key===` `&&(t.preventDefault(),C.value=!0)}let R=b(()=>{let{value:e}=p,{self:{opacityDisabled:t,railColor:n,railColorActive:r,buttonBoxShadow:a,buttonColor:o,boxShadowFocus:c,loadingColor:l,textColor:u,iconColor:f,[h(`buttonHeight`,e)]:m,[h(`buttonWidth`,e)]:g,[h(`buttonWidthPressed`,e)]:_,[h(`railHeight`,e)]:v,[h(`railWidth`,e)]:y,[h(`railBorderRadius`,e)]:b,[h(`buttonBorderRadius`,e)]:x},common:{cubicBezierEaseInOut:S}}=d.value,C,w,T;return j?(C=`calc((${v} - ${m}) / 2)`,w=`max(${v}, ${m})`,T=`max(${y}, calc(${y} + ${m} - ${v}))`):(C=i((s(v)-s(m))/2),w=i(Math.max(s(v),s(m))),T=s(v)>s(m)?y:i(s(y)+s(m)-s(v))),{"--n-bezier":S,"--n-button-border-radius":x,"--n-button-box-shadow":a,"--n-button-color":o,"--n-button-width":g,"--n-button-width-pressed":_,"--n-button-height":m,"--n-height":w,"--n-offset":C,"--n-opacity-disabled":t,"--n-rail-border-radius":b,"--n-rail-color":n,"--n-rail-color-active":r,"--n-rail-height":v,"--n-rail-width":y,"--n-width":T,"--n-box-shadow-focus":c,"--n-loading-color":l,"--n-text-color":u,"--n-icon-color":f}}),z=a?u(`switch`,b(()=>p.value[0]),R,e):void 0;return{handleClick:N,handleBlur:F,handleFocus:P,handleKeyup:I,handleKeydown:L,mergedRailStyle:E,pressed:C,mergedClsPrefix:t,mergedValue:y,checked:S,mergedDisabled:m,cssVars:a?void 0:R,themeClass:z?.themeClass,onRender:z?.onRender}},render(){let{mergedClsPrefix:t,mergedDisabled:n,checked:r,mergedRailStyle:i,onRender:a,$slots:o}=this;a?.();let{checked:s,unchecked:c,icon:l,"checked-icon":u,"unchecked-icon":d}=o,p=!(e(l)&&e(u)&&e(d));return _(`div`,{role:`switch`,"aria-checked":r,class:[`${t}-switch`,this.themeClass,p&&`${t}-switch--icon`,r&&`${t}-switch--active`,n&&`${t}-switch--disabled`,this.round&&`${t}-switch--round`,this.loading&&`${t}-switch--loading`,this.pressed&&`${t}-switch--pressed`,this.rubberBand&&`${t}-switch--rubber-band`],tabindex:this.mergedDisabled?void 0:0,style:this.cssVars,onClick:this.handleClick,onFocus:this.handleFocus,onBlur:this.handleBlur,onKeyup:this.handleKeyup,onKeydown:this.handleKeydown},_(`div`,{class:`${t}-switch__rail`,"aria-hidden":`true`,style:i},f(s,e=>f(c,n=>e||n?_(`div`,{"aria-hidden":!0,class:`${t}-switch__children-placeholder`},_(`div`,{class:`${t}-switch__rail-placeholder`},_(`div`,{class:`${t}-switch__button-placeholder`}),e),_(`div`,{class:`${t}-switch__rail-placeholder`},_(`div`,{class:`${t}-switch__button-placeholder`}),n)):null)),_(`div`,{class:`${t}-switch__button`},f(l,e=>f(u,n=>f(d,r=>_(C,null,{default:()=>this.loading?_(S,Object.assign({key:`loading`,clsPrefix:t,strokeWidth:20},this.spinProps)):this.checked&&(n||e)?_(`div`,{class:`${t}-switch__button-icon`,key:n?`checked-icon`:`icon`},n||e):!this.checked&&(r||e)?_(`div`,{class:`${t}-switch__button-icon`,key:r?`unchecked-icon`:`icon`},r||e):null})))),f(s,e=>e&&_(`div`,{key:`checked`,class:`${t}-switch__checked`},e)),f(c,e=>e&&_(`div`,{key:`unchecked`,class:`${t}-switch__unchecked`},e)))))}});export{M as t};
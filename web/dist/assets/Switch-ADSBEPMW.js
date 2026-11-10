import{Ct as e,E as t,Ft as n,G as r,Gt as i,H as a,Ht as o,I as s,In as c,Kt as l,L as u,Rt as d,Ut as f,Wt as p,X as m,an as h,b as g,fn as _,jt as v,k as y,mn as b,qt as x,v as S,w as C,zn as w}from"./_plugin-vue_export-helper-BL3uulyl.js";import{N as T}from"./api-Dd-BvpDC.js";import{t as E}from"./index-D0nxnmu2.js";function D(e){let{primaryColor:t,opacityDisabled:n,borderRadius:r,textColor3:i}=e;return Object.assign(Object.assign({},E),{iconColor:i,textColor:`white`,loadingColor:t,opacityDisabled:n,railColor:`rgba(0, 0, 0, .14)`,railColorActive:t,buttonBoxShadow:`0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)`,buttonColor:`#FFF`,railBorderRadiusSmall:r,railBorderRadiusMedium:r,railBorderRadiusLarge:r,buttonBorderRadiusSmall:r,buttonBorderRadiusMedium:r,buttonBorderRadiusLarge:r,boxShadowFocus:`0 0 0 2px ${v(t,{alpha:.2})}`})}var O={name:`Switch`,common:S,self:D},k=f(`switch`,`
 height: var(--n-height);
 min-width: var(--n-width);
 vertical-align: middle;
 user-select: none;
 -webkit-user-select: none;
 display: inline-flex;
 outline: none;
 justify-content: center;
 align-items: center;
`,[p(`children-placeholder`,`
 height: var(--n-rail-height);
 display: flex;
 flex-direction: column;
 overflow: hidden;
 pointer-events: none;
 visibility: hidden;
 `),p(`rail-placeholder`,`
 display: flex;
 flex-wrap: none;
 `),p(`button-placeholder`,`
 width: calc(1.75 * var(--n-rail-height));
 height: var(--n-rail-height);
 `),f(`base-loading`,`
 position: absolute;
 top: 50%;
 left: 50%;
 transform: translateX(-50%) translateY(-50%);
 font-size: calc(var(--n-button-width) - 4px);
 color: var(--n-loading-color);
 transition: color .3s var(--n-bezier);
 `,[C({left:`50%`,top:`50%`,originalTransform:`translateX(-50%) translateY(-50%)`})]),p(`checked, unchecked`,`
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
 `),p(`checked`,`
 right: 0;
 padding-right: calc(1.25 * var(--n-rail-height) - var(--n-offset));
 `),p(`unchecked`,`
 left: 0;
 justify-content: flex-end;
 padding-left: calc(1.25 * var(--n-rail-height) - var(--n-offset));
 `),o(`&:focus`,[p(`rail`,`
 box-shadow: var(--n-box-shadow-focus);
 `)]),i(`round`,[p(`rail`,`border-radius: calc(var(--n-rail-height) / 2);`,[p(`button`,`border-radius: calc(var(--n-button-height) / 2);`)])]),l(`disabled`,[l(`icon`,[i(`rubber-band`,[i(`pressed`,[p(`rail`,[p(`button`,`max-width: var(--n-button-width-pressed);`)])]),p(`rail`,[o(`&:active`,[p(`button`,`max-width: var(--n-button-width-pressed);`)])]),i(`active`,[i(`pressed`,[p(`rail`,[p(`button`,`left: calc(100% - var(--n-offset) - var(--n-button-width-pressed));`)])]),p(`rail`,[o(`&:active`,[p(`button`,`left: calc(100% - var(--n-offset) - var(--n-button-width-pressed));`)])])])])])]),i(`active`,[p(`rail`,[p(`button`,`left: calc(100% - var(--n-button-width) - var(--n-offset))`)])]),p(`rail`,`
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
 `,[p(`button-icon`,`
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
 `,[C()]),p(`button`,`
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
 `)]),i(`active`,[p(`rail`,`background-color: var(--n-rail-color-active);`)]),i(`loading`,[p(`rail`,`
 cursor: wait;
 `)]),i(`disabled`,[p(`rail`,`
 cursor: not-allowed;
 opacity: .5;
 `)])]),A=Object.assign(Object.assign({},y.props),{size:String,value:{type:[String,Number,Boolean],default:void 0},loading:Boolean,defaultValue:{type:[String,Number,Boolean],default:!1},disabled:{type:Boolean,default:void 0},round:{type:Boolean,default:!0},"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],checkedValue:{type:[String,Number,Boolean],default:!0},uncheckedValue:{type:[String,Number,Boolean],default:!1},railStyle:Function,rubberBand:{type:Boolean,default:!0},spinProps:Object,onChange:[Function,Array]}),j,M=_({name:`Switch`,props:A,slots:Object,setup(t){j===void 0&&(j=typeof CSS<`u`?CSS.supports!==void 0&&CSS.supports(`width`,`max(1px)`):!0);let{mergedClsPrefixRef:r,inlineThemeDisabled:i,mergedComponentPropsRef:a}=u(t),o=y(`Switch`,`-switch`,k,O,t,r),l=T(t,{mergedSize(e){return t.size===void 0?e?e.mergedSize.value:a?.value?.Switch?.size||`medium`:t.size}}),{mergedSizeRef:f,mergedDisabledRef:p}=l,g=c(t.defaultValue),_=w(t,`value`),v=e(_,g),b=h(()=>v.value===t.checkedValue),S=c(!1),C=c(!1),E=h(()=>{let{railStyle:e}=t;if(e)return e({focused:C.value,checked:b.value})});function D(e){let{"onUpdate:value":n,onChange:r,onUpdateValue:i}=t,{nTriggerFormInput:a,nTriggerFormChange:o}=l;n&&m(n,e),i&&m(i,e),r&&m(r,e),g.value=e,a(),o()}function A(){let{nTriggerFormFocus:e}=l;e()}function M(){let{nTriggerFormBlur:e}=l;e()}function N(){t.loading||p.value||(v.value===t.checkedValue?D(t.uncheckedValue):D(t.checkedValue))}function P(){C.value=!0,A()}function F(){C.value=!1,M(),S.value=!1}function I(e){t.loading||p.value||e.key===` `&&(v.value===t.checkedValue?D(t.uncheckedValue):D(t.checkedValue),S.value=!1)}function L(e){t.loading||p.value||e.key===` `&&(e.preventDefault(),S.value=!0)}let R=h(()=>{let{value:e}=f,{self:{opacityDisabled:t,railColor:r,railColorActive:i,buttonBoxShadow:a,buttonColor:s,boxShadowFocus:c,loadingColor:l,textColor:u,iconColor:p,[x(`buttonHeight`,e)]:m,[x(`buttonWidth`,e)]:h,[x(`buttonWidthPressed`,e)]:g,[x(`railHeight`,e)]:_,[x(`railWidth`,e)]:v,[x(`railBorderRadius`,e)]:y,[x(`buttonBorderRadius`,e)]:b},common:{cubicBezierEaseInOut:S}}=o.value,C,w,T;return j?(C=`calc((${_} - ${m}) / 2)`,w=`max(${_}, ${m})`,T=`max(${v}, calc(${v} + ${m} - ${_}))`):(C=d((n(_)-n(m))/2),w=d(Math.max(n(_),n(m))),T=n(_)>n(m)?v:d(n(v)+n(m)-n(_))),{"--n-bezier":S,"--n-button-border-radius":b,"--n-button-box-shadow":a,"--n-button-color":s,"--n-button-width":h,"--n-button-width-pressed":g,"--n-button-height":m,"--n-height":w,"--n-offset":C,"--n-opacity-disabled":t,"--n-rail-border-radius":y,"--n-rail-color":r,"--n-rail-color-active":i,"--n-rail-height":_,"--n-rail-width":v,"--n-width":T,"--n-box-shadow-focus":c,"--n-loading-color":l,"--n-text-color":u,"--n-icon-color":p}}),z=i?s(`switch`,h(()=>f.value[0]),R,t):void 0;return{handleClick:N,handleBlur:F,handleFocus:P,handleKeyup:I,handleKeydown:L,mergedRailStyle:E,pressed:S,mergedClsPrefix:r,mergedValue:v,checked:b,mergedDisabled:p,cssVars:i?void 0:R,themeClass:z?.themeClass,onRender:z?.onRender}},render(){let{mergedClsPrefix:e,mergedDisabled:n,checked:i,mergedRailStyle:o,onRender:s,$slots:c}=this;s?.();let{checked:l,unchecked:u,icon:d,"checked-icon":f,"unchecked-icon":p}=c,m=!(a(d)&&a(f)&&a(p));return b(`div`,{role:`switch`,"aria-checked":i,class:[`${e}-switch`,this.themeClass,m&&`${e}-switch--icon`,i&&`${e}-switch--active`,n&&`${e}-switch--disabled`,this.round&&`${e}-switch--round`,this.loading&&`${e}-switch--loading`,this.pressed&&`${e}-switch--pressed`,this.rubberBand&&`${e}-switch--rubber-band`],tabindex:this.mergedDisabled?void 0:0,style:this.cssVars,onClick:this.handleClick,onFocus:this.handleFocus,onBlur:this.handleBlur,onKeyup:this.handleKeyup,onKeydown:this.handleKeydown},b(`div`,{class:`${e}-switch__rail`,"aria-hidden":`true`,style:o},r(l,t=>r(u,n=>t||n?b(`div`,{"aria-hidden":!0,class:`${e}-switch__children-placeholder`},b(`div`,{class:`${e}-switch__rail-placeholder`},b(`div`,{class:`${e}-switch__button-placeholder`}),t),b(`div`,{class:`${e}-switch__rail-placeholder`},b(`div`,{class:`${e}-switch__button-placeholder`}),n)):null)),b(`div`,{class:`${e}-switch__button`},r(d,n=>r(f,i=>r(p,r=>b(t,null,{default:()=>this.loading?b(g,Object.assign({key:`loading`,clsPrefix:e,strokeWidth:20},this.spinProps)):this.checked&&(i||n)?b(`div`,{class:`${e}-switch__button-icon`,key:i?`checked-icon`:`icon`},i||n):!this.checked&&(r||n)?b(`div`,{class:`${e}-switch__button-icon`,key:r?`unchecked-icon`:`icon`},r||n):null})))),r(l,t=>t&&b(`div`,{key:`checked`,class:`${e}-switch__checked`},t)),r(u,t=>t&&b(`div`,{key:`unchecked`,class:`${e}-switch__unchecked`},t)))))}});export{M as t};
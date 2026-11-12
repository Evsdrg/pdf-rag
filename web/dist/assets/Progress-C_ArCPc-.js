import{$ as e,D as t,Gt as n,Ht as r,I as i,L as a,Ut as o,Xt as s,an as c,fn as l,k as u,mn as d,qt as f}from"./_plugin-vue_export-helper-BL3uulyl.js";import{A as p,D as m,O as h,k as g,n as _}from"./index-DFXqAcyu.js";var v={success:d(h,null),error:d(p,null),warning:d(m,null),info:d(g,null)},y=l({name:`ProgressCircle`,props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(e,{slots:n}){let r=c(()=>{let t=`gradient`,{fillColor:n}=e;return typeof n==`object`?`${t}-${s(JSON.stringify(n))}`:t});function i(t,n,i,a){let{gapDegree:o,viewBoxWidth:s,strokeWidth:c}=e,l=50+c/2,u=`M ${l},${l} m 0,50
      a 50,50 0 1 1 0,-100
      a 50,50 0 1 1 0,100`,d=Math.PI*2*50;return{pathString:u,pathStyle:{stroke:a===`rail`?i:typeof e.fillColor==`object`?`url(#${r.value})`:i,strokeDasharray:`${Math.min(t,100)/100*(d-o)}px ${s*8}px`,strokeDashoffset:`-${o/2}px`,transformOrigin:n?`center`:void 0,transform:n?`rotate(${n}deg)`:void 0}}}let a=()=>{let t=typeof e.fillColor==`object`,n=t?e.fillColor.stops[0]:``,i=t?e.fillColor.stops[1]:``;return t&&d(`defs`,null,d(`linearGradient`,{id:r.value,x1:`0%`,y1:`100%`,x2:`100%`,y2:`0%`},d(`stop`,{offset:`0%`,"stop-color":n}),d(`stop`,{offset:`100%`,"stop-color":i})))};return()=>{let{fillColor:r,railColor:o,strokeWidth:s,offsetDegree:c,status:l,percentage:u,showIndicator:f,indicatorTextColor:p,unit:m,gapOffsetDegree:h,clsPrefix:g}=e,{pathString:_,pathStyle:y}=i(100,0,o,`rail`),{pathString:b,pathStyle:x}=i(u,c,r,`fill`),S=100+s;return d(`div`,{class:`${g}-progress-content`,role:`none`},d(`div`,{class:`${g}-progress-graph`,"aria-hidden":!0},d(`div`,{class:`${g}-progress-graph-circle`,style:{transform:h?`rotate(${h}deg)`:void 0}},d(`svg`,{viewBox:`0 0 ${S} ${S}`},a(),d(`g`,null,d(`path`,{class:`${g}-progress-graph-circle-rail`,d:_,"stroke-width":s,"stroke-linecap":`round`,fill:`none`,style:y})),d(`g`,null,d(`path`,{class:[`${g}-progress-graph-circle-fill`,u===0&&`${g}-progress-graph-circle-fill--empty`],d:b,"stroke-width":s,"stroke-linecap":`round`,fill:`none`,style:x}))))),f?d(`div`,null,n.default?d(`div`,{class:`${g}-progress-custom-content`,role:`none`},n.default()):l==="default"?d(`div`,{class:`${g}-progress-text`,style:{color:p},role:`none`},d(`span`,{class:`${g}-progress-text__percentage`},u),d(`span`,{class:`${g}-progress-text__unit`},m)):d(`div`,{class:`${g}-progress-icon`,"aria-hidden":!0},d(t,{clsPrefix:g},{default:()=>v[l]}))):null)}}}),b={success:d(h,null),error:d(p,null),warning:d(m,null),info:d(g,null)},x=l({name:`ProgressLine`,props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:`%`},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(n,{slots:r}){let i=c(()=>e(n.height)),a=c(()=>typeof n.fillColor==`object`?`linear-gradient(to right, ${n.fillColor?.stops[0]} , ${n.fillColor?.stops[1]})`:n.fillColor),o=c(()=>n.railBorderRadius===void 0?n.height===void 0?``:e(n.height,{c:.5}):e(n.railBorderRadius)),s=c(()=>n.fillBorderRadius===void 0?n.railBorderRadius===void 0?n.height===void 0?``:e(n.height,{c:.5}):e(n.railBorderRadius):e(n.fillBorderRadius));return()=>{let{indicatorPlacement:e,railColor:c,railStyle:l,percentage:u,unit:f,indicatorTextColor:p,status:m,showIndicator:h,processing:g,clsPrefix:_}=n;return d(`div`,{class:`${_}-progress-content`,role:`none`},d(`div`,{class:`${_}-progress-graph`,"aria-hidden":!0},d(`div`,{class:[`${_}-progress-graph-line`,{[`${_}-progress-graph-line--indicator-${e}`]:!0}]},d(`div`,{class:`${_}-progress-graph-line-rail`,style:[{backgroundColor:c,height:i.value,borderRadius:o.value},l]},d(`div`,{class:[`${_}-progress-graph-line-fill`,g&&`${_}-progress-graph-line-fill--processing`],style:{maxWidth:`${n.percentage}%`,background:a.value,height:i.value,lineHeight:i.value,borderRadius:s.value}},e===`inside`?d(`div`,{class:`${_}-progress-graph-line-indicator`,style:{color:p}},r.default?r.default():`${u}${f}`):null)))),h&&e===`outside`?d(`div`,null,r.default?d(`div`,{class:`${_}-progress-custom-content`,style:{color:p},role:`none`},r.default()):m==="default"?d(`div`,{role:`none`,class:`${_}-progress-icon ${_}-progress-icon--as-text`,style:{color:p}},u,f):d(`div`,{class:`${_}-progress-icon`,"aria-hidden":!0},d(t,{clsPrefix:_},{default:()=>b[m]}))):null)}}});function S(e,t,n=100){return`m ${n/2} ${n/2-e} a ${e} ${e} 0 1 1 0 ${2*e} a ${e} ${e} 0 1 1 0 -${2*e}`}var C=l({name:`ProgressMultipleCircle`,props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(e,{slots:t}){let n=c(()=>e.percentage.map((t,n)=>`${Math.PI*t/100*(e.viewBoxWidth/2-e.strokeWidth/2*(1+2*n)-e.circleGap*n)*2}, ${e.viewBoxWidth*8}`)),r=(t,n)=>{let r=e.fillColor[n],i=typeof r==`object`?r.stops[0]:``,a=typeof r==`object`?r.stops[1]:``;return typeof e.fillColor[n]==`object`&&d(`linearGradient`,{id:`gradient-${n}`,x1:`100%`,y1:`0%`,x2:`0%`,y2:`100%`},d(`stop`,{offset:`0%`,"stop-color":i}),d(`stop`,{offset:`100%`,"stop-color":a}))};return()=>{let{viewBoxWidth:i,strokeWidth:a,circleGap:o,showIndicator:s,fillColor:c,railColor:l,railStyle:u,percentage:f,clsPrefix:p}=e;return d(`div`,{class:`${p}-progress-content`,role:`none`},d(`div`,{class:`${p}-progress-graph`,"aria-hidden":!0},d(`div`,{class:`${p}-progress-graph-circle`},d(`svg`,{viewBox:`0 0 ${i} ${i}`},d(`defs`,null,f.map((e,t)=>r(e,t))),f.map((e,t)=>d(`g`,{key:t},d(`path`,{class:`${p}-progress-graph-circle-rail`,d:S(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:[{strokeDashoffset:0,stroke:l[t]},u[t]]}),d(`path`,{class:[`${p}-progress-graph-circle-fill`,e===0&&`${p}-progress-graph-circle-fill--empty`],d:S(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:{strokeDasharray:n.value[t],strokeDashoffset:0,stroke:typeof c[t]==`object`?`url(#gradient-${t})`:c[t]}})))))),s&&t.default?d(`div`,null,d(`div`,{class:`${p}-progress-text`},t.default())):null)}}}),w=r([o(`progress`,{display:`inline-block`},[o(`progress-icon`,`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),n(`line`,`
 width: 100%;
 display: block;
 `,[o(`progress-content`,`
 display: flex;
 align-items: center;
 `,[o(`progress-graph`,{flex:1})]),o(`progress-custom-content`,{marginLeft:`14px`}),o(`progress-icon`,`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[n(`as-text`,`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),n(`circle, dashboard`,{width:`120px`},[o(`progress-custom-content`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),o(`progress-text`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: inherit;
 font-size: var(--n-font-size-circle);
 color: var(--n-text-color-circle);
 font-weight: var(--n-font-weight-circle);
 transition: color .3s var(--n-bezier);
 white-space: nowrap;
 `),o(`progress-icon`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),n(`multiple-circle`,`
 width: 200px;
 color: inherit;
 `,[o(`progress-text`,`
 font-weight: var(--n-font-weight-circle);
 color: var(--n-text-color-circle);
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 transition: color .3s var(--n-bezier);
 `)]),o(`progress-content`,{position:`relative`}),o(`progress-graph`,{position:`relative`},[o(`progress-graph-circle`,[r(`svg`,{verticalAlign:`bottom`}),o(`progress-graph-circle-fill`,`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[n(`empty`,{opacity:0})]),o(`progress-graph-circle-rail`,`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),o(`progress-graph-line`,[n(`indicator-inside`,[o(`progress-graph-line-rail`,`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[o(`progress-graph-line-fill`,`
 height: inherit;
 border-radius: 10px;
 `),o(`progress-graph-line-indicator`,`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),n(`indicator-inside-label`,`
 height: 16px;
 display: flex;
 align-items: center;
 `,[o(`progress-graph-line-rail`,`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),o(`progress-graph-line-indicator`,`
 background: var(--n-fill-color);
 font-size: 12px;
 transform: translateZ(0);
 display: flex;
 vertical-align: middle;
 height: 16px;
 line-height: 16px;
 padding: 0 10px;
 border-radius: 10px;
 position: absolute;
 white-space: nowrap;
 color: var(--n-text-color-line-inner);
 transition:
 right .2s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `)]),o(`progress-graph-line-rail`,`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[o(`progress-graph-line-fill`,`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[n(`processing`,[r(`&::after`,`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),r(`@keyframes progress-processing-animation`,`
 0% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 100%;
 opacity: 1;
 }
 66% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 0;
 opacity: 0;
 }
 100% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 0;
 opacity: 0;
 }
 `)]),T=Object.assign(Object.assign({},u.props),{processing:Boolean,type:{type:String,default:`line`},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:`default`},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:`%`},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:`outside`},indicatorPlacement:{type:String,default:`outside`},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),E=l({name:`Progress`,props:T,setup(e){let t=c(()=>e.indicatorPlacement||e.indicatorPosition),n=c(()=>{if(e.gapDegree||e.gapDegree===0)return e.gapDegree;if(e.type===`dashboard`)return 75}),{mergedClsPrefixRef:r,inlineThemeDisabled:o}=a(e),s=u(`Progress`,`-progress`,w,_,e,r),l=c(()=>{let{status:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontSize:r,fontSizeCircle:i,railColor:a,railHeight:o,iconSizeCircle:c,iconSizeLine:l,textColorCircle:u,textColorLineInner:d,textColorLineOuter:p,lineBgProcessing:m,fontWeightCircle:h,[f(`iconColor`,t)]:g,[f(`fillColor`,t)]:_}}=s.value;return{"--n-bezier":n,"--n-fill-color":_,"--n-font-size":r,"--n-font-size-circle":i,"--n-font-weight-circle":h,"--n-icon-color":g,"--n-icon-size-circle":c,"--n-icon-size-line":l,"--n-line-bg-processing":m,"--n-rail-color":a,"--n-rail-height":o,"--n-text-color-circle":u,"--n-text-color-line-inner":d,"--n-text-color-line-outer":p}}),d=o?i(`progress`,c(()=>e.status[0]),l,e):void 0;return{mergedClsPrefix:r,mergedIndicatorPlacement:t,gapDeg:n,cssVars:o?void 0:l,themeClass:d?.themeClass,onRender:d?.onRender}},render(){let{type:e,cssVars:t,indicatorTextColor:n,showIndicator:r,status:i,railColor:a,railStyle:o,color:s,percentage:c,viewBoxWidth:l,strokeWidth:u,mergedIndicatorPlacement:f,unit:p,borderRadius:m,fillBorderRadius:h,height:g,processing:_,circleGap:v,mergedClsPrefix:b,gapDeg:S,gapOffsetDegree:w,themeClass:T,$slots:E,onRender:D}=this;return D?.(),d(`div`,{class:[T,`${b}-progress`,`${b}-progress--${e}`,`${b}-progress--${i}`],style:t,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":c,role:e===`circle`||e===`line`||e===`dashboard`?`progressbar`:`none`},e===`circle`||e===`dashboard`?d(y,{clsPrefix:b,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,offsetDegree:this.offsetDegree,percentage:c,viewBoxWidth:l,strokeWidth:u,gapDegree:S===void 0?e===`dashboard`?75:0:S,gapOffsetDegree:w,unit:p},E):e===`line`?d(x,{clsPrefix:b,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,percentage:c,processing:_,indicatorPlacement:f,unit:p,fillBorderRadius:h,railBorderRadius:m,height:g},E):e===`multiple-circle`?d(C,{clsPrefix:b,strokeWidth:u,railColor:a,fillColor:s,railStyle:o,viewBoxWidth:l,percentage:c,showIndicator:r,circleGap:v},E):null)}});export{E as t};
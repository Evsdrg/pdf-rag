import{$ as e,Bn as t,D as n,En as r,Gt as i,Hn as a,Ht as o,I as s,In as c,L as l,Sn as u,Un as d,Ut as f,Xt as p,an as m,cn as h,dn as g,fn as _,jn as v,k as y,ln as b,mn as x,on as S,qt as C,rn as w,sn as T,t as E,un as D,wn as O}from"./_plugin-vue_export-helper-BL3uulyl.js";import{A as k,E as A,h as j,j as M,p as N}from"./api-Dd-BvpDC.js";import{t as P}from"./DataTable-DSWXhd3z.js";import{t as F}from"./Card-CZTCyzav.js";import{t as I}from"./Alert-CvWejbcy.js";import{A as L,D as R,O as z,k as B,n as V}from"./index-CzNorles.js";var H={success:x(z,null),error:x(L,null),warning:x(R,null),info:x(B,null)},U=_({name:`ProgressCircle`,props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(e,{slots:t}){let r=m(()=>{let t=`gradient`,{fillColor:n}=e;return typeof n==`object`?`${t}-${p(JSON.stringify(n))}`:t});function i(t,n,i,a){let{gapDegree:o,viewBoxWidth:s,strokeWidth:c}=e,l=50+c/2,u=`M ${l},${l} m 0,50
      a 50,50 0 1 1 0,-100
      a 50,50 0 1 1 0,100`,d=Math.PI*2*50;return{pathString:u,pathStyle:{stroke:a===`rail`?i:typeof e.fillColor==`object`?`url(#${r.value})`:i,strokeDasharray:`${Math.min(t,100)/100*(d-o)}px ${s*8}px`,strokeDashoffset:`-${o/2}px`,transformOrigin:n?`center`:void 0,transform:n?`rotate(${n}deg)`:void 0}}}let a=()=>{let t=typeof e.fillColor==`object`,n=t?e.fillColor.stops[0]:``,i=t?e.fillColor.stops[1]:``;return t&&x(`defs`,null,x(`linearGradient`,{id:r.value,x1:`0%`,y1:`100%`,x2:`100%`,y2:`0%`},x(`stop`,{offset:`0%`,"stop-color":n}),x(`stop`,{offset:`100%`,"stop-color":i})))};return()=>{let{fillColor:r,railColor:o,strokeWidth:s,offsetDegree:c,status:l,percentage:u,showIndicator:d,indicatorTextColor:f,unit:p,gapOffsetDegree:m,clsPrefix:h}=e,{pathString:g,pathStyle:_}=i(100,0,o,`rail`),{pathString:v,pathStyle:y}=i(u,c,r,`fill`),b=100+s;return x(`div`,{class:`${h}-progress-content`,role:`none`},x(`div`,{class:`${h}-progress-graph`,"aria-hidden":!0},x(`div`,{class:`${h}-progress-graph-circle`,style:{transform:m?`rotate(${m}deg)`:void 0}},x(`svg`,{viewBox:`0 0 ${b} ${b}`},a(),x(`g`,null,x(`path`,{class:`${h}-progress-graph-circle-rail`,d:g,"stroke-width":s,"stroke-linecap":`round`,fill:`none`,style:_})),x(`g`,null,x(`path`,{class:[`${h}-progress-graph-circle-fill`,u===0&&`${h}-progress-graph-circle-fill--empty`],d:v,"stroke-width":s,"stroke-linecap":`round`,fill:`none`,style:y}))))),d?x(`div`,null,t.default?x(`div`,{class:`${h}-progress-custom-content`,role:`none`},t.default()):l==="default"?x(`div`,{class:`${h}-progress-text`,style:{color:f},role:`none`},x(`span`,{class:`${h}-progress-text__percentage`},u),x(`span`,{class:`${h}-progress-text__unit`},p)):x(`div`,{class:`${h}-progress-icon`,"aria-hidden":!0},x(n,{clsPrefix:h},{default:()=>H[l]}))):null)}}}),W={success:x(z,null),error:x(L,null),warning:x(R,null),info:x(B,null)},G=_({name:`ProgressLine`,props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:`%`},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(t,{slots:r}){let i=m(()=>e(t.height)),a=m(()=>typeof t.fillColor==`object`?`linear-gradient(to right, ${t.fillColor?.stops[0]} , ${t.fillColor?.stops[1]})`:t.fillColor),o=m(()=>t.railBorderRadius===void 0?t.height===void 0?``:e(t.height,{c:.5}):e(t.railBorderRadius)),s=m(()=>t.fillBorderRadius===void 0?t.railBorderRadius===void 0?t.height===void 0?``:e(t.height,{c:.5}):e(t.railBorderRadius):e(t.fillBorderRadius));return()=>{let{indicatorPlacement:e,railColor:c,railStyle:l,percentage:u,unit:d,indicatorTextColor:f,status:p,showIndicator:m,processing:h,clsPrefix:g}=t;return x(`div`,{class:`${g}-progress-content`,role:`none`},x(`div`,{class:`${g}-progress-graph`,"aria-hidden":!0},x(`div`,{class:[`${g}-progress-graph-line`,{[`${g}-progress-graph-line--indicator-${e}`]:!0}]},x(`div`,{class:`${g}-progress-graph-line-rail`,style:[{backgroundColor:c,height:i.value,borderRadius:o.value},l]},x(`div`,{class:[`${g}-progress-graph-line-fill`,h&&`${g}-progress-graph-line-fill--processing`],style:{maxWidth:`${t.percentage}%`,background:a.value,height:i.value,lineHeight:i.value,borderRadius:s.value}},e===`inside`?x(`div`,{class:`${g}-progress-graph-line-indicator`,style:{color:f}},r.default?r.default():`${u}${d}`):null)))),m&&e===`outside`?x(`div`,null,r.default?x(`div`,{class:`${g}-progress-custom-content`,style:{color:f},role:`none`},r.default()):p==="default"?x(`div`,{role:`none`,class:`${g}-progress-icon ${g}-progress-icon--as-text`,style:{color:f}},u,d):x(`div`,{class:`${g}-progress-icon`,"aria-hidden":!0},x(n,{clsPrefix:g},{default:()=>W[p]}))):null)}}});function K(e,t,n=100){return`m ${n/2} ${n/2-e} a ${e} ${e} 0 1 1 0 ${2*e} a ${e} ${e} 0 1 1 0 -${2*e}`}var q=_({name:`ProgressMultipleCircle`,props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(e,{slots:t}){let n=m(()=>e.percentage.map((t,n)=>`${Math.PI*t/100*(e.viewBoxWidth/2-e.strokeWidth/2*(1+2*n)-e.circleGap*n)*2}, ${e.viewBoxWidth*8}`)),r=(t,n)=>{let r=e.fillColor[n],i=typeof r==`object`?r.stops[0]:``,a=typeof r==`object`?r.stops[1]:``;return typeof e.fillColor[n]==`object`&&x(`linearGradient`,{id:`gradient-${n}`,x1:`100%`,y1:`0%`,x2:`0%`,y2:`100%`},x(`stop`,{offset:`0%`,"stop-color":i}),x(`stop`,{offset:`100%`,"stop-color":a}))};return()=>{let{viewBoxWidth:i,strokeWidth:a,circleGap:o,showIndicator:s,fillColor:c,railColor:l,railStyle:u,percentage:d,clsPrefix:f}=e;return x(`div`,{class:`${f}-progress-content`,role:`none`},x(`div`,{class:`${f}-progress-graph`,"aria-hidden":!0},x(`div`,{class:`${f}-progress-graph-circle`},x(`svg`,{viewBox:`0 0 ${i} ${i}`},x(`defs`,null,d.map((e,t)=>r(e,t))),d.map((e,t)=>x(`g`,{key:t},x(`path`,{class:`${f}-progress-graph-circle-rail`,d:K(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:[{strokeDashoffset:0,stroke:l[t]},u[t]]}),x(`path`,{class:[`${f}-progress-graph-circle-fill`,e===0&&`${f}-progress-graph-circle-fill--empty`],d:K(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:{strokeDasharray:n.value[t],strokeDashoffset:0,stroke:typeof c[t]==`object`?`url(#gradient-${t})`:c[t]}})))))),s&&t.default?x(`div`,null,x(`div`,{class:`${f}-progress-text`},t.default())):null)}}}),J=o([f(`progress`,{display:`inline-block`},[f(`progress-icon`,`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),i(`line`,`
 width: 100%;
 display: block;
 `,[f(`progress-content`,`
 display: flex;
 align-items: center;
 `,[f(`progress-graph`,{flex:1})]),f(`progress-custom-content`,{marginLeft:`14px`}),f(`progress-icon`,`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[i(`as-text`,`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),i(`circle, dashboard`,{width:`120px`},[f(`progress-custom-content`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),f(`progress-text`,`
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
 `),f(`progress-icon`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),i(`multiple-circle`,`
 width: 200px;
 color: inherit;
 `,[f(`progress-text`,`
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
 `)]),f(`progress-content`,{position:`relative`}),f(`progress-graph`,{position:`relative`},[f(`progress-graph-circle`,[o(`svg`,{verticalAlign:`bottom`}),f(`progress-graph-circle-fill`,`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[i(`empty`,{opacity:0})]),f(`progress-graph-circle-rail`,`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),f(`progress-graph-line`,[i(`indicator-inside`,[f(`progress-graph-line-rail`,`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[f(`progress-graph-line-fill`,`
 height: inherit;
 border-radius: 10px;
 `),f(`progress-graph-line-indicator`,`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),i(`indicator-inside-label`,`
 height: 16px;
 display: flex;
 align-items: center;
 `,[f(`progress-graph-line-rail`,`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),f(`progress-graph-line-indicator`,`
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
 `)]),f(`progress-graph-line-rail`,`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[f(`progress-graph-line-fill`,`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[i(`processing`,[o(`&::after`,`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),o(`@keyframes progress-processing-animation`,`
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
 `)]),Y=Object.assign(Object.assign({},y.props),{processing:Boolean,type:{type:String,default:`line`},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:`default`},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:`%`},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:`outside`},indicatorPlacement:{type:String,default:`outside`},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),X=_({name:`Progress`,props:Y,setup(e){let t=m(()=>e.indicatorPlacement||e.indicatorPosition),n=m(()=>{if(e.gapDegree||e.gapDegree===0)return e.gapDegree;if(e.type===`dashboard`)return 75}),{mergedClsPrefixRef:r,inlineThemeDisabled:i}=l(e),a=y(`Progress`,`-progress`,J,V,e,r),o=m(()=>{let{status:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontSize:r,fontSizeCircle:i,railColor:o,railHeight:s,iconSizeCircle:c,iconSizeLine:l,textColorCircle:u,textColorLineInner:d,textColorLineOuter:f,lineBgProcessing:p,fontWeightCircle:m,[C(`iconColor`,t)]:h,[C(`fillColor`,t)]:g}}=a.value;return{"--n-bezier":n,"--n-fill-color":g,"--n-font-size":r,"--n-font-size-circle":i,"--n-font-weight-circle":m,"--n-icon-color":h,"--n-icon-size-circle":c,"--n-icon-size-line":l,"--n-line-bg-processing":p,"--n-rail-color":o,"--n-rail-height":s,"--n-text-color-circle":u,"--n-text-color-line-inner":d,"--n-text-color-line-outer":f}}),c=i?s(`progress`,m(()=>e.status[0]),o,e):void 0;return{mergedClsPrefix:r,mergedIndicatorPlacement:t,gapDeg:n,cssVars:i?void 0:o,themeClass:c?.themeClass,onRender:c?.onRender}},render(){let{type:e,cssVars:t,indicatorTextColor:n,showIndicator:r,status:i,railColor:a,railStyle:o,color:s,percentage:c,viewBoxWidth:l,strokeWidth:u,mergedIndicatorPlacement:d,unit:f,borderRadius:p,fillBorderRadius:m,height:h,processing:g,circleGap:_,mergedClsPrefix:v,gapDeg:y,gapOffsetDegree:b,themeClass:S,$slots:C,onRender:w}=this;return w?.(),x(`div`,{class:[S,`${v}-progress`,`${v}-progress--${e}`,`${v}-progress--${i}`],style:t,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":c,role:e===`circle`||e===`line`||e===`dashboard`?`progressbar`:`none`},e===`circle`||e===`dashboard`?x(U,{clsPrefix:v,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,offsetDegree:this.offsetDegree,percentage:c,viewBoxWidth:l,strokeWidth:u,gapDegree:y===void 0?e===`dashboard`?75:0:y,gapOffsetDegree:b,unit:f},C):e===`line`?x(G,{clsPrefix:v,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,percentage:c,processing:g,indicatorPlacement:d,unit:f,fillBorderRadius:m,railBorderRadius:p,height:h},C):e===`multiple-circle`?x(q,{clsPrefix:v,strokeWidth:u,railColor:a,fillColor:s,railStyle:o,viewBoxWidth:l,percentage:c,showIndicator:r,circleGap:_},C):null)}}),Z={class:`cat-list`},Q=[`title`],$={class:`track`},ee={class:`n`},te={class:`pct`},ne=E(_({__name:`CategoryBar`,props:{items:{}},setup(e){let t=e,n=m(()=>Math.max(1,...t.items.map(e=>e.chunks))),i=m(()=>t.items.reduce((e,t)=>e+t.chunks,0));return(t,o)=>(O(),b(`div`,Z,[(O(!0),b(w,null,r(e.items,e=>(O(),b(`div`,{key:e.name,class:`cat`},[S(`span`,{class:`name`,title:e.name},d(e.name),9,Q),S(`div`,$,[S(`div`,{class:`fill`,style:a({width:e.chunks/n.value*100+`%`})},null,4)]),S(`span`,ee,d(e.chunks),1),S(`span`,te,d(i.value?Math.round(e.chunks/i.value*100):0)+`%`,1)]))),128))]))}}),[[`__scopeId`,`data-v-64fcc915`]]),re={key:0},ie={key:0,class:`empty`},ae={class:`cards`},oe={class:`card`},se={class:`card`},ce={class:`card`},le={class:`card`},ue={class:`grid`},de={class:`hint`},fe=E(_({__name:`LibraryView`,setup(e){let n=c(null),i=c(``);u(async()=>{try{await N(`stats`,j,e=>{n.value=e})}catch(e){i.value=`无法连接后端服务:${e.message}`}});function a(e){return Math.round(e*100)}function o(e){return e>=1?`success`:e>0?`warning`:`error`}let s=[{title:`分区`,key:`slug`,render:e=>e.slug},{title:`模型`,key:`model`,render:e=>e.model||`-`},{title:`维度`,key:`dim`,width:70,render:e=>e.dim??`-`},{title:`块覆盖`,key:`ratio`,width:150,render:e=>x(X,{type:`line`,percentage:a(e.ratio),status:o(e.ratio),height:8,showIndicator:!1})},{title:`块数`,key:`blocks_covered`,width:130,render:e=>`${e.blocks_covered} / ${e.blocks_total}`},{title:`文件`,key:`files_covered`,width:110,render:e=>`${e.files_covered} / ${e.files_total}`},{title:`部分覆盖`,key:`files_partial`,width:100,render:e=>e.files_partial?x(k,{size:`small`,type:`warning`,round:!0},()=>`${e.files_partial} 份`):`-`}];function l(e){return!!n.value?.vectors?.selected.includes(e)}let f=[{title:`时间`,key:`time`},{title:`新增`,key:`added`,width:80},{title:`移除`,key:`removed`,width:80},{title:`分块`,key:`chunks`,width:80},{title:`耗时(s)`,key:`elapsed`,width:90}];return(e,a)=>(O(),T(t(A),{show:!n.value&&!i.value},{default:v(()=>[i.value?(O(),b(`div`,re,[g(t(I),{type:`warning`},{default:v(()=>[D(d(i.value),1)]),_:1})])):n.value?(O(),b(w,{key:1},[n.value.indexed?(O(),b(w,{key:1},[S(`div`,ae,[S(`div`,oe,[S(`b`,null,d(n.value.files),1),a[0]||=S(`span`,null,`文档`,-1)]),S(`div`,se,[S(`b`,null,d(n.value.chunks),1),a[1]||=S(`span`,null,`总块数`,-1)]),S(`div`,ce,[S(`b`,null,d(n.value.skipped.length),1),a[2]||=S(`span`,null,`无文本跳过`,-1)]),S(`div`,le,[S(`b`,null,d(n.value.last_index||`-`),1),a[3]||=S(`span`,null,`最后索引`,-1)])]),S(`div`,ue,[g(t(F),{title:`类别分布`,class:`col`},{default:v(()=>[g(ne,{items:n.value.categories},null,8,[`items`])]),_:1}),g(t(F),{title:`索引历史`,class:`col`},{default:v(()=>[n.value.history.length?(O(),T(t(P),{key:0,columns:f,data:n.value.history,size:`small`,bordered:!1},null,8,[`data`])):(O(),T(t(M),{key:1,description:`暂无历史记录`}))]),_:1})]),n.value.vectors?.partitions.length?(O(),T(t(F),{key:0,title:`向量分区`,class:`gap`},{"header-extra":v(()=>[S(`span`,de,` 检索使用:`+d(n.value.vectors.selected.length?n.value.vectors.selected.join(` → `):`无(检查优先级/排除配置)`),1)]),default:v(()=>[g(t(P),{columns:s,data:n.value.vectors.partitions,size:`small`,bordered:!1,"row-props":e=>({class:l(e.slug)?`row-on`:``})},null,8,[`data`,`row-props`]),a[4]||=S(`div`,{class:`hint sub`},` 覆盖率按块统计——向量化的输入单位是块,同一文件可能只有部分块有向量。 「部分覆盖」列显示这类文件数,补跑一次索引可恢复。 `,-1)]),_:1})):h(``,!0),n.value.skipped.length?(O(),T(t(F),{key:1,title:`无文本文件(扫描件,无法索引)`,class:`gap`},{default:v(()=>[(O(!0),b(w,null,r(n.value.skipped,e=>(O(),b(`div`,{key:e,class:`skip`},d(e),1))),128))]),_:1})):h(``,!0)],64)):(O(),b(`div`,ie,[g(t(M),{description:`索引库为空,请先在「索引状态」页点击「增量索引」`})]))],64)):h(``,!0)]),_:1},8,[`show`]))}}),[[`__scopeId`,`data-v-eecadf27`]]);export{fe as default};
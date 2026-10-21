import{Bn as e,Bt as t,Cn as n,D as r,F as i,Ht as a,Ln as o,Nn as s,On as c,P as l,T as u,Wt as d,X as f,an as p,cn as m,dn as h,en as g,in as _,ln as v,nn as y,on as b,qt as x,rn as S,sn as C,t as w,xn as T,yn as E,zn as D,zt as O}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{T as k,f as A,k as j,m as M}from"./api-Bfr7BT7g.js";import{i as N}from"./Select-CL5-NE5w.js";import{t as P}from"./DataTable-LzQpshxd.js";import{t as F}from"./Alert-DsU_kLJD.js";import{t as I}from"./Card-Dlu3EbgK.js";import{A as L,O as R,j as z,k as B,n as V}from"./index-Li7ENe2r.js";var H={success:h(B,null),error:h(z,null),warning:h(R,null),info:h(L,null)},U=v({name:`ProgressCircle`,props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(e,{slots:t}){let n=y(()=>{let t=`gradient`,{fillColor:n}=e;return typeof n==`object`?`${t}-${x(JSON.stringify(n))}`:t});function r(t,r,i,a){let{gapDegree:o,viewBoxWidth:s,strokeWidth:c}=e,l=50+c/2,u=`M ${l},${l} m 0,50
      a 50,50 0 1 1 0,-100
      a 50,50 0 1 1 0,100`,d=Math.PI*2*50;return{pathString:u,pathStyle:{stroke:a===`rail`?i:typeof e.fillColor==`object`?`url(#${n.value})`:i,strokeDasharray:`${Math.min(t,100)/100*(d-o)}px ${s*8}px`,strokeDashoffset:`-${o/2}px`,transformOrigin:r?`center`:void 0,transform:r?`rotate(${r}deg)`:void 0}}}let i=()=>{let t=typeof e.fillColor==`object`,r=t?e.fillColor.stops[0]:``,i=t?e.fillColor.stops[1]:``;return t&&h(`defs`,null,h(`linearGradient`,{id:n.value,x1:`0%`,y1:`100%`,x2:`100%`,y2:`0%`},h(`stop`,{offset:`0%`,"stop-color":r}),h(`stop`,{offset:`100%`,"stop-color":i})))};return()=>{let{fillColor:n,railColor:a,strokeWidth:o,offsetDegree:s,status:c,percentage:l,showIndicator:d,indicatorTextColor:f,unit:p,gapOffsetDegree:m,clsPrefix:g}=e,{pathString:_,pathStyle:v}=r(100,0,a,`rail`),{pathString:y,pathStyle:b}=r(l,s,n,`fill`),x=100+o;return h(`div`,{class:`${g}-progress-content`,role:`none`},h(`div`,{class:`${g}-progress-graph`,"aria-hidden":!0},h(`div`,{class:`${g}-progress-graph-circle`,style:{transform:m?`rotate(${m}deg)`:void 0}},h(`svg`,{viewBox:`0 0 ${x} ${x}`},i(),h(`g`,null,h(`path`,{class:`${g}-progress-graph-circle-rail`,d:_,"stroke-width":o,"stroke-linecap":`round`,fill:`none`,style:v})),h(`g`,null,h(`path`,{class:[`${g}-progress-graph-circle-fill`,l===0&&`${g}-progress-graph-circle-fill--empty`],d:y,"stroke-width":o,"stroke-linecap":`round`,fill:`none`,style:b}))))),d?h(`div`,null,t.default?h(`div`,{class:`${g}-progress-custom-content`,role:`none`},t.default()):c==="default"?h(`div`,{class:`${g}-progress-text`,style:{color:f},role:`none`},h(`span`,{class:`${g}-progress-text__percentage`},l),h(`span`,{class:`${g}-progress-text__unit`},p)):h(`div`,{class:`${g}-progress-icon`,"aria-hidden":!0},h(u,{clsPrefix:g},{default:()=>H[c]}))):null)}}}),W={success:h(B,null),error:h(z,null),warning:h(R,null),info:h(L,null)},G=v({name:`ProgressLine`,props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:`%`},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(e,{slots:t}){let n=y(()=>f(e.height)),r=y(()=>typeof e.fillColor==`object`?`linear-gradient(to right, ${e.fillColor?.stops[0]} , ${e.fillColor?.stops[1]})`:e.fillColor),i=y(()=>e.railBorderRadius===void 0?e.height===void 0?``:f(e.height,{c:.5}):f(e.railBorderRadius)),a=y(()=>e.fillBorderRadius===void 0?e.railBorderRadius===void 0?e.height===void 0?``:f(e.height,{c:.5}):f(e.railBorderRadius):f(e.fillBorderRadius));return()=>{let{indicatorPlacement:o,railColor:s,railStyle:c,percentage:l,unit:d,indicatorTextColor:f,status:p,showIndicator:m,processing:g,clsPrefix:_}=e;return h(`div`,{class:`${_}-progress-content`,role:`none`},h(`div`,{class:`${_}-progress-graph`,"aria-hidden":!0},h(`div`,{class:[`${_}-progress-graph-line`,{[`${_}-progress-graph-line--indicator-${o}`]:!0}]},h(`div`,{class:`${_}-progress-graph-line-rail`,style:[{backgroundColor:s,height:n.value,borderRadius:i.value},c]},h(`div`,{class:[`${_}-progress-graph-line-fill`,g&&`${_}-progress-graph-line-fill--processing`],style:{maxWidth:`${e.percentage}%`,background:r.value,height:n.value,lineHeight:n.value,borderRadius:a.value}},o===`inside`?h(`div`,{class:`${_}-progress-graph-line-indicator`,style:{color:f}},t.default?t.default():`${l}${d}`):null)))),m&&o===`outside`?h(`div`,null,t.default?h(`div`,{class:`${_}-progress-custom-content`,style:{color:f},role:`none`},t.default()):p==="default"?h(`div`,{role:`none`,class:`${_}-progress-icon ${_}-progress-icon--as-text`,style:{color:f}},l,d):h(`div`,{class:`${_}-progress-icon`,"aria-hidden":!0},h(u,{clsPrefix:_},{default:()=>W[p]}))):null)}}});function K(e,t,n=100){return`m ${n/2} ${n/2-e} a ${e} ${e} 0 1 1 0 ${2*e} a ${e} ${e} 0 1 1 0 -${2*e}`}var q=v({name:`ProgressMultipleCircle`,props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(e,{slots:t}){let n=y(()=>e.percentage.map((t,n)=>`${Math.PI*t/100*(e.viewBoxWidth/2-e.strokeWidth/2*(1+2*n)-e.circleGap*n)*2}, ${e.viewBoxWidth*8}`)),r=(t,n)=>{let r=e.fillColor[n],i=typeof r==`object`?r.stops[0]:``,a=typeof r==`object`?r.stops[1]:``;return typeof e.fillColor[n]==`object`&&h(`linearGradient`,{id:`gradient-${n}`,x1:`100%`,y1:`0%`,x2:`0%`,y2:`100%`},h(`stop`,{offset:`0%`,"stop-color":i}),h(`stop`,{offset:`100%`,"stop-color":a}))};return()=>{let{viewBoxWidth:i,strokeWidth:a,circleGap:o,showIndicator:s,fillColor:c,railColor:l,railStyle:u,percentage:d,clsPrefix:f}=e;return h(`div`,{class:`${f}-progress-content`,role:`none`},h(`div`,{class:`${f}-progress-graph`,"aria-hidden":!0},h(`div`,{class:`${f}-progress-graph-circle`},h(`svg`,{viewBox:`0 0 ${i} ${i}`},h(`defs`,null,d.map((e,t)=>r(e,t))),d.map((e,t)=>h(`g`,{key:t},h(`path`,{class:`${f}-progress-graph-circle-rail`,d:K(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:[{strokeDashoffset:0,stroke:l[t]},u[t]]}),h(`path`,{class:[`${f}-progress-graph-circle-fill`,e===0&&`${f}-progress-graph-circle-fill--empty`],d:K(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:{strokeDasharray:n.value[t],strokeDashoffset:0,stroke:typeof c[t]==`object`?`url(#gradient-${t})`:c[t]}})))))),s&&t.default?h(`div`,null,h(`div`,{class:`${f}-progress-text`},t.default())):null)}}}),J=O([t(`progress`,{display:`inline-block`},[t(`progress-icon`,`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),a(`line`,`
 width: 100%;
 display: block;
 `,[t(`progress-content`,`
 display: flex;
 align-items: center;
 `,[t(`progress-graph`,{flex:1})]),t(`progress-custom-content`,{marginLeft:`14px`}),t(`progress-icon`,`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[a(`as-text`,`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),a(`circle, dashboard`,{width:`120px`},[t(`progress-custom-content`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),t(`progress-text`,`
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
 `),t(`progress-icon`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),a(`multiple-circle`,`
 width: 200px;
 color: inherit;
 `,[t(`progress-text`,`
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
 `)]),t(`progress-content`,{position:`relative`}),t(`progress-graph`,{position:`relative`},[t(`progress-graph-circle`,[O(`svg`,{verticalAlign:`bottom`}),t(`progress-graph-circle-fill`,`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[a(`empty`,{opacity:0})]),t(`progress-graph-circle-rail`,`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),t(`progress-graph-line`,[a(`indicator-inside`,[t(`progress-graph-line-rail`,`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[t(`progress-graph-line-fill`,`
 height: inherit;
 border-radius: 10px;
 `),t(`progress-graph-line-indicator`,`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),a(`indicator-inside-label`,`
 height: 16px;
 display: flex;
 align-items: center;
 `,[t(`progress-graph-line-rail`,`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),t(`progress-graph-line-indicator`,`
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
 `)]),t(`progress-graph-line-rail`,`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[t(`progress-graph-line-fill`,`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[a(`processing`,[O(`&::after`,`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),O(`@keyframes progress-processing-animation`,`
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
 `)]),Y=Object.assign(Object.assign({},r.props),{processing:Boolean,type:{type:String,default:`line`},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:`default`},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:`%`},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:`outside`},indicatorPlacement:{type:String,default:`outside`},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),X=v({name:`Progress`,props:Y,setup(e){let t=y(()=>e.indicatorPlacement||e.indicatorPosition),n=y(()=>{if(e.gapDegree||e.gapDegree===0)return e.gapDegree;if(e.type===`dashboard`)return 75}),{mergedClsPrefixRef:a,inlineThemeDisabled:o}=i(e),s=r(`Progress`,`-progress`,J,V,e,a),c=y(()=>{let{status:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontSize:r,fontSizeCircle:i,railColor:a,railHeight:o,iconSizeCircle:c,iconSizeLine:l,textColorCircle:u,textColorLineInner:f,textColorLineOuter:p,lineBgProcessing:m,fontWeightCircle:h,[d(`iconColor`,t)]:g,[d(`fillColor`,t)]:_}}=s.value;return{"--n-bezier":n,"--n-fill-color":_,"--n-font-size":r,"--n-font-size-circle":i,"--n-font-weight-circle":h,"--n-icon-color":g,"--n-icon-size-circle":c,"--n-icon-size-line":l,"--n-line-bg-processing":m,"--n-rail-color":a,"--n-rail-height":o,"--n-text-color-circle":u,"--n-text-color-line-inner":f,"--n-text-color-line-outer":p}}),u=o?l(`progress`,y(()=>e.status[0]),c,e):void 0;return{mergedClsPrefix:a,mergedIndicatorPlacement:t,gapDeg:n,cssVars:o?void 0:c,themeClass:u?.themeClass,onRender:u?.onRender}},render(){let{type:e,cssVars:t,indicatorTextColor:n,showIndicator:r,status:i,railColor:a,railStyle:o,color:s,percentage:c,viewBoxWidth:l,strokeWidth:u,mergedIndicatorPlacement:d,unit:f,borderRadius:p,fillBorderRadius:m,height:g,processing:_,circleGap:v,mergedClsPrefix:y,gapDeg:b,gapOffsetDegree:x,themeClass:S,$slots:C,onRender:w}=this;return w?.(),h(`div`,{class:[S,`${y}-progress`,`${y}-progress--${e}`,`${y}-progress--${i}`],style:t,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":c,role:e===`circle`||e===`line`||e===`dashboard`?`progressbar`:`none`},e===`circle`||e===`dashboard`?h(U,{clsPrefix:y,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,offsetDegree:this.offsetDegree,percentage:c,viewBoxWidth:l,strokeWidth:u,gapDegree:b===void 0?e===`dashboard`?75:0:b,gapOffsetDegree:x,unit:f},C):e===`line`?h(G,{clsPrefix:y,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,percentage:c,processing:_,indicatorPlacement:d,unit:f,fillBorderRadius:m,railBorderRadius:p,height:g},C):e===`multiple-circle`?h(q,{clsPrefix:y,strokeWidth:u,railColor:a,fillColor:s,railStyle:o,viewBoxWidth:l,percentage:c,showIndicator:r,circleGap:v},C):null)}}),Z={class:`cat-list`},Q=[`title`],$={class:`track`},ee={class:`n`},te={class:`pct`},ne=w(v({__name:`CategoryBar`,props:{items:{}},setup(t){let r=t,i=y(()=>Math.max(1,...r.items.map(e=>e.chunks))),a=y(()=>r.items.reduce((e,t)=>e+t.chunks,0));return(r,o)=>(T(),b(`div`,Z,[(T(!0),b(g,null,n(t.items,t=>(T(),b(`div`,{key:t.name,class:`cat`},[S(`span`,{class:`name`,title:t.name},e(t.name),9,Q),S(`div`,$,[S(`div`,{class:`fill`,style:D({width:t.chunks/i.value*100+`%`})},null,4)]),S(`span`,ee,e(t.chunks),1),S(`span`,te,e(a.value?Math.round(t.chunks/a.value*100):0)+`%`,1)]))),128))]))}}),[[`__scopeId`,`data-v-64fcc915`]]),re={key:0},ie={key:0,class:`empty`},ae={class:`cards`},oe={class:`card`},se={class:`card`},ce={class:`card`},le={class:`card`},ue={class:`grid`},de={class:`hint`},fe=w(v({__name:`LibraryView`,setup(t){let r=s(null),i=s(``);E(async()=>{try{await A(`stats`,M,e=>{r.value=e})}catch(e){i.value=`无法连接后端服务:${e.message}`}});function a(e){return Math.round(e*100)}function l(e){return e>=1?`success`:e>0?`warning`:`error`}let u=[{title:`分区`,key:`slug`,render:e=>e.slug},{title:`模型`,key:`model`,render:e=>e.model||`-`},{title:`维度`,key:`dim`,width:70,render:e=>e.dim??`-`},{title:`块覆盖`,key:`ratio`,width:150,render:e=>h(X,{type:`line`,percentage:a(e.ratio),status:l(e.ratio),height:8,showIndicator:!1})},{title:`块数`,key:`blocks_covered`,width:130,render:e=>`${e.blocks_covered} / ${e.blocks_total}`},{title:`文件`,key:`files_covered`,width:110,render:e=>`${e.files_covered} / ${e.files_total}`},{title:`部分覆盖`,key:`files_partial`,width:100,render:e=>e.files_partial?h(j,{size:`small`,type:`warning`,round:!0},()=>`${e.files_partial} 份`):`-`}];function d(e){return!!r.value?.vectors?.selected.includes(e)}let f=[{title:`时间`,key:`time`},{title:`新增`,key:`added`,width:80},{title:`移除`,key:`removed`,width:80},{title:`分块`,key:`chunks`,width:80},{title:`耗时(s)`,key:`elapsed`,width:90}];return(t,a)=>(T(),_(o(k),{show:!r.value&&!i.value},{default:c(()=>[i.value?(T(),b(`div`,re,[m(o(F),{type:`warning`},{default:c(()=>[C(e(i.value),1)]),_:1})])):r.value?(T(),b(g,{key:1},[r.value.indexed?(T(),b(g,{key:1},[S(`div`,ae,[S(`div`,oe,[S(`b`,null,e(r.value.files),1),a[0]||=S(`span`,null,`文档`,-1)]),S(`div`,se,[S(`b`,null,e(r.value.chunks),1),a[1]||=S(`span`,null,`总块数`,-1)]),S(`div`,ce,[S(`b`,null,e(r.value.skipped.length),1),a[2]||=S(`span`,null,`无文本跳过`,-1)]),S(`div`,le,[S(`b`,null,e(r.value.last_index||`-`),1),a[3]||=S(`span`,null,`最后索引`,-1)])]),S(`div`,ue,[m(o(I),{title:`类别分布`,class:`col`},{default:c(()=>[m(ne,{items:r.value.categories},null,8,[`items`])]),_:1}),m(o(I),{title:`索引历史`,class:`col`},{default:c(()=>[r.value.history.length?(T(),_(o(P),{key:0,columns:f,data:r.value.history,size:`small`,bordered:!1},null,8,[`data`])):(T(),_(o(N),{key:1,description:`暂无历史记录`}))]),_:1})]),r.value.vectors?.partitions.length?(T(),_(o(I),{key:0,title:`向量分区`,class:`gap`},{"header-extra":c(()=>[S(`span`,de,` 检索使用:`+e(r.value.vectors.selected.length?r.value.vectors.selected.join(` → `):`无(检查优先级/排除配置)`),1)]),default:c(()=>[m(o(P),{columns:u,data:r.value.vectors.partitions,size:`small`,bordered:!1,"row-props":e=>({class:d(e.slug)?`row-on`:``})},null,8,[`data`,`row-props`]),a[4]||=S(`div`,{class:`hint sub`},` 覆盖率按块统计——向量化的输入单位是块,同一文件可能只有部分块有向量。 「部分覆盖」列显示这类文件数,补跑一次索引可恢复。 `,-1)]),_:1})):p(``,!0),r.value.skipped.length?(T(),_(o(I),{key:1,title:`无文本文件(扫描件,无法索引)`,class:`gap`},{default:c(()=>[(T(!0),b(g,null,n(r.value.skipped,t=>(T(),b(`div`,{key:t,class:`skip`},e(t),1))),128))]),_:1})):p(``,!0)],64)):(T(),b(`div`,ie,[m(o(N),{description:`索引库为空,请先在「索引状态」页点击「增量索引」`})]))],64)):p(``,!0)]),_:1},8,[`show`]))}}),[[`__scopeId`,`data-v-eecadf27`]]);export{fe as default};
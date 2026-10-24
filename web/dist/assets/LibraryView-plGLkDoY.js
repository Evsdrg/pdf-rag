import{Bn as e,Bt as t,D as n,F as r,Gt as i,Jt as a,P as o,Pn as s,Rn as c,Sn as l,T as u,Ut as d,Vn as f,Vt as p,Z as m,an as h,bn as g,cn as _,fn as v,in as y,kn as b,ln as x,on as S,rn as C,sn as w,t as T,tn as E,un as D,wn as O}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{T as k,f as A,k as j,m as ee}from"./api-GVzHhqB2.js";import{a as M}from"./Select-CQJzCxls.js";import{t as N}from"./DataTable-CTmR3_qc.js";import{t as P}from"./Card-Ciq6SqEJ.js";import{t as F}from"./Alert-xz8bQa_E.js";import{A as I,O as L,j as R,k as z,n as B}from"./index-ejBjBNv_.js";var V={success:v(z,null),error:v(R,null),warning:v(L,null),info:v(I,null)},H=D({name:`ProgressCircle`,props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(e,{slots:t}){let n=C(()=>{let t=`gradient`,{fillColor:n}=e;return typeof n==`object`?`${t}-${a(JSON.stringify(n))}`:t});function r(t,r,i,a){let{gapDegree:o,viewBoxWidth:s,strokeWidth:c}=e,l=50+c/2,u=`M ${l},${l} m 0,50
      a 50,50 0 1 1 0,-100
      a 50,50 0 1 1 0,100`,d=Math.PI*2*50;return{pathString:u,pathStyle:{stroke:a===`rail`?i:typeof e.fillColor==`object`?`url(#${n.value})`:i,strokeDasharray:`${Math.min(t,100)/100*(d-o)}px ${s*8}px`,strokeDashoffset:`-${o/2}px`,transformOrigin:r?`center`:void 0,transform:r?`rotate(${r}deg)`:void 0}}}let i=()=>{let t=typeof e.fillColor==`object`,r=t?e.fillColor.stops[0]:``,i=t?e.fillColor.stops[1]:``;return t&&v(`defs`,null,v(`linearGradient`,{id:n.value,x1:`0%`,y1:`100%`,x2:`100%`,y2:`0%`},v(`stop`,{offset:`0%`,"stop-color":r}),v(`stop`,{offset:`100%`,"stop-color":i})))};return()=>{let{fillColor:n,railColor:a,strokeWidth:o,offsetDegree:s,status:c,percentage:l,showIndicator:d,indicatorTextColor:f,unit:p,gapOffsetDegree:m,clsPrefix:h}=e,{pathString:g,pathStyle:_}=r(100,0,a,`rail`),{pathString:y,pathStyle:b}=r(l,s,n,`fill`),x=100+o;return v(`div`,{class:`${h}-progress-content`,role:`none`},v(`div`,{class:`${h}-progress-graph`,"aria-hidden":!0},v(`div`,{class:`${h}-progress-graph-circle`,style:{transform:m?`rotate(${m}deg)`:void 0}},v(`svg`,{viewBox:`0 0 ${x} ${x}`},i(),v(`g`,null,v(`path`,{class:`${h}-progress-graph-circle-rail`,d:g,"stroke-width":o,"stroke-linecap":`round`,fill:`none`,style:_})),v(`g`,null,v(`path`,{class:[`${h}-progress-graph-circle-fill`,l===0&&`${h}-progress-graph-circle-fill--empty`],d:y,"stroke-width":o,"stroke-linecap":`round`,fill:`none`,style:b}))))),d?v(`div`,null,t.default?v(`div`,{class:`${h}-progress-custom-content`,role:`none`},t.default()):c==="default"?v(`div`,{class:`${h}-progress-text`,style:{color:f},role:`none`},v(`span`,{class:`${h}-progress-text__percentage`},l),v(`span`,{class:`${h}-progress-text__unit`},p)):v(`div`,{class:`${h}-progress-icon`,"aria-hidden":!0},v(u,{clsPrefix:h},{default:()=>V[c]}))):null)}}}),U={success:v(z,null),error:v(R,null),warning:v(L,null),info:v(I,null)},W=D({name:`ProgressLine`,props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:`%`},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(e,{slots:t}){let n=C(()=>m(e.height)),r=C(()=>typeof e.fillColor==`object`?`linear-gradient(to right, ${e.fillColor?.stops[0]} , ${e.fillColor?.stops[1]})`:e.fillColor),i=C(()=>e.railBorderRadius===void 0?e.height===void 0?``:m(e.height,{c:.5}):m(e.railBorderRadius)),a=C(()=>e.fillBorderRadius===void 0?e.railBorderRadius===void 0?e.height===void 0?``:m(e.height,{c:.5}):m(e.railBorderRadius):m(e.fillBorderRadius));return()=>{let{indicatorPlacement:o,railColor:s,railStyle:c,percentage:l,unit:d,indicatorTextColor:f,status:p,showIndicator:m,processing:h,clsPrefix:g}=e;return v(`div`,{class:`${g}-progress-content`,role:`none`},v(`div`,{class:`${g}-progress-graph`,"aria-hidden":!0},v(`div`,{class:[`${g}-progress-graph-line`,{[`${g}-progress-graph-line--indicator-${o}`]:!0}]},v(`div`,{class:`${g}-progress-graph-line-rail`,style:[{backgroundColor:s,height:n.value,borderRadius:i.value},c]},v(`div`,{class:[`${g}-progress-graph-line-fill`,h&&`${g}-progress-graph-line-fill--processing`],style:{maxWidth:`${e.percentage}%`,background:r.value,height:n.value,lineHeight:n.value,borderRadius:a.value}},o===`inside`?v(`div`,{class:`${g}-progress-graph-line-indicator`,style:{color:f}},t.default?t.default():`${l}${d}`):null)))),m&&o===`outside`?v(`div`,null,t.default?v(`div`,{class:`${g}-progress-custom-content`,style:{color:f},role:`none`},t.default()):p==="default"?v(`div`,{role:`none`,class:`${g}-progress-icon ${g}-progress-icon--as-text`,style:{color:f}},l,d):v(`div`,{class:`${g}-progress-icon`,"aria-hidden":!0},v(u,{clsPrefix:g},{default:()=>U[p]}))):null)}}});function G(e,t,n=100){return`m ${n/2} ${n/2-e} a ${e} ${e} 0 1 1 0 ${2*e} a ${e} ${e} 0 1 1 0 -${2*e}`}var K=D({name:`ProgressMultipleCircle`,props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(e,{slots:t}){let n=C(()=>e.percentage.map((t,n)=>`${Math.PI*t/100*(e.viewBoxWidth/2-e.strokeWidth/2*(1+2*n)-e.circleGap*n)*2}, ${e.viewBoxWidth*8}`)),r=(t,n)=>{let r=e.fillColor[n],i=typeof r==`object`?r.stops[0]:``,a=typeof r==`object`?r.stops[1]:``;return typeof e.fillColor[n]==`object`&&v(`linearGradient`,{id:`gradient-${n}`,x1:`100%`,y1:`0%`,x2:`0%`,y2:`100%`},v(`stop`,{offset:`0%`,"stop-color":i}),v(`stop`,{offset:`100%`,"stop-color":a}))};return()=>{let{viewBoxWidth:i,strokeWidth:a,circleGap:o,showIndicator:s,fillColor:c,railColor:l,railStyle:u,percentage:d,clsPrefix:f}=e;return v(`div`,{class:`${f}-progress-content`,role:`none`},v(`div`,{class:`${f}-progress-graph`,"aria-hidden":!0},v(`div`,{class:`${f}-progress-graph-circle`},v(`svg`,{viewBox:`0 0 ${i} ${i}`},v(`defs`,null,d.map((e,t)=>r(e,t))),d.map((e,t)=>v(`g`,{key:t},v(`path`,{class:`${f}-progress-graph-circle-rail`,d:G(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:[{strokeDashoffset:0,stroke:l[t]},u[t]]}),v(`path`,{class:[`${f}-progress-graph-circle-fill`,e===0&&`${f}-progress-graph-circle-fill--empty`],d:G(i/2-a/2*(1+2*t)-o*t,a,i),"stroke-width":a,"stroke-linecap":`round`,fill:`none`,style:{strokeDasharray:n.value[t],strokeDashoffset:0,stroke:typeof c[t]==`object`?`url(#gradient-${t})`:c[t]}})))))),s&&t.default?v(`div`,null,v(`div`,{class:`${f}-progress-text`},t.default())):null)}}}),q=t([p(`progress`,{display:`inline-block`},[p(`progress-icon`,`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),d(`line`,`
 width: 100%;
 display: block;
 `,[p(`progress-content`,`
 display: flex;
 align-items: center;
 `,[p(`progress-graph`,{flex:1})]),p(`progress-custom-content`,{marginLeft:`14px`}),p(`progress-icon`,`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[d(`as-text`,`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),d(`circle, dashboard`,{width:`120px`},[p(`progress-custom-content`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),p(`progress-text`,`
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
 `),p(`progress-icon`,`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),d(`multiple-circle`,`
 width: 200px;
 color: inherit;
 `,[p(`progress-text`,`
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
 `)]),p(`progress-content`,{position:`relative`}),p(`progress-graph`,{position:`relative`},[p(`progress-graph-circle`,[t(`svg`,{verticalAlign:`bottom`}),p(`progress-graph-circle-fill`,`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[d(`empty`,{opacity:0})]),p(`progress-graph-circle-rail`,`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),p(`progress-graph-line`,[d(`indicator-inside`,[p(`progress-graph-line-rail`,`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[p(`progress-graph-line-fill`,`
 height: inherit;
 border-radius: 10px;
 `),p(`progress-graph-line-indicator`,`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),d(`indicator-inside-label`,`
 height: 16px;
 display: flex;
 align-items: center;
 `,[p(`progress-graph-line-rail`,`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),p(`progress-graph-line-indicator`,`
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
 `)]),p(`progress-graph-line-rail`,`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[p(`progress-graph-line-fill`,`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[d(`processing`,[t(`&::after`,`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),t(`@keyframes progress-processing-animation`,`
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
 `)]),J=Object.assign(Object.assign({},n.props),{processing:Boolean,type:{type:String,default:`line`},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:`default`},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:`%`},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:`outside`},indicatorPlacement:{type:String,default:`outside`},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),Y=D({name:`Progress`,props:J,setup(e){let t=C(()=>e.indicatorPlacement||e.indicatorPosition),a=C(()=>{if(e.gapDegree||e.gapDegree===0)return e.gapDegree;if(e.type===`dashboard`)return 75}),{mergedClsPrefixRef:s,inlineThemeDisabled:c}=r(e),l=n(`Progress`,`-progress`,q,B,e,s),u=C(()=>{let{status:t}=e,{common:{cubicBezierEaseInOut:n},self:{fontSize:r,fontSizeCircle:a,railColor:o,railHeight:s,iconSizeCircle:c,iconSizeLine:u,textColorCircle:d,textColorLineInner:f,textColorLineOuter:p,lineBgProcessing:m,fontWeightCircle:h,[i(`iconColor`,t)]:g,[i(`fillColor`,t)]:_}}=l.value;return{"--n-bezier":n,"--n-fill-color":_,"--n-font-size":r,"--n-font-size-circle":a,"--n-font-weight-circle":h,"--n-icon-color":g,"--n-icon-size-circle":c,"--n-icon-size-line":u,"--n-line-bg-processing":m,"--n-rail-color":o,"--n-rail-height":s,"--n-text-color-circle":d,"--n-text-color-line-inner":f,"--n-text-color-line-outer":p}}),d=c?o(`progress`,C(()=>e.status[0]),u,e):void 0;return{mergedClsPrefix:s,mergedIndicatorPlacement:t,gapDeg:a,cssVars:c?void 0:u,themeClass:d?.themeClass,onRender:d?.onRender}},render(){let{type:e,cssVars:t,indicatorTextColor:n,showIndicator:r,status:i,railColor:a,railStyle:o,color:s,percentage:c,viewBoxWidth:l,strokeWidth:u,mergedIndicatorPlacement:d,unit:f,borderRadius:p,fillBorderRadius:m,height:h,processing:g,circleGap:_,mergedClsPrefix:y,gapDeg:b,gapOffsetDegree:x,themeClass:S,$slots:C,onRender:w}=this;return w?.(),v(`div`,{class:[S,`${y}-progress`,`${y}-progress--${e}`,`${y}-progress--${i}`],style:t,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":c,role:e===`circle`||e===`line`||e===`dashboard`?`progressbar`:`none`},e===`circle`||e===`dashboard`?v(H,{clsPrefix:y,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,offsetDegree:this.offsetDegree,percentage:c,viewBoxWidth:l,strokeWidth:u,gapDegree:b===void 0?e===`dashboard`?75:0:b,gapOffsetDegree:x,unit:f},C):e===`line`?v(W,{clsPrefix:y,status:i,showIndicator:r,indicatorTextColor:n,railColor:a,fillColor:s,railStyle:o,percentage:c,processing:g,indicatorPlacement:d,unit:f,fillBorderRadius:m,railBorderRadius:p,height:h},C):e===`multiple-circle`?v(K,{clsPrefix:y,strokeWidth:u,railColor:a,fillColor:s,railStyle:o,viewBoxWidth:l,percentage:c,showIndicator:r,circleGap:_},C):null)}}),X={class:`cat-list`},Z=[`title`],Q={class:`track`},te={class:`n`},ne={class:`pct`},re=T(D({__name:`CategoryBar`,props:{items:{}},setup(t){let n=t,r=C(()=>Math.max(1,...n.items.map(e=>e.chunks))),i=C(()=>n.items.reduce((e,t)=>e+t.chunks,0));return(n,a)=>(l(),w(`div`,X,[(l(!0),w(E,null,O(t.items,t=>(l(),w(`div`,{key:t.name,class:`cat`},[y(`span`,{class:`name`,title:t.name},f(t.name),9,Z),y(`div`,Q,[y(`div`,{class:`fill`,style:e({width:t.chunks/r.value*100+`%`})},null,4)]),y(`span`,te,f(t.chunks),1),y(`span`,ne,f(i.value?Math.round(t.chunks/i.value*100):0)+`%`,1)]))),128))]))}}),[[`__scopeId`,`data-v-64fcc915`]]),ie={key:0},ae={key:0,class:`empty`},oe={class:`cards`},$={class:`card`},se={class:`card`},ce={class:`card`},le={class:`card`},ue={class:`grid`},de={class:`hint`},fe=T(D({__name:`LibraryView`,setup(e){let t=s(null),n=s(``);g(async()=>{try{await A(`stats`,ee,e=>{t.value=e})}catch(e){n.value=`无法连接后端服务:${e.message}`}});function r(e){return Math.round(e*100)}function i(e){return e>=1?`success`:e>0?`warning`:`error`}let a=[{title:`分区`,key:`slug`,render:e=>e.slug},{title:`模型`,key:`model`,render:e=>e.model||`-`},{title:`维度`,key:`dim`,width:70,render:e=>e.dim??`-`},{title:`块覆盖`,key:`ratio`,width:150,render:e=>v(Y,{type:`line`,percentage:r(e.ratio),status:i(e.ratio),height:8,showIndicator:!1})},{title:`块数`,key:`blocks_covered`,width:130,render:e=>`${e.blocks_covered} / ${e.blocks_total}`},{title:`文件`,key:`files_covered`,width:110,render:e=>`${e.files_covered} / ${e.files_total}`},{title:`部分覆盖`,key:`files_partial`,width:100,render:e=>e.files_partial?v(j,{size:`small`,type:`warning`,round:!0},()=>`${e.files_partial} 份`):`-`}];function o(e){return!!t.value?.vectors?.selected.includes(e)}let u=[{title:`时间`,key:`time`},{title:`新增`,key:`added`,width:80},{title:`移除`,key:`removed`,width:80},{title:`分块`,key:`chunks`,width:80},{title:`耗时(s)`,key:`elapsed`,width:90}];return(e,r)=>(l(),h(c(k),{show:!t.value&&!n.value},{default:b(()=>[n.value?(l(),w(`div`,ie,[x(c(F),{type:`warning`},{default:b(()=>[_(f(n.value),1)]),_:1})])):t.value?(l(),w(E,{key:1},[t.value.indexed?(l(),w(E,{key:1},[y(`div`,oe,[y(`div`,$,[y(`b`,null,f(t.value.files),1),r[0]||=y(`span`,null,`文档`,-1)]),y(`div`,se,[y(`b`,null,f(t.value.chunks),1),r[1]||=y(`span`,null,`总块数`,-1)]),y(`div`,ce,[y(`b`,null,f(t.value.skipped.length),1),r[2]||=y(`span`,null,`无文本跳过`,-1)]),y(`div`,le,[y(`b`,null,f(t.value.last_index||`-`),1),r[3]||=y(`span`,null,`最后索引`,-1)])]),y(`div`,ue,[x(c(P),{title:`类别分布`,class:`col`},{default:b(()=>[x(re,{items:t.value.categories},null,8,[`items`])]),_:1}),x(c(P),{title:`索引历史`,class:`col`},{default:b(()=>[t.value.history.length?(l(),h(c(N),{key:0,columns:u,data:t.value.history,size:`small`,bordered:!1},null,8,[`data`])):(l(),h(c(M),{key:1,description:`暂无历史记录`}))]),_:1})]),t.value.vectors?.partitions.length?(l(),h(c(P),{key:0,title:`向量分区`,class:`gap`},{"header-extra":b(()=>[y(`span`,de,` 检索使用:`+f(t.value.vectors.selected.length?t.value.vectors.selected.join(` → `):`无(检查优先级/排除配置)`),1)]),default:b(()=>[x(c(N),{columns:a,data:t.value.vectors.partitions,size:`small`,bordered:!1,"row-props":e=>({class:o(e.slug)?`row-on`:``})},null,8,[`data`,`row-props`]),r[4]||=y(`div`,{class:`hint sub`},` 覆盖率按块统计——向量化的输入单位是块,同一文件可能只有部分块有向量。 「部分覆盖」列显示这类文件数,补跑一次索引可恢复。 `,-1)]),_:1})):S(``,!0),t.value.skipped.length?(l(),h(c(P),{key:1,title:`无文本文件(扫描件,无法索引)`,class:`gap`},{default:b(()=>[(l(!0),w(E,null,O(t.value.skipped,e=>(l(),w(`div`,{key:e,class:`skip`},f(e),1))),128))]),_:1})):S(``,!0)],64)):(l(),w(`div`,ae,[x(c(M),{description:`索引库为空,请先在「索引状态」页点击「增量索引」`})]))],64)):S(``,!0)]),_:1},8,[`show`]))}}),[[`__scopeId`,`data-v-eecadf27`]]);export{fe as default};
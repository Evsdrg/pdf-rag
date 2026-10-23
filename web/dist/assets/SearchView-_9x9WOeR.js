import{$t as e,D as t,F as n,Ht as r,P as i,Pn as a,Qt as o,Rn as s,Sn as c,Ut as l,Vn as u,Vt as d,Wt as f,an as p,bn as m,cn as h,fn as g,in as _,kn as v,ln as y,on as b,rn as x,sn as S,t as C,tn as w,un as T,wn as E}from"./_plugin-vue_export-helper-CaXOlpYa.js";import{E as D,T as O,k,o as A,s as ee,v as te,w as j}from"./api-GVzHhqB2.js";import{t as M}from"./PageDrawer-CykTIayr.js";import{a as N,r as P,t as F}from"./Select-BRr8OHS-.js";import{t as I}from"./Card-DdG8BZUI.js";import{t as ne}from"./use-message-BGpmsUrK.js";import{t as L}from"./Space-CP8ci0tZ.js";import{t as re}from"./Switch-D0_Xdrdc.js";import{o as R}from"./index-BgAh03Vf.js";var z=d(`divider`,`
 position: relative;
 display: flex;
 width: 100%;
 box-sizing: border-box;
 font-size: 16px;
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
`,[f(`vertical`,`
 margin-top: 24px;
 margin-bottom: 24px;
 `,[f(`no-title`,`
 display: flex;
 align-items: center;
 `)]),r(`title`,`
 display: flex;
 align-items: center;
 margin-left: 12px;
 margin-right: 12px;
 white-space: nowrap;
 font-weight: var(--n-font-weight);
 `),l(`title-position-left`,[r(`line`,[l(`left`,{width:`28px`})])]),l(`title-position-right`,[r(`line`,[l(`right`,{width:`28px`})])]),l(`dashed`,[r(`line`,`
 background-color: #0000;
 height: 0px;
 width: 100%;
 border-style: dashed;
 border-width: 1px 0 0;
 `)]),l(`vertical`,`
 display: inline-block;
 height: 1em;
 margin: 0 8px;
 vertical-align: middle;
 width: 1px;
 `),r(`line`,`
 border: none;
 transition: background-color .3s var(--n-bezier), border-color .3s var(--n-bezier);
 height: 1px;
 width: 100%;
 margin: 0;
 `),f(`dashed`,[r(`line`,{backgroundColor:`var(--n-color)`})]),l(`dashed`,[r(`line`,{borderColor:`var(--n-color)`})]),l(`vertical`,{backgroundColor:`var(--n-color)`})]),B=Object.assign(Object.assign({},t.props),{titlePlacement:{type:String,default:`center`},dashed:Boolean,vertical:Boolean}),V=T({name:`Divider`,props:B,setup(e){let{mergedClsPrefixRef:r,inlineThemeDisabled:a}=n(e),o=t(`Divider`,`-divider`,z,R,e,r),s=x(()=>{let{common:{cubicBezierEaseInOut:e},self:{color:t,textColor:n,fontWeight:r}}=o.value;return{"--n-bezier":e,"--n-color":t,"--n-text-color":n,"--n-font-weight":r}}),c=a?i(`divider`,void 0,s,e):void 0;return{mergedClsPrefix:r,cssVars:a?void 0:s,themeClass:c?.themeClass,onRender:c?.onRender}},render(){var e;let{$slots:t,titlePlacement:n,vertical:r,dashed:i,cssVars:a,mergedClsPrefix:o}=this;return(e=this.onRender)==null||e.call(this),g(`div`,{role:`separator`,class:[`${o}-divider`,this.themeClass,{[`${o}-divider--vertical`]:r,[`${o}-divider--no-title`]:!t.default,[`${o}-divider--dashed`]:i,[`${o}-divider--title-position-${n}`]:t.default&&n}],style:a},r?null:g(`div`,{class:`${o}-divider__line ${o}-divider__line--left`}),!r&&t.default?g(w,null,g(`div`,{class:`${o}-divider__title`},this.$slots),g(`div`,{class:`${o}-divider__line ${o}-divider__line--right`})):null)}}),H={class:`row`},U={class:`row`},W={key:0,class:`hint`},G={key:0,class:`hint`},K={key:1,class:`results`},q={class:`hit-head`},J={class:`loc`},Y={class:`fname`},ie={class:`fpath`},ae={class:`snippet`},X=C(T({__name:`SearchView`,setup(t){let n=ne(),r=a(``),i=a([]),l=a(null),d=a([]),f=a(!1),g=a(!1),C=a(`mixed`),T=a(!0),R=a(8),z=a(``),B=a(JSON.parse(localStorage.getItem(`search_history`)||`[]`)),X=a(null),Z=null,Q=x({get:()=>!!X.value,set:e=>{e||(X.value=null)}});m(async()=>{try{let e=await ee();i.value=e.map(e=>({label:e,value:e}))}catch{n.warning(`无法获取类别列表`)}});function oe(e){let t=[e,...B.value.filter(t=>t!==e)].slice(0,10);B.value=t,localStorage.setItem(`search_history`,JSON.stringify(t))}async function $(e){let t=(e??r.value).trim();if(!t){n.warning(`请输入查询内容`);return}r.value=t,f.value=!0,Z?.abort();let i=new AbortController;Z=i;try{d.value=await j(t,l.value||void 0,R.value,C.value,T.value,z.value.trim()||void 0,0,i.signal),g.value=!0,d.value.length&&oe(t)}catch(e){if(e.name===`AbortError`)return;n.error(`查询失败:${e.message}`)}finally{Z===i&&(f.value=!1,Z=null)}}function se(e){X.value={file:e.file,page:e.page}}function ce(e){let t=e.split(/[\\/]/);return t[t.length-1]}return(t,n)=>(c(),S(w,null,[y(s(I),{title:`检索测试`},{default:v(()=>[y(s(L),{vertical:``,size:12},{default:v(()=>[_(`div`,H,[y(s(P),{value:r.value,"onUpdate:value":n[0]||=e=>r.value=e,size:`large`,placeholder:`输入查询,如: W25Q32 供电电压 / SPI Flash 引脚定义`,clearable:``,onKeyup:n[1]||=o(e=>$(),[`enter`])},null,8,[`value`])]),_(`div`,U,[y(s(L),{align:`center`,wrap:``},{default:v(()=>[y(s(F),{value:l.value,"onUpdate:value":n[2]||=e=>l.value=e,options:i.value,placeholder:`全部类别`,clearable:``,style:{width:`220px`}},null,8,[`value`,`options`]),y(s(P),{value:z.value,"onUpdate:value":n[3]||=e=>z.value=e,size:`small`,placeholder:`限定文档:文件名含,如 QMC6309`,clearable:``,style:{width:`200px`}},null,8,[`value`]),y(s(D),{type:`primary`,loading:f.value,onClick:n[4]||=e=>$()},{default:v(()=>[...n[10]||=[h(`搜索`,-1)]]),_:1},8,[`loading`]),y(s(V),{vertical:``,style:{height:`24px`}}),n[11]||=_(`span`,{class:`opt-lbl`},`条数`,-1),y(s(F),{value:R.value,"onUpdate:value":n[5]||=e=>R.value=e,style:{width:`90px`},options:[{label:`3`,value:3},{label:`5`,value:5},{label:`8`,value:8},{label:`12`,value:12},{label:`20`,value:20}]},null,8,[`value`]),n[12]||=_(`span`,{class:`opt-lbl`},`模式`,-1),y(s(F),{value:C.value,"onUpdate:value":n[6]||=e=>C.value=e,style:{width:`130px`},options:[{label:`混合 (BM25+向量)`,value:`mixed`},{label:`仅全文 BM25`,value:`fts`},{label:`仅语义向量`,value:`vector`}]},null,8,[`value`]),n[13]||=_(`span`,{class:`opt-lbl`},`重排`,-1),y(s(re),{value:T.value,"onUpdate:value":n[7]||=e=>T.value=e},null,8,[`value`])]),_:1})]),B.value.length?(c(),S(w,{key:0},[y(s(L),{size:`small`,wrap:``},{default:v(()=>[n[14]||=_(`span`,{class:`opt-lbl`},`历史:`,-1),(c(!0),S(w,null,E(B.value,e=>(c(),p(s(k),{key:e,size:`small`,style:{cursor:`pointer`},onClick:t=>$(e)},{default:v(()=>[h(u(e),1)]),_:2},1032,[`onClick`]))),128))]),_:1}),y(s(V),{style:{margin:`4px 0`}})],64)):b(``,!0),y(s(O),{show:f.value},{default:v(()=>[g.value?(c(),S(w,{key:1},[d.value.length?(c(),S(`div`,K,[(c(!0),S(w,null,E(d.value,(t,r)=>(c(),p(s(I),{key:r,size:`small`,class:`hit`,onClick:e=>se(t)},{header:v(()=>[_(`div`,q,[y(s(L),{align:`center`,size:`small`},{default:v(()=>[y(s(k),{size:`small`,type:`info`},{default:v(()=>[h(u(t.score),1)]),_:2},1024),t.category?(c(),p(s(k),{key:0,size:`small`,type:`default`},{default:v(()=>[h(u(t.category),1)]),_:2},1024)):b(``,!0),t.model_no?(c(),p(s(k),{key:1,size:`small`,type:`success`},{default:v(()=>[h(u(t.model_no),1)]),_:2},1024)):t.product?(c(),p(s(k),{key:2,size:`small`,type:`success`},{default:v(()=>[h(u(t.product),1)]),_:2},1024)):b(``,!0),t.version?(c(),p(s(k),{key:3,size:`small`,type:`warning`},{default:v(()=>[h(`v`+u(t.version),1)]),_:2},1024)):b(``,!0)]),_:2},1024),y(s(L),{align:`center`,size:`small`},{default:v(()=>[_(`span`,J,`第 `+u(t.page)+` 页`,1),y(s(D),{size:`tiny`,tag:`a`,href:s(te)(t.file,t.page),target:`_blank`,onClick:n[8]||=e(()=>{},[`stop`])},{default:v(()=>[h(u(s(A)(t.file,t.kind)),1)]),_:2},1032,[`href`])]),_:2},1024)])]),default:v(()=>[_(`div`,Y,u(ce(t.file)),1),_(`div`,ie,u(t.file),1),_(`div`,ae,u(t.snippet),1)]),_:2},1032,[`onClick`]))),128))])):(c(),S(`div`,G,[y(s(N),{description:`无命中结果`})]))],64)):(c(),S(`div`,W,[y(s(N),{description:`输入查询并搜索,将混合 BM25 全文 + 语义向量检索`})]))]),_:1},8,[`show`])]),_:1})]),_:1}),y(M,{show:Q.value,"onUpdate:show":n[9]||=e=>Q.value=e,file:X.value?.file??``,page:X.value?.page??1,width:760},null,8,[`show`,`file`,`page`])],64))}}),[[`__scopeId`,`data-v-c9923528`]]);export{X as default};
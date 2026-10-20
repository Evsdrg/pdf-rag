import{Bn as e,Bt as t,Cn as n,D as r,F as i,Ht as a,Ln as o,Nn as s,On as c,P as l,Qt as ee,Ut as u,Vt as d,Zt as te,an as f,cn as p,dn as m,en as h,in as g,ln as _,nn as v,on as y,rn as b,sn as x,t as S,xn as C,yn as w}from"./_plugin-vue_export-helper-kKYb1i6s.js";import{E as T,T as ne,k as E,o as D,s as O,v as k,w as A}from"./api-Bfr7BT7g.js";import{t as j}from"./PageDrawer-Cul-ghW8.js";import{i as M,t as N}from"./Select-Bk1-mE08.js";import{t as P}from"./Input-DAWrBfVg.js";import{t as F}from"./Card-Bp-tWZMj.js";import{n as re,t as I}from"./Space-DTLsBjVt.js";import{t as L}from"./Switch-CERdSBRy.js";import{a as R}from"./index-BFmhv3ZW.js";var z=t(`divider`,`
 position: relative;
 display: flex;
 width: 100%;
 box-sizing: border-box;
 font-size: 16px;
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
`,[u(`vertical`,`
 margin-top: 24px;
 margin-bottom: 24px;
 `,[u(`no-title`,`
 display: flex;
 align-items: center;
 `)]),d(`title`,`
 display: flex;
 align-items: center;
 margin-left: 12px;
 margin-right: 12px;
 white-space: nowrap;
 font-weight: var(--n-font-weight);
 `),a(`title-position-left`,[d(`line`,[a(`left`,{width:`28px`})])]),a(`title-position-right`,[d(`line`,[a(`right`,{width:`28px`})])]),a(`dashed`,[d(`line`,`
 background-color: #0000;
 height: 0px;
 width: 100%;
 border-style: dashed;
 border-width: 1px 0 0;
 `)]),a(`vertical`,`
 display: inline-block;
 height: 1em;
 margin: 0 8px;
 vertical-align: middle;
 width: 1px;
 `),d(`line`,`
 border: none;
 transition: background-color .3s var(--n-bezier), border-color .3s var(--n-bezier);
 height: 1px;
 width: 100%;
 margin: 0;
 `),u(`dashed`,[d(`line`,{backgroundColor:`var(--n-color)`})]),a(`dashed`,[d(`line`,{borderColor:`var(--n-color)`})]),a(`vertical`,{backgroundColor:`var(--n-color)`})]),B=Object.assign(Object.assign({},r.props),{titlePlacement:{type:String,default:`center`},dashed:Boolean,vertical:Boolean}),V=_({name:`Divider`,props:B,setup(e){let{mergedClsPrefixRef:t,inlineThemeDisabled:n}=i(e),a=r(`Divider`,`-divider`,z,R,e,t),o=v(()=>{let{common:{cubicBezierEaseInOut:e},self:{color:t,textColor:n,fontWeight:r}}=a.value;return{"--n-bezier":e,"--n-color":t,"--n-text-color":n,"--n-font-weight":r}}),s=n?l(`divider`,void 0,o,e):void 0;return{mergedClsPrefix:t,cssVars:n?void 0:o,themeClass:s?.themeClass,onRender:s?.onRender}},render(){var e;let{$slots:t,titlePlacement:n,vertical:r,dashed:i,cssVars:a,mergedClsPrefix:o}=this;return(e=this.onRender)==null||e.call(this),m(`div`,{role:`separator`,class:[`${o}-divider`,this.themeClass,{[`${o}-divider--vertical`]:r,[`${o}-divider--no-title`]:!t.default,[`${o}-divider--dashed`]:i,[`${o}-divider--title-position-${n}`]:t.default&&n}],style:a},r?null:m(`div`,{class:`${o}-divider__line ${o}-divider__line--left`}),!r&&t.default?m(h,null,m(`div`,{class:`${o}-divider__title`},this.$slots),m(`div`,{class:`${o}-divider__line ${o}-divider__line--right`})):null)}}),H={class:`row`},U={class:`row`},W={key:0,class:`hint`},G={key:0,class:`hint`},K={key:1,class:`results`},q={class:`hit-head`},J={class:`loc`},Y={class:`fname`},ie={class:`fpath`},ae={class:`snippet`},X=S(_({__name:`SearchView`,setup(t){let r=re(),i=s(``),a=s([]),l=s(null),u=s([]),d=s(!1),m=s(!1),_=s(`mixed`),S=s(!0),R=s(8),z=s(``),B=s(JSON.parse(localStorage.getItem(`search_history`)||`[]`)),X=s(null),Z=null,Q=v({get:()=>!!X.value,set:e=>{e||(X.value=null)}});w(async()=>{try{let e=await O();a.value=e.map(e=>({label:e,value:e}))}catch{r.warning(`无法获取类别列表`)}});function oe(e){let t=[e,...B.value.filter(t=>t!==e)].slice(0,10);B.value=t,localStorage.setItem(`search_history`,JSON.stringify(t))}async function $(e){let t=(e??i.value).trim();if(!t){r.warning(`请输入查询内容`);return}i.value=t,d.value=!0,Z?.abort();let n=new AbortController;Z=n;try{u.value=await A(t,l.value||void 0,R.value,_.value,S.value,z.value.trim()||void 0,0,n.signal),m.value=!0,u.value.length&&oe(t)}catch(e){if(e.name===`AbortError`)return;r.error(`查询失败:${e.message}`)}finally{Z===n&&(d.value=!1,Z=null)}}function se(e){X.value={file:e.file,page:e.page}}function ce(e){let t=e.split(/[\\/]/);return t[t.length-1]}return(t,r)=>(C(),y(h,null,[p(o(F),{title:`检索测试`},{default:c(()=>[p(o(I),{vertical:``,size:12},{default:c(()=>[b(`div`,H,[p(o(P),{value:i.value,"onUpdate:value":r[0]||=e=>i.value=e,size:`large`,placeholder:`输入查询,如: W25Q32 供电电压 / SPI Flash 引脚定义`,clearable:``,onKeyup:r[1]||=te(e=>$(),[`enter`])},null,8,[`value`])]),b(`div`,U,[p(o(I),{align:`center`,wrap:``},{default:c(()=>[p(o(N),{value:l.value,"onUpdate:value":r[2]||=e=>l.value=e,options:a.value,placeholder:`全部类别`,clearable:``,style:{width:`220px`}},null,8,[`value`,`options`]),p(o(P),{value:z.value,"onUpdate:value":r[3]||=e=>z.value=e,size:`small`,placeholder:`限定文档:文件名含,如 QMC6309`,clearable:``,style:{width:`200px`}},null,8,[`value`]),p(o(T),{type:`primary`,loading:d.value,onClick:r[4]||=e=>$()},{default:c(()=>[...r[10]||=[x(`搜索`,-1)]]),_:1},8,[`loading`]),p(o(V),{vertical:``,style:{height:`24px`}}),r[11]||=b(`span`,{class:`opt-lbl`},`条数`,-1),p(o(N),{value:R.value,"onUpdate:value":r[5]||=e=>R.value=e,style:{width:`90px`},options:[{label:`3`,value:3},{label:`5`,value:5},{label:`8`,value:8},{label:`12`,value:12},{label:`20`,value:20}]},null,8,[`value`]),r[12]||=b(`span`,{class:`opt-lbl`},`模式`,-1),p(o(N),{value:_.value,"onUpdate:value":r[6]||=e=>_.value=e,style:{width:`130px`},options:[{label:`混合 (BM25+向量)`,value:`mixed`},{label:`仅全文 BM25`,value:`fts`},{label:`仅语义向量`,value:`vector`}]},null,8,[`value`]),r[13]||=b(`span`,{class:`opt-lbl`},`重排`,-1),p(o(L),{value:S.value,"onUpdate:value":r[7]||=e=>S.value=e},null,8,[`value`])]),_:1})]),B.value.length?(C(),y(h,{key:0},[p(o(I),{size:`small`,wrap:``},{default:c(()=>[r[14]||=b(`span`,{class:`opt-lbl`},`历史:`,-1),(C(!0),y(h,null,n(B.value,t=>(C(),g(o(E),{key:t,size:`small`,style:{cursor:`pointer`},onClick:e=>$(t)},{default:c(()=>[x(e(t),1)]),_:2},1032,[`onClick`]))),128))]),_:1}),p(o(V),{style:{margin:`4px 0`}})],64)):f(``,!0),p(o(ne),{show:d.value},{default:c(()=>[m.value?(C(),y(h,{key:1},[u.value.length?(C(),y(`div`,K,[(C(!0),y(h,null,n(u.value,(t,n)=>(C(),g(o(F),{key:n,size:`small`,class:`hit`,onClick:e=>se(t)},{header:c(()=>[b(`div`,q,[p(o(I),{align:`center`,size:`small`},{default:c(()=>[p(o(E),{size:`small`,type:`info`},{default:c(()=>[x(e(t.score),1)]),_:2},1024),t.category?(C(),g(o(E),{key:0,size:`small`,type:`default`},{default:c(()=>[x(e(t.category),1)]),_:2},1024)):f(``,!0),t.model_no?(C(),g(o(E),{key:1,size:`small`,type:`success`},{default:c(()=>[x(e(t.model_no),1)]),_:2},1024)):t.product?(C(),g(o(E),{key:2,size:`small`,type:`success`},{default:c(()=>[x(e(t.product),1)]),_:2},1024)):f(``,!0),t.version?(C(),g(o(E),{key:3,size:`small`,type:`warning`},{default:c(()=>[x(`v`+e(t.version),1)]),_:2},1024)):f(``,!0)]),_:2},1024),p(o(I),{align:`center`,size:`small`},{default:c(()=>[b(`span`,J,`第 `+e(t.page)+` 页`,1),p(o(T),{size:`tiny`,tag:`a`,href:o(k)(t.file,t.page),target:`_blank`,onClick:r[8]||=ee(()=>{},[`stop`])},{default:c(()=>[x(e(o(D)(t.file,t.kind)),1)]),_:2},1032,[`href`])]),_:2},1024)])]),default:c(()=>[b(`div`,Y,e(ce(t.file)),1),b(`div`,ie,e(t.file),1),b(`div`,ae,e(t.snippet),1)]),_:2},1032,[`onClick`]))),128))])):(C(),y(`div`,G,[p(o(M),{description:`无命中结果`})]))],64)):(C(),y(`div`,W,[p(o(M),{description:`输入查询并搜索,将混合 BM25 全文 + 语义向量检索`})]))]),_:1},8,[`show`])]),_:1})]),_:1}),p(j,{show:Q.value,"onUpdate:show":r[9]||=e=>Q.value=e,file:X.value?.file??``,page:X.value?.page??1,width:760},null,8,[`show`,`file`,`page`])],64))}}),[[`__scopeId`,`data-v-286ae25c`]]);export{X as default};
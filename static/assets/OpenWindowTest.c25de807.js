import{k as _,y as i,z as a,A as $,B as s,F as u,H as t,P as y,C as l,Z as f,X as h,T as g,r as k,S as r}from"./element-plus.5733ce57.js";import{_ as w}from"./index.893f68d1.js";const x=_({name:"SelectPage",props:{isShow:{type:Boolean,default:!1},title:{type:String,default:"\u65B0\u7A97\u53E3"}},emits:["update:show"],setup(e,o){return{close:()=>o.emit("update:show",!e.isShow),slots:o.slots}}}),B={key:0,class:"open-select-mask w-full h-full bg-black bg-opacity-30 z-50 fixed top-0 left-0 flex flex-center"},A={class:"open-select w-11/12 max-w-screen-xl h-5/6 bg-white flex flex-col overflow-x-hidden overflow-y-auto"},E={class:"h-10 flex justify-between items-center px-3 shadow-sm border-b border-gray-100"},S={class:"flex-1 overflow-hidden"},C={key:0,class:"open-select-btn h-12 flex border-t border-gray-100"};function T(e,o,c,m,b,v){const n=i("el-scrollbar");return a(),$(g,{name:"el-fade-in"},{default:s(()=>[e.isShow?(a(),u("div",B,[t("div",A,[t("div",E,[t("span",null,y(e.title),1),t("div",null,[t("i",{class:"el-icon-close cursor-pointer",onClick:o[0]||(o[0]=(...d)=>e.close&&e.close(...d))})])]),t("div",S,[l(n,null,{default:s(()=>[f(e.$slots,"default",{},void 0,!0)]),_:3})]),e.slots.btn?(a(),u("div",C,[f(e.$slots,"btn",{},void 0,!0)])):h("",!0)])])):h("",!0)]),_:3})}var D=w(x,[["render",T],["__scopeId","data-v-9bfe2bca"]]);const N=_({name:"OpenWindowTest",components:{OpenWindow:D},setup(){return{show:k(!1)}}}),V={class:"content"},j=r("\u6253\u5F00\u7A97\u4F53"),F=t("p",{style:{height:"1500px"}},"aaa",-1),O=r("\u9ED8\u8BA4\u6309\u94AE"),W=r("\u9ED8\u8BA4\u6309\u94AE"),z=r("\u9ED8\u8BA4\u6309\u94AE");function P(e,o,c,m,b,v){const n=i("el-button"),d=i("open-window");return a(),u("div",V,[l(n,{onClick:o[0]||(o[0]=p=>e.show=!0)},{default:s(()=>[j]),_:1}),l(d,{show:e.show,"onUpdate:show":o[1]||(o[1]=p=>e.show=p),"is-show":e.show,title:"\u9009\u62E9\u9875"},{btn:s(()=>[l(n,null,{default:s(()=>[O]),_:1}),l(n,null,{default:s(()=>[W]),_:1}),l(n,null,{default:s(()=>[z]),_:1})]),default:s(()=>[F]),_:1},8,["show","is-show"])])}var U=w(N,[["render",P]]);export{U as default};

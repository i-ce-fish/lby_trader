import{h as $,q as c,B as s,O as u,N as f,S as r,z as h,x as l,y as t,D as n,t as a,F as k,P as d,M as o,W as g}from"./element-plus.0596f1e1.js";var x=$({name:"List",props:{data:{type:Array,default:()=>[]},type:{type:String,default:"default"}},setup(){return{}}});const B={key:0},N={class:"flex justify-between items-center"},T={class:"flex items-center"},U={key:0,class:"mr-4"},z={class:"text-sm mb-1"},S={key:1,class:"text-sm mb-1"},V={key:2,class:"text-xs text-gray-500"},j={key:1,class:"component-list-card"},D={key:0,class:"flex items-center py-1 text-black font-medium"},F={class:"px-4 truncate text-base"},L={class:"py-1 h-16 overflow-ellipsis overflow-hidden leading-6"},q={class:"text-sm mb-1"},A={key:1},E={class:"flex items-center justify-between"};function I(i,M,O,P,W,G){const m=c("el-avatar"),p=c("el-tag"),y=c("el-link"),b=c("el-col"),C=c("el-row"),w=c("el-card");return t(),s(u,null,[i.type==="default"?(t(),s("div",B,[(t(!0),s(u,null,f(i.data,(e,_)=>(t(),s("div",{key:_,class:"py-2 border-b hover:bg-gray-100"},[n("div",N,[n("div",T,[e.imgUrl||e.iconClass?(t(),s("div",U,[e.imgUrl?(t(),a(m,{key:0,size:"large",src:e.imgUrl},null,8,["src"])):r("",!0),e.iconClass?(t(),s("i",{key:1,class:k({"text-3xl":!0,[e.iconClass]:!0})},null,2)):r("",!0)])):r("",!0),n("div",null,[e.href?(t(),a(y,{key:0,type:"primary",underline:!1,href:e.href},{default:l(()=>[n("p",z,[d(o(e.subTitle)+" ",1),e.tag?(t(),a(p,{key:0},{default:l(()=>[d(o(e.tag),1)]),_:2},1024)):r("",!0)])]),_:2},1032,["href"])):(t(),s("p",S,[d(o(e.subTitle)+" ",1),e.tag?(t(),a(p,{key:0},{default:l(()=>[d(o(e.tag),1)]),_:2},1024)):r("",!0)])),e.time?(t(),s("p",V,o(e.time),1)):r("",!0)])]),g(i.$slots,"default",{item:e})])]))),128))])):r("",!0),i.type==="card"?(t(),s("div",j,[h(w,{shadow:"never",class:"mb-2"},{header:l(()=>[g(i.$slots,"header")]),default:l(()=>[h(C,null,{default:l(()=>[(t(!0),s(u,null,f(i.data,(e,_)=>(t(),a(b,{key:_,xs:24,sm:12,md:8,class:"c-list-card-body h-40 text-sm text-gray-400"},{default:l(()=>[e.title?(t(),s("div",D,[n("div",null,[e.imgUrl?(t(),a(m,{key:0,size:"small",src:e.imgUrl},null,8,["src"])):r("",!0),e.iconClass?(t(),s("i",{key:1,class:k({"text-3xl":!0,[e.iconClass]:!0})},null,2)):r("",!0)]),n("div",F,o(e.title),1)])):r("",!0),n("div",L,[e.href?(t(),a(y,{key:0,type:"primary",underline:!1,href:e.href},{default:l(()=>[n("p",q,o(e.subTitle),1)]),_:2},1032,["href"])):(t(),s("p",A,o(e.subTitle),1))]),n("div",E,[n("div",null,o(e.tag),1),n("div",null,o(e.time),1)])]),_:2},1024))),128))]),_:1})]),_:3})])):r("",!0)],64)}x.render=I;x.__scopeId="data-v-1bd4ced5";export{x as _};

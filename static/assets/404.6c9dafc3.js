import{h as n,l as d,q as h,y as u,B as p,D as e,M as m,z as v,x as g,J as f,L as b,P as c}from"./element-plus.0596f1e1.js";import{b as k}from"./index.1713b2dc.js";var C="/static/assets/404.538aa4d7.png",S="/static/assets/404_cloud.98e7ac66.png";const t=n({name:"404",setup(){const{color:s}=k().getSetting;return{err404:C,errCloud:S,message:"The webmaster said that you can not enter this page...",color:s}}}),l=()=>{d(s=>({"3e44ae74":s.color.primary}))},r=t.setup;t.setup=r?(s,a)=>(l(),r(s,a)):l;var _=t;const o=s=>(f("data-v-d9293750"),s=s(),b(),s),w={class:"wscn-http404-container"},y={class:"wscn-http404"},B={class:"pic-404"},V=["src"],I=["src"],$=["src"],j=["src"],L={class:"bullshit"},N=o(()=>e("div",{class:"bullshit__oops"},"OOPS!",-1)),P=o(()=>e("div",{class:"bullshit__info"},[c(" All rights reserved "),e("a",{class:"bullshit__info-link",href:"https://wallstreetcn.com",target:"_blank"},"wallstreetcn")],-1)),x={class:"bullshit__headline"},D=o(()=>e("div",{class:"bullshit__info"}," Please check that the URL you entered is correct, or click the button below to return to the homepage. ",-1)),O=c("Back to home");function T(s,a,q,z,A,E){const i=h("router-link");return u(),p("div",w,[e("div",y,[e("div",B,[e("img",{class:"pic-404__parent",src:s.err404,alt:"404"},null,8,V),e("img",{class:"pic-404__child left",src:s.errCloud,alt:"404"},null,8,I),e("img",{class:"pic-404__child mid",src:s.errCloud,alt:"404"},null,8,$),e("img",{class:"pic-404__child right",src:s.errCloud,alt:"404"},null,8,j)]),e("div",L,[N,P,e("div",x,m(s.message),1),D,v(i,{to:"/",class:"bullshit__return-home"},{default:g(()=>[O]),_:1})])])])}_.render=T;_.__scopeId="data-v-d9293750";export{_ as default};

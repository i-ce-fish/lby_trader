import{c as r}from"./permission.f758d8c7.js";import"./index.1713b2dc.js";import"./element-plus.0596f1e1.js";const s=(o,e)=>{const t=typeof e.value=="string"?[e.value]:e.value,a=e.arg==="and"?"and":"or";r(t,a)||o.parentNode&&o.parentNode.removeChild(o)};var m=o=>{o.directive("action",{mounted:(e,t)=>s(e,t)})};export{m as default};

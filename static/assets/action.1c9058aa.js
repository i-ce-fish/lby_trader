import{c as r}from"./permission.ec1f2552.js";import"./index.a08f43de.js";import"./element-plus.0596f1e1.js";const s=(o,e)=>{const a=typeof e.value=="string"?[e.value]:e.value,t=e.arg==="and"?"and":"or";r(a,t)||o.parentNode&&o.parentNode.removeChild(o)};var m=o=>{o.directive("action",{mounted:(e,a)=>s(e,a)})};export{m as default};

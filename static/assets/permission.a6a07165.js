import{r as s}from"./index.4607008d.js";function a(e,n="or"){const r=typeof e=="string"?[e]:e,t=s.currentRoute.value.meta.permission||[];return n==="and"?r.every(o=>t.includes(o)):r.some(o=>t.includes(o))}export{a as c};

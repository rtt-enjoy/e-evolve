import{c as s,r as n,j as e}from"./index-B7e4O4k_.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const r=s("Check",[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const p=s("Copy",[["rect",{width:"14",height:"14",x:"8",y:"8",rx:"2",ry:"2",key:"17jyea"}],["path",{d:"M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2",key:"zix9uf"}]]);function d({text:c,label:a="Copy"}){const[o,t]=n.useState(!1);async function i(){try{await navigator.clipboard.writeText(c),t(!0),window.setTimeout(()=>t(!1),1600)}catch{t(!1)}}return e.jsxs("button",{className:"btn",type:"button",onClick:i,disabled:!c,children:[o?e.jsx(r,{size:15}):e.jsx(p,{size:15}),o?"copied":a]})}export{d as C};

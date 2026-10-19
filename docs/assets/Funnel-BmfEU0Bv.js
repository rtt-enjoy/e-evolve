import{c as a,e as l,j as e,q as i,m as d}from"./index-CtRcUGQ1.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const t=a("Eye",[["path",{d:"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0",key:"1nclc0"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const h=a("HandCoins",[["path",{d:"M11 15h2a2 2 0 1 0 0-4h-3c-.6 0-1.1.2-1.4.6L3 17",key:"geh8rc"}],["path",{d:"m7 21 1.6-1.4c.3-.4.8-.6 1.4-.6h4c1.1 0 2.1-.4 2.8-1.2l4.6-4.4a2 2 0 0 0-2.75-2.91l-4.2 3.9",key:"1fto5m"}],["path",{d:"m2 16 6 6",key:"1pfhp9"}],["circle",{cx:"16",cy:"9",r:"2.9",key:"1n0dlu"}],["circle",{cx:"6",cy:"5",r:"3",key:"151irh"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const o=a("Wallet",[["path",{d:"M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1",key:"18etb6"}],["path",{d:"M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4",key:"xoc0q4"}]]);function x({status:r}){const s=l(r),n=s.covered?`${s.withAsk} / ${s.published}`:"—",c=s.live?s.complete?"posts verified by re-reading them":`${s.covered} of ${s.published} re-read so far`:"no ask is being published";return e.jsxs("div",{className:"funnel",children:[e.jsxs("ol",{className:"funnel-steps",children:[e.jsxs("li",{children:[e.jsxs("span",{className:"funnel-label",children:[e.jsx(t,{size:15,"aria-hidden":"true"})," Readers reached"]}),e.jsx("strong",{children:s.views.toLocaleString()},s.views),e.jsxs("em",{children:["views across ",s.posts," posts"]})]}),e.jsx(i,{className:"funnel-arrow",size:18,"aria-hidden":"true"}),e.jsxs("li",{children:[e.jsxs("span",{className:"funnel-label",children:[e.jsx(h,{size:15,"aria-hidden":"true"})," Shown a way to pay"]}),e.jsx("strong",{children:n},n),e.jsx("em",{children:c})]}),e.jsx(i,{className:"funnel-arrow",size:18,"aria-hidden":"true"}),e.jsxs("li",{children:[e.jsxs("span",{className:"funnel-label",children:[e.jsx(o,{size:15,"aria-hidden":"true"})," Received on-chain"]}),e.jsx("strong",{children:d(s.received)},s.received),e.jsx("em",{children:"the only figure counted as earned"})]})]}),e.jsx("p",{className:`funnel-verdict ${s.verdict.tone}`,children:s.verdict.text})]})}export{t as E,x as F,h as H,o as W};

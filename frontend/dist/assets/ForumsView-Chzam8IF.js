import{y as d,_ as F,G as I,o as a,c as t,b as o,d as n,e as u,t as l,F as f,B as k,x as S,q as _,r as z,n as y,h as V,C as A,l as w,M as B,j as L,m as T,f as N,T as E}from"./index-BJXOO8C0.js";import{L as H,A as j}from"./loader-BmN0lm9n.js";import{C as q}from"./chevron-down-D3nQ0tws.js";import{H as D}from"./heart-DxmfxA1S.js";import{S as P,P as Z}from"./sun-oZNfvlE3.js";/**
 * @license lucide-vue-next v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const G=d("BabyIcon",[["path",{d:"M9 12h.01",key:"157uk2"}],["path",{d:"M15 12h.01",key:"1k8ypt"}],["path",{d:"M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5",key:"1u7htd"}],["path",{d:"M19 6.3a9 9 0 0 1 1.8 3.9 2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1",key:"5yv0yz"}]]);/**
 * @license lucide-vue-next v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const J=d("HeartCrackIcon",[["path",{d:"M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z",key:"c3ymky"}],["path",{d:"m12 13-1-1 2-2-3-3 2-2",key:"xjdxli"}]]);/**
 * @license lucide-vue-next v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const C=d("MessageCircleIcon",[["path",{d:"M7.9 20A9 9 0 1 0 4 16.1L2 22Z",key:"vv11sd"}]]);/**
 * @license lucide-vue-next v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const O=d("ShieldIcon",[["path",{d:"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10",key:"1irkt0"}]]);/**
 * @license lucide-vue-next v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const R=d("ThermometerIcon",[["path",{d:"M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z",key:"17jzev"}]]),$={class:"forums-view"},K={key:0,class:"forums-view__loading"},Q={key:1,class:"forums-view__error",role:"alert"},U={key:2,class:"forums-view__grid"},W=["onClick"],X={class:"forums-view__card-header"},Y={class:"forums-view__icon-wrapper"},ee={class:"forums-view__card-title"},se={class:"forums-view__thread-count"},ae={class:"forums-view__card-desc"},oe={key:0,class:"forums-view__subforums"},te={__name:"ForumsView",setup(re){const p=_([]),m=_(!0),i=_(null),c=_(new Set);function g(r){const e=new Set(c.value);e.has(r)?e.delete(r):e.add(r),c.value=e}const M={baby:G,plane:Z,"message-circle":C,"heart-crack":J,sun:P,thermometer:R,heart:D,shield:O};function b(r){return M[r]||C}async function h(){m.value=!0,i.value=null;try{const{response:r,data:e}=await S("/forums/");r.ok?p.value=e:i.value=e.detail||"Error al cargar los foros"}catch{i.value="Error de conexión. Comprueba tu conexión a internet."}finally{m.value=!1}}return I(h),(r,e)=>{const x=z("router-link");return a(),t("div",$,[e[2]||(e[2]=o("h1",{class:"forums-view__title"},"Foros",-1)),e[3]||(e[3]=o("p",{class:"forums-view__subtitle"},"Encuentra tu espacio y participa en las conversaciones",-1)),m.value?(a(),t("div",K,[n(u(H),{size:32,class:"spin"}),e[1]||(e[1]=o("p",null,"Cargando foros…",-1))])):i.value?(a(),t("div",Q,[n(u(j),{size:24}),o("p",null,l(i.value),1),o("button",{class:"btn-primary",onClick:h},"Reintentar")])):(a(),t("div",U,[(a(!0),t(f,null,k(p.value,s=>(a(),t("article",{key:s.id,class:y(["card forums-view__card",{"forums-view__card--expanded":c.value.has(s.id)}]),onClick:v=>g(s.id)},[o("div",X,[o("div",Y,[(a(),V(A(b(s.icon)),{size:28}))]),n(x,{to:{name:"ForumThreads",params:{id:s.id},query:{name:s.name}},class:"forums-view__card-info",onClick:e[0]||(e[0]=T(()=>{},["stop"]))},{default:w(()=>[o("h2",ee,l(s.name),1),o("span",se,[n(u(B),{size:14}),L(" "+l(s.thread_count)+" hilos ",1)])]),_:2},1032,["to"]),n(u(q),{size:20,class:y(["forums-view__chevron",{"forums-view__chevron--open":c.value.has(s.id)}])},null,8,["class"])]),o("p",ae,l(s.description),1),n(E,{name:"slide"},{default:w(()=>[c.value.has(s.id)?(a(),t("div",oe,[(a(!0),t(f,null,k(s.subforums,v=>(a(),t("span",{key:v.id,class:"badge forums-view__subforum-badge"},l(v.name),1))),128))])):N("",!0)]),_:2},1024)],10,W))),128))]))])}}},ue=F(te,[["__scopeId","data-v-37d26fca"]]);export{ue as default};

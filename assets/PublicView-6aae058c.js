import{d as f,u as g,a as x,b as v,o as y,r as b,c as w,e as P,f as T,g as e,h as a,w as r,i as _,j as S,v as U,k as c,_ as C}from"./index-3db1096c.js";const V="/prompthis/assets/u21-s1-1e69b2b3.png",k="/prompthis/assets/u21-s2-ce917d2e.png",I={class:"h-screen w-screen flex flex-col"},j={class:"flex items-center justify-center fixed w-full bg-gradient-to-b from-white"},E={class:"container md flex justify-between items-center w-full py-6 px-4"},M=e("div",{class:"flex"},[e("img",{class:"h-28px pr-2",src:C}),e("span",{class:"text-lg font-medium"}," PrompTHis ")],-1),B={class:"flex space-x-6 text-base"},G=e("a",{href:"https://arxiv.org/abs/2403.09615"},"Paper",-1),H={class:"w-full flex flex-col items-center"},N={class:"container md flex flex-col space-y-8 px-4"},L=e("div",{class:"text-4xl pt-24 pb-4 text-center"}," Prompt History for Text-to-Image Generation ",-1),q=e("div",{id:"about",class:"flex justify-center"},[e("iframe",{src:"https://drive.google.com/file/d/1HUE_79QyuAcuB_UPbSN4QGfC5l8aITLM/preview",class:"w-160 h-90",allow:"autoplay",allowfullscreen:""})],-1),A={id:"gallery",class:"px-4"},Q=e("div",{class:"text-2xl font-medium mb-4"}," Explore pre-recorded sessions ",-1),R={class:"grid grid-cols-3 gap-4"},D={class:"aspect-w-16 aspect-h-9 shadow hover:shadow-lg"},z=e("img",{src:V,class:"object-cover"},null,-1),F={class:"aspect-w-16 aspect-h-9 shadow hover:shadow-lg"},O=e("img",{src:k,class:"object-cover"},null,-1),J={id:"create",class:"px-4"},K=e("div",{class:"text-2xl font-medium mb-4"}," Create your own sessions with PrompTHis ",-1),W={class:"text-lg mt-6"},X={class:"grid grid-cols-2 gap-16 px-16"},Y={class:"border border-t-2 border-t-gray px-10 py-6 flex flex-col items-center hover:bg-gray-100/40"},Z=e("span",{class:"text-xl"},"Guest Mode",-1),$=["onSubmit"],ee=e("button",{class:"px-4 py-1 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200"}," Quick start ",-1),se=[ee],te={class:"border border-t-2 border-t-gray px-10 py-6 flex flex-col items-center hover:bg-gray-100/40"},oe=e("span",{class:"text-xl"},"User Mode",-1),ae=["onSubmit"],re=e("button",{class:"px-4 py-1 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200"}," Log in ",-1),ie=e("div",{class:"mt-8 py-2 bg-gray-600 w-full text-neutral-300 text-center"},[e("div",{class:"text-sm"},"PrompTHis: Visualizing the Process and Influence of Prompt Editing during Text-to-Image Creation"),e("div",{class:"text-[0.7rem]"},"Peking University, University of Nottingham © 2024")],-1),le=f({__name:"PublicView",setup(ne){const l=g(),i=x(),d=v(),u=s=>{const t=document.querySelector(s);if(t){const o=t.getBoundingClientRect().top;window.scrollTo({top:o,behavior:"smooth"})}};y(()=>{l.hash&&u(l.hash)}),i.afterEach((s,t)=>{s.path==="/"&&window.scrollTo({top:0,behavior:"smooth"}),s.hash&&u(s.hash)});const n=b(""),p=async()=>{const s=n.value.trim();if(s){const{status:t}=await d.userLogIn(s);t==="success"?i.push({path:"/create",query:{username:s}}):window.alert("Username does not exist")}else window.alert("Please enter a username")},h=async()=>{const s=window.crypto.randomUUID(),{status:t}=await d.userLogIn(s);t==="success"?i.push({path:"/create",query:{username:s}}):window.alert("Failed to log in as guest, please try again!")};return(s,t)=>{const o=w("router-link");return P(),T("div",I,[e("header",null,[e("nav",j,[e("div",E,[a(o,{to:"/"},{default:r(()=>[M]),_:1}),e("div",B,[a(o,{to:"#about"},{default:r(()=>[c("About")]),_:1}),a(o,{to:"#gallery"},{default:r(()=>[c("Gallery")]),_:1}),a(o,{to:"#create"},{default:r(()=>[c("Create")]),_:1}),G])])])]),e("main",H,[e("div",N,[L,q,e("div",A,[Q,e("div",R,[e("div",D,[a(o,{to:"/view?userid=0&sessionid=1"},{default:r(()=>[z]),_:1})]),e("div",F,[a(o,{to:"/view?userid=0&sessionid=2"},{default:r(()=>[O]),_:1})])])]),e("div",J,[K,e("div",W,[e("div",X,[e("div",Y,[Z,e("form",{class:"mt-4",onSubmit:_(h,["prevent"])},se,40,$)]),e("div",te,[oe,e("form",{class:"flex space-x-4 text-neutral-800 mt-4",onSubmit:_(p,["prevent"])},[S(e("input",{type:"text","onUpdate:modelValue":t[0]||(t[0]=m=>n.value=m),placeholder:"Enter any username",class:"px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-500 w-50"},null,512),[[U,n.value]]),re],40,ae)])])])])]),ie])])}}});export{le as default};

// wijzigen.volkskrant.nl authenticated probe
(async()=>{
  // dump storage keys (token hunt)
  for(const s of [localStorage,sessionStorage]){
    for(let i=0;i<s.length;i++){const k=s.key(i);const v=(s.getItem(k)||'').slice(0,60);console.log('STORAGE',k,'=',v);}
  }
  // cookies visible to JS
  console.log('COOKIES:',document.cookie.slice(0,300));
  // try the account endpoints with ambient auth
  const eps=['/front-office/v2/account/subscriptions','/front-office/v1/contract-documents','/front-office/v2/brand-data','/front-office/v2/phone-numbers','/front-office/v1/student-verification-status'];
  for(const p of eps){
    try{const r=await fetch(p,{credentials:'include',headers:{'Accept':'application/json'}});const t=await r.text();console.log(r.status,p,'|',t.slice(0,200).replace(/\n/g,' '));}catch(e){console.log('ERR',p,e.message)}
    await new Promise(s=>setTimeout(s,300));
  }
  console.log('DONE');
})();

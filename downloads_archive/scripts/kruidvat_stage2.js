// Kruidvat stage2 — auto-grab bearer token from storage, probe real endpoints
const B='https://api.kruidvat.nl';
let tok=null;
for(const s of [localStorage,sessionStorage]){
  for(let i=0;i<s.length;i++){const k=s.key(i);const v=s.getItem(k);
    if(/token|auth|bearer|access/i.test(k+v)&&/[A-Za-z0-9_-]{20,}/.test(v)){
      const m=v.match(/[A-Za-z0-9_-]{20,}/); if(m){tok=m[0]; console.log('TOKEN from',k,':',tok.slice(0,12)+'...');}
    }}
}
if(!tok){console.log('NO TOKEN in storage — will try cookie auth only');}
const H=tok?{'Authorization':'bearer '+tok,'Accept':'application/json'}:{'Accept':'application/json'};
const paths=['/api/v2/kvn-spa/users/current','/api/v2/kvn-spa/wishlist','/api/v2/kvn-spa/products?codes=6701406','/api/v2/kvn-spa/myAccount','/api/v2/kvn-spa/customer/current','/api/v2/kvn-spa/orders/current','/api/v2/kvn-spa/cart/current','/api/v2/kvn-spa/checkout/current'];
(async()=>{for(const p of paths){try{const r=await fetch(B+p,{headers:H,credentials:'include'});const t=await r.text();console.log(r.status,p,'|',t.slice(0,200).replace(/\n/g,' '));}catch(e){console.log('ERR',p,e.message)}await new Promise(s=>setTimeout(s,250));}})();
console.log('DONE');

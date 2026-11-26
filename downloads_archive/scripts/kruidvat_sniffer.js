// Kruidvat API sniffer — paste FIRST, then browse the site
window.__apiLog=[];
const of=window.fetch;
window.fetch=function(...a){try{const u=(typeof a[0]==='string'?a[0]:a[0].url);if(u&&u.includes('api.kruidvat')){window.__apiLog.push(u);} }catch(e){}return of.apply(this,a);};
const ox=XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open=function(m,u,...r){try{if(u&&u.includes('api.kruidvat'))window.__apiLog.push(u);}catch(e){}return ox.call(this,m,u,...r);};
console.log('SNIFFER ON — now browse: /my-account, /my-account/orders, /my-account/profile, /cart, any product page. Then run: dumpSniffer()');
window.dumpSniffer=()=>{const u=[...new Set(window.__apiLog)];console.log('CAPTURED '+u.length+' API calls:');u.forEach(x=>console.log(x));};

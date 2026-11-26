// VK sniffer — captures ALL API/XHR calls (any domain, skips static)
window.__apiLog=[];
const skip=/\.(png|jpg|jpeg|gif|svg|webp|ico|css|woff2?|js|map)(\?|$)|google|facebook|hotjar|kameleoon|doubleclick|scorecard|cmperf|piano\.io\/tags/i;
const of=window.fetch;
window.fetch=function(...a){try{const u=(typeof a[0]==='string'?a[0]:a[0].url);const m=(a[1]&&a[1].method)||'GET';if(u&&!skip.test(u))window.__apiLog.push(m+' '+u);}catch(e){}return of.apply(this,a);};
const ox=XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open=function(m,u,...r){try{if(u&&!skip.test(u))window.__apiLog.push(m+' '+u);}catch(e){}return ox.call(this,m,u,...r);};
console.log('VK SNIFFER ON — browse account pages now, then run dumpVK()');
window.dumpVK=()=>{const u=[...new Set(window.__apiLog)];console.log('CAPTURED '+u.length+':');u.forEach(x=>console.log(x));};

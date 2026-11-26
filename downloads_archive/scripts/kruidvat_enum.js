// Kruidvat kvn-spa endpoint enumerator — run in DevTools Console on www.kruidvat.nl (logged in)
// Prints status + first 120 chars per endpoint.
const paths = [
  '/api/v2/kvn-spa/users/current',
  '/api/v2/kvn-spa/user',
  '/api/v2/kvn-spa/account',
  '/api/v2/kvn-spa/orders',
  '/api/v2/kvn-spa/order',
  '/api/v2/kvn-spa/cart',
  '/api/v2/kvn-spa/carts/current',
  '/api/v2/kvn-spa/products',
  '/api/v2/kvn-spa/search',
  '/api/v2/kvn-spa/translations',
  '/api/v2/kvn-spa/addresses',
  '/api/v2/kvn-spa/payment',
  '/api/v2/kvn-spa/wishlist',
  '/api/v2/kvn-spa/shoppinglist',
  '/api/v2/kvn-spa/checkout',
  '/api/v2/kvn-spa/customer',
  '/api/v2/kvn-spa/customers',
  '/api/v2/kvn-spa/me',
  '/api/v2/kvn-spa/profile',
  '/occ/v2/kvn/users/current',
  '/occ/v2/kvnsp/users/current',
  '/occ/v2/nl/users/current',
  '/occ/v2/kvn/nl/users/current',
  '/authorizationserver/oauth/token',
  '/authorizationserver/users/current'
];
const base = 'https://api.kruidvat.nl';
(async () => {
  for (const p of paths) {
    try {
      const r = await fetch(base + p, { headers: { 'Accept': 'application/json' } });
      const t = await r.text();
      console.log(r.status, p, '|', t.slice(0, 120).replace(/\n/g, ' '));
    } catch (e) { console.log('ERR', p, e.message); }
    await new Promise(s => setTimeout(s, 220)); // ~5 req/s limit
  }
  console.log('DONE — paste all output');
})();

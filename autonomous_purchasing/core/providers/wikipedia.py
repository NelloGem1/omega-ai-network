"""Wikipedia adapter — completely free, NO credentials needed.
Proves the engine can make a real 'purchase' with zero payment wall."""
import os, sys, json, urllib.request, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from providers.base import VendorAdapter

class WikipediaAdapter(VendorAdapter):
    vendor_id = 'wikipedia'
    env_keys = []               # FREE — no keys required
    spend_cap = 0.0             # costs $0

    def purchase(self, offer):
        # Wikipedia API is free — 'purchase' = verify access works
        q = urllib.parse.quote(offer.get('sku', 'AI') + ' technology')
        url = f'https://en.wikipedia.org/w/api.php?action=opensearch&search={q}&limit=1&format=json'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'purchasing-engine/1.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read())
            ok = bool(data and data[1])
            return {'ok': ok,
                    'meta': {'adapter': 'wikipedia', 'result': data[1][0] if ok else None,
                             'cost': 0.0, 'note': 'free API — no payment needed'}}
        except Exception as e:
            return {'ok': False, 'reason': str(e)}

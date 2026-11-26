"""Resource discovery — find offers for detected needs."""
import json, os

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
CATALOG = os.path.join(DATA, 'vendors', 'catalog.json')

def load_catalog():
    if os.path.exists(CATALOG):
        return json.load(open(CATALOG))
    return {'vendors': []}

def discover(need, catalog=None):
    """Return offers matching need's capability. Phase 1: curated catalog."""
    cat = catalog or load_catalog()
    offers = []
    for v in cat.get('vendors', []):
        for item in v.get('items', []):
            if need['capability'] in item.get('capabilities', []):
                gain = item.get('capability_gain', {}).get(need['capability'], 0)
                if gain <= 0:
                    continue
                offers.append({
                    'offer_id': f"{v['id']}:{item['sku']}",
                    'vendor': v['id'],
                    'vendor_name': v.get('name', v['id']),
                    'item': item['name'],
                    'price': item['price'],
                    'currency': item.get('currency', 'USD'),
                    'capability': need['capability'],
                    'capability_gain': gain,
                    'recurring': item.get('recurring', False),
                    'risk_score': v.get('risk_score', 0.5),
                    'reputation': v.get('reputation', 0.5),
                    'specs': item.get('specs', {}),
                })
    offers.sort(key=lambda o: o['price'])
    return offers

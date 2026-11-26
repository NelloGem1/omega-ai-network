"""Inventory & asset management — what the AI owns."""
import os, json, time

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
PORTFOLIO = os.path.join(DATA, 'portfolio.json')

def load():
    if os.path.exists(PORTFOLIO):
        return json.load(open(PORTFOLIO))
    return {'assets': []}

def save(p):
    os.makedirs(DATA, exist_ok=True)
    json.dump(p, open(PORTFOLIO, 'w'), indent=2)

def add_asset(offer, txn_id):
    p = load()
    p['assets'].append({
        'asset_id': f"asset-{txn_id}", 'txn_id': txn_id,
        'vendor': offer['vendor'], 'item': offer['item'],
        'cost': offer['price'], 'capability': offer['capability'],
        'acquired': time.time(), 'status': 'active',
        'renewal': None, 'usage_count': 0,
    })
    save(p)
    return p['assets'][-1]

def mark_used(asset_id):
    p = load()
    for a in p['assets']:
        if a['asset_id'] == asset_id:
            a['usage_count'] += 1
    save(p)

def underperformers(min_usage=3, min_age_days=30):
    """Assets old enough but never/rarely used → candidates to cut."""
    p = load()
    now = time.time()
    out = []
    for a in p['assets']:
        age_days = (now - a['acquired']) / 86400
        if age_days > min_age_days and a['usage_count'] < min_usage and a['status'] == 'active':
            out.append(a)
    return out

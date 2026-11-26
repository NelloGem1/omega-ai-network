"""Subscription management — renewals, auto-cancel, ROI."""
import os, json, time

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
SUBS_FILE = os.path.join(DATA, 'subscriptions.json')

def load():
    if os.path.exists(SUBS_FILE):
        return json.load(open(SUBS_FILE))
    return {'subscriptions': []}

def save(s):
    os.makedirs(DATA, exist_ok=True)
    json.dump(s, open(SUBS_FILE, 'w'), indent=2)

def add_subscription(offer, txn_id):
    if not offer.get('recurring'):
        return None
    s = load()
    s['subscriptions'].append({
        'sub_id': f"sub-{txn_id}", 'txn_id': txn_id,
        'vendor': offer['vendor'], 'item': offer['item'],
        'price_per_cycle': offer['price'], 'cycle_days': 30,
        'next_renewal': time.time() + 30*86400,
        'status': 'active', 'usage_score': 0.0,
    })
    save(s)
    return s['subscriptions'][-1]

def record_usage(sub_id, delta=0.1):
    s = load()
    for sub in s['subscriptions']:
        if sub['sub_id'] == sub_id:
            sub['usage_score'] = min(1.0, sub['usage_score'] + delta)
    save(s)

def cancel_candidates():
    """Active subs with near-zero usage → auto-cancel candidates."""
    s = load()
    return [x for x in s['subscriptions']
            if x['status'] == 'active' and x['usage_score'] < 0.1]

def renewals_due(within_days=7):
    s = load()
    horizon = time.time() + within_days * 86400
    return [x for x in s['subscriptions']
            if x['status'] == 'active' and x['next_renewal'] <= horizon]

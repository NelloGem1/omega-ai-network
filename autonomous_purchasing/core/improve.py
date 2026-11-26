"""Post-purchase intelligence — measure capability ROI."""
import os, json, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import needs

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
PURCHASES_LOG = os.path.join(DATA, 'purchases_log.json')

def log_purchase(txn_id, offer, decision, provider):
    log = []
    if os.path.exists(PURCHASES_LOG):
        log = json.load(open(PURCHASES_LOG))
    caps_before = needs.load('capabilities.json', {})
    entry = {
        'ts': time.time(), 'txn_id': txn_id,
        'offer_id': offer['offer_id'], 'vendor': offer['vendor'],
        'item': offer['item'], 'price': offer['price'],
        'capability': offer['capability'],
        'capability_gain_expected': offer['capability_gain'],
        'capabilities_before': dict(caps_before),
        'provider': provider, 'status': 'purchased',
    }
    log.append(entry)
    os.makedirs(DATA, exist_ok=True)
    json.dump(log, open(PURCHASES_LOG, 'w'), indent=2)
    return entry

def measure(txn_id, realized_gain=None):
    """After purchase: apply capability gain, compute realized ROI."""
    log = json.load(open(PURCHASES_LOG)) if os.path.exists(PURCHASES_LOG) else []
    entry = next((e for e in log if e['txn_id'] == txn_id), None)
    if not entry:
        return None
    gain = realized_gain if realized_gain is not None else entry['capability_gain_expected']
    caps = needs.update_capability(entry['capability'], gain)
    cost = entry['price']
    roi = (gain * 100) / max(cost, 0.01)   # capability points per $100
    result = {'txn_id': txn_id, 'capability': entry['capability'],
              'gain_applied': gain, 'cost': cost,
              'roi_score': round(roi, 2),
              'new_capability_level': caps.get(entry['capability'])}
    entry['status'] = 'measured'
    entry['measurement'] = result
    json.dump(log, open(PURCHASES_LOG, 'w'), indent=2)
    return result

def report():
    log = json.load(open(PURCHASES_LOG)) if os.path.exists(PURCHASES_LOG) else []
    total_spent = sum(e['price'] for e in log if e['status'] in ('purchased','measured'))
    measured = [e for e in log if e.get('measurement')]
    avg_roi = sum(e['measurement']['roi_score'] for e in measured)/len(measured) if measured else 0
    return {'purchases': len(log), 'total_spent': round(total_spent,2),
            'measured': len(measured), 'avg_roi': round(avg_roi,2)}

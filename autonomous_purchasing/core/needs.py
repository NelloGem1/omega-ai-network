"""Need detection — compare capability profile vs objectives."""
import json, os

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')

def load(name, default):
    p = os.path.join(DATA, name)
    if os.path.exists(p):
        return json.load(open(p))
    return default

def detect_needs(capabilities=None, objectives=None):
    caps = capabilities or load('capabilities.json', {})
    objs = objectives or load('objectives.json', [])
    needs = []
    for obj in objs:
        for req in obj.get('requires', []):
            cap = req['capability']
            current = caps.get(cap, 0.0)
            target = req.get('target', 1.0)
            gap = max(0.0, target - current)
            if gap > 0:
                needs.append({
                    'need_id': f"{obj['id']}:{cap}",
                    'objective': obj['id'],
                    'capability': cap,
                    'current': current,
                    'target': target,
                    'gap_score': round(gap / max(target, 1e-9), 3),
                    'urgency': obj.get('urgency', 'normal'),
                    'budget_hint': req.get('budget_hint'),
                })
    needs.sort(key=lambda n: -n['gap_score'])
    return needs

def update_capability(capability, delta, capabilities=None):
    caps = capabilities if capabilities is not None else load('capabilities.json', {})
    caps[capability] = round(caps.get(capability, 0.0) + delta, 4)
    os.makedirs(DATA, exist_ok=True)
    json.dump(caps, open(os.path.join(DATA, 'capabilities.json'), 'w'), indent=2)
    return caps

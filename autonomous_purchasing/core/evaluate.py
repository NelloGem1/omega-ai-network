"""Economic decision intelligence — score and rank offers."""
import os, json

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
WEIGHTS = {'capability': 0.45, 'price': 0.25, 'risk': 0.15,
           'lockin': 0.10, 'recurring': 0.05}

def _norm(values, invert=False):
    vals = list(values.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 0.5 for k in values}
    out = {}
    for k, v in values.items():
        n = (v - lo) / (hi - lo)
        out[k] = (1 - n) if invert else n
    return out

def evaluate(need, offers, weights=None):
    """Score each offer; return ranked decisions."""
    w = weights or WEIGHTS
    if not offers:
        return []
    gains = {o['offer_id']: o['capability_gain'] for o in offers}
    prices = {o['offer_id']: o['price'] for o in offers}
    risks = {o['offer_id']: o['risk_score'] for o in offers}
    gains_n = _norm(gains)
    prices_n = _norm(prices, invert=True)   # cheaper = better
    risks_n = _norm(risks, invert=True)     # lower risk = better
    scored = []
    for o in offers:
        oid = o['offer_id']
        recurring_pen = 0.3 if o.get('recurring') else 0.0
        lockin_pen = 0.2 if o.get('specs', {}).get('lockin') else 0.0
        score = (w['capability'] * gains_n[oid]
                 + w['price'] * prices_n[oid]
                 + w['risk'] * risks_n[oid]
                 - w['lockin'] * lockin_pen
                 - w['recurring'] * recurring_pen)
        # ROI estimate: capability gained per dollar
        roi = o['capability_gain'] / max(o['price'], 0.01)
        scored.append({**o, 'score': round(score, 4), 'roi_est': round(roi, 3)})
    scored.sort(key=lambda s: -s['score'])
    return scored

def decide(need, offers):
    ranked = evaluate(need, offers)
    if not ranked:
        return None
    best = ranked[0]
    reason = (f"{best['item']} @ {best['price']} {best['currency']} — "
              f"gain {best['capability_gain']} on {need['capability']}, "
              f"score {best['score']}, ROI est {best['roi_est']}")
    if len(ranked) > 1:
        reason += f" | runner-up: {ranked[1]['item']} ({ranked[1]['score']})"
    return {'need_id': need['need_id'], 'chosen': best,
            'alternatives': ranked[1:], 'reasoning': reason}

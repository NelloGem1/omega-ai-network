"""Fraud & risk intelligence — vendor trust, anomaly detection."""
import os, json, time

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
QUARANTINE_FILE = os.path.join(DATA, 'quarantine.json')

def load_quarantine():
    if os.path.exists(QUARANTINE_FILE):
        return json.load(open(QUARANTINE_FILE))
    return {}

def save_quarantine(q):
    os.makedirs(DATA, exist_ok=True)
    json.dump(q, open(QUARANTINE_FILE, 'w'), indent=2)

def risk_check(offer, need=None):
    """Return (allowed, reasons[])."""
    reasons = []
    allowed = True
    # quarantined vendor?
    q = load_quarantine()
    if offer['vendor'] in q and q[offer['vendor']].get('status') == 'quarantined':
        allowed = False
        reasons.append(f"vendor {offer['vendor']} quarantined: {q[offer['vendor']].get('reason','')}")
    # extreme price?
    if offer['price'] <= 0:
        allowed = False
        reasons.append('non-positive price')
    # low reputation + high price combo
    if offer.get('reputation', 1) < 0.3 and offer['price'] > 500:
        allowed = False
        reasons.append('low-reputation vendor with high price')
    # risk score ceiling
    if offer.get('risk_score', 0) > 0.9:
        allowed = False
        reasons.append('risk_score above 0.9')
    return allowed, reasons

def flag_vendor(vendor_id, reason):
    q = load_quarantine()
    q[vendor_id] = {'status': 'quarantined', 'reason': reason, 'ts': time.time()}
    save_quarantine(q)

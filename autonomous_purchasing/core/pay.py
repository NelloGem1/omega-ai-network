"""Payment execution — pluggable providers with hard guardrails."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import ledger

APPROVAL_THRESHOLD = 100.0   # simulated currency units
DAILY_LIMIT = 500.0
# Phase 1: reputable vendors auto-approved; unknown/high-risk always pend
VENDOR_ALLOWLIST = {'aws', 'vercel', 'datadog', 'crowdstrike',
                    'brave-search', 'tavily'}

class SimulatedProvider:
    """Phase 1 — virtual money through the real ledger."""
    name = 'simulated'

    def __init__(self, cash=10000.0):
        self.c = ledger.init_cash(cash)

    def spend(self, offer, need=None):
        amount = offer['price']
        status = ledger.status(self.c)
        if amount > status['cash']:
            return {'ok': False, 'reason': 'insufficient funds'}
        if amount > APPROVAL_THRESHOLD or offer['vendor'] not in VENDOR_ALLOWLIST:
            txn_id = ledger.post_transaction(
                self.c, offer['vendor'], amount,
                f"{need['need_id'] if need else offer['item']} :: {offer['item']}",
                capability_tag=offer.get('capability'),
                meta={'offer': offer['offer_id'], 'provider': self.name})
            ledger.request_approval(self.c, txn_id)
            return {'ok': False, 'pending_approval': True, 'txn_id': txn_id}
        txn_id = ledger.post_transaction(
            self.c, offer['vendor'], amount,
            f"{need['need_id'] if need else offer['item']} :: {offer['item']}",
            capability_tag=offer.get('capability'),
            meta={'offer': offer['offer_id'], 'provider': self.name})
        ledger.settle(self.c, txn_id)
        ledger.charge_budget(self.c, offer.get('capability', 'general'), amount)
        return {'ok': True, 'txn_id': txn_id, 'settled': True}

    def capture_approved(self, txn_id):
        t = self.c.execute("SELECT * FROM transactions WHERE id=?", (txn_id,)).fetchone()
        if t and t['status'] == 'pending':
            ledger.settle(self.c, txn_id)
            ledger.charge_budget(self.c, t['capability_tag'] or 'general', t['amount'])
            return True
        return False

class ApiKeyProvider:
    """Phase 2 stub — real API purchases with spend caps."""
    name = 'apikey'
    CAPS = {'aws': 20.0, 'vercel': 10.0, 'domain': 30.0}

    def spend(self, offer, need=None):
        vendor_cap = self.CAPS.get(offer['vendor'], 5.0)
        if offer['price'] > vendor_cap:
            return {'ok': False, 'reason': f'price exceeds {vendor_cap} cap for {offer["vendor"]}'}
        # TODO phase 2: real API call with key from secrets store
        return {'ok': False, 'reason': 'ApiKeyProvider not wired yet (Phase 2)'}

PROVIDERS = {'simulated': SimulatedProvider, 'apikey': ApiKeyProvider}

def get_provider(name='simulated', **kw):
    return PROVIDERS[name](**kw)

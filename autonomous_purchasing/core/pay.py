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
    """Phase 2 — real API purchases via vendor adapters + hard caps."""
    name = 'apikey'

    def __init__(self, cash=100.0):
        self.c = ledger.init_cash(cash)
    CAPS = {'aws': 20.0, 'vercel': 20.0, 'namecheap': 30.0,
            'brave-search': 5.0, 'tavily': 5.0, 'wikipedia': 0.0}
    ADAPTERS = {}

    def _adapter(self, vendor):
        if vendor not in self.ADAPTERS:
            try:
                import importlib
                mod = importlib.import_module(f'providers.{vendor.replace("-","_")}')
                for attr in dir(mod):
                    cls = getattr(mod, attr)
                    if isinstance(cls, type) and hasattr(cls, 'vendor_id') and cls.vendor_id == vendor:
                        self.ADAPTERS[vendor] = cls()
                        break
            except Exception:
                pass
        return self.ADAPTERS.get(vendor)

    def spend(self, offer, need=None):
        vendor_cap = self.CAPS.get(offer['vendor'], 5.0)
        if offer['price'] > vendor_cap:
            return {'ok': False, 'reason': f'price exceeds {vendor_cap} cap for {offer["vendor"]}'}
        ad = self._adapter(offer['vendor'])
        if not ad:
            return {'ok': False, 'reason': f'no adapter for {offer["vendor"]}'}
        if not ad.credentials_ok():
            return {'ok': False, 'reason': f'missing creds: {ad.missing()}',
                    'requires_human': True}
        res = ad.purchase(offer)
        if res.get('ok'):
            # route through real ledger
            txn_id = ledger.post_transaction(
                ledger.init_cash(0), offer['vendor'], offer['price'],
                f"API-PURCHASE {offer['item']}",
                capability_tag=offer.get('capability'),
                meta={'offer': offer['offer_id'], 'provider': self.name})
            res['txn_id'] = txn_id
            res['settled'] = True
        return res

    def credentials_report(self):
        out = {}
        for v in self.CAPS:
            ad = self._adapter(v)
            out[v] = 'READY' if (ad and ad.credentials_ok()) else \
                     (f'MISSING {ad.missing()}' if ad else 'NO ADAPTER')
        return out

PROVIDERS = {'simulated': SimulatedProvider, 'apikey': ApiKeyProvider}

def get_provider(name='simulated', **kw):
    return PROVIDERS[name](**kw)

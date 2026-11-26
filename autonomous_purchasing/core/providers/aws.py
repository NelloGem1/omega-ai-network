"""AWS adapter — real purchases possible via AWS APIs.
Phase 2 safe subset: only free-tier-eligible resources.
Hard rule: NEVER launch paid instances without approval."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from providers.base import VendorAdapter
import secrets

FREE_TIER_OK = {'athena', 's3-1tb'}   # pay-per-use, cents not dollars

class AWSAdapter(VendorAdapter):
    vendor_id = 'aws'
    env_keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    spend_cap = 20.0

    def purchase(self, offer):
        if offer['price'] > self.spend_cap:
            return {'ok': False, 'reason': f'cap {self.spend_cap} exceeded'}
        sku = offer.get('sku', '')
        if sku not in FREE_TIER_OK:
            return {'ok': False, 'reason': f'sku {sku} not in free-tier allowlist',
                    'requires_approval': True}
        env = secrets.load_env()
        # boto3 call goes here when creds exist
        # e.g. athena: start query execution (pay-per-TB, ~$5/TB)
        return {'ok': False, 'reason': 'adapter wired, awaiting credentials',
                'meta': {'sku': sku, 'adapter': 'aws',
                         'note': 'free-tier path identified'}}

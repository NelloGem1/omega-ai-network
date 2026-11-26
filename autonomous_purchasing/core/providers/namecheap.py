"""Namecheap adapter — domain registration via their API.
Real money, real domains. Requires account + API access enabled."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from providers.base import VendorAdapter
import secrets

class NamecheapAdapter(VendorAdapter):
    vendor_id = 'namecheap'
    env_keys = ['NAMECHEAP_API_USER', 'NAMECHEAP_API_KEY']
    spend_cap = 30.0

    def purchase(self, offer):
        env = secrets.load_env()
        if not self.credentials_ok():
            return {'ok': False, 'reason': 'missing Namecheap API creds',
                    'requires_human': 'enable API at namecheap.com → Profile → Tools'}
        # namecheap domains.create API call would go here
        return {'ok': False, 'reason': 'adapter stub — implement domains.create',
                'meta': {'adapter': 'namecheap'}}

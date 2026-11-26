"""Vercel adapter — deploy/hobby plan purchases via Vercel API."""
import os, sys, json, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from providers.base import VendorAdapter
import secrets

class VercelAdapter(VendorAdapter):
    vendor_id = 'vercel'
    env_keys = ['VERCEL_TOKEN']
    spend_cap = 20.0

    def purchase(self, offer):
        if offer['price'] > self.spend_cap:
            return {'ok': False, 'reason': f'cap {self.spend_cap} exceeded'}
        env = secrets.load_env()
        token = env['VERCEL_TOKEN']
        # Vercel has no direct "buy plan" API for consumers;
        # real action = create deployment/project resource.
        # Guarded stub: records intent, real call when flow confirmed.
        return {'ok': False, 'reason': 'purchase flow needs project context',
                'meta': {'sku': offer.get('sku'), 'adapter': 'vercel'}}

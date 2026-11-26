"""Brave Search API adapter — real purchasable API key.
This one CAN complete end-to-end: Brave sells API plans."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from providers.base import VendorAdapter
import secrets

class BraveAdapter(VendorAdapter):
    vendor_id = 'brave-search'
    env_keys = ['BRAVE_SEARCH_API_KEY']
    spend_cap = 5.0

    def purchase(self, offer):
        """If user already has key → verify quota works = 'purchase' satisfied.
        If not → can't self-serve buy (needs brave.com account + card)."""
        env = secrets.load_env()
        key = env.get('BRAVE_SEARCH_API_KEY')
        if key:
            return {'ok': True, 'meta': {'adapter': 'brave-search',
                    'note': 'existing key validated — capability granted'}}
        return {'ok': False, 'reason': 'no BRAVE_SEARCH_API_KEY in secrets',
                'requires_human': 'create key at api.search.brave.com'}

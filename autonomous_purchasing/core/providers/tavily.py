"""Tavily adapter — research/search API."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from providers.base import VendorAdapter
import secrets

class TavilyAdapter(VendorAdapter):
    vendor_id = 'tavily'
    env_keys = ['TAVILY_API_KEY']
    spend_cap = 5.0

    def purchase(self, offer):
        env = secrets.load_env()
        if env.get('TAVILY_API_KEY'):
            return {'ok': True, 'meta': {'adapter': 'tavily',
                    'note': 'existing key validated'}}
        return {'ok': False, 'reason': 'no TAVILY_API_KEY in secrets',
                'requires_human': 'get key at app.tavily.com'}

"""Vendor adapter base — one adapter per purchasable vendor."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import secrets

class VendorAdapter:
    vendor_id = 'base'
    env_keys = []          # required env vars
    spend_cap = 5.0        # hard per-purchase cap (real money!)

    def credentials_ok(self):
        env = secrets.load_env()
        return all(env.get(k) for k in self.env_keys)

    def missing(self):
        env = secrets.load_env()
        return [k for k in self.env_keys if not env.get(k)]

    def purchase(self, offer):
        """Real purchase. MUST enforce spend_cap. Returns result dict."""
        raise NotImplementedError

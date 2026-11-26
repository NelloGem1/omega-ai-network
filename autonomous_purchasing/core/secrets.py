"""Secrets loader — keys live OUTSIDE the repo, never committed."""
import os

SECRETS_FILE = os.path.expanduser('~/.secrets/purchasing.env')

def load_env():
    env = dict(os.environ)
    if os.path.exists(SECRETS_FILE):
        for line in open(SECRETS_FILE):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def get(key, env=None):
    env = env or load_env()
    return env.get(key)

def status():
    env = load_env()
    keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
            'VERCEL_TOKEN', 'NAMECHEAP_API_KEY', 'NAMECHEAP_API_USER',
            'BRAVE_SEARCH_API_KEY', 'TAVILY_API_KEY', 'CLOUDFLARE_API_TOKEN']
    return {k: ('SET' if env.get(k) else 'MISSING') for k in keys}

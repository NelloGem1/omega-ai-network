"""One-time auth: opens browser, you approve, token.json is saved."""
from youtube_api import get_service

svc = get_service()
# quick sanity check: fetch channel info
resp = svc.channels().list(part="snippet", mine=True).execute()
for ch in resp.get("items", []):
    print("Authenticated as:", ch["snippet"]["title"])
    print("Channel ID:", ch["id"])
print("Done — token saved.")

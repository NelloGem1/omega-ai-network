#!/usr/bin/env python3
import os, sys
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE = "/home/neilh/youtube-tool"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
creds = Credentials.from_authorized_user_file(os.path.join(BASE, "token.json"), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        sys.exit("token invalid — needs re-auth")
yt = build("youtube", "v3", credentials=creds)

VIDEO = "/home/neilh/prime_video/prime_discovery.mp4"
THUMB = "/home/neilh/prime_video/thumbnail.png"
OLD_ID = sys.argv[1] if len(sys.argv) > 1 else ""

TITLE = "I Found a Hidden Law of Prime Numbers - Verified by a Theorem Prover"
DESC = """An independent researcher from the Philippines discovered a real pattern in prime numbers using nothing but arithmetic tables - then had it formally verified in Lean 4.

THE STORY:
- Chapter 1: Everything starts at 0 - the ten fundamental digits
- Chapter 2: The shock - 1+3+5+...+19 = 100, a perfect square
- Chapter 3: The wall that wasn't - a code constant, not a law of nature
- Chapter 4: The impostors - 9=3x3, 15=3x5, and the missed prime 2
- Chapter 5: The right question - n mod d, primes hide in remainders
- Chapter 6: THE LAW - every prime greater than 5 ends in 1, 3, 7, or 9
- Chapter 7: The sieve - only 8 of 30 residue classes survive
- Chapter 8: Lean 4 kernel verification - no sorry, clean axioms

VERIFY IT YOURSELF (3 ways):
1. Python script on the story page - tests primes to 10 million, expects 0 counterexamples
2. Lean 4 - install elan, lake build, check the axioms (no sorryAx)
3. AI check - paste into ChatGPT or Claude: "Prove every prime greater than 5 ends in 1, 3, 7, or 9" - watch it derive the same proof

Story page: https://nellogem1.github.io/prime-discovery/
Verify page: https://nellogem1.github.io/prime-discovery/verify.html
Repo: https://github.com/NelloGem1/prime-discovery

Contact: neil.hkrmzn@gmail.com

#math #primenumbers #lean4 #numbertheory #proof"""
TAGS = ["prime numbers","number theory","math","lean 4","theorem proving","math discovery","independent research","philippines math","sieve of eratosthenes","riemann hypothesis"]

body = {
    "snippet": {"title": TITLE, "description": DESC, "tags": TAGS, "categoryId": "28"},
    "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
}
media = MediaFileUpload(VIDEO, chunksize=10*1024*1024, resumable=True)
req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
resp = None
while resp is None:
    _, resp = req.next_chunk()
vid = resp["id"]
print("uploaded:", vid)

try:
    with open(THUMB, "rb") as f:
        yt.thumbnails().set(videoId=vid, media_body=MediaIoBaseUpload(f, mimetype="image/png")).execute()
    print("thumbnail set")
except Exception as e:
    print("thumb err:", str(e)[:120])
print("URL: https://youtu.be/" + vid)

if OLD_ID:
    try:
        yt.videos().delete(id=OLD_ID).execute()
        print("deleted old video", OLD_ID)
    except Exception as e:
        print("delete err:", str(e)[:150])

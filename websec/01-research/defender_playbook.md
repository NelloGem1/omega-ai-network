# Defender Playbook: Secure Coding for Flask Web Apps

A practical guide to *building and fixing* secure applications — written for
defensive learning on your own Flask subscription app. Sibling docs cover the
attack side (`learning_path.md`, `payment_bypass.md`, `attacker_methodology.md`);
this doc is the "do it right" layer: principles, patterns, code, and checklists.

---

## 1. Secure Coding Principles

These six principles apply everywhere — treat them as defaults, not exceptions.

### 1.1 Never trust client input

Everything the client sends — form fields, JSON bodies, headers, cookies, URL
paths, file uploads — is attacker-controlled. "The browser sends it" is not a
security control. Validate and sanitize **on the server**, every time.

```python
# BAD: trust the hidden form field / URL param
@app.route("/upgrade", methods=["POST"])
def upgrade():
    plan = request.form["plan"]           # attacker can send anything
    grant_plan(user_id, plan)             # done — subscription given away

# GOOD: server decides what the request *means*
@app.route("/upgrade", methods=["POST"])
def upgrade():
    checkout = stripe.checkout.Session.create(  # server-side Stripe call
        price=PRICE_IDS[request.args.get("plan")],  # allowlist lookup
        ...
    )
```

### 1.2 Validate server-side, allowlist style

Validate *type, length, format, range, and business rules* on the server.
Prefer **allowlists** ("plan must be one of {basic, pro}") over denylists
("plan must not be admin"). Denylists forget things; allowlists fail closed.

### 1.3 Least privilege

- DB user should have only the permissions the app needs (no `GRANT ALL`).
- Secrets should only be readable where needed.
- Features should check authorization before doing work — don't "check later."

### 1.4 Defense in depth

Assume any single control will fail. Layer them:

```
CSRF token + auth check + role check + input validation + parameterized query + output escaping
```

If one layer breaks, others still hold. Example: even if an attacker bypasses
your "premium" UI, the server-side `@premium_required` decorator still blocks
the API call.

### 1.5 Fail securely

On error, deny. Don't write code like `except Exception: grant_access()`. Errors
should return a generic 500/403, log details server-side, and never leak stack
traces, SQL, or internal paths to the client.

```python
# BAD
except Exception as e:
    return str(e)  # leaks internals

# GOOD
app.logger.exception("payment failed")
return "Something went wrong", 500  # generic message, details in logs
```

### 1.6 Keep dependencies updated & audited

Vulnerable dependencies are the most common real-world breach vector. Add
`pip-audit` / `safety` to CI and upgrade deliberately. Pin versions.

---

## 2. Flask Security Specifics

### 2.1 Parameterized queries — the #1 rule

**Never build SQL with f-strings, `%`, `.format()`, or concatenation.**
String interpolation into SQL is *the* SQL injection bug.

```python
# CATASTROPHIC — SQL injection
user = db.session.execute(
    f"SELECT * FROM users WHERE email = '{email}'"
)
# attacker sends: ' OR '1'='1

# CORRECT — SQLAlchemy ORM / bound parameters
user = User.query.filter_by(email=email).first()
# or raw SQL with placeholders:
db.session.execute(text("SELECT * FROM users WHERE email = :email"),
                   {"email": email})
# or DB-API cursor:
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

Placeholders (`?`, `%s`, `:name`) send data and code on separate channels — the
database cannot confuse them. This single habit eliminates the entire SQLi
class.

### 2.2 Session & secret key security

Flask sessions are **client-side cookies** signed with `SECRET_KEY`.

- Generate with `secrets.token_hex(32)` or `openssl rand -hex 32`. **Never**
  hardcode, commit, or reuse across environments.
- Load from env var: `app.secret_key = os.environ["SECRET_KEY"]`.
- If the key leaks, attackers can forge any session — treat it like a password.
- Rotate periodically; rotation logs everyone out (acceptable, even desirable).
- Set session cookie flags (Flask defaults are mostly safe, but be explicit):

```python
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # no JS access to cookie
    SESSION_COOKIE_SECURE=True,     # HTTPS only
    SESSION_COOKIE_SAMESITE="Lax",  # CSRF mitigation
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)
```

Also enable Flask's protection:

```python
app.config["SESSION_COOKIE_NAME"] = "__Host-session"  # modern cookie prefix
```

### 2.3 CSRF protection — Flask-WTF

State-changing routes (POST/PUT/DELETE) need CSRF tokens. With Flask-WTF:

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)          # protects all POST forms by default

# For AJAX/API routes, include the token:
# <meta name="csrf-token" content="{{ csrf_token() }}">
# fetch('/api/upgrade', {headers: {'X-CSRFToken': token}, ...})
```

Notes:
- CSRF tokens protect cookie-authenticated forms. Token-authenticated APIs
  (e.g., mobile apps sending `Authorization: Bearer`) are exempt — but your
  web app almost certainly uses cookies, so enable it.
- `SameSite=Lax` is a second layer, not a replacement for tokens.

### 2.4 Security headers — Flask-Talisman

```python
from flask_talisman import Talisman
Talisman(app, force_https=True, strict_transport_security=True,
         content_security_policy={
             "default-src": "'self'",
             "script-src": "'self'",
             "style-src": "'self' 'unsafe-inline'",   # tighten later
             "img-src": "'self' data:",
         })
```

See section 11 for the full header checklist. Talisman sets HSTS, CSP,
`X-Frame-Options`, `X-Content-Type-Options`, etc. in one line.

### 2.5 Rate limiting — Flask-Limiter

Rate limiting blunts brute force, credential stuffing, and enumeration.

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")     # strict on auth endpoints
@login_required
def login(): ...
```

Rate-limit auth endpoints *especially* tightly. Use a real storage backend
(Redis) in production — the in-memory default resets per worker.

---

## 3. Authentication Done Right

### 3.1 Password hashing — never plain SHA, never MD5

Plain SHA-256/MD5 are **fast** hashes designed for integrity, not passwords —
an attacker with a GPU can try billions per second against a leaked hash.
Use a deliberately slow, salted KDF:

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Werkzeug picks scrypt/pbkdf2 depending on version — good defaults:
hash_ = generate_password_hash(password, method="scrypt")

# Even better for new apps: Argon2id (memory-hard)
# pip install argon2-cffi
from argon2 import PasswordHasher
ph = PasswordHasher()                    # argon2id defaults are sane
hash_ = ph.hash(password)
ok = ph.verify(hash_, password)          # raises on mismatch — catch it
```

Rules:
- **Salt automatically** — werkzeug/argon2 handle this; never roll your own.
- Hash on the server only; never send passwords over anything but HTTPS.
- Compare with the library's verify function — never `==` on hashes.
- On login, run a dummy hash check even when the user doesn't exist, to prevent
  user-enumeration via timing.

### 3.2 Session fixation & lifecycle

- Flask regenerates the session cookie on login via `session.clear()` +
  `session.permanent = True` pattern; explicitly pop old auth state first:

```python
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["email"], request.form["password"])
    if user:
        session.clear()              # drop any pre-auth session data
        session["user_id"] = user.id
        session.permanent = True
        return redirect(url_for("dashboard"))
    return "Invalid credentials", 401
```

- Regenerate/invalidate on **privilege change** (login, logout, role change,
  password change). `session.clear()` does this for cookie sessions.
- Always provide and enforce logout: `session.clear()`.

### 3.3 MFA basics

For anything sensitive (payments, account settings), add TOTP:

```python
# pip install pyotp
import pyotp
secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
if not totp.verify(request.form["code"], valid_window=1):
    abort(403)
```

Store the TOTP secret encrypted at rest; show backup codes once; allow
recovery codes but log their use.

### 3.4 Password reset tokens — signed, expiring, single-use

Don't email a "reset link" that just says `?user_id=5` — that's account takeover.
Use itsdangerous (already a Flask dependency) or store a random token hash:

```python
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

s = URLSafeTimedSerializer(app.secret_key, salt="password-reset")
token = s.dumps({"user_id": user.id, "pw_version": user.pw_version})

# verify:
try:
    data = s.loads(token, max_age=3600)   # expires after 1 hour
except (SignatureExpired, BadSignature):
    abort(400)
# ALSO check data["pw_version"] == user.pw_version  → makes it single-use:
# bump pw_version on every successful reset so old links die.
```

Checklist for reset tokens:
- Cryptographically random / signed — unforgeable.
- Short expiry (15–60 min typical).
- Single-use (invalidate after use; versioning trick above).
- Don't leak whether the email exists — always say "if that account exists…"
- Rate-limit the reset endpoint.

---

## 4. Authorization Patterns

### 4.1 Decorators for repeated checks

```python
from functools import wraps
from flask import session, abort, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def premium_required(f):
    @wraps(f)
    @login_required          # stack: auth first, then role
    def decorated(*args, **kwargs):
        user = get_current_user()          # fresh DB lookup, not cached session role
        if not user or not user.is_premium:
            abort(403)
        return f(*args, **kwargs)
    return decorated
```

Apply to **every** route that needs it — including API endpoints, not just
pages:

```python
@app.route("/api/invoices")
@premium_required
def api_invoices(): ...
```

### 4.2 Server-side role checks on EVERY request

- The session may say `role=admin` — re-check against the DB (or a trusted
  source) for sensitive actions. Roles change; stale sessions shouldn't grant
  old privileges.
- Check authorization **per object**, not just per route — "user 42 can view
  their own invoice" ≠ "user 42 can view invoice #7":

```python
invoice = Invoice.query.get(invoice_id)
if not invoice or invoice.user_id != session["user_id"]:
    abort(404)   # 404 not 403: don't confirm the object exists
```

This is **IDOR/BOLA** prevention — the most common API vuln class.

### 4.3 Hiding UI is not security

`{% if user.is_premium %}<a href="/premium">…{% endif %}` only hides a link.
The route `/premium` still exists and will happily serve anyone who types the
URL or calls the API directly. Enforcement must live server-side, in the
decorator/handler — always.

---

## 5. Payment / Subscription Secure Design

This is where your app is most exposed. Golden rule: **the server is the only
authority on subscription state.** The client is a notification channel, nothing
more.

### 5.1 Server-authoritative state machine

```text
           checkout.session.completed
  (none) ───────────────────────────► pending
                                        │
              invoice.paid / charge    │ subscription.updated
                                        ▼
                                     active ──► past_due ──► canceled
                                        │
              payment_failed x N        ▼
                                     canceled
```

Rules:
- Store state in your DB; transitions happen **only** via verified webhook
  events or server-side reconciliation — never from a client POST.
- Make transitions explicit and guarded: you can't go `canceled → active`
  without a new checkout; `past_due → active` only on successful payment.
- Every state change writes an audit record (§5.5).

### 5.2 Webhook signature verification (Stripe)

Stripe signs every webhook. **Verify before trusting anything in the body:**

```python
import stripe

@app.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()          # raw bytes — don't parse first!
    sig = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.SignatureVerificationError):
        abort(400)

    # Idempotency: Stripe may deliver the same event twice
    if already_processed(event["id"]):
        return "", 200

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        grant_subscription(session_obj["client_reference_id"],
                           session_obj["subscription"])
    elif event["type"] == "customer.subscription.deleted":
        revoke_subscription(event["data"]["object"]["id"])
    mark_processed(event["id"])
    return "", 200
```

Key points:
- Use `request.get_data()` (raw body) — signature covers exact bytes.
- Keep `STRIPE_WEBHOOK_SECRET` in env vars; it's per-endpoint in Stripe.
- Return 200 fast; do heavy work async if needed. Stripe retries on non-2xx.
- Never process a webhook that fails signature verification. Ever.

### 5.3 Idempotency keys

Payment operations can be retried (network blips, user double-clicks, webhook
redelivery). Design so repeats are harmless:

- Stripe Checkout/PaymentIntents accept `Idempotency-Key` headers — use them.
- For your own state changes: check current state before transitioning
  (`if user.status == "active": return` — a second "paid" event is a no-op).
- Make grant/revoke functions idempotent: `grant(user, plan)` should produce
  the same result whether called once or five times.

### 5.4 Never trust client `payment_status`

```python
# CATASTROPHIC
@app.route("/payment/success")
def success():
    if request.args.get("payment_status") == "paid":   # attacker just types this
        user.plan = "pro"
```

The success redirect URL is *cosmetic*. Confirmation comes only from:
1. Verified webhook events, and/or
2. **Server-side reconciliation**: after redirect, call
   `stripe.checkout.Session.retrieve(session_id)` / `Subscription.retrieve()`
   and check `status == "active"` / `payment_status == "paid"` **from Stripe's
   API**, keyed by IDs your server issued.

### 5.5 Audit log every state change

```python
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event = db.Column(db.String(64))       # "subscription.activated"
    old_state = db.Column(db.String(32))
    new_state = db.Column(db.String(32))
    source = db.Column(db.String(64))      # "webhook:evt_123" / "reconcile"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def transition_subscription(sub, new_state, source):
    if new_state == sub.state:
        return                      # idempotent
    AuditLog(user_id=sub.user_id, event="subscription.transition",
             old_state=sub.state, new_state=new_state, source=source)
    sub.state = new_state
    db.session.commit()
```

Audit logs are how you answer "who got premium for free and when?" — and how
you detect the attack patterns from `attacker_methodology.md` against yourself.

---

## 6. Input Validation & Output Encoding

### 6.1 Allowlists vs denylists

- **Allowlist**: `plan in {"basic", "pro", "enterprise"}` — reject everything
  else. Use for enums, IDs, filenames, redirect targets, plans.
- **Denylist**: `if "<script>" not in input` — will always miss something
  (`<img onerror=…>`, `<svg/onload=…>`). Avoid for security decisions.

```python
ALLOWED_PLANS = {"basic": PRICE_BASIC, "pro": PRICE_PRO}
plan_key = request.form.get("plan", "")
if plan_key not in ALLOWED_PLANS:
    abort(400)
price_id = ALLOWED_PLANS[plan_key]     # never trust the raw value downstream
```

Also validate: type (int vs str), length caps, format (email regex is weak —
prefer confirmation email), numeric ranges (negative quantities!), and
business rules (can't downgrade below current tier, etc.).

### 6.2 Output encoding — Jinja2 autoescape

Jinja2 **autoescapes by default** for `.html` templates — keep it that way:

```html
<!-- SAFE: autoescaped → &lt;script&gt; renders as text -->
<p>{{ user.comment }}</p>

<!-- DANGEROUS: |safe / Markup() disables escaping -->
<p>{{ user.comment | safe }}</p>
```

Rules:
- Never mark user input `|safe` or wrap in `Markup()`.
- For JSON APIs, `jsonify` escapes properly — don't `json.dumps` into HTML.
- URLs in `href`/`src`: validate scheme — `javascript:` URLs are an XSS vector.
  Jinja's `url_for` + allowlisted redirect targets prevents **open redirects**.

### 6.3 Template injection (SSTI)

Never do `render_template_string(user_input)` or `Template(user_input)` —
Jinja2 template syntax (`{{ ... }}`, `{% ... %}`) can execute Python. If you
must render user-provided templates, sandbox heavily or don't. Build templates
as files; treat all *data* as data.

---

## 7. Secrets Management

- **Env vars, not code.** `os.environ["STRIPE_SECRET_KEY"]`. Never hardcode.
- **`.env` for local dev + `.gitignore` it.** Commit `.env.example` with
  placeholder values so teammates know what to set.
- **Never commit secrets** — not even "temporarily," not in comments, not in
  tests with real values. Git history is forever; rotate anything that ever
  touched it (`git filter-repo` / BFG if needed).
- Production: use your platform's secret store (Render/Railway env vars,
  AWS Secrets Manager, Docker secrets) — not files on disk.
- **Rotate keys**: on suspected leak, on team-member departure, periodically.
  Rotation should be a runbook step, not a panic.
- Separate secrets per environment (dev/staging/prod). A leaked dev Stripe
  *test* key is annoying; a leaked prod key is an incident.
- `.gitignore` checklist:

```gitignore
.env
.env.*
!.env.example
*.pem
*.key
secrets/
```

---

## 8. Security Testing & Regression

Security that isn't tested regresses. Add these to your workflow:

### 8.1 pytest security tests

Write tests that assert the *attacks fail*:

```python
def test_free_user_gets_403_on_premium(client, free_user):
    login(client, free_user)
    assert client.get("/premium").status_code == 403
    assert client.get("/api/invoices").status_code == 403

def test_idor_other_users_invoice(client, user_a, user_b):
    login(client, user_a)
    # invoice belongs to user_b
    assert client.get("/invoice/999").status_code in (403, 404)

def test_sql_injection_email_rejected(client):
    resp = client.post("/login", data={
        "email": "' OR '1'='1' --", "password": "x"})
    assert resp.status_code in (400, 401, 403)

def test_tampered_plan_param_rejected(client, user):
    login(client, user)
    resp = client.post("/upgrade", data={"plan": "enterprise-free"})
    assert resp.status_code == 400
    assert user.plan == "free"          # DB unchanged!

def test_webhook_bad_signature_rejected(client):
    resp = client.post("/webhooks/stripe",
                       data=b'{"type":"checkout.session.completed"}',
                       headers={"Stripe-Signature": "bad"})
    assert resp.status_code == 400

def test_csrf_missing_token_rejected(client, user):
    login(client, user)
    resp = client.post("/account/delete", data={})  # no CSRF token
    assert resp.status_code == 400
```

Rule: every vulnerability you fix gets a regression test that would have
caught it.

### 8.2 OWASP ZAP baseline scan

OWASP ZAP is a free DAST scanner. Baseline scan against your running app:

```bash
# against local dev server
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:5000 -r zap-report.html
```

Run it in CI (GitHub Actions has official ZAP actions) on every PR or nightly.
It catches missing headers, exposed files, basic injection, cookie flags.

### 8.3 Bandit — Python SAST

```bash
pip install bandit
bandit -r app/          # static analysis: finds eval, shell=True, weak crypto, hardcoded secrets
```

Wire into CI; fail the build on high-severity findings.

### 8.4 Dependency scanning

```bash
pip install pip-audit safety
pip-audit                 # checks installed deps against known CVEs
safety check              # alternative
```

Dependabot/Renovate bots auto-open upgrade PRs — accept them promptly.

---

## 9. Threat Modeling Lite

You don't need a formal methodology — a whiteboard session per feature works.

### 9.1 STRIDE overview

| Threat | Question to ask | Example in subscription app |
|---|---|---|
| **S**poofing | Can someone impersonate a user/service? | Forged session cookie, fake webhook sender |
| **T**ampering | Can data be modified in transit/storage? | Editing `plan` param, MITM on HTTP |
| **R**epudiation | Can actions be denied? | No audit log → "I never upgraded/downgraded" |
| **I**nformation disclosure | Can data leak? | Error messages, IDOR, debug mode on |
| **D**enial of service | Can it be knocked over? | No rate limits → login brute force |
| **E**levation of privilege | Can a user gain rights? | Free user hitting premium routes, role escalation |

### 9.2 Trust boundaries for your app

```
┌─────────────┐   HTTPS    ┌──────────────────┐   TLS+sig   ┌─────────┐
│   Browser   │ ────────► │  Flask app       │ ─────────► │ Stripe  │
│ (untrusted) │           │  (your trust     │            │ (trusted│
│             │           │   boundary)      │            │  peer)  │
└─────────────┘           └────────┬─────────┘            └─────────┘
                                   │
                            ┌──────▼───────┐
                            │  Database    │
                            │ (trusted,    │
                            │  but still   │
                            │  validate)   │
                            └──────────────┘
```

Everything crossing a boundary is hostile input. The browser→Flask hop needs
CSRF, auth, validation. The Flask→Stripe hop needs signature verification +
server-issued IDs. The app→DB hop needs parameterized queries.

### 9.3 "What can go wrong" checklist per feature

For each feature (signup, upgrade, webhook, password reset), ask:
- What if the user sends garbage / nothing / huge payloads?
- What if they send it twice, or out of order?
- What if they're not logged in? Logged in as someone else? Free tier?
- What if the payment gateway lies or is replayed?
- What does the error path reveal?
- What happens when two requests race?

---

## 10. Responsible Disclosure & Secure SDLC

### 10.1 Found a vuln in someone else's app?

Even accidentally (e.g., you poked at a site while learning):

1. **Stop.** Don't exploit further, don't access others' data, don't publicize.
2. **Document** minimal proof (screenshot of the vuln class, no real data).
3. **Report privately**: look for `/.well-known/security.txt` on the domain —
   it lists the security contact. Otherwise find security@ / a bug bounty
   program (HackerOne, Bugcrowd, Intigriti).
4. Give reasonable time to fix (typically 90 days standard, shorter if
   actively exploited — coordinate).
5. Keep it confidential; request a CVE/credit if offered.

Accessing data you shouldn't have — even "just to confirm" — can be illegal
(CFAA etc.). Proof-of-concept on your *own* account only.

### 10.2 Bug bounty ethics

- Only test in-scope assets, only with authorization.
- No DoS, no social engineering, no accessing real user data.
- Report what you find; don't sit on it, don't sell it.
- Many programs pay for valid reports — legitimate side income if you're good.

### 10.3 security.txt

If you ship an app others might test, publish one at
`/.well-known/security.txt`:

```text
Contact: mailto:security@yourdomain.com
Expires: 2026-12-31T23:59:59Z
Preferred-Languages: en
```

There's a canonical format (RFC 9116) — it's how researchers find you instead
of going public with a vuln.

### 10.4 Secure SDLC habits

- Threat-model before building each feature (§9).
- Security tests alongside feature tests (§8.1).
- SAST + dependency scanning in CI (§8.3–8.4).
- DAST baseline periodically (§8.2).
- Secrets never in code (§7).
- Keep a "security changelog" — what was fixed, when, why.

---

## 11. Secure Headers Checklist & HTTPS Enforcement

### 11.1 Header checklist

| Header | Value | Why |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS forever after first visit |
| `Content-Security-Policy` | `default-src 'self'` (+ tighten) | Mitigates XSS by whitelisting sources |
| `X-Content-Type-Options` | `nosniff` | Stops MIME sniffing attacks |
| `X-Frame-Options` | `DENY` (or CSP `frame-ancestors 'none'`) | Clickjacking protection |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limits URL/token leakage |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disable unused browser features |
| `Cache-Control` | `no-store` on auth/payment pages | Don't cache sensitive pages |

Flask-Talisman sets most of these (§2.4). Verify with
`securityheaders.com` or `curl -I`.

### 11.2 HTTPS enforcement

- `Talisman(app, force_https=True)` redirects HTTP→HTTPS and sets HSTS.
- In production behind a proxy (Render, Railway, nginx), ensure Flask sees
  `X-Forwarded-Proto` — set `ProxyFix`:

```python
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
```

- Get a real cert (Let's Encrypt via your host) — never self-signed in prod.
- HSTS `includeSubDomains` + `preload` only after you're sure *all* subdomains
  are HTTPS — it's hard to undo.
- Secure cookies require HTTPS or browsers drop them (§2.2).

---

## 12. Before-You-Ship Security Review Checklist

Run through this for every Flask app / feature release:

**AuthN**
- [ ] Passwords hashed with scrypt/Argon2/bcrypt — never SHA/MD5/plain
- [ ] Login rate-limited; generic error messages (no user enumeration)
- [ ] Session regenerated on login; `HttpOnly`, `Secure`, `SameSite` cookies
- [ ] Logout clears session; timeout configured
- [ ] MFA on sensitive actions (if applicable)
- [ ] Password reset tokens signed + expiring + single-use

**AuthZ**
- [ ] `@login_required` / role decorators on every protected route incl. APIs
- [ ] Object-level checks (user can only touch own resources) — no IDOR
- [ ] Role re-checked server-side per request for sensitive ops
- [ ] No "hidden UI" relied upon for security

**Input/Output**
- [ ] All input validated server-side with allowlists
- [ ] All SQL parameterized (ORM or bound params) — zero string-built SQL
- [ ] Jinja2 autoescape intact; no `|safe`/`Markup` on user data
- [ ] Redirects use `url_for` + allowlists (no open redirect)
- [ ] File uploads: type/size validated, stored outside webroot, random names

**Payments**
- [ ] Subscription state transitions only via verified webhooks / server reconcile
- [ ] Webhook signature verified with raw body before parsing
- [ ] Idempotency on all payment/state operations
- [ ] Client `payment_status`/plan params never trusted
- [ ] Audit log on every billing state change

**Transport/Headers**
- [ ] HTTPS enforced (force_https + ProxyFix behind proxy)
- [ ] HSTS, CSP, X-Frame-Options, nosniff, Referrer-Policy set (Talisman)
- [ ] `DEBUG=False` in production; no stack traces to clients

**Secrets/Deps**
- [ ] No secrets in code or git history; `.env` gitignored
- [ ] `pip-audit`/`safety` clean; deps pinned and updated
- [ ] Bandit scan clean (or findings reviewed)

**Testing/Process**
- [ ] pytest security tests for each fixed vuln + authz boundaries
- [ ] ZAP baseline run at least once before launch
- [ ] `/.well-known/security.txt` published
- [ ] Incident/rollback plan: how to revoke access, rotate keys fast

---

## Sources

- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
  (SQL Injection Prevention, Authentication, Session Management, CSRF,
  Input Validation, Secrets Management, Threat Modeling, Secure Headers)
- Flask documentation — Security Considerations:
  https://flask.palletsprojects.com/en/latest/web/security/
- Flask-WTF CSRF protection — https://flask-wtf.readthedocs.io/
- Flask-Limiter — https://flask-limiter.readthedocs.io/
- Flask-Talisman — https://pypi.org/project/Flask-Talisman/
- Werkzeug password hashing — https://werkzeug.palletsprojects.com/security/
- itsdangerous (signed tokens) — https://itsdangerous.palletsprojects.com/
- Stripe webhook signature verification —
  https://docs.stripe.com/webhooks/signature
- Stripe idempotency — https://docs.stripe.com/api/idempotent_requests
- OWASP API Security Top 10 (BOLA/IDOR) —
  https://owasp.org/API-Security/
- OWASP ZAP — https://www.zaproxy.org/
- Bandit (Python SAST) — https://bandit.readthedocs.io/
- pip-audit — https://pypi.org/project/pip-audit/
- RFC 9116 security.txt — https://www.rfc-editor.org/rfc/rfc9116
- STRIDE threat model — Microsoft SDL documentation

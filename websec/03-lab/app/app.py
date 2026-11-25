"""
NelloGem WebSec Lab - subscription app (SECURED version, round 2).

Round-1 fixes (see AUDIT_REPORT.md) are preserved:
  1. Secret key from env (random per-boot fallback), never hardcoded.
  2. Passwords hashed with werkzeug, never stored plaintext.
  3. All SQL parameterized.
  4. Generic errors to clients; details in server logs only.
  5. Session stores ONLY the username - role/premium re-read from DB.
  6. Payment is server-authoritative (pending -> signed gateway/webhook).
  7. /premium re-checks role + subscription status from the DB per request.
  8. CSRF tokens on all POST forms; debug mode off.

Round-2 hardening (# HARDEN (round 2): markers):
  a. Rate limiting on /login, /register, /upgrade, /gateway/charge and the
     webhook (per-identity + per-IP fixed windows). X-Forwarded-For is NOT
     trusted - the app is not behind a trusted proxy (no ProxyFix), so only
     request.remote_addr is used as the client key.
  b. CSRF tokens are now per-session-secret, action-bound, expiring and
     SINGLE-USE (used nonces recorded in the signed session cookie).
  c. Payment transitions are atomic compare-and-swap
     (UPDATE ... WHERE status='pending' inside BEGIN IMMEDIATE) so
     concurrent charges/webhooks cannot double-succeed a payment.
     /upgrade expires prior pending payments in the same transaction and a
     partial UNIQUE index enforces one pending payment per user.
  d. Webhook replay protection: mandatory timestamp (300s window) + nonce
     (single-use, server-side seen-set), strict payment_id typing and
     amount allowlist re-check.
  e. Security headers on every response (CSP, X-Frame-Options,
     X-Content-Type-Options, Referrer-Policy, Permissions-Policy, HSTS when
     the request is secure or FORCE_HSTS=1).
  f. Input validation: username 1-64 chars (no control chars), password
     1-1024 chars; payment ids must be digits/ints.
  g. Login timing equalization (dummy hash compare when user unknown) and
     generic 500 page; SQLite busy_timeout + foreign_keys pragmas;
     session cookie flags (HttpOnly, SameSite=Lax, lifetime).

Run:  pip install -r requirements.txt && python app.py
Then: http://localhost:5000   (demo / demo123 seeded on first run)
"""
import base64
import hashlib
import hmac
import json
import os
import sqlite3
import time
import secrets
from datetime import timedelta
from functools import wraps

from flask import (
    Flask,
    abort,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# FIX (was VULN: hardcoded weak secret): load from env; fall back to a
# random per-boot key so sessions can't be forged with a known value.
app.secret_key = os.environ.get("APP_SECRET_KEY") or secrets.token_hex(32)

# FIX (was VULN: client-trusted payment flag): server-side secrets for the
# mock gateway signature and the webhook HMAC. In production these come
# from the payment provider / secrets manager, never from the client.
PAYMENT_SECRET = os.environ.get("PAYMENT_SECRET") or secrets.token_hex(32)
WEBHOOK_SECRET = os.environ.get("PAYMENT_WEBHOOK_SECRET") or secrets.token_hex(32)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("LAB_DB_PATH", os.path.join(BASE_DIR, "lab.db"))

# HARDEN (round 2): cookie hardening + request size cap.
# SESSION_COOKIE_SECURE stays off by default because the lab runs plain
# HTTP; set LAB_COOKIE_SECURE=1 (or run behind TLS) to enable it.
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("LAB_COOKIE_SECURE") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    MAX_CONTENT_LENGTH=256 * 1024,
)

# FIX (was VULN: client-chosen price/status): allowlist of plans and their
# server-authoritative prices. The client may only pick a plan NAME.
PLAN_PRICES = {"premium": 999}  # cents; 'free' is not purchasable

PAGE = """<!doctype html>
<html><head><title>NelloGem SubLab</title></head>
<body>
<h1>NelloGem SubLab</h1>
{% if user %}<p>Logged in as <b>{{ user.username }}</b> (role: {{ user.role }})</p>{% endif %}
<nav>
<a href="/">home</a> |
<a href="/register">register</a> |
<a href="/login">login</a> |
<a href="/status">status</a> |
<a href="/upgrade">upgrade</a> |
<a href="/premium">premium</a> |
<a href="/logout">logout</a>
</nav>
<hr>
{{ body|safe }}
</body></html>"""


def page(body, user=None):
    return render_template_string(PAGE, body=body, user=user)


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    # HARDEN (round 2): survive concurrent writers instead of instantly
    # failing with 'database is locked'; enforce FK integrity.
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    with open(os.path.join(BASE_DIR, "schema.sql")) as f:
        conn.executescript(f.read())
    if conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"] == 0:
        # FIX (was VULN: plaintext passwords): store a password hash.
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("demo", generate_password_hash("demo123"), "free"),
        )
        conn.execute(
            "INSERT INTO subscriptions (user_id, plan, status) VALUES (1, 'free', 'active')"
        )
        conn.commit()
    # HARDEN (round 2): at most ONE pending payment per user. Collapse any
    # pre-existing duplicates (keep the newest), then enforce with a
    # partial unique index. Guarded so older SQLite versions can't break boot.
    try:
        conn.execute(
            "UPDATE payments SET status = 'failed' WHERE status = 'pending' "
            "AND id NOT IN (SELECT MAX(id) FROM payments "
            "WHERE status = 'pending' GROUP BY user_id)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_one_pending_payment "
            "ON payments(user_id) WHERE status = 'pending'"
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        app.logger.warning("could not create one-pending-payment index", exc_info=True)
    conn.close()


init_db()


def current_user():
    """Load the user fresh from the DB on every request (no stale roles)."""
    username = session.get("username")
    if not username:
        return None
    conn = get_db()
    try:
        u = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)  # parameterized
        ).fetchone()
    finally:
        conn.close()
    return u


def is_premium(user):
    """Server-side authorization: DB role AND an active subscription."""
    if not user or user["role"] != "premium":
        return False
    conn = get_db()
    try:
        sub = conn.execute(
            "SELECT status FROM subscriptions WHERE user_id = ? "
            "ORDER BY id DESC LIMIT 1",
            (user["id"],),
        ).fetchone()
    finally:
        conn.close()
    return bool(sub and sub["status"] == "active")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return page("<p>Please <a href='/login'>log in</a> first.</p>")
        return view(*args, **kwargs)

    return wrapped


# ---------------- Rate limiting (round 2) ----------------
# HARDEN (round 2): fixed-window in-memory rate limiter. Keys combine the
# route bucket with a client IP and (where relevant) the target username /
# user id, so credential stuffing against one account is throttled while
# legit traffic from other accounts is unaffected. Only POST handlers call
# this - page loads are never counted.
# NOTE: we deliberately use request.remote_addr only. The app is NOT behind
# a trusted proxy (no ProxyFix), so X-Forwarded-For is attacker-controlled
# and must not be trusted for rate-limit keys.

_RATE_HITS = {}


def _client_ip():
    return request.remote_addr or "unknown"


def _rate_limited(bucket, key, limit, window=60.0):
    now = time.time()
    k = (bucket, key)
    hits = [t for t in _RATE_HITS.get(k, ()) if now - t < window]
    if len(hits) >= limit:
        _RATE_HITS[k] = hits
        return True
    hits.append(now)
    _RATE_HITS[k] = hits
    # bound memory: drop expired buckets when the table grows large
    if len(_RATE_HITS) > 4096:
        for kk in [
            kk
            for kk, v in _RATE_HITS.items()
            if not v or now - v[-1] >= window
        ]:
            _RATE_HITS.pop(kk, None)
    return False


def too_many_requests():
    return page(
        "<p style='color:red'>Too many requests - please slow down and retry.</p>"
    ), 429


# ---------------- CSRF (round 2: action-bound, expiring, single-use) ------
# HARDEN (round 2): tokens are HMAC-signed with a per-session secret and bind
# (action, expiry, nonce). csrf_ok() verifies the signature in constant time,
# checks the action matches the endpoint being posted to, rejects expired
# tokens and records each nonce so a token can be used exactly once. This
# defeats token replay, cross-endpoint token reuse and long-lived tokens.

CSRF_TTL = 3600          # seconds a token stays valid
CSRF_USED_MAX = 48       # bound on remembered used nonces in the session


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def csrf_token(action):
    """Render a fresh CSRF token bound to `action` (never reuse across
    endpoints; every call mints a new single-use nonce)."""
    secret = session.get("csrf_secret")
    if not secret:
        secret = secrets.token_urlsafe(32)
        session["csrf_secret"] = secret
    nonce = secrets.token_urlsafe(16)
    exp = int(time.time()) + CSRF_TTL
    payload = f"{action}|{exp}|{nonce}".encode()
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    return f"{_b64e(payload)}.{_b64e(sig)}"


def csrf_ok(action):
    """Constant-time verify of a single-use, action-bound CSRF token."""
    token = request.form.get("csrf_token", "")
    secret = session.get("csrf_secret")
    if not secret or "." not in token:
        return False
    p_b64, s_b64 = token.rsplit(".", 1)
    try:
        payload = _b64d(p_b64)
        sig = _b64d(s_b64)
    except Exception:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        return False
    try:
        act, exp_s, nonce = payload.decode().split("|")
        exp = int(exp_s)
    except Exception:
        return False
    if act != action or exp < time.time() or not nonce:
        return False
    used = session.setdefault("csrf_used", [])
    if nonce in used:
        return False  # replay of a consumed token
    used.append(nonce)
    session["csrf_used"] = used[-CSRF_USED_MAX:]
    return True


# ---------------- Input validation helpers (round 2) ----------------
# HARDEN (round 2): bounds that keep the lab usable (tests/clients use short
# values) while blocking oversized/garbage input before it reaches hashing,
# the DB or the HMAC paths.
USERNAME_MIN, USERNAME_MAX = 1, 64
PASSWORD_MAX = 1024


def _valid_username(username):
    return (
        USERNAME_MIN <= len(username) <= USERNAME_MAX
        and all(ord(c) >= 32 for c in username)
    )


# ---------------- Auth routes ----------------

@app.route("/")
def home():
    u = current_user()
    return page(
        "<h2>Welcome to the subscription lab.</h2>"
        "<p>Sign up, log in, and try the premium tier.</p>",
        u,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        if not csrf_ok("register"):
            abort(403)
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        # HARDEN (round 2): throttle account creation per account-name and
        # per source IP (bulk registration / enumeration).
        if _rate_limited("register-user", f"{_client_ip()}|{username}", 5) or \
                _rate_limited("register-ip", _client_ip(), 60):
            return too_many_requests()
        # HARDEN (round 2): input validation before hashing/insert.
        if not _valid_username(username):
            msg = "<p style='color:red'>Invalid username (1-64 chars).</p>"
        elif not (1 <= len(password) <= PASSWORD_MAX):
            msg = "<p style='color:red'>Invalid password.</p>"
        else:
            # FIX (was VULN: string-built SQL): parameterized query; role is
            # server-controlled ('free'), never taken from client input.
            conn = get_db()
            try:
                cur = conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, 'free')",
                    (username, generate_password_hash(password)),
                )
                conn.execute(
                    "INSERT INTO subscriptions (user_id, plan, status) VALUES (?, 'free', 'active')",
                    (cur.lastrowid,),
                )
                conn.commit()
                conn.close()
                return page("<p>Registered! <a href='/login'>Log in</a></p>")
            except sqlite3.IntegrityError:
                conn.rollback()
                conn.close()
                msg = "<p style='color:red'>Username already taken.</p>"
            except Exception:
                # FIX (was VULN: verbose errors): generic message to client,
                # details only in server logs.
                conn.rollback()
                conn.close()
                app.logger.exception("registration failed")
                msg = "<p style='color:red'>Registration failed. Please try again.</p>"
    form = """<h2>Register</h2>
    <form method="post">
    <input type="hidden" name="csrf_token" value="%s">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Sign up</button></form>""" % csrf_token("register") + msg
    return page(form)


# FIX (was VULN: plaintext compare / no hashing): verify hash.
# HARDEN (round 2): compare against a dummy hash when the username does not
# exist so response timing does not reveal which usernames are registered.
_DUMMY_PASSWORD_HASH = generate_password_hash("timing-equalizer-placeholder")


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        if not csrf_ok("login"):
            abort(403)
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        # HARDEN (round 2): throttle credential guessing per account AND per
        # IP (the IP bucket catches distributed single-password sprays).
        if _rate_limited("login-user", f"{_client_ip()}|{username}", 5) or \
                _rate_limited("login-ip", _client_ip(), 90):
            return too_many_requests()
        if not _valid_username(username) or len(password) > PASSWORD_MAX:
            msg = "<p style='color:red'>Invalid credentials.</p>"
        else:
            conn = get_db()
            try:
                # FIX (was VULN: SQL injection in login): parameterized query.
                row = conn.execute(
                    "SELECT * FROM users WHERE username = ?", (username,)
                ).fetchone()
            finally:
                conn.close()
            # Always run a hash comparison (dummy hash for unknown users)
            # so timing does not disclose account existence.
            password_ok = check_password_hash(
                row["password"] if row else _DUMMY_PASSWORD_HASH, password
            )
            # FIX (was VULN: client-controllable session flags): the session
            # stores ONLY the username. Role/premium are re-derived from the
            # DB on every request - nothing privileged is cookie-controlled.
            # session.clear() also rotates the CSRF secret (fixation defense).
            if row and password_ok:
                session.clear()
                session["username"] = row["username"]
                session.permanent = True
                return redirect(url_for("status"))
            msg = "<p style='color:red'>Invalid credentials.</p>"
    form = """<h2>Login</h2>
    <form method="post">
    <input type="hidden" name="csrf_token" value="%s">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Log in</button></form>""" % csrf_token("login") + msg
    return page(form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/status")
@login_required
def status():
    u = current_user()
    conn = get_db()
    try:
        sub = conn.execute(
            "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (u["id"],),
        ).fetchone()
    finally:
        conn.close()
    plan = sub["plan"] if sub else "free"
    # HARDEN (round 2): escape DB-derived values before they enter the
    # |safe body (defense in depth; role/plan are server-controlled today).
    body = f"""<h2>Subscription status</h2>
    <p>Plan: <b>{escape(plan)}</b></p>
    <p>Role (from DB): <b>{escape(u['role'])}</b></p>
    <p>Premium access: <b>{escape(str(is_premium(u)))}</b></p>
    <p><a href="/upgrade">Upgrade to Premium ($9.99/mo)</a></p>"""
    return page(body, u)


# ---------------- Payment flow (server-authoritative) ----------------

def grant_premium(user_id, payment_id):
    """Only called after a payment row is verified 'succeeded'.
    HARDEN (round 2): the role + subscription writes are one transaction."""
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE users SET role = 'premium' WHERE id = ?", (user_id,))
        conn.execute(
            "UPDATE subscriptions SET plan = 'premium', status = 'active' WHERE user_id = ?",
            (user_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        app.logger.exception("grant_premium failed for payment %s", payment_id)
    finally:
        conn.close()


@app.route("/upgrade", methods=["GET", "POST"])
@login_required
def upgrade():
    u = current_user()
    if request.method == "GET":
        return page(
            """<h2>Upgrade to Premium</h2>
            <form method="post">
            <input type="hidden" name="csrf_token" value="%s">
            <input type="hidden" name="plan" value="premium">
            <button type="submit">Pay $9.99 (mock gateway)</button>
            </form>"""
            % csrf_token("payment"),
            u,
        )
    if not csrf_ok("payment"):
        abort(403)
    # HARDEN (round 2): throttle checkout creation per user and per IP.
    if _rate_limited("upgrade-user", f"{_client_ip()}|{u['id']}", 10) or \
            _rate_limited("upgrade-ip", _client_ip(), 60):
        return too_many_requests()

    # FIX (was VULN: client-supplied payment_success flag): the client can
    # only request a plan. Price is looked up server-side; a PENDING payment
    # is created. Nothing is granted here.
    plan = request.form.get("plan", "")
    if plan not in PLAN_PRICES:
        return page("<p style='color:red'>Invalid plan.</p>", u), 400
    amount = PLAN_PRICES[plan]  # server-authoritative amount

    conn = get_db()
    try:
        # HARDEN (round 2): BEGIN IMMEDIATE serializes concurrent checkouts;
        # any earlier pending payment for this user is failed first so a
        # user cannot stack payable checkouts (one-pending invariant).
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "UPDATE payments SET status = 'failed' "
            "WHERE user_id = ? AND status = 'pending'",
            (u["id"],),
        )
        cur = conn.execute(
            "INSERT INTO payments (user_id, amount_cents, status) VALUES (?, ?, 'pending')",
            (u["id"], amount),
        )
        payment_id = cur.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        # unique-index race fallback: someone else just created a pending row
        conn.rollback()
        conn.close()
        return page(
            "<p style='color:red'>You already have a pending payment. "
            "Complete or wait for it to expire.</p>",
            u,
        ), 409
    except Exception:
        conn.rollback()
        conn.close()
        app.logger.exception("upgrade payment creation failed")
        return page("<p style='color:red'>Checkout failed. Please try again.</p>", u), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Hand off to the mock gateway. The gateway signature proves the
    # redirect came from our checkout; the gateway re-verifies the amount
    # against the DB before marking the payment succeeded.
    sig = hmac.new(
        PAYMENT_SECRET.encode(), f"{payment_id}:{amount}".encode(), hashlib.sha256
    ).hexdigest()
    return page(
        f"""<h2>Checkout</h2>
        <p>Amount due: <b>${amount / 100:.2f}</b> (plan: {escape(plan)})</p>
        <form method="post" action="/gateway/charge">
        <input type="hidden" name="csrf_token" value="{csrf_token('payment')}">
        <input type="hidden" name="payment_id" value="{payment_id}">
        <input type="hidden" name="sig" value="{sig}">
        <button type="submit">Pay with mock gateway</button>
        </form>""",
        u,
    )


@app.route("/gateway/charge", methods=["POST"])
def gateway_charge():
    """Mock payment gateway. Verifies the checkout signature and the
    server-side amount, marks the payment succeeded, then activates the
    subscription. This is the ONLY user-facing path that can succeed a
    payment (besides the signed webhook below).

    HARDEN (round 2): CSRF enforced (same 'payment' action as /upgrade -
    the checkout form is part of that flow), rate limited, payment id must
    be numeric, and the pending->succeeded transition is an atomic
    compare-and-swap inside BEGIN IMMEDIATE so two concurrent charges can
    never both succeed the same payment."""
    if not csrf_ok("payment"):
        abort(403)
    if _rate_limited("charge-ip", _client_ip(), 60):
        return too_many_requests()
    payment_id = request.form.get("payment_id", "")
    sig = request.form.get("sig", "")
    # HARDEN (round 2): strict type check - payment ids are integers.
    if not payment_id.isdigit():
        return page("<p>Invalid payment reference.</p>"), 400

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        pay = conn.execute(
            "SELECT * FROM payments WHERE id = ?", (int(payment_id),)
        ).fetchone()
        if pay is None:
            conn.rollback()
            return page("<p>Invalid payment reference.</p>"), 400
        expected = hmac.new(
            PAYMENT_SECRET.encode(),
            f"{pay['id']}:{pay['amount_cents']}".encode(),
            hashlib.sha256,
        ).hexdigest()
        # FIX (was VULN: amount taken from client): amount comes from the DB row.
        if not hmac.compare_digest(sig, expected):
            conn.rollback()
            return page("<p style='color:red'>Gateway signature invalid.</p>"), 403
        # HARDEN (round 2): atomic compare-and-swap. Under BEGIN IMMEDIATE
        # concurrent requests serialize; the loser re-evaluates
        # status='pending' on committed data and gets rowcount 0.
        cur = conn.execute(
            "UPDATE payments SET status = 'succeeded', provider = 'mock' "
            "WHERE id = ? AND status = 'pending'",
            (pay["id"],),
        )
        if cur.rowcount != 1:
            conn.rollback()
            return page("<p>Invalid or already-completed payment.</p>"), 400
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("gateway charge failed")
        return page("<p>Payment failed. Please try again.</p>"), 500
    finally:
        conn.close()

    grant_premium(pay["user_id"], pay["id"])
    return page(
        "<p>Payment successful! You are now PREMIUM.</p>"
        "<a href='/premium'>View premium content</a>"
    )


# HARDEN (round 2): webhook replay protection state. Nonces are remembered
# server-side for the same window as the timestamp tolerance; the table is
# bounded so a flood of valid-signature requests cannot exhaust memory.
WEBHOOK_MAX_AGE = 300          # seconds; |now - timestamp| must be <= this
WEBHOOK_MAX_BODY = 64 * 1024
WEBHOOK_NONCES = {}            # nonce -> expiry epoch
WEBHOOK_NONCE_MAX = 10000


@app.route("/api/payments/webhook", methods=["POST"])
def payment_webhook():
    """Gateway-style webhook: requires a valid HMAC signature over the raw
    body AND a fresh timestamp + single-use nonce inside the signed payload.
    Idempotent - only pending payments transition to succeeded via an atomic
    compare-and-swap."""
    # HARDEN (round 2): throttle webhook floods per source IP.
    if _rate_limited("webhook-ip", _client_ip(), 120):
        return {"error": "rate limited"}, 429
    body = request.get_data()
    if len(body) > WEBHOOK_MAX_BODY:
        abort(413)
    sig = request.headers.get("X-Signature", "")
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        abort(403)
    try:
        event = json.loads(body)
    except Exception:
        abort(400)
    if not isinstance(event, dict):
        abort(400)

    # HARDEN (round 2): replay protection - the signed body must carry a
    # timestamp inside the tolerance window and a nonce never seen before.
    ts = event.get("timestamp")
    nonce = event.get("nonce")
    if (
        not isinstance(ts, (int, float))
        or isinstance(ts, bool)
        or abs(time.time() - ts) > WEBHOOK_MAX_AGE
    ):
        abort(403)  # stale or future-dated -> treat as replay/forgery
    if not isinstance(nonce, str) or not (8 <= len(nonce) <= 128):
        abort(400)
    now = time.time()
    for n, exp in list(WEBHOOK_NONCES.items()):
        if exp < now:
            WEBHOOK_NONCES.pop(n, None)
    if nonce in WEBHOOK_NONCES:
        abort(403)  # replayed nonce
    WEBHOOK_NONCES[nonce] = now + WEBHOOK_MAX_AGE
    if len(WEBHOOK_NONCES) > WEBHOOK_NONCE_MAX:
        oldest = sorted(WEBHOOK_NONCES, key=WEBHOOK_NONCES.get)[
            : len(WEBHOOK_NONCES) - WEBHOOK_NONCE_MAX
        ]
        for n in oldest:
            WEBHOOK_NONCES.pop(n, None)

    if event.get("event") != "payment.succeeded":
        return {"ok": True}
    pid = event.get("payment_id")
    # HARDEN (round 2): strict typing - payment ids are integers, nothing else.
    if type(pid) is not int:
        abort(400)

    conn = get_db()
    upgraded = False
    try:
        conn.execute("BEGIN IMMEDIATE")
        pay = conn.execute(
            "SELECT * FROM payments WHERE id = ?", (pid,)
        ).fetchone()
        if pay and pay["status"] == "pending":
            # HARDEN (round 2): re-verify the amount is a known
            # server-side price before granting anything.
            if pay["amount_cents"] in set(PLAN_PRICES.values()):
                conn.execute(
                    "UPDATE payments SET status = 'succeeded' WHERE id = ?",
                    (pay["id"],),
                )
                conn.commit()
                upgraded = True
            else:
                conn.rollback()
        else:
            conn.rollback()
    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("webhook payment update failed")
        abort(500)
    finally:
        conn.close()

    if upgraded:
        grant_premium(pay["user_id"], pay["id"])
        return {"ok": True, "upgraded": True}
    return {"ok": True, "upgraded": False}


# ---------------- Premium content ----------------

@app.route("/premium")
@login_required
def premium():
    u = current_user()
    # FIX (was VULN: authorization from client-influenceable session flag):
    # check role + subscription status from the DB on EVERY request.
    if not is_premium(u):
        return page(
            "<h2>Premium content</h2><p style='color:red'>"
            "403 - Premium members only. <a href='/upgrade'>Upgrade</a></p>",
            u,
        )
    body = """<h2>Premium content</h2>
    <p>SECRET_RECIPE_42: the secret ingredient is <b>unlimited retries</b>.</p>
    <p>Premium roadmap: quantum billing, AI support, and more.</p>"""
    return page(body, u)


# ---------------- Round-2: response headers & error handling -------------

@app.after_request
def _security_headers(response):
    """HARDEN (round 2): baseline security headers on every response."""
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    # HSTS only makes sense over TLS; emit it for secure requests or when
    # explicitly forced (e.g. behind a TLS-terminating proxy).
    if request.is_secure or os.environ.get("FORCE_HSTS") == "1":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    response.headers.pop("Server", None)
    return response


@app.errorhandler(404)
def _not_found(e):
    return page("<h2>404</h2><p>Page not found.</p>"), 404


@app.errorhandler(500)
def _server_error(e):
    # HARDEN (round 2): generic page to the client; Flask already logged the
    # traceback server-side. Never leak stack traces or SQL details.
    app.logger.error("unhandled 500: %s", e)
    return page("<h2>500</h2><p>Something went wrong on our side.</p>"), 500


if __name__ == "__main__":
    # FIX (was VULN: debug mode on): never run the debugger in this lab.
    app.run(host="127.0.0.1", port=5000, debug=False)

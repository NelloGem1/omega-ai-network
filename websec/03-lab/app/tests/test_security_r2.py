"""Round-2 hardening regression tests.

Covers: security headers, rate limiting (incl. X-Forwarded-For distrust),
single-use + action-bound CSRF tokens, webhook replay protection
(timestamp + nonce), atomic payment transitions under concurrency, the
one-pending-payment invariant, and input validation.
"""
import hashlib
import hmac
import json
import re
import sqlite3
import threading
import time

import app as lab_app
from conftest import get_csrf, register, register_and_login

SECRET_MARKER = "SECRET_RECIPE_42"


def _make_pending(client, username):
    """Register+login a fresh user and create a pending premium payment."""
    register_and_login(client, username)
    html = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    return int(re.search(r'name="payment_id" value="(\d+)"', html).group(1))


def _webhook_post(client, body, sig=True):
    headers = {}
    if sig:
        headers["X-Signature"] = hmac.new(
            lab_app.WEBHOOK_SECRET.encode(), body.encode(), hashlib.sha256
        ).hexdigest()
    return client.post(
        "/api/payments/webhook",
        data=body,
        content_type="application/json",
        headers=headers,
    )


def _signed_body(pid, nonce, ts=None):
    return json.dumps(
        {
            "event": "payment.succeeded",
            "payment_id": pid,
            "timestamp": time.time() if ts is None else ts,
            "nonce": nonce,
        }
    )


# ------------------------------------------------------- headers

def test_security_headers_present(client):
    r = client.get("/")
    h = r.headers
    assert "default-src 'self'" in h["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"]
    assert h["X-Frame-Options"] == "DENY"
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["Referrer-Policy"] == "no-referrer"
    assert "camera=()" in h["Permissions-Policy"]


def test_security_headers_on_error_responses(client):
    r = client.get("/definitely-not-a-route")
    assert r.status_code == 404
    assert r.headers["X-Content-Type-Options"] == "nosniff"


# ------------------------------------------------------- rate limits

def test_login_rate_limit_triggers(client):
    """6th login attempt for the same (ip, username) inside 60s -> 429."""
    codes = []
    for _ in range(7):
        r = client.post(
            "/login",
            data={
                "username": "rl_login_user",
                "password": "wrong",
                "csrf_token": get_csrf(client, "/login"),
            },
            follow_redirects=False,
        )
        codes.append(r.status_code)
    assert codes[:5] == [200] * 5
    assert codes[5] == 429 and codes[6] == 429


def test_register_rate_limit_per_username(client):
    codes = []
    for _ in range(7):
        r = client.post(
            "/register",
            data={
                "username": "rl_reg_user",
                "password": "pw12345",
                "csrf_token": get_csrf(client, "/register"),
            },
        )
        codes.append(r.status_code)
    assert codes[-1] == 429
    assert 429 in codes


def test_xff_does_not_bypass_rate_limit(client):
    """X-Forwarded-For is attacker-controlled (no trusted proxy): rotating
    it must NOT reset the per-account login throttle."""
    codes = []
    for i in range(6):
        r = client.post(
            "/login",
            data={
                "username": "xff_victim",
                "password": "wrong",
                "csrf_token": get_csrf(client, "/login"),
            },
            headers={"X-Forwarded-For": f"10.9.9.{i}"},
            follow_redirects=False,
        )
        codes.append(r.status_code)
    assert codes[-1] == 429


# ------------------------------------------------------- CSRF round 2

def test_csrf_token_is_single_use(client):
    tok = get_csrf(client, "/login")
    r1 = client.post(
        "/login",
        data={"username": "demo", "password": "wrong-pw", "csrf_token": tok},
        follow_redirects=False,
    )
    assert r1.status_code == 200  # token consumed, bad credentials
    r2 = client.post(
        "/login",
        data={"username": "demo", "password": "wrong-pw", "csrf_token": tok},
        follow_redirects=False,
    )
    assert r2.status_code == 403  # replayed token rejected


def test_csrf_token_bound_to_action(client):
    """A token minted for /login must not be accepted by /register."""
    tok = get_csrf(client, "/login")
    r = client.post(
        "/register",
        data={"username": "csrfbind", "password": "pw12345", "csrf_token": tok},
    )
    assert r.status_code == 403


def test_csrf_token_forged_signature_rejected(client):
    """Tampering with the token payload invalidates the HMAC."""
    tok = get_csrf(client, "/register")
    p_b64, s_b64 = tok.rsplit(".", 1)
    forged = p_b64[:-2] + ("AA" if not p_b64.endswith("AA") else "BB") + "." + s_b64
    r = client.post(
        "/register",
        data={"username": "csrfforge", "password": "pw12345", "csrf_token": forged},
    )
    assert r.status_code == 403


# ------------------------------------------------------- webhook replay

def test_webhook_replay_same_nonce_rejected(client):
    pid = _make_pending(client, "wh_replay")
    body = _signed_body(pid, "replay-nonce-0001")
    r1 = _webhook_post(client, body)
    assert r1.status_code == 200 and r1.get_json()["upgraded"] is True
    r2 = _webhook_post(client, body)  # byte-identical replay
    assert r2.status_code == 403
    assert SECRET_MARKER in client.get("/premium").get_data(as_text=True)


def test_webhook_missing_timestamp_rejected(client):
    pid = _make_pending(client, "wh_no_ts")
    body = json.dumps(
        {"event": "payment.succeeded", "payment_id": pid, "nonce": "no-ts-nonce-1"}
    )
    r = _webhook_post(client, body)
    assert r.status_code == 403
    assert SECRET_MARKER not in client.get("/premium").get_data(as_text=True)


def test_webhook_stale_timestamp_rejected(client):
    pid = _make_pending(client, "wh_stale")
    body = _signed_body(pid, "stale-nonce-001", ts=time.time() - 3600)
    r = _webhook_post(client, body)
    assert r.status_code == 403


def test_webhook_future_timestamp_rejected(client):
    pid = _make_pending(client, "wh_future")
    body = _signed_body(pid, "future-nonce-01", ts=time.time() + 3600)
    r = _webhook_post(client, body)
    assert r.status_code == 403


def test_webhook_missing_nonce_rejected(client):
    pid = _make_pending(client, "wh_no_nonce")
    body = json.dumps(
        {
            "event": "payment.succeeded",
            "payment_id": pid,
            "timestamp": time.time(),
        }
    )
    r = _webhook_post(client, body)
    assert r.status_code == 400


def test_webhook_non_integer_payment_id_rejected(client):
    # payment_id as a string must be rejected even with a valid signature
    body = json.dumps(
        {
            "event": "payment.succeeded",
            "payment_id": "1",
            "timestamp": time.time(),
            "nonce": "strpid-nonce-002",
        }
    )
    r = _webhook_post(client, body)
    assert r.status_code == 400


def test_webhook_unsigned_still_rejected_with_new_fields(client):
    pid = _make_pending(client, "wh_unsigned2")
    body = _signed_body(pid, "unsigned-nonce-1")
    r = _webhook_post(client, body, sig=False)
    assert r.status_code == 403


# ------------------------------------------------------- payment races

def test_gateway_charge_concurrent_single_winner(client):
    """8 simultaneous charges of the SAME payment: exactly one may win."""
    register_and_login(client, "racepay")
    html = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    pid = re.search(r'name="payment_id" value="(\d+)"', html).group(1)
    sig = re.search(r'name="sig" value="([0-9a-f]+)"', html).group(1)
    cookie = client.get_cookie("session")

    results = []

    def worker(_i):
        tc = lab_app.app.test_client()
        tc.set_cookie("session", cookie.value, domain="localhost")
        # each thread mints its own single-use 'payment' token via GET /upgrade
        tok = get_csrf(tc, "/upgrade")
        r = tc.post(
            "/gateway/charge",
            data={"payment_id": pid, "sig": sig, "csrf_token": tok},
        )
        results.append(r.status_code)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(results) == 8
    assert results.count(200) == 1, f"expected exactly one success: {results}"
    assert results.count(400) == 7, f"losers must get 400: {results}"
    # and the DB shows the payment succeeded exactly once
    conn = sqlite3.connect(lab_app.DB_PATH)
    row = conn.execute(
        "SELECT status FROM payments WHERE id = ?", (int(pid),)
    ).fetchone()
    conn.close()
    assert row[0] == "succeeded"
    assert SECRET_MARKER in client.get("/premium").get_data(as_text=True)


def test_webhook_concurrent_single_winner(client):
    """Parallel webhook deliveries (distinct nonces) for one payment:
    exactly one reports upgraded=true."""
    pid = _make_pending(client, "whrace")
    results = []

    def worker(i):
        tc = lab_app.app.test_client()
        body = _signed_body(pid, f"race-webhook-nonce-{i:04d}-x")
        r = _webhook_post(tc, body)
        results.append((r.status_code, r.get_json()))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(results) == 6
    winners = [r for r in results if r[1].get("upgraded") is True]
    assert len(winners) == 1, f"expected one winner: {results}"
    assert all(r[0] == 200 for r in results)


def test_second_upgrade_supersedes_pending(client):
    """One-pending invariant: a second /upgrade fails the first pending row."""
    register_and_login(client, "multipay")
    h1 = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    pid1 = int(re.search(r'name="payment_id" value="(\d+)"', h1).group(1))
    h2 = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    pid2 = int(re.search(r'name="payment_id" value="(\d+)"', h2).group(1))
    assert pid1 != pid2
    conn = sqlite3.connect(lab_app.DB_PATH)
    rows = conn.execute(
        "SELECT id, status FROM payments WHERE user_id = "
        "(SELECT id FROM users WHERE username = 'multipay') ORDER BY id"
    ).fetchall()
    conn.close()
    pendings = [r for r in rows if r[1] == "pending"]
    assert len(pendings) == 1 and pendings[0][0] == pid2
    # the superseded payment can no longer be charged
    sig1 = re.search(r'name="sig" value="([0-9a-f]+)"', h1).group(1)
    r = client.post(
        "/gateway/charge",
        data={
            "payment_id": str(pid1),
            "sig": sig1,
            "csrf_token": get_csrf(client, "/upgrade"),
        },
    )
    assert r.status_code == 400


# ------------------------------------------------------- input validation

def test_oversized_username_rejected(client):
    r = register(client, "u" * 200)
    html = r.get_data(as_text=True)
    assert "Invalid username" in html
    conn = sqlite3.connect(lab_app.DB_PATH)
    n = conn.execute(
        "SELECT COUNT(*) FROM users WHERE username = ?", ("u" * 200,)
    ).fetchone()[0]
    conn.close()
    assert n == 0


def test_empty_password_rejected(client):
    r = client.post(
        "/register",
        data={
            "username": "emptypw2",
            "password": "",
            "csrf_token": get_csrf(client, "/register"),
        },
    )
    assert "Invalid password" in r.get_data(as_text=True)


def test_gateway_charge_rejects_non_numeric_payment_id(client):
    register_and_login(client, "badpid")
    r = client.post(
        "/gateway/charge",
        data={
            "payment_id": "1; DROP TABLE payments--",
            "sig": "x",
            "csrf_token": get_csrf(client, "/upgrade"),
        },
    )
    assert r.status_code == 400

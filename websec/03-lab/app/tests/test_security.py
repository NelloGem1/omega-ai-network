"""Regression tests: every exploit proven during the audit must now FAIL."""
import hashlib
import hmac
import json
import sqlite3

import pytest

import app as lab_app
from conftest import get_csrf, login, register, register_and_login

SECRET_MARKER = "SECRET_RECIPE_42"


def premium_denied(client):
    return SECRET_MARKER not in client.get("/premium").get_data(as_text=True)


# ---------------------------------------------------------------- SQLi

def test_sqli_login_bypass_blocked(client):
    """' OR 1=1-- must NOT log anyone in."""
    r = client.post(
        "/login",
        data={
            "username": "' OR 1=1--",
            "password": "x",
            "csrf_token": get_csrf(client, "/login"),
        },
        follow_redirects=False,
    )
    assert r.status_code != 302
    status = client.get("/status").get_data(as_text=True)
    assert "Please" in status or "log in" in status


def test_sqli_register_cannot_create_premium(client):
    """INSERT injection that tries to set role='premium' is stored literally."""
    injected = "sqli_p2','pw','premium')--"
    register(client, injected, "x")
    login(client, injected, "x")
    assert premium_denied(client)
    # and the DB role must still be 'free'
    conn = sqlite3.connect(lab_app.DB_PATH)
    row = conn.execute(
        "SELECT role FROM users WHERE username = ?", (injected,)
    ).fetchone()
    conn.close()
    assert row is not None and row[0] == "free"


def test_sqli_union_data_exfil_not_possible(client):
    """A UNION-style payload must not authenticate."""
    r = client.post(
        "/login",
        data={
            "username": "' UNION SELECT 1,'a','b','free'--",
            "password": "x",
            "csrf_token": get_csrf(client, "/login"),
        },
        follow_redirects=False,
    )
    assert r.status_code != 302 or "session" not in r.headers.get("Set-Cookie", "")


# ------------------------------------------------------- passwords

def test_passwords_are_hashed(client):
    register(client, "hashcheck")
    conn = sqlite3.connect(lab_app.DB_PATH)
    stored = conn.execute(
        "SELECT password FROM users WHERE username = 'hashcheck'"
    ).fetchone()[0]
    conn.close()
    assert stored != "pw12345"
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_wrong_password_rejected(client):
    register_and_login(client, "wrongpw")
    client.get("/logout")
    r = login(client, "wrongpw", "not-the-password")
    assert r.status_code != 302


# -------------------------------------------------------- session

def test_session_cookie_cannot_be_forged_with_old_secret(client):
    """The old hardcoded 'dev-secret-change-me' key must no longer work."""
    from flask import Flask
    from flask.sessions import SecureCookieSessionInterface

    evil_app = Flask(__name__)
    evil_app.secret_key = "dev-secret-change-me"
    serializer = SecureCookieSessionInterface().get_signing_serializer(evil_app)
    forged = serializer.dumps(
        {"username": "demo", "is_premium": True, "role": "admin"}
    )
    client.set_cookie("session", forged)
    status = client.get("/status").get_data(as_text=True)
    assert "Please" in status or "log in" in status


def test_session_flags_are_not_authoritative(client):
    """Even a validly-signed session carrying is_premium=True gets nothing:
    /premium re-checks role + subscription in the DB."""
    register_and_login(client, "flagger")
    with client.session_transaction() as sess:
        sess["is_premium"] = True
        sess["role"] = "premium"
        sess["username"] = "flagger"
    assert premium_denied(client)


# -------------------------------------------------------- payment

def test_client_payment_success_flag_ignored(client):
    register_and_login(client, "payer1")
    client.post(
        "/upgrade",
        data={"payment_success": "1", "csrf_token": get_csrf(client, "/upgrade")},
    )
    assert premium_denied(client)


def test_premium_plan_name_alone_grants_nothing(client):
    register_and_login(client, "payer2")
    client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    )
    # a pending payment was created, but nothing granted yet
    assert premium_denied(client)


def test_gateway_rejects_forged_signature(client):
    register_and_login(client, "payer3")
    html = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    import re

    pid = re.search(r'name="payment_id" value="(\d+)"', html).group(1)
    r = client.post(
        "/gateway/charge",
        data={
            "payment_id": pid,
            "sig": "0" * 64,
            "csrf_token": get_csrf(client, "/upgrade"),
        },
    )
    assert r.status_code == 403
    assert premium_denied(client)


def test_gateway_rejects_replayed_payment(client):
    """Once a payment succeeds it cannot be charged again."""
    register_and_login(client, "payer4")
    html = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    import re

    pid = re.search(r'name="payment_id" value="(\d+)"', html).group(1)
    sig = re.search(r'name="sig" value="([0-9a-f]+)"', html).group(1)
    data = {"payment_id": pid, "sig": sig}
    client.post("/gateway/charge", data={**data, "csrf_token": get_csrf(client, "/upgrade")})
    r = client.post(
        "/gateway/charge",
        data={**data, "csrf_token": get_csrf(client, "/upgrade")},
    )
    assert r.status_code == 400


def test_legitimate_payment_flow_still_works(client):
    register_and_login(client, "payer5")
    html = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    import re

    pid = re.search(r'name="payment_id" value="(\d+)"', html).group(1)
    sig = re.search(r'name="sig" value="([0-9a-f]+)"', html).group(1)
    client.post(
        "/gateway/charge",
        data={
            "payment_id": pid,
            "sig": sig,
            "csrf_token": get_csrf(client, "/upgrade"),
        },
    )
    assert SECRET_MARKER in client.get("/premium").get_data(as_text=True)


# -------------------------------------------------------- webhook

def _pending_payment_id(client):
    import re

    register_and_login(client, "wh_user")
    html = client.post(
        "/upgrade",
        data={"plan": "premium", "csrf_token": get_csrf(client, "/upgrade")},
    ).get_data(as_text=True)
    return int(re.search(r'name="payment_id" value="(\d+)"', html).group(1))


def test_webhook_rejects_missing_signature(client):
    pid = _pending_payment_id(client)
    body = json.dumps({"event": "payment.succeeded", "payment_id": pid})
    r = client.post("/api/payments/webhook", data=body, content_type="application/json")
    assert r.status_code == 403
    assert premium_denied(client)


def test_webhook_rejects_wrong_signature(client):
    pid = _pending_payment_id(client)
    body = json.dumps({"event": "payment.succeeded", "payment_id": pid})
    r = client.post(
        "/api/payments/webhook",
        data=body,
        content_type="application/json",
        headers={"X-Signature": "bad"},
    )
    assert r.status_code == 403
    assert premium_denied(client)


def test_webhook_accepts_valid_signature(client):
    pid = _pending_payment_id(client)
    # round 2: signed body must also carry a fresh timestamp + nonce
    body = json.dumps(
        {
            "event": "payment.succeeded",
            "payment_id": pid,
            "timestamp": __import__("time").time(),
            "nonce": "round1-valid-nonce-01",
        }
    )
    sig = hmac.new(
        lab_app.WEBHOOK_SECRET.encode(), body.encode(), hashlib.sha256
    ).hexdigest()
    r = client.post(
        "/api/payments/webhook",
        data=body,
        content_type="application/json",
        headers={"X-Signature": sig},
    )
    assert r.status_code == 200
    assert SECRET_MARKER in client.get("/premium").get_data(as_text=True)


# -------------------------------------------------------- misc

def test_verbose_errors_not_leaked(client):
    r = register(client, "bad'user", "x")
    html = r.get_data(as_text=True)
    assert "syntax error" not in html and "near" not in html


def test_csrf_required_on_login(client):
    r = client.post("/login", data={"username": "demo", "password": "demo123"})
    assert r.status_code == 403


def test_premium_requires_login(client):
    # fresh client, no session
    fresh = lab_app.app.test_client()
    html = fresh.get("/premium").get_data(as_text=True)
    assert SECRET_MARKER not in html

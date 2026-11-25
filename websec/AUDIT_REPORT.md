# Security Audit Report — NelloGem SubLab (Flask subscription app)

**Target:** `/home/neilh/websec_lab/app/app.py` (+ `schema.sql`)
**Date:** 2026-11-25
**Method:** manual code review → live exploit PoCs (curl/python-requests against `http://127.0.0.1:5000`) → remediation → pytest regression suite.

> Note: the setup agent's scaffold was initially missing; it appeared mid-audit.
> The vulnerable original is preserved at `app/app_vulnerable.py`; the fixed
> version is `app/app.py` (each fix is annotated `# FIX (was VULN: ...)`).

---

## Summary

| # | Vulnerability | Severity | Status |
|---|---------------|----------|--------|
| 1 | SQL injection — login auth bypass | Critical | Fixed + tested |
| 2 | SQL injection — register privilege escalation | Critical | Fixed + tested |
| 3 | Client-trusted payment flag (`payment_success=1`) | Critical | Fixed + tested |
| 4 | Session-cookie forgery (hardcoded secret) + trusted session flags | High | Fixed + tested |
| 5 | Plaintext password storage | High | Fixed + tested |
| 6 | Verbose error messages leak SQL internals | Medium | Fixed + tested |
| 7 | Unsigned/absent webhook verification (new endpoint added with HMAC) | High | Fixed + tested |
| 8 | Missing CSRF protection + `debug=True` | Medium | Fixed + tested |
| 9 | DB connection leaks on error paths (found during fix verification) | Low | Fixed |

---

## VULN 1 — SQL injection in `/login` (auth bypass)

**Location:** `app.py` login route — `"SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)`

**PoC:**
```bash
curl -c jar -X POST http://127.0.0.1:5000/login \
  --data-urlencode "username=' OR 1=1--" --data-urlencode "password=x"
# -> 302 redirect; session authenticated as 'demo' WITHOUT a password
curl -b jar http://127.0.0.1:5000/status
# -> Logged in as demo (role: free)
```

**Fix:** parameterized query `WHERE username = ?`, then `check_password_hash()` against the stored hash. Session now stores only `username`.

**Regression test:** `test_sqli_login_bypass_blocked`, `test_sqli_union_data_exfil_not_possible`

---

## VULN 2 — SQL injection in `/register` (privilege escalation)

**Location:** register route — `INSERT INTO users ... VALUES ('%s','%s','free')` built with `%` formatting.

**PoC:**
```bash
curl -X POST http://127.0.0.1:5000/register \
  --data-urlencode "username=evil', 'pw', 'premium')--" --data-urlencode "password=x"
# -> Registered!  then login as evil/pw -> /premium returns SECRET_RECIPE_42
```

**Fix:** parameterized INSERT; `role` is hard-coded server-side to `'free'` — client input can never reach the role column.

**Regression test:** `test_sqli_register_cannot_create_premium` (asserts injected username stored literally and DB role stays `free`)

---

## VULN 3 — Payment bypass via client-side flag

**Location:** `/upgrade` POST — `paid = request.form.get("payment_success") == "1"` then granted premium + wrote a fake payment row.

**PoC:**
```bash
# as a normal free user:
curl -b jar -c jar -X POST http://127.0.0.1:5000/upgrade --data-urlencode "payment_success=1"
# -> "Payment successful! You are now PREMIUM."  (no money moved)
curl -b jar http://127.0.0.1:5000/premium   # -> SECRET_RECIPE_42
```

**Fix (server-authoritative payment):**
- `/upgrade` accepts only a plan **name**; price comes from server-side `PLAN_PRICES` allowlist. It creates a `payments` row with `status='pending'` — nothing is granted.
- `/gateway/charge` (mock gateway) verifies an HMAC signature `HMAC(PAYMENT_SECRET, "{payment_id}:{amount}")` and the amount **from the DB row**, marks the payment `succeeded`, then activates the subscription.
- `/api/payments/webhook` accepts gateway-style confirmations only with a valid `X-Signature` HMAC over the raw body (`PAYMENT_WEBHOOK_SECRET`), idempotent on `pending` payments.
- Both secrets come from env vars (`PAYMENT_SECRET`, `PAYMENT_WEBHOOK_SECRET`), random per boot otherwise.

**Regression tests:** `test_client_payment_success_flag_ignored`, `test_premium_plan_name_alone_grants_nothing`, `test_gateway_rejects_forged_signature`, `test_gateway_rejects_replayed_payment`, `test_legitimate_payment_flow_still_works`, `test_webhook_rejects_missing_signature`, `test_webhook_rejects_wrong_signature`, `test_webhook_accepts_valid_signature`

---

## VULN 4 — Session forgery + client-controllable session flags

**Two layers:**
1. `app.secret_key = "dev-secret-change-me"` (hardcoded, public in source) → anyone can mint valid session cookies.
2. `/premium` authorized solely on `session["is_premium"]`, which the client could also influence.

**PoC:**
```python
from flask.sessions import SecureCookieSessionInterface
from flask import Flask
app = Flask(__name__); app.secret_key = "dev-secret-change-me"
s = SecureCookieSessionInterface().get_signing_serializer(app)
print(s.dumps({"username": "demo", "is_premium": True, "role": "admin"}))
```
```bash
curl -H "Cookie: session=<forged>" http://127.0.0.1:5000/premium
# -> SECRET_RECIPE_42 for FREE user 'demo'; /status showed role: admin
```

**Fix:**
- `secret_key` from `APP_SECRET_KEY` env var, else `secrets.token_hex(32)` per boot.
- Session stores **only** `username` (+ CSRF token). `role`/`is_premium` session keys removed entirely.
- `/premium` calls `is_premium(user)` which re-reads `users.role` **and** the latest `subscriptions.status` from SQLite on every request.

**Regression tests:** `test_session_cookie_cannot_be_forged_with_old_secret`, `test_session_flags_are_not_authoritative`

---

## VULN 5 — Plaintext password storage

**PoC:** `sqlite3 lab.db "SELECT username,password,role FROM users"` → `('demo','demo123','free')`, etc.

**Fix:** `werkzeug.security.generate_password_hash` / `check_password_hash` (scrypt/PBKDF2) at register and login; demo seed also hashed.

**Regression tests:** `test_passwords_are_hashed`, `test_wrong_password_rejected`

---

## VULN 6 — Verbose error messages

**PoC:** `POST /register username=bad'user` → `Error: near "user": syntax error` (raw SQLite error + confirms injectable query).

**Fix:** generic `"Registration failed. Please try again."` to the client; `app.logger.exception(...)` server-side only.

**Regression test:** `test_verbose_errors_not_leaked`

---

## VULN 7 — Payment webhook had no authentication (hardened)

The original app had no webhook at all — payment state was purely client-driven. The fix introduces `/api/payments/webhook`, which **requires** `X-Signature: HMAC_SHA256(PAYMENT_WEBHOOK_SECRET, raw_body)`; unsigned/tampered bodies get 403 and cannot move a payment out of `pending`.

**Regression tests:** `test_webhook_rejects_missing_signature`, `test_webhook_rejects_wrong_signature`, `test_webhook_accepts_valid_signature`

---

## VULN 8 — `debug=True` + no CSRF protection

**Fix:**
- `app.run(..., debug=False)`.
- Per-session CSRF token (`secrets.token_urlsafe(32)`) rendered as a hidden field in every POST form; `csrf_ok()` enforced on `/register`, `/login`, `/upgrade`, `/gateway/charge`. Tokens are rotated on login (`session.clear()`).

**Regression test:** `test_csrf_required_on_login`

---

## Additional fix found during remediation

- **SQLite connection leaks:** the original `register()` never closed the connection on `IntegrityError`/generic exceptions; repeated failed registrations left RESERVED locks → `database is locked` for all subsequent writes. All DB access now uses try/finally `conn.close()` (+ `rollback()` on error).

---

## Verification

```
$ cd /home/neilh/websec_lab/app && /home/neilh/venv/bin/python -m pytest tests/ -q
..................                                                       [100%]
18 passed in 3.28s
```

A live re-run of every original exploit (SQLi login, SQLi register→premium,
`payment_success=1` bypass, forged session cookie, error leakage, unsigned
webhook, missing CSRF) against the fixed app confirmed **all are blocked**,
while the legitimate register → login → upgrade → mock-gateway → premium flow
still works end-to-end.

## Remaining recommendations (out of scope for this lab)

- Move secrets to a real secrets manager; never fall back to random-per-boot in production (sessions invalidate on restart).
- Add rate limiting on `/login` and `/register`.
- Replace the mock gateway with a real provider (Stripe) and verify webhook signatures per their docs.
- Use Flask-WTF / a maintained CSRF library instead of the hand-rolled token.
- Serve over HTTPS; set `SESSION_COOKIE_SECURE/HTTPONLY/SAMESITE` explicitly.
- `{{ body|safe }}` remains — safe today because all interpolated values are server-controlled, but prefer escaping user data explicitly.

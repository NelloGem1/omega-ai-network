# Defense Round 2 — WebSec Lab subscription app

**Date:** 2026-11-25 · **Target:** `/home/neilh/websec_lab/app/app.py`
**Context:** round-1 fixes (9 vulns, 18 tests) were live and being attacked.
This round anticipated the next wave: race conditions on payments, HMAC
webhook forgery/replay, CSRF token abuse, rate-limit brute force,
second-order SQLi, session fixation, error leaks, mass assignment.

All changes are annotated `# HARDEN (round 2): <reason>` in `app.py`.
Round-1 `# FIX` markers and behavior are preserved.

---

## What was still weak (adversarial self-review of round 1)

| # | Gap found | Risk | Fix added |
|---|-----------|------|-----------|
| R2-1 | **No rate limiting anywhere** — `/login`, `/register`, `/upgrade`, `/gateway/charge`, webhook unlimited | Online brute force / credential stuffing / webhook floods | In-memory fixed-window limiter; per-(IP+identity) AND per-IP buckets on every POST endpoint |
| R2-2 | **X-Forwarded-For would have been trusted blindly** had it been used | Attacker rotates XFF to evade IP limits | Only `request.remote_addr` is used (no ProxyFix configured → XFF is attacker-controlled). Verified by test |
| R2-3 | **CSRF token was per-session, never expired, reusable forever, same token for every form** | Token replay, cross-endpoint reuse, long-lived captured tokens | Tokens are now HMAC-signed `(action, expiry=1h, nonce)` with a per-session secret; **single-use** (used nonces recorded in signed session cookie, capped at 48); action-bound so a login token can't POST to register/upgrade |
| R2-4 | **Payment transition was check-then-act** (`SELECT` status → `UPDATE`) — TOCTOU race | Two concurrent `/gateway/charge` or webhook requests both see `pending` → double success | Atomic compare-and-swap `UPDATE ... WHERE id=? AND status='pending'` inside `BEGIN IMMEDIATE`; loser gets `rowcount=0` → HTTP 400 |
| R2-5 | **No one-pending-payment invariant** — attacker could stack unlimited pending checkouts (observed live: user 13 had 2 pending rows) | Payment spam, confusing ledger, index pressure | `/upgrade` fails prior pendings in the same `BEGIN IMMEDIATE` tx + partial `UNIQUE INDEX ... WHERE status='pending'` (guarded migration, collapses existing dupes at boot) |
| R2-6 | **Webhook had no replay protection** — valid signature reusable forever within secret lifetime | Captured webhook replay; nonce-less forgery attempts | Mandatory `timestamp` (±300 s) + single-use server-side `nonce` set (bounded 10k) inside the signed body; strict `type(payment_id) is int`; amount re-checked against `PLAN_PRICES` allowlist; 64 KB body cap |
| R2-7 | **`/gateway/charge` had NO CSRF check at all** (round-1 miss — only register/login/upgrade were covered) | CSRF-forced charges | `csrf_ok("payment")` — shares the payment-flow action with `/upgrade` (checkout form is part of that flow) |
| R2-8 | **No security headers** | Clickjacking, MIME sniffing, referrer leaks | `after_request`: CSP (`default-src 'self'`, `frame-ancestors 'none'`, `form-action 'self'`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Permissions-Policy`, HSTS when request is secure or `FORCE_HSTS=1` |
| R2-9 | **Login username-enumeration timing** (hash check skipped for unknown users) | Account enumeration | Dummy `check_password_hash` always runs |
| R2-10 | **No input bounds** — username/password/payment_id unbounded; `payment_id` compared as raw string | DoS via huge passwords, type-confusion probes | username 1–64 chars no control chars; password ≤1024; `payment_id.isdigit()` / strict JSON int |
| R2-11 | **Session cookie flags unset; no lifetime** | Fixation/lifetime hardening gaps | `SESSION_COOKIE_HTTPONLY`, `SAMESITE=Lax`, `PERMANENT_SESSION_LIFETIME=1h`, `SESSION_COOKIE_SECURE` via `LAB_COOKIE_SECURE=1` (off by default — lab is plain HTTP); `MAX_CONTENT_LENGTH=256KB` |
| R2-12 | **DB connections had no busy timeout / FK pragma** | `database is locked` under the attacker's concurrent requests | `PRAGMA busy_timeout=10000`, `PRAGMA foreign_keys=ON`, `timeout=10` on connect |
| R2-13 | **500 error handler absent** (Flask default is generic but unhandled paths weren't audited) | Stack-trace/info-leak risk | Explicit `errorhandler(500)` → generic page + server-side log; 404 handler likewise |
| R2-14 | **`{{ body\|safe }}` interpolated DB values unescaped** (`plan`, `role` in status f-string) | Second-order XSS if a DB field is ever attacker-influenced | `markupsafe.escape()` on all DB-derived values inside `\|safe` bodies |

Not changed (deliberate): `/logout` stays GET (test suite + lab UX depend on
it; logout CSRF is low-impact). Username charset stays permissive (1–64) —
round-1 regression test requires SQLi payloads to be *stored literally*,
which is safe because every query is parameterized.

## Test results

```
$ cd /home/neilh/websec_lab/app && /home/neilh/venv/bin/python -m pytest tests/ -q
.......................................                                  [100%]
39 passed in 8.28s
```

- 18 round-1 tests: all still pass (one webhook test updated to include the
  now-mandatory `timestamp`+`nonce` fields — API contract change, not a
  weakening).
- 21 new tests in `tests/test_security_r2.py`:
  - headers present (200 + 404 responses)
  - login rate limit → 429 on 6th attempt; register per-username → 429;
    X-Forwarded-For rotation does NOT bypass the limiter
  - CSRF single-use replay → 403; cross-action token → 403; tampered token → 403
  - webhook: replayed nonce → 403; missing/stale/future timestamp → 403;
    missing nonce → 400; string payment_id → 400; unsigned → 403
  - **concurrency**: 8 simultaneous `/gateway/charge` on one payment →
    exactly one 200, seven 400, single `succeeded` row; 6 parallel webhook
    deliveries → exactly one `upgraded=true`
  - second `/upgrade` supersedes pending (one pending row; old sig → 400)
  - oversized username / empty password rejected; non-numeric payment_id → 400

## Live verification

- App restarted on hardened code (`/home/neilh/venv/bin/python app.py`,
  PID recorded at runtime; log `/tmp/app_r2.log`).
- End-to-end smoke: register → login → upgrade → mock-gateway charge →
  `/premium` returns `SECRET_RECIPE_42`; immediate recharge → 400.
- Response headers confirmed live (CSP, XFO, XCTO, Referrer-Policy,
  Permissions-Policy; SameSite=Lax + HttpOnly session cookie).

## Known residual notes

- `Server: Werkzeug/...` header is added by the dev server *below* the WSGI
  app layer and cannot be stripped via `after_request`; use a production
  WSGI server (gunicorn) to remove it.
- Rate limits are per-process in-memory — fine for the lab; use Redis in prod.
- HSTS is emitted only for secure requests / `FORCE_HSTS=1` (lab is HTTP).
- Webhook nonce set is in-memory; a restart clears it (timestamp window still
  applies). Persist to DB if stronger guarantees are needed.

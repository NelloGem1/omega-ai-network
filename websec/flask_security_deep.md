# Flask / Python Web Security Deep Dive

Python- and Flask-specific attack surface and defenses. Where possible each
topic pairs an attack against the lab app at `/home/neilh/websec_lab/app/app.py`
with the corresponding fix. General vuln classes (IDOR, CSRF, SSRF, etc.) live
in `advanced_web_vulns.md`; this file covers what is *specific* to Flask,
Werkzeug, Jinja2, sqlite3, Python serialization, and the WSGI stack.

---

## 1. Werkzeug debugger (`debug=True`)

### Why it is dangerous

`app.run(debug=True)` activates the Werkzeug interactive debugger: traceback
pages get a `/console` that evaluates arbitrary Python in the server process —
read the DB, `os.system`, read `app.secret_key`/env vars. The traceback page
alone leaks absolute paths, source lines, and **local variable values**
(passwords, SQL strings, session contents, package versions). `debug=True` only
affects the dev server — it is a "temporary" deploy that becomes permanent.

### The PIN

Since Werkzeug 0.11ish the `/console` endpoint is protected by a PIN that is
printed to the server's stdout. It is *not* a password — it is derived from
semi-public machine data:

- `probably_public_bits`: username, `flask.app`, `Flask`, path to `app.py`.
- `private_bits`: `uuid.getnode()` (MAC address as int), machine-id or
  `/proc/self/cgroup` contents (WSL/containers), etc.

Attack scenarios: with any file-read primitive (LFI, path traversal, SSRF
`file://`, backup leak) an attacker recomputes the PIN — tools like
`werkzeug-debug-console-bypass` automate it; in containers `machine-id` is
often shared/stable, making PINs predictable. The **`WERKZEUG_DEBUG_PIN=off`**
env var disables the PIN check entirely — check deployment envs. Repeated
wrong PINs lock the console until restart.

### Lab mapping

`app.py` ends with `app.run(host="127.0.0.1", port=5000, debug=True)`. Note
`127.0.0.1` binding mitigates *remote* access to `/console`, but the tracebacks
still render. Any localhost proxy, port-forward, or port-scan to 5000 exposes
it. Try: `GET /nonexistent` to force a traceback; if the console shows, try the
PIN flow or look for leaked machine bits.

### Defense

```python
# NEVER in production
if __name__ == "__main__":
    app.run(debug=False)          # or omit debug entirely

# Better: use a real WSGI server and control env explicitly
# gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

- Gate debug behind env: `app.run(debug=os.environ.get("FLASK_DEBUG") == "1")`.
- Do not expose Werkzeug's dev server beyond localhost.
- Ensure `WERKZEUG_DEBUG_PIN` is never set to `off` in prod.
- If the debugger must exist on a box you control, firewall `/console` or use
  an auth proxy in front.

---

## 2. Flask session attacks

Flask's default session is **client-side**: a signed (not encrypted) cookie via
itsdangerous `URLSafeTimedSerializer`. Format:

```
base64(payload_json).timestamp.signature
```

What is signed: the whole `payload.timestamp` string. What the client sees:
**everything** — the payload is only base64, not encrypted. So secrets must
never be stored in `session`; it is readable by the user and by anyone who sees
the cookie (proxy logs, XSS exfil, shoulder-surfing).

### Attacks

1. **Weak SECRET_KEY → forge anything.**
   Lab uses `app.secret_key = "dev-secret-change-me"` — trivially in wordlists.
   Attack:
   ```bash
   flask-unsign --decode --cookie 'eyJpc19wcmVtaXVtIjpmYWxzZX0...'
   flask-unsign --unsign --cookie '<cookie>' --wordlist rockyou.txt --no-literal-eval
   flask-unsign --sign --cookie "{'username':'demo','is_premium':True,'role':'premium'}" \
       --secret 'dev-secret-change-me'
   ```
   Replace the cookie → premium flag forged. **This is the single most common
   real-world Flask vuln.**

2. **Over-trusting session contents.** Even with a strong key, the lab stores
   `is_premium` and `role` in the session and `/premium` trusts
   `session.get("is_premium")` without re-checking the DB. If the key leaks
   *or* a lower-privileged path can influence session values (e.g., session is
   populated from user-controlled data), authorization is bypassed. Defense:
   store only `user_id`/`username`; re-fetch role from DB per request
   (or cache with short TTL).

3. **Session fixation.** Flask's default cookie session makes classic fixation
   awkward (no server-side session ID to fix), but if `flask-session` or
   server-side sessions are used, the session ID must be **regenerated at
   login** (`session_interface.regenerate()`). Otherwise an attacker who plants
   a session ID keeps access after the victim logs in. Also: `session.clear()`
   on login/logout prevents key-collision carryover.

4. **Cookie tampering without the key.** You *cannot* modify payload fields
   without a valid HMAC — attempts produce `BadSignature` and Flask silently
   starts a fresh empty session. Attackers therefore target key recovery, not
   bit-flipping. However: **downgrade/strip the cookie** to get an anonymous
   session (sometimes useful for bypassing "logged-in required" logic that only
   checks session presence oddly). Also note the timestamp is signed, so
   `PERMANENT_SESSION_LIFETIME` bounds replay of stolen cookies.

5. **Key rotation / fallback mistakes.** Flask 3.1 adds
   `SECRET_KEY_FALLBACKS`; an old weak key left in fallbacks keeps old forged
   cookies valid. Remove retired keys.

6. **Secret key in source control / logs / error pages.** The debugger
   tracebacks, `git` history, `.env` leaks, and hardcoded defaults
   (`"dev-secret-change-me"`, `"secret"`, `"changeme"`) are all attack paths.
   Generate: `python -c 'import secrets; print(secrets.token_hex())'`.

### Defense

```python
import secrets, os
app.secret_key = os.environ["FLASK_SECRET_KEY"]  # or secrets.token_hex(32)
# never commit; rotate via SECRET_KEY_FALLBACKS during transition only

app.config.update(
    SESSION_COOKIE_SECURE=True,        # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,      # no JS access (mitigates XSS theft)
    SESSION_COOKIE_SAMESITE="Lax",     # CSRF mitigation for top-level nav
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)
```

- Store only an opaque identifier in session; look up privileges server-side.
- For high-security apps use server-side sessions (`flask-session` with Redis)
  so revocation is possible — client-side cookies cannot be revoked.

---

## 3. SQLite-specific issues (vs MySQL/Postgres)

The lab uses `sqlite3` directly with `%`-format strings — the injection itself
is generic, but SQLite changes the exploitation playbook:

### Differences that matter for attackers

- **Stacked queries:** `conn.execute()` runs one statement;
  `executescript()` runs many but is rarely used on user input. UNION-based and
  boolean/time-based blind injection work identically (`' OR 1=1--`,
  `UNION SELECT`).
- **No `SLEEP()`/`BENCHMARK()`.** No sleep function exists; time-based blind
  uses heavy expressions instead:
  `' OR (SELECT CASE WHEN substr(password,1,1)='a' THEN randomblob(100000000) ELSE 0 END)`
  — or skip timing entirely and use `LIKE`/`GLOB` probing (fast, reliable).
- **`ATTACH DATABASE`:** `'; ATTACH DATABASE '/tmp/evil.db' AS evil;--` needs a
  multi-statement path (`executescript`, or injection inside an `INSERT`
  context). Where reachable it creates/writes DB files wherever the process
  can write. `load_extension` is off by default in Python's sqlite3; if app
  code calls `enable_load_extension(True)`, `load_extension('/x.so')` = native
  code exec.
- **No authorizer exposed:** Python's sqlite3 doesn't expose
  `sqlite3_set_authorizer` — parameterized queries are the *only* gate.
- **`LIKE` / `GLOB`:** LIKE is ASCII case-insensitive with `%`/`_` wildcards —
  `password LIKE 'a%'--` guesses char-by-char in boolean-blind. GLOB uses
  `*`/`?`, case-sensitive.
- **`sqlite_master`** replaces `information_schema`:
  `UNION SELECT name, sql FROM sqlite_master--` dumps the whole schema.
- **`PRAGMA`** statements usable in subqueries for fingerprinting
  (`PRAGMA user_version` as a boolean oracle; `PRAGMA database_list`).
- **Type affinity:** SQLite compares loosely — `'1' = 1` can be true; auth
  checks like `WHERE id = %s` behave differently than MySQL (`id=0` tricks).
- **Exfil channels:** `||`, `hex()`, `zeroblob()` work for payloads; there is
  no `INTO OUTFILE`. Exfil is via UNION result sets (or DNS/HTTP only if a
  loadable extension/network feature exists — usually not).

### Lab mapping

`/register` and `/login` build queries with `% (username, password)`. Classic
payloads:

```sql
-- login bypass
username: admin'--
username: ' OR '1'='1'--

-- register: inject role directly (the INSERT wraps values in quotes)
username: x', 'y', 'premium')--     -- tries to land in role column
password: anything
```

For the register INSERT the column list is fixed `(username, password, role)`
with `'free'` literal — inject through `username` to break out and add columns
or close early, e.g. `username = "a','b','premium')-- "` yields
`VALUES ('a','b','premium')-- ','free')`. Then the inserted user's role is
`premium` → login → session `is_premium=True`.

### Defense

```python
# sqlite3 — always parameterized
conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
conn.executemany("INSERT INTO payments (user_id, amount_cents) VALUES (?,?)", rows)

# SQLAlchemy — ORM or Core with bound params; never .format()/.f-string into text()
stmt = text("SELECT * FROM users WHERE username = :u AND password = :p")
db.execute(stmt, {"u": u, "p": p})
```

- Never use `%`, `.format()`, or f-strings to build SQL.
- `conn.row_factory` etc. don't affect injection; only parameter binding does.
- Keep `enable_load_extension` off (default); do not call `executescript` on
  any string containing user data.

---

## 4. Jinja2 SSTI (Server-Side Template Injection)

The lab uses `render_template_string(PAGE, body=body, ...)` and marks `body`
`|safe`. `PAGE` itself is a constant, so SSTI requires reaching the template
*source* — but `body` is HTML-escaped-unless-safe. Watch for:

- `render_template_string(user_input)` anywhere.
- `{{ user_input }}` inside a template — Jinja autoescapes `{{ }}` for HTML,
  **but does not stop SSTI** if the string is evaluated as template source.
- `Markup(...)`, `|safe`, `render_template_string`, `Template(user_input)`.

### Detection payloads (safe → escalating)

```jinja
{{7*7}}                    -> 49 confirms evaluation
{{7*'7'}}                  -> '7777777' confirms Jinja (Python would error/49)
{{config}}                 -> dumps Flask config incl. SECRET_KEY
{{self.__init__.__globals__}} -> reach Python objects
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{lipsum.__globals__.__builtins__.__import__('os').popen('id').read()}}
```

`config` alone often leaks `SECRET_KEY` → then forge sessions (§2) — SSTI and
session attacks chain together.

### Sandbox reality

Jinja2 sandboxes `{{ }}` expressions: no attribute starting with `_` *by
default*? Actually — modern Jinja's `SandboxedEnvironment` blocks unsafe
attributes; the **default** `Environment` used by `render_template_string`
is NOT the sandboxed one, but Flask templates do have `is_safe_attribute`
restrictions? Clarification: Flask uses a regular `Environment` with
`autoescape`; SSTI payloads above work because attribute access to dunder names
is blocked only in `SandboxedEnvironment`. In practice, `{{ ''.__class__... }}`
chains via `__class__.__mro__` are blocked? — They are **not** blocked in
Flask's default env; the classic `lipsum.__globals__` gadget works because
`lipsum` is a Jinja global function. Real-world Flask SSTI almost always goes
through `lipsum`, `cycler`, `joiner`, `namespace`, `url_for.__globals__`, or
`self`/`request` objects. Use `{{cycler.__init__.__globals__.os.popen('id').read()}}`.

- If `SandboxedEnvironment` IS used, known escapes exist via
  `|attr` filter tricks and gadget chains (search "Jinja2 sandbox escape"
  PayloadsAllTheThings); assume sandboxed SSTI is still dangerous.

### Why `|safe` / `Markup()` are dangerous

- `{{ body|safe }}` tells Jinja "this string is already safe HTML" → raw HTML
  injection (XSS) for anything user-controlled placed in `body`.
- In the lab, `msg = f"Error: {e}"` from sqlite exceptions is inserted into the
  page **without escaping** because of `|safe` → reflected XSS via the error
  message (e.g., trigger an exception containing `<script>` — sqlite error
  messages echo input). Even without SSTI, `|safe` on dynamic content = XSS.
- `Markup()` is the programmatic equivalent; wrapping user input in it is the
  same bug.

### Defense

```python
# Don't render user data as template source. Render a template file:
return render_template("status.html", user=u, plan=plan)
# In templates: {{ plan }} autoescapes; only |safe developer-authored strings.

# If you must build HTML strings, escape explicitly:
from markupsafe import escape
msg = f"<p>Error: {escape(e)}</p>"
# Better: return JSON errors for API routes; flash() messages for forms.
```

- Audit every `render_template_string`, `Template(`, `Markup(`, `|safe`.
- CSP headers (Flask-Talisman) reduce XSS impact even if escaping fails.

---

## 5. Python deserialization

- **`pickle.loads(user_bytes)` = remote code execution.** Pickle is not a data
  format; it executes `__reduce__`/`__setstate__` on load. Any endpoint that
  unpickles request bodies, cookies, cache values, or uploaded files is a
  full RCE primitive. Payloads via `pickle` `__reduce__` → `os.system`,
  `subprocess`, reverse shells. Never unpickle untrusted data; use JSON,
  MessagePack, or protobuf.
- **`yaml.load()`** — PyYAML's default `Loader` (pre-6.0 default `Loader`,
  and `yaml.load` without Loader arg in old versions) constructs arbitrary
  Python objects → RCE via `!!python/object/apply:os.system`. Use
  `yaml.safe_load()` always; in PyYAML ≥5.1 `yaml.load` requires an explicit
  Loader and `FullLoader` still allows some object construction — `safe_load`
  is the only safe choice.
- **`marshal.loads`** — similar to pickle for code objects; can load crafted
  code objects. Treat as dangerous with untrusted input (it's intended for
  `.pyc` internals).
- **`shelve`** — built on `pickle`/`dbm`; `shelve.open(path)` on an
  attacker-writable file = same pickle RCE. Also `dbm` files are not safe
  across untrusted writers.
- **`json.loads`** is safe for data, but watch for **prototype-pollution-style**
  key confusion in Python? Less relevant; JSON itself doesn't execute.
- **`eval`/`exec`/`compile`** on user input — sometimes found in "expression"
  endpoints (calculators, filters). Same RCE class as pickle.
- **`ast.literal_eval`** is the safe parser for literal structures — use it
  instead of `eval`.

Flask-relevant sinks: session backends that pickle (old `flask-session` file
backend), caching (pickle-based cache backends), Celery/RQ task payloads if
exposed, and any `request.get_json()` → stored → later `pickle.loads`.

Defense: JSON-only at trust boundaries; if binary needed, sign it (itsdangerous)
and still prefer structured formats.

---

## 6. Flask file upload / file serving

- **`send_file(path)` / `send_from_directory` path traversal.** If a route does
  `send_file("/uploads/" + request.args.get("file"))` or
  `send_from_directory(UPLOAD, filename)` with `..` segments, attacker reads
  arbitrary files (`/etc/passwd`, `app.py`, `lab.db`, `/proc/self/environ` →
  SECRET_KEY). `send_from_directory` sanitizes `..`? It uses `safe_join`
  semantics in modern Werkzeug — **verify the version**; older versions and
  manual concatenation are vulnerable. Attack:
  `GET /download?file=../../app.py` or `....//` bypasses, `%2e%2e%2f` encoding.
- **`send_file` with user-controlled absolute path** — same result; never pass
  raw user input.
- **Filename sanitization:** uploaded filenames (`file.filename`) are
  attacker-controlled: `../../etc/cron.d/x`, `..\\..\\win.ini` on Windows,
  null bytes `%00`, unicode tricks. Always `werkzeug.utils.secure_filename()`
  or generate your own name (`uuid4().hex`) and store the original name in DB.
- **Content-type trust:** don't trust `file.content_type` or extension for
  "is this an image" — check magic bytes, or better, re-encode/validate with
  Pillow. Serving user uploads with the original content-type enables stored
  XSS (`<script>` as `text/html`) and SVG-based XSS (`image/svg+xml` with
  script). Serve from a separate domain or force `Content-Disposition:
  attachment` / `X-Content-Type-Options: nosniff`.
- **Size limits:** Flask doesn't limit upload size by default —
  `MAX_CONTENT_LENGTH = 16 * 1024 * 1024`; also configure web server limits.
- **Zip/tar slip** if extracting archives (`zipfile.extractall` path traversal
  via `../` member names).

Lab note: the lab has no upload route — this is general Flask coverage.

---

## 7. Flask auth patterns gone wrong

- **Timing attacks on login.** String `==` on passwords (or hashes) leaks
  prefix length via response time. Use `hmac.compare_digest` /
  `secrets.compare_digest`, or better `werkzeug.security.check_password_hash`
  (which is constant-time for its formats). The lab compares via SQL `WHERE
  password='...'` — injection aside, timing on nonexistent users vs wrong
  password can also enumerate users if the query path differs (it doesn't
  here, but `SELECT` then compare in Python would).
- **User enumeration via error messages.** `/register` says "Username already
  taken" — confirms valid usernames → enumerate for credential stuffing.
  Login "Invalid credentials" is fine (generic); register should say "could
  not register, try another" or use email verification. Also verbose `Error:
  {e}` leaks whether username exists via UNIQUE constraint vs other errors.
- **Plaintext passwords** (lab stores raw). Use `werkzeug.security.generate_
  password_hash` / `check_password_hash` (scrypt/pbkdf2). On DB leak, plaintext
  = immediate credential reuse everywhere.
- **Remember-me cookies:** Flask's `remember_token` via Flask-Login stores a
  hash in DB; mistakes: storing the raw token, tokens that don't expire or
  rotate on password change, tokens in URL. Prefer short-lived JWT with `exp`
  or server-side token table with revocation.
- **JWT in Flask mistakes:**
  - `alg: none` accepted → forge any token. Pin the algorithm
    (`algorithms=["HS256"]`) and reject `none`.
  - **Algorithm confusion** RS256→HS256: if server uses RSA public key as HMAC
    secret → forge. Use asymmetric algs correctly or symmetric only.
  - Missing/ignored `exp`, `iat`, `nbf` → tokens never expire.
  - `kid` header injection → path traversal / SQLi in key lookup.
  - Verifying signature but not `aud`/`iss` → token reuse across services.
  - Storing roles/entitlements *only* in JWT without re-check → same class as
    session-flag trust (§2).
- **AuthZ vs AuthN:** the lab's `/premium` checks `session["is_premium"]` —
  that's authentication-adjacent state, not authorization. Always re-derive
  entitlement from the DB (or signed server-side record) at the resource.

---

## 8. SQLite subscription-state attacks (race conditions / TOCTOU)

- **TOCTOU between check and update:** pattern `SELECT status ... ; if active:
  UPDATE` is racy. Two concurrent requests can both pass the check. Fix:
  conditional UPDATE — `UPDATE subscriptions SET plan='premium' WHERE user_id=?
  AND status='active'` then check `cursor.rowcount`; or use a transaction with
  `BEGIN IMMEDIATE`.
- **sqlite3 default isolation:** Python's `sqlite3` opens transactions lazily —
  `conn.execute("UPDATE ...")` begins a transaction implicitly only for
  DML? Actually: `isolation_level=""` (default legacy) auto-begins before
  INSERT/UPDATE/DELETE and requires `commit()`. **Concurrent writers get
  `database is locked`** (SQLITE_BUSY) — which the lab turns into verbose 500
  errors. Without `conn.execute("PRAGMA busy_timeout=5000")` or WAL mode,
  concurrent upgrade requests may partially fail or serialize weirdly.
- **Missing transactions:** the lab's `/upgrade` does three writes
  (users.role, subscriptions, payments INSERT) then `commit()`. If the process
  dies mid-way or an exception occurs after `conn.execute` but before
  `commit`, state is inconsistent — e.g., role=premium without payment record,
  or payment without subscription. Wrap in `with conn:` (transaction context)
  or explicit `BEGIN`/`COMMIT`/`ROLLBACK`.
- **Race on payment:** attacker fires N parallel `POST /upgrade
  payment_success=1` — each inserts a payment row; or with a real gateway,
  double-submit/callback replay. Idempotency keys needed for real payments.
- **`lastrowid` reliance:** register uses `cur.lastrowid` — fine single-threaded,
  but think about it if batching.
- **WAL vs rollback journal:** default journal mode serializes writers; enable
  `PRAGMA journal_mode=WAL` for read concurrency but it doesn't fix logic races.
- **Check-then-act on session flags:** `/premium` reads `session` (client
  cookie) — no server state at all; combined with §2 key-cracking it's a pure
  client-side authorization decision.

Defense patterns:

```python
conn = get_db()
try:
    with conn:                       # commits on success, rolls back on exc
        cur = conn.execute(
            "UPDATE subscriptions SET plan='premium', status='active' "
            "WHERE user_id=? AND plan!='premium'", (uid,))
        if cur.rowcount == 0:
            raise AlreadyPremium()
        conn.execute("UPDATE users SET role='premium' WHERE id=?", (uid,))
        conn.execute("INSERT INTO payments ...", (...))
except sqlite3.OperationalError as e:
    if "locked" in str(e): ...       # retry with backoff / busy_timeout
```

Set `PRAGMA busy_timeout`, use `with conn:` everywhere, and make state changes
single conditional statements where possible.

---

## 9. Flask-CORS misconfigurations

Flask-CORS (`flask_cors.CORS(app, ...)`) mistakes:

- **Reflecting Origin:** `CORS(app, origins="*")` is fine for public GET APIs
  *without credentials*. The killer combo:
  ```python
  CORS(app, origins=request.headers.get("Origin"))   # reflects anything
  # or supports_credentials=True with origins="*" or reflected origin
  ```
  Browser sends `Origin: https://evil.com` → response `Access-Control-Allow-
  Origin: https://evil.com` + `Access-Control-Allow-Credentials: true` →
  evil.com JS reads authenticated responses (session cookie included).
- **`supports_credentials=True` + wildcard** — spec forbids `*` with
  credentials; Flask-CORS handles it by reflecting origin, which is exactly
  the vuln. Only combine credentials with an explicit allowlist.
- **Over-broad regex origins:** `origins=[r"https://.*\.example\.com"]` may
  match `https://evil-example.com`? Regex `.*` can overmatch
  (`https://example.com.evil.com` if pattern is loose). Anchor patterns:
  `r"https://[a-z0-9-]+\.example\.com"`.
- **`allow_headers="*"`, `expose_headers`** — minor; `methods="*"` fine but
  review.
- **CORS doesn't stop CSRF** — it controls reading responses; state-changing
  requests still possible cross-origin (they just can't read the response).
  Need CSRF tokens for that (Flask-WTF).
- **Subdomain trust:** allowing `*.example.com` trusts every subdomain —
  including user-content subdomains (XSS there → credentialed CORS read).

Defense:

```python
CORS(app, origins=["https://app.example.com"],
     supports_credentials=True,
     methods=["GET","POST"],
     allow_headers=["Content-Type","Authorization"])
# never reflect request Origin when credentials are allowed
```

Audit: check `Access-Control-Allow-Origin` reflects arbitrary origins in
responses; test with `Origin: https://evil.com` + credentials.

---

## 10. Rate limiting gaps

- **Flask-Limiter bypass via `X-Forwarded-For`:** default key is
  `get_remote_addr()` → the *proxy's* IP if behind nginx → all users share one
  bucket (DoS-ish) or, if `ProxyFix` is applied naively, attacker sets
  `X-Forwarded-For: <random>` per request → **each request a new bucket →
  unlimited brute force**. Flask-Limiter docs: use
  `key_func=get_remote_address` and configure ProxyFix to trust only known
  proxy hops (`x_for=1` or trusted proxy list), or key on
  `request.remote_addr` after correct ProxyFix.
- **Endpoint coverage:** limits applied per-route decorator only cover those
  routes — login brute-force protection doesn't cover `/register`,
  `/upgrade`, password-reset, or 2FA endpoints. Apply a global
  `default_limits` plus stricter auth-endpoint limits:
  ```python
  limiter = Limiter(key_func=get_remote_address,
                    app=app, default_limits=["200 per day","50 per hour"])
  @limiter.limit("5 per minute")
  @app.route("/login")
  ```
- **Storage backend:** in-memory limiter resets on restart and doesn't share
  across workers — use Redis (`storage_uri="redis://..."`).
- **Other bypasses:** case/encoding variants hitting different route rules,
  HTTP method switching (POST vs GET on same logic), header-based key funcs
  trusting client headers, race conditions on the limiter itself (fixed-window
  allows 2x burst at boundary — acceptable for most, use moving window for
  auth endpoints).
- **Lab relevance:** `/login` has no rate limit → online brute force of
  `demo:demo123`-style creds; combined with plaintext passwords (§7) and no
  lockout, credential stuffing is trivial.

Defense checklist: Redis-backed limiter, limits on every auth/payment/
sensitive endpoint, correct ProxyFix trust, alert on limit hits, CAPTCHA or
exponential backoff after N failures (Flask-Limiter supports
`deduct_when`/`swallow_errors` and there's `flask-limiter` + `slowapi`;
for lockouts consider `flask-login` failed-attempt counters or
`django-axes`-style pattern reimplemented).

---

## 11. Defense checklist for Flask (concrete config)

```python
import os, secrets
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# --- secrets & sessions ---
app.secret_key = os.environ["FLASK_SECRET_KEY"]   # secrets.token_hex(32); never hardcode
app.config.update(
    SESSION_COOKIE_SECURE=True,          # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,        # JS can't read it (XSS mitigation)
    SESSION_COOKIE_SAMESITE="Lax",       # or "Strict" for high-security
    SESSION_COOKIE_NAME="__Host-session",# if no Domain set (see below)
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024, # upload cap
)
# SECRET_KEY_FALLBACKS only during rotation; remove old keys after.

# --- proxy handling (only if behind a trusted proxy) ---
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1,
                        x_prefix=1)
# x_for=1 trusts exactly ONE proxy hop. Never x_for=None/all behind
# untrusted clients or XFF becomes attacker-controlled -> rate-limit bypass.

# --- CSRF ---
# flask-wtf: WTF_CSRF_ENABLED=True (default), WTF_CSRF_TIME_LIMIT=None for
# long-lived forms; validate via FlaskForm or csrf.protect() on blueprints.

# --- security headers (Flask-Talisman) ---
from flask_talisman import Talisman
Talisman(app,
         force_https=True,                 # redirect http->https
         strict_transport_security=True,
         content_security_policy={
             "default-src": "'self'",
             "script-src": "'self'",
             "style-src": "'self' 'unsafe-inline'",
             "img-src": "'self' data:",
         },
         frame_options="DENY",)
# For APIs serving JSON set content_security_policy=None and rely on
# X-Content-Type-Options: nosniff (Talisman adds it).

# --- production server ---
# gunicorn -k gthread -w 4 -b 127.0.0.1:8000 wsgi:app   (behind nginx)
# NEVER app.run(debug=True)
```

Parameterized queries:

```python
import sqlite3
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

# sqlite3 style
conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
conn.execute("UPDATE subscriptions SET plan=? WHERE user_id=? AND status=?",
             ("premium", uid, "active"))

# SQLAlchemy style
from sqlalchemy import text
stmt = text("SELECT * FROM users WHERE username = :u")
row = db.execute(stmt, {"u": username}).fetchone()
# NEVER: text(f"... {username}") or text("..." + username)
```

AuthZ decorator pattern:

```python
from functools import wraps
from flask import session, abort

def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper

def premium_required(f):
    @wraps(f)
    @login_required
    def wrapper(*a, **kw):
        # Re-check entitlement server-side — never trust session flags alone
        row = get_db().execute(
            "SELECT role FROM users WHERE id=?", (session["user_id"],)).fetchone()
        if not row or row["role"] != "premium":
            abort(403)
        return f(*a, **kw)
    return wrapper

@app.route("/premium")
@premium_required
def premium(): ...
```

Passwords:

```python
from werkzeug.security import generate_password_hash, check_password_hash
pw_hash = generate_password_hash(password)          # scrypt by default
ok = check_password_hash(stored_hash, password)     # constant-time compare
```

Rate limiting:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address, app=app,
                  default_limits=["200 per day", "50 per hour"],
                  storage_uri="redis://localhost:6379")
@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login(): ...
```

File uploads:

```python
from werkzeug.utils import secure_filename
import uuid
f = request.files["file"]
name = secure_filename(f.filename or "") or uuid.uuid4().hex
# or fully ignore client name:
name = uuid.uuid4().hex + os.path.splitext(secure_filename(f.filename))[1]
f.save(os.path.join(UPLOAD_DIR, name))
# serve via send_from_directory(UPLOAD_DIR, name) — never raw paths
```

---

## 12. Practice mapping (PortSwigger / PayloadsAllTheThings)

| Topic | PortSwigger Academy | PayloadsAllTheThings |
|---|---|---|
| SQL injection (SQLite flavor) | SQL injection all labs; "UNION attacks" | `SQL Injection/SQLite Injection.md` |
| Blind SQLi (no SLEEP) | Blind SQL injection labs | SQLite section — LIKE/GLOB, randomblob timing |
| Session cookie cracking | — (not covered; it's tooling) | — use flask-unsign + rockyou |
| SSTI | Server-side template injection labs | `Server Side Template Injection/` (Jinja2 section) |
| Insecure deserialization | Insecure deserialization labs (Java/PHP focus; concepts transfer) | `Insecure Deserialization/` + Python pickle notes |
| Path traversal / LFI | Path traversal labs | `File Inclusion/` + `Directory Traversal/` |
| File upload | File upload labs | `File Upload/` |
| Auth: brute force, enumeration | Authentication labs | `Brute Force Rate Limit/`, `Username Enumeration/` |
| JWT attacks | JWT labs (alg confusion, none, kid) | `JSON Web Token/` |
| CORS | CORS lab ("Exploiting CORS misconfigurations") | `CORS/` |
| CSRF (no token in lab) | CSRF labs | `CSRF Injection/` |
| XSS via `\|safe`/error reflection | XSS labs (reflected) | `XSS Injection/` |
| Rate limit / brute force | — | `Rate Limit Bypass/` |
| Werkzeug debugger | — (CTF-style; see HackTricks Werkzeug page, THM "Plant Photographer", "Werkzeug" rooms) | — |

Suggested lab order against `app.py`:

1. `/login` SQLi → auth bypass (PortSwigger SQLi basics).
2. `/register` SQLi → insert `role='premium'` row.
3. Decode `session` cookie → `flask-unsign --unsign` with rockyou on
   `dev-secret-change-me` → `--sign` forged `is_premium` cookie → `/premium`.
4. `debug=True` traceback pages → info leak; check `/console` reachability.
5. `/upgrade` `payment_success=1` direct POST (payment bypass — see
   `payment_bypass.md`).
6. Fix everything per §11, then re-test.

---

## Sources

- Flask docs — Configuration Handling / Builtin values:
  https://flask.palletsprojects.com/en/stable/config/
- Flask docs — Security Considerations:
  https://flask.palletsprojects.com/en/stable/web-security/
- Flask docs — API (`secret_key`, session interfaces):
  https://flask.palletsprojects.com/en/stable/api/
- Flask source — `src/flask/sessions.py` (SecureCookieSessionInterface,
  SECRET_KEY_FALLBACKS): https://github.com/pallets/flask/blob/main/src/flask/sessions.py
- Werkzeug docs — Debugging Applications (PIN, WERKZEUG_DEBUG_PIN):
  https://werkzeug.palletsprojects.com/en/stable/debug/
- Werkzeug source — `src/werkzeug/debug/__init__.py` (PIN derivation,
  get_machine_id):
  https://github.com/pallets/werkzeug/blob/main/src/werkzeug/debug/__init__.py
- HackTricks — Werkzeug debugger / PIN bypass:
  https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/werkzeug.html
- HackTricks — Flask (sessions, SSTI):
  https://desecurity.github.io/hacktricks/network-services-pentesting/pentesting-web/flask.html
- Paradoxis — Flask-Unsign:
  https://github.com/paradoxis/flask-unsign
- Flask-Session docs — Security / session fixation:
  https://flask-session.readthedocs.io/en/latest/security.html
- DigiNinja — Cracked Flask lab (session cookie tampering walkthrough):
  https://digi.ninja/blog/cracked_flask
- PortSwigger Web Security Academy:
  https://portswigger.net/web-security
- PayloadsAllTheThings:
  https://github.com/swisskyrepo/PayloadsAllTheThings
- Python sqlite3 docs (transactions, isolation_level, execute vs
  executescript): https://docs.python.org/3/library/sqlite3.html
- PyYAML docs — `yaml.safe_load` vs `load`:
  https://pyyaml.org/wiki/PyYAMLDocumentation

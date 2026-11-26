# FINDING: CORS arbitrary-origin reflection + credentials on internal-api.monzo.com
Date: 2026-11-26 | Researcher: nellogem | Program: Monzo Public BBP (Intigriti)
Severity estimate: Medium-High (impact pending auth-mechanism confirmation)
Scope: internal-api.monzo.com = Tier 1 (*.monzo.com)

## Evidence (inline, per Monzo rules — no attachments allowed)

OPTIONS https://internal-api.monzo.com/accounts
  Origin: https://evil.example
  Access-Control-Request-Method: GET
  Access-Control-Request-Headers: authorization,cookie,x-requested-with

Response 200:
  access-control-allow-origin: https://evil.example   <-- REFLECTED arbitrary origin
  access-control-allow-credentials: true
  access-control-allow-headers: authorization,cookie,x-requested-with  <-- reflects requested headers incl cookie
  access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT

GET https://internal-api.monzo.com/accounts
  -> 401 {"code":"unauthorized.auth_required"} (auth required, endpoint real)

## Live endpoint map (internal-api.monzo.com)
  /accounts            401 auth_required
  /accounts/current    404 no_handler (routing oracle: distinguishes handler vs no-handler)
  /transactions        400 missing_param account_id -> 401 with param
  /transactions/export 401 auth_required
  /feed                400 missing_param account_id -> 401 with param
  /pots                401 auth_required
  /balance             400 missing_param account_id
  /                     200 {"name":"Monzo API"}
  api.monzo.com        same gateway software, identical behavior

## Impact hypothesis
If Monzo web session auth is cookie-based (.monzo.com domain cookies,
SameSite=None), any malicious site can fetch internal-api.monzo.com
cross-origin WITH credentials and read account/transaction data.
If auth is Authorization-header-only, impact is limited -> likely
informative/low. NEEDS: one authenticated session to confirm
whether cookie auth is accepted (no Set-Cookie observed on 401s).

## Blocker
Creating a Monzo account from Philippines likely impossible
(UK residency required). Options: ask Intigriti/Monzo for test
account, or report as misconfiguration with hypothesis.

## UPDATE 2026-11-26 (hunt session 2)

### internal-api endpoint map (all auth-gated, no bypass found)
- /ping/whoami → 200 {"authenticated":false,"client_ip":"..."} — minor info leak
- /accounts /pots /card/freeze /accounts/main-account /transactions/export → 401
- /transactions /feed /balance → 400 missing account_id → 401 with param
- /minimal-banking/{profile,is-verified,secure-account/cards,sessions,status} → 401
- /user-images/profile_picture/user_<uuid> → NO AUTH, returns 404 not_found for
  random UUIDs. Avatar endpoint keyed by user_<uuid>; unguessable IDs → likely
  public-by-design, LOW value unless user_ids leak elsewhere.
- Auth = Bearer header only (JS: authorization: Bearer <token>) → CORS cookie
  impact hypothesis WEAKENS; token theft still possible via XSS+reflection.

### Auth bypass attempts — ALL FAILED (auth solid)
path tricks (case, trailing, ;, %, //), method override, XFF/X-Original-URL/
X-Rewrite-URL/X-User-Id header spoof, Bearer null/empty → all 401/400 correctly.

### OAuth surface (auth.monzo.com → api.monzo.com/login/*)
- OIDC discovery public: issuer auth.monzo.com, ES256, pairwise subs
- client_id: oauth2client_00009XXTN0biZ3vgvysb21 (web app)
- redirect_uri registered: https://web.monzo.com/callback
- authorize endpoint does NOT validate redirect_uri upfront (deferred to
  post-login) — evil redirect URIs load login page fine. UNTESTABLE without
  account; likely validated at code exchange.
- static assets: static-assets.monzo.com

### prod-ffs.io
- web.prod.prod-ffs.io = Next.js 'minimal-banking' web app (Monzo web banking)
- tools.* / payments.e.* hosts = connection timeout (IP allowlist, expected)
- JS leaks: apiPath=https://internal-api.monzo.com/, authEndpoint, gitCommit
- Deep links: monzo:// / monzostage:// schemes

### Verdict
CORS reflection remains the best finding (reportable misconfig, Medium-ish).
No unauthenticated data exposure found. Auth layer is well-built.
BLOCKER: all impactful testing needs a Monzo account (UK residency).

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

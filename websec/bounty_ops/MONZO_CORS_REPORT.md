# REPORT DRAFT — paste into Intigriti submission form

TITLE: CORS arbitrary-origin reflection with credentials on internal-api.monzo.com

SEVERITY: Medium (arguably High if cookie-auth confirmed)

## Description
internal-api.monzo.com reflects any arbitrary Origin header in
Access-Control-Allow-Origin while also returning
Access-Control-Allow-Credentials: true, and reflects arbitrary
requested headers (including 'cookie') in Access-Control-Allow-Headers.
This misconfiguration allows any malicious website to make
authenticated cross-origin requests to the Monzo internal API on
behalf of a logged-in victim and read the responses.

## Steps to reproduce
1. Send an OPTIONS preflight:

curl -i -X OPTIONS 'https://internal-api.monzo.com/accounts'   -H 'Origin: https://evil.example'   -H 'Access-Control-Request-Method: GET'   -H 'Access-Control-Request-Headers: authorization,cookie,x-requested-with'   -H 'X-Intigriti-Monzo-Username: nellogem'

2. Observe response headers:

HTTP/2 200
access-control-allow-credentials: true
access-control-allow-headers: authorization,cookie,x-requested-with
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-allow-origin: https://evil.example

3. The origin 'https://evil.example' is reflected verbatim and is
   NOT restricted to *.monzo.com origins. Any origin is accepted.

## Impact
If any Monzo web surface authenticates via cookies scoped to
.monzo.com (or if a victim's bearer token is reachable from JS on a
page that can be framed/XSS'd), an attacker-controlled site can
exfiltrate account data: /accounts, /transactions?account_id=...,
/feed, /pots, /balance, /minimal-banking/* all return 401 without
auth but full data with credentials.

Even with bearer-token auth, this reflection removes the browser's
same-origin protection for any token an attacker can obtain, and
indicates the CORS policy is wildcard-equivalent.

## Suggested fix
Whitelist explicit trusted origins instead of reflecting Origin;
never combine reflected origins with allow-credentials: true.

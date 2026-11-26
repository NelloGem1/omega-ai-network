# Kruidvat (AS Watson / Intigriti) — recon notes 2026-11-26
Account: neil.hkrmzn@gmail.com (test acct, fake NL address)
Stack: SAP Hybris/Spartacus + Angular, BFF at api.kruidvat.nl/api/v2/kvn-spa/
Auth: bearer token in localStorage['spartacus⚿⚿auth'] + cookies
Rules: UA must contain *intigriti*, header X-Intigriti-Username, ≤5 req/s

## Endpoint map (authenticated, via browser sniffer — 87 calls)
users/current (+ /carts /consenttemplates /agreements)
users/current/carts/{numericId}/deliverymodes
users/{uuid-or-email} → own profile only (403 others)
wishlist[?fields=WISHLIST_PAGE] + /wishlist/{code} (owner-only enforced)
products/{id}, products?codes=, search, cms/*, redirects/*, breadcrumbs,
forms/{newsletterForm,changeEmailForm,changePasswordForm,
      personalInformationForm,physicalLoyaltyMyAccountEnrollmentForm},
translations/*, authorizationserver/oauth/token

## Test results — ALL SECURE
- GET IDOR (users/wishlist/carts adjacent IDs): blocked, ownership enforced
- Cart codes scoped under /users/current — no cross-user access
- PUT /users/current: proper validation (firstName required)
- POST: 405; DELETE /users/current: 200 (self-delete, session killed)
- ?fields= escalation: requires full auth
- Akamai blocks datacenter IPs — browser-only testing

## Verdict
Custom BFF with consistent ownership checks. No vuln found in ~40 probes.
Account deleted mid-test by our own DELETE probe (re-registered).

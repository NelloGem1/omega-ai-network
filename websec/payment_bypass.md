# Payment and Subscription Bypass Vulnerabilities

**Purpose:** defensive research for a self-owned Flask application. Reproduce these tests only against your own app, local environment, or explicitly authorized target.
**Core rule:** the browser, JavaScript, hidden fields, URL parameters, JWT claims, redirect query strings, API bodies, and webhook payloads are attacker-controlled input. Subscription state must be decided server-side from authenticated identity, database state, verified gateway events, and policy.
---

## 1. Client-side payment verification
### Root cause
The app asks the client whether payment succeeded, or trusts client-editable values such as `price`, `plan`, `total`, `paid`, `user_type`, `quantity`, or `payment_status`. JavaScript gates are cosmetic if the API behind them does not enforce entitlement.
### Exploit examples
Tamper checkout input:
```http
POST /api/checkout HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"plan_id":"pro","price":0.00}
```
If the backend charges `price` from the request, the user pays nothing. Response tampering is also common: intercept `{"paid":false,"plan":"pro"}` and forward `{"paid":true,"plan":"pro"}`. If `/premium/report` then succeeds, only the UI was protected:
```http
GET /premium/report HTTP/1.1
Cookie: session=alice
```
Hidden fields and success redirects behave the same way: `payment_status=success`, `plan=enterprise`, `isPremium=true`, or `userType=paid` must never grant access by themselves.
### Detection
- Intercept checkout and inspect every price, plan, quantity, coupon, currency, total, status, and ID field.
- Replay successful-looking requests without paying; remove cookies/localStorage flags and retry premium endpoints.
- Change HTTP methods and route variants (`GET`↔`POST`, `/api/v1`, `/api/internal`).
- Search JS bundles/source maps for `paid=true`, `isPremium`, `plan=pro`, mock URLs, or debug switches.
### Fix
- Keep plans/prices in a server-side catalog keyed by opaque `plan_id`; never accept amount from the client.
- Create the order/payment intent server-side, then verify gateway state before granting entitlement.
- Enforce subscription checks on every premium API/static resource; return minimal data and no internal plan fields.
---

## 2. IDOR / BOLA on subscriptions
### Root cause
Broken Object Level Authorization occurs when the user is authenticated but the server does not verify ownership of the object ID. OWASP API1:2023 specifically covers APIs that accept object IDs in paths, queries, headers, or bodies.
Subscription objects include `subscription_id`, `invoice_id`, `payment_id`, `order_id`, `customer_id`, `plan_id`, and `user_id`.
### Exploit examples
Alice owns `sub_1001`; Bob owns `sub_1002`.
```http
GET /api/subscriptions/1002 HTTP/1.1
Cookie: session=alice
```
If Bob's subscription is returned, object authorization failed. Writes are worse:
```http
POST /api/subscriptions/1002/cancel HTTP/1.1
Cookie: session=alice
```
```http
POST /api/subscriptions HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"user_id":1002,"plan":"enterprise","status":"active"}
```
Payment binding can also be abused:
```http
POST /api/payments/confirm HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"payment_id":"pay_999","subscription_id":"sub_1002"}
```
### Detection
- Create two test accounts and objects for each; swap numeric IDs, UUIDs, and payment IDs.
- Test IDs in path, query, body, headers, and GraphQL variables.
- Exercise read and write operations: view invoice, cancel, change plan, update payment method, download receipt.
- Look for sequential IDs and predictable public identifiers.
### Fix
- Derive `user_id`/tenant from the authenticated session, not request input.
- Enforce object-level authorization in a shared service/decorator on every object access.
- Use unguessable IDs as defense in depth, never as the authorization mechanism.
- Log denied object access and alert on enumeration.
---

## 3. Broken authorization and privilege escalation
### Root cause
Authentication is confused with authorization. Roles/plans may be trusted from JWTs, request fields, cookies, or hidden UI state. Admin endpoints may rely on obscurity. Mass assignment can let clients write `role`, `plan`, `is_admin`, `subscription_status`, or `balance`.
### Exploit examples
Decode a JWT and inspect claims:
```json
{"sub":"user_1001","role":"free","plan":"free"}
```
If weak secrets, `alg:none`, or key-type confusion are accepted, try a modified token claiming `"role":"admin"` or `"plan":"enterprise"`. OWASP JWT guidance warns against unsecured JWTs, key-type confusion, trusting token-header key material, issuer/audience confusion, and cross-token type confusion.
Mass assignment:
```http
PATCH /api/me HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"display_name":"Alice","role":"admin","plan":"enterprise","balance":99999}
```
Function-level authorization bypass (OWASP API5):
```http
POST /api/admin/grant-subscription HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"user_id":"user_1001","plan":"enterprise"}
```
### Detection
- Decode JWTs; inspect `alg`, `kid`, issuer, audience, expiry, and claims.
- In a test environment, try `alg:none`, weak-secret HS256, expired tokens, and tokens from another service.
- Send extra fields in registration/profile/order/subscription payloads.
- Guess admin/internal paths and try `GET`/`POST`/`PUT`/`DELETE` variants.
- Compare free, paid, and admin sessions on the same endpoints.
### Fix
- Keep authoritative role/plan state in the database or policy service; deny by default.
- Use allowlisted DTOs/serializers, never bind request JSON directly to ORM models.
- Pin JWT algorithms, validate issuer/audience/expiry, use strong rotating keys.
- Check function-level authorization consistently on every sensitive route.
---

## 4. Insecure API endpoints
### Root cause
Debug, test, admin, internal, legacy, or undocumented endpoints remain reachable. OWASP API9 warns that APIs expose more endpoints than traditional web apps and that stale/debug endpoints are common; API6 covers sensitive business flows exposed without abuse protection.
### Exploit examples
```http
GET /api/premium/content/42 HTTP/1.1
```
```http
POST /debug/grant-premium HTTP/1.1
Content-Type: application/json
{"user_id":"user_1001","plan":"enterprise"}
```
GraphQL introspection:
```http
POST /graphql HTTP/1.1
Content-Type: application/json
{"query":"{ __schema { queryType { fields { name } } mutationType { fields { name } } } }"}
```
A discovered mutation may allow:
```graphql
mutation { activateSubscription(userId:"user_1001", plan:"enterprise") { status } }
```
Probe paths such as `/api/test-payment`, `/api/mock-checkout`, `/swagger.json`, `/openapi.json`, `/actuator`, `/debug/vars`, `/metrics`, `/healthz`, `/api/v0/...`.
### Detection
- Enumerate routes from JS bundles, source maps, OpenAPI docs, errors, and common wordlists.
- Test every endpoint unauthenticated, as free user, and as admin.
- Run GraphQL introspection, field suggestions, batching, and persisted-query checks.
- Compare 401/403/404 responses for hidden functionality.
### Fix
- Maintain an API inventory; remove or protect debug/test/internal endpoints.
- Apply authn/authz middleware globally rather than per route ad hoc.
- Disable GraphQL introspection and verbose errors in production.
- Put internal APIs behind service auth/network isolation and monitor access.
---

## 5. Webhook and payment-gateway flaws
### Root cause
The app trusts a callback because it reached the webhook URL, or trusts fields in it without verifying authenticity. Dangerous patterns include missing signature checks, empty secrets, OR-logic checks, accepting truncated signatures, replaying old events, trusting redirect parameters, and letting payload values override authoritative gateway API values.
### Exploit examples
Forged Stripe-style event:
```http
POST /webhooks/stripe HTTP/1.1
Content-Type: application/json
{"id":"evt_forged","type":"checkout.session.completed","data":{"object":{"id":"cs_test_123","payment_status":"paid","client_reference_id":"user_1001","metadata":{"plan":"enterprise"}}}}
```
If signature verification is absent, this can activate premium. A redirect callback is not proof either:
```http
GET /payment/return?status=success&session_id=cs_test_123 HTTP/1.1
```
Replay a previously valid webhook body/signature pair; it should not grant credit twice.
### Detection
- Send forged webhook JSON with missing, empty, wrong, truncated, or altered signatures.
- Replay a real captured test webhook multiple times.
- Tamper one byte in the body and confirm rejection.
- Test missing secrets, alternate encodings, old timestamps, and wrong event/object IDs.
- Confirm the app ignores browser redirect `status=success` as payment proof.
### Fix
Stripe requires verifying the signature using the **raw request body**, `Stripe-Signature` header, and endpoint secret. Parsed/re-serialized JSON can break verification, so capture raw bytes first. Stripe also recommends duplicate-event guards.
```python
raw_body = request.get_data()
sig = request.headers.get("Stripe-Signature")
try:
    event = stripe.Webhook.construct_event(raw_body, sig, STRIPE_WEBHOOK_SECRET)
except Exception:
    return "bad signature", 400
if WebhookEvent.objects.filter(gateway_event_id=event["id"]).exists():
    return "", 200
```
Then validate event type, order/session ID, amount, currency, customer mapping, and optionally retrieve authoritative gateway state. Fail closed if secrets are missing; use constant-time comparison and timestamp tolerance where supported; deduplicate by event and payment IDs.
---

## 6. Business-logic flaws
### Root cause
The code performs arithmetic or workflow transitions without business rules. Prices, quantities, currencies, discounts, refunds, trials, and coupons are security-sensitive.
### Exploit examples
Negative quantity:
```http
POST /api/orders HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"items":[{"sku":"pro-month","quantity":-1}]}
```
If total becomes negative, the app may credit the user.
Currency confusion:
```http
POST /api/checkout HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"plan_id":"pro","currency":"JPY","amount":2999}
```
If `2999 JPY` is treated as `2999 USD`, totals are manipulated.
Coupon stacking/refund abuse/trial reset:
```http
POST /api/coupons/redeem HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"code":"SAVE90"}
```
Repeat with multiple or same coupon; test `SAVE90+WELCOME100`. For refunds, replay `POST /api/refunds` with the same `order_id`; check cumulative refund limits. For trials, create aliases or reset device/account identifiers only on your own test accounts.
### Detection
- Boundary-test quantity `-1`, `0`, `1`, large values, floats, strings, arrays, duplicates.
- Change currency, plan, coupon combinations, discount order, and refund count.
- Test partial/full refunds, refund-after-refund, and refund destination changes.
- Cancel/restart trials and check identity rules.
### Fix
- Validate business meaning: positive integer quantities, allowed currencies, max discounts, plan eligibility.
- Recalculate totals server-side from catalog data.
- Make coupon redemption atomic/single-use; store immutable refund ledger entries and enforce cumulative limits.
- Enforce trial eligibility using stable server-side identity/payment policy.
---

## 7. Subscription-state bugs
### Root cause
Subscription lifecycle is treated as a boolean or client-visible flag rather than a server-side state machine. Expiry may be checked only in JS, cancel may not revoke access, downgrade may leave premium fields intact, failed payments may still grant access, or client clocks/tokens may be trusted.
### Exploit examples
Expired session replay:
```http
GET /api/premium/report HTTP/1.1
Cookie: session=old_paid_session
```
Cancel without revoke:
```http
POST /api/subscriptions/current/cancel HTTP/1.1
Cookie: session=alice
```
If response says canceled but `/api/premium/report` still works, state was not updated. Arbitrary transition:
```http
POST /api/subscriptions/current/transition HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"to":"active"}
```
### Detection
- Expire a test subscription or manipulate dev DB time; replay old sessions/tokens/signed URLs.
- Cancel, fail payment, downgrade, refund, and charge back; verify access at each step.
- Try direct `status`, `plan`, `premium_until`, or `features` fields in requests.
- Test webhook ordering such as `invoice.payment_failed` followed by `customer.subscription.deleted`.
### Fix
- Model states explicitly: `trialing -> active -> past_due -> canceled`, `active -> cancel_at_period_end -> canceled`, `paid -> refunded -> revoked`.
- Store `status`, `plan_id`, `current_period_end`, `cancel_at_period_end`, and gateway IDs server-side.
- Enforce entitlement on every sensitive request using server time.
- Only verified gateway events or authorized admin actions may transition state.
- Define cancel/downgrade/refund semantics precisely and revoke at the correct boundary.
---

## 8. Race conditions
### Root cause
Check-then-act (TOCTOU) gaps let concurrent requests pass validation before state updates. PortSwigger describes limit overrun races where requests enter a temporary state before either completes the write. Payment examples: coupon reuse, credit double-spend, gift-card redemption, trial activation, refund duplication, parallel checkout completion.
### Exploit example
Two parallel requests redeem one coupon:
```http
POST /api/coupons/redeem HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"code":"SAVE50"}
```
If code checks `CouponUse.exists()` then creates it without a transaction/unique constraint, both requests can pass. Credit double-spend works similarly: two `POST /api/wallet/pay` requests see the same balance and both succeed.
### Detection
- Target single-use resources: coupons, credits, gift cards, trials, refunds, invites, seats.
- Send 2, then 10–30 synchronized requests.
- Check for duplicate successes, negative balances, repeated discounts, duplicate ledger entries.
- Verify locks are inside transactions; `SELECT ... FOR UPDATE` outside a transaction may not lock.
### Fix
- Put check and mutation in one transaction.
- Use unique constraints (`user_id,coupon_id`, `payment_event_id`, `idempotency_key`).
- Use atomic conditional updates, e.g. `UPDATE credits SET balance=balance-? WHERE user_id=? AND balance>=?`.
- Use row locks inside transactions or appropriate isolation; make webhook/event processing idempotent.
- Rate-limit and alert on suspicious parallel successes.
---

## 9. Mock-payment and dev-mode issues
### Root cause
Development conveniences leak into production: mock gateways, unsigned callbacks, debug flags, hardcoded success, test cards accepted, `PAYMENT_MODE=mock`, or client-side bypass switches.
### Exploit examples
```http
POST /api/mock-payment/complete HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"order_id":"ord_1001"}
```
```http
POST /api/webhooks/mock HTTP/1.1
Content-Type: application/json
{"status":"success","user_id":"user_1001","plan":"enterprise"}
```
```http
POST /api/checkout HTTP/1.1
Cookie: session=alice
Content-Type: application/json
{"plan_id":"pro","dev_mode":true,"force_success":true}
```
Config leakage such as `PAYMENT_PROVIDER=mock`, `MOCK_WEBHOOK_SECRET=`, `ALLOW_TEST_CARDS=true`, or `DEBUG_GRANT_PREMIUM=true` is equally dangerous.
### Detection
- Search routes/config for `mock`, `test`, `dev`, `sandbox`, `fake`, `bypass`, `force`, `debug`.
- Try test cards and sandbox behavior only on your own app.
- Check whether production accepts unsigned/trivially signed callbacks.
- Look for feature flags in bodies, headers, cookies, and accidentally deployed env files.
### Fix
- Separate dev/staging/prod config and secrets; compile out or disable mock endpoints in production.
- Require signed webhook verification even for sandbox/test gateways.
- Never accept client-controlled `dev_mode`, `force_success`, `test`, or `mock` flags for entitlement.
- Add deployment checks that fail if mock provider/debug routes are enabled in prod.
---

## 10. Payment flow architecture done right
### Recommended design
1. Catalog: plans, prices, currencies, and features live server-side.
2. Order creation: authenticated user selects `plan_id`; server creates `Order(status=pending)` and calculates amount.
3. Payment intent: server creates gateway checkout/payment session and stores `gateway_session_id` plus `idempotency_key`.
4. User payment: user pays on gateway-hosted page; browser never supplies authoritative price/status.
5. Return URL: redirect is UX only; it may say “processing,” not “paid.”
6. Webhook: verify raw-body signature, timestamp, event ID, object IDs, amount, currency, and customer mapping.
7. Deduplicate: store processed event/payment IDs; repeated events return success without repeated side effects.
8. State machine: `pending -> paid -> active -> past_due -> canceled`; invalid transitions rejected.
9. Entitlement: derive premium access from current subscription state and `current_period_end`.
10. Audit: log order creation, checkout intent, webhook verification, transitions, entitlement changes, refunds, and admin actions.
### Flask-style pseudocode
```python
@app.post("/api/checkout")
@login_required
def checkout():
    plan = PLAN_CATALOG.get(request.json.get("plan_id"))
    if not plan:
        abort(400)
    order = Order.create(user_id=current_user.id, plan_id=plan.id,
                         amount=plan.price, currency=plan.currency,
                         status="pending", idempotency_key=uuid4())
    session_obj = stripe.checkout.Session.create(
        line_items=[...], client_reference_id=str(order.id),
        metadata={"order_id": str(order.id)},
        idempotency_key=str(order.idempotency_key))
    order.gateway_session_id = session_obj.id
    order.save()
    return {"checkout_url": session_obj.url}
```
```python
@app.post("/webhooks/stripe")
def stripe_webhook():
    raw_body = request.get_data()
    try:
        event = stripe.Webhook.construct_event(
            raw_body, request.headers.get("Stripe-Signature"), STRIPE_WEBHOOK_SECRET)
    except Exception:
        return "bad signature", 400
    if WebhookEvent.objects.filter(gateway_event_id=event["id"]).exists():
        return "", 200
    obj = event["data"]["object"]
    order = Order.objects.select_for_update().get(gateway_session_id=obj["id"])
    # Verify type, payment_status, amount, currency, and customer mapping.
    # Optionally retrieve authoritative session/object state from Stripe.
    if event["type"] == "checkout.session.completed" and obj.get("payment_status") == "paid":
        order.status = "paid"
        Subscription.activate(order.user, order.plan, order.current_period_end)
        WebhookEvent.create(gateway_event_id=event["id"], order=order)
    return "", 200
```
---

## 11. Public real-world examples and labs
Public disclosures/advisories and hands-on labs for pattern recognition. They are not authorization to test those systems.

| Case | Class demonstrated | Source |
|---|---|---|
| CVE-2008-7310, Spree | Mass assignment let client set order state and bypass payment | [NVD](https://nvd.nist.gov/vuln/detail/CVE-2008-7310) |
| CVE-2024-45300, alf.io | Race condition reused limited promo codes | [GitHub advisory](https://github.com/alfio-event/alf.io/security/advisories/GHSA-67jg-m6f3-473g) |
| CVE-2026-55219, Paymenter | Lock outside transaction enabled credit double-spend | [GitHub advisory](https://github.com/Paymenter/Paymenter/security/advisories/GHSA-pgcq-8grm-5rx9) |
| CVE-2025-11564, Tutor LMS | Forged webhook marked orders paid | [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-11564) |
| CVE-2026-0656, iPaymu WooCommerce | Missing webhook authentication marked orders paid | [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-0656) |
| CVE-2026-1305, Japanized/WooCommerce Paidy | Omitted signature header passed permission check | [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-1305) |
| CVE-2026-33731, AVideo Authorize.Net | Signature OR-logic plus payload-over-API values enabled premium fraud | [GitHub advisory](https://github.com/WWBN/AVideo/security/advisories/GHSA-95jh-7r58-xmxw) |
| CVE-2024-21491, Svix webhooks | Different-length signature comparison allowed bypass | [RustSec](https://rustsec.org/advisories/RUSTSEC-2024-0010.html) |
| CVE-2024-1666, Lunary | Free-account restriction enforced only in web UI | [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-1666) |
| Payment Bypass Techniques Lab | Price modification, direct path access, permission bypass | [GitHub lab](https://github.com/zack0x01/Payment-bypass-bug-lab) |
---

## 12. Safe testing methodology on your own app
### Setup
- Run Flask locally or in disposable staging; use test accounts only: free, paid, admin.
- Use Stripe test mode (`sk_test_`, `whsec_`) or a mock gateway you control.
- Never send forged webhooks or race traffic to production or third-party endpoints.
### Burp Suite workflow
1. Browse checkout normally and identify requests in Proxy/HTTP history.
2. Send interesting requests to Repeater and baseline each one.
3. Change one variable at a time: plan, price, quantity, currency, coupon, user/subscription/payment IDs.
4. For state tests, replay cancel/downgrade/refund/return endpoints and inspect DB state.
5. For webhooks, send forged JSON to your local route; bad signatures should return 4xx and not mutate state.
6. For authorization, keep free and paid/admin Repeater tabs; compare object IDs and endpoints.
### Race-condition testing
PortSwigger Repeater can send request groups in parallel. HTTP/1 uses last-byte synchronization; HTTP/2 can use the single-packet attack to reduce network jitter. Turbo Intruder helps with custom concurrency and gates:
```python
engine = RequestEngine(endpoint=target_url, concurrentConnections=10,
                       requestsPerConnection=1, pipeline=False)
gate = Gate()
for i in range(20):
    engine.queue(target_request, gate=gate)
gate.open()
while engine.has_requests():
    engine.next_response()
```
Check DB/logs afterward: exactly one coupon redemption, credit debit, subscription activation, or refund.
### Test matrix
| Area | Tests |
|---|---|
| Client trust | Tamper price, plan, paid flag, hidden fields, success redirect |
| BOLA | Swap subscription/invoice/payment/user IDs across accounts |
| AuthZ | Call admin/debug/premium functions as free user; test JWT edge cases locally |
| API surface | Enumerate endpoints/methods, GraphQL introspection, debug routes |
| Webhooks | Forged body, bad signature, replay, duplicate event, wrong amount/currency |
| Business logic | Negative qty, currency switch, coupon stacking, refund repeat, trial reset |
| State | Expired access, cancel/downgrade/refund transitions, old session replay |
| Race | Parallel coupon redeem, credit spend, checkout completion, refund |
| Mock mode | Mock endpoints, dev flags, test gateway behavior in prod-like config |
### Secure outcome
- Tampered prices ignored; server catalog determines amount.
- Cross-account IDs return consistent `403`/`404`.
- Forged/replayed webhooks do not change subscription state.
- Parallel single-use operations produce exactly one success.
- Expired/canceled subscriptions lose access at the correct server-side boundary.
- Audit logs show who/what/when for every entitlement change.
---

## Sources
- OWASP API Security Top 10 2023: API1 BOLA, API3 Broken Object Property Level Authorization, API5 Broken Function Level Authorization, API6 Unrestricted Access to Sensitive Business Flows, API9 Improper Inventory Management.
- OWASP Authorization, JSON Web Token, Business Logic Security, Third Party Payment Gateway Integration, and Webhook Security Cheat Sheets.
- Stripe Docs: webhook signature verification/event handling and idempotent requests.
- PortSwigger Web Security Academy: race conditions, limit overruns, and single-packet attack methodology.
- NVD, GitHub Security Advisories, and RustSec records listed in Section 11.

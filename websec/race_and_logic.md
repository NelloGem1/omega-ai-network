# Race Conditions and Advanced Business Logic: Deep-Dive Research

**Scope:** authorized testing only — the user's own Flask subscription app, local labs, PortSwigger Academy, PayloadsAllTheThings, or explicitly permitted bug-bounty targets. These techniques are for understanding how payment/subscription controls fail when requests execute concurrently or when the application trusts client-controlled workflow state.

**One-line model:** a race condition wins when two or more requests observe the same pre-change state and then commit conflicting transitions; a business-logic flaw wins when each individual request is syntactically valid but the sequence, state, price, quantity, or entitlement transition violates the intended rule.

---

## 1. Race-condition theory

### 1.1 What a race condition is

A web race condition happens when correctness depends on the order or timing of concurrent requests. The application often assumes a shared resource is modified by one request at a time, but HTTP servers, workers, async frameworks, and browsers routinely process requests in parallel.

The dangerous shape is usually **read-check-decide-write**:

1. Request A reads `coupon.used = false`.
2. Request B reads `coupon.used = false`.
3. Both decide the coupon is valid.
4. Both apply the discount.
5. Both write `coupon.used = true`.

If the read and write are not atomic, the "only once" invariant is broken. This is why PortSwigger describes limit overruns as a subtype of **time-of-check to time-of-use (TOCTOU)** flaws.

### 1.2 Time-of-check vs time-of-use

- **Time of check:** the moment the app validates a condition, e.g. `balance >= price`, `coupon not used`, `seats_available > 0`, `trial not already claimed`, `rate_limit_count < max`.
- **Time of use:** the moment the app commits the mutation, e.g. `INSERT redemption`, `UPDATE balance`, `UPDATE subscription.status`, `DELETE token`, `INSERT vote`.

The vulnerability is the interval between those two points. It may be microseconds, milliseconds, or longer if the handler performs database queries, external API calls, email/SMS delivery, template rendering, cryptography, or sleeps between check and write.

### 1.3 Why parallel requests break assumptions

Developers often test one request at a time. Sequential behavior looks correct because request 1 commits before request 2 checks. Parallel behavior exposes hidden assumptions:

- Flask may run threaded WSGI workers, gevent/eventlet workers, async tasks, or multiple gunicorn/uvicorn processes.
- SQLite and Postgres have different isolation defaults; SQLite serializes writes but not necessarily application-level check-then-act logic.
- Session cookies may be per-user, but two tabs, two devices, or two API calls share the same logical account state.
- A server-side lock may protect a route but not the whole business transaction.
- Webhook handlers, background jobs, and frontend polling can mutate the same subscription row.
- HTTP/2 multiplexing makes it trivial for many requests to be in flight over one connection.

The race window is not always between two identical requests. It can be between:

- `POST /checkout` and `POST /cart/add`
- `POST /payment/webhook` and `GET /premium/report`
- `POST /trial/start` and `POST /account/delete`
- `POST /subscription/downgrade` and `GET /billing/status`
- `POST /coupon/redeem` and `GET /balance`

### 1.4 Sub-states and state machines

PortSwigger's "smashing the state machine" research reframes races as transitions through temporary **sub-states**. A request may enter a sub-state such as "payment verification in progress" or "coupon redemption pending" and exit it only after several operations complete. Another request can interact with the same resource while that sub-state is active.

Examples of short-lived sub-states:

- Order created but payment not yet verified.
- Coupon checked but not yet marked used.
- Password-reset token generated but not yet invalidated.
- Subscription upgraded but webhook not yet reconciled.
- Seat reserved but not yet committed.
- Trial entitlement granted but account not yet marked as trialing.

These are especially relevant to subscription apps because entitlement is often derived from a mutable row (`user.plan`, `subscription.status`, `trial_ends_at`, `balance`) that several endpoints read and write.

---

## 2. Single-packet attacks and Turbo Intruder

### 2.1 Network jitter

If you fire 20 requests "at the same time" from separate TCP connections, network jitter, packet scheduling, TLS handshake timing, and server queueing mean they do not actually arrive together. Some arrive milliseconds apart, which is often enough for request 1 to finish its critical section before request 2 begins.

### 2.2 Last-byte synchronization

The classic workaround is **last-byte sync**:

1. Send every request except its final byte.
2. The server receives almost-complete requests but cannot process them.
3. Send the final byte of each request together.
4. The requests complete nearly simultaneously.

This reduces client-side timing spread, but the requests still travel over separate connections/streams and can be reordered.

### 2.3 HTTP/2 single-packet attack

PortSwigger Research's single-packet attack improves on last-byte sync for HTTP/2 targets:

1. Open one HTTP/2 connection.
2. Queue 20–30 requests on that connection.
3. Withhold a tiny final fragment from each request.
4. Wait briefly for packets to arrive near the target.
5. Send the final fragment for all requests.
6. The OS groups the final fragments into one TCP packet.

The requests complete at almost the same time regardless of prior network jitter. PortSwigger's published benchmark reported roughly a **1 ms median spread / 0.3 ms standard deviation** for the single-packet attack versus **4 ms / 3 ms** for last-byte sync in their test.

Important constraints:

- Best for HTTP/2. HTTP/1.1 cannot multiplex requests over one connection.
- For HTTP/1.1, use multiple connections and last-byte/threaded techniques.
- Very large request bodies may exceed packet/frame limits; PortSwigger research discusses first-sequence-sync workarounds.
- A negative timestamp in Turbo Intruder can mean the server began responding before the request was fully sent — evidence of server-side overlap.

### 2.4 Burp Repeater vs Turbo Intruder

Burp Suite Professional 2023.9+ can send grouped requests in parallel:

- HTTP/1 targets: last-byte synchronization.
- HTTP/2 targets: single-packet attack.
- "Trigger race conditions" custom action helps automate limit-overrun labs.

Burp Community lacks the native grouped parallel request workflow, but testers can use:

- Turbo Intruder if available.
- `curl` loops with background jobs.
- Python `asyncio`/`aiohttp`.
- Go/Rust/Node scripts.
- `Raceocat` or `h2spacex` for lower-level HTTP/2 work.

### 2.5 Turbo Intruder template: coupon reuse

Use this when the captured request is `POST /api/coupon/redeem` with a body containing the coupon code. Replace placeholders with the actual captured request and coupon.

```python
def queueRequests(target, wordlists):
    # HTTP/2 target: Engine.BURP2 + one connection enables the single-packet attack.
    # HTTP/1.1 target: use Engine.THREADED or Engine.BURP with many connections.
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)

    # target.req should contain the coupon body, e.g. {"code":"SAVE50"}.
    # The 'gate' argument withholds the final fragment until openGate().
    for i in range(30):
        engine.queue(target.req, gate='race1')

    engine.openGate('race1')


def handleResponse(req, interesting):
    # Keep successes, duplicates, and unusual statuses; ignore boring 4xx noise.
    if req.status in (200, 201, 202) or 'success' in req.response.lower():
        table.add(req)
```

Expected signal: many successful responses instead of one success plus many "already used" responses. Then verify server-side state: balance/credit, discount applied, coupon redemption count, order total.

### 2.6 Turbo Intruder template: balance double-spend

Use for `POST /api/withdraw`, `POST /api/transfer`, `POST /api/balance/spend`, or any endpoint that checks balance then debits it.

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)

    # Example target.req body: {"amount": 10.00, "destination":"acct_b"}
    # If the app needs a unique idempotency-looking field, remove it or keep it
    # fixed only if testing whether the server treats it as a real idempotency key.
    for i in range(25):
        engine.queue(target.req, gate='race1')

    engine.openGate('race1')


def handleResponse(req, interesting):
    # Look for multiple 200s and then reconcile balance/ledger server-side.
    if req.status == 200 or 'success' in req.response.lower():
        table.add(req)
```

Verification is critical: the HTTP response may say success while the ledger is inconsistent. Check final balance, transaction list, and whether total debits exceed the starting balance.

### 2.7 Turbo Intruder template: vote/like limit bypass

Use for `POST /api/posts/123/vote`, `/like`, `/follow`, `/join`, or `/claim` where one vote/claim per user is expected.

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)

    # Capture one legitimate vote request and send it to Turbo Intruder.
    # If the endpoint has a CSRF token, use the captured value first; if tokens
    # are per-request, this simple identical-request template may need adaptation.
    for i in range(20):
        engine.queue(target.req, gate='vote_race')

    engine.openGate('vote_race')


def handleResponse(req, interesting):
    # Count how many responses indicate success; compare to visible score.
    if req.status == 200 and ('voted' in req.response.lower()
                              or 'liked' in req.response.lower()
                              or 'success' in req.response.lower()):
        table.add(req)
```

For **multi-endpoint races**, queue different requests under separate gates and stagger or synchronize them. PortSwigger's research shows you can align an action that creates a resource with an action that consumes it, for example `POST /cart` plus `POST /cart/checkout`, or login plus admin access.

---

## 3. Race-condition targets in subscription apps

Prioritize endpoints that combine a limit, entitlement, balance, seat, token, or one-time transition with multiple writes.

| Target | Typical check | Race consequence |
|---|---|---|
| Coupon/promo redeem | `coupon.used == false` | Discount applied many times or price driven negative |
| Gift card / credit redeem | `balance/card unused` | Balance credited N times |
| Free trial claim | `user.trial_claimed == false` | Multiple trial periods or concurrent plan grants |
| Referral/self-referral | `referral.applied == false` | Bonus paid repeatedly or self-dealing |
| Upgrade/downgrade | current plan/status read | Entitlement set to higher plan while billing lower plan |
| Refund + access | refund status vs subscription status | Refund succeeds while premium remains active |
| Cancel/reactivate | subscription state transition | New trial, retained access, or duplicate subscription |
| Family/team seats | `seat_count < max` | Oversell seats, negative seat price, or unbounded invites |
| Password-reset token | token valid and unused | Multiple simultaneous resets or token reuse window |
| Email verification / invite | token unused | One invite consumed by many accounts |
| Loyalty points | `points >= cost` | Points spent multiple times or duplicated |
| CAPTCHA/rate limit | attempt count below threshold | Brute-force or OTP bypass |
| Inventory/seat reservation | `available > 0` | Overselling limited plans |
| Webhook replay | event not processed | Duplicate entitlement grants or revocations |

For a Flask app, inspect routes for patterns such as:

```python
if coupon.used:
    return error
coupon.used = True
order.discount = coupon.value
```

That is vulnerable if another request can pass `if coupon.used` before the first request commits. The safer shape is an atomic conditional update or transaction with locking.

---

## 4. Detection methodology

### 4.1 Predict potential collisions

Look for endpoints that:

- Change money, credits, seats, plan, role, trial state, or access.
- Enforce "once", "first", "only one", "maximum", or "per user" rules.
- Read state, call another service, then write state.
- Use session IDs as the only resource key while multiple requests share that session.
- Have multi-step workflows where confirmation can be called directly.
- Interact with the same DB row from different routes.

Ask: **what two requests, sent at the same time, could both pass the same check?**

### 4.2 Probe for clues

Signals that a race window may exist:

- Response time differs between first and duplicate requests.
- Endpoint does several DB queries or external calls.
- State is stored in a cookie/localStorage but authoritative state is server-side.
- Frontend disables a button but backend accepts replay.
- Error says "already used" only after a delay.
- WebSocket/polling updates lag behind POST response.
- Webhook processing is asynchronous.
- Admin/support actions and user actions touch the same subscription.
- Login/session locking exists but does not cover payment endpoints.

### 4.3 Prove the concept cheaply

Before launching 100 requests:

1. Send two identical requests manually in Burp Repeater.
2. Send a sequential pair, then a parallel pair.
3. Compare response codes, bodies, and final server-side state.
4. Repeat 5–10 times; races are probabilistic.
5. Increase batch size only after seeing occasional anomalies.

A useful metric is **state delta vs response count**. If 10 requests return success but only 1 credit was applied, the server reconciled. If 10 requests return success and 10 credits were applied, you found the bug.

### 4.4 Burp Suite Pro workflow

1. Capture the state-changing request.
2. Send it to Repeater.
3. Duplicate the tab 10–30 times.
4. Add all tabs to a group.
5. Use **Send group in parallel**.
6. Burp chooses last-byte sync for HTTP/1 or single-packet attack for HTTP/2.
7. Inspect response order, statuses, lengths, and bodies.
8. Verify state in the app/database.

### 4.5 Burp Community / CLI workarounds

`curl` parallel burst:

```bash
for i in $(seq 1 30); do
  curl -sS -b cookies.txt -H 'Content-Type: application/json' \
    -d '{"code":"SAVE50"}' \
    -o "resp_$i.txt" -w "%{http_code} %{time_total}\n" \
    http://127.0.0.1:5000/api/coupon/redeem &
done
wait
sort -n resp_*.txt | uniq -c
```

Python `asyncio`/`aiohttp` gives better result collection and diffing. The next section provides a skeleton.

---

## 5. Asyncio attack script template

This skeleton fires N concurrent requests with `aiohttp`, captures status/body/time, and summarizes likely successful redemptions. It is a baseline concurrency tester; for true single-packet timing use Turbo Intruder or an HTTP/2-capable tool.

```python
#!/usr/bin/env python3
"""
Race-condition probe for a Flask subscription app.

Usage:
    python3 race_probe.py http://127.0.0.1:5000 /api/coupon/redeem \
        '{"code":"SAVE50"}' 'session=YOUR_COOKIE' 30
"""

import asyncio
import aiohttp
import collections
import json
import sys
import time


async def one_request(session, idx, url, payload, headers):
    started = time.perf_counter()
    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            body = await resp.text()
            elapsed_ms = (time.perf_counter() - started) * 1000
            return {
                "idx": idx,
                "status": resp.status,
                "elapsed_ms": elapsed_ms,
                "body": body[:1000],
                "ok": resp.status in (200, 201, 202),
            }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "idx": idx,
            "status": -1,
            "elapsed_ms": elapsed_ms,
            "body": repr(exc),
            "ok": False,
        }


async def main():
    if len(sys.argv) < 5:
        print(__doc__)
        return 2

    base = sys.argv[1].rstrip("/")
    path = sys.argv[2]
    payload = json.loads(sys.argv[3])
    cookie = sys.argv[4]
    count = int(sys.argv[5]) if len(sys.argv) > 5 else 30

    url = base + path
    headers = {
        "Content-Type": "application/json",
        "Cookie": cookie,
        "User-Agent": "race-probe/1.0",
        "Accept": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [
            asyncio.create_task(one_request(session, i, url, payload, headers))
            for i in range(count)
        ]
        results = await asyncio.gather(*tasks)

    status_counts = collections.Counter(r["status"] for r in results)
    ok_results = [r for r in results if r["ok"]]
    body_groups = collections.Counter(r["body"][:160] for r in results)

    print(f"target={url}")
    print(f"requests={len(results)} ok={len(ok_results)}")
    print("status_counts:", dict(status_counts))
    print("body_groups:")
    for body, n in body_groups.most_common(10):
        print(f"  {n:3d} x {body!r}")

    print("\ninteresting responses:")
    for r in results:
        lower = r["body"].lower()
        interesting = (
            r["ok"]
            or "success" in lower
            or "redeemed" in lower
            or "applied" in lower
            or "credited" in lower
            or "already" in lower
        )
        if interesting:
            print(f"#{r['idx']:02d} status={r['status']} time={r['elapsed_ms']:.1f}ms body={r['body'][:300]!r}")

    if len(ok_results) > 1:
        print("\nPOSSIBLE RACE: multiple requests returned success.")
        print("Verify server-side state before claiming impact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```

Notes:

- For cookie auth, pass the full `Cookie` header value or adapt to `aiohttp.CookieJar`.
- For CSRF-protected Flask forms, include the token in `payload` or headers; capture a fresh token first if needed.
- For stronger simultaneity, use Burp/Turbo Intruder on HTTP/2, or write a lower-level HTTP/2 client. `aiohttp` is excellent for iteration and response analysis but is not a guaranteed single-packet attack.
- Always verify the actual balance, plan, coupon ledger, seat count, or subscription status after the burst.

---

## 6. Business-logic deep patterns

Business-logic vulnerabilities do not require malformed syntax. They exploit valid operations in invalid order, quantity, state, or business context.

### 6.1 Workflow step skipping

Multi-step flows often assume users complete steps in order. Test whether later endpoints can be invoked directly.

Examples:

- `GET /cart/order-confirmation?order-confirmed=true` without paying.
- `POST /checkout/complete` before `/checkout/payment`.
- Calling `POST /subscription/activate` without a successful payment event.
- Skipping email verification then accessing premium routes.
- Jumping from cart to receipt/invoice endpoints.

Detection method:

1. Map every step and request in the flow.
2. Replay each request independently.
3. Reorder requests.
4. Remove required steps.
5. Call confirmation/finalize endpoints with guessed or replayed parameters.
6. Check whether server-side state, not the URL/query flag, authorizes completion.

### 6.2 Price oracle attacks

A "price oracle" is any response that lets you infer the real price or acceptance threshold without directly seeing the database. In a subscription app, look for:

- Plan catalog endpoints returning hidden `price_id`s.
- Coupon validation endpoints returning exact discount or final price.
- Checkout preview vs charge amount mismatches.
- Error messages that distinguish "too expensive" from "invalid plan".
- Timing or status differences between valid and invalid price points.
- Integer IDs that can be enumerated (`plan_id=1`, `price_id=2`).

Attack pattern:

1. Capture legitimate checkout request.
2. Tamper `plan_id`, `price_id`, `amount`, `currency`, `quantity`, `coupon`, or `billing_interval`.
3. Compare preview response, order response, payment amount, and final entitlement.
4. Binary-search boundaries: if `amount=100` fails and `amount=0` succeeds, test intermediate values or manipulate quantity/currency to infer the server's real threshold.
5. Look for mismatches between what the UI displays, what the order stores, and what the payment provider charges.

The goal is not always to see the price; it is to find a field where the server validates existence but not authorization/consistency.

### 6.3 Currency and rounding abuse

Test:

- Pay in one currency, refund in another.
- Negative or zero amounts.
- Fractional minor units (`0.001`, `0.000001`).
- Rounding direction differences between debit and credit.
- Currency conversion applied twice or not at all.
- Tax/discount applied before vs after rounding.
- `float` prices instead of integer minor units.
- Stripe/payment amounts in dollars vs cents mismatch.

PayloadsAllTheThings documents a rounding-error case where a transfer below the minimum precision credited the receiver while not debiting the sender. HackerOne report 808975 shows another rounding/fee-evasion pattern.

### 6.4 Negative, zero, huge, and overflow quantities

Try:

- `quantity=-1`, `quantity=-100`
- `quantity=0`
- `quantity=1.5`, `quantity=1.9`, `quantity=NaN`, `quantity=1e309`
- Very large integers near `2^31-1` or `2^63-1`
- Mixed positive and negative line items
- Quantity in body vs quantity in URL/header
- Seat count as decimal, string, array, or object

PortSwigger's low-level logic lab demonstrates 32-bit integer overflow: enough additions wrap the total negative, then fine-tuning lands it within budget. HackerOne report 364843 shows a real negative-quantity price manipulation.

### 6.5 Referral, loyalty, and bonus abuse

Test:

- Self-referral with a second account.
- Applying multiple referral codes.
- Referral reward before the referee pays/converts.
- Loyalty points spent twice via race condition.
- Points conversion rate or cost supplied by client.
- Signup credit claimed on duplicate accounts.
- One-per-account promo applied across account variants.
- Bonus granted on `email_verified=false` or before required action.

OWASP's Business Logic Security Cheat Sheet explicitly calls out multi-accounting, self-referral, coupon stacking, and race-prone read-check-write operations.

---

## 7. Subscription-specific logic attacks

### 7.1 Plan downgrade while keeping premium

Test transitions:

- `PATCH /api/subscription {"plan":"free"}` then check premium endpoints.
- Cancel subscription but keep `premium_until` in the future.
- Downgrade to free while `subscription.status` remains `active`.
- Remove payment method after upgrade.
- Race downgrade webhook against premium access check.
- Directly call internal/admin plan-change endpoints.

Look for stale entitlements: access checks reading a cached plan, JWT claim, cookie flag, or old DB row after billing state changed.

### 7.2 Cancel-then-refund-keep

Sequence to test:

1. Subscribe or upgrade.
2. Use premium feature.
3. Request refund and cancellation concurrently or in reverse order.
4. Check whether refund revokes entitlement.
5. Check whether cancellation preserves access until period end while refund already returned money.
6. Repeat refund/cancel requests for multiple partial refunds.

The bug is often split responsibility: payment provider marks refunded, app marks canceled, but entitlement service never downgrades.

### 7.3 Trial extension loops

Try:

- Cancel trial then reactivate.
- Delete account and re-register with same payment/device.
- Change email aliases (`user+1@example.com`, dots, plus tags).
- Manipulate `trial_days`, `trial_end`, `trial_ends_at`, or `plan` fields.
- Start trial on multiple subscriptions/seats.
- Race trial start against account deletion or plan change.
- Reuse payment method across accounts to detect whether trial resets.

### 7.4 Family/team seat sharing and overselling

Test:

- Add more seats than purchased.
- Decimal seat counts (`1.9`) where seats are rounded up but price rounded down.
- Invite race: send N invites before seat count updates.
- Transfer/remove/re-add seats.
- Share one paid seat across multiple devices/users.
- Change owner/admin roles.
- Downgrade seats while members retain access.

HackerOne report 1446090 is a strong example: adding `1.9` seats produced two seats but billing multiplied only the integer part.

### 7.5 Proration exploits

Proration is fertile ground because upgrades/downgrades generate credits and charges:

- Upgrade then immediately downgrade and request refund.
- Downgrade then upgrade within same period.
- Change billing interval (`monthly` ↔ `yearly`) repeatedly.
- Add/remove seats near period boundary.
- Trigger proration while a coupon/refund is pending.
- Compare invoice line items, credit balance, and final charge.
- Race plan change with invoice finalization.

Look for negative invoice amounts, credits that exceed payments, or proration calculated from client-supplied timestamps.

### 7.6 Grace-period abuse

If payment fails, apps often grant a grace period. Test:

- Keep using premium after failed payment until grace expires.
- Cancel during grace and retain access.
- Reactivate repeatedly to reset grace.
- Add/remove payment method during dunning.
- Race webhook `invoice.payment_failed` against entitlement check.
- Multiple subscriptions so one failed payment doesn't revoke another.

---

## 8. Defense side

### 8.1 Atomic check-and-set

The core fix is to make the check and mutation one indivisible operation.

Bad pattern:

```python
if not coupon.used:
    apply_discount(order)
    coupon.used = True
```

Better pattern with SQLAlchemy/Postgres:

```python
with db.session.begin():
    coupon = db.session.query(Coupon).filter_by(code=code).with_for_update().one()
    if coupon.used_count >= coupon.max_uses:
        raise InvalidCoupon()
    apply_discount(order)
    coupon.used_count += 1
    redemption = CouponRedemption(user_id=user.id, coupon_id=coupon.id)
    db.session.add(redemption)
```

Even better: a single conditional update or unique constraint.

```sql
UPDATE coupons
SET used_count = used_count + 1
WHERE code = :code
  AND used_count < max_uses
RETURNING id;
```

If zero rows return, reject.

For per-user coupon limits:

```sql
INSERT INTO coupon_redemptions (user_id, coupon_id)
VALUES (:user_id, :coupon_id)
ON CONFLICT (user_id, coupon_id) DO NOTHING
RETURNING id;
```

No row returned means already redeemed.

### 8.2 Transactions and locking

- Use DB transactions for multi-step financial mutations.
- Use `SELECT ... FOR UPDATE` on the row being checked/mutated.
- Use Postgres advisory locks keyed by user/order/coupon if row locking is awkward.
- Keep transactions short; do not call slow external APIs inside them unless necessary.
- Use serializable isolation for high-risk balance/seat operations if the DB supports it.
- Ensure retries are idempotent.

### 8.3 Idempotency keys

For payment, refund, redeem, transfer, seat, and webhook endpoints:

- Require or accept `Idempotency-Key`.
- Store `(user_id, endpoint, idempotency_key)` uniquely.
- Store request fingerprint and response; replay returns same result.
- Reject reuse of the same key with a different payload.
- Expire keys only after safe retention.

This protects against retries, double-clicks, mobile network retries, and attacker replay.

### 8.4 Constraints and invariants

Database constraints are the last line of defense:

- `UNIQUE(user_id, coupon_id)`
- `UNIQUE(order_id, payment_event_id)`
- `CHECK(quantity > 0)`
- `CHECK(amount >= 0)`
- `CHECK(balance >= 0)`
- `CHECK(seat_count <= purchased_seats)`
- `CHECK(plan IN (...))`
- Foreign keys to enforce valid plan/coupon/subscription references.

Application checks alone are bypassable; constraints make invalid states impossible.

### 8.5 Rate limits per user and resource

Rate limiting by IP alone is weak. Limit by:

- authenticated user ID
- subscription/account ID
- coupon code
- endpoint + action
- device/session risk signals

Use atomic counters or Redis with atomic increments. For critical endpoints, combine rate limit with idempotency and audit logging.

### 8.6 Server-side state machines

Define allowed transitions explicitly:

```text
trialing -> active -> past_due -> canceled -> expired
active -> downgraded -> active
created -> paid -> active
refund_requested -> refunded -> revoked
```

Reject impossible transitions regardless of client input. Entitlement should be derived from authoritative state plus current time, not from a client flag.

### 8.7 Webhook and payment safety

- Verify webhook signatures.
- Deduplicate event IDs.
- Process events idempotently.
- Reconcile payment provider state with local subscription state.
- Do not grant entitlement from browser redirect alone.
- Store raw event payload and processing result for audit.

### 8.8 Audit trails and anomaly detection

Log:

- actor, tenant, object IDs
- before/after values for balance, plan, coupon, seat, trial
- request ID, idempotency key, IP/device fingerprint
- response outcome
- webhook event ID

Alert on:

- many successful redemptions from one user/IP/device
- balance going negative
- entitlement granted without payment event
- rapid plan changes
- repeated refund/cancel sequences
- coupon use count exceeding max

---

## 9. Real writeups and cases

### 9.1 Stripe unlimited discount redemption

HackerOne/Stripe case summarized by HackerOne: a researcher used Turbo Intruder to call an accept-discount endpoint 30 times in parallel. Each call succeeded, turning a $20,000 fee discount into roughly $600,000 of fee-free transaction value. Stripe's first fix still left a race condition; the final remediation made redemption atomic. Bounty reported as $5,000.

Source: https://www.hackerone.com/blog/how-business-logic-vulnerability-led-unlimited-discount-redemption

### 9.2 Reverb gift-card multi-redeem

HackerOne report 759247: a gift-card redemption endpoint could be hit with ~30 concurrent Turbo Intruder requests, producing multiple successful redemptions from one card. Classic TOCTOU on "card unused" check.

Source: https://hackerone.com/reports/759247

### 9.3 Keybase invitation limit bypasses

- HackerOne 115007: concurrent invite requests bypassed an invitation limit.
- HackerOne 148609: redesigned invite flow allowed multiple user registrations consuming one invitation.

These show that fixing one race can introduce another when the state machine changes.

Sources:
- https://hackerone.com/reports/115007
- https://hackerone.com/reports/148609
- https://www.josipfranjkovic.com/blog/race-conditions-on-web

### 9.4 GitLab CVE-2022-4037

A race condition in GitLab CE/EE could lead to verified-email forgery and account takeover when GitLab acted as an OAuth provider. James Kettle demonstrated it using the single-packet attack methodology. CVSS 8.5 per NVD.

Sources:
- https://portswigger.net/research/smashing-the-state-machine
- https://www.youtube.com/watch?v=Y0NVIVucQNE
- https://nvd.nist.gov/vuln/detail/cve-2022-4037

### 9.5 Upserve negative-quantity price manipulation

HackerOne report 364843: an order JSON accepted an item with negative quantity, reducing the total price. Demonstrates business logic more than timing: valid syntax, invalid business quantity.

Source: https://hackerone.com/reports/364843

### 9.6 Krisp seat-count decimal flaw

HackerOne report 1446090: changing seats to `1.9` added two seats but billed only for the integer portion. A rounding/type-confusion logic flaw in subscription billing.

Source: https://hackerone.com/reports/1446090

### 9.7 lemlist failed-payment access retention

HackerOne report 1420697: after failed payments and cancellation, the user retained paid features. Shows entitlement revocation failure after payment state changes.

Source: https://hackerone.com/reports/1420697

### 9.8 Rounding/salami attack

PayloadsAllTheThings references HackerOne report 176461: a crypto transfer below precision could credit the receiver while failing to debit the sender. Automating tiny rounding differences can create value.

Source: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Business%20Logic%20Errors/README.md

### 9.9 HackerOne bounty-fee rounding

HackerOne report 808975: micro-value rewards exposed rounding behavior that could bypass part of the platform commission. Useful as a model for testing amount/fee/rounding consistency.

Source: https://hackerone.com/reports/808975

---

## 10. Lab mapping

### 10.1 PortSwigger Race Conditions

Main topic: https://portswigger.net/web-security/race-conditions

Recommended order:

1. **Limit overrun race conditions** — coupon/gift-card style TOCTOU.
2. **Bypassing rate limits via race conditions** — failed-login counter race.
3. **Multi-endpoint race conditions** — align two different requests.
4. **Single-endpoint race conditions** — deeper state-machine collision.
5. **Exploiting time-sensitive vulnerabilities** — password-reset token timing.
6. **Partial construction race conditions** — access partially initialized objects.

Direct lab links:

- https://portswigger.net/web-security/race-conditions/lab-race-conditions-limit-overrun
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-bypassing-rate-limits
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-multi-endpoint
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-single-endpoint
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-exploiting-time-sensitive-vulnerabilities
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-partial-construction

### 10.2 PortSwigger Business Logic labs

Topic: https://portswigger.net/web-security/logic-flaws

Most relevant labs:

- **Excessive trust in client-side controls** — client-supplied price.
- **High-level logic vulnerability** — negative quantity affects cart total.
- **Low-level logic flaw** — integer overflow/wrap in quantity/price.
- **Inconsistent security controls** — coupon/validation inconsistency.
- **Flawed enforcement of business rules** — alternating coupon codes bypasses duplicate check.
- **Inconsistent handling of exceptional input** — malformed/edge input.
- **Infinite money logic flaw** — coupon + gift-card workflow loop.
- **Insufficient workflow validation** — call order-confirmation directly.
- **Weak isolation on dual-use endpoint** — same endpoint serves different roles/flows.
- **Authentication bypass via flawed state machine** — invalid auth state transitions.
- **Authentication bypass via encryption oracle** — oracle reveals valid encrypted input.

### 10.3 PayloadsAllTheThings

Race Condition README: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Race%20Condition/README.md

Covers:

- Limit overrun methodology.
- Rate-limit bypass.
- HTTP/1.1 last-byte sync.
- HTTP/2 single-packet attack.
- Turbo Intruder examples.
- Tools: Turbo Intruder, Raceocat, h2spacex.

Business Logic Errors README: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Business%20Logic%20Errors/README.md

Covers:

- Discount code reuse and race conditions.
- Delivery fee manipulation.
- Currency arbitrage.
- Premium feature exploitation.
- Refund exploitation.
- Cart/wishlist negative quantities.
- Rounding errors.

### 10.4 Suggested practice path for the Flask app

1. Map subscription endpoints: signup, trial, checkout, webhook, cancel, refund, plan change, seats, coupons, balance.
2. For each endpoint, write the invariant: "only one redemption", "balance cannot go negative", "plan must match payment", "seat count cannot exceed purchased".
3. Test each invariant sequentially, then with parallel requests.
4. Try workflow skips before price tampering.
5. Try price/quantity/currency tampering before races.
6. Combine classes: race a plan change against webhook reconciliation, or refund against entitlement revocation.
7. Verify state in DB/logs, not just HTTP responses.

---

## Sources

- PortSwigger, *Race conditions*: https://portswigger.net/web-security/race-conditions
- PortSwigger Research, *Smashing the state machine: the true potential of web race conditions*: https://portswigger.net/research/smashing-the-state-machine
- PortSwigger Research, *The single-packet attack: making remote race-conditions 'local'*: https://portswigger.net/research/the-single-packet-attack-making-remote-race-conditions-local
- PortSwigger, *Business logic vulnerabilities*: https://portswigger.net/web-security/logic-flaws
- Turbo Intruder race-condition docs: https://github.com/PortSwigger/turbo-intruder/blob/master/docs/race-conditions.md
- Turbo Intruder single-packet example: https://github.com/PortSwigger/turbo-intruder/blob/master/resources/examples/race-single-packet-attack.py
- PayloadsAllTheThings, *Race Condition*: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Race%20Condition/README.md
- PayloadsAllTheThings, *Business Logic Errors*: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Business%20Logic%20Errors/README.md
- OWASP, *Business Logic Security Cheat Sheet*: https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html
- HackerOne, *How a Business Logic Vulnerability Led to Unlimited Discount Redemption*: https://www.hackerone.com/blog/how-business-logic-vulnerability-led-unlimited-discount-redemption
- HackerOne reports: https://hackerone.com/reports/759247, https://hackerone.com/reports/115007, https://hackerone.com/reports/148609, https://hackerone.com/reports/364843, https://hackerone.com/reports/1446090, https://hackerone.com/reports/1420697, https://hackerone.com/reports/808975
- CVE-2022-4037 / NVD: https://nvd.nist.gov/vuln/detail/cve-2022-4037
- Josip Franjković, *Race conditions on the web*: https://www.josipfranjkovic.com/blog/race-conditions-on-web

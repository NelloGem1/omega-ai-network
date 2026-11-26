# Trouw (DPG Media) — Rules of Engagement
Source: Intigriti program page, captured 2026-11-26
STATUS: ⏸️ NOT ACCEPTING SUBMISSIONS (paused — monitor for reopening)

## Bounty tiers
- Tier 2 assets: Low €50 / Med €300 / High €800 / Crit €1,200 / Exceptional €2,200
- Tier 3 assets (*.trouw.nl wildcard): Low €25 / Med €50 / High €100 / Crit €200 / Exc €500

## HARD RULES (violation = no bounty / ban)
- ONLY use @intigriti.me email address for comms
- Max 5 requests/second
- REQUIRED header on ALL requests: `X-Intigriti-Username: nellogem`
- NO automatic scanners — manual testing only, creative work required
- Quality over quantity; detailed repro + clear attack scenario
- No public disclosure of vulns/PoCs without consent
- ID check REQUIRED before submitting

## In scope
- myaccount.trouw.nl (T2)
- shop.trouw.nl (T2)
- webwinkel.trouw.nl (T2)
- www.trouw.nl (T2, EXCLUDING /service /inloggen /login /registreren)
- www.trouw.nl/abonnementen (T2)
- *.trouw.nl (T3 wildcard, EXCLUDING abonnement.trouw.nl)
- actie.trouw.nl listed but marked Out of scope — treat as OOS

## OUT OF SCOPE (do not report)
- XSS on www.trouw.nl/abonnementen
- Paywall bypass
- Open redirects in privacy consent endpoints
- Self-XSS, username/email enumeration, missing headers/cookie flags
- CORS misconfig on non-sensitive endpoints, CSRF low impact
- Rate-limit absence, clickjacking w/o impact, CSV injection
- Session invalidation issues, email spoofing/SPF/DMARC
- Blind SSRF w/o business impact, host header w/o impact
- Subdomain takeover w/o actual takeover, file upload w/o proof
- API key disclosure w/o proven business impact
- DoS/DDoS/brute force, spam/social engineering, theoretical issues
- UUID-based IDORs = LOW severity (unless enumerable/leakable UUIDs)

## Severity guide (their examples)
- Exceptional: RCE on prod, full DB access
- Critical: SQLi, all-customer PII, numeric IDOR mass read/write
- High: random users' PII, stored XSS, vertical auth bypass
- Medium: DOM/reflected XSS, IDOR non-critical data, lateral auth bypass
- Low: open redirect, UUID IDOR, reflected XSS w/ interaction

## Notes
- Sites share codebase with other DPG products (AD, De Morgen,
  De Volkskrant, Het Parool, Humo, Libelle) — cross-site bugs = DUPLICATE
- No test credentials provided — test as regular user
- CPDoS on cached content may be scored AC:High

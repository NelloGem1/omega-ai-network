# Monzo Bank — Rules of Engagement
Source: Intigriti program page, captured 2026-11-26
STATUS: ✅ OPEN — accepting submissions
URL: https://app.intigriti.com/researcher/program-redirect/monzobank/monzopublicbugbountyprogram

## Bounty tiers
- Tier 1 (*.monzo.com, *.prod-ffs.io): Low £200 / Med £1,500 / High £4,500 / Crit £8,250 / Exc £12,500
- Tier 2 (iOS 1052238659, Android co.uk.getmondo): Low £125 / Med £950 / High £3,750 / Crit £6,500 / Exc £10,000
- Tier 3 (www.monzo.com, monzo.com): Low £50 / Med £125 / High £325 / Crit £500 / Exc £850

## HARD RULES
- Max **2 requests/second** (STRICTEST we've seen — half of Trouw's limit)
- Required header: `X-Intigriti-Monzo-Username: nellogem`
- @intigriti.me email only
- **Evidence INLINE in report** — staff CANNOT download attachments (no screenshots/videos/files!)
- NEVER target other customers' accounts — own accounts only
- No refunds for test transactions — don't move real money carelessly
- Philippines NOT on restricted-countries list ✅
- ID check required

## In scope
- *.monzo.com (T1 wildcard — includes internal-api.monzo.com which is PUBLIC!)
- *.prod-ffs.io (T1 wildcard — fraud/features service?)
- iOS app 1052238659 (T2)
- Android co.uk.getmondo (T2)
- www.monzo.com, monzo.com (T3)

## OUT OF SCOPE
- */p2p/*, */contact-discovery/*, */inbound-p2p/*
- *.monzo.me, monzo.me, community.monzo.com, login.internal.monzo.com
- Third parties: Okta, Discourse, Mailgun, Adjust, Braze
- mnzpub* OAuth client secrets = PUBLIC BY DESIGN — never report
- Blind SSRF, self-XSS, request smuggling w/o impact, host header w/o impact
- Username/email enumeration, CORS misconfig, missing headers/cookies
- Clickjacking, CSV injection, session invalidation, email bombing
- Rate-limit bypass/absence, brute force, DoS/DDoS
- Mobile: no root detection, no cert pinning, binary path disclosure

## Key intelligence
- internal-api.monzo.com is the main API (used by mobile+web apps) — PUBLIC
- OAuth2 bearer tokens; public clients have secrets starting mnzpub
- Check if OAuth client is public: GET /oauth2/clients/{id} → "confidential": false
- Validation SLA: Exc/Crit 15wd, High 17wd, Med/Low 20wd — late = €25 bonus
- "Check our fix" — €50 bonus for verifying resolved issues
- 701 submissions total, avg payout £441
- No credentials provided — use own Monzo account (UK residency normally required!)

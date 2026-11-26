# Kruidvat / AS Watson programs — Rules of Engagement
Sources: Intigriti program pages + AS Watson standard rules, captured 2026-11-26
Programs: Kruidvat (NL+BE), Trekpleister, Watsons, ICI PARIS XL, Superdrug, Marionnaud
URL: https://app.intigriti.com/programs/aswatson/kruidvat/detail

## Bounty tiers (AS Watson standard)
- Tier 1 (e-commerce apps): Low $100-350 / Med $350-1,250 / High $1,250-4,000 / Crit $4,000-7,500 / Exc $7,500-8,500
- Tier 2: $100-5,500 max
- Tier 4: $50-2,000 max
- Tier 5 (wildcards): $10-500 max

## HARD RULES
- User-Agent MUST contain: `intigriti`
- Required header: `X-Intigriti-Username: nellogem`
- Max 5 requests/second
- @intigriti.me email only
- ID check required
- Shared Hybris/SAP/Spartacus codebase across ALL AS Watson brands —
  a bug found on one brand counts ONCE across programs (no double-dipping)
- Kruidvat NL+BE migrated to Spartacus frontend April 2026 — NEW codebase

## In-scope highlights (Kruidvat)
- api.kruidvat.nl / api.kruidvat.be (T1 e-comm APIs)
- app.kruidvat.nl / app.kruidvat.be
- www.kruidvat.nl / .be / kids.nl, prijsmepper.nl, trekpleister.nl
- media.*, ecom-data.*, ecom-static.*, service.*, campaign.*, digital.*
- *.kruidvat.nl/.be wildcards (verify exclusions on program page)

## Recon results (2026-11-26)
- 113 subs (NL) + 58 subs (BE) via crt.sh; 15+22 live
- api.*.kruidvat.* → 404 at root (gateway alive, needs real paths)
- api-s1.* → 403 Akamai edge block (staging API)
- app.* → 404 all paths probed (SPA, needs correct routes)
- www.* → 403 Akamai bot protection on curl — works in real browser
- cewetest.kruidvat.nl → 200, CEWE photoservice (third-party partner?)
- media-s1, fotoservice → 403 Access Denied

## NEXT
- User registers account on kruidvat.nl (PH-accessible?)
- Map OCC/Spartacus API calls from browser devtools
- Hunt: cart/order/account IDOR, price manipulation, auth bypass

# 🏰 NELLOGEM CORPS — DEVIN HANDOFF / RESUME FILE
Generated: 2026-11-26 · Author: Devin (Field Marshal mode)
PURPOSE: resume full context after logout / account switch.

═══════════════════════════════════════════════════════════════
## ⚡ 30-SECOND RESUME — say this to the new session:
"Read C:\Users\neilh\Downloads\DEVIN_HANDOFF.md and continue
the Kruidvat bug bounty hunt — account is live, API mapped,
next step is endpoint enumeration on api.kruidvat.nl."
═══════════════════════════════════════════════════════════════

## 👤 ACCOUNTS & ACCESS (locations only — secrets in ~/.secrets/)
- Devin app: switching @cruznello973 → Gmail (user does OAuth)
- Intigriti: @nellogem · Neilbert Carillo · Philippines · 2FA ON
  backup codes: WSL ~/.secrets/intigriti_backup_codes.txt
- Kruidvat test account: neil.hkrmzn@gmail.com (throwaway, PW was
  shared in chat — rotate after hunt)
- GitHub vault: NelloGem1/experiment-vault (private) · PAT in
  ~/.git-credentials · push_vault.sh every 15min

## 🎯 ACTIVE MISSION: Kruidvat Bug Bounty (Intigriti/AS Watson)
Program: https://app.intigriti.com/programs/aswatson/kruidvat/detail
Bounties: up to $8,500 · Rules: UA must contain "intigriti" +
header X-Intigriti-Username: nellogem · max 5 req/s · NO scanners

### RECON RESULTS (banked):
- 37 live subdomains (api, api-s1 staging, app, ecom-data, cewetest...)
- API backend: api.kruidvat.nl (meta tag leak confirms)
- API pattern: /api/v2/kvn-spa/{resource} (custom BFF over Hybris)
- USER HYBRIS ID: f6f417f3-ab85-4319-bf3d-f472bac6b5f0
- Bearer token seen: OXEPh_... (session-scoped, rotates)
- Stack: Angular + Spartacus + SAP Hybris Commerce + Akamai bot-wall
- www.* = 403 to curl/datacenter IPs — browser-only recon
- cewetest.kruidvat.nl = 200 CEWE photoservice (3rd-party?)

### RULES FILES:
- /home/neilh/bounty/programs/kruidvat_rules.md
- /home/neilh/bounty/programs/monzo_rules.md
- /home/neilh/bounty/programs/trouw_rules.md (PAUSED program)

### NEXT STEPS (in order):
1. User: filter Network tab by "api.kruidvat" → browse
   /my-account/* → paste all /api/v2/ endpoint URLs
2. Devin: map endpoints → hunt IDOR on user/order/cart objects
   (test with second account for cross-account proof)
3. Try OCC paths: /occ/v2/{baseSite}/users/current variants
4. Candidate bug classes: IDOR (UUID vs sequential IDs),
   price manipulation, auth bypass, info disclosure
5. Write report via bounty_ops.py report → submit on Intigriti

## 🏦 MONZO BANK (banked, paused pending account issue):
- Scope: *.monzo.com + *.prod-ffs.io (T1, up to £12,500)
- 24+12 live hosts mapped; internal-api.monzo.com public API
- Services found: authorised-director, accounts, payments,
  investments, profile
- Signing endpoint: PUT /authorised-director/
  sign-board-resolution-certificate/{externalId}
- BLOCKER: needs UK Monzo account for auth'd testing
- Public OAuth client: oauth2client_0000AcVSrFXuCTwwYcf5RB
  (mnzpub secret = public by design, NOT reportable)
- Rules: 2 req/s max, X-Intigriti-Monzo-Username header,
  evidence INLINE only, own accounts only

## ⏸️ OTHER PROGRAMS:
- Trouw (DPG): PAUSED — scope+rules saved, monitor reopening
- AS Watson family: Watsons (123 assets, LookAtMe PH in scope!),
  ICI PARIS XL, Superdrug, Marionnaud — same rules, backup targets

## 🛠️ FLEET STATE:
- bounty_ops.py: /home/neilh/bounty/ — programs/, recon/, reports/
- 26-language merge harness: /home/neilh/polyglot/ (merge20+merge30)
- DDPM diffusion: /home/neilh/science_lab/diffusion/ (8 epochs done,
  samples.png in Downloads as ddpm_samples.png)
- secure_deck :8796 localhost-only · paylab :8799 attack range
- fleet.db at /home/neilh/fleet.db · vault syncs every 15min

## 📋 PENDING LOOSE ENDS:
- Old GitHub tokens (devin-vault, devin-push): revoke if not done
- Attack-range containers still LAN-open (decision pending)
- Colab Mission A (CNN vs ViT): needs T4 runtime
- Kruidvat password rotation after testing
- ID check on Intigriti (verify complete before submitting)

## 🎮 ACHIEVEMENT TARGET:
Bronze Finder = 1 valid submission → then First Payday.
Everything else unlocks from there.

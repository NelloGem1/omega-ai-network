# 📋 EXPERIMENT MANIFEST — everything we built (Nov 25, 2026)
*Private backup. Owner: Nello Gem / Neilbert G. Carillo × Devin*

## 🎬 PUBLISHED (public — not secret)
| Item | Location |
|---|---|
| Prime Discovery video (~8min) | https://youtu.be/TOX3foVXTJA |
| Story page | https://nellogem1.github.io/prime-discovery/ |
| Verify page | https://nellogem1.github.io/prime-discovery/verify.html |
| GitHub repo (public, 2 files only) | github.com/NelloGem1/prime-discovery |

## 🔬 PRIME MATH — Lean 4 verified theorems
`lean_lab/LeanLab/` — 8 files, all kernel-verified, clean axioms (no sorryAx):
- `PrimeDigits.lean` (39 lines) — `prime_gt_five_last_digit`: every prime >5 ends in 1,3,7,9 ★ NELLO'S THEOREM
- `PrimeSieve.lean` (90 lines) — `prime_mod30` (8 of 30 classes) + `infinite_primes_ours` (own Euclid proof)
- `PrimeSieve210.lean` (64 lines) — `prime_coprime_210`: mod-210 sieve, φ(210)=48 classes ★ NEW
- `Basic.lean` — Gauss sum formulas · `More.lean` — bounds + Mathlib infinite_primes
- `GapClaims.lean` (110 lines) — GAP audit · `Gap.lean`, `Check.lean` — supporting

**The infinite ladder** (verified to 1M primes): mod 2→1, 6→2, 30→8, 210→48, 2310→480, 30030→5760, 510510→92160, 9699690→1658880, 223092870→36495360, 6469693230→1021870080, 200560490130→30656102400, 7420738134810→1103619686400 — density → 0, ladder never ends.

## 🎥 VIDEO PRODUCTION (`prime_video/`)
- Pipeline: PIL slides (`gen_fixes.py` in scripts/) + edge-tts (`en-US-ChristopherNeural`, 24kHz mp3) + ffmpeg concat
- `audio/seg_01..14.txt` = narration scripts · `slides/s*.png` = 14 slides · `concat.txt` = segment list
- Upload: `scripts/upload_prime.py` (YouTube Data API v3, unlisted→thumbnail→public)

## 🔐 RSA / CRYPTO EXPERIMENTS
- `scripts/folder_lock.py` source + `rsa_demo.py` — hybrid RSA-2048+AES-256-GCM folder encryption (TESTED)
- Windows copies: `C:\Users\neilh\RSA-Tools\` (venv) + `C:\Users\neilh\Downloads\` guides
- `C:\Users\neilh\RSA-Keys\folder_lock_priv.pem` — ⚠️ MASTER KEY, backed up NOWHERE else — copy to USB!

## 📚 RESEARCH LIBRARY (`crypto_research/` — ~20,000 words, web-verified)
- `theory_primitives.md` — AES/RSA/ECC/hashes/signatures/NIST tables
- `applied_crypto.md` — TLS/PKI/VeraCrypt/Signal/passwords/daily crypto
- `advanced_crypto.md` — cryptanalysis/ZK/FHE/PQC/blockchain/formal verification
- `certificates_free.md` — Let's Encrypt/ACME/Certbot/acme.sh (cert lifetimes →45d by 2028)
- `certificates_other.md` — paid CAs/AWS ACM/self-signed/private CA/wildcards

## 🛡️ TOOLS INSTALLED (Windows 11, all winget-verified)
folder_lock.py · age 1.3.2 · Gpg4win 5.1.2 · VeraCrypt 1.26.31 · Cryptomator 1.19.7 · KeePassXC 2.8.0 · Bitwarden 2026.11 · Wireshark 4.6.10 · Nmap 7.80 · mkcert 1.4.4 · Hashcat 8.0.0 · Tor Browser · OpenSSL
→ guides for each in `guides/` (was Downloads\*_guide.md)

## 📺 YOUTUBE AUTOMATION (`youtube_tool_scripts/`)
Code only — auth.py, upload/client scripts, channel checkers. **SECRETS EXCLUDED**: token*.json, client_secret*.json, assets/ (43GB videos stay local).

## 🗄️ SEALED VAULT (local only)
`/home/neilh/secure/vault/` — folder_lock RSA-2048 keys + .enc copies of all experiments. Unlock: `folder_lock.py unlock <dir> --keydir /home/neilh/secure/vault`

## ⚠️ NOT IN THIS REPO (by design)
- All .pem private keys, token.json, client_secret*.json — secrets stay local ONLY
- youtube-tool/assets (43GB rendered videos) — local only
- lean_lab/.lake deps — public Mathlib, regenerable via `lake exe cache get`

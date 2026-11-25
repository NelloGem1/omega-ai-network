# 🌐 WebSec Mission — Complete Archive

Everything from the cybersecurity learning mission, in order.

## 📖 01-research/ — Learn first
| File | What |
|---|---|
| learning_path.md | 12-week roadmap + resource map |
| payment_bypass.md | All 8 subscription-bypass vuln classes + fixes |
| attacker_methodology.md | How real hackers hunt (recon → exploit → report) |
| defender_playbook.md | Secure Flask code + regression tests |
| advanced_web_vulns.md | Smuggling, SSTI, OAuth, LLM security |
| flask_security_deep.md | Flask/Python-specific attacks + defenses |
| race_and_logic.md | Race conditions, Turbo Intruder, business logic |
| cheatsheets_index.md | Which reference file for which vuln |
| cli_toolkit.md | All 18 CLI tools + usage |
| docker_setup.md | Docker/WSL lab runbook |

## ⚔️ 02-battle-reports/ — The fights (chronological)
| File | Result |
|---|---|
| exploits.md | 🔴 Round 1: 7 payment-bypass exploits PROVEN |
| AUDIT_REPORT.md | 🛡️ Round 1 defense: 9 vulns → fixed → 18 tests |
| juice_solves.md | 🍹 Juice Shop: 22 challenges solved |
| exploits_round2.md | 🔴 Round 2: break-the-fixes → **0 bypasses survived** |
| DEFENSE_ROUND2.md | 🏆 Round 2 defense: 14 hardening items → 39/39 tests |
| crypto_challenges.md | 🔐 Crypto: RSA factoring, hashcat, ECB, GCM nonce reuse |

## 🧪 03-lab/ — The apps + attack scripts
- `app/` — hardened Flask subscription app (`app.py`), vulnerable original (`app_vulnerable.py`), schema, tests (39 passing)
- `docker-compose.yml` — Juice Shop + DVWA + WebGoat stack
- `CHALLENGES.md` / `SETUP.md` — curriculum + run instructions
- `jssolve.py`, `solve_all.py`–`solve4.py` — Juice Shop solve scripts
- `attack2.py`, `attack3.py` + result logs — round-2 attack scripts
- `challenge*.py` — crypto challenge scripts
- hash/wordlist files — hashcat practice data

## 🛠️ 04-tools-data/
Reference data for the arsenal (see `TOOLS.md` at repo root for the full manifest).

---
*Private experiment vault — NelloGem · synced live from local lab*

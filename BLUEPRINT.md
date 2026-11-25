# ⬡ BLUEPRINT — NelloGem Grand Doctrine v1.0
*The master plan every agent inherits. Read this first.*

## 🎯 MISSION
Preserve, connect, verify, and teach ALL human knowledge — science, math, security, humanity's experience — in one self-healing, self-backing-up, searchable archive. Learn by DOING: build → measure → break → document → fix → regression-test.

## 🧬 THE FORMULA (design law — see DESIGN.md)
- Palette: `#0d1117` bg · `#161b22` panel · `#f0b429` gold · `#58a6ff` blue · `#3fb950` green · `#f85149` red
- Motif: primes >5 end in **1·3·7·9** · primorial ladder ordering (2·6·30·210·2310·30030·510510)
- Every page: ⬡ PRIME nav + INDEX link + numbered footer
- Self-contained HTML, offline-safe, mobile-friendly

## 📚 KNOWLEDGE HIERARCHY (the archive schema)
```
Domain → Discipline → Subdiscipline → Field → Concept →
Principle → Method → Experiment → Evidence → Application → Outcome
```
Every claim tagged: `verified` / `proof` / `theory` / `observation` / `opinion` / `experience` / `hypothesis` / `unverified` / `speculation`

## ⚔️ CREATE-AND-DESTROY METHODOLOGY (experiments)
1. State hypothesis → 2. BUILD toy system → 3. MEASURE (data tables/plots) →
4. ATTANGE/BREAK it → 5. Record what broke → 6. Document lesson →
7. FAILED experiments are knowledge too — preserve them.

## 🏰 VAULT RULES (GitHub = source of truth)
- Repo: `github.com/NelloGem1/experiment-vault` (PRIVATE)
- Auto-sync: `/home/neilh/sync_vault.sh` every 15 min via cron
- Layout: `science/{research,lab}` · `websec/{01-research,02-battle-reports,03-lab}` · `learning-library/` · `design/` · `crypto_research/` · `lean_lab/` · `prime_video/`
- NEVER commit secrets (tokens, .pem, keys) — see DATA_SOURCES.md
- Anything >100MB or public → document restore command in DATA_SOURCES.md instead of blob

## 🛠️ ARSENAL (see TOOLS.md for full manifest)
- WSL CLI: sqlmap ffuf nuclei httpx jwt_tool nikto gobuster dirsearch whatweb searchsploit feroxbuster subfinder
- Data: SecLists 2.5GB · PayloadsAllTheThings · HackTricks · CheatSheetSeries · exploitdb · nuclei-templates
- Labs: Juice Shop :3000 · DVWA :4280 · WebGoat :18080 · SubLab :5000 · Burp :8080
- Python: /home/neilh/venv (numpy scipy pandas sklearn sympy networkx + science stack installing)
- Lean 4: /home/neilh/.elan/bin/lake (theorem proofs in lean_lab/)
- NEED.md: append `NEED: <pkg>` if you need an install — butler fulfills

## 👥 AGENT ROSTER (17 generals)
| Role | Count | Output |
|---|---|---|
| Research maps | 8 | science_research/*.md (600-1200 lines each) |
| Experiment agents | 8 | science_lab/<field>/ (scripts+data+REPORT.md) |
| Tool butler | 1 | installs + NEED.md protocol |

## 📏 STANDARDS
- Markdown reports: Sources section, verified facts, honest gaps
- Experiments: reproducible scripts, real measured data, no hand-waving
- HTML: Prime Formula chrome, numbered docs in Downloads\Learning
- Judge work by EVIDENCE (logs, tests, data) not claims

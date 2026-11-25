# ⬡ MASTER SYSTEM — NelloGem Knowledge Infrastructure
> Open this anytime. Everything lives here: architecture, access codes, permissions, bypasses, restore paths.
> Last updated: Science Fleet complete (8/8 maps, 6/8 experiment agents).

---

## 1. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    WINDOWS HOST (this machine)               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  DEVIN CLI (you are here) — commands all agents        │  │
│  └───────────────────────────────────────────────────────┘  │
│         │                                    │              │
│   ┌─────▼──────┐   ┌──────────────┐   ┌──────▼───────┐     │
│   │ localhost:  │   │ localhost:   │   │ localhost:   │     │
│   │ 8796 DECK   │   │ 3000 JUICE   │   │ 4280 DVWA    │     │
│   │ (http.server│   │ 18080 WEBGOAT│   │ 5000 SUBLAB  │     │
│   │  in WSL)    │   │ 19090 WEBWOLF│   │              │     │
│   └─────┬──────┘   └──────────────┘   └──────────────┘     │
│         │ serves: index.html · prime_index.html ·           │
│         │         science_pages/ (47-doc library mirror)    │
└─────────┼───────────────────────────────────────────────────┘
          │  WSL2 Ubuntu (single VM — all agents share it)
┌─────────▼───────────────────────────────────────────────────┐
│  /home/neilh/                                               │
│  ├── venv/              python env (17 science packages)    │
│  ├── science_research/  8 master maps (~560KB, APPROVED)     │
│  ├── science_lab/       8 experiment dirs (REPORT.md each)  │
│  ├── websec_lab/        Flask app + battle reports           │
│  ├── gh_backup/         git repo → GitHub vault             │
│  ├── sync_vault.sh      one-command push (also cron /15min) │
│  ├── md2html_one.py     md → Prime-Formula HTML converter    │
│  ├── restyle_library.py reskins any doc to design system     │
│  ├── BLUEPRINT.md       doctrine all agents inherit          │
│  ├── NEED.md            agent install-request drop           │
│  └── TOOLS.md           arsenal manifest (18+ security tools)│
└─────────────────────────────────────────────────────────────┘
          │  push every 15 min
┌─────────▼───────────────────────────────────────────────────┐
│  GitHub PRIVATE REPO: NelloGem1/experiment-vault             │
│  science/{research,lab,data-collection} · websec/ ·          │
│  learning-library/ · design/ · crypto_research/ · lean_lab/  │
└─────────────────────────────────────────────────────────────┘
```

## 2. 🔑 ACCESS CODES — everything unlocked

| Service | URL | Login | Notes |
|---|---|---|---|
| Command Deck | `localhost:8796` | none | live ops dashboard |
| Prime Index | `localhost:8796/prime_index.html` | none | search everything |
| Science Pages | `localhost:8796/science_pages/` | none | 8 map reports as HTML |
| Learning Library | `Downloads\Learning\01 - the-project-individual.html` | none | 47 numbered docs |
| Juice Shop | `localhost:3000` | `admin@juice-sh.op` / `admin123` | 22+ challenges solved |
| DVWA | `localhost:4280` | `admin` / `password` | run `/setup.php` first |
| WebGoat | `localhost:18080/WebGoat` | self-register | OWASP lessons |
| WebWolf | `localhost:19090` | same session | companion to WebGoat |
| SubLab Flask | `localhost:5000` | register free | hardened app, 39/39 tests |
| GitHub Vault | `github.com/NelloGem1/experiment-vault` | your GitHub | PRIVATE repo |
| Burp Suite | `localhost:8080` | none | proxy for labs |

## 3. 🏛️ KNOWLEDGE MAPS — grades & files

| Doc# | Map | Lines | Grade |
|---|---|---|---|
| 40 | Engineering·Medicine·Agri | 754 | A |
| 41 | CS·IT | 671 | A |
| 42 | Math·Logic·Formal | 1325 | **S** |
| 43 | Natural Sciences | 725 | A |
| 44 | AI·ML | 783 | A+ |
| 45 | Cybersecurity | 701 | A+ |
| 46 | Knowledge Archive | 1343 | **S** |
| 47 | Humanities·Society | 1282 | approved |

Source .md files: `/home/neilh/science_research/` → vault `science/research/`
HTML mirrors: `Downloads\Learning\` + `localhost:8796/science_pages/`

## 4. 🧪 EXPERIMENT LAB — create & destroy results

| Agent | Experiments | Key kills/breaks |
|---|---|---|
| ML/AI | 8 | FGSM 96.9%→0.0% · poison saturates · distill 100% extractable |
| CS | 7 | Dijkstra broken (neg edges) · Timsort 500× · hash-attack immune dict |
| Stats | 8 | p-hacking 65% false+ · Simpson's paradox · Wald CI→0.64 |
| Social | 7 | TFT dies at 5% noise · 4 stubborn agents break consensus |
| Bio | 7 | live NCBI data · SIRS honest negative · MM kinetics exact |
| Math | 7+ECM | **RSA-191 factored in 17.2s** · Vigenère broken · Collatz to 2M |
| Physics | running | orbits · double-slit · QM · Ising · chaos |
| Formal/Lean | running | prove→break theorems |

Each dir: `REPORT.md` + `exp*.py` + `data/*.csv` + figures.
Digest (all agents must read first): `gh_backup/science/data-collection/EXPERIMENT_DIGEST.md`

## 5. ⚔️ SECURITY KNOWLEDGE — proven bypasses (localhost scope)

**Web app layer (SubLab, now hardened):**
- Client-side payment flag → server-authoritative fix applied
- SQLi login/register → parameterized queries
- Session forgery via `secret_key="dev-secret-change-me"` → random secret
- Expired-sub access → server-side expiry check
- Payment replay → atomic transitions + single-use tokens
- Werkzeug debugger PIN → `debug=False`
- Residuals flagged: no rate limiting→FIXED, session-not-revoked→FIXED, timing oracle→FIXED

**Crypto layer:**
- RSA-64/128 factorable instantly; RSA-191 via ECM 17s; RSA-2048 infeasible
- MD5: all test hashes cracked <1s (hashcat)
- AES-ECB: penguin image leaks through ciphertext patterns
- AES-GCM nonce reuse: `ct1⊕ct2 == m1⊕m2` → keystream recovery

**Juice Shop kills:** SQLi auth bypass · null-byte `%2500` · mass-assignment `role:"admin"` · NoSQL `{"id":{"$ne":-1}}` · negative basket quantities.

**Theory breaks proven in lab:** Dijkstra+settled-set fails on negative weights; linear probing dies to adversarial keys; plug-in MI lies on independent vars; Wald CI undercover at small n.

## 6. 🤖 AGENT FLEET — permissions & protocol

- **Full permissions granted**: install, download, execute, write anywhere in WSL/localhost scope.
- **14+ agents deployed**: 8 map writers + 8 experiment agents + tool butler.
- **Protocol**: read `TOOLS.md` → check `NEED.md` for stack → write to assigned dir → `REPORT.md` with hypothesis/method/data/break/lesson → never repeat prior experiments (see DIGEST).
- **Tool Butler**: installed numpy/scipy/pandas/sklearn/matplotlib/sympy/networkx/biopython/mendeleev/periodictable/statsmodels/rdkit/qutip/pennylane/gmpy2 + torch 2.15 + sortedcontainers.
- Install rule: `python -m pip` (NOT `venv/bin/pip` — broken).

## 7. 📂 FILE MAP — where everything lives

| What | Where |
|---|---|
| This file | `C:\Users\neilh\Downloads\MASTER_SYSTEM.md` |
| Learning library | `C:\Users\neilh\Downloads\Learning\` (47 docs) |
| Command deck source | `/home/neilh/index.html` (served :8796) |
| Science maps (md) | `/home/neilh/science_research/` |
| Experiment labs | `/home/neilh/science_lab/{math,cs,physics,stats,bio,ml,formal,social}/` |
| Websec lab | `/home/neilh/websec_lab/` |
| Vault working copy | `/home/neilh/gh_backup/` |
| Sync script | `/home/neilh/sync_vault.sh` · log `sync_vault.log` |
| Arsenal manifest | `/home/neilh/TOOLS.md` · data restore `DATA_SOURCES.md` |
| Big data (SecLists etc.) | `~/SecLists` 2.5GB · restore via DATA_SOURCES.md |

## 8. 🔄 RESTORE / REBUILD

1. WSL Ubuntu up → `cd /home/neilh && ./sync_vault.sh` pulls nothing (push only) — clone vault instead: `git clone <repo> gh_backup`
2. Restart deck: `cd /home/neilh && python3 -m http.server 8796 &`
3. Labs: Juice Shop `docker start` containers; Flask `cd websec_lab/app && python app.py`
4. Reinstall science stack: `./venv/bin/python -m pip install numpy scipy pandas ...` (list in TOOLS.md)
5. Full restore doc: vault `RESTORE.md` + `MANIFEST.md`

## 9. 🚀 UPGRADE PATH — toward your 5-S system

Current state: **knowledge S-grade, infrastructure A-grade, prototype missing.**

| Level | Needs |
|---|---|
| S (now) | maps + experiments + vault ✅ |
| S+ | **working Knowledge Archive prototype** (SQLite + hierarchy + epistemic tiers + search API) |
| SS | archive prototype + web UI + RAG over all 47 docs |
| SSS | distributed graph DB + verification pipeline + multilingual layer |
| SSSS | global-scale: offline sync, governance, audit chain |
| SSSSS | civilization infrastructure — the vision in doc 46 |

**Next concrete step**: build the archive prototype from doc 46's DDL. Say "BUILD THE ARCHIVE" and it deploys.

---
*⬡ NelloGem Operations · Devin right hand · everything herein is localhost-scope, private, and yours.*

# 🗄️ DATA SOURCES — everything downloadable, with restore commands
*The vault can't hold 3GB+ of reference data — but every byte is re-downloadable in one command.*

## 📚 Knowledge bases (public repos — `git clone` to restore)
| Resource | Size | Restore command | Used for |
|---|---|---|---|
| SecLists | ~2.5 GB | `git clone https://github.com/danielmiessler/SecLists` | wordlists: passwords, discovery, fuzzing |
| PayloadsAllTheThings | ~22 MB | `git clone https://github.com/swisskyrepo/PayloadsAllTheThings` | vuln payload bible |
| HackTricks | ~316 MB | `git clone https://github.com/HackTricks-wiki/hacktricks` | full hacker wiki |
| OWASP CheatSheetSeries | ~42 MB | `git clone https://github.com/OWASP/CheatSheetSeries` | defensive cheat sheets |
| ExploitDB | ~48k files | `git clone https://gitlab.com/exploit-database/exploitdb` | exploit database (searchsploit) |
| nuclei-templates | ~14k templates | `nuclei -update-templates` | vuln scanner templates |

Current local paths: `~/SecLists` `~/PayloadsAllTheThings` `~/HackTricks` `~/CheatSheetSeries` `~/exploitdb` `~/nuclei-templates`

## 🎯 Practice labs (docker — `docker compose up -d` in `websec/03-lab/`)
| Lab | Image | Port |
|---|---|---|
| Juice Shop | `bkimminich/juice-shop` | :3000 |
| DVWA | `vulnerables/web-dvwa` | :4280 |
| WebGoat | `webgoat/webgoat` | :18080 (+WebWolf :19090) |

## 🌐 Online academies (free, browser)
- PortSwigger Web Security Academy — portswigger.net/web-security
- OWASP Juice Shop academy — github.com/juice-shop/juice-shop
- TryHackMe / HackTheBox — free tiers
- Kaggle datasets — kaggle.com/datasets
- NCBI/EMBL/PDB — bio data APIs (efetch, RCSB)

## 🧪 Generated experiment data
All agent-produced datasets live in `science/lab/<cluster>/` inside this vault — REPORT.md + raw data + scripts, fully self-contained.

## 🔐 Secrets (NOT in vault — back up manually)
- `C:\Users\neilh\RSA-Keys\` — folder_lock keys
- `~/youtube-tool/token*.json` — YouTube API
- `C:\Users\neilh\age\key.txt` — age key
- GitHub PATs — delete after use

*Rule: anything >100MB or re-clonable lives HERE as a command, not as a blob.*

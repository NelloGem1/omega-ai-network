# 🧰 MASTER TOOLS MANIFEST — everything installed, where it lives
*Read this first, agent. All tools verified working Nov 25, 2026.*

## 🪟 WINDOWS GUI TOOLS
| Tool | Path | Use |
|---|---|---|
| Burp Suite Community 2026.3.3 | `C:\Users\neilh\AppData\Local\Programs\BurpSuiteCommunity\BurpSuiteCommunity.exe` | Proxy/intercept — port 8080 |
| OWASP ZAP 2.17.0 | `C:\Program Files\ZAP\Zed Attack Proxy\ZAP.exe` | Automated scanner — change port if Burp running |
| VeraCrypt 1.26.31 | `C:\Program Files\VeraCrypt\VeraCrypt.exe` | Disk/container encryption |
| Cryptomator 1.19.7 | `C:\Program Files\Cryptomator\Cryptomator.exe` | Cloud folder vaults |
| KeePassXC 2.8.0 | `C:\Program Files\KeePassXC\KeePassXC.exe` | Password vault |
| Bitwarden 2026.11 | Start Menu | Cloud password manager |
| Wireshark 4.6.10 | Start Menu / `C:\Program Files\Wireshark\` | Packet capture (tshark.exe CLI too) |
| Nmap 7.80 | `C:\Program Files\Nmap\` | Network scanner |
| Tor Browser | Start Menu | Anonymous browsing |
| Hashcat 8.0.0 | `C:\Users\neilh\hashcat\hashcat.exe` | Password-hash auditing |
| mkcert 1.4.4 | PATH (`mkcert`) | Local dev certificates |
| age 1.3.2 | PATH (`age`, `age-keygen`) | Modern file encryption |
| Gpg4win 5.1.2 | `C:\Program Files\GnuPG\bin\gpg.exe` + Kleopatra | OpenPGP encryption |
| OpenSSL | `C:\Program Files\Git\usr\bin\openssl.exe` | Cert inspection/crypto |

## 🐧 WSL CLI ARSENAL (Ubuntu, user neilh)
| Tool | Path/Command | Use |
|---|---|---|
| sqlmap 1.10.4 | `sqlmap` | SQL injection |
| ffuf 2.3.0 | `ffuf` | Web fuzzer |
| nuclei 3.11.1 | `nuclei` (+`~/nuclei-templates`, 14k templates) | Vuln scanner |
| httpx 1.12.0 | `httpx` | HTTP probe |
| jwt_tool | `/home/neilh/venv/bin/python ~/jwt_tool/jwt_tool.py` | JWT attacks |
| curl 8.18 | `curl` | HTTP client |
| nikto 2.1.5 | `~/bin/nikto` (export PATH=$HOME/bin:$PATH) | Web server scanner |
| gobuster 3.8.2 | `~/bin/gobuster` | Dir/DNS brute-forcer |
| dirsearch | `~/bin/dirsearch` | Web path scanner |
| whatweb 0.6.3 | `~/bin/whatweb` | Tech fingerprinting |
| searchsploit | `~/bin/searchsploit` (db: ~/exploitdb) | Exploit database search |
| feroxbuster 2.14.0 | `~/bin/feroxbuster` | Fast recursive scanner |
| subfinder 2.17.0 | `~/bin/subfinder` | Subdomain discovery |
| python3 + venv | `/home/neilh/venv/bin/python` | scripting (has flask?, sympy, cryptography, markdown) |
| pip | `/home/neilh/venv/bin/pip` | install python pkgs |
| Lean 4 + lake | `/home/neilh/.elan/bin/lake` | theorem proving |

## 📚 DATA LIBRARIES (WSL ~)
| Resource | Path | Contents |
|---|---|---|
| SecLists | `~/SecLists` (2.5GB) | wordlists: Passwords/, Discovery/, Fuzzing/ |
| PayloadsAllTheThings | `~/PayloadsAllTheThings` | vuln payload bible |
| HackTricks | `~/HackTricks/src/` | full hacker wiki source |
| CheatSheetSeries | `~/CheatSheetSeries` | OWASP defensive sheets |
| websec_research/ | `~/websec_research/*.md` | 7 research reports |
| crypto_research/ | sealed (.enc) + gh_backup plaintext | 5 crypto reports |

## 🎯 LAB TARGETS
| App | URL | Status |
|---|---|---|
| Juice Shop | http://localhost:3000 | agent installing |
| DVWA | TBD :4280 | agent installing |
| WebGoat | TBD :8080 | agent installing |
| Flask subscription app | http://localhost:5000 (`/home/neilh/websec_lab/app/`) | has # VULN: targets |
| PortSwigger Academy | portswigger.net/web-security | free online labs |

## 🎨 DESIGN SYSTEM (MANDATORY for all HTML/UI work)
- **Read `/home/neilh/DESIGN.md` FIRST** — the Prime Formula v1.0 spec
- Canonical command center: `00 - PRIME INDEX.html` (variant B = art alternate)
- Palette: bg #0d1117 · panel #161b22 · gold #f0b429 · blue #58a6ff · green #3fb950 · red #f85149
- Every page: ⬡ PRIME nav + 1·3·7·9 motif + back-to-index footer
- Learning library: `C:\Users\neilh\Downloads\Learning\` (38 numbered docs)

## 🔐 SECRETS (local only — NEVER commit)
- `C:\Users\neilh\RSA-Keys\folder_lock_priv.pem` — vault master key
- `~/youtube-tool/token*.json`, `client_secret*.json` — YouTube API
- `~/secure/vault/` — encrypted experiment archive
- `C:\Users\neilh\age\key.txt` — age key

## 📋 RULES FOR AGENTS
- sudo: use `wsl -d Ubuntu -u root` for root ops (neilh sudo needs password)
- Permissions: FULL — install, download, execute freely
- Scope: localhost/lab targets ONLY for attacks; never external sites
- jwt_tool needs venv python; nuclei templates at ~/nuclei-templates

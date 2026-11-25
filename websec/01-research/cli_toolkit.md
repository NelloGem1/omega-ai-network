# Web Security CLI Toolkit — WSL Ubuntu

Toolkit for learning ethical web hacking, installed & verified on WSL2 (Ubuntu).

## Installed Tools

### 1. sqlmap — SQL Injection tester
- **Path:** `/usr/bin/sqlmap` (apt package, v1.10.4)
- **Verify:** `sqlmap --version` → `1.10.4#stable`
- **What it does:** Automated detection & exploitation of SQL injection flaws.
- **Beginner example (against a local DVWA/own lab):**
  ```bash
  sqlmap -u 'http://localhost:8080/vulnerabilities/sqli/?id=1&Submit=Submit'
  ```

### 2. ffuf — Fast web fuzzer
- **Path:** `/usr/local/bin/ffuf` (release binary v2.3.0)
- **Verify:** `ffuf -V` → `ffuf version: 2.3.0`
- **What it does:** Discovers hidden directories/files/parameters via wordlists.
- **Beginner example:**
  ```bash
  ffuf -w ~/SecLists/Discovery/Web-Content/common.txt -u http://localhost:8080/FUZZ
  ```

### 3. nuclei — Vulnerability scanner
- **Path:** `/usr/local/bin/nuclei` (release binary v3.11.1)
- **Verify:** `nuclei -version` → `Nuclei Engine Version: v3.11.1`
- **Templates:** `~/nuclei-templates` (14,225 YAML templates, updated)
- **What it does:** Template-based scanner for known CVEs/misconfigs/tech detection.
- **Beginner example:**
  ```bash
  nuclei -u http://localhost:8080
  ```

### 4. SecLists — Wordlist collection
- **Path:** `~/SecLists` (git clone --depth 1, ~2.5 GB)
- **Verified dirs:** `Passwords/`, `Discovery/`, `Fuzzing/`, `Usernames/`, `Payloads/`, `Web-Shells/`
- **What it is:** The standard collection of wordlists for fuzzing/brute-forcing.
- **Key files:**
  - `Passwords/Common-Credentials/10-million-password-list-top-1000000.txt`
  - `Discovery/Web-Content/common.txt`, `raft-medium-directories.txt`
  - `Fuzzing/` (numbers, LFI, SSTI payloads, etc.)

### 5. jwt_tool — JWT attack toolkit
- **Path:** `~/jwt_tool/jwt_tool.py` (git clone)
- **Run with:** `/home/neilh/venv/bin/python ~/jwt_tool/jwt_tool.py`
- **Verify:** `-h` prints full usage (mode -M, exploit -X, target -t, etc.)
- **Deps:** installed into `~/venv` (`pip install -r requirements.txt`)
- **What it does:** Tests JWTs for alg=none, weak secrets, kid/jku/x5u injection, claim tampering.
- **Beginner example:**
  ```bash
  /home/neilh/venv/bin/python ~/jwt_tool/jwt_tool.py <JWT_TOKEN> -t http://localhost:8080/
  ```

### 6. httpx (ProjectDiscovery) + curl
- **httpx Path:** `/usr/local/bin/httpx` (v1.12.0) — fast HTTP probing/fingerprinting
- **Verify:** `httpx -version` → `Current Version: v1.12.0`
- **curl:** `/usr/bin/curl` v8.18.0 (preinstalled)
- **Examples:**
  ```bash
  httpx -u http://localhost:8080 -title -tech-detect
  curl -i http://localhost:8080/
  ```

## Notes
- `sudo` requires a password for the `neilh` user; root commands were run via `wsl -d Ubuntu -u root`.
- nuclei templates live at `~/nuclei-templates` (installed under user neilh).
- gf patterns (github.com/michenriksen/gf): skipped — install is `go install`, not essential; SecLists covers the core need.
- Legal reminder: only test targets you own or have written permission for (DVWA, Juice Shop, PortSwigger labs, HackTheBox, etc.).

## Extended toolkit

> Installed by setup agent. **Note:** `sudo` needs a password for `neilh`, but a passwordless root shell is available via `wsl -d Ubuntu -u root -- bash -c "..."`. Since apt was unavailable to user `neilh`, nikto/whatweb/exploitdb were installed **user-space** (deb extraction into `~/localroot`, git clones) rather than system-wide.

### 7. nikto 2.1.5 — web server scanner
- **Path:** `~/bin/nikto` (wrapper) → real binary `~/localroot/usr/bin/nikto`; config/db/plugins at `~/nikto_exec`
- **Verify:** `nikto -Version` → `Nikto main 2.1.5, LibWhisker 2.5`; `-list-plugins` lists all plugins
- **Usage:** `nikto -h http://target` (note: `-h` is *host*, `-Help` for help)
- **Deps:** perl + LibWhisker/JSON::PP/Net::SSLeay extracted to `~/localroot` (PERL5LIB set by wrapper)

### 8. gobuster 3.8.2 — dir/DNS brute-forcer
- **Path:** `~/bin/gobuster` (GitHub release binary, OJ/gobuster v3.8.2)
- **Verify:** `gobuster -h` → `VERSION: 3.8.2` (no `version` subcommand in v3)
- **Usage:** `gobuster dir -u http://target -w ~/SecLists/Discovery/Web-Content/common.txt`

### 9. dirsearch — python web path scanner
- **Path:** repo `~/dirsearch`, wrapper `~/bin/dirsearch` (uses `~/venv/bin/python`)
- **Verify:** `dirsearch -h` → usage/options printed
- **Deps added to venv:** defusedxml, colorama, PySocks, Jinja2, requests-ntlm, defusedcsv, requests-toolbelt, socksio, httpx-ntlm
- **Usage:** `dirsearch -u http://target -w ~/SecLists/Discovery/Web-Content/common.txt`

### 10. whatweb 0.6.3 — tech fingerprinting
- **Path:** `~/bin/whatweb` (wrapper) → ruby script in `~/localroot` (ruby 3.3.8 + gems extracted user-space)
- **Verify:** `whatweb --version` → `WhatWeb version 0.6.3`
- **Usage:** `whatweb http://target`

### 11. searchsploit / exploitdb — offline exploit archive
- **Path:** repo `~/exploitdb` (cloned from **gitlab.com**/exploit-database/exploitdb — the GitHub repo is now just a redirect stub!), wrapper `~/bin/searchsploit`
- **Verify:** `searchsploit -h` → usage; `searchsploit vsftpd` → finds EDB-ID 49757.py backdoor etc.
- **Update:** `cd ~/exploitdb && git pull`

### 12. feroxbuster 2.14.0 — fast content discovery (rust)
- **Path:** `~/bin/feroxbuster` (GitHub release binary, epi052/feroxbuster)
- **Verify:** `feroxbuster --version` → `feroxbuster 2.14.0`
- **Usage:** `feroxbuster -u http://target -w ~/SecLists/Discovery/Web-Content/common.txt`

### 13. Python security libs in ~/venv
- **Verify:** `~/venv/bin/python -c 'import requests, httpx, bs4'` → requests 2.34.2, httpx 0.28.1, bs4 4.15.0
- Also installed: PySocks, socksio, Jinja2, requests-ntlm, httpx-ntlm, defusedcsv, requests-toolbelt, setuptools

### 14. subfinder 2.17.0 — subdomain enumeration (ProjectDiscovery)
- **Path:** `~/bin/subfinder` (GitHub release binary)
- **Verify:** `subfinder -version` → `Current Version: v2.17.0`
- **Config dir:** `~/.config/subfinder` (add API keys for more sources)
- **Usage:** `subfinder -d example.com`

### Gotchas for future installs
- Git Bash mangles `-c` args starting with `/home/...` → set `MSYS_NO_PATHCONV=1` or don't start the command string with a bare path.
- Files written via UNC path (`\\wsl.localhost\...`) may get CRLF endings → run `sed -i 's/\r$//'` on shell scripts.
- `~/bin` is on PATH via `~/.profile` (login shells); wrappers live there.

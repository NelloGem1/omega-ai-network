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

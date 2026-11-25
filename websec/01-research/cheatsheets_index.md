# Web Security Research Index
Local clones of the key payload/cheat-sheet repositories. All cloned with `--depth 1`.

## 1. PayloadsAllTheThings — OFFENSIVE PAYLOAD BIBLE
- Path: `~/PayloadsAllTheThings` (22M)
- Source: https://github.com/swisskyrepo/PayloadsAllTheThings
- One folder per vuln class, each with a `README.md` containing payloads, intruder wordlists, and detection/notes.

### Read first by vuln class
| Vuln class | File/folder to open first |
|---|---|
| SQL Injection | `SQL Injection/README.md`, then per-DB: `MySQL Injection.md`, `PostgreSQL Injection.md`, `MSSQL Injection.md`, `OracleSQL Injection.md` |
| XSS | `XSS Injection/README.md` (incl. `XSS_Filter_Evasion_Cheat_Sheet.md`) |
| CSRF | `Cross-Site Request Forgery/README.md` |
| SSRF | `Server Side Request Forgery/README.md` (cloud metadata bypasses) |
| JWT | `JWT/README.md` (alg confusion, weak secrets, kid injection) |
| IDOR | `Insecure Direct Object References/README.md` |
| XXE | `XXE Injection/README.md` |
| SSTI | `Server Side Template Injection/README.md` (Jinja2, Twig, Freemarker…) |
| LFI/RFI | `File Inclusion/README.md` |
| Command Injection | `Command Injection/README.md` |
| Path Traversal | `Directory Traversal/README.md` |
| Open Redirect | `Open Redirect/README.md` |
| CORS | `CORS Misconfiguration/README.md` |
| GraphQL | `GraphQL Injection/README.md` |
| API key leaks | `API Key Leaks/README.md` |
| File upload | `Upload Insecure Files/README.md` |
| Deserialization | `Insecure Deserialization/README.md` |
| Request smuggling | `Request Smuggling/README.md` |
| Race conditions | `Race Condition/README.md` |
| Full folder list | `ls ~/PayloadsAllTheThings` |

## 2. HackTricks — MOST COMPLETE TECHNIQUES WIKI
- Path: `~/HackTricks` (316M — gitbook source; content lives under `src/`)
- Source: https://github.com/HackTricks-wiki/hacktricks
- Layout: `~/HackTricks/src/<category>/.../README.md` — an offline copy of hacktricks.wiki.
- Example paths (verify with `find ~/HackTricks/src -iname "*idor*"` etc.):
  - `src/network-services-pentesting/` — service-by-service pentest notes
  - `src/pentesting-web/` — web vuln techniques (SSRF, XSS, SQLi, JWT, access control…)
  - `src/pentesting-web/ssrf-server-side-request-forgery/`
  - `src/pentesting-web/xss-cross-site-scripting/`
  - `src/pentesting-web/sql-injection/`
  - `src/pentesting-web/jwt/`
  - `src/pentesting-web/idor-access-control/` (check actual folder name with find)
- Quick search: `grep -ril "keyword" ~/HackTricks/src | less`

## 3. OWASP Cheat Sheet Series — DEFENSIVE SIDE
- Path: `~/CheatSheetSeries` (42M) → sheets in `~/CheatSheetSeries/cheatsheets/`
- Source: https://github.com/OWASP/CheatSheetSeries
- Key sheets:
  - `Authentication_Cheat_Sheet.md`
  - `Authorization_Cheat_Sheet.md`
  - `Session_Management_Cheat_Sheet.md`
  - `Cross_Site_Scripting_Prevention_Cheat_Sheet.md`
  - `Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md`
  - `Server_Side_Request_Forgery_Prevention_Cheat_Sheet.md` (verify name: `ls ~/CheatSheetSeries/cheatsheets | grep -i forgery`)
  - `Input_Validation_Cheat_Sheet.md`
  - `Cryptographic_Storage_Cheat_Sheet.md`
  - `Content_Security_Policy_Cheat_Sheet.md`
  - `CORS_Security_Cheat_Sheet.md`
  - `Logging_Cheat_Sheet.md`, `REST_Security_Cheat_Sheet.md`
  - Full list: `ls ~/CheatSheetSeries/cheatsheets`

## How to use during practice
1. Before fuzzing a lab bug, open the matching `PayloadsAllTheThings/<class>/README.md` for a payload list and context notes.
2. When stuck on a bypass/technique, `grep -ri "keyword" ~/HackTricks/src` or find the vuln folder and read its README.
3. After solving, skim the OWASP Cheat Sheet for that class — useful for "how would you prevent this" interview answers.
4. Repos update frequently: refresh with `git -C ~/PayloadsAllTheThings pull`, etc.

## Online references
- PortSwigger Web Security Academy: https://portswigger.net/web-security — free labs, mirror these vuln classes
- HackTricks online: https://book.hacktricks.wiki
- PayloadsAllTheThings web view: https://swisskyrepo.github.io/PayloadsAllTheThings/
- OWASP Cheat Sheet Series web: https://cheatsheetseries.owasp.org/

# Obtaining Free TLS/SSL Certificates — Comprehensive Guide

*Research compiled 2026. All facts verified against official documentation; see Sources.*

---

## 1. Let's Encrypt: The Free Certificate Authority

### What it is
Let's Encrypt is a free, automated, open certificate authority (CA) operated by **ISRG (Internet Security Research Group)**, a 501(c)(3) non-profit. It was founded in 2014 by Josh Aas and Eric Rescorla with support from EFF, Mozilla, Cisco, Akamai, and others. Its founding goal: **encrypt the entire web**. Since its launch in December 2015 it has issued over **3 billion certificates** and is the CA used by roughly 60%+ of all certificate deployments on the internet. It is trusted by all major browsers automatically.

### Key characteristics
- **Completely free.** No cost for any number of certificates, no account fees, no credit card.
- **DV only** — Domain Validated certificates. No Organization (OV) or Extended Validation (EV) certs; your domain name cannot appear in a paid organizational sense.
- **Automated only** — issuance happens exclusively through the ACME protocol; there is no manual "click and download" web portal flow.
- **Automated revocation** — certificates are auto-revoked if a domain expires or its DNS stops pointing at the server.

### Certificate lifetimes (changing!)
- **Current default: 90 days** from issuance.
- **2026:** Let's Encrypt is rolling out shorter lifetimes via ACME "profiles":
  - `tlsserver` profile → **45-day** certs (opt-in, available for testing/early adopters).
  - `classic` profile → **64-day** certs starting ~Feb 10, 2027.
  - From **Feb 16, 2028**, the classic profile issues **45-day** certificates with a **7-hour authorization reuse** period.
- **Industry-wide rule:** The CA/Browser Forum voted (Ballot SC-081, April 2025, driven by Apple) to cap public TLS cert lifetimes at **47 days** by **March 15, 2029**, stepping down through 200 days (2026) and 100 days (2027). This applies to ALL publicly-trusted CAs — paid ones included.
- **Short-lived profile:** All subscribers can opt into certificates valid for just **~6 days** for maximum security/automation.
- **Why shorter?** Limits damage from mis-issuance and key compromise; forces automation (which is the whole point — automation makes short lifetimes painless).

### Rate limits (production API)
Enforced per Let's Encrypt account using token buckets:

| Limit | Allowance |
|---|---|
| New orders per account | 300 per 3 hours (refills 1 order / 36 s) |
| Certificates per registered domain (eTLD+1) | **50 per week** |
| New certificates per exact set of hostnames | 5 per week |
| Identifiers (SANs) per certificate | up to 100 (profile-dependent) |
| Authorization failures per account/hostname | 5 per hour |
| Failed authorizations per hostname (all accounts) | 300 per day |
| Duplicate certificate | 5 identical certs per week |

Notes:
- **Renewals are exempt** from issuance rate limits — a cert that renews counts as a renewal, not a new cert, as long as it's within the renewal window.
- The 50/week limit counts every cert containing names under your domain — a cert for `a.example.com` and another for `b.example.com` each consume one hit.
- Hitting a limit is not fatal: buckets refill gradually; there's no manual reset. For development, **always test against staging** (`--staging`), which has much higher limits but deliberately untrusted certs.
- **Staging server:** `https://acme-staging-v02.api.letsencrypt.org/directory` — use it to debug; you'll see browser warnings, which is expected.

---

## 2. The ACME Protocol

ACME (Automatic Certificate Management Environment, RFC 8555) is the protocol that automates certificate issuance and renewal. An **ACME client** (Certbot, acme.sh, Caddy, cert-manager...) talks to a **CA's ACME server** over HTTPS.

### The flow
1. Client generates a key pair and registers an **account** with the CA (email optional for Let's Encrypt).
2. Client creates an **order** requesting a certificate for domain name(s).
3. CA creates **authorizations** — one per domain — and returns **challenges** the client must solve to prove domain control.
4. Client solves the challenge (usually by publishing a token at a predictable location), notifies the CA to validate.
5. CA connects to your server/DNS and checks the token. On success → certificate is signed and returned.
6. Renewal repeats automatically before expiry.

### The three challenge types

| Challenge | How it works | Proves | When to use |
|---|---|---|---|
| **HTTP-01** | CA fetches `http://<domain>/.well-known/acme-challenge/<token>` on port 80 | You control the HTTP service for that exact hostname | Default choice for web servers. Simplest. Needs inbound port 80 open. **Does NOT work for wildcards.** |
| **DNS-01** | Client publishes a TXT record `_acme-challenge.<domain>` via your DNS provider's API (or manually); CA queries DNS | You control the zone's DNS — for the apex AND any subdomain/wildcard | **Required for wildcard certificates** (`*.example.com`). Also works for internal-only hosts with no public web server. Needs DNS API credentials or manual TXT updates. |
| **TLS-ALPN-01** | Client runs a TLS server on port 443 presenting a special self-signed cert containing the token; CA validates during TLS handshake | You control the TLS endpoint | Alternative to HTTP-01 when port 80 is blocked but 443 is open. Not supported by all clients; also cannot do wildcards. |

**Wildcard rule:** HTTP-01 and TLS-ALPN-01 only prove control of one exact hostname. To issue `*.example.com`, **DNS-01 is mandatory** — it proves zone control, which logically extends to any name in the zone. Common practice: request `example.com` + `*.example.com` in one SAN cert.

**Multi-domain SAN certs:** One certificate can cover up to ~100 identifiers (e.g., `example.com`, `www.example.com`, `api.example.com`). Every identifier counts toward rate limits separately per registration but shares one cert download.

---

## 3. Certbot — The Standard Client

Certbot is the EFF/ISRG-backed reference ACME client, written in Python. Install it via your distro's package manager, pipx, or the OS-specific instructions on certbot.eff.org.

### Install (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install certbot
# or the snap, which is EFF's recommended method:
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot
```

### Getting a certificate — the four main modes

**A. With a web server plugin (easiest — handles config + reload automatically)**
```bash
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot --apache -d example.com
```
The plugin temporarily modifies your server config, performs HTTP-01 validation, installs the cert, and sets up HTTPS redirects. Renewal re-uses the plugin.

**B. Standalone (no existing web server on 80/443)**
```bash
sudo systemctl stop nginx apache2   # free up port 80
sudo certbot certonly --standalone -d example.com
sudo systemctl start nginx apache2
```
Certbot spins up its own temporary web server to answer the challenge. For renewals you need port 80 free at renewal time — use a pre/post hook or `--webroot` instead.

**C. Webroot (works alongside a running server, no downtime)**
```bash
sudo certbot certonly --webroot -w /var/www/html -d example.com
```
Pre-configure your web server to serve `/.well-known/acme-challenge/` from a directory; certbot drops the token file there. Ideal for renewals.

**D. Manual / DNS (wildcards, split-horizon)**
```bash
sudo certbot certonly --manual --preferred-challenges dns -d example.com -d '*.example.com'
```
Certbot prints the TXT record; you create it in your DNS panel. Fine for one-offs; painful for automation — prefer acme.sh for DNS API automation.

### Where everything lives
```
/etc/letsencrypt/
├── live/example.com/
│   ├── fullchain.pem      # cert + chain (what servers serve)
│   ├── privkey.pem        # private key (keep secret)
│   ├── cert.pem           # cert only
│   ├── chain.pem          # intermediates only
│   └── README             # symlink warnings
├── archive/example.com/   # all historical certs/keys
├── renewal/example.com.conf  # renewal config (authenticator, hooks)
└── accounts/              # ACME account keys
```
`live/` entries are symlinks into `archive/` — safe to reference in nginx/apache/caddy configs.

### Auto-renewal
- Certbot installs a **systemd timer** (`certbot.timer`, runs twice daily by default) or a cron job (`/etc/cron.d/certbot`).
- Renewals happen only when <30 days remain (or per `renew_before_expiry` in renewal conf).
- Dry-run test: `sudo certbot renew --dry-run` (hits staging, safe).
- Force early renewal: `sudo certbot renew --force-renewal` or `sudo certbot certonly ... --force-renewal`.
- Pre/post hooks: `--pre-hook "systemctl stop nginx"`, `--post-hook "systemctl start nginx"`, or renewal hooks in `/etc/letsencrypt/renewal-hooks/{pre,deploy,post}/`.
- Deploy hook example — reload nginx after every successful renewal:
  ```bash
  sudo tee /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'EOF'
  #!/bin/sh
  systemctl reload nginx
  EOF
  sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
  ```

---

## 4. acme.sh — The Lightweight Alternative

acme.sh is a pure-shell ACME client (github.com/acmesh-official/acme.sh), actively maintained. It's the default CA client in many tools and is owned/sponsored by ZeroSSL (though it supports Let's Encrypt and other CAs equally well).

### Install
```bash
curl https://get.acme.sh | sh -s email=admin@example.com
# installs to ~/.acme.sh/, adds a cron job automatically, sets the CA (ZeroSSL default → switch to LE)
acme.sh --set-default-ca --server letsencrypt
```

### Key advantages over Certbot
- **100+ DNS provider plugins** (`dns_cf` Cloudflare, `dns_aws`, `dns_google`, `dns_ali`, `dns_pdns`, etc.) — enables fully automated **wildcard** and internal certs with zero manual DNS steps.
- No dependencies beyond `curl`/`openssl`/`cron`; tiny footprint; runs on routers, NAS, macOS, FreeBSD.
- **Cron-based renewal** — installs a daily cron entry; v3.1.x runs every 6 hours and enables **ARI (ACME Renewal Information, RFC 9773)** by default, so renewals happen when the CA recommends rather than on a fixed schedule.
- `--install-cert` copies certs to stable paths (e.g., `/etc/ssl/`) and stores a `--reloadcmd` to reload your web server after each renewal.

### Example: wildcard via Cloudflare
```bash
export CF_Token="<zone-dns-edit-token>"   # scoped API token, not global key
acme.sh --issue --dns dns_cf -d example.com -d '*.example.com' \
  --install-cert -d example.com \
  --key-file       /etc/ssl/private/example.key \
  --fullchain-file /etc/ssl/certs/example.crt \
  --reloadcmd      "systemctl reload nginx"
```
The DNS plugin creates `_acme-challenge` TXT records via the Cloudflare API, waits for validation, then deletes them automatically. Renewal reuses the saved credentials.

### When to pick acme.sh over Certbot
- Wildcards or DNS-01 automation (biggest win)
- Non-Linux/embedded environments
- You want minimal footprint and cron control

---

## 5. Other ACME Clients & Automated HTTPS

| Client | Platform | Notes |
|---|---|---|
| **win-acme (wacs.exe)** | Windows | THE client for Windows/IIS/Apache/nginx/SimpleHTTP. Scheduled-task auto-renewal, pluggable validators incl. DNS-01 via many providers, built-in store for IIS. Also on GitHub as win-acme/win-acme. Free. |
| **getssl** | Shell | Older shell client similar to acme.sh; lighter DNS plugin set; still works but less actively developed. |
| **Caddy** | Any (Go binary) | **Zero-config HTTPS**: `example.com { ... }` in a `Caddyfile` → Caddy does ACME, certs, renewal, and OCSP automatically. Best-in-class for simple deployments. |
| **Traefik** | Any (Go binary) | Reverse proxy with built-in ACME (Let's Encrypt/ZeroSSL) via labels/`certificatesResolvers` + Docker provider. Ideal for Docker stacks. |
| **Kubernetes cert-manager** | K8s | Issues/renews certs via ACME (and other issuers) into `Certificate` CRDs → stored as `tls` secrets consumed by Ingress/Gateway. Supports HTTP-01, DNS-01 (many providers), and ZeroSSL via EAB. |
| **Plesk/cPanel/DirectAdmin** | Hosting panels | Built-in Let's Encrypt integration — one click, handles everything. |
| **lego** | Go | Popular Go ACME library + CLI used by many tools; certbot-compatible flags. |

**Rule of thumb:** if a tool is a reverse proxy or orchestrator (Caddy, Traefik, cert-manager), let IT handle ACME — don't run a separate client.

---

## 6. ZeroSSL Free Tier

ZeroSSL is a commercial CA that offers a genuinely free ACME tier:

- **Free ACME certificates:** unlimited 90-day certs via ACME, including **multi-domain and wildcards** — ZeroSSL advertises "no rate limits" on the ACME path (reasonable-usage policy applies; max ~6 DNS labels excluding public suffix).
- **ACME endpoint:** `https://acme.zerossl.com/v2/DV90`
- **EAB required:** unlike Let's Encrypt, ZeroSSL requires **External Account Binding** — you create an account at zerossl.com, generate EAB credentials (HMAC key + KID) in the developer section, and pass them to your client (`certbot register --eab-kid ... --eab-hmac-key ...`, cert-manager `externalAccountBinding`, acme.sh handles it).
- **Paid tiers:** the free *dashboard* plan allows 3 manually-created 90-day certs; ACME path is unlimited regardless of plan. Paid plans add longer-lived "annual" certs, SSL monitoring, etc.
- **Positioning:** marketing push around "90-day certs for everyone," REST API, and owning acme.sh. Quality/trust is comparable (browser-trusted root), but Let's Encrypt remains the default community choice.

vs Let's Encrypt: same ACME protocol, same free DV certs; ZeroSSL keeps 90-day lifetimes for now (though industry ballot SC-081 will eventually force it down too — its "annual" certs are capped at 199 days), requires EAB signup, and has softer guarantees.

---

## 7. Common Failures & Fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `Connection refused` / timeout on HTTP-01 | Port 80 blocked inbound (firewall, ISP, cloud security group) | Open TCP 80 inbound, or use `--webroot`, or switch to DNS-01/TLS-ALPN-01 |
| `unauthorized` / "invalid response" | DNS points to wrong IP, or server serves wrong vhost, or redirect loop | Verify `dig A example.com` = your IP; check nginx `server_name`; avoid HTTPS redirects during validation |
| `too many failed authorizations` | 5 failures/account/hostname/hour | **Wait ~1 hour**; fix the underlying issue first — retrying immediately won't help |
| `too many certificates already issued` (50/week/domain) | Rate limit on registered domain | Wait for refill (1 cert/202 min); consolidate certs; renewals unaffected |
| Wildcard fails with HTTP-01 | Wildcards require DNS-01 | Use acme.sh/Certbot `--preferred-challenges dns` + DNS API |
| `no such host` / NXDOMAIN | DNS propagation not complete | Wait, or validate against the authoritative NS; check TTLs |
| Cert issued but browser warns | Serving `cert.pem` only instead of `fullchain.pem`, or missing intermediate | Always serve the full chain (`fullchain.pem`) |
| Renewal fails silently | Port 80/443 blocked at renewal time; standalone mode needs port 80 free | Use webroot/nginx plugin; add deploy hooks |
| `key type not supported` / weak key errors | Old client or RSA-1024 | Modern clients use ECDSA P-256 by default; `--key-type ecdsa` or `rsa` |
| Multi-SAN cert rejected | One bad domain in list fails whole order | Validate each name separately; check every SAN resolves publicly |
| Email not received / expiry notices | Notifications opt-in and best-effort | Don't rely on them — automation (certbot.timer/acme.sh cron) is the real safety net |

---

## 8. Cost Reality Check: Free vs Paid

| | Free (Let's Encrypt / ZeroSSL ACME) | Paid CA (Sectigo, DigiCert, GlobalSign…) |
|---|---|---|
| Price | $0 | $10–$500+/yr |
| Validation | DV only | DV / OV / **EV** (company identity shown) |
| Issuance | Fully automated via ACME | Often manual portal, some offer ACME |
| Lifetime | 90 days → shrinking to 45 days (2028–29) | Up to 398 days historically, also shrinking to ≤47 days by 2029 (industry-wide) |
| Warranty/liability | No meaningful warranty | $10k–$1M+ insurance, contract support |
| Support | Community forums only | 24/7 phone/chat/SLA |
| Organization name in cert | No (just domain) | OV/EV include legal entity |
| Best for | Websites, APIs, IoT, internal services | E-commerce needing EV trust signals, enterprises needing audits/contracts, code where contractual CA required |

**Bottom line:** For ~95% of use cases (encrypt a domain you control), free CAs are strictly better — automated, trusted, and the paid advantages (EV green bar is dead anyway; browsers dropped visual EV distinction in 2019) rarely matter. Paid certs buy you **support contracts, warranties, OV/EV identity, and sometimes longer lifetimes** — not stronger encryption. Note the 47-day industry cap means "longer lifetime" is disappearing for everyone.

---

## Quick-Start Cheatsheet

```bash
# Ubuntu + nginx, fastest path:
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com --redirect
sudo certbot renew --dry-run

# Wildcard via Cloudflare:
curl https://get.acme.sh | sh
~/.acme.sh/acme.sh --set-default-ca --server letsencrypt
CF_Token=xxx ~/.acme.sh/acme.sh --issue --dns dns_cf \
  -d example.com -d '*.example.com' --install-cert \
  --key-file /etc/ssl/priv.key --fullchain-file /etc/ssl/fullchain.pem
```

---

## Sources

- Let's Encrypt — Certificate Lifetime Rationale and Plans: https://letsencrypt.org/docs/cert-lifetimes/
- Let's Encrypt — Decreasing Certificate Lifetimes to 45 Days (Dec 2025): https://letsencrypt.org/2025/12/02/from-90-to-45
- Let's Encrypt — ACME Profiles: https://letsencrypt.org/docs/profiles/
- Let's Encrypt — Rate Limits: https://letsencrypt.org/docs/rate-limits/
- Let's Encrypt — Scaling Rate Limits (Jan 2025): https://letsencrypt.org/2025/01/30/scaling-rate-limits
- Let's Encrypt — Rate Limits & 45-Day Certs (Feb 2026): https://letsencrypt.org/2026/02/24/rate-limits-45-day-certs
- heise — 47 days: CA/B Forum decision on shorter certs: https://www.heise.de/en/news/47-days-CAs-browser-manufacturers-decide-on-shorter-duration-for-certificates-10353244.html
- acmeprotocol.dev — Certificate lifetime timeline (Ballot SC-081): https://acmeprotocol.dev/webpki/cert-lifetime/
- ZeroSSL — ACME documentation: https://zerossl.com/documentation/acme
- ZeroSSL — ACME feature/pricing: https://zerossl.com/features/acme , https://zerossl.com/pricing
- cert-manager — ZeroSSL tutorial (EAB setup): https://cert-manager.io/docs/tutorials/zerossl/zerossl/
- acme.sh — GitHub: https://github.com/acme-sh/acme.sh
- ssl.sh — acme.sh DNS API/wildcard guide: https://ssl.sh/guides/acme-sh-dns-api-wildcard/
- win-acme: https://github.com/win-acme/win-acme
- Certbot docs: https://eff-certbot.readthedocs.io/
- Let's Encrypt community — failed validation limit: https://community.letsencrypt.org/t/failed-validation-limit-validation-ip-addresses-and-authorization-lifetime/31520

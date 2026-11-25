# Obtaining TLS/SSL Certificates — All Options Besides Let's Encrypt

Companion to the Let's Encrypt notes. Covers paid commercial CAs, budget providers, cloud-platform certificates, self-signed certs, private/internal CAs, wildcard/multi-domain certs, and code-signing/S-MIME certificates.

---

## 1. Paid Commercial CAs

The "real" certificate authorities trusted by all browsers. Certificates are issued for a fee, typically billed as a subscription (1/2/3-year terms) with annual reissuance.

### The big four

| CA | Notes |
|---|---|
| **DigiCert** | Market leader for enterprise certs. ~$1.25M–$1.75M warranties; Smart Seal customer-trust badge; TLS Inspector / CertCentral management platforms. Basic DV from ~$150–290/yr, Basic OV ~$250–290/yr, EV from ~$356–484/yr. |
| **Sectigo** (formerly Comodo) | Best value mainstream CA. Huge reseller market; often cheapest path to OV/EV. PositiveSSL DV can be under $10/yr on sale; InstantSSL OV ~$40–60/yr; EV ~$150–210/yr. |
| **GlobalSign** | Enterprise PKI specialist; managed PKI, code signing, IoT/device certs. Higher prices, more managed-service focus. |
| **Entrust** | Legacy CA (Datacard lineage), strong in government/regulated industries; also sells SSL via Sectigo-branded resellers. |

### Validation levels

- **DV (Domain Validated)** — prove control of the domain (DNS record, HTTP file, or email). Issued in minutes. Cheapest: **~$10–60/yr**. No company identity in the cert.
- **OV (Organization Validated)** — business must supply legal registration docs, address, phone verification. Company name is embedded in the cert. **~$40–300/yr**.
- **EV (Extended Validation)** — deepest vetting: legal entity docs, verified physical address, telephone, vetting of domain control and authorization. **~$150–900/yr** (DigiCert Secure Site EV ~$910/yr; budget resellers ~$150/yr).

### Why the "green padlock" is gone

Historically EV certs triggered a green address bar / "padlock + company name" UI in browsers. **All major browsers (Chrome 77, Firefox 70, Safari) removed EV UI in 2019** after phishing studies showed users didn't notice the difference. Today **an EV cert looks identical to DV in the browser** — same padlock, same HTTPS indicator. EV still matters for: procurement requirements (banks/enterprise vendors mandate it), higher warranties ($1.5M+ vs $10k–100k), and some phishing-resistance heuristics, but it is no longer a visible trust signal.

### Warranties

Commercial CAs include a **certificate warranty**: if the CA's vetting is found negligent and a fraudulent cert causes damage, they pay up to a cap (DV ~$10k–50k, OV ~$250k–1M, EV ~$1.5M+). This is liability insurance on the CA's diligence — essentially irrelevant for personal sites.

---

## 2. Budget / Resold Paid Options

Certificates from the same major CAs resold at lower prices by discounters:

- **ZeroSSL** — freemium; 90-day free certs (like Let's Encrypt), plus 1-year paid DV (~$10–30/yr), OV/EV, wildcard. API-driven, popular for automation.
- **SSL.com** — full CA itself; competitive pricing on OV/EV (often cheaper than DigiCert), strong code-signing line.
- **Namecheap / GoDaddy / SSLs.com / Sectigo resellers** — resell Sectigo/DigiCert/GlobalSign certs 30–60% below CA-direct pricing. Same certificate, same trust — the brand on the reseller invoice differs from the issuer name in the cert.
- **ssl.sh, ssls.com, datassl.com** — price-aggregators; 1-year DV from ~$8–10, OV ~$40–80, EV ~$150–210.

**Key fact:** certificates are signed by the root CA (e.g. "Sectigo RSA"), not the reseller — buying "cheap" doesn't reduce browser trust.

---

## 3. Cloud-Platform Certificates

### AWS Certificate Manager (ACM)

- **Free** public TLS certs issued by **Amazon Trust Services** (trusted by all browsers).
- **Only usable inside AWS** — the private key never leaves AWS; certs bind to ALB/NLB, CloudFront, API Gateway, App Runner, Cognito, Amplify, etc. Cannot download (non-exportable) except via the newer exportable-certificates feature (limits apply).
- **Automatic DNS-01 validation + renewal** as long as the validation CNAME exists (works great with Route 53).
- **Region quirk:** ALB/NLB certs must be in the resource's region; **CloudFront certs must be requested in us-east-1**.
- Since Nov 2025, ACM also supports the **ACME protocol** for automated issuance on EC2 (still AWS-bound).

### Google Trust Services / Google Certificate Manager

- Free GTS certs provisioned automatically for **GCP HTTPS Load Balancers, Cloud Run, App Engine** domains.
- **Google Certificate Manager** — paid (~$0.03–0.10/cert/month-ish scaling) map-based cert management for GCP LB; wildcard + multi-domain support.
- Same model as ACM: free inside the platform, not portable.

### Azure App Service managed certificates

- **Free** TLS cert for custom domains on App Service — auto-issued and auto-renewed by App Service.
- Limitations: **no wildcard**, no custom root CAs, can't export, basic validation only (must map the custom domain first). Requires Basic+ App Service plan.
- "App Service certificates" (paid, GoDaddy-issued) and BYOC PFX upload also supported.

### Cloudflare Origin CA + Universal SSL

- **Universal SSL:** every proxied domain gets a **free auto-renewing edge cert** covering apex + `*.domain` (one level). Universal SSL renews automatically; no config needed.
- **Origin CA certificates:** free certs Cloudflare signs for the origin-to-edge hop. Trusted **only by Cloudflare** — browsers warn if served directly; valid as long as traffic is proxied through Cloudflare (orange-cloud). Long-lived (up to 15 years), no revocation needed.
- Caveat: Origin CA + Universal SSL make you dependent on Cloudflare's proxy for trust.

---

## 4. Self-Signed Certificates

### Creating one

```bash
# Single self-signed cert + key (1 year)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=example.internal/O=My Org"

# With SANs (needed for modern browsers / IPs)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 825 -nodes \
  -addext "subjectAltName=DNS:app.internal,DNS:localhost,IP:192.168.1.10" \
  -subj "/CN=app.internal"
```

### When they are OK

- Internal tools never exposed to the public internet (admin panels, dashboards).
- Dev/test environments, home labs.
- IoT/device fleets where you control the trust store.
- Service-to-service mTLS inside a closed network.

### When they're NOT OK

- Any public-facing site — browsers will warn "Not Secure" / NET::ERR_CERT_AUTHORITY_INVALID.
- You cannot push a self-signed cert into browsers/OS trust stores of your users at scale.

### Making clients trust it

- **Browser:** click through the warning (Chrome -> Advanced -> Proceed) — only viable for yourself.
- **OS trust store:** copy `cert.pem` into `/usr/local/share/ca-certificates/` + `update-ca-certificates` (Debian/Ubuntu); Keychain Access on macOS; `certlm.msc` on Windows. Distributes trust to everything using the system store.
- **Java apps:** import into the JDK cacerts (`keytool -importcert`).
- **curl:** `curl --cacert cert.pem https://...`

### mkcert — the right tool for local dev

`mkcert` creates a **local CA once**, installs it into your OS + browser trust stores, then issues per-project certs that browsers trust with **no warnings**. The standard solution for `https://localhost` dev servers.

```bash
mkcert -install                    # one-time: local CA into trust stores
mkcert localhost 127.0.0.1 ::1     # issues cert.pem + key.pem
```

---

## 5. Private / Internal CAs

When an organization needs certificates for internal services (k8s, service mesh, VPNs, internal web apps) it often runs its **own CA**.

### OpenSSL root CA walkthrough

```bash
# 1. Root CA key + self-signed cert (10 years)
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -key rootCA.key -sha256 -days 3650 \
  -out rootCA.crt -subj "/CN=MyCorp Root CA"

# 2. Server key + CSR
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/CN=internal.example.com"

# 3. Sign with root CA (extfile adds SANs + serverAuth EKU)
openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key \
  -CAcreateserial -out server.crt -days 825 -sha256 \
  -extfile <(printf "subjectAltName=DNS:internal.example.com\nextendedKeyUsage=serverAuth")
```

Distribute `rootCA.crt` to every client/device trust store. Renew/rotate each leaf cert on your own schedule.

### Tools

- **step-ca** (`smallstep`) — modern ACME-compatible CA server; issues short-lived certs via ACME, integrates with device identity (TPM, cloud metadata). De-facto standard for zero-trust internal PKI.
- **TinyCA** — simple GUI for managing a small internal CA (Windows/Linux).
- **HashiCorp Vault PKI** — CA-as-a-service with ACME endpoint, dynamic secrets.
- **EJBCA / Microsoft AD CS** — enterprise-grade CA for large orgs / Windows shops.

### Security responsibilities (you ARE the CA)

- Protect the **root key** offline/HSM — its compromise = forge any cert.
- Enforce SAN/EKU correctness, CRL/OCSP if you want revocation, short lifetimes.
- Audit issuance; rotate root keys on a multi-year plan with cross-signing.
- Manage expiry yourself — no external reminders.

---

## 6. Wildcard & Multi-Domain Certificates

- **Wildcard:** `*.example.com` covers ONE level of subdomains (`www`, `api`) but NOT apex or `a.b.example.com`. Must be DV or OV — **EV certs cannot be wildcards** (CA/B rules).
- **Multi-SAN / UCC:** one cert listing multiple FQDNs (e.g. `example.com, example.net, www.example.com`). Legacy "UCC" certs allowed up to 100 SANs.
- **Pricing:** wildcard roughly 3–10x a single-domain cert (DV wildcard ~$60–130/yr, OV wildcard ~$150–360/yr, DigiCert ~$500+/yr). Each extra SAN on multi-domain certs adds ~$30–80/yr.
- **Validation requirement:** wildcards **require DNS-01 validation** (a TXT record) because HTTP/email can't prove control of all possible subdomains. Same for multi-domain certs covering multiple registered domains.
- vs. Let's Encrypt: LE already gives free wildcard + 100 SANs — paid wildcard mainly buys **1-year validity** (fewer renewals), support, and OV/EV identity.

---

## 7. Code Signing Certificates (Bonus — Different PKI Purpose)

TLS certs prove server identity; **code-signing certs sign software binaries** so OSes can verify publisher identity + integrity. Completely different Extended Key Usage (`codeSigning`), different issuance process.

- **OV code signing:** verifies the organization. Windows SmartScreen still shows "unknown publisher" reputation warnings until the cert builds reputation (unless EV).
- **EV code signing:** deeper vetting; **instantly earns SmartScreen reputation** on Windows; required by some app stores/enterprise policies. Must be stored on FIPS hardware token or cloud HSM (CA/B Forum rule since 2023 — no more downloadable EV keys).
- **Signing:** Windows `signtool sign /fd sha256 /tr <timestamp-URL> /td sha256 file.exe`; macOS `codesign` + **notarization** (`xcrun notarytool`) is mandatory for Gatekeeper since Catalina — Apple notarization is a separate Apple service, not a CA cert.
- Price: OV ~$80–400/yr, EV ~$250–700/yr. Sectigo/SSL.com/DigiCert all sell them; cheap "$10 code signing certs" on the gray market are often stolen/revoked keys — avoid.

---

## 8. Email Certificates — S/MIME (Brief)

Same X.509 PKI, different Extended Key Usage (`emailProtection`). S/MIME certs let users **sign and encrypt email**; the sender's cert is embedded in messages so recipients verify identity without a separate CA trust step for the recipient. DV email certs are cheap (~$10–30/yr); OV/EV versions verify the person/org. Not widely deployed because webmail + PGP/GPG cover most needs, and Outlook/Thunderbird support is patchy.

---

## 9. Choosing Guide

| Scenario | Best option |
|---|---|
| Personal site / blog | Let's Encrypt (free) or ZeroSSL free — or cheap Sectigo DV (~$10) if you want 1-yr validity |
| Small business public site | Sectigo/SSL.com **OV** (~$40–80/yr) — shows company name in cert |
| E-commerce / finance / enterprise vendor requirement | **EV** (~$150–500/yr) — procurement-mandated, highest warranty |
| High-traffic enterprise needing SLAs, inspection, managed PKI | DigiCert Secure Site / GlobalSign managed PKI |
| All-in on AWS / GCP / Azure | **ACM / GTS / App Service managed certs** — free, auto-renewing |
| Site behind Cloudflare proxy | **Cloudflare Universal SSL** (edge) + Origin CA (origin) — free |
| Internal tools, admin panels, home lab | **Self-signed** or **mkcert** (dev) |
| Organization-wide internal PKI, k8s, service mesh | **step-ca / Vault PKI / AD CS** private CA |
| Many subdomains under one domain | **Wildcard** (DNS-01 required) |
| Several unrelated domains on one server | **Multi-SAN/UCC** cert |
| Signing Windows/macOS software | **Code-signing cert** (OV or EV), NOT a TLS cert |
| Encrypting/signing email | **S/MIME cert** |
| IoT / embedded fleet | Private CA (step-ca) or managed device PKI (GlobalSign IoT, AWS IoT certs) |

---

## 10. Installation Overview

A TLS deployment needs **three files**:

- `cert.pem` / `fullchain.pem` — your leaf cert (+ intermediates; "fullchain" includes them)
- `privkey.pem` / `key.pem` — private key (keep secret, 0600 perms)

### Nginx

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate     /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
}
```

### Apache

```apache
<VirtualHost *:443>
    ServerName example.com
    SSLEngine on
    SSLCertificateFile      /etc/ssl/certs/cert.pem
    SSLCertificateKeyFile   /etc/ssl/private/privkey.pem
    SSLCertificateChainFile /etc/ssl/certs/chain.pem
</VirtualHost>
```

### IIS (Windows)

Import the **PFX** (cert + key + chain bundled) via IIS Manager -> Server Certificates -> Complete Certificate Request, then bind it to the site on 443. PFX password-protected; export via `certlm.msc` or openssl: `openssl pkcs12 -export -out site.pfx -inkey key.pem -in cert.pem -certfile chain.pem`.

### Renewal differences

| Type | Renewal |
|---|---|
| Paid commercial | Manual CSR -> CA validates again -> reissue -> reinstall. 1-yr certs on "multi-year" plans are reissued annually by the reseller (subscription model). Watch expiry — no auto-renewal unless you automate. |
| Cloud-managed (ACM/GTS/App Service/Cloudflare) | Fully automatic — invisible to you. |
| Self-signed / private CA | You are the CA: set your own expiry, reissue with your own tooling (cron + step-ca/openssl). |

---

## Sources

- DigiCert pricing & warranty tiers — https://www.techradar.com/news/best-ssl-certificate-provider
- Sectigo/DigiCert reseller price lists — https://www.datassl.com/en/pricing , https://karizanta.com/ssl-certificates , https://ssl.sh/certificates/
- CA price increases (Nov 2024) — https://www.eurovps.com/faq/price-increase-for-ssl-certificate-based-products/
- AWS ACM docs — https://docs.aws.amazon.com/acm/latest/userguide/acm-services.html , https://jhooq.com/aws-certificate-manager-acm-step-by-step/
- Azure App Service TLS certs — https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate , https://learn.microsoft.com/en-us/azure/app-service/overview-tls
- Cloud cert management comparison — https://certpulse.dev/blog/cloud-provider-certificate-management-compared-aws-acm-vs-azure-key-vault-vs-goo
- CA/B Forum EV hardware-token rule — CA/Browser Forum Baseline Requirements (public summaries)

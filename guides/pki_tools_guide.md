# PKI Tools Guide — OpenSSL + mkcert + step CLI

## OpenSSL — the original crypto toolbox

Already installed (ships with Git). Check: `openssl version`

### Most useful commands
```powershell
# Inspect a real certificate (what the padlock shows)
echo | openssl s_client -connect github.com:443 -servername github.com 2>$null | openssl x509 -noout -subject -issuer -dates

# Generate a private key + self-signed cert (testing only)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"

# Hash a file (fingerprint it)
openssl dgst -sha256 file.txt
```

## mkcert 1.4.4 — local HTTPS without warnings

**The magic trick:** creates a local Certificate Authority your computer trusts → local dev sites get REAL padlocks, zero warnings.

### Setup (once)
```powershell
mkcert -install          # creates local CA, trusts it in Windows + browsers
```

### Make a cert for local dev
```powershell
cd your-project-folder
mkcert localhost 127.0.0.1 myapp.local
# → creates myapp.local.pem + myapp.local-key.pem
```

Point your dev server at those files → `https://localhost` works with a real padlock.

## step CLI (smallstep) — modern cert management

Optional advanced tool for managing private CAs and short-lived certs — install via `winget search smallstep` if needed.

## How this connects to real certificates
| Situation | Tool |
|---|---|
| Public website | Let's Encrypt (free, real CA) |
| Local development | **mkcert** (auto-trusted local CA) |
| Internal company network | Private CA (openssl/step-ca) |
| Inspect any site's cert | `openssl s_client` |

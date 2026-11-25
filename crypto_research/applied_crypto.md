# Applied Real-World Cryptography

*A practical, fact-checked guide to the cryptography you actually use every day — TLS/HTTPS, certificates, encrypted messaging, password hashing, and the crypto in banking, Wi-Fi, and code signing.*

> Scope note: this report covers deployed, standardized, audited cryptography as actually used in the real world — not academic algorithms in isolation. Algorithm details are kept accurate but intentionally brief; pointers to primary sources are in the Sources section.

---

## 1. HTTPS / TLS in Practice

### What a TLS handshake actually does

When your browser connects to `https://example.com`, it performs a TLS handshake before any HTTP bytes flow:

1. **ClientHello** — the browser sends supported TLS versions, cipher suites, and extensions (supported groups/elliptic curves, key-share for TLS 1.3, ALPN for HTTP/2 vs 1.3, SNI to tell the server which hostname you want).
2. **ServerHello + certificate** — the server picks a protocol version and cipher suite and sends its **X.509 certificate chain** (server cert + intermediates, usually 2–3 certificates).
3. **Certificate validation** — the client verifies the chain up to a trusted root CA in its trust store, checks expiry, hostname (SNI), and revocation status (OCSP stapling or CRLs; soft-fail in practice).
4. **Key exchange** — both sides establish shared secrets. In TLS 1.3 this is ephemeral Diffie–Hellman (usually X25519) with the client's certificate signature binding it to the handshake — providing **forward secrecy**: compromise of the server's long-term private key does not decrypt past sessions.
5. **Session keys** — a Key Schedule (HKDF in TLS 1.3) derives distinct keys for client→server and server→client encryption and integrity.
6. **Encrypted application data** — all subsequent records are protected by an AEAD cipher.

**The hybrid trick:** asymmetric (public-key) crypto is used only to authenticate and agree on shared secrets; symmetric crypto does the bulk encryption because it is orders of magnitude faster and gives confidentiality *and* integrity (AEAD) at once.

### TLS 1.2 vs TLS 1.3 (major differences)

| | TLS 1.2 (2008) | TLS 1.3 (2018) |
|---|---|---|
| Handshake RTTs | 2 (full) / 1 (resumed) | 1 (full) / 0-RTT (resumed) |
| Key exchange | Many options incl. static RSA (no forward secrecy) | Ephemeral DH only — all key exchanges have forward secrecy |
| Cipher suites | CBC + HMAC combos, RC4/3DES legacy | AEAD only (AES-GCM, ChaCha20-Poly1305) |
| Handshake visibility | ServerHello and certs in cleartext | EncryptedExtensions and later handshake encrypted |
| Signature algorithms | RSA/DSA/ECDSA | Removes static RSA key transport, legacy hashes |

TLS 1.3 (RFC 9846) removed insecure legacy algorithms, made everything post-ServerHello encrypted, and simplified the state machine. TLS 1.2 remains widely deployed and is not "broken" when configured correctly (AEAD suites, ECDHE, strong certs), but TLS 1.3 is now dominant on major sites.

### What the padlock actually guarantees — and doesn't

**It guarantees:** the connection is encrypted in transit and authenticated to *a domain name* (the one in the certificate). It does **not** guarantee the website is trustworthy, that the operator is honest, or that content is safe. A phishing site with a valid cert gets a padlock. Padlocks mean "encrypted + authenticated to this hostname," not "safe."

---

## 2. Certificates & PKI

### X.509 structure

X.509 v3 certificates are signed data structures containing (RFC 5280):

- **Subject/issuer** fields, serial number, validity window (`notBefore`–`notAfter`)
- **Public key** of the subject + signature algorithm
- **Extensions**: Subject Alternative Names (SANs — the actual hostnames), Key Usage / Extended Key Usage (serverAuth), Basic Constraints (CA vs end-entity), Authority/Subject Key Identifiers, Certificate Policies, SCT list

### Certificate authorities

Browsers/OSes ship a **trust store** of ~100–150 root CA certificates. Chains work leaf → intermediate → root. Major commercial CAs: **DigiCert, Sectigo (formerly Comodo), GlobalSign**; free CA: **Let's Encrypt** (now issues the majority of web certs). Enterprise/private PKI (Active Directory CS, step-ca, Vault PKI) exists for internal networks.

### Certificate Transparency (CT)

Since ~2018, browsers require publicly trusted TLS certs to carry **Signed Certificate Timestamps** from multiple independent CT logs (RFC 6962). All issued certs are logged publicly; monitors detect mis-issuance. Let's Encrypt operates its own logs (Sycamore, Willow) and submits everything it issues. CT is a major deterrent against rogue-CA issuance.

### Expiry & renewal

- Let's Encrypt certs last **90 days** (6-day short-lived option exists). Industry rules (CA/B Forum Baseline Requirements) cap public TLS cert lifetime at 398 days since Sept 2020, and **47 days starting March 15, 2029**.
- Renewal is automated via **ACME** (the protocol Let's Encrypt pioneered): HTTP-01, DNS-01, or TLS-ALPN-01 challenges prove domain control. Tools: certbot, acme.sh, Caddy/Traefik/Nginx auto-renewal.
- Expired certs are the #1 self-inflicted TLS outage — automation is the norm, manual renewal the exception.

---

## 3. Encrypted Tools People Actually Use

### VeraCrypt — full-disk / container encryption

Free, open-source successor to TrueCrypt. Creates encrypted file containers or encrypts entire partitions/OS drives. On-the-fly encryption: data is decrypted transparently on read/write. Algorithms: AES, Serpent, Twofish (and cascades like AES-Twofish-Serpent), XTS mode, with PBKDF2/RIPEMD-160 or SHA-512 key derivation and a bootloader PIN/password system. The "hidden volume" feature allows plausible deniability. Cross-platform (Windows, macOS, Linux).

### Signal — E2E messaging

Signal uses the **Signal Protocol** (formerly Axolotl):

- **X3DH** (now largely superseded by **PQXDH** for post-quantum hybrid key agreement) bootstraps a shared secret from pre-published key bundles.
- The **Double Ratchet** then derives fresh message keys per message using two ratchets: a symmetric KDF chain (forward secrecy within a session) and a Diffie–Hellman ratchet that ratchets keys every round-trip (post-compromise security — healing after key theft). See signal.org specifications.
- Messages are sealed with AES-256-CBC (or ChaCha20-Poly1305) plus HMAC; sender keys for group chats. Metadata minimization: sealed sender hides who sent what from Signal's servers.
- Signal also offers **disappearing messages**, registration lock, and usernames (phone-number-private mode).

### age and GPG — file encryption

- **age** (Filippo Valsorda, 2019): deliberately tiny, modern file-encryption tool/format. X25519 (classic) or X25519+ML-KEM-768 (post-quantum hybrid) recipients, ChaCha20-Poly1305 AEAD, HKDF-SHA-256, 128-bit file key per file wrapped to each recipient — a **hybrid RSA/ECC + symmetric** construction like PGP but sane defaults, no config options, no keyrings. It can encrypt to SSH public keys for convenience.
- **GnuPG / OpenPGP**: the old standard. RSA or Curve25519 keys, hybrid encryption (asymmetric wraps a session key; symmetric encrypts the payload), signatures, web-of-trust keyservers, armor format. Powerful but notoriously complex UX — and PGP's crypto is sound while its ecosystem (key management, UX) is the weak point.

### Password managers

- **Bitwarden** (open source, self-hostable), **1Password** (closed source, polished): master password → derives encryption key (PBKDF2/Argon2) → encrypts the vault locally → syncs ciphertext to cloud. The server never sees plaintext vaults. 1Password uses **Secret Key** (a second 128-bit key) for zero-knowledge even against their own servers.
- Browser extensions autofill over TLS; vault lock/unlock, emergency access, TOTP storage included.

### Proton suite

Proton Mail/Calendar/Drive/Pass/VPN: Swiss-jurisdiction end-to-end encrypted email (OpenPGP under the hood, with automatic key exchange between Proton users), encrypted cloud storage, password manager, and VPN (WireGuard/OpenVPN-based). Notable because it offers E2E email to non-technical users at scale.

---

## 4. Cryptography in Your Daily Life

- **Wi-Fi WPA2/WPA3**: WPA2 uses **AES-CCMP** (AES-CTR + CBC-MAC) for data encryption plus **4-way handshake** (EAPOL) to derive per-session keys from PMK/PTK — replay-resistant. WPA3 replaces the PSK 4-way exchange with **SAE (Dragonfly/Dragonfly-HS)**, a password-authenticated key exchange (PAKE) resistant to offline dictionary attacks, plus forward secrecy (perfect forward secrecy via ephemeral DH) and protected management frames (802.11w). Enterprise modes: 802.1X/EAP.
- **Banking**: card numbers protected by **EMV chip** crypto (per-transaction cryptograms, asymmetric card authentication), **TLS** for online banking, **HSMs** (Hardware Security Modules — tamper-resistant devices performing crypto ops, FIPS 140-2/140-3 validated) inside banks/payment processors, and **3-D Secure** for card-not-present auth.
- **Secure Boot**: UEFI Secure Boot verifies signatures on bootloader/kernel/shim against keys in the firmware's db, establishing a chain of trust from firmware → OS. Enabled by default on most modern PCs; Microsoft's Secure Boot key enrollment (2026 plan) extends this to third-party/option-ROM code. Measured against bootkits/rootkits, not a silver bullet.
- **Code signing**: Authenticode (Windows), Apple code signing/notarization, GPG-signed commits/packages — digital signatures prove publisher identity and integrity of binaries.
- **JWT tokens**: JSON Web Tokens (RFC 7519) are `header.payload.signature` — typically RS256/ES256/EdDSA signatures (asymmetric) or HS256 (HMAC symmetric, for internal services). Used pervasively in OAuth2/OIDC APIs. Gotchas: `alg: none` confusion, algorithm confusion attacks, `kid` injection — hence strict validation libraries.

---

## 5. Password Security

### How passwords are actually stored

You **never store plaintext or fast hashes**. Instead:

1. **Salt**: a unique random value per user (stored next to the hash).
2. **Slow KDF / password hash**: bcrypt, scrypt, or **Argon2id** (winner of the Password Hashing Competition, 2015; RFC 9106). These are memory-hard/CPU-hard functions designed to make brute force expensive on both CPUs and GPUs/ASICs.
3. Store the resulting hash; verify by recomputing.

### Why NOT plain SHA-256/SHA-512 for passwords

SHA-256 is designed to be *fast* — a modern GPU can try billions of guesses/sec. A breached database of SHA-256(password) falls to rainbow tables and dictionary attacks in seconds. bcrypt (1999) adds a work factor (cost parameter, e.g. 12 → ~250ms per hash on typical hardware); scrypt adds memory-hardness; Argon2id adds both plus side-channel resistance. Even salted SHA-256 is only marginally better — still too fast.

### MFA & modern practice

- **MFA**: TOTP (RFC 6238, e.g. Google Authenticator), hardware security keys (FIDO2/WebAuthn — phishing-resistant public-key auth), push approvals. SMS codes are the weakest common factor.
- **Password managers** (see §3) generate and store unique high-entropy passwords — the single biggest real-world defense.
- Guidance (NIST SP 800-63B): favor length over arbitrary complexity rules, check against breached-password lists, no forced periodic rotation unless compromise suspected.

---

## 6. File/Folder Encryption Workflows — Tool Comparison

Consider a typical `folder_lock.py`-style script: RSA (or ECC) encrypts a random AES key per file; AES (likely GCM or CBC+HMAC) encrypts the contents. This is the correct **hybrid public-key encryption** pattern — same as age/GPG.

| Tool | Model | Best for |
|---|---|---|
| **Custom script (RSA+AES hybrid)** | Per-file or per-folder keys, recipient public keys | Learning, controlled environments; fine if built on vetted primitives (cryptography.io, PyNaCl) — dangerous if hand-rolled |
| **age** | Same hybrid idea, standardized format, modern primitives, post-quantum option | Encrypting files/folders to specific people; backup archives; git-crypt-like workflows; CLI composability |
| **GPG** | Mature, keyservers/web-of-trust, signatures | Long-established interop, signed+encrypted email attachments |
| **VeraCrypt** | Encrypted container/volume mounted as a drive | Whole-disk or large-folder confidentiality where you want files to "just be there" while unlocked; plausible deniability |
| **Cryptomator** | Transparent per-file encryption inside cloud folders (Dropbox/Drive) | Encrypting files *before* they hit untrusted cloud sync |
| **7-Zip / zip AES-256** | Password-protected archives | Quick sharing of an archive to someone who has the password (weaker: single password, no per-recipient keys) |

**When to use which:** share with specific recipients → age or GPG; protect an entire folder transparently → VeraCrypt container; protect files syncing to cloud → Cryptomator; whole-disk → VeraCrypt system encryption or OS-native (FileVault, BitLocker — note BitLocker without TPM PIN is weaker). Custom code is acceptable for education/interop but should wrap vetted libraries, not implement primitives.

---

## 7. Common Mistakes (Real-World Crypto Fails)

- **Rolling your own crypto**: The #1 sin. Implementing AES, RSA, or modes from scratch almost always introduces subtle, exploitable flaws. Use vetted libraries (libsodium, OpenSSL, `cryptography`, BoringSSL) and standard constructions.
- **ECB mode penguin**: ECB encrypts identical plaintext blocks to identical ciphertext blocks — patterns leak (the famous encrypted-Tux image). ECB is only acceptable for tiny fixed-size data (e.g., some single-block fields). Use CBC (withEncrypt-then-MAC) or, preferably, AEAD modes (GCM, ChaCha20-Poly1305).
- **IV/nonce reuse**: Reusing a nonce in GCM/CTR catastrophically leaks the keystream and can recover the auth key. Generate fresh random nonces (or use XChaCha20-Poly1305 for random nonces).
- **Hardcoded keys/secrets in source**: Keys in GitHub get scraped within minutes. Use env vars, secret managers, KMS/HSM.
- **Security through obscurity**: "The algorithm is secret" fails the Kerckhoffs principle — secrecy must reside only in keys. Obscurity can be a *layer*, never the foundation.
- **MD5/SHA-1 anywhere security-relevant**: Both broken for collision resistance (SHAttered 2017; chosen-prefix collisions since). Still fine for checksums, never for signatures/passwords.
- **RSA without OAEP / textbook RSA**: Raw RSA (textbook) is malleable; always use OAEP padding (age does). RSA keys <2048 bits are deprecated.
- **JWT `alg:none` / algorithm confusion**: Accepting attacker-supplied `alg` lets attackers forge tokens — pin algorithms server-side.
- **Ignoring metadata**: Encryption hides content, not traffic patterns, recipients, or timestamps — metadata protection requires different tools (mixnets, Tor).
- **Not verifying signatures/hosts**: Disabling cert validation (`verify=False`, `--insecure`) silently removes authentication — the most common real-world TLS failure.

---

## 8. Legal & Ethical Landscape

### Export controls & the "crypto wars"

- Until **1996**, U.S. classified cryptography as **munitions** under ITAR — export of strong crypto was treated like arms exports. Limits included key-length caps (40-bit "export-grade" crypto in browsers, famously breakable).
- **1993: Clipper Chip** — Clinton admin proposed key-escrow hardware (government-held copies of all keys). Rejected after cryptographer Matt Blaze found flaws and industry/academia pushed back; abandoned 1996.
- **1996–1999**: Clinton admin gradually liberalized — moved crypto to Commerce Control List, removed key-length limits; by **January 2000**, "any encryption of any key length" could be exported to most countries (with carve-outs for state sponsors of terrorism). This effectively ended export controls for mass-market crypto.
- Today: Wassenaar Arrangement still covers some crypto exports, but mainstream TLS/strong crypto is freely distributable. PGP, Signal, VeraCrypt are legal everywhere; some countries (China, Russia, Iran) restrict *use* domestically or require backdoor cooperation.

### Backdoor debates

- "Going dark" vs "golden key" arguments recur (FBI–Apple 2016 dispute over encrypted iPhones; EU Chat Control proposals; UK Online Safety Act client-side scanning debates).
- The cryptographic consensus: **you cannot build a backdoor only for good actors**. Math doesn't know who's asking — a key escrow or exceptional-access mechanism weakens the whole system (Keys Under Doormats, Abelson et al. 2015). E2E encryption in Signal/WhatsApp/Proton is legal; *mandating* weakened crypto is the contested policy question.
- **Why strong crypto is legal**: speech/code is protected expression (US First Amendment — *Junger v. Daley*, *Bernstein v. US*), harms are speculative, and strong crypto demonstrably prevents real harms (ransomware, fraud, surveillance abuse).

---

## Sources

- TLS 1.3 RFC 9846: https://www.rfc-editor.org/rfc/rfc9846.html
- IETF TLS 1.3 overview: https://www.ietf.org/blog/tls13/
- TLS 1.2 vs 1.3 (Microsoft VirtualClient docs): https://microsoft.github.io/VirtualClient/docs/workloads/openssl-tls12-vs-tls13/
- Let's Encrypt — CT logs: https://letsencrypt.org/docs/ct-logs/
- Let's Encrypt — certificate lifetimes: https://letsencrypt.org/docs/cert-lifetimes/
- Let's Encrypt — profiles: https://letsencrypt.org/docs/profiles/
- Let's Encrypt — FAQ: https://letsencrypt.org/docs/faq/
- Signal Double Ratchet spec: https://signal.org/docs/specifications/doubleratchet/
- Signal X3DH spec: https://signal.org/docs/specifications/x3dh/
- Signal protocol overview: https://cryptography.gundy.dev/applied/signal/
- age repository: https://github.com/filosottile/age
- age format spec (C2SP): https://github.com/C2SP/C2SP/blob/main/age.md
- age man page (recipient/identity formats): https://github.com/FiloSottile/age/blob/main/doc/age.1.ronn
- Clinton admin encryption export policy update (1999): https://clintonwhitehouse6.archives.gov/1999/09/1999-09-16-fact-sheet-on-administration-updates-encryption-export-policy.html
- New America — Crypto Wars of the 1990s: https://www.newamerica.org/insights/doomed-to-repeat-history-lessons-from-the-crypto-wars-of-the-1990s/
- Wired — Clinton relaxes crypto exports (1999): https://www.wired.com/1999/09/clinton-relaxes-crypto-exports/
- Brookings — brief history of US encryption policy: https://www.brookings.edu/articles/a-brief-history-of-u-s-encryption-policy/
- NIST SP 800-63B (digital identity guidelines): https://pages.nist.gov/800-63-3/sp800-63b.html
- RFC 9106 (Argon2): https://www.rfc-editor.org/rfc/rfc9106.html
- RFC 6238 (TOTP): https://www.rfc-editor.org/rfc/rfc6238.html
- RFC 7519 (JWT): https://www.rfc-editor.org/rfc/rfc7519.html
- RFC 5280 (X.509 PKI): https://www.rfc-editor.org/rfc/rfc5280.html
- RFC 6962 (Certificate Transparency): https://www.rfc-editor.org/rfc/rfc6962.html
- Keys Under Doormats paper (Abelson et al.): https://www.schneier.com/wp-content/uploads/2015/07/PDF-keys_under_doormats.pdf
- VeraCrypt: https://veracrypt.fr
- Proton: https://proton.me
- Bitwarden: https://bitwarden.com · 1Password: https://1password.com

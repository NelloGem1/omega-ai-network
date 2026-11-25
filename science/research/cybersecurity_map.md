# Cybersecurity, Cryptography, Privacy & Digital Trust — Master Knowledge Map

*A comprehensive synthesis of principles, algorithms, mathematics, tools, applications, and open problems. Written as a map: each section names what exists, where the deep-dives live, and what to learn next.*

**Companion documents (read these for depth — this map cites rather than duplicates them):**

| File | Covers |
|---|---|
| `~/websec_research/learning_path.md` | 12-week beginner web-security curriculum |
| `~/websec_research/payment_bypass.md` | Business-logic / authorization flaws deep-dive |
| `~/websec_research/advanced_web_vulns.md` | API security, request smuggling, cache deception, advanced SSRF, uploads |
| `~/websec_research/attacker_methodology.md` | Recon → exploitation workflow |
| `~/websec_research/defender_playbook.md` | Secure-coding defenses for Flask apps |
| `~/websec_research/race_and_logic.md`, `exploits.md`, `flask_security_deep.md`, `cli_toolkit.md`, `cheatsheets_index.md`, `docker_setup.md`, `CHALLENGES.md`, `SETUP.md` | Lab mechanics and tooling |
| `~/gh_backup/crypto_research/theory_primitives.md` | Symmetric/asymmetric/hash/signature primitives, security levels |
| `~/gh_backup/crypto_research/advanced_crypto.md` | Cryptanalysis, ZK, HE, MPC, PQC, blockchain crypto |
| `~/gh_backup/crypto_research/applied_crypto.md` | TLS/HTTPS in practice, PKI, password storage, real-world crypto fails |
| `~/gh_backup/crypto_research/certificates_free.md` | Let's Encrypt / ACME / Certbot / acme.sh |
| `~/gh_backup/crypto_research/certificates_other.md` | Paid CAs, cloud certs, self-signed, mkcert |
| `~/TOOLS.md` | Installed tool manifest (Burp, ZAP, sqlmap, nuclei, hashcat, age, gpg, Lean 4, …) |

---

## Part 0 — How to read this map

Security is one field with four layers:

1. **Cryptography** — the math that provides confidentiality, integrity, authenticity, non-repudiation.
2. **Cybersecurity** — applying that math (and much non-crypto engineering) to protect systems, networks, apps, data, and people.
3. **Privacy & digital trust** — the socio-technical layer: who controls data, how identity is proven, how systems earn trust.
4. **Security research** — the methods (ethical hacking, formal methods, protocol design) that keep the field honest.

A recurring theme: **crypto provides tools; security is the engineering of using them correctly.** Most real-world breaches are not broken math — they are misconfiguration, logic flaws, stolen credentials, and unpatched software. The attacker-methodology report makes the same point empirically.

---

# PART I — CRYPTOGRAPHY

## 1. Foundations: what cryptography must achieve

Security goals (CIA + extensions):

- **Confidentiality** — only authorized parties read the data (encryption).
- **Integrity** — data cannot be altered undetected (MACs, signatures, AEAD).
- **Authentication** — verify who sent something / who you are talking to.
- **Non-repudiation** — sender cannot later deny (digital signatures; weaker in practice than theory).
- **Availability** — systems stay up (mostly *not* crypto's job; it's an ops problem).
- **Anonymity / unlinkability** — privacy goals (mix networks, ZK, Tor).

Two families:

- **Symmetric** — one shared secret key; fast; used for bulk data.
- **Asymmetric (public-key)** — key pair; slow; used for key exchange, signatures, identity.

**The hybrid pattern** (see `theory_primitives.md` §5): asymmetric crypto bootstraps a random symmetric session key; symmetric crypto does all the bulk encryption. This is how TLS, SSH, PGP, and Signal actually work.

## 2. Symmetric cryptography

### 2.1 Block ciphers

- **AES** (Rijndael, standardized 2001): 128-bit block, key sizes 128/192/256. Substitution–permutation network: SubBytes, ShiftRows, MixColumns, AddRoundKey over 10/12/14 rounds. Hardware-accelerated (AES-NI), the default everywhere.
- **Other block ciphers**: Camellia, SM4 (Chinese national standard), Twofish/Serpent (AES finalists, rarely deployed).
- **Modes of operation** — how a block cipher encrypts multi-block messages:
  - **ECB** — each block independent; leaks patterns (the famous ECB penguin). Never use for structured data.
  - **CBC** — chained, needs random IV, malleable without MAC → padding-oracle attacks.
  - **CTR / GCM / CCM / OCB / XChaCha20-Poly1305** — authenticated modes (AEAD); the only acceptable choice today.
- **Stream ciphers**: **ChaCha20** (and XChaCha20 with 192-bit nonce) — fast in software, constant-time by design, used in TLS 1.3, WireGuard, age. Salsa20 predecessor.
- **RC4** — broken (biased keystream, WEP/Klein attacks); banned in TLS since 2015.

### 2.2 AEAD — the correct primitive

Authenticated encryption with associated data: confidentiality + integrity in one API (AES-GCM, ChaCha20-Poly1305). Associated data is authenticated but not encrypted (e.g., HTTP headers). Rule: **never encrypt-then-MAC by hand; use AEAD.**

### 2.3 Tools & applications

- `openssl enc`/`openssl` CLI, `age` (modern file encryption, X25519+ChaCha20-Poly1305), VeraCrypt (AES cascades, plausible deniability), Cryptomator, LUKS/dm-crypt (Linux full-disk), BitLocker/FileVault (OS FDE).
- Passwords: do **not** use raw AES/SHA — use memory-hard KDFs (see §7.3).

## 3. Asymmetric cryptography

### 3.1 RSA (1977)

- **Math**: choose primes p, q; n = pq; φ(n) = (p−1)(q−1); pick e coprime to φ; d = e⁻¹ mod φ. Public (n, e), private (n, d). Security rests on **integer factorization** hardness.
- **Key sizes**: 2048-bit minimum today (≈112-bit security); 3072 for ~128-bit; 4096 for longevity. `theory_primitives.md` §7 has the full comparable-security table.
- **Uses**: signatures (RSA-PSS preferred over PKCS#1 v1.5 — Bleichenbacher padding oracle attacks), encryption (RSA-OAEP only; textbook RSA is malleable), key transport.
- **Weaknesses**: large keys/signatures (~256–512 B), slow, side-channel sensitive (timing → constant-time implementations required), quantum-vulnerable (Shor).

### 3.2 Diffie–Hellman key exchange (1976)

- **Math**: in group G of prime order q with generator g: Alice sends g^a, Bob sends g^b, shared secret g^(ab). Security = **computational Diffie–Hellman (CDH)** assumption in finite fields or elliptic curves.
- **Ephemeral DH** (DHE/ECDHE) gives **forward secrecy**: compromise of long-term keys does not expose past sessions. Static DH does not — a major reason TLS 1.3 mandates (EC)DHE.

### 3.3 Elliptic-curve cryptography (ECC)

- **Math**: points on curve y² = x³ + ax + b over finite field F_p (or F_2^m). Group law = chord-and-tangent addition; scalar multiplication is one-way (ECDLP). ~10× smaller keys than RSA for equal security: 256-bit ECC ≈ 3072-bit RSA.
- **Curves in use**:
  - **Curve25519 / X25519** — ECDH; fast, complete addition formulas (no invalid-curve edge cases), the TLS/WireGuard/SSH default.
  - **Ed25519** — EdDSA signatures over Curve25519; deterministic nonces (no RNG needed), small fast signatures, used by OpenSSH, age, minisign, Tor.
  - **P-256/P-384 (NIST curves)** — widely deployed, some controversy over possible backdoors (nothing proven); require careful validation.
  - **secp256k1** — Bitcoin/Ethereum.
- **Invalid-curve attacks**: implementations must validate public keys lie on the curve; twist/security of small-order points matters.

### 3.4 Other asymmetric schemes

- **ElGamal** — DH-based encryption; malleable (needs hashed ElGamal or KEM usage); basis of Cramer–Shoup (CCA-secure).
- **Goldwasser–Micali, Rabin, Paillier** — textbook/less common; Paillier gives additive homomorphism (used in some e-voting/crypto-currency schemes).
- **Isogeny crypto (SIDH/SIKE)** — was a PQC candidate; **broken in 2022** (Castryck–Decru attack) — a lesson in cryptanalysis humility.

### 3.5 Pairing-based cryptography & aggregate signatures

- **Pairings** (Weil/Tate/optimal ate on BN/BLS curves like BLS12-381): map two groups into a third, enabling unique properties — identity-based encryption (Boneh–Franklin), short group signatures, and **aggregate signatures** (BLS): n signatures verify as one — used in Ethereum consensus (attestations), TLS certificate compression research, blockchain scaling.
- **Cost**: pairing computations are expensive; used where aggregation pays off.

### 3.6 KEMs — the modern view of encryption

- Public-key *encryption* is being replaced by **Key Encapsulation Mechanisms**: asymmetric crypto only wraps a symmetric key; symmetric AEAD does the data. This separation simplifies proofs and avoids CCA pitfalls.
- Standards: RSA-KEM / ECIES-style KEMs historically; **ML-KEM** is the PQC KEM (§6). HPKE (RFC 9180) standardizes KEM+KDF+AEAD composition for application developers — prefer HPKE over hand-rolled hybrids.

## 4. Hash functions

- **Purpose**: fixed-size digest with preimage/second-preimage/collision resistance; also KDFs, MACs, commitments, PoW.
- **SHA-2 family**: SHA-224/256/384/512 (Merkle–Damgård, length-extension vulnerable when used naively as MAC — use HMAC). SHA-256 still fine for integrity; NIST moving on.
- **SHA-3 / Keccak**: sponge construction, different design lineage, no length extension; used in Ethereum, many protocols.
- **BLAKE2/BLAKE3**: faster than SHA-2/3, tree hashing built in; default in many modern systems (age uses BLAKE2b).
- **MD5, SHA-1**: collision-broken (SHAttered 2017 for SHA-1) — usable only for non-security checksums.
- **Password hashing** is a different discipline: slow, salted, memory-hard KDFs — **Argon2id** (winner of Password Hashing Competition, 2015), scrypt, bcrypt, PBKDF2 (legacy fallback). See `applied_crypto.md` §5.

## 5. Digital signatures & non-repudiation

- **What they prove**: "holder of private key k signed message m" — assuming secure key storage. They do **not** prove the human intended it (key theft, coercion, endpoint compromise all break this).
- **Schemes**: RSA-PSS, ECDSA (nonce-reuse catastrophic — Sony PS3, blockchain thefts; deterministic k via RFC 6979), **EdDSA/Ed25519** (preferred: deterministic by design), Schnorr signatures (Bitcoin Taproot, simpler proofs).
- **Applications**: code signing (GPG, Sigstore/cosign for supply chain), software update verification, document signing, TLS client certs, eIDAS qualified signatures (EU legal non-repudiation).

## 6. Post-quantum cryptography (PQC)

- **Threat**: Shor's algorithm solves factoring & ECDLP in polynomial time on a large quantum computer → RSA, DH, ECDH, ECDSA, EdDSA all fall. Grover halves symmetric security (AES-256 → ~128-bit; ChaCha20-256 fine).
- **Harvest-now-decrypt-later**: adversaries store ciphertext today, decrypt when quantum arrives → long-lived secrets need PQC **now**.
- **NIST PQC standardization (finalized Aug 2024)**:
  - **ML-KEM (Kyber)** — lattice-based KEM (module-LWE), key encapsulation, TLS replacement for ECDH.
  - **ML-DSA (Dilithium)** — lattice signatures, TLS/firmware/code signing.
  - **SLH-DSA (SPHINCS+)** — stateless hash-based signatures (conservative, large/slow — backup).
  - **FN-DSA (Falcon)** — compact fast signatures (standardized later, 2024/25).
  - **HQC** — code-based KEM selected as backup.
- **Migration**: hybrid key exchange (X25519+ML-KEM) deployed in TLS 1.3/Chrome, Cloudflare, Signal; CNSA 2.0 timelines (US gov: PQC by ~2030-2033); "crypto agility" — design systems so algorithms are pluggable.
- **Status**: lattice assumptions are newer and less battle-tested than factoring/ECC; expect continued cryptanalysis (see SIKE cautionary tale).

## 7. Advanced cryptographic primitives

### 7.1 Zero-knowledge proofs (ZKPs)

- **Idea**: prove knowledge of a witness w satisfying relation R(x,w) without revealing w. Properties: completeness, soundness, zero-knowledge.
- **Interactive proofs** → **Fiat–Shamir heuristic** → non-interactive (in ROM).
- **zk-SNARKs** (Groth16 etc.): tiny proofs, need trusted setup (toxic waste); used in Zcash, rollups.
- **zk-STARKs**: no trusted setup, post-quantum-ish (hash-based), larger proofs; StarkNet, Tornado-style systems.
- **Bulletproofs**: no setup, larger; confidential transactions (Monero).
- **Sigma protocols** (Schnorr, Chaum–Pedersen): building blocks for anonymous credentials, threshold sigs.
- **Applications**: blockchain scalability (zk-rollups), private identity/credentials, verifiable computation, password proofs.

### 7.2 Homomorphic encryption (HE)

- **Somewhat HE**: Paillier (additive), BFV/BGV/CKKS (leveled, approximate arithmetic for ML).
- **Fully HE (FHE)**: Gentry's 2009 blueprint — bootstrapping refreshes ciphertext; schemes: **TFHE** (fast boolean gates), **CKKS** (approximate reals, ML inference), **BGV/ BFV**.
- **Status**: real but slow (seconds–minutes per op); Microsoft SEAL, OpenFHE, Zama toolchain. Use case: compute on encrypted data in untrusted clouds (confidential analytics, private genomics, encrypted search).

### 7.3 Multi-party computation & secret sharing

- **MPC**: k parties compute f(x₁…xₙ) revealing only the output (Yao garbled circuits, GMW, BGW). Applications: private auctions, joint fraud detection, threshold key management.
- **Secret sharing**: Shamir (t-of-n via polynomial over GF(p)); proactive/verified variants. Used in key ceremonies, HSM clusters, DNSSEC root key ceremonies, crypto custody.
- **Threshold signatures**: (t-of-n) Schnorr/FROST — no single private key exists (Fireblocks, smart-contract wallets, Tor directory authorities use threshold crypto).

### 7.4 Other notable primitives

- **Oblivious transfer, private information retrieval (PIR)**, **searchable encryption** (leaky — see §privacy critiques), **functional encryption**, **attribute-based encryption**, **verifiable delay functions (VDFs)**, **proof-of-work/proof-of-stake** as cryptographic-economic primitives.

## 8. Real-world cryptographic protocols

Deep-dives: `applied_crypto.md`, `certificates_*.md`. Summary:

- **TLS 1.3**: handshake = ephemeral ECDHE (+ML-KEM hybrid increasingly) → AEAD session keys (HKDF key schedule); mutual auth via X.509 certificates; 0-RTT for resumption (replay risk); certificate revocation via OCSP stapling / CRLite. Guarantees: confidentiality + integrity of the channel — **not** of endpoints.
- **SSH**: host-key verification, user auth (keys > passwords), agent forwarding risks.
- **Signal protocol** (X3DH + Double Ratchet): E2E encrypted messaging with forward secrecy + post-compromise security; metadata still visible to server (sealed sender mitigates).
- **PGP/GPG**: web-of-trust alternative to PKI; painful UX; used for email/signing/git commits.
- **age / libsodium / Tink**: modern "just use this" libraries — NaCl/libsodium (Daniel J. Bernstein) is the reference for "don't roll your own."
- **WireGuard**: Noise protocol framework — minimal crypto, modern (Curve25519, ChaCha20-Poly1305, BLAKE2); kernel-space, radically simpler than IPsec/OpenVPN.

## 9. PKI & certificates

- **X.509 chain**: leaf ← intermediates ← root; root in trust store (OS/browser). Chain validation = signatures + validity + name constraints + revocation (CRL/OCSP) + CT logs.
- **Web PKI**: Let's Encrypt (free, ACME protocol, 90-day certs, automation-first) vs. paid CAs (EV/OV/DV — the "green bar" is dead; all DV now). Details in `certificates_free.md` / `certificates_other.md`.
- **ACME challenges**: HTTP-01, DNS-01 (wildcards), TLS-ALPN-01.
- **Beyond web PKI**: private PKI, SPIFFE/SPIRE (workload identity in cloud-native), SSH CA (Netflix/Bastion-style short-lived certs), mTLS in service meshes (Istio/Linkerd).
- **Failure modes**: mis-issued certs (DigiNotar 2011 → bankruptcy), CA compromise, hostname validation bugs, cert expiry outages (Oculus/Fastly incidents), trust-store bloat.

### 9.1 Certificate validation — what a client actually checks

1. Chain builds to a trusted root (path validation, name constraints).
2. Each signature verifies; validity window OK; EKU/SAN matches hostname (exact or wildcard rules).
3. Revocation status (OCSP stapled / CRL / CRLite); CT log inclusion proves publicly logged issuance.
4. Modern browsers require CT; pinning (HPKP) is dead — deprecated after abuse; use Expect-CT/CSP `report-uri` instead.

### 9.2 Enterprise identity on top of PKI

- **mTLS everywhere** in service meshes (SPIFFE/SPIRE issues short-lived SVIDs — workload identity replaces IP-based trust).
- **SSH CA** model: host + user certs signed by an offline-rooted CA → short-lived access, no authorized_keys sprawl (used by Netflix BLESS, smallstep).
- **Code signing**: Authenticode (Windows), Apple notarization, GPG/minisign, Sigstore (keyless signing via Fulcio CA + Rekor transparency log + ephemeral certs from OIDC identity) — the modern answer to "who built this."

---

# PART II — CRYPTANALYSIS & SECURITY FOUNDATIONS

*This part answers: "how does the math actually fail, and how do we know a scheme is secure?" The answers are more nuanced than "it's math, trust it."*

## 10. The mathematics underneath

| Area | Concepts | Where used |
|---|---|---|
| Number theory | primes, modular arithmetic, Fermat/Euler, discrete log, Pohlig–Hellman, CRT | RSA, DH, ElGamal |
| Abstract algebra | groups, rings, fields, finite fields GF(p)/GF(2ⁿ) | ECC, AES field ops, Shamir |
| Elliptic curves | group law, point counting ( Schoof ), pairing-friendly curves (BLS12-381) | ECDSA/EdDSA, BLS aggregate sigs |
| Lattice theory | LLL/BKZ reduction, shortest vector (SVP/CVP), Module-LWE | ALL post-quantum winners |
| Coding theory | linear codes, syndrome decoding | McEliece, HQC (PQC backups) |
| Hash functions | sponge/MD constructions, collision bounds | SHA-2/3, BLAKE, STARKs |
| Probability/complexity | advantage, negligible functions, PPT adversaries | security definitions |
| Information theory | Shannon entropy, one-time pad, Kerckhoffs's principle | secrecy fundamentals |

**Kerckhoffs's principle** (1883): security must reside in the key, not the algorithm's secrecy. Shannon's maxim: *the enemy knows the system.* The one-time pad is the only provably unbreakable cipher (Shannon 1949) — and it requires a key as long as the message, used once, distributed secretly. Everything practical is a compromise against those impossible requirements.

### 10.1 How to actually learn the math

- **Finite fields / modular arithmetic**: any intro number theory (or *A Friendly Introduction to Number Theory*). You need comfort with mod-p arithmetic before ECC makes sense.
- **Elliptic curves**: *Guide to Elliptic Curve Cryptography* (Hankerson–Menezes–Vanstone) is the standard reference; for intuition, the "chord-and-tangent" visualizations and 2×2 toy curves over small primes.
- **Lattices (PQC)**: the *Lattice Estimator* tool + the NIST submission docs; start with the "Learning With Errors" intuition (noisy linear equations are hard to solve).
- **Complexity**: Sipser's *Introduction to the Theory of Computation* — enough to read "PPT adversary" and "negligible advantage" precisely.
- **In this repo**: Lean 4 + Mathlib is installed — the endgame for *verifying* crypto math rather than just learning it.

## 11. Cryptanalysis — attacking cryptography legally/academically

Detailed taxonomy in `advanced_crypto.md` §1:

- **Brute force / exhaustive key search** — bounded by key length; why 128-bit symmetric is comfortable, 80-bit is not.
- **Frequency analysis** — classical ciphers (substitution, Vigenère); index of coincidence; modern relevance: traffic analysis.
- **Meet-in-the-middle** — doubles effective brute-force cost for double encryption (2DES → 2^80 not 2^112, hence 3DES deprecated).
- **Differential cryptanalysis** (Biham–Shamir) — chosen-plaintext attack tracking XOR differences through rounds; how AES was validated.
- **Linear cryptanalysis** (Matsui) — approximating rounds with linear relations.
- **Algebraic attacks** — express cipher as polynomial system; Gröbner bases.
- **Related-key attacks** — AES-256 reduced-round results; why key separation matters.
- **Implementation attacks** — see §12.
- **Protocol attacks** — see §13.

## 12. Side-channel & implementation security

- **Timing attacks**: RSA/ECDSA private-key recovery via operation timing (Brumley–BONEH 2003); constant-time code (no branches on secrets).
- **Power analysis**: DPA/SPA on smartcards, TPMs, HSMs — differential power analysis extracts keys from ~thousands of traces.
- **Cache attacks**: Flush+Reload, Prime+Probe — cross-VM key extraction (Spectre/Meltdown family 2018 blurred CPU/microarchitecture into crypto security).
- **Fault injection**: voltage/clock glitching, laser fault attacks → P-256 nonce corruption → key recovery ("bellcore attack").
- **Rowhammer**, **EM emanations** (TEMPEST/van Eck), **acoustic** key extraction.
- **Mitigations**: constant-time libraries (libsodium, BoringSSL), masking/hiding countermeasures, secure elements/HSMs, side-channel evaluation labs (Common Criteria, FIPS 140-3).

## 13. Protocol security & formal methods

- **Security models**: Dolev–Yao adversary (network attacker controls channel, cannot break crypto); Canetti's UC framework (Universal Composability — "protocols are secure if they're UC-secure").
- **Protocol flaws are logic flaws**: replay, reflection, unknown key-share, downgrade attacks — the math can be perfect and the protocol still broken (TLS renegotiation, SSH Terrapin 2023, IKE padding-oracle).
- **Symbolic vs. computational proofs**: Tamarin, ProVerif, Scyther — automatic protocol verifiers; applied to TLS 1.3, 5G AKA, Signal, WireGuard analyses.
- **Key lifecycle**: generation (CSPRNG), distribution, storage (HSM/TPM/secure enclave), rotation, revocation, destruction. Most "crypto failures" are lifecycle failures.
- **Randomness failures**: Debian OpenSSL bug (2008, predictable keys), Dual_EC_DRBG backdoor suspicion (NIST withdrew 2014), IoT devices with hardcoded/seeded RNGs → factorable keys at internet scale.

## 13b. Common cryptographic failure modes (the "how it actually breaks" list)

Nearly every real-world crypto incident is one of these:

1. **Nonce/IV reuse** — AES-GCM nonce reuse leaks auth key + plaintext XOR; ECDSA nonce reuse leaks private key; ChaCha20 nonce reuse similar. *Rule: never reuse a nonce under one key.*
2. **Malleability** — CBC without MAC, textbook RSA, ECB: attacker flips bits predictably. *Fix: AEAD.*
3. **Padding-oracle attacks** — Bleichenbacher '98/'98 on RSA PKCS#1 v1.5 (still seen in old TLS stacks), Vaudenay on CBC. *Fix: OAEP/PSS, AEAD, constant-time error handling.*
4. **RNG failure** — predictable seeds/keys (Debian OpenSSL 2008, blockchain wallets from weak entropy, PlayStation 3 ECDSA nonce). *Fix: audited CSPRNGs (getrandom, /dev/urandom), never seed from time/PID.*
5. **JWT mistakes** — `alg: none`, RS256→HS256 key-confusion, weak HMAC secrets (crackable → forge tokens). *Tool: `jwt_tool`.*
6. **Hardcoded keys/secrets** — in source, mobile apps, firmware, CI logs; scanners (gitleaks/trufflehog) + rotation.
7. **Key storage** — keys next to ciphertext, in env vars, in git, in browser localStorage; use HSM/KMS/keystore + envelope encryption.
8. **Downgrade/wrong-curve** — protocol downgrade attacks (POODLE, FREAK, Logjam), invalid-curve ECDH, missing certificate validation (`verify=False` in Python requests — an epidemic).
9. **Length-extension** — naive `SHA256(secret || msg)` as MAC; *fix: HMAC or SHA-3/BLAKE2.*
10. **"Don't roll your own"** — homebrew ciphers, custom KDFs, modified AES. Academic exercise OK; production never. Use libsodium/age/Tink/BoringSSL.

## 14. Hardness assumptions & "provable" security

- Standard assumptions: factoring (RSA), discrete log (DH/DSS), CDH/DDH, LWE (lattices), one-wayness of hash functions.
- **Provable security**: reduce breaking the scheme to solving a believed-hard problem (e.g., EUF-CMA security of Schnorr under discrete log + ROM).
- Caveats: reductions are asymptotic, often in idealized models (ROM ≠ standard model); "reduction loss" matters; quantum changes everything (Shor kills factoring/DL; Grover halves symmetric).
- **Unsolved**: whether lattice problems used in NIST PQC are truly quantum-hard at scale; fine-grained complexity; P vs NP remains open (implies factoring might be easy someday).

## 15. Standards & governance bodies

- **NIST** (US): AES, SHA-2/3, post-quantum standards, FIPS 140-3 (crypto modules), SP 800- series (key management SP 800-57, TLS guidance SP 800-52).
- **IETF**: TLS (RFC 8446), JOSE (JWT), WireGuard docs, ACME RFC 8555.
- **ITU-T**: X.509, X.500 directory.
- **ISO/IEC JTC1 SC27**, **Common Criteria** (security evaluation), **FIPS**, **eIDAS** (EU trust services regulation).
- **CA/Browser Forum**: Baseline Requirements governing public TLS CAs.
- **Signal/age/libsodium**: de-facto modern standards set by working code, not committees.

---

# PART III — CYBERSECURITY DOMAINS

*Where cryptography meets messy reality: networks, software, hardware, humans, and organizations. The deep web-app corpus lives in `~/websec_research/`; this part maps the whole territory.*

## 16. Security engineering mindset

Before domains — the cross-cutting principles (expanded in `defender_playbook.md` §1):

- **Never trust client input**; validate server-side, allowlist-style.
- **Least privilege** everywhere (processes, DB users, IAM roles, network segments).
- **Defense in depth** — assume each layer fails; combine controls.
- **Fail securely** — deny by default; errors must not leak data or bypass auth.
- **Secure defaults**; make the secure path the easy path.
- **Complete mediation** — check authorization on every request, every time.
- **Separation of duties**, **economy of mechanism** (small auditable TCB), **psychological acceptability** (usable security).
- **Patch & dependency hygiene** — most breaches exploit known CVEs in unpatched software.

## 17. Network security

- **OSI/Layers**: physical → data link (MACsec, 802.1X) → network (IPsec, firewalls, segmentation) → transport (TLS/DTLS, TCP/UDP security) → session/presentation (Kerberos, SSH) → application.
- **Perimeter → Zero Trust**: "never trust, always verify" — micro-segmentation, mTLS everywhere, identity-aware proxies; BeyondCorp model. VPNs concentrate risk; Zero Trust distributes it.
- **Firewalls**: stateless vs. stateful; NGFW (L7 inspection); WAF (web-specific, see §18).
- **IDS/IPS**: signature-based (Snort/Suricata) vs. anomaly/ML-based; Zeek for network metadata; placement matters (inline IPS vs. passive IDS).
- **VPNs**: IPsec (IKEv2, complex), OpenVPN (TLS-based), **WireGuard** (modern, preferred), Tailscale/Headscale (WireGuard mesh + identity).
- **DNS security**: DNSSEC (signed DNS, authenticity not confidentiality), DoH/DoT (encrypted DNS), DNS filtering (Pi-hole, NextDNS), tunneling detection.
- **Email security**: SPF/DKIM/DMARC (anti-spoofing), MTA-STS/TLS-RPT, phishing remains #1 initial vector.
- **Wireless**: WPA2/WPA3 (SAE replaces PSK-handshake KRACK issues), evil-twin detection, enterprise 802.1X/EAP.
- **Network forensics**: full packet capture (Arkime/Moloch), NetFlow/sFlow, Zeek logs.
- **Segmentation & air gaps**: VLANs, microsegmentation, data-diode/air-gap realities (Stuxnet crossed air gaps).

## 17b. Network attack patterns & defenses (attacker view)

- **MITM**: ARP spoofing, rogue DHCP, evil-twin Wi-Fi, DNS hijack, BGP hijack (route leaks — happened to major CDNs), captive-portal phishing. *Defenses*: TLS (authentication defeats most MITM), 802.1X, DHCP snooping, DNSSEC, RPKI for BGP.
- **Scanning/recon**: nmap SYN scans, banner grabbing, ASN/IP-range enumeration; defenders see this constantly — honeypots (Cowrie, T-Pot) turn scans into intel.
- **Lateral movement concepts**: pass-the-hash/ticket, credential dumping (Mimikatz), token theft, RDP/SSH pivoting, living-off-land binaries (LOLBins); detection via identity telemetry, not just network.
- **Exfiltration channels**: DNS tunneling, HTTPS to bulletproof hosts, cloud storage abuse, steganography; DLP + egress anomaly detection.
- **DoS/DDoS**: volumetric (Cloudflare/Akamai scrubbing), protocol (SYN flood, amplification — DNS/NTP/memcached), application-layer (Slowloris, HTTP/2 rapid reset); rate limiting + anycast + upstream filtering.

## 18. Web & application security

*Primary corpus: `~/websec_research/` — the most developed area of this research.*

- **OWASP Top 10 (2025)**: broken access control, cryptographic failures, injection, insecure design, security misconfiguration, vulnerable components, auth failures, software/data integrity failures, logging failures, SSRF.
- **Injection**: SQLi (parameterized queries/ORM only), NoSQLi, command injection, template injection (SSTI), LDAP/XPath, header injection (CRLF).
- **XSS**: reflected/stored/DOM; mitigations: output encoding, CSP, Trusted Types, HttpOnly cookies.
- **CSRF**: token-based, SameSite cookies, Origin checks.
- **AuthN/AuthZ**: session management, JWT pitfalls (alg=none, key confusion, weak secrets — see `jwt_tool`), OAuth2/OIDC misconfigurations, password reset flaws, MFA fatigue.
- **Access control**: IDOR/BOLA (the payment-bypass family — `payment_bypass.md`), privilege escalation, forced browsing, mass assignment.
- **Business logic**: race conditions (`race_and_logic.md`), workflow bypasses, price/quantity tampering — scanners miss these; methodology report covers the mindset.
- **Server-side**: SSRF (cloud metadata 169.254.169.254), deserialization, path traversal, file upload (`advanced_web_vulns.md` §5), XXE, request smuggling (§3), cache deception/poisoning (§3–4 of advanced report), prototype pollution.
- **Client-side**: clickjacking (frame-ancestors), postMessage abuse, DOM clobbering, supply-chain (malicious npm packages — see §22 secure SDLC).
- **WAF limits**: useful as a speed bump; not a fix for code flaws; bypass research is an arms race.

## 19. Operating-system & endpoint security

- **Linux**: discretionary access control (permissions, capabilities), **SELinux/AppArmor** (MAC), namespaces/cgroups (containers), auditd, seccomp-bpf, secure boot, FDE (LUKS), kernel attack surface (eBPF risks).
- **Windows**: UAC, Defender/EDR, WDAC/AppLocker, Credential Guard, BitLocker, registry ACLs, PowerShell logging/AMSI.
- **macOS**: SIP, Gatekeeper, TCC privacy model, FileVault, notarization.
- **Endpoint detection & response (EDR)**: telemetry → behavioral detection; CrowdStrike/SentinelOne/Wazuh (open-source).
- **Memory safety**: ~70% of severe CVEs are memory-corruption (Microsoft/Google stats) → Rust, memory-safe languages, ASan/MSan/UBSan fuzzing, CHERI capability hardware.
- **Secure boot chain**: firmware → bootloader → kernel → userspace; measured boot + remote attestation (TPM).

## 20. Database security

- **Access control**: least-privilege DB users per app; no app-as-admin.
- **Injection**: parameterized queries/ORM — the #1 rule (`defender_playbook.md` §2.1).
- **Encryption**: TLS in transit, TDE/encrypted columns at rest; application-level encryption (envelope encryption) for sensitive fields.
- **Auditing**: query logging, Database Activity Monitoring (DAM), immutable audit trails.
- **Data-level**: row-level security (Postgres RLS), column masking, dynamic data masking, tokenization/vaulting (Vault, AWS KMS envelope pattern).
- **Backups**: encrypted, tested restores, offline/immutable copies vs. ransomware.

## 21. Cloud & IAM security

- **Shared responsibility model**: provider secures *of* cloud; customer secures *in* cloud — most cloud breaches are misconfiguration, not provider failure.
- **IAM**: roles over users/keys; MFA mandatory; permission boundaries; just-in-time access; access reviews; AWS IAM Access Analyzer / GCP Policy Analyzer / Azure PIM.
- **Network**: security groups/NACLs, private subnets, VPC flow logs, egress control, NAT gateways.
- **Data**: KMS envelope encryption, S3 bucket policies (public exposure is the classic fail), object lock/immutability, secrets managers (never env vars in code).
- **Workload identity**: SPIFFE/SPIRE, IRSA (EKS), instance metadata service risks (SSRF → credential theft).
- **Cloud posture**: CSPM tools (Wiz, Orca, Prowler open-source), benchmarks CIS, infrastructure-as-code scanning (Checkov, tfsec).
- **Serverless/containers**: minimal attack surface, but secrets-in-env and over-privileged execution roles persist; container escape is rarer but real (runC CVEs).

## 22. Mobile security

- **iOS**: sandboxing, App Transport Security (ATS), Keychain, Secure Enclave, code signing + notarization, app attest.
- **Android**: sandbox per app, SELinux, Play Integrity API, keystore/TEE, scoped storage.
- **Threats**: repackaged apps, overlay attacks, insecure IPC (Intents/URL schemes), root/jailbreak detection limits, side-loaded malware, mobile phishing (AiTM proxies defeat SMS MFA → passkeys help).
- **MDM/EMM**: enterprise app wrapping, device compliance, conditional access.
- **App shielding**: RASP, obfuscation (limited value vs. determined attackers but raises cost).

## 23. IoT & OT/ICS security

- **IoT**: default passwords (Mirai botnet 2016 → DNS outage), unpatchable firmware, insecure update channels (signed OTA essential), segmentation from corporate LAN.
- **OT/ICS**: PLCs/SCADA, safety instrumented systems — can't just "patch and reboot"; Purdue model segmentation; Stuxnet as canonical case study; IEC 62443 standard.
- **Supply chain**: hardware Trojans, counterfeit chips, BMC/IPMI exposure.

## 24. Social engineering & the human layer

- **Phishing**: credential harvest, AiTM (evilginx-style) → session cookie theft; smishing/vishing; business email compromise (BEC) is higher-loss than malware.
- **Defenses**: FIDO2/passkeys (phishing-resistant MFA), DMARC, security-awareness training (mixed evidence — pair with technical controls), email link rewriting, out-of-band verification for payments.
- **Physical**: tailgating, USB drops, evil-maid attacks (LUKS/header protection), dumpster diving.
- **Insider threat**: least privilege, DLP, UEBA, separation of duties, offboarding checklist.

---

# PART IV — DEFENSIVE SECURITY & SECURITY OPERATIONS

*The flip side of offense: find flaws before attackers do, detect what slips through, respond when it does. Offensive skill and defensive rigor are two halves of the same discipline.*

## 24b. Application security specifics (beyond web)

- **API security** (expanded in `advanced_web_vulns.md` §1): BOLA/IDOR is the dominant API flaw; GraphQL introspection + nested-query DoS + batching abuse; mass assignment; excessive data exposure (returning whole ORM objects); inconsistent rate limits across endpoints.
- **gRPC/RPC**: reflection enabled in prod leaks schema; HTTP/2 rapid-reset DoS; metadata injection.
- **Webhooks/callbacks**: unsigned or replayable callbacks → forged events; verify signatures (Stripe-style HMAC), enforce freshness windows.
- **File handling**: path traversal (`../../`), symlink races, decompression bombs, polyglot files; store uploads outside webroot, rename, serve via signed URLs.
- **Deserialization**: Java (`readObject`), PHP (`unserialize`), Python `pickle`, .NET `BinaryFormatter` — remote code execution primitives; prefer JSON with strict schemas.
- **XXE**: XML parsers resolving external entities → file read/SSRF; disable external entities or use JSON.
- **Race conditions** (see `race_and_logic.md`): TOCTOU on filesystem/quotas, double-spend in payment flows, coupon reuse; defenses: atomic DB ops, unique constraints, idempotency keys, pessimistic locking.

## 25. Threat modeling

- **STRIDE** (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) — per-element analysis.
- **Process**: define scope → diagram data flows (DFD) → identify threats per STRIDE → prioritize → mitigate.
- **Tools**: Microsoft Threat Modeling Tool, OWASP Threat Dragon, IriusRisk, pytm (Python-as-code).
- **Attack trees** (Schneier), **PASTA**, **LINDDUN** (privacy threat modeling — pairs with §28).
- **When**: at design time (cheapest fixes), before major releases, after incidents.

## 26. Secure SDLC & security engineering

- **Phases**: requirements (security user stories, abuse cases) → design (threat model, secure architecture) → implementation (SAST, secrets scanning, lint rules) → test (DAST, fuzzing, pentest) → deploy (hardening, SBOM) → operate (monitoring, patching).
- **Shift-left vs. shift-everywhere**: gates early, but verification continues through production.
- **SBOM** (Software Bill of Materials): CycloneDX/SPDX formats; required by US EO 14028 for federal suppliers; enables rapid CVE impact analysis (Log4Shell showed why).
- **SAST/DAST/SCA/IaC scanning**: Semgrep, CodeQL, SonarQube; ZAP/Burp for DAST; Dependabot/Renovate/OSV-Scanner for deps; Checkov/tfsec for IaC.
- **Fuzzing**: AFL++, libFuzzer, honggfuzz — coverage-guided; how most memory bugs are found now.
- **Secrets scanning**: gitleaks, trufflehog, GitHub push protection — leaked keys are a top breach cause.
- **Bug bounties & responsible disclosure**: HackerOne/Bugcrowd/Intigriti; ISO 29147/30111 disclosure standards; safe-harbor policies.

## 27. Vulnerability management

- **Lifecycle**: discover (scanners, audits, researcher reports) → triage → assess severity → prioritize → remediate/mitigate/accept → verify → track SLA.
- **CVSS v4.0**: base/temporal/environmental scoring (0–10); pair with EPSS (exploit prediction) and KEV (CISA Known Exploited Vulnerabilities catalog) — patch KEV first.
- **CVE/NVD** ecosystem; **CWE** weakness taxonomy; **CAPEC** attack patterns.
- **Patch management**: test environments, maintenance windows for OT, virtual patching via WAF when patching is impossible, EOL software inventory.
- **Vuln scanners in this lab**: nuclei (14k templates), nikto, whatweb, searchsploit — see `cli_toolkit.md` and TOOLS.md.

## 28. Privacy engineering & data protection

### 28.1 Regulatory landscape

- **GDPR** (EU, 2018): lawfulness basis, data minimization, purpose limitation, storage limitation, rights (access, erasure, portability, objection), DPIAs for high-risk processing, breach notification ≤72h, fines to 4% global revenue.
- **CCPA/CPRA** (California), **PIPEDA** (Canada), **LGPD** (Brazil), **DPDP** (India), sector rules: HIPAA (US health), PCI-DSS (payments), GLBA (finance), FERPA (education).
- **Schrems II** (2020): EU–US data transfers need supplementary measures (DPF adequacy, SCCs + encryption).

### 28.2 Privacy-enhancing technologies (PETs)

- **k-anonymity / l-diversity / t-closeness**: generalization/suppression for dataset release (Sweeney 2002; Netflix Prize de-anonymization showed limits).
- **Differential privacy**: randomized responses/query answers with ε-bounds; Google RAPPOR, Apple/Google telemetry, US Census 2020; formal guarantee independent of auxiliary info.
- **Federated learning**: train on-device, share gradients; gradient-leakage attacks show it's not automatically private → combine with DP/secure aggregation.
- **Homomorphic encryption & MPC** (see §7): private analytics, joint computation without data sharing.
- **Synthetic data**, **data clean rooms**, **pseudonymization vs. anonymization** (pseudonyms are still personal data under GDPR).
- **PETs critique**: most add complexity + utility loss; "privacy by design" (Cavoukian's 7 principles) argues for data minimization first — don't collect what you don't need.

### 28.3 Privacy operations

- **Data mapping/RoPA**, retention schedules, consent management (CMPs), DSAR workflows (access/erasure requests), privacy impact assessments, breach notification runbooks, vendor DPAs, cookie/consent enforcement (ePrivacy directive).

## 29. Digital identity & authentication

- **Passwords**: hashed with Argon2id/scrypt/bcrypt + salt + pepper; breached-password screening (k-anonymity HIBP API); length > complexity; NIST SP 800-63B (no periodic forced rotation, allow paste managers, check against breach lists).
- **MFA**: SMS (weak — SIM swap, AiTM), TOTP (better), push (fatigue attacks → number matching), **FIDO2/WebAuthn passkeys** (phishing-resistant, asymmetric, platform/roaming authenticators). This is the single biggest account-security upgrade available.
- **OAuth 2.0 / OIDC**: authorization (delegated access) vs. authentication (identity); flows: auth code + PKCE (the correct modern flow), implicit deprecated, client credentials for M2M; common bugs: redirect_uri validation, state/nonce missing → CSRF/login-confusion, token leakage via referer.
- **SAML**: enterprise SSO; XML signature wrapping attacks historically.
- **SSO/IGA**: centralized provisioning/deprovisioning (SCIM), joiner-mover-leaver lifecycle.
- **Identity proofing**: document verification, liveness detection — for KYC/regulated onboarding.
- **Workload/machine identity**: mTLS, SPIFFE IDs, API keys (rotate, scope narrowly, vault them — never in git).

## 30. Secure communications

- **At rest**: FDE (FileVault/BitLocker/LUKS/VeraCrypt), encrypted backups, encrypted object storage.
- **In transit**: TLS everywhere (no exceptions — use HSTS, cert pinning sparingly), SSH for admin access, WireGuard/IPsec VPNs, DoH/DoT for DNS, encrypted email (S/MIME, PGP — adoption poor), Signal/Session/Matrix+Element for messaging.
- **Metadata problem**: E2E encryption hides content, not who-talks-to-whom/when/how-much — traffic analysis remains; Tor (onion routing, three-hop circuits, directory authorities via threshold signatures) and mix networks (Loopix, Nym) address it; VPNs shift trust to provider.
- **Key verification**: safety numbers (Signal), TOFU (SSH known_hosts), transparency logs (CT, Key Transparency for messaging — CONIKS).

## 31. Blockchain & cryptocurrency security

*Deep-dive: `advanced_crypto.md` §6.*

- **Primitives**: hash chains (block integrity), Merkle trees, digital signatures (ECDSA/secp256k1, Ed25519 on Solana), consensus as economic game theory.
- **Consensus**: PoW (Bitcoin — energy + ASIC arms race) vs. PoS (Ethereum post-Merge — slashing, finality) vs. BFT variants (Tendermint, HotStuff); 51%/nothing-at-stake attacks; long-range attacks.
- **Smart-contract security**: reentrancy (DAO hack 2016), oracle manipulation, flash-loan attacks, integer overflow, access-control bugs, upgradeability proxy risks; tools: Slither, Mythril, Foundry fuzz/invariant tests, formal verification (Certora).
- **Wallet security**: hot vs. cold, seed phrase custody (Shamir + steel backups), hardware wallets, multisig (Gnosis Safe), MPC wallets, address poisoning, blind-signing risks.
- **Layer-2**: optimistic rollups (fraud proofs) vs. ZK-rollups (validity proofs); bridge security is the weakest link (multiple multi-billion bridge hacks).
- **Regulatory**: MiCA (EU), SEC/ETF landscape — compliance is now part of "security."

## 32. Secure AI systems

- **Threat surface unique to ML**: models are assets (IP), inputs are adversarial space, training pipeline is supply chain.
- **Adversarial examples**: imperceptible perturbations fool classifiers; defenses largely broken cat-and-mouse; matters for: content moderation evasion, autonomous vehicles, biometric spoofing, malware classifiers.
- **Data poisoning**: label flipping, backdoor triggers (BadNets), membership-inference attacks (privacy leak), model inversion/extraction (steal model via API queries).
- **LLM-specific**: prompt injection (direct + indirect via retrieved content — the "SQLi of LLM apps"), jailbreaks, data exfiltration via tool use, insecure plugin ecosystems, training-data memorization of secrets.
- **Defenses**: input/output filtering, least-privilege tool scoping, human-in-the-loop for consequential actions, model signing/provenance (Sigstore for ML artifacts), confidential computing for inference, red-teaming as continuous practice (OWASP LLM Top 10, MITRE ATLAS).
- **Secure AI development**: dataset provenance, differential-privacy training, federated learning with secure aggregation, evals as security gates.

## 33. Incident response, forensics & threat hunting

- **IR lifecycle** (NIST SP 800-61): Preparation → Detection & Analysis → Containment → Eradication → Recovery → Post-Incident.
- **Forensics**: order of volatility (capture RAM before disk), write-blockers, chain of custody, timeline analysis (Plaso/log2timeline), memory forensics (Volatility), disk forensics (Autopsy/Sleuth Kit), network forensics (§17), cloud forensics (CloudTrail/GCP audit logs).
- **Ransomware playbook**: isolate (network segment, creds reset), identify scope via EDR/identity logs, don't pay (sanctions risk, no guarantee) — restore from immutable backups, negotiate only as last resort.
- **Threat hunting**: hypothesis-driven proactive search (e.g., "look for Kerberoasting", "anomalous OAuth grants"); MITRE ATT&CK as common vocabulary; detection-as-code (Sigma rules, YARA).
- **Tabletop exercises**: run IR plans before real incidents; purple-team exercises.

## 34. Security operations (SecOps / SOC)

- **Telemetry stack**: EDR endpoints + network (Zeek) + cloud audit logs + identity (Entra/Okta logs) + app logs → SIEM (Splunk, Sentinel, Elastic, Wazuh open-source).
- **Detection engineering**: ATT&CK-mapped detections, MITRE CALDERA/atomic tests for validation, false-positive tuning.
- **SOAR**: automated enrichment/response (auto-isolate host on EDR alert); balance automation vs. alert fatigue.
- **Metrics**: MTTD/MTTR, coverage vs. ATT&CK, alert precision — avoid vanity metrics (alert count).
- **Purple teaming**: red (attack simulation: Atomic Red Team, CALDERA, Sliver/Cobalt Strike in authorized labs) + blue collaboration.
- **Threat intel**: STIX/TAXII formats, ISACs, vendor feeds; intel without detection engineering is shelfware.
- **Logging & retention**: centralize logs (Windows Event Forwarding, syslog/Vector/Fluent Bit), immutable storage (S3 Object Lock, WORM), retention aligned to legal/regulatory needs — logs are both detection input and forensic evidence.
- **Identity as the new perimeter**: most modern intrusions authenticate *validly* with stolen creds → invest in IdP telemetry, impossible-travel/anomalous-grant detections, and phishing-resistant MFA over network monitoring alone.

## 35. Malware analysis & reverse engineering (defensive)

- **Static**: strings, PE headers (pestudio, DIE), disassembly (Ghidra — NSA's free RE suite, IDA, Binary Ninja), YARA rules.
- **Dynamic**: sandboxes (Any.Run, CAPE, Joe Sandbox), VM-isolated detonation, API call monitoring (ProcMon, Wireshark), debugger (x64dbg, WinDbg, gdb+pwndbg).
- **By category**: ransomware (encryptor analysis → decryptor via key-recovery), stealers (credential extraction TTPs), RATs, fileless malware (living-off-land: PowerShell, WMI, LOLBins).
- **Purpose**: detection rules, IOCs/TTPs for hunters, decryptor development, takedown evidence. **Legal**: analyze in VMs/labs only; never execute unknown samples on hosts.

## 36. Cryptographic key & secrets management

- **HSMs** (hardware security modules), **TPMs**, **secure enclaves** (Intel SGX/TDX — though SGX has had many side-channel breaks; **AMD SEV-SNP**, **ARM CCA** for confidential VMs), cloud KMS/HSM (AWS CloudHSM, Azure Managed HSM, GCP HSM).
- **Secrets lifecycle**: generate in vault → inject at runtime → rotate → audit access; HashiCorp Vault, AWS Secrets Manager, SOPS/age for git-encrypted secrets, Sealed Secrets for k8s.
- **Envelope encryption** pattern: DEK encrypts data, KEK (in KMS/HSM) encrypts DEK — enables rotation without re-encrypting data.
- **Confidential computing**: encrypt data in use via TEEs (trusted execution environments); remote attestation proves enclave integrity — emerging but with real side-channel caveats (see §39).

---

# PART V — SECURITY RESEARCH & PROFESSIONAL PRACTICE

*How the field advances: authorized adversarial testing, mathematical proof, protocol design, and the institutions (bounties, disclosure norms, conferences) that make it legal and rewarding.*

## 36b. Governance, compliance & security careers

### Governance frameworks

- **ISO/IEC 27001** — ISMS standard (certifiable); Annex A controls; risk assessment + SoA + internal audit cycle.
- **NIST CSF 2.0** — Govern/Identify/Protect/Detect/Respond/Recover; free, widely adopted.
- **SOC 2** — service-organization trust criteria (security/availability/confidentiality); required for SaaS sales.
- **PCI-DSS 4.0** — cardholder data; segmentation, quarterly scans, SAQ/ROC.
- **HIPAA/HITECH, GDPR, CCPA** — sectoral privacy regimes (§28.1).
- **Common Criteria** — product security evaluation (EAL levels); FIPS 140-3 for crypto modules.
- **Cyber insurance**: questionnaires drive baseline controls; war-exclusion clauses post-NotPetya litigation.

### Career map

| Role | Focus | Typical entry |
|---|---|---|
| SOC analyst | alert triage, detection eng | Security+, SIEM basics |
| Pentester / red teamer | authorized offensive testing | OSCP, HTB/TryHackMe |
| AppSec engineer | secure SDLC, code review | OSWE, secure-coding practice |
| Cloud security engineer | IAM, CSPM, cloud-native | AWS/GCP/Azure security certs |
| Cryptography engineer | protocol design, implementation | math + CS; rare, high demand |
| Privacy engineer | PETs, DPIAs, compliance | GDPR + eng hybrid |
| Malware analyst | RE, detection | Ghidra/FLARE-VM, GCFA-ish |
| GRC / risk | frameworks, audits | CISA, ISO 27001 LA |
| Security researcher | 0-days, disclosure | bug bounties, CTFs |

## 37. Ethical hacking & penetration testing

- **Legal frame first**: written authorization (rules of engagement, scope, testing windows); bug-bounty safe harbor; CFAA/Computer Misuse Act equivalents; never test external systems without permission. *This lab: localhost/lab targets only.*
- **Methodology** (mirrors `attacker_methodology.md`): reconnaissance (subdomain enum — subfinder, DNS, OSINT) → scanning (nmap, nuclei, httpx) → enumeration (ffuf/dirsearch/gobuster, whatweb) → exploitation (manual + sqlmap/jwt_tool/searchsploit) → post-exploitation (privesc, lateral movement concepts) → reporting.
- **Pentest types**: external/network, web app, wireless, social engineering (authorized), red team (full-scope adversary simulation), purple team.
- **Deliverables**: findings with severity (CVSS), reproduction steps, evidence, remediation; executive summary for leadership.
- **Certifications**: Security+/CySA+ (foundational), OSCP (hands-on gold standard), PNPT, eJPT; OSWE/OSCE for advanced web.
- **Practice platforms**: PortSwigger Academy (free, best web labs), Hack The Box, TryHackMe, PicoCTF, local labs (Juice Shop, DVWA, WebGoat per SETUP.md).

## 38. Formal verification & protocol design

- **Why**: tests find bugs you thought of; proofs cover all cases. Heartbleed, KRACK, Spectre were design/implementation gaps formal methods target.
- **Tools**: Lean 4 + Mathlib (installed locally — used for theorem proving), Coq, Isabelle/HOL; Tamarin/ProVerif for protocols; CryptoVerif; seL4 (formally verified microkernel); CompCert (verified C compiler); Fiat-Crypto/HACL* (verified crypto code); AWS s2n, Google's Tink use verified components.
- **Verified crypto**: HACL*/EverCrypt (project Everest) — machine-checked implementations of TLS components, X25519, AES.
- **Protocol design principles**: minimal trusted computing base, explicit adversary model, forward secrecy by default, downgrade resistance, key separation, formal verification before deployment.
- **Type systems for security**: information-flow control (Jif, Flow Caml), capability systems, linear types for resource safety.

## 39. Emerging frontiers & unsolved problems

- **Post-quantum transition** (in progress): hybrid deployments, crypto-agility, PQC side-channel analysis, standardization of stateless-hash sigs at scale.
- **Homomorphic encryption maturity**: bootstrapping performance, hardware acceleration (GPU/FPGA), standardization (ISO/IEC HE, HE-IR), real deployments (privacy-preserving ML, genomic analysis).
- **Confidential computing**: TEE attestation ecosystems, side-channel reality (Foreshadow, Plundervolt, Æpic/Downfall showed SGX/TDX vulnerable) — promises exceed current guarantees.
- **AI security arms race**: adversarial robustness is unsolved; LLM agent security (tool-use boundaries) is a live research area; AI-generated vulnerability discovery (e.g., LLM-assisted fuzzing) cuts both ways.
- **Unsolvable/unsolved hard problems**: P vs NP; quantum advantage timeline (estimates 5–30 years, high variance); proving lattice assumptions; watermarking AI content reliably; anonymous credentials that are both private and accountable.
- **Zero-knowledge at scale**: proof generation cost, hardware acceleration, recursive proofs, zkVMs (RISC Zero, SP1) making arbitrary-program ZK practical.
- **Secure multi-party / threshold everything**: threshold ECDSA in production (Fireblocks/Coinbase), FROST standardization, multi-party E2E encrypted messaging research.
- **Metadata resistance**: mix networks (Nym), VOPRF/private credentials, traffic-analysis-resistant protocols — largely unsolved at internet scale.
- **Post-quantum + privacy combined**: PQ ZK proofs (STARKs already PQ-ish), private PQ key exchange research.

## 40. Learning roadmap — beginner → advanced

*Web-security-specific 12-week plan: `learning_path.md`. This is the broader security/crypto arc.*

**Stage 0 — Foundations (weeks 1–4)**
- How the internet works: TCP/IP, DNS, HTTP, TLS handshake (draw it), PKI basics.
- Linux command line, scripting (Python), git. Read `applied_crypto.md` §1–2.
- Ports 8080/3000 lab targets: run Juice Shop, DVWA, WebGoat (`docker_setup.md`, SETUP.md).

**Stage 1 — Web app security (weeks 5–12)**
- Follow `learning_path.md` Phases 1–3: HTTP → OWASP Top 10 → access control/business logic (the payment-bypass zone).
- Tools: Burp Community, ZAP, ffuf, sqlmap, jwt_tool — see `cli_toolkit.md` + TOOLS.md.
- Build a Flask app and break/fix it (`flask_security_deep.md`, `defender_playbook.md`).

**Stage 2 — Systems & networks (weeks 13–20)**
- nmap/NSE, Wireshark/tshark, firewall concepts, Linux privilege model, log analysis.
- TryHackMe/HTB beginner paths; study `attacker_methodology.md`.

**Stage 3 — Cryptography proper (weeks 21–28)**
- `theory_primitives.md` end-to-end: AES modes, RSA math, ECC, hashes, signatures — implement small examples (Python `cryptography` lib; openssl CLI).
- Then `advanced_crypto.md`: ZK intro, HE concepts, PQC survey.
- Optional stretch: Lean 4 + Mathlib (installed) for formalization; Tamarin/ProVerif tutorials.

**Stage 4 — Defense & operations (weeks 29–36)**
- Threat modeling a real app; write Sigma/YARA rules; set up Wazuh or a home SOC; IR tabletop; vulnerability-management workflow with CVSS/EPSS/KEV.
- Privacy: GDPR basics, implement differential privacy toy example, study PETs literature.

**Stage 5 — Specialization (ongoing)**
- Pick a lane: web bug bounty (HackerOne), cloud security (CIS benchmarks, PACU-style labs), malware analysis (flare-vm, Ghidra), crypto research (ePrint, lattice estimators), AI security (MITRE ATLAS, garak LLM scanner), hardware/side-channel (ChipWhisperer).

**Specialization tracks worth considering**
- **Crypto researcher**: lattice estimation, implementation security, ePrint reading group.
- **Web bug bounty hunter**: pick a program scope, learn one vuln class deeply (see `payment_bypass.md` methodology), submit reports.
- **Cloud security**: build everything in IaC, break it with PMapper/Pacu-style labs, earn AWS Security Specialty.
- **Privacy engineer**: GDPR + build a DP-preserving analytics demo; study Google's differential-privacy libraries.
- **Hardware/side-channel**: ChipWhisperer + a smartcard/TPM; power-trace analysis tutorials.

**Universal rules**: labs/localhost only without written authorization; document everything; read disclosures/writeups (PortSwigger research, Google Project Zero, NCC Group); contribute to open-source security tooling.

---

# APPENDIX A — Tool quick-reference (full inventory: TOOLS.md)

| Domain | Key tools (installed) |
|---|---|
| Web proxy/scan | Burp Suite, OWASP ZAP, nuclei, ffuf, httpx, nikto, gobuster, dirsearch, feroxbuster, whatweb, subfinder |
| Exploitation aids | sqlmap, jwt_tool, searchsploit, hashcat, John the Ripper |
| Crypto/PKI | openssl, gpg, age, mkcert, certbot/acme.sh, ssh-keygen |
| Networks | nmap, Wireshark/tshark, tcpdump, iptables/nftables, WireGuard |
| Forensics/RE | Autopsy, Volatility, Ghidra, YARA, strings, Wireshark |
| Secrets/keys | KeePassXC, Bitwarden, VeraCrypt, HashiCorp Vault |
| Scripting | Python3 venv (flask, cryptography, sympy, markdown), Lean 4 + lake |
| Wordlists/data | SecLists (2.5GB), PayloadsAllTheThings, HackTricks, CheatSheetSeries, nuclei-templates |
| Labs | Juice Shop :3000, DVWA :4280, WebGoat :8080, local Flask app :5000 |

# APPENDIX B — Canonical reading list

- **Crypto theory**: Katz & Lindell *Introduction to Modern Cryptography*; Boneh–Shoup *Graduate Course in Applied Crypto* (free online).
- **Web security**: PortSwigger Web Security Academy (free labs); OWASP Testing Guide / ASVS / Cheat Sheet Series.
- **Systems**: *The Practice of Network Security Monitoring*; MITRE ATT&CK; NIST SP 800-61 (IR), SP 800-63 (digital identity), SP 800-53 (controls).
- **Privacy**: Solove *Understanding Privacy*; NIST Privacy Framework; GDPR text + EDPB guidance.
- **Research**: ePrint IACR (crypto preprints), USENIX Security / IEEE S&P / CCS / NDSS proceedings, Google Project Zero blog, PortSwigger Research.
- **PQC**: NIST PQC project pages; *Recommendations for Stateful Hash-Based Signature Schemes*; migration guides from CISA/NSA.

# APPENDIX C — Mental models cheat-sheet

1. **Crypto gives you tools; security is using them without footguns.** Most breaches: misconfig, logic, credentials, unpatched CVEs — not broken math.
2. **Hybrid always**: asymmetric bootstraps symmetric; never RSA-encrypt a file directly.
3. **AEAD always**: encryption without authentication is malleable and dangerous.
4. **Keys are the perimeter**: key management failures cause most crypto incidents.
5. **Assume breach**: design for detection, containment, and recovery — prevention alone fails.
6. **Least privilege + complete mediation + fail secure**: the defensive trinity.
7. **Verify, don't trust**: signatures, attestation, SBOMs, transparency logs — provenance is the new perimeter.
8. **The human is the attack surface**: phishing-resistant MFA (passkeys) beats awareness training alone.
9. **Metadata leaks**: E2E hides content, not context — privacy requires thinking about traffic analysis.
10. **Crypto agility**: algorithm choice will change (PQC); never hardcode assumptions about "the" algorithm.

---

# APPENDIX D — Canonical breach case studies (what each teaches)

| Incident | Year | Root cause | Lesson |
|---|---|---|---|
| Heartbleed | 2014 | OpenSSL buffer over-read (missing bounds check) | memory safety + disclosure ethics; OpenSSL was underfunded |
| Sony PS3 | 2010 | static ECDSA nonce → private key recovery | RNG/nonce discipline |
| DigiNotar | 2011 | CA issued fraudulent certs; no CT | PKI trust is fragile; CT now mandatory |
| Target | 2013 | third-party HVAC vendor creds → POS malware | supply chain + segmentation |
| Equifax | 2017 | unpatched Struts CVE + expired cert blinded monitoring | patch SLAs + monitoring coverage |
| NotPetya | 2017 | M.E.Doc update supply chain + EternalBlue | supply chain, segmentation, backups |
| SolarWinds | 2020 | build-system compromise → signed malicious update | build integrity, SBOM, assume breach |
| Colonial Pipeline | 2021 | single leaked VPN password, no MFA | MFA + OT segmentation |
| Log4Shell | 2021 | JNDI lookup in Log4j → RCE everywhere | dependency risk at scale; SBOM value |
| MOVEit | 2023 | SQLi in managed file transfer → mass extortion | patch velocity on edge appliances |
| Change Healthcare | 2024 | Citrix portal without MFA → ransomware | MFA on every remote access path |
| Polyfill.io | 2024 | domain sold → JS supply-chain injection | third-party script risk; SRI/subresource integrity |

Pattern across all: **the math held; the systems around it failed** — credentials, patching, segmentation, monitoring, supply chain.

---

## Sources & provenance

- Internal research corpus (this machine): `~/websec_research/*.md` (12 reports), `~/gh_backup/crypto_research/*.md` (5 reports), `~/TOOLS.md`, `~/science_research/math_logic_map.md`, `ml_pipeline_guide.md`.
- Standards & primary docs: NIST (FIPS 140-3, SP 800-53/57/61/63/207 privacy, PQC standards), RFC 8446 (TLS 1.3), RFC 8555 (ACME), X.509/ITU-T, ISO/IEC 27001 & 29147/30111, eIDAS, GDPR/EDPB, PCI-DSS, MITRE ATT&CK/CALDERA/ATLAS, CWE/CVE/CVSS/EPSS/KEV, CA/Browser Forum BRs.
- Key papers/events referenced: Biham–Shamir differential cryptanalysis; Matsui linear cryptanalysis; Shor 1994; Gentry 2009 FHE; NIST PQC standardization (Aug 2024); Castryck–Decru SIKE break 2022; Shor→ harvest-now-decrypt-later analyses; Signal Protocol specs; Noise protocol framework; zk-SNARK/STARK literature; Dwork differential privacy; Sweeney k-anonymity.
- Tools/docs: OWASP (Top 10 2025, ASVS, Cheat Sheets, Threat Dragon, LLM Top 10), PortSwigger Web Security Academy & Research, Let's Encrypt/ACME docs, libsodium/NaCl docs, WireGuard whitepaper, Ghidra/Volatility/YARA docs, HashiCorp Vault docs.

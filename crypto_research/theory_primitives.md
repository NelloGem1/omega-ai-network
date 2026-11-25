# Cryptographic Primitives & Theory — Research Report

*A structured reference on modern cryptographic primitives: symmetric and asymmetric algorithms, hash functions, digital signatures, key exchange, the role of prime numbers, security-level equivalences, and the historical milestones that shaped the field.*

---

## 1. Symmetric Cryptography

Symmetric ciphers use a **single shared secret key** for both encryption and decryption. They are extremely fast — the workhorses of real-world systems — but the key must be shared securely beforehand, which is where asymmetric crypto comes in (see §5).

### 1.1 AES (Advanced Encryption Standard)

- **Approved in 2001** as **FIPS 197** by the U.S. National Institute of Standards and Technology (NIST), selected from the open AES competition (1997–2000) of 15 candidates. The winning algorithm, designed by Belgian cryptographers **Joan Daemen and Vincent Rijmen**, was originally named **Rijndael** (a portmanteau of the two surnames).
- AES is a **block cipher**: it operates on fixed-size **128-bit blocks** in **10, 12, or 14 rounds**, depending on key size. (Counterintuitively, the 192-bit key gets 12 rounds and 256-bit gets 14.)
- **Key sizes:** AES-128, AES-192, AES-256. Only 128- and 256-bit are widely standardized in protocols (TLS 1.3 allows all three).
- **Why AES won:** it beat a strong field (including Serpent, Twofish, RC6, and Mars) on security *and* performance. On modern CPUs it gets hardware acceleration through the **AES-NI** instruction set (introduced by Intel in 2010), delivering on the order of **~1–2 GB/s per core** for AES-CTR/GCM workloads. In constant-time software form it runs near memory bandwidth on mobile devices.
- **Security margins:** AES has no known practical attack against any of the three key sizes. Academic "related-key" attacks on AES-192/256 (Biclique attacks by Biryukov, Khovratovich, and Rechberger, 2011) reduce the *effective* key space only marginally (e.g., AES-256 attacks to ~2^254 rather than 2^256) and are not practical.
- **Brute-force cost estimates:** AES-128 is completely beyond classical reach; even with every GPU on Earth running flat out for billions of years it would not be searched.

### 1.2 ChaCha20 / XChaCha20

- Designed by **Daniel J. Bernstein** in 2008 (published as part of his SNOW stream cipher lineage). "ChaCha" = "Chacha Cha Cha" stream cipher; "20" = 20 rounds (8 quarter-rounds per double-round × 10).
- A **stream cipher**: generates a keystream and XORs it with plaintext. No padding needed; any length is handled natively.
- **Key size:** fixed **256-bit** key + 96-bit nonce (12-byte) in standard ChaCha20; XChaCha20 extends the nonce to 192 bits for safe random nonces.
- **Why it matters:** ChaCha20 is built entirely from **32-bit additions, rotations, and XORs** — no table lookups — making it **constant-time by construction** and immune to the cache-timing attacks that plagued AES implementations. It is the default cipher in **TLS 1.3 alongside AES-GCM**, in OpenSSH, WireGuard (uses ChaCha20-Poly1305), and most modern mobile/edge stacks. Roughly comparable in speed to AES-NI hardware; sometimes faster on ARM/mobile without AES-NI.
- Modern standardized form: **ChaCha20-Poly1305** (RFC 8439) — an authenticated encryption construction.

### 1.3 Block ciphers vs. stream ciphers

- **Block ciphers** (AES, DES, 3DES): permute fixed-size blocks. Reused directly on repetitive plaintext they leak patterns (ECB mode problem). Need a **mode of operation** to be safe.
- **Stream ciphers** (ChaCha20, RC4): XOR a key-dependent keystream with arbitrary-length plaintext. Stateless and naturally counter-based variants are common today.
- Historically important, now broken/deprecated: **DES** (56-bit key, broken by brute force via EFF's Deep Crack in ~3 days in 1998) and **RC4** (broken by multiple practical attacks; banned from TLS by RFC 7465).

### 1.4 Modes of operation

A bare block cipher only encrypts one block. Modes chain blocks:

| Mode | Properties | Status |
|---|---|---|
| **ECB** | Deterministic, leaks patterns | Never use for real data (famous "ECB penguin" image attack) |
| **CBC** | Deterministic per-position, needs random IV, padding oracles possible | Legacy; still used in disk encryption contexts |
| **CTR** | Turns block cipher into stream cipher; counter nonce | Secure, widely used (TLS 1.2) |
| **GCM** | CTR + GHASH authentication (AEAD); nonce reuse catastrophic | **The standard**: TLS 1.3 default, IPsec, disk encryption |
| **CCM, OCB** | Other AEAD modes | Used in specific niches |

**AEAD (Authenticated Encryption with Associated Data)** modes like GCM and ChaCha20-Poly1305 provide **confidentiality + integrity + authentication** in one pass — they are the correct way to use symmetric crypto today. Raw CBC/CTR without MACs is considered an anti-pattern.

---

## 2. Asymmetric Cryptography

Asymmetric (public-key) crypto uses a **key pair**: a public key anyone can use to encrypt or verify, and a private key only the owner holds to decrypt or sign. The security rests on mathematical problems believed hard to invert — factoring and discrete logarithms.

### 2.1 RSA (Rivest–Shamir–Adleman, 1977)

- Published in **1977** in *"A Method for Obtaining Digital Signatures and Public-Key Cryptosystems"* (CACM 21(2), pp. 120–126). Invented by Ron Rivest, Adi Shamir, Leonard Adleman at MIT.
- **How it works:** security relies on the difficulty of **factoring large semiprimes** `n = p × q`. The public key is `(n, e)` with `e` typically 65,537; the private key is `d`, the modular inverse of `e` mod `λ(n)`. Decryption is `m = c^d mod n`.
- **Key-size evolution:**
  - **512-bit** RSA factored in 1999 (3 months, CADO-NFS); **768-bit** factored in 2009 (two years, hundreds of machines) — RSA-512 fell in days on modern hardware.
  - **1024-bit:** now considered **broken for high-security use** (~80-bit security); still used in legacy systems.
  - **2048-bit:** the minimum widely accepted today; NIST SP 800-131A says it's acceptable for protection through **2030** (~112-bit security).
  - **3072-bit:** ~128-bit security; required if data must remain secure past 2030.
  - **4096-bit:** ~152-bit security; popular for signing/root CAs.
  - **7680-bit** reaches ~192-bit security; **15360-bit** reaches ~256-bit (NIST SP 800-57 Table 2).
- **Cost:** RSA operations are ~1000× slower than AES and keys/ciphertexts are large (2048-bit = 256 bytes). RSA is therefore reserved for key establishment and signatures, never bulk data.
- **Quantum vulnerability:** Shor's algorithm (1994) breaks RSA in polynomial time on a quantum computer.

### 2.2 Diffie–Hellman Key Exchange (1976)

- Invented by **Whitfield Diffie and Martin Hellman** (Stanford, 1976) — "New Directions in Cryptography." Independently reinvented by **Ralph Merkle** in 1974 (secret-key distribution, his "Merkle's puzzles").
- **How it works:** two parties publicly agree on prime `p` and generator `g`. Alice sends `g^a mod p`, Bob sends `g^b mod p`; both compute the shared secret `g^(ab) mod p`. An eavesdropper sees only the public values.
- Security = difficulty of the **discrete logarithm problem** (DLP) in a prime-order group. Plain finite-field DH with 1024-bit `p` is now weak; 2048-bit minimum, 3072-bit preferred.
- **Ephemeral DH (DHE/ECDHE)** with fresh keys per session gives **forward secrecy**: compromising a long-term key doesn't reveal past sessions.

### 2.3 Elliptic Curve Cryptography (ECC, 1985)

- Independently proposed by **Neal Koblitz** ("Elliptic Curve Cryptosystems," 1985) and **Victor Miller** ("Use of Elliptic Curves in Cryptography," 1985).
- Works over the group of points on an elliptic curve `y² = x³ + ax + b` over a finite field. The security problem is the **elliptic-curve discrete logarithm problem (ECDLP)**, which has **no known sub-exponential algorithm** — unlike factoring, which has the Number Field Sieve. Therefore ECC gives the same security with *much* smaller keys:
  - RSA-1024 ≈ ECC-160 (80-bit)
  - RSA-2048 ≈ **ECC-224** (112-bit)
  - RSA-3072 ≈ **ECC-256** (128-bit)
  - RSA-7680 ≈ ECC-384 (192-bit)
  - RSA-15360 ≈ ECC-521 (256-bit)
- **Smaller keys = smaller signatures and faster operations.** A 256-bit ECC private key does what a 3072-bit RSA key does.
- **Named curves:** NIST P-256, P-384, P-521 (widely standardized); **Curve25519** (by Daniel Bernstein, 2005/2006) — chosen for its design, speed, and resistance to implementation pitfalls.

### 2.4 Curve25519, Ed25519, X25519

- **Curve25519**: a Montgomery curve (`y² = x³ + 486662x² + x`) over GF(2²⁵⁵−19). Uses the **Montgomery ladder** for fast, constant-time scalar multiplication.
  - **X25519**: the Diffie-Hellman analogue (key exchange). Default in OpenSSH, WireGuard, TLS 1.3, Noise protocols, Signal.
  - **Ed25519**: signatures on the birationally-equivalent **Edwards curve** (by Bernstein et al., 2011–2012, a deterministic Schnorr-style scheme). ~128-bit security, ~64-byte signatures, microsecond signing, no RNG needed (deterministic nonces). Now the most widely used signature scheme outside the certificate ecosystem.
- **Why Curve25519 exists:** designed with explicit criteria — fast on all platforms (no timing side channels), no points of small order, no special cases, clean constant-time implementations. It avoids the subtle failures that plagued NIST curve implementations.

### 2.5 ElGamal (1985)

- **Taher ElGamal**, "A Public Key Cryptosystem and a Signature Scheme Based on Discrete Logarithms" (1985).
- An encryption/signature scheme generalizing DH to encryption: ciphertext `(c1, c2) = (g^k, m·h^k)` where `h = g^x`. Also the basis for **DSA** (Digital Signature Algorithm, NIST FIPS 186, 1994) and **ECDSA** ( elliptic-curve variant, 1999).
- Properties: probabilistic encryption (needs a fresh random `k` per message — nonce reuse leaks the key), malleable ciphertexts (fixed by using it only inside authenticated constructions).

---

## 3. Hash Functions

Hash functions map arbitrary-length input to a **fixed-size digest** (e.g., 256 bits). They are **one-way** (preimage resistance), **collision-resistant** (can't find two inputs with the same hash), and **second-preimage resistant**. Crucially, **hashes are NOT encryption** — you cannot recover the input from the digest; they provide **integrity and commitment**, not confidentiality.

### 3.1 SHA family (NIST)

- **SHA-1** (1995, 160-bit): **broken** — practical collision found by Google/CWI in 2017 ("SHAttered," ~$110k of GPU compute). Deprecated everywhere.
- **SHA-256 / SHA-512** (2001, part of SHA-2): the current workhorses. SHA-256 = 64 rounds over 32-bit words; SHA-512 uses 64-bit words. Used in TLS 1.3, blockchains, Git, TLS certificates, MACs (HMAC-SHA256), etc.
- **SHA-3 / Keccak** (2015, FIPS 202): a different design (sponge construction) chosen in 2012 from 64 candidates after the SHA-3 competition. Provides a hedge against attacks on SHA-2's Merkle–Damgård design. Still niche in practice.
- **SHAKE128/256**: extendable-output functions from SHA-3, used in some PQC schemes.

### 3.2 BLAKE family (non-NIST, widely used)

- **BLAKE2** (2012/2013, Jean-Philippe Aumasson et al.): faster than SHA-2/SHA-3, tree hashing modes, used in **libsodium**, WireGuard-adjacent tooling, `blake2b` in Python. BLAKE2b-256 is used in many modern stacks.
- **BLAKE3** (2020, Jack O'Connor et al.): extreme parallelism, SIMD-optimized, ~10× faster than SHA-256 on large data, used in IPFS, rsync alternatives, ZFS checksums, `b3sum`. Tree-hash structure; standardized-ish via the BLAKE3 spec (not a NIST FIPS).
- **What hashes are for:** file integrity checks, password hashing (with salt + KDF — never raw SHA-256), digital signatures (signing `H(m)` not `m`), checksums, blockchain linking, MACs via HMAC, random number derivation, commitment schemes.

---

## 4. Digital Signatures

Signatures prove **authenticity, integrity, and non-repudiation**: only the holder of the private key could have produced the signature, the message is unaltered, and the signer cannot later deny it.

| Scheme | Basis | Signature size | Notes |
|---|---|---|---|
| **RSA signature** | Factoring | key-size-dependent (256 B for RSA-2048) | Encrypts `H(m)` with private key; verify with public. Still dominant in X.509 certificates. |
| **DSA** | Finite-field DLP | ~320 bits | NIST 1994; essentially legacy. |
| **ECDSA** | Elliptic-curve DLP | ~64–72 bytes | Dominant in TLS certs, Bitcoin. Requires careful nonce generation — bad RNG = key recovery (the **PS3 fail0verflow / Sony ECDSA nonce reuse** scandal). |
| **Ed25519** | Edwards-curve Schnorr | 64 bytes | Deterministic, fast, constant-time, no RNG needed. Standard in SSH, age encryption, minisign, WireGuard-adjacent tooling. Used by libsodium/Signal ecosystem. |
| **Ed448** | Curve448 | 114 bytes | Higher-security variant. |

Post-quantum signatures (NIST 2024): **ML-DSA** (Dilithium-derived, FIPS 204) and **SLH-DSA** (SPHINCS+ hash-based, FIPS 205). See §8.

---

## 5. Key Exchange in Practice — The Hybrid Pattern

Real-world cryptography (TLS 1.3, SSH, WireGuard, Signal) uses a **hybrid** construction:

```
        ┌─────────────────────────────────────────────┐
        │  Asymmetric crypto  (slow, expensive)        │
        │  • Key exchange: X25519 ECDH / ECDHE          │
        │  • Authentication: Ed25519 / RSA / ECDSA sig  │
        │  Purpose: agree on a shared secret + prove    │
        │           identity                             │
        └──────────────────┬──────────────────────────┘
                           ▼
              Shared secret (e.g., 256-bit key)
                           ▼
        ┌─────────────────────────────────────────────┐
        │  Symmetric crypto  (fast, cheap)             │
        │  • AEAD: AES-256-GCM or ChaCha20-Poly1305    │
        │  Purpose: encrypt all actual data            │
        └─────────────────────────────────────────────┘
```

**Why hybrid:** asymmetric ops cost ~1000× more than symmetric ones and produce large ciphertexts. So you use asymmetric crypto *only* to establish a shared secret once (or per session for forward secrecy), then derive session keys with a KDF (HKDF) and encrypt gigabytes with AES/ChaCha.

**TLS 1.3 handshake example (ECDHE + Ed25519/RSA cert + AES-GCM):**
1. Client sends `ClientHello` with supported cipher suites + a fresh ephemeral X25519 public key.
2. Server picks one, sends its ephemeral X25519 public key + its certificate (containing a long-term Ed25519/RSA signature key) + signature over the handshake.
3. Both sides compute the shared ECDH secret; a KDF derives AES-256-GCM traffic keys.
4. All subsequent application data flows through AES-256-GCM or ChaCha20-Poly1305.
5. With **ECDHE**, even if the server's long-term key is later stolen, past sessions stay secure (**forward secrecy**). TLS 1.3 removed static RSA key transport entirely for this reason.

---

## 6. Primes' Role in Cryptography

Prime numbers are the bedrock of both RSA and ECC:

### 6.1 RSA needs large primes
- `n = p × q` where p, q are two random ~1024-bit primes. The security is that factoring `n` (a ~2048-bit semiprime) is computationally infeasible.
- **Key generation pipeline:** generate a random odd candidate → small-prime sieve (reject candidates divisible by small primes 3, 5, 7, …) → **Miller–Rabin primality test** (probabilistic: run k rounds of modular exponentiation; each round is a "witness" test) → when Miller–Rabin passes, you have a *probable prime*. For extra certainty, **Lucas probable prime tests** or deterministic variants are used. OpenSSL/BoringSSL generate RSA primes with hundreds of Miller–Rabin rounds; generation takes ~seconds for 2048-bit keys.
- **Last-digit filters:** since primes > 5 must end in 1, 3, 7, or 9, candidates are generated only in those residue classes; small-prime trial division quickly eliminates most composites before Miller–Rabin.

### 6.2 ECC needs points on curves
- Curve operations require solving point additions/doublings in a finite field `GF(p)` (prime field) or `GF(2^m)` (binary field). For prime-field curves, the field size `p` itself is prime (e.g., Curve25519 uses p = 2²⁵⁵ − 19, a prime chosen because 2²⁵⁵ − 19 has efficient reduction: `19` is small, enabling fast modular reduction without division).
- Curve order (number of points) must be prime or have a large prime factor for security — e.g., Curve25519's group has order `8 × L` where `L` is a 252-bit prime; X25519 clamps scalars to kill the cofactor.

### 6.3 Primality testing & sieving
- **Miller–Rabin:** for random odd `n`, pick random base `a`, check `a^(n−1) ≡ 1 (mod n)` and related conditions. No known composite passes many random rounds — the probability of a false positive is ≤ 4^(-k). It is the standard "probable prime" test used in key generation.
- **Lucas test / BPSW:** a combined Miller–Rabin + Lucas test is considered deterministic-enough for practical use (no known counterexamples).
- **Sieving:** the **General Number Field Sieve (GNFS)** and **Special Number Field Sieve (SNFS)** are the algorithms that *break* RSA — they find the factors of `n` in sub-exponential time. The "sieving" step finds smooth relations among numbers; this is exactly the machinery an attacker uses, which is why prime size matters.
- **Where this connects:** RSA-2048's ~112-bit security means factoring requires ~2^112 work — beyond any classical computer but (critically) within reach of a large quantum computer running **Shor's algorithm**, which factors in polynomial time. Hence the urgent PQC transition (§8).

---

## 7. Security Levels — Comparable Key Sizes

From **NIST SP 800-57 Part 1 Rev. 5 (May 2020), Table 2** — bits of security vs. required key sizes:

| Security strength | Symmetric (AES) | RSA / DH / DSA | ECC (field size) |
|---|---|---|---|
| ~80 bits | AES-80* | 1024 | 160–223 |
| **112 bits** | AES-128 | **2048** | **224–255** |
| **128 bits** | AES-128 | **3072** | **256–383** |
| 192 bits | AES-192/256 | **7680** | **384–511** |
| **256 bits** | **AES-256** | **15360** | **512–571** |

*NIST allows AES-80 historically but AES-128 is the minimum today. *

Key takeaways:
- **AES-128 ≈ RSA-3072 ≈ ECC-256** (all ~128-bit security).
- **AES-256 ≈ RSA-15360 ≈ ECC-521** (~256-bit).
- ECC keys are ~10× smaller than RSA keys for the same strength.
- NIST SP 800-131A: 112-bit (RSA-2048/ECC-224) acceptable for protection through **2030**; migrate to 128-bit before then.

---

## 8. Historical Milestones

| Year | Event |
|---|---|
| **1943** | **ENIGMA broken** at Bletchley Park (Turing et al.) — the first large-scale demonstration that "unbreakable" ciphers fall to systematic cryptanalysis. |
| **1976** | **Diffie–Hellman** key exchange published — the conceptual birth of public-key crypto. Independently, Merkle's puzzles (1974) solved key distribution. |
| **1977** | **RSA** published (Rivest, Shamir, Adleman). First practical public-key encryption + signatures. |
| **1985** | **ECC** proposed independently by Koblitz and Miller. ElGamal published. |
| **1991** | **PGP** released by Phil Zimmermann — brings asymmetric + symmetric crypto to the masses. |
| **1994** | **Shor's algorithm** published — proves a quantum computer can factor integers and solve discrete logs in polynomial time, breaking RSA, DH, ECDSA, and ECDH. |
| **1997–2000** | **AES competition**: NIST runs an open, international contest; Rijndael (Daemen & Rijmen) wins; standardized as FIPS 197 in **2001**. Replaces DES/3DES. |
| **1998** | DES broken by brute force (EFF Deep Crack, ~3 days / $250k). 3DES deprecated. |
| **1999** | **ECDSA** standardized (FIPS 186-2); ECC gains traction in constrained devices. |
| **2005/2006** | **Curve25519** designed by Bernstein; later Ed25519 signatures (2012). |
| **2011–2012** | First practical **quantum annealing / factoring demos**; NSA begins PQC planning. Academic lattice crypto (Regev's LWE, 2005) provides the foundation. |
| **2012** | **SHA-3 competition** launched; Keccak wins (2015, FIPS 202). |
| **2015** | **NIST PQC standardization** begins: 82 submissions from 25 countries. |
| **2017** | **SHA-1 collision** demonstrated (SHAttered) — SHA-1 fully deprecated. |
| **2020** | **BLAKE3** released. |
| **2022** | NIST selects finalists: **CRYSTALS-Kyber** (KEM), **CRYSTALS-Dilithium** (signatures), **SPHINCS+** (hash-based signatures), **FALCON**. |
| **Aug 13, 2024** | NIST publishes final PQC standards: **FIPS 203 (ML-KEM, from Kyber), FIPS 204 (ML-DSA, from Dilithium), FIPS 205 (SLH-DSA, from SPHINCS+)**. First quantum-resistant cryptographic standards. |
| **2024–2035** | NIST IR 8547 migration timeline: deprecate quantum-vulnerable algorithms, with high-risk systems transitioning first; full transition targeted by ~2035. |

**Why RSA (and ECDSA/ECDH) will fall:** Shor's algorithm solves factoring and discrete logarithms in polynomial time on a quantum computer. A sufficiently large fault-tolerant quantum computer could break RSA-2048/ECC-256 in hours. Current estimates suggest such machines may exist within 10–30 years. Symmetric crypto (AES) survives — Grover's algorithm only halves the effective key length (AES-256 remains ~128-bit quantum-safe). This is why NIST spent 2015–2024 standardizing lattice-based (ML-KEM, ML-DSA) and hash-based (SLH-DSA) replacements.

---

## Sources

- NIST FIPS 197 (AES), FIPS 202 (SHA-3), FIPS 186 (DSA/ECDSA), FIPS 203/204/205 (PQC): https://csrc.nist.gov/
- NIST SP 800-57 Part 1 Rev. 5 — Recommendation for Key Management (security-strength equivalences): https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf
- NIST SP 800-131A Rev. 2 — Transitioning the Use of Cryptographic Algorithms: https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-131ar2.pdf
- NIST PQC announcement (Aug 13, 2024): https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards
- NIST IR 8547 — Transition to Post-Quantum Cryptography Standards: https://csrc.nist.gov/pubs/ir/8547/ipd
- Rivest, Shamir, Adleman (1977), "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems," CACM 21(2):120–126.
- Diffie & Hellman (1976), "New Directions in Cryptography," IEEE Trans. Info. Theory 22(6):644–654.
- Koblitz (1985), "Elliptic Curve Cryptosystems," J. Cryptology 1:203–209; Miller (1985), "Use of Elliptic Curves in Cryptography," CRYPTO '85.
- Bernstein, "Curve25519: new Diffie-Hellman speed records" (2006); Bernstein et al., "Ed25519" (2012).
- Daemen & Rijmen, "The Design of Rijndael" (AES proposal): https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines/aes-development
- "SHAttered" SHA-1 collision (Google/CWI, 2017): https://shattered.io/
- RFC 8446 — TLS 1.3: https://www.rfc-editor.org/rfc/rfc8446.html
- RFC 8439 — ChaCha20-Poly1305: https://www.rfc-editor.org/rfc/rfc8439.html
- NIST SP 800-56A/B/C — key establishment/derivation recommendations.

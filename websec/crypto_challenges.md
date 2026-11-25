# Crypto Challenges — Attacking Weak Implementations

Goal: learn *why* strong crypto matters by breaking weak crypto on our own test data.
Tools: Python 3 (`sympy`, `cryptography`), Hashcat v8.0.0 (Windows, Intel UHD 750 GPU), WSL Ubuntu.

---

## Challenge 1: Factor a toy RSA key

**Setup** — `challenge1_rsa.py` generates toy RSA keys: two random primes of `bits` bits each (primality via `sympy.isprime`), `n = p*q`, `e=65537`, `d = e⁻¹ mod φ(n)`. Attacker only knows `n`.

**Attack** — `sympy.factorint(n)` (trial division → Pollard rho → p−1 → ECM) recovers the factors.

**Results** (measured on this machine):

| RSA modulus size | Primes | Factor time | Result |
|---|---|---|---|
| 64-bit n | 2×32-bit | **0.146 s** | factored |
| 128-bit n | 2×64-bit | **2.16 s** | factored |
| 192-bit n | 2×96-bit | **> 600 s (timeout)** | did not finish |
| 2048-bit n | 2×1024-bit | infeasible | — |

Keygen of a real 2048-bit RSA key (`cryptography` lib, same class as `folder_lock.py` uses): < 1 s — generation is cheap, factoring is not.

**Lesson** — factoring cost grows roughly exponentially with key size (`~exp(√(ln n · ln ln n))` for NFS-class algorithms). Doubling the modulus from 64→128 bits cost ~15× more time; 192 bits blew past 10 minutes. A 2048-bit modulus is ~10²⁹ times larger than 192-bit — completely out of reach. Real-world anchors: RSA-768 (232 digits) took ~2000 CPU-years (2009); RSA-829 (250 digits, RSA-250) took ~2700 core-years (2020). Never roll your own RSA with small keys; always use ≥2048-bit (3072/4096 preferred) from a vetted library.

---

## Challenge 2: Hashcat cracks weak password hashes

**Setup** — `weak_hashes.txt`: MD5 hashes of 16 top-password-list entries (`password123`, `qwerty`, `letmein`, `dragon`, …). `strong_hash.txt`: MD5 of `Xk9#mQv2!zLp7$wR4nT` (16 chars, mixed case + symbols). `wordlist.txt`: the 16 weak passwords (+ strong pw as a candidate for run 1); `wordlist_common.txt`: the 16 weak passwords only.

**Attack** — `hashcat.exe -m 0` (MD5, raw) against a 16–17 word dictionary, Intel UHD 750 GPU.

**Results**:
- Weak set: **16/16 recovered in < 1 second** (~2972 H/s on dictionary mode). Full plaintexts in `C:\Users\neilh\websec_lab\cracked.txt`.
- Strong hash vs. same wordlist: **0/1 recovered** — not in dictionary, survived.

**Lesson** — MD5 is broken *as a password hash* regardless of dictionary luck: it's fast (billions of guesses/sec on real GPUs), unsalted, and rainbow-tableable. Even a strong password only survived because it wasn't in a 16-word list — a real attacker uses rockyou.txt (~14M words), rules/mangling, and mask attacks (`?a?a?a?a?a?a` = 6-char anything in seconds). Always use a slow, salted KDF: **bcrypt, scrypt, or Argon2id** (what `folder_lock.py`-style tools should use for passphrase→key derivation). MD5/SHA-1 are fine for checksums, never for passwords.

---

## Challenge 3: AES-ECB pattern leakage (the "penguin")

**Setup** — `challenge3_ecb_image.py`: encrypt with `cryptography`'s AES in **ECB mode** (each 16-byte block encrypted independently, same key → same ciphertext for same plaintext).

**Attack** — no key needed; just *look* at the ciphertext.

**Results**:
- Plaintext of 4 identical 16-byte blocks (`ff0000ff` × 16) → **all 4 ciphertext blocks byte-identical** (`ccc75edf…7ba2` repeated).
- A 64×64 "image" made of 4 identical horizontal stripes → **all 4 ciphertext stripes identical**: the stripe pattern (i.e., the picture's outline) survives encryption intact.

**Lesson** — ECB is a *codebook*: identical plaintext blocks always produce identical ciphertext blocks, so structure leaks. This is the famous [ECB penguin](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Electronic_codebook_(ECB)) demo — encrypting a Tux bitmap under ECB leaves the penguin visibly intact. Real ECB ciphertexts (e.g., old TLS misconfigurations, some database field encryption) leak which records are equal, enable block-reordering/splicing, and cut-and-paste attacks. **Always use an authenticated mode with random IV: AES-GCM, AES-CBC with random IV + HMAC, or ChaCha20-Poly1305.** Never ECB, never reuse IVs.

---

## Challenge 4: AES-GCM nonce reuse = catastrophic failure

**Setup** — `challenge34_ecb_gcm.py`: AES-GCM with a random 256-bit key, and the **same 12-byte nonce used for two different messages** (a classic implementation bug — e.g., counter reset, hardcoded nonce, RNG failure).

**Attack** — attacker sees only `ct1`, `ct2` (no key).

**Results**:
```
msg1 = "Attack at dawn!"   ct1 = 0b3993b4…32d
msg2 = "Attack at noon!"   ct2 = 0b3993b4…21d
ct1 XOR ct2  = 000000000000000000000a0e180000
msg1 XOR msg2 = 000000000000000000000a0e180000   ← identical!
```

GCM is a stream cipher: `ct = pt XOR keystream(nonce, key)`. Same nonce → same keystream → `ct1 ⊕ ct2 = m1 ⊕ m2`. If the attacker knows/guesses *either* plaintext, the other is recovered byte-for-byte; two unknown plaintexts still leak their XOR (often enough to recover both via crib-dragging). Auth tags can also be forged in some reuse scenarios.

**Lesson** — nonce reuse in GCM/CTR/ChaCha is a *total* break, worse than weak keys in some ways because it's silent. Nonces must be **unique per key** — use random 96-bit nonces (birthday-safe for ~2³² messages), or better, let the library manage it (AESGCM's `encrypt` API in `cryptography` does this correctly). Many real breaches (e.g., nonce reuse in WPA/IoT firmware, the "nonce-misuse" attacks on JWT/AEAD libraries) trace to this one bug.

---

## Summary table

| # | Weakness attacked | Tool | Result | Fix |
|---|---|---|---|---|
| 1 | Small RSA modulus (64–192-bit) | sympy.factorint | 64/128-bit fall in <3s; 192-bit >10min; 2048-bit impossible | ≥2048-bit RSA or Ed25519 |
| 2 | MD5 password hashes + weak passwords | hashcat -m 0 | 16/16 in <1s | Argon2id/bcrypt/scrypt + salt |
| 3 | AES-ECB mode | cryptography ECB | structure/pattern leaks fully | AES-GCM / CBC+HMAC / ChaCha20-Poly1305 |
| 4 | AES-GCM nonce reuse | cryptography AESGCM | ct⊕ct = pt⊕pt → plaintext recovery | unique nonce per key, always |

## Files
- `challenge1_rsa.py` — toy RSA gen + factoring timings
- `challenge34_ecb_gcm.py` — ECB block-identical + GCM nonce-reuse demos
- `challenge3_ecb_image.py` — ECB stripe/image leakage demo
- `weak_hashes.txt`, `strong_hash.txt`, `wordlist*.txt`, `weak_hashes_only.txt` — hashcat inputs
- `C:\Users\neilh\websec_lab\cracked.txt` — hashcat recovered plaintexts

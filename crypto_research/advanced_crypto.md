# Advanced Cryptography Research Report

*A deep-dive companion to the beginner-level reports on symmetric ciphers, asymmetric cryptography, hashes, signatures, TLS, and passwords. This document covers cryptanalysis, advanced primitives (ZKP, FHE, MPC), post-quantum cryptography, blockchain, formal verification, hardware cryptography, key management, and open problems.*

---

## 1. Cryptanalysis & Attacks

### 1.1 Brute Force

Brute force enumerates every possible key until the correct one is found. Its feasibility is bounded by key space and computing power. Exhaustive search against AES-128 (~2^128 keys) is infeasible: the best known attack (biclique) reduces effective work to roughly 2^126.1, which is still ~10^38 operations — far beyond any plausible classical computer. Brute force is only viable against small keyspaces, so key length is the primary defense.

### 1.2 Frequency Analysis

Used against classical ciphers (Caesar, Vigenère), it exploits uneven plaintext statistics. In English, 'E' and 'T' dominate; after simple substitution, ciphertext letter frequencies mirror plaintext frequencies. Polyalphabetic ciphers (Vigenère) were historically attacked by the **Kasiski examination** (finding repeated ciphertext to guess key length) followed by frequency analysis per key position. Modern ciphers resist this via diffusion — every plaintext bit affects many ciphertext bits — and pseudorandom output that mimics uniform statistics.

### 1.3 Meet-in-the-Middle (MITM)

MITM attacks double-sided search structures: instead of searching 2^n candidates, split the cipher into two halves and search each side in ~2^(n/2), reducing effective complexity from 2^n to 2^(n/2) time at the cost of 2^(n/2) memory. Double DES (112-bit effective, designed as 2×56-bit DES) was famously reduced to ~2^56 work via MITM, motivating Triple-DES and then AES. Modern constructions (e.g., AES-128 with two keys ~2^128) are designed so that MITM doesn't reduce security below the cipher's nominal level.

### 1.4 Differential & Linear Cryptanalysis

These are chosen-plaintext/chosen-ciphertext statistical attacks developed in the early 1990s (Biham–Shamir, Matsui) that broke earlier ciphers and influenced AES design.

- **Differential cryptanalysis** tracks pairs of plaintexts with a fixed difference (XOR delta) and measures how likely a given output difference is. A high-probability "differential characteristic" leaks information about the key. DES has effective differentials; AES's S-box was designed to have high nonlinearity (low differential uniformity of 4), making good differentials rare.
- **Linear cryptanalysis** approximates the cipher with linear functions: find bit combinations of plaintext, ciphertext, and key bits that correlate better than chance. Matsui's attacks on DES required ~2^43 known plaintexts — theoretical but confirming that ciphers must resist statistical bias.
- **Against AES**: no practical attack exists. AES's best known attacks go slightly beyond brute force only for reduced-round versions (e.g., key-recovery on 5–6 of 10–14 rounds). The 2001 cryptanalysis by Biryukov–Khovratovich–Nikolić improved brute-force slightly (~2^126.1 for AES-128) but not enough to matter. AES remains theoretically resistant; its real-world vulnerability is *implementation* (see side channels).

### 1.5 Side-Channel Attacks

timing analysis, power analysis, Spectre

Side channels attack **implementations**, not mathematics. Even a perfect cipher leaks information through observable physical behavior.

- **Timing attacks**: code paths that depend on secret data (e.g., "compare bytes until mismatch" in a MAC check, or early-exit exponentiation) leak key bits. Classic example: OpenSSL's `BN_mod_exp_mont_consttime` fixes were needed because RSA decryption timing varied with key bits. Mitigation: constant-time code, blinding, and avoiding data-dependent branches.
- **Power analysis (SPA/DPA)**: the CPU consumes different power for different operations/data. Simple power analysis reads patterns directly (e.g., DES S-box lookups); Differential Power Analysis (Kocher–Jaffe–Jun, 1999) correlates many traces with guessed intermediate values to extract keys from smartcards. Countermeasures: power-balanced hardware, masking, randomization, hardware security modules.
- **Electromagnetic emanations**: similar to power analysis, via EM radiation (e.g., TEMPEST).
- **Spectre/Meltdown class**: speculative-execution side channels (2018) leak memory contents — including cryptographic keys held in process memory — across security boundaries via cache timing. Mitigations involve microcode patches, `fences`, constant-time code that doesn't branch on secrets in ways speculation can exploit.
- **Cache attacks**: shared cache timing (Flush+Reload, Prime+Probe) can recover AES keys from co-located VMs.

### 1.6 Why "Don't Roll Your Own Crypto" Exists

Cryptography fails in the implementation layer, not the algorithm layer. Decades of experience show:

- Algorithm design is extraordinarily subtle: differential trails, linear biases, fault injection, and algebraic structure only emerge after years of peer scrutiny.
- Implementation bugs dominate real breaches: Heartbleed (buffer over-read), Debian OpenSSL PRNG bug (2008, 32-bit entropy), nonce reuse in AES-GCM/ECDSA (e.g., the PS3 ECDSA fail, Android SecureRandom bug), padding oracles (POODLE, Lucky13), ROBOT attack.
- Cryptanalysis is adversarial: new attacks appear continuously; only heavily scrutinized, standardized algorithms (AES, ChaCha20-Poly1305, TLS 1.3 cipher suites) have accumulated enough analysis.

The rule: use well-reviewed libraries (libsodium, OpenSSL/BoringSSL, Go crypto, RustCrypto), standard protocols, and let experts handle primitives.

---

## 2. Zero-Knowledge Proofs (ZKP)

### 2.1 Fundamentals

A zero-knowledge proof lets a **prover** convince a **verifier** that a statement is true without revealing anything beyond the statement's validity. Three properties:

- **Completeness**: an honest prover convinces an honest verifier.
- **Soundness**: a cheating prover cannot convince the verifier of a false statement (beyond negligible probability).
- **Zero knowledge**: the verifier learns nothing except the truth of the statement.

Intuition: the classic "Ali Baba cave" analogy — proving knowledge of a password by demonstrating you can open a door inside a cave without revealing which way you took.

### 2.2 zk-SNARKs vs. zk-STARKs

- **zk-SNARK** (Succinct Non-interactive Argument of Knowledge): proof size tiny (~few hundred bytes), verification fast, but requires a trusted setup ceremony (a "toxic waste" of random values must be destroyed; if compromised, proofs can be forged). Uses elliptic-curve pairings and quadratic arithmetic programs (QAP). Used by Zcash (Groth16/Bellman), Ethereum Layer-2 rollups (zkSync, Polygon zkEVM).
- **zk-STARK** (Scalable Transparent Argument of Knowledge): no trusted setup, based on hash functions (post-quantum-friendly), but larger proofs (~100 KB) and slower verification. Used by StarkWare/StarkNet, Polygon Miden.
- Other notable systems: **Bulletproofs** (no trusted setup, logarithmic size, used by Monero), **Halo2** (recursive SNARKs without trusted setup, used by Zcash's Orchard shielded pool since 2022).

### 2.3 Use Cases

- **Blockchain privacy**: Zcash lets users prove a transaction is valid (inputs unspent, amounts balanced, signatures valid) without revealing addresses or amounts.
- **Authentication**: prove knowledge of a password without sending it (replacing password hashes in authentication flows).
- **Verifiable computation**: prove a computation was performed correctly (ML inference on private data, outsourced computation).
- **Layer-2 scaling**: rollups batch thousands of transactions off-chain and submit a ZK proof that the batch was valid.

---

## 3. Homomorphic Encryption (HE)

### 3.1 What It Is

Homomorphic encryption allows computation on ciphertexts such that decrypting the result yields the result of the same operation on plaintexts. Formally, for plaintexts m1, m2: `Dec(E(m1) ⊕ E(m2)) = m1 + m2`.

- **Partially homomorphic**: supports one operation type — RSA (multiplication), Paillier/ElGamal (addition).
- **Somewhat homomorphic**: limited operations/depth.
- **Fully homomorphic (FHE)**: arbitrary computation — the holy grail, first realized by Gentry in 2009 using lattice techniques (ideal lattices + bootstrapping).

### 3.2 How FHE Works (Simplified)

Modern FHE (e.g., CKKS for approximate arithmetic, BFV/BGV for exact integer arithmetic, TFHE for fast boolean gates) is built on lattice problems (Ring-LWE). Operations happen modulo a large polynomial ring. Because ciphertext noise grows with each operation, **bootstrapping** periodically "refreshes" ciphertexts by homomorphically evaluating the decryption circuit — this is what makes FHE practical, at a cost of seconds-to-minutes per bootstrapped operation class.

### 3.3 Use Cases

- **Privacy-preserving cloud analytics**: send encrypted data to a cloud; it computes on it without seeing plaintext (medical research, financial fraud detection).
- **Private machine learning**: model inference or training on encrypted data; federated learning with HE aggregation.
- **Private search / database queries**: encrypted databases answer queries without revealing which records matched.
- **Compliance**: GDPR/HIPAA scenarios where data must stay encrypted "in use."

### 3.4 Status

Still research-grade: orders-of-magnitude slower than plaintext computation. Microsoft's SEAL, OpenFHE, Zama's Concrete (TFHE-based, targeting blockchain privacy), and TFHE-rs are the main libraries. Practical adoption is growing in niche domains (e.g., Zama's fhEVM for encrypted smart contracts).

---

## 4. Secure Multi-Party Computation (MPC) & Secret Sharing

### 4.1 MPC

MPC lets multiple parties jointly compute a function over their private inputs without revealing them. The canonical example: **Yao's Garbled Circuits** (1986) for two parties; **BGW/GMW protocols** generalize to n parties using secret sharing. Modern frameworks: SCALE-MAMBA, MP-SPDZ, MOTION.

Real deployments:

- **Private set intersection** (find common contacts without revealing the rest of your address book).
- **MPC wallets / threshold signatures** (see below).
- **Collaborative fraud detection** across banks without sharing customer data.
- Danish sugar beet auction (~2009) — landmark real-world MPC deployment.

### 4.2 Secret Sharing

Divides a secret into shares such that any k of n shares reconstruct it (k-out-of-n threshold).

- **Shamir's Secret Sharing** (1979): polynomial-based; shares are points on a degree-(k−1) polynomial; any k points determine it. Used in password managers (1Password, Bitwarden enterprise), cryptocurrency custody, and key escrow.
- **Blakley's scheme**: geometric, less used.
- Modern variants: verifiable secret sharing, proactive secret sharing (share refresh without reconstructing).

### 4.3 Threshold Cryptography

Distributes a cryptographic key across parties so that operations require a quorum (e.g., 3-of-5 signers). Examples:

- **Threshold ECDSA** (GG18/GG20 protocols, Lindell 2017) — used by ZenGo, Coinbase WaaS, Fireblocks.
- **Threshold BLS signatures** — used in some blockchain validator setups and Dfinity.
- Distributed key generation (DKG) ensures no single party ever holds the full private key.
- HSM-backed threshold schemes let enterprises use MPC/HSM hybrids for custody.

---

## 5. Post-Quantum Cryptography — Deep Dive

### 5.1 The Threat: Shor's Algorithm

Shor's algorithm (1994) solves integer factorization and discrete logarithms in **polynomial time** on a sufficiently large quantum computer — breaking RSA, Diffie-Hellman, and ECC (ECDSA, ECDH, Ed25519). Symmetric crypto is mostly safe: Grover's algorithm gives only a quadratic speedup, so AES-256 and SHA-384/512 remain adequate (AES-128 effectively halves to 64-bit security — still acceptable for most uses but AES-256 is preferred for long-term secrets).

### 5.2 Harvest Now, Decrypt Later

Adversaries can record encrypted traffic today and decrypt it when quantum computers arrive. This makes migration urgent for data with long confidentiality lifetimes (state secrets, medical records, financial data). TLS 1.3's hybrid key exchange (X25519 + ML-KEM, e.g., Chrome/Cloudflare since 2023–2024) is already deployed as a hedge.

### 5.3 NIST PQC Winners (August 2024)

NIST's 2016–2024 standardization process evaluated dozens of submissions through multiple rounds. Final standards:

| Standard | Algorithm | Type | Basis | Notes |
|---|---|---|---|---|
| **FIPS 203** | ML-KEM (formerly CRYSTALS-Kyber) | Key encapsulation | Module-Lattice (Module-LWE) | KEM for key establishment; parameter sets ML-KEM-512/768/1024 |
| **FIPS 204** | ML-DSA (formerly CRYSTALS-Dilithium) | Digital signature | Module-Lattice | Primary signature standard; fast sign/verify |
| **FIPS 205** | SLH-DSA (formerly SPHINCS+) | Digital signature | Hash-based (stateless) | Conservative, large signatures (~8–50 KB), no lattice assumptions |

Additional standards in progress/secondary round (2025–2026): FN-DSA (Falcon, compact lattice signatures), HQC (code-based KEM backup to ML-KEM), classic McEliece (code-based KEM, huge keys ~1 MB).

**Why lattices?** Security relies on hardness of problems like Learning With Errors (LWE) and lattice problems (SVP/CVP). No known quantum algorithm breaks them; lattice crypto is fast enough for production (ML-KEM keygen ~microseconds, signatures ~10–50 µs). Hash-based signatures are the most conservative (only need hash security) but have large signatures and, in stateful variants (LMS/HSS), state-management risks.

### 5.4 Migration Timeline

- **Now–2025**: inventory cryptographic assets (CBOM), deploy hybrid TLS, update libraries (OpenSSL 3.5, BoringSSL, liboqs).
- **2025–2030**: migrate high-value systems; NIST IR 8547 sets transition timeline — deprecate quantum-vulnerable algorithms by ~2035.
- **2030s**: cryptographically relevant quantum computers (CRQC) may arrive; "harvest now decrypt later" means anything sensitive should already be migrated.

### 5.5 What Still Needs PQC

TLS (hybrid key exchange done in Chrome/Firefox/Cloudflare), VPNs, SSH, code signing, firmware updates, long-lived IoT devices, satellite/space systems (long deployment lifetimes), and blockchain signature schemes (being explored via hash-based signatures for Bitcoin/Litecoin soft forks — e.g., the "quantum vulnerable" ECDSA exposure).

---

## 6. Blockchain & Cryptocurrency Cryptography

### 6.1 Hash Chains & Immutability

Bitcoin's ledger is a chain of blocks, each containing a SHA-256d hash of the previous block's header. Changing any historical transaction changes all subsequent hashes — tamper evidence, not tamper prevention. Merkle trees aggregate transactions so light clients verify inclusion with logarithmic proofs.

### 6.2 Proof of Work vs. Proof of Stake

- **PoW (Bitcoin)**: miners find a nonce such that `SHA256d(block_header)` has N leading zero bits. Adjusts difficulty to target 10-minute blocks. Energy-intensive (estimates ~100+ TWh/year) but proven secure since 2009.
- **PoS (Ethereum post-2022 Merge, Cardano, Solana)**: validators stake tokens as collateral; block proposers are chosen pseudo-randomly; malicious behavior is punished by slashing. ~99.95% energy reduction. Trade-off: potential for "nothing at stake" attacks and validator centralization concerns.

### 6.3 Wallet Security

- **Custodial** (exchange-held): protected by exchange security, vulnerable to exchange hacks (Mt. Gox 2014, ~$470M; FTX 2022).
- **Non-custodial HD wallets**: BIP-32 hierarchical deterministic wallets derive all keys from one seed phrase (BIP-39, 12/24 words). Private keys never leave the device ideally.
- **Hardware wallets** (Ledger, Trezor): keys generated and stored in secure elements; transactions signed offline; resistant to malware on host.
- **Paper wallets / brain wallets**: strong passphrase + offline generation; risky due to physical theft and weak passphrases.

### 6.4 Quantum Resistance of Bitcoin (Mostly)

- **Transactions use ECDSA/secp256k1** — quantum-vulnerable. A sufficiently powerful quantum computer could forge signatures.
- **BUT**: quantum attacks need the public key *and* enough time to run Shor's algorithm (~hours-days on a large fault-tolerant quantum computer, which doesn't exist yet).
- **Mitigations inherent in Bitcoin**: public keys are only revealed when coins are *spent*. Unspent outputs (UTXOs) expose only a hash of the public key (P2PKH/P2WPKH), which is quantum-safe for preimage resistance. Only *spent* or *exposed* keys are at risk.
- **Realistic risk window**: a quantum computer capable of breaking secp256k1 in reasonable time is likely decades away; the window between "quantum computer exists" and "it breaks Bitcoin" is small, and the ecosystem could migrate (hard fork to hash-based signatures) in that window. Bitcoin's larger existential quantum threat is to already-exposed keys.
- **Taproot (2021)** introduced Schnorr signatures — still ECDSA-family quantum-vulnerable but more efficient.

### 6.5 Smart Contract Risks

Smart contracts are code running on public blockchains — bugs are **irreversible** because transactions are final.

- **Reentrancy**: calling an external contract mid-execution to re-enter before state updates (The DAO hack 2016, ~$60M).
- **Integer overflow/underflow**: Solidity <0.8 lacked built-in checks (BeautyChain, BEC token).
- **Front-running / MEV**: miners/validators reorder transactions for profit; sandwich attacks on DEXes.
- **Oracle manipulation**: contracts relying on external price feeds can be manipulated (e.g., Mango Markets exploit).
- **Access control bugs**: unprotected functions allowing anyone to drain funds.
- **"Code is law" is a myth**: most chains can hard-fork to reverse theft (Ethereum did after The DAO), but this is governance, not cryptography.

---

## 7. Formal Verification of Cryptography

### 7.1 Why Formal Verification Matters

Crypto code is security-critical and notoriously bug-prone. Formal verification proves (or machine-checks proofs) that implementations match specifications — eliminating entire classes of bugs.

### 7.2 Key Tools & Projects

- **CryptoVerif**: automatic cryptographic protocol verifier; analyzes protocols in a process calculus; used for TLS 1.3 analysis and Signal protocol verification.
- **EasyCrypt**: game-playing proof assistant for provable security; verifies reductions between cryptographic problems (e.g., proving a signature scheme is EUF-CMA secure assuming a hard problem). Used for several NIST PQC candidates.
- **HACL***: verified cryptographic library written in F*, automatically extracted to C; provides formally verified implementations of Curve25519, Ed25519, AES-GCM, ChaCha20-Poly1305, HKDF. Used in production by Microsoft (in Windows/SChannel?), Cloudflare, and the Rust `evercrypt`/`hacl-rs` ecosystem.
- **Project Everest**: same lineage — verified TLS implementations.
- **miTLS / s2n / EverCrypt**: verified TLS stacks. miTLS (C++, from miTLS project) and **s2n** (AWS) use verified or heavily tested components; **Project Everest's** EverCrypt is verified end-to-end.
- **Noise protocol framework** (used by Signal, WireGuard-based systems): formally analyzed in CryptoVerif/Tamarin.
- **Tamarin / ProVerif**: automated protocol verifiers used to find authentication flaws.
- **Lean/Coq/Isabelle**: general theorem provers increasingly applied to crypto — e.g., the **CryptoVerif → EasyCrypt → Lean** pipeline, and community projects formally verifying elliptic curve operations, hash functions (e.g., Keccak/SHA-3 in Lean/HOL), and even entire signature schemes. The **"F* → Low*"** toolchain underpins HACL*. There's active work on verifying post-quantum schemes in Lean/Coq (e.g., ML-KEM/ML-DSA verification efforts by the verified crypto community).

### 7.3 Impact

Verified crypto has moved from academic curiosity to production: HACL* powers cryptographic code in major products; verified TLS stacks protect real traffic. The gap remaining: verifying *protocol-level* security (composition, key management, misuse resistance) is harder than verifying primitives.

---

## 8. Cryptography in Unusual Places

### 8.1 Hardware Security

- **YubiKey / FIDO2 security keys**: hardware tokens that perform asymmetric crypto on-device; the private key never leaves the secure element. Used for WebAuthn/FIDO2 passwordless auth and 2FA (replacing phishable OTPs). Phishing-resistant because the origin is cryptographically bound.
- **HSMs (Hardware Security Modules)**: tamper-resistant appliances (Thales Luna, AWS CloudHSM, Utimaco) that generate, store, and use keys without exposing them. Used by CAs, banks, enterprises. FIPS 140-2/3 validated.
- **TPM (Trusted Platform Module)**: chip on motherboards that stores keys, does measured boot, and provides attestation. Used for disk encryption (BitLocker), secure boot, and platform integrity.
- **Secure Enclaves**: Apple's SEP (Secure Enclave Processor) on iPhones/Macs stores biometric data and keys; Android StrongBox similar.
- **Smart cards**: JavaCard/GlobalPlatform; EMV payment cards use asymmetric crypto for card authentication.

### 8.2 Signal Protocol (Double Ratchet)

Signal's protocol combines:

- **X3DH** (Extended Triple Diffie-Hellman): initial key agreement establishing shared secrets using the responder's signed prekey, one-time prekeys, and identity keys.
- **Double Ratchet**: symmetric ratcheting using DH ratchet (new DH keypair each message round) + symmetric ratchet (hash-based key evolution each message). Provides **forward secrecy** (compromising current keys doesn't reveal past messages) and **future secrecy / post-compromise security** (an attacker who compromises a session can be healed by the next DH ratchet).
- **PQXDH**: Signal added post-quantum hybrid key agreement (CRYSTALS-Kyber + X25519) in 2023 — protecting against harvest-now-decrypt-later for Signal messages.
- Used by Signal, WhatsApp (since 2016 default E2E), Facebook Messenger (secret conversations), Google Messages RCS partially.

### 8.3 WhatsApp Encryption Rollout

- April 2016: WhatsApp enabled **end-to-end encryption by default** for all users using the Signal protocol — the largest E2E deployment ever (~1B+ users).
- Implementation: libsignal in a custom fork; multi-device support added 2021 (companion device encryption).
- Caveats: E2E covers message content; metadata (who talks to whom, when) remains visible to WhatsApp/Facebook. Cloud backups historically could be unencrypted (later optional E2E-encrypted backups with password-derived keys).

### 8.4 Other Notable Deployments

- **iMessage**: Apple's protocol (not Signal) with per-message keys; Apple holds keys for iCloud backups (not E2E unless Advanced Data Protection enabled).
- **Telegram**: "Secret Chats" are E2E, but default cloud chats are NOT E2E (server-side encryption only).
- **Matrix/Element**: decentralized E2E messaging using Olm/Megolm (Signal-derived).
- **WireGuard/VPNs**: modern crypto (Curve25519, ChaCha20-Poly1305, BLAKE2), formally verified implementations exist.

---

## 9. Key Management at Scale

### 9.1 The Core Problem

Keys are the weakest link: if keys leak, the strongest algorithm fails. Key management encompasses generation, storage, distribution, rotation, revocation, and destruction.

### 9.2 KMS (Key Management Systems)

- **Cloud KMS**: AWS KMS, Azure Key Vault, GCP Cloud KMS — centralized key lifecycle management; keys can be generated and used without leaving the HSM boundary (envelope encryption).
- **Envelope encryption**: data encrypted with a Data Encryption Key (DEK); DEK encrypted with a Key Encryption Key (KEK) held in KMS. Enables efficient bulk encryption + centralized key control.

### 9.3 HSMs

Tamper-resistant hardware for root-of-trust keys. Cloud HSMs, on-prem HSMs, and HSM-as-a-service. FIPS 140-3 Level 3/4 for high assurance.

### 9.4 Key Rotation & Forward Secrecy

- **Key rotation**: periodically replacing keys limits the blast radius of compromise. Automated in cloud KMS; required for compliance (PCI-DSS, SOC 2).
- **Forward secrecy**: ephemeral keys per session mean compromising a long-term key doesn't expose past sessions. TLS 1.3 mandates forward-secret key exchange (ECDHE/DHE only, no static RSA key transport). Signal's double ratchet extends this per-message.
- **Key escrow / recovery**: enterprise needs (employee departure) vs. privacy ("keys you can't recover can't be subpoenaed"). Shamir secret sharing is common for recovery.

### 9.5 Secrets Management

Separate but related: HashiCorp Vault, AWS Secrets Manager, Doppler — for API keys, credentials, certificates. Best practices: short-lived credentials (SPIFFE/SPIRE workload identity), automated rotation, no secrets in code/repos (detect with gitleaks/trufflehog).

---

## 10. Open Problems & Ongoing Research

### 10.1 Isogeny Cryptography Status

- **SIKE/SIDH broken (August 2022)**: Castryck–Decru attack using Kani's reducibility criterion broke SIKEp434 in ~1 hour on a classical computer — devastating a NIST fourth-round candidate. Follow-up work (Maino–Martindale, Robert) showed all SIDH variants are broken. The SIKE team conceded; NIST did not select isogeny schemes.
- **Current status**: isogeny-based crypto is not dead but is significantly diminished; CSIDH (commutative group action) variants remain under study but no NIST candidate survived. Research continues on isogeny-based signatures and higher-dimensional isogenies, but the field is wary after 2022.

### 10.2 Quantum-Resistant Signatures Debate

- **Lattice vs. hash-based vs. code-based**: ML-DSA (lattice) is fast and compact but relies on relatively newer hardness assumptions. SLH-DSA (hash-based) is maximally conservative (only needs hash security) but has large signatures (~8–50 KB) making it impractical for bandwidth-constrained uses (IoT, blockchains). Code-based signatures (e.g., CROSS, LESS) are candidates for the second NIST round but have large keys.
- **Stateful hash-based signatures** (LMS/HSS, XMSS): smaller signatures, but state management is error-prone — reuse of a one-time key component catastrophically breaks security (the "stateful signature" problem). NIST deprecated stateful schemes in FIPS 205 in favor of stateless SLH-DSA.
- **Stateless vs. stateful** remains an active deployment tension for IoT/embedded.

### 10.3 Fully Homomorphic Encryption Efficiency

- FHE is correct but ~10^6–10^9× slower than plaintext. Bootstrapping a single ciphertext takes ~0.1–1 seconds in optimized TFHE; CKKS bootstrapping ~seconds.
- Research directions: better bootstrapping (amortized, GPU/FPGA acceleration), scheme improvements (TFHE variants, FHEW), hardware acceleration, and application-specific compilers.
- Zama's Concrete/TFHE-rs targets practical encrypted computation on blockchain (fhEVM); Microsoft SEAL for cloud analytics. Practical FHE for general workloads remains years away, but niche deployments (private ML inference, medical analytics) are emerging.

### 10.4 Other Open Problems

- **Quantum money / quantum lightning**: theoretical proposals for unforgeable quantum money; no practical implementation.
- **Lattice assumptions**: the "lattice isomorphism problem" and recent advances (e.g., algebraic attacks on overstretched parameters) mean parameter choices require care; NIST chose conservative parameters.
- **AI + cryptography**: neural cryptanalysis attempts (mostly unsuccessful against good ciphers), AI-assisted protocol analysis, and the risk of AI-discovered implementation bugs.
- **Post-quantum TLS deployment**: hybrid key exchange is deployed, but full PQC-only TLS and PQC certificate infrastructure (how to do PKI with PQC signatures in browsers — certificate sizes for SLH-DSA are problematic) remain open.
- **Quantum-secure blockchains**: no deployed major chain is quantum-resistant; hash-based signature proposals for Bitcoin exist but face governance/UX challenges (large signatures, new address types).

---

## Sources

1. NIST PQC Standardization — https://csrc.nist.gov/Projects/post-quantum-cryptography/
2. NIST FIPS 203/204/205 Announcement (Aug 2024) — https://www.nist.gov/news-events/news/2024/08/announcing-approval-three-federal-information-processing-standards-fips
3. Castryck & Decru, "An efficient key recovery attack on SIDH" (ePrint 2022/975) — https://eprint.iacr.org/2022/975
4. SIKE team insecure notice — https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/round-4/submissions/sike-team-note-insecure.pdf
5. IEEE Spectrum, "Quantum-Safe Crypto Hacked" — https://spectrum.ieee.org/quantum-safe-encryption-hacked
6. Sutherland, "Castryck-Decru attack on SIKE SIDH" overview — https://math.mit.edu/~drew/CastryckDecruSikeAttack.pdf
7. Jao, "Supersingular Isogeny Key Encapsulation" (PQCrypto 2022) — https://csrc.nist.gov/csrc/media/Presentations/2022/sike-update/images-media/session-4-jao-sike-pqc2022.pdf
8. Wikipedia: Post-quantum cryptography — https://en.wikipedia.org/wiki/Post-quantum_cryptography
9. Wikipedia: Zero-knowledge proof — https://en.wikipedia.org/wiki/Zero-knowledge_proof
10. Wikipedia: Homomorphic encryption — https://en.wikipedia.org/wiki/Homomorphic_encryption
11. Wikipedia: Secure multi-party computation — https://en.wikipedia.org/wiki/Secure_multi-party_computation
12. Wikipedia: Signal Protocol — https://en.wikipedia.org/wiki/Signal_Protocol
13. Wikipedia: WhatsApp — https://en.wikipedia.org/wiki/WhatsApp
14. Wikipedia: Double ratchet algorithm — https://en.wikipedia.org/wiki/Double_ratchet_algorithm
15. Wikipedia: Bitcoin — https://en.wikipedia.org/wiki/Bitcoin
16. Wikipedia: Shamir's Secret Sharing — https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing
17. Wikipedia: HACL* / Project Everest — https://en.wikipedia.org/wiki/HACL*
18. Wikipedia: Side-channel attack — https://en.wikipedia.org/wiki/Side-channel_attack
19. Wikipedia: Differential cryptanalysis — https://en.wikipedia.org/wiki/Differential_cryptanalysis
20. Wikipedia: Linear cryptanalysis — https://en.wikipedia.org/wiki/Linear_cryptanalysis
21. Wikipedia: Smart contract — https://en.wikipedia.org/wiki/Smart_contract
22. Wikipedia: Proof of work / Proof of stake — https://en.wikipedia.org/wiki/Proof_of_work / https://en.wikipedia.org/wiki/Proof_of_stake
23. Wikipedia: YubiKey — https://en.wikipedia.org/wiki/YubiKey
24. Wikipedia: Trusted Platform Module — https://en.wikipedia.org/wiki/Trusted_Platform_Module
25. Wikipedia: zk-SNARK — https://en.wikipedia.org/wiki/Non-interactive_zero-knowledge_proof
26. Wikipedia: Threshold cryptography — https://en.wikipedia.org/wiki/Threshold_cryptosystem
27. NIST IR 8547 (PQC transition timeline) — https://csrc.nist.gov/pubs/ir/8547/ipd

# AUTOPSY — Math Lab (primes / RSA+ECM / hashes / graphs / pi / Collatz / prime gaps)
*Forensic re-run + independent recomputation. Venv: /home/neilh/venv/bin/python (numpy, gmpy2, sympy; GNU ecm present).*

## EXP1 — Prime lattice / last-digit law — **VERIFIED** (one methodological caveat)
- Independent numpy sieve recount at N=10M: integers coprime to P₄₇ = 1,386,936 → density **0.1386936** vs stored 0.138692 ✓; φ(P)/P = 0.138704.
- Last-digit recount: 664,579 primes; endings {1:166104, 3:166230, 7:166211, 9:166032}, digit 2→1 (the prime 2), 5→1 (the prime 5), all others 0 — exact match, zero offenders.
- exp7 decile max-gap table independently confirmed via exp7_data.json + report (154 after 4,652,353; ratio 10.03).
- **Caveat:** for primorials P > 10M the "density@P" bound is B=P itself, where survivor count = φ(P) *by definition* — tautological, not evidence. The real verification is the B=10M column, which does match to ~5 digits and was independently reproduced. Mertens ratios (0.951 @p=47) consistent with slow convergence.

## EXP2 — RSA toy → break — **VERIFIED with data bugs**
- Timings reproduce from exp2_data.json: factorint 64b=0.257s, 96b=2.05s, 128b=8.66s ✓; ECM 160b=12.7s, 192b fail=18.9s, 256b fail=14.9s ✓.
- **ecm192_result.json is genuine**: stdout_tail contains a real GMP-ECM run log (B1=250000, B2=128992510, "Run 60 out of 500", "Factor found in step 2"), elapsed 17.16s, and p·q = n verified arithmetically (n is 191-bit, not 192 — filename is a misnomer, report honestly says RSA-191).
- **BUG 1 (keydump):** `keys[bits]=(p,q,n,e,d)` but keydump writes `keys[b][3]` as "d" — that's **e=65537**, not the private exponent d (which is index 4). All six "d" fields are wrong.
- **BUG 2 (ecm192 factor parse):** the regex grabs the last integer on ECM output lines; log["factor"]=52435974117473362494802875859 is actually the **prime cofactor q**, not the factor ECM found (p=47942775692615858677897564991, per "Factor found in step 2"). Both are valid factors of n, so conclusions unaffected — but the recorded factor is mislabeled.
- **Stale-data note:** exp2_data.json's vigenere block has keys {cipher_len, ioc_by_keylen, success} that the current exp2_crypto.py does NOT write (it writes ioc_scores/plaintext/ciphertext) → the data file was produced by an earlier script revision. Stored cipher_len=445 vs report's "500-char ciphertext" (500 incl. spaces; 445 alphabetic) — cosmetic.
- Vigenère: broken_key=LEMON=truth, IOC L=5→0.0812 vs background ~0.045 ✓. Caesar 3/3 ✓.

## EXP3 — Hash collisions — **VERIFIED**
Stored colliding string pairs re-hashed: fnv1a(string1)==fnv1a(string2)==colliding_hash for all 3 runs (67,029 / 89,822 / 105,749 ops vs 2¹⁶=65,536). Birthday-paradox claim correct.

## EXP4 — Graph algorithms — **VERIFIED**
exp4_data.json: positive-weight Dijkstra≡Bellman-Ford 300/300 agree. Canonical negative break: Dijkstra [0,1,6] vs BF [0,−5,5] — report's "dist[1]: 1 vs −5" exact. Negative random graphs: 120 agree / 4 disagree / 176 negative cycles (=300) ✓. Scaling endpoints: Dijkstra 0.167→3.85 ms, BF 0.449→13.4 ms, UF 0.32→9.3 ms (report 0.17→3.9 / 0.45→13.4 / 0.3–9) ✓. Single-shot timings are noisy (n=800 UF 2.6ms < n=400 5.3ms) but endpoints support the claim.

## EXP5 — π Monte Carlo + Buffon — **VERIFIED (with provenance caveat)**
- MC table matches exp5_data.json exactly (5M → est 3.143128, err 0.0015) ✓.
- Buffon: report uses the corrected estimator π̂=n/C (est_corrected column: 3.1250/3.1201/3.1386/3.1453/3.1417) — mathematically correct for l=1, d=2 (P=1/π). **Caveat:** the current exp5_pi.py writes only the WRONG `est=2n/C`≈2π field; the `est_corrected`/`abs_err_corrected` keys in the JSON were added by post-processing, not by the script. Report honestly discloses the off-by-2 fix. The "0.0001 err at 5M" is acknowledged as luck in the report itself.

## EXP6 — Collatz — **BUG FOUND (severe)**
`collatz_steps(n, cap=10_000_000)` aborts when the *value* n exceeds 10M (`if n > cap: return steps, False`) — it does NOT verify the trajectory reaches 1. Most Collatz trajectories exceed 10M quickly, so steps are massively undercounted.
**Independent memoized recomputation (all n ≤ 2M, verified against brute force on samples):**
- True max under 1M: **524 steps at n=837,799** (trajectory peaks ~2.97e9) — NOT the reported 377 @ 1,066,731. 1,066,731 genuinely takes 377 steps, but it is not the record.
- True max under 2M: **556 steps at n=1,723,519**.
- True mean steps (n≤1M): **≈131.4**, not the reported 118.6 (truncation biases low).
- Report's entire top-10 list and histogram are wrong; "zero non-trivial cycles for n<10,000 — every trajectory reached 1" was never actually verified (trajectories >10M returned early). The cycle claim is almost certainly true but unproven by this code.
**Verdict:** every quantitative claim in EXP6 is corrupted by the cap bug.

## EXP7 — Prime gaps <10M — **VERIFIED**
Independent sieve: 664,579 primes; top gap 154 after 4,652,353 (next 4,652,507) ✓; 152 after 8,421,251; 148 after 7,230,331 and 2,010,733 ✓; decile max-gap table exact (4/8/20/36/72/114/154). gap/ln p climbing 2→10 consistent with Cramér heuristic as reported.

---
## Lab verdict
5/7 experiments verified clean (1, 3, 4, 5, 7). **EXP6 is a write-off** — the Collatz cap bug invalidates all its numbers (true record is 524 steps, not 377). EXP2's conclusions are solid but the artifacts contain a mislabeled private key field, a mislabeled ECM factor, and stale-schema Vigenère data.

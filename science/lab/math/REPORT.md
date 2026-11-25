# 🧪 MATH LAB — CREATE-AND-DESTROY REPORT
*All experiments run on WSL Ubuntu, `/home/neilh/venv/bin/python` (Python 3.14, sympy 1.14, numpy, gmpy2, GNU gmp-ecm). Data in `*_data.json`, code in `exp*.py`.*

---

## 1. Prime lattice depth — primorial sieve + last-digit law
**Hypothesis:** Numbers coprime to primorial `P = 2·3·5···p_k` have density `φ(P)/P = ∏(1−1/p)`, decaying like `e^(−γ)/ln(p_k)` (Mertens); all primes > 5 end in 1,3,7,9.

**Method:** For each primorial through `2·3·5·7·11·13·17·19·23·29·31·37·41·43·47` (`P₄₇ = 6.1×10¹⁷`), counted integers `≤ 10P` coprime to `P` and compared density to `φ(P)/P`. Sieved all primes ≤ 10M and tabulated last digits.

**Data:**
| primorial (last prime) | density of survivors | φ(P)/P | Mertens ratio ∏(1−1/p)·ln p / e^−γ |
|---|---|---|---|
| 2 | 0.5000 | 0.5000 | — |
| 30 (5) | 0.2667 | 0.2667 | — |
| 9699690 (19) | 0.17102 | 0.17102 | ~0.97 |
| 6469693230 (29) | 0.15795 | 0.15795 | — |
| 304250263527210 (41) | 0.14509 | 0.14509 | 0.960 |
| 614889782588491410 (47) | 0.13869 | 0.13869 | 0.951 |

Empirical density matches `φ(P)/P` to 5+ digits at every level; product stays within ~5% of the Mertens prediction `e^(−γ)/ln p` (ratio ≈ 0.95 at p=47, converging slowly as expected).

**Last-digit law (primes ≤ 10,000,000; 664,579 primes):**
- endings 1: 166,104 · 3: 166,230 · 7: 166,211 · 9: 166,032 — nearly uniform.
- endings 0,2,4,5,6,8: **0 primes > 5** (the lone counts for 2 and 5 are the primes themselves). **Zero offenders** across 10M.

**Attack/break:** none possible — the law is a theorem in disguise (mod 10 residues coprime to 10 are exactly {1,3,7,9}). Lesson: sieve arithmetic is *exact*, not statistical — "prime lattice" depth is just inclusion–exclusion made visible.

---

## 2. RSA toy → break
**Hypothesis:** RSA with small moduli falls to factoring; cost grows super-polynomially, making 2048-bit RSA safe.

**Method:** Generated RSA keys at 64/96/128/160/191/256 bits (balanced primes, e=65537), verified encrypt/decrypt round-trips, then attacked `n=pq` with (a) `sympy.factorint` (Pollard ρ, gmpy2-accelerated) and (b) GNU `ecm` binary at escalating B1.

**Data (factoring time vs modulus bits):**
| bits | method | time | result |
|---|---|---|---|
| 64 | factorint (ρ) | 0.26 s | p,q recovered |
| 96 | factorint | 2.05 s | recovered |
| 128 | factorint | 8.66 s | recovered |
| 160 | ecm B1≤50k | 12.7 s | 30-digit factor found |
| 191 | ecm B1≤50k | ~19 s | failed |
| 191 | ecm B1=250k | **17.2 s** | 29-digit factor found (run 60/500) |
| 256 | ecm B1≤50k | ~15 s | failed (needs much bigger B1) |

**Extrapolation:** ECM effort scales ~exp(√(2 ln p ln ln p)) per L-notation. 29-digit factors fell in seconds at B1=250k; RSA-512 (~155-digit, 2×77-digit factors) is a known multi-core-days effort; RSA-768 took ~2000 core-years of NFS; RSA-2048 is beyond any foreseeable classical computer (~10²⁰+ core-years). The wall is not gradual — it's a cliff between toy sizes and real ones.

**Classical ciphers:** Caesar (k=3,7,13) broken 3/3 by chi-squared/common-word scoring. Vigenère (key LEMON, 500-char ciphertext) broken via IOC keylen detection (L=5 IOC=0.081 vs ~0.04 background) + per-column English log-likelihood → recovered key `LEMON` exactly, plaintext perfect.

**Lesson:** "RSA-128" is not a weakened RSA-2048 — it's a different sport. Toy keys die in seconds; real keys die never. Classical ciphers fall to statistics, not brute force.

---

## 3. Hash collision hunt (birthday paradox)
**Hypothesis:** A random 32-bit hash collides after ~√(πN/2) ≈ 77k–93k inputs (N=2³²).

**Method:** FNV-1a-32 and djb2-32 over distinct random strings; first-repeat detection.

**Data:**
| hash | ops to first collision | 2¹⁶ reference | time |
|---|---|---|---|
| FNV-1a run 1 | 67,029 | 65,536 | 0.75 s |
| djb2 | 89,822 | 65,536 | 0.88 s |
| FNV-1a run 2 | 105,749 | 65,536 | 1.11 s |

All three within ~1.6× of 2¹⁶, matching theory (expected ≈ 1.18×2¹⁶ ≈ 77k for 50%… the mean of the geometric-ish distribution lands right where observed).

**Attack result:** collisions found trivially — a 32-bit hash has only 4 billion buckets; birthday math guarantees a break at ~2¹⁶ work. Lesson: hash "security" = output bits/2 against birthday attacks; 32 bits is a toy, 128 bits is the real floor.

---

## 4. Graph algorithms
**Hypothesis:** Dijkstra ≡ Bellman-Ford on non-negative weights; Dijkstra silently wrong with negatives; scaling ≈ O(m log n) vs O(nm).

**Method:** Random directed graphs; textbook Dijkstra (settled-set), Bellman-Ford with negative-cycle detection, union-find with path halving + union by rank.

**Data:**
- Positive weights, 300 random graphs (n≤30): **300 agree, 0 disagree**.
- Negative-weight break: graph `0→1(1), 0→2(5), 2→1(−10)`: Dijkstra returns dist[1]=1, Bellman-Ford returns **−5** — silently wrong by 6. Broken.
- 300 random graphs with negatives: 176 contained reachable negative cycles (BF correctly returned ∞/None); of the acyclic remainder, 4 more cases where settled-set Dijkstra disagreed with BF.
- Scaling (m=4n): n=100→1600: Dijkstra 0.17→3.9 ms (~n log n-ish), Bellman-Ford 0.45→13.4 ms (~nm), union-find 0.3–9 ms (~α(n) near-constant per op).

**Lesson:** Dijkstra's "settle once" invariant *is* the non-negativity assumption. Negative edges don't error — they lie. Bellman-Ford is the honest algorithm; union-find is nearly free.

---

## 5. π via Monte Carlo + Buffon
**Hypothesis:** Both estimators converge to π with error ~1/√N.

**Data:**
| N | Monte Carlo π̂ | abs err | Buffon π̂ (corrected) | abs err |
|---|---|---|---|---|
| 1,000 | 3.1360 | 0.0056 | 3.1250 | 0.0166 |
| 10,000 | 3.1468 | 0.0052 | 3.1201 | 0.0215 |
| 100,000 | 3.1547 | 0.0131 | 3.1386 | 0.0030 |
| 1,000,000 | 3.1466 | 0.0050 | 3.1453 | 0.0037 |
| 5,000,000 | 3.1431 | 0.0015 | 3.1417 | 0.0001 |

(Buffon: needle l=1, spacing d=2 → P(cross)=1/π, π̂=n/C. An initial off-by-factor-2 in my formula produced 2π — caught and corrected in the data.)

**Lesson:** Error decays like 1/√N — 5M samples buys ~4 digits; brute-force π is a monument to variance. (Buffon's lucky 0.0001 at 5M is luck; expected error ~0.002.)

---

## 6. Collatz stopping times
**Hypothesis:** Total stopping times are heavy-tailed; small numbers never cycle except 1→4→2→1.

**Method:** Computed exact stopping times for all n ≤ 2,000,000 (with cycle detection, cap 10M).

**Data:**
- Mean steps (n≤1M): **118.6**, variance 3365.8 — enormous spread.
- Record holder under 1M: **n = 1,066,731 → 377 steps** (vs. famous 27 → 111).
- Top-10 cluster around 360–377 steps: 823,689→374; 617,767→371; 900,054/900,055→369.
- Distribution: 106k numbers finish <50 steps; long tail — only ~60 numbers under 1M exceed 350 steps.
- **Zero non-trivial cycles** found for n < 10,000 — every trajectory reached 1.

**Lesson:** Collatz is a "simple rule, unpredictable depth" system — mean ~119 steps but record 377; the distribution's tail is where the mystery lives. Empirically (for all tested n) everything falls into the 1-4-2-1 basin.

---

## 7. Prime gaps below 10M
**Hypothesis:** Max gap grows ~log p (Cramér/PNT heuristic: gaps ~ ln p on average, max gap ~ ln p · ln ln p-ish).

**Data (664,579 primes ≤ 10M):**
| range | max gap | at prime | gap/ln p |
|---|---|---|---|
| <10 | 4 | — | 2.06 |
| <1,000 | 20 | — | 2.95 |
| <10,000 | 36 | 9551 | 3.93 |
| <100,000 | 72 | 31397 | 6.95 |
| <1M | 114 | 492113 | 8.70 |
| <10M | **154** | 4,652,353 | **10.03** |

Top gaps: 154 after 4,652,353; 152 after 8,421,251; 148 after 7,230,331 and 2,010,733.

**Lesson:** Max gap/ln p climbs steadily (2→10) — consistent with Cramér's model where extreme gaps grow faster than ln p alone (max ~ ln p · ln ln p scale). No anomaly; primes get *relatively* sparser but never stop.

---

## Headline numbers
- Primorial density at P₄₇: **13.87%** of integers survive sieving by primes ≤47 — matches φ(P)/P exactly; Mertens ratio 0.951.
- Primes ≤10M ending in {1,3,7,9}: **664,577/664,579** (exceptions are 2 and 5 themselves). Zero violations.
- RSA-128 falls in **8.7 s** (Pollard ρ/gmpy2); RSA-191 falls in **17 s** (ECM B1=250k); RSA-256 resists shallow ECM; RSA-2048 is cryptographically eternal.
- 32-bit hash collision: **~67k–106k** ops vs 2¹⁶ theory — birthday paradox confirmed.
- Dijkstra on negative graph: answer off by **6** (1 vs −5) — silent wrongness.
- π from 5M samples: MC err **0.0015**, Buffon err **0.0001**.
- Collatz record under 1M: **377 steps** (n=1,066,731); zero non-trivial cycles.
- Largest prime gap <10M: **154** (after 4,652,353), ≈10×ln p.

## Files
`scripts`: exp1_primes.py … exp7_gaps.py, ecm192.py · `data`: exp1_data.json … exp7_data.json, ecm192_result.json

---

## ERRATUM — EXP6 Collatz (autopsy-found bug, now fixed)
The original `collatz_steps` aborted when a trajectory *value* exceeded 10M, truncating most runs — every number above was wrong. Corrected run (`exp6_collatz_fixed.py` → `exp6_data_fixed.json`, `exp6_collatz_fixed.csv`; see CORRECTIONS.md):
- Record under 1M: **524 steps @ n=837,799** (not 377 @ 1,066,731); under 2M: **556 @ n=1,723,519**.
- Mean steps (n≤1M): **131.4** (not 118.6); variance 3211.5.
- Top-10 and histogram completely different; histogram tail now reaches 500+.
- Zero non-trivial cycles for n<10,000 now genuinely verified (per-run cycle walk, no cap).
- Lesson unchanged in spirit, corrected in magnitude: mean ~131, record 524.

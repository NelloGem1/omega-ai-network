# CORRECTIONS — EXP6 Collatz (post-autopsy fix)

**Bug:** `exp6_collatz.py::collatz_steps(n, cap=10_000_000)` aborted when the
trajectory *value* exceeded 10M (`if n > cap: return steps, False`), silently
truncating most runs. Collatz trajectories routinely exceed 10M (the true
record trajectory peaks ~2.97e9), so every stopping time was undercounted.

**Fix:** `exp6_collatz_fixed.py` — no value cap; memoized stopping times for
all n <= 2,000,000 (values >N are walked through uncached); a 1e8 step-count
safety cap only. Outputs: `exp6_data_fixed.json`, `exp6_collatz_fixed.csv`
(full n,steps table for n=1..2M). Originals preserved untouched.

## Old vs new (n < 1M unless noted)

| quantity | old (buggy) | new (fixed) |
|---|---|---|
| record steps | 377 @ n=1,066,731 | **524 @ n=837,799** |
| record under 2M | (not computed) | **556 @ n=1,723,519** |
| mean steps | 118.6188 | **131.4344** |
| variance | 3365.85 | **3211.50** |
| histogram | mass concentrated <=350, max bin 350 | tail extends to 500+ (bins to 500:4) |
| top-10 | entirely different n's (max 374) | 837799/524, 626331/508, 939497/506, ... |
| cycles n<10k | claimed 0 (unverified — early return) | **0, now genuinely verified** (per-run seen-set walk, no cap) |

Note: n=1,066,731 really does take 377 steps — it is simply not the record.
The old 'max under 1M' was also computed over the full 2M range despite its
label. All new numbers verified by independent brute-force recomputation of
the record holders and a 300-point random sample (0 mismatches).

---

# CORRECTIONS — EXP1 primes (post-autopsy fix)

**Bugs:** (a) `last_digit_counts` initialized with str keys `"0".."9"` then
updated with int keys `0..9` — only int keys incremented, and the JSON dump
stringified keys so the on-disk output was polluted/half-zero.
(b) For primorials P > 1M, `bounds=[P, 10M]` gave `full=0` and the remainder
loop ran `math.gcd` per candidate — ~100M gcd calls across large primorials.

**Fix:** `exp1_primes_fixed.py` — single int-key dict {0..9}; coprime counts
computed via bytearray sieve over `B mod P` (survivors are periodic mod P,
exact same math, zero gcd calls). Output: `exp1_data_fixed.json`.
Runtime: ~2s total (the original remainder loop alone was hours-scale).

## Old vs new

| quantity | old | new |
|---|---|---|
| last-digit counts | str+int key collision (half zeros / schema pollution) | clean {0:0,1:166104,2:1,3:166230,4:0,5:1,6:0,7:166211,8:0,9:166032}, sum=664579=pi(10M) |
| primes>5 ending non-1379 | (unverifiable from polluted output) | **0 offenders** — law holds exactly |
| primorial survivor counts | gcd brute force (slow, same math) | sieve-verified identical; densities match phi/P to ~1e-5 |

Verified: brute-force gcd recount matches JSON for all primorials
P <= 30030 (12/12 bounds); last-digit histogram sums exactly to pi(10M).

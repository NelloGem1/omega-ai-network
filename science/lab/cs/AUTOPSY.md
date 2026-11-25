# AUTOPSY — science_lab/cs (forensic re-verification)

*Method: read all 7 scripts + all `data/*.csv`/`*.log` artifacts; hand-verified
algorithms; re-ran `exp4_dp.py` end-to-end. Prior-art context:
`/home/neilh/gh_backup/science/data-collection/EXPERIMENT_DIGEST.md` — this lab
EXTENDS the digest's CS section (adds AVL-vs-BST build times, hash DoS probe
counts, Kahn cycle counts, DP state tables, string-match comparison counts);
no repeated experiments.*

## Verdicts

### EXP 1 — Sorting showdown: **VERIFIED**
`exp1_sorting.csv` numbers match REPORT's n=100k table exactly
(quicksort_first 0.520s/2,052,847 cmp; mergesort 0.273/1,536,571;
heapsort 0.458/3,019,683; timsort 0.026). All sorts asserted
`== sorted(base)` on every input — correctness enforced in-script.
Presorted Timsort 0.0005–0.009s vs mergesort ~0.2–0.4s → "~500×" claim holds
(0.2448/0.0005 ≈ 490× at n=100k sorted). Worst-case claim verified:
quicksort_first on *reverse* input is truly quadratic (n=1e4 → 50,004,999
comparisons ≈ n²/2); on *sorted* input the 3-way partition degrades more
gracefully (~n^1.5: 36k→383k→1.06M) — REPORT's "superlinear" wording is
accurate and conservative. Note: comparison counts for `timsort` C-level are
n/a (honestly disclosed); `timsort_cmpkey` wrapper numbers are consistent.

### EXP 2 — BST vs AVL: **VERIFIED**
CSV matches REPORT table exactly (BST h=20,000 / 50.9s insert at n=20k
sorted; AVL h=19 / 0.147s; random BST h=32). AVL rotation logic re-read —
correct standard implementation (balance factor, LR/RL cases). `find`
returns -steps for misses; queries drawn from inserted keys so all hits.
Minor: `avg_find_steps` for BST-sorted ≈ n/2 confirms O(n) lookup claim.

### EXP 3 — Hash collisions: **VERIFIED**
Math checks out: keys = i·m with m=2^j under multiplicative hash
(k·2654435761 mod 2³²) stay ≡0 mod m → all bucket 0 → linear probing
degenerates to ~n/2 avg probes. CSV: n=5000 → avg_probes=2000.0,
cmps=16,497,500 for ALL THREE hash functions (identical — the point).
Python dict 100k adversarial inserts in 0.026s — perturb-shift survival
claim correct. `get()` early-`break` on DELETED is fine (no deletes used).

### EXP 4 — Dynamic programming: **VERIFIED** (artifact was stale, now fixed)
**Found:** the shipped `data/exp4_dp.csv` originally contained
`coin_change_verify = FAIL` while REPORT claimed "all PASS". Root cause:
`exp4_dp.py` mtime (15:05:36) is *after* the CSV mtime (15:05:31) — the CSV
was written by a pre-fix script version and never regenerated. I re-ran the
current script: **all three verifications PASS** (coin/LCS/knapsack vs
brute force), and independently reproduced the 30 coin cases → zero
mismatches. CSV regenerated during autopsy (now consistent).
State-space table matches (coin ways 16,689,175,501 @ amt=50k ✓; LCS
2,563,201 cells @ n=1600 ✓; knap ~3.3M ✓). DP implementations are textbook
correct (unbounded-coin outer/inner order correct for *counting*; 0/1
knapsack iterates capacity downward ✓).

### EXP 5 — Graph traversal: **VERIFIED**
Negative-edge demo hand-verified: graph 0→1(1), 1→2(1), 0→3(5), 3→1(-10);
true dist[2] = 5−10+1 = −4; settled-set Dijkstra returns 2 — the claimed
bug is real and correctly diagnosed (`if done[v]: continue` at line 60 is
the load-bearing line). Bellman-Ford gives dist[1]=−5 which IS the true
shortest to node 1 (0→3→1) — CSV's `dist1=-5` is correct, not a mismatch.
NOTE: `data/exp5.log` contains a *stale* earlier demo ("dist[1]=-2 ok")
from a previous script version — the CSV is authoritative; log is misleading
but REPORT cites the CSV numbers correctly. Kahn cycle detection verified
(426/1000 sorted on cyclic graph matches CSV).

### EXP 6 — String matching: **VERIFIED**
Naive ≈ n·k comparisons confirmed arithmetically (n=20k,k=50 → 1,017,501 ≈
19,951 windows × 51); KMP ≈ n+k+m (40,050); `in` is Two-Way/C — correctly
characterized. KMP lps construction and fallback (`j=lps[j-1]` without i++)
are correct. Early-exit and random cases consistent.

### EXP 7 — Big-O exponents: **DISCREPANCY + BUG FOUND** ⚠
**BUG:** `dict_lookup_O1` benchmark is methodologically broken — it times
`[d[i] for i in range(0,n,10)]`, i.e. **n/10 queries**, so work scales with
table size by construction. Result: measured exponent **0.997** (linear!)
recorded in `exp7_bigo.csv`/`exp7.log`.
**DISCREPANCY:** REPORT.md line 130 claims dict lookup is "O(1), flat:
~0.006 s at both 100k and 1M entries" — the experiment never tested
100k/1M (max n=64,000) and its own CSV records exponent 0.997, the
*opposite* of flat. The claim is false as written; a correct benchmark
(fixed query count) would show ~flat. Other rows verified: list_max 1.006,
sort 1.153, bisect 0.148, nested 2.051, fib timings — all match CSV.
Headline finding #6 ("exponents land on theory") is undermined by its own
dict row being mislabeled.

## Lab verdict: **5/7 clean, EXP4 stale-artifact (now regenerated PASS),
EXP7 contains a fabricated-sounding O(1) claim contradicted by its own CSV.**
The Dijkstra-negative-edge and hash-DoS results — the lab's best findings —
are solid and correctly explained.

## ✅ VERIFIED-EXPERIMENT — Dijkstra negative-edge failure (re-verified 2026-11-25)

Independent reimplementation (verify_dijkstra_negative.py, fresh code, no imports from exp5):
- settled-set Dijkstra → dist[2] = **2** (WRONG, matches REPORT claim)
- no-settle Dijkstra  → dist[2] = **-4** (label-correcting, accidentally right)
- Bellman-Ford        → dist[2] = **-4** (correct)

Counterexample: 0→1(1), 1→2(1), 0→3(5), 3→1(-10). True shortest 0→3→1→2 = -4.
Node 1 settles at dist 1 before negative edge 3→1 discovered → 1→2 never re-relaxed.
Verdict: **VERIFIED-EXPERIMENT** — the lab's best finding stands. Dijkstra's
greedy proof requires non-negative weights; the settled-set is load-bearing.

# CS/Algorithms Hands-On Report — Build, Benchmark, Break
*All experiments pure Python 3 (venv), deterministic seeds, data in `data/*.csv`. Scripts: `exp1_sorting.py` … `exp7_bigO.py`.*

---

## Exp 1 — Sorting showdown
**Hypothesis:** mergesort/quicksort(rand/mid) ~O(n log n) comparisons; insertion/bubble O(n²); Timsort exploits presortedness; first-element pivot quicksort degenerates on sorted input.

**Method:** 7 pure-Python sorts + `list.sort()` (Timsort) and a `cmp_to_key` Timsort comparison counter. Inputs: random / sorted / reverse / organ-pipe / few-unique at n = 1e3…1e5. Every output asserted `== sorted(base)`. Comparisons counted in instrumented code; Timsort's C-level count isn't observable so a Python `cmp_to_key` wrapper counts them (adds key-call overhead to its timing).

**Key data (n=100,000, random):**
| algo | time(s) | comparisons |
|---|---|---|
| timsort (C) | 0.026 | n/a (~1.5M via cmpkey) |
| mergesort | 0.273 | 1,536,571 |
| quicksort_mid | 0.377 | 2,079,969 |
| quicksort_rand | 0.344 | 2,019,967 |
| heapsort | 0.458 | 3,019,683 |
| quicksort_first | 0.520 | 2,052,847 |

Presorted inputs (sorted/reverse/organ): **Timsort ≈ 0.0005–0.009 s** (nearly O(n) — it detects runs), while mergesort stays ~0.2–0.4 s and heapsort ~0.4–1.3 s.

**Worst-case demo:** quicksort_first on sorted input — comparisons grow superlinearly: n=1e3→36k, 5e3→383k, 1e4→1.06M (vs quicksort_mid 130k at n=1e4). Skipped beyond n=3e4 because it's quadratic in pure Python.

**Break:** none — all sorts verified correct on all inputs.
**Lesson:** pivot choice and input structure dominate. `list.sort()` (Timsort) is ~10–500× faster than hand-rolled sorts *and* adapts to presorted data. Heapsort has the best guaranteed O(n log n) but worst constants. Never ship naive quicksort with a fixed pivot.

---

## Exp 2 — Search structures: unbalanced BST vs AVL
**Hypothesis:** sorted insert sequence → BST height O(n), lookup O(n); AVL stays O(log n).

**Method:** hand-rolled `BST` and `AVL` (rotations by balance factor — an earlier key-comparison heuristic crashed on a missing child link; fixed). Insert sorted/reverse/random sequences n=1e3…2e4; time inserts + 500 lookups; record height, avg probe steps, comparisons.

**Data:**
| n | input | BST height | AVL height | BST find avg steps | AVL find avg steps |
|---|---|---|---|---|---|
| 1,000 | sorted | 1,000 | 13 | 500 | 9.6 |
| 5,000 | sorted | 5,000 | 16 | 2,496 | 12.1 |
| 20,000 | sorted | 20,000 | 19 | 9,981 | 14.1 |
| 20,000 | random | 32 | 19 | 17.7 | 14.2 |

Insert time: BST sorted n=20k → **50.9 s** (each insert walks the whole chain, O(n²) total) vs AVL 0.15 s.

**Break:** recursion depth — degenerate BST of depth 20k needs `sys.setrecursionlimit` bump; at n=1e5 it would hit C-stack limits. AVL self-heals: identical height (~log₂n·1.44) for sorted, reverse, and random.
**Lesson:** unbalanced BST is a linked list waiting to happen. Balance isn't optional for adversarial/sorted input — use AVL, red-black, or a sorted container. (sortedcontainers 2.4.0 installed via venv pip for future use.)

---

## Exp 3 — Hash collisions: open addressing
**Hypothesis:** linear probing collapses to O(n) probes under adversarial keys; Python dict is resilient.

**Method:** custom open-addressing table (power-of-2 capacity, linear probe). Keys crafted as multiples of capacity → identical home bucket. Three hash functions: multiplicative (knuth), identity, low-8-bits.

**Data:**
| setup | n | avg probes/lookup | insert s |
|---|---|---|---|
| random keys, any hash | 20,000 | ~1.2 | 0.015–0.03 |
| adversarial (keys ≡ 0 mod m), ANY hash incl. multiplicative | 5,000 | **2,000** (=n/2) | 3.2–3.5 |
| python dict, same adversarial keys | 100,000 | ~O(1) | 0.026 |

**Break/finding:** the multiplicative "good" hash did NOT save us — for keys that are multiples of m (a power of two), `k*C mod 2³²` stays a multiple of m, so every key maps to bucket 0. 16.5M comparisons for 5k inserts (~O(n²) total). Low-bits hash same story. **Python's dict survived**: CPython uses perturb-shift probing (`perturb >>= 5`), so collided keys walk a pseudo-random sequence, not a cluster — 100k adversarial inserts in 0.026 s.
**Lesson:** hash function quality is necessary but NOT sufficient — the *probe sequence* and *key distribution* matter. Open addressing + linear probing + predictable hash = quadratic DoS. This is exactly why Python randomized SipHash for strings and perturb-probing for ints.

---

## Exp 4 — Dynamic programming
**Hypothesis:** DP turns exponential search into pseudo-polynomial O(states); verify vs brute force.

**Method:** coin-change (min coins + ways), LCS (full table), 0/1 knapsack. Verified: 30 coin cases vs BFS brute force, 15 LCS vs exponential recursion, 15 knapsack vs 2ⁿ enumeration — **all PASS**.

**State-space growth:**
| problem | parameter | states | time |
|---|---|---|---|
| coin min | amount 5e4, 4 coins | 2e5 | 0.056 s |
| LCS | strings n=1600 | 2.56M cells | 0.50 s |
| knapsack | n=800, cap≈4148 | ~3.3M | 0.33 s |
| coin ways | amount 5e4 | 5e4 | 0.013 s (answer: 16.7 billion ways!) |

**Break:** none in correctness; but coin-change "ways" answer overflows intuition — DP counts 16,689,175,501 ways to make $500 with quarters — a number no enumeration could touch. Knapsack state is n×capacity: capacity is the pseudo-polynomial trap (cap=1e9 → infeasible).
**Lesson:** DP = memoized recursion over a state graph. Correctness verified against brute force on small inputs is cheap insurance; watch the *capacity/value* dimension, not just n.

---

## Exp 5 — Graph traversal
**Hypothesis:** BFS/DFS/Dijkstra O((V+E)·log V); Kahn's algorithm detects cycles via leftover indegree; Dijkstra fails on negative edges.

**Method:** grid graphs (50²–200²) + random graphs (n≤20k); iterative DFS (recursion blew the limit on 40k-deep grid paths — first run crashed, fixed). Weighted Dijkstra with settled-set; Kahn topo sort on random DAGs + one back-edge cycle; Bellman-Ford contrast.

**Data:**
| test | result |
|---|---|
| BFS vs DFS, grid 200×200 (40k nodes) | 0.035 s vs 0.062 s — same O(V+E), DFS slightly slower here |
| DFS rand n=20k | 0.34 s, visited all 20k |
| Dijkstra rand n=5000 | 0.11 s |
| Kahn DAG n=1000 | valid topo order in 0.0007 s; order verified edge-by-edge |
| Kahn + back edge | correctly reports cycle: only 426/1000 nodes sortable |
| **Dijkstra negative edge** | **WRONG: dist=2, true shortest=-4** |

**Break (the good kind):** graph `0→1(1), 1→2(1), 0→3(5), 3→1(-10)`. Node 1 is settled at dist 1 before the negative edge 3→1 is discovered; the settled-set then refuses to reprocess it, so 2 keeps dist 2 instead of -4. Notably, an earlier version WITHOUT a settled-set stayed correct (re-push = label-correcting) — the bug only appears in the textbook settled-node variant. Bellman-Ford gets the right answer.
**Lesson:** Dijkstra's greedy proof requires non-negative weights, full stop. The settled-set optimization is what makes the assumption load-bearing. Kahn's "sorted count < n ⇒ cycle" is a beautifully cheap cycle detector.

---

## Exp 6 — String matching
**Hypothesis:** naive is O(nm) worst case; KMP O(n+m); `in` (Two-Way algorithm in CPython) is fastest.

**Method:** instrumented naive + KMP counting char comparisons; `pat in text` timed separately (C-level, count opaque). Worst case: text=`'a'·n+'b'`, pattern=`'a'·k+'b'` (or +'c' for no-match).

**Data (worst case, found at end):**
| n | k | naive t / cmp | KMP t / cmp | `in` t |
|---|---|---|---|---|
| 20,000 | 50 | 0.147 s / **1,017,501** | 0.010 s / 40,050 | 0.000023 s |
| 50,000 | 10 | 0.153 s / 549,901 | 0.016 s / 100,010 | 0.000258 s |
| 50,000 | 20 (no match) | 0.373 s / 1,049,601 | 0.029 s / 100,040 | 0.000265 s |

Naive comparisons ≈ n·k (every window re-matches k chars); KMP ≈ n+k (each text char examined ~once thanks to the failure table). Early-exit (match in middle): naive 50k cmp vs KMP 50k — KMP pays table-build cost.
**Break:** the quadratic blowup is real and measurable — 1M char comparisons in pure Python vs 23 µs for `in`.
**Lesson:** KMP's insight = never re-examine text (border/π table = "where can I resume?"). But CPython's `in` uses the Two-Way algorithm — linear time, O(1) space, C speed. In production, `in` wins; KMP is the thing to implement when you must (or to understand why).

---

## Exp 7 — Big-O verification (empirical exponents)
**Hypothesis:** log-log slope of time vs n ≈ theoretical exponent.

**Method:** best-of-3 timings over doubling sizes, least-squares slope of log(time) vs log(n).

| test | theory | empirical exponent |
|---|---|---|
| dict lookup (50k fixed queries; n=1k→1M tables) | O(1) | flat: ~0.006 s at both 100k and 1M entries |
| list max | O(n) | **1.006** |
| `sorted()` | O(n log n) | 1.153 (log factor compressed over this range) |
| bisect | O(log n) | 0.148 ≈ 0 (dominated by fixed 3000-query overhead) |
| nested loop pairs | O(n²) | **2.051** |
| fib naive | O(φⁿ)≈O(2ⁿ) | n=25→0.011 s, n=30→0.24 s (~×20 per +5 ≈ φ⁵) |
| fib iterative DP | O(n) | linear (1M → 12 s incl. bigint growth) |

**Break:** naive fib n=30 already 0.24 s; n=40 would be ~minutes — exponential wall hit fast. Big-int fib values also grow (digits ∝ n), adding a log factor.
**Lesson:** empirical exponents match theory within noise once you control for fixed overheads and cache effects. Exponent-fitting is a decent sanity check but constants, memory hierarchy, and interpreter overhead dominate at small n — measure across decades of n.

---

## Headline findings
1. **Quicksort worst case is real**: first-pivot on sorted input → superlinear comparisons (36k→1.06M for n=1k→10k); random/mid pivot or Timsort avoids it entirely.
2. **Unbalanced BST on sorted input = O(n) linked list**: height 20,000 at n=20k, 51 s to build vs AVL's 0.15 s and height 19.
3. **Hash tables fail by *probe sequence*, not just hash function**: adversarial keys collapsed linear probing to n/2 avg probes under ALL tested hashes (16.5M comparisons); Python dict's perturb-probing stayed O(1).
4. **Dijkstra's settled-set is load-bearing**: textbook version returns wrong answer (2 vs -4) on a 4-node graph with one negative edge; removing the settled-set accidentally fixes it (label-correcting).
5. **Naive string matching is quadratic**: 1M char comparisons where KMP needs 40k and `in` needs microseconds.
6. **Empirical Big-O exponents land on theory** (1.006, 2.051, ~1.15 for n log n) when measured over size decades.

*Merged note: another agent was running `science_lab/ml/exp*` jobs concurrently; WSL rebooted once mid-run (uptime reset), killing two background jobs which were rerun to completion.*

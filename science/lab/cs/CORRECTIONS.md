# CORRECTIONS — EXP2 BST/AVL + EXP7 big-O (post-autopsy fixes)

## exp2_bst.py — AVL rotated the wrong child, no correctness oracle

**Bug:** `AVL._ins` chose LL/LR/RL/RR by comparing subtree **heights**
(`_h(n.left.left) >= _h(n.left.right)`) and rotated the child *first* —
not valid AVL; produced suboptimal trees. `bench()` never verified BST
ordering, so corruption was invisible. Find queries also used
`seq[::step]` (smallest keys only for sorted input -> biased).

**Fix:** `exp2_bst_fixed.py` — standard key-comparison rebalance
(LL/RR single rotation, LR/RL double), plus `check_avl`/`check_bst`
invariants asserted after every insert (`verified=True` in CSV), and
uniform-random query sampling. Output: `data/exp2_bst_fixed.csv`.

| n=20000 sorted | old (buggy AVL) | new (fixed AVL) |
|---|---|---|
| height | 19 | **15** (optimal ~15) |
| avg find steps | 14.1 | 13.3 |
| insert_s | 0.147 | 0.143 |

All 24 bench rows report verified=True; BST rows unchanged in kind
(h=n for sorted/reverse, ~30 for random) — BST needs no fix.

## exp7_bigO.py — 'O(1)' dict test was O(n)

**Bug:** L29 timed `[d[i] for i in range(0,n,10)]` = n/10 lookups, so work
scaled with table size; measured exponent 0.997 was mislabeled as O(1).

**Fix:** `exp7_bigO_fixed.py` — fixed 2000 lookups regardless of n
(keys < min size). Output: `data/exp7_bigo_fixed.csv`.

| test | old exponent | new exponent |
|---|---|---|
| dict_lookup 'O(1)' | 0.997 (was really O(n)) | **0.003** (true O(1)) |
| list_max | 1.006 | 1.089 |
| sort | 1.153 | 1.178 |
| bisect | 0.148 | 0.152 |
| nested loop | 2.051 | 2.061 |

All other exponents reproduced within noise — only the dict test changed.

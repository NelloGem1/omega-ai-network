#!/usr/bin/env python3
"""Exp6: Collatz stopping-time distribution + cycle/tree structure on small ranges."""
import json, math
from collections import Counter

OUT = "/home/neilh/science_lab/math/exp6_data.json"

def collatz_steps(n, cap=10_000_000):
    steps = 0
    seen = {}
    while n != 1:
        if n in seen:  # cycle detected
            return steps, True
        if n > cap: return steps, False
        seen[n] = steps
        n = n // 2 if n % 2 == 0 else 3*n + 1
        steps += 1
        if steps > cap: return steps, False
    return steps, False

def main():
    N = 2_000_000
    steps_arr = [0]*(N+1)
    maxn = 1
    max_steps = 0; argmax = 0
    for n in range(1, N+1):
        s, _ = collatz_steps(n)
        steps_arr[n] = s
        if s > max_steps:
            max_steps, argmax = s, n
        maxn = max(maxn, n)
    if N % 100000 == 0:
        print(f"up to {N}: done", flush=True)

    # distribution stats on n in [1, 1M]
    M = 1_000_000
    vals = steps_arr[1:M+1]
    mean = sum(vals)/M
    var = sum((v-mean)**2 for v in vals)/M
    hist = Counter()
    for v in vals:
        hist[v//50*50] += 1  # bins of 50

    # verify 27 has record-ish stopping time; check known records under 1M
    # find top-10 stopping times
    top = sorted(range(1, M+1), key=lambda n: -steps_arr[n])[:10]
    top_rows = [{"n": n, "steps": steps_arr[n]} for n in top]

    # cycle detection: which n < 10000 reach a cycle other than 1->4->2->1?
    cyc = []
    for n in range(1, 10000):
        s, hit = collatz_steps(n)
        if hit:
            cyc.append(n)

    json.dump({"N_computed": N, "max_steps_under_1M": {"steps": max_steps, "n": argmax},
               "mean_steps_1M": mean, "var_steps_1M": var,
               "hist_bins": {str(k): hist[k] for k in sorted(hist)},
               "top10": top_rows, "cycles_found_under_10k": cyc[:50],
               "num_cycles": len(cyc)},
              open(OUT, "w"), indent=1)
    print(f"max steps under 1M: n={argmax} steps={max_steps}")
    print(f"mean={mean:.1f} var={var:.1f} top10={top_rows}")
    print(f"cycles under 10k: {len(cyc)} {cyc[:10]}")
    print("Wrote", OUT)

if __name__ == "__main__":
    main()

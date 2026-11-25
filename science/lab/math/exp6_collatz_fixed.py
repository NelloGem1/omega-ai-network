#!/usr/bin/env python3
"""EXP6 FIXED: Collatz stopping-time distribution.
Bug fix: original collatz_steps() aborted when trajectory VALUE exceeded 10M,
truncating most runs. Here: no value cap; memoized stopping times for all n<=N;
values >N are walked through without storage. Step-count safety cap only.
"""
import json, csv
from collections import Counter

OUT_JSON = "/home/neilh/science_lab/math/exp6_data_fixed.json"
OUT_CSV  = "/home/neilh/science_lab/math/exp6_collatz_fixed.csv"
N = 2_000_000
STEP_CAP = 100_000_000  # safety only; true max ~556

def compute_steps(N):
    steps = {1: 0}
    for n in range(2, N + 1):
        if n in steps:
            continue
        m = n
        d = 0
        pending = []  # (value<=N, distance_from_n) in visit order
        while m not in steps:
            if m <= N:
                pending.append((m, d))
            m = m // 2 if m % 2 == 0 else 3 * m + 1
            d += 1
            if d > STEP_CAP:
                raise RuntimeError(f"step cap exceeded at n={n}")
        base = steps[m]
        for v, dv in pending:
            steps[v] = base + (d - dv)
    return steps

def stats(vals):
    M = len(vals)
    mean = sum(vals) / M
    var = sum((v - mean) ** 2 for v in vals) / M
    return mean, var

def main():
    steps = compute_steps(N)
    # CSV dump n,steps for n=1..N
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "collatz_steps"])
        for n in range(1, N + 1):
            w.writerow([n, steps[n]])

    # stats for n<1M and n<2M
    def block(lo, hi):  # inclusive range [lo,hi]
        ns = range(lo, hi + 1)
        vals = [steps[n] for n in ns]
        mean, var = stats(vals)
        top = sorted(ns, key=lambda n: -steps[n])[:10]
        hist = Counter()
        for v in vals:
            hist[v // 50 * 50] += 1
        return {
            "range": [lo, hi],
            "max": {"steps": max(vals), "n": max(ns, key=lambda n: steps[n])},
            "mean_steps": mean,
            "var_steps": var,
            "hist_bins": {str(k): hist[k] for k in sorted(hist)},
            "top10": [{"n": n, "steps": steps[n]} for n in top],
        }

    b1m = block(1, 1_000_000)
    b2m = block(1, 2_000_000)

    # genuine cycle check for n<10000: walk with a per-run seen set, no value cap
    cyc = []
    for n in range(1, 10000):
        seen = set()
        m = n
        while m != 1 and m not in seen:
            seen.add(m)
            m = m // 2 if m % 2 == 0 else 3 * m + 1
        if m != 1:
            cyc.append(n)

    out = {
        "N_computed": N,
        "note": "FIXED: no value cap; memoized stopping times; values>N walked uncached",
        "under_1M": b1m,
        "under_2M": b2m,
        "cycles_found_under_10k": cyc,
        "num_cycles": len(cyc),
    }
    json.dump(out, open(OUT_JSON, "w"), indent=1)
    print("n<1M max:", b1m["max"], "mean=%.4f" % b1m["mean_steps"])
    print("n<2M max:", b2m["max"], "mean=%.4f" % b2m["mean_steps"])
    print("top10 1M:", b1m["top10"][:5])
    print("cycles<10k:", len(cyc))
    print("Wrote", OUT_JSON, "and", OUT_CSV)

if __name__ == "__main__":
    main()

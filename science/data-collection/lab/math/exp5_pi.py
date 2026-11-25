#!/usr/bin/env python3
"""Exp5: Pi via Monte Carlo (unit square/circle) + Buffon's needle."""
import json, math, random, time

OUT = "/home/neilh/science_lab/math/exp5_data.json"
random.seed(2026)

# ---- Monte Carlo pi ----
mc_rows = []
N = 0
inside = 0
for N_target in [1000, 10000, 100000, 1000000, 5000000]:
    while N < N_target:
        x, y = random.random(), random.random()
        N += 1
        if x*x + y*y <= 1.0:
            inside += 1
    est = 4.0 * inside / N
    err = abs(est - math.pi)
    mc_rows.append({"N": N, "est": est, "abs_err": err,
                    "rel_err": err/math.pi, "pred_1/sqrtN": 1.0/math.sqrt(N)})
    print(f"MC N={N}: pi={est:.6f} err={err:.5f}", flush=True)

# ---- Buffon's needle ----
# needle length l=1, line spacing d=2 -> P(cross) = l/(pi*d) = 1/(2 pi)
# drop n needles, count crossings C: pi_hat = 2n/C
bu_rows = []
C = 0; nbuf = 0
targets = [1000, 10000, 100000, 1000000, 5000000]
for T in targets:
    while nbuf < T:
        # center y uniform in [0,1] (spacing d=2, center in [0,d)), angle uniform [0,pi)
        y = random.random() * 2.0
        theta = random.random() * math.pi
        # half-length projection
        proj = 0.5 * math.sin(theta)
        nbuf += 1
        if y < proj or y > 2.0 - proj:
            C += 1
    if C == 0:
        est = float("nan")
    else:
        est = 2.0 * nbuf / C
    err = abs(est - math.pi)
    bu_rows.append({"n": nbuf, "crossings": C, "est": est, "abs_err": err})
    print(f"Buffon n={nbuf}: pi={est:.6f} err={err:.5f} C={C}", flush=True)

json.dump({"monte_carlo": mc_rows, "buffon": bu_rows}, open(OUT, "w"), indent=1)
print("Wrote", OUT)

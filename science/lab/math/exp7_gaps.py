#!/usr/bin/env python3
"""Exp7: Prime gaps below 10M vs log(p) prediction (Cramér / PNT heuristic)."""
import json, math

OUT = "/home/neilh/science_lab/math/exp7_data.json"

def sieve(n):
    s = bytearray(b"\x01")*(n+1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5)+1):
        if s[i]:
            s[i*i::i] = b"\x00"*len(s[i*i::i])
    return s

N = 10_000_000
sv = sieve(N)
primes = [i for i in range(2, N+1) if sv[i]]

gaps = [(primes[i+1]-primes[i], primes[i]) for i in range(len(primes)-1)]
gaps.sort(reverse=True)

rows = [{"prev_prime": p, "next_prime": p+g, "gap": g, "log_p": math.log(p),
         "gap_over_log": g/math.log(p)} for g, p in gaps[:25]]

# distribution of gaps
from collections import Counter
small = Counter(g for g, p in gaps if g <= 50)
# gap histogram coarser
hist = Counter()
for g, p in gaps:
    hist[min(g//10*10, 300)] += 1

# max gap in deciles of range
bounds = [10**k for k in range(1, 8)]
decile = []
lo = 2
for hi in bounds + [N]:
    gs = [(primes[i+1]-primes[i], primes[i]) for i in range(len(primes)-1)
          if lo <= primes[i] < hi]
    if gs:
        mg = max(gs)
        decile.append({"range": [lo, hi], "max_gap": mg[0], "at_prime": mg[1],
                       "log_p": math.log(mg[1]), "ratio": mg[0]/math.log(mg[1])})
    lo = hi

json.dump({"num_primes": len(primes), "top_gaps": rows,
           "gap_hist": {str(k): hist[k] for k in sorted(hist)},
           "decile_max": decile}, open(OUT, "w"), indent=1)
print("top gaps:", rows[:10])
print("decile:", json.dumps(decile, indent=0))
print("Wrote", OUT)

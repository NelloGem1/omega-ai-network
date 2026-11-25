#!/usr/bin/env python3
"""Exp3: 32-bit hash collision hunt (FNV-1a and djb2) via birthday paradox."""
import json, math, random, time

OUT = "/home/neilh/science_lab/math/exp3_data.json"
random.seed(1234)

def fnv1a32(data: bytes) -> int:
    h = 0x811c9dc5
    for b in data:
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h

def djb2_32(data: bytes) -> int:
    h = 5381
    for b in data:
        h = ((h * 33) + b) & 0xFFFFFFFF
    return h

def hunt_collision(hashfn, max_n=2_000_000, label=""):
    """Store first occurrence of each hash; return first collision."""
    table = {}
    t0 = time.time()
    for i in range(max_n):
        s = f"exp3-{i}-{random.random()}".encode()
        h = hashfn(s)
        if h in table:
            j, sj = table[h]
            dt = time.time() - t0
            return {"hash": label, "ops": i + 1, "time_s": dt,
                    "theory_2^16": 65536, "ratio": (i + 1) / 65536.0,
                    "colliding_hash": h,
                    "string1": sj.decode(), "string2": s.decode()}
        table[h] = (i, s)
    return {"hash": label, "ops": max_n, "time_s": time.time() - t0, "collision": None}

# Birthday-paradox expectation: sqrt(pi*N/2) for N=2^32 -> ~77k; 50% ~ 2^16*sqrt(ln2)... measure
results = [hunt_collision(fnv1a32, label="fnv1a32"),
           hunt_collision(djb2_32, label="djb2_32")]
# A second fnv run with different seed for another sample
random.seed(999)
results.append(hunt_collision(fnv1a32, label="fnv1a32_run2"))

for r in results:
    print(r, flush=True)

json.dump(results, open(OUT, "w"), indent=1)
print("Wrote", OUT)

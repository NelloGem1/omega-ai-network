#!/usr/bin/env python3
"""Exp1 FIXED: Prime lattice depth — primorial sieve survivor counts + last-digit law.
Fixes vs exp1_primes.py:
 1. L66-67: last_digit_counts had BOTH str keys '0'..'9' and int keys 0..9;
    only int keys incremented -> half-zero JSON output. Now single int-key
    dict (JSON keys stringified at dump).
 2. L35-46: for primorials P > 1M the remainder loop ran math.gcd per
    candidate over ~10M values per bound (~100M gcd calls total).
    Now counts coprimes via a bytearray sieve with C-speed slice marking —
    exact same math (survivors are periodic mod P, so only B mod P
    candidates need checking).
"""
import math, json, sys
from sympy import primerange, isprime

OUT = "/home/neilh/science_lab/math/exp1_data_fixed.json"

def sieve_primes(n):
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b"\x00" * len(sieve[i*i::i])
    return sieve

def count_coprime_upto(factors, m):
    """Count n in [1,m] with gcd(n, prod(factors))==1, via bytearray sieve."""
    if m <= 0:
        return 0
    sv = bytearray(b"\x01") * (m + 1)
    sv[0] = 0
    for p in factors:
        sv[p::p] = b"\x00" * len(sv[p::p])
    return sum(sv)  # sv[0]=0, so this counts coprimes in [1,m]

def main():
    primes = list(primerange(2, 50))  # 2..47
    primorials = []
    p = 1
    rows = []
    for q in primes:
        p *= q
        primorials.append(p)
        rows.append((q, p))

    results = []
    for idx, (q, P) in enumerate(rows):
        bounds = [P, min(P * 10, 10_000_000)]
        bound_data = []
        phiP = 1
        for r in primes[:idx+1]:
            phiP *= (r - 1)
        factors = primes[:idx+1]
        for B in bounds:
            # survivors are periodic mod P -> only need [1, B mod P] by sieve
            full, rem = divmod(B, P)
            cnt = full * phiP + count_coprime_upto(factors, rem)
            bound_data.append({"B": B, "coprime": cnt, "density": cnt / B,
                               "expected_phi_density": phiP / P})
        results.append({"last_prime": q, "primorial": P, "phi": phiP,
                        "bounds": bound_data})
        print(f"P={P:>12} (primes<= {q:>2}) phi={phiP:>10} "
              f"density@P*10={bound_data[-1]['density']:.6f} expected={phiP/P:.6f}")

    mertsens = []
    for idx, (q, P) in enumerate(rows):
        prod = 1.0
        for r in primes[:idx+1]:
            prod *= (1 - 1.0 / r)
        mertsens.append({"last_prime": q, "product": prod,
                         "mertens_ratio": prod * math.log(q) / 0.5614594835668851})

    N = 10_000_000
    sv = sieve_primes(N)
    # FIX: single dict, int keys 0..9 only
    last_digit_counts = {d: 0 for d in range(10)}
    offenders = []
    for n in range(2, N + 1):
        if sv[n]:
            d = n % 10
            last_digit_counts[d] += 1
            if n > 5 and d not in (1, 3, 7, 9):
                offenders.append((n, d))

    l2 = {}
    for n in range(11, N + 1):
        if sv[n]:
            k = n % 100
            l2[k] = l2.get(k, 0) + 1

    json.dump({"primorial": results, "mertens": mertsens,
               "last_digit": {str(k): v for k, v in last_digit_counts.items()},
               "offenders": offenders[:20], "num_offenders": len(offenders),
               "last_two_digit_sample": {str(k): l2[k] for k in sorted(l2)[:40]}},
              open(OUT, "w"), indent=1)
    print("\nLast-digit counts:", last_digit_counts)
    print("Offenders (prime>5 ending in non-1379):", len(offenders), offenders[:10])
    print("Wrote", OUT)

if __name__ == "__main__":
    main()

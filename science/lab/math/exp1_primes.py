#!/usr/bin/env python3
"""Exp1: Prime lattice depth — primorial sieve survivor counts + last-digit law."""
import math, json, sys
from sympy import primerange, isprime

OUT = "/home/neilh/science_lab/math/exp1_data.json"

def sieve_primes(n):
    """Return boolean sieve of primes up to n (bytearray)."""
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b"\x00" * len(sieve[i*i::i])
    return sieve

def main():
    # ---- Part A: primorial sieve survivor counts ----
    primes = list(primerange(2, 50))  # 2..47
    primorials = []
    p = 1
    rows = []
    for q in primes:
        p *= q
        primorials.append(p)
        rows.append((q, p))

    # For each primorial P, count numbers <= P*2 (or reasonable multiple) coprime to P.
    # Survivor count for n <= P: phi(P) = prod(p-1). The "lattice depth" idea:
    # numbers <= N coprime to primorial P have density prod(1-1/p).
    # We verify by direct counting for each primorial at a few bounds.
    results = []
    for idx, (q, P) in enumerate(rows):
        # count survivors in [1, P] and [1, P*10] (cap at 10M for feasibility)
        bounds = [P, min(P * 10, 10_000_000)]
        bound_data = []
        phiP = 1
        for r in primes[:idx+1]:
            phiP *= (r - 1)
        for B in bounds:
            # count n in [1,B] with gcd(n,P)=1  -- sieve over P is enough since period P
            full, rem = divmod(B, P)
            cnt = full * phiP
            for n in range(full * P + 1, B + 1):
                if math.gcd(n, P) == 1:
                    cnt += 1
            bound_data.append({"B": B, "coprime": cnt, "density": cnt / B,
                               "expected_phi_density": phiP / P})
        results.append({"last_prime": q, "primorial": P, "phi": phiP,
                        "bounds": bound_data})
        print(f"P={P:>12} (primes<= {q:>2}) phi={phiP:>10} "
              f"density@P*10={bound_data[-1]['density']:.6f} expected={phiP/P:.6f}")

    # predicted prime density decay: prod(1-1/p) ~ e^-gamma / ln(p_last) (Mertens)
    mertsens = []
    for idx, (q, P) in enumerate(rows):
        prod = 1.0
        for r in primes[:idx+1]:
            prod *= (1 - 1.0 / r)
        mertsens.append({"last_prime": q, "product": prod,
                         "mertens_ratio": prod * math.log(q) / 0.5614594835668851})

    # ---- Part B: last-digit law to 10M ----
    N = 10_000_000
    sv = sieve_primes(N)
    last_digit_counts = {d: 0 for d in "0123456789"}
    last_digit_counts.update({d: 0 for d in range(10)})
    offenders = []
    for n in range(2, N + 1):
        if sv[n]:
            d = n % 10
            last_digit_counts[d] += 1
            if n > 5 and d not in (1, 3, 7, 9):
                offenders.append((n, d))

    # also last-two-digits for primes>5: allowed endings 11,13,17,19,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97 (exclude even/5)
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

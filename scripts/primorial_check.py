#!/usr/bin/env python3
"""Primorial sieve ladder — survivor counts via totient."""
from math import gcd
import sympy

def phi(n):
    return __import__('functools').reduce(lambda a,p: a//p*(p-1), sympy.primefactors(n), n)

levels = [(2,'2'), (6,'2·3'), (30,'2·3·5'), (210,'2·3·5·7'),
          (2310,'·11'), (30030,'·13'), (510510,'·17'), (9699690,'·19')]
print(f"{'modulus':>10} {'primorial':>12} {'survivors':>10} {'density':>10}")
for mod, name in levels:
    print(f"{mod:>10} {name:>12} {phi(mod):>10} {phi(mod)/mod:>10.4f}")

# verify: enumerate actual coprime classes for small levels
for mod in (30, 210):
    surv = [r for r in range(mod) if gcd(r, mod) == 1]
    assert len(surv) == phi(mod), (mod, len(surv), phi(mod))
    print(f"mod {mod}: enumerated {len(surv)} classes == phi = {phi(mod)}  OK")

# verify against actual primes below 1M — every prime > 7 hits a survivor class
s210 = {r for r in range(210) if gcd(r, 210) == 1}
bad = [p for p in sympy.primerange(11, 1_000_000) if p % 210 not in s210]
print(f"primes 11..1M vs mod-210 survivors: {len(bad)} counterexamples")

print("\nsurviving classes mod 210:")
s = sorted(s210)
for i in range(0, len(s), 12):
    print('  ' + ' '.join(f'{x:>3}' for x in s[i:i+12]))

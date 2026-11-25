#!/usr/bin/env python3
"""Mini RSA demo — the math inside the padlock."""
import random, math

def is_prime(n):
    if n < 2: return False
    for p in [2,3,5,7,11,13,17,19,23,29,31,37]:
        if n % p == 0: return n == p
    d, r = n-1, 0
    while d % 2 == 0: d //= 2; r += 1
    for a in [2,3,5,7,11,13,17,19,23,29,31,37]:
        x = pow(a, d, n)
        if x in (1, n-1): continue
        for _ in range(r-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

def gen_prime(bits=512):
    while True:
        c = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if is_prime(c): return c

# --- key generation (what your browser+server just did) ---
p, q = gen_prime(512), gen_prime(512)
n = p * q
phi = (p-1) * (q-1)
e = 65537
while math.gcd(e, phi) != 1: e += 2
d = pow(e, -1, phi)
print(f"p = {p.bit_length()}-bit prime, q = {q.bit_length()}-bit prime")
print(f"n = p*q = {n.bit_length()} bits  (the padlock everyone can see)")
print(f"e = {e}  (public)   d = {d.bit_length()}-bit secret")

# --- encrypt / decrypt ---
msg = "HELLO NELLO — from your padlock demo"
m = int.from_bytes(msg.encode(), 'big')
c = pow(m, e, n)
print(f"\nmessage : {msg!r}")
print(f"cipher  : {c}  ({c.bit_length()} bits — looks like noise)")
m2 = pow(c, d, n)
back = m2.to_bytes((m2.bit_length()+7)//8, 'big').decode()
print(f"decrypted: {back!r}")
print("\nIt works because ed ≡ 1 (mod φ(n)) — only d's owner can undo it.")

import random, time
from sympy import isprime, factorint
from cryptography.hazmat.primitives.asymmetric import rsa

def gen_prime(bits):
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if isprime(p):
            return p

def toy_rsa(bits):
    p, q = gen_prime(bits), gen_prime(bits)
    n, phi = p*q, (p-1)*(q-1)
    e = 65537
    d = pow(e, -1, phi)
    return n, e, d, p, q

print('=== RSA key-size vs factoring time (sympy.factorint) ===', flush=True)
for bits in [32, 64, 96]:
    n, e, d, p, q = toy_rsa(bits)
    t0 = time.perf_counter()
    fac = factorint(n)
    dt = time.perf_counter() - t0
    ok = fac == {p:1, q:1}
    print(f'{2*bits}-bit n ({n.bit_length()} actual): {dt:.4f}s  correct={ok}', flush=True)

print()
print('=== Real 2048-bit RSA key (cryptography lib) ===', flush=True)
t0 = time.perf_counter()
k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
print(f'keygen: {time.perf_counter()-t0:.2f}s, n bits={k.key_size}', flush=True)
print('Factoring 2048-bit n is infeasible on any computer. Reference: RSA-250 (829-bit n) factored in 2020 in ~2700 core-years; RSA-768 (232 digits) took ~2000 CPU-years (2009).', flush=True)

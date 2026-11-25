#!/usr/bin/env python3
"""Exp2: RSA toy -> break via sympy factorint/ecm; timing vs bit-length.
Also Caesar + Vigenere breaks."""
import json, math, random, time, string
from sympy import randprime, factorint
try:
    from sympy.ntheory import ecm
    HAVE_ECM = True
except Exception:
    HAVE_ECM = False

OUT = "/home/neilh/science_lab/math/exp2_data.json"
random.seed(42)

def rsa_keygen(bits, e=65537):
    pbits = bits // 2
    qbits = bits - pbits
    while True:
        p = randprime(2**(pbits-1), 2**pbits)
        q = randprime(2**(qbits-1), 2**qbits)
        if p != q:
            n = p * q
            phi = (p-1)*(q-1)
            if math.gcd(e, phi) == 1:
                d = pow(e, -1, phi)
                return p, q, n, e, d

def rsa_encrypt(m, n, e):
    return pow(m, e, n)

def time_factor(n, limit=None):
    t0 = time.time()
    f = factorint(n, limit=limit)
    return f, time.time() - t0

def time_ecm(n, B1=2000, curves=50):
    t0 = time.time()
    facs = set()
    n_ = n
    for c in range(curves):
        try:
            g = ecm.find_factor(n_, B1=B1, B2=B1*100, curve=None)
        except Exception:
            g = None
        if g and 1 < g < n_:
            facs.add(int(g)); facs.add(int(n_//g)); break
    return facs, time.time() - t0

# ---------- RSA experiments ----------
rsa_rows = []
for bits in [64, 96, 128, 160, 192]:
    p, q, n, e, d = rsa_keygen(bits)
    m = random.randrange(2, n)
    c = rsa_encrypt(m, n, e)
    assert pow(c, d, n) == m
    # factor via factorint (Pollard rho) with a limit so we don't hang forever
    lim = 10**7 if bits <= 128 else 10**6
    f, dt = time_factor(n, limit=lim)
    fac_total = sum(f.values())
    factored_fully = (fac_total == 2 and all(v == 1 for v in f.values()))
    row = {"bits": bits, "n": str(n), "p_bits": p.bit_length(), "q_bits": q.bit_length(),
           "factorint_time": dt, "factorint": {str(k): v for k, v in f.items()},
           "fully_factored": factored_fully}
    rsa_rows.append(row)
    print(f"RSA {bits}-bit: factorint={dt:.2f}s fully={factored_fully} factors={list(f)[:3]}", flush=True)

# ECM attempt on a fresh 192-bit and (if fast enough) 256-bit modulus
for bits in [192, 256]:
    p, q, n, e, d = rsa_keygen(bits)
    m = random.randrange(2, n)
    c = rsa_encrypt(m, n, e)
    facs, dt = time_ecm(n, B1=2000, curves=200)
    print(f"RSA {bits}-bit ECM: {dt:.2f}s found={sorted(facs)}", flush=True)
    rsa_rows.append({"bits": bits, "ecm_time": dt, "ecm_found": sorted(facs),
                     "ecm_success": len(facs) == 2})

# ---------- Caesar cipher ----------
def caesar_enc(text, k):
    out = []
    for ch in text:
        if ch.isalpha():
            a = 'A' if ch.isupper() else 'a'
            out.append(chr((ord(ch) - ord(a) + k) % 26 + ord(a)))
        else:
            out.append(ch)
    return ''.join(out)

def caesar_break(ct):
    scores = []
    for k in range(26):
        pt = caesar_enc(ct, -k)
        # chi-squared-ish: count common letters
        common = sum(pt.lower().count(w) for w in ['the','and','ing','ion','ent','her','tha'])
        scores.append((common, k, pt))
    scores.sort(reverse=True)
    return scores[0]

msg = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDRUNSTHROUGHTHEFOREST"
for k in [3, 7, 13]:
    ct = caesar_enc(msg, k)
    best = caesar_break(ct)
    print(f"Caesar k={k}: broke key={best[1]} correct={best[1]==k}", flush=True)

# ---------- Vigenere ----------
def vig_enc(text, key):
    out = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            a = 'A' if ch.isupper() else 'a'
            out.append(chr((ord(ch) - ord(a) + ord(key[ki] % 32) % 26) % 26 + ord(a)))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

def vig_break(ct, keylen=None):
    # try key lengths 1..12, pick best by IOC-ish score per column via chi-squared
    ct_clean = [c for c in ct if c.isalpha()]
    def score_keylen(L):
        total = 0
        for i in range(L):
            col = ct_clean[i::L]
            best = 0
            for k in range(26):
                dec = ''.join(chr((ord(c) - 65 - k) % 26 + 65) for c in col)
                # count 'etaoinshrdlu'
                s = sum(dec.count(ch) for ch in 'ETAOINSHRDLU')
                best = max(best, s)
            total += best
        return total / max(1, len(ct_clean))
    if keylen is None:
        scores = [(score_keylen(L), L) for L in range(1, 13)]
        keylen = max(scores)[1]
    key = []
    for i in range(keylen):
        col = ct_clean[i::keylen]
        bestk, bests = 0, -1
        for k in range(26):
            dec = ''.join(chr((ord(c) - 65 - k) % 26 + 65) for c in col)
            s = sum(dec.count(ch) for ch in 'ETAOINSHRDLU')
            if s > bests: bests, bestk = s, k
        key.append(bestk)
    return ''.join(chr(k + 65) for k in key)

vmsg = "ATTACKATDAWNWETAKETHEBEACHANDTHEENEMYFLEESINTOTHENIGHT"
vkey = "LEMON"
vct = vig_enc(vmsg.upper(), vkey)
bk = vig_break(vct)
print(f"Vigenere key={vkey} broke={bk} match={bk==vkey}", flush=True)
# decrypt with broken key
def vig_dec(ct, key):
    out = []
    ki = 0
    for ch in ct:
        if ch.isalpha():
            out.append(chr((ord(ch) - 65 - (ord(key[ki % len(key)]) - 65)) % 26 + 65))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)
pt = vig_dec(vct, bk)
print("Vigenere decrypted:", pt[:60], flush=True)

json.dump({"rsa": rsa_rows,
           "caesar": [{"key": k} for k in [3,7,13]],
           "vigenere": {"true_key": vkey, "broken_key": bk, "pt_prefix": pt[:60]}},
          open(OUT, "w"), indent=1)
print("Wrote", OUT)

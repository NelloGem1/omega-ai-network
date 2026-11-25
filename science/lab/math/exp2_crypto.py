#!/usr/bin/env python3
"""Exp2: RSA toy -> break.
- Keygen+encrypt at 64..256 bits.
- Break via sympy factorint (Pollard rho, gmpy2-accelerated) with hard timeout.
- Break via GNU GMP-ECM binary with escalating B1.
- Extrapolate to 2048-bit infeasibility.
- Caesar + Vigenere breaks."""
import json, math, random, time, subprocess, os, signal
import gmpy2
from gmpy2 import mpz
from sympy import randprime, factorint

OUT = "/home/neilh/science_lab/math/exp2_data.json"
random.seed(42)

class Timeout(Exception): pass
def handler(signum, frame): raise Timeout()
signal.signal(signal.SIGALRM, handler)

def rsa_keygen(bits, e=65537):
    pbits = bits // 2
    qbits = bits - pbits
    while True:
        p = int(randprime(2**(pbits-1), 2**pbits))
        q = int(randprime(2**(qbits-1), 2**qbits))
        if p != q:
            n = p*q
            phi = (p-1)*(q-1)
            if math.gcd(e, phi) == 1:
                return p, q, n, e, pow(e, -1, phi)

def rsa_encrypt(m, n, e):
    return pow(m, e, n)

def timed_factorint(n, seconds):
    signal.alarm(int(seconds))
    t0 = time.time()
    try:
        f = factorint(n)
        dt = time.time()-t0
        return {"result": {str(k): v for k, v in f.items()}, "time": dt,
                "complete": __import__("functools").reduce(lambda a,kv: a*kv[0]**kv[1], f.items(), 1) == n}
    except Timeout:
        return {"result": None, "time": seconds, "complete": False, "timeout": True}
    except Exception as ex:
        return {"result": None, "time": time.time()-t0, "error": str(ex)}
    finally:
        signal.alarm(0)

def timed_ecm_binary(n, b1_list, max_total=300):
    """Run GNU ecm binary, escalating B1. Returns time to first factor."""
    t0 = time.time()
    for b1 in b1_list:
        if time.time()-t0 > max_total: break
        try:
            r = subprocess.run(["ecm", "-c", "100", str(b1)],
                               input=str(n)+"\n", capture_output=True, text=True,
                               timeout=max_total - (time.time()-t0) + 5)
            # parse "Factor found in step ... : <digits> digits" or the factor line
            for line in r.stdout.splitlines():
                # ecm prints factors like "... : 123456789... " hard to parse;
                # use sympy to recover: collect candidate factors printed
                pass
            # simpler: run ecm with -q and check stdout for lines containing the factor
            # Instead use python wrapper: parse all integers on lines after "Factor found"
            facs = []
            for line in r.stdout.splitlines():
                if "Factor found" in line or ":" in line:
                    for tok in line.replace(":", " ").split():
                        try:
                            v = int(tok)
                            if v > 1 and n % v == 0:
                                facs.append(v)
                        except ValueError:
                            pass
            if facs:
                f = facs[0]
                return {"b1": b1, "time": time.time()-t0, "factor": f,
                        "cofactor_bits": (n//f).bit_length()}
        except subprocess.TimeoutExpired:
            break
    return {"time": time.time()-t0, "factor": None}

rsa_rows = []
keys = {}
# small sizes: factorint with timeout
for bits in [64, 96, 128]:
    p, q, n, e, d = rsa_keygen(bits)
    m = random.randrange(2, n)
    c = rsa_encrypt(m, n, e)
    assert pow(c, d, n) == m
    keys[bits] = (p, q, n, e, d)
    r = timed_factorint(n, 90)
    rsa_rows.append({"bits": bits, "n": str(n), "p_bits": p.bit_length(),
                     "factorint": r})
    print(f"RSA {bits}: factorint {r['time']:.2f}s complete={r.get('complete')}", flush=True)

# larger sizes: GNU ecm binary
for bits in [160, 192, 256]:
    p, q, n, e, d = rsa_keygen(bits)
    m = random.randrange(2, n)
    c = rsa_encrypt(m, n, e)
    assert pow(c, d, n) == m
    keys[bits] = (p, q, n, e, d)
    r = timed_ecm_binary(n, [2000, 11000, 50000], max_total=240)
    rsa_rows.append({"bits": bits, "n": str(n), "ecm": r,
                     "p_bits": p.bit_length()})
    print(f"RSA {bits}: ecm {r['time']:.1f}s factor={r.get('factor')}", flush=True)

# save private keys for verification record
keydump = {str(b): {"p": str(keys[b][0]), "q": str(keys[b][1]),
                    "n": str(keys[b][2]), "d": str(keys[b][3])} for b in keys}

# ---------- Caesar ----------
def caesar_enc(text, k):
    out = []
    for ch in text:
        if ch.isalpha():
            a = 'A' if ch.isupper() else 'a'
            out.append(chr((ord(ch)-ord(a)+k) % 26 + ord(a)))
        else:
            out.append(ch)
    return ''.join(out)

def caesar_break(ct):
    best = None
    for k in range(26):
        pt = caesar_enc(ct, -k)
        score = sum(pt.lower().count(w) for w in ['the','and','ing','ion','ent','her','tha','for'])
        if best is None or score > best[0]:
            best = (score, k, pt)
    return best

msg = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDRUNSTHROUGHTHEFOREST"
caesar_rows = []
for k in [3, 7, 13]:
    ct = caesar_enc(msg, k)
    sc, bk, pt = caesar_break(ct)
    caesar_rows.append({"key": k, "broken_key": bk, "score": sc})
    print(f"Caesar k={k}: broke={bk} correct={bk==k}", flush=True)

# ---------- Vigenere ----------
def vig_enc(text, key):
    out = []; ki = 0
    for ch in text:
        if ch.isalpha():
            a = 'A' if ch.isupper() else 'a'
            out.append(chr((ord(ch)-ord(a)+(ord(key[ki % len(key)])-65)) % 26 + ord(a)))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

FREQ = {'A':.08167,'B':.01492,'C':.02782,'D':.04253,'E':.12702,'F':.02228,'G':.02015,
'H':.06094,'I':.06966,'J':.00153,'K':.00772,'L':.04025,'M':.02406,'N':.06749,
'O':.07507,'P':.01929,'Q':.00095,'R':.05987,'S':.06327,'T':.09056,'U':.02758,
'V':.00978,'W':.02360,'X':.00150,'Y':.01974,'Z':.00074}
LOGF = {c: math.log(v) for c, v in FREQ.items()}

def _ioc(s):
    from collections import Counter
    n = len(s); c = Counter(s)
    return sum(v*(v-1) for v in c.values())/(n*(n-1)) if n > 1 else 0.0

def col_logp(col, k):
    return sum(LOGF.get(chr((ord(c)-65-k) % 26 + 65), -20) for c in col)

def vig_break(ct, maxlen=15):
    """IOC picks key length; per-column English log-likelihood recovers key."""
    clean = [c for c in ct if c.isalpha()]
    iocs = [(sum(_ioc(''.join(clean[i::L])) for i in range(L))/L, L)
            for L in range(1, maxlen+1)]
    keylen = max(iocs)[1]
    key = []
    for i in range(keylen):
        col = ''.join(clean[i::keylen])
        key.append(max(range(26), key=lambda k: col_logp(col, k)))
    return ''.join(chr(k+65) for k in key), keylen, sorted(iocs, reverse=True)[:5]

def vig_dec(ct, key):
    out = []; ki = 0
    for ch in ct:
        if ch.isalpha():
            out.append(chr((ord(ch)-65-(ord(key[ki % len(key)])-65)) % 26 + 65))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

words = ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDRUNSTHROUGHTHEFOREST"
         "WHILETHEWIND BLOWS GENTLY ACROSS THE MEADOWS AND THE RIVER FLOWS "
         "TOWARD THE SEA UNDER THE WATCHFUL EYES OF THE STARS ")
vmsg = (words * 8)[:500]
vkey = "LEMON"
vct = vig_enc(vmsg, vkey)
bk, bklen, kscores = vig_break(vct)
pt = vig_dec(vct, bk)
print(f"Vigenere true={vkey} broke={bk} len={bklen} match={bk==vkey}", flush=True)
print("Vigenere plaintext:", pt[:70], flush=True)

json.dump({"rsa": rsa_rows, "keys": keydump,
           "caesar": caesar_rows,
           "vigenere": {"true_key": vkey, "broken_key": bk, "broken_len": bklen,
                        "ioc_scores": kscores, "plaintext": pt, "ciphertext": vct,
                        "method": "IOC keylen + per-column English log-likelihood"}},
          open(OUT, "w"), indent=1)
print("Wrote", OUT)

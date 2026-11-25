#!/usr/bin/env python3
"""Deep ECM attempt on a 192-bit RSA semiprime (96-bit factors, ~29 digits)."""
import random, time, subprocess, json
from sympy import randprime
random.seed(777)
p = int(randprime(2**95, 2**96)); q = int(randprime(2**95, 2**96))
n = p*q
log = {"n": str(n), "p": str(p), "q": str(q), "n_bits": n.bit_length()}
t0 = time.time()
try:
    r = subprocess.run(["ecm", "-c", "500", "250000"], input=str(n)+"\n",
                       capture_output=True, text=True, timeout=1500)
    out = r.stdout
except subprocess.TimeoutExpired:
    out = "TIMEOUT"
log["elapsed"] = time.time()-t0
log["stdout_tail"] = out[-3000:] if isinstance(out, str) else out
# try to extract a factor
import re
found = None
if isinstance(out, str):
    for line in out.splitlines():
        for tok in re.split(r"[^0-9]+", line):
            if tok:
                v = int(tok)
                if 1 < v < n and n % v == 0:
                    found = v
log["factor"] = found
json.dump(log, open("/home/neilh/science_lab/math/ecm192_result.json","w"), indent=1)
print(json.dumps({k: log[k] for k in ("elapsed","factor","n_bits")}))
print(out[-1500:] if isinstance(out,str) else out)

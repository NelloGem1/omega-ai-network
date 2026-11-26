#!/usr/bin/env python3
"""LIMITLESS COMPRESSION LAB — novel + classic algorithms, auto-select, benchmark."""
import zlib, bz2, lzma, os, math, json, time, struct
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA, exist_ok=True)

# ---------- entropy analysis ----------
def entropy(data):
    if not data: return 0
    c = Counter(data); n = len(data)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def redundancy_score(data):
    """0=incompressible(random) 1=highly redundant"""
    e = entropy(data)
    return max(0.0, 1.0 - e/8.0)

# ---------- CLASSIC ----------
def zlib_c(d): return zlib.compress(d,9)
def bz2_c(d): return bz2.compress(d,9)
def lzma_c(d): return lzma.compress(d,preset=9)

# ---------- NOVEL 1: RLE+varint (byte-level run encoding) ----------
def rle_c(d):
    out = bytearray(); i=0; n=len(d)
    while i<n:
        j=i+1
        while j<n and d[j]==d[i] and j-i<255: j+=1
        run=j-i
        if run>=4:
            out += bytes([0xFF, d[i], run])
        else:
            for k in range(i,j): out.append(d[k])
        i=j
    return bytes(out)

def rle_d(c):
    out=bytearray(); i=0
    while i<len(c):
        if c[i]==0xFF and i+2<len(c):
            out += bytes([c[i+1]])*c[i+2]; i+=3
        else: out.append(c[i]); i+=1
    return bytes(out)

# ---------- NOVEL 2: dictionary/BPE-lite (learn top n-grams, emit token stream) ----------
def dict_c(d, topk=256):
    # find most frequent 4-byte substrings → dictionary
    grams = Counter(d[i:i+4] for i in range(len(d)-3))
    vocab = [g for g,_ in grams.most_common(topk)]
    vidx = {g:i for i,g in enumerate(vocab)}
    out = bytearray([len(vocab)])
    # header: vocab
    for g in vocab: out += g
    i=0; n=len(d)
    while i<n:
        matched=False
        for L in (8,6,5,4):
            if i+L<=n:
                sub=d[i:i+L]
                # try longest dict match
                for g in vocab:
                    if sub[:len(g)]==g and len(g)>=4:
                        out.append(0x80|vidx[g]); i+=len(g); matched=True; break
                if matched: break
        if not matched:
            out.append(d[i]); i+=1
    return bytes(out)

# ---------- NOVEL 3: XOR-delta for numeric/structured data ----------
def delta_c(d):
    if len(d)<2: return b'\x00'+d
    out=bytearray([0x01])
    prev=d[0]; out.append(prev)
    for b in d[1:]:
        out.append((b-prev)&0xFF); prev=b
    return bytes(out)

def delta_d(c):
    if not c or c[0]!=1: return c[1:] if c else c
    out=bytearray([c[1]]); prev=c[1]
    for x in c[2:]:
        prev=(prev+x)&0xFF; out.append(prev)
    return bytes(out)

# ---------- NOVEL 4: cross-file dedup (content-defined chunking lite) ----------
def dedup_key(d, chunk=4096):
    """Return set of chunk hashes for cross-file dedup detection."""
    return {hash(d[i:i+chunk]) for i in range(0,len(d),chunk)}

# ---------- auto-select ----------
ALGO = {'zlib':zlib_c,'bz2':bz2_c,'lzma':lzma_c,'rle':rle_c,'dict':dict_c,'delta':delta_c}

def compress(d, algo=None):
    if algo is None:
        algo = auto_select(d)
    t=time.time(); c = ALGO[algo](d); dt=time.time()-t
    return c, algo, dt

def auto_select(d):
    """Brute-force: compress with each algo, pick smallest."""
    best, best_size = 'zlib', len(d)
    for algo in ('zlib','bz2','lzma','rle'):
        try:
            c = ALGO[algo](d)
            if 0 < len(c) < best_size:
                best, best_size = algo, len(c)
        except Exception: pass
    return best

def decompress(c, algo):
    if algo=='zlib': return zlib.decompress(c)
    if algo=='bz2': return bz2.decompress(c)
    if algo=='lzma': return lzma.decompress(c)
    if algo=='rle': return rle_d(c)
    if algo=='delta': return delta_d(c)
    if algo=='dict': return None  # dict needs vocab — store wrapper
    return None

# ---------- integrity ----------
def checksum(d):
    import hashlib
    return hashlib.sha256(d).hexdigest()[:16]

# ---------- benchmark ----------
def make_bench_files():
    """Generate diverse test data."""
    files = {}
    # 1. text log (highly compressible)
    files['log.txt'] = (b'2024-01-01 INFO server started\n'*500 +
                        b'2024-01-01 ERROR connection refused\n'*300 +
                        b'2024-01-01 WARN high latency\n'*200)
    # 2. CSV-ish numeric (delta-friendly)
    files['metrics.csv'] = b''.join(b'%d,%d,%d\n'%(i,i*2,i*3) for i in range(5000))
    # 3. random bytes (incompressible)
    import random; random.seed(1)
    files['random.bin'] = bytes(random.getrandbits(8) for _ in range(50000))
    # 4. source code (medium)
    files['code.py'] = open(__file__,'rb').read()*30
    # 5. repetitive pattern
    files['pattern.bin'] = b'ABCDEFGH'*5000
    # 6. JSON data
    files['data.json'] = (b'{"id":%d,"name":"user%d","score":%d}'%(i,i,i%100) for i in range(3000))
    files['data.json'] = b''.join(files['data.json'])
    return files

def bench():
    files = make_bench_files()
    report = []
    for name, data in files.items():
        orig = len(data)
        row = {'file':name,'orig':orig,'entropy':round(entropy(data),2),
               'redundancy':round(redundancy_score(data),2),'algos':{}}
        for algo in ALGO:
            try:
                t=time.time(); c=ALGO[algo](data); dt=time.time()-t
                ok = decompress(c,algo)==data if algo!='dict' else 'n/a'
                row['algos'][algo] = {'size':len(c),'ratio':round(orig/len(c),2) if len(c) else 0,
                                      'time_ms':round(dt*1000,1),'roundtrip':ok}
            except Exception as e:
                row['algos'][algo] = {'error':str(e)[:40]}
        # auto-select pick
        auto = auto_select(data); c,_,_ = compress(data,auto)
        row['auto_algo']=auto; row['auto_size']=len(c)
        row['auto_ratio']=round(orig/len(c),2) if len(c) else 0
        report.append(row)
        print(f"{name}: orig={orig} auto={auto} ratio={row['auto_ratio']}x")
    return report

if __name__=='__main__':
    rep = bench()
    out = os.path.join(os.path.dirname(__file__),'bench','report.json')
    json.dump(rep, open(out,'w'), indent=2)
    print('saved', out)

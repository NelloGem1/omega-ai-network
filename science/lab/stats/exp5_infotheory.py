import numpy as np
from heapq import heappush, heappop
import collections, math, zlib

rng = np.random.default_rng(5)

print("=== 5a. Huffman coding vs entropy bound ===")
def huffman_lengths(freqs):
    # returns code lengths per symbol
    heap=[(f,i,[i]) for i,f in enumerate(freqs) if f>0]
    heap=[(f,[i]) for i,f in enumerate(freqs) if f>0]
    heap.sort(key=lambda t:t[0])
    import heapq as hq
    heap=[(f, idx, [idx]) for idx,(i,f) in enumerate([(i,f) for i,f in enumerate(freqs) if f>0])]
    heap=[(f, k, [sym]) for k,(sym,f) in enumerate([(i,f) for i,f in enumerate(freqs) if f>0])]
    hq.heapify(heap); cnt=len(heap); lens={}
    while len(heap)>1:
        f1,_,s1=hq.heappop(heap); f2,_,s2=hq.heappop(heap)
        for s in s1+s2: lens[s]=lens.get(s,0)+1
        hq.heappush(heap,(f1+f2,cnt,s1+s2)); cnt+=1
    return lens

def entropy_bits(freqs):
    t=sum(freqs); return -sum((f/t)*math.log2(f/t) for f in freqs if f>0)

# skewed distribution
freqs=[50,20,10,8,5,3,2,1,1]
tot=sum(freqs)
H = entropy_bits(freqs)
lens = huffman_lengths(freqs)
# map: freqs list index = symbol; need symbol list
syms=[i for i,f in enumerate(freqs) if f>0]
f2=[f for f in freqs if f>0]
lens2=huffman_lengths(f2)
avg_len = sum(l*f for l,f in zip([lens2[s] for s in range(len(f2))],f2))/tot
print(f"freqs={f2}")
print(f"entropy H={H:.4f} bits/sym, Huffman avg len={avg_len:.4f} bits/sym, redundancy={avg_len-H:.4f}")

print("=== 5b. Real text compression vs entropy ===")
# use TOOLS.md content if reachable; else synthetic English-like
import os
paths=["/home/neilh/TOOLS.md","/home/neilh/science_lab/stats/exp5_infotheory.py"]
text=open(paths[0],errors="ignore").read()[:200000]
bytes_data=text.encode()
H_order0 = entropy_bits(np.bincount(np.frombuffer(bytes_data,dtype=np.uint8),minlength=256))
z = zlib.compress(bytes_data,9)
print(f"text len={len(bytes_data)} bytes")
print(f"order-0 entropy={H_order0:.3f} bits/byte -> bound {H_order0*len(bytes_data)/8:.0f} bytes")
print(f"zlib size={len(z)} bytes ({len(z)*8/len(bytes_data):.3f} bits/byte)")
# order-1 (context) entropy estimate on byte pairs is heavy; do char-level order-1
txt = text[:50000]
pairs = collections.Counter(zip(txt, txt[1:]))
ctx = collections.Counter(txt[:-1])
H1 = sum(-c/len(txt)*sum((cc/c)*math.log2(cc/c) for cc in [pairs[(a,b) for b in txt[1:] if False] or 0]) for a,c in [])
# simpler: compute conditional entropy properly
H_cond=0.0
for a,c in ctx.items():
    tot=c
    for b in set(txt):
        cc=pairs.get((a,b),0)
        if cc: H_cond += (cc/len(txt))*math.log2(tot/cc)
print(f"order-1 conditional entropy ~= {H_cond:.3f} bits/char (lower bound on achievable)")
print(f"actual char entropy achieved by zlib ~ {len(z)*8/len(bytes_data):.3f} bits/byte")

print("=== 5c. Plug-in entropy bias: small samples ===")
# true distribution over 26 letters; estimate H from n samples
freqs=np.array([8.2,1.5,2.8,4.3,12.7,2.2,2.0,6.1,7.0,0.15,0.77,4.0,2.4,6.7,7.5,1.9,0.095,6.0,6.3,9.1,2.8,0.98,2.4,0.15,2.0,0.074])
p=freqs/freqs.sum(); H_true=-(p*np.log2(p)).sum()
for n in [100,1000,10000]:
    ests=[]
    for _ in range(300):
        s=rng.choice(26,size=n,p=p)
        c=np.bincount(s,minlength=26)/n
        c=c[c>0]
        ests.append(-(c*np.log2(c)).sum())
    print(f"n={n:>6}: plug-in H={np.mean(ests):.4f} (true {H_true:.4f}), bias={np.mean(ests)-H_true:+.4f} bits")

print("=== 5d. Mutual information plug-in bias ===")
# independent X,Y over k states -> true MI=0; plug-in MI >0
for k in [4,16]:
    for n in [100,1000,10000]:
        mis=[]
        for _ in range(200):
            x=rng.integers(0,k,n); y=rng.integers(0,k,n)
            joint=np.zeros((k,k))
            for a,b in zip(x,y): joint[a,b]+=1
            pj=joint/n; px=pj.sum(1); py=pj.sum(0)
            mi=0
            for i in range(k):
                for j in range(k):
                    if pj[i,j]>0: mi+=pj[i,j]*math.log2(pj[i,j]/(px[i]*py[j]))
            mis.append(mi)
        print(f"k={k}, n={n}: mean plug-in MI={np.mean(mis):.4f} bits (true 0) — bias ~ {(k-1)**2/(2*n*math.log(2)):.4f} predicted")

import numpy as np
import heapq as hq
import collections, math, zlib

rng = np.random.default_rng(5)

print("=== 5a. Huffman coding vs entropy bound ===")
def huffman_lengths(freqs):
    items=[(f,i,[i]) for i,f in enumerate(freqs) if f>0]
    hq.heapify(items); cnt=len(items); lens={}
    while len(items)>1:
        f1,_,s1=hq.heappop(items); f2,_,s2=hq.heappop(items)
        for s in s1+s2: lens[s]=lens.get(s,0)+1
        hq.heappush(items,(f1+f2,cnt,s1+s2)); cnt+=1
    return lens

def entropy_bits(freqs):
    t=sum(freqs); return -sum((f/t)*math.log2(f/t) for f in freqs if f>0)

freqs=[50,20,10,8,5,3,2,1,1]
tot=sum(freqs)
H = entropy_bits(freqs)
lens = huffman_lengths(freqs)
avg_len = sum(lens.get(i,0)*f for i,f in enumerate(freqs))/tot
print(f"freqs={freqs}")
print(f"entropy H={H:.4f} bits/sym, Huffman avg len={avg_len:.4f} bits/sym, redundancy={avg_len-H:.4f}")

print("=== 5b. Real text compression vs entropy ===")
text=open("/home/neilh/TOOLS.md",errors="ignore").read()[:200000]
bytes_data=text.encode()
counts=np.bincount(np.frombuffer(bytes_data,dtype=np.uint8),minlength=256)
H_order0 = entropy_bits(counts)
z = zlib.compress(bytes_data,9)
print(f"text len={len(bytes_data)} bytes")
print(f"order-0 entropy={H_order0:.3f} bits/byte -> bound ~{H_order0*len(bytes_data)/8:.0f} bytes")
print(f"zlib size={len(z)} bytes ({len(z)*8/len(bytes_data):.3f} bits/byte)")
txt = text[:50000]
pairs = collections.Counter(zip(txt, txt[1:]))
ctx = collections.Counter(txt[:-1])
H_cond=0.0
n=len(txt)-1
for (a,b),cc in pairs.items():
    H_cond += (cc/n)*math.log2(ctx[a]/cc)
print(f"order-1 conditional entropy ~= {H_cond:.3f} bits/char")
print(f"zlib achieved ~ {len(z)*8/len(bytes_data):.3f} bits/byte")

print("=== 5c. Plug-in entropy bias: small samples ===")
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
for k in [4,16]:
    for n in [100,1000,10000]:
        mis=[]
        for _ in range(200):
            x=rng.integers(0,k,n); y=rng.integers(0,k,n)
            joint=np.zeros((k,k))
            for a,b in zip(x,y): joint[a,b]+=1
            pj=joint/n; px=pj.sum(1); py=pj.sum(0)
            mi=0.0
            for i in range(k):
                for j in range(k):
                    if pj[i,j]>0: mi+=pj[i,j]*math.log2(pj[i,j]/(px[i]*py[j]))
            mis.append(mi)
        print(f"k={k}, n={n}: mean plug-in MI={np.mean(mis):.4f} bits (true 0); naive bias approx {(k-1)**2/(2*n*math.log(2)):.4f}")

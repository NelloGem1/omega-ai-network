#!/usr/bin/env python3
"""Experiment 3: Open-addressing hash table - good hash vs adversarial collisions."""
import random, time, csv, os
random.seed(11)
DATA='/home/neilh/science_lab/cs/data'
DELETED = object()

class OALinProbe:
    """Open addressing, linear probing, multiplicative-ish hash mod m."""
    def __init__(self, capacity=1024, hashfn=None):
        self.m = capacity
        self.keys = [None]*self.m
        self.vals = [None]*self.m
        self.used = 0
        self.cmp = 0
        self.hashfn = hashfn or (lambda k: (k*2654435761) % (2**32))
    def _h(self,k): return self.hashfn(k) % self.m
    def insert(self,k,v):
        i=self._h(k); probes=0
        while self.keys[i] is not None and self.keys[i] is not DELETED:
            self.cmp+=1; probes+=1
            if probes>self.m: raise RuntimeError('table full')
            i=(i+1)%self.m
        if self.keys[i] is None: self.used+=1
        self.keys[i]=k; self.vals[i]=v
        return probes+1
    def get(self,k):
        i=self._h(k); probes=0
        while self.keys[i] is not None:
            self.cmp+=1; probes+=1
            if self.keys[i] is k or self.keys[i]==k: return self.vals[i], probes
            if self.keys[i] is DELETED: break
            i=(i+1)%self.m
            if probes>self.m: break
        return None, probes

def run(keys_vals, m, hashfn, label):
    t=OALinProbe(m, hashfn)
    t0=time.perf_counter()
    for k,v in keys_vals: t.insert(k,v)
    tins=time.perf_counter()-t0
    qs=[k for k,_ in keys_vals[::max(1,len(keys_vals)//2000)][:2000]]
    t0=time.perf_counter(); tot=0
    for q in qs:
        _,p=t.get(q); tot+=p
    tget=time.perf_counter()-t0
    return dict(setup=label, n=len(keys_vals), cap=m, insert_s=round(tins,4),
                get_s=round(tget,4), avg_probes=round(tot/len(qs),2), cmps=t.cmp)

def good_hash(k): return (k*2654435761) % (2**32)
def ident_hash(k): return k          # identity: collisions mod m
def lowbits_hash(k): return k & 0xFF # only low 8 bits -> massive collision if m<=256

def adversarial_keys(m, count):
    # keys that are all 0 mod m under identity-ish hash: multiples of m
    return [(i*m + random.randrange(m)) for i in range(count)]  # distinct keys, same low bits? 

def main():
    rows=[]
    # Scenario A: random keys, good multiplicative hash
    for n in [1000, 5000, 20000]:
        kv=[(random.randrange(10**9), i) for i in range(n)]
        m=1
        while m < n*2: m*=2
        rows.append(run(kv,m,good_hash,f'random_goodhash_n{n}'))
        rows.append(run(kv,m,ident_hash,f'random_identhash_n{n}'))
    # Scenario B: adversarial - keys crafted so hash mod m collide.
    for n in [500, 1000, 2000, 5000]:
        m=16
        while m < n*2: m*=2
        # keys all congruent 0 mod m -> same bucket under identity hash
        kv=[(i*m, i) for i in range(n)]
        rows.append(run(kv,m,ident_hash,f'adversarial_ident_n{n}'))
        rows.append(run(kv,m,good_hash,f'adversarial_goodhash_n{n}'))
        # keys sharing low 8 bits -> collide under lowbits hash
        kv2=[((i % (m//256))*256 + (i//(m//256))*m*256, i) for i in range(n)]
        rows.append(run(kv2,m,lowbits_hash,f'adversarial_lowbits_n{n}'))
    # Python dict comparison on adversarial int keys
    for n in [10000, 100000]:
        m=1024
        kv=[(i*m, i) for i in range(n)]
        d={}
        t0=time.perf_counter()
        for k,v in kv: d[k]=v
        tins=time.perf_counter()-t0
        t0=time.perf_counter()
        for k,v in kv[::10]: _=d[k]
        tget=time.perf_counter()-t0
        rows.append(dict(setup=f'pydict_adversarial_n{n}', n=n, cap=0, insert_s=round(tins,4),
                         get_s=round(tget,4), avg_probes=0, cmps=0))
        print('pydict', n, tins, tget, flush=True)
    with open(f'{DATA}/exp3_hashtable.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows: print(r, flush=True)
    print('wrote exp3_hashtable.csv')

main()

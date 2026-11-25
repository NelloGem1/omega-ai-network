#!/usr/bin/env python3
"""exp7_bigO FIXED: log-log slope exponents.
Fix vs exp7_bigO.py L29: 'dict_lookup_O1' did range(0,n,10) = n/10 lookups,
i.e. O(n) work mislabeled as O(1). Now performs a FIXED number of lookups
(LOOKUPS=3000) regardless of table size n -> per-lookup cost is O(1) and
total measured time should be flat in n (exponent ~0).
Also bumps reps for the noisy single-shot tests where cheap."""
import time, math, csv, os, random, bisect, sys
sys.setrecursionlimit(300000)
random.seed(13)
DATA='/home/neilh/science_lab/cs/data'
LOOKUPS = 2000  # FIX: constant work independent of n

def timeit(fn, reps=3):
    best=float('inf')
    for _ in range(reps):
        t0=time.perf_counter(); fn(); dt=time.perf_counter()-t0
        best=min(best,dt)
    return best

def slope(xs, ys):
    lx=[math.log(x) for x in xs]; ly=[math.log(max(y,1e-9)) for y in ys]
    n=len(xs); mx=sum(lx)/n; my=sum(ly)/n
    num=sum((a-mx)*(b-my) for a,b in zip(lx,ly))
    den=sum((a-mx)**2 for a in lx)
    return num/den

def main():
    rows=[]
    sizes=[2000,4000,8000,16000,32000,64000]

    # dict lookup O(1) — FIX: fixed LOOKUPS queries, not n/10
    xs=[];ys=[]
    keys=list(range(LOOKUPS))  # all < min(sizes)=2000
    for n in sizes:
        d={i:i for i in range(n)}
        t=timeit(lambda:[d[i] for i in keys])
        xs.append(n);ys.append(t); rows.append(dict(test='dict_lookup_O1',n=n,time_s=round(t,6)))
    sl=slope(xs,ys); print('dict_lookup exponent',round(sl,3),'(expect ~0)',flush=True)
    rows.append(dict(test='dict_lookup_O1_exponent',n='',time_s='',exponent=round(sl,3)))

    # list max O(n)
    xs=[];ys=[]
    for n in sizes:
        lst=[random.random() for _ in range(n)]
        t=timeit(lambda:max(lst))
        xs.append(n);ys.append(t); rows.append(dict(test='list_max_On',n=n,time_s=round(t,6)))
    sl=slope(xs,ys); print('list_max exponent',round(sl,3),flush=True)
    rows.append(dict(test='list_max_On_exponent',n='',time_s='',exponent=round(sl,3)))

    # sort O(n log n)
    xs=[];ys=[]
    for n in sizes:
        lst=[random.random() for _ in range(n)]
        t=timeit(lambda:sorted(lst))
        xs.append(n);ys.append(t); rows.append(dict(test='sort_O(nlogn)',n=n,time_s=round(t,6)))
    sl=slope(xs,ys); print('sort exponent',round(sl,3),'(expect ~1.x)',flush=True)
    rows.append(dict(test='sort_O(nlogn)_exponent',n='',time_s='',exponent=round(sl,3)))

    # bisect O(log n)
    xs=[];ys=[]
    for n in sizes:
        srt=sorted(random.random() for _ in range(n))
        t=timeit(lambda:[bisect.bisect_left(srt,random.random()) for _ in range(3000)])
        xs.append(n);ys.append(t); rows.append(dict(test='bisect_Ologn',n=n,time_s=round(t,6)))
    sl=slope(xs,ys); print('bisect exponent',round(sl,3),'(expect ~0)',flush=True)
    rows.append(dict(test='bisect_Ologn_exponent',n='',time_s='',exponent=round(sl,3)))

    # nested loop O(n^2), small sizes
    xs=[];ys=[]
    for n in [200,400,800,1600,3200]:
        arr=list(range(n))
        t=timeit(lambda:sum(1 for i in arr for j in arr if i<j and (i+j)%7==0),reps=1)
        xs.append(n);ys.append(t); rows.append(dict(test='nested_loop_On2',n=n,time_s=round(t,4)))
    sl=slope(xs,ys); print('nested exponent',round(sl,3),'(expect ~2)',flush=True)
    rows.append(dict(test='nested_loop_On2_exponent',n='',time_s='',exponent=round(sl,3)))

    # fib naive exponential vs memoized linear
    def fib_naive(n):
        if n<2: return n
        return fib_naive(n-1)+fib_naive(n-2)
    xs=[];ys=[]
    for n in [10,15,20,25,28,30]:
        t=timeit(lambda:fib_naive(n),reps=1)
        xs.append(n);ys.append(t); rows.append(dict(test='fib_naive_exp',n=n,time_s=round(t,4)))
        print('fib naive',n,round(t,4),flush=True)
    def fib_iter(n):
        a,b=0,1
        for _ in range(n): a,b=b,a+b
        return a
    xs=[];ys=[]
    for n in [1000,10000,100000,1000000]:
        t=timeit(lambda:fib_iter(n),reps=1)
        xs.append(n);ys.append(t); rows.append(dict(test='fib_dp_lin',n=n,time_s=round(t,4)))
        print('fib iter',n,round(t,4),flush=True)

    with open(f'{DATA}/exp7_bigo_fixed.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['test','n','time_s','exponent']); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in ['test','n','time_s','exponent']})
    print('wrote exp7_bigo_fixed.csv',flush=True)
main()

#!/usr/bin/env python3
"""Experiment 1: Sorting showdown - pure-Python sorts vs Timsort."""
import sys, time, random, json, csv, os, math, functools
sys.setrecursionlimit(1_000_000)
random.seed(42)
DATA = '/home/neilh/science_lab/cs/data'
os.makedirs(DATA, exist_ok=True)

def quicksort(a, pivot='first'):
    """In-place 3-way quicksort; returns comparison count."""
    cmp = [0]
    def q(lo, hi):
        if hi - lo <= 1: return
        if pivot == 'first': p = a[lo]
        elif pivot == 'last':  p = a[hi-1]
        elif pivot == 'mid':   p = a[(lo+hi)//2]
        else:                  p = a[random.randrange(lo, hi)]
        lt, i, gt = lo, lo, hi
        while i < gt:
            cmp[0] += 1
            if a[i] < p:   a[lt], a[i] = a[i], a[lt]; lt += 1; i += 1
            elif a[i] > p: gt -= 1; a[i], a[gt] = a[gt], a[i]
            else: i += 1
        q(lo, lt); q(gt, hi)
    q(0, len(a))
    return cmp[0]

def mergesort(a):
    cmp = [0]
    def ms(lo, hi):
        if hi - lo <= 1: return
        mid = (lo+hi)//2
        ms(lo, mid); ms(mid, hi)
        tmp = []; i, j = lo, mid
        while i < mid and j < hi:
            cmp[0] += 1
            if a[i] <= a[j]: tmp.append(a[i]); i += 1
            else:           tmp.append(a[j]); j += 1
        tmp += a[i:mid]; tmp += a[j:hi]
        a[lo:hi] = tmp
    ms(0, len(a))
    return cmp[0]

def heapsort(a):
    cmp = [0]; n = len(a)
    def sift(size, root):
        while True:
            c = 2*root+1
            if c >= size: break
            cmp[0] += 1
            if c+1 < size:
                cmp[0] += 1
                if a[c] < a[c+1]: c += 1
            if a[root] < a[c]:
                a[root], a[c] = a[c], a[root]; root = c
            else: break
    for s in range(n//2 - 1, -1, -1): sift(n, s)
    for end in range(n-1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift(end, 0)
    return cmp[0]

def insertion(a):
    cmp = [0]
    for i in range(1, len(a)):
        j = i
        while j > 0:
            cmp[0] += 1
            if a[j-1] <= a[j]: break
            a[j-1], a[j] = a[j], a[j-1]; j -= 1
    return cmp[0]

def bubble(a):
    cmp = [0]; n = len(a)
    for i in range(n):
        swapped = False
        for j in range(n-1-i):
            cmp[0] += 1
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]; swapped = True
        if not swapped: break
    return cmp[0]

ALGOS = {
    'quicksort_first': lambda a: quicksort(a, 'first'),
    'quicksort_mid':   lambda a: quicksort(a, 'mid'),
    'quicksort_rand':  lambda a: quicksort(a, 'rand'),
    'mergesort':       lambda a: mergesort(a),
    'heapsort':        lambda a: heapsort(a),
    'insertion':       lambda a: insertion(a),
    'bubble':          lambda a: bubble(a),
    'timsort':         lambda a: timsort_wrap(a),
}

def timsort_wrap(a):
    t0 = sorted(a)
    # comparison count for Timsort is not observable in C; estimate via cmp_to_key separately
    return 0

def gen(kind, n):
    if kind == 'random':  return [random.randrange(10**6) for _ in range(n)]
    if kind == 'sorted':  return list(range(n))
    if kind == 'reverse': return list(range(n, 0, -1))
    if kind == 'organ':
        h = n//2
        return list(range(h)) + list(range(n-1, h-1, -1))
    if kind == 'fewuniq': return [random.randrange(5) for _ in range(n)]

def skip(name, kind, n):
    if name == 'bubble' and n > 2000: return True
    if name == 'insertion' and n > 10000: return True
    if name in ('quicksort_first','quicksort_mid') and kind in ('sorted','reverse','organ','fewuniq') and n > 20000: return True
    return False

def main():
    rows = []
    sizes = [1000, 5000, 10000, 30000, 100000]
    kinds = ['random', 'sorted', 'reverse', 'organ', 'fewuniq']
    for n in sizes:
        for kind in kinds:
            base = gen(kind, n)
            for name, fn in ALGOS.items():
                if skip(name, kind, n): continue
                a = list(base)
                t0 = time.perf_counter()
                cmp_n = fn(a)
                dt = time.perf_counter() - t0
                assert a == sorted(base), f'{name} wrong on {kind} n={n}'
                rows.append(dict(n=n, kind=kind, algo=name, time_s=round(dt,4),
                                 comparisons=cmp_n,
                                 nlogn=round(dt/(n*max(1,math.log2(n))),8)))
                print(f'n={n} {kind:8s} {name:16s} t={dt:7.3f}s cmp={cmp_n}', flush=True)
            # Timsort comparison count via cmp_to_key
            c = [0]
            def cmpf(x,y): c[0]+=1; return (x>y)-(x<y)
            a = list(base)
            t0=time.perf_counter(); sorted(a, key=functools.cmp_to_key(cmpf)); dt=time.perf_counter()-t0
            rows.append(dict(n=n, kind=kind, algo='timsort_cmpkey', time_s=round(dt,4),
                             comparisons=c[0], nlogn=round(dt/(n*math.log2(n)),8)))
            print(f'n={n} {kind:8s} timsort_cmpkey   t={dt:7.3f}s cmp={c[0]}', flush=True)
    with open(f'{DATA}/exp1_sorting.csv','w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print('wrote', f'{DATA}/exp1_sorting.csv', len(rows), 'rows')

main()

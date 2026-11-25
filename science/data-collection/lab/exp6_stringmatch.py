#!/usr/bin/env python3
"""Experiment 6: Naive vs KMP vs Python 'in' - worst-case a^n b, char-comparison counts."""
import time, csv, os, random
random.seed(5)
DATA='/home/neilh/science_lab/cs/data'

def naive_count(text, pat):
    """returns (found, char comparisons)"""
    n,m=len(text),len(pat); cmp=0
    for i in range(n-m+1):
        j=0
        while j<m:
            cmp+=1
            if text[i+j]!=pat[j]: break
            j+=1
        if j==m: return True, cmp
    return False, cmp

def kmp_count(text, pat):
    n,m=len(text),len(pat); cmp=0
    # build lps
    lps=[0]*m; k=0
    for i in range(1,m):
        cmp+=1  # count table-build comparisons too
        while k>0 and pat[i]!=pat[k]: k=lps[k-1]; cmp+=1
        if pat[i]==pat[k]: k+=1
        lps[i]=k
    i=j=0
    while i<n:
        cmp+=1
        if text[i]==pat[j]:
            i+=1; j+=1
            if j==m: return True, cmp
        elif j>0: j=lps[j-1]
        else: i+=1
    return False, cmp

def main():
    rows=[]
    # --- worst case: 'a'*n + 'b' pattern 'a'*k+'b' ---
    for n,k in [(1000,10),(5000,10),(20000,10),(20000,50),(50000,10)]:
        text='a'*n+'b'; pat='a'*k+'b'
        for name,fn in [('naive',naive_count),('kmp',kmp_count)]:
            t0=time.perf_counter(); found,cmp=fn(text,pat); dt=time.perf_counter()-t0
            assert found
            rows.append(dict(test='worstcase', n=n, k=k, algo=name, time_s=round(dt,4), comparisons=cmp))
            print(f'n={n} k={k} {name}: t={dt:.4f}s cmp={cmp}', flush=True)
        t0=time.perf_counter(); found = pat in text; dt=time.perf_counter()-t0
        rows.append(dict(test='worstcase', n=n, k=k, algo='python_in', time_s=round(dt,6), comparisons='?'))
        print(f'n={n} k={k} python_in: t={dt:.6f}s found={found}', flush=True)

    # --- no-match random: 'a'*n + 'b' vs pat 'a'*k+'c' (fails at last char) ---
    for n,k in [(10000,20),(50000,20)]:
        text='a'*n+'b'; pat='a'*k+'c'
        for name,fn in [('naive',naive_count),('kmp',kmp_count)]:
            t0=time.perf_counter(); found,cmp=fn(text,pat); dt=time.perf_counter()-t0
            assert not found
            rows.append(dict(test='nomatch', n=n, k=k, algo=name, time_s=round(dt,4), comparisons=cmp))
            print(f'nomatch n={n} k={k} {name}: t={dt:.4f}s cmp={cmp}', flush=True)
        t0=time.perf_counter(); found = pat in text; dt=time.perf_counter()-t0
        rows.append(dict(test='nomatch', n=n, k=k, algo='python_in', time_s=round(dt,6), comparisons='?'))
        print(f'nomatch n={n} k={k} python_in: t={dt:.6f}s found={found}', flush=True)

    # --- random strings: all three ---
    for n,m in [(20000,10),(100000,10),(100000,50)]:
        text=''.join(random.choice('abcd') for _ in range(n))
        pat=''.join(random.choice('abcd') for _ in range(m))
        for name,fn in [('naive',naive_count),('kmp',kmp_count)]:
            t0=time.perf_counter(); found,cmp=fn(text,pat); dt=time.perf_counter()-t0
            rows.append(dict(test='random', n=n, k=m, algo=name, time_s=round(dt,4), comparisons=cmp))
            print(f'rand n={n} m={m} {name}: t={dt:.4f}s cmp={cmp}', flush=True)
        t0=time.perf_counter(); found = pat in text; dt=time.perf_counter()-t0
        rows.append(dict(test='random', n=n, k=m, algo='python_in', time_s=round(dt,6), comparisons='?'))
        print(f'rand n={n} m={m} python_in: t={dt:.6f}s found={found}', flush=True)

    # --- early-exit pattern found in middle ---
    for n in [100000]:
        text='x'*50000 + 'hello world' + 'y'*50000
        pat='hello world'
        for name,fn in [('naive',naive_count),('kmp',kmp_count)]:
            t0=time.perf_counter(); found,cmp=fn(text,pat); dt=time.perf_counter()-t0
            rows.append(dict(test='earlyfound', n=n, k=len(pat), algo=name, time_s=round(dt,4), comparisons=cmp))
            print(f'early n={n} {name}: t={dt:.4f}s cmp={cmp}', flush=True)

    with open(f'{DATA}/exp6_string.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['test','n','k','algo','time_s','comparisons'])
        w.writeheader(); w.writerows(rows)
    print('wrote exp6_string.csv', flush=True)

main()

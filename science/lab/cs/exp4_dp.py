#!/usr/bin/env python3
"""Experiment 4: Dynamic programming - coin change, LCS, knapsack.
Verify vs brute force on small inputs; measure state-space growth."""
import random, time, csv, os, itertools, math
random.seed(3)
DATA='/home/neilh/science_lab/cs/data'

# ---------- Coin change ----------
def coin_change_min(coins, amount):
    """min coins to make amount; INF if impossible. O(amount*len(coins)) states."""
    INF=float('inf'); dp=[INF]*(amount+1); dp[0]=0
    states=0
    for a in range(1,amount+1):
        for c in coins:
            states+=1
            if a>=c and dp[a-c]+1<dp[a]: dp[a]=dp[a-c]+1
    return dp[amount], states

def coin_change_brute(coins, amount):
    # BFS over amounts = Dijkstra-unweighted; exponential worst case, fine for small
    from collections import deque
    seen={0:0}; q=deque([0])
    while q:
        a=q.popleft()
        if a==amount: return seen[a]
        for c in coins:
            na=a+c
            if na<=amount and na not in seen:
                seen[na]=seen[a]+1; q.append(na)
    return None

def coin_change_count(coins, amount):
    """number of ways (order-independent via index loop)."""
    dp=[0]*(amount+1); dp[0]=1
    for c in coins:
        for a in range(c,amount+1): dp[a]+=dp[a-c]
    return dp[amount]

# ---------- LCS ----------
def lcs(s1, s2):
    m,n=len(s1),len(s2)
    dp=[[0]*(n+1) for _ in range(m+1)]
    for i in range(1,m+1):
        for j in range(1,n+1):
            if s1[i-1]==s2[j-1]: dp[i][j]=dp[i-1][j-1]+1
            else: dp[i][j]=max(dp[i-1][j],dp[i][j-1])
    return dp[m][n], (m+1)*(n+1)

def lcs_brute(s1,s2):
    # exponential: try all ways to delete chars
    best=0
    def rec(i,j,l):
        nonlocal best
        if l+min(len(s1)-i,len(s2)-j)<=best: return
        if i==len(s1) or j==len(s2): best=max(best,l); return
        if s1[i]==s2[j]: rec(i+1,j+1,l+1)
        rec(i+1,j,l); rec(i,j+1,l)
    rec(0,0,0); return best

# ---------- 0/1 Knapsack ----------
def knapsack(w, v, cap):
    n=len(w); dp=[0]*(cap+1)
    for i in range(n):
        for c in range(cap, w[i]-1, -1):
            dp[c]=max(dp[c], dp[c-w[i]]+v[i])
    return dp[cap]

def knapsack_brute(w,v,cap):
    best=0
    for mask in range(1<<len(w)):
        tw=tv=0
        for i in range(len(w)):
            if mask>>i & 1: tw+=w[i]; tv+=v[i]
        if tw<=cap: best=max(best,tv)
    return best

def main():
    rows=[]
    # --- verify coin change vs BFS brute force ---
    ok=True
    for _ in range(30):
        coins=random.sample(range(1,20), random.randint(2,4))
        amt=random.randint(1,60)
        dp_val,_=coin_change_min(coins,amt)
        bf=coin_change_brute(coins,amt)
        bf = -1 if bf is None else bf
        if dp_val==float('inf'): dp_val=-1
        if dp_val!=bf: ok=False; print('MISMATCH coin',coins,amt,dp_val,bf)
    rows.append(dict(test='coin_change_verify', result='PASS' if ok else 'FAIL', detail='30 random small cases vs BFS brute force'))
    print('coin verify', ok, flush=True)

    # --- verify LCS vs brute ---
    ok=True
    alpha='ab'
    for _ in range(15):
        s1=''.join(random.choice(alpha) for _ in range(random.randint(4,9)))
        s2=''.join(random.choice(alpha) for _ in range(random.randint(4,9)))
        dpv,_=lcs(s1,s2); bf=lcs_brute(s1,s2)
        if dpv!=bf: ok=False; print('MISMATCH lcs',s1,s2,dpv,bf)
    rows.append(dict(test='lcs_verify', result='PASS' if ok else 'FAIL', detail='15 random small cases vs exponential brute force'))
    print('lcs verify', ok, flush=True)

    # --- verify knapsack vs brute ---
    ok=True
    for _ in range(15):
        n=random.randint(3,8)
        w=[random.randint(1,10) for _ in range(n)]
        v=[random.randint(1,20) for _ in range(n)]
        cap=random.randint(10,30)
        if knapsack(w,v,cap)!=knapsack_brute(w,v,cap): ok=False; print('MISMATCH ks')
    rows.append(dict(test='knapsack_verify', result='PASS' if ok else 'FAIL', detail='15 random small cases vs 2^n brute force'))
    print('knapsack verify', ok, flush=True)

    # --- state-space growth: coin change ---
    for amt in [100,500,1000,5000,10000,20000,50000]:
        coins=[1,5,10,25]
        t0=time.perf_counter(); val,st=coin_change_min(coins,amt); dt=time.perf_counter()-t0
        rows.append(dict(test='coin_states', n=amt, time_s=round(dt,4), states=st, answer=val))
        print(f'coin amt={amt} states={st} t={dt:.3f}s ans={val}', flush=True)

    # --- LCS state growth: random strings ---
    for n in [100,200,400,800,1600]:
        s1=''.join(random.choice('ACGT') for _ in range(n))
        s2=''.join(random.choice('ACGT') for _ in range(n))
        t0=time.perf_counter(); val,st=lcs(s1,s2); dt=time.perf_counter()-t0
        rows.append(dict(test='lcs_states', n=n, time_s=round(dt,4), states=st, answer=val))
        print(f'lcs n={n} states={st} t={dt:.3f}s lcs={val}', flush=True)

    # --- knapsack state growth ---
    for n in [100,200,400,800]:
        w=[random.randint(1,20) for _ in range(n)]; v=[random.randint(1,50) for _ in range(n)]
        cap=sum(w)//2
        t0=time.perf_counter(); val=knapsack(w,v,cap); dt=time.perf_counter()-t0
        rows.append(dict(test='knap_states', n=n, time_s=round(dt,4), states=n*cap, answer=val))
        print(f'knap n={n} cap={cap} states~{n*cap} t={dt:.3f}s val={val}', flush=True)

    # coin count ways (unbounded) growth check
    for amt in [1000,5000,10000,20000,50000]:
        t0=time.perf_counter(); c=coin_change_count([1,5,10,25],amt); dt=time.perf_counter()-t0
        rows.append(dict(test='coin_ways', n=amt, time_s=round(dt,4), states=amt, answer=c))
        print(f'coin ways amt={amt} t={dt:.3f}s ways={c}', flush=True)

    with open(f'{DATA}/exp4_dp.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['test','n','time_s','states','answer','result','detail'], extrasaction='ignore')
        w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in ['test','n','time_s','states','answer','result','detail']})
    print('wrote exp4_dp.csv', flush=True)

main()

#!/usr/bin/env python3
"""Experiment 5: Graph traversal - BFS/DFS/Dijkstra, Kahn topo sort + cycle detect,
Dijkstra wrong answer on negative edges."""
import random, time, csv, os, heapq, sys
sys.setrecursionlimit(300000)
from collections import deque, defaultdict
random.seed(9)
DATA='/home/neilh/science_lab/cs/data'

# ---------- BFS / DFS on grid and random graph ----------
def grid_graph(W,H):
    adj=defaultdict(list)
    for y in range(H):
        for x in range(W):
            u=y*W+x
            for dx,dy in ((1,0),(0,1)):
                nx,ny=x+dx,y+dy
                if nx<W and ny<H: adj[u].append(ny*W+nx); adj[ny*W+nx].append(u)
    return adj, W*H

def rand_graph(n,p=0.01):
    adj=defaultdict(list)
    for u in range(n):
        for v in range(u+1,n):
            if random.random()<p: adj[u].append(v); adj[v].append(u)
    return adj,n

def bfs(adj,s,n):
    seen=[False]*n; seen[s]=True; q=deque([s]); order=[]
    while q:
        u=q.popleft(); order.append(u)
        for v in adj[u]:
            if not seen[v]: seen[v]=True; q.append(v)
    return order

def dfs(adj,s,n):
    # iterative DFS to avoid recursion limits on deep graphs
    seen=[False]*n; order=[]; stack=[(s,iter(adj[s]))]
    seen[s]=True; order.append(s)
    while stack:
        u,it=stack[-1]
        advanced=False
        for v in it:
            if not seen[v]:
                seen[v]=True; order.append(v); stack.append((v,iter(adj[v]))); advanced=True; break
        if not advanced: stack.pop()
    return order

def dijkstra(adj,s,n):
    """adj: dict u -> list of (v,w). Standard textbook version with a
    settled-set: once a node is popped it is final (INVALID for w<0)."""
    dist=[float('inf')]*n; dist[s]=0
    done=[False]*n
    pq=[(0,s)]
    while pq:
        d,u=heapq.heappop(pq)
        if done[u]: continue
        done[u]=True
        for v,w in adj[u]:
            if done[v]: continue          # <-- the assumption that breaks on negatives
            nd=d+w
            if nd<dist[v]: dist[v]=nd; heapq.heappush(pq,(nd,v))
    return dist

# ---------- Kahn topological sort + cycle detection ----------
def kahn(adj,n):
    indeg=[0]*n
    for u in adj:
        for v in adj[u]: indeg[v]+=1
    q=deque([u for u in range(n) if indeg[u]==0])
    order=[]
    while q:
        u=q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v]-=1
            if indeg[v]==0: q.append(v)
    return order, len(order)==n  # sorted, acyclic?

def make_dag(n,p=0.02):
    """random DAG: edges only u->v with u<v"""
    adj=defaultdict(list)
    for u in range(n):
        for v in range(u+1,n):
            if random.random()<p: adj[u].append(v)
    return adj,n

def add_cycle(adj,n):
    """add edge n-1 -> 0 (back edge) creating a cycle if path 0->...->n-1 exists"""
    adj=defaultdict(list,{k:list(v) for k,v in adj.items()})
    adj[n-1].append(0)
    return adj

def main():
    rows=[]
    # --- BFS vs DFS timing on grid + random ---
    for W,H in [(50,50),(100,100),(200,200)]:
        adj,n=grid_graph(W,H)
        for name,fn in [('bfs',bfs),('dfs',dfs)]:
            t0=time.perf_counter(); o=fn(adj,0,n); dt=time.perf_counter()-t0
            assert len(o)==n
            rows.append(dict(test='traversal', input=f'grid{W}x{H}', algo=name, n=n, time_s=round(dt,5)))
            print(f'grid {W}x{H} {name}: t={dt:.4f}s visited={len(o)}', flush=True)
    for n in [1000,5000,20000]:
        adj,_=rand_graph(n,0.005)
        for name,fn in [('bfs',bfs),('dfs',dfs)]:
            t0=time.perf_counter(); o=fn(adj,0,n); dt=time.perf_counter()-t0
            rows.append(dict(test='traversal', input=f'rand{n}', algo=name, n=n, time_s=round(dt,5), visited=len(o)))
            print(f'rand n={n} {name}: t={dt:.4f}s visited={len(o)}', flush=True)

    # --- Dijkstra correctness + timing ---
    # weighted random graph
    for n,p in [(500,0.02),(2000,0.01),(5000,0.005)]:
        adj=defaultdict(list)
        for u in range(n):
            for v in range(u+1,n):
                if random.random()<p:
                    w=random.randint(1,100)
                    adj[u].append((v,w)); adj[v].append((u,w))
        t0=time.perf_counter(); dist=dijkstra(adj,0,n); dt=time.perf_counter()-t0
        rows.append(dict(test='dijkstra', input=f'rand{n}', algo='dijkstra', n=n, time_s=round(dt,4), answer=dist[n-1] if dist[n-1]<float('inf') else 'unreach'))
        print(f'dijkstra rand n={n}: t={dt:.4f}s dist_last={dist[n-1]}', flush=True)
    # grid weighted
    W=H=100
    adj=defaultdict(list); n=W*H
    for y in range(H):
        for x in range(W):
            u=y*W+x
            for dx,dy in ((1,0),(0,1)):
                nx,ny=x+dx,y+dy
                if nx<W and ny<H:
                    v=ny*W+nx; w=random.randint(1,20)
                    adj[u].append((v,w)); adj[v].append((u,w))
    t0=time.perf_counter(); dist=dijkstra(adj,0,n); dt=time.perf_counter()-t0
    print(f'dijkstra grid100: t={dt:.4f}s dist={dist[n-1]}', flush=True)
    rows.append(dict(test='dijkstra', input='grid100', algo='dijkstra', n=n, time_s=round(dt,4), answer=dist[n-1]))

    # --- Kahn topo sort: DAG vs cyclic ---
    for n,p in [(100,0.05),(500,0.02),(1000,0.01)]:
        adj,_=make_dag(n,p)
        t0=time.perf_counter(); order,acyc=kahn(adj,n); dt=time.perf_counter()-t0
        assert acyc and len(order)==n
        # sanity: every edge u->v has pos(u)<pos(v)
        pos={u:i for i,u in enumerate(order)}
        assert all(pos[u]<pos[v] for u in adj for v in adj[u])
        rows.append(dict(test='kahn', input=f'dag{n}', n=n, time_s=round(dt,5), answer=f'acyclic order={len(order)}'))
        print(f'kahn DAG n={n}: t={dt:.5f}s order={len(order)}', flush=True)
        adjc=add_cycle(adj,n)
        t0=time.perf_counter(); order2,acyc2=kahn(adjc,n); dt=time.perf_counter()-t0
        assert not acyc2 and len(order2)<n
        rows.append(dict(test='kahn_cycle', input=f'cyclic{n}', n=n, time_s=round(dt,5), answer=f'cycle detected, {len(order2)}/{n} sorted'))
        print(f'kahn cyclic n={n}: t={dt:.5f}s sorted={len(order2)}/{n} -> cycle', flush=True)

    # --- Dijkstra on negative edges: wrong answer demo ---
    # classic: 0->1 weight 5, 0->2 weight 1, 2->1 weight -3 => true shortest 0->2->1 = -2
    # 0->1(1), 1->2(1), 0->3(5), 3->1(-10): node 1 is finalized before the
    # negative edge 3->1 is discovered, so 1->2 is never re-relaxed.
    adj_neg=defaultdict(list)
    adj_neg[0]=[(1,1),(3,5)]; adj_neg[1]=[(2,1)]; adj_neg[2]=[]; adj_neg[3]=[(1,-10)]
    dist=dijkstra(adj_neg,0,4)
    true_shortest=-4  # 0->3->1->2 = 5-10+1
    print(f'Dijkstra negative-edge demo: got dist[2]={dist[2]}, true shortest={true_shortest} -> {"WRONG" if dist[2]!=true_shortest else "ok"}', flush=True)
    rows.append(dict(test='dijkstra_negative', input='neg_edges', n=4, time_s=0, answer=f'dijkstra={dist[2]} true={true_shortest}'))
    # Bellman-Ford for contrast
    n=4; d=[float('inf')]*n; d[0]=0
    edges=[(0,1,1),(1,2,1),(0,3,5),(3,1,-10)]
    for _ in range(n-1):
        for u,v,w in edges:
            if d[u]+w<d[v]: d[v]=d[u]+w
    print(f'Bellman-Ford same graph: dist[1]={d[1]} (correct)', flush=True)
    rows.append(dict(test='bellman_ford', input='neg_edges', n=3, time_s=0, answer=f'dist1={d[1]}'))

    with open(f'{DATA}/exp5_graph.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['test','input','algo','n','time_s','visited','answer'], extrasaction='ignore')
        w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in ['test','input','algo','n','time_s','visited','answer']})
    print('wrote exp5_graph.csv', flush=True)

main()

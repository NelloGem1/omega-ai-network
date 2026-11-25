#!/usr/bin/env python3
"""Independent verification: Dijkstra fails on negative edges.
Counterexample from cs/exp5_graph.py + REPORT.md.
Graph: 0->1(1), 1->2(1), 0->3(5), 3->1(-10). True shortest 0->3->1->2 = -4."""
import heapq

adj = {0:[(1,1),(3,5)], 1:[(2,1)], 2:[], 3:[(1,-10)]}
N = 4

def dijkstra_settled(adj, s, n):
    """Textbook settled-set version (the one that breaks)."""
    dist=[float('inf')]*n; dist[s]=0; done=[False]*n; pq=[(0,s)]
    while pq:
        d,u=heapq.heappop(pq)
        if done[u]: continue
        done[u]=True
        for v,w in adj[u]:
            if done[v]: continue
            nd=d+w
            if nd<dist[v]: dist[v]=nd; heapq.heappush(pq,(nd,v))
    return dist

def dijkstra_no_settle(adj, s, n):
    """Label-correcting variant (re-push allowed) — accidentally correct."""
    dist=[float('inf')]*n; dist[s]=0; pq=[(0,s)]
    while pq:
        d,u=heapq.heappop(pq)
        if d>dist[u]: continue
        for v,w in adj[u]:
            nd=d+w
            if nd<dist[v]: dist[v]=nd; heapq.heappush(pq,(nd,v))
    return dist

def bellman_ford(adj, s, n):
    edges=[(u,v,w) for u in adj for v,w in adj[u]]
    d=[float('inf')]*n; d[s]=0
    for _ in range(n-1):
        for u,v,w in edges:
            if d[u]!=float('inf') and d[u]+w<d[v]: d[v]=d[u]+w
    return d

d1 = dijkstra_settled(adj,0,N)
d2 = dijkstra_no_settle(adj,0,N)
d3 = bellman_ford(adj,0,N)
print(f"settled-set Dijkstra  dist[2] = {d1[2]}   (REPORT claims 2)")
print(f"no-settle Dijkstra    dist[2] = {d2[2]}")
print(f"Bellman-Ford          dist[2] = {d3[2]}   (true = -4)")
assert d1[2]==2,  "settled-set should give WRONG answer 2"
assert d3[2]==-4, "Bellman-Ford should give TRUE answer -4"
print("VERIFIED-EXPERIMENT: Dijkstra settled-set FAILS on negative edges "
      "(2 vs true -4); Bellman-Ford correct. Matches REPORT.md + exp5_graph.csv.")

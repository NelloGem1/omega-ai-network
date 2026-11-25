#!/usr/bin/env python3
"""Exp4: Graph algorithms — Dijkstra, Bellman-Ford, union-find.
Verify equal on positive weights; BREAK Dijkstra with negative weights;
measure scaling vs n."""
import json, random, heapq, time

OUT = "/home/neilh/science_lab/math/exp4_data.json"
random.seed(7)
INF = float("inf")

def dijkstra(n, adj, src=0):
    dist = [INF]*n; dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

def bellman_ford(n, edges, src=0):
    dist = [INF]*n; dist[src] = 0
    for _ in range(n-1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; changed = True
        if not changed: break
    # negative cycle check
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None  # negative cycle reachable
    return dist

def rand_graph(n, m, wmin=1, wmax=20, allow_neg=False):
    adj = [[] for _ in range(n)]
    edges = []
    for _ in range(m):
        u = random.randrange(n); v = random.randrange(n)
        if u == v: continue
        w = random.randint(wmin, wmax)
        if allow_neg and random.random() < 0.3:
            w = -random.randint(1, 10)
        adj[u].append((v, w)); edges.append((u, v, w))
    return adj, edges

# ---- correctness on positive weights ----
agree = 0; disagree = 0
for trial in range(200):
    n = random.randint(5, 30); m = random.randint(n, 4*n)
    adj, edges = rand_graph(n, m)
    d1 = dijkstra(n, adj)
    d2 = bellman_ford(n, edges)
    if d2 is None: continue
    if d1 == d2: agree += 1
    else: disagree += 1
print(f"Positive weights: agree={agree} disagree={disagree}", flush=True)

# ---- BREAK Dijkstra with negative weights ----
# classic: 0->1 (5), 0->2 (1), 2->1 (-3). True shortest 0->2->1 = -2; Dijkstra gives 5.
adj = [[] for _ in range(3)]
edges = [(0,1,5),(0,2,1),(2,1,-3)]
adj[0].append((1,5)); adj[0].append((2,1)); adj[2].append((1,-3))
d_dij = dijkstra(3, adj)
d_bf = bellman_ford(3, edges)
print(f"Negative-weight graph: dijkstra={d_dij} bellman_ford={d_bf}", flush=True)
broken = d_dij != d_bf

# random negative graphs: how often does Dijkstra disagree?
neg_disagree = 0; neg_agree = 0; neg_cycles = 0
for trial in range(500):
    n = random.randint(5, 15); m = random.randint(n, 3*n)
    adj, edges = rand_graph(n, m, wmin=-10, wmax=20, allow_neg=True)
    d1 = dijkstra(n, adj); d2 = bellman_ford(n, edges)
    if d2 is None:
        neg_cycles += 1; continue
    if d1 == d2: neg_agree += 1
    else: neg_disagree += 1
print(f"Negative weights: agree={neg_agree} disagree={neg_disagree} negcycles={neg_cycles}", flush=True)

# ---- union-find ----
class UF:
    def __init__(self, n): self.p = list(range(n)); self.r = [0]*n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        if self.r[ra] < self.r[rb]: ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]: self.r[ra] += 1
        return True

# ---- scaling ----
scaling = []
for n in [100, 200, 400, 800, 1600, 3200]:
    m = 4*n
    adj, edges = rand_graph(n, m)
    # time dijkstra (heap)
    t0 = time.time(); dijkstra(n, adj); td = time.time()-t0
    # time bellman-ford
    t0 = time.time(); bellman_ford(n, edges); tb = time.time()-t0
    # time union-find on same edges (undirected)
    uf = UF(n)
    t0 = time.time()
    for u, v, w in edges:
        uf.union(u, v)
    tuf = time.time()-t0
    scaling.append({"n": n, "m": m, "dijkstra_s": td, "bellman_ford_s": tb, "unionfind_s": tuf})
    print(f"n={n}: dij={td*1e3:.2f}ms bf={tb*1e3:.2f}ms uf={tuf*1e3:.2f}ms", flush=True)

json.dump({"correctness": {"agree": agree, "disagree": disagree},
           "negative_break": {"dijkstra": d_dij, "bellman_ford": d_bf, "broken": broken},
           "negative_random": {"agree": neg_agree, "disagree": neg_disagree, "cycles": neg_cycles},
           "scaling": scaling}, open(OUT, "w"), indent=1)
print("Wrote", OUT)

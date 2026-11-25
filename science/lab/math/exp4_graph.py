#!/usr/bin/env python3
"""Exp4 v2: Graph algorithms — textbook Dijkstra (settled set), Bellman-Ford,
union-find. Verify equal on positive weights; BREAK Dijkstra with negative
weights; measure scaling vs n (capped)."""
import json, random, heapq, time, sys

OUT = "/home/neilh/science_lab/math/exp4_data.json"
random.seed(7)
INF = float("inf")

def dijkstra(n, adj, src=0):
    """Textbook Dijkstra: each node settled once (breaks on negative weights)."""
    dist = [INF]*n; dist[src] = 0
    settled = [False]*n
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if settled[u]: continue
        settled[u] = True
        for v, w in adj[u]:
            if not settled[v] and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist

def bellman_ford(n, edges, src=0):
    dist = [INF]*n; dist[src] = 0
    for _ in range(n-1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; changed = True
        if not changed: break
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None
    return dist

def rand_graph(n, m, wmin=1, wmax=20, allow_neg=False):
    adj = [[] for _ in range(n)]
    edges = []
    tries = 0
    while len(edges) < m and tries < m*10:
        tries += 1
        u = random.randrange(n); v = random.randrange(n)
        if u == v: continue
        w = random.randint(wmin, wmax)
        if allow_neg and random.random() < 0.3:
            w = -random.randint(1, 10)
        adj[u].append((v, w)); edges.append((u, v, w))
    return adj, edges

agree = disagree = 0
for trial in range(300):
    n = random.randint(5, 30); m = random.randint(n, 4*n)
    adj, edges = rand_graph(n, m)
    d1 = dijkstra(n, adj); d2 = bellman_ford(n, edges)
    if d2 is None: continue
    if d1 == d2: agree += 1
    else: disagree += 1
print(f"Positive: agree={agree} disagree={disagree}", flush=True)

# canonical break: 0->1(1), 0->2(5), 2->1(-10): true dist[1] = -5
adj = [[(1,1)], [(2,5)], [(1,-10)]]
edges = [(0,1,1),(0,2,5),(2,1,-10)]
d_dij = dijkstra(3, adj); d_bf = bellman_ford(3, edges)
print(f"Break graph: dijkstra={d_dij} bf={d_bf}", flush=True)
broken = (d_dij != d_bf)

neg_agree = neg_disagree = neg_cycles = 0
examples = []
for trial in range(300):
    n = random.randint(5, 15); m = random.randint(n, 3*n)
    adj, edges = rand_graph(n, m, wmin=-10, wmax=20, allow_neg=True)
    d1 = dijkstra(n, adj); d2 = bellman_ford(n, edges)
    if d2 is None:
        neg_cycles += 1; continue
    if d1 == d2: neg_agree += 1
    else:
        neg_disagree += 1
        if len(examples) < 3:
            examples.append({"n": n, "dij": d1, "bf": d2})
print(f"Negative random: agree={neg_agree} disagree={neg_disagree} cycles={neg_cycles}", flush=True)

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

# sanity: union-find components
uf = UF(6)
for a,b in [(0,1),(1,2),(3,4)]: uf.union(a,b)
uf_ok = (uf.find(0)==uf.find(2)) and (uf.find(0)!=uf.find(3)) and (uf.find(4)==uf.find(3))
print("UF sanity:", uf_ok, flush=True)

scaling = []
for n in [100, 200, 400, 800, 1600]:
    m = 4*n
    adj, edges = rand_graph(n, m)
    t0 = time.time(); dijkstra(n, adj); td = time.time()-t0
    t0 = time.time(); bellman_ford(n, edges); tb = time.time()-t0
    uf = UF(n); t0 = time.time()
    for u, v, w in edges: uf.union(u, v)
    tuf = time.time()-t0
    scaling.append({"n": n, "m": m, "dijkstra_s": td, "bellman_ford_s": tb, "unionfind_s": tuf})
    print(f"n={n}: dij={td*1e3:.2f}ms bf={tb*1e3:.2f}ms uf={tuf*1e3:.2f}ms", flush=True)

json.dump({"correctness": {"agree": agree, "disagree": disagree},
           "negative_break": {"dijkstra": d_dij, "bellman_ford": d_bf, "broken": broken},
           "negative_random": {"agree": neg_agree, "disagree": neg_disagree,
                                "cycles": neg_cycles, "examples": examples},
           "unionfind_sanity": uf_ok, "scaling": scaling},
          open(OUT, "w"), indent=1)
print("Wrote", OUT)

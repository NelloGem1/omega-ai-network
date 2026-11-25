#!/usr/bin/env python3
"""Experiment 2 FIXED: Unbalanced BST vs AVL - degenerate height on sorted input.
Fixes vs exp2_bst.py:
 1. AVL rebalance now compares the inserted KEY against child keys to pick
    LL/LR/RL/RR (was: height comparison + rotating the child first, which is
    not valid AVL and can corrupt the tree).
 2. bench() now verifies BST ordering + AVL balance invariants after insert
    (was: no correctness oracle at all).
 3. find queries are a uniform random sample of seq (was: seq[::step], which
    for sorted input queried only the smallest keys -> biased find benchmark).
"""
import sys, time, random, csv, os
sys.setrecursionlimit(1_000_000)
random.seed(7)
DATA = '/home/neilh/science_lab/cs/data'

class Node:
    __slots__ = ('key','left','right','height')
    def __init__(self, k):
        self.key=k; self.left=None; self.right=None; self.height=1

class BST:
    def __init__(self): self.root=None; self.cmp=0
    def insert(self, k):
        self.root = self._ins(self.root, k)
    def _ins(self, n, k):
        if n is None: return Node(k)
        self.cmp += 1
        if k < n.key: n.left = self._ins(n.left, k)
        elif k > n.key: n.right = self._ins(n.right, k)
        return n
    def height(self):
        def h(n): return 0 if n is None else 1+max(h(n.left), h(n.right))
        return h(self.root)
    def find(self, k):
        n = self.root; steps=0
        while n:
            steps+=1; self.cmp+=1
            if k==n.key: return steps
            n = n.left if k<n.key else n.right
        return -steps
    def inorder(self):
        out=[]
        def w(n):
            if n is None: return
            w(n.left); out.append(n.key); w(n.right)
        w(self.root); return out
    def check_bst(self):
        vals = self.inorder()
        return vals == sorted(vals) and len(set(vals)) == len(vals)

def check_avl(n):
    """Return (ok, height); verifies BST order + |balance|<=1 + correct heights."""
    if n is None: return True, 0
    lok, lh = check_avl(n.left)
    rok, rh = check_avl(n.right)
    if not (lok and rok): return False, 0
    if n.left and n.left.key >= n.key: return False, 0
    if n.right and n.right.key <= n.key: return False, 0
    if abs(lh - rh) > 1: return False, 0
    if n.height != 1 + max(lh, rh): return False, 0
    return True, n.height

class AVL(BST):
    def _ins(self, n, k):
        if n is None: return Node(k)
        self.cmp += 1
        if k < n.key: n.left = self._ins(n.left, k)
        elif k > n.key: n.right = self._ins(n.right, k)
        else: return n
        n.height = 1 + max(self._h(n.left), self._h(n.right))
        bal = self._h(n.left) - self._h(n.right)
        # FIX: standard AVL — choose rotation by KEY comparison, single/double
        # rotation applied at the correct node.
        if bal > 1:
            if k < n.left.key:
                return self._rotR(n)          # LL
            n.left = self._rotL(n.left)       # LR
            return self._rotR(n)
        if bal < -1:
            if k > n.right.key:
                return self._rotL(n)          # RR
            n.right = self._rotR(n.right)     # RL
            return self._rotL(n)
        return n
    @staticmethod
    def _h(n): return 0 if n is None else n.height
    @staticmethod
    def _rotL(n):
        r=n.right; n.right=r.left; r.left=n
        n.height=1+max(AVL._h(n.left),AVL._h(n.right))
        r.height=1+max(AVL._h(r.left),AVL._h(r.right))
        return r
    @staticmethod
    def _rotR(n):
        l=n.left; n.left=l.right; l.right=n
        n.height=1+max(AVL._h(n.left),AVL._h(n.right))
        l.height=1+max(AVL._h(l.left),AVL._h(l.right))
        return l
    def check(self):
        return check_avl(self.root)[0]

def bench(cls, seq, queries):
    t = cls(); t0=time.perf_counter()
    for k in seq: t.insert(k)
    tins = time.perf_counter()-t0
    # correctness oracle (was missing entirely)
    if cls is AVL:
        ok = t.check()
    else:
        ok = t.check_bst()
    assert ok, f'{cls.__name__} failed structural verification on n={len(seq)}'
    t0=time.perf_counter(); hits=0; tot=0
    for q in queries:
        s = t.find(q); tot+=abs(s); hits += (s>0)
    tfind = time.perf_counter()-t0
    return dict(height=t.height(), insert_s=round(tins,4), find_s=round(tfind,4),
                avg_find_steps=round(tot/len(queries),1), hits=hits, ncomp=t.cmp,
                verified=True)

def main():
    rows=[]
    for n in [1000, 5000, 10000, 20000]:
        for kind in ['sorted','reverse','random']:
            if kind=='sorted': seq=list(range(n))
            elif kind=='reverse': seq=list(range(n,0,-1))
            else: seq=random.sample(range(n*10), n)
            # FIX: uniform-random query sample instead of biased seq[::step]
            queries = random.sample(seq, min(500, len(seq)))
            for clsname, cls in [('BST',BST),('AVL',AVL)]:
                r = bench(cls, seq, queries)
                rows.append(dict(n=n, input=kind, tree=clsname, **r))
                print(f'n={n} {kind:7s} {clsname}: h={r["height"]} tins={r["insert_s"]:.3f}s tfind={r["find_s"]:.4f}s avgsteps={r["avg_find_steps"]} verified={r["verified"]}', flush=True)
    with open(f'{DATA}/exp2_bst_fixed.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print('wrote exp2_bst_fixed.csv')

main()

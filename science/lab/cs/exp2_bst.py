#!/usr/bin/env python3
"""Experiment 2: Unbalanced BST vs AVL - degenerate height on sorted input."""
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

class AVL(BST):
    def _ins(self, n, k):
        if n is None: return Node(k)
        self.cmp += 1
        if k < n.key: n.left = self._ins(n.left, k)
        elif k > n.key: n.right = self._ins(n.right, k)
        else: return n
        n.height = 1 + max(self._h(n.left), self._h(n.right))
        bal = self._h(n.left) - self._h(n.right)
        if bal > 1:
            if self._h(n.left.left) >= self._h(n.left.right): n.left = self._rotR(n.left)
            else: n.left = self._rotL(n.left)
            return self._rotR(n)
        if bal < -1:
            if self._h(n.right.right) >= self._h(n.right.left): n.right = self._rotL(n.right)
            else: n.right = self._rotR(n.right)
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
    def _rot(self,n):
        bal = self._h(n.left)-self._h(n.right)
        if bal>1: return self._rotR(n)
        if bal<-1: return self._rotL(n)
        return n

def bench(cls, seq, queries):
    t = cls(); t0=time.perf_counter()
    for k in seq: t.insert(k)
    tins = time.perf_counter()-t0
    t0=time.perf_counter(); hits=0; tot=0
    for q in queries:
        s = t.find(q); tot+=abs(s); hits += (s>0)
    tfind = time.perf_counter()-t0
    return dict(height=t.height(), insert_s=round(tins,4), find_s=round(tfind,4),
                avg_find_steps=round(tot/len(queries),1), hits=hits, ncomp=t.cmp)

def main():
    rows=[]
    for n in [1000, 5000, 10000, 20000]:
        for kind in ['sorted','reverse','random']:
            if kind=='sorted': seq=list(range(n))
            elif kind=='reverse': seq=list(range(n,0,-1))
            else: seq=random.sample(range(n*10), n)
            queries = seq[::max(1,n//500)][:500]
            for clsname, cls in [('BST',BST),('AVL',AVL)]:
                r = bench(cls, seq, queries)
                rows.append(dict(n=n, input=kind, tree=clsname, **r))
                print(f'n={n} {kind:7s} {clsname}: h={r["height"]} tins={r["insert_s"]:.3f}s tfind={r["find_s"]:.4f}s avgsteps={r["avg_find_steps"]}', flush=True)
            # setrecursionlimit check for degenerate BST
    with open(f'{DATA}/exp2_bst.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print('wrote exp2_bst.csv')

main()

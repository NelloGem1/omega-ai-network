#!/usr/bin/env python3
"""Automata-lite: DFA/NFA simulator + verification of (a|b)*abb + break tests."""
from itertools import product

class DFA:
    def __init__(self, states, alphabet, start, accepts, trans):
        self.states, self.alphabet, self.start = states, alphabet, start
        self.accepts, self.trans = accepts, trans  # trans: (state, sym) -> state
    def accepts_str(self, s):
        q = self.start
        for c in s:
            if c not in self.alphabet: return False
            q = self.trans.get((q, c))
            if q is None: return False
        return q in self.accepts

def dfa_for_regex_star_suffix(prefix_alt='ab', suffix='abb'):
    """DFA for (a|b)*abb — KMP-style: track longest suffix of input that is
    a prefix of 'abb'. States 0..2 = matched length."""
    pat = suffix
    m = len(pat)
    # build failure via KMP prefix function
    pi = [0]*m
    k = 0
    for i in range(1, m):
        while k and pat[i] != pat[k]: k = pi[k-1]
        if pat[i] == pat[k]: k += 1
        pi[i] = k
    states = list(range(m))  # 0..m-1 ; accept only m-1? need state m too
    # standard: states = matched length 0..m-1 plus dead? use m states where
    # state i means longest suffix matching prefix of length i, i in 0..m-1
    # accept when after consuming char we reach length m -> accept state m.
    # Simpler: states 0..m (m = full match -> accept sink that still tracks)
    states = list(range(m+1))
    trans = {}
    for q in range(m+1):
        for c in 'ab':
            # simulate KMP from state q on char c
            # state q means we have matched q chars of pattern (q<m)
            if q == m:
                # after full match, the suffix 'abb' itself ends with 'b';
                # KMP continue: matched length after 'abb' + c
                # compute properly below using generic sim
                pass
    # Generic simulation helper: given matched-length q and char c, compute new length
    def step(q, c):
        # we conceptually have string = pat[:q] + c ; find longest suffix that's prefix of pat
        s = pat[:min(q,m)] + c
        # longest k<=m such that s endswith pat[:k]
        for k in range(min(m, len(s)), -1, -1):
            if s.endswith(pat[:k]): return k
        return 0
    trans = {(q,c): step(q,c) for q in states for c in 'ab'}
    return DFA(states, ['a','b'], 0, {m}, trans)

def naive_nfa_accepts(s):
    # NFA simulation: states = positions in pattern suffix matching (subset)
    # (a|b)* then must end with 'abb': equivalent check s.endswith('abb') and len>=3
    return len(s) >= 3 and s.endswith('abb')

def main():
    dfa = dfa_for_regex_star_suffix()
    # reference: language = strings over {a,b} ending in 'abb', len>=3
    tests = ['', 'a', 'ab', 'abb', 'aabb', 'abab', 'babb', 'aaabbb',
             'abba', 'abbb', 'bab', 'aab', 'xyz', 'abbab', 'a'*50+'abb']
    import itertools, random
    random.seed(1)
    for _ in range(3000):
        tests.append(''.join(random.choice('ab') for _ in range(random.randint(0,12))))
    bad = 0
    for s in tests:
        if any(c not in 'ab' for c in s):
            dfa_ok = False
        else:
            dfa_ok = dfa.accepts_str(s)
        ref = naive_nfa_accepts(s)
        if dfa_ok != ref:
            bad += 1
            print('MISMATCH', repr(s), 'dfa=', dfa_ok, 'ref=', ref)
    print(f'[verify] {len(tests)} strings tested, {bad} mismatches')

    # BREAK tests: malformed strings must be rejected
    malformed = ['abc', 'ab', 'aab', 'abab', 'aXb', 'ABB', 'ab b']
    print('[break] malformed-string rejections:')
    for s in malformed:
        print(f'  {s!r:10} dfa_accepts={dfa.accepts_str(s)}  (expect False)')

    # note: 'ababb' DOES end with 'abb' -> correctly accepted (in language)
    assert dfa.accepts_str('ababb') == True
    # state-count comparison: (a|b)*abb needs 4 DFA states (KMP)
    print(f'[states] (a|b)*abb DFA uses {len(dfa.states)} states')

    # naive subset construction blow-up demo: NFA for (a|b)*abb then powerset
    # NFA states: loop state L + pattern positions p0,p1,p2
    # subset construction reachable sets
    nfa_states = ['L','p0','p1','p2']
    # transitions on 'a'/'b' as NFA (epsilon-free except self-loop on L for a,b)
    nfa_trans = {
        ('L','a'): {'L','p0'}, ('L','b'): {'L','p0'},
        ('p0','b'): {'p1'},
        ('p1','b'): {'p2'},
        ('p2','a'): set(), ('p2','b'): set(),
    }
    start_set = frozenset({'L'})
    accept_nfa = {'p2'}
    seen = {start_set}; work = [start_set]; dfa_size = 0
    while work:
        S = work.pop(); dfa_size += 1
        for c in 'ab':
            T = frozenset().union(*(nfa_trans.get((q,c), set()) for q in S)) if S else frozenset()
            if T and T not in seen:
                seen.add(T); work.append(T)
    print(f'[subset] NFA->DFA reachable subsets = {dfa_size} (states: {sorted(map(sorted,seen))})')

if __name__ == '__main__':
    main()

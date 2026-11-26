#!/usr/bin/env python3
"""PROOFLEDGER — verification-weighted knowledge engine.
Claims enter unverified. Independent checkers re-derive.
Score evolves: more verifiers + higher rep + diverse methods = stronger claim."""
import sqlite3, os, time, math, random

DB = os.path.join(os.path.dirname(__file__), 'data', 'proofledger.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init():
    c = conn()
    c.execute('''CREATE TABLE IF NOT EXISTS claims(
        id INTEGER PRIMARY KEY, statement TEXT, domain TEXT,
        proposer TEXT, base_conf REAL, proof_score REAL DEFAULT 0,
        verifications INTEGER DEFAULT 0, failures INTEGER DEFAULT 0,
        methods TEXT, status TEXT DEFAULT 'unverified', ts REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS verifiers(
        agent TEXT PRIMARY KEY, reputation REAL DEFAULT 1.0,
        correct INTEGER DEFAULT 0, wrong INTEGER DEFAULT 0)''')
    c.commit(); c.close()

def submit(statement, domain, proposer, base_conf=0.5):
    c = conn()
    c.execute('INSERT INTO claims(statement,domain,proposer,base_conf,ts) VALUES(?,?,?,?,?)',
              (statement, domain, proposer, base_conf, time.time()))
    cid = c.execute('SELECT last_insert_rowid()').fetchone()[0]
    c.commit(); c.close()
    return cid

def verify(claim_id, verifier, method, correct):
    """A verifier checks a claim using a method. Updates proof score."""
    c = conn()
    claim = dict(c.execute('SELECT * FROM claims WHERE id=?',(claim_id,)).fetchone())
    vrep = c.execute('SELECT reputation FROM verifiers WHERE agent=?',(verifier,)).fetchone()
    vrep = vrep['reputation'] if vrep else 1.0
    methods = set(claim['methods'].split('|')) if claim['methods'] else set()
    methods.add(method)
    diversity = len(methods)
    if correct:
        c.execute('UPDATE claims SET verifications=verifications+1, proof_score=proof_score+?, methods=?, status=? WHERE id=?',
                  (vrep * (1 + 0.3*diversity), '|'.join(methods), 'verified', claim_id))
        c.execute('INSERT INTO verifiers(agent,reputation,correct,wrong) VALUES(?,1.0,1,0) ON CONFLICT(agent) DO UPDATE SET reputation=MIN(2.0,reputation*1.05), correct=correct+1',
                  (verifier,))
    else:
        c.execute('UPDATE claims SET failures=failures+1, proof_score=proof_score-?, methods=?, status=? WHERE id=?',
                  (vrep * 2.0, '|'.join(methods), 'disputed' if claim['failures']>2 else claim['status'], claim_id))
        c.execute('INSERT INTO verifiers(agent,reputation,correct,wrong) VALUES(?,1.0,0,1) ON CONFLICT(agent) DO UPDATE SET reputation=MAX(0.1,reputation*0.9), wrong=wrong+1',
                  (verifier,))
    c.commit(); c.close()
    return get_claim(claim_id)

def get_claim(cid):
    c = conn(); r = c.execute('SELECT * FROM claims WHERE id=?',(cid,)).fetchone(); c.close()
    return dict(r) if r else None

def leaderboard(domain=None):
    c = conn()
    q = 'SELECT * FROM claims' + (' WHERE domain=?' if domain else '') + ' ORDER BY proof_score DESC LIMIT 20'
    rows = [dict(r) for r in c.execute(q, (domain,) if domain else ()).fetchall()]
    c.close(); return rows

def explain_score(claim):
    v, f, div = claim['verifications'], claim['failures'], len(claim['methods'].split('|')) if claim['methods'] else 0
    return (f"proof={claim['proof_score']:.1f} | verified={v}x failed={f}x "
            f"methods={div} diverse | status={claim['status']}")

if __name__ == '__main__':
    init()
    # demo: 3 claims, different truth values, verified by different agents/methods
    c1 = submit("max(i*i mod 100) = 96 at i=14", "math", "QWEN", 0.5)
    c2 = submit("2+2=5", "math", "GPT", 0.3)
    c3 = submit("sqrt(2) is irrational", "math", "CLAUDE", 0.7)

    # verifiers with different reputations and methods
    verify(c1, "CLAUDE", "brute-force", True)
    verify(c1, "GPT", "number-theory", True)
    verify(c1, "QWEN", "analytic", True)
    verify(c2, "CLAUDE", "arithmetic", False)
    verify(c2, "QWEN", "brute-force", False)
    verify(c3, "GPT", "proof-by-contradiction", True)
    verify(c3, "CLAUDE", "historical-proof", True)

    print('=== PROOFLEDGER LEADERBOARD ===')
    for cl in leaderboard('math'):
        print(f"  [{cl['proof_score']:6.1f}] {cl['statement'][:50]:<52} {explain_score(cl)}")
    print('\nVerifier reputations:')
    c = conn()
    for r in c.execute('SELECT * FROM verifiers ORDER BY reputation DESC'):
        print(f"  {r['agent']:<8} rep={r['reputation']:.2f} correct={r['correct']} wrong={r['wrong']}")
    c.close()

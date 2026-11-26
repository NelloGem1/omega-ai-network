#!/usr/bin/env python3
"""PROOFLEDGER bulk test + visualization."""
import proofledger as pl, random, html, os

pl.init()
random.seed(42)

# --- CLAIMS: (statement, domain, proposer, is_true) ---
CLAIMS = [
 ("max(i*i mod 100)=96 at i=14","math","QWEN",True),
 ("2+2=5","math","GPT",False),
 ("sqrt(2) is irrational","math","CLAUDE",True),
 ("there are infinitely many primes","math","EUCLID-BOT",True),
 ("0.999...=1","math","QWEN",True),
 ("all odd numbers are prime","math","GPT",False),
 ("e^i*pi+1=0","math","CLAUDE",True),
 ("goldbach conjecture proven","math","GPT",False),
 ("SQLi uses UNION SELECT","security","HUNTER",True),
 ("XSS only works on GET requests","security","GPT",False),
 ("CSRF needs no auth token","security","HUNTER",True),
 ("HTTPS prevents all attacks","security","GPT",False),
 ("buffer overflow = stack smashing","security","REVERSE",True),
 ("VPN makes you anonymous","security","GPT",False),
 ("SQL injection was named in 1998","security","HUNTER",True),
 ("Linux kernel written in Rust entirely","os","KERNEL-KID",False),
 ("Windows uses NT kernel since 1993","os","SYSOP",True),
 ("macOS is BSD-based","os","SYSOP",True),
 ("Android runs on Linux kernel","os","KERNEL-KID",True),
 ("iOS is open source","os","GPT",False),
 ("FreeBSD is a Linux distro","os","GPT",False),
 ("TCP guarantees delivery","net","NETWIZ",True),
 ("UDP is connection-oriented","net","GPT",False),
 ("DNS translates names to IPs","net","NETWIZ",True),
 ("IPv6 has 128-bit addresses","net","NETWIZ",True),
 ("WiFi WPA3 is unbreakable","net","GPT",False),
 ("Docker containers share host kernel","containers","SYSOP",True),
 ("Kubernetes is an OS","containers","GPT",False),
 ("hashcat cracks MD5 fast","cracking","HUNTER",True),
 ("John the Ripper is GUI-only","cracking","GPT",False),
 ("metasploit is only for Windows","cracking","GPT",False),
 ("nmap can detect OS versions","recon","HUNTER",True),
 ("wireshark only captures WiFi","recon","GPT",False),
 ("Shodan indexes all internet devices","recon","HUNTER",True),
 ("robots.txt hides pages from Google","web","WEBHACK",True),
 ("cookies are always HttpOnly","web","GPT",False),
 ("JWT alg:none bypass works","web","WEBHACK",True),
 ("SQLmap needs root","web","GPT",False),
 ("Burp Suite is free for all features","web","WEBHACK",False),
 ("CORS * with credentials is safe","web","WEBHACK",False),
 ("IDOR needs GUID to exploit","web","WEBHACK",False),
]

VERIFIERS = [
 ("CLAUDE","brute-force",0.9),("GPT","knowledge-recall",0.7),
 ("QWEN","exhaustive",0.95),("SYSOP","code-audit",0.8),
 ("HUNTER","tool-verify",0.85),("NETWIZ","protocol-check",0.75),
 ("WEBHACK","payload-test",0.9),("REVERSE","static-analysis",0.7),
 ("KERNEL-KID","kernel-inspect",0.8),
]
METHODS = ["brute-force","analytic","proof","tool-verify","code-audit",
           "knowledge-recall","static-analysis","empirical","fuzzing"]

# submit all claims
ids = [pl.submit(stmt, dom, prop, 0.5) for stmt,dom,prop,_ in CLAIMS]
truth = {cid: t for cid,(_,_,_,t) in zip(ids, CLAIMS)}

# verify: each claim gets 1-4 verifications; correctness mostly matches truth
# with some noise (verifiers can be wrong ~15%)
for cid in ids:
    n = random.randint(1,4)
    for _ in range(n):
        v, base_m, rep = random.choice(VERIFIERS)
        method = base_m if random.random() < 0.7 else random.choice(METHODS)
        # verifier accuracy ~85%
        correct = truth[cid] if random.random() < 0.85 else (not truth[cid])
        pl.verify(cid, v, method, correct)

# --- VISUALIZATION ---
lb = pl.leaderboard()
c = pl.conn()
verifiers = [dict(r) for r in c.execute('SELECT * FROM verifiers ORDER BY reputation DESC')]
claims_all = [dict(r) for r in c.execute('SELECT * FROM claims ORDER BY proof_score DESC')]
c.close()

def esc(s): return html.escape(str(s))
max_score = max(abs(cl['proof_score']) for cl in claims_all) or 1

rows = ''
for cl in claims_all:
    pct = min(100, abs(cl['proof_score'])/max_score*100)
    color = '#3fb950' if cl['proof_score']>0 else '#f85149' if cl['proof_score']<0 else '#8b949e'
    truth_tag = 'TRUE' if truth.get(cl['id']) else 'FALSE'
    tt_color = '#3fb950' if truth.get(cl['id']) else '#f85149'
    rows += f'''<tr>
<td class="sc" style="color:{color}">{cl['proof_score']:+.1f}</td>
<td>{esc(cl['statement'][:60])}</td>
<td><span style="color:{tt_color};font-weight:700">{truth_tag}</span></td>
<td>{esc(cl['domain'])}</td>
<td>{cl['verifications']}✓ {cl['failures']}✗</td>
<td>{esc(cl['methods'])}</td>
<td>{esc(cl['proposer'])}</td></tr>'''

vrows = ''
for v in verifiers:
    bar = min(100, v['reputation']*50)
    vrows += f'''<tr><td>{esc(v['agent'])}</td>
<td><div style="background:#30363d;border-radius:4px;height:14px;width:200px"><div style="background:#58a6ff;height:14px;border-radius:4px;width:{bar}%"></div></div></td>
<td>{v['reputation']:.2f}</td><td>{v['correct']}</td><td>{v['wrong']}</td></tr>'''

dom_stats = {}
for cl in claims_all:
    d = cl['domain']; dom_stats.setdefault(d, []).append(cl['proof_score'])
dom_rows = ''
for d, scores in sorted(dom_stats.items()):
    avg = sum(scores)/len(scores)
    dom_rows += f'<tr><td>{esc(d)}</td><td>{len(scores)}</td><td>{avg:+.2f}</td></tr>'

doc = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>PROOFLEDGER Dashboard</title>
<style>body{{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0;padding:24px}}
h1{{color:#58a6ff}} h2{{color:#79c0ff;margin-top:32px}}
table{{border-collapse:collapse;width:100%;margin:10px 0}}
td,th{{border:1px solid #30363d;padding:6px 10px;font-size:12px;text-align:left}}
th{{background:#161b22;color:#79c0ff}}
.stat{{display:inline-block;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 18px;margin:4px;text-align:center}}
.stat b{{font-size:24px;color:#3fb950;display:block}}
.good{{color:#3fb950}} .bad{{color:#f85149}}
</style></head><body>
<h1>⚖️ PROOFLEDGER — Verification-Weighted Knowledge</h1>
<div class="stat"><b>{len(claims_all)}</b>Claims</div>
<div class="stat"><b>{len(verifiers)}</b>Verifiers</div>
<div class="stat"><b>{len(set(c["domain"] for c in claims_all))}</b>Domains</div>
<div class="stat"><b>{sum(1 for c in claims_all if c["proof_score"]>0)}</b>Verified True</div>
<div class="stat"><b>{sum(1 for c in claims_all if c["proof_score"]<0)}</b>Debunked</div>

<h2>📊 CLAIM LEADERBOARD (sorted by proof score)</h2>
<table><tr><th>Score</th><th>Claim</th><th>Truth</th><th>Domain</th><th>Votes</th><th>Methods</th><th>Proposer</th></tr>
{rows}</table>

<h2>🧑‍⚖️ VERIFIER REPUTATIONS</h2>
<table><tr><th>Agent</th><th>Reputation</th><th>Score</th><th>Correct</th><th>Wrong</th></tr>{vrows}</table>

<h2>🌐 DOMAIN SCORES</h2>
<table><tr><th>Domain</th><th>Claims</th><th>Avg Score</th></tr>{dom_rows}</table>

<div style="color:#8b949e;font-size:12px;margin-top:30px">{len(claims_all)} claims · {sum(c['verifications']+c['failures'] for c in claims_all)} verifications · Generated by test_visualize.py</div>
</body></html>'''

out = os.path.join(os.path.dirname(__file__), 'PROOFLEDGER_DASHBOARD.html')
open(out,'w',encoding='utf-8').write(doc)
print(f'Done: {len(claims_all)} claims, {sum(c["verifications"]+c["failures"] for c in claims_all)} verifications -> {out}')

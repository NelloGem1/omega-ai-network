#!/usr/bin/env python3
"""Global OS Encyclopedia builder — merges datasets, dedupes, drops junk,
emits SQLite + single-page HTML with deliverables A-J."""
import sqlite3, os, sys, html, json
from collections import defaultdict
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, 'data'))
from os_data import DATA as D1
try:
    from os_data_global import G as D2
    from os_data3 import G3 as D3
except Exception:
    D2 = []; D3 = []

DROP = {'Mint? no','Mandriva-derived?','Rosa','Debian (global)',
 'PinePhone OS options','BIRD vs Quagga note','BIRD routing',
 'Pilot OS (NeXT?)','Trion/Trio OS','RobotX/RobotOS','OS-9 (dup)',
 'CarPlay/Android Auto','BlackBerry IVI','OSD/VS','OS/VS','DOS/VSE',
 'VM/XA','MVS/SP','OS/390','GCOS 7/8','BS2000','A2','Classic Environment',
 'bridgeOS','HomePod OS','Apple Remote Desktop','MSIX/Windows App SDK',
 'Windows on ARM','Windows Subsystem for Linux','Sailfish (Jolla)',
 'NuttX RTOS robots','QNX SDP','Linux Automotive','GENIVI','ROS Industrial',
 'BIRD','FRRouting','Quagga','Amiga Kickstart','AmigaOS 3.1/4.0',
 # v3 junk/dup/BIOS-firmware/non-OS
 'Igalia? no','TuxBot?','Russian: Rosa','Aurora','KaOS','Playtron','Clover',
 'Untangle NG','OPNsense firewall','RouterBOARD firmware','TrustedBSD? dup',
 'MAC framework','SafeRTOS','uC/OS','VxWorks 653','NuttX','RIOT','Minix 3.3',
 'Cosmos? dup','Jeanne','lingering?','TrustedGRUB','Dasharo','OpenContrail',
 'Debian Testing','Debian Unstable','Debian Stable','Debian GNU/Linux',
 'ROSA Fresh','ROSA Server','ROSA Mobile','ROSA Embedded','ALT Education',
 'ALT Server','ALT Workstation','ALT Mobile','Astra SE','Astra Linux Mobile',
 'Astra Linux Embedded','Astra Linux Server','Astra Linux Special',
 'GPD OS','Ayaneo OS','Logitech G Cloud OS','GeForce NOW OS',
 'Xbox Cloud Gaming OS','PS Remote Play OS','Nintendo Switch Online OS',
 'Steam Machine OS','ROG Ally OS','Lenovo Legion Go OS',
 'Dreamcast BIOS','PlayStation BIOS','GameCube BIOS','Wii BIOS','3DS BIOS',
 'PSP BIOS','Vita BIOS','Xbox BIOS','Xbox 360 BIOS','Xbox One BIOS','PS4 BIOS',
 'PS5 BIOS','Switch BIOS','Turbografx-16 PC Engine','Puppy derivatives',
 'OpenUNIX','Calc Linux','Microsoft Windows 95/98/ME','OS-9','QNX Neutrino dup',
 'KaOS (see above)','OpenBSD dup','Minix dup','Contiki dup','FreeRTOS dup',
 'Zephyr dup','ThreadX dup','VxWorks dup','QNX dup','Ubuntu Touch dup'}

def junk(r):
    name = r[0]
    if name in DROP or '?' in name: return True
    # rows where nearly everything is '—'
    dash = sum(1 for x in r[1:] if str(x).strip() in ('—','-',''))
    return dash >= 8

# normalize to dict
entries = []
for cat, rows in D1.items():
    for r in rows:
        entries.append({'name':r[0],'dev':r[1],'year':r[2],'cat':cat,
            'purpose':r[4],'arch':r[5],'license':r[6],'kernel':r[7],'status':r[8],
            'country':'—','latest':'—','website':'—','family':r[3]})
for r in list(D2)+list(D3):
    if len(r) < 12:
        r = tuple(list(r) + ['—']*(12-len(r)))
    entries.append({'name':r[0],'country':r[1],'dev':r[2],'year':r[3],
        'latest':r[4],'status':r[5],'cat':r[6],'kernel':r[7],'parent':r[8],
        'license':r[9],'purpose':r[10],'website':r[11],'family':r[6]})

# dedupe by lowercase name (keep first = richer record)
seen = {}
for e in entries:
    k = e['name'].lower().strip()
    if k not in seen and not junk([e['name']]+list(e.values())[1:]):
        seen[k] = e
E = list(seen.values())

# ---- SQLite ----
db = os.path.join(BASE,'os_encyclopedia.db')
if os.path.exists(db): os.remove(db)
c = sqlite3.connect(db); c.row_factory = sqlite3.Row
c.execute('''CREATE TABLE os(name TEXT, country TEXT, dev TEXT, year TEXT,
 latest TEXT, status TEXT, category TEXT, kernel TEXT, parent TEXT,
 license TEXT, purpose TEXT, website TEXT)''')
for e in E:
    c.execute('INSERT INTO os VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
      (e['name'],e.get('country','—'),e['dev'],e['year'],e.get('latest','—'),
       e['status'],e['cat'],e.get('kernel','—'),e.get('parent',e.get('kernel','—')),
       e['license'],e['purpose'],e.get('website','—')))
c.execute('CREATE INDEX i_cat ON os(category)'); c.execute('CREATE INDEX i_country ON os(country)')
c.commit(); c.close()

# ---- HTML deliverables ----
def esc(s): return html.escape(str(s))
def status_bucket(s):
    s = s.lower()
    if 'active' in s or 'niche' in s: return 'Active/Niche'
    if 'discontinued' in s or 'historical' in s or 'merged' in s: return 'Discontinued/Historical'
    return 'Experimental/Other'

cats = defaultdict(list); countries = defaultdict(list); years = defaultdict(list)
for e in E:
    cats[e['cat']].append(e); countries[e.get('country','—')].append(e); years[e['year']].append(e)

status_map = defaultdict(list)
for e in E: status_map[status_bucket(e['status'])].append(e)

# family tree = category groups
# kernel comparison: group by kernel text similarity (simple: top kernels)
kernel_count = defaultdict(int)
for e in E:
    k = (e.get('kernel') or e.get('parent') or '—').split('/')[0].strip()
    kernel_count[k]+=1
top_kernels = sorted(kernel_count.items(), key=lambda x:-x[1])[:25]

def card(e):
    return f'''<div class="card"><div class="nm">{esc(e['name'])}</div>
<div class="mt"><b>{esc(e.get('country','—'))}</b> · {esc(e['dev'])} · {esc(e['year'])}–{esc(e.get('latest','—'))}</div>
<div class="mt">{esc(e['status'])} · {esc(e.get('kernel','—'))}</div>
<div class="mt">{esc(e['purpose'])}</div></div>'''

def section(title, items, keyfn=None):
    out = f'<h2>{title}</h2>'
    groups = defaultdict(list)
    for e in items: groups[keyfn(e) if keyfn else 'All'].append(e)
    for g, rows in sorted(groups.items()):
        out += f'<h3>{esc(g)} <span class="cnt">({len(rows)})</span></h3><div class="grid">'
        for e in sorted(rows, key=lambda x:x['name']): out += card(e)
        out += '</div>'
    return out

parts = [f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>World OS Encyclopedia</title><style>
body{{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0;padding:24px}}
h1{{color:#58a6ff}} h2{{color:#79c0ff;border-bottom:1px solid #30363d;padding-top:28px}}
h3{{color:#c9d1d9;margin:18px 0 8px}} .cnt{{color:#8b949e;font-size:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;margin-bottom:14px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px}}
.nm{{font-weight:700;color:#f0f6fc}} .mt{{font-size:12px;color:#8b949e;margin-top:2px}}
table{{border-collapse:collapse;width:100%;margin:10px 0}} td,th{{border:1px solid #30363d;padding:6px 10px;font-size:13px;text-align:left}}
th{{background:#161b22;color:#79c0ff}} nav a{{color:#58a6ff;margin-right:12px;text-decoration:none;font-size:13px}}
.stat{{display:inline-block;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 18px;margin:4px;text-align:center}}
.stat b{{font-size:22px;color:#3fb950;display:block}}
</style></head><body>
<h1>🌍 WORLD OS ENCYCLOPEDIA</h1>
<div class="stat"><b>{len(E)}</b>OS entries</div>
<div class="stat"><b>{len(cats)}</b>categories</div>
<div class="stat"><b>{len(countries)}</b>countries</div>
<div class="stat"><b>{len(set(e["year"] for e in E))}</b>years covered</div>
<nav>{''.join(f'<a href="#{i}">{esc(k)}</a>' for i,k in enumerate(['A-Database','B-Countries','C-Timeline','D-Kernels','E-Families','F-Status','G-Stats','H-All']))}</nav>''']

# A: master database by category
parts.append(section('A · MASTER DATABASE (by category)', E, lambda e: e['cat']))
# B: by country
parts.append(section('B · COUNTRY-BY-COUNTRY CATALOG', E, lambda e: e.get('country','—')))
# C: timeline by decade
parts.append(section('C · HISTORICAL TIMELINE', E, lambda e: (e['year'][:3]+'0s') if e['year'][:1].isdigit() else e['year']))
# D: kernel comparison table
parts.append('<h2>D · KERNEL & ARCHITECTURE COMPARISON</h2><table><tr><th>Kernel/Foundation</th><th>OSes</th></tr>')
for k,n in top_kernels: parts.append(f'<tr><td>{esc(k)}</td><td>{n}</td></tr>')
parts.append('</table>')
# E: family tree = category sections already; add parent grouping
parts.append('<h2>E · FAMILY TREE (by category)</h2>')
parts.append('<table><tr><th>Family</th><th>Count</th><th>Representative OSes</th></tr>')
for cat, rows in sorted(cats.items(), key=lambda x:-len(x[1])):
    names = ', '.join(e['name'] for e in sorted(rows,key=lambda x:x['name'])[:6])
    parts.append(f'<tr><td>{esc(cat)}</td><td>{len(rows)}</td><td>{esc(names)}{"…" if len(rows)>6 else ""}</td></tr>')
parts.append('</table>')
# F: status lists
parts.append(section('F · STATUS BREAKDOWN', E, lambda e: status_bucket(e['status'])))
# G: stats
parts.append('<h2>G · ECOSYSTEM STATISTICS</h2><table><tr><th>Metric</th><th>Value</th></tr>')
parts.append(f'<tr><td>Total OSes</td><td>{len(E)}</td></tr>')
parts.append(f'<tr><td>Categories</td><td>{len(cats)}</td></tr>')
parts.append(f'<tr><td>Countries represented</td><td>{len(countries)}</td></tr>')
parts.append(f'<tr><td>Distinct years</td><td>{len(set(e["year"] for e in E))}</td></tr>')
parts.append(f'<tr><td>Active/Niche</td><td>{len(status_map["Active/Niche"])}</td></tr>')
parts.append(f'<tr><td>Discontinued/Historical</td><td>{len(status_map["Discontinued/Historical"])}</td></tr>')
parts.append(f'<tr><td>Experimental</td><td>{len(status_map["Experimental/Other"])}</td></tr>')
parts.append('</table>')
# H: all alphabetical
parts.append(section('H · COMPLETE ALPHABETICAL INDEX', E, lambda e:'All'))
parts.append(f'<div style="color:#8b949e;font-size:12px;margin-top:30px">DB: os_encyclopedia.db · Entries: {len(E)} · Built by build_global.py</div>')
parts.append('</body></html>')

out = os.path.join(BASE,'OS_WORLD_ENCYCLOPEDIA.html')
open(out,'w',encoding='utf-8').write(''.join(parts))
print(f'OK {len(E)} entries -> {out}')

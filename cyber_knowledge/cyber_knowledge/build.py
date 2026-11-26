#!/usr/bin/env python3
import html, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data'))
from cyber_data import DATA

LEVEL_COLORS = {'Foundation':'#58a6ff','Offensive':'#f85149','Defensive':'#3fb950',
 'Specialized':'#d29922','Advanced':'#bc8cff','Expert':'#f778ba','Emerging':'#39c5cf',
 'Core':'#8b949e','Theory':'#8b949e','Architecture':'#8b949e','Practice':'#8b949e',
 'Engineering':'#79c0ff','Design':'#79c0ff','Infrastructure':'#79c0ff','National':'#f0883e'}

def esc(s): return html.escape(str(s))

out = ['''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Cybersecurity Master Knowledge Base</title><style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0;padding:24px}
h1{color:#58a6ff} h2{color:#79c0ff;border-bottom:1px solid #30363d;padding-top:28px;margin-top:36px}
h3{color:#c9d1d9;margin:20px 0 10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:10px;margin-bottom:16px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px}
.nm{font-weight:700;color:#f0f6fc;font-size:14px}
.lv{display:inline-block;font-size:10px;padding:2px 8px;border-radius:10px;color:#0d1117;font-weight:700;margin-left:6px}
.mt{font-size:12px;color:#8b949e;margin-top:4px}
.kc{font-size:11px;color:#58a6ff;margin-top:4px}
.df{font-size:11px;color:#3fb950;margin-top:4px}
nav{position:sticky;top:0;background:#0d1117;padding:10px 0;border-bottom:1px solid #30363d;z-index:9}
nav a{color:#58a6ff;margin-right:12px;text-decoration:none;font-size:13px}
.stat{display:inline-block;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 18px;margin:4px;text-align:center}
.stat b{font-size:22px;color:#3fb950;display:block}
.toc{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin:16px 0}
.toc a{color:#79c0ff;text-decoration:none;display:block;padding:3px 0}
</style></head><body>
<h1>🛡️ CYBERSECURITY MASTER KNOWLEDGE BASE</h1>
<div class="stat"><b>'''+str(sum(len(v) for v in DATA.values()))+'''</b>Topics</div>
<div class="stat"><b>'''+str(len(DATA))+'''</b>Sections</div>
<div class="stat"><b>'''+str(len(set(l for v in DATA.values() for _,l,_,_,_ in v)))+'''</b>Levels</div>
<nav>''']

toc_items = []
for i,(sec,rows) in enumerate(DATA.items(),1):
    toc_items.append(f'<a href="#s{i}">{esc(sec)} ({len(rows)})</a>')
out.append('<div class="toc">' + ''.join(toc_items) + '</div>')
out.append('</nav>')

total = 0
for i,(sec,rows) in enumerate(DATA.items(),1):
    out.append(f'<h2 id="s{i}">{esc(sec)} <span style="color:#8b949e;font-size:14px">({len(rows)})</span></h2>')
    out.append('<div class="grid">')
    for name,level,summary,concepts,defense in rows:
        lc = LEVEL_COLORS.get(level.split('/')[0].split('+')[0].strip(),'#8b949e')
        out.append(f'''<div class="card">
<div class="nm">{esc(name)}<span class="lv" style="background:{lc}">{esc(level)}</span></div>
<div class="mt">{esc(summary)}</div>
<div class="kc"><b>Key:</b> {esc(concepts)}</div>
<div class="df"><b>Defense:</b> {esc(defense)}</div></div>''')
        total += 1
    out.append('</div>')

out.append(f'<div style="color:#8b949e;font-size:12px;margin-top:30px">{total} topics · Built by cyber_knowledge/build.py · Educational reference only — all testing must be authorized</div>')
out.append('</body></html>')

path = os.path.join(os.path.dirname(__file__),'CYBER_KNOWLEDGE.html')
open(path,'w',encoding='utf-8').write(''.join(out))
print(f'OK {total} topics -> {path}')

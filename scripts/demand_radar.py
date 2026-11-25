#!/usr/bin/env python3
"""Demand Radar — collect job-market data from free APIs, cluster demand, serve dashboard."""
import json, re, time, html, urllib.request, collections, os
from http.server import HTTPServer, BaseHTTPRequestHandler

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) demand-radar/1.0"}
CACHE = "/home/neilh/demand_radar_cache.json"
CACHE_TTL = 1800  # 30 min

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

SKILL_PATTERNS = [
    "python","javascript","typescript","react","node","aws","azure","gcp","docker","kubernetes",
    "sql","postgres","mysql","mongodb","redis","graphql","rest","api","microservices",
    "machine learning","deep learning","ai","llm","nlp","computer vision","pytorch","tensorflow",
    "data analysis","data engineering","etl","spark","pandas","tableau","power bi","excel",
    "devops","ci/cd","terraform","ansible","linux","git","agile","scrum",
    "react native","flutter","ios","android","swift","kotlin",
    "seo","semrush","google ads","facebook ads","marketing","content","copywriting",
    "video editing","editing","premiere","after effects","motion graphics","animation",
    "graphic design","photoshop","illustrator","ui/ux","figma","sketch","canva",
    "social media","tiktok","instagram","youtube","influencer",
    "customer service","support","sales","account executive","business development",
    "project management","product manager","product owner","scrum master",
    "finance","accounting","bookkeeping","payroll","quickbooks",
    "hr","recruiting","talent","onboarding",
    "nursing","registered nurse","medical","healthcare","patient","clinical",
    "teacher","education","tutor","curriculum",
    "electrician","plumber","hvac","construction","carpentry","roofing",
    "driver","warehouse","logistics","supply chain","forklift","delivery",
    "chef","cook","restaurant","hospitality","hotel",
    "pharmacist","dental","veterinary","therapist","counselor",
    "legal","paralegal","compliance","contract",
    "cybersecurity","security","infosec","penetration","soc",
    "qa","testing","quality assurance","sdet","automation testing",
    "blockchain","crypto","web3","solidity","smart contract",
    "salesforce","hubspot","crm","erp","sap","workday",
    "technical writing","documentation","content writing","copy editor",
    "transcription","captioning","subtitle","localization","translation",
    "voice over","voiceover","narration","podcast",
    "3d","blender","cinema 4d","unity","unreal","game",
    "ar","vr","xr","metaverse",
    "notion","airtable","zapier","make","automation","rpa",
    "shopify","woocommerce","e-commerce","ecommerce","magento",
    "wordpress","webflow","wix","squarespace","cms",
    "email marketing","mailchimp","klaviyo","campaign",
    "remote","hybrid","full-time","part-time","contract","freelance",
]
SKILL_RE = [(s, re.compile(r'\b' + re.escape(s) + r'\b', re.I)) for s in SKILL_PATTERNS]

def norm_skill(s):
    return s.lower()

def extract_skills(text):
    t = text.lower()
    return {s for s, rx in SKILL_RE if rx.search(t)}

def clean_html(h):
    return re.sub(r'<[^>]+>', ' ', h or '')

def collect_remoteok():
    jobs = []
    try:
        d = json.loads(fetch("https://remoteok.com/api"))
        for j in d[1:]:
            if not isinstance(j, dict): continue
            jobs.append({
                "source": "RemoteOK", "title": j.get("position",""),
                "company": j.get("company",""), "location": j.get("location","") or "Remote",
                "tags": j.get("tags") or [], "salary": j.get("salary_min") or "",
                "url": j.get("url","")})
    except Exception as e:
        print("remoteok fail:", e)
    return jobs

def collect_remotive():
    jobs = []
    try:
        d = json.loads(fetch("https://remotive.com/api/remote-jobs?limit=200"))
        for j in d.get("jobs", []):
            jobs.append({
                "source": "Remotive", "title": j.get("title",""),
                "company": j.get("company_name",""), "location": "Remote",
                "tags": j.get("tags") or [],
                "salary": (j.get("salary") or ""),
                "url": j.get("url","")})
    except Exception as e:
        print("remotive fail:", e)
    return jobs

def collect_hn_hiring():
    """Latest 'Who is hiring' thread comments via Algolia."""
    jobs = []
    try:
        d = json.loads(fetch('https://hn.algolia.com/api/v1/search?tags=story&query=Who%20is%20hiring&hitsPerPage=3'))
        hits = d.get("hits", [])
        if not hits: return jobs
        oid = hits[0]["objectID"]
        c = json.loads(fetch(f'https://hn.algolia.com/api/v1/items/{oid}'))
        for ch in c.get("children", [])[:400]:
            txt = ch.get("text") or ""
            # first line usually 'Company | Role | Location | REMOTE'
            first = txt.split("<p>")[0]
            first = re.sub(r'<[^>]+>', ' ', first).strip()
            parts = [p.strip() for p in re.split(r'\||—|–', first) if p.strip()]
            title = parts[1] if len(parts) > 1 else (parts[0] if parts else "")
            comp = parts[0] if parts else ""
            loc = parts[-1] if len(parts) > 2 else ""
            skills = extract_skills(clean_html(txt))
            jobs.append({"source":"HN Hiring","title":title,"company":comp,
                         "location":loc or "Remote","tags":sorted(skills),
                         "salary":"","url":f'https://news.ycombinator.com/item?id={ch.get("id")}'})
    except Exception as e:
        print("hn fail:", e)
    return jobs

def collect_arbeitnow():
    jobs = []
    try:
        d = json.loads(fetch("https://www.arbeitnow.com/api/job-board-api"))
        for j in d.get("data", [])[:200]:
            jobs.append({"source":"Arbeitnow","title":j.get("title",""),
                         "company":j.get("company_name",""),
                         "location":j.get("location",""),
                         "tags":extract_skills((j.get("title","")+" "+clean_html(j.get("description","")))[:3000]),
                         "salary":"","url":j.get("url","")})
    except Exception as e:
        print("arbeitnow fail:", e)
    return jobs

def collect_usajobs():
    """US federal jobs — public API, no key needed for search? actually needs key; try without."""
    return []

def analyze(jobs):
    skill_count = collections.Counter()
    cat_count = collections.Counter()
    companies = collections.Counter()
    sources = collections.Counter()
    titles = collections.Counter()
    for j in jobs:
        sources[j["source"]] += 1
        companies[j["company"]] += 1
        titles[j["title"].lower().strip()] += 1
        text = (j["title"] + " " + " ".join(j.get("tags",[]))).lower()
        for s in extract_skills(text):
            skill_count[s] += 1
    return {
        "total": len(jobs),
        "sources": dict(sources.most_common()),
        "top_skills": skill_count.most_common(40),
        "top_companies": companies.most_common(20),
        "top_titles": titles.most_common(25),
    }

def build_data():
    jobs = []
    jobs += collect_remoteok()
    jobs += collect_remotive()
    jobs += collect_hn_hiring()
    jobs += collect_arbeitnow()
    return jobs, analyze(jobs)

PAGE = """<!doctype html><html><head><meta charset=utf-8><title>Demand Radar</title>
<meta http-equiv=refresh content=60>
<style>
body{background:#0d1117;color:#e6edf3;font-family:system-ui;margin:0;padding:24px}
h1{font-size:22px}h2{font-size:15px;color:#8b949e;margin:24px 0 8px;text-transform:uppercase;letter-spacing:1px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}
.bar{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:13px}
.bar .n{width:90px;color:#8b949e}.bar .t{flex:1;background:#21262d;border-radius:4px;height:14px;position:relative}
.bar .f{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,#1f6feb,#58a6ff);border-radius:4px}
.bar .c{width:40px;text-align:right;color:#c9d1d9}
.stat{font-size:28px;font-weight:700;color:#58a6ff}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:6px 8px;border-bottom:1px solid #21262d;text-align:left}
th{color:#8b949e;font-weight:600}
a{color:#58a6ff;text-decoration:none}
.tag{display:inline-block;background:#21262d;border-radius:10px;padding:1px 8px;font-size:11px;margin:2px;color:#c9d1d9}
#src{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}
.src{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 16px}
</style></head><body>
<h1>📡 Demand Radar — what the job market is asking for</h1>
<div id=src>__SRC__</div>
<div class=grid>
<div class=card><div class=stat>__TOTAL__</div><div style="color:#8b949e;font-size:12px">jobs analyzed</div>
<h2>Top in-demand skills</h2><div class=bar style="color:#8b949e;font-size:12px"><span class=n>skill</span><span class=t></span><span class=c>count</span></div>
__SKILLS__</div>
<div class=card><h2>Top hiring companies</h2>
<table>__COMPANIES__</table></div>
<div class=card><h2>Most common job titles</h2>
<table>__TITLES__</table></div>
<div class=card><h2>All detected skills</h2>__ALLSKILLS__</div>
</div>
<p style="color:#8b949e;font-size:12px;margin-top:24px">Sources: RemoteOK · Remotive · HN Who-is-hiring · Arbeitnow · refreshed every 30min · auto-refresh 60s</p>
</body></html>"""

def render(stats):
    src = "".join(f'<div class=src><b>{k}</b><br><span style="color:#8b949e">{v} jobs</span></div>' for k,v in stats["sources"].items())
    mx = max([c for _,c in stats["top_skills"]] or [1])
    skills = "".join(
        f'<div class=bar><span class=n>{html.escape(s)}</span><span class=t><span class=f style="width:{int(100*c/mx)}%"></span></span><span class=c>{c}</span></div>'
        for s,c in stats["top_skills"][:20])
    comp = "".join(f'<tr><td>{html.escape(c)}</td><td style="text-align:right">{n}</td></tr>' for c,n in stats["top_companies"])
    tit = "".join(f'<tr><td>{html.escape(t.title())}</td><td style="text-align:right">{n}</td></tr>' for t,n in stats["top_titles"])
    allsk = " ".join(f'<span class=tag>{html.escape(s)}</span>' for s,_ in stats["top_skills"])
    return PAGE.replace("__SRC__",src).replace("__TOTAL__",str(stats["total"])) \
               .replace("__SKILLS__",skills).replace("__COMPANIES__",comp) \
               .replace("__TITLES__",tit).replace("__ALLSKILLS__",allsk)

DATA = {"stats": None, "page": "<h1>loading…</h1>", "ts": 0}

def refresh():
    global DATA
    try:
        jobs, stats = build_data()
        DATA = {"stats": stats, "page": render(stats), "ts": time.time(), "jobs": len(jobs)}
        json.dump({"stats": stats, "ts": DATA["ts"]}, open(CACHE,"w"))
        print("refreshed:", stats["total"], "jobs")
    except Exception as e:
        print("refresh fail:", e)

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api"):
            body = json.dumps(DATA.get("stats") or {}).encode()
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
            self.wfile.write(body); return
        if DATA["page"] == "<h1>loading…</h1>" or time.time()-DATA["ts"]>CACHE_TTL:
            self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
            self.wfile.write("<meta http-equiv=refresh content=3><h1>Collecting job data...</h1>".encode()); return
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(DATA["page"].encode())
    def log_message(self,*a): pass

if __name__ == "__main__":
    # load cache if fresh
    if os.path.exists(CACHE):
        try:
            c = json.load(open(CACHE))
            if time.time()-c["ts"] < CACHE_TTL:
                DATA.update({"stats":c["stats"],"ts":c["ts"],"page":render(c["stats"])})
        except Exception: pass
    import threading
    threading.Thread(target=lambda: (refresh(),), daemon=True).start()
    # periodic refresh
    def loop():
        while True:
            time.sleep(CACHE_TTL); refresh()
    threading.Thread(target=loop, daemon=True).start()
    print("Demand Radar on http://localhost:8792")
    HTTPServer(("0.0.0.0", 8792), H).serve_forever()

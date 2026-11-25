#!/usr/bin/env python3
"""Unified content-factory dashboard — serves live status at http://localhost:8791"""
import json, os, glob, time, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE = "/home/neilh/youtube-tool"
PS_ROOT = "/home/neilh/pastel_skies"
ASSETS = os.path.join(BASE, "assets")
STUDIO = "/home/neilh/MUSIC_AI_STUDIO"
PORT = 8791

CHANNELS = [
    {"key": "ps", "name": "Pastel Skies", "token": os.path.join(BASE, "token_ps.json"),
     "sched": os.path.join(PS_ROOT, "ps_schedule.json"),
     "staging": os.path.join(STUDIO, "06_OUTPUTS/staging"),
     "built_log": os.path.join(PS_ROOT, "ps_built.txt"),
     "factory_log": os.path.join(PS_ROOT, "ps_factory.log"),
     "uploaded_log": os.path.join(PS_ROOT, "ps_uploaded.txt")},
    {"key": "mm", "name": "Movie Moments Edits", "token": os.path.join(BASE, "token3.json"),
     "sched": os.path.join(ASSETS, "mm_schedule.json"),
     "staging": "/home/neilh/Downloads/MOVIE_MOMENTS",
     "built_log": os.path.join(ASSETS, "mm_uploaded.txt"),
     "factory_log": os.path.join(ASSETS, "mm_par.log"),
     "uploaded_log": os.path.join(ASSETS, "mm_uploaded.txt")},
    {"key": "shorts", "name": "Movie Moments Shorts", "token": os.path.join(BASE, "token3.json"),
     "sched": os.path.join(ASSETS, "mm_schedule.json"),
     "staging": "/home/neilh/Downloads/MOVIE_MOMENTS_SHORTS",
     "built_log": os.path.join(ASSETS, "shorts_queue_done.txt"),
     "factory_log": os.path.join(ASSETS, "shorts_factory.log"),
     "uploaded_log": os.path.join(ASSETS, "shorts_queue_done.txt")},
]

def yt_service(token_path):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def channel_videos(token_path):
    """Recent uploads incl. scheduled (private+publishAt)."""
    try:
        yt = yt_service(token_path)
        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = yt.playlistItems().list(part="contentDetails", playlistId=uploads,
                                     maxResults=25).execute()
        ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        if not ids:
            return []
        vids = yt.videos().list(part="snippet,status,contentDetails",
                                id=",".join(ids)).execute()
        out = []
        for v in vids.get("items", []):
            st = v.get("status", {})
            out.append({
                "id": v["id"],
                "title": v["snippet"]["title"],
                "privacy": st.get("privacyStatus"),
                "publishAt": st.get("publishAt"),
                "publishedAt": v["snippet"].get("publishedAt"),
                "duration": v["contentDetails"].get("duration"),
                "thumb": v["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
            })
        return out
    except Exception as e:
        return [{"error": str(e)}]

def read_json(p):
    try:
        return json.load(open(p))
    except Exception:
        return {}

def count_lines(p):
    try:
        return sum(1 for l in open(p) if l.strip() and not l.startswith("#"))
    except Exception:
        return 0

def staging_files(d):
    try:
        return sorted(f for f in os.listdir(d) if f.endswith(".mp4"))
    except Exception:
        return []

def last_log_line(p, n=3):
    try:
        lines = [l.strip() for l in open(p, errors="replace") if l.strip()]
        return lines[-n:]
    except Exception:
        return []

def iso_to_ts(s):
    try:
        from datetime import datetime, timezone
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0

STATUS_CACHE = {"t": 0, "data": None}

def build_status():
    now = time.time()
    if STATUS_CACHE["data"] and now - STATUS_CACHE["t"] < 60:
        return STATUS_CACHE["data"]
    channels = []
    for c in CHANNELS:
        vids = channel_videos(c["token"])
        sched = read_json(c["sched"])
        tokens = sched.get("tokens", {})
        published_today = sum(1 for v in vids
                              if v.get("privacy") == "public"
                              and iso_to_ts(v.get("publishedAt", "")) > now - 86400)
        scheduled = [v for v in vids
                     if v.get("publishAt") and iso_to_ts(v["publishAt"]) > now - 3600]
        scheduled.sort(key=lambda v: v["publishAt"])
        built = count_lines(c["built_log"])
        staged = staging_files(c["staging"])
        channels.append({
            "key": c["key"], "name": c["name"],
            "published_today": published_today,
            "scheduled": scheduled[:15],
            "scheduled_count": len(scheduled),
            "quota_used": sum(t.get("count", 0) for t in tokens.values()),
            "quota_max": len(tokens) * 6,
            "next_slot": sched.get("next_slot"),
            "built_total": built,
            "staged": staged,
            "staged_count": len(staged),
            "log_tail": last_log_line(c["factory_log"]),
            "recent": [v for v in vids if not v.get("publishAt")][:8],
        })
    data = {"now": now, "channels": channels,
            "uptime_note": "refreshes every 60s"}
    STATUS_CACHE["t"], STATUS_CACHE["data"] = now, data
    return data

HTML = """<!doctype html><html><head><meta charset=utf-8><title>Content Factory</title>
<meta http-equiv=refresh content=30>
<style>
body{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;margin:0;padding:24px}
h1{font-size:22px} h2{font-size:17px;margin:28px 0 10px;color:#79c0ff}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;margin:10px 0}
.row{display:flex;gap:24px;flex-wrap:wrap}
.stat{font-size:26px;font-weight:700}.lbl{font-size:11px;color:#8b949e;text-transform:uppercase}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:6px 8px;border-bottom:1px solid #21262d;text-align:left}
.sched{color:#d29922}.pub{color:#3fb950}.pend{color:#8b949e}
img{width:120px;border-radius:6px;vertical-align:middle}
.bar{background:#21262d;border-radius:6px;height:10px;width:220px;display:inline-block;vertical-align:middle}
.bar>i{display:block;height:10px;border-radius:6px;background:linear-gradient(90deg,#1f6feb,#3fb950)}
.log{font-family:monospace;font-size:11px;color:#8b949e;white-space:pre-wrap}
small{color:#6e7681}
</style></head><body>
<h1>🎬 Content Factory Dashboard</h1><small>auto-refresh 30s · <span id=now></span></small>
<div id=root>loading…</div>
<script>
async function go(){
 const d = await (await fetch('/api/status')).json();
 document.getElementById('now').textContent = new Date().toLocaleString();
 let h='';
 for(const c of d.channels){
  const pct = c.quota_max? Math.round(100*c.quota_used/c.quota_max):0;
  h+=`<h2>${c.name}</h2><div class=card>
   <div class=row>
    <div><div class=stat>${c.published_today}</div><div class=lbl>published (24h)</div></div>
    <div><div class=stat>${c.scheduled_count}</div><div class=lbl>scheduled ahead</div></div>
    <div><div class=stat>${c.built_total}</div><div class=lbl>total built</div></div>
    <div><div class=stat>${c.staged_count}</div><div class=lbl>staged now</div></div>
    <div><div class=lbl>quota today</div><div class=stat>${c.quota_used}/${c.quota_max}</div>
      <span class=bar><i style="width:${pct}%"></i></span> ${pct}%</div>
   </div>
   <h3>Scheduled publishes</h3><table><tr><th></th><th>Publish at (UTC)</th><th>Title</th><th>ID</th></tr>`;
  for(const v of c.scheduled){
   const t=new Date(v.publishAt).toLocaleString();
   h+=`<tr><td><img src="${v.thumb}"></td><td class=sched>${t}</td><td>${v.title}</td><td><a style=color:#58a6ff href="https://youtu.be/${v.id}">${v.id}</a></td></tr>`;
  }
  h+=`</table><h3>Recent public</h3><table>`;
  for(const v of c.recent){
   h+=`<tr><td><img src="${v.thumb}"></td><td class=pub>${v.publishedAt?v.publishedAt.slice(0,16).replace('T',' '):''}</td><td>${v.title}</td><td><a style=color:#58a6ff href="https://youtu.be/${v.id}">${v.id}</a></td></tr>`;
  }
  h+=`</table><div class=log>${(c.log_tail||[]).join('\\n')}</div></div>`;
 }
 document.getElementById('root').innerHTML=h;
}
go(); setInterval(go,30000);
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/status"):
            body = json.dumps(build_status()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        else:
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print("dashboard on http://localhost:%d" % PORT, flush=True)
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()

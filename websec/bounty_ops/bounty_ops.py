#!/usr/bin/env python3
"""
bounty_ops.py — NelloGem Bug Bounty Operations Deck
Commands:
  add <name> <platform> <scope...>     register a program
  list                                 show tracked programs
  recon <domain>                       passive+light recon → recon/<domain>.txt
  probe <url>                          fingerprint a target (headers/tech/cookies)
  report <title>                       generate a submission-ready report skeleton
  hunt <domain>                        full pipeline: recon + probe + checklist
  scopecheck <domain>                  verify target is inside registered scope
LEGAL: only run recon/probe against programs whose published scope covers
the target. Passive recon (crt.sh, DNS) is lowest-risk; active scanning
must stay inside scope and rate-limited.
"""
import json, os, re, sys, socket, subprocess, urllib.request, urllib.parse, ssl, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PROGRAMS = os.path.join(ROOT, "programs", "programs.json")
RECON_DIR = os.path.join(ROOT, "recon")
REPORT_DIR = os.path.join(ROOT, "reports")
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

UA = {"User-Agent": "bounty-recon/1.0 (authorized security research)"}

def load_programs():
    if not os.path.exists(PROGRAMS): return {}
    return json.load(open(PROGRAMS))

def save_programs(p):
    json.dump(p, open(PROGRAMS,"w"), indent=2)

def add_program(name, platform, scope):
    p = load_programs()
    p[name] = {"platform": platform, "scope": scope,
               "added": datetime.date.today().isoformat(), "status": "active"}
    save_programs(p)
    print(f"[+] {name} registered on {platform} — {len(scope)} scope entries")

def list_programs():
    p = load_programs()
    if not p: print("No programs tracked. Use: bounty_ops.py add <name> <platform> <scope...>")
    for n, d in p.items():
        print(f"{n:30s} {d['platform']:12s} scope={len(d['scope'])} added={d['added']}")

def in_scope(domain):
    """Check domain against all registered scopes."""
    d = domain.lower().strip()
    hits = []
    for name, prog in load_programs().items():
        for s in prog["scope"]:
            s = s.lower().strip()
            if s.startswith("*."):
                if d == s[2:] or d.endswith("." + s[2:]): hits.append((name, s))
            elif d == s or d.endswith("." + s): hits.append((name, s))
    return hits

def crtsh_subdomains(domain):
    """Passive: certificate transparency logs — crt.sh, fallback certspotter."""
    subs = set()
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        req = urllib.request.Request(url, headers=UA)
        data = json.loads(urllib.request.urlopen(req, timeout=30, context=CTX).read())
        for e in data:
            for n in e.get("name_value","").split("\n"):
                n = n.strip().lower().lstrip("*.")
                if n and domain in n: subs.add(n)
    except Exception:
        pass
    if not subs:
        try:
            url = f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"
            data = json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30, context=CTX).read())
            for e in data:
                for n in e.get("dns_names",[]):
                    n = n.strip().lower().lstrip("*.")
                    if n and domain in n: subs.add(n)
        except Exception as e:
            return [f"ERROR: {e}"]
    return sorted(subs)

def resolve(host):
    try: return sorted({ai[4][0] for ai in socket.getaddrinfo(host, None)})
    except Exception: return []

def port_probe(host, ports=(80,443,3000,8000,8080,8443,5000,4000,9000)):
    """Light TCP connect scan — top common web ports only."""
    open_ports = []
    for port in ports:
        try:
            s = socket.create_connection((host, port), timeout=1.5)
            s.close(); open_ports.append(port)
        except Exception: pass
    return open_ports

def http_probe(url):
    """Fingerprint: status, server, powered-by, cookies, security headers."""
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=15, context=CTX)
        h = dict(r.headers)
        body = r.read(200000).decode("utf-8","replace")
        tech = []
        for t in ["wp-content","react","vue","angular","next","django","rails",
                  "laravel","express","jquery","bootstrap","cloudflare"]:
            if t in body.lower() or t in str(h).lower(): tech.append(t)
        sec_headers = [x for x in ["content-security-policy","x-frame-options",
            "x-content-type-options","strict-transport-security",
            "referrer-policy","permissions-policy"] if x not in {k.lower() for k in h}]
        return {"status": r.status, "server": h.get("Server","?"),
                "powered_by": h.get("X-Powered-By","?"),
                "cookies": h.get("Set-Cookie","-")[:120],
                "missing_sec": sec_headers, "tech": tech,
                "title": (re.search(r"<title>([^<]*)</title>", body, re.I) or [None,"?"])[1][:80]}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": str(e)[:100]}
    except Exception as e:
        return {"error": str(e)[:120]}

def wayback_urls(domain, limit=40):
    """Passive: historical URLs from Wayback Machine CDX."""
    try:
        url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=text&fl=original&collapse=urlkey&limit={limit}"
        out = subprocess.run(["curl","-s","--max-time","30",url],
                             capture_output=True, text=True).stdout
        return [l.strip() for l in out.splitlines() if l.strip()][:limit]
    except Exception as e:
        return [f"ERROR: {e}"]

def js_endpoints(domain):
    """Look for JS files on the main page that often leak API routes."""
    try:
        html = urllib.request.urlopen(
            urllib.request.Request(f"https://{domain}/", headers=UA),
            timeout=15, context=CTX).read().decode("utf-8","replace")
        return sorted(set(re.findall(r'src="([^"]+\.js[^"]*)"', html)))[:20]
    except Exception as e:
        return [f"ERROR: {e}"]

def recon(domain):
    os.makedirs(RECON_DIR, exist_ok=True)
    out = [f"# RECON REPORT — {domain}",
           f"# {datetime.datetime.now().isoformat()}",
           f"# ⚠ VERIFY SCOPE BEFORE ANY ACTIVE TESTING\n"]
    scope_hits = in_scope(domain)
    out.append(f"SCOPE CHECK: {'✅ ' + str(scope_hits) if scope_hits else '❌ NOT in registered scope — DO NOT ACTIVE-SCAN'}\n")

    out.append("== SUBDOMAINS (crt.sh passive) ==")
    subs = crtsh_subdomains(domain)
    out += subs if subs else ["(none)"]
    live_subs = []
    for s in subs[:30]:
        if not s.startswith("ERROR") and resolve(s):
            live_subs.append(s)
    out.append(f"\nLIVE SUBDOMAINS ({len(live_subs)}):")
    out += live_subs

    out.append(f"\n== PORTS on {domain} (light web scan) ==")
    ports = port_probe(domain)
    out.append(str(ports) if ports else "(none of common web ports open)")

    for scheme in ["https","http"]:
        info = http_probe(f"{scheme}://{domain}/")
        if "error" not in info or info.get("status"):
            out.append(f"\n== HTTP PROBE {scheme}://{domain} ==")
            out.append(json.dumps(info, indent=2))
            break

    out.append("\n== JS FILES (endpoint leak candidates) ==")
    out += js_endpoints(domain)

    out.append("\n== WAYBACK URLS (historical endpoints) ==")
    out += wayback_urls(domain)

    out.append("\n== HUNTING CHECKLIST ==")
    out += ["[ ] IDOR: change object IDs in API calls (orders/users/files)",
            "[ ] Access control: access admin paths as regular user",
            "[ ] Info disclosure: /.git /.env /backup /api/docs /swagger",
            "[ ] Auth: JWT alg confusion, password reset poisoning",
            "[ ] Injection: ' OR 1=1-- in every parameter",
            "[ ] XSS: reflected params, search boxes, error pages",
            "[ ] Business logic: negative quantities, race conditions, coupon abuse",
            "[ ] Subdomain takeover: dangling CNAMEs on live_subs",
            "[ ] JS files: grep for api_key, token, internal endpoints"]

    path = os.path.join(RECON_DIR, f"{domain}.txt")
    open(path,"w").write("\n".join(out))
    print(f"[+] recon → {path}")
    print(f"    subs={len(subs)} live={len(live_subs)} ports={ports}")
    return path

def report(title, domain=""):
    os.makedirs(REPORT_DIR, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')[:50]
    path = os.path.join(REPORT_DIR, f"{slug}.md")
    tpl = f"""# {title}

**Program:** <platform/program name>
**Target:** {domain or '<URL/endpoint>'}
**Severity:** <Low/Medium/High/Critical>
**Weakness:** <CWE-ID if known, e.g. CWE-639 IDOR>

## Summary
<1-2 sentences: what breaks and why it matters>

## Steps to Reproduce
1. <exact request: method, URL, headers, body>
2. <what to change to trigger the bug>
3. <expected vs actual behavior>

## Impact
<what an attacker gains: data accessed, actions performed, blast radius>

## Evidence
<screenshot paths / response snippets — NO real user data, redact PII>

## Suggested Fix
<concrete remediation>

---
STATUS: DRAFT — fill every <angle> before submitting.
DUP CHECK: search platform hacktivity for this vuln class + target first.
"""
    open(path,"w").write(tpl)
    print(f"[+] report skeleton → {path}")

def hunt(domain):
    """Full pipeline."""
    hits = in_scope(domain)
    if not hits:
        print(f"[!] {domain} is NOT in any registered program scope.")
        print("    Register it first: bounty_ops.py add <prog> <platform> <scope>")
        print("    Running PASSIVE recon only (crt.sh/DNS/wayback — no packets to target).")
    recon(domain)
    print("\nNext: open the recon file, work the checklist top-down.")
    print("When you find something: bounty_ops.py report \"<title>\" " + domain)

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 5:
        add_program(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == "list": list_programs()
    elif cmd == "recon" and len(sys.argv) >= 3: recon(sys.argv[2])
    elif cmd == "probe" and len(sys.argv) >= 3:
        print(json.dumps(http_probe(sys.argv[2]), indent=2))
    elif cmd == "report" and len(sys.argv) >= 3:
        report(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "")
    elif cmd == "hunt" and len(sys.argv) >= 3: hunt(sys.argv[2])
    elif cmd == "scopecheck" and len(sys.argv) >= 3:
        hits = in_scope(sys.argv[2])
        print("IN SCOPE: " + str(hits) if hits else "NOT IN SCOPE")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()

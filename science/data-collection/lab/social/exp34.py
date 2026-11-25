import numpy as np, json
from scipy.optimize import minimize
rng=np.random.default_rng(3)

# ---------- EXP3: Tragedy of the Commons ----------
# N agents choose extraction e_i in [0, emax]. Productivity declines with total G.
# payoff_i = e_i*(V - c*G) - k*e_i^2   (private benefit minus congestion minus effort cost)
N=8; V=10.0; c=0.5; k=0.8; emax=8.0
def payoffs(e):
    G=e.sum(); return e*(V-c*G)-k*e**2
def social(e): return payoffs(e).sum()

# Nash via best-response iteration
def br(e,i):
    # maximize over e_i given others fixed
    o=e.sum()-e[i]
    f=lambda x: -(x*(V-c*(o+x))-k*x*x)
    r=minimize(f,[e[i]],bounds=[(0,emax)],method="L-BFGS-B")
    return r.x[0]
e=np.full(N,2.0)
for _ in range(200):
    en=e.copy()
    for i in range(N): en[i]=br(en,i)
    if np.max(np.abs(en-e))<1e-9: e=en; break
    e=en
G_ne=e.sum(); w_ne=social(e)
print('NASH: e*=',np.round(e,3),'G=',round(G_ne,3),'social welfare=',round(w_ne,3))

# Social optimum: symmetric + scipy joint check
r=minimize(lambda x:-social(x),np.full(N,2.0),bounds=[(0,emax)]*N,method='L-BFGS-B')
eopt=r.x; G_opt=eopt.sum(); w_opt=social(eopt)
print('OPT : e*=',np.round(eopt,3),'G=',round(G_opt,3),'social welfare=',round(w_opt,3))
print(f'overgrazing: Nash G={G_ne:.2f} vs Opt G={G_opt:.2f} ({(G_ne/G_opt-1)*100:.0f}% excess); welfare loss {(1-w_ne/w_opt)*100:.1f}%')

# Punishment: if G>threshold, all pay penalty P. Test grid.
def nash_with_penalty(P,thr):
    ee=np.full(N,2.0)
    for _ in range(300):
        en=ee.copy()
        for i in range(N):
            o=en.sum()-ee[i]
            f=lambda x: -(x*(V-c*(o+x))-k*x*x) - (P if o+x>thr else 0)
            r=minimize(f,[ee[i]],bounds=[(0,emax)],method="L-BFGS-B")
            en[i]=r.x[0]
        if np.max(np.abs(en-ee))<1e-8: ee=en;break
        ee=en
    return ee
results={}
for P in [0,2,4,6,8,10]:
    ee=nash_with_penalty(P,thr=G_opt*1.1)
    results[P]={'G':float(ee.sum()),'welfare':float(social(ee))}
    print(f'punish P={P}: G={ee.sum():.2f} welfare={social(ee):.2f} (opt {w_opt:.2f})')

# ---------- EXP4: Market equilibrium ----------
# D(p)=120-6p ; S(p)=10+4p ; tâtonnement
a,b,c0,d=120,6,10,4
def D(p): return a-b*p
def S(p): return c0+d*p
# analytic eq
peq=(a-c0)/(b+d); qeq=D(peq)
print(f'analytic equilibrium: p*={peq:.2f}, q*={qeq:.1f}')
p=5.0; hist=[]
lam=0.4
for t in range(200):
    excess=D(p)-S(p)
    hist.append((p,excess))
    p=p+lam*excess/10.0
    if abs(excess)<1e-9: break
print(f'tatonnement converged p={p:.3f} after {t+1} iters; final excess={hist[-1][1]:.2e}')
# trace first/last
print('first 5:',[(round(x,2),round(e,2)) for x,e in hist[:5]],' last:',round(hist[-1][0],3))

# price ceiling below equilibrium
for ceil in [10.0,15.0]:
    pc=min(ceil,peq)  # sellers can't charge above ceil; effective price=ceil
    short=D(pc)-S(pc)
    print(f'price ceiling {ceil}: D={D(pc):.1f} S={S(pc):.1f} shortage={short:.1f} (at eq q={qeq:.1f})')
# also floor above eq
for fl in [20.0]:
    pf=fl; surplus=S(pf)-D(pf)
    print(f'price floor {fl}: surplus={surplus:.1f}')

json.dump({'commons':{'nash_e':e.tolist(),'opt_e':eopt.tolist(),'nash_G':float(G_ne),'opt_G':float(G_opt),
          'w_ne':float(w_ne),'w_opt':float(w_opt),'punishment':{str(k):v for k,v in results.items()}},
          'market':{'peq':peq,'qeq':qeq,'tatonnement_final':float(p)}},
          open('/home/neilh/science_lab/social/exp34_results.json','w'),indent=1)

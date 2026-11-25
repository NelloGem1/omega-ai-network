import numpy as np, json
from scipy.optimize import minimize
N=8; V=10.0; c=0.5; k=0.8; emax=8.0; thr=8.333*1.1
def social(e): return (e*(V-c*e.sum())-k*e**2).sum()
def nash(rho):
    ee=np.full(N,2.0)
    for _ in range(400):
        en=ee.copy()
        for i in range(N):
            o=en.sum()-ee[i]
            def f(x,o=o):
                G=o+x[0]; base=x[0]*(V-c*G)-k*x[0]**2
                return -(base - rho*x[0]*max(0.0,G-thr))
            r=minimize(f,[ee[i]],bounds=[(0,emax)],method='L-BFGS-B')
            en[i]=r.x[0]
        if np.max(np.abs(en-ee))<1e-8: ee=en;break
        ee=en
    return ee
print('rho  G      welfare')
res={}
for rho in [0,0.5,1,2,3,5,8]:
    ee=nash(rho); res[rho]={'G':float(ee.sum()),'welfare':float(social(ee))}
    print(f'{rho:4.1f} {ee.sum():6.2f} {social(ee):8.2f}')
json.dump(res,open('/home/neilh/science_lab/social/exp3b_results.json','w'),indent=1)

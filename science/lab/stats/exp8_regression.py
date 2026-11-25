import numpy as np, numpy.linalg as la
from scipy import stats
rng=np.random.default_rng(21)

print("=== 8a. Simpsons paradox: treatment effect reverses ===")
n=400000
S=rng.binomial(1,0.5,n)
T=np.where(S==0, rng.binomial(1,0.9,n), rng.binomial(1,0.1,n))
Y = 2.0*S + 0.2*T + rng.normal(0,0.5,n)   # true T effect = +0.2
mt=Y[T==1].mean()-Y[T==0].mean()
for s in [0,1]:
    d=Y[(T==1)&(S==s)].mean()-Y[(T==0)&(S==s)].mean()
    print(f"stratum S={s}: treated-control diff={d:+.3f}")
print(f"pooled diff={mt:+.3f}  <-- sign reversed vs true +0.2")
X=np.column_stack([np.ones(n),T]); b=la.lstsq(X,Y,rcond=None)[0]
X2=np.column_stack([np.ones(n),T,S]); b2=la.lstsq(X2,Y,rcond=None)[0]
print(f"OLS coef T (omit S)={b[1]:+.3f}; (include S)={b2[1]:+.3f}; true=0.2")

print("=== 8b. Confounder: ice-cream vs drowning ===")
n=100000
Temp=rng.uniform(0,40,n)
Ice=rng.poisson(Temp*0.8,n)
Drown=rng.poisson(0.02*Temp**1.5,n)
print(f"corr(Ice,Drown)={np.corrcoef(Ice,Drown)[0,1]:.3f}")
Ic=Ice-Ice.mean(); Dc=Drown-Drown.mean(); Tc=Temp-Temp.mean()
bI=Ic@Tc/(Tc@Tc); bD=Dc@Tc/(Tc@Tc)
rI=Ic-bI*Tc; rD=Dc-bD*Tc
print(f"partial corr | Temp = {np.corrcoef(rI,rD)[0,1]:.4f}")

print("=== 8c. Noise predictor does not inflate coef but adds noise ===")
noise=rng.normal(0,1,n)
Xn=np.column_stack([np.ones(n),T,S,noise])
bn=la.lstsq(Xn,Y,rcond=None)[0]
print(f"coefs [const,T,S,noise]={np.round(bn,3)}")

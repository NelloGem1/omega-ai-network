import numpy as np, numpy.linalg as la
rng=np.random.default_rng(21)
n=400000
S=rng.binomial(1,0.5,n)
T=np.where(S==0, rng.binomial(1,0.9,n), rng.binomial(1,0.1,n))
Y = 2.0*S + 0.2*T + rng.normal(0,0.5,n)
noise=rng.normal(0,1,n)
Xn=np.column_stack([np.ones(n),T,S,noise])
bn=la.lstsq(Xn,Y,rcond=None)[0]
print("coefs [const,T,S,noise]=",np.round(bn,3))

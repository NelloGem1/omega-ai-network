import numpy as np
from scipy import stats
rng=np.random.default_rng(123)
N=200000
# runs test with float
bits=(rng.random(N)>0.5).astype(np.int64)
runs=1+int(np.sum(bits[1:]!=bits[:-1])); n1=int(bits.sum()); n0=N-n1
mu=2*n0*n1/N+1
var=2*n0*n1*(2*n0*n1-N)/(N*N*(N-1))
z=(runs-mu)/np.sqrt(var); p=2*(1-stats.norm.cdf(abs(z)))
print(f"runs={runs}, expected={mu:.1f}, z={z:+.2f}, p={p:.4f}")

# LCG low-byte test: x_{n+1}=(1103515245 x+12345) mod 2^31, take low 8 bits
x=12345; lows=np.empty(N,np.uint8)
for i in range(N):
    x=(1103515245*x+12345)%(2**31); lows[i]=x&0xFF
counts=np.bincount(lows,minlength=256)
chi2=((counts-N/256)**2/(N/256)).sum()
print(f"LCG low-byte chi2={chi2:.1f}, p={1-stats.chi2.cdf(chi2,255):.3g}")
# period of low byte is tiny; show first 20 vs next 20
print("first 20 low bytes:", lows[:20].tolist())
print("bytes 256..275  :", lows[256:276].tolist())

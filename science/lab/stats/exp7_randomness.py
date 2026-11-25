import numpy as np
from scipy import stats

rng = np.random.default_rng(123)
N = 200000
print("=== 7a. Chi-square uniformity test on byte stream ===")
for name, data in [("numpy PCG64", rng.integers(0,256,N)),
                   ("os.urandom", np.frombuffer(__import__("os").urandom(N),dtype=np.uint8))]:
    counts = np.bincount(data, minlength=256)
    chi2 = ((counts - N/256)**2/(N/256)).sum()
    p = 1-stats.chi2.cdf(chi2, 255)
    print(f"{name:12s}: chi2={chi2:.1f} (df=255), p={p:.4f}")

print("=== 7b. Serial correlation (lag-1) test ===")
for name, x in [("numpy uniform", rng.random(N)),
                ("numpy ints", rng.integers(0,2**31,N)/2**31)]:
    r1 = np.corrcoef(x[:-1], x[1:])[0,1]
    # Ljung-Box-ish: z = r*sqrt(N)
    z = r1*np.sqrt(N)
    p = 2*(1-stats.norm.cdf(abs(z)))
    print(f"{name:14s}: lag-1 r={r1:+.6f}, z={z:+.2f}, p={p:.4f}")

print("=== 7c. Runs test on bits ===")
bits = (rng.random(N)>0.5).astype(int)
# count runs
runs = 1 + np.sum(bits[1:]!=bits[:-1])
n1 = bits.sum(); n0 = N-n1
mu = 2*n0*n1/N + 1
var = 2*n0*n1*(2*n0*n1-N)/(N*N*(N-1))
z = (runs-mu)/np.sqrt(var)
p = 2*(1-stats.norm.cdf(abs(z)))
print(f"runs={runs}, expected={mu:.1f}, z={z:+.2f}, p={p:.4f}")

print("=== 7d. MT19937 determinism: same seed -> same stream ===")
a=np.random.RandomState(42).rand(5); b=np.random.RandomState(42).rand(5)
print("RandomState(42) twice identical:", np.array_equal(a,b))
# period note
print("MT19937 period = 2^19937-1 (~10^6000); state recoverable from 624 consecutive 32-bit outputs")

print("=== 7e. Naive LCG fails badly (for contrast) ===")
# x_{n+1} = (1103515245 x + 12345) mod 2^31, output high bits
x=12345; out=[]
for _ in range(N):
    x=(1103515245*x+12345)%2**31
    out.append(x/2**31)
out=np.array(out)
r1=np.corrcoef(out[:-1],out[1:])[0,1]
counts=np.histogram(out,bins=256,range=(0,1))[0]
chi2=((counts-N/256)**2/(N/256)).sum()
print(f"LCG lag-1 r={r1:+.6f} (z={r1*np.sqrt(N):+.1f}), chi2 p={1-stats.chi2.cdf(chi2,255):.4g}")

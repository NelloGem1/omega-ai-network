import numpy as np
from scipy import stats

rng = np.random.default_rng(7)
print("=== 2. CLT: standardized sums, n = 1,2,4,...,1024 ===")
# distributions: Uniform(0,1), Exp(1), Bernoulli(0.3), Pareto a=3 (finite var)
dists = {
    "Uniform":   (lambda n: rng.uniform(0,1,n), 0.5, 1/12),
    "Exponential":(lambda n: rng.exponential(1,n), 1.0, 1.0),
    "Bernoulli": (lambda n: rng.binomial(1,0.3,n), 0.3, 0.21),
    "Pareto a=3":(lambda n: (1-rng.uniform(0,1,n))**(-1/3), 1.5, 0.75),
}
ns = [1,2,4,8,16,32,64,128,256,512,1024]
print("dist        | " + " ".join(f"n={n:<5}" for n in ns))
for name,(gen,mu,var) in dists.items():
    row=[]
    for n in ns:
        M = 20000
        s = gen(n*M).reshape(M,n).sum(1)
        z = (s - n*mu)/np.sqrt(n*var)
        row.append(stats.normaltest(z).pvalue)  # normality p-value; low=non-normal
    print(f"{name:12s} | " + " ".join(f"{p:.2e} " for p in row))
print("(normaltest p-value; small p => reject normality)")

print("=== 2b. Skewness & excess kurtosis of sums decay ===")
for name,(gen,mu,var) in dists.items():
    for n in [1,16,256]:
        x = gen(200000*n//n) if False else gen(200000)
        # take sums of n
        k = 200000//n
        s = x[:k*n].reshape(k,n).sum(1)
        sk = stats.skew(s); ku = stats.kurtosis(s)  # excess
        print(f"{name:12s} n={n:>4}: skew={sk: .4f}  ex.kurt={ku: .4f}")

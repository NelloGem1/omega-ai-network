import numpy as np
from scipy import stats
rng = np.random.default_rng(3)

print("=== 4a. Beta-Binomial: posterior mean vs MLE vs true ===")
# true p=0.3, observe k=3 successes in n=10
k,n = 3,10
for prior in [(1,1),(0.5,0.5),(10,10),(0.1,0.1),(2,8)]:
    a,b = prior
    post_a, post_b = a+k, b+n-k
    pm = post_a/(post_a+post_b)
    lo,hi = stats.beta.ppf([0.025,0.975],post_a,post_b)
    print(f"prior Beta{prior}: post mean={pm:.3f} 95%CI=[{lo:.3f},{hi:.3f}]")
print(f"true p=0.3, MLE={k/n:.3f}")

print("=== 4b. Frequentist CI coverage for p, small n ===")
# Wilson vs Wald coverage, p=0.3, n=20, 100000 sims
n=20; p_true=0.3; reps=100000
k = rng.binomial(n,p_true,reps)
ph = k/n
# Wald
se = np.sqrt(ph*(1-ph)/n); se[se==0]=1e-9
wald = (ph-1.96*se <= p_true) & (p_true <= ph+1.96*se)
# Wilson
z=1.96; denom=1+z*z/n
cen=(ph+z*z/(2*n))/denom; half=z*np.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/denom
wil = (cen-half <= p_true) & (p_true <= cen+half)
print(f"n={n}, p={p_true}: Wald coverage={wald.mean():.4f}, Wilson coverage={wil.mean():.4f}")
# breakdown at extreme p
for pt in [0.05, 0.5]:
    k = rng.binomial(n,pt,reps); ph=k/n
    se=np.sqrt(ph*(1-ph)/n); se[se==0]=1e-9
    wald=(ph-1.96*se<=pt)&(pt<=ph+1.96*se)
    print(f"p={pt}: Wald coverage={wald.mean():.4f}")

print("=== 4c. Prior sensitivity: same data, different stories ===")
# n=10, k=1. Weak vs informative prior
for prior in [(1,1),(0.5,0.5),(50,50),(1,50)]:
    a,b=prior; pa,pb=a+1,b+9
    print(f"prior Beta{prior}: mean={pa/(pa+pb):.3f} 95%CI=[{stats.beta.ppf(0.025,pa,pb):.3f},{stats.beta.ppf(0.975,pa,pb):.3f}]")

print("=== 4d. Bayes factor / Lindley paradox lite: n large, small effect ===")
# xbar=0.1, sigma=1 known; H0:mu=0 vs H1:mu~N(0,1); frequentist p vs Bayes factor
xbar=0.1; n=100
z = xbar*np.sqrt(n)
pval = 2*(1-stats.norm.cdf(abs(z)))
bf10 = stats.norm.pdf(xbar,0,np.sqrt(1/n+1)) / stats.norm.pdf(xbar,0,np.sqrt(1/n))
# marginal under H1: xbar ~ N(0, 1/n + 1); under H0: N(0,1/n)
print(f"z={z:.2f}, frequentist p={pval:.4f}; Bayes factor B10={bf10:.3f} (favors H1 if >1)")

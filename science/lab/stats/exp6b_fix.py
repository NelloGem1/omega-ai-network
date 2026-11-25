import numpy as np
from scipy import stats
rng=np.random.default_rng(11)
n=50
sig=0; sigb=0; R=5000
for _ in range(R):
    x=rng.normal(0,1,n)
    y=0.3*x+np.sqrt(1-0.09)*rng.normal(0,1,n)
    p=stats.pearsonr(x,y).pvalue
    sig+= p<0.05
    sigb+= p<0.05/20
print(f"power r=0.3 n=50: uncorrected={sig/R:.3f}, bonferroni={sigb/R:.3f}")

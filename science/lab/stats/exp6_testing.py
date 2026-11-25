import numpy as np
from scipy import stats
rng = np.random.default_rng(11)

print("=== 6a. p-hacking: 20 null tests ===")
n_tests=20; n=50; reps=2000
false_pos=np.zeros(reps,dtype=int)
for r in range(reps):
    cnt=0
    for t in range(n_tests):
        x=rng.normal(0,1,n); y=rng.normal(0,1,n)
        p=stats.pearsonr(x,y).pvalue
        if p<0.05: cnt+=1
    false_pos[r]=cnt>0
print(f"P(at least one p<0.05 among 20 null tests)={false_pos.mean():.3f} (nominal 0.05; expected ~{1-0.95**20:.3f})")
# expected number of false positives per study
k=[]
for r in range(reps):
    c=sum(stats.pearsonr(rng.normal(0,1,n),rng.normal(0,1,n)).pvalue<0.05 for _ in range(n_tests))
    k.append(c)
print(f"mean #false positives per 20-test study={np.mean(k):.2f}")

print("=== 6b. Bonferroni correction ===")
alpha_bonf=0.05/20
# redo with bonferroni
fp_bonf=0
for r in range(2000):
    hit=False
    for t in range(n_tests):
        p=stats.pearsonr(rng.normal(0,1,n),rng.normal(0,1,n)).pvalue
        if p<alpha_bonf: hit=True; break
    fp_bonf+=hit
print(f"P(any p<0.0025 among 20 null tests)={fp_bonf/2000:.3f} (~0.05)")
# power loss demo: true effect r=0.3, n=50
sig=sum(stats.pearsonr(*(lambda: (rng.normal(0,1,n), 0.3*rng.normal(0,1,n)+np.sqrt(1-0.09)*rng.normal(0,1,n)))()).pvalue<0.05 for _ in range(5000))
sigb=sum(stats.pearsonr(*(lambda: (rng.normal(0,1,n), 0.3*rng.normal(0,1,n)+np.sqrt(1-0.09)*rng.normal(0,1,n)))()).pvalue<0.0025 for _ in range(5000))
print(f"power r=0.3 n=50: uncorrected={sig/5000:.3f}, bonferroni={sigb/5000:.3f}")

print("=== 6c. Optional stopping bias ===")
# peek after each batch of 10, stop when p<0.05, max 100 obs; true null
stops=[]; final_ps=[]
for r in range(5000):
    data=[]; stopped=False
    for batch in range(10):
        data.extend(rng.normal(0,1,10))
        p=stats.ttest_1samp(data,0).pvalue
        if p<0.05:
            stops.append(len(data)); final_ps.append(p); stopped=True; break
    if not stopped:
        stops.append(100); final_ps.append(p)
print(f"fraction stopped early (claimed sig)={len(final_ps)/5000:.3f}; mean n at stop={np.mean(stops):.1f}")
# compare: fixed n=100 test
fp_fixed=np.mean([stats.ttest_1samp(rng.normal(0,1,100),0).pvalue<0.05 for _ in range(5000)])
print(f"fixed-n=100 false positive rate={fp_fixed:.3f}")

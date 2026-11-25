import numpy as np
rng = np.random.default_rng(1)

print("=== 3a. Sample variance: ddof=0 (MLE) vs ddof=1 (unbiased) ===")
print("n      bias(ddof=0)   bias(ddof=1)   MSE(ddof=0)   MSE(ddof=1)")
for n in [2,3,5,10,30,100]:
    reps=200000
    x = rng.normal(5,2,(reps,n))
    s0 = x.var(1,ddof=0); s1 = x.var(1,ddof=1)
    b0=(s0-4).mean(); b1=(s1-4).mean()
    mse0=((s0-4)**2).mean(); mse1=((s1-4)**2).mean()
    print(f"{n:<6} {b0: .5f}      {b1: .6f}      {mse0:.4f}      {mse1:.4f}")

print("=== 3b. Std estimator bias: E[s] < sigma ===")
for n in [2,5,10,30,100,1000]:
    reps=200000
    x = rng.normal(0,1,(reps,n))
    s = np.sqrt(x.var(1,ddof=1))
    # theoretical E[s]=sigma*c4
    from scipy.special import gamma
    c4 = np.sqrt(2/(n-1))*gamma(n/2)/gamma((n-1)/2)
    print(f"n={n:>5}: E[s]={s.mean():.5f}  theory={c4:.5f}  rel bias={(s.mean()-1)*100:.2f}%")

print("=== 3c. Bernoulli p-hat: bias & variance ===")
p=0.1
for n in [10,50,200]:
    reps=200000
    phat = rng.binomial(1,p,(reps,n)).mean(1)
    print(f"n={n:>4}: bias={phat.mean()-p:+.6f}  sd={phat.std():.4f}  theory sd={np.sqrt(p*(1-p)/n):.4f}")

print("=== 3d. Median vs mean for heavy tail (Cauchy) ===")
# Cauchy: mean is useless; median is fine and robust
for n in [100,1000]:
    x = np.tan(np.pi*(rng.uniform(0,1,(2000,n))-0.5))
    print(f"n={n}: mean-of-means sd={x.mean(1).std():.3f}, median-of-medians sd={np.median(x,1).std():.3f} (median true=0)")

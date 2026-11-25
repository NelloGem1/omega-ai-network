import numpy as np

rng = np.random.default_rng(42)
print("=== 1a. Hit-or-miss pi ===")
Ns = [10**2, 10**3, 10**4, 10**5, 10**6]
for N in Ns:
    x = rng.uniform(-1, 1, N); y = rng.uniform(-1, 1, N)
    inside = (x*x + y*y) <= 1.0
    pi_est = 4.0 * inside.mean()
    print(f"N={N:>8}: pi={pi_est:.5f}  err={abs(pi_est-np.pi):.2e}")

print("=== 1b. Buffon needle (L=1, D=2) ===")
# needle length L=1, line spacing D=2 -> P(cross)=2L/(pi D)=1/pi
for N in [10**3, 10**4, 10**5, 10**6]:
    pos = rng.uniform(0, 2, N)          # center distance to nearest line in [0,D/2]? use [0,1)
    ang = rng.uniform(0, np.pi, N)      # angle to line direction
    cross = (pos <= 0.5*np.abs(np.sin(ang)))  # half-length 0.5*sin(theta)
    p_est = cross.mean()
    pi_est = 1.0/p_est if p_est>0 else np.nan
    print(f"N={N:>8}: P={p_est:.5f}  pi={pi_est:.4f}  err={abs(pi_est-np.pi):.3e}")

print("=== 1c. Integral of sin(x) 0..pi = 2 ===")
for N in Ns:
    xs = rng.uniform(0, np.pi, N)
    est = np.pi * np.sin(xs).mean()
    print(f"N={N:>8}: I={est:.5f}  err={abs(est-2):.2e}")

print("=== 1d. Error scaling log-log (pi hit-or-miss) ===")
errs = []
for N in [10**3,3*10**3,10**4,3*10**4,10**5,3*10**5,10**6,3*10**6]:
    x = rng.uniform(-1,1,N); y = rng.uniform(-1,1,N)
    errs.append(abs(4*((x*x+y*y)<=1).mean()-np.pi))
Ns2 = np.array([10**3,3*10**3,10**4,3*10**4,10**5,3*10**5,10**6,3*10**6],float)
sl = np.polyfit(np.log10(Ns2), np.log10(errs), 1)[0]
print(f"fitted slope = {sl:.3f} (theory ~ -0.5)")

print("=== 1e. E[X]: Gaussian vs Pareto(a=1.5) vs Cauchy ===")
for name, gen in [("Gaussian", lambda n: rng.normal(0,1,n)),
                  ("Pareto a=1.5", lambda n: (1-rng.uniform(0,1,n))**(-1/1.5)),
                  ("Cauchy", lambda n: np.tan(np.pi*(rng.uniform(0,1,n)-0.5)))]:
    print(f"-- {name}")
    for N in [10**3, 10**4, 10**5, 10**6]:
        m = gen(N).mean()
        print(f"   N={N:>8}: sample mean={m: .4f}")

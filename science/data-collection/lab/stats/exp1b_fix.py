import numpy as np
rng = np.random.default_rng(42)
print("=== 1b. Buffon needle (L=1, D=2, d in [0,1]) ===")
for N in [10**3, 10**4, 10**5, 10**6]:
    d = rng.uniform(0, 1, N)
    ang = rng.uniform(0, np.pi, N)
    cross = d <= 0.5*np.abs(np.sin(ang))
    p = cross.mean(); pi_est = 1.0/p
    print(f"N={N:>8}: P={p:.5f}  pi={pi_est:.4f}  err={abs(pi_est-np.pi):.3e}")

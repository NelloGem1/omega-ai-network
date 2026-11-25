"""EXP5: SIR / SIRS epidemiology with solve_ivp."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def sir_rhs(t, y, beta, gamma):
    S, I, R = y
    dS = -beta * S * I
    dI = beta * S * I - gamma * I
    dR = gamma * I
    return [dS, dI, dR]

def sirs_rhs(t, y, beta, gamma, w):  # waning immunity rate w (1/days)
    S, I, R = y
    dS = -beta * S * I + w * R
    dI = beta * S * I - gamma * I
    dR = gamma * I - w * R
    return [dS, dI, dR]

beta, gamma = 0.4, 0.1   # R0 = beta/gamma = 4
t = np.linspace(0, 160, 1600)
y0 = [0.999, 0.001, 0.0]

sol = solve_ivp(sir_rhs, (0, 160), y0, args=(beta, gamma), t_eval=t, rtol=1e-8)
S, I, R = sol.y
print(f"SIR: peak prevalence={I.max()*100:.1f}% at day {t[np.argmax(I)]:.0f}")
herd = 1 - gamma / beta
print(f"analytic herd-immunity threshold: {herd*100:.0f}% immune; final R={R[-1]*100:.1f}%")

# R0 sweep
print("\n=== R0 effect (beta = R0*gamma) ===")
for R0 in [0.8, 1.0, 1.5, 4.0, 10.0]:
    s = solve_ivp(sir_rhs, (0, 200), y0, args=(R0*gamma, gamma), t_eval=t, rtol=1e-8)
    ii = s.y[1]
    print(f"R0={R0:4.1f}: peak={ii.max()*100:5.1f}%  final attack rate={(1-s.y[0][-1])*100:5.1f}%")

# BREAK: SIRS — waning immunity -> endemic oscillations / persistence
w = 0.02  # average immunity 50 days
sol2 = solve_ivp(sirs_rhs, (0, 800), y0, args=(beta, gamma, w), t_eval=np.linspace(0,800,8000), rtol=1e-8)
S2, I2, R2 = sol2.y
t2 = sol2.t
print(f"\n=== BREAK: SIRS (waning immunity, mean 1/w={1/w:.0f} days) ===")
print(f"after transient (t>400): I mean={I2[t2>400].mean()*100:.2f}%, "
      f"min={I2[t2>400].min()*100:.2f}%, max={I2[t2>400].max()*100:.2f}%")
# count oscillation peaks
from scipy.signal import find_peaks
peaks, _ = find_peaks(I2[t2>400], prominence=0.001)
print(f"persistent oscillations detected: {len(peaks)} peaks post-transient")

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
axes[0].plot(t, S*100, label="S"); axes[0].plot(t, I*100, label="I"); axes[0].plot(t, R*100, label="R")
axes[0].set_title(f"SIR (R0={beta/gamma:.0f})"); axes[0].legend(); axes[0].set_xlabel("day")
axes[1].plot(t2, I2*100)
axes[1].set_title(f"SIRS waning immunity w={w}/day"); axes[1].set_xlabel("day")
plt.tight_layout(); plt.savefig("/home/neilh/science_lab/bio/sir_sirs.png", dpi=120)
print("saved sir_sirs.png")

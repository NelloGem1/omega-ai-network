"""EXP4: Enzyme kinetics — Michaelis-Menten, inhibition modes, substrate-inhibition break."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

rng = np.random.default_rng(7)
Vmax_true, Km_true = 100.0, 5.0

def mm(S, Vmax, Km): return Vmax * S / (Km + S)
def mm_comp(S, Vmax, Km, Ki):   # competitive: apparent Km up
def mm_comp(S, Vmax, Km, Ki): return Vmax * S / (Km*(1 + S*0 + 1) , 0) if False else Vmax*S/(Km*(1+Ki/1e9)+S)
# define properly with inhibitor conc I fixed
def mm_competitive(S, Vmax, Km, Ki, I):
    return Vmax * S / (Km*(1 + I/Ki) + S)
def mm_noncompetitive(S, Vmax, Km, Ki, I):
    return (Vmax/(1 + I/Ki)) * S / (Km + S)
def mm_substrate_inhib(S, Vmax, Km, Ki):
    return Vmax * S / (Km + S + S*S/Ki)

S = np.linspace(0.1, 50, 60)
v = mm(S, Vmax_true, Km_true) + rng.normal(0, 2.0, S.size)

# fit Vmax, Km
popt, pcov = curve_fit(mm, S, v, p0=[80, 4], bounds=([0, 0], [500, 100]))
perr = np.sqrt(np.diag(pcov))
print(f"MM fit: Vmax={popt[0]:.1f}±{perr[0]:.1f} (true 100), Km={popt[1]:.2f}±{perr[1]:.2f} (true 5)")

# Lineweaver-Burk for comparison
inv_S, inv_v = 1/S, 1/v
lb = np.polyfit(inv_S, inv_v, 1)
print(f"Lineweaver-Burk: Vmax={1/lb[1]:.1f}, Km={lb[0]/lb[1]:.2f}  (noisier estimator)")

# inhibition comparison at I = Ki
Ki, I = 2.0, 2.0
v_c = mm_competitive(S, Vmax_true, Km_true, Ki, I)
v_n = mm_noncompetitive(S, Vmax_true, Km_true, Ki, I)
v0 = mm(S, Vmax_true, Km_true)
# diagnostic: ratio v_inhib/v0 at low vs high S
low = slice(0, 10); high = slice(-10, None)
print(f"\ncompetitive: v/v0 low-S={np.mean(v_c[low]/v0[low]):.3f} high-S={np.mean(v_c[high]/v0[high]):.3f} (Vmax unchanged)")
print(f"noncompetitive: v/v0 low-S={np.mean(v_n[low]/v0[low]):.3f} high-S={np.mean(v_n[high]/v0[high]):.3f} (Vmax drops)")

# BREAK: substrate inhibition — same Vmax/Km but high [S] inhibits
def mm_si(S, Vmax, Km, Ki): return mm_substrate_inhib(S, Vmax, Km, Ki)
v_si = mm_si(S, Vmax_true, Km_true, Ki=15.0)
peak = S[np.argmax(v_si)]
print(f"\n=== BREAK: substrate inhibition ===")
print(f"v peaks at [S]={peak:.1f} then declines: v(50)/v(peak)={v_si[-1]/v_si.max():.3f}")
try:
    popt2, _ = curve_fit(mm, S, v_si, p0=[80, 4], bounds=([0,0],[500,100]))
    print(f"plain MM fit on inhibited data: Vmax={popt2[0]:.1f}, Km={popt2[1]:.2f} — biased! residual at high S={v_si[-1]-mm(S[-1],*popt2):.1f}")
except Exception as ex:
    print(ex)
# fit the correct model
popt3, _ = curve_fit(mm_si, S, v_si, p0=[80, 4, 10], bounds=([0,0,0],[500,100,1e4]))
print(f"substrate-inhibition fit: Vmax={popt3[0]:.1f}, Km={popt3[1]:.2f}, Ki={popt3[2]:.1f}")

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(S, v, s=12, label="MM data+noise")
ax.plot(S, mm(S, *popt), "k-", label=f"fit Vmax={popt[0]:.0f} Km={popt[1]:.1f}")
ax.plot(S, v_c, "--", label="competitive I=Ki")
ax.plot(S, v_n, ":", label="noncompetitive I=Ki")
ax.plot(S, v_si, "-.", label="substrate inhibition Ki=15")
ax.set_xlabel("[S]"); ax.set_ylabel("v"); ax.legend(fontsize=8); ax.set_title("Enzyme kinetics")
plt.tight_layout(); plt.savefig("/home/neilh/science_lab/bio/kinetics.png", dpi=120)
print("saved kinetics.png")

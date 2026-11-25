"""EXP1: Periodic trends. Uses `mendeleev` (periodictable PyPI pkg is the
STFC physics tables, not chemistry data). Hypothesis: radius shrinks across a
period, eneg/ionization rise; exceptions in transition metals & lanthanides."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mendeleev

rows = []
for el in mendeleev.get_all_elements():
    try:
        grp = el.group
        g = getattr(grp, "group_id", grp)
        per = el.period
        p = getattr(per, "id", per)
        g = int(g) if g else None
        p = int(p) if p else None
        if not g or not p or g > 18 or p > 7:
            continue
        r = el.atomic_radius            # covalent radius, pm
        en = el.en_pauling              # Pauling electronegativity
        ie = el.ionenergies.get(1)      # first ionization energy, eV
        if r and en is not None and ie:
            rows.append(dict(sym=el.symbol, Z=el.atomic_number, p=p, g=g,
                             r=float(r), en=float(en), ie=float(ie)))
    except Exception:
        continue
print(f"elements with complete data: {len(rows)}")
rs = np.array([x["r"] for x in rows]); ens = np.array([x["en"] for x in rows]); ies = np.array([x["ie"] for x in rows])
print(f"radius {rs.min():.0f}-{rs.max():.0f} pm | eneg {ens.min():.2f}-{ens.max():.2f} | IE1 {ies.min():.2f}-{ies.max():.2f} eV")

# within each period, fit radius ~ group (main groups only, g<=2 or g>=13)
print("\n=== radius = a + b*group, per period (main-group elements) ===")
r2s = []
for p in range(1, 8):
    sub = [(x["g"], x["r"]) for x in rows if x["p"] == p and (x["g"] <= 2 or x["g"] >= 13)]
    if len(sub) >= 4:
        g = np.array([s[0] for s in sub], float); r = np.array([s[1] for s in sub], float)
        A = np.vstack([np.ones_like(g), g]).T
        c, *_ = np.linalg.lstsq(A, r, rcond=None)
        pred = A @ c
        r2 = 1 - np.sum((r - pred)**2) / np.sum((r - r.mean())**2)
        r2s.append(r2)
        print(f"period {p}: r={c[0]:6.1f}{c[1]:+7.1f}*g   R2={r2:.3f} n={len(sub)}")
print(f"mean R2 = {np.mean(r2s):.3f}")

# electronegativity vs group within period 2/3
print("\n=== eneg vs group (periods 2 & 3) ===")
for p in (2, 3):
    sub = [(x["g"], x["en"]) for x in rows if x["p"] == p and x["en"]]
    print(f"p{p}: " + " ".join(f"g{g}:{e:.2f}" for g, e in sorted(sub)))

# anomalies: biggest IE1 jumps between consecutive-Z elements
d = np.diff(ies); syms = [x["sym"] for x in sorted(rows, key=lambda x: x["Z"])]
idx = np.argsort(np.abs(d))[::-1][:6]
print("\n=== largest IE1 jumps (group-boundary effects) ===")
for i in sorted(idx):
    print(f"  {syms[i]}({rows[i]['Z']}) -> {syms[i+1]}({rows[i+1]['Z']}): {d[i]:+.2f} eV")

# lanthanide check: radii nearly constant across f-block
fblock = [x for x in rows if x["g"] is None]  # not captured; lanthanides have group None
# use period=6 and Z 57-71 via mendeleev directly
lan = []
for z in range(57, 72):
    el = mendeleev.element(z)
    if el.atomic_radius:
        lan.append((el.symbol, float(el.atomic_radius)))
print("\nlanthanides radii (pm):", lan, "-> contraction is small (~few pm across series)")

# heatmap period x group
grid = {k: np.full((7, 18), np.nan) for k in ("r", "en", "ie")}
for x in rows:
    for k in grid:
        grid[k][x["p"]-1, x["g"]-1] = x[k]
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
for ax, k, name in zip(axes, ("r","en","ie"), ("atomic radius (pm)", "Pauling eneg", "IE1 (eV)")):
    im = ax.imshow(grid[k], cmap="viridis", aspect="auto")
    ax.set_title(name); ax.set_xlabel("group"); ax.set_ylabel("period")
    fig.colorbar(im, ax=ax, fraction=0.05)
plt.tight_layout(); plt.savefig("periodic_heatmap.png", dpi=120)
print("\nsaved periodic_heatmap.png")

# BREAK: same linear fit but INCLUDING transition metals (g 3-12)
print("\n=== BREAK: include d-block in radius~group fit ===")
for p in (4, 5):
    sub_all = [(x["g"], x["r"]) for x in rows if x["p"] == p]
    sub_mg  = [(x["g"], x["r"]) for x in rows if x["p"] == p and (x["g"] <= 2 or x["g"] >= 13)]
    for tag, sub in (("all-groups", sub_all), ("main-only", sub_mg)):
        g = np.array([s[0] for s in sub], float); r = np.array([s[1] for s in sub], float)
        A = np.vstack([np.ones_like(g), g]).T
        c, *_ = np.linalg.lstsq(A, r, rcond=None)
        pred = A @ c
        r2 = 1 - np.sum((r - pred)**2) / np.sum((r - r.mean())**2)
        print(f"period {p} {tag}: slope={c[1]:+.1f} pm/group, R2={r2:.3f}")
print("-> d-block breaks the smooth 'radius decreases with group' trend (filled d orbitals shield poorly)")

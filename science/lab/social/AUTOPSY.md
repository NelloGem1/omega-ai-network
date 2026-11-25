# AUTOPSY — Social Science Lab (game theory / networks / opinions / signaling)
*Forensic re-run of every experiment. Venv: /home/neilh/venv/bin/python.*

## EXP1 — Iterated Prisoner's Dilemma — **BUG FOUND**
**Bug (exp1_pd.py):** `play()` calls `sa.act(ha,hb)` and `sb.act(ha,hb)` — BOTH players receive `(ha,hb) = (playerA_hist, playerB_hist)`. In `wrap().act`, tit-for-tat returns `hb[-1][1]`:
- As player **B**: `hb` is B's own history `(b,a)` → `[1]` = opponent's last action → correct TFT.
- As player **A**: `hb` is B's history `(b,a)` → `[1]` = **A's own last action** → TFT-A degenerates to "repeat own last move", initialized to cooperate → **acts as always-cooperate**.

Net effect: the "tit_for_tat" column is a 50/50 mix of always-cooperate and true TFT; random/grim scores are contaminated because they farm the cooperator seat. Dead code above `play()` and unused `act`-signature handling show the script was patched mid-debug and never cleaned.

**Independent re-run (corrected history semantics, same payoffs/rounds/matches):**
| strategy | reported clean | TRUE clean | reported noisy | TRUE noisy(5%) |
|---|---|---|---|---|
| grim_trigger | 2.659 | 2.659 | 2.355 | **2.099** |
| tit_for_tat | 2.415 | **2.539** | 1.906 | **2.057** |
| random | 2.260 | **1.972** | 2.029 | **2.000** |
| always_cooperate | 2.251 | 2.251 | 1.830 | 1.872 |
| always_defect | 2.012 | 2.012 | 2.078 | 2.078 |

Grim/AC/AD reproduce to 6 decimals (history-insensitive in this setup), confirming the rest of the pipeline is sound; every TFT-influenced number is wrong.
**Verdict on conclusions:** headline survives qualitatively — grim (2.659) still beats true TFT (2.539); under 5% noise TFT (2.057) still lands below always-defect (2.078), though barely. But reported magnitudes (TFT 2.415, random 2.260, noisy grim 2.355, noisy TFT 1.906) are artifacts. Lesson stands, numbers do not.

## EXP2 — Nash equilibrium finder — **VERIFIED**
Re-ran exp2_nash.py: 2x2 mean NE 1.21, P(none)=8.4%; 3x3 mean 1.34, P(none)=12.8%; 397 no-pure-NE 2x2 games → 175 fully-mixed; example mix p=0.8, q=0.533 gives row EVs 4.2=4.2, col EVs 1.8=1.8. `mixed_ne_2x2` algebra checked by hand — correct. Matching Pennies pure-NE list is empty.

## EXP3 + 3b — Tragedy of the Commons — **VERIFIED**
Re-ran exp34.py + exp3b.py exactly: Nash G=13.115 / welfare 27.95 vs opt G=8.333 / welfare 41.667 (57% over-extraction, −32.9% welfare). Lump-sum fine P∈{0..10} leaves G=13.11 unchanged (non-marginal penalty cannot move FOC — mechanism-design point is correct). Per-unit fine rho=2–3 → G=9.17, welfare≈41. Minor caveat: exp3b's best response uses `o=en.sum()-ee[i]` mixing updated/unupdated neighbors (Gauss-Seidel/Jacobi hybrid) — converges fine here.

## EXP4 — Market equilibrium — **VERIFIED**
Re-ran: analytic p*=11, q*=54; tatonnement converges p=11.000 in exactly 50 iters, final excess 8.08e-10 (report: 8e-10). Ceiling 10 → D−S=10 shortage; ceiling 15 → 0; floor 20 → surplus 90. All match.

## EXP5 — Network science — **VERIFIED (one report discrepancy)**
Re-ran exp567.py: ER/WS/BA metrics reproduce exactly (ER largest component n=997, ASP 4.04, diam 9; WS clust 0.449; BA maxdeg 91, ASP 3.54, diam 6). Six-degrees ASP/log n = 0.48–0.60.
- **Attack numbers come from exp5fix.py/exp5fix.json**, not exp567.py — exp567's `frag()` is itself broken: `if k>800: break` fires at k=801 before the k=832 sample, so it records only k=416. exp5fix fixes the loop and produces the reported series (targeted 0.976→0.356 @1200 removals; random 0.755; k=900: 0.623 vs 0.818). Values verified in exp5fix.json.
- **DISCREPANCY:** report claims "crude power-law exponent ~2". Stored `pl_exponent`=**1.30** (polyfit over all degree bins k≥1); BA theory gives γ≈3 for P(k), and the fit is dominated by low-degree bins. "~2" is unsupported by the artifact.

## EXP6 — Deffuant opinion dynamics — **VERIFIED**
Re-ran: eps sweep gives 2/2/3/3/1 clusters exactly as reported; xrange 0→1 at eps≤0.2, consensus at 0.5. 4 stubborn agents {0,1,0,1} at eps=0.5 → 2 persistent clusters vs 1 baseline (mean |x−0.5| 0.500 vs 0.019). Matches.

## EXP7 — Cheap talk / signaling — **VERIFIED**
Re-ran: all 4 pure NE are babbling ([G,G,…] or [B,B,…]); separating NE correctly absent (bad type always mimics). Receiver invests iff msg-EV>0; prior-1/2 babbling gives EV=+0.5 → invest. Costly-signal threshold c>1 is analytically correct. Enumeration is exhaustive over 2×2×2×2 strategy profiles.

---
## Lab verdict
5/7 experiments clean; **EXP1 contains a real implementation bug** (asymmetric history → TFT-as-player-A = always-cooperate) corrupting every TFT/random/noise number though not the qualitative conclusions; **EXP5 has one unsupported claim** (power-law "~2" vs computed 1.30) and a silently-broken first attack script superseded by exp5fix.

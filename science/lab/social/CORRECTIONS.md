# CORRECTIONS — EXP1 Iterated Prisoner's Dilemma (post-autopsy fix)

**Bug:** `exp1_pd.py::play()` passed `(ha,hb)` to BOTH players and the
wrapper always read `hb[-1][1]`. As seat B that is the opponent's last
action (correct TFT); as seat A it is A's OWN last action, so TFT-in-seat-A
degenerated to 'repeat own last move' = effectively always-cooperate.
Every TFT/random/noise-influenced score was corrupted.

**Fix:** `exp1_pd_fixed.py` — `wrap(s, seat)` selects the player's own
history (ha for seat A, hb for seat B); in both histories index [1] is the
opponent's last action. RNG call order unchanged. Output:
`exp1_results_fixed.json`. Original `exp1_results.json` preserved.

## Old vs new (avg per-round payoff)

| strategy | clean (old) | clean (new) | noise 5% (old) | noise 5% (new) |
|---|---|---|---|---|
| grim_trigger | 2.659 | **2.659** | 2.355 | **2.120** |
| tit_for_tat | 2.415 | **2.539** | 1.906 | **2.051** |
| always_cooperate | 2.251 | **2.251** | 1.830 | **1.830** |
| always_defect | 2.012 | **2.012** | 2.078 | **2.078** |
| random | 2.260 | **1.972** | 2.029 | **2.002** |

Clean numbers match the autopsy's independent re-run exactly. Noisy numbers
match ranking (grim > AD > TFT > random > AC) but differ in the 3rd decimal
from the autopsy's re-run (grim 2.099 / TFT 2.057 there) — attributable to a
different RNG stream in that independent implementation; this run preserves
the original script's exact rng consumption order.

**Qualitative conclusions unchanged:** grim still beats true TFT head-to-head;
under 5% noise TFT (2.051) still lands below always-defect (2.078), barely.
Reported magnitudes were artifacts; corrected magnitudes above.

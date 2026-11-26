# AUTOPSY — physics lab (forensic re-verification)
*Marshal-rank audit. Method: read every script, recompute every headline number from raw CSVs, then re-ran ALL 7 scripts end-to-end in the venv.*

## Verdicts

| Exp | Claim | Verdict | Evidence |
|---|---|---|---|
| orbit.py | Kepler ratio 0.9998±0.0006; ΔE/E=6.5e-13/100 orb | **VERIFIED** | Full rerun reproduced: ratio mean 0.9998 std 0.0006; drift 6.524e-13. CSV recomputation matches. |
| doubleslit.py | Δy meas 4.99mm vs 5.00mm; V linear 1→0 in p | **VERIFIED** | Rerun: spacing 0.00499 vs theory 0.00500; V = [1.0,0.9,...,0.0] exactly linear. |
| gas.py | P slope 353 vs NkT/A=300 (+18%); equipartition 0.994; vx/vy=3.28 | **VERIFIED** | Full deterministic rerun (seed 42) reproduced gas.log numbers EXACTLY (slope 353.29, eq 0.994, aniso 3.28). Physics sound: sequential pairwise elastic collisions conserve KE; wall-flux pressure is the correct microscopic definition. +18% over ideal is a real finite-density (virial/B2) effect at packing fraction ~0.09 — interpretation in report is reasonable. |
| wave.py | superposition bounded 2.08; CFL=1.5 → \|u\|~2e11 | **VERIFIED** | Rerun: max\|u\|=2.081 bounded; CFL=1.5 → 1.986e11. Leapfrog update and CFL=1.5 violation both correct. |
| schrodinger.py | box eig err 5.1e-6; well FD vs analytic ~0.5%; T(1)=1.9e-3, T(4)=3.4e-13 | **VERIFIED** | Rerun: rel err -5.14e-6; FD {-4.7681,-4.0789,-2.9565,-1.4666} vs analytic {-4.7705,-4.0884,-2.977,-1.4995}; T_exact(1)=1.888e-3, T_exact(4)=3.361e-13. |
| pendulum.py | λ≈0.8/time; ΔE/E=2.4e-4/80s | **VERIFIED w/ nit** | Rerun: λ=0.815, drift 2.368e-4, sep→17.9 rad (max transient 41). sympy-derived EOM is correct (checked Lagrange chain-rule and energy function consistency). |
| ising.py | Var(m) peaks T=2.25 vs exact 2.269; \|m\|=0.98 @1.5 | **VERIFIED** | Rerun identical (seeded per-T). CSV: Var_m max 0.545 @ T=2.25; \|m\|=0.9849 @1.5. Finite-size shift direction/magnitude correct for L=32. |

## Discrepancies / nits (none affect conclusions)
1. **pendulum.py report wording**: "two ICs differing by 1e-9 rad" — actually the perturbation is **1e-9 in angular velocity ω₂** (`s2 = s0 + [0,0,0,1e-9]` on the `[θ1,ω1,θ2,ω2]` state); initial angular separation is ~0 (first recorded sep=2e-12 after one RK4 step). Cosmetic mislabel, dynamics unaffected.
2. **ising.py statistics caveat**: only ~12 magnetization samples per temperature (`(it-ntherm) % 256 == 0` over 3000 iters). Var(m) peak is still correct, but error bars would be wide; a skeptic should note the Tc estimate rests on ~12 correlated samples near the peak.
3. **schrodinger.py dead code**: `barrier_T()` and `T_num()` are stubs returning None (~40 lines of abandoned scattering-matrix attempts). Harmless, but the tunneling 'verification' is analytic-formula vs WKB only — no independent numerical T was computed. Report's method description is honest about this.
4. **doubleslit.py dead print**: first `print('fringe spacing theory...')` computes a bogus 'measured' value (0.0000) via a disabled code path; the real find_peaks measurement is correct. Cosmetic.
5. gas.py pressure +18% is *attributed* to virial correction — plausible (packing fraction η≈0.094) but not independently derived in the lab; flagged as interpretation, not error.

## Commands run
- Re-ran: doubleslit.py, wave.py, orbit.py, schrodinger.py, ising.py, pendulum.py, gas.py — all completed, outputs reproduced (logs: /home/neilh/ph_*.log).
- Independent CSV recomputation of every headline number (numpy/scipy).

## Bottom line
**PHYSICS: VERIFIED.** All seven experiments reproduce; every REPORT.md headline number checks against raw data and fresh runs. Only cosmetic wording issues (pendulum IC description, dead code).

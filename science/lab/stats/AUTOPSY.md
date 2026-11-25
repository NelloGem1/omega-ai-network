# AUTOPSY — science_lab/stats (forensic re-verification)

*Method: read all 11 scripts; re-ran EVERY experiment in `/home/neilh/venv`
(numpy 2.5.5 / scipy 1.18.1). All sims are seeded → re-runs reproduce exactly.
No output files were saved by the agent, so every REPORT number was checked
against a fresh run. Prior-art: `gh_backup/science/data-collection/
EXPERIMENT_DIGEST.md` — this lab is complementary (no digest stats section
existed); nothing repeated.*

## Verdicts

### EXP 1 — Monte Carlo: **VERIFIED** (original had a real bug, fix verified)
Re-ran `exp1_montecarlo.py`: pi hit-or-miss errs 2.16e-2→2.07e-3 ✓;
log-log slope **−0.621** exact match; Cauchy means 0.690/0.317/−1.323/1.139
match REPORT's 0.69/0.32/−1.32/1.14 exactly; Pareto→~3 ✓.
**Bug found & disclosed:** original Buffon used `pos∈[0,2)` → pi_est≈6.26
(wrong geometry; correct distance range is [0,1] for D=2). `exp1b_fix.py`
gives pi=3.1405 @N=1e6 — REPORT's number is from the fix and is correct.
Honest disclosure in "Issues encountered".

### EXP 2 — CLT: **VERIFIED** with one overstatement
Reproduced the full normaltest table. Exact matches: Pareto a=3 p=2.44e-297
@1024 (REPORT "≈1e-297" ✓); Exp skew 1.99→0.48→0.18 ✓.
**Minor DISCREPANCY:** REPORT says "Uniform normal by n≈16; Exponential by
n≈1024; Bernoulli n≈512". Actual p-values: Uniform passes ~n=32 (p=0.016 @16
still rejects); Exponential still rejects at n=1024 (p=5.0e-3 <0.05);
Bernoulli still rejects at n=512 (p=0.0125), passes at 1024. Convergence is
*slower* than reported — the p-values quoted are real but "normal by" is wrong.

### EXP 3 — Estimator bias: **VERIFIED**
Bit-exact reproduction: ddof=0 bias −2.001@ n=2 (−σ²/n ✓), MSE 12.03 vs
32.11 (REPORT 12.0/32.1 ✓ — unbiased has ~2.7× the MSE, report correct);
E[s] rel-bias −20.2%@n=2, −2.78%@n=10 ✓ (c4 theory matches to 4 decimals);
p-hat unbiased, sd matches theory; Cauchy mean-of-means sd=21684 vs
median-of-medians 0.162 (REPORT 21684/0.16 ✓). Cosmetic: c4 formula emits
nan warning at n=1000 (scipy gamma overflow) — printed theory=nan, harmless.

### EXP 4 — Bayesian vs frequentist: **VERIFIED**
Exact: Wald coverage 0.6415 @p=0.05,n=20 (REPORT 0.64 ✓), Wilson 0.9750 ✓,
Wald@p=0.5 = 0.959 (REPORT 0.96 ✓); Beta(50,50) posterior mean 0.464 on
k=1/n=10 (REPORT "0.17→0.46" ✓); z=1, p=0.317, Bayes factor B10=0.163
(REPORT 0.32/0.16 ✓ — favors H0, correctly stated).

### EXP 5 — Information theory: **PARTIAL DISCREPANCY (stale input data)**
Huffman 2.2300 vs H=2.2017, redundancy 0.0283 ✓ exact. Plug-in entropy bias
−0.1762@100 / −0.0169@1000 ✓ exact. Plug-in MI: k=4,n=100 → 0.0665
(REPORT 0.067 ✓); k=16,n=100 → **1.4855** (REPORT 1.49 ✓).
**DISCREPANCY:** all TOOLS.md compression numbers are stale — the file was
modified (mtime 15:16) after the experiment ran. Report claims 4448 B,
H=5.41, bound ~3010 B, zlib=2263 B (4.07 bits/B), order-1 H≈3.51; rerun on
the current file gives 5299 B, H=5.395, bound ~3574 B, zlib=2681 B
(4.048 bits/B), order-1 3.542. Direction of every claim still holds
(zlib < order-0 bound, > order-1 bound); original numbers were almost
certainly correct for the file version at run time. Flagged, not fatal.

### EXP 6 — Testing traps: **VERIFIED** (original bug real & disclosed)
6a: P(≥1 sig)=0.652, mean 0.98 false pos ✓ exact. 6c: optional stopping →
100% "success", mean n=87.7, fixed-n FPR 0.045 ✓ exact.
**Bug found & disclosed:** `exp6_testing.py` 6b generated y independent of x
→ power≈α (measured 0.052/0.003 — confirms the bug). `exp6b_fix.py`
(y=0.3x+√0.91ε) gives power 0.570 uncorrected / 0.181 Bonferroni —
matches REPORT (0.57→0.18) exactly. Bonferroni family-wise 0.042 ✓.

### EXP 7 — Randomness quality: **VERIFIED** (two bugs real & disclosed)
PCG64 χ²=241.5, p=0.719 (REPORT 0.72 ✓); lag-1 r=−0.0015, p=0.51 ✓;
LCG high-bit χ² p=0.317 (REPORT 0.32 ✓); MT19937 determinism ✓.
LCG low-byte **period-256 proven**: lows[0:20] == lows[256:276] exactly,
χ² p=1.0 (perfectly uniform marginal, fully predictable — report's phrasing
is precise). **Bugs disclosed:** int64 overflow in runs test (nan — fixed
in exp7b_fix, which gives p=0.0059 = REPORT's 0.006 ✓).
NIT: REPORT's "os.urandom χ² p=0.17" is not reproducible (os.urandom is
nondeterministic; rerun gave p=0.69) — plausible single-draw value, can't
verify, low risk.

### EXP 8 — Regression pitfalls: **VERIFIED** (script has a latent crash)
Simpson's paradox exact: strata +0.208/+0.196, pooled **−1.398**
(REPORT −1.40 ✓); OLS omit-S −1.398 / include-S +0.202 (REPORT −1.40/+0.20
✓); ice-cream r=0.664 (REPORT 0.66 ✓), partial r=−0.002 ≈0 ✓;
noise-coef 0.001 via `exp8c.py` ✓.
**BUG (undisclosed):** `exp8_regression.py` section 8c **crashes** —
`noise` has length n=100000 (leftover from 8b) vs T/S/Y length 400000 →
ValueError in column_stack. The shipped script cannot run to completion;
the claim survives only via the separate `exp8c.py`. REPORT's "Issues"
section does not mention this crash.

## Lab verdict: **mostly clean — every headline number reproduced exactly.**
Three stale/broken artifacts found: exp5 TOOLS.md inputs changed post-run
(numbers directionally right, magnitudes unverifiable), exp8_regression.py
8c crashes (workaround exists), exp2 convergence-n thresholds slightly
overstated. All four `_fix`/`_b` companion scripts correspond to real,
disclosed first-draft bugs — good epistemics, sloppy artifact hygiene
(no saved outputs anywhere; several claims only checkable by re-running).

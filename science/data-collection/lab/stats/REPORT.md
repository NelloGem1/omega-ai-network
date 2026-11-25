# Stats Lab Report — Probability, Estimation, Inference

*Agent run: Monte Carlo → estimators → Bayes → information theory → testing traps → RNG quality → regression pitfalls. All sims numpy RNG seeded; venv python.*

## Headline findings

- MC error scales ~N^-0.5 as theory (fitted slope -0.62 on log-log, noisy at large N); **Cauchy mean never converges** — sample mean wanders ±1 even at N=10^6.
- CLT holds but **heavy tails (Pareto a=3) still fail normality tests at n=1024** — finite variance is not enough; skew/kurtosis decay ~n^-1/2 and ~1/n.
- Sample variance ddof=0 is biased (-sigma²/n) yet has **lower MSE than the unbiased ddof=1** at every n — unbiased is not better. Std dev is biased low even when the variance estimator is unbiased (Jensen): -20% at n=2.
- Wald 95% CI for a proportion collapses to **64% coverage at p=0.05, n=20**; Wilson stays ~97.5%. Beta posterior with Beta(50,50) prior drags estimate from 0.17 to 0.46 on n=10,k=1 — priors dominate small data.
- Huffman within 0.03 bits/sym of entropy; zlib beats the order-0 entropy bound via context (4.07 vs 5.41 bits/byte) but sits above the order-1 bound (3.51). **Plug-in entropy is biased low** (-0.18 bits at n=100) and **plug-in MI is strictly positive for independent variables** — 1.49 bits of phantom information at k=16,n=100.
- 20 null tests → **65% chance of a "significant" result**; Bonferroni restores ~4% but kills power (57%→18%). Peeking every 10 obs until p<0.05 → **100% of null studies "succeed"**.
- numpy PCG64 passes chi-square/serial tests; naive LCG **low byte repeats with period 256** — uniform-looking but fully predictable. MT19937 is deterministic: same seed → identical stream, and state is recoverable from 624 consecutive 32-bit outputs.
- **Simpson's paradox reproduced**: pooled treatment effect -1.40 vs true +0.20 (sign flip); conditioning on the confounder restores it. Ice-cream↔drowning correlation 0.66 vanishes (partial r≈0) given temperature.

## Exp 1 — Monte Carlo (`exp1_montecarlo.py`, `exp1b_fix.py`)

- **Hypothesis:** estimator error ~ N^-1/2.
- **Method:** hit-or-miss pi, Buffon needle (L=1, D=2), integral of sin on [0,pi], sample means of Gaussian / Pareto(1.5) / Cauchy.
- **Data:** pi err 2.2e-2 @ N=1e2 → 2e-3 @ N=1e6; Buffon pi=3.1405 @ N=1e6; log-log slope -0.621.
- **Break:** Cauchy mean = 0.69, 0.32, -1.32, 1.14 for N=1e3..1e6 — no convergence (undefined mean). Pareto a=1.5 converges to ~3 (true mean a/(a-1)=3) but slowly.
- **Lesson:** MC gives unbiased-but-noisy answers; heavy tails break everything downstream (CLT needs finite variance).

## Exp 2 — CLT (`exp2_clt.py`)

- **Hypothesis:** standardized sums → N(0,1) regardless of parent distribution.
- **Method:** D'Agostino-Pearson normaltest p-values for sums n=1..1024, M=20000 reps; skew/excess-kurtosis tracked.
- **Data:** Uniform normal by n≈16; exponential by n≈1024 (p=5e-3); Bernoulli n≈512; **Pareto a=3 never passes** (p≈1e-297 at n=1024). Skew decays ~n^-1/2 (Exp: 1.99→0.48→0.18), kurtosis ~1/n.
- **Break:** finite-variance heavy tails converge arbitrarily slowly; normaltest has huge power at M=20000 so "reject" ≠ practically non-normal.
- **Lesson:** CLT is asymptotic; check moments, not just n.

## Exp 3 — Estimator bias (`exp3_estimator.py`)

- **Hypothesis:** MLE variance is biased, the unbiased version fixes it; std is unbiased too.
- **Data:** Var bias ddof=0 = -σ²/n exactly (-2.0 at n=2); ddof=1 unbiased but **MSE larger** (32.1 vs 12.0 at n=2). E[s]=σ·c4: -20.2% at n=2, -2.8% at n=10. p-hat unbiased, sd matches √(p(1-p)/n). Cauchy: mean-of-means sd=21684 vs median-of-medians sd=0.16.
- **Break:** "unbiased" is not "accurate"; sqrt breaks unbiasedness (Jensen).
- **Lesson:** report MSE, not just bias; use median/robust estimators for heavy tails.

## Exp 4 — Bayesian vs frequentist (`exp4_bayes.py`)

- **Hypothesis:** posterior ≈ CI; both degrade at small n, differently.
- **Data:** k=3,n=10: Beta(10,10) prior → posterior mean 0.43 vs MLE 0.30; Beta(1,50) → 0.03. Wald coverage p=0.05,n=20: **0.64** (Wilson 0.975); at p=0.5 Wald 0.96. Lindley-lite: z=1 (p=0.32) gives Bayes factor 0.16 favoring H0.
- **Break:** Wald interval is anti-conservative exactly where it's used most (rare events, small n). Priors are not neutral — Beta(50,50) is a strong claim.
- **Lesson:** Wilson/Agresti-Coull or Beta posterior; state your prior; p-values and BFs answer different questions.

## Exp 5 — Information theory (`exp5_infotheory.py`)

- **Hypothesis:** Huffman ≈ H+1 bit; real compressors beat order-0 entropy via context; plug-in estimators are biased.
- **Data:** Huffman 2.230 vs H=2.202 bits/sym (redundancy 0.028). TOOLS.md (4448 B): order-0 H=5.41 bits/B → bound ~3010 B; zlib=2263 B (4.07 bits/B); order-1 conditional H≈3.51 bits/char. Plug-in entropy bias: -0.176 bits @ n=100, -0.017 @ n=1000 (true 4.176). Plug-in MI for **independent** vars: 0.067 bits (k=4,n=100), **1.49 bits (k=16,n=100)** — matches Miller-Madow bias (k-1)²/(2n ln2).
- **Break:** plug-in MI/entropy on small samples manufactures structure that isn't there — a "discovery" of dependence can be pure bias.
- **Lesson:** entropy is a functional of the distribution, not the sample; use NSB/Miller-Madow corrections or holdout data.

## Exp 6 — Testing traps (`exp6_testing.py`, `exp6b_fix.py`)

- **Hypothesis:** multiple comparisons + optional stopping inflate false positives.
- **Data:** 20 null correlations → P(≥1 sig)=**0.652**; mean 0.98 false positives/study. Bonferroni α=0.0025 → family-wise 0.042 but power for r=0.3,n=50 drops 0.57→0.18. Sequential peeking (10 obs/batch, stop at p<0.05, max 100): **every** null study terminates "significant" at mean n=87.7 vs fixed-n FPR 0.045.
- **Break:** the file-drawer/peeking protocol guarantees a publishable result from pure noise.
- **Lesson:** pre-register, correct for multiplicity (or use FDR), never peek without α-spending (e.g., O'Brien-Fleming).

### Exp 6b fix note
First run had a generation bug (y decorrelated from x → power≈α). Fixed: y=0.3x+√0.91·ε gives power 0.570 uncorrected.

## Exp 7 — Randomness quality (`exp7_randomness.py`, `exp7b_fix.py`)

- **Hypothesis:** modern RNGs pass standard tests; weak PRNGs don't.
- **Data:** numpy PCG64 bytes: χ²=241.5 p=0.72; lag-1 r=-0.0015 p=0.51. os.urandom χ² p=0.17. Runs test p=0.006 (borderline — one of several tests, consistent with chance at family level). LCG high bits pass χ² (p=0.32) BUT low byte has **period 256** — bytes[0:20] == bytes[256:276] exactly.
- **Break:** marginal uniformity ≠ randomness; LCG low-order bits cycle trivially. MT19937: same seed → identical output (verified); period 2^19937-1 but state recoverable from 624×32-bit outputs — fine for sims, fatal for crypto.
- **Lesson:** test the bits you actually use; never use MT/LCG for security.

## Exp 8 — Regression pitfalls (`exp8_regression.py`, `exp8c.py`)

- **Hypothesis:** pooled association ≠ conditional association when treatment allocation correlates with a confounder.
- **Data:** S~Bern(0.5); P(T=1|S=0)=0.9, P(T=1|S=1)=0.1; Y=2S+0.2T+ε. Within strata T-effect = +0.21/+0.20; **pooled = -1.40** (sign flip!). OLS omitting S gives -1.40; including S gives +0.20. Ice-cream vs drownings: r=0.66 → partial r≈-0.002 | temperature.
- **Break:** naive regression confidently reports a harmful treatment that is actually beneficial.
- **Lesson:** stratify/adjust for confounders; association is not causation; a noise covariate leaves coefficients intact (coef noise=0.001) but inflates variance.

## Files

- `exp1_montecarlo.py`, `exp1b_fix.py` — MC pi/needle/integrals/heavy tails
- `exp2_clt.py` — CLT convergence
- `exp3_estimator.py` — bias/MSE of variance, std, p-hat, median-vs-mean
- `exp4_bayes.py` — Beta-Binomial, CI coverage, prior sensitivity, Bayes factor
- `exp5_infotheory.py` — Huffman, zlib vs entropy orders, plug-in entropy/MI bias
- `exp6_testing.py`, `exp6b_fix.py` — p-hacking, Bonferroni, optional stopping
- `exp7_randomness.py`, `exp7b_fix.py` — χ²/serial/runs tests, LCG period, MT note
- `exp8_regression.py`, `exp8c.py` — Simpson's paradox, confounder, noise covariate
- `REPORT.md` — this file

## Issues encountered

- WSL VM hung once under a heavy Python loop; recovered via `wsl --shutdown`. All heavy sims kept under ~1 min.
- Three first-draft scripts had bugs (Buffon geometry range, decorrelated y in the power sim, int64 overflow in the runs test, Simpson confounding too weak) — fixed in `_fix`/`exp8c` files; results above are from corrected versions.

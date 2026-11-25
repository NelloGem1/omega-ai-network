# Bio/Chem/Data Science Lab — CREATE-AND-DESTROY Report
*Agent run: 2026-… · Python `/home/neilh/venv/bin/python` · scripts in `/home/neilh/science_lab/bio/`*

Public data fetched: NCBI efetch (human insulin mRNA NM_000207.3, 465 nt),
UniProt FASTA (insulin P01308, lysozyme P00698), sklearn iris (150×4).

**Note on `periodictable`:** the PyPI package `periodictable` (v2.1.0) is the
STFC *physics constants* tables — it has no electronegativity/ionization data.
Used **`mendeleev` 1.4.0** for the chemistry periodic table instead.

---

## EXP1 — Periodic trends (`exp1_periodic.py`, `periodic_heatmap.png`)
- **Hypothesis:** atomic radius decreases across a period and increases down a
  group; eneg/IE1 show the inverse; d-block and f-block break the pattern.
- **Method:** `mendeleev.get_all_elements()` → 67 elements with complete
  radius/eneg/IE1. Per-period OLS fit `radius = a + b·group` (main groups only);
  heatmap of all three properties over period×group.
- **Findings:** main-group radius vs group fits well (mean R²=0.886, slopes
  ≈ −4.5 to −5.9 pm/group); eneg rises monotonically across p2/p3
  (e.g. p2: Li 0.98 → F 3.98). Largest IE1 drops are exactly at group
  boundaries (F→Na −12.3 eV, Cl→K −8.6 eV). Lanthanide radii are nearly flat
  (175–195 pm, ~20 pm across 15 elements — the lanthanide contraction).
- **BREAK:** including d-block (groups 3–12) collapses the fit (R² 0.94→0.36–0.65)
  — filled d orbitals shield poorly, so "radius shrinks with group" is a
  main-group-only law.
- **Lesson:** periodic "laws" are regime-dependent; always state the element subset.

## EXP2 — DNA sequence statistics (`exp2_dna.py`)
- **Data:** human insulin CDS, 465 nt, fetched live from NCBI efetch.
- **Findings:** GC = 63.9% (vs 62.6% for an iid same-composition control);
  codon usage strongly biased (χ²=183, p≈7e-19); dinucleotide spectrum
  non-random (χ²=73.7, p≈1e-9) — CG strongly under-represented (0.32× expected,
  CpG suppression), TG/CT over-represented.
- **BREAK:** column-shuffling preserves GC% exactly but collapses the
  dinucleotide χ² to p=0.33 and halves windowed-GC variance (4.26→3.70).
  Composition statistics survive shuffling; *order* statistics do not.
- **Lesson:** GC% is a first-order property; dinucleotide/k-mer signals encode
  biology (codon structure, methylation) and are destroyed by shuffle.

## EXP3 — Protein analysis (`exp3_protein.py`)
- **Data:** UniProt FASTA — human insulin (110 aa, MW 11.98 kDa), hen lysozyme
  (147 aa, MW 16.24 kDa).
- **Findings:** charge@pH7 −3.4 (insulin, acidic) vs +8.5 (lysozyme, basic —
  consistent with its antimicrobial role); instability index 19.9 (lysozyme,
  stable) vs 40.3 (insulin proprotein, marginally unstable). Kyte-Doolittle
  window-9 hydrophobicity: neither is membrane protein → no TM helices
  predicted (correct — both are secreted globular proteins).
- **BREAK:** shuffled lysozyme keeps identical composition/MW/charge but
  instability index flips 19.9→42.8 (stable→unstable) and hydrophobicity
  autocorrelation at lag 10 drops 0.142→0.023. Charge/composition are
  shuffle-invariant; *stability and hydrophobic clustering are not*.
- **Lesson:** 1-D physicochemical profiles carry real structural signal that
  composition alone misses.

## EXP4 — Enzyme kinetics (`exp4_kinetics.py`, `kinetics.png`)
- **Hypothesis:** Michaelis-Menten v=Vmax·S/(Km+S); competitive inhibition
  raises apparent Km only; noncompetitive lowers Vmax only.
- **Method:** simulated noisy v(S), `curve_fit` for Vmax/Km; analytic inhibitor
  variants at I=Ki; Lineweaver-Burk cross-check.
- **Findings:** recovered Vmax=100.4±0.6 (true 100), Km=5.25±0.15 (true 5).
  Competitive: v/v0 →0.91 at high [S] (Vmax preserved); noncompetitive: flat
  0.50 at all [S] (Vmax halved). Clean mechanistic discrimination.
- **BREAK:** substrate inhibition (v declines at high S, peak at [S]=8.6,
  v(50)/v(peak)=0.49) fitted with plain MM gives Vmax=34.4, Km=0.24 — wildly
  biased. Fitting the correct substrate-inhibition model recovers
  Vmax=100.0, Km=5.00, Ki=15.0 exactly. Wrong model → wrong parameters,
  confidently.
- **Lesson:** residual structure at high [S] is the diagnostic; model misspecification
  is silent unless you check residuals.

## EXP5 — SIR/SIRS epidemiology (`exp5_sir.py`, `sir_sirs.png`)
- **Hypothesis:** R0=β/γ controls outbreak size; waning immunity (SIRS) permits
  endemic persistence; seasonal forcing produces sustained oscillations.
- **Method:** `solve_ivp` (rtol=1e-8), β=0.4, γ=0.1 (R0=4), 160-day horizon;
  R0 sweep; SIRS with w=0.02 (mean immunity 50 d); forced SIRS with
  β(t)=β0(1+0.3·cos(2πt/365)).
- **Findings:** SIR peak prevalence 40.4% at day 27, final attack rate 98%
  (herd-immunity threshold 75% — recovered R=98% matches theory). R0 sweep:
  R0≤1 → ~0% attack; R0=1.5 → 53%; R0=4 → 98%; R0=10 → 100%.
- **BREAK:** SIRS does *not* give persistent oscillations — it decays to a
  stable endemic equilibrium (I≈12.5% for w=0.02). Only 2 damped transient
  peaks. Adding seasonal β(t) forcing produces sustained annual oscillations
  (I swinging 21–27%). Honest negative result: simple SIRS equilibrates;
  oscillations need an external driver.
- **Lesson:** "endemic oscillations" require forcing (seasonality, variants);
  waning immunity alone → stable endemic state.

## EXP6 — Phylogenetics-lite (`exp6_phylo.py`)
- **Method:** simulated 600-nt sequences on a known 5-taxon tree (per-branch
  mutation rates), Hamming distances, hand-rolled UPGMA.
- **Findings:** recovered `(outgroup,((human,chimp),(gorilla,orangutan)))` —
  exactly the simulated topology; human–chimp distance 0.043 ≪ human–gorilla
  0.168, as expected.
- **BREAK:** independent shuffling of each sequence explodes mean pairwise
  distance 0.19→0.75 and collapses variance 0.0078→0.0002 — every pair becomes
  equidistant, so UPGMA yields a star-like meaningless tree.
- **Lesson:** phylogenetic signal = *conserved positions*; distance methods are
  only as good as the alignment's conserved columns.

## EXP7 — Iris EDA (`exp7_iris.py`, `iris_pca.png`)
- **Findings:** petal_length/petal_width correlate 0.96 (redundant);
  sepal_width nearly uncorrelated with everything (−0.1…−0.4). PCA-2D explains
  95.8% of variance (PC1 73%). Shapiro tests: sepal_length, petal_length,
  petal_width are NON-normal (mixtures of 3 species — expected). IQR flags 4
  sepal_width outliers; |z|>3 flags 1. Most extreme samples are virginica/setosa
  boundary cases, not errors.
- **Lesson:** iris "outliers" are mostly class-boundary points; non-normality is
  an artifact of pooling species — check per-class before calling anomalies.

---

## Summary table
| # | Experiment | Headline result | Break result |
|---|-----------|-----------------|--------------|
| 1 | Periodic trends | radius~group R²≈0.89 main groups | d-block collapses fit (R²→0.36) |
| 2 | DNA stats | CpG suppressed 0.32×, codon bias p~1e-19 | shuffle kills order stats, keeps GC% |
| 3 | Proteins | insulin −3.4 / lysozyme +8.5 @pH7 | shuffle flips stability index |
| 4 | Kinetics | Vmax/Km recovered ±1% | substrate inhibition → MM fit biased 3× |
| 5 | SIR/SIRS | R0=4 → 98% attack rate | waning immunity → stable eq., not oscillations |
| 6 | Phylo-lite | UPGMA recovers true topology | shuffle → equidistant star tree |
| 7 | Iris EDA | PCA-2D = 95.8% var; petal dims r=0.96 | "outliers" are class-boundary points |

**Files:** `exp1_periodic.py … exp7_iris.py`, `periodic_heatmap.png`,
`kinetics.png`, `sir_sirs.png`, `iris_pca.png`.

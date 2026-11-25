# AUTOPSY — Bio/Chem Lab (periodic trends / DNA / protein / kinetics / SIR-SIRS / phylo / iris)
*Forensic re-run. Live data refetched from NCBI efetch + UniProt REST during autopsy — all reproduced.*

## EXP1 — Periodic trends — **VERIFIED**
Re-ran exp1_periodic.py (mendeleev 1.4.0): 67 elements; per-period main-group radius fits mean R²=**0.886** (report 0.886), slopes −4.4 to −5.9 pm/group (report "≈−4.5 to −5.9" — period-3 slope is −4.4, trivially outside the stated range). Enig p2: Li 0.98 → F 3.98 ✓. IE1 boundary drops F→Na −12.28, Cl→K −8.63 eV ✓. Lanthanide radii 175–195 pm ✓. BREAK: d-block inclusion collapses R² to 0.654 (p4) / 0.363 (p5) vs main-only 0.935/0.939 — report's "0.94→0.36–0.65" exact.

## EXP2 — DNA sequence statistics — **VERIFIED** (one wording overstatement)
Live refetch of NM_000207.3 (465 nt) reproduces every number: GC 63.87% vs iid-control 62.58%; codon χ²=183.2, p=6.67e-19; dinucleotide χ²=73.7, p=9.63e-10; CG at 0.32× expected; TG/CT over-represented; shuffle → dinuc p=0.328, GC% preserved.
- **Minor discrepancy:** report says shuffle "halves windowed-GC variance (4.26→3.70)". Those are **standard deviations**: 4.26→3.70 is a ~13% std / ~24% variance reduction — "halves" overstates it. Direction correct, magnitude wrong.
- Methodological note: codon χ² is computed only over observed codons with expected counts renormalized — acceptable but slightly favorable vs a full 64-codon test.

## EXP3 — Protein analysis — **VERIFIED**
Live UniProt refetch reproduces: insulin P01308 = 110 aa, MW 11,980.8 Da, charge@pH7 −3.37, instability 40.3; lysozyme P00698 = **147 aa** (report correct — my prior was wrong), MW 16,238.5 Da, charge +8.50, instability 19.9. Shuffled lysozyme: instability 19.9→42.8, lag-10 hydrophobicity autocorr 0.142→0.023 — exact. No TM helices predicted for either (correct: both secreted globular). Note: charge@pH7 is essentially shuffle-invariant (8.50→8.46) as claimed.

## EXP4 — Enzyme kinetics — **VERIFIED** (exact reproduction)
Re-ran: MM fit Vmax=100.4±0.6, Km=5.25±0.15 (true 100/5); competitive v/v0→0.911 high-S vs noncompetitive flat 0.500; substrate-inhibition peak at [S]=8.6 (=√(Km·Ki)=√75), v(50)/v(peak)=0.486≈0.49; plain-MM fit on inhibited data → Vmax=34.4, Km=0.24 (wildly biased ✓); correct SI model recovers Vmax=100.0, Km=5.00, Ki=15.0 exactly. Lineweaver-Burk cross-check Vmax=99.0, Km=4.94 also printed.

## EXP5 — SIR/SIRS — **VERIFIED** (honest negative result confirmed)
Re-ran: SIR peak 40.4% at day 27, final R=98.0%, herd threshold 75% ✓. R0 sweep: 0.8→0.5%, 1.0→1.6%, 1.5→52.6%, 4→98%, 10→100% ✓. SIRS w=0.02: post-transient I pinned at 12.50% (stable endemic eq, min=max=mean), exactly 2 damped transient peaks ✓. Seasonal forcing (note: forced run uses w=0.05, not 0.02 — report doesn't specify): 2 sustained annual peaks, late I range 21.1–27.0% ✓.

## EXP6 — Phylogenetics-lite — **VERIFIED** (exact reproduction)
Re-ran: pairwise distances human–chimp 0.043 ≪ human–gorilla 0.168; UPGMA recovers `(outgroup,((human,chimp),(gorilla,orangutan)))` — exact simulated topology. Shuffle break: mean pairwise 0.194→0.747, variance 0.0078→0.0002 ✓. (The script's `checks` prints are sloppy — `or True` — but the printed Newick tree is correct and is what the report cites.)

## EXP7 — Iris EDA — **VERIFIED**
Re-ran: petal_length/petal_width r=0.96; sepal_width correlations −0.12/−0.43/−0.37; PCA-2D 95.8% (PC1 73.0%); Shapiro non-normal for sepal_length (p=0.010), petal_length (7.4e-10), petal_width (1.7e-8); sepal_width normal (p=0.101). IQR outliers: 4× sepal_width; |z|>3: 1. Most extreme samples are virginica/setosa boundary points ✓.

---
## Lab verdict
**Clean sheet.** All 7 experiments independently reproduced, including the live NCBI/UniProt fetches. Only flaws are cosmetic: "halves windowed-GC variance" overstates a ~24% variance drop (EXP2), and EXP6's self-check prints are vacuous (`or True`) though the actual tree output is correct.

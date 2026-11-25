# AUTOPSY — science_lab/ml (forensic re-verification)

*Method: read every file, re-ran all three experiment scripts end-to-end in
`/home/neinh/venv` (sklearn 1.9.1 / numpy 2.5.5 / torch 2.15.0 CPU). All runs
are seed-deterministic (random_state=42 / default_rng(42) / torch.manual_seed(42)).
Prior-art context: `/home/neilh/gh_backup/science/data-collection/EXPERIMENT_DIGEST.md`
(note: the live path `/home/neilh/science/data-collection/EXPERIMENT_DIGEST.md`
does not exist — only the gh_backup copy). This lab EXTENDS the digest's ML
section (FGSM, overfit, poisoning, drift) rather than repeating it — all 8
experiments here are new variants/additions. Nothing below repeats digest work.*

## Verdicts

### EXP 1 — Baseline comparison: **VERIFIED**
Re-ran `exp1_2_baseline_overfit.py`. All accuracies reproduce exactly:
LogReg 0.9622, RF(200) 0.9667, MLP 0.9578; confusion matrix identical
(digit 8 hub: 5 errors → {1:3, 7:1, 3:1}; digit 9: 3; digit 5: 2 — matches
REPORT lines 31–34 and `exp1_2_output.txt` lines 22–30).
Timings differ under load (MLP fit 10.6s vs reported 2.6s) — irrelevant,
accuracy/gap are the claims. RF-vs-LogReg inference ratio ~140× confirmed
(253µs vs ~2–4µs; ratio is timing-sensitive but order is right).

### EXP 2 — Overfitting sweep: **VERIFIED**
Full 3×3 Ridge sweep reproduces `exp1_2_output.txt` bit-for-bit
(deg2/α0.01: train 1.0000 / val 0.1911 / gap +0.8089; deg3 val 0.5556).
LogReg+poly stays ≤3.6pt gap — confirmed. No leakage: StandardScaler and
PolynomialFeatures are `fit` on train only (lines 68–75). Ridge-on-labels
caveat is honestly flagged in the script's own NOTE.

### EXP 3 — FGSM adversarial: **VERIFIED**
Re-ran: clean 0.9689 → ε=0.05: 0.8178, ε=0.1: 0.5311, ε=0.2: 0.0267,
ε=0.5: 0.0000 — identical to `exp3_4_5_output.txt`. Gradient direction is
correct (x + ε·sign(∇loss), ascending — the right sign for untargeted FGSM;
clamped to [0,1] after /16 scaling). Per-sample gradients correct (single
batched backward over the test set).

### EXP 4 — Label poisoning: **VERIFIED** (one wording nit)
Reproduced exactly: 5%→0.8844, 10%→0.8956, 20%→0.8844 test acc; poisoned-label
agreement on flipped samples = 7.5%. Non-monotonicity (10% better than 5/20%)
is real — different flip sets, small n. REPORT interprets correctly
("rejects the poison"). NIT: the script's own print says "it memorized the
lie" — the opposite of what 7.5% agreement means; REPORT got it right anyway.

### EXP 5 — Concept drift: **VERIFIED** (one overstatement)
Reproduced: in-domain 0.9956, unseen 5–9 = 0.0000, histogram
[131 98 27 479 161], retrain 0.9622. NIT: the "remap 0–4→5–9 = 19.2%
upper bound" (REPORT line 110) is a *single arbitrary +5 label shift*, not
a bound over permutations — a Hungarian best-mapping could score differently.
Harmless direction (still ≪ in-domain), but "upper bound" is mislabeled;
call it "one fixed relabeling".

### EXP 6 — Unsupervised KMeans/PCA: **VERIFIED**
Re-ran: ARI 0.6489, purity 0.7832, cluster→digit table identical,
PC1–3 = 0.401, PC1–10 = 0.738 — all exact. Hungarian mapping via
`linear_sum_assignment` is correct; KMeans/PCA fit on train split only.

### EXP 7 — NLP-lite 20news: **VERIFIED**
Re-ran: train=1073/test=713, acc 0.8710 exact; feature lists identical.
Proper train/test split, TF-IDF+LogReg pipeline, no leakage.

### EXP 8 — Distillation: **VERIFIED**
Re-ran: teacher=student=oracle agreement 1.0000, test acc 0.9622 both.
Honest framing: this shows a *linear* teacher is perfectly self-distillable
— the "extraction" claim is appropriately scoped in REPORT.

## Lab verdict: **CLEAN** — 8/8 experiments verified by re-run; numbers in
REPORT.md match raw outputs exactly. Only cosmetic nits (EXP5 "upper bound"
labeling, EXP4 print-string irony). `adversarial_digits.png` regenerated.

# ML Create-and-Destroy Lab — REPORT

*All experiments run on WSL Ubuntu with `/home/neilh/venv/bin/python`
(sklearn 1.9.1, numpy 2.5.5, torch 2.15.0 CPU). Dataset: sklearn `digits`
(1797×64) unless noted. Scripts + raw outputs in this directory.*

| # | Experiment | Script | Headline result |
|---|-----------|--------|-----------------|
| 1 | Baseline comparison | `exp1_2_baseline_overfit.py` | RF best: **96.7%** test; digit **8** most confused |
| 2 | Overfitting sweep | same | Ridge poly-2: train 100% / val **19%** — gap **+81pts** |
| 3 | FGSM adversarial | `exp3_4_5_attack_poison_drift.py` | ε=0.5 → accuracy **0.0%** (from 96.9%) |
| 4 | Label poisoning | same | 20% flipped labels → only ~8pt test drop (LogReg robust) |
| 5 | Concept drift | same | train 0–4 / test 5–9 → **0%**; retrain recovers to 96.2% |
| 6 | Unsupervised | `exp6_7_8_unsup_nlp_distill.py` | KMeans ARI **0.649**, purity 78.3%; PCA-2 = 28% var |
| 7 | NLP-lite | same | 20news 2-class TF-IDF acc **87.1%** |
| 8 | Distillation | same | student↔teacher agreement **100%** (linear model fully cloned) |

---

## EXP 1 — Baseline models (hypothesis: ensembles beat linear)

**Method:** 75/25 stratified split; LogisticRegression, RandomForest(200),
MLP(128,64); measured fit time + per-sample inference latency.

| Model | Train acc | Test acc | Gap | Fit | Inference |
|---|---|---|---|---|---|
| LogisticRegression | 1.0000 | 0.9622 | +3.8pt | 1.1s | **1.6 µs** |
| RandomForest(200) | 1.0000 | **0.9667** | +3.3pt | 0.9s | 224 µs |
| MLP(128,64) | 0.9777 | 0.9578 | +2.0pt | 2.6s | 5.7 µs |

**Confusion analysis:** digit **8** is the hub of confusion (5 errors →
predicted as 1, 7, 3), then 9 (3 errors) and 5 (2 errors). Loop-y digits
(8, 9, 5, 6, 0) confuse with each other; straight-line digits (1, 7) are
nearly perfect. Classic stroke-topology failure.

**Break:** RF wins accuracy but is **140× slower** per inference than
logreg — accuracy isn't free.
**Lesson:** pick by the metric that matters; on this clean tabular-ish
image data all three are within 1pt.

## EXP 2 — Overfitting live (hypothesis: capacity × features → memorization)

**Method:** PolynomialFeatures degree {1,2,3} × Ridge alpha
{0.01, 1, 100}, plus LogReg+poly as sanity check.

| Degree | Alpha | Train | Val | Gap | Features |
|---|---|---|---|---|---|
| 1 | any | 0.24 | 0.23 | +2pt | 64 |
| 2 | 0.01 | **1.0000** | **0.1911** | **+81pt** | 2,144 |
| 2 | 100 | 0.757 | 0.491 | +27pt | 2,144 |
| 3 | 0.01–100 | 1.0000 | 0.556 | +44pt | 47,904 |

**Break:** degree-2 poly with light regularization memorizes the training
set completely while generalizing *worse than chance-ish* (19%). Raising
alpha to 100 shrinks the gap 3× — regularization is the brake pedal.
LogReg+poly stayed flat (~96–97% val, gap ≤3.6pt) because C=10 + L2
already regularizes; capacity alone didn't break it.
**Lesson:** the train/val gap is the overfitting *thermometer* — watch it,
not just val accuracy.

## EXP 3 — Adversarial attack (hypothesis: tiny L∞ perturbations flip predictions)

**Method:** trained a torch MLP (128→64) on digits (clean acc 96.9%),
then FGSM: `x' = x + ε·sign(∇ₓ loss)`.

| ε | Test acc | Drop |
|---|---|---|
| 0.0 | 0.9689 | — |
| 0.05 | 0.8178 | −15.1pt |
| 0.1 | 0.5311 | −43.8pt |
| 0.2 | 0.0267 | −94.2pt |
| 0.5 | **0.0000** | −96.9pt |

**Break:** at ε=0.2 (pixel values perturbed by ≤20% of range — visually
still digit-like, see `adversarial_digits.png`) the model collapses to
2.7%. At ε=0.5 accuracy is literally zero.
**Lesson:** neural nets learn brittle features; gradient-aligned noise is
a loaded gun. Defenses: adversarial training, input denoising,
certified robustness.

## EXP 4 — Data poisoning (hypothesis: flipped labels degrade the model)

**Method:** flip 5/10/20% of *training* labels to wrong digits, retrain
LogReg, measure test acc; also measured how often the poisoned model
agrees with the *poisoned* labels on flipped samples.

| Poison | Test acc | Drop vs clean (96.2%) |
|---|---|---|
| 5% | 0.8844 | −7.8pt |
| 10% | 0.8956 | −6.7pt |
| 20% | 0.8844 | −7.8pt |

Surprising: **decay saturates ~8pt** — LogReg's global linear boundary
can't be locally hijacked the way a memorizing model can. The poisoned
model agrees with the false labels on only **7.5%** of flipped samples —
it mostly *rejects* the poison rather than memorizing it.
**Break:** try this on a high-capacity model (RF/deep net) or targeted
poisoning (flip only one class pair) — damage would be much worse.
**Lesson:** simple models are incidentally robust to random label noise;
the attack surface is memorization capacity + targeted flips.

## EXP 5 — Concept drift (hypothesis: unseen classes = total failure)

**Method:** train on digits 0–4 only, evaluate on held-out 0–4 (in-domain)
vs digits 5–9 (domain shift); then retrain on all digits.

- In-domain val acc: **99.56%**
- Unseen 5–9 raw: **0.00%** (model can only emit labels 0–4 — every
  prediction is structurally wrong)
- Remap upper bound (0–4→5–9): 19.2% — even relabeling can't save it;
  the features themselves are unseen
- Predicted-label histogram on 5–9: `[131 98 27 479 161]` — everything
  collapses toward digit 3
- After retrain on all digits: **96.2%** — fully recovered

**Break:** new classes don't degrade gracefully, they *annihilate* —
the model confidently mislabels every single unseen sample.
**Lesson:** monitor for novel inputs (confidence scores, out-of-distribution
detectors); drift repair requires new data, not just retraining on old.

## EXP 6 — Unsupervised structure (hypothesis: pixels cluster by digit)

**Method:** KMeans(k=10) on raw train pixels + Hungarian cluster→digit
mapping; PCA on 64-d pixel space.

- **ARI = 0.649** (0=random, 1=perfect); cluster purity after best
  mapping = **78.3%**
- Clusters 6,4,5,0,7 are pure (>95% single digit); clusters 0 (digit 9)
  and 1 (digit 8) are polluted — visually similar loops merge
- PCA: PC1=14.6%, PC1–2=28.4%, PC1–3=40.1%, PC1–10=73.8% of variance

**Break:** KMeans recovers *shape families* (loops vs. strokes) but can't
split look-alikes (8↔9, 3↔5) — unsupervised has no label signal for
fine distinctions.
**Lesson:** ARI 0.65 means clusters carry real but lossy class info —
good for exploration/pretraining features, not for classification.

## EXP 7 — NLP-lite (hypothesis: TF-IDF separates atheism vs space)

**Method:** `fetch_20newsgroups` (alt.atheism vs sci.space),
TF-IDF (20k feats, 1–2 grams, english stopwords) + LogReg.

- Test acc = **87.1%** (713 test docs)
- Top features class 'alt.atheism': god, religion, bible, atheism,
  islam, morality, objective…
- Top features class 'sci.space': space, nasa, moon, orbit, launch,
  earth, spacecraft, shuttle, lunar…

**Break:** the model is a bag-of-words zealot — "god" or "nasa" alone
nearly decides the class; sarcasm, mixed-topic posts, or adversarial
keyword stuffing would fool it.
**Lesson:** interpretability is free with linear models — the feature
weights ARE the explanation.

## EXP 8 — Distillation / extraction-ish (hypothesis: student can clone teacher)

**Method:** LogReg teacher trained on true labels; student trained only
on teacher's predictions over the training inputs. Compared agreement
on held-out test.

- Teacher test acc: 96.22% — Student test acc: **96.22%**
- Teacher/student agreement on test: **100.00%**
- Student vs oracle-trained model agreement: **100.00%**

**Break:** for a linear teacher, distillation is *perfect* — the
student recovers the identical decision boundary. Model extraction of
logreg is trivial; the defense isn't secrecy of weights, it's that
linear models are simple. Nonlinear teachers (RF/NN) leak less per
query but more queries still clone them.
**Lesson:** "model stealing" needs no gradients — just prediction access
+ enough queries. Assume any served model is extractable.

---

## Cross-cutting lessons

1. **Measure before trusting** — every "break" here was quantified
   (acc drop, ARI, gap), not vibes.
2. **Capacity is the attack surface** — overfitting, poisoning
   memorization, and adversarial brittleness all scale with model
   flexibility; regularization and simple models are free robustness.
3. **Distribution shift is the silent killer** — FGSM is loud, drift is
   quiet: 99.6% in-domain → 0% out-of-domain with no warning.
4. **Linearity cuts both ways** — LogReg is poison-robust AND
   perfectly extractable; there's no free lunch, only trade-offs.

## Artifacts

- `exp1_2_baseline_overfit.py` + `exp1_2_output.txt`
- `exp3_4_5_attack_poison_drift.py` + `exp3_4_5_output.txt`
- `exp6_7_8_unsup_nlp_distill.py` + `exp6_7_8_output.txt`
- `adversarial_digits.png` — clean vs ε=0.1 / ε=0.5 FGSM examples
  (row 0: true label; rows 1–2: predicted label after attack)

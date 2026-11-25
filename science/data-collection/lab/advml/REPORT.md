# REPORT — PGD attack + defense arms race (MNIST MLP, CPU)

## Hypothesis
Escalating from single-step FGSM to iterative PGD (eps=0.3) should break defenses that only
survived FGSM; conversely, defenses matched to attack strength (PGD-adversarial training)
or that destroy perturbation structure (input quantization) should hold up.

## Prior work (EXPERIMENT_DIGEST.md)
- FGSM eps=0.5 dropped MNIST MLP acc 96.9% -> 0.0%; eps=0.3 on Colab T4: 0.949 -> 0.000.
- FGSM-based adversarial training recovered to ~71% under FGSM. Untested vs iterative attacks.
- This experiment EXTENDS: adds PGD, tests whether 71% holds, adds PGD-AT and preprocessing defenses.

## Method
- Data: MNIST, normalized ((x-0.1307)/0.3081). Train subset 20,000 / test 3,000 (CPU-friendly).
- Model: MLP 784->256->128->10, ReLU, Adam lr=1e-3. Baseline + FGSM-AT: 4 epochs.
  PGD-AT: weak inner attack (alpha=0.01, 10 steps) 3 epochs; strong inner attack
  (alpha=0.03, 20 steps) 4 epochs.
- Attacks (all eps=0.3, random start in L-inf ball):
  - FGSM: 1 step, alpha=eps.
  - PGD-spec: 10 steps, alpha=0.01 (mission spec — weak: max travel 0.1 < eps).
  - PGD-strong: 30 steps, alpha=0.05 (properly uses the eps=0.3 budget).
  - Attacks on preprocessing defenses are ADAPTIVE (gradient flows through the
    transform; bit-depth uses straight-through estimator).
- Defenses: (a) FGSM-AT model vs PGD; (b) PGD-adversarial training; (c) input
  preprocessing on the undefended model: 3-bit depth reduction, 3x3 avg-pool smoothing.

## BUG FOUND & FIXED (important for fleet)
First PGD implementation used x - alpha*sign(grad) i.e. gradient DESCENT on the loss —
it made inputs MORE classifiable (adv acc rose to 1.0 on a random net). PGD must ASCEND
the loss: x + alpha*sign(grad). Same sign error existed in PGD-AT training. Fixed in
experiment.py, eval_strong.py, round3.py. Lesson: sanity-check attack direction on a
random-weight net before trusting any attack/defense number.

## Results — attack-vs-defense matrix (test accuracy under attack; higher = defense holds)

| defense                  | clean | FGSM  | PGD-10 (spec) | PGD-30 (strong) |
|--------------------------|-------|-------|---------------|-----------------|
| none (baseline)          | 0.956 | 0.052 | 0.697         | 0.018           |
| FGSM-adversarial training| 0.956 | 0.739 | 0.910         | 0.681           |
| PGD-AT (weak inner)      | 0.952 | 0.511 | 0.879         | 0.366           |
| PGD-AT (strong inner)    | 0.944 | 0.756 | 0.904         | 0.718           |
| + 3-bit depth reduction  | 0.953 | 0.758*| 0.920         | 0.734           |
| + 3x3 avg-pool smoothing | 0.951 | 0.118*| 0.740         | 0.056           |

* adaptive attack through the preprocessor (FGSM column: adaptive for smooth=0.118;
naive FGSM on bitdepth = 0.758). PGD columns are always adaptive.

## Breaks / surprises
1. Mission-spec PGD (alpha=0.01 x 10 steps) is nearly toothless: it can travel at most
   0.1 in L-inf vs the 0.3 budget — FGSM (one 0.3 step) beats it on every defense.
   Iterative attacks need alpha ~ eps/steps or more steps to matter.
2. FGSM-AT's '71% recovery' does NOT hold vs strong PGD in absolute terms — it retains
   68.1%, essentially matching strong PGD-AT (71.8%) and 3-bit quantization (73.4%)
   at a fraction of the training cost.
3. PGD-AT with a WEAK inner attack (matching the spec) is worse than FGSM-AT vs strong
   PGD (36.6% vs 68.1%): adversarial training must match or exceed attacker strength.
   Strengthening the inner attack (alpha=0.03, 20 steps) fixes it -> 71.8%.
4. 3-bit depth reduction is the best cost/benefit defense here: no retraining, ~equal
   to strong PGD-AT under strong PGD and FGSM. Smoothing is nearly useless vs PGD
   (5.6%) though it blunts naive FGSM.
5. Note: quantization defense evaluated with STE gradients; a quantization-aware
   attacker (e.g. optimizing over discrete levels or Expectation-Over-Transformation)
   might do better — open extension.

## Lesson
The arms race is about attack/defense MATCHING, not raw strength: iterative PGD >> FGSM,
but a cheap input-quantization defense or correctly-matched adversarial training
recovers most accuracy. Also: verify attack implementations on random nets first —
a sign error silently turns an attack into a defense booster.

## Files
- experiment.py — round 1 (spec PGD; sign bug fixed post-hoc, results in results.json are pre-fix/invalid for PGD rows)
- eval_strong.py — corrected attacks, full matrix -> results2.json, run2.log
- round3.py — strong-inner PGD-AT -> results3.json, run3.log
- results.json / results2.json / results3.json — raw numbers

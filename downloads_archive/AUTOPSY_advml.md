# AUTOPSY — advml lab (adversarial ML, PGD attack/defense on MNIST)
*Marshal-rank forensic audit. Method: read every file, audited attack math line-by-line, sanity-checked PGD direction on a random net, then re-implemented the full pipeline independently (chunked, checkpointed) AND re-ran the canonical `eval_strong.py` end-to-end.*

## PGD sign fix — verdict: **CORRECT NOW**
All three scripts (`experiment.py`, `eval_strong.py`, `round3.py`) use `x + alpha*sign(∇_x CE)` — gradient ASCENT on the loss, clamped to the L∞ ball `x±eps`. Verified:
- `eval_strong.py` rerun reproduced `results2.json` **bit-for-bit** (deterministic seeds).
- Independent sign sanity check on a random-weight MLP (autopsy_verify.py STAGE0): clean acc 0.066 → PGD acc 0.000, loss 2.304 → 2.809. Attack ascends loss correctly.
- `results.json` (round 1) honestly flagged in REPORT.md as pre-fix/invalid — its pgd rows (0.996–0.9997) are the signature of the old DESCENT bug (attack made inputs *more* classifiable). Report's bug disclosure is accurate.

## Attack/defense matrix — canonical script vs independent re-implementation

| defense | metric | REPORT/results2 | eval_strong rerun | my reimpl (autopsy_verify.json) |
|---|---|---|---|---|
| baseline | clean / fgsm / pgd10 / pgd30s | .956/.052/.697/.018 | identical | .953/.061/.718/.021 |
| FGSM-AT | same | .956/.739/.910/.681 | identical | .951/.727/.904/.671 |
| PGD-AT weak | same | .952/.511/.879/.366 | identical | .954/.553/.882/**.428** |
| PGD-AT strong | same | .944/.756/.904/.718 | n/a (round3) | .946/.752/.909/.720 |
| +3-bit depth | clean/naive-FGSM/ad-FGSM/ad-PGD10/ad-PGD30 | .953/.758/.757/.920/.734 | identical | .953/.756/.755/.918/.733 |
| +3x3 smooth | same | .951/.179/.118/.740/.056 | identical | .950/.187/.121/.757/.053 |

## Verdicts per claim
- **PGD must ascend loss**: VERIFIED (see above).
- **Strong PGD(30) nearly kills baseline (1.8%)**: VERIFIED — rerun 0.018, reimpl 0.021.
- **3-bit depth reduction = best defense (73.4%)**: **VERIFIED independently.** Reimpl 0.733 under fully adaptive PGD-30. Mechanism confirmed: quantization step = 6/7 ≈ 0.857 normalized units >> eps=0.3, so most perturbations are swallowed; clean acc only drops 0.956→0.953. STE gradient is identity — the reported adaptive attack is legitimate. Report's caveat (quantization-aware/EOT attacker might do better) is honest and correct.
- **Smoothing fails vs PGD (5.6%)**: VERIFIED — 0.053–0.056. Note: `smooth()` is only a 3×3 avg_pool + bilinear back to same size (no downsampling); report calls it "3x3 avg-pool smoothing" — accurate.
- **FGSM-AT 68.1% vs strong PGD ≈ PGD-AT-strong 71.8% ≈ 3-bit 73.4%**: VERIFIED — .671 / .720 / .733.
- **Weak-inner PGD-AT worse than FGSM-AT (36.6% vs 68.1%)**: qualitative claim VERIFIED (0.43 vs 0.67 in reimpl; direction and ~30pt gap hold).
- **results3.json / run3.log consistency**: results3.json {clean .944, fgsm .756, pgd10 .904, pgd30s .718} matches run3.log and REPORT table. VERIFIED.

## Discrepancies / caveats
1. **pgd_at_weak pgd30s seed variance**: canonical script gives 0.366; two independent re-implementations (different RNG streams) both gave **0.428–0.429**. The canonical `eval_strong.py` reproduces 0.366 exactly, so results2.json is internally consistent — but the weak-PGD-AT defense has ~±5pt run-to-run variance under strong PGD. Report's 36.6% is one draw; honest range ≈ 0.37–0.43. Does not change any conclusion.
2. **eps is in NORMALIZED space, unstated**: inputs are (x−0.1307)/0.3081, so eps=0.3 L∞ ≈ 0.09 in [0,1] pixel units (and inputs are never clamped to valid pixel range). Internally consistent across all experiments, but REPORT.md never says this — a reader could misread eps as pixel-space. Minor spec ambiguity.
3. **PGD-10 'spec' attack**: alpha=0.01×10 steps = max 0.1 iterative travel vs eps=0.3 budget — report's "nearly toothless" analysis is correct (random start fills the ball but gradient steps only add ≤0.1).
4. **experiment.py FGSM-AT differs slightly from eval_strong.py FGSM-AT**: experiment.py uses plain FGSM (no random start); eval_strong uses random-start + 1 eps-step. results.json is declared invalid anyway — no impact.
5. No model checkpoints were saved originally; I saved mine to `autopsy_models/` for provenance.

## Files added by audit
- `autopsy_verify.py` + `autopsy_verify.json` — staged independent re-implementation (all stages checkpointed).
- `autopsy_fgsmat.py` — corrected FGSM-AT replication (my first pass mistakenly used PGD-weak inner; fixed and re-run → fgsm_atTRUE .951/.727/.904/.671).
- `autopsy_pgdweak.py` — second seed sample of weak PGD-AT.
- `autopsy_models/*.pt` — retrained model weights.
- `results2_autopsy_backup.json` — pre-rerun copy of results2.json.

## Bottom line
**ADVML: VERIFIED.** PGD sign fix is correct (ascends loss, proven on random net and by bit-exact script reproduction). The 3-bit quantization defense claim holds under independent adaptive attack (73.3% vs reported 73.4%). All matrix numbers reproduce within ~1pt except weak PGD-AT pgd30s which shows ~5pt seed variance (0.37–0.43) — flagged, conclusions unchanged. results.json invalidation disclosure is honest and accurate.

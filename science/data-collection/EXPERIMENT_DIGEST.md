# EXPERIMENT DIGEST — what the generals learned (all agents MUST read before starting)
## ML/AI agent (COMPLETE - 8 experiments)
- FGSM adversarial: clean acc 96.9% -> 0.0% at eps=0.5 (torch MLP, digits)
- Overfit proof: poly-deg2+Ridge a=0.01 -> train 100% / val 19.1%
- Label poisoning 5-20%: only ~7pt test damage (saturates - model robust)
- Concept drift train0-4/test5-9 -> 0% (retrain recovers 96.2%)
- KMeans ARI 0.649, purity 78.3%; PCA PC1-3 = 40% var
- TF-IDF+LogReg atheism-vs-space: 87.1%, interpretable features
- Distillation: student 100% agreement w/ teacher - models extractable
- RF 96.7% > LogReg 96.2% > MLP 95.8%; RF 140x slower inference
- Digit 8 = confusion hub (->1,7,3)
RULES FOR ALL AGENTS: read this file + sibling REPORT.md files first; cite prior results; never repeat a proven experiment - EXTEND it.

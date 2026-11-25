# 🧠 ML Data Pipeline — The 5 Things Everyone Forgets
*A field guide for the gaps between "I trained a model" and "I deployed a reliable one."*

> Companion lab: `science_lab/ml/lab_ml_pipeline.py` — every concept below has a runnable exercise.

---

## 1. Validation Split — THREE splits, not two

**The mistake:** train/test only → you tune on test → test stops being honest → deployed model surprises you.

```
raw data ──► TRAIN (fit the model)
          ──► VALIDATION (tune hyperparams, early stop, pick model)
          ──► TEST (final exam — touch ONCE at the end)
```

Typical ratios: 60/20/20 or 70/15/15. With little data use **k-fold cross-validation** on the train set instead of a fixed val split.

```python
from sklearn.model_selection import train_test_split
X_tr, X_tmp = train_test_split(X, test_size=0.4, stratify=y, random_state=42)
X_val, X_te = train_test_split(X_tmp, test_size=0.5, stratify=y, random_state=42)
```

**Golden rule:** the test set answers "how good is my FINAL model?" — never use it to make decisions.

---

## 2. Feature Engineering — raw data → useful inputs

Models can't see patterns you don't expose. Techniques:

- **Scaling** — StandardScaler/MinMax (essential for distance/SVM/neural nets)
- **Encoding** — one-hot for categories, target-encoding for high-cardinality
- **Polynomial/interaction** — `PolynomialFeatures` for nonlinear boundaries
- **Domain features** — ratios, logs, bins, text→TF-IDF, image→embeddings
- **Feature selection** — drop noise (mutual info, permutation importance)

```python
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
model = make_pipeline(StandardScaler(), PolynomialFeatures(2), LogisticRegression())
```

**Lab exercise:** digits accuracy before vs after scaling + poly features.

---

## 3. Regularization — stop the model memorizing

Overfitting = great train score, terrible real-world score. Fixes:

| Technique | What it does | sklearn knob |
|---|---|---|
| L2 Ridge | shrinks weights toward 0 | `Ridge(alpha=…)` |
| L1 Lasso | shrinks + zeroes useless features | `Lasso(alpha=…)` |
| ElasticNet | both | `ElasticNet` |
| Dropout | randomly kills neurons (NNs) | `Dropout(p)` in torch |
| Early stopping | halt when val loss rises | `EarlyStopping` callback |
| More data / augmentation | the real cure | — |

`alpha`/`C` is the dial: **higher alpha = simpler model**. Tune it on VALIDATION, never test.

**Lab exercise:** polynomial degree sweep — watch train↑ / val↓ = overfit signature.

---

## 4. Deployment & Monitoring — inference is not the end

A model in production is a living system:

```
train → validate → TEST → deploy → MONITOR → retrain
```

- **Save/load**: `joblib.dump(model, "model.joblib")` — version it like code
- **Drift**: input data changes (new user behavior, sensor aging, new categories) → performance silently decays
- **Monitor**: prediction distribution, latency, error rates, data-schema checks, alert thresholds
- **Retrain triggers**: scheduled (weekly) or drift-detected
- **Rollback plan**: keep previous model artifact

```python
import joblib
joblib.dump(model, "digits_model.joblib")
model2 = joblib.load("digits_model.joblib")   # inference = predict only
```

**Lab exercise:** train → save → load → predict; then feed corrupted inputs → watch confidence collapse.

---

## 5. Ethics & Bias Audit — BEFORE and AFTER

Check bias **before training** (data problems) and **after** (model problems):

- **Representation** — does the data cover all groups? Missing groups → blind spots
- **Label bias** — were labels assigned fairly? Historical bias gets learned
- **Proxy variables** — zip code "predicts" race; model learns discrimination legally
- **Fairness metrics** — demographic parity, equalized odds, calibration per group
- **Explainability** — can you explain WHY it decided? (SHAP/LIME/coefficients)
- **Impact** — who is harmed if it's wrong? High-stakes ≠ same tolerance

```python
from sklearn.metrics import accuracy_score
# per-group accuracy — a big gap = bias alarm
for g in groups.unique():
    m = groups == g
    print(g, accuracy_score(y[m], model.predict(X[m])))
```

**Lab exercise:** synthetic biased dataset — model achieves 95% overall but fails one group; per-group audit exposes it.

---

## The Full Pipeline (memorize this)

```
collect → clean → engineer → SPLIT(60/20/20) → train →
tune on VAL → regularize → TEST once → audit bias →
deploy → monitor drift → retrain → repeat
```

**The meta-lesson:** every stage has a failure mode. The engineers who ship reliable AI are the ones who test each stage, not just the final accuracy number.

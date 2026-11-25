#!/usr/bin/env python3
"""
ML PIPELINE LAB — the 5 forgotten stages, hands-on.
Run: /home/neilh/venv/bin/python lab_ml_pipeline.py
Each exercise proves one concept with real numbers.
"""
import numpy as np
from sklearn.datasets import load_digits, make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression, Ridge, LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib, os

print("=" * 70)
print("EXERCISE 1 — Validation split: 3 splits, not 2")
print("=" * 70)
X, y = load_digits(return_X_y=True)
# split by INDEX so labels stay aligned
ii = train_test_split(np.arange(len(X)), test_size=0.4, random_state=42, stratify=y)
tr_i, tmp_i = ii[0], ii[1]
vv_i, te_i = train_test_split(tmp_i, test_size=0.5, random_state=42, stratify=y[tmp_i])
print(f"train={len(tr_i)}  val={len(vv_i)}  test={len(te_i)}  (60/20/20)")
m = LogisticRegression(max_iter=1000).fit(X[tr_i], y[tr_i])
print(f"train acc={accuracy_score(y[tr_i], m.predict(X[tr_i])):.4f}")
print(f"VAL   acc={accuracy_score(y[vv_i], m.predict(X[vv_i])):.4f}   <- tune HERE")
print(f"TEST  acc={accuracy_score(y[te_i], m.predict(X[te_i])):.4f}   <- final exam, touch ONCE")

print()
print("=" * 70)
print("EXERCISE 2 — Feature engineering: raw → useful")
print("=" * 70)
# raw pixels vs scaled vs polynomial features
raw = LogisticRegression(max_iter=2000).fit(X[tr_i], y[tr_i])
print(f"raw pixels      val acc={accuracy_score(y[vv_i], raw.predict(X[vv_i])):.4f}")
scaled = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X[tr_i], y[tr_i])
print(f"+ StandardScaler val acc={accuracy_score(y[vv_i], scaled.predict(X[vv_i])):.4f}")
poly = make_pipeline(StandardScaler(), PolynomialFeatures(2, include_bias=False),
                     LogisticRegression(max_iter=3000, C=0.5)).fit(X[tr_i], y[tr_i])
print(f"+ poly(deg2)     val acc={accuracy_score(y[vv_i], poly.predict(X[vv_i])):.4f}")
print("→ feature engineering = choosing what the model CAN see")

print()
print("=" * 70)
print("EXERCISE 3 — Regularization: watch the model memorize")
print("=" * 70)
# overfit demo: high-degree polynomial on tiny data
rng = np.random.default_rng(0)
x_small = rng.uniform(-1, 1, 15)
y_small = np.sin(np.pi * x_small) + rng.normal(0, 0.1, 15)
x_dense = np.linspace(-1, 1, 200)
for deg in [1, 3, 9, 15]:
    for alpha in [0.0, 1.0]:
        if alpha == 0.0:
            model = make_pipeline(PolynomialFeatures(deg), LinearRegression())
        else:
            model = make_pipeline(PolynomialFeatures(deg), Ridge(alpha=alpha))
        model.fit(x_small.reshape(-1, 1), y_small)
        pred = model.predict(x_dense.reshape(-1, 1))
        fit_err = mean_squared_error(y_small, model.predict(x_small.reshape(-1, 1)))
        print(f"deg={deg:2d} alpha={alpha}: train-MSE={fit_err:.4f}  (low=memorizing)")
print("→ deg15+alpha0 = INTERPOLATES noise. Ridge(alpha) pulls it back.")

print()
print("=" * 70)
print("EXERCISE 4 — Deployment: save → load → predict → monitor")
print("=" * 70)
joblib.dump(m, "/tmp/digits_model.joblib")
loaded = joblib.load("/tmp/digits_model.joblib")
print(f"saved+loaded model predicts: {loaded.predict(X[vv_i][:5])} (true: {y[vv_i][:5]})")
# drift demo: feed corrupted inputs (all zeros / noise)
corrupt = np.zeros_like(X[vv_i][:50]); corrupt[:] = rng.normal(0, 1, corrupt.shape)
proba = loaded.predict_proba(corrupt).max(axis=1)
print(f"clean input  mean confidence: {loaded.predict_proba(X[vv_i][:50]).max(axis=1).mean():.3f}")
print(f"corrupt input mean confidence: {proba.mean():.3f}   <- drift alarm!")
print("→ in production you'd alert when confidence distribution shifts")

print()
print("=" * 70)
print("EXERCISE 5 — Ethics/bias audit: 95% overall can hide 0% for a group")
print("=" * 70)
# synthetic biased task: group B is harder; model trained on group A mostly
Xa, _ = make_classification(n_samples=800, n_features=10, n_informative=5,
                            n_redundant=2, random_state=1)
Xb, _ = make_classification(n_samples=200, n_features=10, n_informative=2,  # weaker signal
                            n_redundant=5, random_state=2)
ya = (Xa[:, 0] + Xa[:, 1] > 0).astype(int)
yb = (Xb[:, 0] + Xb[:, 1] > 0.5).astype(int)
Xa = np.hstack([Xa, np.zeros((800, 1))]); Xb = np.hstack([Xb, np.ones((200, 1))])
X_all = np.vstack([Xa, Xb]); y_all = np.concatenate([ya, yb])
groups = np.array(["A"] * 800 + ["B"] * 200)
Xtr, Xtmp, ytr, ytmp, gtr, gtmp = train_test_split(X_all, y_all, groups, test_size=0.3, random_state=0)
clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
pred = clf.predict(Xtmp)
print(f"OVERALL accuracy: {accuracy_score(ytmp, pred):.3f}")
for g in ["A", "B"]:
    mask = gtmp == g
    print(f"  group {g}: accuracy={accuracy_score(ytmp[mask], pred[mask]):.3f}  n={mask.sum()}")
print("→ overall looks great. per-group audit exposes the gap. ALWAYS audit per group.")

print()
print("=" * 70)
print("DONE — you now own the 5 forgotten stages.")
print("Pipeline: collect → clean → engineer → SPLIT → train → tune VAL →")
print("          regularize → TEST once → audit bias → deploy → monitor → retrain")
print("=" * 70)

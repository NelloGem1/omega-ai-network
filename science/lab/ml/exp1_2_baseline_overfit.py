#!/usr/bin/env python3
"""Experiments 1 & 2: baseline model comparison + overfitting sweep."""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, confusion_matrix
import time

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
print(f"digits: train={len(Xtr)} test={len(Xte)} features={X.shape[1]}")

print("\n" + "=" * 70)
print("EXP 1 — BASELINE MODEL COMPARISON")
print("=" * 70)
models = {
    "LogisticRegression": LogisticRegression(max_iter=3000, C=1.0),
    "RandomForest(200)": RandomForestClassifier(
        n_estimators=200, random_state=42, n_jobs=-1),
    "MLP(128,64)": MLPClassifier(
        hidden_layer_sizes=(128, 64), max_iter=500, random_state=42,
        early_stopping=True),
}
results = {}
for name, m in models.items():
    t0 = time.perf_counter()
    m.fit(Xtr, ytr)
    train_t = time.perf_counter() - t0
    tr_acc = accuracy_score(ytr, m.predict(Xtr))
    te_acc = accuracy_score(yte, m.predict(Xte))
    # inference latency: batch predict over test set, repeated
    t0 = time.perf_counter()
    for _ in range(20):
        m.predict(Xte)
    inf_ms = (time.perf_counter() - t0) / 20 / len(Xte) * 1000
    results[name] = dict(train=tr_acc, test=te_acc, fit_s=train_t,
                         inf_ms=inf_ms, model=m)
    print(f"{name:22s} train={tr_acc:.4f} test={te_acc:.4f} "
          f"gap={tr_acc-te_acc:+.4f} fit={train_t:6.2f}s "
          f"infer={inf_ms*1000:.2f}us/sample")

best = max(results, key=lambda k: results[k]["test"])
print(f"\nbest test acc: {best} = {results[best]['test']:.4f}")

cm = confusion_matrix(yte, results[best]["model"].predict(Xte))
print("\nconfusion matrix (rows=true, cols=pred):")
print("    " + " ".join(f"{d:3d}" for d in range(10)))
for d in range(10):
    print(f"{d:3d} " + " ".join(f"{v:3d}" for v in cm[d]))
# which digits confuse most (off-diagonal mass per digit)
off = cm.copy()
np.fill_diagonal(off, 0)
print("\nmost-confused digits (off-diag errors):")
for d in np.argsort(off.sum(axis=1))[::-1][:5]:
    top = np.argsort(off[d])[::-1][:3]
    print(f"  true={d}: {off[d].sum()} errors -> predicted {top} "
          f"({[int(off[d][t]) for t in top]})")

print("\n" + "=" * 70)
print("EXP 2 — OVERFITTING LIVE: poly-degree x Ridge-alpha sweep")
print("=" * 70)
scaler = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)
print(f"{'degree':>6} {'alpha':>8} {'train_acc':>9} {'val_acc':>8} "
      f"{'gap':>8} {'n_features':>11}")
for deg in (1, 2, 3):
    poly = PolynomialFeatures(deg, include_bias=False)
    Xp_tr = poly.fit_transform(Xtr_s)
    Xp_te = poly.transform(Xte_s)
    for alpha in (0.01, 1.0, 100.0):
        m = Ridge(alpha=alpha).fit(Xp_tr, ytr)
        tr = accuracy_score(ytr, np.rint(m.predict(Xp_tr)).clip(0, 9).astype(int))
        te = accuracy_score(yte, np.rint(m.predict(Xp_te)).clip(0, 9).astype(int))
        print(f"{deg:>6} {alpha:>8} {tr:>9.4f} {te:>8.4f} {tr-te:>+8.4f} "
              f"{Xp_tr.shape[1]:>11}")
print("\nNOTE: Ridge regression on digit labels — gap grows with degree")
print("unless alpha compensates. True overfit showcase below:")
# cleaner overfit demo: LogisticRegression on poly features, tiny alpha
print(f"\n{'model':>34} {'train':>8} {'val':>8} {'gap':>8}")
for deg in (1, 2, 3):
    pipe = make_pipeline(
        StandardScaler(), PolynomialFeatures(deg, include_bias=False),
        LogisticRegression(max_iter=3000, C=10.0))
    pipe.fit(Xtr, ytr)
    tr = accuracy_score(ytr, pipe.predict(Xtr))
    te = accuracy_score(yte, pipe.predict(Xte))
    print(f"LogReg + poly(deg={deg}) C=10        {tr:>8.4f} {te:>8.4f} "
          f"{tr-te:>+8.4f}")

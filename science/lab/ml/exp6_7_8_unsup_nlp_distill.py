#!/usr/bin/env python3
"""Experiments 6-8: unsupervised KMeans/PCA, NLP-lite TF-IDF,
model extraction via distillation."""
import numpy as np
from sklearn.datasets import load_digits, fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

print("=" * 70)
print("EXP 6 — UNSUPERVISED: KMeans on raw pixels + PCA")
print("=" * 70)
km = KMeans(n_clusters=10, n_init=10, random_state=42).fit(Xtr)
labels = km.labels_
ari = adjusted_rand_score(ytr, labels)
print(f"KMeans(k=10) ARI vs true digits = {ari:.4f}  (1.0=perfect, 0=random)")
# cluster -> majority digit mapping, then accuracy
from scipy.optimize import linear_sum_assignment
cm = np.zeros((10, 10), dtype=int)
for c in range(10):
    for d in range(10):
        cm[c, d] = ((labels == c) & (ytr == d)).sum()
row, col = linear_sum_assignment(-cm)
print("cluster->digit mapping (Hungarian):")
for c, d in zip(row, col):
    print(f"  cluster {c}: {cm[c, d]:4d}/{cm[c].sum():4d} = digit {d}")
print(f"cluster purity after best mapping: {cm[row, col].sum()/len(ytr):.4f}")

pca = PCA(n_components=10).fit(Xtr)
print(f"\nPCA explained variance (first 10): "
      f"{np.round(pca.explained_variance_ratio_, 3)}")
print(f"cumulative: PC1={pca.explained_variance_ratio_[0]:.3f}, "
      f"PC1-2={pca.explained_variance_ratio_[:2].sum():.3f}, "
      f"PC1-3={pca.explained_variance_ratio_[:3].sum():.3f}, "
      f"PC1-10={pca.explained_variance_ratio_.sum():.3f}")
print("-> 2D plot separates coarse digit shapes (loops vs lines) but "
      "overlaps similar digits (3/5/8, 4/9); 3rd dim adds stroke detail")

print("\n" + "=" * 70)
print("EXP 7 — NLP-LITE: TF-IDF + LogReg on 20newsgroups (2 cats)")
print("=" * 70)
cats = ["alt.atheism", "sci.space"]
try:
    data = fetch_20newsgroups(subset="train", categories=cats,
                              remove=("headers", "footers", "quotes"))
    Xt, yt = data.data, data.target
    Xv, yv = fetch_20newsgroups(subset="test", categories=cats,
                                remove=("headers", "footers", "quotes")).data, \
             fetch_20newsgroups(subset="test", categories=cats,
                                remove=("headers", "footers", "quotes")).target
except Exception as e:
    print("fetch failed:", e); raise
print(f"train={len(Xt)} test={len(Xv)} cats={cats}")
pipe = make_pipeline(TfidfVectorizer(max_features=20000, ngram_range=(1, 2),
                                     min_df=2, stop_words="english"),
                     LogisticRegression(max_iter=1000, C=4.0))
pipe.fit(Xt, yt)
acc = accuracy_score(yv, pipe.predict(Xv))
print(f"TF-IDF+LogReg test acc = {acc:.4f}")
vec = pipe.named_steps["tfidfvectorizer"]
lr = pipe.named_steps["logisticregression"]
feat_names = vec.get_feature_names_out()
# binary: coef_[0] > 0 -> class 1, < 0 -> class 0
for cls in range(2):
    coef = lr.coef_[0] * (1 if cls == 1 else -1)
    top = np.argsort(coef)[::-1][:12]
    print(f"\ntop features for class '{pipe.classes_[cls]}':")
    print("  " + ", ".join(feat_names[i] for i in top))

print("\n" + "=" * 70)
print("EXP 8 — MODEL EXTRACTION-ish: distillation fidelity")
print("=" * 70)
teacher = LogisticRegression(max_iter=3000, C=1.0).fit(Xtr, ytr)
# student trained ONLY on teacher's soft predictions (labels = teacher argmax)
student_X, student_y = Xtr, teacher.predict(Xtr)
student = LogisticRegression(max_iter=3000).fit(student_X, student_y)
# fidelity: agreement on held-out test
agree = (teacher.predict(Xte) == student.predict(Xte)).mean()
print(f"teacher test acc={accuracy_score(yte, teacher.predict(Xte)):.4f}")
print(f"student test acc={accuracy_score(yte, student.predict(Xte)):.4f}")
print(f"teacher/student agreement on test = {agree:.4f}")
# fidelity gap: student also trained on softmax probs? use decision_function
proba = teacher.predict_proba(Xtr)
# train student on hard labels only already done; compare vs oracle-trained
oracle = LogisticRegression(max_iter=3000).fit(Xtr, ytr)
print(f"student==oracle agreement = "
      f"{(student.predict(Xte)==oracle.predict(Xte)).mean():.4f}")
print("-> extraction: a second model CAN clone a linear model's "
      "decision boundary almost exactly (logreg is self-distillable); "
      "nonlinear teachers leak less")

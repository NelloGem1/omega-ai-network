"""EXP7: Public dataset — iris EDA, PCA, normality, outliers."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats

X, y = load_iris(return_X_y=True)
feat = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
targets = load_iris().target_names
print(f"iris: {X.shape[0]} samples x {X.shape[1]} features, classes={targets}")

# distributions + normality per feature
print("\n=== per-feature stats ===")
for i, f in enumerate(feat):
    x = X[:, i]
    stat, p = stats.shapiro(x) if len(x) <= 5000 else (stats.normaltest(x).statistic, stats.normaltest(x).pvalue)
    print(f"{f:14s}: mean={x.mean():5.2f} std={x.std():4.2f} skew={stats.skew(x):+.2f} "
          f"kurt={stats.kurtosis(x):+.2f} Shapiro p={p:.3g} {'NON-normal' if p<0.05 else 'ok'}")

# correlation matrix
C = np.corrcoef(X.T)
print("\ncorrelations:")
for i, f in enumerate(feat):
    print(" ".join(f"{C[i,j]:+.2f}" for j in range(4)))

# PCA 2D
Xs = StandardScaler().fit_transform(X)
pca = PCA(n_components=2).fit(Xs)
Xp = pca.transform(Xs)
print(f"\nPCA explained variance: {pca.explained_variance_ratio_*100} (cum {pca.explained_variance_ratio_.sum()*100:.1f}%)")

# outliers: IQR and Z-score on standardized features
print("\n=== outliers ===")
for i, f in enumerate(feat):
    x = X[:, i]; q1, q3 = np.percentile(x, [25, 75]); iqr = q3 - q1
    out_iqr = np.sum((x < q1 - 1.5*iqr) | (x > q3 + 1.5*iqr))
    z = np.abs(stats.zscore(x)); out_z = np.sum(z > 3)
    print(f"{f:14s}: IQR outliers={out_iqr}, |z|>3 outliers={out_z}")
# extreme point: which sample is most extreme overall?
rad = np.linalg.norm(Xs, axis=1)
worst = np.argsort(rad)[-5:][::-1]
print("most extreme samples (Mahalanobis-ish radius):",
      [(int(i), targets[y[i]], round(float(rad[i]),2)) for i in worst])

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, data, ttl in [(axes[0], Xs, "PCA-2D of iris (standardized)"), (axes[1], X, "raw PCA-2D")]:
    Z = pca.transform(data) if ax is axes[0] else PCA(n_components=2).fit_transform(StandardScaler().fit_transform(data))
    for c in range(3):
        ax.scatter(Z[y==c,0], Z[y==c,1], s=18, label=targets[c])
    ax.set_title(ttl); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("/home/neilh/science_lab/bio/iris_pca.png", dpi=120)
print("saved iris_pca.png")

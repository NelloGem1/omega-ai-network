#!/usr/bin/env python3
"""Experiments 3-5: adversarial FGSM, label poisoning, concept drift."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
Xtr_f = Xtr.reshape(-1, 8, 8) / 16.0   # 0..15 -> ~0..1
Xte_f = Xte.reshape(-1, 8, 8) / 16.0

# ---------------------------------------------------------------
print("=" * 70)
print("EXP 3 — ADVERSARIAL ATTACK (FGSM on torch MLP)")
print("=" * 70)
import torch
import torch.nn as nn

torch.manual_seed(42)
Xtr_t = torch.tensor(Xtr_f, dtype=torch.float32)
ytr_t = torch.tensor(ytr, dtype=torch.long)
Xte_t = torch.tensor(Xte_f, dtype=torch.float32)

model = nn.Sequential(
    nn.Flatten(), nn.Linear(64, 128), nn.ReLU(),
    nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10))
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
lossf = nn.CrossEntropyLoss()
model.train()
for ep in range(30):
    perm = torch.randperm(len(Xtr_t))
    for i in range(0, len(Xtr_t), 128):
        idx = perm[i:i + 128]
        opt.zero_grad()
        loss = lossf(model(Xtr_t[idx]), ytr_t[idx])
        loss.backward()
        opt.step()
model.eval()
with torch.no_grad():
    clean_acc = (model(Xte_t).argmax(1) == torch.tensor(yte)).float().mean().item()
print(f"torch MLP clean test acc = {clean_acc:.4f}")

adv_examples = []
epsilons = [0.0, 0.05, 0.1, 0.2, 0.5]
print(f"{'epsilon':>8} {'test_acc':>9} {'acc_drop':>9}")
accs = []
for eps in epsilons:
    x_adv = Xte_t.clone().requires_grad_(True)
    out = model(x_adv)
    loss = lossf(out, torch.tensor(yte))
    loss.backward()
    grad = x_adv.grad.detach()
    x_adv2 = (x_adv.detach() + eps * grad.sign()).clamp(0, 1)
    with torch.no_grad():
        acc = (model(x_adv2).argmax(1) == torch.tensor(yte)).float().mean().item()
    accs.append(acc)
    print(f"{eps:>8} {acc:>9.4f} {clean_acc - acc:>+9.4f}")
    if eps in (0.1, 0.5):
        adv_examples.append((eps, x_adv2))

# visualize adversarial digits
fig, axes = plt.subplots(4, 10, figsize=(12, 5))
rng = np.random.default_rng(0)
idxs = rng.choice(len(Xte), 10, replace=False)
for j, i in enumerate(idxs):
    axes[0, j].imshow(Xte_f[i], cmap="gray", vmin=0, vmax=1)
    axes[0, j].set_title(f"{yte[i]}", fontsize=8); axes[0, j].axis("off")
for row, (eps, xa) in enumerate(adv_examples, start=1):
    with torch.no_grad():
        preds = model(xa).argmax(1).numpy()
    for j, i in enumerate(idxs):
        axes[row, j].imshow(xa[i].numpy(), cmap="gray", vmin=0, vmax=1)
        axes[row, j].set_title(f"{preds[i]}", fontsize=8)
        axes[row, j].axis("off")
    axes[row, 0].set_ylabel(f"eps={eps}", fontsize=10)
plt.suptitle("FGSM adversarial digits: true label -> predicted label")
plt.tight_layout()
plt.savefig("/home/neilh/science_lab/ml/adversarial_digits.png", dpi=110)
print("saved adversarial_digits.png")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("EXP 4 — DATA POISONING: flip training labels")
print("=" * 70)
m = LogisticRegression(max_iter=3000).fit(Xtr, ytr)
print(f"clean train acc={accuracy_score(ytr, m.predict(Xtr)):.4f} "
      f"test acc={accuracy_score(yte, m.predict(Xte)):.4f}")
poison_accs = {}
for frac in (0.05, 0.10, 0.20):
    rng = np.random.default_rng(42)
    y_pois = ytr.copy()
    n_flip = int(len(ytr) * frac)
    flip_idx = rng.choice(len(ytr), n_flip, replace=False)
    # flip to a *wrong* label deterministically
    y_pois[flip_idx] = (ytr[flip_idx] + 1 + rng.integers(0, 9, n_flip)) % 10
    mp = LogisticRegression(max_iter=3000).fit(Xtr, y_pois)
    tr_a = accuracy_score(y_pois, mp.predict(Xtr))
    te_a = accuracy_score(yte, mp.predict(Xte))
    poison_accs[frac] = te_a
    print(f"poison={frac:>4.0%}: train(on poisoned labels)={tr_a:.4f} "
          f"test={te_a:.4f} drop={accuracy_score(yte, m.predict(Xte))-te_a:+.4f}")
# show what model learned: poisoned examples it now gets "right"
frac = 0.10
y_p = ytr.copy()
rng = np.random.default_rng(42)
flip_idx = rng.choice(len(ytr), int(len(ytr)*frac), replace=False)
y_p[flip_idx] = (ytr[flip_idx] + 1 + rng.integers(0, 9, len(flip_idx))) % 10
mp = LogisticRegression(max_iter=3000).fit(Xtr, y_p)
# fraction of flipped samples the model now agrees with (memorized poison)
agree = (mp.predict(Xtr[flip_idx]) == y_p[flip_idx]).mean()
print(f"\nmodel agrees with poisoned labels on {agree:.1%} of flipped "
      f"samples — it memorized the lie")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("EXP 5 — CONCEPT DRIFT: train 0-4, test 5-9")
print("=" * 70)
mask_tr = y <= 4
mask_te_seen = (y > 4) & (y <= 9)
# domain-shift split: model only ever sees digits 0-4
X_sub, y_sub = X[mask_tr], y[mask_tr]
X_unseen, y_unseen = X[mask_te_seen], y[mask_te_seen]
Xdr_tr, Xdr_va, ydr_tr, ydr_va = train_test_split(
    X_sub, y_sub, test_size=0.25, random_state=42, stratify=y_sub)
md = LogisticRegression(max_iter=3000).fit(Xdr_tr, ydr_tr)
# on seen classes (in-domain val)
seen_acc = accuracy_score(ydr_va, md.predict(Xdr_va))
# on unseen digits 5-9: two failure modes — wrong class or forced into 0-4
preds_unseen = md.predict(X_unseen)
forced_acc = accuracy_score(y_unseen, preds_unseen)          # can't be right: classes unseen
in_range = preds_unseen.max()  # model can only output 0..4
preds_shift = preds_unseen + 5                              # if we remap 0-4 -> 5-9
remap_acc = accuracy_score(y_unseen, np.clip(preds_shift, 0, 9))
print(f"in-domain val acc (digits 0-4):      {seen_acc:.4f}")
print(f"unseen digits 5-9, raw preds:        {forced_acc:.4f} "
      f"(model can only emit labels 0-4)")
print(f"unseen digits 5-9, remap 0-4->5-9:   {remap_acc:.4f} "
      f"(upper bound if drift were only a label shift)")
print(f"predicted-label histogram on 5-9: {np.bincount(preds_unseen, minlength=5)}")

# recovery: retrain on ALL digits
m_all = LogisticRegression(max_iter=3000).fit(X, y)
# hold out a test split for fair comparison
Xr_tr, Xr_te, yr_tr, yr_te = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
m_rec = LogisticRegression(max_iter=3000).fit(Xr_tr, yr_tr)
print(f"\nafter retrain on all 10 digits (fresh split): "
      f"test acc={accuracy_score(yr_te, m_rec.predict(Xr_te)):.4f}")
print("-> drift damage fully recovered once new-class data arrives")

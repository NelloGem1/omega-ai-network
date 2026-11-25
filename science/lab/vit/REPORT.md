# ViT Deep Experiments — NelloGem Fleet Report

**Environment:** WSL Ubuntu, Python venv `/home/neilh/venv/bin/python`, torch 2.15.0+cpu, timm 1.0.31, torchvision. 4 CPU cores, 5 GB RAM.
**Workdir:** `/home/neilh/science_lab/vit/` — scripts: `vit_exp.py` (train/attack CLI), `make_plots.py`, `run_attacks.sh`; results in `results/<tag>/{metrics.json,model.pt,attack.json}`; plots `results_summary.png`, `acc_vs_time.png`; datasets in `data/` (FashionMNIST + CIFAR-10 downloaded via torchvision).

## Shared protocol
- Datasets loaded as raw [0,1] tensors; `prep()` does bilinear resize to `img_size`, 1→3 channel repeat (ViT), and ImageNet-style `(x-0.5)/0.5` normalization. Attack gradients flow through prep to the raw [0,1] input.
- Optimizer: AdamW lr=1e-3, weight_decay=0.05, cosine LR over epochs, CrossEntropy, batch 128 (64/48 for ViT variants to fit RAM), seed 0. Train subset = first `ntrain` of a seeded permutation; test subset `ntest`=2000.
- Inference time = eval-mode forward over the 2000-image test subset, batch 128, including prep (resize+norm). Train time = wall-clock for all epochs.

## Exp 1 — Fashion-MNIST: ViT vs CNN vs MLP (ntrain=8000, 3 epochs)

| model | params | clean acc | train time | infer ms/img |
|---|---|---|---|---|
| MLP (784→512→256→10) | 0.54M | **0.829** | 1.9 s | 0.022 |
| CNN (3 conv blocks + GAP) | 0.094M | 0.745 | 87.1 s | 1.68 |
| ViT-tiny patch16 @112 | 5.50M | 0.563 | 628.7 s (10.5 min) | 9.29 |

- **Hypothesis:** ViT should match/beat CNN on Fashion-MNIST.
- **Result:** ViT is far worse *and* far slower at this data budget. Train acc after 3 epochs only 53.5% — ViT is severely undertrained on 8k images (see Exp 2b).
- **Lesson:** ViTs are data-hungry; 8k samples × 3 epochs is nowhere near enough. CNN wins on every axis here.

## Exp 2 — ViT variants / accuracy-vs-cost

| tag | config | params | clean acc | train time | infer ms/img |
|---|---|---|---|---|---|
| fm_vit_tiny_112_b | vit_tiny @112, 8000 img, **6 ep** | 5.50M | **0.718** | 19.9 min | 6.40 |
| var_vit224_tiny | vit_tiny @224, 3000 img, 3 ep, bs64 | 5.53M | 0.351 | 12.7 min | 25.1 |
| var_vitsmall_112 | vit_small @112, 3000 img, 3 ep, bs48 | 21.6M | 0.352 | 9.2 min | 20.0 |

- **Hypothesis:** more epochs / bigger img_size / bigger model → better ViT accuracy.
- **Result:** Doubling epochs 3→6 (same 8k imgs) lifted ViT 0.563→0.718 — still below MLP 0.829 but closing. @224 vs @112 at 3k/3ep: similar accuracy, **4× slower inference** (25 vs ~6–9 ms/img) for no gain at this budget. vit_small (4× params) matched vit_tiny (0.352 vs 0.351) — capacity is not the bottleneck, data/epochs are.
- **Lesson:** At small scale, resolution and model size barely matter; optimization budget (epochs×data) dominates. ViT's cost only pays off with much larger datasets.

## Exp 3 — CIFAR-10 transfer check (ntrain=8000, 3 epochs)

| model | params | clean acc | train time | infer ms/img | FGSM adv acc (eps=0.3) |
|---|---|---|---|---|---|
| CNN | 0.095M | **0.455** | 91 s | 1.21 | **0.234** |
| ViT-tiny @112 | 5.50M | 0.320 | 6.9 min | 5.65 | 0.003 |

- **Hypothesis:** ViT gap vs CNN would persist on color images.
- **Result:** Yes — CNN beats ViT 0.455 vs 0.320 at ~4.5× less train time and ~5× faster inference.
- **Lesson:** Same story as Fashion-MNIST: on 8k-image subsets the inductive bias of convnets wins decisively.

## Exp 4 — BREAK test: FGSM attack, eps=0.3, n=1000

Attack applied to raw [0,1] inputs, `x_adv = clamp(x + eps·sign(∇_x CE), 0, 1)`.

| model | dataset | clean acc | adv acc | drop |
|---|---|---|---|---|
| MLP | Fashion | 0.826 | 0.001 | 0.825 |
| CNN | Fashion | 0.732 | 0.054 | 0.678 |
| ViT-tiny@112 (3ep) | Fashion | 0.556 | 0.013 | 0.543 |
| ViT-tiny@112 (6ep) | Fashion | 0.706 | 0.061 | 0.645 |
| ViT-tiny@224 | Fashion | 0.323 | 0.013 | 0.310 |
| vit_small@112 | Fashion | 0.361 | 0.044 | 0.317 |
| CNN | CIFAR | 0.458 | 0.234 | 0.224 |
| ViT-tiny@112 | CIFAR | 0.304 | 0.003 | 0.301 |

- **Hypothesis:** ViT's global attention might be more robust to pixel perturbations than MLP.
- **Result:** At eps=0.3 **every model is destroyed** — adversarial accuracy ≤6% everywhere. The 6-epoch ViT retains the highest Fashion adv accuracy (6.1% vs MLP 0.1%, CNN 5.4%), i.e. marginally more robust than the MLP and roughly tied with the CNN *in absolute terms*. On CIFAR the CNN is clearly more robust (23.4% vs 0.3%). Lower-accuracy ViT variants show smaller *drops* only because their clean accuracy was already low (floor effect).
- **Lesson:** FGSM eps=0.3 is a total break for all three architectures on these subsets — no free robustness from attention. If anything, the well-trained CNN is the most robust on CIFAR.

## Reproduce
```
cd /home/neilh/science_lab/vit
/home/neilh/venv/bin/python vit_exp.py train --tag fm_vit_tiny_112_b --model vit --dataset fashion --img-size 112 --epochs 6 --ntrain 8000 --lr 1e-3 --batch 128
/home/neilh/venv/bin/python vit_exp.py attack --tag fm_vit_tiny_112_b --eps 0.3 --n 1000
/home/neilh/venv/bin/python make_plots.py
```
See `results/*/metrics.json` and `attack.json` for every number above. Note: WSL VM crashed once mid-run (5 GB RAM); per-epoch `last.pt` checkpoints were added to `vit_exp.py` afterwards as insurance — the crashed run was simply re-executed.

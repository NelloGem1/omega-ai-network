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
## CS agent (COMPLETE - 7 experiments)
- Timsort ~500x faster on presorted input (run detection); quicksort first-pivot superlinear worst case confirmed
- BST sorted-insert -> height=n (51s @20k) vs AVL height=19 (0.15s)
- Adversarial hash keys collapse linear probing to n/2 probes; Python dict immune (perturb-shift)
- Dijkstra WITH settled-set BROKEN on negative edges (dist=2 vs true -4); Bellman-Ford correct; version w/o settled-set stays correct
- KMP 40k comparisons vs naive 1M; Big-O exponents match theory (max=1.006, nested=2.051)
RULE: extend - e.g. test Fibonacci heaps, Fibonacci hashing, cache-oblivious layouts.
## Bio/Chem agent (COMPLETE - 7 experiments, fetched LIVE NCBI+UniProt data)
- Periodic radius fits R2=0.89 main groups; lanthanide contraction flattens radii; d-block collapses fit
- Human insulin CDS: GC=63.9%, CpG suppressed 0.32x, codon bias p~7e-19; shuffle kills dinucleotide signal
- MM kinetics recovers Vmax/Km exactly; substrate inhibition biases plain fit 3x
- SIR R0=4 -> 40% peak, 98% attack rate; HONEST NEGATIVE: SIRS gives stable endemic eq not oscillations
- UPGMA recovered exact 5-taxon tree; shuffle -> star tree
- Iris PCA 95.8% var; "outliers" = class boundaries not errors
RULE: extend - fetch more live NCBI data, test more genomes/kinases.
## Math agent (COMPLETE - 7 experiments + ECM RSA breaker)
- Prime lattice: coprime density = phi(P)/P EXACT through P47=6.1e17; last-digit law verified 10M primes
- RSA factoring: 64b=0.26s,128b=8.7s; GNU ECM 191b=17.2s!; 256b resists; 2048-bit infeasible
- Vigenere broken via IOC (key=LEMON exact); hash collisions at ~1.6x of 2^16 theory
- Dijkstra settled-set broken on negative weights (returns 1 vs true -5); 176/300 neg graphs have neg cycles
- Collatz verified to n<=2M, record 377 steps; max prime gap <10M = 154 (Cramer-consistent)
RULE: extend - try ECM on 300b+, SIQS for >256b, explore Cramer gap bounds.
## Marshal Colab session (PERSONAL - Tesla T4 free GPU)
- MNIST MLP train: 96.3% acc in ~30s on T4
- FGSM eps=0.3: clean 0.949 -> attacked 0.000 (confirmed twice)
- Adversarial training defense: clean 0.961 / attack 0.711 (recovered from 0%)
- ViT-tiny local CPU training in progress (vit_mnist_local.py)
## AdvML agent (COMPLETE - PGD attack/defense matrix on MNIST)
- Strong PGD(30 steps): baseline acc 1.8% - nearly total kill
- Defense must MATCH attacker strength: FGSM-AT 68.1% vs strong-PGD; PGD-AT-strong 71.8% best
- SURPRISE: 3-bit depth reduction = best defense (73.4%) at ZERO training cost
- JPEG smoothing fails (5.6%); preprocessing evaluated adaptively (STE gradients)
- Bug found: PGD must ASCEND loss (x + a*sign(grad))
RULE: extend - EOT attacker vs bit-depth defense; test on CIFAR-10/ViT.
## Marshal Colab ViT (PERSONAL - Tesla T4)
- vit_tiny_patch16_224, full MNIST 60k, 224px, 5 epochs: TEST ACC 0.9738
- BEATS MLP baseline 0.963 -> Transformer wins on MNIST
- Local CPU ViT (12k,128px,2ep): 0.5965; full retrain 60k x5ep in progress

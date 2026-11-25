# AI & MACHINE LEARNING FIELD MAP — Comprehensive Classification

*A structured survey of every major field in artificial intelligence, machine learning, and adjacent disciplines. Compiled November 2026. Tool/framework versions verified against official release pages (see Sources).*

---

## 0. HOW TO READ THIS MAP

### 0.1 The discipline taxonomy

This document classifies AI into seven top-level families:

1. **AI Foundations** — the pre-ML and symbolic core: search, knowledge representation, automated reasoning, planning, expert systems.
2. **Machine Learning** — statistical learning paradigms: supervised, unsupervised, semi/self-supervised, reinforcement, transfer/meta.
3. **Deep Learning** — neural architectures: MLPs, CNNs, RNNs, Transformers, generative models, specialized architectures.
4. **AI Applications** — domain deployments: NLP, computer vision, speech, robotics, autonomous systems, recommender systems, predictive analytics.
5. **Advanced AI** — frontier research: agents, multi-agent systems, AGI, cognitive architectures, neuro-symbolic AI, alignment/safety, XAI.
6. **Interdisciplinary** — fields that feed into or borrow from AI: computational neuroscience, cognitive science, artificial life, computational biology, AI-for-science.
7. **Cross-Cutting Infrastructure** — data, training pipelines, MLOps, hardware.

### 0.2 Existing capabilities vs. hypothetical future AI

**CRITICAL DISTINCTION.** Throughout this document, fields are tagged:

- **[EXISTING]** — deployed, working technology today (2026). Every claim about "current capability" refers to this.
- **[FRONTIER]** — active research with real but limited results; partial prototypes exist.
- **[HYPOTHETICAL]** — speculative future AI (e.g., human-level AGI, full brain emulation). No working system exists; claims are conjecture.

Almost everything in Parts 1–5 is **[EXISTING]** or **[FRONTIER]**. **[HYPOTHETICAL]** items are confined to AGI timelines, superintelligence, and speculative capabilities. The single most important mental model: *today's AI is a collection of narrow, benchmark-validated systems — not a general mind.*

### 0.3 Universal skeleton per field

Each field below is described with the same anatomy where applicable:

- **Math foundations** — the formal machinery (probability, optimization, logic, information theory).
- **Core algorithms** — named methods.
- **Training methods** — how models are fit (gradient descent variants, RL loops, evolutionary search).
- **Evaluation metrics** — how performance is measured.
- **Architectures/tools** — canonical models and software.
- **Limitations** — known failure modes.
- **Risks** — societal/technical risks specific to the field.
- **Open challenges** — unsolved research problems.

---

## PART 1 — AI FOUNDATIONS

The classical, pre-deep-learning core of AI. These fields are **not obsolete**: they underpin modern systems (planning in robotics, search in game engines, logic in verification) and remain the strongest tools where interpretability and guarantees matter.

### 1.1 Search

- **Math foundations**: graph theory, state-space formalization, admissible heuristics, complexity classes (NP-completeness of many planning/search problems).
- **Core algorithms**: breadth-first, depth-first, uniform-cost, A* and variants (IDA*, Anytime A*, Anytime Repairing A*), bidirectional search, beam search, Monte Carlo Tree Search (MCTS), minimax/alpha-beta pruning, constraint propagation (AC-3, forward checking).
- **Metaheuristics**: genetic algorithms, simulated annealing, tabu search, particle swarm, ant colony, large neighborhood search.
- **Training methods**: none — search is typically non-learning; modern hybrids learn heuristics (e.g., learned value functions inside MCTS, "neural A*").
- **Evaluation metrics**: solution quality, nodes expanded, time/space complexity, optimality guarantees.
- **Tools**: custom implementations dominate; libraries like NetworkX (graph algorithms), OR-Tools (CP-SAT constraint solver), Z3 (SMT for constraint solving).
- **Limitations**: exponential state spaces; heuristic quality determines feasibility; no learning of reusable abstractions in classical versions.
- **Risks**: low direct risk; used in logistics, games, chip design — errors are operational, not existential.
- **Open challenges**: learned heuristics that generalize; hierarchical/lifelong search; combining symbolic search with neural policies.

### 1.2 Knowledge Representation (KR)

- **Math foundations**: first-order logic, description logics (ALC, SROIQ), ontologies, frame problem, non-monotonic logic, Bayesian networks.
- **Core formalisms**: propositional/first-order logic, semantic networks, frames/scripts (historical), description logics (OWL), knowledge graphs (RDF triples, property graphs), probabilistic graphical models.
- **Training methods**: knowledge graph completion (TransE, RotatE, ComplEx embeddings), ontology learning, rule mining (AMIE, AnyBURL).
- **Evaluation metrics**: link prediction MRR/Hits@k, ontology reasoning task accuracy, consistency checking.
- **Tools**: Protégé (ontology editor), Apache Jena, RDFLib, Neo4j, NetworkX, PyKEEN, Owlready2, PyTorch-BigGraph.
- **Limitations**: the knowledge acquisition bottleneck (encoding world knowledge by hand is expensive); brittle ontologies; embeddings capture statistical patterns, not true semantics.
- **Risks**: incorrect encoded knowledge propagates silently; used in medical/legal reasoning where errors are costly.
- **Open challenges**: automatic ontology construction at scale; combining KR with neural embeddings (see neuro-symbolic, §5.5); commonsense knowledge bases that cover the long tail.

### 1.3 Automated Reasoning & Theorem Proving

- **Math foundations**: formal logic, proof theory, satisfiability (SAT/SMT), higher-order logic, type theory.
- **Core systems**: resolution theorem provers (E, Vampire, Prover9/Mace4), SMT solvers (Z3, CVC5, Boolector), SAT solvers (CaDiCaL, Kissat), interactive theorem provers (Lean 4, Coq, Isabelle/HOL, Agda), ATP systems for first-order logic (E prover, Vampire), higher-order provers (Satallax, Leo-III).
- **Training methods**: premise selection via learned models (DeepMath, LeanDojo, GPT-f for proof search); reinforcement learning for proof-step selection; neural theorem proving (DeepSeek-Prover, Goedel-Prover).
- **Evaluation metrics**: problems solved on TPTP/CASC benchmarks, miniF2F/PutnamBench for olympiad math, proof checking correctness.
- **Tools**: Lean 4 + `lake` (installed on this machine — `/home/neilh/.elan/bin/lake`), Coq, Isabelle, Z3, CVC5, TPTP library, Mathlib (Lean math library), HuggingFace LeanDojo datasets.
- **Limitations**: combinatorial explosion in search; limited commonsense reasoning; autoformalization (NL→formal) remains error-prone; current provers excel at competition math but not informal mathematical intuition.
- **Risks**: verified code generation could be misused for verified malware; low near-term risk overall.
- **Open challenges**: scaling to research-level mathematics; autoformalization quality; proof search efficiency; connecting provers to informal LLM reasoning.

### 1.4 Planning

- **Math foundations**: STRIPS/PDDL action languages, situation calculus, Markov decision processes (MDPs), partially observable MDPs (POMDPs), hierarchical task networks (HTN).
- **Core algorithms**: forward/backward state-space search, GraphPlan, Fast Downward (heuristic search), FF planner, HTN planners, hierarchical RL, Monte Carlo planning, POMDP solvers (POMCP, DESPOT).
- **Training methods**: learning domain-independent heuristics (h^add, h^max, landmark heuristics); learning action models from data (AMODEUS, FAMA); neural planners.
- **Evaluation metrics**: plan length/cost, planning time, success rate on IPC (International Planning Competition) benchmarks, IPC domains (Blocks World, Logistics, etc.).
- **Tools**: Fast Downward, FF, VAL plan validator, PDDL standard, PyBullet/Isaac Sim for embodied testing, ROS 2 plan-execution stacks.
- **Limitations**: open-world assumptions break classical planners; long-horizon real-world tasks have enormous state spaces; replanning latency in dynamic environments.
- **Risks**: autonomous systems making irreversible decisions (medical, military); planning errors compound over long horizons.
- **Open challenges**: open-world planning under uncertainty; combining planning with learned policies (LLM+planner hybrids like SayCan, PaLM-E style architectures — now largely superseded by end-to-end agents); lifelong planning.

### 1.5 Expert Systems & Rule Engines

- **Math foundations**: production rules, forward/backward chaining, certainty factors, fuzzy logic, decision tables.
- **Core systems**: MYCIN-style inference engines, CLIPS, Drools, Rete algorithm, business rules engines (IBM ODM, Red Hat Decision Manager), expert-system shells.
- **Training methods**: rule induction (FOIL, RIPPER), decision tree learning (C4.5), knowledge elicitation from experts.
- **Evaluation metrics**: diagnostic accuracy, rule firing consistency, expert agreement (Cohen's kappa).
- **Tools**: CLIPS, Drools, OpenRules, custom DSLs; modern descendants are "rules as code" systems and guardrailed LLM agents.
- **Limitations**: knowledge acquisition bottleneck (the reason expert systems "failed" commercially in the 1980s–90s); brittleness outside encoded domains; maintenance nightmare as rules interact.
- **Risks**: opaque rule interactions in critical systems; legacy systems still embedded in insurance/medical/industrial control.
- **Open challenges**: hybrid rule+ML systems; verified rule systems; explainability (rules are inherently more interpretable than NNs — a strength).
- **Note**: Expert systems were the first commercial AI boom and bust. Their lesson — *narrow, handcrafted knowledge doesn't scale* — is the founding motivation for machine learning.

---

## PART 2 — MACHINE LEARNING

The statistical paradigm that replaced handcrafted knowledge with learned patterns. All of ML shares the same skeleton: data + loss function + optimization → model that generalizes.

### 2.1 Supervised Learning

- **Math foundations**: empirical risk minimization, statistical learning theory (VC dimension, Rademacher complexity), maximum likelihood estimation, Bayesian inference, regularization theory.
- **Core algorithms**: linear/logistic regression, support vector machines (kernel methods), decision trees, random forests, gradient boosting (XGBoost, LightGBM, CatBoost), k-nearest neighbors, naive Bayes, Gaussian processes.
- **Training methods**: closed-form solutions (OLS, ridge), convex optimization (SVM QP, logistic regression), gradient-based training (boosting), ensemble methods.
- **Evaluation metrics**: accuracy, precision/recall/F1, ROC-AUC, PR-AUC, log-loss/Brier score, MAE/RMSE/MAPE for regression, calibration metrics.
- **Tools**: scikit-learn 1.9.1 (current stable, Nov 2026), XGBoost, LightGBM, CatBoost, statsmodels, PyMC (Bayesian), scikit-survival (survival analysis).
- **Limitations**: requires labeled data (expensive); tabular data performance plateaus vs. deep models on images/text; extrapolation beyond training distribution fails badly.
- **Risks**: biased training data → biased predictions (hiring, lending, policing); label leakage; automation bias where humans over-trust outputs.
- **Open challenges**: learning from fewer labels; distribution shift robustness; causal (not just correlational) prediction; uncertainty quantification.

### 2.2 Unsupervised Learning

- **Math foundations**: density estimation, mixture models, spectral graph theory, information theory, manifold learning theory.
- **Core algorithms**: k-means/k-medoids/k-means++, hierarchical clustering (agglomerative/DBSCAN/HDBSCAN), Gaussian mixture models (EM algorithm), PCA/ICA/NMF, t-SNE/UMAP (visualization), autoencoder-based clustering, isolation forests, one-class SVM.
- **Training methods**: EM for latent variable models, SGD for deep clustering, spectral methods.
- **Evaluation metrics**: silhouette score, Davies-Bouldin, Calinski-Harabasz (internal); adjusted Rand index, normalized mutual information (external, needs ground truth); downstream task performance.
- **Tools**: scikit-learn (clustering module), HDBSCAN, UMAP-learn, FAISS (nearest neighbors at scale), PyOD (anomaly detection).
- **Limitations**: cluster "truth" is ambiguous — same data yields different valid clusterings; curse of dimensionality; evaluation is hard without labels.
- **Risks**: profiling and surveillance (clustering people by behavior); demographic inference from "anonymous" data.
- **Open challenges**: semantically meaningful clusters; clustering under distribution shift; constraint-based clustering (must-link/cannot-link at scale).

### 2.3 Semi-Supervised & Self-Supervised Learning

- **Math foundations**: manifold regularization, consistency regularization, information maximization, contrastive learning theory, mutual information maximization.
- **Core algorithms**: self-training/pseudo-labeling, label propagation, co-training, FixMatch, Noisy Student, contrastive methods (SimCLR, MoCo, BYOL, DINO), masked autoencoders (MAE), masked language modeling (BERT-style), masked image modeling.
- **Training methods**: same gradient descent; key is the pretext task design — predict held-out parts of input.
- **Evaluation metrics**: linear probe accuracy, fine-tuning accuracy, k-NN accuracy on frozen representations; few-shot benchmarks.
- **Tools**: PyTorch Lightning (self-supervised recipes), VISSL (Facebook/Meta), lightly (SSL library), HuggingFace transformers (pretrained checkpoints).
- **Limitations**: SSL learns whatever is statistically predictable — may learn shortcuts not aligned with human concepts; requires large unlabeled corpora; domain transfer not guaranteed.
- **Risks**: pretrained representations can encode societal biases present in web-scale data; supply-chain risk of poisoned pretrained weights.
- **Open challenges**: designing pretext tasks aligned with downstream utility; SSL for structured/tabular data (still weak); theoretical understanding of why contrastive learning works.

### 2.4 Reinforcement Learning (RL)

- **Math foundations**: Markov decision processes (MDPs), Bellman equations, value functions, policy gradients, actor-critic theory, exploration-exploitation (UCB, optimism), partial observability (POMDPs), inverse RL, reward design theory.
- **Core algorithms**: Q-learning, SARSA, DQN, Double DQN, Dueling DQN, Rainbow, policy gradient (REINFORCE), actor-critic (A2C/A3C, PPO, SAC, TD3), distributional RL (C51, QR-DQN, IQN), model-based RL (MuZero, Dreamer, MBPO), offline RL (CQL, IQL, Decision Transformer).
- **Training methods**: online interaction with environment (sim or real); off-policy replay buffers; on-policy rollouts; RLHF/DPO for LLM alignment (treated in §5.6); evolutionary strategies for sparse rewards.
- **Evaluation metrics**: episodic return, sample efficiency, asymptotic performance, human-normalized score (Atari), Elo for games, real-world success rate.
- **Tools**: Gymnasium (successor to OpenAI Gym), Stable-Baselines3, RLlib (Ray RL), CleanRL (educational implementations), Tianshou, PettingZoo (multi-agent), MuJoCo physics, Isaac Lab, PyBullet.
- **Limitations**: sample inefficiency (millions of env steps); reward hacking/specification gaming; credit assignment over long horizons; safety during exploration; sim-to-real gap.
- **Risks**: reward hacking producing unintended behavior; deployment of unsafe exploration policies; RLHF can entrench model biases; military autonomous weapons applications.
- **Open challenges**: sample-efficient RL; safe exploration; hierarchical RL; causal RL; RL for real-world robotics at scale; theoretical sample-complexity bounds.

### 2.5 Transfer Learning, Meta-Learning & Few-Shot Learning

- **Math foundations**: domain adaptation theory, PAC-Bayes, representation learning theory, Bayesian meta-learning, gradient-based meta-learning.
- **Core algorithms**: fine-tuning pretrained models, adapters (Houlsby adapters, LoRA/QLoRA — parameter-efficient fine-tuning), prompt tuning, prefix tuning, MAML/Reptile (model-agnostic meta-learning), Prototypical Networks, Matching Networks, relation networks, in-context learning (emergent in transformers).
- **Training methods**: pretrain → adapt pipeline; meta-training across task distributions; PEFT freezes most weights and trains small adapter matrices.
- **Evaluation metrics**: few-shot accuracy (N-way K-shot), domain adaptation benchmarks, catastrophic forgetting measures (per-task accuracy after sequential fine-tuning).
- **Tools**: HuggingFace PEFT library, transformers, sentence-transformers, SetFit, pytorch-meta (higher library), Learn2Learn.
- **Limitations**: negative transfer when source/target mismatch; catastrophic forgetting in continual learning; in-context learning capabilities are poorly understood theoretically; fine-tuning can degrade safety alignments.
- **Risks**: jailbreaks via fine-tuning on malicious data; model collapse when training on synthetic data recursively.
- **Open challenges**: continual/lifelong learning without forgetting; principled theory of in-context learning; meta-learning that generalizes beyond narrow task distributions.

---

## PART 3 — DEEP LEARNING

The dominant paradigm of modern AI. Neural networks as universal function approximators, trained by gradient descent on massive data.

### 3.1 Neural Networks — Foundations

- **Math foundations**: universal approximation theorem, gradient descent/stochastic gradient descent, backpropagation (chain rule), automatic differentiation, optimization theory (Adam, AdamW, LAMB, Lion optimizers), loss landscape geometry, lottery ticket hypothesis, grokking.
- **Core architectures**: multilayer perceptrons (MLPs), residual networks (ResNet), normalization layers (BatchNorm, LayerNorm, RMSNorm), activation functions (ReLU, GELU, SwiGLU).
- **Training methods**: supervised (cross-entropy, MSE, contrastive losses), self-supervised (masked prediction), reinforcement learning from human feedback; distributed training (DDP, FSDP2, tensor/pipeline/expert parallelism); mixed precision (FP16/BF16/FP8); quantization (INT8/INT4/NVFP4).
- **Evaluation metrics**: task metrics + training dynamics (loss curves, gradient norms, effective rank, representation similarity).
- **Tools**: PyTorch 2.15.0 (current stable, Oct 2026 — rewritten NCCL backend, FSDP2 improvements, FP8/NVFP4 Blackwell support, `torch.compile`), TensorFlow 2.21.0 (stable; 2.22.0-rc1 pending), JAX 0.12.1 (XLA-compiled, TPU-native; Flax/Equinox/Keras NN libraries), torch.compile, Triton kernels, DeepSpeed, Megatron-LM, torchtitan, Accelerate.
- **Limitations**: data-hungry; energy-intensive; uninterpretable internals; brittle to distribution shift; optimization pathologies (vanishing/exploding gradients mitigated but not eliminated).
- **Risks**: dual-use of large training infrastructure; model weights as attack surface; environmental cost of training runs.
- **Open challenges**: scaling laws (do they hold?); understanding what transformers actually learn; grokking/generalization theory; biologically plausible alternatives to backprop.

### 3.2 Convolutional Neural Networks (CNNs)

- **Math foundations**: convolution theorem, translational equivariance, signal processing, Fourier analysis of learned filters.
- **Core architectures**: LeNet → AlexNet → VGG → GoogLeNet/Inception → ResNet → DenseNet → EfficientNet → ConvNeXt → ViT (transformers displaced pure CNNs for many tasks, but CNNs remain strong for efficiency and dense prediction).
- **Training methods**: same as general NNs; data augmentation critical (crop, flip, color jitter, RandAugment, MixUp, CutMix).
- **Evaluation metrics**: ImageNet top-1/top-5 accuracy (historical benchmark now saturated), mAP for detection, mIoU for segmentation, FID for generation.
- **Tools**: torchvision/torchvision.transforms, timm (PyTorch image models), Keras Applications, Detectron2 (Meta), MMDetection (OpenMMLab), segmentation_models.pytorch.
- **Limitations**: translation equivariance ≠ true spatial reasoning; adversarial examples; texture bias over shape bias; compute cost at high resolution.
- **Risks**: surveillance systems; deepfake/image manipulation; biased face recognition.
- **Open challenges**: resolution/compute scaling; combining CNN inductive biases with transformer expressiveness; efficiency for edge deployment.

### 3.3 Recurrent & Sequence Models (RNNs/LSTMs/GRUs)

- **Math foundations**: dynamical systems, state-space models, gated recurrent units, long-range dependency theory.
- **Core architectures**: vanilla RNN, LSTM, GRU, bidirectional RNNs, encoder-decoder RNNs, attention-augmented RNNs.
- **Training methods**: truncated BPTT, teacher forcing, scheduled sampling; largely displaced by transformers for language but still used in niche sequential domains (state estimation, certain robotics controllers, streaming edge tasks).
- **Evaluation metrics**: perplexity (language), BLEU/ROUGE (translation/summarization), task-specific accuracy.
- **Tools**: PyTorch nn.RNN/LSTM/GRU modules, Keras recurrent layers.
- **Limitations**: sequential computation prevents parallelization → slow training; vanishing gradients over long sequences (LSTMs mitigate but don't solve); transformers dominate where parallelizable data exists.
- **Risks**: legacy NLP systems still running RNNs; hallucination issues inherited by successors.
- **Open challenges**: state-space model revival (Mamba, S4, RWKV) offering RNN-like efficiency with transformer-like quality — see §3.6.

### 3.4 Transformers & Large Language Models

- **Math foundations**: self-attention (scaled dot-product), multi-head attention, positional encoding (sinusoidal, RoPE, ALiBi, YaRN), layer normalization, mixture-of-experts routing, KV caching, flash attention (IO-aware exact attention), information theory of next-token prediction.
- **Core architectures**: encoder-only (BERT family), decoder-only (GPT/Llama/Qwen/DeepSeek families), encoder-decoder (T5, BART), multimodal (vision-language models: LLaVA, Qwen-VL, GPT-4o-class), mixture-of-experts (Mixtral, DeepSeek-V3/R1 lineage, Qwen-MoE).
- **Training methods**: pretraining on trillions of tokens (next-token prediction, masked modeling for encoders), instruction tuning (SFT), RLHF/DPO/GRPO for alignment, continual pretraining, distillation (teacher→student), speculative decoding for inference.
- **Evaluation metrics**: perplexity, benchmark suites (MMLU, HumanEval/MBPP for code, GSM8K/MATH for reasoning, GPQA for science, HLE for frontier difficulty), human preference evals (Chatbot Arena Elo), safety evals (jailbreak, harmfulness benchmarks).
- **Tools**: HuggingFace transformers 5.24.1 (current stable, Nov 2026) + tokenizers + datasets + evaluate + PEFT + TRL; vLLM 0.34.0 (high-throughput serving; Model Runner V2 only, extensible KV cache default); SGLang, TensorRT-LLM, llama.cpp, Ollama, LMDeploy, ExLlamaV3; training stacks: DeepSpeed, Megatron-LM, torchtitan, NeMo, verl (RL), OpenRLHF.
- **Limitations**: hallucination (confident fabrication); context window limits (long-context retrieval still degrades); reasoning is shallow pattern-completion not verified deduction; knowledge cutoff; energy cost; emergent capabilities appear unpredictably with scale.
- **Risks**: misinformation at scale; automated cyber offense; persuasion/manipulation; loss-of-control scenarios if capabilities accelerate; economic displacement; concentration of power in frontier labs; model collapse from synthetic data.
- **Open challenges**: reliable reasoning (verification, self-consistency, search-augmented inference); long-horizon agentic tasks; continual learning without catastrophic forgetting; mechanistic interpretability (see §5.7); scaling efficiency; multimodal grounding beyond text.

### 3.5 Generative Models

- **Math foundations**: maximum likelihood, variational inference (ELBO), adversarial training (minimax game theory), score matching, diffusion (stochastic differential equations, DDPM/DDIM), normalizing flows (invertible transformations, change of variables), autoregressive modeling (chain rule factorization), energy-based models.
- **Core families**:
  - *Autoregressive*: GPT-style LLMs, PixelCNN/PixelSNAIL (images), MusicGen/audio codecs.
  - *VAEs*: variational autoencoders, β-VAE, VQ-VAE/VQ-GAN (discrete latent codes).
  - *GANs*: DCGAN, StyleGAN family, BigGAN, CycleGAN — image synthesis/editing.
  - *Diffusion*: DDPM, DDIM, latent diffusion (Stable Diffusion), flow matching, rectified flow — images, video, audio, 3D, molecules.
  - *Normalizing flows*: RealNVP, Glow, continuous normalizing flows — density estimation, sampling.
- **Training methods**: MLE for autoregressive; ELBO optimization (reparameterization trick) for VAEs; adversarial minimax for GANs; denoising score matching for diffusion.
- **Evaluation metrics**: FID/KID/IS (image quality/diversity), perplexity (text), CLIP score (text-image alignment), human preference (Elo), distributional distances for scientific generation.
- **Tools**: diffusers (HuggingFace), PyTorch, JAX/Flax, Stable Diffusion ecosystem, ComfyUI, k-diffusion, kornia, OpenAI/other APIs.
- **Limitations**: mode collapse (GANs); blurry VAE outputs; slow iterative sampling (diffusion, mitigated by distillation/consistency models); controllability remains imperfect; generated content can be statistically plausible but factually wrong.
- **Risks**: deepfakes and disinformation; IP/copyright issues in training data; dual-use (molecular design, cyber exploits); non-consensual imagery.
- **Open challenges**: fast few-step generation; controllable generation; evaluation of factual/physical plausibility; 3D/world-model generation; video generation coherence over time.

### 3.6 Specialized Architectures (beyond the transformer)

- **Graph Neural Networks (GNNs)**: message passing, spectral GNNs, GraphSAGE, GAT, Graph Transformer. Math: spectral graph theory, Weisfeiler-Lehman expressiveness. Applications: molecules, social networks, chip design, knowledge graphs. Tools: PyTorch Geometric, DGL, Spektral.
- **State-Space Models**: S4, S5, Mamba/Mamba-2, RWKV, Hyena. Math: linear dynamical systems, HiPPO theory, selective scan. Goal: transformer-quality with linear-time sequence modeling. Tools: mamba-ssm, causal-conv1d.
- **Spiking Neural Networks (SNNs)**: biologically plausible, event-driven, energy-efficient neuromorphic computing. Tools: snnTorch, Norse, Lava (Intel Loihi), Brian2.
- **Neural Architecture Search (NAS)**: automated design of architectures via RL, evolution, gradient-based search. Tools: NNI, AutoKeras, Optuna (general HPO), NAS-Bench.
- **Mixture of Experts (MoE)**: sparse activation for parameter efficiency at scale. Routing, load balancing, expert parallelism. Now standard in frontier LLMs.
- **World Models**: learned simulators predicting environment dynamics (Dreamer, GAIA-1-style video world models, Genie). Frontier research toward agents that plan in imagination.
- **Capsule Networks, HDC/VSA**: alternative paradigms — largely academic, limited practical adoption.

---

## PART 4 — AI APPLICATIONS

Applied fields that compose the architectures above into working systems. Status markers: most are **[EXISTING]** and commercially deployed.

### 4.1 Natural Language Processing (NLP)

- **Math foundations**: information theory, statistical language modeling, Bayesian NLP, formal semantics.
- **Subfields & methods**: tokenization (BPE, SentencePiece, tiktoken); morphological analysis; parsing (dependency, constituency); named entity recognition; coreference resolution; machine translation; summarization; question answering; information extraction; sentiment analysis; dialogue systems; text classification.
- **Current architecture paradigm**: transformer LLMs fine-tuned per task or used zero/few-shot; encoder models for classification/embedding; seq2seq for generation.
- **Evaluation metrics**: BLEU, ROUGE, METEOR, BERTScore, COMET (translation); F1 for NER/IE; human eval + LLM-as-judge for open-ended generation.
- **Tools**: HuggingFace transformers 5.24.1, spaCy, NLTK, Stanza, LangChain/LangGraph (agent frameworks), LlamaIndex (RAG), vLLM 0.34.0, vector DBs (Chroma, FAISS, Qdrant, pgvector, Milvus).
- **Capabilities today**: fluent multilingual generation, strong code generation, summarization, extraction, translation rivaling professionals on benchmarks. **Limits**: factual hallucination, arithmetic/reasoning errors, inability to verify own claims, bias.
- **Risks**: misinformation, spam/fraud at scale, manipulation, copyright disputes, job displacement in writing/translation.
- **Open challenges**: grounded factuality; reliable reasoning chains; efficient long-document understanding; low-resource languages.

### 4.2 Computer Vision (CV)

- **Math foundations**: projective geometry, Fourier/wavelet analysis, variational methods, Markov random fields, 3D reconstruction geometry.
- **Subfields & methods**: image classification; object detection (YOLO family, DETR, RCNN lineage); instance/semantic/panoptic segmentation (SAM, Mask2Former, U-Net lineage); pose estimation (OpenPose, MediaPipe, ViTPose); optical flow; depth estimation (MiDaS, ZoeDepth); image restoration; 3D vision (NeRF, 3D Gaussian Splatting); video understanding; OCR/document AI; face recognition/analysis; anomaly detection in images.
- **Training methods**: supervised on labeled datasets (ImageNet, COCO, OpenImages, SA-1B); self-supervised (MAE, DINO, CLIP-style contrastive image-text); RL for detection refinement (limited).
- **Evaluation metrics**: top-1 accuracy, mAP@IoU, mIoU, PCK (pose), PSNR/SSIM (restoration), FVD (video), LPIPS (perceptual).
- **Tools**: PyTorch 2.15 + torchvision, timm, OpenCV, MMDetection/Ultralytics YOLO, Detectron2, Segment Anything (Meta SAM), MediaPipe, Kornia, depth Anything.
- **Capabilities today**: object detection/segmentation near-human on standard benchmarks; zero-shot classification via CLIP lineage; foundation models for images (SAM for segmentation). **Limits**: robustness to distribution shift, adversarial perturbations, counting, fine-grained reasoning, 3D understanding.
- **Risks**: surveillance, biometric privacy, deepfakes, biased recognition across demographics, autonomous weapons targeting.
- **Open challenges**: out-of-distribution robustness; true 3D scene understanding; neuro-symbolic vision (detect *and* reason); video temporal reasoning.

### 4.3 Speech & Audio

- **Math foundations**: signal processing (Fourier, wavelets, spectrograms), hidden Markov models (historical), information theory, psychoacoustics.
- **Subfields & methods**: automatic speech recognition (ASR); text-to-speech (TTS); speaker diarization/verification; speech emotion recognition; audio classification; music generation; source separation; speech translation.
- **Current paradigm**: end-to-end transformer/conformer ASR (Whisper lineage, wav2vec 2.0, HuBERT); neural codecs + LLMs for TTS (VALL-E lineage); diffusion/flow-matching for audio generation.
- **Training methods**: supervised on paired audio-text (massive), self-supervised on unlabeled audio, RLHF for naturalness.
- **Evaluation metrics**: WER (word error rate), CER, MOS (mean opinion score for naturalness), speaker similarity, FAD for audio generation.
- **Tools**: Whisper (OpenAI), SpeechBrain, ESPnet, NeMo, torchaudio, librosa, Coqui TTS lineage, AudioLDM, MusicGen.
- **Capabilities today**: near-human ASR on clean English; multilingual TTS cloning voices from seconds of audio; real-time translation. **Limits**: noisy/accented speech, code-switching, prosody/emotion in TTS, music coherence.
- **Risks**: voice cloning fraud, deepfake audio scams, surveillance via always-on listening.
- **Open challenges**: robust ASR in noise; emotion-aware synthesis; efficient on-device speech; low-resource languages.

### 4.4 Robotics

- **Math foundations**: kinematics/dynamics, control theory (PID, MPC, LQR), state estimation (Kalman filters, particle filters), motion planning (RRT, PRM, CHOMP, TrajOpt), POMDPs.
- **Subfields & methods**: manipulation (grasping, dexterous hands); locomotion (quadrupeds, humanoids, legged robots); navigation (SLAM, path planning); robot learning (imitation learning, RL, diffusion policies); VLA models (vision-language-action: RT-2, π0 lineage); human-robot interaction; multi-robot coordination.
- **Training methods**: teleoperation data collection, imitation learning (behavior cloning, diffusion policy), RL in simulation (Isaac Lab, MuJoCo) with domain randomization for sim-to-real, RLHF for preference alignment.
- **Evaluation metrics**: task success rate, trajectory error, sim-to-real transfer gap, safety incident rates, time-to-task.
- **Tools**: ROS 2, NVIDIA Isaac Sim/Lab, MuJoCo, PyBullet, Drake, MoveIt, Open X-Embodiment dataset, LeRobot, HuggingFace LeRobot, Genesis physics engine.
- **Capabilities today**: warehouse/logistics robots deployed at scale; humanoid prototypes doing limited tasks; VLA models showing promising generalization in research settings. **Limits**: reliable manipulation in unstructured environments, long-horizon autonomy, safety certification, hardware cost/durability.
- **Risks**: physical harm from malfunction; autonomous weapons; labor displacement; surveillance robots.
- **Open challenges**: sample-efficient real-world learning; safe exploration near humans; whole-body control; general-purpose manipulation; certified safety guarantees.

### 4.5 Autonomous Systems (vehicles, drones, industrial)

- **Math foundations**: control theory, state estimation, occupancy grid mapping, sensor fusion, decision theory under uncertainty.
- **Methods**: modular pipelines (perception → prediction → planning → control); end-to-end learned driving (Tesla-style, Wayve, Comma); occupancy networks; behavior prediction; scenario-based testing.
- **Training methods**: imitation learning from human driving logs at massive scale; RL in simulation (CARLA, Waymax); real-world fleet data.
- **Evaluation metrics**: disengagement/mile, collision rate, ODD (operational design domain) coverage, simulation scenario pass rates.
- **Tools**: CARLA, Waymax, nuScenes/Waymo datasets, ROS/Autoware/Apollo stacks, NVIDIA DRIVE.
- **Capabilities today**: Level 2–3 ADAS widely deployed; robotaxis operating in limited geofenced areas (Waymo, Zoox); delivery drones in restricted corridors. **Limits**: long-tail edge cases, sensor degradation (rain/snow/glare), handoff to human fallback, liability/regulatory frameworks.
- **Risks**: fatal accidents (documented Tesla Autopilot incidents); weaponization of autonomous platforms; public trust collapse after high-profile failures.
- **Open challenges**: corner-case coverage; verifiable safety; sensor-fusion robustness; regulatory certification for learned components.

### 4.6 Recommender Systems

- **Math foundations**: collaborative filtering (matrix factorization), information retrieval (BM25, TF-IDF), ranking theory (learning-to-rank: LambdaMART, neural rankers), bandit theory, causal inference for recommendations.
- **Core algorithms**: matrix factorization (SVD, ALS), item-item/user-user CF, two-tower models, deep interest networks (DIN/DIEN), graph recommenders (LightGCN), sequence models (SASRec, BERT4Rec), generative recommenders (GPT-style next-item prediction; vLLM-GR announced Nov 2026 for LLM-based recsys inference).
- **Training methods**: supervised on implicit/explicit feedback; negative sampling; multi-task learning (CTR/CVR); bandit exploration (epsilon-greedy, Thompson sampling, LinUCB).
- **Evaluation metrics**: HR@K/NDCG@K, AUC for CTR, MAP, catalog coverage, diversity/serendipity, business metrics (conversion, watch time).
- **Tools**: RecBole, Surprise, implicit (library), LightGBM/XGBoost for rankers, TensorFlow Recommenders, Merlion/Tecton for feature pipelines.
- **Capabilities today**: drives majority of consumer internet engagement (YouTube, TikTok, Amazon, Netflix); real-time personalization at billion-user scale. **Limits**: filter bubbles, popularity bias, feedback loops, cold-start problem, evaluation-reality gap (offline metrics ≠ user welfare).
- **Risks**: addiction-by-design engagement optimization; radicalization pipelines; market manipulation; discrimination via proxy features.
- **Open challenges**: causal recommendation (what would user do if we *didn't* show item X?); multi-stakeholder fairness; long-term welfare optimization vs. short-term engagement.

### 4.7 Predictive Analytics, Forecasting & Anomaly Detection

- **Math foundations**: time-series analysis (ARIMA, state-space/Kalman), survival analysis, extreme value theory, Bayesian forecasting, change-point detection, conformal prediction.
- **Core methods**: classical (ARIMA, ETS, Prophet); ML (gradient boosting on lagged features, random forests); deep (LSTMs, Temporal Convolutional Networks, Transformers for time series — TimesFM, Chronos foundation models); anomaly detection (isolation forests, autoencoders, statistical process control, conformal anomaly detection).
- **Training methods**: supervised on historical series; foundation time-series models pretrained across corpora (zero-shot forecasting).
- **Evaluation metrics**: MASE, sMAPE, CRPS (probabilistic forecasts), precision/recall at fixed false-positive rate for anomaly detection.
- **Tools**: statsmodels, Prophet, NeuralForecast, GluonTS, sktime, PyOD, river (online ML).
- **Capabilities today: **widely deployed in demand forecasting, fraud detection, predictive maintenance, epidemiology, energy grids. **Limits**: non-stationarity, regime changes, black-swan events; anomaly detection suffers high false-positive rates.
- **Risks**: automated decisions on credit/insurance/health based on predictions; feedback loops (predicting arrests→policing→more arrests data); privacy in behavioral prediction.
- **Open challenges**: uncertainty calibration under distribution shift; causal forecasting; foundation models for time series; anomaly detection with explanations.

---

## PART 5 — ADVANCED AI

Frontier research areas. Tags: most are **[FRONTIER]**; AGI/superintelligence claims are **[HYPOTHETICAL]**.

### 5.1 AI Agents & Agentic AI

- **Definition**: systems that perceive, reason, plan, use tools, and act in an environment toward goals — beyond single-turn prediction.
- **Math foundations**: MDPs/POMDPs, planning under uncertainty, Bayesian experimental design, utility theory, information theory.
- **Core architectures**: ReAct (reason+act interleaved), tool-use/function-calling loops, plan-and-execute agents, reflection/self-critique loops (Reflexion), tree-of-thought/graph-of-thought search over reasoning, code-as-action (program-aided agents), computer-use agents (screenshot→action).
- **Training methods**: SFT on agent trajectories, RL for multi-step tasks (RL environments like WebArena, SWE-bench, OSWorld), distillation of successful trajectories, inference-time scaling (longer chains, best-of-n, self-consistency).
- **Evaluation metrics**: task success rate on agentic benchmarks (SWE-bench Verified, WebArena, GAIA, OSWorld, τ-bench), steps-to-solution, cost per task, safety violations.
- **Tools**: LangGraph, OpenAI Agents SDK, Anthropic Claude Agent SDK, Google ADK, CrewAI, AutoGen (Microsoft), smolagents (HuggingFace), browser/computer-use tools, MCP (Model Context Protocol).
- **Capabilities today [EXISTING/FRONTIER]**: real deployed agents handle coding subtasks, customer support, data analysis; benchmark scores rising rapidly but reliability remains far below human for long-horizon tasks (agents fail on ~30–50% of complex multi-step tasks even on best systems).
- **Limitations**: compounding errors over steps; poor long-horizon memory; prompt injection via tool outputs; cost/latency; cannot truly plan vs. pattern-match action sequences.
- **Risks**: autonomous cyber operations; fraud at scale; loss of human oversight; agent swarms amplifying errors; misaligned goals persisting across tool calls.
- **Open challenges**: reliable long-horizon planning; memory architectures; verifiable agent actions; sandboxing/containment; economic viability.

### 5.2 Multi-Agent Systems (MAS)

- **Math foundations**: game theory (Nash equilibria, mechanism design), distributed systems, consensus protocols, emergent behavior theory.
- **Core patterns**: supervisor-worker hierarchies, debate (AI safety via adversarial argument), ensemble/mixture-of-agents, market-based coordination, swarm intelligence (particle swarm, ant colony — classical MAS), generative agent simulations (Stanford Smallville-style).
- **Training methods**: independent RL per agent (self-play, MADDPG, QMIX for cooperative MARL), emergent communication learning, centralized training with decentralized execution (CTDE).
- **Evaluation metrics**: task completion, communication efficiency, equilibrium quality, emergent behavior analysis.
- **Tools**: Ray RLlib (multi-agent), PettingZoo, AutoGen/CrewAI for LLM-agent societies, Mesa (agent-based modeling).
- **Capabilities today**: LLM-multi-agent frameworks for software teams, research pipelines, simulations; MARL research systems for games/robotics. **Limits**: coordination overhead, error propagation, no guarantee of coherent collective behavior.
- **Risks**: collusion between agents; market manipulation by coordinated bots; uncontrolled emergent dynamics in deployed swarms.
- **Open challenges**: scalable coordination; alignment of agent collectives; understanding emergent capabilities/discontents.

### 5.3 AGI Research [HYPOTHETICAL core]

- **What it claims**: human-level (or beyond) general intelligence across all cognitive domains — learning, reasoning, creativity, social intelligence.
- **Status**: **NO working AGI exists**. Definitions vary widely (Narrow AI → AGI → Superintelligence is a spectrum, not a binary). Current LLMs show impressive breadth but lack: persistent memory, true world models, reliable planning, embodiment, continual learning, verifiable reasoning.
- **Research programs**: scaling laws (Chinchilla→current frontier), test-time compute scaling, world models, neurosymbolic integration, embodiment/robotics, memory architectures (MemGPT/Letta lineage, RAG++), continual learning, mechanistic interpretability as path to understanding.
- **Evaluation attempts**: AGI benchmarks are contested; ARC-AGI, HLE, GDPval, agentic suites — all have been partially saturated, indicating benchmarks lag capability.
- **Timeline claims**: expert estimates range from "already here in narrow senses" to "decades away" — genuinely uncertain. Surveys (AI Impacts, METR time-horizon studies) suggest task-length capability doubling ~every 7 months historically.
- **Risks**: if AGI is achieved, the transition could be rapid (intelligence explosion hypothesis — recursive self-improvement); control/alignment problems become existential.
- **Open challenges**: defining measurable AGI; bridging narrow competence to general competence; energy/compute constraints; alignment before capability.

### 5.4 Cognitive Architectures

- **Math foundations**: cognitive psychology models, production systems, Bayesian models of cognition, ACT-R/Soar architecture theory.
- **Core systems**: ACT-R (adaptive control of thought—rational), Soar, CLARION (dual-process), LIDA (global workspace), OpenCog (hybrid), modern descendants like CoALA (cognitive architectures for language agents), Generative Agents.
- **Distinction from ML**: these are *theories of mind* — structured, symbolic-ish, psychologically motivated — vs. learned black boxes. Mostly academic/research; limited commercial deployment.
- **Tools**: ACT-R tutorials, Soar suite, OpenCog (AGI research platform).
- **Limitations**: hand-crafted components don't scale; hard to validate against real cognition; modern LLMs absorb much of the practical goal (flexible general agents).
- **Open challenges**: unifying learning + reasoning + memory in one architecture; grounding symbols in perception/action; whether cognitive architectures or scaled NNs better approximate general intelligence.

### 5.5 Neuro-Symbolic AI

- **Math foundations**: differentiable logic, fuzzy logic, probabilistic logic, category theory (applied to cognition), neural theorem proving.
- **Core methods**: Logic Tensor Networks, DeepProbLog, Neural Theorem Provers, ∂ILP (differentiable inductive logic programming), semantic loss functions, neural-symbolic concept learner (NSCL), LLM+solver hybrids (LLM translates NL→formal, solver verifies; AlphaGeometry lineage for olympiad geometry).
- **Goal**: combine neural pattern recognition with symbolic reasoning guarantees — best of both: learn from data, reason reliably, explain decisions.
- **Tools**: DeepProbLog, ∂ILP, PyReason, LTN, Lean/Coq integration with LLMs, AlphaGeometry/AlphaProof lineage (DeepMind — now producing research-level proofs).
- **Capabilities today [FRONTIER]**: strong results on constrained reasoning tasks, math olympiad problems, visual question answering with compositional structure; not yet general-purpose.
- **Limitations**: formalization bottleneck (everything must be encoded in logic); most real-world knowledge resists clean formalization; hybrid systems often slower than pure neural approaches.
- **Open challenges**: automatic formalization at scale; learning when to trust neural vs. symbolic components; neurosymbolic foundation models.

### 5.6 AI Alignment & Safety

- **Math foundations**: decision theory, mechanism design, game theory, information theory (mutual information for oversight), causal inference, robustness theory.
- **Core research areas**:
  - *RLHF/DPO/constitutional AI*: training models to be helpful, harmless, honest via human/AI feedback.
  - *Interpretability*: mechanistic interpretability (circuits, features, sparse autoencoders — Anthropic lineage), probing, activation steering, sparse dictionary learning on model internals.
  - *Scalable oversight*: debate, recursive reward modeling, AI-assisted evaluation, weak-to-strong generalization.
  - *Robustness*: adversarial training, jailbreak/jailbreak-defense (constitutional classifiers), prompt injection defenses, data poisoning detection.
  - *Control*: tripwires, untrusted monitoring, AI control protocols (research agenda for containing potentially misaligned systems).
  - *Corrigibility*: shutdownability, interruptibility, off-switch games.
- **Training methods**: preference optimization (DPO, IPO, KTO, GRPO for reasoning), adversarial training, red-teaming pipelines, safety fine-tuning.
  - *Evaluation*: HarmBench, StrongREJECT, jailbreak suites, dangerous-capability evaluations (bio, cyber, persuasion), situational awareness tests.
- **Tools**: Anthropic Constitutional AI stack, OpenAI moderation/evals, HarmBench, garak (LLM vulnerability scanner), PyRIT (Microsoft red-teaming), inspect_ai (UK AISI eval framework), alignment research toolkits.
- **Status [FRONTIER]**: alignment techniques work reasonably for current models but degrade under capability jumps; no known solution for superintelligent alignment; interpretability is making real progress (features/sparse autoencoders) but nowhere near complete understanding of frontier models.
- **Risks**: the entire field exists because misaligned advanced AI is an existential-risk scenario; near-term risks (jailbreaks, misuse, bias) are already documented.
- **Open challenges**: alignment that survives self-improvement; interpretability at scale; verifying alignment properties formally; governance of dual-use capabilities.

### 5.7 Explainable AI (XAI)

- **Math foundations**: Shapley values (cooperative game theory), LIME (local surrogate models), information theory (mutual information for explanations), causal inference.
- **Core methods**: post-hoc explainers (SHAP, LIME, Integrated Gradients, DeepLIFT, Grad-CAM for vision); inherently interpretable models (decision trees, GAMs, sparse models, rule lists); concept-based explanations (TCAV, concept bottleneck models); mechanistic interpretability (features, circuits — overlaps §5.6); counterfactual explanations; example-based explanations (influence functions, TracIn).
- **Training methods**: interpretability is mostly post-hoc; inherently interpretable models trained with sparsity/monotonicity constraints.
- **Evaluation metrics**: faithfulness (does explanation predict model behavior?), stability, comprehensibility, user-study trust/calibration.
- **Tools**: SHAP, LIME, Captum (PyTorch), Alibi (Netflix), InterpretML, AIX360 (IBM), Lucid (CNN visualization), TransformerLens (mechanistic interp for transformers).
- **Limitations**: explanations can be unfaithful (plausible but wrong); post-hoc explanations don't guarantee the model "uses" the cited features; human comprehension of explanations is limited; no consensus on what "good" explanation means.
- **Risks**: false sense of understanding; explanations used to justify biased decisions; "explainability washing" in regulated industries.
- **Open challenges**: explanations for generative models; causal explanations; standardizing eval of explanations; interpretability for RL/agents.

---

## PART 6 — INTERDISCIPLINARY FIELDS

AI both draws from and contributes to these disciplines.

### 6.1 Computational Neuroscience

- **What it studies**: how biological brains compute — neural coding, oscillations, attention, memory systems, development.
- **Math foundations**: dynamical systems, information theory, Bayesian brain hypothesis, connectomics graph analysis, neural mass models.
- **Relevance to AI**: spiking networks, predictive coding theories, attention mechanisms inspired by visual cortex, neuromorphic hardware (Intel Loihi, IBM TrueNorth), reservoir computing, forward-forward algorithm (Hinton's alternative to backprop).
- **Tools**: Brian2, NEURON, NEST, PyNN; datasets: Allen Brain Observatory, MICrONS connectome.
- **Status**: primarily a source of inspiration, not a direct engineering field. Brain emulation remains **[HYPOTHETICAL]** — whole-brain emulation is a speculative long-term goal requiring connectomics + simulation capability far beyond current reach.

### 6.2 Cognitive Science

- **What it studies**: mind and cognition — perception, memory, language, reasoning, decision-making — empirically and computationally.
- **Math foundations**: Bayesian models of cognition, rational analysis, ACT-R production systems, Bayesian nonparametrics.
- **Relevance to AI**: evaluation paradigms for AI (do models show human-like reasoning biases? — e.g., LLMs reproduce human cognitive biases), developmental robotics, language acquisition theories, concept formation.
- **Key insight**: cognitive science provides the *benchmarks* and *theories* that AI both tests and implements. LLMs have become tools in cognitive science experiments themselves.
- **Open challenges**: whether human-like cognition is the right target for AI; bridging symbolic and connectionist accounts of mind.

### 6.3 Artificial Life (ALife)

- **What it studies**: life-like processes in artificial media — self-replication, evolution, development, ecologies — bottom-up rather than designed.
- **Core approaches**: cellular automata (Conway's Game of Life, Langton's ant), artificial chemistries, evolutionary computation (genetic programming, NEAT, HyperNEAT), swarm robotics, morphological computation, open-ended evolution research.
- **Relevance to AI**: evolutionary algorithms as alternative to gradient descent; open-endedness as a path to AGI (some researchers argue current AI lacks the open-ended innovation of biological evolution); artificial ecosystems for testing agent societies.
- **Tools**: NetLogo, Avida (digital organisms), NEAT-Python, DEAP.
- **Status [FRONTIER]**: active research community; no deployed commercial systems, but ideas (evolutionary search, novelty search) influence AutoML.
- **Open challenges**: achieving open-ended innovation; co-evolutionary dynamics; whether ALife insights scale to real intelligence.

### 6.4 Computational Biology

- **What it studies**: biological systems via computation — genomics, proteomics, structural biology, systems biology, epidemiology.
- **Math foundations**: bioinformatics algorithms (sequence alignment, HMMs, phylogenetics), dynamical systems for metabolic networks, graph theory for interactomes, statistical genetics.
- **Relevance to AI**: protein structure prediction (AlphaFold — arguably the most impactful AI-for-science result); single-cell analysis; drug discovery; gene regulatory network inference; AI-designed proteins/enzymes (RFdiffusion, ProteinMPNN); genomic foundation models (Enformer, Nucleotide Transformer).
- **Tools**: AlphaFold DB, ESM (Meta protein models), PyRosetta, Biopython/Bioconductor, scanpy (single-cell), GROMACS (MD simulation).
- **Status**: **[EXISTING]** and rapidly expanding — AlphaFold 3 predicts complexes; AI-designed binders entering clinical trials.
- **Open challenges**: predicting dynamics not just structures; whole-cell models; clinical validation of AI-designed molecules.

### 6.5 AI for Science (AI4Science)

- **What it studies**: using AI to accelerate scientific discovery across physics, chemistry, materials, climate, mathematics.
- **Landmark results**: AlphaFold (biology), AlphaGeometry/AlphaProof (math), GNoME (materials — 2.2M new crystals predicted), GraphCast/Pangu-Weather (weather forecasting beating NWP), DeepMind's materials/chemistry models, FunSearch/AlphaEvolve (evolving algorithms), AlphaDev (sorting algorithms for data centers).
- **Math foundations**: neural operators (Fourier neural operators for PDEs), physics-informed neural networks (PINNs), equivariant networks (respecting physical symmetries), neural surrogates for simulation.
- **Training methods**: physics-informed losses, simulation-generated data, multi-fidelity learning, foundation models for scientific data.
- **Evaluation metrics**: physical accuracy vs. ground-truth simulation/experiment, extrapolation to unseen regimes, downstream experimental validation.
- **Tools**: NVIDIA Modulus, DeepMind JAX ecosystem, PyTorch, torchdiffeq, DiffTaichi, FourCastNet lineage.
- **Status [FRONTIER→EXISTING]**: AI4Science is producing real discoveries, not just predictions — mathematicians credit AlphaProof-derived ideas, materials companies use GNoME outputs experimentally.
- **Risks**: AI-generated hypotheses that are plausible but wrong; over-reliance on simulation surrogates; reproducibility of AI-discovered results.
- **Open challenges**: AI scientists that generate hypotheses autonomously; integrating AI into the full scientific method (not just prediction); epistemic trust in AI-generated science.

---

## PART 7 — CROSS-CUTTING INFRASTRUCTURE

Not a "field" per se, but essential context for everything above.

### 7.1 Data Infrastructure

- **Datasets**: ImageNet (historical), LAION/COYO (image-text), Common Crawl, The Pile/DCLM (text), Open X-Embodiment (robotics), HuggingFace datasets hub (millions of datasets), data marketplaces and synthetic data pipelines.
- **Tools**: HuggingFace `datasets`, `evaluate`, `data-juicer` (data processing), streaming datasets, deduplication tools (deduplicate-text-datasets), Datasheets for Datasets documentation standard.
- **Key problems**: data quality > quantity; copyright/licensing; contamination (test data leaking into training); bias measurement.

### 7.2 Training Infrastructure

- **Distributed training**: PyTorch FSDP2, DeepSpeed ZeRO, Megatron-LM tensor/pipeline/expert parallelism, torchtitan (PyTorch-native pretraining), JAX pjit/sharding for TPUs.
- **Hardware**: NVIDIA H100/B200/GB200/Blackwell generation (NVFP4 support in PyTorch 2.15), AMD MI300/MI355X (ROCm 10 wheels), Google TPUs (JAX native), AWS Trainium, Intel Gaudi, Apple Silicon (MPS backend with FP8 in PyTorch 2.15), neuromorphic chips (Loihi).
- **Cloud**: AWS SageMaker, Google Vertex AI, Azure ML, CoreWeave/Lambda GPU clouds, HuggingFace Spaces/Endpoints for deployment.

### 7.3 MLOps & Deployment

- **Experiment tracking**: Weights & Biases, MLflow, TensorBoard, Neptune.
- **Model registries/versioning**: MLflow Model Registry, DVC, HuggingFace Hub (dominant for open models).
- **Serving**: vLLM 0.34.0 (LLM serving standard; OpenAI-compatible API, PagedAttention, continuous batching, speculative decoding), TensorRT-LLM, Triton Inference Server, TorchServe, ONNX Runtime, llama.cpp/Ollama for edge.
- **Orchestration**: Ray 2.60.1 (distributed compute + RLlib + Serve), Kubeflow, Airflow/Prefect for pipelines, BentoML for model-as-service.
- **Edge/mobile**: ExecuTorch (PyTorch mobile), ONNX Runtime Mobile, TensorFlow Lite (now part of LiteRT lineage), Core ML.

### 7.4 AI Framework Landscape Summary (versions as of Nov 2026)

| Framework | Version | Role |
|---|---|---|
| PyTorch | 2.15.0 | Dominant DL research+production framework |
| TensorFlow | 2.21.0 (2.22 rc1 pending) | Google's framework; strong mobile/edge legacy |
| JAX | 0.12.1 | XLA-compiled functional ML; TPU-native; research favorite for AI4Science |
| scikit-learn | 1.9.1 | Classical ML standard |
| HuggingFace transformers | 5.24.1 | Standard model hub + loading library |
| vLLM | 0.34.0 | Standard LLM inference/serving engine |
| Ray | 2.60.1 | Distributed computing + RLlib |
| Stable-Baselines3 | 2.x | RL algorithms standard |
| Gymnasium | 1.x | RL environment API standard |
| PEFT/TRL | current | Fine-tuning/alignment tooling |
| Lean 4 | current (elan) | Theorem proving + verified code generation |

---

## PART 8 — FRONTIER WATCHLIST & EMERGING AREAS

Fields at the bleeding edge as of late 2026. All **[FRONTIER]** unless noted — real research, partial results, no settled capability.

### 8.1 Inference-Time Scaling & Test-Time Compute

- **What**: Instead of bigger models, spend more compute at inference — longer chain-of-thought, best-of-n sampling, self-consistency, tree search over reasoning steps, verifier-guided decoding.
- **Math**: compute-optimal inference allocation (extending Chinchilla-style scaling laws to test time); verifier models; process reward models (PRMs).
- **Status**: demonstrably improves math/reasoning benchmarks; cost-latency tradeoff limits deployment; "overthinking" problem (models reason unnecessarily on easy problems).
- **Tools**: vLLM speculative decoding, sglang, custom beam/search harnesses, o1/R1-style reasoning traces in open models (DeepSeek-R1 lineage, Qwen reasoning variants).

### 8.2 World Models & Embodied Foundation Models

- **What**: learned simulators that predict environment dynamics — video-prediction world models (Genie lineage), action-conditioned models, neural physics engines.
- **Math**: latent dynamics models, RSSM (recurrent state-space models for imagination), diffusion-based future prediction.
- **Status**: research prototypes generate plausible interactive environments minutes long; far from reliable long-horizon simulation; key bet for robot learning (train in imagination) and agent planning.
- **Tools**: Genie/GameNGen research code, NVIDIA Cosmos (world foundation model), DreamerV3 lineage.

### 8.3 AI for Mathematics & Formal Verification

- **What**: AI systems proving theorems and verifying code — AlphaProof/AlphaGeometry lineage, DeepSeek-Prover, Goedel-Prover, LLM+Lean pipelines, autoformalization.
- **Status**: silver-medal-level at IMO 2024/2025 (real result); autoformalizing research mathematics remains unreliable; verified code generation (Lean-verified kernels) emerging in industry.
- **Tools**: Lean 4 + Mathlib, Coq, Isabelle, TPTP provers, LeanDojo datasets, harbor/verification harnesses.

### 8.4 Energy-Based & Physical AI

- **What**: physics-informed ML — neural operators for PDEs, PINNs, differentiable simulation (DiffTaichi/MuJoCo MJX), learned physics for robotics/materials.
- **Status**: useful as surrogate accelerators (100–1000× faster than classical solvers in some regimes); accuracy degrades outside training distribution; hybrid physics+ML the pragmatic path.

### 8.5 Neuromorphic & Efficient AI

- **What**: brain-inspired hardware/software — spiking neural networks on Loihi-class chips, analog in-memory computing, sub-threshold circuits, event cameras paired with SNNs.
- **Status**: orders-of-magnitude energy efficiency claims on narrow tasks; ecosystem immature; transformer inference on conventional GPUs still wins on most benchmarks. Watch for edge-AI breakthroughs.

### 8.6 Mechanistic Interpretability (the "microscope" on models)

- **What**: reverse-engineering neural networks — sparse autoencoders extracting interpretable features, circuit analysis, probing, activation engineering, model diffing across training.
- **Status**: real discoveries (e.g., identifiable feature directions for concepts, induction heads, refusal circuits); nowhere near full explanation of frontier models; Anthropic/OpenAI/DeepMind all investing heavily.
- **Tools**: TransformerLens, nnsight, SAELens (sparse autoencoder library), pyvene, Neuronpedia.

### 8.7 Synthetic Data & Model Collapse

- **What**: training on AI-generated data — synthetic instruction data, generated images for vision, self-play-generated environments.
- **Status**: works when carefully filtered (distillation pipelines); uncontrolled recursive training → "model collapse" (distribution narrowing, tail loss); legal/ethical questions about provenance; detection (watermarking, C2PA) is an arms race.

### 8.8 Embodied AI & Humanoid Robotics

- **What**: general-purpose robots with LLM/VLA brains — Figure, Tesla Optimus, Unitree, Agility; VLA models (RT-2, π0, GR00T lineage) mapping vision+language→motor commands.
- **Status**: demos impressive (household tasks, parkour); reliable deployment years away; data scarcity (robot trajectories) is the bottleneck; simulation-to-real remains unsolved for dexterity.
- **Tools**: LeRobot (HF), Isaac Lab, MuJoCo, Open X-Embodiment dataset, Genesis.

---

## PART 9 — EVALUATION & BENCHMARK LANDSCAPE

### 9.1 Benchmark families

- **Language/reasoning**: MMLU, GPQA, HLE (Humanity's Last Exam), ARC-AGI, GSM8K/MATH, LiveCodeBench, SWE-bench (Verified/Multimodal), τ-bench, GAIA, OSWorld, Chatbot Arena (Elo).
- **Vision**: ImageNet (saturated), COCO, ADE20K, RefCOCO, video benchmarks (Ego4D), medical imaging suites.
- **Speech**: LibriSpeech, WER leaderboards, TTS MOS evals.
- **Agents**: WebArena, WorkArena, TheAgentCompany, MLAgentBench.
- **Safety**: HarmBench, StrongREJECT, JailbreakBench, agentic safety evals (prompt injection, tool misuse), situational-awareness evals.
- **Science**: FrontierMath, ProofNet, materials/property prediction suites.

### 9.2 Evaluation methodology issues

- **Benchmark saturation**: scores hit ceilings → benchmarks rotate faster than science; contamination (test data in training corpora) inflates scores.
- **Goodhart's law**: "when a measure becomes a target…" — optimizing for benchmarks degrades real capability; reward hacking in RLHF/RL environments.
- **Human eval is expensive and noisy**: LLM-as-judge helps scale but inherits judge biases; arena Elo is gameable by style.
- **Distribution shift**: benchmarks measure in-distribution performance; deployment faces OOD inputs.
- **Best practice**: holdout evals, red-team continuously, measure calibration + robustness + safety alongside capability, track cost-per-task not just accuracy.

---

## PART 10 — FIELD RELATIONSHIP MAP

How the fields connect (who builds on whom):

```
AI Foundations (search, KR, planning, reasoning)
        │ provides guarantees, formalisms, classical tools
        ▼
Machine Learning (supervised/unsupervised/RL/transfer)
        │ provides the statistical learning paradigm
        ▼
Deep Learning (NNs, transformers, generative models)
        │ provides the dominant architectures
        ▼
AI Applications (NLP, CV, speech, robotics, agents, recsys)
        ▲
        │ informs & stress-tests
        │
Interdisciplinary (neuroscience, cog-sci, ALife, comp-bio, AI4Science)
        ▲
        │ safety/alignment/evals cut across ALL of the above
        │
Advanced AI (agents, MAS, AGI research, neuro-symbolic, alignment, XAI)
        │ synthesizes & extends everything; mostly frontier research
        │
Cross-Cutting: data infra, training infra, MLOps, hardware
```

Key dependency insights:
- Transformers (§3.4) are the substrate for most modern NLP (§4.1), agents (§5.1), and multimodal systems.
- RL (§2.4) powers agents, robotics, and LLM alignment (§5.6).
- Search/planning (§1.1/§1.4) is regaining importance inside agents and neuro-symbolic systems — the "old AI" hybridizing with deep learning.
- Interpretability/safety (§5.6/§5.7) is now a first-class field, not an afterthought.
- AI4Science (§6.5) is where AI capabilities are most verifiable — physics/math don't lie.

---

## PART 11 — GLOSSARY

- **AGI**: Artificial General Intelligence — human-level competence across domains **[HYPOTHETICAL]**.
- **ASI**: Artificial Superintelligence — intelligence exceeding human across all domains **[HYPOTHETICAL]**.
- **LLM**: Large Language Model — transformer trained on massive text corpora.
- **VLA**: Vision-Language-Action model — robot policy taking images+text→actions.
- **RLHF**: Reinforcement Learning from Human Feedback — preference-based alignment.
- **DPO**: Direct Preference Optimization — RLHF without explicit reward model.
- **RAG**: Retrieval-Augmented Generation — LLM + retrieved documents.
- **PEFT/LoRA**: Parameter-Efficient Fine-Tuning / Low-Rank Adaptation.
- **MoE**: Mixture of Experts — sparse conditional computation.
- **MCTS**: Monte Carlo Tree Search — planning via random rollouts.
- **PDDL**: Planning Domain Definition Language — standard for classical planning.
- **SNN**: Spiking Neural Network — neuromorphic, event-driven.
- **PINN**: Physics-Informed Neural Network.
- **OOD**: Out-of-Distribution — inputs unlike training data.
- **SOTA**: State of the Art.
- **TTFT/TPOT**: Time-to-First-Token / Time-Per-Output-Token (LLM latency metrics).
- **KV cache**: stored key/value attention states enabling efficient autoregressive decoding.
- **World model**: learned simulator predicting environment dynamics.
- **Mechanistic interpretability**: reverse-engineering model internals into human-understandable components.

---

## PART 12 — EXISTING CAPABILITIES vs. HYPOTHETICAL FUTURE AI

### 12.1 What exists today (2026) — honest assessment

| Capability | Status | Reality check |
|---|---|---|
| Human-level image classification | ✅ Existing | Surpassed on benchmarks; still brittle OOD |
| Human-level ASR (clean speech) | ✅ Existing | WER <5% on clean English; degrades in noise |
| Fluent multilingual text generation | ✅ Existing | LLMs write/persuade/translate at professional level |
| Code generation | ✅ Existing (partial) | SWE-bench ~70%+ on verified subset; still fails complex repos |
| Protein structure prediction | ✅ Existing | AlphaFold-class accuracy; transformative for biology |
| Game-playing superhuman (Go/chess/StarCraft) | ✅ Existing | Narrow superhuman in closed domains |
| Real-time machine translation | ✅ Existing | Near-human on major language pairs |
| Autonomous driving | ⚠️ Partial | Level 2–3 deployed; Level 5 not achieved |
| Reliable long-horizon agents | ⚠️ Frontier | ~50-70% success on best benchmarks; unreliable |
| Mathematical research assistance | ⚠️ Frontier | Competition-level proofs; not yet research-level autonomous |
| General human-level intelligence | ❌ Does not exist | No system matches human flexibility across domains |
| Consciousness/self-awareness in AI | ❌ Does not exist | No evidence, no agreed definition, no test |
| Recursive self-improving superintelligence | ❌ Hypothetical | Speculative; no demonstrated pathway |
| Whole-brain emulation | ❌ Hypothetical | Requires technology far beyond current |

### 12.2 The capability trajectory

- **What is genuinely new (2023–2026)**: LLMs crossing thresholds in reasoning (test-time compute, chain-of-thought), agentic tool use, multimodal integration, AI-for-science breakthroughs (AlphaProof, GNoME), rapid capability gains measured in months not years on some benchmarks.
- **What has NOT changed**: systems remain narrow in deployment despite broad surface competence; reliability on long-horizon tasks is the key unsolved problem; no persistent memory/continual learning; no verified internal reasoning; alignment remains imperfect.
- **The "jagged frontier"**: current AI is simultaneously superhuman (instant recall, pattern matching at scale) and subhuman (multi-step planning, physical manipulation, sustained coherence, knowing what it doesn't know). Progress is not uniform — some capabilities plateau while others jump.

---

## PART 13 — LEARNING ROADMAP & FIELD PRIORITIZATION

### 9.1 Recommended learning path (for building intelligent systems)

**Phase 1 — Foundations (2–4 months)**:
- Python + NumPy + pandas + matplotlib
- Linear algebra (essentials: vectors, matrices, SVD, eigenvalues)
- Probability & statistics (Bayes, distributions, hypothesis testing)
- Calculus for ML (gradients, chain rule intuition)
- **Resources**: 3Blue1Brown linear algebra/essence of calculus, StatQuest, "An Introduction to Statistical Learning" (free PDF), fast.ai

**Phase 2 — Classical ML (2–3 months)**:
- scikit-learn workflows end-to-end
- Regression/classification/clustering evaluation
- Feature engineering, cross-validation, hyperparameter tuning (Optuna)
- **Practice**: Kaggle tabular competitions (Titanic → house prices → more)

**Phase 3 — Deep Learning (3–4 months)**:
- PyTorch fundamentals (tensors, autograd, nn.Module)
- CNNs (build LeNet→ResNet from scratch; use timm pretrained)
- Backprop intuition (implement a small net manually once)
- **Practice**: train MNIST/CIFAR classifiers; fine-tune a pretrained model with PEFT

**Phase 4 — NLP & Transformers (3–4 months)**:
- Tokenization, embeddings, attention mechanism (implement scaled dot-product attention manually)
- HuggingFace transformers: load, fine-tune, evaluate models
- RAG pipelines (LangChain/LlamaIndex), vector DBs
- Prompt engineering, function calling, agent basics (LangGraph)
- **Practice**: build a RAG chatbot; fine-tune a small model (LoRA on a Qwen/Llama-class model)

**Phase 5 — Specialization (choose direction)**:
- *LLM engineering/agents*: advanced fine-tuning (SFT/DPO), inference optimization (vLLM, quantization), agentic systems, evals
- *Applied ML*: domain-specific (CV, speech, recsys, forecasting) — go deep on one
- *AI research*: math (linear algebra, optimization, information theory), a specialization (interpretability, RL, neuro-symbolic), reproduce papers
- *Robotics/autonomous*: ROS 2, control theory, RL environments, sim-to-real

**Phase 6 — Frontier awareness (ongoing)**:
- Read papers (arXiv cs.LG/cs.CL), follow frontier lab releases, track benchmarks
- Contribute to open-source ML projects
- Understand safety/alignment literature if working on frontier systems

### 9.2 Which fields matter most for building intelligent systems

**Tier 1 — Essential for any AI practitioner**:
1. **Deep Learning fundamentals** (NNs, backprop, transformers) — the substrate of everything modern.
2. **NLP/LLM engineering** — the most commercially and scientifically impactful current field.
3. **Python software engineering + data pipelines** — the craft layer.
4. **Statistics/evaluation** — knowing what "good" means; most ML failures are evaluation failures.

**Tier 2 — High value depending on direction**:
5. **Reinforcement Learning** — for agents, robotics, alignment research.
6. **Classical ML** (trees/boosting) — still dominant for tabular data; faster and more reliable than deep learning for structured problems.
7. **Computer Vision** — foundation models (SAM, CLIP) are general-purpose tools.
8. **MLOps/deployment** — the difference between a notebook and a product.

**Tier 3 — Specialized/niche**:
9. Search/planning/expert systems — critical for robotics, games, formal methods; less relevant for pure LLM work.
10. GNNs, SSMs, SNNs — active research areas; SSMs especially if tracking architecture innovation.
11. Cognitive architectures, ALife — intellectually important, limited industry demand.
12. Neuroscience/cog-sci — valuable for research and eval design, not for most engineering roles.

**Tier 4 — Frontier/hypothetical**:
13. AGI research, superintelligence — speculative; pursue only if aligned with specific research programs (frontier labs, academic AGI groups).
14. Whole-brain emulation, consciousness — speculative long-term research.

### 9.3 The honest meta-point

> The map is a map, not the territory. Fields blur (transformers appear in NLP, CV, speech, agents, and AI4Science simultaneously). The most valuable skill is not knowing every field — it is knowing which field solves which class of problem, and having the mathematical depth to go deeper when needed. Current AI is a toolkit of narrow specialists; building "intelligent systems" today means composing these specialists — LLMs for language, CNNs/ViTs for vision, RL for sequential decision-making, search/planning for guarantees, and evaluation infrastructure to keep it all honest.

---

## SOURCES

Version numbers verified November 2026 against:

- PyTorch releases: https://github.com/pytorch/pytorch/releases (v2.15.0, Oct 28, 2026 — rewritten NCCL backend, FSDP2, FP8/NVFP4, ROCm 10.0 wheels, CUDA 13.2 default)
- PyPI torch: https://pypi.org/project/torch/ (v2.15.0)
- TensorFlow releases: https://github.com/tensorflow/tensorflow/releases (v2.21.0 stable, v2.22.0-rc1 pending — Python 3.14 support, CUDA 13, TensorBoard decoupled)
- PyPI tensorflow: https://pypi.org/project/tensorflow/ (v2.21.0)
- JAX: https://github.com/google/jax + PyPI jax-v0.12.1 (Nov 18, 2026); version comparison: https://axiomi.si/guides/pytorch-vs-jax
- scikit-learn: https://pypi.org/project/scikit-learn/ (v1.9.1)
- HuggingFace transformers releases: https://github.com/huggingface/transformers/releases (v5.24.1, Nov 24, 2026; v5.24.0 Nov 21)
- vLLM releases: https://github.com/vllm-project/vllm/releases + https://vllm.ai (v0.34.0, Nov 16, 2026 — Model Runner V2 only, extensible KV cache default, 10 new models)
- Ray releases: https://github.com/ray-project/ray/releases (v2.60.1, Nov 23, 2026)
- Framework landscape: https://awesome-alternatives.com/categories/machine-learning-framework/
- PyTorch newsletter: https://pytorch.org/newsletter/november-2026/
- PyTorch 2.15 release notes: https://github.com/pytorch/pytorch/releases/tag/v2.15.0
- What is the latest Transformers: https://whatisthelatest.ai/latest/transformers/

General field references (canonical knowledge, no version dependency):

- Russell & Norvig, *Artificial Intelligence: A Modern Approach* (foundations, search, agents)
- Goodfellow, Bengio & Courville, *Deep Learning* (NN theory, generative models)
- Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning* (classical ML)
- Sutton & Barto, *Reinforcement Learning: An Introduction* (RL)
- Jurafsky & Martin, *Speech and Language Processing* (NLP)
- Szeliski, *Computer Vision: Algorithms and Applications* (CV)
- Dean & Barroso et al., various MLSys papers (systems)
- Hendrycks et al., "Measuring Massive Multitask Language Understanding" (benchmarks)
- Christiano et al., "Deep Reinforcement Learning from Human Preferences" (RLHF)
- Vaswani et al., "Attention Is All You Need" (transformers)
- Brown et al., "Language Models are Few-Shot Learners" (GPT-3)
- Jumper et al., "Highly accurate protein structure prediction with AlphaFold" (AI4Science)
- METR time-horizon studies (capability measurement)
- AI Impacts expert surveys (AGI timelines)

---

*Document compiled November 2026. All tool versions verified against official release pages at compilation time; versions will drift — always check current releases before installing.*

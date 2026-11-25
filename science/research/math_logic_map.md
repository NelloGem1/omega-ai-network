# 🧮 MATHEMATICS, LOGIC & FORMAL SCIENCES — COMPREHENSIVE CLASSIFICATION MAP

*A structured knowledge map of the entire mathematical sciences. Compiled Nov 25, 2026.*
*Every field documents: subfields, fundamental concepts, key principles, methods, applications, prerequisites, and connections. See §11 Gaps & Emerging Fields — this map is deliberately NOT claimed complete.*

---

## 📋 TABLE OF CONTENTS

1. [What Are the Formal Sciences?](#1-what-are-the-formal-sciences)
2. [Pure Mathematics](#2-pure-mathematics)
3. [Applied Mathematics](#3-applied-mathematics)
4. [Discrete Mathematics](#4-discrete-mathematics)
5. [Probability & Statistics](#5-probability--statistics)
6. [Information, Decision & Computational Sciences](#6-information-decision--computational-sciences)
7. [Formal Sciences: Logic, Foundations & Proof](#7-formal-sciences-logic-foundations--proof)
8. [Knowledge Hierarchy Framework](#8-knowledge-hierarchy-framework)
9. [How Mathematics Underpins CS, Engineering, Crypto & AI](#9-how-mathematics-underpins-cs-engineering-crypto--ai)
10. [Cross-Domain Connections & Prerequisite Ladder](#10-cross-domain-connections--prerequisite-ladder)
11. [Gaps & Emerging Fields](#11-gaps--emerging-fields)
12. [Sources](#12-sources)

---

## 1. WHAT ARE THE FORMAL SCIENCES?

The **formal sciences** (also called the *mathematical sciences*, *abstract sciences*, or *formal methods*) study abstract objects, structures, and the rules governing them — using **axioms, definitions, and deductive proof** rather than empirical experiment. They form the theoretical backbone of every other science and of all engineered technology.

### 1.1 The six great branches

| Branch | Character | Primary question |
|---|---|---|
| **Pure Mathematics** | Structures, patterns, beauty for their own sake | "What is true about abstract structure?" |
| **Applied Mathematics** | Math deployed to model real systems | "How do we compute/simulate reality?" |
| **Discrete Mathematics** | Finitary and countable structures | "How do we count, organize, and compute over finite sets?" |
| **Probability & Statistics** | Uncertainty and data | "How do we reason under uncertainty and learn from evidence?" |
| **Information/Decision Sciences** | Information, choice, control | "How is information measured, and how should agents choose?" |
| **Formal Sciences proper** | Logic, formal systems, proof | "What can be proven, computed, and mechanized?" |

### 1.2 Epistemology — how formal sciences differ from empirical ones

| Property | Formal Sciences | Empirical Sciences |
|---|---|---|
| Truth criterion | Proof from axioms | Experimental observation |
| Objects of study | Abstract (numbers, functions, spaces, structures) | Physical/empirical entities |
| Verification | Logical deduction; formal proof | Measurement; replication |
| Falsification | Disproof via counterexample or inconsistency | Failure of prediction |
| Knowledge accumulates | Additively (theorems are permanent) | Revocably (theories can be superseded) |
| Primary tools | Proof, computation, abstraction | Experiment, measurement, modeling |

### 1.3 The application ↔ theory cycle

Mathematics in the broad sense develops as a continuous interplay between application and theory (per Trinity College Dublin's framing):

```
Real-world problem  →  mathematical model  →  abstract theory
       ↑                                          ↓
       └──────────  new applications  ←────  new theorems
```

- **Applied Mathematics** is the entry point: turn engineering/physics/business problems into mathematics.
- **Pure Mathematics** is the deepening: once abstraction takes over, the structure itself becomes the object of study.
- **Formal Sciences** supply the foundations both sides stand on: logic says what "proof" means; computability says what "algorithm" means.

---

## 2. PURE MATHEMATICS

*Pure mathematics studies structures, patterns, and symmetries for their inherent interest. In practice, today's pure fields routinely become tomorrow's applied tools: number theory → cryptography, topology → data science, algebraic geometry → machine learning.*

### 2.1 Algebra

**Subfields:** elementary algebra; abstract/modern algebra; linear algebra; multilinear algebra; ring theory; field theory/Galois theory; group theory; module theory; representation theory; Lie theory; homological algebra; K-theory; universal algebra; nonassociative algebra.

**Fundamental concepts:**
- **Group** — set with an associative binary operation having identity and inverses (encodes symmetry)
- **Ring** — two operations (addition forms an abelian group; multiplication distributes)
- **Field** — ring where every nonzero element has a multiplicative inverse (ℚ, ℝ, ℂ, finite fields 𝔽_p)
- **Vector space / module** — algebraic structure generalizing linear spaces
- **Homomorphism / isomorphism** — structure-preserving maps; formal "sameness" of structures
- **Ideal** — kernel-like subset absorbing multiplication
- **Spectrum** — set of prime ideals; the modern bridge between algebra and geometry
- **Algebraic closure** — smallest extension field containing all roots of all polynomials

**Key principles:**
- **Symmetry = structure**: groups encode all possible symmetry; every continuous symmetry of space is a Lie group
- **Homomorphism theorems**: every quotient of a structure factors through a canonical map
- **Galois correspondence**: field extensions ↔ subgroups; settles solvability of polynomial equations by radicals
- **Fundamental theorem of algebra**: every degree-n polynomial over ℂ has exactly n roots (with multiplicity)
- **Structure theorems**: finitely generated abelian groups are ℤ^r ⊕ torsion; finite simple groups classified (CFSG)

**Methods:** axiomatic reasoning, diagram chasing, spectral sequences, sheaf methods (algebraic geometry), Gröbner bases (computational algebra), tensor products, adjoint functors, free constructions.

**Prerequisites:** set theory, logic, elementary proof; real analysis recommended.

**Connections:** number theory (rings of integers, class field theory); geometry (algebraic geometry, Lie groups); logic (model theory, universal algebra); CS (cryptographic groups — RSA uses cyclic groups, ECC uses elliptic-curve groups; Lie groups in robotics/control).

### 2.2 Number Theory

**Subfields:** elementary number theory; analytic number theory; algebraic number theory; arithmetic geometry; transcendental number theory; additive combinatorics; Diophantine geometry; prime number theory; modular forms; p-adic numbers; L-functions; automorphic forms.

**Fundamental concepts:**
- **Primes** — atoms of multiplication (Fundamental Theorem of Arithmetic)
- **Congruences / modular arithmetic** ℤ/nℤ
- **Euler totient φ(n)** — count of units mod n; the number-theoretic heart of RSA
- **Quadratic reciprocity** — law governing which primes are quadratic residues of others
- **Riemann zeta function** ζ(s) = Σ n^(−s) — encodes prime distribution
- **L-functions** — generalizations linking number theory to representation theory
- **Elliptic curves** — genus-1 algebraic curves with a group law; basis of modern cryptography
- **p-adic numbers** — completion of ℚ w.r.t. the p-adic metric; essential in modern NT

**Key principles:**
- **Prime Number Theorem**: π(x) ~ x/ln x — primes thin out logarithmically
- **Dirichlet's theorem**: infinitely many primes in every coprime arithmetic progression
- **Riemann Hypothesis** (OPEN, Millennium Prize): all nontrivial zeros of ζ lie on Re(s)=1/2 — sharpens prime distribution bounds
- **Fermat's Last Theorem** (Wiles, 1994): x^n + y^n = z^n has no positive integer solutions for n > 2
- **Modularity theorem**: every rational elliptic curve is modular — the bridge Wiles used

**Methods:** sieve methods (Selberg, large sieve), circle method (Hardy–Ramanujan–Vinogradov), modular forms, p-adic analysis, heights, exponential sums, automorphic representations.

**Prerequisites:** algebra (groups, rings, fields, Galois theory), complex analysis for analytic NT, algebraic geometry for arithmetic geometry.

**Connections:** algebra (Galois, algebraic geometry); analysis (zeta/L-functions); cryptography (RSA security = factoring hardness; ECC = discrete logarithm hardness; Diffie–Hellman key exchange); CS (primality testing — AKS deterministic polynomial algorithm 2002; hashing).

### 2.3 Geometry

**Subfields:** Euclidean/affine/projective geometry; differential geometry; Riemannian geometry; algebraic geometry; complex geometry; symplectic geometry; contact geometry; discrete/convex geometry; geometric group theory; non-Euclidean geometry; conformal geometry.

**Fundamental concepts:**
- **Manifold** — space locally modeled on ℝ^n, smoothly glued
- **Metric tensor / line element** — infinitesimal distance structure
- **Curvature** — Gaussian, sectional, Ricci, scalar; measures deviation from flatness
- **Connection / covariant derivative** — rule for differentiating tensor fields on manifolds
- **Geodesic** — shortest-path curve generalizing straight lines
- **Sheaf** — assigns algebraic data to open sets; modern language of geometry
- **Scheme** — Grothendieck's unification of algebraic geometry and commutative algebra
- **Moduli space** — parameter space classifying geometric objects
- **Symplectic form** — closed nondegenerate 2-form; the geometry of phase space

**Key principles:**
- **Gauss's Theorema Egregium**: Gaussian curvature is intrinsic — measurable from within the surface
- **Gauss–Bonnet theorem**: ∫ curvature dA = 2πχ — total curvature determined by topology
- **Noether's theorem**: every continuous symmetry ↔ conserved quantity (physics)
- **Brouwer fixed-point theorem**: continuous self-map of a disk has a fixed point
- **Parallel postulate independence**: rejection yields hyperbolic and elliptic geometries
- **Hairy ball theorem**: no nonvanishing continuous tangent vector field on S²

**Methods:** tensor calculus, exterior differential forms, moving frames, variational methods, elliptic PDEs on manifolds, sheaf cohomology, moduli theory, h-principle (Gromov).

**Prerequisites:** linear algebra, multivariable calculus, topology basics; ODEs for geodesics.

**Connections:** topology (manifold classification); algebra (algebraic geometry, schemes); analysis (geometric analysis); physics (general relativity, gauge theory, string theory); CS (computer graphics, robotics, computer vision, geometric deep learning).

### 2.4 Topology

**Subfields:** point-set/general topology; algebraic topology; differential topology; geometric topology; low-dimensional topology (2D, 3D, 4D); knot theory; manifold topology; homotopy theory; homology/cohomology theory; persistent homology & topological data analysis (applied interface).

**Fundamental concepts:**
- **Topological space** — set + collection of open sets satisfying axioms
- **Continuous map / homeomorphism** — "rubber-sheet equivalence"
- **Compactness, connectedness, separation axioms**
- **Homotopy / homotopy groups π_n** — deformations; higher-dimensional holes
- **Fundamental group π₁** — loops modulo homotopy; first algebraic invariant of a space
- **Homology H_n / cohomology H^n** — algebraic invariants counting holes in each dimension
- **Fiber bundle / fibration** — space locally a product
- **Cobordism** — classification of manifolds up to bounding a manifold

**Key principles:**
- **Brouwer invariance of domain/dimension**: continuous bijection of ℝ^n implies homeomorphism
- **Borsuk–Ulam theorem**: any map S^n → ℝ^n identifies some antipodal pair — yields ham sandwich theorem, necklace-splitting
- **Poincaré conjecture** (Perelman, 2003): every simply-connected closed 3-manifold is S³ — proved via Ricci flow
- **Surface classification**: closed surfaces classified by Euler characteristic & orientability
- **4-manifold richness**: Donaldson & Seiberg–Witten theory show 4D topology is wildly more complex than other dimensions

**Methods:** simplicial approximation, singular (co)homology, spectral sequences, obstruction theory, surgery theory, Ricci flow with surgery.

**Prerequisites:** set theory, analysis (compactness), basic algebra (groups for π₁).

**Connections:** geometry (differential topology of manifolds); analysis (geometric analysis, PDE on manifolds); algebra (homological algebra); CS (topological data analysis, persistent homology, network topology); physics (topological phases of matter, topological quantum field theory).

### 2.5 Analysis

**Subfields:** real analysis; complex analysis; functional analysis; harmonic analysis; measure theory; operator theory; several complex variables; potential theory; asymptotic analysis; geometric analysis; microlocal analysis.

**Fundamental concepts:**
- **ε–δ definition of limit** — rigorous foundation of calculus
- **Metric space / normed space** — abstract distance and size
- **Complete space (Banach/Hilbert spaces)** — spaces where Cauchy sequences converge
- **Measure & integration** — generalization of length/area/volume to arbitrary sets
- **Holomorphic function** — complex-differentiable; satisfies Cauchy–Riemann equations
- **Operator** — linear map between function spaces (differential operators, integral operators)
- **Distribution / generalized function** — Dirac delta and beyond; foundation of PDE theory
- **Fourier transform** — decomposes functions into frequencies
- **Spectrum of an operator** — generalized eigenvalues

**Key principles:**
- **Completeness & convergence**: Banach fixed-point theorem — contraction mappings have unique fixed points (basis of numerical analysis and ODE existence)
- **Cauchy integral theorem**: contour integrals of holomorphic functions vanish — the engine of complex analysis
- **Maximum modulus principle**: holomorphic functions attain max on boundary
- **Hahn–Banach theorem**: extension of linear functionals — separates points from closed convex sets
- **Riesz representation theorem**: continuous linear functionals on Hilbert spaces are inner products with vectors
- **Plancherel theorem**: Fourier transform preserves L² norm — unitary equivalence between position and frequency

**Methods:** ε–δ proofs, Lebesgue integration, functional calculus, Sobolev spaces, spectral theory, singular integrals, pseudodifferential operators, Calderón–Zygmund theory.

**Prerequisites:** calculus, real numbers, set theory, basic topology.

**Connections:** differential equations (existence/regularity via Sobolev spaces); geometry (geometric analysis, Ricci flow); probability (measure-theoretic probability, stochastic processes); physics (quantum mechanics = Hilbert space operator theory; Fourier optics); engineering (signal processing, control theory, PDE models).

### 2.6 Calculus & Differential Equations

**Subfields:** differential calculus; integral calculus; multivariable calculus; vector calculus; ordinary differential equations (ODEs); partial differential equations (PDEs); calculus of variations; differential forms; tensor analysis.

**Fundamental concepts:**
- **Derivative** — local rate of change; linear approximation
- **Integral** — accumulation; inverse operation of differentiation
- **Gradient, divergence, curl, Laplacian** — fundamental differential operators
- **ODE** — equation involving derivatives of one unknown function of one variable
- **PDE** — equation involving partial derivatives of several variables
- **Initial/boundary value problem** — constraints making a differential equation solvable
- **Phase space / flow** — trajectories of a dynamical system
- **Variational principle** — physical laws as stationary points of action functionals

**Key principles:**
- **Fundamental theorem of calculus**: differentiation and integration are inverse operations
- **Mean value theorems**: link average rate to instantaneous rate
- **Existence & uniqueness (Picard–Lindelöf)**: Lipschitz conditions guarantee unique local solutions of ODEs
- **Well-posedness (Hadamard)**: solution exists, is unique, and depends continuously on data
- **Maximum principle**: solutions of elliptic/parabolic PDEs attain extrema on boundary — basis of numerical schemes
- **Energy methods**: multiply PDE by solution and integrate to get a priori estimates

**Methods:** separation of variables, eigenfunction expansions, Green's functions, characteristics, finite differences, finite elements, spectral methods, perturbation methods, numerical continuation.

**Prerequisites:** algebra, trigonometry, basic limits; linear algebra for systems of ODEs/PDEs.

**Connections:** physics (nearly all of classical & quantum physics is differential equations); engineering (structural mechanics, fluid dynamics, heat transfer, control); CS (numerical simulation, graphics); biology (population dynamics, epidemiology, neural models); economics (optimal control, growth models).

### 2.7 Set Theory & Foundations

**Subfields:** naive/classical set theory; axiomatic set theory (ZFC); constructive set theory; alternative foundations (type theory, topos theory, homotopy type theory); large cardinals; forcing; inner model theory; independence results.

**Fundamental concepts:**
- **Set** — collection of objects (naive) or defined via axioms (ZFC)
- **Axioms of ZFC** — pairing, union, power set, infinity, replacement, separation, choice, extensionality, foundation
- **Cardinality** — size of a set; ℵ₀ (countable), continuum 2^ℵ₀
- **Ordinal numbers** — well-ordered sets; generalize natural numbers to transfinite
- **Axiom of Choice** — every family of nonempty sets has a choice function; independent of ZFC
- **Gödel universe L, forcing extensions** — methods for proving independence
- **Large cardinals** — strongly inaccessible, measurable, supercompact cardinals
- **Axiom of determinacy (AD)** — alternative to Choice; makes all sets Lebesgue measurable

**Key principles:**
- **Cantor's theorem**: no set is in bijection with its power set — hierarchy of infinities
- **Cantor's diagonal argument**: real numbers uncountable; Gödel's incompleteness (logic)
- **Continuum Hypothesis** (CH): 2^ℵ₀ = ℵ₁? — independent of ZFC (Gödel 1938, Cohen 1963)
- **Well-ordering theorem**: equivalent to AC
- **Foundation/regularity**: no set contains itself — prevents paradoxes

**Methods:** transfinite induction/recursion, forcing (Cohen), inner models, fine structure theory, Boolean-valued models, constructibility.

**Prerequisites:** logic (first-order logic), basic proof techniques.

**Connections:** logic (independence results, model theory); topology (cardinal invariants, descriptive set theory); category theory (topos-theoretic foundations); type theory (homotopy type theory as alternative foundation); computer science (type theory underlies proof assistants).

### 2.8 Category Theory

**Subfields:** pure category theory; homological algebra; topos theory; higher category theory; ∞-categories; monoidal/closed categories; enriched categories; operads; sheaf theory; derived categories.

**Fundamental concepts:**
- **Category** — objects + morphisms + composition laws (generalizes sets-with-functions, groups-with-homomorphisms)
- **Functor** — structure-preserving map between categories
- **Natural transformation** — map between functors
- **Adjunction** — universal relationship between functors ("free ⊣ forgetful")
- **Limit / colimit** — categorical product/sum; universal constructions
- **Monoidal category** — category with tensor product (vector spaces, representations)
- **Topos** — category generalizing Set with internal logic
- **∞-category / (∞,1)-category** — weak higher-category where morphisms between morphisms exist up to coherent homotopy

**Key principles:**
- **Yoneda lemma**: an object is fully determined by its interactions — "the category is determined by its morphisms"
- **Adjoint functor theorems**: existence of adjoints from completeness/cocompleteness + preservation conditions
- **Representability**: many constructions are representable functors (e.g., Spec of a ring)
- **Universal property**: defines objects by how they relate to all others, not by elements
- **Grothendieck's six functors**: formalism unifying cohomology theories in algebraic geometry

**Methods:** diagram chasing, universal properties, Kan extensions, model categories, simplicial methods, derivators, higher topoi.

**Prerequisites:** set theory, basic algebra, comfort with abstraction; topology for sheaves.

**Connections:** algebraic geometry (schemes, étale cohomology); topology (homotopy theory via ∞-groupoids); logic (topos logic, categorical logic); CS (functional programming — Haskell/Scala typeclasses; database theory; applied category theory); homotopy type theory (univalent foundations).

### 2.9 Logic (mathematical logic — see also §7)

**Subfields:** propositional logic; first-order/predicate logic; higher-order logic; modal logic; intuitionistic/constructive logic; many-valued logic; non-classical logics; model theory; proof theory; recursion theory; algorithmic information theory; philosophical logic.

**Fundamental concepts:**
- **Syntax vs semantics**: formulas (proof theory) vs structures (model theory)
- **Satisfiability / validity** — when formulas are true in all/some models
- **Completeness theorem**: every valid formula is provable (Gödel completeness, 1930)
- **Compactness theorem**: satisfiable every finite subset → satisfiable
- **Löwenheim–Skolem theorems**: model sizes are flexible
- **Decidability / undecidability** — whether truth is mechanically checkable
- **Model** — a structure interpreting a formal language

**Key principles:**
- **Soundness & completeness**: provable = true (for first-order logic)
- **Gödel's incompleteness theorems**: any consistent system containing arithmetic has true-but-unprovable statements (first); cannot prove own consistency (second)
- **Church–Turing thesis**: effective computability = Turing machine computability
- **Compactness → ultraproducts**: nonstandard analysis is a corollary of model theory

**Methods:** natural deduction, sequent calculus, tableau methods, resolution (automated theorem proving), ultraproducts, Ehrenfeucht–Fraïssé games, type theory.

**Prerequisites:** set theory, basic proof techniques, philosophy of mathematics optional.

**Connections:** foundations (set theory, proof theory); CS (formal verification, logic programming, SAT solving); mathematics itself (all rigorous proof rests on logic); philosophy (truth, meaning, existence).

---

## 3. APPLIED MATHEMATICS

*Applied mathematics turns real-world problems into mathematical models, solves them (often numerically), and interprets results back in physical terms.*

### 3.1 Mathematical Modeling

**Subfields:** physical modeling; biological modeling; economic/financial modeling; engineering modeling; social modeling; continuum mechanics; multi-scale modeling; uncertainty quantification.

**Fundamental concepts:**
- **Model** — simplified mathematical representation of a real system
- **Governing equations** — ODEs, PDEs, difference equations, stochastic equations
- **Constitutive relations** — material-specific laws closing a model
- **Dimensional analysis** — Buckingham π theorem; reduces parameter space
- **Scaling / asymptotic analysis** — dominant-balance approximations
- **Validation & verification (V&V)** — does the model match reality? is the computation correct?

**Key principles:**
- **Model hierarchy**: phenomenological → mechanistic → first-principles models trade simplicity for fidelity
- **Conservation laws**: mass, momentum, energy underpin most physical models
- **Dimensional homogeneity**: equations must be dimensionally consistent
- **Asymptotic regimes**: solutions simplify in distinguished limits (small/large parameters)

**Methods:** dimensional analysis, perturbation theory, scaling analysis, inverse problems, parameter estimation, uncertainty propagation (Monte Carlo, polynomial chaos).

**Prerequisites:** core calculus, ODEs/PDEs, linear algebra, basic probability.

**Connections:** every empirical science (physics, chemistry, biology, economics); engineering (all disciplines); statistics (model checking); numerical analysis (solution methods).

### 3.2 Numerical Analysis & Scientific Computing

**Subfields:** numerical linear algebra; numerical integration/differentiation; ODE/PDE solvers; root finding; interpolation/approximation; optimization algorithms; numerical stability; high-performance computing (HPC); scientific visualization; computational geometry algorithms.

**Fundamental concepts:**
- **Discretization** — replacing continuous problems by finite-dimensional ones
- **Convergence** — solution approaches true answer as mesh/time step → 0
- **Stability** — errors do not amplify catastrophically
- **Condition number** — sensitivity of problem to input perturbations
- **Truncation vs roundoff error** — approximation error vs floating-point error
- **Mesh / grid / elements** — spatial discretizations
- **Iterative vs direct solvers** — e.g., Jacobi/Gauss–Seidel vs LU decomposition

**Key principles:**
- **Lax equivalence theorem**: for linear problems, consistency + stability ⟹ convergence
- **Well-conditioned problems have unique solutions**; ill-conditioned problems amplify noise
- **Order of accuracy**: method with error O(h^p) converges p-th order
- **CFL condition**: explicit time-stepping stability requires Δt ≤ C·Δx (Courant–Friedrichs–Lewy)

**Methods:** finite differences, finite volumes, finite elements, spectral methods, boundary elements, Monte Carlo, quasi-Monte Carlo, multigrid, Krylov subspace methods, adaptive mesh refinement.

**Prerequisites:** linear algebra, calculus, ODEs/PDEs, basic programming; numerical linear algebra (SVD, QR, LU) essential.

**Connections:** applied math broadly (all computational modeling); CS (algorithms, HPC, GPU computing); engineering simulation; AI (training large models is numerical optimization at scale); climate/weather prediction; CFD; structural analysis.

### 3.3 Optimization & Operations Research

**Subfields:** linear programming; integer/mixed-integer programming; nonlinear programming; convex optimization; combinatorial optimization; dynamic programming; stochastic programming; game-theoretic optimization; multi-objective optimization; large-scale optimization.

**Fundamental concepts:**
- **Objective function** — quantity to minimize/maximize
- **Feasible set / constraints** — admissible solutions
- **Convexity** — any local optimum is global (for convex problems)
- **Duality** — every primal problem has a dual; strong duality under conditions
- **KKT conditions** — first-order necessary conditions for constrained optima
- **Gradient/Hessian** — first/second-order local behavior
- **Complexity class** — P, NP, NP-hard; determines algorithmic difficulty

**Key principles:**
- **Fundamental theorem of linear programming**: optimum at vertex of feasible polytope
- **Karush–Kuhn–Tucker conditions**: generalize Lagrange multipliers to inequality constraints
- **Convex duality**: maximizing concave / minimizing convex functions is tractable
- **No free lunch theorem**: no algorithm beats all others on all problems — average-case matters
- **P ≠ NP conjecture**: most important open problem in complexity (Millennium Prize)

**Methods:** simplex method, interior-point methods, branch-and-bound, cutting planes, gradient descent variants (SGD, Adam), simulated annealing, genetic algorithms, Benders decomposition, column generation.

**Prerequisites:** linear algebra, calculus, basic probability; linear programming foundations.

**Connections:** operations research (logistics, scheduling, supply chains); machine learning (training = optimization; deep learning = stochastic gradient descent); economics (utility maximization); engineering (optimal design, control); cryptography (lattice-based crypto relies on hardness of lattice problems).

### 3.4 Computational Mathematics

**Subfields:** symbolic computation; computer algebra systems; exact arithmetic; algorithmic geometry; computational algebraic geometry; computer-aided proof; formal verification (see §7); computational number theory; numerical-symbolic hybrid methods.

**Fundamental concepts:**
- **Symbolic computation** — manipulation of mathematical expressions exactly
- **Computer algebra system (CAS)** — software like Mathematica, Maple, SageMath, SymPy
- **Exact vs floating-point arithmetic** — rational/algebraic numbers vs IEEE doubles
- **Gröbner bases** — algorithmic tool for polynomial systems
- **Formal proof assistant** — software verifying proofs step-by-step (Lean, Coq, Isabelle)

**Key principles:**
- **Exactness**: symbolic methods avoid roundoff; essential for cryptography and number theory
- **Computational complexity governs feasibility**: which math problems are solvable in practice
- **Proof-carrying code**: programs come with machine-checked correctness proofs

**Methods:** Buchberger's algorithm (Gröbner bases), cylindrical algebraic decomposition, resultant methods, interval arithmetic, SAT/SMT solving, formal proof in dependent type theory.

**Prerequisites:** programming, algebra, basic algorithms; numerical methods for hybrid approaches.

**Connections:** CS (algorithms, formal methods); crypto (exact arithmetic, lattice algorithms); pure math (experimental mathematics, conjecture generation — Ramanujan machine, TxGraffiti); AI (automated theorem proving).

### 3.5 Mathematical Physics

**Subfields:** classical mechanics; quantum mechanics; statistical mechanics; general relativity; quantum field theory; string theory; condensed matter theory; fluid dynamics; plasma physics; mathematical biology interfaces; integrable systems.

**Fundamental concepts:**
- **Lagrangian/Hamiltonian mechanics** — variational formulations of dynamics
- **Action principle** — δS = 0 governs all fundamental physics
- **Wavefunction / Hilbert space** — quantum state space
- **Operator formalism** — observables as self-adjoint operators
- **Partition function** — bridge between statistical mechanics and thermodynamics
- **Gauge theory** — symmetry-based description of fundamental forces
- **Renormalization** — handling infinities in quantum field theory

**Key principles:**
- **Noether's theorem**: continuous symmetry → conserved quantity (energy, momentum, charge)
- **Least action principle**: systems follow paths extremizing action
- **Correspondence principle**: quantum mechanics reduces to classical in appropriate limit
- **Ergodic hypothesis**: time averages = ensemble averages (foundational for statistical mechanics)

**Methods:** PDE analysis, spectral theory, path integrals, operator algebras, conformal field theory, integrable system methods (inverse scattering, solitons), lattice methods, tensor networks.

**Prerequisites:** classical mechanics, PDEs, functional analysis (Hilbert spaces), group theory, differential geometry.

**Connections:** physics (of course); pure math (geometry, topology, algebra — physics drives pure math); engineering (quantum computing, materials); CS (quantum algorithms, simulation).

---

## 4. DISCRETE MATHEMATICS

*Discrete mathematics studies countable/finitary structures — the mathematics of computation itself.*

### 4.1 Graph Theory

**Subfields:** structural graph theory; extremal graph theory; algebraic graph theory; topological graph theory; geometric graph theory; probabilistic graph theory; network science (applied); graph algorithms; random graphs.

**Fundamental concepts:**
- **Graph** — vertices + edges; directed/undirected, weighted/unweighted
- **Path, cycle, connectivity, components**
- **Tree** — connected acyclic graph; minimum connector
- **Planarity** — embeddable in plane without crossings
- **Chromatic number** — minimum colors for proper vertex coloring
- **Matching, flow, cut** — central combinatorial structures
- **Spectral graph theory** — eigenvalues of adjacency/Laplacian matrices
- **Random graph models** — Erdős–Rényi, preferential attachment, small-world

**Key principles:**
- **Euler's formula**: V − E + F = 2 for planar graphs (generalized by Euler characteristic)
- **Kuratowski's theorem**: planar graphs exclude K₅ and K₃,₃ minors
- **Four color theorem**: every planar map is 4-colorable (proved by computer, 1976 — first major computer-assisted proof)
- **Max-flow min-cut theorem**: max flow = min cut capacity — cornerstone of network optimization
- **Handshaking lemma**: sum of degrees is even
- **Small-world phenomenon**: most real networks have short average path lengths

**Methods:** combinatorial arguments, graph algorithms (DFS, BFS, Dijkstra, Ford–Fulkerson, Kruskal/Prim), spectral methods, probabilistic method (Erdős), graph limits, expander theory.

**Prerequisites:** set theory, basic combinatorics, elementary algebra; linear algebra for spectral methods.

**Connections:** CS (data structures, algorithms, network routing, compilers — CFGs); operations research (network flow, scheduling); physics (lattice models, network science); biology (protein interaction networks, phylogenetics); social science (social networks); topology (graph embeddings).

### 4.2 Combinatorics

**Subfields:** enumerative combinatorics; extremal combinatorics; algebraic combinatorics; analytic combinatorics; probabilistic combinatorics; design theory; partition theory; matroid theory; order theory/combinatorial optimization interfaces.

**Fundamental concepts:**
- **Permutation / combination** — arrangements vs selections
- **Generating function** — encodes sequences as power series
- **Recurrence relation** — sequence defined by previous terms
- **Inclusion-exclusion** — counting union via intersections
- **Pigeonhole principle** — n+1 objects into n boxes forces collision
- **Ramsey theory** — unavoidable structure in large enough systems
- **Matroid** — abstraction of linear independence/graphic matroids
- **Design** — balanced incomplete block designs (BIBD), finite geometries

**Key principles:**
- **Pigeonhole principle**: forces structure from size alone
- **Ramsey's theorem**: for any coloring of large enough complete graph, monochromatic substructure exists
- **Sperner's lemma**: combinatorial analog of Brouwer fixed point
- **Hall's marriage theorem**: condition for perfect matching in bipartite graphs
- **Generating function duality**: sequences ↔ analytic functions; asymptotics via singularity analysis

**Methods:** bijective proofs, generating functions, sieve methods, probabilistic method, entropy methods, algebraic techniques (representation theory), computer enumeration.

**Prerequisites:** discrete math basics, induction, basic probability.

**Connections:** graph theory (designs, matchings); CS (algorithm analysis, data structures); number theory (additive combinatorics); statistics (design of experiments, sampling); cryptography (combinatorial designs in secret sharing).

### 4.3 Boolean Algebra & Logic-Based Structures

**Subfields:** Boolean algebra; propositional logic; Boolean function theory; switch-level design; logic minimization; digital circuit design; SAT solving; formal verification (Boolean methods).

**Fundamental concepts:**
- **Boolean algebra** — algebra of {0,1} with AND/OR/NOT satisfying lattice axioms
- **Boolean function** — mapping {0,1}^n → {0,1}; represented by truth tables, DNF/CNF, BDDs
- **Binary decision diagram (BDD)** — canonical representation enabling efficient manipulation
- **SAT (satisfiability)** — deciding if a Boolean formula has a satisfying assignment
- **Logic gate** — physical implementation of Boolean operations
- **Combinational vs sequential logic** — memoryless vs stateful circuits

**Key principles:**
- **De Morgan's laws**: duality between AND/OR under negation
- **Quine–McCluskey / espresso**: algorithms for minimal Boolean expressions
- **CNF transformation**: every Boolean formula equivalent to conjunctive normal form
- **Cook–Levin theorem**: SAT is NP-complete — the canonical NP-complete problem
- **Functional completeness**: {AND, OR, NOT} or {NAND} alone suffice for all Boolean functions

**Methods:** Karnaugh maps, Quine–McCluskey, BDD manipulation, SAT solvers (DPLL, CDCL), AIG rewriting, formal equivalence checking.

**Prerequisites:** propositional logic, set theory, basic digital electronics.

**Connections:** digital electronics (all hardware); CS (SAT solving, formal verification, hardware verification); cryptography (Boolean circuits implement ciphers); logic (§7); coding theory.

### 4.4 Algorithms & Data Structures

**Subfields:** algorithm design & analysis; data structures; computational complexity; randomized algorithms; approximation algorithms; streaming algorithms; parallel/distributed algorithms; quantum algorithms; online algorithms; algorithmic game theory.

**Fundamental concepts:**
- **Algorithm** — finite sequence of unambiguous steps solving a problem
- **Time/space complexity** — resource usage as function of input size
- **Big-O / Θ / Ω notation** — asymptotic growth classification
- **P, NP, NP-complete, NP-hard** — complexity classes
- **Lower bounds** — information-theoretic/communication/algebraic limits
- **Randomized algorithm** — uses randomness (Monte Carlo vs Las Vegas)
- **Amortized analysis** — average cost over sequences of operations

**Key principles:**
- **Master theorem**: recursive divide-and-conquer recurrence solutions
- **Potential method / accounting method**: amortized analysis techniques
- **Greedy stays ahead / exchange argument**: proving greedy optimality
- **Dynamic programming optimal substructure**: optimal solution contains optimal subsolutions
- **Reduction**: problem A reduces to B → solving B solves A; basis of NP-completeness proofs
- **P vs NP**: whether efficiently verifiable = efficiently solvable (OPEN, Millennium Prize)

**Methods:** divide-and-conquer, dynamic programming, greedy algorithms, backtracking, branch-and-bound, hashing, probabilistic analysis, amortization, competitive analysis (online algorithms).

**Prerequisites:** programming, discrete math, basic probability; linear algebra for some advanced algorithms.

**Connections:** all of CS; operations research; crypto (algorithmic hardness assumptions); computational biology; machine learning (training algorithms); physics (simulations).

### 4.5 Coding Theory & Cryptography Interfaces

**Subfields:** error-correcting codes; cryptographic primitives; information-theoretic security; lattice-based crypto; post-quantum crypto; zero-knowledge proofs (mathematical foundations).

**Fundamental concepts:**
- **Error-correcting code** — systematic redundancy enabling error detection/correction
- **Hamming distance / code rate** — distance vs efficiency tradeoff
- **Perfect code** — achieves Hamming bound with equality
- **Linear code** — codewords form a vector subspace
- **Cryptographic hardness assumption** — problem believed computationally intractable
- **Public-key cryptography** — asymmetric key establishment
- **Zero-knowledge proof** — prove knowledge without revealing it

**Key principles:**
- **Shannon's channel coding theorem**: reliable communication possible iff rate < capacity
- **Singleton bound**: d ≤ n − k + 1 for [n,k,d] codes
- **RSA security** rests on integer factorization hardness
- **ECC security** rests on elliptic-curve discrete logarithm hardness
- **Post-quantum crypto** must resist quantum attacks (lattice, code-based, hash-based, isogeny-based)

**Methods:** Hamming codes, Reed–Solomon codes, LDPC codes, polar codes, BCH codes, lattice reduction (LLL), number-theoretic transforms.

**Prerequisites:** algebra (finite fields, groups), linear algebra, information theory basics.

**Connections:** information theory (§6); number theory (RSA, ECC); algebra (finite fields, lattices); CS (implementation, side-channel attacks); communications engineering.

---

## 5. PROBABILITY & STATISTICS

*The mathematics of uncertainty, randomness, and data-driven inference.*

### 5.1 Probability Theory

**Subfields:** measure-theoretic probability; combinatorial probability; conditional probability/Bayes; random variables & distributions; limit theorems; stochastic processes; martingales; Markov chains; queuing theory; extreme value theory; large deviations.

**Fundamental concepts:**
- **Probability space** — (Ω, F, P): sample space, σ-algebra, probability measure
- **Random variable** — measurable function Ω → ℝ
- **Distribution function / density / mass function** — complete description of a random variable
- **Expectation, variance, moments** — summary statistics
- **Independence, conditional probability** — core dependence structures
- **Martingale** — fair-game process; E[X_{n+1}|F_n] = X_n
- **Markov property** — future depends only on present state

**Key principles:**
- **Kolmogorov axioms**: non-negativity, normalization, countable additivity
- **Law of large numbers**: sample means converge to expectation
- **Central limit theorem**: sums of iid variables → Gaussian (universal limit)
- **Bayes' theorem**: P(A|B) = P(B|A)P(A)/P(B) — updating beliefs with evidence
- **Optional stopping theorem**: martingale expectations preserved at stopping times
- **Total probability / law of total expectation**: decomposition over partitions

**Methods:** measure theory integration, characteristic functions, generating functions, coupling, Poisson approximation, Stein's method, martingale inequalities, renewal theory.

**Prerequisites:** measure theory (or at least integration), real analysis, basic combinatorics.

**Connections:** statistics (the inferential half); stochastic processes (§5.3); finance (option pricing, risk); physics (statistical mechanics, quantum probability); CS (randomized algorithms, machine learning); insurance/actuarial science.

### 5.2 Statistics & Statistical Inference

**Subfields:** descriptive statistics; frequentist inference; Bayesian inference; parametric & nonparametric statistics; regression analysis; hypothesis testing; experimental design; multivariate statistics; time series analysis; survival analysis; high-dimensional statistics; causal inference; statistical learning theory.

**Fundamental concepts:**
- **Population vs sample** — inference from data to underlying distribution
- **Parameter / estimator / statistic** — θ, θ̂(X), T(X)
- **Sufficiency, completeness** — when data reduction loses no information
- **Likelihood function** — L(θ|x) ∝ P(x|θ); basis of ML estimation
- **Prior / posterior / likelihood** — Bayesian inference components
- **Confidence interval / credible interval** — uncertainty quantification
- **p-value / Bayes factor** — evidence measures (contested interpretations)
- **Bias-variance tradeoff** — fundamental prediction dilemma
- **Confounding / selection bias** — threats to causal inference

**Key principles:**
- **Cramér–Rao bound**: lower bound on variance of unbiased estimators via Fisher information
- **Gauss–Markov theorem**: OLS is BLUE under classical assumptions
- **Law of large numbers + CLT** underpin asymptotic inference
- **Bayes' theorem** is the engine of Bayesian updating
- **Neyman–Pearson lemma**: likelihood ratio test is most powerful for simple hypotheses
- **Multiple comparisons problem**: testing many hypotheses inflates false positives (Bonferroni, FDR)

**Methods:** maximum likelihood estimation (MLE), method of moments, Bayesian MCMC, bootstrap/resampling, permutation tests, ANOVA, regression (linear, logistic, mixed-effects), generalized linear models, propensity score matching, instrumental variables, difference-in-differences.

**Prerequisites:** probability theory, calculus, linear algebra; measure theory for theoretical depth.

**Connections:** all empirical sciences (data analysis); machine learning (§6.6); epidemiology; econometrics; quality control; A/B testing in tech; survey methodology.

### 5.3 Stochastic Processes

**Subfields:** discrete-time processes; continuous-time processes; Markov chains; Brownian motion & diffusion processes; Lévy processes; point processes; queueing theory; renewal theory; stochastic calculus; filtering theory; interacting particle systems; random walks.

**Fundamental concepts:**
- **Stochastic process** — collection of random variables indexed by time/space
- **Markov chain** — memoryless state transitions
- **Stationarity** — distribution invariant under time shifts
- **Brownian motion** — continuous-time Gaussian process with independent increments
- **Martingale** — fair stochastic process
- **Poisson process** — random event arrivals
- **Itô integral / stochastic differential equation (SDE)** — calculus for random paths
- **Generator / transition semigroup** — operator description of Markov processes

**Key principles:**
- **Markov property**: P(X_{t+1}|history) = P(X_{t+1}|X_t)
- **Kolmogorov forward/backward equations**: evolution of Markov transition probabilities
- **Itô's formula / Itô isometry**: rules of stochastic calculus differ from ordinary calculus (second-order term)
- **Girsanov theorem**: change of measure for Brownian motion — foundation of mathematical finance
- **Martingale representation theorem**: every martingale is a stochastic integral
- **Ergodic theorem**: time averages → space averages for stationary ergodic processes

**Methods:** discrete-state analysis, generating functions, spectral methods, martingale techniques, Itô calculus, Monte Carlo simulation, thinning algorithms for point processes, fluid limits, heavy-traffic approximations.

**Prerequisites:** probability theory, real analysis; measure theory and functional analysis for rigor.

**Connections:** statistics (time series); finance (option pricing — Black–Scholes from Itô calculus); physics (statistical mechanics, quantum field theory — stochastic quantization); biology (population dynamics, gene expression noise); queueing (telecom, call centers); CS (randomized algorithms, probabilistic verification).

### 5.4 Experimental Design & Sampling

**Subfields:** classical experimental design; survey sampling; clinical trial design; A/B testing; optimal design; space-filling designs; adaptive designs; design of computer experiments (surrogate modeling).

**Fundamental concepts:**
- **Experimental unit / treatment / response** — basic design vocabulary
- **Randomization** — protects against confounding
- **Blocking / stratification** — control known nuisance variation
- **Replication / replication vs pseudoreplication** — true independent units
- **Factorial design** — varying multiple factors systematically
- **Response surface methodology** — modeling continuous factors
- **Power analysis** — sample size determination

**Key principles:**
- **Fisher's principles**: randomization, replication, local control
- **ANOVA decomposition**: partitioning variance into treatment + error components
- **Orthogonality of designs**: uncorrelated treatment estimates
- **Information matrix**: quantifies design efficiency

**Methods:** randomized controlled trials (RCTs), Latin squares, split-plot designs, fractional factorials, response surface designs, sequential probability ratio tests (SPRT), multi-armed bandits (adaptive designs).

**Prerequisites:** probability, statistics basics, linear models.

**Connections:** statistics (inference machinery); medicine (clinical trials); agriculture (historical origin — Rothamsted); tech industry (A/B testing); psychology; economics (natural experiments).

---

## 6. INFORMATION, DECISION & COMPUTATIONAL SCIENCES

*Sciences at the intersection of mathematics, information, and rational choice.*

### 6.1 Information Theory

**Subfields:** Shannon information theory; rate-distortion theory; network information theory; quantum information theory; algorithmic information theory; cryptographic information theory; statistical learning theory connections.

**Fundamental concepts:**
- **Entropy H(X)** — average uncertainty of a random variable
- **Mutual information I(X;Y)** — information shared between variables
- **Channel capacity C** — maximum reliable communication rate
- **Source coding / channel coding theorems** — fundamental limits of compression & transmission
- **Kullback–Leibler divergence** — distance between distributions
- **Rate-distortion function** — minimum rate for given distortion
- **Kolmogorov complexity** — algorithmic information content of individual objects

**Key principles:**
- **Shannon's source coding theorem**: compression below entropy is impossible; achievable asymptotically
- **Shannon's channel coding theorem**: reliable communication iff rate < capacity C = max I(X;Y)
- **Data processing inequality**: processing cannot increase mutual information
- **Channel capacity of Gaussian channel**: C = B log₂(1 + SNR) — Shannon–Hartley law
- **No free lunch in compression**: cannot compress all messages

**Methods:** entropy coding (Huffman, arithmetic), error-correcting codes, LDPC/polar codes, hypothesis testing via information measures, rate-distortion optimization, typical set arguments.

**Prerequisites:** probability, basic analysis; measure theory for rigor.

**Connections:** communications engineering (all digital comms); cryptography (entropy = security measure, perfect secrecy via one-time pad); CS (data compression, Kolmogorov complexity bounds computability); statistics (information criteria — AIC/BIC); machine learning (information bottleneck, mutual information maximization).

### 6.2 Game Theory & Decision Theory

**Subfields:** cooperative game theory; non-cooperative game theory; mechanism design; auction theory; evolutionary game theory; bargaining theory; social choice theory; decision theory under uncertainty; utility theory; behavioral game theory; algorithmic game theory.

**Fundamental concepts:**
- **Game** — players, strategies, payoffs
- **Nash equilibrium** — strategy profile where no player can unilaterally improve
- **Dominant strategy / iterated elimination** — solution concepts
- **Zero-sum games** — strictly competitive (minimax theorem)
- **Mechanism** — rules of a game designed to achieve desired outcome
- **Utility function** — preferences over outcomes
- **Expected utility / subjective expected utility** — rational choice under risk
- **Bayesian game** — games with incomplete information
- **Core, Shapley value** — cooperative solution concepts
- **Arrow's impossibility theorem** — no voting system satisfies all fairness axioms

**Key principles:**
- **Von Neumann minimax theorem**: every finite zero-sum game has a value in mixed strategies
- **Nash existence theorem**: every finite game has a mixed-strategy Nash equilibrium
- **Revelation principle**: any implementable outcome can be achieved by a direct truthful mechanism
- **Gibbard–Satterthwaite theorem**: every non-dictatorial voting system is manipulable
- **Expected utility maximization**: rational agent maximizes E[U] under risk
- **Allais paradox / Ellsberg paradox**: violations of expected utility → behavioral critiques

**Methods:** normal/extended form representation, backward induction, linear programming for zero-sum games, mechanism design constructions, evolutionary dynamics (replicator equation), computational equilibrium finding (simplicial subdivision, homotopy methods).

**Prerequisites:** probability, basic algebra; utility theory needs some analysis.

**Connections:** economics (market design, auctions — spectrum auctions, ad auctions); political science (voting, international relations); biology (evolutionary stable strategies, signaling); CS (algorithmic mechanism design, auctions for ad placement); AI (multi-agent systems, RL).

### 6.3 Control Theory & Dynamical Systems

**Subfields:** classical control (frequency domain); modern control (state space); optimal control; robust control; adaptive control; nonlinear control; stochastic control; hybrid systems; networked control; control of PDEs (distributed parameter systems); systems identification; MPC (model predictive control).

**Fundamental concepts:**
- **State-space model** — ẋ = Ax + Bu, y = Cx + Du (linear systems)
- **Transfer function** — frequency-domain I/O description
- **Stability** — asymptotic (eigenvalues in LHP), BIBO stability
- **Controllability / observability** — can inputs steer states? can outputs reveal states?
- **Feedback** — closed-loop control; fundamental to all engineering
- **Optimal control** — minimize cost functional subject to dynamics
- **Lyapunov function** — energy-like function proving stability
- **Kalman filter** — optimal linear estimator for noisy systems

**Key principles:**
- **Cayley–Hamilton theorem**: matrix satisfies its own characteristic polynomial
- **PBH test**: controllability/observability via rank conditions
- **Pontryagin's maximum principle**: necessary conditions for optimal control
- **Bellman equation / dynamic programming**: optimal cost-to-go satisfies recursion
- **Separation principle**: for LQG, estimation and control can be designed independently
- **Lyapunov's direct method**: stability via energy decrease
- **Small-gain theorem**: stability of interconnected systems under gain bounds

**Methods:** state-space analysis, pole placement, LQR/LQG design, root locus, Bode/Nyquist plots, Lyapunov methods, MPC optimization, Kalman filtering, system identification (subspace methods), backstepping for nonlinear systems.

**Prerequisites:** linear algebra (matrix theory), differential equations, basic probability (for stochastic control).

**Connections:** engineering (aerospace, automotive, robotics, power systems, process control); CS (real-time systems, robotics planning); economics (dynamic optimization); neuroscience (motor control models); AI (reinforcement learning is optimal control with unknown dynamics).

### 6.4 Complexity Theory

**Subfields:** computational complexity (P, NP, PSPACE, EXPTIME); circuit complexity; communication complexity; proof complexity; average-case complexity; parameterized complexity; fine-grained complexity; quantum complexity; descriptive complexity; structural complexity.

**Fundamental concepts:**
- **Time/space complexity classes** — resource-bounded computation classes
- **NP-completeness** — hardest problems in NP; Cook–Levin theorem (SAT)
- **Oracle machines / relativization** — computation with black-box subroutines
- **Circuit complexity** — size/depth of Boolean circuits needed
- **Communication complexity** — bits needed for distributed computation
- **Proof complexity** — length of proofs in formal systems
- **P ≠ NP** — the central open problem (Millennium Prize, $1M)

**Key principles:**
- **Cook–Levin theorem**: SAT is NP-complete — every NP problem reduces to it
- **Karp–Lipton theorem**: if NP ⊆ P/poly then PH collapses
- **Savitch's theorem**: NSPACE(s) ⊆ DSPACE(s²)
- **Hierarchy theorems**: more time/space → strictly more problems solvable
- **Natural proofs barrier** (Razborov–Rudich): explains why circuit lower bounds are hard
- **IP = PSPACE** (Shamir): interactive proofs capture polynomial space
- **BPP ⊆ Σ₂ ∩ Π₂**: randomized computation is not too powerful

**Methods:** diagonalization, circuit lower bound techniques, algebraic methods (polynomial identity testing), probabilistic method, communication protocols, arithmetization, sum-of-squares hierarchy.

**Prerequisites:** algorithms, computability theory (§7), basic logic; some need algebraic geometry (PCP theorem).

**Connections:** CS (core of theoretical CS); crypto (NP-hardness → one-way functions assumption); logic (proof complexity connects to Gödel); optimization (NP-hard problems define intractability); quantum computing (quantum complexity classes).

### 6.5 Operations Research (OR) & Management Science

**Subfields:** linear/integer programming; network optimization; scheduling; inventory theory; queueing applications; facility location; transportation/logistics; supply chain management; revenue management; project management (PERT/CPM); multi-criteria decision analysis (MCDA).

**Fundamental concepts:**
- **Decision variables** — quantities under control
- **Objective + constraints** — optimization formulation
- **Relaxation** — dropping constraints for tractable bounds
- **Heuristic / metaheuristic** — approximate solution methods
- **Critical path** — longest path determining project duration
- **Safety stock** — buffer inventory against uncertainty

**Key principles:**
- **Simplex method** solves LP in practice polynomially (Karmarkar interior-point provably polynomial)
- **Branch-and-bound**: exact method for integer programs via relaxation bounds
- **Critical path method**: minimum project duration = longest path in precedence network
- **Newsvendor model**: optimal order quantity balances overage vs underage costs
- **Queueing tradeoff**: utilization vs waiting time (Kingman's formula)

**Methods:** simplex/interior-point, branch-and-cut, heuristics (greedy, local search, genetic algorithms, simulated annealing, tabu search), Monte Carlo simulation, queuing analysis, linear programming under uncertainty (stochastic programming, robust optimization).

**Prerequisites:** optimization (§3.3), probability, linear algebra.

**Connections:** business/management; logistics; manufacturing; healthcare (surgery scheduling, resource allocation); defense (logistics); economics; engineering.

### 6.6 Machine Learning & AI Foundations (Mathematical View)

**Subfields:** statistical learning theory; supervised learning; unsupervised learning; reinforcement learning; deep learning (mathematical aspects); optimization for ML; generalization theory; PAC learning; kernel methods; graphical models; Bayesian deep learning; neural network theory.

**Fundamental concepts:**
- **Empirical risk minimization** — minimize training error
- **Generalization gap** — difference between training and test error
- **VC dimension** — capacity measure of hypothesis class
- **PAC learning** — probably approximately correct framework
- **Kernel trick** — implicit high-dimensional feature maps via inner products
- **Neural network** — parameterized function composed of linear maps + nonlinearities
- **Loss function** — training objective
- **Regularization** — penalty preventing overfitting

**Key principles:**
- **Bias-variance decomposition**: test error = bias² + variance + irreducible noise
- **No free lunch theorem**: no learner dominates all others on all distributions
- **Universal approximation theorem**: sufficiently large neural networks approximate any continuous function
- **Gradient descent convergence**: under smoothness/strong convexity assumptions, GD converges
- **Double descent**: modern overparameterized models defy classical bias-variance — active research area
- **PAC-Bayes bounds**: generalization bounds via posterior distributions

**Methods:** empirical risk minimization, SGD variants (Adam, momentum), backpropagation (chain rule), kernel methods (SVM, kernel ridge), boosting, EM algorithm, MCMC, variational inference, attention mechanisms (transformers), optimization (L-BFGS, Newton methods).

**Prerequisites:** probability, statistics, linear algebra, multivariable calculus, optimization; functional analysis for theory.

**Connections:** statistics (§5.2); optimization (§3.3); information theory (§6.1); computation (§4.4); neuroscience (inspiration for neural nets); all application domains of AI.

---

## 7. FORMAL SCIENCES: LOGIC, FOUNDATIONS & PROOF

*The sciences of formal systems themselves — what can be proven, computed, and mechanized.*

### 7.1 Mathematical Logic

**Subfields:** propositional logic; first-order logic; higher-order logic; modal logic (necessity/possibility); intuitionistic/constructive logic; many-valued & fuzzy logic; paraconsistent logic; relevance logic; linear logic; non-standard analysis (model-theoretic); abstract model theory.

**Fundamental concepts:**
- **Formal language** — alphabet + grammar generating well-formed formulas
- **Axiom / inference rule** — starting points and deduction rules
- **Proof / derivation** — finite sequence of formulas each justified by rules
- **Semantics** — truth in structures/models
- **Soundness** — provable → true
- **Completeness** — true → provable
- **Consistency** — no contradictions derivable
- **Decidability** — whether validity is mechanically checkable

**Key principles:**
- **Soundness & completeness of first-order logic** (Gödel): provable = valid
- **Compactness theorem**: every finitely satisfiable theory is satisfiable — yields nonstandard analysis, ultraproducts
- **Löwenheim–Skolem**: countable theories have countable models (downward); infinite models of any larger cardinality (upward)
- **Gödel incompleteness (first)**: consistent systems containing arithmetic have true-but-unprovable statements
- **Gödel incompleteness (second)**: such systems cannot prove own consistency
- **Church–Turing thesis**: all reasonable models of effective computation are equivalent
- **Lindenbaum's lemma**: every consistent theory extends to a complete consistent theory

**Methods:** natural deduction, sequent calculus, Hilbert-style systems, tableau method, resolution (Robinson), model construction, ultraproducts, Ehrenfeucht–Fraïssé games, forcing for independence.

**Prerequisites:** set theory, basic proof techniques; philosophy optional.

**Connections:** foundations (set theory, type theory); CS (SAT solving, formal verification, logic programming, database theory); all of mathematics (proof itself); philosophy (truth, meaning, existence).

### 7.2 Proof Theory & Formal Systems

**Subfields:** Hilbert-style systems; natural deduction; sequent calculus; structural proof theory; cut elimination; ordinal analysis; reverse mathematics; proof mining; provability logic; proof complexity (interaction with §6.4).

**Fundamental concepts:**
- **Formal system** — language + axioms + rules of inference
- **Proof normalization / cut elimination** — removing detours from proofs
- **Subformula property** — proofs only use subformulas of conclusion
- **Consistency proof** — proof that a system has no contradictions
- **Ordinal analysis** — measuring consistency strength via ordinals
- **Reverse mathematics** — which axioms are needed for which theorems

**Key principles:**
- **Gentzen's cut-elimination theorem**: sequent calculus proofs can be normalized
- **Curry–Howard correspondence**: proofs ↔ programs; propositions ↔ types; normalization ↔ computation termination
- **Gentzen's consistency proof for PA**: arithmetic consistency via ordinal analysis up to ε₀
- **Reverse mathematics**: over RCA₀, many theorems equivalent to ACA₀, ATR₀, Π¹₁-CA₀ — big five systems
- **Hilbert's program**: formalize all mathematics finitely — shown impossible by Gödel, but partially rehabilitated by ordinal analysis

**Methods:** sequent calculus manipulation, natural deduction trees, ordinal notation systems, proof mining (extracting computational content), functional interpretation (Dialectica interpretation), realizability.

**Prerequisites:** mathematical logic, basic proof theory; type theory for Curry–Howard.

**Connections:** logic (§7.1); type theory (§7.4); CS (proof assistants use Curry–Howard — Lean, Coq); foundations (consistency strength hierarchy).

### 7.3 Computability & Recursion Theory

**Subfields:** Turing machines; recursive functions; λ-calculus; register machines; degrees of unsolvability; computable analysis; algorithmic randomness; Kolmogorov complexity; oracle computation; enumeration degrees; inductive inference.

**Fundamental concepts:**
- **Turing machine** — abstract device manipulating tape symbols; universal definition of computation
- **Recursive/decidable function** — computable by algorithm
- **Recursively enumerable (RE)** — enumerable but not necessarily decidable
- **Halting problem** — undecidable (Turing, 1936)
- **Reduction** — problem A reduces to B if solving B solves A
- **Turing degree** — relative computability classification
- **Oracle machine** — TM with black-box subroutine
- **Computable real number** — reals computable to arbitrary precision

**Key principles:**
- **Church–Turing thesis**: every effectively calculable function is Turing-computable
- **Undecidability of halting**: no algorithm decides whether arbitrary programs halt
- **Rice's theorem**: every nontrivial semantic property of programs is undecidable
- **Kleene's recursion theorem**: programs can produce their own descriptions
- **s-m-n theorem**: parameter specialization of computable functions
- **Hierarchy theorems**: time/space hierarchies for computable functions
- **Algorithmic information theory**: Kolmogorov complexity K(x) = length of shortest program producing x — uncomputable but deeply useful

**Methods:** diagonalization, recursion theorem applications, priority arguments, forcing for computability, algorithmic randomness (Martin-Löf tests), lattice of c.e. degrees.

**Prerequisites:** logic, basic set theory; programming intuition helps.

**Connections:** CS (all of theoretical CS); complexity (§6.4); logic (§7.1); algorithmic information theory connects to information theory (§6.1); cryptography (one-way functions relate to average-case vs worst-case hardness).

### 7.4 Type Theory & Formal Verification

**Subfields:** simple type theory; dependent type theory; homotopy type theory (HoTT); Martin-Löf type theory; System F / polymorphic lambda calculus; intuitionistic type theory; category-theoretic semantics of type theory; proof assistants; program verification; certified programming.

**Fundamental concepts:**
- **Type** — classification of terms (like sets, but constructive)
- **Dependent type** — type depending on a term (e.g., vectors of length n)
- **Propositions as types / Curry–Howard**: proofs = programs, propositions = types
- **Universe** — type of types
- **Identity type / path type** — equality as a type, not a proposition
- **Univalence axiom** — equivalent types are equal (in HoTT)
- **Proof assistant** — software checking proofs: Lean 4, Coq/Rocq, Isabelle/HOL, Agda, Metamath

**Key principles:**
- **Curry–Howard–Lambek correspondence**: proofs ↔ programs ↔ categorical morphisms — triple isomorphism
- **Univalence**: isomorphism = equality for types — makes type theory equivalent to homotopy theory
- **Canonicity**: closed terms of type-theoretic naturals compute to numerals
- **Proof irrelevance vs propositional truncation**: handling proof content in type theory
- **Normalization for type theories**: ensures type checking terminates (for strongly normalizing systems)

**Methods:** natural deduction style, tactics (in Lean/Coq), rewriting, dependent elimination, higher inductive types (HoTT), cubical type theory, proof search heuristics, SMT integration.

**Prerequisites:** logic, basic programming, λ-calculus; category theory for semantics.

**Connections:** logic (§7.1–7.3); category theory (§2.8); topology (HoTT = synthetic homotopy theory); CS (verified software, compiler correctness, proof-carrying code); mathematics (formalization of major theorems — four color theorem, Kepler conjecture, odd order theorem).

### 7.5 Formal Methods & Automated Reasoning

**Subfields:** theorem proving (automated & interactive); model checking; SAT/SMT solving; program verification; deductive verification; abstract interpretation; symbolic execution; proof-carrying code; formal specification.

**Fundamental concepts:**
- **Theorem prover** — software deriving proofs automatically or interactively
- **Model checker** — exhaustively verifies finite-state system properties
- **SAT solver** — decides Boolean satisfiability (DPLL, CDCL algorithms)
- **SMT solver** — SAT + theories (linear arithmetic, arrays, bitvectors)
- **Hoare logic** — {P} C {Q} program correctness triples
- **Abstract interpretation** — approximate semantics for static analysis
- **TLA+ / Z / Alloy** — formal specification languages

**Key principles:**
- **Soundness of verification**: verified property truly holds (if checker is sound)
- **Completeness tradeoff**: full verification is undecidable; practical methods are sound but incomplete
- **Small model property**: many logics have finite counterexamples — enables model checking
- **CDCL efficiency**: conflict-driven clause learning makes modern SAT solvers practical

**Methods:** resolution, tableau, sequent calculus automation, BDD-based model checking, bounded model checking, abstract interpretation domains (intervals, octagons, polyhedra), symbolic execution with constraint solving.

**Prerequisites:** logic, basic CS/programming; some need automata theory.

**Connections:** CS (software/hardware correctness); crypto (verified implementations); aerospace/defense (DO-178C requires formal methods); mathematics (automated theorem proving, AI for math).

---

## 8. KNOWLEDGE HIERARCHY FRAMEWORK

*An expandable hierarchy for organizing any mathematical/logic knowledge domain. Each level can be drilled into — this structure applies recursively.*

```
DOMAIN (e.g., Pure Mathematics)
 └── DISCIPLINE (e.g., Algebra)
      └── SUBDISCIPLINE (e.g., Representation Theory)
           └── FIELD (e.g., Modular Representations)
                └── CONCEPT (e.g., Brauer character)
                     └── PRINCIPLE (e.g., Brauer's theorem on blocks)
                          └── METHOD (e.g., decomposition matrix computation)
                               └── EXPERIMENT (e.g., GAP computation of small groups)
                                    └── EVIDENCE (e.g., published theorem, computer verification)
                                         └── APPLICATION (e.g., classification of finite simple groups)
                                              └── OUTCOME (e.g., Atlas of finite groups, sporadic group discovery)
```

### 8.1 Definitions of each level

| Level | What it is | Example |
|---|---|---|
| **Domain** | Broadest category of study | Pure Mathematics, Applied Mathematics, Formal Sciences |
| **Discipline** | Major recognized branch | Algebra, Topology, Probability, Logic |
| **Subdiscipline** | Specialized area within discipline | Algebraic Geometry, Algebraic Topology, Bayesian Statistics |
| **Field** | Specific research/topic area | Elliptic Curves over Finite Fields, Persistent Homology, Homotopy Type Theory |
| **Concept** | Fundamental idea/definition | Group, Manifold, Entropy, Nash Equilibrium, Turing Machine |
| **Principle** | Law/theorem governing concepts | Fundamental Theorem of Algebra, Bayes' Theorem, Noether's Theorem, Pigeonhole Principle |
| **Method** | Technique for applying principles | Gröbner bases, Monte Carlo simulation, spectral methods, proof by induction |
| **Experiment** | Concrete instantiation/test | Computing a decomposition matrix in GAP; simulating Brownian motion; SAT-solving a formula |
| **Evidence** | Result supporting knowledge | Published proof, computer verification, experimental data, counterexample |
| **Application** | Real-world use of the knowledge | ECC cryptography, medical imaging, A/B testing, verified software |
| **Outcome** | Measurable consequence | Secure communications, new materials, drug approvals, bug-free systems |

### 8.2 Why this hierarchy matters

1. **Prerequisite mapping**: to understand a Field, you need its Concepts and Principles; to apply a Method, you need the underlying Field.
2. **Cross-domain linking**: the same Concept (e.g., "group") appears in Algebra, Geometry (symmetry), Physics (gauge theory), and CS (cryptography) — the hierarchy reveals these connections.
3. **Pedagogical sequencing**: learning paths follow the hierarchy bottom-up or top-down depending on goal (theorist vs practitioner).
4. **Research frontier identification**: Gaps & Emerging Fields (§11) appear where new Subdisciplines are forming.

### 8.3 Cross-cutting "lateral" connections

Many concepts transcend single domains:

| Concept | Appears in | Connection |
|---|---|---|
| **Symmetry/Group** | Algebra, Geometry, Physics, Chemistry | Noether's theorem links symmetry to conservation |
| **Probability** | Statistics, Physics, CS, Finance, Biology | Universal language of uncertainty |
| **Linear Algebra** | Pure Math, ML, Physics, Engineering, Graphics | Ubiquitous computational backbone |
| **Topology** | Pure Math, Data Science, Physics, Neuroscience | Shape of data, phase transitions, brain networks |
| **Logic** | Foundations, CS, Math itself, Philosophy | What "proof" and "computation" mean |
| **Optimization** | OR, ML, Control, Economics, Engineering | Choosing best among alternatives |
| **Information** | Info Theory, CS, Biology, Physics | Universal currency of communication |
| **Category Theory** | Algebra, Topology, Logic, CS, Physics | Universal language of structure and composition |

---

## 9. HOW MATHEMATICS UNDERPINS CS, ENGINEERING, CRYPTO & AI

### 9.1 Mathematics → Computer Science

| Math Area | CS Application |
|---|---|
| **Logic & Proof Theory** | Formal verification, type systems, program correctness proofs |
| **Computability Theory** | What computers can/cannot compute; halting problem limits |
| **Complexity Theory** | P vs NP defines tractability; NP-completeness guides algorithm design |
| **Graph Theory** | Data structures, network algorithms, compilers (parse trees), social networks |
| **Boolean Algebra** | Digital circuits, SAT solving, hardware verification |
| **Linear Algebra** | Graphics, ML, numerical methods, PageRank, data analysis |
| **Category Theory** | Functional programming semantics, database theory, type theory |
| **Information Theory** | Data compression, communication protocols, Kolmogorov complexity |
| **Probability & Statistics** | Randomized algorithms, ML, A/B testing, anomaly detection |
| **Number Theory** | Cryptography (RSA, ECC, Diffie-Hellman, post-quantum) |
| **Algorithms & Discrete Math** | Everything in CS — algorithms ARE discrete mathematics made executable |
| **Formal Methods** | Model checking, theorem proving, verified software |

**Key insight**: CS is applied discrete mathematics + applied logic. Every algorithm is a mathematical object; every data structure is an algebraic/combinatorial structure; every correctness proof is a logical derivation.

### 9.2 Mathematics → Engineering

| Math Area | Engineering Application |
|---|---|
| **Differential Equations** | Structural mechanics, fluid dynamics, heat transfer, electromagnetics, control |
| **Linear Algebra** | Circuit analysis, structural analysis, signal processing, robotics (kinematics) |
| **Numerical Analysis** | All simulation: CFD, FEA, thermal analysis, electromagnetic simulation |
| **Optimization** | Design optimization, control systems, resource allocation, logistics |
| **Probability & Statistics** | Quality control, reliability engineering, signal processing, risk analysis |
| **Fourier/Harmonic Analysis** | Signal processing, communications, image processing, vibration analysis |
| **Differential Geometry** | Robotics (configuration spaces), general relativity (physics), computer graphics |
| **Graph Theory** | Network design, power grids, transportation systems, VLSI layout |
| **Stochastic Processes** | Queueing (telecom), reliability, maintenance scheduling, inventory |
| **Complex Analysis** | Control theory (Nyquist stability), fluid mechanics, electromagnetics |

**Key insight**: Engineering is applied mathematics constrained by physical laws. Every engineered system is a mathematical model solved (usually numerically) under constraints.

### 9.3 Mathematics → Cryptography

| Math Area | Crypto Application |
|---|---|
| **Number Theory** | RSA (factoring), Diffie-Hellman (discrete log), ECC (elliptic curves), primality testing |
| **Algebra** | Group theory (finite fields, elliptic curves), ring theory (lattices, ideals) |
| **Computational Complexity** | One-way functions, NP-hardness assumptions, zero-knowledge proofs |
| **Information Theory** | Perfect secrecy (one-time pad), entropy bounds, channel capacity for secure comms |
| **Boolean Algebra/Logic** | Circuit implementations, SAT-based cryptanalysis, formal verification of crypto |
| **Lattice Theory** | LWE/RLWE (post-quantum crypto), NTRU, GGH cryptosystems |
| **Coding Theory** | Error-correcting codes, McEliece cryptosystem (code-based crypto) |
| **Probability** | Random number generation, side-channel analysis, differential privacy |
| **Graph Theory** | Graph isomorphism-based crypto, network security protocols |
| **Algebraic Geometry** | Elliptic curve cryptography, isogeny-based crypto (SIKE — broken by Castryck-Decru 2022) |

**Key insight**: Cryptography is mathematics weaponized for security. Every cryptosystem rests on a mathematical hardness assumption; every break is a mathematical advance (or a computational breakthrough, e.g., Shor's quantum algorithm).

### 9.4 Mathematics → Artificial Intelligence

| Math Area | AI Application |
|---|---|
| **Linear Algebra** | Neural networks (matrix operations), embeddings, attention mechanisms, PCA |
| **Calculus** | Backpropagation (chain rule), gradient descent, optimization |
| **Probability & Statistics** | Bayesian inference, generative models, uncertainty quantification, RL |
| **Optimization** | Training neural networks, convex relaxations, combinatorial optimization in planning |
| **Information Theory** | Information bottleneck, mutual information objectives, entropy regularization |
| **Graph Theory** | GNNs, knowledge graphs, social network analysis, recommendation systems |
| **Logic** | Knowledge representation, neuro-symbolic AI, automated reasoning, theorem proving |
| **Topology** | Topological data analysis for ML, persistent homology features |
| **Category Theory** | Deep learning architectures (functorial formulations), compositionality |
| **Computational Complexity** | What AI can/can't compute efficiently; sample complexity bounds |
| **Dynamical Systems** | Recurrent networks, continuous-time models, chaos in neural dynamics |
| **Game Theory** | Multi-agent RL, mechanism design for AI systems, adversarial robustness |

**Key insight**: AI is applied mathematics at massive scale. Neural networks are parameterized functions trained by gradient-based optimization on probability distributions; the theory (generalization, optimization landscapes, expressivity) is actively developed mathematics.

---

## 10. CROSS-DOMAIN CONNECTIONS & PREREQUISITE LADDER

### 10.1 The prerequisite ladder (simplified)

```
Level 0: Arithmetic, basic algebra, logic basics
    ↓
Level 1: Precalculus, elementary functions, set theory basics
    ↓
Level 2: Calculus (differential & integral), linear algebra basics, discrete math basics
    ↓
Level 3: Multivariable calculus, linear algebra (advanced), probability basics, proof techniques
    ↓
Level 4: Real analysis, abstract algebra, topology basics, measure theory basics
    ↓
Level 5: Functional analysis, differential geometry, measure-theoretic probability, advanced algebra
    ↓
Level 6: Research-level specialization (algebraic geometry, stochastic processes, proof theory, etc.)
```

### 10.2 Major interconnection hubs

1. **Linear Algebra** — connects pure (modules, representations), applied (numerical methods), ML, physics, engineering.
2. **Analysis** — connects ODEs/PDEs, functional analysis, probability, geometry (geometric analysis), physics.
3. **Algebra** — connects number theory, geometry (algebraic geometry), topology (homological algebra), CS (crypto groups).
4. **Topology** — connects geometry, algebra (algebraic topology), analysis (geometric analysis), data science (TDA).
5. **Logic** — connects foundations, proof theory, CS (formal methods), mathematics itself.
6. **Probability** — connects statistics, stochastic processes, physics (stat mech), finance, ML.
7. **Optimization** — connects OR, control, ML, economics, engineering design.
8. **Category Theory** — connects algebra, topology, logic, CS (type theory), physics (topological QFT).
9. **Information Theory** — connects communications, cryptography, statistics, ML, physics.

### 10.3 The "applied ↔ pure" feedback loop

- **Number theory** (pure) → **cryptography** (applied) → **post-quantum crypto** (new pure problems in lattices).
- **Topology** (pure) → **topological data analysis** (applied) → **new invariants** (pure).
- **Category theory** (pure) → **applied category theory** in CS/database → **new categorical structures** (pure).
- **Statistical mechanics** (applied physics) → **probability theory** (pure) → **concentration inequalities** → **ML theory** (applied).
- **Fourier analysis** (pure) → **signal processing** (applied) → **uncertainty principle refinements** (pure).

---

## 11. GAPS & EMERGING FIELDS

*This map is intentionally NOT exhaustive. The following areas are rapidly developing, underrepresented in classical classifications, or sit at disciplinary boundaries.*

### 11.1 Homotopy Type Theory (HoTT) & Univalent Foundations
- **What**: Type theory where equality is modeled as paths/homotopies; univalence axiom makes equivalent types equal.
- **Status**: Active research program (Voevodsky, 2006–2017); Lean's mathlib uses related ideas.
- **Connections**: §2.8 category theory, §7.4 type theory, topology (synthetic homotopy theory).
- **Gap**: Not yet mainstream in mathematics education; practical adoption limited.

### 11.2 Tropical Geometry & Idempotent Mathematics
- **What**: Algebraic geometry over the tropical semiring (min-plus algebra); degenerations of algebraic varieties.
- **Status**: Active research (2000s–present); connections to mirror symmetry, enumerative geometry.
- **Connections**: §2.3 algebraic geometry, §3.5 mathematical physics, optimization (tropical = piecewise-linear optimization).
- **Gap**: Still largely pure; applied uses emerging.

### 11.3 Applied Category Theory
- **What**: Using category-theoretic methods (monoidal categories, operads, sheaves) in CS, data science, systems engineering.
- **Status**: Growing community; used in database theory, machine learning architectures, systems modeling.
- **Connections**: §2.8 category theory, §7.4 type theory, §4.4 algorithms.
- **Gap**: Often criticized as "abstract nonsense" by practitioners; empirical benefits still being demonstrated.

### 11.4 AI-Assisted Mathematical Discovery & Proof
- **What**: Machine learning for conjecture generation, proof search, theorem proving; neural theorem provers; autoformalization.
- **Status**: Rapidly growing (2020s); notable results: Ramanujan machine, TxGraffiti conjectures, DeepMind's AlphaGeometry, GPT-based math.
- **Connections**: §7.5 formal methods, §6.6 ML, all of pure mathematics.
- **Gap**: Whether AI will produce genuinely novel mathematics vs. repackaging known results is open.

### 11.5 Topological Data Analysis (TDA) & Applied Topology
- **What**: Using topological invariants (persistent homology) to analyze data shape.
- **Status**: Active applied field (2000s–present); used in genomics, materials science, neuroscience.
- **Connections**: §2.4 topology, §6.6 ML, §5 statistics.
- **Gap**: Interpretation of topological features can be subtle; computational scalability.

### 11.6 Quantum Mathematics & Quantum Information
- **What**: Mathematics of quantum computing, quantum error correction, quantum information theory.
- **Status**: Rapidly growing; post-quantum cryptography depends on it.
- **Connections**: §2.5 functional analysis, §5.3 stochastic processes, §6.1 information theory, §2.2 number theory (lattices).
- **Gap**: Many foundational questions about quantum computation's power remain open (BQP vs NP, etc.).

### 11.7 Machine Learning Theory & Neural Network Mathematics
- **What**: Rigorous theory of deep learning: optimization landscapes, generalization bounds, expressivity, implicit bias.
- **Status**: Very active (2010s–present); "deep learning theory" is now a recognized field.
- **Connections**: §6.6 ML, §3.3 optimization, §5.2 statistics, §2.5 analysis.
- **Gap**: Theory lags practice; many empirical phenomena (double descent, grokking) lack complete explanation.

### 11.8 Experimental Mathematics & Computer-Assisted Proof
- **What**: Using computation to discover conjectures, verify proofs (four color theorem), and explore mathematical objects.
- **Status**: Established but growing; SageMath, Mathematica, Lean enable new workflows.
- **Connections**: §3.4 computational math, §7.5 formal methods, all of pure math.
- **Gap**: Acceptance of computer proofs varies by community; reproducibility concerns.

### 11.9 Mathematical Biology & Epidemiological Modeling
- **What**: Mathematical models of biological systems: population dynamics, epidemiology, neuroscience, ecology.
- **Status**: Mature but expanding; COVID-19 highlighted importance.
- **Connections**: §3.1 modeling, §5 probability/statistics, §2.6 differential equations, §6.3 dynamical systems.
- **Gap**: Multi-scale integration (molecular → organism → population) remains challenging.

### 11.10 Econophysics & Complex Systems Mathematics
- **What**: Applying statistical physics methods to economics, finance, social systems; emergence, phase transitions, power laws.
- **Status**: Interdisciplinary; some results controversial.
- **Connections**: §3.5 math physics, §5 probability, §6.2 game theory, §4 graph theory.
- **Gap**: Rigorous foundations often weaker than in physics; predictive power debated.

### 11.11 Other Notable Gaps
- **Fuzzy/rough set theory** — alternatives to classical logic for vagueness; niche but used in AI.
- **Fractal geometry & chaos theory** — geometric structures of fractional dimension; active in physics/biology.
- **Numerical algebraic geometry** — solving polynomial systems numerically; growing field.
- **Formal epistemology of mathematics** — how we know mathematical truths; philosophy-math interface.
- **Mathematical psychology & neuroeconomics** — mathematical models of cognition and decision-making.
- **Proof theory for AI safety** — using formal methods to verify AI systems; emerging critical area.
- **Mathematics of deep learning** — specific subfield covering transformers, diffusion models, RL theory.
- **Synthetic differential geometry** — infinitesimal reasoning without limits; niche but elegant.
- **Noncommutative geometry** — geometry of noncommutative algebras; Connes' program connecting to physics.
- **Higher category theory in physics** — topological field theories, factorization algebras.

---

## 12. SOURCES

*Compiled from standard mathematical references and verified via web search Nov 25, 2026.*

### 12.1 Classification & Structure
- **NSF Division of Mathematical Sciences** — "The Mathematical Sciences: Their Structure and Contributions" — nine subfields classification (foundations, algebra/combinatorics, number theory/algebraic geometry, topology/geometry, analysis, probability, applied math, computational math, statistics).
- **Trinity College Dublin — School of Mathematics** — "Types of Mathematics" — applied vs pure vs theoretical physics framing; application ↔ theory cycle.
- **MSC2020 (Mathematics Subject Classification)** — zbMATH/Open — official subject classification scheme used for research indexing.
- **Wikipedia — Mathematics** — general overview, epistemology, major areas.

### 12.2 Pure Mathematics
- **Wikipedia — Abstract Algebra, Number Theory, Geometry, Topology, Mathematical Analysis, Set Theory, Category Theory** — standard reference for subfields and key results.
- **Stanford Encyclopedia of Philosophy** — entries on set theory, philosophy of mathematics, logic.
- **nLab** — category theory and higher category theory reference.
- **nCatLab** — applied category theory resources.

### 12.3 Applied Mathematics & Computation
- **SIAM (Society for Industrial and Applied Mathematics)** — journals and classification for applied math.
- **Trinity College Dublin** — mathematical modeling methodology.
- **Numerical Recipes** — standard reference for numerical methods.
- **Wikipedia — Numerical Analysis, Optimization, Operations Research** — method classifications.

### 12.4 Probability & Statistics
- **Wikipedia — Probability Theory, Statistics, Stochastic Processes, Information Theory** — standard references.
- **MIT OpenCourseWare** — probability, statistics, stochastic processes course materials.
- **Casella & Berger, Statistical Inference** — standard graduate textbook.
- **Durrett, Probability: Theory and Examples** — standard probability textbook.

### 12.5 Information, Decision & Computational Sciences
- **Cover & Thomas, Elements of Information Theory** — canonical information theory text.
- **Myerson, Game Theory** — canonical game theory text.
- **Sutton & Barto, Reinforcement Learning** — RL foundations.
- **Arora & Barak, Computational Complexity** — standard complexity text.
- **Papadimitriou, Computational Complexity** — classic text.

### 12.6 Formal Sciences & Logic
- **Stanford Encyclopedia of Philosophy** — entries on logic, computability, Gödel's theorems.
- **Enderton, A Mathematical Introduction to Logic** — standard logic textbook.
- **Sipser, Introduction to the Theory of Computation** — standard computability/complexity text.
- **Homotopy Type Theory book** (HoTT Book, 2013) — univalent foundations.
- **Lean 4 / mathlib documentation** — current state of formalized mathematics.

### 12.7 Emerging Fields (verified via web search)
- **AMS Notices** — "Mathematics: the Rise of the Machines" (arXiv:2511.17203) — AI for mathematical discovery survey.
- **arXiv:2601.13209** — "AI for Mathematics: Progress, Challenges, and Prospects" — AI4Math review.
- **arXiv:2510.15795** — "Synthetic perspectives on spaces and categories" — HoTT and simplicial type theory.
- **arXiv:2511.17203** — AI for mathematical discovery: Ramanujan machine, TxGraffiti, AlphaGeometry.
- **MIT Vantage lecture notes** — Drew Armstrong on AI-assisted theorem proving.

### 12.8 Cross-Domain Applications
- **Shor's algorithm (1994)** — quantum factoring; motivates post-quantum crypto.
- **Castryck–Decru attack (2022)** — broke SIKE isogeny crypto; example of math breaking crypto.
- **Four color theorem (1976)** — first major computer-assisted proof.
- **Perelman (2003)** — Ricci flow proof of Poincaré conjecture; example of geometric analysis solving topology.
- **Wiles (1994)** — Fermat's Last Theorem via modular forms; number theory landmark.

---

*End of map. This document covers the major branches of mathematics, logic, and formal sciences as of November 2026. It is not exhaustive — see §11 for emerging areas and acknowledged gaps. For deeper exploration, follow the knowledge hierarchy (§8) within each field.*

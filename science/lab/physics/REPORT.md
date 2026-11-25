# Physics Simulation Lab — CREATE-AND-DESTROY Report
*Agent run: build model → run → perturb/break assumptions. All sims: numpy/scipy/matplotlib, venv python.*

Workdir: `/home/neilh/science_lab/physics/` — scripts `*.py`, data `data/*.csv`, plots `plots/*.png`.

---

## 1. Orbital mechanics (`orbit.py`)
- **Hypothesis:** 2-body gravity obeys Kepler's 3rd law; RK4 conserves energy; drag causes inspiral.
- **Method:** RK4 integrator, μ=1 units; circular orbits a ∈ {0.5…8}; period measured by upward y-crossings; 100-orbit energy track; quadratic drag run.
- **Data:** `data/orbit_kepler.csv`, `orbit_energy.csv`, `orbit_drag_r.csv`.
- **Results:** T²/(4π²a³) = 0.9998 ± 0.0006 (theory 1.0). Relative energy drift over 100 orbits: **6.5e-13**. Under drag=0.02 radius decays monotonically.
- **Plots:** `orbit_traj.png`, `orbit_energy.png`, `orbit_drag.png`, `orbit_drag_r.png`.
- **BREAK:** added velocity-squared drag → clean decay spiral (no closed orbit, r → 0).
- **Lesson:** symplectic-ish behavior of RK4 at small dt; non-conservative forces monotonically drain energy — the integrator doesn't fight physics.

## 2. Double slit (`doubleslit.py`)
- **Hypothesis:** I(θ) ∝ cos²(πdy/λL); which-way measurement destroys fringes.
- **Method:** analytic intensity on screen y∈[−20,20] mm, λ=500 nm, L=1 m, d=0.1 mm; single-slit envelope; decoherence as mixture I=(1−p)I_coh+pI_inc.
- **Results:** measured fringe spacing **0.00499 m** vs theory Δy=λL/d=**0.00500 m**. Visibility V=(Imax−Imin)/(Imax+Imin) falls **linearly 1.0→0.0** as which-way weight p goes 0→1.
- **Plots:** `doubleslit_fringes.png`, `doubleslit_decoherence.png`.
- **BREAK:** incoherent (which-way) sum = flat intensity — fringes gone, exactly as complementarity demands.
- **Lesson:** interference is an amplitude phenomenon; any which-way information (even partial) linearly suppresses contrast.

## 3. Ideal gas (`gas.py`)
- **Hypothesis:** elastic hard-disk gas satisfies PV=NkT and equipartition; removing collisions kills thermalization.
- **Method:** N=300 disks (σ=0.02) in 1×1 box, kB=m=1 units; sequential pairwise elastic collisions + specular walls; P measured **directly** as wall momentum flux (2m|vx| per hit / wall length·time); T from ⟨v²⟩.
- **Bugs fought:** fancy-index `+=` with duplicate particle indices silently dropped collision impulses → runaway heating (T→10⁷); wrong approaching-pair sign (p<0 vs p>0); simultaneous-impulse resolution lost ~33% KE → switched to sequential pair resolution → **KE conserved to machine precision**.
- **Results:** T held exactly at target (50→800 K). P vs T perfectly linear: slope 353 vs ideal-gas Nk/A=300 (**~18% high**, consistent with excluded-volume/virial correction for σ=0.02 disks, packing fraction ≈0.09). Equipartition ⟨½mv_x²⟩/(kT/2) = **0.994**.
- **Plots:** `gas_pv.png`, `gas_freeexpansion.png`.
- **BREAK:** collisions disabled + imposed x-velocity shear → vx/vy anisotropy 3.28 persists forever; no thermalization, just ballistic bouncing.
- **Lesson:** molecular chaos requires collisions; wall reflections alone conserve every particle's speed forever.

## 4. Wave equation (`wave.py`)
- **Hypothesis:** 1D string obeys superposition; leapfrog stable iff CFL c·dt/dx ≤ 1.
- **Method:** u_tt=c²u_xx, fixed ends, leapfrog; Gaussian pulse & two-pulse & sin(πx) mode cases.
- **Results:** two pulses pass through each other unchanged (max|u|=2.08 bounded). **CFL=1.5 → max|u| grows to 2×10¹¹** within t=0.5 — textbook numerical instability.
- **Plots:** `wave_superposition.png`, `wave_mode.png`, `wave_cfl_blowup.png`.
- **BREAK:** violated CFL → exponential blow-up, captured on symlog plot.
- **Lesson:** explicit schemes have a hard stability boundary; linearity (superposition) survives only inside it.

## 5. Schrödinger FD (`schrodinger.py`)
- **Hypothesis:** FD Hamiltonian reproduces analytic eigenvalues; tunneling T decays exponentially with barrier width.
- **Method:** sparse 3-point Laplacian, Dirichlet box L=10, Nx=400; `eigsh` lowest 6; finite well (V=−5, w=4) vs pole-free transcendental root solve; rectangular-barrier T exact formula vs WKB.
- **Results:** infinite box: n=0 eigenvalue rel err **5.1e-6**. Finite well: FD {−4.768,−4.079,−2.957,−1.467} vs analytic {−4.771,−4.088,−2.977,−1.500} (~0.5% FD error). Tunneling E=3,V0=10: T(w=1)=1.9e-3 → T(w=4)=3.4e-13 — log-linear decay matching WKB exp(−2κw).
- **Plots:** `schrod_box.png`, `schrod_tunneling.png`.
- **BREAK:** (analytic side) tan-pole root finder produced garbage → rewrote equations in pole-free ξ,η form; FD side is the robust reference.
- **Lesson:** FD is trustworthy to O(dx²); tunneling is exponential, so modest width changes → orders-of-magnitude T changes.

## 6. Double pendulum chaos (`pendulum.py`)
- **Hypothesis:** energy conserved; nearby ICs diverge exponentially (positive Lyapunov).
- **Method:** EOM derived **symbolically with sympy** from the Lagrangian (hand-coded formula blew up — wrong signs); RK4 dt=2e-3, T=80 s; two ICs differing by 1e-9 rad.
- **Results:** E/E0 drift 2.4e-4 over 80 s. Separation grows 2e-12 → ~18 rad (saturated); log-slope gives rough λ ≈ **0.8 /time** — exponential until angles decorrelate.
- **Plots:** `pendulum_energy.png`, `pendulum_lyapunov.png`; data `pendulum_sep.csv`.
- **BREAK:** chaos itself is the "break" — determinism + sensitive dependence; also demonstrated that a wrong analytic EOM gives nan in seconds.
- **Lesson:** trust sympy over memory for messy EOM; chaos = finite-precision inevitability.

## 7. 2D Ising (`ising.py`)
- **Hypothesis:** ferromagnetic order below Tc≈2.269 (J=kB=1); susceptibility peaks at Tc.
- **Method:** Metropolis with checkerboard vectorized updates (independent sublattices), L=32, 1500 therm + 3000 meas sweeps per T.
- **Results:** |m|≈0.98 at T=1.5, collapses through T≈2.25–2.38; Var(m) peaks at **T=2.25** vs exact 2.269 — finite-size shift expected (peak moves toward Tc from below as L→∞; L=32 undershoots slightly and transition is rounded).
- **Plots:** `ising_m.png`, `ising_chi.png`; data `ising.csv`.
- **BREAK:** n/a — but finite size IS the perturbation: no true singularity, just a rounded peak shifted from 2.269.
- **Lesson:** Monte Carlo nails Tc to ~1% even at modest L; fluctuations (Var m) locate Tc better than ⟨m⟩.

---

## Headline numbers
| Exp | Key result |
|---|---|
| Orbit | Kepler ratio 0.9998±0.0006; ΔE/E=6.5e-13/100 orbits |
| Double slit | Δy meas 4.99 mm vs 5.00 mm theory; V: 1→0 linear in decoherence |
| Gas | P∝T slope 353 vs 300 ideal (+18% virial); equipartition 0.994 |
| Wave | CFL=1.5 → \|u\|~10¹¹ blow-up |
| Schröd. | box eig err 5e-6; T tunnel 1.9e-3→3.4e-13 for w 1→4 |
| Pendulum | λ≈0.8/time; ΔE/E=2.4e-4/80 s |
| Ising | Tc estimate 2.25 vs 2.269 exact |

## Issues encountered
- WSL connection timed out twice mid-run; fixed runs re-executed, outputs verified by file timestamps/content.
- `gas.py` needed three bug fixes (fancy-index lost updates, approaching-sign error, simultaneous-collision energy loss → sequential resolver). Final version conserves KE exactly.
- `pendulum.py` hand-derived EOM unstable → replaced with sympy-derived equations.
- `ising.py` variance double-subtraction bug → fixed, rerun clean.
- NEED.md: nothing needed — numpy/scipy/matplotlib/sympy all present in venv.

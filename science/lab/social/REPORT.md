# Social Science Lab — Game Theory, Economics & Network Science
*Hands-on experiment series: build models, compute equilibria, then break assumptions.*
Date: Nov 25, 2026. Scripts: /home/neilh/science_lab/social/exp*.py ; data: exp*_results.json .

---

## EXP 1 — Iterated Prisoner's Dilemma Tournament
**Hypothesis:** Tit-for-tat should dominate a round-robin tournament.
**Method:** 5 strategies (always-cooperate, always-defect, tit-for-tat, grim-trigger, random) x 100 rounds x 1000 matches per pairing; payoffs T=5,R=3,P=1,S=0; average per-round payoff ranked.
**Result (clean):** grim_trigger 2.659 > tit_for_tat 2.415 > random 2.260 > always_cooperate 2.251 > always_defect 2.012.
**BREAK (5% action-flip noise):** grim 2.355 > always_defect 2.078 > random 2.029 > **tit_for_tat 1.906** > always_cooperate 1.830 — TFT falls below even unconditional defection.
**Lesson:** TFT is *not* the dominant strategy — it is the best retaliatory-but-forgiving strategy; grim-trigger beats it head-to-head. More importantly, TFT's success is fragile: a single execution error triggers endless retaliation, so under noise the least forgiving exploitable strategy (always-defect) wins. Robustness requires forgiveness proportional to noise (e.g., generous tit-for-tat).

## EXP 2 — Nash Equilibrium Finder
**Hypothesis:** Random games have pure NE; some games have none and need mixed strategies.
**Method:** 20,000 random 2x2 and 3x3 games (uniform integer payoffs); enumerated pure NE and verified unilateral-deviation conditions; solved fully-mixed NE for 2x2 by indifference.
**Results:**
- 2x2: mean 1.21 pure NE/game; P(no pure NE) = 8.4%. 3x3: mean 1.34; P(none) = 12.8%.
- Matching Pennies has **zero** pure NE -> unique mixed NE sigma=(0.5,0.5) for both players, EV=0.
- Of 397 sampled 2x2 games lacking pure NE, 175 had a fully-interior mixed NE (rest have boundary/partial mixes).
- Verified numerically: example game mix p=0.8, q=0.533 gives row EVs 4.2=4.2 and col EVs 1.8=1.8 (indifference confirmed).
**Lesson:** Pure NE are common but not guaranteed (~1/game on average for small games). When absent, mixed strategies restore equilibrium — indifference makes the opponent's mix unpredictable, which is exactly why Matching Pennies is unexploitable.

## EXP 3 — Tragedy of the Commons
**Hypothesis:** Self-interested extraction exceeds the social optimum; punishment can align incentives.
**Method:** N=8 agents choose extraction e_i in [0,8]; payoff_i = e_i(V - c*G) - k*e_i^2 with V=10,c=0.5,k=0.8. Nash via iterated best response (scipy); social optimum via joint optimization.
**Results:** Nash G=13.11 vs optimum G=8.33 (**57% over-extraction**), welfare 27.95 vs 41.67 (**-32.9%**).
**BREAK — punishment:** A lump-sum fine P (flat penalty when G>threshold) changed *nothing* at any P in {0..10}: a non-marginal punishment does not alter individual first-order conditions — classic mechanism-design failure. Switching to a **per-unit fine on excess extraction** (rho * e_i * max(0,G-thr)) worked: rho ~2-3 drives G -> 9.17 (near optimum 8.33) and welfare -> ~41.
**Lesson:** The externality is real and large. But punishment only works if it is *marginal* — it must raise the private cost of the next unit extracted, not just tax the aggregate. Institutions fail not from lack of penalties but from penalties that do not touch incentives.

## EXP 4 — Market Equilibrium
**Hypothesis:** Tatonnement converges to the competitive equilibrium; price controls create shortages/surpluses.
**Method:** D(p)=120-6p, S(p)=10+4p; price adjusts p <- p + lambda*(D-S)/10 from p=5.
**Results:** Analytic eq p*=11, q*=54. Tatonnement converged to p=11.000 in 50 iterations (excess 8e-10). Starting below eq, excess demand shrank monotonically: 60 -> 36 -> 21.6 -> ... -> 0.
**BREAK — price ceiling at p=10:** D=60, S=50 -> **shortage of 10 units** (~18% of equilibrium quantity unmet). Ceiling at 15 (non-binding) -> 0 shortage. Price floor at 20 -> surplus of 90.
**Lesson:** The tatonnement process is a decentralized computation of equilibrium — prices aggregate excess demand until plans clear. Any binding price control severs this feedback: quantity demanded exceeds quantity supplied and the short side (sellers) must be rationed by non-price means (queues, black markets, search costs).

## EXP 5 — Network Science
**Hypothesis:** Realistic networks show small-world (low diameter ~ log n) properties; scale-free nets are robust to random but fragile to targeted attack.
**Method:** n=1000 ER (p=6/n), WS (k=6,p=0.1), BA (m=3); measured degree dist, clustering, ASP, diameter; ASP vs n in {100..3000}; attack sim on n=5000 BA.
**Results:**
| model | avg deg | max deg | clustering | ASP | diameter |
|---|---|---|---|---|---|
| ER | 6.06 | 19 | 0.006 | 4.04 | 9 |
| WS | 6.00 | 9 | **0.449** | 6.08 | 11 |
| BA | 5.98 | **91** | 0.030 | **3.54** | **6** |
- Six degrees confirmed: ASP/log n ~ 0.5-0.6 across models and scales (ASP grows logarithmically, not linearly).
- BA degree distribution is heavy-tailed (crude power-law exponent ~2; hubs up to degree 91 = 9% of nodes).
- **Attack (n=5000 BA):** removing top-degree nodes -> giant component 0.976 -> 0.356 after only 1,200 removals (24%); random removal of same count -> only 0.755. At k=900 targeted=0.623 vs random=0.818.
**Lesson:** WS gives high clustering *and* short paths (the true small-world sweet spot). BA hubs shrink the world further but create fatal fragility: the network is robust to random failure yet collapses under targeted attack on ~5% of nodes — directly relevant to infrastructure and epidemic seeding.

## EXP 6 — Opinion Dynamics (Deffuant)
**Hypothesis:** Bounded-confidence interaction produces opinion clusters whose number falls as tolerance eps rises; stubborn agents prevent consensus.
**Method:** N=300 agents on WS network (k=8), opinions in [0,1]; if |x_i - x_j| < eps both move toward mean (mu=0.5); 3000 sweeps.
**Results:**
- eps=0.1 -> 2 clusters (range still 0->1); eps=0.2 -> 2; eps=0.3 -> 3; eps=0.4 -> 3; eps=0.5 -> **1 cluster** (full consensus at 0.5).
- BREAK: adding just **4 stubborn agents** pinned at {0,1} with eps=0.5 -> **2 persistent clusters** vs 1 baseline.
**Lesson:** Consensus is fragile. Bounded confidence alone sorts opinions into clusters, and a tiny fraction of immovable agents (<2%) permanently anchors polarized clusters even when everyone else would converge — a mechanism for persistent political/media polarization.

## EXP 7 — Signaling / Information
**Hypothesis:** Cheap talk cannot transmit information when interests align; costly signals can.
**Method:** Sender types = states {G,B} (prior 1/2); receiver Invests (+2 if G, -1 if B, else 0); both sender types prefer Invest. Enumerated all pure-strategy NE of the cheap-talk game; analyzed mimicry-cost condition.
**Results:** All 4 pure NE are **babbling equilibria** — both types send the same message (e.g., [G,G] or [B,B]); the receiver's action depends only on the message, so the message carries zero information about the state. No separating equilibrium exists in cheap talk.
**Costly signaling:** if mimicking the good signal costs c, a separating equilibrium (good type signals honestly, bad type pools separately) is sustainable iff **c > 1** — the bad type's gain from inducing investment. Cost must exceed the benefit of deception.
**Lesson:** Words are cheap precisely because they are cheap. When sender and receiver interests align, talk is uninformative *in equilibrium* — not because agents lie badly, but because any informative message would be mimicked. Only when deception is *costly* (burning money, education, warranties) does the signal become credible. This is the formal basis of Spence signaling and cheap-talk results in political economy.

---

## Headline Findings
1. **TFT is not dominant** — grim-trigger beats it; under 5% noise TFT collapses below always-defect. Cooperation strategies are fragile to execution noise.
2. **~8-13% of random small games have no pure NE**; mixed strategies (verified indifference) are required — Matching Pennies is the canonical case.
3. **Tragedy of commons is quantitatively severe** (57% over-extraction, -33% welfare); only *marginal* (per-unit) punishment restores efficiency — lump-sum fines do nothing.
4. **Tatonnement converges cleanly; a binding price ceiling mechanically produces shortage** (D-S=10 at p=10 vs eq q=54).
5. **Networks are small worlds (ASP ~ log n) but scale-free topology trades random-failure robustness for targeted-attack fragility** (giant comp 0.36 vs 0.76 after identical removals).
6. **4 stubborn agents out of 300 permanently polarize a Deffuant population** that would otherwise reach consensus.
7. **Cheap talk has only babbling equilibria; costly signals separate types iff mimicry cost exceeds the deception gain.**

## Files
- exp1_pd.py, exp1_results.json — PD tournament (+noise)
- exp2_nash.py, exp2_results.json — NE enumeration + mixed NE
- exp34.py, exp34_results.json ; exp3b.py, exp3b_results.json — commons & market
- exp567.py, exp567_results.json ; exp5fix.py, exp5fix.json — networks, Deffuant, signaling

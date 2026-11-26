# AUTONOMOUS PURCHASING INTELLIGENCE ENGINE — Architecture
Version 1.0 | 2026-11-26 | Fleet: WSL /home/neilh/autonomous_purchasing

## Vision
AI that identifies its own capability needs, discovers resources,
evaluates value, purchases within hard financial guardrails,
measures whether each purchase improved capability, and compounds.

## Design principles
1. LEDGER FIRST — every monetary movement is double-entry,
   auditable, immutable. No purchase without a ledger entry.
2. CAGE BEFORE WINGS — spending authority is granted in layers:
   simulation → API-only → capped virtual card → agentic protocols.
3. MEASURE OR IT DIDN'T HAPPEN — every purchase links to a
   capability metric; ROI is computed, not assumed.
4. HUMAN KILL-SWITCH — any spend above threshold requires
   explicit approval token. Default-deny for new vendors.

## Modules

### core/ledger.py — double-entry accounting (SQLite)
Tables: accounts, transactions, entries, budgets, approvals.
- accounts: cash, escrow, per-vendor spend buckets
- transactions: id, ts, vendor, amount, purpose, capability_tag
- entries: debit/credit pairs (balance must equal zero per txn)
- budgets: per-category caps, per-vendor caps, daily caps
- approvals: pending spends above threshold

### core/needs.py — need detection
Input: objective spec (JSON: capabilities + target metrics).
Compares current capability profile vs objective → emits NEED records
{need_id, capability, gap_score, urgency, budget_hint}.
Capability profile lives in data/capabilities.json and is updated
by post-purchase measurements.

### core/discovery.py — resource discovery
Pluggable sources:
- vendors/catalog.json (curated vendor DB)
- web search adapter (stub → real API later)
- price feeds
Output: OFFER records {offer_id, vendor, item, price, specs,
capability_delta_estimate, risk_score}.

### core/evaluate.py — economic decision intelligence
Score = w1*capability_gain + w2*price_efficiency
      - w3*risk - w4*lock_in - w5*recurring_cost
Multi-offer comparison per need. Outputs RANKED list +
DECISION {need_id, chosen_offer, runner_up, reasoning}.

### core/negotiation.py — negotiation intelligence
Phase 3 stub. Vendors rarely negotiate; supports:
- volume discount requests (API vendors)
- AP2/ACP agentic protocols when they mature
- bundle detection (buy X get Y cheaper)

### core/pay.py — payment execution
PaymentProvider interface:
  authorize(spend) -> hold
  capture(txn) -> settle
  refund(txn)
Implementations:
- SimulatedProvider (Phase 1 — virtual ledger only)
- ApiKeyProvider (Phase 2 — AWS/Vercel/etc, real spend, hard caps)
- CardProvider (Phase 3 — virtual card, allowlist, thresholds)

### core/subscriptions.py — subscription management
Tracks recurring charges, renewal calendar,
auto-cancel rules (unused N days → cancel),
subscription ROI vs usage metrics.

### core/portfolio.py — inventory & asset management
What the AI owns: API keys, accounts, licenses, datasets,
hardware reservations. Each asset: cost basis, capability
contribution, depreciation, renewal date.

### core/risk.py — fraud & risk intelligence
- vendor reputation scoring
- price anomaly detection (spend >2x category avg → flag)
- new-vendor quarantine (first purchase = approval required)
- velocity limits (max N purchases/day)

### core/alloc.py — resource allocation intelligence
Budget optimizer: distributes budget across needs by
marginal ROI. Portfolio rebalancing: kill underperforming
assets, double down on high-ROI capabilities.

### core/improve.py — self-improvement investment
Tracks capability_before/after per purchase.
Computes realized ROI = (capability_gain * value_per_capability)
                        / total_cost.
Feeds back into evaluation weights (online learning lite).

### orchestrator.py — the brain
Loop: scan needs → discover → evaluate → risk-check →
approval-gate → pay → verify → measure → ledger → repeat.
CLI: python orchestrator.py run "objective spec"
     python orchestrator.py status
     python orchestrator.py ledger
     python orchestrator.py approve <txn_id>

## Data files
- data/capabilities.json — current capability profile
- data/objectives.json — active objectives
- data/vendors/catalog.json — vendor/offers database
- data/purchases.db — SQLite ledger
- data/portfolio.json — owned assets

## Phased rollout
PHASE 1 (now): full simulation — fake money, real logic.
  Proves: need detection, scoring, guardrails, ROI loop.
PHASE 2: API-key purchasing — AWS free-tier, Vercel hobby,
  domain APIs. Real spend under $50 total, hard caps.
PHASE 3: virtual card (Privacy.com/Wise) — merchant allowlist,
  $5/day cap, $25 approval threshold.
PHASE 4: agentic protocols (AP2/ACP) as they mature.

## Kill criteria / safety
- Ledger imbalance → halt all spending
- Budget breach attempt → reject + alert
- Vendor risk score > threshold → quarantine
- Human can freeze engine: touch data/FROZEN

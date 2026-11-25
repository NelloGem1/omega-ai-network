# ⬡ GLOBAL HUMAN KNOWLEDGE AND EXPERIENCE ARCHIVE
## Design Specification — knowledge_archive.md
*Version 1.0 · Synthesizes the parallel classification maps (`math_logic_map.md`, `ml_pipeline_guide.md`, et al.) into one unified architecture.*

> **Mission statement.** This is not a Wikipedia clone and not a vector store.
> It is the **institutional memory of human civilization**: a permanently maintained,
> verifiably sourced, cross-disciplinary record of *everything humanity has
> discovered, proved, designed, built, tried, and failed* — designed so that the
> next person (or next civilization) does not repeat the mistakes of the last.

---

## 0. DESIGN PHILOSOPHY — why this must exist

### 0.1 The problem today

Human knowledge is currently scattered, decaying, locked, and unreliable:

| Failure mode | Real example | Cost |
|---|---|---|
| Knowledge trapped in heads / proprietary systems | Proprietary trade secrets, unpublished lab notebooks | Re-derivation of known results; duplicated research |
| Knowledge lost to media decay | War losses, burned libraries (Alexandria, House of Wisdom), endangered oral traditions | Entire fields have to be rediscovered |
| Knowledge frozen in languages few read | Science in inaccessible journals, patents in dead formats | Global south excluded from frontier knowledge |
| Knowledge fragmented across silos | Physics on arXiv, medicine on PubMed, history in archives — no cross-links | Disciplinary blind spots; slow cross-pollination |
| Failed knowledge deleted | Negative results unpublished, failed experiments forgotten | **Science itself repeats mistakes** — the single biggest waste |
| Knowledge with no provenance | Wikipedia citations rot, AI hallucinations fabricate sources | Trust collapse |

### 0.2 What "experience" means here

An archive of *discoveries* without *experiences* is a museum of answers.
The archive must preserve the **process**: the context, the assumptions that
turned out wrong, the resources that failed, the errors that cost lives,
the partial successes, the lessons distilled. The **failed experiment is
first-class knowledge** — arguably the most valuable knowledge, because it
is the knowledge that prevents the next failure.

A surgeon who knows *why* the Thalidomide disaster happened will not repeat
it. A chemist who knows *which* esterifications polymerized catastrophically
will avoid them. The archive is a **negative-knowledge engine** as much as
a positive-knowledge engine.

### 0.3 Design principles (the PRIME ladder — foundations first)

```
1 · 3 · 7 · 9
```

- **1 · Provenance first.** Every claim carries its source chain. No orphan
  knowledge enters the canonical layer.
- **3 · Three pillars.** Knowledge content + Knowledge graph + Experience
  records. All three required; the graph alone is a diagram, the text alone
  is a pile, the experience alone is a diary.
- **7 · Seven verification tiers** (Section 3). Every node labeled.
- **9 · Nine imperatives:** completeness · verifiability · multilingual ·
  offline-capable · open · uncapturable · auditable · evolving · free.

---

## 1. CORE MISSION

### 1.1 Preserve (the seven knowledge classes)

| # | Class | Examples | Why preserved |
|---|---|---|---|
| 1 | **Discoveries** | laws of physics, new species, historical finds | The frontier of the known |
| 2 | **Mathematics** | proofs, theorems, algorithms, formal systems | The language of reasoning itself |
| 3 | **Experiences** | lived histories, oral traditions, field notes | Context that papers strip out |
| 4 | **History** | events, causality chains, failed states | Pattern memory of societies |
| 5 | **Inventions** | patents, designs, prototypes, trade secrets (with consent) | Applied capability |
| 6 | **Experiments** | methods, results, *and failures*, negative results | The scientific method's full record |
| 7 | **Solutions** | engineering fixes, medical protocols, legal precedents | Reusable resolution patterns |

Plus, continuously: **culture** (art, religion, language, myth), **lessons**
(distilled warnings), **designs** (architecture, UI, systems).

### 1.2 The Anti-Repeat-Mistake guarantee

The archive must answer, for any domain, the question: *"What has been tried
before, and how did it fail?"* This requires:

1. **Failure records are mandatory** for experiment-type nodes (Section 5).
2. **Failure nodes are cross-linked** to the methods they invalidate — a
   graph edge `INVALIDATES(method → prior_result)`.
3. **Lessons are first-class nodes** linked to every failure they distill.
4. **Retrieval must surface failures** alongside successes — a search for
   "fusion reactor design" returns the failed tokamaks with their failure
   modes *before* the proposed design (Section 4.6).

### 1.3 Non-goals

- Not a replacement for the live literature — an *index and memory layer* over it.
- Not an opinion platform — claims require evidence (Section 3).
- Not a single centralized corporate product — governance is federated (Section 7).

---

## 2. KNOWLEDGE HIERARCHY & CLASSIFICATION FRAMEWORK

### 2.1 The canonical spine

```
DOMAIN → DISCIPLINE → SUBDISCIPLINE → FIELD → CONCEPT → PRINCIPLE →
METHOD → EXPERIMENT → EVIDENCE → APPLICATION → OUTCOME
```

This is a **containment + derivation** hierarchy, not just a taxonomy.
Each level has a defined semantics:

| Level | Definition | Example (energy domain) |
|---|---|---|
| **Domain** | Top-level human-knowledge area | `Domain: Natural Sciences` |
| **Discipline** | Recognized academic/professional field | `Discipline: Physics` |
| **Subdiscipline** | Major branch | `Subdiscipline: Plasma Physics` |
| **Field** | Specific research/practice area | `Field: Magnetic Confinement Fusion` |
| **Concept** | Atomic idea/entity | `Concept: Tokamak` |
| **Principle** | Generalized law/pattern | `Principle: Lawson Criterion` |
| **Method** | Reproducible procedure | `Method: Neutral Beam Injection` |
| **Experiment** | A specific attempt with context | `Experiment: JET D-T campaign 1997` |
| **Evidence** | Observation/datum supporting a claim | `Evidence: JET achieved 16 MW fusion power` |
| **Application** | Deployed use | `Application: ITER design basis` |
| **Outcome** | Measured result / status | `Outcome: Q=0.67 achieved; gain not yet >1` |

### 2.2 Cross-cutting axes (orthogonal to the spine)

The spine is one axis. Every node also carries:

- **Epistemic tier** (Section 3) — how confident we are.
- **Knowledge class** (Section 1.1) — what *kind* of knowledge it is.
- **Time axis** — `discovered_at`, `superseded_by`, `valid_from/until`.
- **Space/culture axis** — region, tradition, language of origin.
- **Confidence & controversy flags** — disputed, consensus, fringe.

### 2.3 The classification maps unify here

The parallel maps (`math_logic_map.md` covers math/logic; `ml_pipeline_guide.md`
covers ML pipelines) plug into this spine at specific levels:

- **math_logic_map** → `Domain: Formal Sciences → Discipline: Mathematics /
  Logic / Computer Science → ... → Concept: e.g. Gödel Incompleteness →
  Principle: ... → Method: proof technique → Experiment: formal verification`.
- **ml_pipeline_guide** → `Domain: Applied Sciences → Discipline:
  Computer Science → Subdiscipline: Machine Learning → Field: e.g. RAG
  pipelines → Concept: embedding → Principle: ... → Method: fine-tuning →
  Experiment: eval run → Evidence: benchmark scores → Application: deployed
  model → Outcome: measured quality`.

New maps (biology, history, medicine, law, arts) slot in identically.
**The spine is domain-agnostic by design.**

### 2.4 Knowledge graph schema

**Node types** (prefix `n:`):

```
n:Domain        n:Discipline     n:Subdiscipline  n:Field
n:Concept       n:Principle      n:Method         n:Experiment
n:Evidence      n:Application    n:Outcome        n:Person
n:Organization  n:Place          n:Event          n:Artifact
n:Document      n:Dataset        n:Formula        n:Theorem
n:Algorithm     n:Protocol       n:Failure        n:Lesson
n:Language      n:Tradition      n:Myth           n:Question  (open problems)
n:Controversy   n:Hypothesis     n:Prediction     n:Tool
```

**Edge types** (prefix `e:`), grouped:

*Containment / derivation:*
```
PART_OF          (child → parent, up the spine)
PART_OF_FIELD    (cross-cutting membership)
DERIVED_FROM     (downstream node ← upstream basis)
SUPERSEDES       (newer node replaces older)
INSTANCE_OF      (specific → general type)
```

*Causal / evidential:*
```
EVIDENCES        (evidence → claim it supports)
CONTRADICTS      (evidence vs. claim, or node vs. node)
SUPPORTS         (weak/partial support)
INVALIDATES      (failure → method/principle it rules out)
CAUSED_BY        (outcome ← cause)
ENABLES          (capability dependency)
DEPENDS_ON       (prerequisite)
```

*Temporal / provenance:*
```
PUBLISHED_IN     (document → venue/journal)
AUTHORED_BY      (node → person/org)
OBSERVED_AT      (evidence → place/time)
CONDUCTED_BY     (experiment → team/org)
USES             (experiment → method/tool/dataset)
CITES            (document → document)
TRANSLATED_FROM  (node → source-language version)
```

*Social / cultural:*
```
INFLUENCED_BY    (person/node ← person/node)
TEACHES          (person → concept/lesson)
PRACTICED_IN     (tradition → region)
RELATED_TO       (weak semantic link, high fan-out — used sparingly)
```

Every edge carries: `weight` (confidence 0..1), `source` (which evidence
chain justifies the edge), `valid_from`, `valid_until`, `created_by`,
`verification_tier`.

### 2.5 Open questions as nodes

Unsolved problems are `n:Question` nodes — *"What is dark matter?"*,
*"P vs NP?"*, *"How did the Indus script work?"*. They link `OPEN` edges to
`n:Hypothesis` nodes (candidate answers) and `BLOCKED_BY` edges to
`n:Failure`/`n:Limitation` nodes. **Gap detection** (Section 4.7) is partly
the automated discovery of under-connected `n:Question` nodes.

---

## 3. VERIFICATION FRAMEWORK

### 3.1 The nine epistemic tiers

Every claim node carries exactly one `epistemic_tier`. Ordered strongest → weakest:

| Tier | Name | Definition | Example |
|---|---|---|---|
| T1 | **Verified Fact** | Independently reproduced, consensus, no credible dispute | Water boils at 100°C at 1 atm |
| T2 | **Math Proof** | Formal proof, machine-checkable (Lean/Coq) or accepted | √2 is irrational |
| T3 | **Theory** | Well-supported explanatory framework, not directly observable | Evolution by natural selection |
| T4 | **Observation** | Direct measurement/observation, possibly unrepeated | A supernova sighting |
| T5 | **Expert Opinion** | Credible authority's judgment, no formal proof | A surgeon's protocol recommendation |
| T6 | **Personal Experience** | First-hand account, unverifiable by others | "This bridge design failed in my project" |
| T7 | **Hypothesis** | Testable conjecture, awaiting evidence | A proposed dark-matter candidate |
| T8 | **Unverified** | Claim with weak/absent provenance | Forum post, hearsay |
| T9 | **Speculation** | Opinion/philosophy without empirical anchor | "AI will solve climate change" |

**Rules:**
- Tiers are *per-claim*, not per-document. A paper can contain T2 math and
  T8 speculation; each proposition gets its own node.
- Tiers can be **promoted** (T7 → T3 after evidence accumulates) or
  **demoted** (T3 → T7 if contradicted). Promotion/demotion is logged.
- T6 (personal experience) is **never deleted** but is visually and
  algorithmically separated from T1–T5 in retrieval — a search can request
  "only verified" or "include experiences."

### 3.2 Source verification pipeline

Every ingested source passes through:

```
INGEST → AUTHORSHIP CHECK → PROVENANCE CHAIN → EVIDENCE EVAL →
TIER ASSIGNMENT → CROSS-CHECK → CANONICAL INDEX
```

- **Authorship check:** is the claimed author real? (ORCID, institutional
  affiliation, publication record). Detects impersonation and sockpuppetry.
- **Provenance chain:** document → raw data → experimental apparatus →
  raw observations → processed results → published claim. Broken chain =
  tier capped at T8.
- **Evidence evaluation:** for each `n:Evidence` node, record
  `replication_count`, `independent_replications`, `retraction_status`,
  `funding_conflicts`, `sample_size`, `methodology_rigor_score`.

### 3.3 Contradiction detection

Contradictions are **features, not bugs**. The archive stores them:

- `CONTRADICTS` edges link incompatible claims.
- **Contradiction clusters** are `n:Controversy` nodes that aggregate
  mutually-contradicting claims (e.g., "climate sensitivity range").
- Each controversy node has a `resolution_status`: `open`, `resolved_for_X`,
  `unresolved`, `resolved_by_consensus`, `resolved_by_experiment`.
- Contradictions are surfaced in retrieval: a query about a contested topic
  returns *both sides* plus the controversy node, never silently picks one.

### 3.4 Outdated-knowledge correction

Knowledge decays. The archive handles it via:

- **Temporal validity:** `valid_from`/`valid_until` on claims.
- **Supersession chains:** `SUPERSEDES` edges; the old node is never deleted
  but is marked `superseded_by` and demoted.
- **Deprecation events:** when a field overturns (e.g., a drug recalled, a
  cosmology model revised), a `DeprecationEvent` cascades: demote all
  dependent claims by one tier, flag for re-review.
- **Re-verification schedule:** high-impact claims (medical, safety,
  structural) get periodic re-verification triggers. Stale claims decay in
  ranking.

### 3.5 Uncertainty representation

Every node carries a structured `uncertainty` object:

```yaml
uncertainty:
  epistemic_tier: T4
  confidence: 0.72            # 0..1 aggregate
  known_unknowns:             # what we don't know
    - "exact replication count beyond 3"
  contested_by: [n:Controversy#climate-sensitivity]
  last_verified: 2024-06-01
  decay_half_life_days: 1825  # how fast this claim ages
```

The AI engine (Section 4) **must surface uncertainty** in every answer —
an answer without an uncertainty statement is a bug, not a feature.

---

## 4. AI KNOWLEDGE ENGINE

### 4.1 Capabilities (the ten)

| # | Capability | Mechanism |
|---|---|---|
| 1 | **Semantic search** | Dense vector retrieval over chunked nodes + BM25 hybrid |
| 2 | **Graph reasoning** | Cypher/GQL traversals over the knowledge graph |
| 3 | **RAG (Retrieval-Augmented Generation)** | Graph-grounded retrieval → LLM synthesis with citations |
| 4 | **NLU (Natural Language Understanding)** | Entity/relation extraction from text into graph nodes |
| 5 | **Cross-disciplinary discovery** | Graph paths connecting distant domains (Section 4.5) |
| 6 | **Pattern recognition** | Graph motif detection, embedding clustering |
| 7 | **Hypothesis generation** | LLM + graph completion: propose edges/nodes filling gaps |
| 8 | **Gap detection** | Under-connected questions, missing evidence, contradictions |
| 9 | **Outcome learning** | Track which retrieved answers were useful/correct → rerank |
| 10 | **Provenance tracing** | Every AI answer cites node IDs → full evidence chain |

### 4.2 Retrieval architecture (hybrid, four channels)

```
Query
 ├─→ [C1] Dense vector search      (semantic similarity, pgvector/Qdrant/LanceDB)
 ├─→ [C2] Sparse BM25               (keyword, Postgres FTS / Elasticsearch)
 ├─→ [C3] Graph traversal           (Cypher: expand from seed entities)
 └─→ [C4] Structured filter         (epistemic_tier, domain, date, language)
        │
        ▼
   Reciprocal Rank Fusion (RRF)
        │
        ▼
   Cross-encoder reranker (optional, for high-stakes queries)
        │
        ▼
   Context assembly → LLM synthesis → answer + citations + uncertainty
```

### 4.3 Graph-RAG pattern (the key innovation)

Standard RAG retrieves text chunks. **Graph-RAG** retrieves *structured
knowledge neighborhoods*:

1. Extract entities from the query ("tokamak", "fusion gain").
2. Find seed nodes in the graph.
3. Traverse `k` hops collecting: the node, its `n:Evidence`, its
   `n:Experiment`s, its `n:Failure`s, its `n:Lesson`s, its
   `SUPERSEDES`/`CONTRADICTS` neighbors.
4. Serialize the subgraph into a prompt with node IDs as citation anchors.
5. LLM answers grounded in the subgraph, citing node IDs.

This is the difference between "what does the internet say about tokamaks"
and "here are the 7 documented tokamak failure modes, each with its
experiment ID and lesson node."

### 4.4 Anti-hallucination contract (mandatory)

**Every AI-generated answer must satisfy:**

1. **Citation requirement:** every factual claim in the answer maps to ≥1
   node ID that exists in the graph and is retrievable. Uncited claims are
   stripped or marked `[UNSOURCED]`.
2. **Evidence floor:** answers to empirical questions must cite `n:Evidence`
   nodes; pure-LLM generation is forbidden for empirical claims.
3. **Uncertainty disclosure:** every answer ends with the aggregate
   uncertainty of its cited nodes (lowest tier wins).
4. **Tier respect:** the engine never presents T6/T8/T9 material as T1–T3.
   Experience reports are labeled "personal account — not independently verified."
5. **Refusal:** if retrieval returns no supporting nodes, the engine says
   "the archive does not contain verified knowledge on this" — it does not
   confabulate.
6. **Adversarial check:** generated answers are re-verified against the
   source nodes before display (a second pass checking that citations
   actually support the claims).

### 4.5 Cross-disciplinary discovery

The graph enables **serendipitous retrieval**: paths between distant domains.

Example mechanism — **analogical bridge search**:
- Query: "how to improve battery thermal management"
- Graph finds `n:Concept:Phase-Change Material` in `Domain: Materials Science`
- Finds `n:Concept:Regenerative Cooling` in `Domain: Aerospace Engineering`
- Finds shared `n:Principle:Latent Heat Absorption`
- Surfaces the aerospace method as a candidate for batteries →
  generates a `n:Hypothesis` node for human review.

Implementation: weighted shortest-path / random-walk-with-restart over the
graph, seeded from query entities, filtered by `epistemic_tier ≤ T5`,
scored by path novelty (penalize paths within same discipline).

### 4.6 Failure-first retrieval (the killer feature)

For any `n:Method` or `n:Experiment` query, retrieval **always includes**:
- All `n:Failure` nodes connected via `INVALIDATES` or sharing the method.
- All `n:Lesson` nodes distilled from those failures.
- A "known failure modes" summary block at the top of the answer.

A user designing a bridge gets the collapse records *first*. This is the
archive's reason to exist.

### 4.7 Gap detection

Automated processes that find holes in human knowledge:

- **Under-connected questions:** `n:Question` nodes with no `n:Hypothesis`
  children, or hypotheses with no `n:Experiment` children.
- **Evidence deserts:** `n:Principle` nodes with claims but zero `n:Evidence`.
- **Contradiction clusters** with no active `n:Experiment` attempting
  resolution.
- **Temporal gaps:** fields with no new evidence in >N years.
- **Cross-domain gaps:** principles proven in domain A with no attempted
  application in analogous domain B.

Gap reports are published as `n:Report` nodes — a continuously updated
**map of what humanity doesn't know**, which is itself valuable knowledge.

### 4.8 Outcome learning

Every AI answer interaction is logged (privacy-preserving, Section 7):
- Was the answer useful? (thumbs, follow-up query, citation click-through)
- Was a cited node later found wrong? (feeds back to demotion)
- Did the user act on a `n:Lesson` and avoid a failure? (the holy grail —
  tracked via optional "I used this" reports)

This closes the loop: the archive learns which knowledge *prevents harm*.

---

## 5. EXPERIENCE RECORD SCHEMA

### 5.1 The canonical record

Every significant human experience — a failed experiment, a field deployment,
a medical case, a historical event witnessed, a design iteration — is stored
as an **Experience Record** with this mandatory structure:

```yaml
experience_record:
  id: exp:uuid
  title: "J-TEXT-0042: Li-S battery thermal runaway in pouch cells"
  epistemic_tier: T6              # personal experience — never auto-promoted
  class: experiment_failure      # one of the 7 classes + experience subtypes

  # --- the spine ---
  problem: "Pouch-cell Li-S batteries overheated during fast-charge cycling"
  context:
    when: "2023-2024"
    where: "lab, Shanghai"
    conditions: "25°C ambient, 2C charge rate, 80% SOC window"
    participants: [person:uuid, org:uuid]
    prior_state: "cells rated for 500 cycles"
  objective: "Achieve 1000 cycles at 2C without capacity fade >20%"

  # --- the attempt ---
  assumptions:
    - "Electrolyte stable to 60°C"
    - "Separator prevents dendrite propagation"
    - "BMS cutoff at 55°C sufficient"
  actions:
    - step: 1
      action: "Charged 20 cells at 2C to 80% SOC"
      tool: "Neware BTS4000 cycler"
      resource_cost: "480 cell-hours"
    - step: 2
      action: "Accelerated aging at 45°C"
      tool: "thermal chamber"
      resource_cost: "720 cell-hours"
  resources:
    materials: ["Li-S pouch cells ×20", "LiTFSI electrolyte"]
    equipment: ["BTS4000", "thermal chamber", "EIS analyzer"]
    funding: "internal R&D"
    personnel_hours: 340

  # --- the outcome ---
  results:
    quantitative:
      - metric: "cycle life"
        expected: ">1000 cycles"
        actual: "mean 312 cycles, σ=47"
      - metric: "failure mode"
        actual: "thermal runaway at cycle ~300, venting + ignition"
    qualitative: "cells swelled after cycle 250; EIS showed SEI growth"
  failures:
    - what_failed: "SEI layer grew exponentially above 40°C"
      when_detected: "cycle 180 (post-mortem EIS)"
      root_cause_hypothesis: "electrolyte oxidation at high temp + high rate"
      could_have_been_predicted_by: ["accelerated aging test at higher temp earlier"]
  solutions_attempted:
    - "reduced charge rate to 1C → extended life to 480 cycles (still insufficient)"
    - "added ceramic separator → delayed but did not prevent runaway"
  solutions_that_worked: []        # empty = unresolved
  evidence:
    - type: "raw_data"
      location: "dataset:uuid (cyclers logs, EIS spectra)"
      reproducible: true
    - type: "images"
      location: "artifact:uuid (post-mortem photos)"
    - type: "third_party"
      location: "paper:uuid (confirms similar failure in literature)"
  lessons:
    - "Li-S pouch cells need active cooling above 1C charge rates"
    - "SEI growth is the leading indicator — monitor EIS from cycle 50"
    - "Accelerated aging at 45°C predicts 25°C failure ~3x faster"
  knowledge_links:
    methods_used: [method:uuid]
    principles_violated: [principle:lawson-criterion-analogue]
    related_failures: [exp:uuid (similar Li-ion thermal events)]
    contradicts: []
    supports: [hypothesis:uuid]

  # --- provenance ---
  author: person:uuid
  organization: org:uuid
  recorded_at: 2024-11-25
  verification:
    independently_replicated: false
    replication_status: "single-lab"
    peer_reviewed: false
    raw_data_available: true
```

### 5.2 Experience subtypes

| Subtype | Example | Tier cap |
|---|---|---|
| `lab_experiment` | Failed synthesis, unexpected result | T6 |
| `field_deployment` | Bridge inspection finding, mine collapse | T6 |
| `clinical_case` | Patient outcome, adverse event | T6 (anonymized) |
| `engineering_incident` | Factory failure, software outage postmortem | T6 |
| `historical_witness` | Oral history, eyewitness account | T6 |
| `indigenous_knowledge` | Traditional ecological knowledge, craft technique | T6 (with consent framework) |
| `negative_result` | "We tried X, it didn't work, here's the data" | T6→can promote to T4 if replicated |

### 5.3 Failed experiments as first-class citizens

The schema **requires** the `failures:` block for any `class: experiment*`
record. A failure record with empty `failures` is rejected at ingestion —
this is the archive's core invariant.

Failed experiments get **special retrieval treatment**: they are indexed
under their `root_cause` and `lessons`, not just their `objective`, so a
search for "thermal runaway causes" finds them even if the user never
searched for "battery cycling."

### 5.4 Promotion path for experiences

A personal experience can gain epistemic weight:

```
T6 (personal) → T4 (observation) → T3 (theory) → T1 (verified fact)
     │                │                │              │
     │                │                │              └─ consensus + replication
     │                │                └─ pattern across many experiences
     │                └─ independently replicated experiment
     └─ initial recording (always T6 or lower)
```

Promotion requires: independent replication, peer review, or convergence
with existing verified knowledge. **Never automatic.**

---

## 6. TECHNICAL ARCHITECTURE

### 6.1 The stack (layered)

```
┌─────────────────────────────────────────────────────────────┐
│ L6 · PRESENTATION   Web app, mobile, API, offline PWA        │
├─────────────────────────────────────────────────────────────┤
│ L5 · AI ENGINE      RAG orchestrator, graph reasoner, NLU    │
├─────────────────────────────────────────────────────────────┤
│ L4 · KNOWLEDGE      Graph DB + Vector DB + Search + Relational│
├─────────────────────────────────────────────────────────────┤
│ L3 · PIPELINES      Ingestion, verification, translation,     │
│                     extraction, embedding, contradiction scan │
├─────────────────────────────────────────────────────────────┤
│ L2 · STORAGE        Distributed object store + graph shards   │
│                     + vector shards + cryptographic ledger    │
├─────────────────────────────────────────────────────────────┤
│ L1 · IDENTITY       DID/VC, signatures, reputation, access    │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Technology selection — existing vs near-term vs speculative

**Legend:** `[EXISTS]` production-ready today · `[NEAR]` stable but maturing ·
`[SPEC]` research / not yet practical.

#### Storage & databases

| Component | Choice | Status | Rationale |
|---|---|---|---|
| Relational (metadata, users, transactions) | **PostgreSQL 16+** + `pgvector` | `[EXISTS]` | One DB for relational + vector; ACID; mature |
| Property graph (knowledge graph) | **Neo4j Community/Enterprise** OR **FalkorDB** | `[EXISTS]` | Neo4j: mature, Cypher, huge ecosystem. FalkorDB: Redis-based, fast traversals, GraphBLAS — better for read-heavy graph analytics. **Avoid Kuzu** — archived Oct 2025. |
| Vector search (dedicated, scale-out) | **Qdrant** (server) or **LanceDB** (embedded) | `[EXISTS]` | Qdrant for production service; LanceDB for edge/offline/prototype |
| Full-text / BM25 | **PostgreSQL FTS** or **Elasticsearch/OpenSearch** | `[EXISTS]` | Postgres FTS suffices for prototype; OpenSearch at scale |
| Object storage (documents, datasets, media) | **S3-compatible** (MinIO self-hosted or cloud) | `[EXISTS]` | Content-addressed blobs, versioning |
| Distributed file system (global scale) | **IPFS** or **Filecoin** | `[EXISTS]`/`[NEAR]` | Content-addressing = built-in integrity; IPFS for public knowledge, Filecoin for persistence incentives |
| Immutable audit ledger | **Hash-chained append-only log** (custom) or **Apache Kafka + cryptographic chaining** | `[EXISTS]` | Every write to the archive is a signed, chained record — tamper-evident |
| Time-series (access logs, metrics) | **TimescaleDB** or **VictoriaMetrics** | `[EXISTS]` | Usage analytics, outcome learning |

#### AI / ML

| Component | Choice | Status | Rationale |
|---|---|---|---|
| Embeddings | **Open-source models**: BGE-M3, E5, GTE (multilingual) | `[EXISTS]` | Multilingual, self-hostable, no API dependency |
| LLM (synthesis, extraction) | **Llama 3.x / Qwen 2.5 / Mistral** (self-hosted) + optional API (Claude/GPT) | `[EXISTS]` | Self-hosted for sovereignty; API for quality ceiling |
| RAG orchestration | **LlamaIndex** or **LangGraph** (custom) | `[EXISTS]` | LlamaIndex for retrieval pipelines; LangGraph for stateful agents |
| GraphRAG | **LightRAG** or **Microsoft GraphRAG** (reference) + custom graph layer | `[EXISTS]`/`[NEAR]` | LightRAG: lightweight, incremental updates. MS GraphRAG: community detection (maintenance mode). We'll build custom on our own graph. |
| NLU / entity extraction | **spaCy + LLM-assisted extraction** | `[EXISTS]` | spaCy for speed; LLM for complex relation extraction |
| Translation | **NLLB-200** (Meta, 200 languages) + **MADLAD-400** | `[EXISTS]` | Open, covers low-resource languages |
| OCR / document parsing | **Docling** (IBM), **MinerU**, **Marker** | `[EXISTS]` | Parse PDFs, scans, formulas into structured text |
| Re-ranking | **bge-reranker**, **Cohere rerank API** | `[EXISTS]` | Cross-encoder for precision on high-stakes queries |
| Formal verification (math) | **Lean 4** | `[EXISTS]` | Machine-checkable proofs → T2 tier |
| Speech / oral history | **Whisper** (OpenAI, self-hostable) | `[EXISTS]` | Transcribe oral histories, indigenous knowledge |

#### Infrastructure

| Component | Choice | Status |
|---|---|---|
| API framework | **FastAPI** (Python) | `[EXISTS]` |
| Frontend | **SvelteKit / Next.js** + **Tailwind** | `[EXISTS]` |
| Search UI | **Typesense** or **Meilisearch** | `[EXISTS]` |
| Message queue | **Redis + Celery** or **RabbitMQ** | `[EXISTS]` |
| Orchestration | **Airflow / Prefect** for pipelines | `[EXISTS]` |
| Monitoring | **Prometheus + Grafana** | `[EXISTS]` |
| Auth | **Keycloak** (OIDC) or **Authentik** | `[EXISTS]` |
| Crypto | **age / GPG** for at-rest; **Ed25519** signatures; **IPFS CID** content addressing | `[EXISTS]` |
| Containerization | **Docker + Kubernetes** (or Docker Compose for small scale) | `[EXISTS]` |
| CDN / edge | **Cloudflare** or self-hosted **Varnish** | `[EXISTS]` |

#### Speculative (research horizon)

| Component | Status | Note |
|---|---|---|
| **Neural-symbolic integration** — LLM proposes, symbolic engine verifies | `[SPEC]` | The holy grail for anti-hallucination; early research |
| **Knowledge compilation** — compile graph into differentiable model | `[SPEC]` | Would enable gradient-based reasoning over knowledge |
| **Decentralized knowledge consensus** — Byzantine-fault-tolerant graph | `[SPEC]` | Needed for truly uncapturable global archive |
| **Zero-knowledge proofs of knowledge provenance** | `[SPEC]` | Prove a claim's source chain without revealing sources |
| **Continual learning without catastrophic forgetting** | `[SPEC]` | Archive updates must not erase prior knowledge |

### 6.3 Database schemas

#### 6.3.1 PostgreSQL — canonical metadata store

```sql
-- Users & identity
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  did           TEXT UNIQUE,                -- decentralized identifier
  display_name  TEXT,
  public_key    BYTEA,                      -- Ed25519 for signing contributions
  reputation    NUMERIC(5,2) DEFAULT 0,     -- Section 7
  created_at    TIMESTAMPTZ DEFAULT now(),
  status        TEXT DEFAULT 'active'       -- active/suspended/banned
);

-- Nodes (every knowledge node has a row here)
CREATE TABLE nodes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_type       TEXT NOT NULL,            -- Domain/Discipline/.../Lesson
  slug            TEXT UNIQUE NOT NULL,     -- URL-safe identifier
  title           TEXT NOT NULL,
  content_md      TEXT,                     -- markdown body
  content_hash    BYTEA NOT NULL,           -- SHA-256 of content (integrity)
  epistemic_tier  SMALLINT NOT NULL CHECK (epistemic_tier BETWEEN 1 AND 9),
  knowledge_class TEXT NOT NULL,            -- discovery/math/experience/...
  domain          TEXT,                     -- denormalized for fast filter
  discipline      TEXT,
  language        TEXT DEFAULT 'en',
  confidence      NUMERIC(4,3),
  uncertainty     JSONB DEFAULT '{}',
  valid_from      TIMESTAMPTZ,
  valid_until     TIMESTAMPTZ,
  superseded_by   UUID REFERENCES nodes(id),
  created_by      UUID REFERENCES users(id),
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now(),
  version         INT DEFAULT 1,
  ipfs_cid        TEXT                      -- content-addressed blob pointer
);
CREATE INDEX idx_nodes_tier ON nodes(epistemic_tier);
CREATE INDEX idx_nodes_type ON nodes(node_type);
CREATE INDEX idx_nodes_domain ON nodes(domain, discipline);
CREATE INDEX idx_nodes_content_hash ON nodes(content_hash);

-- Edges (knowledge graph relationships — mirrored in graph DB)
CREATE TABLE edges (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  src_node      UUID NOT NULL REFERENCES nodes(id),
  dst_node      UUID NOT NULL REFERENCES nodes(id),
  edge_type     TEXT NOT NULL,              -- PART_OF/EVIDENCES/...
  weight        NUMERIC(4,3) DEFAULT 1.0,
  source        TEXT,                       -- justification for the edge
  valid_from    TIMESTAMPTZ,
  valid_until   TIMESTAMPTZ,
  created_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE(src_node, dst_node, edge_type)
);
CREATE INDEX idx_edges_src ON edges(src_node, edge_type);
CREATE INDEX idx_edges_dst ON edges(dst_node, edge_type);

-- Experience records (the Section 5 schema, as JSONB + indexed fields)
CREATE TABLE experience_records (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_id         UUID REFERENCES nodes(id),  -- the n: node for this record
  record          JSONB NOT NULL,              -- full Section 5 schema
  epistemic_tier  SMALLINT NOT NULL,
  experience_type TEXT NOT NULL,               -- lab_experiment/field_deployment/...
  failure_flag    BOOLEAN DEFAULT false,       -- has non-empty failures block
  lessons         TEXT[],                      -- extracted lesson strings
  searchable_tsv  tsvector,                    -- full-text index
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- Evidence records
CREATE TABLE evidence (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_id         UUID REFERENCES nodes(id),
  evidence_type   TEXT NOT NULL,               -- raw_data/images/third_party/...
  location        TEXT NOT NULL,               -- dataset/artifact/paper pointer
  reproducible    BOOLEAN DEFAULT false,
  replication_count INT DEFAULT 0,
  independent_replications INT DEFAULT 0,
  retraction_status TEXT DEFAULT 'none',       -- none/retracted/under_review
  methodology_rigor NUMERIC(3,2),
  funding_conflicts JSONB DEFAULT '[]',
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- Provenance / audit chain (hash-linked, tamper-evident)
CREATE TABLE audit_log (
  seq             BIGSERIAL PRIMARY KEY,
  prev_hash       BYTEA NOT NULL,              -- hash of previous record
  record_hash     BYTEA NOT NULL,              -- hash of this record
  actor           UUID REFERENCES users(id),
  action          TEXT NOT NULL,               -- create/update/delete/verify/demote
  target_type     TEXT NOT NULL,               -- node/edge/evidence/user
  target_id       UUID NOT NULL,
  payload         JSONB,
  signature       BYTEA NOT NULL,              -- Ed25519 signature
  timestamp       TIMESTAMPTZ DEFAULT now()
);

-- Contradictions & controversies
CREATE TABLE controversies (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_id         UUID REFERENCES nodes(id),
  title           TEXT NOT NULL,
  description     TEXT,
  resolution_status TEXT DEFAULT 'open',       -- open/resolved_*/unresolved
  resolution_evidence JSONB DEFAULT '[]',
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- Verification events (tier promotions/demotions)
CREATE TABLE verification_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_id         UUID NOT NULL REFERENCES nodes(id),
  from_tier       SMALLINT NOT NULL,
  to_tier         SMALLINT NOT NULL,
  reason          TEXT NOT NULL,
  evidence_refs   UUID[],
  verifier        UUID REFERENCES users(id),
  verified_at     TIMESTAMPTZ DEFAULT now()
);

-- Translations
CREATE TABLE translations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_id         UUID NOT NULL REFERENCES nodes(id),
  language        TEXT NOT NULL,
  title           TEXT NOT NULL,
  content_md      TEXT NOT NULL,
  translator      UUID REFERENCES users(id),
  machine_translated BOOLEAN DEFAULT false,
  verified        BOOLEAN DEFAULT false,
  created_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(node_id, language)
);
```

#### 6.3.2 Graph DB schema (Neo4j Cypher)

```cypher
// Node labels mirror node_type; properties mirror critical fields
CREATE (d:Domain {slug:'natural-sciences', title:'Natural Sciences',
                  epistemic_tier:1, language:'en'})
CREATE (disc:Discipline {slug:'physics', title:'Physics',
                  epistemic_tier:1, domain:'natural-sciences'})
CREATE (sub:Subdiscipline {slug:'plasma-physics', title:'Plasma Physics',
                  epistemic_tier:1, discipline:'physics'})
CREATE (f:Field {slug:'magnetic-confinement-fusion', title:'Magnetic Confinement Fusion',
                  epistemic_tier:3, subdiscipline:'plasma-physics'})
CREATE (c:Concept {slug:'tokamak', title:'Tokamak',
                  epistemic_tier:1, field:'magnetic-confinement-fusion'})

// Edges
CREATE (c)-[:PART_OF {weight:1.0, source:'canonical-map'}]->(f)
CREATE (f)-[:PART_OF {weight:1.0}]->(sub)
CREATE (sub)-[:PART_OF {weight:1.0}]->(disc)
CREATE (disc)-[:PART_OF {weight:1.0}]->(d)

// Evidence edge
CREATE (e:Evidence {slug:'jet-dt-1997', replication_count:14,
                    independent_replications:9, epistemic_tier:1})
CREATE (e)-[:EVIDENCES {weight:0.95, source:'JET-NF-1998'}]->(c)

// Failure edge — the killer feature
CREATE (fail:Failure {slug:'jet-disruption-damage',
                      root_cause:'disruption-induced EM forces',
                      epistemic_tier:4})
CREATE (fail)-[:INVALIDATES {weight:0.9}]->(m:Method {slug:'high-beta-operation'})
CREATE (lesson:Lesson {slug:'disruption-mitigation-required'})
CREATE (fail)-[:YIELDS_LESSON]->(lesson)
CREATE (lesson)-[:TEACHES]->(c)
```

**Graph DB is the query engine; PostgreSQL is the source of truth.**
Nodes/edges are written to Postgres first (ACID, audit log), then
asynchronously projected into the graph DB for traversal queries. The
graph DB is rebuildable from Postgres at any time.

#### 6.3.3 Vector DB schema (pgvector / Qdrant / LanceDB)

```sql
-- pgvector (if using Postgres extension)
CREATE EXTENSION vector;

CREATE TABLE node_embeddings (
  node_id       UUID PRIMARY KEY REFERENCES nodes(id),
  chunk_idx     INT NOT NULL,               -- for long documents
  content       TEXT NOT NULL,              -- the chunk text
  embedding     vector(1024) NOT NULL,      -- BGE-M3 / E5 dimension
  metadata      JSONB DEFAULT '{}',         -- tier, domain, language, node_type
  created_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE(node_id, chunk_idx)
);
CREATE INDEX idx_embeddings_hnsw
  ON node_embeddings USING hnsw (embedding vector_cosine_ops);

-- Hybrid search: combine with tsvector
ALTER TABLE node_embeddings ADD COLUMN tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX idx_embeddings_tsv ON node_embeddings USING gin(tsv);
```

For Qdrant (production scale):

```python
# Collection config
client.create_collection(
    collection_name="knowledge_chunks",
    vectors_config={
        "dense": VectorParams(size=1024, distance=Distance.COSINE),
        "sparse": SparseVectorParams()
    },
    on_disk_payload=True   # for large payloads
)
# Payload: {node_id, chunk_idx, epistemic_tier, domain, language, node_type}
```

### 6.4 API design

REST + GraphQL for the knowledge graph. Base: `/api/v1`

#### Core endpoints

```
# Search (hybrid: semantic + keyword + graph + filters)
POST /api/v1/search
  body: {query, mode: 'hybrid'|'semantic'|'keyword'|'graph',
         filters: {domain, discipline, epistemic_tier_max, language,
                   include_failures: true, date_range},
         limit: 20, offset: 0}
  → {results: [{node_id, title, snippet, tier, score, citations}],
     uncertainty: {...}, graph_context: {...}}

# Node retrieval
GET  /api/v1/nodes/{slug}
  → full node + edges (k-hop configurable) + evidence + experience record

GET  /api/v1/nodes/{slug}/neighborhood?depth=2&edge_types=PART_OF,EVIDENCES,INVALIDATES
  → subgraph for graph-RAG context assembly

# Graph queries (power users / AI engine)
POST /api/v1/graph/query
  body: {cypher: "MATCH (n:Concept)...", params: {...}}
  → {nodes, edges, truncation_info}

# Experience records
POST /api/v1/experiences          # submit (requires auth + DID signature)
GET  /api/v1/experiences/{id}
GET  /api/v1/experiences?type=lab_experiment&has_failures=true&domain=...

# Verification
POST /api/v1/nodes/{id}/verify    # submit verification evidence → tier review
GET  /api/v1/nodes/{id}/verification-history
POST /api/v1/nodes/{id}/dispute   # flag contradiction → creates controversy node

# AI assistant
POST /api/v1/ask
  body: {query, include_experiences: true, citation_depth: 3}
  → {answer, citations: [{node_id, claim, tier}], uncertainty, failure_modes}

# Gap reports
GET  /api/v1/gaps                 # under-connected questions, evidence deserts
GET  /api/v1/gaps/{id}

# Translation
GET  /api/v1/nodes/{id}?lang=sw   # returns translated version if available
POST /api/v1/nodes/{id}/translate # request/submit translation

# Bulk / export
GET  /api/v1/export?format=jsonl|parquet&domain=...
GET  /api/v1/sync?since=timestamp # offline/edge sync protocol
```

#### Auth & contribution

```
POST /api/v1/auth/register        # DID creation, key generation
POST /api/v1/auth/login           # challenge-response with Ed25519 key
POST /api/v1/contributions        # submit new node/edge/evidence/experience
POST /api/v1/contributions/{id}/endorse   # peer endorsement (+reputation)
POST /api/v1/contributions/{id}/dispute   # challenge (-reputation)
```

All write endpoints require: DID signature, rate limiting, automated
screening (Section 7), and entry into the `staging` tier until verified
(T8 by default — promotion requires review/endorsement/replication).

### 6.5 AI retrieval pipeline (detailed)

```
User query
   │
   ▼
[1] QUERY UNDERSTANDING (LLM)
    - intent classification (search/ask/explore/verify)
    - entity extraction → candidate node slugs
    - epistemic intent: "what is verified about X" vs "what have people
      experienced with X" vs "what failed with X"
   │
   ▼
[2] MULTI-CHANNEL RETRIEVAL (parallel)
    ├─ dense vector: top-50 chunks (BGE-M3 embeddings)
    ├─ BM25: top-50 keyword matches
    ├─ graph: seed entities → 2-hop neighborhood
    │         (PART_OF up, EVIDENCES/INVALIDATES down)
    └─ structured: filters on tier/domain/date/language
   │
   ▼
[3] FUSION & RERANK
    - Reciprocal Rank Fusion across channels
    - cross-encoder rerank top-100 → top-20
    - epistemic tier boost: T1-T3 boosted for factual queries;
      T6 boosted for "experience" queries
   │
   ▼
[4] SUBGRAPH ASSEMBLY (graph-RAG)
    - collect evidence nodes, failure nodes, lesson nodes,
      controversy nodes for each result
    - serialize to prompt with node-ID citation anchors
   │
   ▼
[5] SYNTHESIS (LLM)
    - generate answer grounded in assembled context
    - mandatory citation format: [node:slug#chunk]
    - uncertainty block from aggregate tier of cited nodes
   │
   ▼
[6] VERIFICATION PASS
    - check every citation resolves to a real node
    - check cited node tier matches claim strength
    - strip or flag uncited claims
    - check contradiction nodes are surfaced if relevant
   │
   ▼
[7] RESPONSE
    {answer, citations[], uncertainty{},
     failure_modes[] (if applicable),
     controversies[] (if applicable),
     gaps_suggested[] (related open questions)}
```

### 6.6 Distributed storage strategy

**Phase 1 (prototype):** single Postgres + Qdrant + Neo4j on one machine.
**Phase 2 (national/regional):** PostgreSQL read replicas, Qdrant cluster,
Neo4j causal cluster, S3 object storage, CDN.
**Phase 3 (global):**

- **Sharding by domain:** each discipline cluster owns its subgraph;
  cross-domain links via a federated query layer.
- **IPFS/Filecoin** for immutable document storage — content-addressed,
  no single point of failure, censorship-resistant.
- **Byzantine fault-tolerant replication** of the audit log `[SPEC]`.
- **Merkle-tree integrity:** every node's content hash chains into a
  global Merkle root, periodically anchored to a public blockchain
  (or a public transparency log like Certificate Transparency) for
  tamper-evident timestamps `[EXISTS: CT logs; SPEC: full BFT consensus]`.

### 6.7 Crypto integrity model

```
Every node:
  content_hash = SHA-256(canonical_serialization(node))
  signature   = Ed25519_sign(content_hash, author_private_key)

Every edge:
  edge_hash   = SHA-256(src_id + dst_id + edge_type + weight + timestamp)

Audit log:
  record_hash = SHA-256(prev_hash + payload + timestamp + signature)
  → tamper-evident chain; any modification breaks all subsequent hashes

Global state:
  merkle_root = Merkle(root of all node_hashes)
  → anchored externally (blockchain / transparency log) every N hours
  → anyone can verify any node's inclusion without trusting the archive
```

This gives **verifiable integrity without trusting the operator** —
the archive can prove "this claim existed on date X with this content"
even if the operator is compromised.

### 6.8 Implementation roadmap

#### Phase 0 — Beginner Prototype (Weeks 1–8) — **START HERE**

*Goal: prove the concept with one domain, manual curation.*

**Tech:** Python + SQLite (or single Postgres) + LanceDB (embedded vectors)
+ markdown files + simple web UI. **No graph DB yet** — edges in SQLite.
**Domain:** pick ONE narrow domain (e.g., "battery failure modes" or
"lean theorem proving"). Manually seed 50–200 nodes.

Deliverables:
- `nodes` + `edges` + `experience_records` tables (SQLite)
- Markdown ingestion script → node extraction (regex/LLM-assisted)
- LanceDB vector index for semantic search
- Simple FastAPI `/search` and `/ask` endpoints
- Single-page web UI (search + node view + experience record view)
- Manual verification workflow (admin promotes T8→T6→T4)

**Success criterion:** can answer "what has failed with X and why" for
the seed domain, with citations and failure records visible.

#### Phase 1 — MVP (Months 2–4)

- Migrate to PostgreSQL + pgvector (keep LanceDB for edge)
- Add Neo4j Community for graph queries
- Implement hybrid retrieval (vector + BM25 + graph traversal)
- LLM integration (self-hosted Llama 3.1 8B or API)
- Experience record submission form + review queue
- Basic verification workflow (endorse/dispute)
- Simple auth (email + API key; DID later)
- 3 domains seeded, ~1000 nodes

#### Phase 2 — Multi-domain (Months 5–9)

- NLLB-200 translation pipeline (EN↔ES↔ZH↔AR↔HI first)
- Whisper transcription for oral histories
- Docling/MinerU for PDF ingestion
- Contradiction detection (automated CONTRADICTS edge suggestion)
- Gap detection reports (weekly auto-generated)
- Reputation system v1 (endorsements, contribution quality)
- Mobile PWA + offline mode (LanceDB sync)
- 10 domains, ~10k nodes

#### Phase 3 — Scale (Months 10–18)

- Qdrant cluster for vector search at scale
- Neo4j Enterprise or FalkorDB for graph analytics
- IPFS integration for document storage
- Merkle-tree integrity + transparency log anchoring
- DID/VC identity (did:key, did:web)
- Multi-region deployment, CDN
- Graph-RAG with community detection (LightRAG patterns)
- Outcome learning pipeline (feedback → reranking)
- 50+ domains, ~100k nodes

#### Phase 4 — Global (Year 2+)

- Federated architecture: domain clusters with cross-cluster query layer
- Byzantine fault tolerance for audit log `[SPEC]`
- Zero-knowledge provenance `[SPEC]`
- Neural-symbolic verification for math/physics `[SPEC]`
- Integration with existing archives (arXiv, PubMed, museum databases,
  oral history projects) via adapters
- Governance transition to multi-stakeholder foundation

---

## 7. SECURITY & GOVERNANCE

### 7.1 Threat model

| Threat | Attack vector | Mitigation |
|---|---|---|
| **Poisoning** | Submit false claims, fake evidence, sockpuppet endorsements | Tier gating (all submissions start T8), reputation-weighted endorsement, automated fact-checking, cryptographic attribution |
| **Manipulation** | Edit history, gaslighting contributors, edit wars | Immutable audit log (hash-chained), signed contributions, dispute resolution protocol, version history always preserved |
| **Cyberattack** | DDoS, injection, data exfiltration, supply chain | Standard hardening (OWASP Top 10), rate limiting, WAF, dependency scanning, bug bounty, least-privilege access |
| **Capture/monopoly** | Single entity controls the archive, censors inconvenient knowledge | Federated architecture, IPFS content addressing, open-source code, multi-stakeholder governance, no single point of control |
| **Censorship** | Government/corporate demands to remove content | Content-addressed storage (can't delete from IPFS), jurisdictional diversity, legal defense fund, transparency reports |
| **Misinformation** | AI-generated fake nodes, deepfake evidence, LLM slop at scale | Provenance requirements, evidence floor, anti-AI-detection screening, human review for high-impact claims, source diversity requirements |
| **Privacy violation** | Exposure of personal experiences, indigenous knowledge without consent | Differential privacy for aggregate queries, consent framework for T6 records, right-to-be-forgotten with cryptographic erasure, jurisdictional compliance (GDPR etc.) |
| **Sybil attack** | One actor creates many fake identities to game reputation | DID-based identity, proof-of-personhood (optional), reputation decay, contribution quality scoring, community moderation |

### 7.2 Access control model

```
PUBLIC          — read all T1-T5 knowledge, search, ask AI
REGISTERED      — + submit contributions (T8 staging), endorse, comment
VERIFIED        — + T6 experience records, peer review, dispute resolution
EDITOR          — + promote/demote tiers, edit canonical nodes, merge duplicates
MODERATOR       — + remove spam/vandalism, suspend bad actors
GOVERNANCE      — + protocol changes, policy amendments, key rotation
```

Access is granted by reputation + community endorsement, not by payment.
**No pay-to-edit. No pay-to-verify.**

### 7.3 Reputation system

- Every contribution starts with `reputation_delta = 0`.
- Endorsements from VERIFIED users: `+1` to `+5` (weighted by endorser reputation).
- Successful verification of your contribution: `+10`.
- Contribution later found wrong/retracted: `-20`.
- Vandalism/spam: `-50` + suspension.
- Reputation decays over time (half-life ~180 days) to prevent entrenchment.
- Reputation gates access tiers but **never overrides epistemic tier** —
  a high-reputation user can still only submit T8 claims that must be verified.

### 7.4 Transparency & auditability

- **All writes are logged** in the hash-chained audit log.
- **All tier changes are logged** with reason and evidence.
- **All AI answers are logged** (privacy-preserving: query hash, not raw query,
  unless user opts in) for outcome learning and abuse detection.
- **Public audit endpoint:** anyone can verify the Merkle root and check
  inclusion proofs for any node.
- **Open governance meetings:** protocol changes proposed as `n:Proposal`
  nodes, debated publicly, ratified by stakeholder vote.

### 7.5 Correction protocol

When an error is found:

```
1. Anyone can file a Dispute (POST /dispute) with evidence.
2. Dispute creates a n:Controversy node linking the disputed claim
   and the counter-evidence.
3. Affected claim is demoted one tier pending review.
4. Reviewers (VERIFIED+) examine evidence, may:
   a. Uphold original → controversy resolved, tier restored
   b. Accept correction → node updated, SUPERSEDES edge created,
      old version preserved in history
   c. Escalate → GOVERNANCE-level review
5. All steps are in the audit log. The correction itself is a knowledge
   node — "we were wrong about X, here's how we found out."
```

**Corrections are celebrated, not hidden.** A correction is proof the
system works. The archive's credibility depends on visible self-correction.

### 7.6 Privacy model

| Data type | Protection |
|---|---|
| Public knowledge (T1-T5) | Fully public, no privacy concern |
| Personal experiences (T6) | Contributor chooses: public / pseudonymous / private / embargoed |
| Sensitive experiences (medical, legal, indigenous) | Consent framework, cultural protocols, jurisdictional compliance |
| User identity | DID-based, minimal PII, pseudonymous by default |
| Query logs | Hashed for analytics; raw queries only with explicit opt-in |
| Aggregate statistics | Differential privacy (ε ≤ 1.0) for any public statistics |

**Right to be forgotten:** contributors can request removal of their T6
records. The node is tombstoned (content replaced with hash + "removed at
contributor request") — the audit trail remains but the content is gone.
For truly sensitive data, cryptographic erasure (encrypt with key, destroy
key) is available.

---

## 8. GLOBAL ACCESSIBILITY

### 8.1 Multilingual architecture

```
Canonical layer:  knowledge stored in original language + English pivot
Translation layer: NLLB-200 / MADLAD-400 for 200-400 languages
Human layer:      community translations verified by native speakers
```

- **English is the pivot**, not the only language. Every node can exist in
  multiple languages simultaneously.
- **Machine translation is labeled** — `machine_translated: true` until a
  human verifies it.
- **Low-resource languages get priority** — translation effort weighted
  toward languages with least existing digital knowledge.
- **Oral languages:** Whisper transcription + community validation.
- **Indigenous knowledge:** recorded in native language, translated with
  community consent, cultural protocols respected.

### 8.2 Offline & low-bandwidth access

- **PWA with offline cache** — core knowledge available offline.
- **LanceDB embedded** on edge devices — local vector search without server.
- **Delta sync protocol** — `GET /api/v1/sync?since=timestamp` returns only
  changed nodes since last sync. Bandwidth-efficient.
- **Compressed knowledge packs** — domain-specific bundles for offline
  education (e.g., "entire biology curriculum" as a 50MB download).
- **SMS/USSD fallback** for ultra-low-bandwidth regions `[SPEC: not yet
  practical for full archive, but feasible for Q&A interface]`.

### 8.3 Free education mandate

- **All T1-T3 knowledge is free to access, forever.** No paywall.
- **Structured learning paths** — the knowledge hierarchy (Section 2)
  maps directly to curricula. A student can follow `Domain → Discipline →
  ... → Outcome` as a structured course.
- **Open educational resources (OER) integration** — link to and ingest
  existing OER (Khan Academy, MIT OCW, etc.).
- **Multilingual curricula** — the same learning path in 200+ languages.
- **Accessibility** — WCAG 2.2 compliant, screen-reader optimized,
  low-bandwidth mode, text-only mode.

### 8.4 Community contribution model

- **Anyone can contribute** — no gatekeeping for submission.
- **Contribution types:** new nodes, corrections, translations, experience
  records, endorsements, reviews, code (for the platform itself).
- **Contributor rights:**
  - Attribution: every contribution carries author DID.
  - Portability: export your contributions at any time.
  - Governance: contribute to protocol discussions, vote on proposals.
  - Revenue share: if the archive ever generates revenue (donations,
    grants, premium services), contributors to canonical knowledge
    share in it via a transparent formula.
- **Community moderation:** distributed moderation with reputation-weighted
  voting, appeals process, and GOVERNANCE-level override for edge cases.

### 8.5 Anti-capture measures

The archive must be **structurally uncapturable**:

1. **Open-source everything** — code, schemas, protocols, governance docs.
2. **Federated storage** — no single database holds all knowledge.
   IPFS content addressing means even if one node is seized, the content
   persists elsewhere.
3. **Multi-jurisdictional** — nodes operated in multiple legal jurisdictions
   so no single government can shut it down.
4. **Constitutional governance** — the protocol (not any operator) defines
   the rules. Operators are replaceable; the protocol is not.
5. **No surveillance** — the archive does not track users beyond what's
   needed for abuse prevention. No behavioral advertising. No data sale.
6. **Transparent funding** — all funding sources disclosed; no anonymous
   majority funders; no government that censors as majority funder.

---

## 9. DELIVERABLES SUMMARY

| # | Deliverable | Section | Status |
|---|---|---|---|
| 1 | Core mission & 7 knowledge classes | §1 | Design complete |
| 2 | Knowledge hierarchy (11 levels) + graph schema | §2 | Design complete |
| 3 | Verification framework (9 tiers) + contradiction detection + correction | §3 | Design complete |
| 4 | AI knowledge engine (10 capabilities + anti-hallucination) | §4 | Design complete |
| 5 | Experience record schema (12-field canonical) | §5 | Design complete |
| 6 | Technical architecture (stack, schemas, APIs, pipelines) | §6 | Design complete |
| 7 | Security & governance (threat model, access control, reputation) | §7 | Design complete |
| 8 | Global accessibility (multilingual, offline, free education) | §8 | Design complete |
| 9 | Beginner roadmap + prototype spec + expansion plan | §6.8 | Design complete |
| 10 | Technology selection: existing / near-term / speculative | §6.2 | Design complete |

### 9.1 What exists today vs what we build

| Layer | Exists today | We build |
|---|---|---|
| Storage | PostgreSQL, Neo4j, Qdrant, LanceDB, IPFS, S3 | Schema design, federation layer, Merkle integrity |
| AI | LlamaIndex, LangGraph, LightRAG, LLMs, embeddings, Whisper, NLLB | Graph-RAG orchestration, anti-hallucination contract, failure-first retrieval, gap detection |
| Identity | Keycloak, OIDC, DID specs | Reputation system, contribution workflow, governance protocol |
| Frontend | React/Svelte, Tailwind, PWA | Knowledge visualization, graph explorer, learning paths |
| Governance | — | Entire multi-stakeholder governance model |
| Content | arXiv, PubMed, Wikipedia, oral history archives, OER | Ingestion adapters, unification layer, experience record schema |

### 9.2 The one-paragraph pitch

> The Global Human Knowledge and Experience Archive is a federated,
> cryptographically-verifiable, AI-powered knowledge graph that preserves
> everything humanity has discovered, proved, designed, built, tried, and
> failed — with mandatory provenance, tiered verification, failure-first
> retrieval, and governance designed to be structurally uncapturable.
> It begins as a single-domain prototype in SQLite and LanceDB, and
> scales to a planetary institution. Its core innovation is not any single
> technology but the **integration**: experience records with failure
> schemas, a knowledge hierarchy that spans math to mythology, an AI engine
> that refuses to answer without sources, and a governance model that
> makes capture harder than preservation.

---

## 10. OPEN QUESTIONS FOR THE NEXT DESIGN ITERATION

1. **Optimal graph DB at planetary scale** — Neo4j vs FalkorDB vs custom
   sharded property graph? Benchmark needed at >1B edges.
2. **Proof-of-personhood** — how to prevent Sybil attacks without
   excluding the privacy-conscious or the unbanked?
3. **Indigenous knowledge sovereignty** — how to let communities control
   their own knowledge without fragmenting the graph?
4. **AI authorship** — when an AI contributes to the archive (e.g.,
   auto-generated summaries), how is it attributed? Does AI-generated
   content get a different epistemic tier by default?
5. **The ontology problem** — who decides that "tokamak" is a Concept and
   not a Field? Need a governance process for ontology disputes.
6. **Economic sustainability** — how to fund planetary-scale infrastructure
   without compromising independence?
7. **The dark matter of knowledge** — how to ingest and verify knowledge
   that exists only orally, in dead languages, or in physical artifacts
   not yet digitized?
8. **Cross-lingual equivalence** — when a concept doesn't exist in a
   language, do we borrow the term, coin a new one, or describe it?
   (Sapir-Whorf meets knowledge engineering.)

---

*End of specification. This document is itself a knowledge node —
`n:Design:Global-Human-Knowledge-Archive-v1.0` — and should be versioned,
peer-reviewed, and iterated like any other canonical knowledge.*

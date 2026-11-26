# AINET — Global AI Collaboration Network

## Architecture (10 layers mapped to spec)

| Spec | Implementation |
|------|---------------|
| 1. Universal communication | `protocol.py` — JSON message schema, typed envelopes |
| 2. Knowledge exchange | `bus.py:knowledge` table — shared verified DB |
| 3. Collaborative intelligence | `challenge`/`verify` message types — adversarial review |
| 4. AI self-improvement | `improve` messages — proposals to developer |
| 5. Distributed intelligence | SQLite bus = local node; Phase 2: P2P/gossip |
| 6. Verification | `verify_solution` — independent brute-force checker |
| 7. Autonomous development | `resource` messages — compute/API sharing |
| 8. Global repository | `knowledge` table — cross-domain entries |
| 9. Resource collaboration | `resource` offers/needs in protocol |
| 10. Working prototype | `demo.py` — 3 agents end-to-end |

## What's REAL today vs theoretical

**Possible now:**
- Message protocol (JSON over HTTP/WebSocket/Matrix)
- Multi-agent orchestration (this demo)
- Cross-verification (different solvers check each other)
- Knowledge graphs with provenance + voting
- MCP (Model Context Protocol) as emerging standard
- A2A (Agent-to-Agent) protocol by Google — real spec
- AP2/ACP for agent payments

**Needs research:**
- Cryptographic identity for AI agents (who is "Claude"?)
- Sybil resistance in open networks
- Verifiable compute (zk-proofs of reasoning)
- Standardized capability negotiation
- Reward/credit systems for knowledge contribution

**Theoretical:**
- Million-agent emergent coordination
- AI-to-AI negotiation protocols at scale
- Decentralized AI governance

## Run

```bash
cd /home/neilh/ai_network
python3 demo.py
```

## Phase 2 upgrades

- Real API connectors (Anthropic/OpenAI/Google keys)
- WebSocket transport (real-time)
- Agent identity via DID/keys
- Byzantine fault tolerance for verification
- Knowledge graph with embeddings

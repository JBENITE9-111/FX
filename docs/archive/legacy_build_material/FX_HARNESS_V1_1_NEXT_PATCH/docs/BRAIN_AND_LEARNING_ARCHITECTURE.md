# FX Brain + Learning Architecture

## What "see the brain" means

The UI should expose **decision provenance**, not hidden chain-of-thought.

For every request, show:

```text
RUN
├─ Market universe        COMPLETE
├─ Data quality           COMPLETE
├─ Global regime          COMPLETE
├─ Asset selection        COMPLETE
├─ HTF structure          COMPLETE
├─ Location               COMPLETE
├─ Volatility             COMPLETE
├─ Volume                 COMPLETE
├─ Order flow             COMPLETE/WARN
├─ PlayBook match         COMPLETE
├─ Model council          COMPLETE
├─ Historical analogues   COMPLETE
├─ Fraud agent            COMPLETE
├─ Risk officer           BLOCKED/COMPLETE
└─ Final action           NO_TRADE/PAPER/LIVE_PROPOSAL
```

Each node can show:

- deterministic inputs used
- data source and timestamps
- EvidenceItem IDs
- calculated metrics
- model/version IDs
- model vote
- confidence/calibration
- validation status
- assumptions
- vetoes
- plain-English summary
- input/output hashes
- elapsed time

Do not display hidden chain-of-thought tokens.

## Trader decision engine

Use the uploaded trader-analysis hierarchy:

1. Global regime
2. Asset selection / In Play
3. Relative strength
4. Higher-timeframe structure
5. Location
6. Volatility
7. Volume
8. Liquidity / order flow
9. Setup classification
10. Entry trigger
11. Invalidation
12. Reward
13. Expectancy
14. Deterministic position size
15. Trade quality
16. Trade monitoring
17. Post-trade review
18. Learning / PlayBook proposal

This becomes a typed evidence pipeline, not one LLM prompt.

## Continuous learning

FX can observe continuously, but learning is split into four clocks:

### 1-second clock
- ingest quotes/trades/bars where the provider supports it
- data-quality checks
- update streaming features
- record predictions/signals
- update broker/execution telemetry

### minute/hour clock
- recompute richer factors
- detect regime shifts
- update candidate rankings
- retrieve historical analogues

### training clock
- retrain challenger models
- never overwrite champion
- chronological train/OOS/walk-forward
- cost/stress/model-killer tests

### promotion clock
- promotion is an explicit state-machine transition
- paper -> shadow -> micro live -> limited live
- never performed by the streaming learner itself

## TurboVec memory families

Store embeddings for:

- `strategy_memory`
- `failure_memory`
- `trade_memory`
- `regime_memory`
- `research_memory`
- `model_memory`
- `execution_memory`
- `user_decision_memory`

Do not store raw prices as embeddings instead of time-series data.

Recommended hybrid retrieval:

`DuckDB/SQL filter -> candidate memory IDs -> TurboVec allowlist rerank`

Examples:

- same instrument + same timeframe + same regime
- same setup family
- same failure class
- same strategy lineage

## Security

Google Authenticator itself is a TOTP client. FX should implement RFC 6238 server-side and allow the user to scan a QR code into Google Authenticator.

For stronger security later add WebAuthn/passkeys.

Live entry requires:

1. LIVE_TRADING_ENABLED
2. approved deployment manifest
3. fresh data
4. broker reconciliation
5. risk PASS
6. kill switch clear
7. proposal unchanged
8. explicit user approval
9. fresh TOTP
10. execution-service signature validation

Paper trading may run autonomously.

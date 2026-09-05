# FX — Codex next build prompt

Read these first and treat them as authoritative:

1. `/Users/macmac/Documents/Codex/FX/CODEX.md`
2. every Markdown file under `/Users/macmac/Documents/Codex/FX/docs/`
3. the latest FX Full Conversation V2 context
4. the trader-decision-engine analysis

Then inspect the current repository before modifying anything. Reuse working code; do not create duplicate subsystems.

## Objective

Build **FX Harness V1.1: Secure Autonomous Paper Bots + Continuous Market Learning + Observable Brain + Local Vector Memory**.

### Non-negotiable

- Paper bots may scan, decide and execute automatically.
- Live entries may NOT be autonomous.
- Live requires deterministic risk PASS + explicit user approval + fresh TOTP.
- `AI_CAN_EXECUTE_LIVE=false`.
- Do not expose broker secrets to LLM/research processes.
- No withdrawal permissions.
- NO TRADE remains a first-class result.
- Never auto-promote a newly trained model or strategy to live.

## A. Integrate Trader Brain

Implement the 18-layer trader framework as typed pipeline stages:

1. Global Regime
2. In-Play / Asset Selection
3. Relative Strength
4. HTF Structure
5. Location
6. Volatility
7. Volume
8. Liquidity / Order Flow
9. PlayBook Setup
10. Entry Trigger
11. Structural Invalidation
12. Reward / Opposing Pressure
13. Historical Expectancy
14. Deterministic Position Sizing
15. Trade Quality
16. Live/Paper Monitoring
17. Post-Trade Review
18. Learning Proposal

Use the strongest ideas from:
- SMB: catalyst, In Play, PlayBook, tape/liquidity, risk, review
- Rayner: structure -> value -> trigger -> exit
- TraderTV: VWAP, volume, levels, multi-timeframe
- tastylive: distributions/IV/probability/many-small-occurrences for options research
- Cowen: crypto regime, dominance, relative valuation
- Khoo: trend/multi-timeframe/risk-derived sizing
- Steven Hart: define/backtest/optimize/execute
- DataDash: HTF structure + liquidity + volume
- Boyle: risk skepticism/fraud logic
- Plain Bagel: investment fundamentals
- Coin Bureau / Bankless: crypto fundamentals/narratives

No YouTube personality is trusted as a source of edge. Their rules become hypotheses and must pass FX validation.

## B. Brain panel

Add a live right-side `BRAIN` panel.

Show structured run state, not hidden chain-of-thought:
- stages
- tools invoked
- evidence IDs
- data sources
- timestamps
- model votes
- validation status
- assumptions
- vetoes
- risk decision
- elapsed time
- hashes
- next action

Add SSE/WebSocket streaming so the user sees nodes transition:
WAITING -> RUNNING -> COMPLETE/BLOCKED/FAILED.

## C. TurboVec

Install/use `turbovec`.

Build `services/memory/` with:
- IdMapIndex
- stable uint64 IDs
- local persistence
- incremental sync
- metadata sidecar
- allowlist search

Memory types:
- strategy
- failure
- trade
- regime
- research
- model
- execution
- user decision

Use SQL/DuckDB filters first, then TurboVec allowlist reranking.

Never replace Parquet/DuckDB raw market storage with a vector DB.

## D. Continuous market learning

Create a background market-learning worker.

Every second where data permits:
- ingest
- quality check
- normalize
- update online stats/features
- record signals/predictions before outcome
- persist telemetry

Do NOT retrain capital-controlling models every second.

Use scheduled challenger training and validation:
- chronological split
- OOS
- walk-forward
- transaction costs
- parameter sensitivity
- bootstrap/Monte Carlo
- multiple-testing controls
- Model Killer
- paper/shadow evidence

Champion/challenger only.
No silent overwrite.

## E. Security

Do not vendor or depend on the archived `google/google-authenticator` application repository.

Implement standards:
- RFC 6238 TOTP compatible with Google Authenticator
- keychain storage for TOTP server secret
- one-time enrollment QR
- short-lived signed trade approval token
- token bound to exact proposal + risk-decision IDs
- expiry + nonce
- constant-time signature verification

Later architecture placeholder:
- WebAuthn/passkeys

Live approval:
TradeProposal -> RiskDecision PASS -> user clicks approve -> TOTP -> signed approval -> isolated execution service.

## F. Bot modes

Each bot:
- WATCH
- PAPER_AUTO
- SHADOW
- MICRO_LIVE_APPROVAL
- LIMITED_LIVE_APPROVAL

Do not implement autonomous live entry.

Paper bot behavior:
- scheduled scan
- evidence pipeline
- risk gate
- if NO_TRADE: log and stop
- if PAPER_ELIGIBLE: submit to paper broker
- broker-native paper stop/TP where available
- reconcile
- journal
- score outcome

## G. Tests

Add tests proving:
- live blocked when disabled
- live blocked without risk PASS
- live blocked with stale/incorrect approval
- live blocked with modified proposal
- live blocked without TOTP
- AI_CAN_EXECUTE_LIVE=true causes startup failure
- paper automation does not require live approval
- TurboVec memory survives sync/load
- allowlist filters results
- streaming learner does not promote models
- Brain trace contains evidence summaries but no hidden-chain-of-thought field

## H. End result

I should be able to type:

`fx`

then ask:

> Find the strongest opportunity right now.

FX should visibly run the full research graph, return a grounded answer, and either:
- NO TRADE
- PAPER AUTO candidate/execution
- SHADOW candidate
- LIVE PROPOSAL requiring approval

Never fabricate live data or strategy statistics.

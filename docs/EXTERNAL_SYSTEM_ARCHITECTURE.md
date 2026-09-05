# FX External Quant Architecture

## FX Core

Location:

/Users/macmac/Documents/Codex/FX/.venv-core

Responsibilities:

- UI
- chat
- Kimi + Ollama committee
- London Strategic Edge
- canonical data
- strategies
- model council
- validation orchestration
- deterministic risk
- paper proposals
- Mission Control

Never install large unrelated frameworks directly here.

---

## OpenBB

Role:

SECONDARY RESEARCH SERVICE

Use for:

- macro
- SEC
- economics
- fundamentals
- alternative financial providers

Rule:

OpenBB research data is not execution-authoritative.

---

## Backtrader

Role:

INDEPENDENT VALIDATOR

Purpose:

Replay surviving strategies in a second engine to detect implementation errors.

No broker credentials.

---

## Freqtrade Strategy Repository

Role:

STRATEGY GENOME SOURCE

Never trust published performance.

Parse:

- entry conditions
- exit conditions
- indicators
- stop
- ROI
- timeframe
- parameter ranges

Then implement natively inside FX.

---

## MetaTrader Strategy Repository

Role:

FOREX / CFD STRATEGY GENOME SOURCE

Useful examples include:

- Bollinger + RSI
- multiple moving averages
- MACD combinations
- Nadaraya-Watson envelopes
- ATR protection
- COT + trend
- linear-regression methods

Important:

Detect and penalize grid/martingale behavior.

---

## FinRL-X

Role:

REINFORCEMENT-LEARNING LAB

No live authority.

RL experiments must pass the same FX validation protocol as any other strategy.

---

## Obsidian AI

Role:

ARCHITECTURE REFERENCE

Adopt concepts:

- visual workflow DAG
- human-in-the-loop approvals
- streaming workflow status
- execution traces
- agent versioning
- memory
- eval harness
- provider routing

Do not merge the whole project into FX.

---

## Hummingbot

Role:

FUTURE CRYPTO-SPECIALIZED EXECUTION SERVICE

Run in Docker later.

Potential executors:

- directional position
- DCA
- grid
- TWAP
- arbitrage
- cross-exchange market making
- liquidity provision

No HFT in FX V1.

---

## Permanent trust boundary

RESEARCH
MODELS
STRATEGIES
AI
      ↓

DETERMINISTIC RISK

      ↓

HUMAN APPROVAL

      ↓

ISOLATED EXECUTION SERVICE

      ↓

BROKER / EXCHANGE

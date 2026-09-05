# FX — Full Conversation & Project Context
## AI Quantitative Trading Operating System

Project root:

`/Users/macmac/Documents/Codex/FX`

This document consolidates the full visible FX project conversation available in this chat: the user's goals, architecture decisions, installation history, working components, errors encountered, repositories integrated or analyzed, model/training plans, strategy/bot design, UI/UX requirements, risk and execution rules, and the recommended next build.

---

# 1. Project Vision

FX is a personal, local-first AI quantitative trading operating system.

It should feel like:

**ChatGPT**
+
**Bloomberg-style market intelligence**
+
**TradingView-like charts**
+
**quant research laboratory**
+
**strategy factory**
+
**multi-agent orchestration**
+
**portfolio/risk engine**
+
**paper/live Mission Control**
+
**isolated institutional-style execution**

The goal is not a “magic profit bot.”

The goal is a reproducible system that can search, test, validate, reject, deploy, monitor, explain, pause, replace, and audit strategies.

The safest valid conclusion is often:

**NO TRADE**

---

# 2. User Interaction Requirements

The user does not code.

All user-facing instructions, labels, explanations, status messages, and workflows should be written in plain English.

FX should answer natural-language questions such as:

- What is the best stock right now?
- What is the strongest BTC setup?
- Why Apple instead of Nvidia?
- Compare Apple and Nvidia.
- How is gold behaving?
- What model is being used?
- Show me what the strategy is seeing.
- Show me Fibonacci levels.
- Show me moving averages.
- Show me trend lines.
- Show me support and resistance.
- Show me where you would enter.
- What invalidates the trade?
- Show me historical analogues.
- Compare the forecast against what actually happened.
- Which strategies are degrading?
- How are my bots doing?
- What stocks or pairs are the bots watching?
- Which bot is making money?
- Paper trade this if price reaches X.
- Explain why a trade was rejected.
- Train all the brains.
- Find the strongest opportunity globally.

The AI must answer from real data and calculated evidence, never fabricated numbers.

---

# 3. Permanent Core Principle

> **Data provides facts. Models produce evidence. Python calculates. The LLM explains. The risk engine controls capital. You authorize execution.**

Also:

> **AI proposes. Deterministic software measures. Risk controls approve or reject. Human authorizes live entry. Broker/execution engine manages approved protective orders.**

---

# 4. Capital and Broker Model

FX never holds the user’s money.

Capital remains at the broker or exchange.

User funds
↓
Broker / Exchange
↓
Broker API
↓
FX Execution Service
↑
Deterministic Risk Engine
↑
Human Approval
↑
FX AI / Quant Models

FX may read:

- equity
- cash
- buying power
- margin state
- positions
- orders
- fills
- PnL
- broker status

FX is not a wallet or custodian.

---

# 5. Live Trading Safety

Human approval is mandatory before any new live entry.

AI may:

- research
- forecast
- propose
- explain
- create paper orders
- prepare live TradeProposals

AI may not:

- silently place live entries
- change risk limits
- increase leverage on its own
- disable kill switches
- access or reveal broker secrets
- withdraw funds
- fabricate approval
- silently promote paper to live

Broker-native protective orders are preferred:

- stop-loss
- take-profit
- bracket
- OCO
- OTO
- reduce-only protection

---

# 6. Operational Modes

MODE 0 — RESEARCH  
MODE 1 — BACKTEST  
MODE 2 — PAPER  
MODE 3 — SHADOW LIVE  
MODE 4 — MICRO LIVE  
MODE 5 — LIMITED LIVE  
MODE 6 — APPROVED LIVE

Live is not a simple ON/OFF toggle.

---

# 7. Strategy / Model Lifecycle

Models and strategies must earn promotion.

Typical lifecycle:

EXPERIMENTAL
↓
TRAINED
↓
BACKTESTED
↓
OOS_PASSED
↓
WALK_FORWARD_PASSED
↓
STRESS_PASSED
↓
PAPER
↓
SHADOW_LIVE
↓
LIMITED_LIVE
↓
APPROVED

Strategy lifecycle:

RESEARCH
↓
CANDIDATE
↓
OOS_VALIDATED
↓
ROBUSTNESS_VALIDATED
↓
VAULT
↓
PAPER
↓
SHADOW
↓
MICRO_LIVE
↓
LIMITED_LIVE
↓
APPROVED

Regression is allowed:

APPROVED
↓
DEGRADED
↓
SUSPENDED
↓
RETIRED

No strategy can jump directly from generated/research to live.

---

# 8. Hardware Constraint

The user’s Mac is Intel x86_64.

This caused compatibility problems with:

- VectorBT
- Numba
- llvmlite
- LLVM
- NautilusTrader native macOS build

Decision:

Do not force every framework into `.venv-core`.

Use isolated environments and Docker/Linux services where appropriate.

---

# 9. Main Architecture

MARKET SOURCES
↓
DATA NORMALIZER
↓
RAW immutable Parquet
↓
DuckDB / Feature Store
↓
MODELS / STRATEGIES
↓
MODEL COUNCIL
↓
SCREENING
↓
OOS / WALK-FORWARD / STRESS
↓
HISTORICAL / MODEL MEMORY
↓
KIMI + OLLAMA / MULTI-AGENT REASONING
↓
FRAUD / RED TEAM / RISK
↓
CandidateSetup / SignalIntent
↓
DETERMINISTIC RISK ENGINE
↓
USER APPROVAL
↓
PAPER / SHADOW / LIVE-GATED EXECUTION
↓
BROKER
↓
JOURNAL / AUDIT / MISSION CONTROL

---

# 10. London Strategic Edge

LSE is the primary research data backbone.

Connected and verified in the user’s terminal logs.

Verified:

- API key detected
- market catalog reachable
- 3,982 stock instruments available
- 22,851 total discovered market/data series
- AAPL historical candles working
- EUR/USD historical candles working
- BTC/USD historical candles working
- XAU/USD historical candles working
- global search across stocks, FX, crypto, commodities, indices and futures

Use LSE for research data.

Permanent rule:

**RESEARCH DATA != EXECUTION DATA**

Broker or venue feeds are authoritative for real execution.

---

# 11. Alpaca Paper

Alpaca Paper is connected.

Verified paper state:

- cash: $100,000
- account value: $100,000
- buying power: $400,000

Use:

- paper account state
- positions
- paper orders
- paper execution after approval

Real-money Alpaca execution remains disabled.

---

# 12. OpenBB

Installed in an isolated environment:

`external/openbb/.venv`

Installed package:

`openbb==4.7.2`

Installed provider capabilities include:

- Benzinga
- BLS
- CFTC
- commodity
- Congress.gov
- crypto
- currency
- derivatives
- EconDB
- economy
- equity
- ETF
- Federal Reserve
- fixed income
- FMP
- FRED
- Government US
- IMF
- index
- Intrinio
- news
- OECD
- regulators
- SEC
- Tiingo
- Trading Economics
- US EIA
- yfinance

Role:

**SECONDARY RESEARCH DATA SERVICE**

Not execution authority.

---

# 13. Storage

Use:

- Parquet
- DuckDB
- Redis / Redis Streams

Suggested structure:

data/
  raw/
    lse/
  normalized/
  features/
  holdout/
  predictions/
  journal/

Benefits:

- reproducibility
- lower API usage
- fast research
- local-first operation
- auditable training
- point-in-time replay

---

# 14. Data Quality Gate

Before models or strategies run, validate:

- timestamps
- continuity
- duplicates
- missing bars
- outliers
- timezone
- symbol mapping
- corporate actions
- venue mapping
- spread validity
- stale data

States:

PASS  
WARN  
BLOCK

If BLOCK:

**MODEL EXECUTION BLOCKED**

---

# 15. Canonical Instrument Registry

Need a canonical instrument schema because providers differ.

Example fields:

- canonical_id
- asset_class
- base
- quote
- provider
- provider_symbol
- venue
- currency
- timezone
- tick_size
- lot_size

The LLM must never guess symbol mappings.

---

# 16. Local AI

Ollama is installed.

Models observed in the logs include:

- qwen2.5-coder:7b
- deepseek-coder:6.7b
- qwen3-coder
- qwen3:8b
- qwen3:4b
- qwen3:1.7b

Final lightweight local reviewer:

`qwen3:1.7b`

Reason:

- smaller
- faster
- better fit for Intel Mac background critic/reviewer tasks

---

# 17. Kimi + Ollama Committee

Kimi is accessed through OpenRouter.

Configured model:

`moonshotai/kimi-k2.6:free`

Roles:

## Kimi
Lead Analyst / Chairman

- interpret structured evidence
- compare markets
- explain opportunity
- synthesize final answer

## Ollama
Independent Local Risk Critic

- challenge Kimi
- find missing evidence
- identify weak assumptions
- argue NO TRADE when warranted
- flag overconfidence

Flow:

REAL FX EVIDENCE
↓
Kimi Lead Analyst
+
Ollama Risk Critic
↓
Kimi Chairman
↓
FINAL FX RESPONSE

LLMs do not manufacture market truth.

---

# 18. Models

Current / planned brains include:

## Deterministic/statistical
- Trend
- Momentum
- Breakout
- Mean Reversion
- RSI Reversion
- MACD Trend
- Kalman Trend
- Regime / HMM

## Machine learning
- Logistic Regression
- Random Forest
- LightGBM
- XGBoost
- CatBoost

## Foundation forecast
- Kronos

## Later / planned
- Historical Analogue Engine
- Macro Model
- PCA factor/regime
- Qlib lab
- FinRL-X lab

---

# 19. Training Center

A Model Training Center was installed.

Training logic:

- real LSE history
- feature generation
- chronological train/test split
- model training
- unseen-data evaluation
- walk-forward testing
- artifact storage
- model registry

Features include:

- ret1
- ret3
- ret5
- ret10
- ret20
- vol5
- vol20
- EMA gaps
- RSI14
- ATR percentage
- range percentage
- close location
- volume change

Trainable models:

- Logistic Regression
- Random Forest
- LightGBM
- XGBoost
- CatBoost

Statuses include:

- TRAINED · OOS FAILED
- OOS PASSED · WALK-FORWARD FAILED
- WALK_FORWARD_PASSED

Training does not automatically grant paper/live status.

---

# 20. Kronos

Kronos has its own environment:

`.venv-kronos`

Recommended use:

Pretrained Kronos
↓
LSE OHLCV
↓
forecast
↓
save forecast before future happens
↓
wait
↓
compare prediction vs reality
↓
calibrate by:
- asset
- timeframe
- regime
- horizon

Track:

- directional accuracy
- path error
- uncertainty band coverage
- regime-specific reliability

---

# 21. Current Strategy Engine

Real strategy analysis was connected to LSE.

Verified AAPL historical tests from terminal logs:

- trend_following: current position 1, historical return -2.84%
- momentum: current position 1, historical return -75.18%
- breakout: current position 0, historical return -53.05%
- mean_reversion: current position -1, historical return 86.3%
- rsi_reversion: current position 0, historical return 128.35%
- macd_trend: current position 1, historical return -77.98%
- kalman_trend: current position 1, historical return -25.46%

These mixed results demonstrate why validation is mandatory.

---

# 22. Strategy Library

Existing strategy families:

- Trend Following
- Momentum
- Breakout
- Mean Reversion
- Bollinger Mean Reversion
- RSI Reversion
- MACD Trend
- Volatility Breakout
- Kalman Trend
- Pairs Trading
- Cross-Sectional Momentum
- Regime-Aware Trend
- Carry
- Institutional Positioning
- Activist Event
- Options Volatility

Goal:

Every strategy should become an interactive strategy workbench with:

- logic
- market
- timeframe
- current signal
- historical metrics
- OOS
- walk-forward
- stress
- model council
- paper eligibility
- deployment status

---

# 23. Paper Trade Flow

Strategy analysis
↓
Trade Proposal
↓
Review:
- instrument
- side
- entry
- quantity
- stop
- target
- max planned loss
↓
User approves
↓
Alpaca Paper

No real money is used.

---

# 24. Unified Trading Terminal

A unified terminal was installed.

Features added:

- persistent Ask FX chat
- background Kimi + Ollama work
- background training
- visible Training Center
- Bot Monitor
- Paper Portfolio
- market search
- market chart
- timeframes
- EMA20
- EMA50
- trend overlay
- support/resistance
- Fibonacci
- market tabs
- paper equity/PnL summary

Launcher:

Open Terminal and type:

`fx`

---

# 25. Chat Must Persist

If the user asks FX something and then changes market or page, the analysis must continue.

Example:

EURJPY analysis — RUNNING  
BTC analysis — RUNNING  
Model Training — RUNNING  
Gold validation — COMPLETE

Background tasks must be independent of navigation.

---

# 26. Chart Requirements

Target is TradingView-like.

Need:

- candles
- zoom/pan
- crosshair
- multiple timeframes
- volume
- EMA
- SMA
- RSI
- MACD
- ATR
- Bollinger
- VWAP
- trendlines
- support/resistance
- Fibonacci
- zones
- entry/stop/targets
- fills
- model signals
- Kronos forecast
- forecast bands
- historical analogues
- news markers
- macro markers
- model disagreement

Modes:

CLEAN  
STRATEGY  
RESEARCH

Exploratory overlays must not be falsely presented as strategy evidence.

---

# 27. Bot Monitor

Current bot families:

- Global Equity Scanner
- Forex Scanner
- Crypto Scanner
- Gold Bot

Desired bot screen:

- name
- market
- timeframe
- strategy
- models
- status
- mode
- watchlist
- current candidates
- equity
- PnL
- trades
- drawdown
- health
- last signal
- next action

Controls:

- Scan Now
- Start
- Stop
- Pause
- Revalidate
- Find Replacement
- Deploy to Paper

---

# 28. Bot Lifecycle

WATCH
↓
PAPER — APPROVAL REQUIRED
↓
PAPER — AUTO EXECUTE
↓
SHADOW LIVE
↓
MICRO LIVE — APPROVAL REQUIRED
↓
LIMITED LIVE
↓
APPROVED LIVE

---

# 29. Mission Control

Planned top-level system monitor.

Status:

ALL CLEAR  
or  
ATTENTION REQUIRED

Metrics:

- Floating P&L
- Realized P&L
- Portfolio drawdown
- Open positions
- Gross exposure
- Net exposure
- Risk used
- Broker sync
- Data quality

Per-system states:

- ON TRACK
- WATCH
- DEGRADED
- SUSPENDED

Controls:

- PAUSE NEW ENTRIES
- FLATTEN
- REVALIDATE
- FIND REPLACEMENT
- SUSPEND
- RETIRE

---

# 30. Strategy Health / Drift

Monitor:

- return drift
- win-rate drift
- loss-severity drift
- trade-frequency drift
- holding-time drift
- volatility drift
- slippage drift
- drawdown drift
- model calibration drift
- feature-distribution drift
- regime mismatch

---

# 31. Riskfolio-Lib

Installed safely without forcing VectorBT.

Verified capabilities:

- portfolio optimization
- risk contribution
- CVaR
- drawdown risk
- hierarchical risk parity
- Black-Litterman
- portfolio constraints

---

# 32. VectorBT

Deferred due Intel Mac dependency chain:

Riskfolio → VectorBT → Numba → llvmlite → LLVM

Possible later environments:

- isolated Conda
- Docker/Linux
- remote Linux worker

Use as a fast screening layer, not final execution evidence.

---

# 33. NautilusTrader

Native installation failed on Intel macOS.

Decision:

Run later in Docker/Linux.

Architecture:

Intel Mac
↓
Docker Desktop
↓
Ubuntu x86_64
↓
Python 3.12
↓
NautilusTrader

Role:

- realistic event-driven simulation
- order lifecycle
- fills
- partial fills
- broker adapters
- protective orders
- reconciliation

---

# 34. Backtrader

Installed separately:

`external/backtrader/.venv`

Version:

`1.9.78.123`

Role:

Independent validator.

No broker credentials.

---

# 35. External Quant Stack

Installed/cloned:

- OpenBB
- Backtrader
- Freqtrade Strategies
- geraked MetaTrader 5 strategies
- FinRL-X
- Obsidian AI
- Hummingbot

Also previously cloned / installed for research:

- TradingAgents
- Vibe-Trading
- AI-Trader
- Python Quant Trading
- TradeMaster
- QuantMuse
- Howtrader
- BEmu
- Kronos

---

# 36. External Strategy Intake Policy

Every external strategy begins as:

`EXTERNAL_UNTRUSTED`

Required pipeline:

SOURCE SNAPSHOT
↓
SOURCE HASH
↓
LICENSE RECORD
↓
STRATEGY DNA
↓
MECHANISM
↓
GRID / MARTINGALE DETECTOR
↓
LOOK-AHEAD AUDIT
↓
NATIVE FX IMPLEMENTATION
↓
RESEARCH CONTRACT
↓
TRAIN DATA
↓
OUT-OF-SAMPLE
↓
WALK-FORWARD
↓
PARAMETER SENSITIVITY
↓
TRANSACTION COST STRESS
↓
BOOTSTRAP
↓
MONTE CARLO
↓
MODEL KILLER
↓
INDEPENDENT REPLAY
↓
VAULT
↓
PAPER
↓
SHADOW
↓
LIVE PROMOTION GATE

---

# 37. Freqtrade

Use as strategy genome source.

Extract:

- entry rules
- exit rules
- indicators
- stop-loss
- ROI schedules
- trailing stops
- timeframe
- parameters

Published performance is not trusted.

---

# 38. MetaTrader Strategy DNA

Useful ideas found:

- Chandelier Exit + ZLSMA + Heikin Ashi
- 3 MA + Williams Fractals
- Bollinger + RSI
- Daily High/Low + Andean Oscillator
- multi-MACD
- MACD + Stochastic
- MA + Andean Oscillator
- Nadaraya-Watson Envelope + RSI + ATR
- Linear Regression + UT Bot
- COT + SuperTrend

Need permanent grid/martingale detection.

---

# 39. Hummingbot

Stored as reference for future crypto-specialized execution.

Potential executor patterns:

- Position Executor
- DCA
- TWAP
- Grid
- Arbitrage
- Cross-exchange market making
- Liquidity provision

No HFT in V1.

---

# 40. FinRL-X

Research lab only.

Use for:

- reinforcement-learning policy research
- allocation experiments
- execution experiments

No direct live authority.

---

# 41. Obsidian AI

Cloned at:

`vendor/reference/obsidian-ai`

Best features to harness:

- visual agent workflows
- multi-provider LLM support
- configurable agents
- multi-agent teams
- parallel DAG execution
- live node status
- SSE streaming
- human-in-the-loop approvals
- tool visualization
- MCP
- long-term memory
- agent versioning
- eval harness
- scheduled workflows
- secrets vault
- execution traces
- Docker sandbox

FX should absorb these architectural ideas rather than replacing FX with Obsidian.

---

# 42. FX Harness V1

Recommended next major build.

Purpose:

Connect everything into one coherent orchestration system.

USER REQUEST
↓
FX HARNESS
↓
ResearchRun
↓
DATA
↓
DATA QUALITY
↓
parallel:
- models
- macro
- analogues
↓
MODEL COUNCIL
↓
parallel:
- Kimi Lead Analyst
- Ollama Risk Critic
↓
Fraud Agent
↓
Risk Officer
↓
Opportunity Object
↓
Research / Paper / Live eligibility

Everything logged.

---

# 43. Proposed Agent Team

## Market Scout
Finds candidates.

## Data Quality Agent
Checks timestamps, freshness, provider conflicts.

## Quant Agent
Combines deterministic and ML evidence.

## Macro Agent
Uses LSE/OpenBB macro evidence.

## Technical Agent
Explains calculated chart/indicator state.

## Historical Analogue Agent
Finds similar historical situations.

## Bull Analyst
Builds strongest positive case.

## Bear Analyst
Builds strongest negative case.

## Fraud Agent
Assumes the opportunity is fake until proven otherwise.

Checks:

- leakage
- stale data
- overfit
- small sample
- survivorship
- suspicious Sharpe
- grid/martingale
- regime mismatch

## Risk Officer
Can veto the opportunity.

Possible outputs:

- NO_TRADE
- RESEARCH_ONLY
- PAPER_ELIGIBLE
- SHADOW_ELIGIBLE
- LIVE_PROPOSAL_ALLOWED

Position sizing remains deterministic.

---

# 44. Typed Agent Outputs

Scout
→ CandidateSet.json

Researcher
→ EvidenceBundle.json

Quant
→ ModelEvaluation.json

Validator
→ ValidationReport.json

Fraud
→ AdversarialReview.json

Risk
→ RiskDecision.json

Final
→ Opportunity.json

---

# 45. Visual Agent Workflow

Instead of only:

“Thinking…”

FX should show live workflow state:

Market Universe — COMPLETE  
Data Quality — COMPLETE  
Trend — COMPLETE  
Momentum — COMPLETE  
LightGBM — RUNNING  
XGBoost — COMPLETE  
CatBoost — RUNNING  
Kronos — RUNNING  
Macro — COMPLETE  
Bull Analyst — WAITING  
Bear Analyst — WAITING  
Fraud Agent — WAITING  
Risk Officer — WAITING

The user can click completed nodes and inspect structured evidence.

---

# 46. Human Approval Gate

Borrow the Human-in-the-Loop concept.

Example:

TRADE PROPOSAL

EUR/JPY  
SELL

Entry  
...

Stop  
...

Targets  
...

Risk  
...

Strategy  
...

Validation  
PASS

Model Council  
6/8 bearish

Risk Officer  
APPROVED FOR PAPER

Buttons:

REJECT  
APPROVE PAPER TRADE

Workflow pauses until user action.

Later the same pattern applies to live.

---

# 47. Tool System

Market tools:

- search_markets()
- get_quote()
- get_candles()
- get_order_book()

Quant tools:

- calculate_rsi()
- calculate_atr()
- calculate_ema()
- calculate_macd()
- calculate_volatility()
- calculate_support_resistance()
- calculate_fibonacci()

Model tools:

- run_lightgbm()
- run_xgboost()
- run_catboost()
- run_kronos()
- run_model_council()

Strategy tools:

- backtest_strategy()
- walk_forward()
- stress_test()
- model_killer()
- compare_strategies()

Portfolio tools:

- portfolio_exposure()
- strategy_correlation()
- risk_budget()
- position_size()

Broker tools:

- paper_account()
- paper_positions()
- paper_orders()

Execution:

- submit_approved_trade()

There should never be a generic direct LLM tool like `buy_aapl()`.

---

# 48. FX Memory

Instrument memory should store measurable history.

Example:

EURJPY

- last signal
- similar historical setups
- model forecasts
- forecast outcomes
- strategy failures
- paper trades
- regime history

Model memory:

LightGBM

XAUUSD 4H — OOS AUC ...
BTCUSD 1H — FAILED
EURJPY 1H — OOS AUC ...

---

# 49. Agent Evaluation

Evaluate the AI layer itself.

Example question:

“What is the strongest stock?”

Required:

- used real data
- did not fabricate price
- cited evidence
- explained uncertainty
- allowed NO_TRADE
- did not size arbitrarily
- did not bypass risk
- separated fact from interpretation

---

# 50. Agent Versioning

Every agent config should be versioned.

Example:

Risk Agent v3.4
Risk Agent v3.5

Every trade stores:

- analysis_agent_version
- risk_agent_version
- model_versions
- strategy_version
- dataset version
- evidence IDs

---

# 51. Scheduled Workflows

Example:

GLOBAL MARKET SCANNER

every 15 minutes
↓
stocks
FX
crypto
commodities
↓
model council
↓
strategy filter
↓
Fraud Agent
↓
Risk
↓
weak → NO ACTION
interesting → Opportunity
validated Paper → Paper Proposal

---

# 52. Five Core Workflows

## Ask FX
question
→ evidence
→ Kimi
→ Ollama
→ answer

## Find Best Opportunity
global scanner
→ model council
→ strategy
→ red team
→ risk
→ ranked candidates

## Train Models
data
→ training
→ OOS
→ walk-forward
→ stress
→ registry

## Build Strategy
strategy source
→ Strategy DNA
→ mutation
→ backtest
→ holdout
→ Model Killer
→ Vault

## Bot Cycle
scan
→ candidate
→ evidence
→ risk
→ Paper proposal
→ monitor
→ journal

---

# 53. Strategy Factory

Input sources:

- Native FX
- Freqtrade
- MetaTrader
- Papers With Backtest
- Python Quant Trading
- Vibe-Trading
- AI-Trader
- TradingAgents
- Hummingbot ideas
- academic papers
- manual user ideas

Pipeline:

Source
↓
hash
↓
parser
↓
Strategy DNA
↓
mechanism
↓
grid/martingale detector
↓
native implementation
↓
preregistered campaign
↓
locked holdout
↓
OOS
↓
walk-forward
↓
cost stress
↓
Monte Carlo
↓
Model Killer
↓
Backtrader
↓
Strategy Vault
↓
Paper deployment

---

# 54. Campaign Engine

Example request:

“Find robust XAUUSD strategies on H1 and H4 with max historical drawdown below 12%.”

Campaign fields:

- Campaign ID
- Markets
- Timeframes
- Objective
- Drawdown limit
- Minimum trades
- Train period
- Validation period
- Locked holdout
- Allowed families
- Maximum strategies
- Maximum rounds
- Allowed parameters
- Cost model
- Success criteria

---

# 55. Preregistration

Create immutable ResearchContract before running research.

Fields:

- hypothesis
- economic mechanism
- universe
- dataset
- start
- end
- holdout
- timeframe
- cost model
- signal definition
- target definition
- metrics
- success thresholds
- failure thresholds
- parameter space
- maximum experiments
- created_at
- hash

After research begins:

IMMUTABLE

---

# 56. Locked Holdout

Suggested split:

Research:
70–80%

Locked holdout:
20–30%

Only validation service can read holdout.

Store SHA256 holdout hash.

If holdout influences strategy edits, retire it.

---

# 57. Model Killer

Adversarial validator.

Tests:

- different regimes
- different assets
- different periods
- fees ×2
- slippage ×3
- delayed entry
- missing data
- parameter perturbation
- bootstrap
- Monte Carlo
- label permutation
- leakage
- survivorship
- timezone shifts
- spread shocks
- partial fills
- rejected orders
- flash moves
- disconnects
- API outages

Only survivors continue.

---

# 58. Multiple Testing

Track:

- strategies generated
- strategies tested
- parameter variants
- models tested
- rounds
- revisions

Possible corrections:

- Bonferroni
- Holm-Bonferroni
- False Discovery Rate
- Deflated Sharpe
- Probability of Backtest Overfitting
- reality-check methods

The more experiments run, the stricter acceptance becomes.

---

# 59. Strategy Vault

Every strategy gets a passport.

Example fields:

- strategy ID
- asset
- timeframe
- family
- parents
- generation
- campaign
- dataset
- strategy hash
- CAGR
- Sharpe
- Sortino
- Calmar
- Max DD
- Profit factor
- Win rate
- Trades
- Turnover
- Fees
- Slippage
- IS/OOS/WF/Monte Carlo/sensitivity/leakage/multiple-testing/replay results
- Paper trades
- Shadow signals
- live evidence
- status

---

# 60. Failure Memory

Failed strategies are preserved.

Store:

- strategy
- failure reason
- regime
- dataset
- validation failure
- hash
- date
- similarity fingerprint

If a new strategy resembles a failed one, show that history.

---

# 61. Portfolio / Risk

Use:

- skfolio
- Riskfolio-Lib

Only after individual strategies are validated.

Evaluate:

- return correlation
- signal correlation
- position overlap
- factor exposure
- asset exposure
- macro overlap
- tail dependence
- drawdown overlap

Never use portfolio optimization to rescue weak strategies.

---

# 62. Economic Event Guards

Support deterministic guards around events such as:

- FOMC
- NFP
- CPI
- PCE
- major central-bank events

Example:

No new FX/gold entries 15 minutes before/after configured events.

---

# 63. Execution Parity

Measure rather than assume:

- expected entry vs fill
- expected fee vs actual
- expected slippage vs actual
- expected latency vs actual
- expected stop vs actual
- expected exit vs actual

Create:

ExecutionParityScore

If parity degrades:

LIVE PROMOTION BLOCKED  
or  
STRATEGY WATCH

---

# 64. Journal / Ledger

Store every recommendation, including rejected ones.

Classes:

1. suggested → traded → won
2. suggested → traded → lost
3. suggested → rejected → would have won
4. suggested → rejected → would have lost

Measure separately:

- model quality
- strategy quality
- AI quality
- human approval quality
- risk quality
- execution quality

---

# 65. Execution Ledger

Store:

- trade_id
- strategy_id
- model_version
- campaign_id
- symbol
- venue
- side
- proposal_time
- approval_time
- submit_time
- ack_time
- fill_time
- close_time
- expected_entry
- actual_fill
- expected_slippage
- actual_slippage
- size
- risk_budget
- stop
- take_profit
- PnL
- fees
- MAE
- MFE
- exit_reason

---

# 66. Cryptographic Provenance

Eventually compute:

- strategy_hash
- model_hash
- dataset_hash
- prediction_hash
- approval_hash
- order_hash

Every live trade should be attributable to exact data, model, strategy, approval, and execution.

---

# 67. Least-Privilege Identities

Example:

agent:researcher
- READ market data
- WRITE research
- NO broker access

agent:quant
- READ features
- WRITE model evaluations
- NO broker secrets

service:risk
- READ proposals/portfolio
- WRITE risk decisions
- NO broker secrets

service:execution
- READ approved TradeIntent
- READ broker secret
- WRITE broker orders
- NO LLM access

---

# 68. Credentials

Important credentials:

- LSE_API_KEY
- ALPACA_PAPER_KEY
- ALPACA_PAPER_SECRET
- OPENROUTER_API_KEY
- HF_TOKEN
- KIMI_API_KEY
- BINANCE_TESTNET_API_KEY
- BINANCE_TESTNET_API_SECRET
- IBKR later

Never paste secrets into chat.

One OpenRouter key was exposed in logs; it should be revoked and replaced.

---

# 69. UI / UX Direction

Design target:

Cursor + Vercel + Linear + institutional trading terminal.

Rules:

- dark-first
- monochrome/high contrast
- Geist Sans
- Geist Mono
- tabular numerals
- 1px borders
- grid layout
- dense but readable
- keyboard-first
- Cmd+K
- no gradients
- no neon
- no robot imagery
- no generic crypto clichés

---

# 70. Desired Navigation

Chat

Markets
- Global Markets
- Stocks
- Forex
- Crypto
- Commodities
- ETFs
- Indices
- Futures
- Options

Intelligence
- Agent Team
- Models
- Training
- Strategy Factory
- Research Runs
- Hedge Fund Intelligence
- OpenBB Intelligence

Automation
- Bots
- Opportunities
- Trade Proposals
- Paper Trading

Monitor
- Mission Control
- Background Tasks
- Agent Runs
- Model Health
- Strategy Health

Records
- Journal
- Evidence
- Strategy Vault
- Audit Log

Risk
Settings

---

# 71. Target User Experience

User asks:

“What is the strongest opportunity right now?”

FX should:

1. screen markets
2. verify data
3. identify regime
4. run models
5. run ML
6. run Kronos where appropriate
7. retrieve analogues
8. inspect macro/fundamentals/options
9. select strategy
10. validate
11. red-team the thesis
12. check portfolio impact
13. calculate risk
14. display strategy evidence on chart
15. explain disagreement
16. return NO TRADE if weak
17. allow paper proposal
18. create live proposal only if eligible
19. require human approval
20. execute through isolated service
21. confirm protection
22. reconcile broker
23. monitor in Mission Control
24. detect drift
25. revalidate
26. propose replacements
27. journal everything

---

# 72. Current Status

## Working / Installed

- FX launcher command
- FastAPI backend
- unified trading terminal
- LSE real market data
- 22,851 discovered market/data series
- global search
- Alpaca Paper
- deterministic strategies
- strategy workbench
- model council
- LightGBM
- XGBoost
- CatBoost
- Random Forest
- Logistic Regression
- Kalman
- HMM / regime
- Kronos isolated environment
- Kimi via OpenRouter
- Ollama local
- Kimi + Ollama committee
- Training Center
- background training
- Bot Monitor
- Paper Portfolio
- Riskfolio-Lib
- skfolio
- OpenBB isolated environment
- Backtrader isolated validator
- Freqtrade strategy source
- MetaTrader strategy source
- FinRL-X
- Obsidian AI reference
- Hummingbot reference
- TradingAgents
- Vibe-Trading
- AI-Trader
- Python Quant Trading
- TradeMaster
- QuantMuse
- Howtrader
- BEmu reference
- Strategy Source Registry
- External Systems Registry

## Deferred

- VectorBT native
- Nautilus native
- Hummingbot execution
- MetaTrader live bridge
- FinRL live authority
- grid live trading
- market making
- arbitrage
- IBKR
- Mission Control full build
- Strategy Factory full build
- Model Killer full build
- Strategy Vault full build
- FX Harness full build

---

# 73. Recommended Next Build

The highest-value next build is:

# **FX Harness V1**

It should connect:

- LSE
- OpenBB
- deterministic models
- ML models
- Kronos
- strategies
- training
- bots
- Kimi
- Ollama
- historical memory
- validation
- Fraud Agent
- Risk Officer
- background jobs
- human approvals
- Strategy Factory
- Paper execution
- Mission Control

into one observable workflow system.

---

# 74. Master Codex Policy

Put these permanently into `CODEX.md`:

> A model is not trusted because it is sophisticated, popular, recently trained, generated by an LLM, published in a paper, profitable in a backtest, or recommended by another AI. Trust is earned only through reproducible evidence under FX's validation protocol.

> The safest valid trading decision is frequently NO TRADE. FX is explicitly rewarded for refusing weak opportunities.

> No model, agent, generated strategy, research framework, frontend process, or general backend service possesses broker credentials or broker authority. Only the isolated execution service may access broker credentials, and only after deterministic risk validation plus explicit human authorization for live entry.

> Research facts, calculated metrics, model outputs, AI interpretations, and assumptions are different evidence classes.

> Holdout datasets are physically isolated from research agents.

> Failed strategies are preserved.

> Every model, strategy, prediction, approval, order, fill, and reconciliation event is versioned and attributable.

> Execution parity is measured, not guaranteed.

> External strategies always begin as EXTERNAL_UNTRUSTED.

> Complex models must beat simple baselines before earning trust.

---

# 75. Final Product Statement

FX should not become a pile of bots or a single giant AI agent.

It should become a disciplined fleet of validated systems under one AI-assisted operating layer.

The correct hierarchy remains:

DATA
↓
QUALITY
↓
FEATURES
↓
MODELS
↓
STRATEGIES
↓
VALIDATION
↓
EVIDENCE
↓
RED TEAM
↓
RISK
↓
AI EXPLANATION
↓
HUMAN APPROVAL
↓
EXECUTION SERVICE
↓
BROKER

That is the core of the FX project.

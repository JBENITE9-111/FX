# FX COMPLETE CONVERSATION CONTEXT
## Codex Handoff Compilation

**Permanent root:** `/Users/macmac/Documents/Codex/FX`

This document compiles the major decisions and development history from the FX project conversation.

## Vision

The user wants a local-first, multi-asset AI quantitative trading application combining professional market data, charting, research, strategies, bots, AI agents, risk, paper execution, journaling, continuous learning, and eventually tightly controlled live trading.

The desired product should feel like a powerful “money machine,” but explicitly not like a gambling casino. The operating interpretation is disciplined compounding through validated edge and bounded risk, never guaranteed profit.

## Primary operating law

```text
Data provides facts.
Models provide evidence.
Python calculates.
LLM explains.
Risk Engine controls capital.
Human authorizes live entry.
```

`NO_TRADE` is desirable whenever evidence is insufficient.

## Core architecture

```text
DATA
→ QUALITY
→ MARKET INTELLIGENCE
→ REGIME
→ ASSET SELECTION
→ MULTI-TIMEFRAME STRUCTURE
→ FEATURES
→ MODELS
→ STRATEGIES
→ VALIDATION
→ HISTORICAL EVIDENCE
→ COUNTER-THESIS
→ META DECISION
→ PORTFOLIO
→ DETERMINISTIC RISK
→ PAPER / SHADOW / LIVE PROPOSAL
→ EXECUTION
→ RECONCILIATION
→ MISSION CONTROL
→ JOURNAL
→ LEARNING
```

## Data and tools

London Strategic Edge became the primary research-data backbone. Project logs previously showed thousands of instruments and multi-asset historical access including AAPL, EURUSD, BTCUSD, and XAUUSD.

Alpaca Paper was connected earlier, but the user later made the explicit decision that bot paper execution should happen locally on the Mac rather than depend on Alpaca. Alpaca can remain for independent execution-parity testing.

OpenBB, Backtrader, Riskfolio-Lib, Kronos, Kimi/OpenRouter, and Ollama are important parts of the broader research stack.

## External repositories and architectural research

The project examined or referenced strategy/research repos including Freqtrade strategies, StockSharp strategies, MetaTrader repositories, Hummingbot, FinRL-X, TradingAgents, Vibe-Trading, AI-Trader, TradeMaster, QuantMuse, Howtrader, BEmu, Kronos, FinceptTerminal, TurboVec, Google Authenticator, Grok Build, and Grok-1.

External strategies begin `EXTERNAL_UNTRUSTED` and must pass the internal validation pipeline.

### FinceptTerminal

Useful ideas absorbed:

- one-fetch/many-subscribers DataHub
- bounded-context event topics
- TTL caching
- broker/provider adapter boundaries
- workflow DAGs
- service registry
- system health
- reconciliation
- modular-monolith organization

Fincept’s AGPL source should not be copied casually into FX.

### TurboVec

Chosen as a possible local semantic-memory layer. Use structured SQL/DuckDB filtering first, then TurboVec allowlist/semantic reranking. Do not use it as the raw price database.

### Google Authenticator

The archived Google Authenticator repo was not selected as an app server dependency. FX uses RFC6238-compatible TOTP with secrets stored in the OS keychain.

### Grok Build / Grok-1

Grok Build contributed ideas for observable long-running agents, checkpoints, headless execution, tools, sandboxing, skills/plugins/hooks, and interruptibility.

Grok-1 itself is too large to run practically on the current Intel Mac. Its useful conceptual idea is sparse expert routing: use the most relevant specialists rather than invoking every expert for every decision.

## Professional trader operating-system research

Recurring trader decision pattern:

```text
What market?
Is the instrument worth trading?
What is the regime?
Where is the opportunity?
What invalidates the thesis?
How much can be lost?
What confirms entry?
How is profit harvested?
```

SMB-style sequence discussed:

```text
CATALYST
→ RELATIVE ATTENTION
→ MARKET REGIME
→ SECTOR
→ LEVELS
→ PLAYBOOK
→ PRICE ACTION
→ VOLUME
→ TAPE / ORDER FLOW
→ LIQUIDITY
→ INVALIDATION
→ R:R
→ SETUP SCORE
→ POSITION SIZE
→ ENTRY
→ MANAGEMENT
→ EXIT
→ REVIEW
```

Rayner-style framework:

```text
Market Structure
→ Area of Value
→ Entry Trigger
→ Exit
```

TraderTV concepts included VWAP, volume, catalysts, key levels, premarket, and multi-timeframe analysis.

tastylive concepts included IV, IV rank, probability, Greeks, DTE, small positions and repeated occurrences as research hypotheses.

Crypto research concepts included BTC trend, BTC dominance, ETH/BTC, liquidity, rates, DXY, funding, open interest and relative valuation.

## Strategy Library

Strategies discussed/shown include:

- Trend Following
- Momentum
- 20-Period Breakout
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
- Fibonacci Trend Pullback
- VWAP Pullback
- Opening Drive
- Liquidity Sweep Reversal
- Statistical Arbitrage
- Relative Value
- Event Trading
- Order Flow

Installed does not mean validated.

## Strategy validation

Lifecycle:

```text
EXTERNAL_UNTRUSTED / IDEA
→ FORMAL_SPECIFICATION
→ BACKTESTED
→ VALIDATION_PASSED
→ OOS_VALIDATED
→ WALK_FORWARD_VALIDATED
→ PARAMETER_STABILITY_VALIDATED
→ COST_STRESS_VALIDATED
→ MONTE_CARLO_VALIDATED
→ MODEL_KILLER_VALIDATED
→ LOCKED_HOLDOUT_VALIDATED
→ INDEPENDENT_REPLAY_VALIDATED
→ VAULT
→ SHADOW
→ PAPER
→ MICRO_LIVE
→ LIMITED_LIVE
→ APPROVED
```

No stage skipping.

Research protections include chronological splits, walk-forward, locked holdouts, multiple-testing controls, cost stress, Monte Carlo, complexity penalty, point-in-time data, survivorship protection, and independent replay.

## FX Harness V1.1

The Harness patch architecture included:

- TOTP
- signed short-lived live approvals
- deterministic execution policy
- LiveGate
- Brain trace
- TurboVec memory
- continuous-learning foundation
- Trader Brain schema
- Brain/security API concepts

Permanent safety flag:

`AI_CAN_EXECUTE_LIVE=false`

## UI findings

A repository search identified these important current UI files:

```text
backend/app/web/terminal.py
backend/app/web/global_markets.py
backend/app/web/research_hub.py
backend/app/web/strategy_workbench.py
backend/app/web/chat.py

backend/app/api/chat.py
backend/app/api/control_center.py
backend/app/api/global_markets.py
backend/app/api/research_brains.py
backend/app/api/strategy_lab.py

backend/app/services/models/council.py
backend/app/services/research/grounded_answer.py
```

The terminal contains Global Markets, Market Workspace, Model Council, Ask FX, Paper Trading Portfolio, and Live Trading Gate concepts.

## UI requirements

The user wants the app easier to understand.

Raw JSON from the Model Council should be translated into human-readable sections such as:

```text
Market View
Model Votes
Trend
Momentum
Volatility
Key Levels
Fibonacci
Why FX Is Waiting
Decision
```

Global Markets should be organized by Forex, Crypto, Stocks, ETFs, Indices, Commodities, and Futures.

Secondary pages should have a button back to `/terminal`.

## Fibonacci

The user requested Fibonacci research and visualization.

Project decision: Fibonacci is location/confluence evidence, not standalone authority.

Core levels:

```text
23.6
38.2
50
61.8
78.6
```

Extensions for research:

```text
127.2
161.8
261.8
```

Uptrend anchors low→high; downtrend anchors high→low.

Combine Fibonacci with trend, structure, support/resistance, EMA/VWAP, volume, order flow, candle confirmation, regime, and historical expectancy.

An explicit research requirement is to test Fibonacci against random/ordinary retracement levels instead of assuming predictive value.

## Trading Bots

Current bot cards shown by the user:

- Global Equity Scanner
- Forex Scanner
- Crypto Scanner
- Gold Bot

The cards showed status, mode, strategy, timeframe, watchlist, candidates, Scan Now, Start, Stop.

The current bots act primarily like scanners.

Desired lifecycle:

```text
WATCH
→ SCAN
→ CANDIDATE
→ NORMALIZED SIGNAL
→ RISK
→ LOCAL PAPER
→ MONITOR
→ EXIT
→ JOURNAL
→ TRAINING
```

`Start` means keep scanning; it must never mean start spending real money.

## Signal Center

Candidate rankings should become normalized signals with:

```text
instrument
asset class
bot
strategy
timestamp
LONG / SHORT / NO_TRADE
entry
stop
target 1
target 2
profit plan
expected R
confidence
risk status
eligibility
reason
data source
timeframe
```

## Local paper trading

The user explicitly requested local paper trading, not Alpaca execution.

Desired architecture:

```text
REAL MARKET DATA
→ BOT / STRATEGY
→ SIGNAL
→ DETERMINISTIC RISK
→ LOCAL SQLITE PAPER BROKER
→ $100,000 VIRTUAL ACCOUNT
→ POSITIONS
→ P&L
→ JOURNAL
→ TRAINING
```

The local paper engine should support longs, shorts, buy/sell orders, close, mark-to-market, cash, equity, exposure, realized P&L, unrealized P&L, order history, position history, and training events.

Alpaca may remain connected for independent testing but should not be required for normal local paper execution.

## Paper micro-fleet

A separate research fleet concept assigned $1 virtual capital to each of the 16 strategy workers. This is intended to measure strategy behavior and accumulate observations, not produce meaningful portfolio returns.

Strategies may remain `NO_TRADE` while still running and collecting observations.

## Mandatory stop-loss and profit plan

The latest explicit user requirement: every bot should always have stop loss and profit logic.

This is now a hard project law.

Before any automated paper/shadow/live entry:

```text
entry != null
structural_invalidation != null
stop != null
profit_plan != null
position_size != null
maximum_loss != null
```

If stop or profit plan is missing:

`NO_TRADE`

Profit plans can include fixed take profit, multiple targets, trailing stop, time exit, structural exit, or separately validated dynamic exits.

Forbidden behaviors include martingale, doubling after losses, unbounded averaging down, revenge sizing, no-stop trading, and unbounded grid recovery.

## Continuous learning

“Learning every second” is interpreted safely as continuous observation/telemetry, not continuous live model mutation.

Use separate clocks:

- streaming ingest/telemetry
- feature/regime refresh
- challenger training
- validated promotion

Never:

```text
loss
→ change parameters
→ deploy immediately
```

## Risk Engine

Risk is sovereign and cannot be overridden by an LLM.

Track trade, strategy, asset, asset-class and portfolio risk; correlation clusters; volatility; ATR; spread; slippage; liquidity; drawdown; daily/weekly loss; event risk; data quality; reconciliation; execution parity; strategy/model/system health; and kill switches.

Position sizing must be derived after structural invalidation and stop distance are known.

## Mission Control

Target metrics:

- paper equity
- cash
- realized/unrealized P&L
- drawdown
- open positions
- gross/net exposure
- risk used
- strategy health
- model health
- data quality
- system health
- execution parity
- reconciliation
- security

## Global Newspaper

The user wants Journal & Research Sources to evolve into a personal global financial newspaper refreshed every 30 minutes.

Coverage includes finance, markets, economics, central banks, politics, geopolitics, currencies, commodities, crypto, rates, inflation, jobs, GDP, tariffs, sanctions, elections, conflict, and earnings.

Headlines should remain source-labelled with original links. No paywall bypass.

## Observable Brain

The user wants to see what the system is doing similarly to an engineering agent interface.

Expose structured decision provenance:

```text
stage
status
summary
sources
evidence IDs
metrics
model votes
checks
assumptions
vetoes
versions
hashes
elapsed time
next action
```

Do not expose hidden chain-of-thought.

## Agent architecture

Use specialist agents where useful:

- Macro
- Forex
- Crypto
- Trend
- Momentum
- Mean Reversion
- Volatility
- Order Flow
- Fundamentals
- Event
- Counter-Thesis
- Execution
- Portfolio

Risk remains separate and always runs.

## Security

AI/research must not receive broker secrets, withdrawal credentials, TOTP secrets, or approval signing keys.

Live trading should not be enabled just by changing one environment variable.

Live progression:

```text
RESEARCH
→ BACKTEST
→ SHADOW
→ LOCAL PAPER
→ MICRO LIVE
→ LIMITED LIVE
→ APPROVED LIVE
```

Human approval and TOTP remain required for live entry.

## Intel Mac constraint

The current machine is Intel macOS.

Do not install NautilusTrader natively. Use Ubuntu x86_64 Docker when/if Nautilus is added.

## Terminal-paste issue

The user repeatedly encountered zsh errors because Markdown/prose was pasted directly into Terminal, including errors like `zsh: command not found: Permanent`, `This`, and decorative separator lines.

All large patches should therefore be wrapped in one heredoc shell script so only valid shell syntax is pasted.

## Final product behavior

The project should behave like a disciplined quantitative trading operation:

```text
find opportunity
reject weak setups
define invalidation
define stop
define profit plan
size risk
execute eligible paper trades
monitor
exit
journal
learn
```

Every trade must know before entry:

```text
how much can be lost
where the thesis is wrong
how profit will be harvested
when the trade ends
```

That is the project’s operational definition of a well-behaved money machine rather than a gambling casino.

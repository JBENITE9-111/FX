# FX — Local-First AI Quantitative Trading Operating System

**Permanent project root**

`/Users/macmac/Documents/Codex/FX`

## Mission

FX is a local-first, multi-asset quantitative trading operating system for research, strategy validation, local paper trading, bot monitoring, risk control, journaling, and controlled progression toward live trading.

The intended behavior is a disciplined money-making system, not a gambling casino. The system should prefer capital survival, positive expectancy, and repeatable behavior over trade frequency.

## Core operating hierarchy

```text
DATA
→ QUALITY + PROVENANCE
→ MARKET INTELLIGENCE
→ REGIME
→ ASSET SELECTION
→ STRUCTURE / LOCATION
→ MODELS
→ STRATEGIES
→ VALIDATION
→ COUNTER-THESIS
→ PORTFOLIO
→ DETERMINISTIC RISK
→ TRADE / NO_TRADE
→ PAPER / SHADOW / LIVE PROPOSAL
→ EXECUTION
→ MONITORING
→ JOURNAL
→ LEARNING
```

`NO_TRADE` is always a valid result.

## Non-negotiable trade protection

Every executable trade must define before entry:

```text
entry
structural invalidation
stop loss
profit-taking plan
position size
maximum loss
expected costs
risk/reward
```

A profit-taking plan may be a fixed target, multiple targets, trailing stop, time exit, structural exit, or another separately validated exit method.

Automatic trades are invalid if either is missing:

```text
STOP = NONE
PROFIT_PLAN = NONE
```

Reject:

```text
martingale
doubling after losses
unbounded averaging down
loss chasing
revenge sizing
no-stop trading
unbounded grid recovery
```

## Safe defaults

```env
TRADING_MODE=research
LIVE_TRADING_ENABLED=false
PAPER_TRADING_ENABLED=true
SHADOW_TRADING_ENABLED=true
MANUAL_ORDER_APPROVAL_REQUIRED=true
TOTP_REQUIRED_FOR_LIVE=true
AI_CAN_EXECUTE_LIVE=false
AI_CAN_CHANGE_RISK_LIMITS=false
AI_CAN_ACCESS_BROKER_SECRETS=false
AI_CAN_DISABLE_KILL_SWITCH=false
```

## Data

Primary research source:

`London Strategic Edge`

Research data and execution data are separate. Broker/exchange state is authoritative for external execution.

Storage:

- Parquet + DuckDB: market/research data
- SQLite: local app state, local paper positions/orders, journals, agent runs, cache
- TurboVec: semantic memory only

## Important current UI files

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

## Favorites and scheduled research

Open `http://127.0.0.1:8000/operations` from **Favorites & Operations** in the terminal sidebar.

- Adding any verified LSE instrument creates a persistent 10-minute local monitor.
- The card shows a short `BUY`, `SELL`, or `WAIT` entry decision, the research bias, provider, market-data timestamp, and calculated protection levels.
- An unqualified strategy remains `WAIT`/`BLOCK` even when its research bias is long or short.
- Schedules and in-app notifications work only while this Mac and the FX service are running.
- Telegram and Discord use the same notification router and remain `NOT_CONFIGURED` until their backend-only environment variables are set.

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=
```

The app never sends live orders from the scheduler. Local paper orders still require entry, structural invalidation, stop, profit plan, maximum loss and position size.

## Global Markets

Organize by:

```text
Forex
Crypto
Stocks
ETFs
Indices
Commodities
Futures
```

## User-facing model output

Never dump raw JSON in normal UI. Translate it into:

```text
Market View
Bullish / Bearish / Mixed / No Clear Edge
Model Votes
Trend
Momentum
Volatility
Fibonacci
Key Levels
Why FX Is Waiting
Decision
```

## Strategy lifecycle

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

## Trading bots

Current scanner concepts:

```text
Global Equity Scanner
Forex Scanner
Crypto Scanner
Gold Bot
Commodities Scanner
Indices Scanner
ETF Scanner
Futures Scanner
```

Desired lifecycle:

```text
WATCH
→ SCAN
→ CANDIDATE
→ SIGNAL
→ RISK
→ LOCAL PAPER
→ MONITOR
→ EXIT
→ JOURNAL
→ TRAINING EVENT
```

A normalized signal must include:

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
profit-taking plan
expected R
confidence
risk status
eligibility
reason
data source
timeframe
```

## Local paper trading

Preferred development execution:

```text
REAL MARKET DATA
→ BOT / STRATEGY
→ SIGNAL
→ DETERMINISTIC RISK
→ LOCAL PAPER BROKER
→ SQLITE
→ VIRTUAL POSITIONS
→ P&L
→ JOURNAL
→ TRAINING
```

Local paper trading should not require Alpaca. Alpaca Paper may remain available as an independent execution-parity reference.

## Fibonacci

Fibonacci is a location/confluence feature, not a standalone trading rule.

Retracements:

```text
23.6
38.2
50
61.8
78.6
```

Research extensions:

```text
127.2
161.8
261.8
```

Validate Fibonacci against ordinary/random retracement levels. Combine with structure, trend, support/resistance, EMA/VWAP, volume, order flow, candlestick confirmation, regime, and historical expectancy.

## Training

Continuous learning means observing and measuring continuously, not modifying production models continuously.

```text
observe
→ record
→ train challenger
→ validate
→ holdout
→ shadow
→ paper
→ approve
→ deploy
```

Never:

```text
lose
→ tweak
→ redeploy immediately
```

## Risk Engine

Risk is sovereign and may veto any opportunity.

Track:

```text
trade risk
strategy risk
asset risk
portfolio exposure
correlation
liquidity
spread
slippage
drawdown
daily/weekly loss
data quality
system health
execution health
reconciliation
kill switches
```

## Security

AI/research must never receive broker secrets, withdrawal credentials, TOTP secrets, or approval signing keys.

Keep:

`AI_CAN_EXECUTE_LIVE=false`

TOTP enrollment and the always-on security/health sentinel are available at
`http://127.0.0.1:8000/security`. The sentinel observes health and creates local
SQLite backups; it cannot change risk limits or authorize trades.

## Development verification

```bash
./scripts/clean-workspace.sh
.venv-core/bin/python -m pytest -q
.venv-core/bin/python -m compileall -q backend services tests
```

`pytest.ini` restricts project test discovery to `tests/`; downloaded reference
repositories under `vendor/` keep their own dependency and test environments.

## Codex start

```bash
cd "/Users/macmac/Documents/Codex/FX"
codex
```

Before changing anything, Codex should read:

```text
README.md
AGENTS.md
FX_COMPLETE_CONVERSATION_CONTEXT.md
docs/TRADING_SYSTEM_CONSTITUTION.md
docs/RISK_ENGINE_SPEC.md
docs/STRATEGY_PROMOTION_PIPELINE.md
```

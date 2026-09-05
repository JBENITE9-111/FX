# FX — COMPLETE CHAT HANDOFF FOR A NEW CHAT

## Permanent Project Root

`/Users/macmac/Documents/Codex/FX`

## CRITICAL STATUS — READ FIRST

The user did **NOT** execute the last two Terminal code answers from the previous chat.

Do **not** assume the README / AGENTS / context / Quant Research Lab changes from those two answers are installed.

### The two unexecuted answers were

1. **FX → CODEX FINAL HANDOFF**
   - Intended to create/update:
     - `README.md`
     - `AGENTS.md`
     - `FX_COMPLETE_CONVERSATION_CONTEXT.md`
   - Intended to pause only **new** automatic local-paper entries.
   - Intended to preserve current local-paper positions.
   - Intended to set:
     - `FX_LOCAL_PAPER_AUTO_BOTS=false`
     - `FX_STOP_REQUIRED=true`
     - `FX_PROFIT_PLAN_REQUIRED=true`
     - `LIVE_TRADING_ENABLED=false`
     - `AI_CAN_EXECUTE_LIVE=false`
   - Intended to document the local-paper accounting problem and missing protected-order contract.

2. **FX MASTER CODEX HANDOFF V2**
   - Intended to merge the first handoff with the newly supplied quant-finance research.
   - Intended to create/update:
     - `README.md`
     - `AGENTS.md`
     - `FX_COMPLETE_CONVERSATION_CONTEXT.md`
     - `docs/QUANT_RESEARCH_LAB.md`
     - `research/quant_projects/`
     - `services/research_integrity/`
     - `services/information_diffusion/`
     - `services/options_intelligence/`
     - `services/prediction_markets/`
   - Intended to add:
     - `FX_MAX_LOSS_REQUIRED=true`
     - `FX_RISK_REWARD_REQUIRED=true`
     - `FX_DSR_REQUIRED_FOR_PROMOTION=true`
     - `FX_PBO_REQUIRED_FOR_PROMOTION=true`
     - `FX_LOCKED_HOLDOUT_REQUIRED=true`
     - `FX_PREDICTION_MARKETS_MODE=research_only`

## REQUIRED NEXT ACTION IN THE NEW CHAT

The new chat should immediately give the user **ONE SINGLE copy/paste Terminal block** that combines the two unexecuted answers above.

The code must:

- target `/Users/macmac/Documents/Codex/FX`,
- use one heredoc installer,
- require no ZIP,
- require no separate downloads,
- back up existing handoff files,
- preserve current local-paper positions and databases,
- pause only new automatic local-paper entries,
- keep live trading disabled,
- keep AI live execution disabled,
- write the full README,
- write the full AGENTS file,
- write the full FX conversation/context file,
- write the Quant Research Lab document,
- create the research folders,
- print verification at the end.

The user wants the code **immediately**, not another explanation-only response.

---

# PROJECT VISION

FX is a local-first multi-asset quantitative trading operating system for:

- Forex
- Crypto
- Stocks
- ETFs
- Indices
- Commodities
- Gold
- Futures
- Options research
- Macro

The desired product combines:

- TradingView-style charts
- Bloomberg-style market intelligence
- quantitative research
- strategy factory
- model council
- AI agents
- trading bots
- local paper trading
- portfolio monitoring
- risk management
- journal
- continuous training
- event/news intelligence
- Mission Control

The user has described the desired system as a “money machine,” but explicitly wants it to be **well-behaved, disciplined, risk-controlled, evidence-driven, and not a gambling casino**.

Correct engineering interpretation:

`validated edge + bounded losses + defined profit-taking + portfolio risk control + continuous measurement + deliberate promotion`

---

# CORE OPERATING LAW

- Data provides facts.
- Models provide evidence.
- Python performs calculations.
- The LLM explains.
- Portfolio aggregates exposure.
- The Risk Engine controls capital.
- The user authorizes live entry.

`NO_TRADE` is a first-class valid result.

---

# MASTER DECISION PIPELINE

```text
MARKET DATA
↓
DATA QUALITY
↓
PROVENANCE
↓
SYSTEM HEALTH
↓
GLOBAL REGIME
↓
ASSET SELECTION
↓
RELATIVE STRENGTH
↓
MULTI-TIMEFRAME STRUCTURE
↓
LOCATION
↓
VOLATILITY
↓
VOLUME
↓
LIQUIDITY / ORDER FLOW
↓
EVENT / NEWS CONTEXT
↓
STRATEGY
↓
MODELS
↓
HISTORICAL ANALOGUES
↓
COUNTER-THESIS
↓
MODEL COUNCIL
↓
PORTFOLIO IMPACT
↓
DETERMINISTIC RISK ENGINE
↓
TRADE / NO_TRADE
↓
LOCAL PAPER / SHADOW / LIVE PROPOSAL
↓
EXECUTION
↓
POSITION MONITOR
↓
STOP / TAKE PROFIT / EXIT
↓
RECONCILIATION
↓
JOURNAL
↓
TRAINING
```

No model, strategy, bot, or agent may bypass Risk.

---

# PRIMARY DATA SOURCE

Primary research source:

`London Strategic Edge`

Earlier project logs showed working multi-asset access including examples such as:

- AAPL
- EURUSD
- BTCUSD
- XAUUSD

and broad global market discovery.

Permanent distinction:

`RESEARCH DATA != EXECUTION DATA`

---

# STORAGE

Use:

- Parquet + DuckDB for analytical/time-series market data.
- SQLite for local paper accounts, orders, positions, journals, strategy state, agent runs, app metadata and cache.
- TurboVec for semantic memory.

TurboVec should store things like:

- trade memories
- strategy memories
- failure memories
- regime memories
- research memories
- execution memories

It should **not** replace raw price storage.

---

# EXISTING / REFERENCED STACK

The project has discussed, installed, or referenced:

- London Strategic Edge
- OpenBB
- Backtrader
- Riskfolio-Lib
- Kronos
- Kimi / OpenRouter
- Ollama
- TurboVec
- Alpaca Paper as an optional external paper/execution-parity reference
- TradingAgents
- Hummingbot
- FinRL-X
- TradeMaster
- QuantMuse
- Howtrader
- Freqtrade strategies
- MetaTrader strategies
- FinceptTerminal architecture
- Google-Authenticator-compatible TOTP
- Grok Build agent-runtime concepts
- Grok-1 sparse-expert concepts

---

# FINCEPTTERMINAL

Useful architecture absorbed:

- one-fetch / many-subscribers DataHub
- bounded-context event topics
- TTL cache
- provider adapters
- broker adapters
- workflow DAG
- service registry
- system health
- reconciliation
- modular-monolith structure

Fincept open-source code is AGPL, so the project decision was to use it as architectural inspiration rather than blindly copy source.

---

# TURBOVEC

Useful pattern:

```text
DuckDB / SQL filter
↓
candidate IDs
↓
TurboVec allowlist
↓
semantic rerank
```

Appropriate for semantic memory, not raw market time series.

---

# TOTP / GOOGLE AUTHENTICATOR

The archived Google Authenticator repo was not selected as an application-server dependency.

Use RFC6238-compatible TOTP.

TOTP secrets should be stored in the OS keychain.

Live approvals should be short-lived, signed, proposal-bound, risk-decision-bound, and nonce-protected.

---

# GROK / AGENT ARCHITECTURE

Grok Build contributed useful concepts:

- headless execution
- long-running tasks
- checkpoints
- tools
- skills
- plugins/hooks
- sandboxing concepts
- interruptibility
- observable execution

Grok-1 itself is too large for practical local deployment on the current Intel Mac.

Useful conceptual contribution:

`sparse expert routing`

Possible specialists:

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
- Options
- Counter-Thesis
- Execution
- Portfolio

Risk is always separate.

---

# PROFESSIONAL TRADER RESEARCH

Recurring professional workflow:

```text
What market?
Is the instrument worth trading?
What is the regime?
Where is the asymmetric opportunity?
What invalidates the thesis?
How much can be lost?
What confirms entry?
How will profit be taken?
```

SMB-style process:

```text
Catalyst
→ Attention
→ Regime
→ Sector
→ Levels
→ Playbook
→ Price Action
→ Volume
→ Tape / Order Flow
→ Liquidity
→ Invalidation
→ Risk/Reward
→ Setup Score
→ Position Size
→ Entry
→ Management
→ Exit
→ Review
```

Rayner-style framework:

`Market Structure → Area of Value → Entry Trigger → Exit`

Other research included VWAP, volume, catalysts, premarket, multi-timeframe analysis, IV/IV Rank/Greeks, crypto regime, BTC dominance, funding, open interest, DXY, rates, fundamentals and relative strength.

---

# STRATEGY LIBRARY

Strategies discussed/shown:

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

---

# STRATEGY PROMOTION PIPELINE

```text
EXTERNAL_UNTRUSTED / IDEA
↓
FORMAL SPECIFICATION
↓
BACKTEST
↓
VALIDATION
↓
OOS
↓
WALK-FORWARD
↓
PARAMETER STABILITY
↓
COST STRESS
↓
MONTE CARLO
↓
MODEL KILLER
↓
BACKTEST OVERFITTING TESTS
↓
DEFLATED SHARPE
↓
LOCKED HOLDOUT
↓
INDEPENDENT REPLAY
↓
VAULT
↓
SHADOW
↓
LOCAL PAPER
↓
MICRO LIVE
↓
LIMITED LIVE
↓
APPROVED
```

No stage skipping.

---

# FX HARNESS V1.1

Harness concepts included:

- TOTP
- signed approval tokens
- execution policy
- LiveGate
- Brain trace
- TurboVec memory
- continuous-learning foundation
- Trader Brain schema
- security API
- Brain API

Permanent invariant:

`AI_CAN_EXECUTE_LIVE=false`

---

# IMPORTANT CURRENT UI FILES

A real repository search identified:

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

Important UI elements found in `terminal.py`:

- Model Council
- Global Markets
- Market Workspace
- Ask FX
- Paper Trading Portfolio
- Live Trading Gate

---

# UI REQUIREMENTS

## Global Markets

Organize into:

- ALL
- FOREX
- CRYPTO
- STOCKS
- ETFs
- INDICES
- COMMODITIES
- FUTURES

Show symbol, friendly name, asset class, price, change, source, market state.

## Model Council

Do not display raw JSON.

Translate it into a user-friendly panel containing:

- Market View
- bullish/bearish/neutral vote counts
- Trend
- Momentum
- Volatility
- Fibonacci
- Key Levels
- Why FX Is Waiting
- Decision

## Navigation

Secondary pages should provide a clear button back to:

`/terminal`

---

# FIBONACCI

Project decision:

`Fibonacci = Location / Confluence`

not a standalone signal.

Core retracement levels:

- 23.6%
- 38.2%
- 50.0%
- 61.8%
- 78.6%

Research extensions:

- 127.2%
- 161.8%
- 261.8%

Uptrend anchors:

`confirmed swing low → confirmed swing high`

Downtrend anchors:

`confirmed swing high → confirmed swing low`

Combine with:

- structure
- support/resistance
- EMA
- VWAP
- volume
- order flow
- candlestick confirmation
- regime
- historical expectancy

Research requirement:

`test Fibonacci against ordinary/random retracement levels`

---

# TRADING BOTS

Current scanner concepts:

- Global Equity Scanner
- Forex Scanner
- Crypto Scanner
- Gold Bot

Current UI fields included:

- Status
- Mode
- Strategy
- Timeframe
- Watching
- Current candidates
- Scan Now
- Start
- Stop

These currently behave primarily like scanners.

Desired lifecycle:

```text
WATCH
↓
SCAN
↓
CANDIDATE
↓
NORMALIZED SIGNAL
↓
PROTECTED TRADE PLAN
↓
RISK
↓
LOCAL PAPER
↓
MONITOR
↓
STOP / TARGET / EXIT
↓
JOURNAL
↓
TRAINING
```

`Start` means start scanning, never start live-money trading.

---

# SIGNAL CONTRACT

Every normalized signal should contain:

```text
signal_id
bot_id
strategy_id
instrument
asset_class
timestamp
LONG / SHORT / NO_TRADE
score
confidence
entry
structural_invalidation
stop
target_1
target_2
profit_plan
maximum_loss
expected_r
time_stop
risk_status
eligibility
reason
data_source
timeframe
evidence_ids
```

---

# LOCAL PAPER TRADING

The user explicitly requested:

> trade locally with paper money, not in Alpaca

Preferred architecture:

```text
REAL MARKET DATA
↓
BOT / STRATEGY
↓
SIGNAL
↓
PROTECTED ORDER
↓
RISK
↓
LOCAL SQLITE PAPER BROKER
↓
$100,000 VIRTUAL ACCOUNT
↓
POSITIONS
↓
P&L
↓
JOURNAL
↓
TRAINING
```

Alpaca may remain installed as an optional external parity test, but should not be required for normal paper trading.

---

# CRITICAL LOCAL-PAPER ACCOUNTING BUG

A recent local-paper run reportedly showed:

```text
Starting equity     $100,000
Cash                 $99,500
Reported equity      $99,500
Unrealized P&L             0
Exposure                $800
```

This indicates an accounting problem.

For unchanged long positions:

`cash decrease + long market value = equity approximately unchanged`

The next chat / Codex must audit:

- cash
- long market value
- short accounting
- equity
- realized P&L
- unrealized P&L
- gross exposure
- net exposure

before re-enabling automatic local-paper entries.

---

# CRITICAL TRADE-PROTECTION DEFECT

The first local-paper executor could open positions without guaranteed:

- stop loss
- profit plan
- maximum loss

The user explicitly required:

> the bot should always have stop loss and profit

This is now a permanent project law.

Desired safety flags:

```text
FX_LOCAL_PAPER_AUTO_BOTS=false
FX_STOP_REQUIRED=true
FX_PROFIT_PLAN_REQUIRED=true
FX_MAX_LOSS_REQUIRED=true
FX_RISK_REWARD_REQUIRED=true

PAPER_TRADING_ENABLED=true
SHADOW_TRADING_ENABLED=true

LIVE_TRADING_ENABLED=false
AI_CAN_EXECUTE_LIVE=false
AI_CAN_CHANGE_RISK_LIMITS=false
AI_CAN_ACCESS_BROKER_SECRETS=false
AI_CAN_DISABLE_KILL_SWITCH=false

MANUAL_ORDER_APPROVAL_REQUIRED=true
TOTP_REQUIRED_FOR_LIVE=true
```

Existing paper positions should **not** be automatically closed or modified just because the safety handoff is applied.

They can be preserved for diagnosis.

---

# MANDATORY PROTECTED-TRADE CONTRACT

Every executable PAPER, SHADOW, MICRO_LIVE, or LIVE order must define before entry:

- instrument
- asset class
- direction
- entry
- structural invalidation
- stop loss
- profit-taking plan
- target 1 and/or target 2 and/or a validated trailing exit
- maximum loss
- position size
- expected costs
- expected R
- time stop where applicable
- strategy ID
- strategy version
- risk-decision ID

Hard rule:

```python
if stop is None:
    return NO_TRADE

if profit_plan is None:
    return NO_TRADE

if maximum_loss is None:
    return NO_TRADE
```

No autonomous bot may create a naked position.

---

# DETERMINISTIC POSITION MONITOR

For every open bot position, track:

- entry
- side
- quantity
- stop
- target 1
- target 2
- trailing rule
- time stop
- current price
- MAE
- MFE
- risk remaining

On stop: execute planned exit.

On target: execute planned profit-taking action.

LLMs should not enforce stops; deterministic code should.

---

# PAPER STRATEGY MICRO-FLEET

A separate research micro-fleet concept assigned:

`$1 virtual capital per strategy`

Purpose:

- continuous observation
- strategy comparison
- research statistics

It is not the main portfolio.

A strategy may remain `NO_TRADE` while still collecting observations.

---

# CONTINUOUS LEARNING

“Learning every second” means continuously observe and record, not continuously rewrite production models.

Separate clocks:

## Streaming clock
- prices
- spreads
- returns
- telemetry
- predictions

## Feature clock
- regime
- correlations
- rankings
- analogues

## Training clock
- challenger models
- OOS
- walk-forward

## Promotion clock
- validated explicit promotion

Never:

`LOSS → CHANGE PARAMETERS → LIVE DEPLOY`

Track:

- sample size
- trades
- win rate
- average win R
- average loss R
- expectancy R
- profit factor
- Sharpe
- Sortino
- Calmar
- max drawdown
- MAE
- MFE
- holding time
- regime performance
- asset performance
- slippage
- costs
- execution parity

---

# RISK ENGINE

Risk has veto authority.

Inputs include:

- equity
- cash
- buying power
- margin
- positions
- pending orders
- symbol exposure
- asset exposure
- asset-class exposure
- sector exposure
- currency exposure
- factor exposure
- venue exposure
- correlation
- tail dependence
- ATR
- volatility
- spread
- slippage
- liquidity
- market impact
- strategy drawdown
- portfolio drawdown
- daily loss
- weekly loss
- event risk
- data quality
- system health
- broker health
- reconciliation
- execution parity
- kill switches

Correct sizing order:

```text
structural invalidation
↓
volatility buffer
↓
stop
↓
stop distance
↓
allowed risk
↓
position size
```

Never define stop placement from a desired position size.

---

# FX GLOBAL NEWSPAPER

The user wants Journal & Research Sources to become a personal institutional-style financial newspaper.

Coverage:

- finance
- markets
- economics
- central banks
- politics
- geopolitics
- stocks
- FX
- crypto
- commodities
- rates
- inflation
- employment
- GDP
- tariffs
- sanctions
- elections
- conflicts
- earnings

Refresh target:

`every 30 minutes`

Preserve headline, source, time, category, original link.

No paywall bypass.

---

# OBSERVABLE BRAIN

Expose structured process stages:

```text
DATA
QUALITY
SYSTEM HEALTH
EVENT RISK
REGIME
ASSET SELECTION
RELATIVE STRENGTH
STRUCTURE
LOCATION
FIBONACCI
VOLATILITY
VOLUME
ORDER FLOW
STRATEGY
MODELS
ANALOGUES
COUNTER-THESIS
PORTFOLIO
RISK
FINAL
```

Show:

- status
- summary
- sources
- evidence IDs
- metrics
- model votes
- assumptions
- vetoes
- versions
- hashes
- elapsed time
- next action

Do not expose hidden chain-of-thought.

---

# SECURITY

Never expose to AI/research:

- broker secrets
- exchange secrets
- withdrawal credentials
- TOTP secret
- approval signing key

Keep:

```text
AI_CAN_EXECUTE_LIVE=false
LIVE_TRADING_ENABLED=false
```

---

# LIVE TRADING PROGRESSION

```text
RESEARCH
↓
BACKTEST
↓
SHADOW
↓
LOCAL PAPER
↓
MICRO LIVE
↓
LIMITED LIVE
↓
APPROVED LIVE
```

Live entry later requires:

- validated strategy
- risk PASS
- reconciliation PASS
- system-health PASS
- kill switch clear
- human approval
- fresh TOTP
- signed approval

---

# INTEL MAC CONSTRAINT

Current environment is Intel macOS.

Do not install NautilusTrader natively.

Use Ubuntu x86_64 Docker if/when NautilusTrader is introduced.

---

# TERMINAL-PASTE PROBLEM

The user repeatedly hit zsh errors because Markdown/prose/decorative separators were pasted directly into Terminal.

Examples included:

- `zsh: command not found: Permanent`
- `zsh: command not found: This`
- `zsh: command not found: #######`

Permanent response rule:

For large Terminal changes, provide **one heredoc installer block**:

```bash
cat > /tmp/change.sh <<'FXSCRIPT'
...
FXSCRIPT

bash /tmp/change.sh
```

No ZIP. No separate fragments. No prose inside the pasteable shell code unless commented.

---

# QUANT RESEARCH LAB — NEW MATERIAL

The user uploaded a document titled:

**The 4 Quant Finance Projects That Make You Stand Out**

by `@chrispathway`.

The four projects should be incorporated as **research infrastructure**, not automatically live-tradable systems.

## 1. Prediction Market Mispricing Engine

Research:

- YES + NO pricing
- cross-venue equivalent events
- order-book parsing
- fees
- spread
- slippage
- gas/venue costs
- latency
- available depth
- capital sizing

Core principle:

`gross price discrepancy != executable edge`

Required evaluation:

- fees
- crossed spread
- slippage
- gas
- latency
- partial fills
- depth
- venue rules
- settlement definitions
- contract equivalence

Current FX mode:

`RESEARCH_ONLY`

## 2. Information Diffusion / Hawkes Engine

Use timestamped macro/news events and market activity to research:

- news → price excitation
- price → price self-excitation
- cross-market excitation
- information half-life
- endogeneity ratio

Potential concept:

`half_life = ln(2) / beta`

Potential use:

```text
NEWS EVENT
↓
HAWKES / DIFFUSION MODEL
↓
INFORMATION ABSORPTION SCORE
↓
EVENT-RISK FILTER
```

## 3. Implied Risk-Neutral Distribution

Use options to research market-implied future pricing distributions.

Concept:

`risk-neutral density ≈ second derivative of call price with respect to strike`

Engineering pipeline:

```text
OPTION CHAIN
↓
QUALITY FILTER
↓
IV INVERSION
↓
SMOOTH IMPLIED-VOL SURFACE
↓
ARBITRAGE CHECKS
↓
SMOOTH CALL CURVE
↓
SECOND DERIVATIVE
↓
RISK-NEUTRAL DENSITY
↓
TAIL / SKEW ANALYSIS
```

Treat as market-implied pricing evidence, not literal real-world probability.

## 4. Backtest Overfitting Detector

Highest priority of the four for direct FX strategy governance.

Required concepts:

- Deflated Sharpe Ratio
- Probabilistic Sharpe Ratio
- Probability of Backtest Overfitting
- Minimum Track Record Length
- trial count
- selection bias
- skew
- kurtosis
- multiple-testing correction

Required research-campaign logic:

```text
REGISTER ALL TRIALS
↓
BACKTEST RESULTS
↓
TRIAL COUNT
↓
BEST STRATEGY
↓
RAW SHARPE
↓
DEFLATED SHARPE
↓
PBO
↓
TRACK-RECORD CHECK
↓
MULTIPLE-TESTING CONTROL
↓
VALID / REJECT
```

Permanent principle:

`best backtest != best strategy`

---

# QUANT RESEARCH LAB TARGET STRUCTURE

The unexecuted V2 handoff intended to create:

```text
docs/QUANT_RESEARCH_LAB.md

research/quant_projects/

services/research_integrity/

services/information_diffusion/

services/options_intelligence/

services/prediction_markets/
```

Suggested statuses:

- IDEA
- RESEARCH
- RUNNING
- VALIDATING
- VALIDATED
- REJECTED

None of these statuses imply live-trading eligibility.

---

# EXACT REQUIREMENT FOR THE NEXT CHAT

The user did **not** execute the previous two Terminal answers.

The next chat must combine them and produce **one final complete Terminal installer**.

The installer should:

1. Set root:
   `/Users/macmac/Documents/Codex/FX`

2. Back up if present:
   - `README.md`
   - `AGENTS.md`
   - `FX_COMPLETE_CONVERSATION_CONTEXT.md`
   - `docs/QUANT_RESEARCH_LAB.md`

3. Preserve current databases and paper positions.

4. Pause only new automatic local-paper entries.

5. Safely update `.env` with at least:

```text
FX_LOCAL_PAPER_AUTO_BOTS=false
FX_STOP_REQUIRED=true
FX_PROFIT_PLAN_REQUIRED=true
FX_MAX_LOSS_REQUIRED=true
FX_RISK_REWARD_REQUIRED=true

PAPER_TRADING_ENABLED=true
SHADOW_TRADING_ENABLED=true

LIVE_TRADING_ENABLED=false
AI_CAN_EXECUTE_LIVE=false
AI_CAN_CHANGE_RISK_LIMITS=false
AI_CAN_ACCESS_BROKER_SECRETS=false
AI_CAN_DISABLE_KILL_SWITCH=false

MANUAL_ORDER_APPROVAL_REQUIRED=true
TOTP_REQUIRED_FOR_LIVE=true

FX_QUANT_RESEARCH_LAB_ENABLED=true
FX_DSR_REQUIRED_FOR_PROMOTION=true
FX_PBO_REQUIRED_FOR_PROMOTION=true
FX_LOCKED_HOLDOUT_REQUIRED=true

FX_PREDICTION_MARKETS_MODE=research_only
```

6. Write complete `README.md`.

7. Write complete `AGENTS.md`.

8. Write complete `FX_COMPLETE_CONVERSATION_CONTEXT.md`.

9. Write `docs/QUANT_RESEARCH_LAB.md`.

10. Create:
   - `research/quant_projects/`
   - `services/research_integrity/`
   - `services/information_diffusion/`
   - `services/options_intelligence/`
   - `services/prediction_markets/`

11. Add `__init__.py` placeholders where appropriate.

12. Add `research/quant_projects/README.md`.

13. Print verification.

14. Keep live trading disabled.

15. Keep AI live execution disabled.

16. Do not automatically close/reset existing local paper positions.

17. Do not re-enable local auto bots until protected-order and accounting tests pass.

18. End by telling the user to run:

```bash
cd "/Users/macmac/Documents/Codex/FX"
codex
```

and instruct Codex to read:

- `README.md`
- `AGENTS.md`
- `FX_COMPLETE_CONVERSATION_CONTEXT.md`
- `docs/QUANT_RESEARCH_LAB.md`

before changing anything.

---

# IMMEDIATE CODEX PRIORITIES AFTER HANDOFF

Recommended order:

1. Audit current repository.
2. Audit local paper database.
3. Fix local paper accounting.
4. Build protected-order schema.
5. Build deterministic stop-loss monitor.
6. Build deterministic take-profit monitor.
7. Add accounting/protection tests.
8. Normalize actual scanner signals.
9. Connect scanner signals to deterministic Risk.
10. Re-enable automatic local-paper bots only after tests pass.
11. Connect Strategy Library to protected local paper execution.
12. Improve Model Council UI.
13. Organize Global Markets by asset class.
14. Implement Backtest Overfitting Detector.
15. Add DSR/PBO to strategy-promotion gates.
16. Build Hawkes information-diffusion research.
17. Build options risk-neutral distribution research.
18. Build prediction-market research in research-only mode.
19. Expand Mission Control.
20. Continue challenger-model / training / validation infrastructure.

---

# FINAL PRODUCT PHILOSOPHY

A disciplined FX “money machine” means:

```text
FIND REAL EDGE
↓
VERIFY DATA
↓
VALIDATE STRATEGY
↓
DEFINE INVALIDATION
↓
DEFINE STOP
↓
DEFINE PROFIT PLAN
↓
DEFINE MAXIMUM LOSS
↓
SIZE POSITION
↓
EXECUTE PAPER
↓
MONITOR
↓
STOP / TAKE PROFIT / EXIT
↓
JOURNAL
↓
LEARN
↓
REVALIDATE
↓
REPEAT ONLY WHAT SURVIVES
```

Never:

```text
SIGNAL
↓
BET
↓
HOPE
```

---

# FIRST MESSAGE TO SEND IN THE NEW CHAT

After uploading this file, send:

> Read this entire FX handoff file completely. Treat `/Users/macmac/Documents/Codex/FX` as the permanent project root.
>
> Critical: I did **not** execute the last two Terminal code answers from the previous chat. Do not assume their README/AGENTS/context/quant-lab changes exist.
>
> I need you to **immediately provide ONE SINGLE copy-paste Terminal code block** that merges those two unexecuted answers, with all updates and fixes included.
>
> It must:
> - write directly into `/Users/macmac/Documents/Codex/FX`,
> - require no ZIP and no separate downloads,
> - use one heredoc installer,
> - back up existing handoff files,
> - preserve current paper positions,
> - pause only new automatic local-paper entries,
> - set mandatory stop/profit/max-loss/risk-reward safety flags,
> - keep live trading and AI live execution disabled,
> - create/update `README.md`, `AGENTS.md`, `FX_COMPLETE_CONVERSATION_CONTEXT.md`, and `docs/QUANT_RESEARCH_LAB.md`,
> - create the quant research folders,
> - incorporate Backtest Overfitting, Hawkes Information Diffusion, Risk-Neutral Distribution, and Prediction Market research,
> - clearly document the local-paper accounting bug and protected-order defect,
> - and print final verification.
>
> Do not just explain it. Give me the complete Terminal code immediately.


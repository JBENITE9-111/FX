# AGENTS.md — FX Codex Operating Instructions

## Root

Always work inside:

`/Users/macmac/Documents/Codex/FX`

Do not create a parallel FX application.

## Before editing

Read:

1. `README.md`
2. `FX_COMPLETE_CONVERSATION_CONTEXT.md`
3. `docs/TRADING_SYSTEM_CONSTITUTION.md`
4. `docs/RISK_ENGINE_SPEC.md`
5. `docs/STRATEGY_PROMOTION_PIPELINE.md`

Then inspect the current repository and reuse working modules instead of duplicating them.

## Preserve working systems

Do not casually replace:

- London Strategic Edge
- Kimi/OpenRouter
- Ollama
- OpenBB
- Backtrader
- Riskfolio-Lib
- Kronos
- Training Center
- Strategy Library
- Trading Bots
- Global Markets
- Market Workspace
- Journal/Newspaper
- local paper systems
- `fx` launcher

Backup before meaningful edits.

## Project behavior

FX must behave like a disciplined quantitative desk, not a casino.

Optimize for:

- capital survival
- positive expectancy
- repeatability
- risk-adjusted returns
- explainability
- honest performance measurement

`NO_TRADE` is a first-class output.

## Mandatory stop and profit plan

Every executable PAPER, SHADOW, or LIVE trade requires:

```text
entry
structural invalidation
stop loss
profit-taking plan
maximum loss
position size
```

Allowed profit-taking plans include fixed target, multiple targets, trailing stop, validated time exit, or validated structural/dynamic exit.

Hard rule:

```python
if stop is None:
    return NO_TRADE

if profit_plan is None:
    return NO_TRADE
```

Never create automatic naked positions.

## Forbidden behavior

Do not implement or activate:

- martingale
- doubling after losses
- unbounded averaging down
- loss chasing
- revenge sizing
- no-stop trading
- unbounded grid recovery
- automatic risk-limit increases
- strategy self-promotion

## Local paper first

Current development priority:

```text
real market data
→ strategy/bot
→ signal
→ risk
→ local SQLite paper broker
→ positions/P&L
→ journal
→ training
```

Do not require Alpaca for local paper execution.

## Bot signal contract

Normalize candidates into:

```text
instrument
asset_class
strategy_id
bot_id
timestamp
direction
score
entry
stop
target_1
target_2
profit_plan
expected_r
confidence
risk_status
eligibility
reason
data_source
timeframe
```

Never display unexplained candidate numbers as if they were actionable trades.

## UI

Do not expose raw JSON in user-facing panels.

Important current files:

```text
backend/app/web/terminal.py
backend/app/web/global_markets.py
backend/app/web/research_hub.py
backend/app/web/strategy_workbench.py
backend/app/web/chat.py
```

Organize Global Markets into Forex, Crypto, Stocks, ETFs, Indices, Commodities, Futures.

Add clear navigation back to `/terminal` from secondary pages.

## Fibonacci

Treat Fibonacci as location/confluence evidence, never standalone authority.

## Learning

Continuous learning does not authorize continuous production mutation.

Use challenger models and the full validation pipeline.

## Research integrity

Protect against:

- look-ahead bias
- survivorship bias
- label leakage
- revised future data
- holdout contamination
- multiple-testing overfit

Use chronological splits, OOS, walk-forward, cost stress, Monte Carlo, parameter stability, and locked holdouts.

## Risk sovereignty

No LLM may bypass deterministic risk.

Risk always runs even when sparse expert routing selects only a few analytical specialists.

## Live trading

Do not silently enable live trading.

Keep:

`AI_CAN_EXECUTE_LIVE=false`

Live entry requires validation, reconciliation, system health, kill-switch clearance, deterministic risk pass, human approval, and TOTP.

## Security

Never log or expose broker credentials, withdrawal credentials, TOTP secrets, or signing keys.

## Observability

Record structured evidence, not hidden chain-of-thought:

```text
run_id
stage
status
summary
evidence_ids
model_votes
checks
assumptions
vetoes
input_hash
output_hash
elapsed_ms
```

## Code quality

Before finishing:

- compile changed Python
- run import tests
- run route tests
- run local paper tests
- run risk tests
- verify safety environment
- verify that claimed features actually work

## Terminal patches

When generating large terminal patches, always wrap them in one heredoc script. Do not mix Markdown prose into pasteable shell blocks.

## End-state

Build a disciplined fleet of validated systems under one observable AI-assisted operating layer.

The project should systematically:

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

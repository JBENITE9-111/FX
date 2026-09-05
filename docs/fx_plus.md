# FX — Favorites, Alerts, Strategy Reports, Agentic Research & Paper-Only Intelligence
## Codex Implementation Handoff / Product Specification / Architecture / QA Contract
**Version:** 1.0  
**Date:** 2026-09-05  
**Project:** FX local research + bot-training + paper-trading platform

---

# 0. MASTER INSTRUCTION TO CODEX

Read this file completely before changing the application.

Treat this document as an implementation brief, product specification, architecture proposal, safety contract, and QA acceptance plan.

The objective is **not** to build a notification toy or a system that constantly tells the user to trade.

The objective is to extend FX into a disciplined **research → strategy → model council → supervisor → deterministic risk validation → paper signal → notification → outcome tracking → evaluation** platform.

The system must remain **RESEARCH + PAPER TRADING ONLY**. Do not enable live-money execution.

Work hands-off where possible:
- inspect the existing repository, README, AGENTS and architecture;
- reuse existing services before creating duplicates;
- run the app;
- exercise the UI;
- call real local APIs;
- test Discord integrations using test messages when credentials are configured;
- test scheduling;
- test report generation;
- test restart persistence;
- test failure modes;
- preserve evidence;
- fix implementation issues you can verify;
- do not fake health states, market prices, provider status, signals, confidence, or successful delivery.

If this document conflicts with a safer existing hard rule in the repository, preserve the safer rule and document the conflict.

---

# 1. PRODUCT VISION

FX should become a **paper-only trading research laboratory** in which the user can:

1. Maintain a curated list of favorite instruments.
2. Configure how each favorite is monitored.
3. Ask any bot or strategy for a standardized report on demand.
4. Ask the system to explain the plan being used to pursue a defined research goal.
5. Schedule recurring analyses.
6. Receive meaningful state changes through:
   - the FX application,
   - Discord.
7. Store every analysis, signal, veto, notification and paper outcome.
8. Compare strategies and bots based on evidence rather than presentation.
9. Use multiple specialist agents/brains without allowing an LLM to bypass deterministic risk rules.
10. Gradually build an auditable dataset that can be used to evaluate whether any bot has earned promotion through a strict validation lifecycle.

The UX principle is:

> **The app may analyze frequently; it must only alert when something meaningfully changes or when the user explicitly asks for a periodic report.**

---

# 2. NEW CORE MODULE: FAVORITES / WATCHLIST

Add a first-class section in the left navigation:

`Favorites` or `Watchlist`

Recommended name:

# ⭐ Favorites

A user should be able to add an asset to Favorites from:
- Global Markets
- Market Workspace
- Model Training
- Strategies
- Bots
- Ask FX / FX Intelligence
- Paper Portfolio where appropriate

Use one canonical instrument registry. Do not create page-specific hard-coded ticker lists.

## 2.1 Supported asset classes

At minimum, where the current data layer supports them:

- Stocks
- Forex
- Crypto
- Indices
- Commodities
- ETFs

Do not expose an instrument as operational unless its provider mapping actually resolves.

## 2.2 Favorite card

Each favorite should show a concise current state:

```text
★ EUR/USD

Asset class: Forex
Monitoring: ON
Primary timeframe: 15m
Strategy: Model Council
Next analysis: 12:05
Last analysis: 12:00
Current state: WATCHING
Risk state: OK
Alerts: Discord + App
```

Avoid turning the card into a wall of metrics.

## 2.3 Favorite detail page

Each favorite should have dedicated controls:

```text
EUR/USD
FOREX

★ Favorite

MONITORING
Analysis                    ON
Signal alerts               ON

SCHEDULE
Frequency                   Every 5 minutes
Timezone                    User-selected / explicit
Trading session             Any / London / New York / overlap / custom

TIMEFRAMES
Execution timeframe         15m
Context timeframes          1H, 4H

ANALYSIS
Strategy                    Model Council
Bot / squad                 Trading Team
Minimum evidence threshold  configurable
Minimum R:R                 configurable

NOTIFICATIONS
FX App                      ON
Discord                     ON

NOTIFY WHEN
BUY confirmed               ON
SELL confirmed              ON
Signal changes              ON
Invalidated                 ON
Expired                     optional
TP reached                  ON
SL reached                  ON
WATCH                       optional
NO TRADE                    optional
Every analysis              OFF by default

[Generate Report Now]
[Run Analysis Now]
[Send Test Alert]
[Save]
```

---

# 3. FREQUENCY IS NOT TRADE FREQUENCY

This must be embedded in the product semantics.

If a favorite is configured to run every 5 minutes:

```text
10:00 analyze
10:05 analyze
10:10 analyze
10:15 analyze
...
```

that does **not** mean:

```text
10:00 signal
10:05 signal
10:10 signal
10:15 signal
...
```

Possible states are:

```text
NO_SETUP
WATCHING
POTENTIAL_LONG
POTENTIAL_SHORT
LONG_CONFIRMED
SHORT_CONFIRMED
BLOCKED
INVALIDATED
EXPIRED
TP1_HIT
TP2_HIT
STOP_HIT
CLOSED
```

A repeated state should normally be deduplicated.

Example:

```text
10:00 LONG_CONFIRMED
10:05 LONG_CONFIRMED
10:10 LONG_CONFIRMED
```

Do not send three identical phone alerts.

But:

```text
LONG_CONFIRMED -> INVALIDATED
```

must create a meaningful event.

---

# 4. CENTRAL SIGNAL / RESEARCH EVENT CONTRACT

Every strategy and bot should return a standardized machine-readable envelope.

Do not let each strategy invent incompatible output.

Recommended conceptual schema:

```json
{
  "event_id": "unique-id",
  "instrument_id": "canonical-id",
  "symbol": "EURUSD",
  "asset_class": "forex",

  "generated_at": "ISO-8601",
  "market_data_asof": "ISO-8601",
  "provider": "provider-name",

  "strategy_id": "trend_pullback_v2",
  "strategy_version": "2.1.0",
  "bot_id": "trend_bot_v4",
  "model_version": "optional",

  "execution_timeframe": "15m",
  "context_timeframes": ["1h", "4h"],

  "state": "LONG_CONFIRMED",
  "direction": "LONG",

  "entry": 1.1725,
  "entry_zone": [1.1720, 1.1730],
  "stop_loss": 1.1685,
  "take_profits": [1.1760, 1.1800],
  "risk_reward": 2.4,

  "expires_at": "ISO-8601",
  "invalidation": "15m close below 1.1690",

  "market_regime": "TRENDING",
  "technical_summary": "...",
  "fundamental_summary": "...",
  "news_risk": "MEDIUM",

  "raw_model_score": 0.78,
  "calibrated_confidence": null,
  "confidence_label": "UNVERIFIED_SCORE",

  "model_votes": [],
  "supervisor_decision": "APPROVE",
  "risk_decision": "APPROVE",

  "evidence": [],
  "risks": [],
  "no_trade_conditions": []
}
```

## Critical confidence rule

Do not display an arbitrary model score as a literal probability of success.

Until historical calibration exists, UI language should distinguish:

- `Model score`
- `Agreement score`
- `Evidence score`

from:

- `Calibrated probability`

A 78/100 model score is **not automatically a 78% chance of profit**.

---

# 5. WHAT A COMPLETE TRADE SIGNAL MUST CONTAIN

When the system decides that a paper setup is actionable, the report should include:

- Asset / canonical instrument
- Asset class
- Direction
- Entry or entry zone
- Stop loss
- One or more take-profit levels
- Risk/reward calculation
- Execution timeframe
- Supporting timeframes
- Strategy name + version
- Bot / model identity where relevant
- Signal creation timestamp
- Market-data timestamp
- Data provider
- Expiration
- Invalidation condition
- Market regime
- Technical evidence
- Fundamental/macro context when relevant
- News/event risk when available
- Model Council votes when used
- Supervisor decision
- Deterministic risk decision
- Paper-only status

If a required field cannot be calculated, the system must not silently invent it.

---

# 6. RISK GOVERNOR: HARD VETO

Preserve a strict separation:

```text
LLMs / AI agents
    ↓
Research and synthesis

Deterministic strategies
    ↓
Candidate setup

Supervisor
    ↓
Recommendation

Deterministic Risk Governor
    ↓
PERMISSION / VETO

Paper Execution
```

The Risk Governor must be able to block a recommendation.

Examples:

- missing stop loss;
- invalid target;
- R:R below policy;
- stale price data;
- high-impact event blackout if such a policy is configured;
- duplicate exposure;
- portfolio concentration;
- drawdown limit;
- invalid instrument;
- market closed where relevant;
- impossible price ordering;
- unsupported execution type.

No AI majority vote can bypass hard risk policy.

---

# 7. NEW ON-DEMAND REPORT GENERATOR

This is a core feature.

From any Bot, Strategy, Favorite, Model Council result, or Paper position, provide:

`Generate Report`

The report generator must support at least four report types.

## 7.1 Bot Report

Question answered:

> What is this bot doing, how does it work, how has it performed, and what evidence supports continuing to train it?

Include:

- Bot identity
- Version
- Purpose
- Assets
- Timeframes
- Inputs/features
- Strategy/model
- What "training" means for this bot
- Current status
- Last run
- Current recommendation
- Risk rules
- Historical test methodology
- Out-of-sample metrics
- Walk-forward metrics if available
- Paper metrics
- Sample size
- Drawdown
- Failure modes
- Regimes where it works / fails
- Recent drift
- Known limitations
- Promotion status
- Next recommended experiment

## 7.2 Strategy Report

Question answered:

> What exactly is this strategy, what are its rules, and has it survived proper validation?

Include:

- Strategy ID/name/version
- Thesis
- Allowed asset classes
- Allowed timeframes
- Entry rules
- Exit rules
- SL logic
- TP logic
- Position/risk logic
- Filters
- Regime assumptions
- Required data
- Backtest period
- Train/validation/test split
- Walk-forward results
- Costs/spread/slippage assumptions
- Sensitivity to parameters
- Known failure cases
- Paper performance
- Current status

## 7.3 Trade / Signal Report

Question answered:

> Why does this setup exist right now?

Include:

- all standardized signal fields;
- evidence;
- strongest bull case;
- strongest bear case;
- dissent;
- supervisor rationale;
- risk verdict;
- what would invalidate it;
- what needs to happen next.

## 7.4 Goal / Plan Report

The user wants to be able to ask:

> "What plan are we using to achieve X goal?"

Add a report type called:

`Goal Plan`

Examples:

- reduce maximum drawdown;
- improve a trend bot's out-of-sample Sharpe;
- improve signal precision;
- reduce false breakouts;
- improve BTC strategy robustness;
- compare two models;
- test a new candlestick hypothesis.

A Goal Plan report should contain:

```text
GOAL
SUCCESS METRICS
BASELINE
HYPOTHESIS
EXPERIMENT PLAN
DATA NEEDED
STRATEGIES/BOTS INVOLVED
RISK CONSTRAINTS
VALIDATION METHOD
PASS/FAIL THRESHOLD
CURRENT PROGRESS
WHAT CHANGED SINCE LAST REPORT
NEXT ACTION
STOP CONDITIONS
```

Do not let the system write vague "we will improve performance" plans.

---

# 8. REPORT FORMATS

The same underlying report data should be reusable in:

1. Full in-app report
2. Markdown export
3. JSON export
4. Short Discord embed/message
6. Daily digest
7. Future PDF export if useful

Do not generate five independent versions of the facts.

Generate a canonical report object and render it to channels.

---


# 10. DISCORD

Discord should be treated as a structured research/lab channel.

Suggested server/channel architecture:

```text
FX LAB
├── #morning-brief
├── #signals
├── #forex
├── #stocks
├── #crypto
├── #model-council
├── #risk-alerts
├── #paper-trades
├── #performance
├── #reports
└── #system-health
```

For V1 outbound alerts, Discord webhooks are sufficient.

Do not create one Discord bot per internal strategy.

Use a single notification layer and identify the source:

```text
TREND BOT
RISK GOVERNOR
MODEL COUNCIL
SUPERVISOR
SYSTEM HEALTH
```

---

# 11. USE ONE DISCORD NOTIFICATION ROUTER

Required architecture:

```text
Signal / Report / Health Event
        ↓
Event Store
        ↓
Notification Policy
        ↓
Notification Router
        ├── FX App
        └── Discord
```

Future channels can be added without changing strategy logic.

Conceptual interface:

```python
class NotificationChannel:
    async def send(self, event, rendered_message): ...
    async def healthcheck(self): ...
```

Then:

- `DiscordChannel`
- `InAppChannel`

---

# 12. SCHEDULER

Support:

- 5m
- 10m
- 15m
- 30m
- 1h
- 2h
- 4h
- daily
- custom cron/schedule
- session-aware schedules where useful

Important:

Schedules must be persisted.

Do not implement production scheduling as only:

```python
while True:
    sleep(300)
```

At minimum store:

```text
alert_rule
id
favorite_id
enabled
schedule_type
interval_minutes
cron_expression
timezone
execution_timeframe
context_timeframes
strategy_id
bot_id
min_evidence
min_rr
channels
event_types
quiet_hours
last_run_at
next_run_at
```

After application restart, schedules must recover.

---

# 13. EVENT STORE + JOURNAL

Discord is a delivery mechanism, not the database.

Persist every important event before delivery.

Recommended event families:

```text
analysis.completed
signal.state_changed
signal.confirmed
signal.invalidated
signal.expired
risk.vetoed
paper.order_created
paper.order_filled
paper.position_closed
report.generated
notification.requested
notification.sent
notification.failed
provider.stale
provider.recovered
bot.degraded
system.health_changed
```

Store enough information to reconstruct what the system believed at that moment.

---

# 14. NOTIFICATION DEDUPLICATION + RATE CONTROL

Implement:

- event IDs;
- state transition checks;
- deduplication keys;
- retry policies;
- rate limits;
- exponential backoff where appropriate;
- delivery status;
- last error;
- delivery timestamp.

Example dedup key:

```text
EURUSD:15m:trend_pullback_v2:LONG_CONFIRMED
```

A repeated unchanged analysis should not spam the user.

---

# 15. MORNING BRIEF

Provide a configurable scheduled report:

```text
FX MORNING BRIEF

Favorites scanned: 12
Actionable paper setups: 1
Watching: 4
No setup: 7
Risk blocks: 0

TOP RESEARCH CANDIDATE
EUR/USD
Bias: bullish
State: WATCHING
Strategy: Trend Pullback
What must happen: retest + confirmation

MAJOR EVENT RISKS
...

SYSTEM
Market data: healthy
Scheduler: healthy
Discord: healthy
```

Do not force a "top trade" if none exists.

---

# 16. EVENING REVIEW

Example:

```text
FX PAPER REVIEW

Analyses: 126
New signals: 3
Risk vetoes: 2
Paper trades opened: 2
Paper trades closed: 1

Net paper P&L: ...
Max drawdown today: ...
Fees/slippage simulated: ...

BEST EVIDENCE-ADJUSTED STRATEGY
...

WORST / DEGRADED STRATEGY
...

SIGNALS AVOIDED BY RISK GOVERNOR
...

BOT PROMOTION CHANGES
...

DATA/PROVIDER INCIDENTS
...
```

No celebratory "winning bot" language based on a tiny sample.

---

# 17. MULTI-BRAIN / TRADING TEAM INTEGRATION

The existing multi-brain concept should feed Favorites reports and scheduled analyses.

Recommended modes:

```text
Single
Compare
Council
Fusion (if actually supported/configured)
Trading Team
Auto
```

The flagship mode should be `Trading Team`.

Suggested specialist roles:

- Macro Brain
- Technical Brain
- Momentum Brain
- Quant Brain
- News Brain
- Bear / Red Team Brain
- Risk Research Brain
- Supervisor

All brains should receive the same timestamped verified market context.

Do not let individual LLMs fetch or invent inconsistent prices independently unless tool provenance is explicit.

---

# 18. STRUCTURED OUTPUT FOR BRAINS

Every brain should return a compatible schema.

Example:

```json
{
  "stance": "BUY|SELL|WAIT",
  "evidence_score": 72,
  "thesis": "...",
  "invalidation": "...",
  "risks": [],
  "missing_data": [],
  "no_trade_conditions": []
}
```

Entry/SL/TP values can be included when the role is authorized to propose them, but deterministic validators must verify them.

---

# 19. SUPERVISOR

Supervisor responsibilities:

```text
collect analyses
identify consensus
identify disagreement
identify missing evidence
compare historical reliability
consider regime
ask the risk layer
issue research verdict
```

Supervisor statuses:

- APPROVE_FOR_PAPER
- WAIT
- BLOCK
- INSUFFICIENT_DATA
- PROVIDER_ERROR
- STALE_DATA

Supervisor is governance, not magic.

---

# 20. RED-TEAM / CHALLENGE MODE

Add:

- Challenge this verdict
- Ask Bear Committee
- Ask Bull Committee
- What would change this decision?
- Backtest this thesis
- Show historical analogues
- Explain disagreement

This is especially useful to reduce correlated consensus among multiple LLMs.

---

# 21. MODEL / AGENT SCORECARDS

Store per model and role:

```text
model_id
provider
role
task_type
latency
cost
tokens
structured_output_valid
prediction
raw_score
calibrated_score
paper_outcome
MAE/MFE where relevant
regime
asset_class
timeframe
```

Evaluate with metrics appropriate to the task, potentially including:

- Brier score
- calibration error
- precision
- recall
- false-positive rate
- abstention quality
- expectancy
- profit factor
- Sharpe/Sortino where appropriate
- drawdown
- regime stability

Do not optimize solely for directional accuracy.

---

# 22. STRATEGY RESEARCH LESSONS FROM THE PROVIDED TRADING SOURCES

The external trading videos should be treated as **hypothesis sources, not truth**.

## 22.1 Simple level-based / "sneaky pivot" concept

The researched summary of the provided video describes a very simple 15-minute approach using:
- previous day's high/low;
- additional swing highs/lows;
- predefined horizontal levels;
- confirmation around those levels;
- explicit stop/target logic.

Useful lesson for FX:
- simplicity can improve explainability;
- level-based hypotheses are easy to encode and backtest;
- predefined levels reduce discretionary hindsight.

But:
- promotional P&L claims must not be accepted as validation;
- false breaks/liquidity sweeps matter;
- rules must be made exact;
- the strategy must be tested out-of-sample;
- spread, slippage and regime dependence must be modeled.

Create a research candidate, not a production strategy.

Suggested experiment ID:

`PREV_DAY_LEVEL_REACTION_V1`

Possible features:
- previous-day high;
- previous-day low;
- distance to level;
- first-touch vs repeated touch;
- wick beyond level;
- close back inside;
- candle range/ATR;
- time-of-day;
- session;
- trend context;
- volume where reliable;
- volatility regime.

Test:
- continuation versus rejection;
- false breakout rate;
- first touch vs later touches;
- different sessions;
- different assets.

## 22.2 Candlestick pattern material

The second provided video is associated with candlestick-pattern education.

Useful lesson:
- candles are OHLC summaries;
- pattern labels can be encoded as features;
- context matters more than the pattern name alone.

Do not build a bot that trades "hammer = buy" or "engulfing = sell" in isolation.

Research:
- pattern + trend context;
- pattern + support/resistance;
- pattern + volatility;
- pattern + session;
- pattern + volume;
- forward returns after pattern;
- multiple holding horizons.

Every candlestick rule must be objectively computable.

## 22.3 Beginner trading concepts

The third provided video is titled "Trading Explained For Complete Beginners - In 17 Minutes."

Use beginner material for:
- product education;
- glossary;
- onboarding;
- clarifying long/short, risk, order types, candles, leverage, etc.

Do not use beginner content as evidence that a strategy has edge.

---

# 23. GOOSE RESEARCH: WHAT IS RELEVANT TO FX

The `aaif-goose/goose` project is a general-purpose native open-source AI agent with:
- desktop app;
- CLI;
- API;
- multiple AI providers including Ollama and OpenRouter;
- MCP-based extensions;
- reusable recipes;
- scheduling;
- subagents / delegated tasks.

Important: do not blindly embed Goose as a dependency.

First ask:

> Which architectural patterns from Goose solve an FX problem better than our current implementation?

## 23.1 Recipes

Goose recipes package:
- prompts/instructions;
- settings;
- tools/extensions;
- parameters;
- structured output;
- subrecipes.

FX equivalent:

# Strategy / Research Recipes

Examples:
- `analyze_favorite.yaml`
- `generate_bot_report.yaml`
- `daily_watchlist_brief.yaml`
- `strategy_red_team.yaml`
- `paper_trade_postmortem.yaml`

This is highly relevant.

## 23.2 Scheduled recipes

Goose supports scheduling reusable recipes.

Architectural lesson:
- scheduled work should reference versioned reusable workflow definitions;
- scheduled runs should produce inspectable sessions/results;
- schedules should be manageable;
- a schedule should have run history.

FX should adopt these concepts whether or not Goose code itself is used.

## 23.3 Subagents

Goose supports specialist delegated subagents in isolated sessions/context.

FX equivalent:

```text
Main Analysis Recipe
├── Technical Research
├── Macro Research
├── Quant Research
├── Bear Case
└── Risk Research
        ↓
Supervisor
```

This maps closely to the Trading Team concept.

## 23.4 MCP extensions

Goose uses MCP as an extensibility mechanism.

Potential FX lesson:
- keep external tools/providers behind explicit interfaces;
- consider MCP only where it improves interoperability;
- do not force internal deterministic market/risk code through MCP merely for fashion.

Possible future MCP-facing tools:
- market data query;
- economic calendar;
- paper portfolio read-only tools;
- strategy result lookup;
- report lookup.

Execution permissions must remain tightly controlled.

## 23.5 Custom distributions / embedded API

Goose can be distributed with configured providers/extensions and can be used through an API.

Potential future idea:
- a purpose-built "FX Research Agent" distribution/profile;
- local-first orchestration around OpenRouter/Ollama;
- recipe library specifically for quant QA, reports, and research.

Again: architecture first, dependency second.

---

# 24. RECOMMENDED FX RECIPE CONCEPT

Create an internal abstraction inspired by recipes:

```yaml
id: favorite-market-analysis-v1
name: Favorite Market Analysis
version: 1.0.0

inputs:
  instrument_id: required
  execution_timeframe: required
  strategy_id: optional

steps:
  - validate_instrument
  - fetch_market_snapshot
  - verify_freshness
  - compute_features
  - detect_regime
  - run_deterministic_strategies
  - run_selected_ai_team
  - red_team
  - supervisor
  - risk_validate
  - create_event
  - persist_report
  - route_notifications

output_schema:
  report: FavoriteAnalysisReportV1
```

Every scheduled analysis should store the recipe/workflow version used.

---

# 25. UI: FAVORITES COMMAND CENTER

Recommended structure:

```text
┌────────────────────────────────────────────────────────────┐
│ FAVORITES                                 PAPER / RESEARCH │
├────────────────────────────────────────────────────────────┤
│ Search / Add Asset                                           │
│ [asset class] [market] [universe] [asset] [☆ add]           │
├────────────────────────────────────────────────────────────┤
│ FILTERS                                                      │
│ All | Signals | Watching | No Setup | Risk Blocked | Errors │
├────────────────────────────────────────────────────────────┤
│ EUR/USD    WATCHING      15m   Model Council   Next 12:05    │
│ BTC/USD    NO_SETUP      15m   Trend+Momentum  Next 12:05    │
│ AAPL       BLOCKED       1h    Breakout        Next 13:00    │
└────────────────────────────────────────────────────────────┘
```

Clicking an item opens:
- market view;
- current report;
- strategy;
- schedule;
- notification policy;
- history;
- bot opinions;
- risk;
- performance.

---

# 26. UI: REPORT BUTTONS EVERYWHERE RELEVANT

Add contextual actions:

On Bot page:
`Generate Bot Report`

On Strategy page:
`Generate Strategy Report`

On Favorite:
`Generate Market Report`

On Model Council:
`Generate Council Report`

On Signal:
`Generate Signal Report`

On experiment/goal:
`Generate Goal Plan`

Add:
`Export .md`

This is particularly useful for Codex handoffs and research review.

---

# 27. HEALTH / OBSERVABILITY

Add real service health:

```text
Market Data       HEALTHY / STALE / OFFLINE
Scheduler         HEALTHY / DEGRADED
Database          HEALTHY
Discord          CONNECTED / NOT CONFIGURED / FAILED
Ollama            RESPONDING / OFFLINE
Kimi              RESPONDING / NOT CONFIGURED
OpenRouter        RESPONDING / NOT CONFIGURED
Model Council     HEALTHY / DEGRADED
Paper Engine      HEALTHY
```

A green indicator must be based on a meaningful recent check.

If market data becomes stale:
- suspend new actionable signals;
- alert once;
- do not spam;
- notify when recovered.

---

# 28. SECURITY

Secrets:
- `.env` or appropriate secret manager;
- never frontend;
- never git;
- never report exports;
- never logs.

Review:
- `.gitignore`;
- historical commits if relevant;
- API response leakage;
- browser devtools exposure;
- structured log redaction.

Discord webhook URLs are credentials.

---

# 29. LOCAL-RUNTIME LIMITATION

Current FX is local-first.

If the Mac:
- sleeps;
- shuts down;
- loses connectivity;
- stops the backend;

scheduled analysis and alerts stop.

Expose this honestly in the UI:

```text
Scheduler runtime: LOCAL
Background alerts require this machine and FX services to remain running.
```

Future:
- optional VPS/cloud worker;
- same event/report contracts;
- no need to rewrite strategy logic.

Do not prematurely cloud-migrate the whole platform just for notifications.

---

# 30. PAPER-BOT PROMOTION LIFECYCLE

Continue using an evidence-based lifecycle:

```text
CANDIDATE
↓
RESEARCH
↓
BACKTESTED
↓
OUT_OF_SAMPLE_VALIDATED
↓
WALK_FORWARD_VALIDATED
↓
PAPER_TRADING
↓
PAPER_PROVEN
↓
ELIGIBLE_FOR_HUMAN_REVIEW
↓
FUTURE_LIVE_CANDIDATE
```

No automation in this specification should promote a bot directly to live trading.

---

# 31. IMPLEMENTATION ARCHITECTURE

Adapt names to the existing repository rather than forcing this exact tree.

Conceptual modules:

```text
services/
  favorites/
    registry
    favorites_service
    monitoring_policy

  research/
    workflow_registry
    report_generator
    report_schema
    evidence

  signals/
    signal_schema
    state_machine
    deduplication
    invalidation

  notifications/
    router
    policies
    discord
    in_app
    templates

  scheduling/
    schedule_store
    scheduler
    run_history

  intelligence/
    market_context
    model_council
    trading_team
    supervisor
    red_team

  risk/
    governor
    policies

  evaluation/
    strategy_scorecard
    bot_scorecard
    model_scorecard
    calibration

  journal/
    events
    reports
    notifications
```

---

# 32. DATABASE / PERSISTENCE ENTITIES

Recommended conceptual entities:

## favorites
- id
- instrument_id
- enabled
- created_at

## monitoring_rules
- favorite_id
- schedule
- timezone
- strategy_id
- bot/squad
- timeframes
- thresholds
- notification policy

## analysis_runs
- run_id
- workflow_id/version
- instrument
- start/end
- status
- data_asof
- provider
- error

## signals
- standardized signal fields

## reports
- report_id
- report_type
- subject_id
- schema_version
- generated_at
- content_json
- markdown_snapshot

## notification_deliveries
- event_id
- channel
- status
- attempt
- sent_at
- error_code

## goal_plans
- goal
- baseline
- success criteria
- experiment plan
- status
- progress snapshots

---

# 33. API CONCEPTS

Adapt to current API conventions.

Potential routes:

```text
GET    /api/favorites
POST   /api/favorites
DELETE /api/favorites/{id}

GET    /api/favorites/{id}
PUT    /api/favorites/{id}/monitoring
POST   /api/favorites/{id}/analyze
POST   /api/favorites/{id}/report

POST   /api/reports/bot/{bot_id}
POST   /api/reports/strategy/{strategy_id}
POST   /api/reports/signal/{signal_id}
POST   /api/reports/goal

GET    /api/reports/{report_id}
GET    /api/reports/{report_id}/markdown

GET    /api/notifications/health
POST   /api/notifications/discord/test

GET    /api/schedules
POST   /api/schedules
PUT    /api/schedules/{id}
POST   /api/schedules/{id}/run-now
POST   /api/schedules/{id}/pause
```

Do not blindly add these if equivalent routes already exist.

---

# 34. ALERT POLICY EXAMPLE

The user should be able to choose:

```text
Alert immediately when:
[x] new BUY/SELL paper signal
[x] signal invalidated
[x] stop hit
[x] take profit hit
[x] risk veto
[x] market feed failure

Optional:
[ ] WATCHING
[ ] NO TRADE
[ ] every analysis

Digest:
[x] morning brief
[x] evening review
```

Default toward low-noise.

---

# 35. REPORT PROMPT CONTRACT

If an LLM helps synthesize a report, give it facts and enforce:

```text
You are a research-report synthesizer.

You may:
- summarize provided evidence;
- explain strategy logic;
- identify contradictions;
- identify missing evidence;
- describe deterministic risk decisions.

You may not:
- invent prices;
- invent provider status;
- invent backtest metrics;
- invent P&L;
- invent confidence calibration;
- claim a strategy has edge without supplied evidence;
- rewrite a WAIT/BLOCK decision as a BUY/SELL recommendation.

Every factual market or performance claim must map to supplied structured data.
Unknown values must remain Unknown / Not available.
```

---

# 36. QA ACCEPTANCE TESTS

Codex must test the feature end-to-end.

## Favorites
- add stock;
- add FX pair;
- add crypto;
- add index if supported;
- reject unresolved symbol;
- remove favorite;
- persistence after restart.

## Scheduling
- create 5m rule;
- create daily rule;
- pause;
- resume;
- run now;
- restart and verify persistence;
- verify timezone behavior.

## Signals
- NO_SETUP;
- WATCHING;
- LONG;
- SHORT;
- invalidation;
- expiration;
- duplicate unchanged state;
- changed state.

## Report generator
- bot report;
- strategy report;
- signal report;
- goal plan;
- missing-data behavior;
- Markdown export.

## Discord
- not configured;
- valid webhook;
- invalid webhook;
- retry;
- formatting;
- deduplication.

## Data safety
- stale market data;
- missing candle;
- timestamp mismatch;
- unsupported asset.

## Risk
- missing SL -> block;
- invalid TP -> block;
- R:R violation -> block;
- stale data -> block;
- duplicate exposure rule if configured.

## UI
- responsive;
- loading;
- error;
- empty;
- status truthfulness;
- no raw JSON in user-facing views.

---

# 37. REQUIRED AUTOMATED TESTS

Add tests appropriate to the codebase for:

- signal schema validation;
- state transition rules;
- deduplication;
- R:R calculation;
- risk vetoes;
- report schema;
- scheduler persistence;
- notification router;
- Discord template rendering;
- secrets not serialized;
- market-data timestamp freshness;
- bot report missing-data behavior.

---

# 38. OBSERVABILITY EVENTS

Structured logs/events:

```text
FAVORITE_CREATED
MONITORING_RULE_UPDATED
SCHEDULE_TRIGGERED
ANALYSIS_STARTED
MARKET_DATA_RESOLVED
MARKET_DATA_STALE
STRATEGY_COMPLETED
COUNCIL_COMPLETED
SUPERVISOR_COMPLETED
RISK_APPROVED
RISK_VETOED
SIGNAL_STATE_CHANGED
REPORT_GENERATED
NOTIFICATION_QUEUED
DISCORD_SENT
DISCORD_FAILED
ANALYSIS_COMPLETED
ANALYSIS_FAILED
```

Never log secrets.

---

# 39. HANDS-OFF CODEX EXECUTION PLAN

Execute in this order:

## Phase A — Discovery
1. Read repository instructions.
2. Map current services.
3. Find existing Favorites/watchlist code.
4. Find scheduler.
5. Find signal representation.
6. Find notification code.
7. Find Model Council/Supervisor.
8. Find report/export code.
9. Find paper execution and risk.
10. Find DB/persistence.

## Phase B — Architecture decision
Write a short implementation plan using existing abstractions.

## Phase C — Core contracts
Implement or unify:
- instrument ID;
- signal/event schema;
- report schema;
- state machine.

## Phase D — Favorites
Implement persistent watchlist and configuration.

## Phase E — Report Generator
Implement canonical reports + Markdown export.

## Phase F — Scheduler
Persistent jobs + run history.

## Phase G — Notification Router
In-app + Discord.

## Phase H — Intelligence integration
Connect strategy/council/supervisor/risk results.

## Phase I — Journal/evaluation
Persist analysis + notification + outcome lineage.

## Phase J — UI
Favorites command center + report actions + settings/health.

## Phase K — QA
Run acceptance suite; fix verified defects.

---

# 40. FINAL CODEX DELIVERABLES

Create/update documentation such as:

```text
docs/FAVORITES_ALERTS_ARCHITECTURE.md
docs/REPORTING_SYSTEM.md
docs/NOTIFICATION_SYSTEM.md
docs/SIGNAL_CONTRACT.md
docs/QA/FAVORITES_ALERTS_QA.md
```

Use existing repo conventions if different.

Final response to user must state:

1. What existed already.
2. What was implemented.
3. Exact files changed.
4. Database/schema changes.
5. Discord status.
7. Scheduler status.
8. Report-generator status.
9. Signal state-machine status.
10. Risk-gate status.
11. Tests run.
12. Passed/failed/blocked.
13. Known limitations.
14. How to use the feature.
15. What remains for the next phase.

Do not say only "done."

---

# 41. NON-NEGOTIABLE PRODUCT PRINCIPLES

1. PAPER ONLY.
2. Frequent analysis does not imply frequent trading.
3. WAIT / NO TRADE is a successful possible output.
4. Risk layer can veto.
5. LLMs do research; deterministic code owns hard risk.
6. Every market value has provider + timestamp provenance.
7. Confidence is not a probability until calibrated.
8. Alerts are state-driven, deduplicated and low-noise.
9. Discord is a delivery channel, not system-of-record.
10. Every signal/report can be reconstructed from stored evidence.
11. Strategy claims must be validated, not believed.
12. Promotional trading content is hypothesis inspiration only.
13. No hidden live-execution path.
14. No fake green status indicators.
15. No raw backend JSON in normal UX.
16. Unknown is better than fabricated.
17. Version workflows, strategies, models and reports.
18. Preserve enough evidence for forensic postmortems.
19. Reward robustness over lucky P&L.
20. Build for future auditability.

---

# 42. SOURCE REVIEW / RESEARCH NOTES

## User-provided prior architecture documents

The supplied project materials already established two important foundations:

### A. Favorites + Discord alert architecture
They define:
- Favorites/watchlist;
- per-asset schedules;
- standardized signals;
- stop loss/take profit;
- risk veto;
- signal lifecycle;
- Discord alerts and research channels;
- persistent signal journal;
- health monitoring;
- paper-only execution.

This handoff consolidates and converts those concepts into an implementation contract.

### B. Multi-brain / OpenRouter architecture
They define:
- Single / Compare / Council / Fusion / Trading Team concepts;
- standardized model output;
- supervisor;
- deterministic risk engine;
- model scoring;
- market context;
- cost/routing concerns.

This handoff connects that intelligence layer directly to Favorites, reports and scheduled notifications.

## aaif-goose/goose

Repository:
https://github.com/aaif-goose/goose

Key relevant properties reviewed:
- general-purpose local AI agent;
- desktop/CLI/API;
- multi-provider support;
- MCP extensions;
- recipes;
- scheduling;
- subagents;
- structured reusable workflows.

Official documentation reviewed:
- https://goose-docs.ai/docs/guides/recipes/
- https://goose-docs.ai/docs/guides/recipes/session-recipes/
- https://goose-docs.ai/docs/guides/recipes/subrecipes/
- https://goose-docs.ai/docs/tutorials/subagents/

Use Goose as an architectural reference unless a direct dependency clearly improves the existing FX implementation.

## Discord

Official webhook docs:
https://docs.discord.com/developers/resources/webhook

Relevant:
- webhooks are a low-friction way to post to channels;
- initial outbound alerts do not require a full Discord bot;
- webhook execution supports normal content and richer message payloads.

## Trading video: simple level strategy

Provided URL:
https://www.youtube.com/watch?v=zspMXJVbfAY

Research identified it as:
`How Trading Like an Idiot Makes Me $10,000/Month (15 Minutes a Day)`

Extracted concept:
- 15m timeframe;
- previous-day high/low;
- swing levels;
- confirmation around predefined levels;
- simple stop/target logic.

Treat as a research hypothesis only.

## Trading video: candlesticks

Provided URL:
https://www.youtube.com/watch?v=m4WOwgUMQuc

Research identifies it as candlestick-pattern educational material, commonly referenced as:
`The BEST Candlestick Pattern Guide You'll EVER FIND`

Use for:
- objective candle feature definitions;
- education;
- research hypotheses.

Do not assume named patterns have edge.

## Trading beginner video

Provided URL:
https://www.youtube.com/watch?v=8LRQIDAzyv8

Title observed:
`Trading Explained For Complete Beginners - In 17 Minutes`

Use primarily for educational/onboarding concepts, not strategy validation.

## Google AI Mode share links

Provided:
- https://share.google/aimode/9HyH3bC6qxIYQk6Wr
- https://share.google/aimode/CuUbEFfRVLzIFk2QT
- https://share.google/aimode/Eo0RkZuvYZckwICEY

Direct fetching of these share URLs was unavailable in the research environment.

Do **not** fabricate their contents.

The two uploaded Markdown source files contain substantial prior research on:
- Favorites/alerts/signals/Discord;
- multi-brain/OpenRouter/council/supervisor architecture.

Codex should treat this handoff as the consolidated implementation brief. If the user later provides exported text from the Google AI Mode shares, ingest it as an additional source and reconcile it explicitly against this version.

---

# 43. FINAL NORTH STAR

The final system should feel like this:

```text
                        FAVORITES
                            ↓
                     Persistent Schedule
                            ↓
                    Fresh Market Snapshot
                            ↓
                      Feature / Regime
                            ↓
                    Deterministic Strategy
                            ↓
                       Specialist Team
                            ↓
                         Red Team
                            ↓
                         Supervisor
                            ↓
                   Deterministic Risk Gate
                       ↙           ↘
                    BLOCK         APPROVE
                      ↓              ↓
                  Journal       Paper Signal
                                    ↓
                              Event / Report
                                    ↓
                         Notification Policy
                          ↙       ↓       ↘
                       FX App  Discord
                                    ↓
                              Paper Outcome
                                    ↓
                             Evaluation Store
                                    ↓
                         Bot/Strategy Scorecard
                                    ↓
                             Next Experiment
```

The user should be able to open FX and answer, in plain English:

- What are my favorite markets?
- What is being monitored?
- When will each asset be analyzed next?
- What changed?
- Why did I receive this alert?
- Which bot/strategy generated it?
- What evidence was used?
- What did the other bots think?
- What did the supervisor decide?
- Did the risk governor approve it?
- What is the exact paper setup?
- When does it expire?
- What invalidates it?
- What happened afterward?
- How has this bot performed out-of-sample?
- Is it improving?
- What plan are we following to improve it?
- What experiment comes next?
- Are Discord/data/AI/scheduler actually healthy?

If the application cannot answer those questions, the feature is not finished.

---

# 44. ONE-SENTENCE IMPLEMENTATION STATEMENT

> **Turn FX Favorites into an evidence-driven monitoring and reporting command center: persist favorite instruments and per-asset schedules, run standardized strategy/model-council analyses, route every candidate through a deterministic risk governor, store the full event/report lineage, and deliver only meaningful state changes or requested digests through the FX app, Discord—while keeping all execution strictly paper-only and making every bot, strategy and goal explainable through an on-demand report.**

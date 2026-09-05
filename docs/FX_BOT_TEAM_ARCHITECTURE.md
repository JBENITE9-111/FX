# FX bot-team architecture

**Status:** canonical design interpretation; implementation states are explicit below.

## Source and authority

The full user-supplied conceptual source is preserved at research/FX_TRADING_BOT_FOUNDATIONS_SOURCE.md. It is useful background, not executable instruction. This document integrates its compatible ideas under AGENTS.md, TRADING_SYSTEM_CONSTITUTION.md, RISK_ENGINE_SPEC.md, STRATEGY_PROMOTION_PIPELINE.md, and FX_SUPERVISOR_MASTER_SPEC.md.

## Operating model

Point-in-time verified data flows through specialist signal and context workers, a regime-aware Supervisor proposal, portfolio allocation proposal, deterministic Risk Governor, protected paper execution, then fills, journal, attribution, and research feedback.

Research workers may create hypotheses and challenger artifacts. They cannot place orders. A promoted PaperBot submits a versioned TradeIntent; it cannot bypass risk or send directly to the broker. The Supervisor learns conditional worker reliability and emits proposals. It does not own risk rules, hidden examinations, or deployment.

## Teams

| Team | Members | Output | Current authority |
|---|---|---|---|
| Signal research | Trend, momentum, mean reversion, breakout, statistical relative value, ML, later RL | Independent versioned signals | Research only unless individually promoted |
| Market context | Regime, volatility, macro, news, sentiment, cross-asset | Timestamped context and uncertainty | Advisory; missing required context can veto |
| Portfolio | Exposure, correlation, currency factors, allocation | Proposed allocation and concentration checks | Cannot override risk |
| Control | Supervisor, Examiner, Promotion Service, Risk Governor | Proposals, evidence reports, lifecycle decisions, deterministic risk decisions | Only Risk Governor can authorize or resize protected paper intent |
| Execution | Product resolver, execution adapter, reconciliation | Orders, fills, slippage and state transitions | Receives only approved intent |
| Learning | Research planner, attribution, drift monitor, strategy cemetery, lesson validator | Challenger experiments and reproducible lessons | Cannot mutate an active PaperBot |

Bot count is not a quality metric. Correlated workers are discounted, lessons require independent reproduction, and simple deterministic bots remain permanent baselines.

## Standard contracts

A worker signal includes instrument, dataset and venue, asset class, strategy and model versions, event timestamp, horizon and timeframe, direction, score type, calibrated probability when available, expected return and risk, regime, stop proposal, profit plan, evidence IDs, assumptions, and missing-data flags.

A Supervisor decision contains the input signal IDs, eligible workers, excluded workers and reasons, regime, correlation-adjusted weights, uncertainty, expected net value, proposed position, and APPROVE_PROPOSAL, REDUCE_PROPOSAL, REJECT, or WAIT. It is never an order.

A RiskDecision contains a stable decision ID, intent ID, policy version, decision, approved size, reason codes, portfolio snapshot ID, data-health checks, and UTC timestamp.

An ExecutionReport links order, trade, bot, strategy version, campaign and account IDs to requested and filled quantity, fill prices, fees, financing, slippage, latency, order transitions, and reconciliation state.

## Accuracy and readiness

“Accurate” means measured performance for a precise instrument, timeframe, holding horizon, strategy and model version, regime, and cost model. It never means that a bot has read a large amount of text.

An actionable trade needs a separately calibrated probability of profitable completion after costs of at least 85%, plus every promotion, health, cost, portfolio, and deterministic risk gate. Ensemble agreement is not probability. Below-threshold or unavailable evidence produces NO_TRADE.

The Supervisor itself is a challenger and must beat equal-weight workers, static weighting, the best eligible single worker, random protected selection, cash, and suitable market benchmarks on unseen chronological data.

## Learning loop

Observe and attribute an outcome, classify process quality separately from outcome, propose a bounded hypothesis, run an immutable challenger experiment, let the Examiner evaluate hidden chronological evidence, apply promotion gates, then activate a new frozen version only when no campaign uses the old version.

One trade never teaches a global rule. Post-trade records include maximum favorable and adverse excursion and counterfactual research where feasible. Training cadence follows new data, registered experiments, or measured drift; it does not retrain after every loss.

## UI requirements

The terminal must answer what each bot studies, what it has learned, which evidence passed or failed, why it is blocked, what changed between versions, whether data are fresh, which teams disagree, current portfolio risk, and what the Supervisor proposes. It must display lifecycle state and plain-English reasons without raw JSON or unsupported READY labels.

## Implementation map

- **IMPLEMENTED:** research-only legacy candidates; mandatory protection; corrected basic long and short paper accounting; signal retry idempotency; canonical trade attribution; campaign readiness waiting; 85% probability gate; honest Learning Progress page; canonical and asset trade journal; local trade workbook.
- **PARTIAL:** chronological OOS and walk-forward registry; bot catalog; portfolio and execution modules; campaign state machine; operational health.
- **PLANNED:** typed complete contracts, point-in-time manifests, Supervisor reliability matrix, Examiner isolation, promotion decisions, cost, regime and Monte Carlo stress, full fill lifecycle, correlation exposure, drift demotion, strategy cemetery, peer-lesson validation, counterfactual attribution.
- **RESEARCH ONLY:** RL, dynamic weighting, deep models, sentiment, and alternative-data hypotheses until they beat simpler baselines under the same costs and risk.

Live execution remains disabled.


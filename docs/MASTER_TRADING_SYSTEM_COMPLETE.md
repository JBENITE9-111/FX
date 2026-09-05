# MASTER TRADING SYSTEM
## Complete Strategy, Risk, Research, Execution, Monitoring, and Governance Specification

**Version:** 1.0  
**Purpose:** Single source of truth for building a serious multi-asset trading research and execution system for Forex, Crypto, Stocks, Futures, and Options.  
**Primary design principle:** Capital survival comes before profit.

---

# 1. SYSTEM MISSION

The system is not designed to “always find a trade.”

Its job is to:

1. Understand the market environment.
2. Decide whether an asset deserves attention.
3. Identify a valid strategy or setup.
4. Estimate expected return, downside, and uncertainty.
5. Measure portfolio-level risk.
6. Reject weak or dangerous trades.
7. Execute approved trades with realistic cost and liquidity controls.
8. Monitor open positions and thesis validity.
9. Reconcile the broker/exchange state continuously.
10. Review every result.
11. Learn through controlled research.
12. Never self-modify production behavior without validation and approval.

The preferred default state is:

`NO_TRADE`

A trade must earn the right to use capital.

---

# 2. TRADING SYSTEM CONSTITUTION

These rules are immutable unless explicitly changed by system governance.

1. Capital survival is more important than profit.
2. `NO_TRADE` is always a valid decision.
3. No AI model, LLM, strategy, or human-like agent can override deterministic risk limits.
4. Backtest performance alone can never authorize live deployment.
5. Holdout data cannot be reused for optimization after inspection.
6. Broker/exchange state is the source of truth for live positions and orders.
7. Unknown or inconsistent position state freezes new trading.
8. Strategies cannot modify or redeploy themselves directly.
9. Every production decision must be reproducible.
10. Every order must reference strategy version, model version, feature version, risk-policy version, and data provenance.
11. Every strategy must define explicit invalidation conditions.
12. Every live trade must have bounded risk.
13. Every strategy must demonstrate positive out-of-sample expectancy after realistic costs.
14. Correlated positions count as aggregated risk.
15. System health can veto a trade.
16. Missing, stale, conflicting, or corrupted data means `NO_TRADE`.
17. Expected transaction costs must be included before a trade is approved.
18. Slippage assumptions must be realistic and stress tested.
19. Liquidity must constrain position size.
20. No live strategy may depend on future information, revised future data, or leaked labels.
21. Production changes follow proposal → test → validation → holdout → shadow → paper → tiny capital → limited production → full promotion.
22. Drawdown can automatically reduce or suspend risk.
23. Strategy degradation must reduce capital before optimization is attempted.
24. All risk limits operate before execution.
25. Survival always outranks opportunity.

---

# 3. HIGH-LEVEL ARCHITECTURE

```text
MARKET DATA SOURCES
    ↓
DATA QUALITY + PROVENANCE LAYER
    ↓
MARKET INTELLIGENCE
    ↓
REGIME ENGINE
    ↓
ASSET SELECTION ENGINE
    ↓
STRATEGY ENSEMBLE
    ↓
COUNTER-THESIS / SKEPTIC ENGINE
    ↓
META DECISION ENGINE
    ↓
PORTFOLIO ENGINE
    ↓
DETERMINISTIC RISK ENGINE
    ↓
EXECUTION ENGINE
    ↓
BROKER / EXCHANGE
    ↓
RECONCILIATION
    ↓
TRADE MONITOR
    ↓
POST-TRADE REVIEW
    ↓
RESEARCH / LEARNING LAB
```

The Research / Learning Lab may propose changes.

It may never deploy them directly.

---

# 4. SYSTEM ROLES

## 4.1 Market Data Layer

Collect:

- OHLCV
- trades
- quote data
- order books
- spreads
- funding
- open interest
- options chains
- implied volatility
- implied volatility rank
- Greeks
- news
- economic calendar
- earnings
- corporate actions
- macro data
- on-chain metrics
- token unlocks
- stablecoin supply
- market breadth
- sector data
- benchmark indices
- broker/exchange position data

Possible technology roles:

- OpenBB: research and broad market data.
- MetaTrader 5: Forex/CFD execution and broker data.
- Hummingbot: crypto exchange execution and market making/order-book workflows.
- Freqtrade: crypto strategy research/backtesting/execution patterns.
- StockSharp: multi-market strategy research/execution components.
- Dedicated exchange/broker APIs: source-of-truth live execution and reconciliation.
- Parquet/DuckDB: canonical local research store.

---

# 5. DATA QUALITY ENGINE

No strategy receives raw unvalidated data.

Every observation should include:

```text
instrument_id
source
event_timestamp
received_timestamp
processed_timestamp
timezone
revision_status
quality_score
staleness
missing_flag
outlier_flag
corporate_action_adjustment
```

Checks:

- missing candles
- duplicate candles
- stale quotes
- impossible prices
- crossed books
- timestamp drift
- timezone mismatch
- wrong instrument mapping
- symbol changes
- split errors
- dividend adjustment errors
- exchange outage
- stale economic data
- revised macro releases
- incomplete options chains
- abnormal bid/ask spreads

If quality threshold fails:

`NO_TRADE`

---

# 6. INSTRUMENT REGISTRY

Every tradable instrument needs a canonical record.

Example:

```yaml
instrument_id: BTCUSDT_BINANCE_PERP
asset_class: crypto
base: BTC
quote: USDT
venue: binance
instrument_type: perpetual
tick_size: 0.1
lot_size: 0.001
min_notional: 5
timezone: UTC
funding: true
shortable: true
leverage_available: true
```

Never identify instruments only by ticker text.

---

# 7. MARKET INTELLIGENCE LAYER

The intelligence layer interprets context before technical entries are considered.

Inputs may include:

## Macro
- rates
- central-bank policy
- inflation
- payrolls
- GDP
- unemployment
- yield curve
- DXY
- VIX
- credit spreads
- liquidity conditions

## Stocks
- earnings
- guidance
- analyst revisions
- sector rotation
- index alignment
- relative strength
- short interest
- corporate actions

## Forex
- rate differentials
- central-bank expectations
- economic surprises
- currency-strength comparisons
- session behavior

## Crypto
- BTC dominance
- ETH/BTC
- stablecoin liquidity
- funding
- open interest
- liquidations
- exchange flows
- token unlocks
- on-chain behavior
- ETF flows when relevant
- protocol events

## Options
- IV
- IV rank
- skew
- term structure
- expected move
- delta
- gamma
- theta
- vega
- DTE
- liquidity

Output:

```text
market_context_score
macro_bias
event_risk
liquidity_condition
risk_on_off_state
```

---

# 8. REGIME ENGINE

Every strategy receives a market regime classification before activation.

Possible states:

```text
TREND_UP_LOW_VOL
TREND_UP_HIGH_VOL
TREND_DOWN_LOW_VOL
TREND_DOWN_HIGH_VOL
RANGE_LOW_VOL
RANGE_HIGH_VOL
BREAKOUT_EXPANSION
COMPRESSION
PANIC
EUPHORIA
ILLIQUID
EVENT_RISK
UNKNOWN
```

Each strategy specifies where it is:

- allowed
- reduced
- blocked

Example:

```yaml
strategy: trend_following
allowed:
  - TREND_UP_LOW_VOL
  - TREND_UP_HIGH_VOL
  - TREND_DOWN_LOW_VOL
  - TREND_DOWN_HIGH_VOL
reduced:
  - BREAKOUT_EXPANSION
blocked:
  - RANGE_LOW_VOL
  - UNKNOWN
```

---

# 9. ASSET SELECTION ENGINE

The system should first determine whether an asset is “in play.”

Parameters:

- catalyst
- unusual volume
- relative volume
- gap
- volatility
- liquidity
- spread
- sector movement
- benchmark alignment
- news intensity
- institutional attention proxy
- premarket activity
- order-book depth
- options activity
- funding anomaly
- open-interest change
- market-cap constraints
- shortability
- borrow availability

Output:

```text
IN_PLAY_SCORE: 0-100
```

If below threshold:

`NO_TRADE`

---

# 10. MULTI-TIMEFRAME STRUCTURE

Suggested timeframes depend on strategy, but the architecture should support:

- Monthly
- Weekly
- Daily
- 4H
- 1H
- 30m
- 15m
- 5m
- 1m
- tick/order-book

Typical hierarchy:

```text
Daily / 4H → regime and major structure
1H / 15m → setup context
5m → setup formation
1m / order book → execution
```

---

# 11. CORE MARKET STRUCTURE PARAMETERS

Track:

- higher highs
- higher lows
- lower highs
- lower lows
- swing points
- support
- resistance
- previous day high/low
- previous week high/low
- opening range
- premarket high/low
- VWAP
- anchored VWAP
- volume profile
- high-volume nodes
- low-volume nodes
- trendlines
- moving averages
- ATR
- realized volatility
- compression
- expansion
- range width
- breakout acceptance
- failed breakout
- failed breakdown
- retest quality
- trend slope
- distance from major structure

---

# 12. STRATEGY FAMILY FRAMEWORK

The system should host multiple specialist strategies instead of one giant strategy.

Primary families:

1. Trend following
2. Breakout
3. Breakout retest
4. Momentum continuation
5. VWAP pullback
6. Opening drive
7. Mean reversion
8. Range reversal
9. Support/rejection
10. Resistance/rejection
11. Liquidity sweep reversal
12. Statistical arbitrage
13. Relative-value trading
14. Volatility selling
15. Volatility buying
16. Event trading
17. Order-flow trading
18. Market making
19. Carry/funding strategies
20. Long-term allocation/regime strategies

Each strategy must be defined as a PlayBook.

---

# 13. PLAYBOOK SCHEMA

Every strategy should contain:

```yaml
strategy_id:
version:
asset_classes:
allowed_regimes:
blocked_regimes:

market_selection:
  catalyst_required:
  min_relative_volume:
  min_liquidity:
  max_spread:

context:
  higher_timeframe_bias:
  sector_alignment:
  benchmark_alignment:

setup:
  structure_conditions:
  volume_conditions:
  volatility_conditions:
  order_flow_conditions:

entry:
  trigger:
  order_type:
  max_chase_distance:

invalidation:
  structural_level:
  volatility_buffer:

exit:
  stop:
  target_1:
  target_2:
  trailing_logic:
  time_stop:

risk:
  default_risk:
  max_risk:
  portfolio_cap:

execution:
  allowed_order_types:
  max_slippage:
  max_participation_rate:

monitoring:
  thesis_failure_conditions:

statistics:
  minimum_samples:
  expected_win_rate:
  expected_r:
  expectancy:
  profit_factor:
  drawdown:
```

---

# 14. SMB-STYLE DECISION MODEL

Use this for catalyst-driven equities and momentum environments.

Sequence:

```text
CATALYST
↓
RELATIVE ATTENTION
↓
MARKET REGIME
↓
SECTOR CONTEXT
↓
KEY LEVELS
↓
PLAYBOOK MATCH
↓
PRICE ACTION
↓
VOLUME
↓
TAPE / ORDER FLOW
↓
LIQUIDITY
↓
INVALIDATION
↓
EXPECTED R:R
↓
SETUP QUALITY
↓
POSITION SIZE
↓
ENTRY
↓
MANAGEMENT
↓
REVIEW
```

Key parameters:

- catalyst quality
- relative volume
- gap size
- benchmark direction
- sector direction
- support/resistance
- VWAP
- tape speed
- bid/ask behavior
- absorption
- liquidity
- stop location
- expected reward
- setup quality
- MAE/MFE

---

# 15. RAYNER-STYLE STRUCTURE MODEL

Core framework:

```text
M = Market Structure
A = Area of Value
E = Entry Trigger
E = Exit
```

Questions:

1. Trend, range, or transition?
2. Where is the area of value?
3. How did price approach it?
4. Is there rejection?
5. Is there a valid entry trigger?
6. Where is structural invalidation?
7. What volatility buffer is required?
8. Where is opposing pressure?
9. Is reward/risk acceptable?
10. What position size follows from the stop?

Useful fields:

```text
market_structure
area_of_value
approach_quality
entry_trigger
structural_invalidation
atr_buffer
distance_to_opposing_structure
expected_r
```

---

# 16. TRADERTV-STYLE INTRADAY MODEL

Core concepts:

- VWAP
- volume
- key levels
- catalyst
- relative volume
- multi-timeframe context

VWAP pullback example:

```text
1. Asset is in play.
2. Strong opening impulse.
3. Relative volume elevated.
4. Direction established.
5. Controlled retracement.
6. Pullback volume contracts.
7. Price approaches VWAP.
8. VWAP holds or rejects.
9. Confirmation appears.
10. Enter.
11. Stop at thesis failure.
12. Target prior high/low or structural extension.
```

---

# 17. TASTYLIVE-STYLE OPTIONS MODEL

Use probability and volatility, not simple directional guessing.

Inputs:

- liquidity
- IV
- IV rank
- IV percentile
- skew
- term structure
- delta
- gamma
- theta
- vega
- DTE
- expected move
- buying power
- portfolio correlation
- defined vs undefined risk

Common research-style parameters:

```text
entry around ~45 DTE
manage around ~21 DTE
consider profit-taking around partial max-profit targets
small positions
many occurrences
```

These are research starting points, not immutable rules.

Every options strategy must be independently validated.

---

# 18. BENJAMIN COWEN-STYLE CRYPTO REGIME MODEL

This is not primarily an execution system.

It is a crypto allocation/regime engine.

Inputs:

- BTC trend
- BTC dominance
- ETH/BTC
- TOTAL market cap
- TOTAL2/TOTAL3
- stablecoin supply
- liquidity
- DXY
- rates
- equities
- volatility
- long-term regression/risk bands
- BTC relative strength
- altcoin relative strength

Possible output states:

```text
BTC_DOMINANT_RISK_ON
BTC_DOMINANT_RISK_OFF
ALT_ROTATION
ALT_EUPHORIA
CAPITULATION
ACCUMULATION
NEUTRAL
```

---

# 19. ADAM-KHOO-STYLE TREND MODEL

Useful architecture:

- trend structure
- multi-timeframe confirmation
- moving-average alignment
- retracement
- consolidation
- breakout
- volatility threshold
- defined stop
- fixed or adaptive reward multiple
- risk-based sizing

For Forex also consider:

```text
strong_currency
vs
weak_currency
```

Relative strength should be tested as a filter.

---

# 20. ORDER-FLOW ENGINE

Especially relevant for intraday stocks, futures, and crypto.

Features:

```text
spread
depth_5bps
depth_10bps
bid_depth
ask_depth
order_book_imbalance
microprice
trade_intensity
aggressor_buy_ratio
aggressor_sell_ratio
cancel_rate
replenishment_rate
absorption
sweep_activity
liquidity_vacuum
```

Example:

```text
OBI =
(BidDepth - AskDepth) /
(BidDepth + AskDepth)
```

No feature is assumed predictive.

Everything must be tested.

---

# 21. VOLUME ENGINE

Track:

- absolute volume
- relative volume
- volume z-score
- breakout volume
- pullback volume
- volume acceleration
- volume exhaustion
- volume profile
- delta where available
- session-adjusted volume

Common continuation structure:

```text
impulse volume ↑
pullback volume ↓
breakout volume ↑
```

---

# 22. VOLATILITY ENGINE

Track:

- ATR
- realized volatility
- historical volatility
- implied volatility
- IV rank
- IV percentile
- volatility term structure
- volatility skew
- volatility-of-volatility
- compression
- expansion

Outputs:

```text
LOW_VOL
NORMAL_VOL
HIGH_VOL
EXTREME_VOL
```

---

# 23. PREDICTION ENGINE

Do not restrict prediction to:

```text
UP
DOWN
```

Prefer return distribution estimates.

Example:

```text
P05: -2.4%
P25: -0.7%
P50: +0.6%
P75: +1.9%
P95: +4.2%
```

Possible horizons:

- 5m
- 15m
- 1H
- 4H
- 1D
- 1W

Prediction is not trade authorization.

---

# 24. EXPECTANCY ENGINE

For each strategy/regime pair calculate:

```text
win_probability
average_win_R
average_loss_R
expectancy_R
profit_factor
sample_size
confidence_interval
```

Formula:

```text
Expectancy =
P(win) × AvgWin
-
P(loss) × AvgLoss
```

Require positive expectancy after:

- fees
- spread
- slippage
- funding
- borrow
- market impact

---

# 25. HISTORICAL ANALOGUE ENGINE

Before approving a trade, search for historically similar states.

Feature vector may include:

```text
regime
volatility
trend
volume
ATR
RSI
VWAP distance
rates
VIX
DXY
funding
open_interest
correlations
liquidity
```

Retrieve similar observations and analyze:

- next-period return
- MAE
- MFE
- time-to-profit
- time-to-stop
- outcome distribution

This is evidence, not certainty.

---

# 26. COUNTER-THESIS ENGINE

Every candidate trade must be attacked before approval.

Bull thesis example:

```text
LONG BTC
```

Counter-thesis checks:

- resistance too close
- weak volume
- negative divergence
- excessive funding
- open interest overheating
- macro headwind
- benchmark weakness
- order-flow conflict
- poor liquidity
- historical analogues weak
- event risk imminent
- spread abnormal
- strategy degraded

Output:

```text
counter_thesis_score
fatal_objection
nonfatal_objections
```

If fatal objection exists:

`NO_TRADE`

---

# 27. META DECISION ENGINE

Possible outputs:

```text
STRONG_LONG
LONG
NO_TRADE
SHORT
STRONG_SHORT
```

Composite inputs:

```text
macro_score
regime_score
in_play_score
relative_strength_score
structure_score
location_score
volume_score
volatility_score
order_flow_score
fundamental_score
historical_expectancy
counter_thesis_score
liquidity_score
execution_feasibility
portfolio_impact
```

Do not use a simple average.

Weights should be strategy-specific and validated.

---

# 28. PORTFOLIO ENGINE

Trade-level risk is insufficient.

Track:

- gross exposure
- net exposure
- asset-class exposure
- sector exposure
- country exposure
- currency exposure
- crypto beta
- equity beta
- volatility exposure
- duration exposure
- factor exposure
- strategy exposure
- venue exposure
- correlated risk clusters

Example:

```text
Long BTC
Long ETH
Long SOL
Long MSTR
Long COIN
```

These are not five independent trades.

They may represent one concentrated crypto/risk-on exposure.

---

# 29. CORRELATION ENGINE

Track rolling correlations:

- 20-day
- 60-day
- 120-day
- stress-period correlation
- intraday correlation where relevant

Correlations are time varying.

Portfolio risk must use current and stress assumptions.

---

# 30. VOLATILITY TARGETING

Equal dollars are not equal risk.

Possible risk normalization:

```text
risk_contribution ≈ position_size × volatility
```

Higher-volatility assets should generally receive less capital for equal risk contribution.

---

# 31. DETERMINISTIC RISK ENGINE

This is the sovereign layer.

No strategy, LLM, or model can bypass it.

Required checks:

```text
max_risk_per_trade
max_risk_per_strategy
max_risk_per_asset
max_risk_per_asset_class
max_daily_loss
max_weekly_loss
max_monthly_drawdown
max_gross_exposure
max_net_exposure
max_leverage
max_correlated_cluster_risk
max_venue_exposure
max_order_notional
max_position_notional
max_open_positions
max_slippage
max_spread
min_liquidity
event_risk_block
data_quality_block
system_health_block
```

---

# 32. POSITION SIZING

Base formula:

```text
risk_per_unit = abs(entry - stop)

position_size =
allowed_trade_risk /
risk_per_unit
```

Final size:

```text
final_position_size =
min(
    risk_based_size,
    liquidity_based_size,
    portfolio_based_size,
    strategy_limit,
    venue_limit,
    broker_limit
)
```

Never calculate stop from desired position size.

Position size comes from risk.

---

# 33. SETUP-QUALITY SIZING

Optional and only after validation.

Example:

```text
score < 70 → NO_TRADE
70-79 → 0.25R
80-89 → 0.50R
90-94 → 0.75R
95+ → 1.00R
```

Exact thresholds must be empirically validated.

Hard risk limits remain unchanged.

---

# 34. DRAWDOWN-AWARE RISK

Example framework:

```text
normal state: 100% allowed risk
drawdown > 5%: 75%
drawdown > 8%: 50%
drawdown > 12%: 25%
drawdown > 15%: suspend and review
```

Exact values must be calibrated to strategy statistics.

---

# 35. RISK OF RUIN

Every strategy and portfolio should estimate:

```text
probability_of_ruin
expected_max_drawdown
95pct_drawdown
99pct_drawdown
expected_losing_streak
```

Primary objective:

```text
maximize long-run compounded return
subject to very low probability of ruin
```

---

# 36. TRANSACTION COST MODEL

Every backtest and live decision must include:

- commissions
- maker/taker fees
- spread
- slippage
- funding
- borrow fees
- overnight financing
- exchange fees
- market impact
- FX conversion
- taxes if relevant to research context

---

# 37. SLIPPAGE MODEL

Do not assume:

```text
fill_price = signal_price
```

Model:

```text
expected_slippage =
f(
    spread,
    volatility,
    order_size,
    order_book_depth,
    trading_volume,
    session,
    order_type,
    venue,
    latency
)
```

Stress test slippage at multiples of historical estimates.

---

# 38. LIQUIDITY-AWARE SIZING

Before execution:

```text
can this position be entered?
can it be exited?
what percentage of visible depth would we consume?
what is expected market impact?
```

The relevant question is not only:

“Can we get in?”

It is also:

“Can we get out when wrong?”

---

# 39. EXECUTION ENGINE

Signal generation and order execution must be independent.

Possible order types:

- market
- limit
- stop
- stop-limit
- post-only
- reduce-only
- IOC
- FOK
- TWAP
- VWAP
- iceberg
- passive maker
- aggressive taker
- smart-routing logic

Execution algorithm selection should depend on:

- urgency
- spread
- liquidity
- volatility
- size
- order-book depth
- signal half-life

---

# 40. ORDER STATE MACHINE

Every order must use explicit states.

```text
SIGNAL_CREATED
RISK_APPROVED
ORDER_CREATED
SUBMITTED
ACKNOWLEDGED
PARTIALLY_FILLED
FILLED
POSITION_OPEN
EXIT_SUBMITTED
CLOSED
RECONCILED
```

Failure states:

```text
REJECTED
CANCELLED
TIMEOUT
STALE
DUPLICATE
BROKER_DISCONNECTED
UNKNOWN_STATE
```

Unknown state:

freeze new trading.

---

# 41. RECONCILIATION SERVICE

Continuously compare:

```text
INTERNAL DATABASE
vs
BROKER / EXCHANGE
```

Check:

- positions
- orders
- fills
- cash
- margin
- realized PnL
- unrealized PnL

Mismatch:

```text
FREEZE NEW ORDERS
ALERT
RECONCILE
```

---

# 42. KILL SWITCHES

Implement:

## Global kill switch
Stops all trading.

## Strategy kill switch
Disables one strategy.

## Instrument kill switch
Disables one symbol.

## Venue kill switch
Disables one broker/exchange.

## Risk kill switch
Triggered by:

- daily loss
- weekly loss
- drawdown
- abnormal slippage
- extreme volatility
- API failures
- reconciliation mismatch
- duplicate orders
- data corruption
- runaway order rate
- margin anomaly

---

# 43. LIVE TRADE MONITOR

After entry, continuously evaluate:

- price behavior
- structure
- volume
- VWAP
- order flow
- spread
- volatility
- benchmark movement
- sector movement
- funding
- open interest
- news
- event risk
- thesis validity

Possible actions:

```text
HOLD
ADD
REDUCE
TAKE_PARTIAL
MOVE_STOP
EXIT
EMERGENCY_EXIT
```

Adding requires new risk approval.

---

# 44. THESIS INVALIDATION

Every trade must answer:

```text
What exact condition proves the trade thesis wrong?
```

Stop logic should combine:

```text
structural_invalidation
+
volatility_buffer
```

Do not use arbitrary percentage stops unless the strategy specifically validates them.

---

# 45. TIME STOPS

Track:

- time_to_profit
- time_to_target
- time_to_stop
- time_in_trade

If a setup historically resolves quickly, prolonged stagnation can be evidence of thesis decay.

A strategy may define:

```text
if expected resolution window is exceeded:
    reduce or exit
```

Only after testing.

---

# 46. MAE AND MFE

Track:

## MAE
Maximum Adverse Excursion

## MFE
Maximum Favorable Excursion

Use them to optimize:

- stop placement
- target placement
- trailing logic
- partial exits
- time stops

Example analysis:

```text
winning trades rarely exceed -0.4 ATR MAE
current stop = 1.5 ATR
```

Potential inefficiency.

Do not change production until validated.

---

# 47. STRATEGY DECAY DETECTION

Track rolling:

- expectancy
- win rate
- average R
- profit factor
- Sharpe
- Sortino
- Calmar
- drawdown
- MAE
- MFE
- slippage
- fill quality
- signal frequency
- turnover
- regime distribution

Example:

```text
Historical expectancy: +0.44R
Last 100 trades: +0.31R
Last 50 trades: +0.12R
Last 25 trades: -0.19R
```

Status:

```text
HEALTHY
WATCH
DEGRADING
SUSPENDED
```

Degrading strategy:

reduce capital or move to shadow mode.

Do not immediately re-optimize.

---

# 48. BACKTESTING RULES

Backtests must include:

- point-in-time data
- realistic spread
- fees
- slippage
- borrow
- funding
- execution delay
- liquidity limits
- corporate actions
- delisted stocks
- correct timestamps
- realistic order matching
- partial fills where relevant

Never optimize on future information.

---

# 49. TRAIN / VALIDATION / HOLDOUT

Example:

```text
2015-2021 = research/train
2022-2023 = validation
2024-2025 = holdout
2026 = shadow/paper/forward
```

Once holdout results are seen and used to adjust the strategy, that holdout is contaminated.

Create a new holdout.

---

# 50. WALK-FORWARD TESTING

Example:

```text
Train 2018-2020 → Test 2021
Train 2019-2021 → Test 2022
Train 2020-2022 → Test 2023
Train 2021-2023 → Test 2024
Train 2022-2024 → Test 2025
```

The objective is not one great result.

The objective is persistent edge.

---

# 51. MONTE CARLO TESTING

Randomize trade sequences and simulate thousands of paths.

Measure:

- median drawdown
- 95th-percentile drawdown
- 99th-percentile drawdown
- longest losing streak
- probability of ruin
- equity dispersion
- time underwater

---

# 52. STRESS TESTING

Test:

```text
fees +25%
fees +50%
slippage ×1.5
slippage ×2
entry delayed 1 bar
entry delayed 2 bars
10% missed trades
20% missed trades
API latency
price gaps
missing data
spread spikes
exchange outage
broker rejection
partial fills
```

A strategy that dies under small imperfections is not robust.

---

# 53. PARAMETER STABILITY

Prefer broad stable regions over narrow peaks.

Bad:

```text
EMA 27 → Sharpe 2.4
EMA 26 → Sharpe 0.6
EMA 28 → Sharpe 0.5
```

Better:

```text
EMA 20 → 1.4
EMA 25 → 1.6
EMA 30 → 1.55
EMA 35 → 1.47
```

Robustness > optimization peak.

---

# 54. OVERFITTING FIREWALL

Every candidate strategy receives an overfitting score based on:

- number of parameters
- number of experiments tried
- feature count
- search-space size
- out-of-sample stability
- walk-forward stability
- parameter plateau width
- cost robustness
- regime robustness
- sample size
- complexity

Reject strategies that depend on excessive tuning.

---

# 55. COMPLEXITY PENALTY

If:

```text
Strategy A:
5 parameters
Sharpe 1.55

Strategy B:
47 parameters
Sharpe 1.62
```

Prefer A unless B demonstrates materially stronger robustness.

---

# 56. SURVIVORSHIP BIAS

Stock universes must include:

- delisted companies
- bankrupt companies
- removed index members
- historical constituents

Use point-in-time universes.

---

# 57. LOOK-AHEAD BIAS

If an event occurred at:

```text
16:05:23
```

it cannot influence a trade at:

```text
16:05:00
```

Timestamp all:

- market data
- news
- earnings
- macro
- analyst updates
- token events

---

# 58. OPTIONS-SPECIFIC RISK

Track:

- delta
- gamma
- theta
- vega
- IV
- IV rank
- skew
- DTE
- assignment
- early exercise
- liquidity
- spread
- tail risk
- buying power
- margin expansion

Undefined-risk options require strict exposure controls.

---

# 59. CRYPTO-SPECIFIC RISK

Track:

- funding
- open interest
- liquidation clusters
- basis
- spot/perpetual divergence
- stablecoin flows
- exchange concentration
- exchange outage risk
- API risk
- token unlocks
- protocol risk
- depeg risk
- chain congestion

Example:

```text
Price ↑
OI ↑ sharply
Funding extremely positive
```

is different from:

```text
Price ↑
OI stable
Funding neutral
Spot buying strong
```

---

# 60. FOREX-SPECIFIC RISK

Track:

- spread changes
- rollover
- swap/financing
- session liquidity
- central-bank events
- economic releases
- rate differentials
- currency-strength relationships
- weekend gaps
- broker-specific execution

Major-event windows may block or reduce risk.

---

# 61. STOCK-SPECIFIC RISK

Track:

- earnings
- halts
- LULD
- short availability
- borrow fee
- premarket/after-hours liquidity
- splits
- dividends
- mergers
- secondary offerings
- analyst events
- SEC/company announcements

---

# 62. MODEL ENSEMBLE

Possible models:

- deterministic trend
- breakout
- mean reversion
- volatility
- LightGBM
- XGBoost
- CatBoost
- Random Forest
- logistic regression
- regime classifier
- order-flow model
- fundamental model

Do not let one model dominate automatically.

Model disagreement is information.

Example:

```text
Trend: LONG 0.82
Breakout: LONG 0.76
ML: LONG 0.68
Order Flow: LONG 0.81
Macro: SHORT 0.61
```

Possible final:

```text
LONG
confidence 0.72
```

But if disagreement is extreme:

`NO_TRADE`

---

# 63. PROBABILITY CALIBRATION

If a model says 80% confidence repeatedly, outcomes should be correct roughly 80% of the time in comparable conditions.

Track calibration buckets:

```text
50-60%
60-70%
70-80%
80-90%
90-100%
```

Danger:

```text
predicted 90%
actual 61%
```

The model is overconfident.

---

# 64. LLM ROLE

LLMs are appropriate for:

- news interpretation
- earnings interpretation
- narrative extraction
- macro synthesis
- strategy hypothesis generation
- post-trade critique
- research summaries
- anomaly explanations
- counter-thesis generation
- journaling
- report generation

LLMs must not directly control:

- hard risk limits
- margin calculations
- reconciliation
- kill switches
- broker truth
- stop enforcement
- position limits
- production deployment

---

# 65. STRATEGY PROMOTION PIPELINE

Mandatory stages:

```text
IDEA
↓
FORMAL SPECIFICATION
↓
BACKTEST
↓
WALK-FORWARD
↓
VALIDATION
↓
HOLDOUT
↓
MONTE CARLO
↓
STRESS TEST
↓
SHADOW LIVE
↓
PAPER
↓
TINY CAPITAL
↓
LIMITED PRODUCTION
↓
FULL PRODUCTION
```

Failure at any stage returns strategy to research.

---

# 66. SHADOW TRADING

Shadow mode:

- live market data
- real signals
- realistic simulated execution
- no broker orders

Compare:

```text
predicted fill
vs
real obtainable fill
```

Track:

- latency
- missed trades
- spread
- slippage
- signal decay

---

# 67. CHAMPION / CHALLENGER

Production:

```text
CHAMPION
```

Research:

```text
CHALLENGER_A
CHALLENGER_B
CHALLENGER_C
```

Challengers operate in shadow mode.

Promotion requires statistically meaningful evidence.

---

# 68. IMMUTABLE VERSIONING

Every order should reference:

```text
strategy_id
strategy_version
model_version
feature_version
risk_policy_version
dataset_version
code_commit_hash
configuration_hash
```

Example:

```yaml
strategy_id: VWAP_PULLBACK
strategy_version: 2.4.1
model_version: lgbm_17
feature_version: features_8.3
risk_policy_version: risk_3.1
dataset_hash: abc123
code_commit: 9ff83a
```

---

# 69. TRADE EXPLANATION RECORD

Before execution:

```text
Instrument:
Direction:
Strategy:
Regime:
Why now:
Primary evidence:
Counter-thesis:
Entry:
Invalidation:
Stop:
Target 1:
Target 2:
Historical sample size:
Historical win rate:
Expected R:
Expected value:
Estimated transaction cost:
Estimated slippage:
Risk as % NAV:
Portfolio impact:
Why not larger:
Cancellation conditions:
```

Every trade must be explainable.

---

# 70. POST-TRADE RECORD

Store:

```text
trade_id
strategy_id
strategy_version
regime
market_context
screenshots
features
volume
order_flow
entry
stop
targets
size
fills
slippage
fees
funding
MAE
MFE
time_to_profit
time_to_stop
time_to_target
PnL
R_multiple
exit_reason
errors
what_worked
what_failed
execution_quality
thesis_quality
```

---

# 71. PERFORMANCE ATTRIBUTION

Do not only report total PnL.

Break down:

```text
trend_strategy
breakout_strategy
mean_reversion
options
crypto
forex
stocks
execution_slippage
fees
funding
borrow
risk_reductions
regime_errors
model_errors
manual_intervention
```

Example:

```text
Gross strategy alpha: +18.0%
Fees: -2.4%
Slippage: -1.8%
Funding: -0.9%
Execution errors: -0.4%
Net: +12.5%
```

---

# 72. CORE PERFORMANCE METRICS

Track:

- CAGR
- Sharpe
- Sortino
- Calmar
- Omega
- Profit Factor
- expectancy
- average R
- win rate
- max drawdown
- average drawdown
- CVaR
- VaR
- tail ratio
- recovery factor
- turnover
- exposure
- time underwater
- average holding time
- stability by regime
- stability by asset
- stability by year
- stability by volatility state

---

# 73. STRATEGY RESEARCH SCORE

Suggested multi-dimensional scoring:

```text
Return Quality
Risk Quality
Out-of-Sample Stability
Walk-Forward Stability
Cost Robustness
Parameter Robustness
Regime Diversity
Sample Size
Execution Feasibility
Complexity Penalty
```

Never optimize only for net profit.

---

# 74. STRATEGY COMPETITION

Candidate strategies compete on:

- expectancy
- Sharpe
- Sortino
- Calmar
- drawdown
- turnover
- robustness
- OOS performance
- regime stability
- cost sensitivity
- complexity
- liquidity feasibility

A slightly lower-return but robust strategy can be superior.

---

# 75. SELF-LEARNING POLICY

The system may discover:

```text
VWAP pullback
RVOL > 3
positive earnings catalyst
QQQ aligned
sector aligned
morning session
```

has superior historical expectancy.

The system may propose:

```text
NEW FILTER
```

But deployment sequence remains:

```text
PROPOSE
↓
BACKTEST
↓
VALIDATE
↓
HOLDOUT
↓
SHADOW
↓
PAPER
↓
APPROVAL
↓
DEPLOY
```

Never:

```text
OBSERVE LOSS
↓
CHANGE PARAMETER
↓
LIVE DEPLOY
```

---

# 76. SYSTEM HEALTH ENGINE

Track:

- CPU/memory
- network
- API health
- broker connectivity
- exchange connectivity
- data delays
- queue lag
- database health
- clock drift
- failed jobs
- stale prices
- reconciliation age
- order error rate

Any critical health failure can veto new trading.

---

# 77. EVENT RISK ENGINE

Track upcoming:

- FOMC
- CPI
- NFP
- GDP
- ECB
- BOE
- BOJ
- earnings
- major company events
- FDA
- crypto unlocks
- ETF decisions
- hard forks
- elections where market relevant
- major regulatory decisions

Strategies define behavior:

```text
BLOCK
REDUCE
ALLOW
EVENT_ONLY
```

---

# 78. NO-TRADE CONDITIONS

Automatic `NO_TRADE` when:

- edge too weak
- expected return below costs
- spread too large
- liquidity too low
- regime unknown
- major event too close
- data stale
- data conflicting
- model disagreement excessive
- historical sample too small
- strategy degraded
- portfolio concentration too high
- risk limit reached
- broker mismatch
- system health degraded
- execution cost too high
- stop too wide
- reward too small
- opposing structure too close
- slippage estimate unstable

---

# 79. EXAMPLE TRADE DECISION

```text
BTCUSDT LONG

Regime:
TREND_UP_HIGH_VOL

Strategy:
4H BREAKOUT_RETEST

Macro:
74/100

HTF Structure:
88/100

Relative Strength:
83/100

Location:
91/100

Volume:
76/100

Liquidity:
82/100

Order Flow:
79/100

Historical Setup Quality:
81/100

Counter-Thesis:
Moderate resistance above

Entry:
X

Structural Invalidation:
Y

Stop:
Y - volatility buffer

Target 1:
Z1

Target 2:
Z2

Expected R:
2.4R

Historical samples:
437

Historical expectancy:
+0.39R

Estimated fees:
X

Estimated slippage:
Y

Risk:
0.40% NAV

Portfolio impact:
Acceptable

Decision:
LONG
```

---

# 80. MASTER DECISION SEQUENCE

Every candidate trade should pass through:

```text
1. DATA VALID?
2. SYSTEM HEALTHY?
3. EVENT RISK ACCEPTABLE?
4. ASSET IN PLAY?
5. REGIME KNOWN?
6. STRATEGY ALLOWED IN REGIME?
7. HIGHER-TIMEFRAME STRUCTURE VALID?
8. LOCATION ATTRACTIVE?
9. VOLUME CONFIRMS?
10. VOLATILITY SUITABLE?
11. ORDER FLOW CONFIRMS?
12. FUNDAMENTALS/MACRO NON-FATAL?
13. HISTORICAL EXPECTANCY POSITIVE?
14. COUNTER-THESIS SURVIVED?
15. REWARD/RISK ACCEPTABLE?
16. EXPECTED RETURN > COSTS?
17. PORTFOLIO EXPOSURE ACCEPTABLE?
18. CORRELATION ACCEPTABLE?
19. LIQUIDITY ACCEPTABLE?
20. RISK ENGINE APPROVES?
21. EXECUTION FEASIBLE?
22. ORDER SUBMITTED?
23. BROKER ACKNOWLEDGED?
24. POSITION RECONCILED?
25. THESIS MONITORED?
26. EXIT EXECUTED?
27. TRADE REVIEWED?
```

Any failure can return:

`NO_TRADE`

---

# 81. RECOMMENDED DEVELOPMENT ORDER

## Phase 1
Data and research foundation.

- canonical instruments
- clean historical data
- provenance
- Parquet/DuckDB
- cost model
- backtesting

## Phase 2
Risk foundation.

- position sizing
- portfolio exposure
- drawdown limits
- kill switches
- reconciliation
- system health

## Phase 3
Core deterministic strategies.

- trend
- breakout
- mean reversion
- VWAP pullback
- momentum

## Phase 4
Regime engine.

## Phase 5
Strategy scoring and ensemble.

## Phase 6
ML models.

## Phase 7
Historical analogue search.

## Phase 8
Counter-thesis agent.

## Phase 9
Shadow live.

## Phase 10
Paper execution.

## Phase 11
Tiny capital with strict limits.

## Phase 12
Champion/challenger production.

---

# 82. REPOSITORY CONCEPT

Suggested logical structure:

```text
trading-system/
├── CONSTITUTION.md
├── config/
│   ├── risk/
│   ├── strategies/
│   ├── venues/
│   └── instruments/
├── data/
│   ├── ingestion/
│   ├── quality/
│   ├── provenance/
│   └── storage/
├── intelligence/
│   ├── macro/
│   ├── news/
│   ├── fundamentals/
│   ├── crypto/
│   └── options/
├── regime/
├── strategies/
│   ├── trend/
│   ├── breakout/
│   ├── mean_reversion/
│   ├── vwap/
│   ├── volatility/
│   └── order_flow/
├── models/
├── portfolio/
├── risk/
├── execution/
├── reconciliation/
├── monitoring/
├── research/
│   ├── backtests/
│   ├── walk_forward/
│   ├── monte_carlo/
│   ├── stress/
│   └── experiments/
├── review/
├── reports/
└── tests/
```

---

# 83. FINAL PRINCIPLE

The goal is not to build:

> one bot with one perfect strategy

The goal is to build:

> a market operating system that hosts multiple competing strategies, understands when each one is appropriate, measures uncertainty, rejects poor trades, protects capital deterministically, executes realistically, and continuously researches improvements without allowing unvalidated changes into production.

The best trading system is not the one that predicts the most.

It is the one that:

- survives
- knows when it does not know
- controls exposure
- understands costs
- adapts carefully
- measures itself honestly
- prevents catastrophic mistakes
- compounds durable edge over time

---

# 84. NON-NEGOTIABLE PRODUCTION RULE

Before any live-capital deployment:

```text
NO strategy may go live unless:

1. Data is validated.
2. Costs are modeled.
3. Out-of-sample expectancy is positive.
4. Walk-forward is acceptable.
5. Monte Carlo risk is acceptable.
6. Stress tests are acceptable.
7. Parameter stability is acceptable.
8. Shadow trading is acceptable.
9. Paper execution is acceptable.
10. Risk engine approves.
11. Reconciliation is operational.
12. Kill switches are operational.
13. Strategy/version provenance is complete.
14. Manual emergency control exists.
```

If any item is missing:

`DO NOT DEPLOY`

---

# 85. MASTER OUTPUT CONTRACT

Every strategy decision should ultimately produce a machine-readable object equivalent to:

```yaml
decision:
  instrument:
  asset_class:
  timestamp:
  direction:
  action:
  strategy_id:
  strategy_version:

context:
  regime:
  macro_score:
  in_play_score:
  structure_score:
  location_score:
  volume_score:
  volatility_score:
  order_flow_score:
  fundamental_score:
  relative_strength_score:

prediction:
  p05_return:
  p25_return:
  median_return:
  p75_return:
  p95_return:
  confidence:
  calibration_bucket:

historical_evidence:
  sample_size:
  win_rate:
  avg_win_r:
  avg_loss_r:
  expectancy_r:
  profit_factor:

counter_thesis:
  score:
  fatal_objection:
  objections:

trade:
  entry:
  stop:
  structural_invalidation:
  target_1:
  target_2:
  expected_r:
  time_stop:

costs:
  fees:
  spread:
  expected_slippage:
  funding:
  borrow:
  total_expected_cost:

portfolio:
  existing_exposure:
  correlated_exposure:
  post_trade_exposure:

risk:
  requested_risk:
  approved_risk:
  position_size:
  risk_engine_status:
  veto_reason:

execution:
  venue:
  order_type:
  max_slippage:
  max_participation:
  status:

provenance:
  model_version:
  feature_version:
  risk_policy_version:
  dataset_version:
  code_commit:
  configuration_hash:
```

This object becomes the canonical record for every attempted trade, including rejected trades.

---

# END OF MASTER SPECIFICATION

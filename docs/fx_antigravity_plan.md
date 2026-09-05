# FX Autonomous Trading Bot — Multi-Asset Self-Learning System

## Mission

Build autonomous trading bots inside FX that start with \$1 training capital per asset class, trade across **any timeframe**, learn from every decision, self-assess their own readiness, and stop when a configurable profit target is reached. The \$1 is training capital to observe bot behavior and knowledge acquisition — not production capital.

## Core Principle

> If the bot feels that it is not enough trained, it will not be available to use.

The bot has a **Readiness Gate**: a self-assessment system that measures its own knowledge, win rate stability, and strategy confidence. Until it passes readiness, it only observes and records — it does not trade.

---

## Asset Classes & Starting Pairs

The system is multi-asset from day one. Start with the classic, most liquid, most relevant instruments:

| Asset Class | Starting Pairs | Data Source | Execution |
|-------------|---------------|-------------|-----------|
| **Crypto** | BTCUSDT, ETHUSDT | Binance API | Local Paper → Binance Testnet |
| **Forex** | EURUSD, GBPUSD, USDJPY | London Strategic Edge / OANDA | Local Paper → Broker |
| **Commodities** | XAUUSD (Gold), Oil (WTI) | LSE / Broker Feed | Local Paper → Broker |
| **Stocks** | AAPL, MSFT, SPY | Yahoo Finance / Alpaca | Local Paper → Alpaca Paper |

Each asset class gets its own bot instance with \$1 training capital. They share the same strategy engine and learning system but maintain separate knowledge bases per asset class.

---

## Bot Readiness System

The bot has 4 readiness levels. It cannot trade until it reaches Level 3.

### Level 0 — OBSERVING (No trades, learning only)
**Requirements to enter**: Bot is started
**What it does**:
- Fetches live market data every cycle
- Computes all indicators and features
- Runs all strategies and records what they WOULD have done
- Builds regime history
- Records NO_TRADE with full analysis
- **Trades**: ZERO — observation only

**Exits to Level 1 when**:
- 500+ observation cycles completed
- Has seen at least 2 different regime types (trending + ranging)
- Has computed indicators for at least 20 trading sessions

### Level 1 — PAPER_TESTING (Simulated trades on local paper)
**Requirements to enter**: Level 0 complete
**What it does**:
- Everything from Level 0
- Takes paper trades on the local SQLite broker
- Measures win rate, expectancy, drawdown, Sharpe
- Records every trade outcome with full provenance
- Compares strategy performance per regime
- **Trades**: Paper only, \$1 virtual capital

**Exits to Level 2 when** (ALL must be true):
- 50+ paper trades completed
- Rolling 30-trade win rate ≥ 50%
- Rolling 30-trade expectancy > 0 (positive edge after costs)
- Max drawdown < 20%
- Profit factor > 1.1
- At least 3 strategies have been used and measured
- Bot has traded in at least 2 different regime types

### Level 2 — VALIDATED (Ready for testnet/extended paper)
**Requirements to enter**: Level 1 metrics passed
**What it does**:
- Continues paper trading with larger sample
- Runs walk-forward validation on learned weights
- Challenger vs champion model comparison
- Out-of-sample testing on held-out data
- **Trades**: Paper with full risk management

**Exits to Level 3 when** (ALL must be true):
- 200+ total paper trades
- Rolling 100-trade win rate ≥ 52%
- Rolling 100-trade expectancy > 0.2% per trade
- Sharpe ratio > 0.5 (annualized)
- Max drawdown < 15%
- Challenger model beats champion on holdout
- No single strategy responsible for > 60% of profits (diversified edge)

### Level 3 — READY (Available for real capital)
**Requirements to enter**: Level 2 metrics passed + human approval
**What it does**:
- Bot displays as "READY" in the dashboard
- User can allocate real capital and set profit target
- Continues learning and can be demoted back to Level 2 if metrics degrade
- **Trades**: Real or paper, user's choice

### Demotion Rules
- If rolling 50-trade expectancy goes negative → demote to Level 1
- If drawdown exceeds 25% → demote to Level 1 and pause
- If 5 consecutive losses → pause for cooling period (2 hours)
- If data quality degrades → pause until resolved

---

## Adaptive Timeframe System

The bot trades on ANY timeframe. It doesn't pick one — it adapts based on regime, volatility, and asset class.

### How It Selects Timeframes

```
1. SCAN all available timeframes: 1m, 5m, 15m, 1h, 4h, 1d
2. IDENTIFY the dominant regime on each timeframe
3. SELECT the timeframe where:
   - The trend is clearest (highest ADX)
   - The signal quality is strongest (highest confluence score)
   - The risk/reward is best (tightest stop relative to target)
4. USE higher timeframe for trend direction
5. USE selected timeframe for signal generation
6. USE lower timeframe for entry timing (optional refinement)
```

### Timeframe Hierarchy Per Asset Class

| Asset Class | Trend TF | Signal TF | Entry TF | Why |
|-------------|----------|-----------|----------|-----|
| Crypto | 4h / 1d | 15m / 1h / 4h | 5m / 15m | 24/7 market, high volatility |
| Forex | 1d / 1w | 1h / 4h | 15m / 1h | Session-based, moderate vol |
| Commodities | 1d / 1w | 1h / 4h | 15m / 1h | Macro-driven, trending |
| Stocks | 1d / 1w | 1d / 4h | 1h / 4h | Daily bars most reliable |

The bot **learns** which timeframe combinations work best per asset through its observation system. After 200+ observations, it may discover that "Gold on 1H signals with 4H trend has 61% win rate, but on 15m signals only 47%" — and it adjusts automatically.

---

## Strategy Engine (5 Core + 2 Meta)

### Core Signal Strategies

**Strategy 1 — Trend Following**
- EMA 9/21/55 crossover with ADX confirmation
- Entry: Fast > Medium > Slow AND ADX > 25
- Stop: Below Slow EMA or last swing low + 0.5×ATR buffer
- Profit plan: Trail stop at 1.5×ATR below price
- Works best in: TRENDING regime

**Strategy 2 — Mean Reversion**
- Bollinger Bands (20, 2.0) + RSI(14)
- Entry: Price below lower band AND RSI < 30 (long) or above upper band AND RSI > 70 (short)
- Stop: Beyond the band by 0.5×ATR
- Profit plan: Return to 20-period mean (middle band)
- Works best in: RANGING regime

**Strategy 3 — Breakout**
- 20-period high/low breakout with volume > 2× average
- Entry: Price breaks above 20-period high with ATR expanding > 1.5× median
- Stop: Below the consolidation range bottom
- Profit plan: 2× consolidation range height
- Works best in: Transitioning from RANGING to TRENDING

**Strategy 4 — Momentum**
- MACD (12/26/9) histogram + Rate of Change (14)
- Entry: MACD hist > 0 and growing AND ROC > 0 AND price > 21 EMA
- Stop: Below 21 EMA or last swing low
- Profit plan: MACD histogram shrinks for 3 consecutive bars → exit
- Works best in: TRENDING with acceleration

### Meta Strategies (Decision Layer)

**Strategy 5 — Regime Detector**
- Classifies market as TRENDING / RANGING / VOLATILE using ADX + ATR percentile + Bollinger Width
- TRENDING: ADX > 25, price making higher highs/lows (or lower lows/highs)
- RANGING: ADX < 20, price bouncing between support/resistance
- VOLATILE: ATR > 90th percentile of last 100 periods
- Adjusts strategy weights based on regime:

```python
REGIME_WEIGHTS = {
    "TRENDING":  {"trend": 0.40, "mean_rev": 0.10, "breakout": 0.25, "momentum": 0.25},
    "RANGING":   {"trend": 0.15, "mean_rev": 0.35, "breakout": 0.20, "momentum": 0.30},
    "VOLATILE":  {"trend": 0.20, "mean_rev": 0.15, "breakout": 0.35, "momentum": 0.30},
}
```

**Strategy 6 — Confluence Scorer**
- Weighted vote across strategies 1-4, filtered by regime
- Score = Σ(strategy_signal × regime_weight)
- LONG if score > +0.60, SHORT if score < -0.60, else NO_TRADE
- In VOLATILE regime, threshold raises to ±0.75

**Strategy 7 — Monte Carlo Position Sizer**
- Simulates 1,000 price paths based on recent volatility
- Determines optimal position size for given capital and risk tolerance
- Accounts for: spread, slippage, max drawdown tolerance
- Output: position_size, probability_of_ruin, expected_return_distribution

---

## Trade Execution Rules

### Before Every Trade (Non-Negotiable)

```python
# Every trade MUST have all of these defined BEFORE entry
required = {
    "entry": float,               # exact entry price
    "stop": float,                # stop loss price
    "structural_invalidation": float,  # where thesis is wrong
    "target_1": float,            # first profit target
    "target_2": float,            # second profit target
    "profit_plan": str,           # FIXED / TRAILING / TIME_EXIT
    "position_size": float,       # units to trade
    "risk_amount": float,         # max $ at risk
    "risk_pct": float,            # risk as % of capital (max 2%)
    "expected_r": float,          # reward/risk ratio (min 1.5)
    "confluence_score": float,    # min 0.60
    "regime": str,                # TRENDING / RANGING / VOLATILE
    "readiness_level": int,       # must be >= 1 for paper, >= 3 for live
}

if any(v is None for v in required.values()):
    return NO_TRADE

if required["risk_pct"] > 0.02:
    return NO_TRADE  # never risk more than 2%

if required["expected_r"] < 1.5:
    return NO_TRADE  # minimum 1.5:1 reward/risk

if required["confluence_score"] < 0.60:
    return NO_TRADE
```

### Forbidden Behaviors (Hard-Coded Blocks)

```python
FORBIDDEN = [
    "martingale",                    # doubling after losses
    "averaging_down_unbounded",      # adding to losers without limit
    "no_stop_trading",               # any trade without a stop
    "revenge_sizing",                # increasing size after losses
    "strategy_self_promotion",       # bot promoting its own untested changes
    "live_without_gate",             # any live trade without LiveGate + TOTP
    "risk_override",                 # bypassing risk engine
    "parameter_tweak_after_loss",    # changing params immediately after a loss
]
```

### Cooling Periods

| Trigger | Action |
|---------|--------|
| 3 consecutive losses | Pause 1 hour, reduce position size by 50% for next 5 trades |
| 5 consecutive losses | Pause 2 hours, review signal quality |
| Max daily loss (5%) hit | Stop trading for the day |
| Max weekly loss (10%) hit | Stop trading for the week, require human review |
| Drawdown > 15% | Demote to Level 1, stop real trading |

---

## Profit Target System

The bot stops trading when the profit target is reached for a given campaign.

```python
class ProfitTargetMonitor:
    def __init__(self, starting_capital: float, target_amount: float):
        self.starting = starting_capital    # e.g., $1.00
        self.target = target_amount         # e.g., $20.00
        self.target_pct = (target_amount / starting_capital) - 1  # 1900%

    def check(self, current_equity: float) -> str:
        if current_equity >= self.target:
            return "TARGET_REACHED"          # stop trading, celebrate
        if current_equity <= self.starting * 0.80:
            return "MAX_LOSS_BREACH"         # stop trading, review
        progress = (current_equity - self.starting) / (self.target - self.starting)
        return f"IN_PROGRESS ({progress:.1%})"
```

Configuration:
```env
BOT_STARTING_CAPITAL=1.00
BOT_PROFIT_TARGET=20.00
BOT_MAX_LOSS_PCT=0.20
BOT_PAUSE_ON_TARGET=true
```

---

## What The Bot Records (Every Single Cycle)

### Decision Log (even for NO_TRADE)
```
timestamp, instrument, asset_class, timeframe_used,
regime, adx, atr, atr_percentile, rsi, macd_hist, macd_signal,
ema9, ema21, ema55, bollinger_upper, bollinger_lower, bollinger_width,
z_score, volume, volume_ratio, spread, spread_pct,
trend_signal, mean_rev_signal, breakout_signal, momentum_signal,
regime_weights, confluence_score, final_decision,
entry_price, stop_price, target_1, target_2,
position_size, risk_amount, risk_pct, expected_r,
readiness_level, bot_knowledge_score
```

### Trade Log (for executed trades)
```
trade_id, decision_id, instrument, asset_class,
side, entry_price, entry_time, exit_price, exit_time,
stop_price, target_1, target_2, profit_plan,
quantity, notional, realized_pnl, realized_pnl_pct,
max_adverse_excursion, max_favorable_excursion,
duration_seconds, strategy_used, regime_at_entry, regime_at_exit,
slippage, spread_cost, total_cost,
was_stopped_out, reached_target, exit_reason
```

### Knowledge Log (aggregated lessons)
```
lesson_id, instrument, asset_class, strategy,
regime, timeframe, session (Asian/London/NY),
sample_size, win_rate, avg_win_r, avg_loss_r,
expectancy, profit_factor, sharpe,
observation (human-readable insight),
created_at, updated_at, confidence_level
```

---

## Architecture — New Files

### Component 1: Multi-Asset Data Providers

#### [NEW] `providers/binance/binance_provider.py`
- Async Binance REST + WebSocket data feed
- Klines, ticker, orderbook for crypto pairs
- Testnet/production URL switching via env vars
- Rate limiting, reconnection, error recovery

#### [NEW] `providers/binance/binance_executor.py`
- `BinanceExecutor` implementing `BrokerAdapter` ABC
- Testnet-only by default; live requires LiveGate
- Maps to `CanonicalOrder` / `CanonicalOrderResult`

#### [NEW] `providers/multi_asset_feed.py`
- Unified data interface across all asset classes
- Routes to correct provider: Binance (crypto), LSE (forex/commodities), Yahoo/Alpaca (stocks)
- Returns standardized OHLCV + metadata regardless of source

### Component 2: Strategy Engine

#### [NEW] `services/strategies/adaptive_strategies.py`
- All 7 strategies (Trend, Mean Rev, Breakout, Momentum, Regime, Confluence, Monte Carlo)
- Asset-class-aware parameters (crypto vs forex vs commodities vs stocks)
- Timeframe-adaptive: works on any timeframe passed to it
- Outputs normalized signals matching existing FX signal contract

### Component 3: Bot Brain

#### [NEW] `services/bots/auto_trader.py`
- Main autonomous bot controller
- Readiness gate (Level 0-3)
- Profit target monitor
- Cooling period enforcement
- Multi-asset loop: one bot instance per asset class
- Background asyncio task compatible with FastAPI

#### [NEW] `services/bots/readiness_gate.py`
- Self-assessment system
- Tracks: observations, trades, win rate, expectancy, drawdown, Sharpe
- Level promotion/demotion logic
- Knowledge score calculation

### Component 4: Learning & Knowledge

#### [NEW] `services/journal/trade_journal.py`
- SQLite tables: bot_decisions, bot_trades, bot_lessons, bot_performance
- Records every cycle including NO_TRADE
- Aggregates lessons after configurable trade count

#### [NEW] `services/memory/strategy_memory.py`
- Per-asset, per-strategy, per-regime performance memory
- Time-of-day patterns (session analysis)
- Feeds learned patterns back into confluence scorer weights
- Challenger/champion model system

#### [MODIFY] `services/learning/market_learning.py`
- Add `MultiAssetLearner` extending `StreamingLearner`
- Per-strategy, per-asset performance tracking
- Regime-correlated performance analysis

### Component 5: API & Dashboard

#### [NEW] `backend/app/api/auto_trader.py`
- REST endpoints for bot control and monitoring
- `GET /api/auto-trader/status` — readiness level, equity, target progress per asset
- `GET /api/auto-trader/suggestions` — current entry suggestions
- `GET /api/auto-trader/trades` — trade history
- `GET /api/auto-trader/knowledge` — learned patterns
- `GET /api/auto-trader/readiness` — detailed readiness metrics
- `POST /api/auto-trader/start` — start bot for an asset class
- `POST /api/auto-trader/stop` — stop bot
- `POST /api/auto-trader/configure` — set target, capital, pairs

#### [NEW] `backend/app/web/auto_trader.py`
- Dashboard at `/auto-trader`
- Readiness level visualization per asset class
- Profit target progress bar
- Trade history table
- Strategy performance breakdown
- Knowledge log viewer
- Entry suggestion cards
- Start / Stop / Configure controls

### Component 6: Integration

#### [MODIFY] `backend/app/main.py`
- Register auto-trader API and web routers
- Add background task for bot loop

#### [MODIFY] `.env.example`
- Add all `BOT_*` environment variables

#### [NEW] `scripts/auto_trader_runner.py`
- Standalone CLI runner for testing
- `python scripts/auto_trader_runner.py --asset crypto --symbol BTCUSDT --capital 1.0 --target 20.0`

#### [NEW] `tests/test_auto_trader.py`
- Unit tests for strategies, readiness gate, profit target, risk checks
- Integration test: full cycle with mock market data

---

## File Summary

| File | Action | Purpose |
|------|--------|---------|
| `providers/binance/binance_provider.py` | NEW | Crypto market data from Binance |
| `providers/binance/binance_executor.py` | NEW | Crypto order execution via Binance |
| `providers/multi_asset_feed.py` | NEW | Unified data interface for all asset classes |
| `services/strategies/adaptive_strategies.py` | NEW | 7 strategies adaptive to any timeframe/asset |
| `services/bots/auto_trader.py` | NEW | Main autonomous bot controller |
| `services/bots/readiness_gate.py` | NEW | Bot self-assessment and readiness levels |
| `services/journal/trade_journal.py` | NEW | Trade recording and performance analytics |
| `services/memory/strategy_memory.py` | NEW | Learned patterns and strategy knowledge |
| `services/learning/market_learning.py` | MODIFY | Add MultiAssetLearner class |
| `backend/app/api/auto_trader.py` | NEW | REST API endpoints |
| `backend/app/web/auto_trader.py` | NEW | Dashboard web page |
| `backend/app/main.py` | MODIFY | Register new routers |
| `.env.example` | MODIFY | Add bot environment variables |
| `scripts/auto_trader_runner.py` | NEW | CLI runner script |
| `tests/test_auto_trader.py` | NEW | Automated tests |

---

## Verification Plan

### Automated Tests
```bash
python -m pytest tests/test_auto_trader.py -v
```

Tests cover:
- All 7 strategy signal generation with known inputs
- Readiness gate level transitions (0→1→2→3 and demotions)
- Profit target monitor (target reached, max loss breach)
- Risk checks (stop required, confluence threshold, position sizing)
- Cooling period enforcement
- Trade journal recording (including NO_TRADE)
- Knowledge aggregation after N trades
- Multi-asset data feed routing

### Manual Verification
1. Start bot in Level 0 → verify it observes without trading
2. After 500 cycles → verify promotion to Level 1
3. Watch paper trades → verify stop loss and profit plan on every trade
4. After 50 paper trades → check readiness metrics
5. Trigger demotion → verify bot stops and drops to Level 1
6. Set \$1 → \$20 target → verify bot stops at target
7. Visit `/auto-trader` dashboard → verify all panels work
8. Check knowledge base → verify learned patterns are sensible

### Safety Verification
```bash
grep -r "AI_CAN_EXECUTE_LIVE" .env
# Must show: AI_CAN_EXECUTE_LIVE=false
```
All live paths require LiveGate + TOTP. Bot cannot self-promote to live.

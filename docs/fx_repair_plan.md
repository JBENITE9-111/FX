# FX Master Repair & Build Plan

Every issue from the forensic report, in the exact order to fix them. Each task builds on the previous ones. Nothing gets built on a broken foundation.

> [!IMPORTANT]
> **This is a real app with real data.** Every fix is designed so the system becomes trustworthy enough to train bots on real market information and eventually trade with real money. Shortcuts here mean the bot learns wrong things or fails silently when it matters.

---

## Phase 1 — Fix The Foundation (Tasks 1-10)

*Nothing else works reliably until these are done. Every bug here undermines everything built on top.*

---

### Task 1: Fix SQLite Connection Leaks

**Why this matters**: Your bot calls the database every 60 seconds. Each call opens a connection that never closes. After 6 hours = 360 leaked connections. After 24 hours = 1,440. Your Mac will eventually refuse to open more files and the bot crashes with no explanation.

**What's broken**:
- `services/local_paper/broker.py` — every function calls `_connect()` which opens a new connection
- `services/bot_signals/store.py` — same pattern
- `services/cache/ttl_cache.py` — same pattern
- `services/agents/supervisor.py` — same pattern

**What to do**:
```python
# CURRENT (broken) — connection opened, never closed
def get_account():
    with _connect() as conn:  # 'with' only handles transactions, NOT closing
        row = conn.execute("SELECT * FROM account WHERE id=1").fetchone()
    return dict(row)

# FIXED — explicit close in finally block
def get_account():
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM account WHERE id=1").fetchone()
        conn.commit()
        return dict(row)
    finally:
        conn.close()  # THIS is what was missing
```

**Files to fix**:
- `services/local_paper/broker.py` — every function that calls `_connect()`
- `services/bot_signals/store.py` — every function that calls `_connect()`
- `services/cache/ttl_cache.py` — every function that calls `_connect()`
- `services/agents/supervisor.py` — every function that calls `_connect()`
- `services/paper_fleet/fleet.py` — the `_connect()` usage in `run_cycle()`

**Verification**: Run the app for 1 hour and check open file descriptors:
```bash
lsof -p $(pgrep -f "uvicorn") | grep sqlite | wc -l
# Should stay constant (1-3), not growing
```

---

### Task 2: Move Schema Creation Out Of `_connect()`

**Why this matters**: Right now, every database call runs 5 `CREATE TABLE IF NOT EXISTS` statements plus an `ALTER TABLE` migration check. A single bot cycle that calls `get_account()`, `positions()`, and `submit_market_order()` runs schema creation 15 times. This wastes CPU and makes every operation slower.

**What to do**:
- Create a one-time `init_database()` function that runs at app startup
- Remove all `CREATE TABLE` and `ALTER TABLE` from `_connect()`
- Call `init_database()` from `backend/app/main.py` at startup

**Files to modify**:
- `services/local_paper/broker.py` — extract schema creation to `init_database()`
- `services/bot_signals/store.py` — same
- `services/paper_fleet/fleet.py` — same
- `backend/app/main.py` — call `init_database()` on startup

**New file**:
- `backend/app/core/database.py` — centralized database initialization and connection management

---

### Task 3: Create `backend/app/core/` — Centralized Configuration

**Why this matters**: Configuration is currently scattered across 30+ files, each calling `os.getenv()` with its own defaults. If you want to change the database path, you need to find every file that references it. One typo in a default value and a part of the app silently uses wrong settings.

**What to do**:
Create `backend/app/core/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    # Trading safety
    trading_mode: str = "research"
    live_trading_enabled: bool = False
    ai_can_execute_live: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/fx.db"
    local_paper_db: str = "data/local_paper/local_paper.sqlite3"

    # LLM
    ollama_enabled: bool = True
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:8b"
    openrouter_enabled: bool = False
    openrouter_api_key: str = ""
    kimi_enabled: bool = False
    kimi_api_key: str = ""

    # Brokers
    binance_testnet_enabled: bool = False
    binance_testnet_api_key: str = ""
    binance_testnet_api_secret: str = ""
    alpaca_enabled: bool = False

    # Bot
    bot_starting_capital: float = 1.00
    bot_profit_target: float = 20.00
    bot_max_loss_pct: float = 0.20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**Files to create**:
- `backend/app/core/__init__.py`
- `backend/app/core/config.py` — centralized settings
- `backend/app/core/database.py` — connection management

**Files to modify**: Every file that currently uses `os.getenv()` — import `settings` from core instead. This is ~25 files but each change is a one-liner.

---

### Task 4: Add Global Error Handling

**Why this matters**: Right now, if a route crashes, one of two things happens: (1) the error is silently swallowed by a broad `except Exception:` and the user gets wrong data, or (2) the error propagates as an ugly 500 response with a Python traceback. Neither is acceptable for a system you need to trust.

**What to do**:
Create `backend/app/core/errors.py`:
```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger("fx")

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error on {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url.path),
        },
    )
```

Register in `main.py`:
```python
from backend.app.core.errors import global_exception_handler
app.add_exception_handler(Exception, global_exception_handler)
```

Then **remove** all broad `except Exception: pass` blocks across the codebase and replace them with specific exception handling that logs and re-raises.

**Files to create**:
- `backend/app/core/errors.py`
- `backend/app/core/logging_config.py` — structured logging to file + console

**Files to modify**:
- `backend/app/main.py` — register handler, set up logging
- `backend/app/api/chat.py` — remove broad except
- `backend/app/api/market.py` — remove broad except
- `backend/app/api/global_markets.py` — remove broad except
- `backend/app/api/control_center.py` — remove broad except, fix `__import__("asyncio")` anti-pattern
- `backend/app/api/strategy_lab.py` — remove broad except
- `backend/app/main.py` — make route import failures LOUD, not silent

---

### Task 5: Add Basic Authentication

**Why this matters**: Without auth, anyone on your WiFi network can access the app, start bots, and submit trades. Even for a personal app, this is dangerous — a mistyped URL, a port scan, or a family member accidentally hitting the endpoint could cause problems.

**What to do**:
Create `backend/app/core/auth.py`:
```python
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib, os

# Simple API key auth — good enough for personal use
API_KEY_HASH = hashlib.sha256(
    os.getenv("FX_API_KEY", "fx-dev-key-change-me").encode()
).hexdigest()

security = HTTPBearer(auto_error=False)

async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # Allow web pages without auth (they use session cookies)
    if request.url.path.startswith("/web/") or request.url.path == "/":
        return

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing API key")

    provided_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    if provided_hash != API_KEY_HASH:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

**Files to create**:
- `backend/app/core/auth.py`

**Files to modify**:
- `backend/app/main.py` — add auth middleware
- `.env.example` — add `FX_API_KEY`

---

### Task 6: Fix LLM Fallback Chain

**Why this matters**: When Ollama is down (which happens — updates, crashes, Mac sleep), the entire "Ask FX" feature dies. You have 3 LLM providers configured in `.env.example` but only one is used.

**What to do**:
Create `backend/app/core/llm.py`:
```python
async def ask_llm(messages: list[dict], timeout: int = 90) -> str:
    """Try Ollama → Kimi → OpenRouter → error message."""

    if settings.ollama_enabled:
        try:
            return await _ask_ollama(messages, timeout)
        except Exception as e:
            logger.warning(f"Ollama failed: {e}, trying fallback...")

    if settings.kimi_enabled and settings.kimi_api_key:
        try:
            return await _ask_kimi(messages, timeout)
        except Exception as e:
            logger.warning(f"Kimi failed: {e}, trying fallback...")

    if settings.openrouter_enabled and settings.openrouter_api_key:
        try:
            return await _ask_openrouter(messages, timeout)
        except Exception as e:
            logger.warning(f"OpenRouter failed: {e}")

    return "All LLM providers are currently unavailable. Please check Ollama is running."
```

**Files to create**:
- `backend/app/core/llm.py` — unified LLM client with fallback

**Files to modify**:
- `backend/app/api/chat.py` — use `ask_llm()` instead of direct Ollama calls

---

### Task 7: Fix Dead Code & Silent Failures

**Why this matters**: Dead code confuses future development. Silent failures mean parts of the app can be broken for weeks without anyone knowing.

**What to do**:
1. `backend/app/web/training.py` — Remove the 400+ lines of unreachable HTML after the `RedirectResponse` on line 20, OR remove the redirect and restore the page
2. `backend/app/main.py` — Change all route import `except Exception:` blocks to log the FULL error with traceback and raise if in development mode:
```python
try:
    from backend.app.routes.fx_newspaper import router as fx_newspaper_router
    app.include_router(fx_newspaper_router)
except Exception as e:
    import traceback
    logger.error(f"FAILED to load fx_newspaper routes: {traceback.format_exc()}")
    if settings.app_env == "development":
        raise  # Fail loud in dev
```
3. `backend/app/api/broker.py` — Add clear `"⚠️ MOCK DATA"` label to mock responses

---

### Task 8: Persist TOTP Rate Limiting

**Why this matters**: If someone tries to brute-force your TOTP codes, the rate limiter stops them — but only until the app restarts, at which point they can try again from zero.

**What to do**:
Move `_failures` and `_locked_until` from instance variables to SQLite:
```python
# In services/auth/totp.py
def _record_failure(self, user_id: str):
    with self._db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO totp_failures (user_id, count, locked_until, updated_at) "
            "VALUES (?, COALESCE((SELECT count FROM totp_failures WHERE user_id=?), 0) + 1, ?, ?)",
            (user_id, user_id, lock_time, now)
        )
```

**Files to modify**:
- `services/auth/totp.py` — persist rate limiting state to SQLite

---

### Task 9: Write The First 10 Real Tests

**Why this matters**: You cannot trust a trading system with zero tests. Every future change could silently break something. These 10 tests protect the most critical paths — the ones where a bug means wrong trades or lost money.

**What to create**: `tests/test_critical_paths.py`

```python
# Test 1: Paper broker can open a long position
def test_paper_broker_open_long():
    order = submit_market_order(instrument="BTCUSDT", asset_class="crypto",
                                side="BUY", price=50000.0, notional=1.0)
    assert order.status == "filled"
    assert order.quantity > 0

# Test 2: Paper broker enforces stop loss requirement
def test_paper_broker_rejects_without_stop():
    # Signal interpreter must return NO_TRADE if stop is None
    signal = normalize_candidate(...)
    assert signal["stop"] is not None or signal["direction"] == "NO_TRADE"

# Test 3: Risk decision rejects when risk > 2%
def test_risk_rejects_oversized_position(): ...

# Test 4: LiveGate blocks when AI_CAN_EXECUTE_LIVE=false
def test_live_gate_blocks_ai_execution(): ...

# Test 5: Signal normalization produces valid contract
def test_signal_contract_completeness(): ...

# Test 6: Fleet cycle runs without error
def test_fleet_cycle_completes(): ...

# Test 7: Paper broker handles close position correctly
def test_paper_broker_close_position(): ...

# Test 8: Paper broker tracks P&L accurately
def test_paper_broker_pnl_calculation(): ...

# Test 9: Approval token expires correctly
def test_approval_token_expiry(): ...

# Test 10: Position sizing respects max notional
def test_position_size_limit(): ...
```

**Files to create**:
- `tests/conftest.py` — test fixtures, temp database setup
- `tests/test_critical_paths.py` — the 10 tests above

**Verification**: `python -m pytest tests/ -v` — all 10 must pass

---

### Task 10: Add Database Backups

**Why this matters**: Your SQLite databases contain ALL trade history, paper positions, fleet state, and learned knowledge. If they get corrupted (power loss, disk issue, bad write), you lose everything the bots learned.

**What to do**:
Create `scripts/backup-databases.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/Users/macmac/Documents/Codex/FX/backups/$(date +%Y-%m-%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp data/fx.db "$BACKUP_DIR/"
cp data/local_paper/local_paper.sqlite3 "$BACKUP_DIR/"
cp data/paper_fleet/fleet.sqlite3 "$BACKUP_DIR/"
echo "Backup complete: $BACKUP_DIR"
# Keep only last 30 days
find /Users/macmac/Documents/Codex/FX/backups -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

Add to crontab: `0 */6 * * * /Users/macmac/Documents/Codex/FX/scripts/backup-databases.sh`

---

## Phase 2 — Build Missing Core (Tasks 11-20)

*Now the foundation is solid. Build the components needed for real bot training.*

---

### Task 11: Build Binance Data Provider

**Why this matters**: This is the #1 blocker. Without real-time crypto data, the bot cannot observe or trade crypto markets. Binance has the most liquid crypto markets and a testnet for safe testing.

**What to create**: `providers/binance/binance_provider.py`
- Async REST client using `httpx` for klines, ticker, orderbook
- WebSocket client for real-time price stream
- Testnet URL switching via `settings.binance_testnet_enabled`
- Rate limiting (1200 requests/minute for Binance)
- Automatic reconnection on WebSocket disconnect
- Returns standardized OHLCV format matching LSE provider

**What to create**: `providers/binance/binance_executor.py`
- Implements `BrokerAdapter` ABC from `services/execution/broker_adapter.py`
- Methods: `health()`, `account()`, `positions()`, `submit_order()`, `cancel_order()`
- Testnet-only by default
- Maps Binance order types to `CanonicalOrder` / `CanonicalOrderResult`

**Dependencies**: Task 3 (config), Task 1 (connection management)

---

### Task 12: Build Unified Data Feed

**Why this matters**: The bot needs ONE interface to get price data regardless of asset class. Currently each provider has its own format, and the fleet uses Yahoo Finance as a hacky fallback.

**What to create**: `providers/multi_asset_feed.py`
```python
class MultiAssetFeed:
    async def get_ohlcv(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Returns standardized OHLCV regardless of asset class."""
        asset_class = self._classify(symbol)  # BTCUSDT→crypto, EURUSD→forex, AAPL→stocks
        if asset_class == "crypto":
            return await self.binance.get_klines(symbol, interval, limit)
        elif asset_class in ("forex", "commodities"):
            return await self.lse.history(symbol, interval, limit)
        elif asset_class == "stocks":
            return await self.yahoo.get_history(symbol, interval, limit)

    async def get_price(self, symbol: str) -> float:
        """Current price for any symbol."""
        ...
```

**Dependencies**: Task 11 (Binance provider)

---

### Task 13: Build Historical Data Storage

**Why this matters**: Without stored historical data, the bot cannot backtest strategies, measure performance over time, or train on past market conditions. Every time the fleet runs, it re-downloads 6 months of data from Yahoo Finance — wasteful and unreliable.

**What to do**:
- Create `services/data/market_store.py` — stores OHLCV data in Parquet files organized by `data/parquet/{asset_class}/{symbol}/{interval}/`
- Create `services/data/data_quality.py` — validates incoming data (no gaps, no future timestamps, no negative prices, reasonable OHLCV relationships)
- Create `scripts/fetch-historical-data.py` — one-time download of 2 years of daily data for all starting pairs
- Wire fleet to read from local Parquet first, API only if local data is stale

**Starting pairs to fetch**:
- Crypto: BTCUSDT, ETHUSDT (Binance)
- Forex: EURUSD, GBPUSD, USDJPY (LSE)
- Commodities: XAUUSD (Gold), WTICL (Oil) (LSE)
- Stocks: AAPL, MSFT, SPY (Yahoo Finance)

**Dependencies**: Task 12 (unified feed)

---

### Task 14: Build Proper Strategy Engine

**Why this matters**: The current fleet has 16 strategies but 6 are stubs, and the ones that work use simplistic logic (e.g., just EMA crossover). For the bot to learn real patterns, the strategies need to produce signals with proper stops, targets, and confidence scores — not hardcoded 1.5×ATR stops for everything.

**What to create**: `services/strategies/adaptive_strategies.py`

Each strategy must:
1. Accept OHLCV data from any timeframe
2. Calculate asset-specific parameters (Gold stops differ from BTCUSDT stops)
3. Return the full normalized signal contract (entry, stop, target_1, target_2, profit_plan, expected_r, confidence)
4. Include a `NO_TRADE` path when conditions aren't met
5. Track its own historical performance

**7 strategies to implement**:
1. Trend Following — EMA 9/21/55 + ADX confirmation + Kalman smoothing
2. Mean Reversion — Bollinger(20,2) + RSI(14) + Z-score
3. Momentum — MACD(12,26,9) + ROC(14) + volume confirmation
4. Breakout — 20-period high/low breakout + ATR expansion + volume surge
5. Regime Detector — ADX + ATR percentile + Bollinger width → TRENDING/RANGING/VOLATILE
6. Confluence Scorer — Weighted vote across strategies 1-4, filtered by regime
7. Monte Carlo Sizer — 1,000 path simulation for position sizing

**Fix existing**: Update `services/bot_signals/interpreter.py` to use asset-specific stop calculations instead of hardcoded 1.5×ATR for everything.

**Dependencies**: Task 13 (historical data for calibration)

---

### Task 15: Build Trade Journal With Persistence

**Why this matters**: The bot cannot learn if it doesn't remember what happened. Currently, the learning module (`market_learning.py`) stores everything in memory — restart the app and all knowledge is gone.

**What to create**: `services/journal/trade_journal.py`

SQLite tables:
```sql
-- Every single decision cycle, including NO_TRADE
CREATE TABLE bot_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    instrument TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    timeframe TEXT,
    regime TEXT,
    adx REAL, atr REAL, rsi REAL, macd_hist REAL,
    ema9 REAL, ema21 REAL, ema55 REAL,
    z_score REAL, volume_ratio REAL, spread REAL,
    trend_signal INTEGER, mean_rev_signal INTEGER,
    breakout_signal INTEGER, momentum_signal INTEGER,
    confluence_score REAL,
    final_decision TEXT NOT NULL,  -- LONG, SHORT, NO_TRADE
    entry_price REAL, stop_price REAL,
    target_1 REAL, target_2 REAL,
    risk_pct REAL, expected_r REAL,
    readiness_level INTEGER
);

-- Every executed trade with full outcome
CREATE TABLE bot_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER REFERENCES bot_decisions(id),
    instrument TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL, entry_time REAL NOT NULL,
    exit_price REAL, exit_time REAL,
    stop_price REAL, target_1 REAL, target_2 REAL,
    quantity REAL, realized_pnl REAL,
    max_adverse_excursion REAL,  -- worst drawdown during trade
    max_favorable_excursion REAL,  -- best unrealized profit during trade
    strategy_used TEXT, regime_at_entry TEXT,
    exit_reason TEXT,  -- STOP_HIT, TARGET_HIT, SIGNAL_REVERSAL, TIME_EXIT
    duration_seconds REAL
);

-- Aggregated lessons learned from trade outcomes
CREATE TABLE bot_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument TEXT, asset_class TEXT, strategy TEXT,
    regime TEXT, timeframe TEXT,
    sample_size INTEGER NOT NULL,
    win_rate REAL, avg_win_r REAL, avg_loss_r REAL,
    expectancy REAL, profit_factor REAL,
    observation TEXT NOT NULL,  -- human-readable insight
    confidence_level REAL,
    created_at REAL, updated_at REAL
);
```

**Dependencies**: Task 2 (database management), Task 14 (strategies produce proper signals)

---

### Task 16: Build Readiness Gate

**Why this matters**: This is YOUR key requirement — "if the bot feels that it is not enough trained, it will not be available to use." The readiness gate is the bot's self-assessment system.

**What to create**: `services/bots/readiness_gate.py`

```python
class ReadinessGate:
    def assess(self, asset_class: str) -> ReadinessLevel:
        stats = self.journal.get_stats(asset_class)

        # Level 0: OBSERVING — not enough data
        if stats.total_observations < 500:
            return ReadinessLevel.OBSERVING

        # Level 1: PAPER_TESTING — enough observations, testing paper trades
        if stats.total_paper_trades < 50:
            return ReadinessLevel.PAPER_TESTING

        # Level 2: VALIDATED — enough paper trades, checking performance
        if not self._meets_performance_criteria(stats):
            return ReadinessLevel.PAPER_TESTING  # demote

        if stats.total_paper_trades < 200:
            return ReadinessLevel.VALIDATED

        # Level 3: READY — validated performance over 200+ trades
        if self._meets_extended_criteria(stats):
            return ReadinessLevel.READY

        return ReadinessLevel.VALIDATED

    def _meets_performance_criteria(self, stats) -> bool:
        return (
            stats.win_rate_30 >= 0.50 and      # 50%+ win rate over last 30 trades
            stats.expectancy_30 > 0 and         # positive expectancy
            stats.max_drawdown < 0.20 and       # drawdown under 20%
            stats.profit_factor_30 > 1.1        # profit factor > 1.1
        )
```

**Dependencies**: Task 15 (trade journal provides the stats)

---

### Task 17: Connect Learning Module To Persistence

**Why this matters**: `market_learning.py` currently loses ALL data on restart. The bot needs to remember what it learned across restarts.

**What to modify**: `services/learning/market_learning.py`
- Save `OnlineMoments` state (n, mean, m2) to SQLite periodically
- Load on startup
- Add per-strategy performance tracking: "Trend Following on Gold during London session = 62% win rate over 47 samples"

**What to create**: `services/memory/strategy_memory.py`
- SQLite-backed pattern store
- Methods: `record_outcome()`, `get_strategy_performance()`, `get_best_regime_for_strategy()`, `get_known_bad_setups()`
- Feeds learned patterns back into the confluence scorer as weight adjustments

**Dependencies**: Task 15 (journal provides outcomes to learn from)

---

### Task 18: Wire Alpaca To BrokerAdapter ABC

**Why this matters**: The `BrokerAdapter` ABC defines a clean interface but nothing implements it. The Alpaca client is standalone with its own API. For the system to support multiple brokers through one interface, Alpaca needs to conform to the adapter pattern.

**What to modify**: `providers/alpaca/paper_client.py`
- Implement `BrokerAdapter` ABC methods
- Add async support (currently sync only)
- Add error handling and retry logic
- Map Alpaca responses to `CanonicalOrder` / `CanonicalOrderResult`

**Dependencies**: Task 11 (Binance executor also implements the same ABC, so both brokers work the same way)

---

### Task 19: Add Jinja2 Templating

**Why this matters**: Every web page is a massive HTML string embedded in Python. Terminal.py is 3,786 lines of inline HTML. This makes UI changes painful, breaks IDE support, and makes the code unmaintainable.

**What to do**:
1. Install Jinja2: `pip install jinja2`
2. Create `backend/app/templates/` directory
3. Create a base template: `templates/base.html` (shared header, nav, CSS, JS)
4. Extract each page into its own template: `templates/terminal.html`, `templates/global_markets.html`, etc.
5. Modify each web route to render the template instead of returning inline HTML

**Start with**: Terminal and Global Markets pages (most used). Convert remaining pages one at a time.

**Dependencies**: None (can run in parallel with other tasks)

---

### Task 20: Expand Test Suite To 30+ Tests

**Why this matters**: Task 9 created 10 critical tests. Now we need to cover the new components built in Tasks 11-18.

**Tests to add**:
```
tests/
├── test_critical_paths.py      (10 tests — from Task 9)
├── test_binance_provider.py    (5 tests — connection, klines, ticker, rate limit, reconnect)
├── test_strategies.py          (7 tests — one per strategy, signal contract validation)
├── test_readiness_gate.py      (4 tests — level transitions, demotion, promotion, edge cases)
├── test_trade_journal.py       (4 tests — record decision, record trade, aggregate lessons, persist across restart)
├── test_data_quality.py        (3 tests — gap detection, future timestamp rejection, negative price rejection)
└── conftest.py                 (fixtures, temp databases, mock market data)
```

**Dependencies**: Tasks 11-18 (need the components to test)

---

## Phase 3 — Build The Autonomous Bot (Tasks 21-26)

*The foundation is fixed, the core components exist. Now build the brain.*

---

### Task 21: Build Auto-Trader Controller

**What to create**: `services/bots/auto_trader.py`

The main autonomous loop:
```python
class AutoTrader:
    async def run_cycle(self):
        # 1. Check profit target
        if self.profit_monitor.check(self.equity) == "TARGET_REACHED":
            await self.stop("Profit target reached")
            return

        # 2. Check readiness
        level = self.readiness_gate.assess(self.asset_class)
        if level == ReadinessLevel.OBSERVING:
            await self.observe_only()  # record data, no trades
            return

        # 3. Fetch market data
        ohlcv = await self.feed.get_ohlcv(self.symbol, self.timeframe, 200)

        # 4. Compute features and regime
        regime = self.regime_detector.detect(ohlcv)

        # 5. Run all strategies
        signals = [strategy.generate(ohlcv, regime) for strategy in self.strategies]

        # 6. Confluence vote
        final = self.confluence.vote(signals, regime)

        # 7. Record decision (even NO_TRADE)
        self.journal.record_decision(final, ohlcv, regime)

        # 8. Execute if actionable
        if final.direction == "NO_TRADE":
            return

        if level < ReadinessLevel.PAPER_TESTING:
            return  # observe only, no execution even on paper

        # 9. Risk check
        if not self.risk_gate.approve(final, self.account):
            self.journal.record_veto(final, "Risk gate rejected")
            return

        # 10. Execute
        await self.execute(final)

        # 11. Learn from outcome (when trade closes)
        # handled by trade_journal on position close
```

**Dependencies**: Tasks 14 (strategies), 15 (journal), 16 (readiness), 12 (data feed)

---

### Task 22: Build Profit Target & Risk Controls

**What to create**: Part of `services/bots/auto_trader.py`

```python
# Cooling periods
COOLING_RULES = {
    3: {"pause_hours": 1, "size_reduction": 0.50},   # 3 consecutive losses
    5: {"pause_hours": 2, "size_reduction": 0.25},   # 5 consecutive losses
}

# Daily/weekly limits
MAX_DAILY_LOSS_PCT = 0.05    # 5% of capital
MAX_WEEKLY_LOSS_PCT = 0.10   # 10% of capital

# Demotion triggers
DEMOTION_TRIGGERS = {
    "negative_expectancy_50": "Rolling 50-trade expectancy < 0",
    "drawdown_25": "Drawdown exceeds 25%",
    "win_rate_below_40": "Win rate below 40% over 50 trades",
}
```

---

### Task 23: Build Telegram Alerts

**Why this matters**: You can't watch the dashboard 24/7. Telegram notifications tell you when something important happens — trade taken, target hit, bot demoted, error occurred.

**What to create**: `services/notifications/telegram.py`

Events to notify:
- Trade opened (instrument, side, entry, stop, target)
- Trade closed (instrument, P&L, duration)
- Profit target reached
- Readiness level change (promotion or demotion)
- Daily summary (trades, P&L, equity, readiness)
- Error/critical failure

Setup: Create a Telegram bot via @BotFather (free), get the token, add to `.env`.

**Dependencies**: None (can run in parallel)

---

### Task 24: Add WebSocket Support

**Why this matters**: Right now every page requires manual refresh. With WebSockets, the dashboard updates in real-time: live prices, bot status, position changes, P&L updates.

**What to do**:
- Add WebSocket endpoint: `/ws/auto-trader`
- Push events: price updates, bot decisions, trade executions, readiness changes
- Modify dashboard JavaScript to connect via WebSocket and update DOM

**Dependencies**: Task 26 (dashboard)

---

### Task 25: Build Auto-Trader API

**What to create**: `backend/app/api/auto_trader.py`

```
GET  /api/auto-trader/status          — readiness, equity, P&L, target progress per asset
GET  /api/auto-trader/suggestions     — current entry suggestions with confidence
GET  /api/auto-trader/trades          — trade history with full details
GET  /api/auto-trader/knowledge       — learned patterns per strategy/asset/regime
GET  /api/auto-trader/readiness       — detailed readiness metrics per asset class
GET  /api/auto-trader/performance     — strategy performance breakdown
POST /api/auto-trader/start           — start bot for an asset class
POST /api/auto-trader/stop            — stop bot
POST /api/auto-trader/configure       — set target, capital, pairs
```

---

### Task 26: Build Auto-Trader Dashboard

**What to create**: `backend/app/web/auto_trader.py` + `backend/app/templates/auto_trader.html`

Dashboard at `/auto-trader` showing:
- **Readiness Level** per asset class with progress bars (Level 0 → 3)
- **Profit Target** progress bar (e.g., \$1.00 → \$3.47 / \$20.00 target)
- **Current Position** — instrument, side, entry, current price, unrealized P&L
- **Entry Suggestions** — next signal with confidence, entry, stop, targets
- **Trade History** — table with filters by date, instrument, strategy, outcome
- **Strategy Scoreboard** — which strategies are winning/losing per regime
- **Knowledge Log** — what the bot has learned, human-readable insights
- **Controls** — Start / Stop / Reset / Change Target

---

## Phase 4 — Harden For Production (Tasks 27-30)

*The system works. Now make it production-grade so you can trust it with real money.*

---

### Task 27: Dockerize

**Why this matters**: Your Mac sleeps. Docker lets you run the bot on a \$5/month VPS 24/7.

**What to create**:
- `Dockerfile` — Python 3.11, install deps, run FastAPI
- `docker-compose.yml` — app + optional Redis for caching
- `infrastructure/deploy.sh` — one-command deployment to VPS

---

### Task 28: Build Strategy Validation Pipeline

**Why this matters**: You have 47 imported Freqtrade strategies and 10 MT5 strategy reports sitting unused. The documented lifecycle (EXTERNAL_UNTRUSTED → APPROVED) exists as documentation but no code runs it.

**What to create**: `services/validation/pipeline.py`
- Backtest runner using Backtrader (already installed)
- Out-of-sample splitter (70/15/15 train/validate/holdout)
- Walk-forward validator
- Monte Carlo simulator
- Cost stress test (2x, 3x normal spread)
- Auto-reject strategies with < 50% OOS win rate or < 1.0 profit factor
- Promote passing strategies through the lifecycle directories

---

### Task 29: Build Freqtrade Strategy Adapter

**Why this matters**: 47 Freqtrade strategies sit in `strategy_sources/imported/` doing nothing. An adapter translates their signals into FX's normalized format.

**What to create**: `services/strategies/freqtrade_adapter.py`
- Parses Freqtrade `IStrategy` classes
- Extracts `populate_buy_trend()` and `populate_sell_trend()` logic
- Translates to FX signal contract (entry, stop, target, direction)
- Marks adapted strategies as `EXTERNAL_UNTRUSTED` in registry
- Feeds them into the validation pipeline (Task 28)

---

### Task 30: Monitoring & System Health

**What to create**: `services/monitoring/health_dashboard.py`

Tracks:
- Database sizes and growth rate
- API response times (p50, p95, p99)
- Bot cycle times
- LLM availability
- Data feed freshness (how old is the latest price?)
- Strategy drift (is performance degrading?)
- System resource usage (CPU, memory, disk)

Alerts via Telegram (Task 23) when:
- Database > 500MB
- API p95 > 5 seconds
- Data feed stale > 5 minutes
- Any strategy's rolling 30-trade expectancy turns negative

---

## Execution Order & Dependencies

```
WEEK 1: Tasks 1-10 (Foundation)
  1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10
  (sequential — each builds on the last)

WEEK 2: Tasks 11-13 (Data Layer)
  11 → 12 → 13
  (sequential — feed → unified → storage)

WEEK 3: Tasks 14-18 (Trading Core)
  14, 15, 16, 17 can run in parallel
  18 depends on 11
  19 can run in parallel with everything

WEEK 4: Tasks 21-26 (Autonomous Bot)
  21 depends on 14, 15, 16, 12
  22 depends on 21
  23 can run in parallel
  24 depends on 26
  25 depends on 21
  26 depends on 25

WEEK 5-6: Tasks 27-30 (Production Hardening)
  All can run in parallel
  20 can run at any time after the components it tests exist
```

---

## What This Gives You At The End

After all 30 tasks:

1. ✅ **Trustworthy foundation** — no connection leaks, no silent failures, proper auth, proper logging
2. ✅ **Real market data** — Binance (crypto), LSE (forex/commodities), Yahoo/Alpaca (stocks) all through one interface
3. ✅ **7 adaptive strategies** — each producing proper signals with stops and targets calibrated per asset
4. ✅ **Self-aware bot** — refuses to trade until it proves itself through 4 readiness levels
5. ✅ **Complete trade journal** — every decision recorded, including NO_TRADE, with full analysis
6. ✅ **Learning system** — bot builds knowledge over time, remembers across restarts, feeds patterns back into strategies
7. ✅ **Profit targeting** — set \$1 → \$20, bot trades until target is hit then stops
8. ✅ **Safety controls** — cooling periods, daily limits, demotion, LiveGate for real money
9. ✅ **Dashboard** — real-time view of everything the bot is doing and learning
10. ✅ **Telegram alerts** — know immediately when something happens
11. ✅ **33+ automated tests** — catch bugs before they reach your bot
12. ✅ **Production-ready** — Docker deployment, backups, monitoring, health checks

# FX Project — Complete Forensic Analysis Report

**Date**: September 5, 2026
**Scope**: Every Python source file, configuration, provider, strategy, test, and data structure
**Method**: Three parallel forensic analysts read all code line by line
**Files analyzed**: 80+ Python files, ~10,000+ lines of code

---

## Project Vital Signs

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Python files | 80+ | Substantial codebase |
| Backend files | 28 (~5,190 lines) | PARTIAL — mix of solid and stub |
| Services files | 20+ (~3,500 lines) | PARTIAL — core exists, many stubs |
| Providers | 6 directories, only 2 have code | 🔴 CRITICAL GAP |
| Tests | 1 file (7 lines: `assert True`) | 🔴 ZERO real tests |
| Strategies in pipeline | 0 at any stage | 🔴 Pipeline is documentation only |
| Infrastructure | Empty directory | 🔴 No deployment capability |
| Historical data stored | 0 bytes (Parquet/DuckDB empty) | 🔴 No data persistence |

---

## 🔴 CRITICAL ISSUES (9)

These are bugs or gaps that would cause failures, data loss, or security breaches in production.

### 1. SQLite Connection Leaks — Every Database Call
**Files**: [broker.py](file:///Users/macmac/Documents/Codex/FX/services/local_paper/broker.py), [store.py](file:///Users/macmac/Documents/Codex/FX/services/bot_signals/store.py), [ttl_cache.py](file:///Users/macmac/Documents/Codex/FX/services/cache/ttl_cache.py), [supervisor.py](file:///Users/macmac/Documents/Codex/FX/services/agents/supervisor.py)

All database calls use `with _connect() as conn:` which handles transactions but **does NOT close the connection** in Python's `sqlite3`. Every function call opens a new connection that is never closed, leaking file descriptors and memory. On a bot running every 60 seconds, this will exhaust system resources within hours.

### 2. Schema Migration Runs On EVERY Database Call
**File**: [broker.py](file:///Users/macmac/Documents/Codex/FX/services/local_paper/broker.py) L69-277

The `_connect()` function runs `CREATE TABLE IF NOT EXISTS` for 5 tables AND an `ALTER TABLE` migration check on every single call. A bot calling `positions()` then `submit_market_order()` then `get_account()` runs the full schema creation 3 times per cycle.

### 3. Zero Authentication On All Endpoints
**File**: [main.py](file:///Users/macmac/Documents/Codex/FX/backend/app/main.py)

No authentication middleware exists. Every API endpoint is publicly accessible on port 8000. Anyone on the same network can start/stop bots, submit paper trades, and access all data. No CSRF protection on POST endpoints either.

### 4. TOTP Rate Limiting Is In-Memory Only
**File**: [totp.py](file:///Users/macmac/Documents/Codex/FX/services/auth/totp.py) L29-30

TOTP failure counting (`_failures`, `_locked_until`) is stored in instance variables. Server restart = rate limiting wiped = brute-force possible.

### 5. Chat API Has No Fallback — Ollama Down = Entire Feature Dead
**File**: [chat.py](file:///Users/macmac/Documents/Codex/FX/backend/app/api/chat.py) L46-87

Hardcoded to Ollama with a 90-second timeout. If Ollama is down, the entire chat feature crashes. Despite `.env.example` having OpenRouter and Kimi configured, there's no fallback chain.

### 6. Binance Provider Is COMPLETELY EMPTY
**Directory**: [providers/binance/](file:///Users/macmac/Documents/Codex/FX/providers/binance/)

Zero files. No crypto data feed. No crypto execution. The `.env.example` has `BINANCE_TESTNET_*` variables but nothing uses them. **This is the #1 blocker for the autonomous trading bot goal.**

### 7. Dead Code — Entire Training Page Is Unreachable
**File**: [training.py](file:///Users/macmac/Documents/Codex/FX/backend/app/web/training.py) L20+

The `training()` endpoint returns a `RedirectResponse` on line 20, making the 400+ lines of HTML code after it completely unreachable.

### 8. Silent Route Failures Hide Critical Errors
**File**: [main.py](file:///Users/macmac/Documents/Codex/FX/backend/app/main.py) L102-183

Entire route suites are wrapped in `except Exception:` blocks that just `print()` a warning. If a critical service breaks, the API starts with half its routes missing — silently.

### 9. Broker API Returns Mock Data As If Real
**File**: [broker.py](file:///Users/macmac/Documents/Codex/FX/backend/app/api/broker.py) L42-76

When Alpaca is disabled (the default), the endpoint returns hardcoded \$100,000 account data with `"mock": True` buried in the response. The UI shows this as if it's real account data with no visual indicator.

---

## 🟠 MAJOR GAPS (16)

These are missing components that prevent the system from functioning as described in README.md and AGENTS.md.

### Backend & Architecture

| # | Gap | Description |
|---|-----|-------------|
| 10 | **`backend/app/core/` is EMPTY** | Intended for shared config, DB connections, utilities. Configuration is scattered across files with `os.getenv()` calls. |
| 11 | **No templating engine** | All 28 web pages generate HTML inline in Python strings. Some are 3,000+ lines of minified HTML/CSS/JS embedded in Python. |
| 12 | **No WebSocket support** | All data served via REST polling. No real-time price updates, no live bot status, no streaming signals. |
| 13 | **Agent architecture is a STUB** | [fx_agents.py](file:///Users/macmac/Documents/Codex/FX/backend/app/routes/fx_agents.py) returns a hardcoded placeholder list. None of the 12 specialist agents described in AGENTS.md (Macro, Forex, Crypto, Trend, etc.) actually exist. |

### Services

| # | Gap | Description |
|---|-----|-------------|
| 14 | **6/16 strategies are stubs** | [fleet.py](file:///Users/macmac/Documents/Codex/FX/services/paper_fleet/fleet.py) L256-265: Pairs Trading, Cross-Sectional Momentum, Carry, Institutional Positioning, Activist Event, and Options Volatility all return "Waiting for validated adapter". |
| 15 | **Learning module is in-memory only** | [market_learning.py](file:///Users/macmac/Documents/Codex/FX/services/learning/market_learning.py): All learned data (returns, variance) is lost on restart. Nothing persists. Nothing acts on what it learns. |
| 16 | **Reconciler is naive** | [reconciler.py](file:///Users/macmac/Documents/Codex/FX/services/reconciliation/reconciler.py): Only checks `internal_qty - broker_qty > tolerance`. Doesn't handle partial fills, in-flight orders, P&L discrepancies, or execution latency. |
| 17 | **Signal interpreter has toy logic** | [interpreter.py](file:///Users/macmac/Documents/Codex/FX/services/bot_signals/interpreter.py): Stop is always 1.5×ATR, target always 1.0×ATR. No asset-specific calibration, no volatility-adjusted stops, no structural analysis. |
| 18 | **BrokerAdapter ABC has ZERO implementations** | [broker_adapter.py](file:///Users/macmac/Documents/Codex/FX/services/execution/broker_adapter.py) defines the interface but nothing implements it. Alpaca client doesn't use it either. |

### Infrastructure & Data

| # | Gap | Description |
|---|-----|-------------|
| 19 | **Zero tests** | [tests/](file:///Users/macmac/Documents/Codex/FX/tests/) has only `test_placeholder.py` with `assert True`. No unit, integration, strategy, or risk tests. |
| 20 | **No historical data storage** | `data/parquet/` and `data/duckdb/` are empty. No market data is stored locally. Fleet uses Yahoo Finance live calls. |
| 21 | **Infrastructure directory is empty** | No Docker, docker-compose, deployment scripts, monitoring config, or backup scripts. |
| 22 | **No backup system** | SQLite databases contain all trade history, paper positions, and fleet state. Zero backup mechanism. |
| 23 | **Strategy pipeline is documentation only** | All 5 strategy lifecycle directories (`deployed/`, `generated/`, `validated/`, `vault/`, `retired/`) are EMPTY. No strategy has ever been validated through the documented pipeline. |
| 24 | **47 imported Freqtrade strategies are unusable** | Raw Freqtrade `IStrategy` files in `strategy_sources/imported/`. No adapter exists to convert them to FX signal format. |
| 25 | **MT5 .ex5 binaries are black boxes** | 10+ compiled MetaTrader Expert Advisors in `vendor/`. Binary format — cannot extract logic for use in Python. |

---

## 🟡 QUALITY CONCERNS (11)

### Code Quality

| # | Concern | Location |
|---|---------|----------|
| 26 | **Broad `except Exception:` everywhere** | `api/global_markets.py`, `api/chat.py`, `api/market.py`, `api/control_center.py`, `api/strategy_lab.py` — hides critical bugs |
| 27 | **No request/response validation** | Most API endpoints accept raw dicts. Only `risk/decision_contract.py` uses Pydantic models. |
| 28 | **`__init__.py` files are almost all empty** | No proper module exports. Forces deep import paths (`from services.execution.live_gate import LiveGate` instead of `from services.execution import LiveGate`). |
| 29 | **Dynamic import anti-pattern** | [control_center.py](file:///Users/macmac/Documents/Codex/FX/backend/app/api/control_center.py) L134: `await __import__("asyncio").to_thread(...)` instead of module-level import. |
| 30 | **Journal page is minified HTML on one line** | [journal.py](file:///Users/macmac/Documents/Codex/FX/backend/app/web/journal.py): Entire HTML/JS is one unreadable line. |
| 31 | **Fleet uses Yahoo Finance as fallback** | [fleet.py](file:///Users/macmac/Documents/Codex/FX/services/paper_fleet/fleet.py) L106-134: Should use London Strategic Edge but falls back to `yfinance`. |
| 32 | **Sparse router is naive** | [sparse_router.py](file:///Users/macmac/Documents/Codex/FX/services/agents/sparse_router.py): Routes by hardcoded tag set intersection, not semantic similarity or LLM-based routing. |

### UI/UX

| # | Concern | Location |
|---|---------|----------|
| 33 | **No filtering on journal** | Can't filter trades by date, instrument, strategy, or bot. No P&L summary, no charts, no export. |
| 34 | **No real-time updates** | Everything requires manual page refresh. No auto-update, no WebSocket, no Server-Sent Events. |
| 35 | **No mobile responsiveness** | CSS is basic. Pages break on mobile screens. |
| 36 | **Mock data displayed as real** | Broker account shows \$100,000 mock data with no visual differentiation from real data. |

---

## 🟢 GOOD IMPLEMENTATIONS (8)

What's working well and should be preserved.

| # | Component | Why It's Good |
|---|-----------|---------------|
| 37 | **LiveGate + Execution Policy** | Rigorous safety checks: kill-switch, data quality, reconciliation, TOTP, HMAC-signed approval tokens. Well-separated concerns. |
| 38 | **Local Paper Broker** | 1,095 lines of functional paper trading: longs, shorts, position tracking, P&L, order history, training events. |
| 39 | **Risk Decision Contract** | Comprehensive Pydantic models: `DecisionContext`, `TradePlan`, `CostEstimate`, `PortfolioImpact`, `RiskDecision`, `Provenance`. |
| 40 | **DataHub pub/sub** | Clean async pub/sub with TTL caching and subscriber isolation. |
| 41 | **HMAC-based approval tokens** | Short-lived, strongly-coupled approval tokens that bind intent, expiration, and risk decision. |
| 42 | **Signal normalization contract** | Consistent signal format across all bots and strategies. |
| 43 | **Strategy fleet concept** | \$1 micro-capital per strategy, observation-based learning, NO_TRADE as first-class output. |
| 44 | **Project documentation** | README.md, AGENTS.md, TRADING_SYSTEM_CONSTITUTION.md, RISK_ENGINE_SPEC.md — clear, disciplined, well-thought-out operational rules. |

---

## Improvement Plan — 4 Phases

### Phase 1: Fix Critical Infrastructure (Week 1)
**Goal**: Make the existing system reliable before adding anything new.

1. **Fix SQLite connection leaks** — change `_connect()` to use a connection pool or explicit `conn.close()` in a `try/finally`
2. **Move schema creation out of `_connect()`** — run once at startup, not on every call
3. **Add basic authentication** — even a simple API key middleware protects against network access
4. **Add global exception handler** — FastAPI middleware that logs errors properly instead of swallowing them
5. **Fix training page dead code** — remove the unreachable 400 lines or fix the redirect
6. **Add LLM fallback chain** — Ollama → Kimi → OpenRouter → graceful error message
7. **Persist TOTP rate limiting** — move failure counts to SQLite
8. **Write 10 critical tests**: paper broker order submission, risk decision validation, signal normalization, LiveGate authorization, fleet cycle execution

### Phase 2: Build Missing Core (Weeks 2-3)
**Goal**: Fill the gaps that prevent the system from actually trading.

9. **Implement Binance provider** — data feed + executor implementing `BrokerAdapter` ABC
10. **Implement multi-asset data feed** — unified interface routing to Binance (crypto), LSE (forex/commodities), Yahoo/Alpaca (stocks)
11. **Build strategy engine** — 7 adaptive strategies with proper stop/target calculation per asset class
12. **Build readiness gate** — Level 0-3 self-assessment system
13. **Build trade journal** — persistent SQLite recording of every decision including NO_TRADE
14. **Connect learning module to persistence** — save learned patterns to SQLite, survive restarts
15. **Implement `backend/app/core/`** — centralized config, database manager, shared utilities
16. **Add Jinja2 templating** — extract HTML from Python strings into proper templates

### Phase 3: Autonomous Bot (Weeks 3-4)
**Goal**: Build the autonomous trading bot on top of the solid foundation.

17. **Build auto-trader controller** — main loop with profit targeting, cooling periods, demotion rules
18. **Build confluence scorer** — weighted multi-strategy voting with regime filtering
19. **Build strategy memory** — persistent knowledge base of per-strategy, per-regime performance
20. **Build Telegram alerting** — trade notifications, daily summary, demotion alerts
21. **Add WebSocket support** — real-time price updates and bot status on the dashboard
22. **Build auto-trader dashboard** — readiness level, profit progress, trade history, knowledge log
23. **Wire Alpaca client to BrokerAdapter** — unify all execution through the adapter pattern

### Phase 4: Harden & Scale (Week 5+)
**Goal**: Make the system production-ready.

24. **Dockerize the application** — `Dockerfile` + `docker-compose.yml` for local and VPS deployment
25. **Add database backups** — automated daily backup of all SQLite files
26. **Build CI pipeline** — run tests automatically on code changes
27. **Add monitoring** — system health dashboard, data quality alerts, strategy performance degradation detection
28. **Connect imported strategies** — build Freqtrade-to-FX adapter for the 47 imported strategies
29. **Add historical data pipeline** — fetch and store market data in Parquet/DuckDB for backtesting
30. **Run the strategy validation pipeline** — take the best strategies through the full EXTERNAL_UNTRUSTED → APPROVED lifecycle

---

## The Bottom Line

Your FX project has **excellent architectural thinking** — the documentation, safety rules, risk contracts, and operational philosophy are better than most professional trading systems. The LiveGate, approval tokens, and risk decision contract are genuinely solid.

**The weakness is execution**: many components exist as documentation or stubs rather than working code. The providers are mostly empty, the strategy pipeline has never been run, there are zero tests, and critical bugs (connection leaks, no auth, swallowed exceptions) would cause failures in any sustained operation.

**The path forward**: Fix the foundation first (Phase 1), then build the missing core (Phase 2), then build the autonomous bot on top (Phase 3). Don't build the bot on top of the current foundation — the connection leaks and silent failures will undermine everything.

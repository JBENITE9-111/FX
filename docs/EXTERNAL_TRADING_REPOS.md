# FX External Trading Repository Decisions

## Integrated / adapted

### TradingAgents
Use:
- analyst roles
- bull vs bear debate
- trader proposal
- risk review
- portfolio approval
- decision memory ideas
- point-in-time correctness principles

Do not:
- give the LLM direct broker authority.

### Vibe-Trading
Use:
- price provenance
- adjusted/raw data labeling
- no-look-ahead backtesting
- next-bar execution
- realistic fees/slippage
- kill switch patterns
- broker reconciliation
- OS keyring secret patterns
- shadow account concepts

### AI-Trader
Use:
- agent-native workflow ideas
- Paper Trading concepts
- background worker separation
- trade synchronization patterns

Do not:
- enable uncontrolled copy trading.

### Riskfolio-Lib
Installed.

Use:
- portfolio optimization
- CVaR
- drawdown risk
- hierarchical risk parity
- risk contribution
- Black-Litterman
- portfolio constraints

### Kronos
Installed separately.

Use:
- probabilistic OHLC forecasting

Status:
NOT VALIDATED FOR FX LIVE TRADING.

### Python Quant Trading Strategies
Reference library only.

Extract:
- MACD
- pairs
- London breakout
- Dual Thrust
- RSI
- Bollinger
- Monte Carlo
- option straddle concepts

Important:
Original examples may assume frictionless trading.
FX must add fees, slippage and realistic execution.

## Reference only

### StockSharp
Excellent mature execution architecture and connector reference.

Not embedded because:
- C# ecosystem
- huge separate platform
- duplicates FX execution architecture

### TradeMaster
RL research laboratory only.

No direct live authority.

### Howtrader
Crypto execution/reference framework.

Keep for later exchange-specific research.

### QuantMuse
Research architecture reference.

## Bloomberg

Real Bloomberg market data requires authorized Bloomberg access.

Bloomberg GitHub engineering repositories do not provide free Bloomberg
Professional data.

## BEmu

NEVER A MARKET DATA SOURCE.

Its price values are fabricated.

Permitted uses:
- API compatibility tests
- software testing
- message-shape development

Forbidden:
- model training
- strategy decisions
- trade proposals
- risk calculations
- portfolio valuation

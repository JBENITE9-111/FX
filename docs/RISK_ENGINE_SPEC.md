# FX Deterministic Risk Engine

Risk has absolute veto authority.

Inputs include:

- equity
- cash
- buying power
- margin
- positions
- pending orders
- symbol exposure
- asset-class exposure
- sector exposure
- country exposure
- currency exposure
- factor exposure
- venue exposure
- rolling correlation
- stress correlation
- tail dependence
- volatility
- ATR
- spread
- expected slippage
- liquidity/depth
- market impact
- strategy drawdown
- portfolio drawdown
- daily/weekly loss
- event risk
- data quality
- broker health
- reconciliation state
- execution parity
- strategy health
- model health
- system health
- kill switches

Position sizing:

risk_per_unit = abs(entry - stop)

risk_based_size =
allowed_trade_risk / risk_per_unit

final_position_size =
min(
    risk_based_size,
    liquidity_based_size,
    portfolio_based_size,
    strategy_limit,
    venue_limit,
    broker_limit
)

Correct order:

structural invalidation
-> volatility buffer
-> stop
-> risk allowance
-> position size

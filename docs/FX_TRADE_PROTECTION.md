# FX Local-Paper Trade Protection

FX binds every generated protection plan to its instrument, asset class,
direction, entry, notional, quantity, timeframe, market-data timestamp,
strategy, bot, and plan version. Generated plans expire after five minutes and
are consumed after one order. A changed context requires recalculation.

## Risk calculation

The default per-trade cap is 0.25% of current paper equity. New risk is also
limited by the remaining 2% daily-loss capacity, 3% open-risk capacity, local
position-notional limit, and total-exposure limit.

```text
loss at stop = quantity × abs(entry − stop)
modeled allowance = notional × configured cost bps
planned loss envelope = loss at stop + modeled allowance
```

The envelope is a modeled control, not a guaranteed maximum. Gaps, liquidity,
and slippage can create a worse fill. Quote-level costs are not yet available,
so the default 10 bps allowance is explicitly an assumption and is configurable
with `FX_PAPER_MODELED_COST_BPS` or an asset-class override.

## Automatic paper exits

- `FIXED_1_5R`: closes the full position at 1.5R.
- `SCALE_1R_2R`: closes half at 1R, moves the remaining stop to cost-adjusted
  breakeven, then closes the remainder at 2R.
- `TRAIL_AFTER_1R`: activates at 1R and ratchets a one-ATR stop from the next
  verified source bar.
- A newly submitted user-defined plan establishes the current source bar as its
  baseline, then receives automatic stop protection from the next complete bar;
  unstructured targets remain manual instead of being guessed.
- Legacy positions are preserved, sanitized, and marked `AWAITING_REVIEW`.
  Historical text or stale levels never gain automatic execution authority.

The evaluator runs through the existing authenticated persistent scheduler
every 30 seconds while FX and this Mac are running. Each source bar is evaluated
once. A bar touching both stop and target uses the conservative stop-first
result. Gap-through stops use the adverse opening price plus the configured
modeled allowance. Automatic outcomes are recorded as `AUTO_STOP`,
`AUTO_TARGET_1`, `AUTO_TARGET_2`, or `AUTO_TRAIL` in orders, trades, operations,
and training evidence.

This subsystem cannot place live orders. `AI_CAN_EXECUTE_LIVE=false` remains
mandatory.

# FX Historical Market Memory Baseline

Generated on 2026-09-07 from real London Strategic Edge daily candles. This is
a reproducibility ledger, not a trade recommendation or profitability claim.
All returns below are locked-test results after a 10 bps turnover cost model.

| Instrument | Coverage | Rows | Quality | Strategy | Return | CAGR | Sharpe | Max DD | Profit factor | Trades | Decision |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| EUR/USD | 2020-07-08 to 2026-09-07 | 2,000 | PASS | Trend Following | -4.55% | -2.89% | -0.50 | -9.61% | 0.92 | 8 | NOT_ELIGIBLE |
| EUR/USD | 2020-07-08 to 2026-09-07 | 2,000 | PASS | MACD Trend | -10.05% | -6.45% | -1.16 | -12.11% | 0.82 | 37 | NOT_ELIGIBLE |
| EUR/USD | 2020-07-08 to 2026-09-07 | 2,000 | PASS | Breakout | -4.53% | -2.88% | -1.53 | -4.82% | 0.48 | 52 | NOT_ELIGIBLE |
| BTC/USD | 2021-01-15 to 2026-09-07 | 2,000 | PASS | Trend Following | -22.66% | -20.91% | -0.33 | -41.17% | 0.95 | 10 | NOT_ELIGIBLE |
| BTC/USD | 2021-01-15 to 2026-09-07 | 2,000 | PASS | MACD Trend | +17.00% | +15.40% | 0.55 | -22.80% | 1.08 | 32 | NOT_ELIGIBLE |
| BTC/USD | 2021-01-15 to 2026-09-07 | 2,000 | PASS | Breakout | -1.84% | -1.68% | 0.01 | -22.61% | 1.00 | 55 | NOT_ELIGIBLE |
| AAPL | 2018-10-15 to 2026-09-04 | 2,000 | REVIEW_REQUIRED | All | — | — | — | — | — | — | BLOCKED_DATA_QUALITY |

AAPL contains one absolute close-to-close move above 50% on 2026-05-18 while
the provider adjustment policy is unspecified. Its analogue output and all
strategy evidence are blocked pending source/corporate-action verification.

The positive BTC/USD MACD locked-test result is insufficient for promotion. It
has only 32 position-change observations, a 22.8% maximum drawdown, and has not
passed parameter stability, Monte Carlo, multiple-testing adjustment,
independent replay, protected stop/target simulation, or portfolio risk review.

Local retained storage for this baseline is approximately 2.0 MiB including
both schema generations created during validation. Runtime data and result JSON
remain ignored by Git; immutable experiment manifests in the local registry
preserve the failures.

# FX Historical Data Roadmap

## Completed foundation

- source, dataset, artifact, and experiment registry;
- bounded immutable raw and curated storage;
- UTC/OHLC quality checks and discontinuity review;
- leakage-aware daily regimes and dated analogues;
- chronological cost-stressed research exams;
- read-only API and reproducible CLI.

## Next phase

1. Verify provider retention terms and equity adjustment policy.
2. Add adjusted equity data and a security master.
3. Implement parameter-stability and Monte Carlo gates.
4. Add a multiple-testing ledger and Deflated Sharpe/PBO evidence.
5. Add deterministic stop/target and spread/slippage fill simulation.
6. Build independent replay and backtest-to-paper reconciliation.
7. Expose evidence in Market Memory and Ask FX without raw JSON.
8. Add point-in-time macro, events, CFTC, and cross-asset inputs.

Tick, quote, order-book, futures-curve, and options history remain later phases.
They should be acquired only for strategies that require them and only after
license, storage, and query-cost review.

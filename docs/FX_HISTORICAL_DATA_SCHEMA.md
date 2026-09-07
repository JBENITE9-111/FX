# FX Historical Data Schema

## Canonical daily bars (`ohlcv-utc-v2`)

Required fields:

```text
timestamp  UTC, unique, ascending
open       positive numeric
high       >= open, low, close
low        <= open, high, close
close      positive numeric
```

`volume` is optional because several Forex sources do not provide comparable
centralized volume. Provider fields may be retained as additional columns.

## Registry entities

- `sources`: authority, license class, retention and redistribution policy.
- `datasets`: source, dataset, symbol, asset class, venue, timeframe, schema,
  and corporate-action policy.
- `artifacts`: content hashes, paths, coverage, quality, lineage, and Git commit.
- `experiments`: artifact, strategy/version, input hash, result manifest, and
  research status.

Artifacts are content addressed and immutable. Changed data or a changed schema
creates a new identity instead of silently rewriting historical evidence.

## Derived evidence

`market-state-v1` calculates returns, realized volatility, ATR percentage, and
EMA trend gap. Expanding volatility thresholds are shifted by one bar so the
current classification uses only information already available.

`analogues-v1` returns dated non-overlapping matches and a distribution of
forward outcomes. `chronological-cost-stress-v2` records 60/20/20 development,
validation, and locked-test segments with one-bar execution lag and multiple
cost assumptions.

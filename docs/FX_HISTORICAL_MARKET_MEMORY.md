# FX Historical Market Memory

Historical Market Memory converts retained market history into reproducible
research evidence. It does not authorize orders or promise profitability.

## Implemented vertical slice

```text
London Strategic Edge candles
-> UTC/OHLC quality checks
-> immutable raw JSONL
-> content-addressed Zstd Parquet
-> SQLite source/dataset/artifact registry
-> leakage-aware market states
-> dated historical analogues
-> chronological strategy exams with cost stress
-> RESEARCH_ONLY / NOT_ELIGIBLE
```

The authoritative registry is `data/historical/registry.sqlite3`. Raw,
curated, manifest, and experiment artifacts live below `data/historical/` and
are ignored by Git. Every retained artifact has raw and curated SHA-256 hashes,
coverage, row count, schema version, source, adjustment policy, validation
status, lineage, creation time, and producing Git commit.

## Commands

Build a bounded daily research artifact:

```bash
cd /Users/macmac/Documents/Codex/FX
.venv-core/bin/python scripts/build-market-memory.py \
  --symbol 'EUR/USD' --dataset fx --asset-class Forex \
  --timeframe 1d --limit 2000
```

Inspect through the API after starting FX:

```bash
curl -s http://127.0.0.1:8000/api/market-memory/sources
curl -s http://127.0.0.1:8000/api/market-memory/datasets
```

Ingestion is limited to 5,000 rows per request and a 256 MiB default per-run
budget while retaining 5 GiB free disk. Override only deliberately:

```env
FX_HISTORY_MAX_INGEST_BYTES=268435456
FX_HISTORY_MIN_FREE_BYTES=5368709120
```

## Present limits

- Daily bars only for the first strategy-exam version.
- Provider corporate-action treatment is not yet verified.
- Analogues use bar-derived features and omit news, spread, and liquidity.
- Exams model a one-bar lag and 5/10/20 bps cost stress, but not intrabar
  stops, targets, partial fills, market impact, or point-in-time constituents.
- All results remain research evidence. Deterministic risk, protected paper
  examination, independent replay, and the remaining promotion gates still
  apply.

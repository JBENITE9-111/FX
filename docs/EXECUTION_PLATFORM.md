# FX Execution Platform

## Local host

Machine:

- macOS
- Intel x86_64

## Native FX services

The following remain native on the Mac:

- Next.js frontend
- FastAPI
- Ollama
- LLM Router
- Alpaca market data
- Alpaca paper brokerage interface
- CCXT market connectivity
- DuckDB
- Parquet
- Redis
- Polars rtcompat
- pandas
- LightGBM
- XGBoost
- skfolio
- Kronos/model services
- research services
- chart engine
- journal
- audit services

## NautilusTrader

NautilusTrader is not installed into the native Intel macOS environment.

Current upstream supported macOS architecture is ARM64.

The production execution layer will therefore run in an isolated Linux
environment where official x86_64 wheels are supported.

Planned topology:

FX Mac
  |
  | typed execution messages
  |
  v
Nautilus Linux Execution Service
  |
  v
Broker

## Security boundary

The Linux execution service must not expose brokerage credentials to:

- frontend
- LLMs
- generated strategy code
- research agents
- model workers

Only the deterministic execution service may read broker credentials.

Live trading remains disabled until the defined paper/shadow validation
pipeline is complete.

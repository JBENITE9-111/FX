# FinceptTerminal Architecture — Concepts Absorbed Into FX

Source studied:
Fincept-Corporation/FinceptTerminal

Important license note:
The open FinceptTerminal repository is AGPL-3.0-or-later.
FX should use it as an architectural reference unless the project owner explicitly
chooses AGPL-compatible source reuse. Do not copy Fincept source files into FX by default.

## Valuable patterns adopted conceptually

### 1. One-fetch / many-subscribers DataHub

Fincept separates its financial data plane from screens and downstream consumers.

FX adopts the same principle:

provider
-> normalized topic
-> DataHub
-> many subscribers

A single provider request should be shareable by:
- charts
- strategies
- models
- brain panel
- mission control
- alerts
- journal
- workflow nodes

This avoids duplicate API calls and inconsistent snapshots.

### 2. Bounded contexts

Use clear topic namespaces:

market:*
news:*
econ:*
macro:*
crypto:*
derivatives:*
portfolio:*
paper:*
broker:<id>:*
agent:*
workflow:*
risk:*
brain:*
system:*

Cross-context communication should prefer typed events/topics rather than deep imports.

### 3. TTL cache

Data has different useful lifetimes.

Examples:

quotes -> seconds
daily history -> minutes/hours
instrument metadata -> hours/days
fundamentals -> hours/days
macro releases -> event/revision aware

Cache policy belongs near the data plane rather than being reimplemented by each screen.

### 4. Integration adapters

Broker/provider interfaces should translate external APIs into canonical FX types.

External providers should not leak their raw schemas across the whole application.

### 5. Secure credential isolation

Credentials stay outside AI/research code.

FX continues to prefer macOS Keychain / OS-secured credentials for highly sensitive secrets.

### 6. Python worker boundary

Heavy analytics should have a controlled execution boundary.

Long-running/hot analytics should eventually use persistent worker processes rather than
starting a new Python process for every request.

### 7. Unified AI tool surface

Market data, portfolio, research, journal, strategy and workflow operations should be exposed
through a controlled tool registry so different AI providers do not implement separate logic.

### 8. Workflow DAG

The observable FX Brain can evolve into a workflow DAG:

DATA
-> QUALITY
-> REGIME
-> STRATEGY
-> MODELS
-> ANALOGUES
-> COUNTER-THESIS
-> PORTFOLIO
-> RISK
-> EXECUTION FEASIBILITY
-> DECISION

Nodes should be inspectable, typed and replayable.

### 9. Repositories and migrations

Persistent application state should use versioned schema migrations.

Research time-series data remains Parquet + DuckDB.
Small application state/cache/metadata may use SQLite.

### 10. Modular-monolith principle

FX does not need dozens of network microservices just because the architecture has many domains.

Keep local components modular, typed and independently testable.
Use process isolation only where it materially improves compatibility, security or reliability.

Examples where isolation does make sense:
- Kronos
- NautilusTrader Docker
- OpenBB separate environment
- Backtrader validator
- future Hummingbot execution service

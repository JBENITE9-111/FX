# FX Harness V1 — Next Patch

This patch adds four things to the existing FX architecture:

1. **Secure live-action approval**
   - TOTP compatible with Google Authenticator and other RFC 6238 apps.
   - TOTP secrets are stored in the OS keychain through `keyring`, not in `.env`.
   - Live-entry execution remains impossible without a deterministic risk pass + explicit human approval + fresh TOTP.
   - Paper execution can be automated.

2. **TurboVec local memory**
   - Local vector memory for strategy memory, trade memory, failure memory, research memory and historical analogues.
   - Uses `IdMapIndex` so durable FX IDs survive deletes.
   - Uses incremental `sync()` to persist only changes.
   - Raw market ticks/bars remain in Parquet/DuckDB; TurboVec is semantic memory, not the time-series database.

3. **Observable "brain"**
   - FX exposes a structured `DecisionTrace`.
   - It shows stages, tools, evidence IDs, model votes, risk vetoes, hashes, elapsed time and plain-English rationale.
   - It intentionally does **not** expose hidden chain-of-thought. The UI should display auditable evidence/reason summaries instead.

4. **Always-learning market loop**
   - Can ingest market observations every second.
   - Updates streaming statistics and memory continuously.
   - Does **not** retrain or promote capital-controlling models every second.
   - Retraining, validation and promotion remain separate gated processes.

## Important operating law

Paper bots may be fully automatic.

Live entry is never autonomous in this patch:

`AI/Models -> TradeProposal -> deterministic RiskDecision -> user approval -> TOTP -> Execution Service -> Broker`

Broker-native protective exits can run automatically after an approved entry.

## Install

From `/Users/macmac/Documents/Codex/FX`:

```bash
python -m pip install pyotp keyring qrcode[pil] turbovec numpy pydantic
```

Copy the directories in this patch into the matching locations in the FX repository.

Add to `.env.example`:

```env
FX_AUTH_ACCOUNT=jacobo
FX_AUTH_ISSUER=FX
FX_LIVE_APPROVAL_TTL_SECONDS=90

FX_MEMORY_ENABLED=true
FX_MEMORY_DIM=384
FX_MEMORY_BITS=4
FX_MEMORY_PATH=data/memory/fx_memory.tvim

FX_MARKET_LEARNING_INTERVAL_SECONDS=1
FX_MODEL_RETRAIN_INTERVAL_SECONDS=3600

LIVE_TRADING_ENABLED=false
MANUAL_ORDER_APPROVAL_REQUIRED=true
TOTP_REQUIRED_FOR_LIVE=true
AI_CAN_EXECUTE_LIVE=false
```

Do not store a TOTP secret, broker key, or withdrawal credential in `.env`.

## API integration

Mount:

```python
from apps.api.routes.security import router as security_router
from apps.api.routes.brain import router as brain_router

app.include_router(security_router)
app.include_router(brain_router)
```

At startup:

```python
from services.brain.trace import brain_trace_store
from services.memory.turbovec_store import get_memory_store

memory = get_memory_store()
```

## UI

Create a right-side panel called **BRAIN** with:

- RUNNING / COMPLETE / BLOCKED
- current stage
- data sources
- model votes
- strategy matched
- risk checks
- evidence references
- vetoes
- assumptions
- next action

Do not label it "raw chain of thought".

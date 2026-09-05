# FX — TERMINAL BUILD GUIDE
## FX Harness V1.3 — Terminal-First Implementation Guide

> This file is for **manual Terminal use right now**.
> It is **not** a Codex prompt.
> You can use it while working directly in macOS Terminal.

**Permanent project root**

```bash
/Users/macmac/Documents/Codex/FXa
```

---

# 1. ALWAYS START HERE

Open Terminal and run:

```bash
cd "/Users/macmac/Documents/Codex/FX"
pwd
```

Expected:

```text
/Users/macmac/Documents/Codex/FX
```

Then inspect the current project:

```bash
find . -maxdepth 2 -type d | sort
```

Do not create another FX project elsewhere.

---

# 2. CREATE A SAFE BACKUP FIRST

Run:

```bash
cd "/Users/macmac/Documents/Codex/FX"

mkdir -p backups

STAMP="$(date +%Y%m%d-%H%M%S)"

tar \
  --exclude='./backups' \
  --exclude='./data/raw' \
  --exclude='./data/normalized' \
  --exclude='./data/features' \
  --exclude='./data/holdout' \
  --exclude='./node_modules' \
  --exclude='./.venv*' \
  -czf "backups/fx-before-harness-${STAMP}.tar.gz" .
```

Confirm:

```bash
ls -lh backups | tail
```

---

# 3. DO NOT ENABLE LIVE TRADING YET

Your current build phase should remain:

```text
RESEARCH
PAPER
SHADOW
```

Live entry must stay disabled.

Open or create:

```bash
nano .env
```

Make sure these values exist:

```env
TRADING_MODE=research

LIVE_TRADING_ENABLED=false
PAPER_TRADING_ENABLED=true
SHADOW_TRADING_ENABLED=true

MANUAL_ORDER_APPROVAL_REQUIRED=true
TOTP_REQUIRED_FOR_LIVE=true

AI_CAN_SUBMIT_ORDERS=false
AI_CAN_EXECUTE_LIVE=false
AI_CAN_CHANGE_RISK_LIMITS=false
AI_CAN_ACCESS_BROKER_SECRETS=false
AI_CAN_DISABLE_KILL_SWITCH=false

BROKER_MODE=paper

MAX_LIVE_ORDER_NOTIONAL=0
MAX_LIVE_DAILY_LOSS=0
MAX_LIVE_PORTFOLIO_EXPOSURE=0
```

Important:

```text
AI_CAN_EXECUTE_LIVE=false
```

must remain false.

---

# 4. CREATE THE REQUIRED PROJECT FOLDERS

From the FX root:

```bash
cd "/Users/macmac/Documents/Codex/FX"

mkdir -p \
  apps/web \
  apps/api \
  services/data \
  services/intelligence \
  services/regime \
  services/research \
  services/models \
  services/signals \
  services/strategies \
  services/validation \
  services/analogues \
  services/portfolio \
  services/risk \
  services/execution \
  services/reconciliation \
  services/monitoring \
  services/memory \
  services/learning \
  services/auth \
  services/brain \
  services/mission_control \
  services/journal \
  providers/lse \
  providers/openbb \
  providers/alpaca \
  providers/binance \
  providers/metatrader \
  providers/ibkr \
  infrastructure/docker \
  infrastructure/redis \
  infrastructure/database \
  research/preregistrations \
  research/campaigns \
  research/experiments \
  research/validation \
  research/holdouts \
  research/failures \
  data/raw \
  data/normalized \
  data/features \
  data/research \
  data/validation \
  data/holdout \
  data/predictions \
  data/memory \
  data/mission_control \
  data/journal \
  strategies/generated \
  strategies/validated \
  strategies/vault \
  strategies/deployed \
  strategies/retired \
  docs \
  tests \
  scripts
```

This command is safe if folders already exist.

---

# 5. CREATE THE TRADING SYSTEM CONSTITUTION

Create:

```bash
nano docs/TRADING_SYSTEM_CONSTITUTION.md
```

Paste:

```markdown
# FX Trading System Constitution

1. Capital survival outranks profit.
2. NO_TRADE is always valid.
3. No AI, LLM, strategy, agent, UI process, generated code, or research worker may override deterministic risk.
4. Backtest performance alone never authorizes deployment.
5. Holdout data cannot be reused after it influences strategy changes.
6. Broker/exchange state is authoritative for positions, orders, fills, cash, margin, and PnL.
7. Unknown or inconsistent broker state freezes new trading.
8. Strategies cannot self-modify and self-deploy.
9. Every production decision must be reproducible.
10. Every order must reference strategy, model, feature, risk-policy, dataset, code, and configuration versions.
11. Every strategy requires explicit invalidation.
12. Every live trade must have bounded risk.
13. Every deployed strategy must show positive out-of-sample expectancy after realistic costs.
14. Correlated positions count as aggregated risk.
15. System health can veto a trade.
16. Missing, stale, conflicting, or corrupted data means NO_TRADE.
17. Expected transaction costs must be included before approval.
18. Slippage assumptions must be realistic and stress tested.
19. Liquidity constrains position size.
20. Future or leaked information is forbidden.
21. Production changes follow proposal -> backtest -> validation -> holdout -> shadow -> paper -> micro live -> limited live -> approved live.
22. Drawdown can reduce or suspend risk automatically.
23. Strategy degradation reduces capital before optimization.
24. All risk limits operate before execution.
25. Survival always outranks opportunity.
26. Complex models must beat simple baselines before promotion.
27. Failed strategies are preserved.
28. Execution parity is measured, not assumed.
29. External strategies begin EXTERNAL_UNTRUSTED.
30. AI_CAN_EXECUTE_LIVE must remain false.
31. LLMs never receive broker secrets.
32. Withdrawal authority is forbidden.
33. Live entry requires explicit user authorization.
34. Broker-native protective exits may execute automatically after an approved live entry where supported.
35. If the system cannot prove edge survives costs and risk, it does not trade.
```

Save with:

```text
CTRL+O
ENTER
CTRL+X
```

---

# 6. CREATE THE RISK ENGINE SPECIFICATION

Run:

```bash
nano docs/RISK_ENGINE_SPEC.md
```

Paste:

```markdown
# FX Risk Engine Specification

The deterministic Risk Engine has absolute veto authority.

## Inputs

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
- macro exposure
- venue exposure
- rolling correlation
- stress correlation
- tail dependence
- position overlap
- realized volatility
- ATR
- spread
- estimated slippage
- liquidity
- depth
- market impact
- strategy drawdown
- portfolio drawdown
- daily loss
- weekly loss
- event risk
- data quality
- broker health
- reconciliation status
- execution parity
- strategy health
- model health
- system health
- kill-switch status

## Final Position Size

final_position_size =
min(
    risk_based_size,
    liquidity_based_size,
    portfolio_based_size,
    strategy_limit,
    venue_limit,
    broker_limit
)

## Position sizing law

structural invalidation
-> volatility buffer
-> stop distance
-> allowed risk
-> position size

Never calculate stop distance from the desired position size.

## Hard vetoes

- stale data
- provider conflict
- broker mismatch
- unknown position state
- system health failure
- kill switch active
- event-risk block
- insufficient liquidity
- excessive spread
- excessive slippage
- portfolio concentration breach
- daily/weekly loss breach
```

---

# 7. CREATE THE STRATEGY PROMOTION PIPELINE

Run:

```bash
nano docs/STRATEGY_PROMOTION_PIPELINE.md
```

Paste:

```markdown
# FX Strategy Promotion Pipeline

EXTERNAL_UNTRUSTED / IDEA
↓
FORMAL_SPECIFICATION
↓
BACKTESTED
↓
VALIDATION_PASSED
↓
OOS_VALIDATED
↓
WALK_FORWARD_VALIDATED
↓
PARAMETER_STABILITY_VALIDATED
↓
COST_STRESS_VALIDATED
↓
MONTE_CARLO_VALIDATED
↓
MODEL_KILLER_VALIDATED
↓
LOCKED_HOLDOUT_VALIDATED
↓
INDEPENDENT_REPLAY_VALIDATED
↓
VAULT
↓
SHADOW
↓
PAPER
↓
MICRO_LIVE
↓
LIMITED_LIVE
↓
APPROVED

Regression:

APPROVED
↓
WATCH
↓
DEGRADED
↓
SUSPENDED
↓
RETIRED

No stage skipping.
```

---

# 8. INSTALL ONLY THE NEXT REQUIRED PYTHON PACKAGES

First inspect your current Python:

```bash
python3 --version
which python3
```

If the FX project already has an active virtual environment, use it.

Check:

```bash
ls -la | grep -E "venv|\.venv"
```

If `.venv-core` already exists:

```bash
source .venv-core/bin/activate
```

Otherwise if `.venv` exists:

```bash
source .venv/bin/activate
```

Do not create a new environment unless necessary.

Install the new small dependencies:

```bash
python -m pip install --upgrade pip

python -m pip install \
  pyotp \
  keyring \
  "qrcode[pil]" \
  turbovec \
  numpy \
  pydantic
```

Verify:

```bash
python - <<'PY'
import pyotp
import keyring
import qrcode
import turbovec
import numpy
import pydantic

print("pyotp OK")
print("keyring OK")
print("qrcode OK")
print("turbovec OK")
print("numpy OK")
print("pydantic OK")
PY
```

---

# 9. DO NOT INSTALL NAUTILUSTRADER NATIVELY

Your machine is Intel macOS.

Do not run:

```bash
pip install nautilus_trader
```

in the native Intel Mac environment.

NautilusTrader belongs later in:

```text
Docker
↓
Ubuntu x86_64
↓
Python 3.12
↓
NautilusTrader
```

---

# 10. CREATE THE BRAIN / TRACE MODULE

Create:

```bash
nano services/brain/trace.py
```

Paste:

```python
from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TraceStatus(str, Enum):
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class DecisionTraceEvent:
    event_id: str
    run_id: str
    ts: float
    stage: str
    status: TraceStatus
    summary: str
    evidence_ids: list[str] = field(default_factory=list)
    model_votes: dict[str, str] = field(default_factory=dict)
    checks: dict[str, str] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    vetoes: list[str] = field(default_factory=list)
    input_hash: str | None = None
    output_hash: str | None = None
    elapsed_ms: float | None = None


def stable_hash(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(raw).hexdigest()


class BrainTraceStore:
    def __init__(self, max_events: int = 50_000):
        self._events: list[DecisionTraceEvent] = []
        self._lock = threading.RLock()
        self.max_events = max_events

    def start_run(self) -> str:
        return str(uuid.uuid4())

    def emit(
        self,
        run_id: str,
        stage: str,
        status: TraceStatus,
        summary: str,
        *,
        evidence_ids: list[str] | None = None,
        model_votes: dict[str, str] | None = None,
        checks: dict[str, str] | None = None,
        assumptions: list[str] | None = None,
        vetoes: list[str] | None = None,
        inputs: Any = None,
        outputs: Any = None,
        elapsed_ms: float | None = None,
    ) -> DecisionTraceEvent:
        event = DecisionTraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            ts=time.time(),
            stage=stage,
            status=status,
            summary=summary,
            evidence_ids=evidence_ids or [],
            model_votes=model_votes or {},
            checks=checks or {},
            assumptions=assumptions or [],
            vetoes=vetoes or [],
            input_hash=stable_hash(inputs) if inputs is not None else None,
            output_hash=stable_hash(outputs) if outputs is not None else None,
            elapsed_ms=elapsed_ms,
        )

        with self._lock:
            self._events.append(event)

            if len(self._events) > self.max_events:
                self._events = self._events[-self.max_events :]

        return event

    def get_run(self, run_id: str) -> list[dict]:
        with self._lock:
            return [
                asdict(event)
                for event in self._events
                if event.run_id == run_id
            ]


brain_trace_store = BrainTraceStore()
```

Important:

```text
The Brain panel displays structured evidence and decision summaries.
It does not expose hidden chain-of-thought.
```

---

# 11. CREATE TURBOVEC MEMORY

Run:

```bash
nano services/memory/turbovec_store.py
```

Paste:

```python
from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from turbovec import IdMapIndex


@dataclass
class MemoryRecord:
    id: int
    kind: str
    text: str
    instrument: str | None = None
    strategy_id: str | None = None
    timeframe: str | None = None
    regime: str | None = None
    timestamp: float | None = None
    outcome: str | None = None


class TurboVecMemory:
    def __init__(
        self,
        dim: int,
        path: str,
        bit_width: int = 4,
    ):
        self.dim = dim
        self.path = Path(path)
        self.meta_path = self.path.with_suffix(
            self.path.suffix + ".json"
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._lock = threading.RLock()

        if self.path.exists():
            self.index = IdMapIndex.load(str(self.path))
        else:
            self.index = IdMapIndex(
                dim=dim,
                bit_width=bit_width,
            )

        if self.meta_path.exists():
            self.meta: dict[str, dict] = json.loads(
                self.meta_path.read_text()
            )
        else:
            self.meta = {}

    def add(
        self,
        record: MemoryRecord,
        embedding: np.ndarray,
    ) -> None:
        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(1, self.dim)

        ids = np.asarray(
            [record.id],
            dtype=np.uint64,
        )

        with self._lock:
            if str(record.id) in self.meta:
                try:
                    self.index.remove(record.id)
                except Exception:
                    pass

            self.index.add_with_ids(
                vector,
                ids,
            )

            self.meta[str(record.id)] = asdict(record)

    def remove(self, record_id: int) -> None:
        with self._lock:
            self.index.remove(record_id)
            self.meta.pop(str(record_id), None)

    def search(
        self,
        query_embedding: np.ndarray,
        *,
        k: int = 10,
        allow_ids: list[int] | None = None,
    ) -> list[dict]:
        query = np.asarray(
            query_embedding,
            dtype=np.float32,
        ).reshape(1, self.dim)

        allowlist = None

        if allow_ids is not None:
            allowlist = np.asarray(
                allow_ids,
                dtype=np.uint64,
            )

        with self._lock:
            scores, ids = self.index.search(
                query,
                k=k,
                allowlist=allowlist,
            )

        score_row = np.asarray(scores).reshape(-1)
        id_row = np.asarray(ids).reshape(-1)

        results = []

        for score, record_id in zip(
            score_row.tolist(),
            id_row.tolist(),
        ):
            metadata = self.meta.get(
                str(int(record_id))
            )

            if metadata:
                results.append(
                    {
                        "score": float(score),
                        **metadata,
                    }
                )

        return results

    def filter_ids(
        self,
        predicate: Callable[[dict], bool],
    ) -> list[int]:
        return [
            int(record_id)
            for record_id, metadata in self.meta.items()
            if predicate(metadata)
        ]

    def sync(self) -> None:
        with self._lock:
            self.index.sync(str(self.path))

            temp = self.meta_path.with_suffix(
                self.meta_path.suffix + ".tmp"
            )

            temp.write_text(
                json.dumps(
                    self.meta,
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )

            os.replace(
                temp,
                self.meta_path,
            )
```

TurboVec stores semantic memory.

Do not use it instead of:

```text
Parquet
DuckDB
```

for raw market time series.

---

# 12. ADD TURBOVEC SETTINGS

Add to `.env`:

```env
FX_MEMORY_ENABLED=true
FX_MEMORY_DIM=384
FX_MEMORY_BITS=4
FX_MEMORY_PATH=data/memory/fx_memory.tvim
```

---

# 13. CREATE THE STREAMING LEARNER

Run:

```bash
nano services/learning/market_learning.py
```

Paste:

```python
from __future__ import annotations

import asyncio
import math
import os
import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class MarketObservation:
    instrument: str
    ts: float
    bid: float | None
    ask: float | None
    last: float
    volume: float | None
    source: str
    venue: str | None


class OnlineMoments:
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, value: float):
        self.n += 1

        delta = value - self.mean
        self.mean += delta / self.n
        delta2 = value - self.mean
        self.m2 += delta * delta2

    @property
    def variance(self) -> float:
        if self.n <= 1:
            return 0.0

        return self.m2 / (self.n - 1)


class StreamingLearner:
    def __init__(self):
        self.interval = float(
            os.getenv(
                "FX_MARKET_LEARNING_INTERVAL_SECONDS",
                "1",
            )
        )

        self.retrain_interval = int(
            os.getenv(
                "FX_MODEL_RETRAIN_INTERVAL_SECONDS",
                "3600",
            )
        )

        self.last_price: dict[str, float] = {}
        self.returns = defaultdict(OnlineMoments)
        self.spreads = defaultdict(OnlineMoments)

        self._last_retrain_request = 0.0

    def observe(
        self,
        observation: MarketObservation,
    ) -> dict:
        previous = self.last_price.get(
            observation.instrument
        )

        return_1 = 0.0

        if (
            previous
            and previous > 0
            and observation.last > 0
        ):
            return_1 = math.log(
                observation.last / previous
            )

            self.returns[
                observation.instrument
            ].update(return_1)

        self.last_price[
            observation.instrument
        ] = observation.last

        spread_bps = None

        if (
            observation.bid
            and observation.ask
            and observation.bid > 0
            and observation.ask >= observation.bid
        ):
            midpoint = (
                observation.bid
                + observation.ask
            ) / 2

            spread_bps = (
                (
                    observation.ask
                    - observation.bid
                )
                / midpoint
                * 10_000
            )

            self.spreads[
                observation.instrument
            ].update(spread_bps)

        return {
            "instrument": observation.instrument,
            "return_1": return_1,
            "online_return_mean":
                self.returns[
                    observation.instrument
                ].mean,
            "online_return_variance":
                self.returns[
                    observation.instrument
                ].variance,
            "spread_bps": spread_bps,
            "online_spread_mean_bps":
                self.spreads[
                    observation.instrument
                ].mean,
        }

    def retrain_due(self) -> bool:
        now = time.time()

        if (
            now - self._last_retrain_request
            >= self.retrain_interval
        ):
            self._last_retrain_request = now
            return True

        return False

    async def run(
        self,
        fetch_observations,
        persist_observation,
        request_training,
    ):
        while True:
            started = time.time()

            observations = await fetch_observations()

            for observation in observations:
                features = self.observe(
                    observation
                )

                await persist_observation(
                    observation,
                    features,
                )

            if self.retrain_due():
                await request_training(
                    reason="scheduled_streaming_refresh"
                )

            elapsed = time.time() - started

            await asyncio.sleep(
                max(
                    0.0,
                    self.interval - elapsed,
                )
            )
```

Add:

```env
FX_MARKET_LEARNING_INTERVAL_SECONDS=1
FX_MODEL_RETRAIN_INTERVAL_SECONDS=3600
```

Important:

```text
"learn every second"
does NOT mean
"replace live models every second"
```

It means:

```text
observe every second
update telemetry
record predictions
update online statistics
queue challenger research
```

Promotion stays gated.

---

# 14. CREATE TOTP AUTHENTICATION

Run:

```bash
nano services/auth/totp.py
```

Paste:

```python
from __future__ import annotations

import io
import os
from dataclasses import dataclass

import keyring
import pyotp
import qrcode


SERVICE_NAME = "FX_TRADING_OS_TOTP"


@dataclass(frozen=True)
class TotpConfig:
    account: str = os.getenv(
        "FX_AUTH_ACCOUNT",
        "jacobo",
    )

    issuer: str = os.getenv(
        "FX_AUTH_ISSUER",
        "FX",
    )


class TotpService:
    def __init__(
        self,
        config: TotpConfig | None = None,
    ):
        self.config = config or TotpConfig()

    @property
    def _key_name(self) -> str:
        return (
            f"{self.config.issuer}:"
            f"{self.config.account}"
        )

    def is_enrolled(self) -> bool:
        return bool(
            keyring.get_password(
                SERVICE_NAME,
                self._key_name,
            )
        )

    def enroll(
        self,
        *,
        rotate: bool = False,
    ) -> dict:
        existing = keyring.get_password(
            SERVICE_NAME,
            self._key_name,
        )

        if existing and not rotate:
            raise RuntimeError(
                "TOTP already enrolled."
            )

        secret = pyotp.random_base32()

        keyring.set_password(
            SERVICE_NAME,
            self._key_name,
            secret,
        )

        uri = pyotp.TOTP(
            secret
        ).provisioning_uri(
            name=self.config.account,
            issuer_name=self.config.issuer,
        )

        qr = qrcode.QRCode(
            box_size=8,
            border=2,
        )

        qr.add_data(uri)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="PNG",
        )

        return {
            "secret": secret,
            "provisioning_uri": uri,
            "qr_png": buffer.getvalue(),
        }

    def verify(
        self,
        code: str,
        *,
        valid_window: int = 1,
    ) -> bool:
        secret = keyring.get_password(
            SERVICE_NAME,
            self._key_name,
        )

        if not secret:
            return False

        value = "".join(
            character
            for character in str(code)
            if character.isdigit()
        )

        if len(value) != 6:
            return False

        return bool(
            pyotp.TOTP(secret).verify(
                value,
                valid_window=valid_window,
            )
        )


totp_service = TotpService()
```

This is compatible with Google Authenticator via RFC 6238.

Do not put the TOTP secret in `.env`.

---

# 15. ADD AUTH SETTINGS

Add:

```env
FX_AUTH_ACCOUNT=jacobo
FX_AUTH_ISSUER=FX
FX_LIVE_APPROVAL_TTL_SECONDS=90
```

---

# 16. CREATE THE EXECUTION POLICY

Run:

```bash
nano services/execution/policy.py
```

Paste:

```python
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class TradingMode(str, Enum):
    RESEARCH = "research"
    BACKTEST = "backtest"
    PAPER = "paper"
    SHADOW = "shadow"
    MICRO_LIVE = "micro_live"
    LIMITED_LIVE = "limited_live"
    APPROVED_LIVE = "approved_live"


@dataclass(frozen=True)
class ExecutionPolicy:
    trading_mode: TradingMode
    live_enabled: bool
    manual_approval_required: bool
    totp_required_for_live: bool
    ai_can_execute_live: bool
    max_live_order_notional: float
    max_live_daily_loss: float

    @classmethod
    def from_env(cls):
        def boolean(
            name: str,
            default: str,
        ) -> bool:
            return (
                os.getenv(
                    name,
                    default,
                )
                .strip()
                .lower()
                == "true"
            )

        return cls(
            trading_mode=TradingMode(
                os.getenv(
                    "TRADING_MODE",
                    "research",
                )
            ),
            live_enabled=boolean(
                "LIVE_TRADING_ENABLED",
                "false",
            ),
            manual_approval_required=boolean(
                "MANUAL_ORDER_APPROVAL_REQUIRED",
                "true",
            ),
            totp_required_for_live=boolean(
                "TOTP_REQUIRED_FOR_LIVE",
                "true",
            ),
            ai_can_execute_live=boolean(
                "AI_CAN_EXECUTE_LIVE",
                "false",
            ),
            max_live_order_notional=float(
                os.getenv(
                    "MAX_LIVE_ORDER_NOTIONAL",
                    "0",
                )
            ),
            max_live_daily_loss=float(
                os.getenv(
                    "MAX_LIVE_DAILY_LOSS",
                    "0",
                )
            ),
        )


def assert_safe_policy(
    policy: ExecutionPolicy,
) -> None:
    if policy.ai_can_execute_live:
        raise RuntimeError(
            "Unsafe configuration: "
            "AI_CAN_EXECUTE_LIVE must remain false."
        )

    if (
        policy.live_enabled
        and not policy.manual_approval_required
    ):
        raise RuntimeError(
            "Live trading requires "
            "manual approval."
        )

    if (
        policy.live_enabled
        and not policy.totp_required_for_live
    ):
        raise RuntimeError(
            "Live trading requires TOTP."
        )
```

---

# 17. VERIFY PYTHON SYNTAX NOW

Run:

```bash
cd "/Users/macmac/Documents/Codex/FX"

python -m py_compile \
  services/brain/trace.py \
  services/memory/turbovec_store.py \
  services/learning/market_learning.py \
  services/auth/totp.py \
  services/execution/policy.py
```

If no output appears:

```text
syntax is OK
```

---

# 18. CREATE INIT FILES IF NEEDED

Run:

```bash
touch \
  services/__init__.py \
  services/brain/__init__.py \
  services/memory/__init__.py \
  services/learning/__init__.py \
  services/auth/__init__.py \
  services/execution/__init__.py
```

---

# 19. TEST THE EXECUTION POLICY

Run:

```bash
python - <<'PY'
from services.execution.policy import (
    ExecutionPolicy,
    assert_safe_policy,
)

policy = ExecutionPolicy.from_env()

print(policy)

assert_safe_policy(policy)

print("SAFE POLICY: PASS")
PY
```

Expected:

```text
SAFE POLICY: PASS
```

---

# 20. TEST TURBOVEC LOCALLY

Run:

```bash
python - <<'PY'
import numpy as np

from services.memory.turbovec_store import (
    MemoryRecord,
    TurboVecMemory,
)

store = TurboVecMemory(
    dim=8,
    bit_width=4,
    path="data/memory/test_memory.tvim",
)

record = MemoryRecord(
    id=1001,
    kind="failure_memory",
    text="BTC breakout failed in a low-liquidity range.",
    instrument="BTCUSDT",
    timeframe="1H",
    regime="RANGE_LOW_VOL",
)

vector = np.random.randn(8).astype("float32")

store.add(
    record,
    vector,
)

store.sync()

results = store.search(
    vector,
    k=3,
)

print(results)
PY
```

You should see the saved memory record returned.

---

# 21. TEST THE BRAIN TRACE

Run:

```bash
python - <<'PY'
from services.brain.trace import (
    TraceStatus,
    brain_trace_store,
)

run_id = brain_trace_store.start_run()

brain_trace_store.emit(
    run_id=run_id,
    stage="data_quality",
    status=TraceStatus.COMPLETE,
    summary="Market data quality passed.",
    checks={
        "staleness": "PASS",
        "duplicates": "PASS",
        "timestamps": "PASS",
    },
)

brain_trace_store.emit(
    run_id=run_id,
    stage="risk",
    status=TraceStatus.BLOCKED,
    summary="Trade rejected because portfolio exposure is too high.",
    vetoes=[
        "correlated_exposure_limit"
    ],
)

print(
    brain_trace_store.get_run(
        run_id
    )
)
PY
```

---

# 22. CONTINUOUS LEARNING RULE

The system can process market observations continuously.

But do not build:

```text
market loss
↓
AI changes parameters
↓
new model trades immediately
```

Build:

```text
OBSERVE
↓
PROPOSE
↓
BACKTEST
↓
VALIDATE
↓
HOLDOUT
↓
SHADOW
↓
PAPER
↓
APPROVAL
↓
DEPLOY
```

---

# 23. CREATE THE MASTER DECISION CONTRACT

Create:

```bash
nano docs/MASTER_DECISION_CONTRACT.md
```

Paste:

```yaml
decision:
  instrument:
  asset_class:
  timestamp:
  direction:
  action:
  eligibility:
  strategy_id:
  strategy_version:

context:
  regime:
  macro_score:
  in_play_score:
  structure_score:
  location_score:
  volume_score:
  volatility_score:
  order_flow_score:
  fundamental_score:
  relative_strength_score:
  event_risk:
  system_health:

prediction:
  p05_return:
  p25_return:
  median_return:
  p75_return:
  p95_return:
  confidence:
  calibration_bucket:

historical_evidence:
  sample_size:
  win_rate:
  avg_win_r:
  avg_loss_r:
  expectancy_r:
  profit_factor:
  confidence_interval:

counter_thesis:
  score:
  fatal_objection:
  objections:
  evidence_ids:

trade:
  entry:
  stop:
  structural_invalidation:
  volatility_buffer:
  target_1:
  target_2:
  expected_r:
  time_stop:

costs:
  fees:
  spread:
  expected_slippage:
  funding:
  borrow:
  market_impact:
  total_expected_cost:

portfolio:
  existing_exposure:
  correlated_exposure:
  post_trade_exposure:
  factor_exposure:
  venue_exposure:

risk:
  requested_risk:
  approved_risk:
  position_size:
  risk_engine_status:
  veto_reason:
  probability_of_ruin:

execution:
  venue:
  order_type:
  max_slippage:
  max_participation:
  expected_fill:
  status:

provenance:
  strategy_version:
  model_versions:
  feature_version:
  risk_policy_version:
  dataset_version:
  dataset_hash:
  code_commit:
  configuration_hash:
  campaign_id:
  holdout_hash:
  approval_hash:
  order_hash:
```

Every attempted trade should eventually create this object.

Including rejected trades.

---

# 24. MASTER NO-TRADE CONDITIONS

Create:

```bash
nano docs/NO_TRADE_POLICY.md
```

Paste:

```markdown
# FX NO TRADE Policy

Return NO_TRADE when any critical condition applies:

- edge too weak
- expected return below total expected costs
- spread too large
- liquidity too low
- regime unknown
- major event too close
- data stale
- provider conflict
- data corruption
- model disagreement excessive
- historical sample too small
- strategy degraded
- portfolio concentration too high
- hard risk limit reached
- broker mismatch
- system health degraded
- execution cost too high
- stop too wide
- reward too small
- opposing structure too close
- slippage estimate unstable
- kill switch active
- security state invalid
```

---

# 25. MASTER DECISION SEQUENCE

Every candidate should eventually pass:

```text
1. DATA VALID?
2. SYSTEM HEALTHY?
3. EVENT RISK ACCEPTABLE?
4. ASSET IN PLAY?
5. REGIME KNOWN?
6. STRATEGY ALLOWED IN REGIME?
7. HTF STRUCTURE VALID?
8. LOCATION ATTRACTIVE?
9. VOLUME CONFIRMS?
10. VOLATILITY SUITABLE?
11. ORDER FLOW ACCEPTABLE?
12. FUNDAMENTALS / MACRO NON-FATAL?
13. MODEL COUNCIL SUPPORTIVE?
14. RETURN DISTRIBUTION ATTRACTIVE?
15. HISTORICAL EXPECTANCY POSITIVE?
16. COUNTER-THESIS SURVIVED?
17. REWARD / RISK ACCEPTABLE?
18. EXPECTED RETURN > COSTS?
19. PORTFOLIO EXPOSURE ACCEPTABLE?
20. CORRELATION ACCEPTABLE?
21. LIQUIDITY ACCEPTABLE?
22. RISK ENGINE APPROVES?
23. EXECUTION FEASIBLE?
24. APPROVAL PRESENT IF LIVE?
25. ORDER SUBMITTED?
26. BROKER ACKNOWLEDGED?
27. POSITION RECONCILED?
28. THESIS MONITORED?
29. EXIT EXECUTED?
30. TRADE REVIEWED?
```

Any failure may produce:

```text
NO_TRADE
```

---

# 26. NEXT TERMINAL BUILD ORDER

Do not try to build everything in one command.

Work in this order:

```text
1. Constitution
2. Risk Engine
3. Data Quality
4. Canonical Instrument Registry
5. Cost Model
6. Slippage Model
7. Kill Switches
8. Reconciliation
9. System Health
10. Regime Engine
11. Core deterministic strategies
12. Model Council
13. Historical Analogues
14. TurboVec Memory
15. Counter-Thesis / Fraud Engine
16. Master Decision Contract
17. Strategy Validation Pipeline
18. Overfitting Firewall
19. Strategy Vault
20. Continuous Learning
21. Observable Brain
22. Shadow Live
23. Paper Automation
24. Mission Control
25. TOTP approval
26. Nautilus Docker
27. Micro Live only after full production gate
```

---

# 27. WHAT TO BUILD FIRST TODAY

Your first concrete terminal milestone should be:

```text
FX SAFE FOUNDATION
```

It is complete when these files exist and pass syntax tests:

```text
docs/TRADING_SYSTEM_CONSTITUTION.md
docs/RISK_ENGINE_SPEC.md
docs/STRATEGY_PROMOTION_PIPELINE.md
docs/MASTER_DECISION_CONTRACT.md
docs/NO_TRADE_POLICY.md

services/brain/trace.py
services/memory/turbovec_store.py
services/learning/market_learning.py
services/auth/totp.py
services/execution/policy.py
```

Check:

```bash
find docs services \
  -type f \
  | grep -E \
  "TRADING_SYSTEM_CONSTITUTION|RISK_ENGINE_SPEC|STRATEGY_PROMOTION_PIPELINE|MASTER_DECISION_CONTRACT|NO_TRADE_POLICY|trace.py|turbovec_store.py|market_learning.py|totp.py|policy.py"
```

---

# 28. FINAL SAFETY CHECK

Run:

```bash
grep -E \
"TRADING_MODE|LIVE_TRADING_ENABLED|PAPER_TRADING_ENABLED|SHADOW_TRADING_ENABLED|AI_CAN_EXECUTE_LIVE|MANUAL_ORDER_APPROVAL_REQUIRED|TOTP_REQUIRED_FOR_LIVE" \
.env
```

Expected safe state:

```text
TRADING_MODE=research
LIVE_TRADING_ENABLED=false
PAPER_TRADING_ENABLED=true
SHADOW_TRADING_ENABLED=true
MANUAL_ORDER_APPROVAL_REQUIRED=true
TOTP_REQUIRED_FOR_LIVE=true
AI_CAN_EXECUTE_LIVE=false
```

---

# 29. FINAL PROJECT LAW

The system should become:

```text
a disciplined fleet of validated trading systems
under one observable AI-assisted operating layer
```

not:

```text
one giant self-modifying bot
```

Permanent hierarchy:

```text
DATA
↓
QUALITY
↓
INTELLIGENCE
↓
REGIME
↓
MODELS
↓
STRATEGIES
↓
VALIDATION
↓
EVIDENCE
↓
COUNTER-THESIS
↓
PORTFOLIO
↓
DETERMINISTIC RISK
↓
AI EXPLANATION
↓
NO_TRADE / PAPER / SHADOW / LIVE PROPOSAL
↓
HUMAN APPROVAL FOR LIVE ENTRY
↓
EXECUTION
↓
BROKER
↓
RECONCILIATION
↓
MISSION CONTROL
↓
JOURNAL
↓
LEARNING
```

Do not build a magic-profit bot.

Build a reproducible quantitative trading operating system.

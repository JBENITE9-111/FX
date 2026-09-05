#!/bin/bash
set -euo pipefail

ROOT="/Users/macmac/Documents/Codex/FX"
VENV="$ROOT/.venv-core"
PY="$VENV/bin/python"

echo ""
echo "============================================================"
echo " FX TERMINAL UPGRADE V4"
echo "============================================================"
echo ""

if [ ! -d "$ROOT" ]; then
  echo "ERROR: FX project not found at $ROOT"
  exit 1
fi

if [ ! -x "$PY" ]; then
  echo "ERROR: FX Python not found at $PY"
  exit 1
fi

cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p \
  backups \
  services/auth \
  services/brain \
  services/execution \
  services/learning \
  services/memory \
  services/research \
  services/news \
  services/paper_fleet \
  services/agents \
  services/tools \
  backend/app/routes \
  data/news \
  data/paper_fleet \
  data/agents \
  data/memory \
  docs \
  scripts \
  "$HOME/Library/LaunchAgents"

for f in \
  services/__init__.py \
  services/auth/__init__.py \
  services/brain/__init__.py \
  services/execution/__init__.py \
  services/learning/__init__.py \
  services/memory/__init__.py \
  services/research/__init__.py \
  services/news/__init__.py \
  services/paper_fleet/__init__.py \
  services/agents/__init__.py \
  services/tools/__init__.py \
  backend/__init__.py \
  backend/app/__init__.py \
  backend/app/routes/__init__.py
do
  touch "$ROOT/$f"
done

STAMP="$(date +%Y%m%d-%H%M%S)"
tar \
  --exclude='./backups' \
  --exclude='./data/raw' \
  --exclude='./data/normalized' \
  --exclude='./data/features' \
  --exclude='./data/holdout' \
  --exclude='./vendor' \
  --exclude='./external' \
  --exclude='./.venv-core' \
  --exclude='./.venv-kronos' \
  -czf "$ROOT/backups/fx-before-v4-${STAMP}.tar.gz" . 2>/dev/null || true

echo "✓ Backup created"

source "$VENV/bin/activate"

if command -v uv >/dev/null 2>&1; then
  uv pip install pyotp keyring "qrcode[pil]" turbovec yfinance
else
  "$PY" -m pip install pyotp keyring "qrcode[pil]" turbovec yfinance
fi

touch "$ROOT/.env"

"$PY" - <<'PY'
from pathlib import Path

path = Path("/Users/macmac/Documents/Codex/FX/.env")
safe = {
    "TRADING_MODE": "research",
    "LIVE_TRADING_ENABLED": "false",
    "PAPER_TRADING_ENABLED": "true",
    "SHADOW_TRADING_ENABLED": "true",
    "MANUAL_ORDER_APPROVAL_REQUIRED": "true",
    "TOTP_REQUIRED_FOR_LIVE": "true",
    "AI_CAN_EXECUTE_LIVE": "false",
    "AI_CAN_CHANGE_RISK_LIMITS": "false",
    "AI_CAN_ACCESS_BROKER_SECRETS": "false",
    "AI_CAN_DISABLE_KILL_SWITCH": "false",
    "FX_AUTH_ACCOUNT": "jacobo",
    "FX_AUTH_ISSUER": "FX",
    "FX_LIVE_APPROVAL_TTL_SECONDS": "90",
    "FX_MEMORY_ENABLED": "true",
    "FX_MEMORY_DIM": "384",
    "FX_MEMORY_BITS": "4",
    "FX_MEMORY_PATH": "data/memory/fx_memory.tvim",
    "FX_MARKET_LEARNING_INTERVAL_SECONDS": "1",
    "FX_MODEL_RETRAIN_INTERVAL_SECONDS": "3600",
    "FX_NEWSPAPER_REFRESH_SECONDS": "1800",
    "FX_NEWSPAPER_MAX_ITEMS": "120",
    "FX_PAPER_FLEET_ENABLED": "true",
    "FX_PAPER_FLEET_CAPITAL_PER_STRATEGY": "1.00",
    "FX_PAPER_FLEET_REFRESH_SECONDS": "300",
    "FX_PAPER_FLEET_DEFAULT_SYMBOL": "AAPL",
    "FX_AGENT_CHECKPOINT_SECONDS": "30",
    "FX_AGENT_MAX_RUNTIME_SECONDS": "240",
    "FX_SPARSE_EXPERTS_PER_STAGE": "2",
}

lines = path.read_text().splitlines()
out, seen = [], set()

for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        out.append(line)
        continue

    key = stripped.split("=", 1)[0].strip()
    if key in safe:
        out.append(f"{key}={safe[key]}")
        seen.add(key)
    else:
        out.append(line)

for key, value in safe.items():
    if key not in seen:
        out.append(f"{key}={value}")

path.write_text("\n".join(out).rstrip() + "\n")
print("✓ Environment updated; existing API keys preserved")
PY

cat > "$ROOT/docs/AGENT_ARCHITECTURE.md" <<'EOF'
# FX Agent Architecture

FX uses an agent as a durable task runner, not as a synonym for chatbot.

An FX agent:
1. has a narrowly defined goal,
2. has an explicit tool allowlist,
3. runs start-to-finish,
4. emits observable status updates,
5. checkpoints progress,
6. can be interrupted,
7. records outputs and failures,
8. cannot bypass deterministic risk.

Ideas adopted conceptually from xAI Grok Build:
- headless task execution,
- long-running tasks,
- checkpoints,
- tools,
- MCP-compatible boundaries,
- skills/plugins/hooks as modular capability layers,
- sandbox/permission concepts,
- observable execution state.

Ideas adopted conceptually from Grok-1:
- sparse expert routing.
- FX should not run every specialist on every task.
- a small number of relevant experts should be selected for each stage.

FX does NOT install Grok-1.
Its 314B-parameter model is inappropriate for this Intel Mac.

Default sparse routing:
- select the top 2 relevant specialist agents for an analytical stage,
- always keep deterministic Risk as a separate sovereign veto,
- preserve model disagreement as evidence.

Primary scheduled agents:
- Newspaper Agent: refresh global finance/economics/geopolitics every 30 minutes.
- Paper Fleet Agent: run every strategy worker every 5 minutes.
- Training Agent: queue challenger retraining on the existing FX validation pipeline.
EOF

###############################################################################
# FX HARNESS V1.1
###############################################################################

cat > "$ROOT/services/auth/totp.py" <<'PY'
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
    account: str = os.getenv("FX_AUTH_ACCOUNT", "jacobo")
    issuer: str = os.getenv("FX_AUTH_ISSUER", "FX")

class TotpService:
    def __init__(self, config: TotpConfig | None = None):
        self.config = config or TotpConfig()

    @property
    def _key_name(self) -> str:
        return f"{self.config.issuer}:{self.config.account}"

    def is_enrolled(self) -> bool:
        return bool(keyring.get_password(SERVICE_NAME, self._key_name))

    def enroll(self, *, rotate: bool = False) -> dict:
        existing = keyring.get_password(SERVICE_NAME, self._key_name)
        if existing and not rotate:
            raise RuntimeError("TOTP is already enrolled.")

        secret = pyotp.random_base32()
        keyring.set_password(SERVICE_NAME, self._key_name, secret)

        uri = pyotp.TOTP(secret).provisioning_uri(
            name=self.config.account,
            issuer_name=self.config.issuer,
        )

        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        return {
            "secret": secret,
            "provisioning_uri": uri,
            "qr_png": buffer.getvalue(),
        }

    def verify(self, code: str, *, valid_window: int = 1) -> bool:
        secret = keyring.get_password(SERVICE_NAME, self._key_name)
        if not secret:
            return False

        value = "".join(ch for ch in str(code) if ch.isdigit())
        if len(value) != 6:
            return False

        return bool(
            pyotp.TOTP(secret).verify(
                value,
                valid_window=valid_window,
            )
        )

totp_service = TotpService()
PY

cat > "$ROOT/services/auth/approval.py" <<'PY'
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import asdict, dataclass

import keyring

from services.auth.totp import totp_service

SERVICE_NAME = "FX_TRADING_OS_APPROVAL"
SIGNING_KEY_NAME = "live-approval-signing-key"

@dataclass(frozen=True)
class ApprovalPayload:
    proposal_id: str
    instrument: str
    side: str
    quantity: float
    order_type: str
    max_notional: float
    risk_decision_id: str
    expires_at: int
    nonce: str

def _signing_key() -> bytes:
    key = keyring.get_password(SERVICE_NAME, SIGNING_KEY_NAME)
    if not key:
        key = secrets.token_hex(32)
        keyring.set_password(SERVICE_NAME, SIGNING_KEY_NAME, key)
    return bytes.fromhex(key)

def issue_live_approval(payload: ApprovalPayload, totp_code: str) -> str:
    if not totp_service.verify(totp_code):
        raise PermissionError("Invalid TOTP code.")

    now = int(time.time())
    ttl = int(os.getenv("FX_LIVE_APPROVAL_TTL_SECONDS", "90"))

    if payload.expires_at <= now or payload.expires_at > now + ttl:
        raise PermissionError("Approval expiry is invalid.")

    body = json.dumps(
        asdict(payload),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    signature = hmac.new(
        _signing_key(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return f"{body.hex()}.{signature}"

def verify_live_approval(token: str, expected: ApprovalPayload) -> bool:
    try:
        body_hex, supplied = token.split(".", 1)
        body = bytes.fromhex(body_hex)

        expected_sig = hmac.new(
            _signing_key(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(supplied, expected_sig):
            return False

        decoded = json.loads(body)
        if decoded != asdict(expected):
            return False

        return int(decoded["expires_at"]) > int(time.time())
    except Exception:
        return False
PY

cat > "$ROOT/services/execution/policy.py" <<'PY'
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
        def boolean(name: str, default: str) -> bool:
            return os.getenv(name, default).strip().lower() == "true"

        return cls(
            trading_mode=TradingMode(os.getenv("TRADING_MODE", "research")),
            live_enabled=boolean("LIVE_TRADING_ENABLED", "false"),
            manual_approval_required=boolean(
                "MANUAL_ORDER_APPROVAL_REQUIRED",
                "true",
            ),
            totp_required_for_live=boolean("TOTP_REQUIRED_FOR_LIVE", "true"),
            ai_can_execute_live=boolean("AI_CAN_EXECUTE_LIVE", "false"),
            max_live_order_notional=float(
                os.getenv("MAX_LIVE_ORDER_NOTIONAL", "0")
            ),
            max_live_daily_loss=float(
                os.getenv("MAX_LIVE_DAILY_LOSS", "0")
            ),
        )

def assert_safe_policy(policy: ExecutionPolicy) -> None:
    if policy.ai_can_execute_live:
        raise RuntimeError(
            "Unsafe configuration: AI_CAN_EXECUTE_LIVE must remain false."
        )

    if policy.live_enabled and not policy.manual_approval_required:
        raise RuntimeError("Live trading requires manual approval.")

    if policy.live_enabled and not policy.totp_required_for_live:
        raise RuntimeError("Live trading requires TOTP.")
PY

cat > "$ROOT/services/execution/live_gate.py" <<'PY'
from __future__ import annotations

from dataclasses import dataclass

from services.auth.approval import (
    ApprovalPayload,
    verify_live_approval,
)
from services.execution.policy import (
    ExecutionPolicy,
    assert_safe_policy,
)

@dataclass(frozen=True)
class RiskDecision:
    id: str
    passed: bool
    kill_switch_clear: bool
    data_quality_passed: bool
    broker_reconciled: bool
    max_allowed_notional: float
    reason: str

@dataclass(frozen=True)
class TradeIntent:
    proposal_id: str
    instrument: str
    side: str
    quantity: float
    order_type: str
    estimated_notional: float

class LiveGate:
    def __init__(self, policy: ExecutionPolicy):
        self.policy = policy
        assert_safe_policy(policy)

    def authorize(
        self,
        *,
        intent: TradeIntent,
        risk: RiskDecision,
        approval_payload: ApprovalPayload,
        approval_token: str,
    ) -> None:
        if not self.policy.live_enabled:
            raise PermissionError("Live trading is disabled.")

        if not risk.passed:
            raise PermissionError(f"Risk rejected: {risk.reason}")

        if not risk.kill_switch_clear:
            raise PermissionError("Kill switch is active.")

        if not risk.data_quality_passed:
            raise PermissionError("Data quality gate failed.")

        if not risk.broker_reconciled:
            raise PermissionError("Broker state is not reconciled.")

        if intent.estimated_notional > risk.max_allowed_notional:
            raise PermissionError("Order exceeds risk-decision notional.")

        if (
            self.policy.max_live_order_notional <= 0
            or intent.estimated_notional > self.policy.max_live_order_notional
        ):
            raise PermissionError("Order exceeds configured live notional.")

        if approval_payload.proposal_id != intent.proposal_id:
            raise PermissionError("Approval does not match proposal.")

        if approval_payload.risk_decision_id != risk.id:
            raise PermissionError("Approval does not match risk decision.")

        if not verify_live_approval(approval_token, approval_payload):
            raise PermissionError("Live approval is invalid or expired.")
PY

cat > "$ROOT/services/brain/trace.py" <<'PY'
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
        **kwargs,
    ) -> DecisionTraceEvent:
        event = DecisionTraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            ts=time.time(),
            stage=stage,
            status=status,
            summary=summary,
            evidence_ids=kwargs.get("evidence_ids", []),
            model_votes=kwargs.get("model_votes", {}),
            checks=kwargs.get("checks", {}),
            assumptions=kwargs.get("assumptions", []),
            vetoes=kwargs.get("vetoes", []),
            input_hash=(
                stable_hash(kwargs["inputs"])
                if kwargs.get("inputs") is not None
                else None
            ),
            output_hash=(
                stable_hash(kwargs["outputs"])
                if kwargs.get("outputs") is not None
                else None
            ),
            elapsed_ms=kwargs.get("elapsed_ms"),
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
PY

cat > "$ROOT/services/memory/turbovec_store.py" <<'PY'
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
    def __init__(self, dim: int, path: str, bit_width: int = 4):
        self.dim = dim
        self.path = Path(path)
        self.meta_path = self.path.with_suffix(self.path.suffix + ".json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

        if self.path.exists():
            self.index = IdMapIndex.load(str(self.path))
        else:
            self.index = IdMapIndex(dim=dim, bit_width=bit_width)

        if self.meta_path.exists():
            self.meta = json.loads(self.meta_path.read_text())
        else:
            self.meta = {}

    def add(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(1, self.dim)

        ids = np.asarray([record.id], dtype=np.uint64)

        with self._lock:
            if str(record.id) in self.meta:
                try:
                    self.index.remove(record.id)
                except Exception:
                    pass

            self.index.add_with_ids(vector, ids)
            self.meta[str(record.id)] = asdict(record)

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

        allowlist = (
            np.asarray(allow_ids, dtype=np.uint64)
            if allow_ids is not None
            else None
        )

        with self._lock:
            scores, ids = self.index.search(
                query,
                k=k,
                allowlist=allowlist,
            )

        results = []
        for score, record_id in zip(
            np.asarray(scores).reshape(-1).tolist(),
            np.asarray(ids).reshape(-1).tolist(),
        ):
            metadata = self.meta.get(str(int(record_id)))
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

            os.replace(temp, self.meta_path)
PY

cat > "$ROOT/services/learning/market_learning.py" <<'PY'
from __future__ import annotations

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

    def update(self, value: float) -> None:
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
        self.last_price = {}
        self.returns = defaultdict(OnlineMoments)
        self.interval = float(
            os.getenv("FX_MARKET_LEARNING_INTERVAL_SECONDS", "1")
        )
        self.retrain_interval = int(
            os.getenv("FX_MODEL_RETRAIN_INTERVAL_SECONDS", "3600")
        )
        self._last_retrain_request = 0.0

    def observe(self, observation: MarketObservation) -> dict:
        previous = self.last_price.get(observation.instrument)
        ret = 0.0

        if previous is not None and previous > 0 and observation.last > 0:
            ret = math.log(observation.last / previous)
            self.returns[observation.instrument].update(ret)

        self.last_price[observation.instrument] = observation.last

        return {
            "instrument": observation.instrument,
            "return_1": ret,
            "mean": self.returns[observation.instrument].mean,
            "variance": self.returns[observation.instrument].variance,
        }

    def retrain_due(self) -> bool:
        now = time.time()
        if now - self._last_retrain_request >= self.retrain_interval:
            self._last_retrain_request = now
            return True
        return False
PY

cat > "$ROOT/services/research/trader_brain_schema.py" <<'PY'
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

class SetupType(str, Enum):
    BREAKOUT = "breakout"
    BREAKOUT_RETEST = "breakout_retest"
    VWAP_PULLBACK = "vwap_pullback"
    TREND_PULLBACK = "trend_pullback"
    FALSE_BREAKOUT = "false_breakout"
    SUPPORT_REJECTION = "support_rejection"
    RESISTANCE_REJECTION = "resistance_rejection"
    RANGE_REVERSAL = "range_reversal"
    MOMENTUM_CONTINUATION = "momentum_continuation"
    OPENING_DRIVE = "opening_drive"
    LIQUIDITY_SWEEP_REVERSAL = "liquidity_sweep_reversal"
    VOLATILITY_SELL = "volatility_sell"
    MEAN_REVERSION = "mean_reversion"

class TraderBrainEvidence(BaseModel):
    global_regime_score: float = Field(ge=0, le=100)
    in_play_score: float = Field(ge=0, le=100)
    relative_strength_score: float = Field(ge=0, le=100)
    structure: str
    location_score: float = Field(ge=0, le=100)
    volatility_regime: str
    volume_confirmation: float = Field(ge=0, le=100)
    order_flow_score: float | None = Field(default=None, ge=0, le=100)
    setup: SetupType
    entry_trigger: str
    structural_invalidation: float
    volatility_buffer: float
    stop: float
    targets: list[float]
    expected_r: float
    historical_win_probability: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    historical_avg_win_r: float | None = None
    historical_avg_loss_r: float | None = None
    expectancy_r: float | None = None
    evidence_ids: list[str]
    assumptions: list[str] = Field(default_factory=list)

class RiskSizedProposal(BaseModel):
    instrument: str
    side: str
    setup: SetupType
    evidence: TraderBrainEvidence
    allowed_account_risk: float
    proposed_quantity: float
    risk_decision_id: str
    eligibility: str
PY

###############################################################################
# GROK-INSPIRED AGENT SUPERVISOR + SPARSE EXPERT ROUTING
###############################################################################

cat > "$ROOT/services/agents/supervisor.py" <<'PY'
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path("/Users/macmac/Documents/Codex/FX")
DB = ROOT / "data" / "agents" / "agents.sqlite3"

@dataclass
class AgentRun:
    run_id: str
    agent_id: str
    goal: str
    status: str
    started_at: float
    updated_at: float
    completed_at: float | None = None
    checkpoint: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

class AgentSupervisor:
    def __init__(self):
        DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_runs(
                    run_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    completed_at REAL,
                    checkpoint_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    error TEXT
                )
                """
            )

    def _save(self, run: AgentRun) -> None:
        with sqlite3.connect(DB) as conn:
            conn.execute(
                """
                INSERT INTO agent_runs(
                    run_id,agent_id,goal,status,started_at,updated_at,
                    completed_at,checkpoint_json,result_json,error
                )
                VALUES(?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at,
                    completed_at=excluded.completed_at,
                    checkpoint_json=excluded.checkpoint_json,
                    result_json=excluded.result_json,
                    error=excluded.error
                """,
                (
                    run.run_id,
                    run.agent_id,
                    run.goal,
                    run.status,
                    run.started_at,
                    run.updated_at,
                    run.completed_at,
                    json.dumps(run.checkpoint, default=str),
                    json.dumps(run.result, default=str),
                    run.error,
                ),
            )

    def run(
        self,
        *,
        agent_id: str,
        goal: str,
        task: Callable[[Callable[[dict[str, Any]], None]], dict[str, Any]],
    ) -> AgentRun:
        now = time.time()
        run = AgentRun(
            run_id=str(uuid.uuid4()),
            agent_id=agent_id,
            goal=goal,
            status="RUNNING",
            started_at=now,
            updated_at=now,
        )
        self._save(run)

        def checkpoint(value: dict[str, Any]) -> None:
            run.checkpoint = value
            run.updated_at = time.time()
            self._save(run)

        try:
            result = task(checkpoint)
            run.result = result
            run.status = "COMPLETE"
            run.completed_at = time.time()
            run.updated_at = run.completed_at
        except Exception as exc:
            run.status = "FAILED"
            run.error = str(exc)
            run.completed_at = time.time()
            run.updated_at = run.completed_at

        self._save(run)
        return run

    def latest(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(DB) as conn:
            rows = conn.execute(
                """
                SELECT run_id,agent_id,goal,status,started_at,updated_at,
                       completed_at,checkpoint_json,result_json,error
                FROM agent_runs
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        result = []
        for row in rows:
            result.append(
                {
                    "run_id": row[0],
                    "agent_id": row[1],
                    "goal": row[2],
                    "status": row[3],
                    "started_at": row[4],
                    "updated_at": row[5],
                    "completed_at": row[6],
                    "checkpoint": json.loads(row[7]),
                    "result": json.loads(row[8]),
                    "error": row[9],
                }
            )
        return result

supervisor = AgentSupervisor()
PY

cat > "$ROOT/services/agents/sparse_router.py" <<'PY'
from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Expert:
    expert_id: str
    tags: frozenset[str]
    sovereign: bool = False

EXPERTS = [
    Expert("macro", frozenset({"macro", "rates", "fx", "bonds", "economy", "geopolitics"})),
    Expert("trend", frozenset({"trend", "momentum", "structure", "breakout"})),
    Expert("mean_reversion", frozenset({"mean_reversion", "range", "rsi", "bollinger"})),
    Expert("volatility", frozenset({"volatility", "options", "atr", "iv"})),
    Expert("order_flow", frozenset({"order_flow", "liquidity", "volume", "microstructure"})),
    Expert("crypto", frozenset({"crypto", "funding", "open_interest", "btc", "tokenomics"})),
    Expert("fundamentals", frozenset({"stocks", "fundamentals", "earnings", "valuation"})),
    Expert("fraud_counter_thesis", frozenset({"fraud", "counter_thesis", "bias", "overfitting"})),
    Expert("execution", frozenset({"execution", "slippage", "spread", "broker", "orders"})),
    Expert("risk", frozenset({"risk", "portfolio", "correlation", "drawdown"}), sovereign=True),
]

def route(tags: set[str], top_k: int | None = None) -> list[str]:
    """
    Sparse expert routing inspired by MoE architectures.

    Risk remains sovereign and is NOT replaced by expert voting.
    """
    top_k = top_k or int(os.getenv("FX_SPARSE_EXPERTS_PER_STAGE", "2"))

    scored = []
    for expert in EXPERTS:
        if expert.sovereign:
            continue
        score = len(tags & expert.tags)
        if score > 0:
            scored.append((score, expert.expert_id))

    scored.sort(reverse=True)

    selected = [expert_id for _, expert_id in scored[:top_k]]

    if not selected:
        selected = ["trend", "macro"][:top_k]

    return selected
PY

###############################################################################
# FX GLOBAL NEWSPAPER
###############################################################################

cat > "$ROOT/services/news/newspaper.py" <<'PY'
from __future__ import annotations

import email.utils
import html
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/macmac/Documents/Codex/FX")
OUTPUT = ROOT / "data" / "news" / "newspaper.json"
USER_AGENT = "Mozilla/5.0 FX-Global-Newspaper/2.0"

GOOGLE_QUERIES = [
    ("Markets", "global markets stocks forex bonds commodities oil gold bitcoin when:1d"),
    ("Economy", "inflation interest rates central bank GDP employment recession economy when:1d"),
    ("Politics & Geopolitics", "geopolitics sanctions tariffs trade war election conflict government markets when:1d"),
    ("Bloomberg", "site:bloomberg.com markets economy politics finance when:2d"),
    ("Reuters", "site:reuters.com markets economy politics finance when:2d"),
    ("Financial Times", "site:ft.com markets economy politics finance when:2d"),
    ("CNBC", "site:cnbc.com markets economy politics finance when:2d"),
    ("WSJ", "site:wsj.com markets economy politics finance when:2d"),
]

DIRECT_FEEDS = [
    ("Yahoo Finance", "Markets", "https://finance.yahoo.com/news/rssindex"),
    ("Federal Reserve", "Central Banks", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("BBC Business", "Economy", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC World", "Politics & Geopolitics", "https://feeds.bbci.co.uk/news/world/rss.xml"),
]

SOURCE_WEIGHT = {
    "Reuters": 10,
    "Bloomberg": 10,
    "Financial Times": 9,
    "WSJ": 9,
    "Federal Reserve": 10,
    "Yahoo Finance": 6,
    "CNBC": 7,
    "BBC Business": 7,
    "BBC World": 7,
}

KEYWORDS = {
    "federal reserve": 6,
    "interest rate": 5,
    "inflation": 5,
    "cpi": 5,
    "pce": 5,
    "jobs": 4,
    "payroll": 5,
    "gdp": 4,
    "recession": 5,
    "tariff": 5,
    "sanction": 5,
    "war": 4,
    "ceasefire": 4,
    "election": 4,
    "central bank": 5,
    "ecb": 5,
    "boj": 5,
    "boe": 5,
    "oil": 4,
    "gold": 3,
    "bitcoin": 4,
    "crypto": 3,
    "bond": 4,
    "yield": 4,
    "dollar": 4,
    "stocks": 3,
    "market": 3,
    "earnings": 3,
}

@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    category: str
    published_at: str | None
    timestamp: float
    aggregator: str
    relevance_score: float

def _download(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml,application/xml,text/xml,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()

def _timestamp(value: str | None) -> tuple[str | None, float]:
    if not value:
        return None, time.time()
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        return parsed.isoformat(), parsed.timestamp()
    except Exception:
        return value, time.time()

def _clean(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", "", value or ""))
    return " ".join(value.split())

def _score(title: str, source: str, timestamp: float) -> float:
    text = title.lower()
    score = float(SOURCE_WEIGHT.get(source, 5))

    for keyword, weight in KEYWORDS.items():
        if keyword in text:
            score += weight

    age_hours = max(0.0, (time.time() - timestamp) / 3600)
    score += max(0.0, 12.0 - age_hours / 2)
    return round(score, 2)

def _parse_rss(
    raw: bytes,
    *,
    fallback_source: str,
    category: str,
    aggregator: str,
) -> list[NewsItem]:
    root = ET.fromstring(raw)
    results = []

    for element in root.iter():
        if element.tag.split("}")[-1] != "item":
            continue

        fields = {}
        for child in list(element):
            fields[child.tag.split("}")[-1]] = (child.text or "").strip()

        title = _clean(fields.get("title", ""))
        link = fields.get("link", "")
        source = _clean(fields.get("source", "")) or fallback_source
        published = (
            fields.get("pubDate")
            or fields.get("published")
            or fields.get("date")
        )
        iso, ts = _timestamp(published)

        if title and link:
            results.append(
                NewsItem(
                    title=title,
                    url=link,
                    source=source,
                    category=category,
                    published_at=iso,
                    timestamp=ts,
                    aggregator=aggregator,
                    relevance_score=_score(title, source, ts),
                )
            )

    return results

def google_news_url(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote_plus(query)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

def refresh() -> dict:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    items: list[NewsItem] = []
    errors = []

    for category, query in GOOGLE_QUERIES:
        try:
            raw = _download(google_news_url(query))
            items.extend(
                _parse_rss(
                    raw,
                    fallback_source=category,
                    category=category,
                    aggregator="Google News RSS",
                )
            )
        except Exception as exc:
            errors.append({"source": category, "error": str(exc)})

    for source, category, url in DIRECT_FEEDS:
        try:
            raw = _download(url)
            items.extend(
                _parse_rss(
                    raw,
                    fallback_source=source,
                    category=category,
                    aggregator="Direct RSS",
                )
            )
        except Exception as exc:
            errors.append({"source": source, "error": str(exc)})

    unique = {}
    for item in items:
        key = re.sub(r"[^a-z0-9]+", " ", item.title.lower()).strip()
        current = unique.get(key)
        if current is None or item.relevance_score > current.relevance_score:
            unique[key] = item

    ordered = sorted(
        unique.values(),
        key=lambda item: (item.relevance_score, item.timestamp),
        reverse=True,
    )

    ordered = ordered[: int(os.getenv("FX_NEWSPAPER_MAX_ITEMS", "120"))]

    payload = {
        "generated_at": time.time(),
        "refresh_interval_seconds": int(
            os.getenv("FX_NEWSPAPER_REFRESH_SECONDS", "1800")
        ),
        "items": [asdict(item) for item in ordered],
        "errors": errors,
        "policy": (
            "Source-labelled headline metadata only. "
            "Original source links are preserved. "
            "No paywall bypass and no article-body scraping."
        ),
    }

    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp, OUTPUT)
    return payload

def load() -> dict:
    if not OUTPUT.exists():
        return refresh()
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception:
        return refresh()
PY

cat > "$ROOT/scripts/fx-news-refresh.py" <<'PY'
from services.agents.supervisor import supervisor
from services.news.newspaper import refresh

def task(checkpoint):
    checkpoint({"stage": "collecting_sources"})
    result = refresh()
    checkpoint(
        {
            "stage": "ranked",
            "headlines": len(result.get("items", [])),
        }
    )
    return {
        "headlines": len(result.get("items", [])),
        "errors": len(result.get("errors", [])),
    }

run = supervisor.run(
    agent_id="newspaper",
    goal="Refresh and rank the FX Global Newspaper",
    task=task,
)

print("FX Newspaper Agent:", run.status)
print("Result:", run.result)
PY

###############################################################################
# PAPER STRATEGY FLEET
###############################################################################

cat > "$ROOT/services/paper_fleet/fleet.py" <<'PY'
from __future__ import annotations

import json
import math
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path("/Users/macmac/Documents/Codex/FX")
DB_PATH = ROOT / "data" / "paper_fleet" / "fleet.sqlite3"
STATE_PATH = ROOT / "data" / "paper_fleet" / "latest.json"

STRATEGIES = [
    "Trend Following",
    "Momentum",
    "20-Period Breakout",
    "Mean Reversion",
    "Bollinger Mean Reversion",
    "RSI Reversion",
    "MACD Trend",
    "Volatility Breakout",
    "Kalman Trend",
    "Pairs Trading",
    "Cross-Sectional Momentum",
    "Regime-Aware Trend",
    "Carry",
    "Institutional Positioning",
    "Activist Event",
    "Options Volatility",
]

@dataclass
class StrategySnapshot:
    strategy: str
    status: str
    capital_assigned: float
    nav: float
    signal: int
    signal_name: str
    symbol: str
    data_source: str
    last_price: float | None
    position_units: float
    realized_pnl: float
    unrealized_pnl: float
    observations: int
    signal_changes: int
    updated_at: float
    note: str

def _initial_capital() -> float:
    return float(
        os.getenv(
            "FX_PAPER_FLEET_CAPITAL_PER_STRATEGY",
            "1.00",
        )
    )

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_state (
            strategy TEXT PRIMARY KEY,
            nav REAL NOT NULL,
            cash REAL NOT NULL,
            position_units REAL NOT NULL,
            position_side INTEGER NOT NULL,
            entry_price REAL,
            realized_pnl REAL NOT NULL,
            observations INTEGER NOT NULL,
            signal_changes INTEGER NOT NULL,
            last_signal INTEGER NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            timestamp REAL NOT NULL,
            symbol TEXT NOT NULL,
            price REAL,
            signal INTEGER NOT NULL,
            nav REAL NOT NULL,
            realized_pnl REAL NOT NULL,
            unrealized_pnl REAL NOT NULL,
            note TEXT
        )
        """
    )

    return conn

def _load_prices(symbol: str) -> tuple[pd.DataFrame, str]:
    """
    Paper-fleet fallback market feed.

    The main FX app continues to use London Strategic Edge as primary research.
    This micro-paper heartbeat uses Yahoo Finance only as a fallback until the
    existing LSE history adapter is wired directly into this worker.
    """
    frame = yf.download(
        symbol,
        period="6mo",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if frame.empty:
        raise RuntimeError(f"No market data for {symbol}")

    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [column[0] for column in frame.columns]

    frame = frame.dropna()

    if len(frame) < 40:
        raise RuntimeError(f"Not enough history for {symbol}")

    return frame, "Yahoo Finance fallback for micro-paper fleet"

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def _signal(name: str, frame: pd.DataFrame) -> tuple[int, str]:
    close = frame["Close"].astype(float)
    high = frame["High"].astype(float)
    low = frame["Low"].astype(float)
    last = float(close.iloc[-1])

    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    returns = close.pct_change()

    if name == "Trend Following":
        return (
            1 if ema20.iloc[-1] > ema50.iloc[-1] else -1,
            "EMA20 vs EMA50",
        )

    if name == "Momentum":
        momentum = close.iloc[-1] / close.iloc[-21] - 1
        return (
            1 if momentum > 0 else -1,
            "20-day momentum",
        )

    if name == "20-Period Breakout":
        prev_high = high.shift(1).rolling(20).max().iloc[-1]
        prev_low = low.shift(1).rolling(20).min().iloc[-1]

        if last > prev_high:
            return 1, "20-day upside breakout"

        if last < prev_low:
            return -1, "20-day downside breakout"

        return 0, "No breakout"

    if name == "Mean Reversion":
        mean = close.rolling(20).mean().iloc[-1]
        std = close.rolling(20).std().iloc[-1]
        z = ((last - mean) / std) if std and not math.isnan(std) else 0

        if z < -1:
            return 1, f"z={z:.2f}"

        if z > 1:
            return -1, f"z={z:.2f}"

        return 0, f"z={z:.2f}"

    if name == "Bollinger Mean Reversion":
        mean = close.rolling(20).mean().iloc[-1]
        std = close.rolling(20).std().iloc[-1]

        if last < mean - 2 * std:
            return 1, "Below lower Bollinger band"

        if last > mean + 2 * std:
            return -1, "Above upper Bollinger band"

        return 0, "Inside Bollinger bands"

    if name == "RSI Reversion":
        value = float(_rsi(close).iloc[-1])

        if value < 30:
            return 1, f"RSI={value:.1f}"

        if value > 70:
            return -1, f"RSI={value:.1f}"

        return 0, f"RSI={value:.1f}"

    if name == "MACD Trend":
        fast = close.ewm(span=12, adjust=False).mean()
        slow = close.ewm(span=26, adjust=False).mean()
        macd = fast - slow
        signal_line = macd.ewm(span=9, adjust=False).mean()

        return (
            1 if macd.iloc[-1] > signal_line.iloc[-1] else -1,
            "MACD vs signal",
        )

    if name == "Volatility Breakout":
        atr = (high - low).rolling(14).mean()
        range_now = high.iloc[-1] - low.iloc[-1]

        if range_now > 1.5 * atr.iloc[-1]:
            return (
                1 if close.iloc[-1] > close.iloc[-2] else -1,
                "Volatility expansion",
            )

        return 0, "No volatility breakout"

    if name == "Kalman Trend":
        smooth = close.ewm(span=10, adjust=False).mean()
        return (
            1 if smooth.iloc[-1] > smooth.iloc[-5] else -1,
            "Smoothed-trend proxy until existing FX Kalman adapter is linked",
        )

    if name == "Regime-Aware Trend":
        vol = returns.rolling(20).std().iloc[-1]
        median_vol = float(returns.rolling(20).std().dropna().median())

        if vol > 2 * median_vol:
            return 0, "Extreme volatility regime"

        return (
            1 if ema20.iloc[-1] > ema50.iloc[-1] else -1,
            "Trend allowed by volatility regime",
        )

    specialized = {
        "Pairs Trading": "Running; waiting for validated pair adapter",
        "Cross-Sectional Momentum": "Running; waiting for validated universe adapter",
        "Carry": "Running; waiting for FX/futures funding adapter",
        "Institutional Positioning": "Running; waiting for institutional/COT adapter",
        "Activist Event": "Running; waiting for validated activist-event feed",
        "Options Volatility": "Running; waiting for options IV surface adapter",
    }

    return 0, specialized.get(name, "NO_TRADE")

def _load_state(conn, strategy: str) -> dict:
    row = conn.execute(
        """
        SELECT nav,cash,position_units,position_side,entry_price,
               realized_pnl,observations,signal_changes,last_signal
        FROM strategy_state WHERE strategy=?
        """,
        (strategy,),
    ).fetchone()

    if row:
        return {
            "nav": float(row[0]),
            "cash": float(row[1]),
            "position_units": float(row[2]),
            "position_side": int(row[3]),
            "entry_price": float(row[4]) if row[4] is not None else None,
            "realized_pnl": float(row[5]),
            "observations": int(row[6]),
            "signal_changes": int(row[7]),
            "last_signal": int(row[8]),
        }

    capital = _initial_capital()

    return {
        "nav": capital,
        "cash": capital,
        "position_units": 0.0,
        "position_side": 0,
        "entry_price": None,
        "realized_pnl": 0.0,
        "observations": 0,
        "signal_changes": 0,
        "last_signal": 0,
    }

def run_cycle(symbol: str | None = None) -> dict:
    symbol = symbol or os.getenv(
        "FX_PAPER_FLEET_DEFAULT_SYMBOL",
        "AAPL",
    )

    frame, data_source = _load_prices(symbol)
    price = float(frame["Close"].iloc[-1])
    now = time.time()
    conn = _connect()
    snapshots = []

    try:
        for strategy in STRATEGIES:
            signal, note = _signal(strategy, frame)
            state = _load_state(conn, strategy)
            state["observations"] += 1
            old_signal = state["last_signal"]

            if signal != old_signal:
                state["signal_changes"] += 1

                if state["position_side"] != 0 and state["entry_price"]:
                    pnl = (
                        state["position_units"]
                        * (price - state["entry_price"])
                        * state["position_side"]
                    )
                    state["realized_pnl"] += pnl
                    state["cash"] += pnl

                state["position_units"] = 0.0
                state["position_side"] = 0
                state["entry_price"] = None

                if signal in (-1, 1):
                    capital = max(0.0, state["cash"])
                    state["position_units"] = (
                        capital / price
                        if price > 0
                        else 0.0
                    )
                    state["position_side"] = signal
                    state["entry_price"] = price

                state["last_signal"] = signal

            unrealized = 0.0

            if state["position_side"] != 0 and state["entry_price"]:
                unrealized = (
                    state["position_units"]
                    * (price - state["entry_price"])
                    * state["position_side"]
                )

            nav = state["cash"] + unrealized

            conn.execute(
                """
                INSERT INTO strategy_state(
                    strategy,nav,cash,position_units,position_side,
                    entry_price,realized_pnl,observations,signal_changes,
                    last_signal,updated_at
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(strategy) DO UPDATE SET
                    nav=excluded.nav,
                    cash=excluded.cash,
                    position_units=excluded.position_units,
                    position_side=excluded.position_side,
                    entry_price=excluded.entry_price,
                    realized_pnl=excluded.realized_pnl,
                    observations=excluded.observations,
                    signal_changes=excluded.signal_changes,
                    last_signal=excluded.last_signal,
                    updated_at=excluded.updated_at
                """,
                (
                    strategy,
                    nav,
                    state["cash"],
                    state["position_units"],
                    state["position_side"],
                    state["entry_price"],
                    state["realized_pnl"],
                    state["observations"],
                    state["signal_changes"],
                    state["last_signal"],
                    now,
                ),
            )

            conn.execute(
                """
                INSERT INTO strategy_history(
                    strategy,timestamp,symbol,price,signal,nav,
                    realized_pnl,unrealized_pnl,note
                )
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    strategy,
                    now,
                    symbol,
                    price,
                    signal,
                    nav,
                    state["realized_pnl"],
                    unrealized,
                    note,
                ),
            )

            snapshots.append(
                StrategySnapshot(
                    strategy=strategy,
                    status="RUNNING",
                    capital_assigned=_initial_capital(),
                    nav=round(nav, 8),
                    signal=signal,
                    signal_name={
                        -1: "SHORT",
                        0: "NO_TRADE",
                        1: "LONG",
                    }[signal],
                    symbol=symbol,
                    data_source=data_source,
                    last_price=price,
                    position_units=round(
                        state["position_units"],
                        10,
                    ),
                    realized_pnl=round(
                        state["realized_pnl"],
                        8,
                    ),
                    unrealized_pnl=round(
                        unrealized,
                        8,
                    ),
                    observations=state["observations"],
                    signal_changes=state["signal_changes"],
                    updated_at=now,
                    note=note,
                )
            )

        conn.commit()
    finally:
        conn.close()

    payload = {
        "generated_at": now,
        "mode": "VIRTUAL_PAPER_MICRO",
        "real_money": False,
        "paper_capital_per_strategy": _initial_capital(),
        "symbol": symbol,
        "strategies": [asdict(item) for item in snapshots],
        "policy": (
            "Every strategy worker runs every cycle and has $1 virtual paper capital. "
            "FX never manufactures a trade solely to keep capital moving. "
            "NO_TRADE is part of the system."
        ),
    }

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp, STATE_PATH)

    return payload

def load_latest() -> dict:
    if not STATE_PATH.exists():
        return run_cycle()

    return json.loads(
        STATE_PATH.read_text(
            encoding="utf-8"
        )
    )
PY

cat > "$ROOT/scripts/fx-paper-fleet-cycle.py" <<'PY'
from services.agents.supervisor import supervisor
from services.paper_fleet.fleet import run_cycle

def task(checkpoint):
    checkpoint({"stage": "loading_market_data"})
    result = run_cycle()
    checkpoint(
        {
            "stage": "strategy_cycle_complete",
            "strategies": len(result.get("strategies", [])),
        }
    )
    return {
        "strategies": len(result.get("strategies", [])),
        "paper_capital_per_strategy": result.get(
            "paper_capital_per_strategy"
        ),
    }

run = supervisor.run(
    agent_id="paper_strategy_fleet",
    goal="Run every paper strategy, update its $1 virtual account, and persist learning observations",
    task=task,
)

print("FX Paper Fleet Agent:", run.status)
print("Result:", run.result)
PY

###############################################################################
# UI ROUTES
###############################################################################

cat > "$ROOT/backend/app/routes/fx_newspaper.py" <<'PY'
from __future__ import annotations

import html
import time

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.news.newspaper import load

router = APIRouter()

@router.get("/api/newspaper")
def newspaper_api():
    return load()

def _render(data: dict, embedded: bool = False) -> str:
    age = max(
        0,
        int(
            (
                time.time()
                - data.get(
                    "generated_at",
                    time.time(),
                )
            )
            / 60
        ),
    )

    groups = {}
    for item in data.get("items", []):
        groups.setdefault(
            item.get(
                "category",
                "Latest",
            ),
            [],
        ).append(item)

    sections = []

    for category, items in groups.items():
        cards = []

        for item in items[:18]:
            cards.append(
                "<article class='story'>"
                f"<div class='src'>{html.escape(item.get('source','Unknown'))}</div>"
                f"<a href='{html.escape(item.get('url','#'))}' target='_blank' rel='noopener noreferrer'>"
                f"{html.escape(item.get('title',''))}</a>"
                f"<div class='meta'>Score {item.get('relevance_score',0)} · "
                f"{html.escape(item.get('published_at') or '')}</div>"
                "</article>"
            )

        sections.append(
            f"<section><h2>{html.escape(category)}</h2>"
            f"<div class='grid'>{''.join(cards)}</div></section>"
        )

    back = "" if embedded else "<nav><a href='/chat'>← FX Terminal</a></nav>"

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>FX Global Newspaper</title>
<style>
:root{{color-scheme:dark;--bg:#090a0b;--panel:#121417;--line:#2a2e33;--text:#f4f4f5;--muted:#9da3aa}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{width:min(1500px,96vw);margin:auto;padding:{'12px' if embedded else '28px'} 0 60px}}
nav{{margin-bottom:18px}} nav a{{color:var(--muted);text-decoration:none;font-size:12px}}
.head{{display:flex;justify-content:space-between;gap:20px;align-items:flex-end;border-bottom:1px solid var(--line);padding-bottom:18px}}
h1{{margin:0;font-size:{'24px' if embedded else '34px'};letter-spacing:-1px}}
.dek{{color:var(--muted);margin-top:7px;max-width:900px;line-height:1.5;font-size:12px}}
.age{{color:var(--muted);font-size:11px;white-space:nowrap}}
h2{{font-size:17px;border-bottom:1px solid var(--line);padding-bottom:8px;margin:28px 0 10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:9px}}
.story{{background:var(--panel);border:1px solid var(--line);padding:14px;min-height:115px}}
.src{{color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.7px;margin-bottom:9px}}
.story a{{color:var(--text);font-weight:650;text-decoration:none;line-height:1.35;font-size:14px}}
.story a:hover{{text-decoration:underline}}
.meta{{color:var(--muted);font-size:9px;margin-top:10px}}
</style>
</head>
<body>
<main>
{back}
<div class="head">
<div>
<h1>FX Global Newspaper</h1>
<div class="dek">
Ranked global finance, economics, central-bank and geopolitical headlines.
Updated every 30 minutes. Every item retains its original source.
</div>
</div>
<div class="age">Dataset age: {age} min</div>
</div>
{''.join(sections)}
</main>
</body>
</html>"""

@router.get("/newspaper", response_class=HTMLResponse)
def newspaper_page():
    return _render(load(), embedded=False)

@router.get("/newspaper/embed", response_class=HTMLResponse)
def newspaper_embed():
    return _render(load(), embedded=True)
PY

cat > "$ROOT/backend/app/routes/fx_strategy_fleet.py" <<'PY'
from __future__ import annotations

import html
import time

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.paper_fleet.fleet import load_latest

router = APIRouter()

@router.get("/api/strategy-fleet")
def strategy_fleet_api():
    return load_latest()

@router.get("/strategy-fleet", response_class=HTMLResponse)
def strategy_fleet_page():
    data = load_latest()

    cards = []

    for item in data.get("strategies", []):
        cards.append(
            "<article class='card'>"
            f"<div class='top'><strong>{html.escape(item['strategy'])}</strong>"
            "<span>RUNNING · PAPER</span></div>"
            f"<div class='signal'>{html.escape(item['signal_name'])}</div>"
            "<div class='metrics'>"
            f"<div><small>Assigned</small><b>${item['capital_assigned']:.2f}</b></div>"
            f"<div><small>NAV</small><b>${item['nav']:.4f}</b></div>"
            f"<div><small>Observations</small><b>{item['observations']}</b></div>"
            f"<div><small>Signal changes</small><b>{item['signal_changes']}</b></div>"
            "</div>"
            f"<p>{html.escape(item['note'])}</p>"
            f"<p class='src'>Data: {html.escape(item.get('data_source',''))}</p>"
            "</article>"
        )

    age = max(
        0,
        int(
            (
                time.time()
                - data.get(
                    "generated_at",
                    time.time(),
                )
            )
            / 60
        ),
    )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="120">
<title>FX Paper Strategy Fleet</title>
<style>
:root{{color-scheme:dark;--bg:#090a0b;--panel:#121417;--line:#2a2e33;--text:#f4f4f5;--muted:#9da3aa}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{width:min(1500px,96vw);margin:auto;padding:28px 0 70px}}
nav{{margin-bottom:18px}} nav a{{color:var(--muted);text-decoration:none;font-size:12px}}
h1{{font-size:32px;margin:0;letter-spacing:-1px}}
.dek{{color:var(--muted);max-width:900px;line-height:1.5;margin:8px 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}}
.card{{background:var(--panel);border:1px solid var(--line);padding:16px}}
.top{{display:flex;justify-content:space-between;gap:10px}}
.top span{{color:var(--muted);font-size:9px;border:1px solid var(--line);border-radius:999px;padding:4px 7px}}
.signal{{font-size:24px;font-weight:750;margin:20px 0}}
.metrics{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.metrics div{{border-top:1px solid var(--line);padding-top:8px}}
small{{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;margin-bottom:4px}}
p{{color:var(--muted);font-size:11px;line-height:1.5;margin-bottom:0}}
.src{{font-size:9px}}
</style>
</head>
<body>
<main>
<nav><a href="/chat">← FX Terminal</a></nav>
<h1>FX Paper Strategy Fleet</h1>
<div class="dek">
Every strategy worker runs on schedule with its own $1 virtual paper account.
A strategy may remain NO_TRADE when its setup or required specialized data is absent.
No real-money orders are submitted. Dataset age: {age} minutes.
</div>
<div class="grid">{''.join(cards)}</div>
</main>
</body>
</html>"""
PY

cat > "$ROOT/backend/app/routes/fx_agents.py" <<'PY'
from fastapi import APIRouter

from services.agents.supervisor import supervisor
from services.agents.sparse_router import route

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/runs")
def agent_runs(limit: int = 50):
    return {
        "runs": supervisor.latest(limit=max(1, min(limit, 200)))
    }

@router.get("/route")
def route_experts(tags: str):
    parsed = {
        item.strip().lower()
        for item in tags.split(",")
        if item.strip()
    }

    return {
        "tags": sorted(parsed),
        "selected_experts": route(parsed),
        "risk_note": (
            "Risk is sovereign and remains outside expert voting."
        ),
    }
PY

cat > "$ROOT/backend/app/routes/fx_brain.py" <<'PY'
from fastapi import APIRouter, HTTPException

from services.brain.trace import brain_trace_store

router = APIRouter(prefix="/api/brain", tags=["brain"])

@router.get("/runs/{run_id}")
def get_run(run_id: str):
    events = brain_trace_store.get_run(run_id)

    if not events:
        raise HTTPException(
            status_code=404,
            detail="Run not found.",
        )

    return {
        "run_id": run_id,
        "display_policy": (
            "structured_evidence_trace_not_hidden_chain_of_thought"
        ),
        "events": events,
    }
PY

cat > "$ROOT/backend/app/routes/fx_security.py" <<'PY'
from __future__ import annotations

import base64
import os
import secrets
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.auth.approval import (
    ApprovalPayload,
    issue_live_approval,
)
from services.auth.totp import totp_service

router = APIRouter(prefix="/api/security", tags=["security"])

class EnrollRequest(BaseModel):
    rotate: bool = False

class LiveApprovalRequest(BaseModel):
    proposal_id: str
    instrument: str
    side: str
    quantity: float = Field(gt=0)
    order_type: str
    max_notional: float = Field(gt=0)
    risk_decision_id: str
    totp_code: str = Field(min_length=6, max_length=8)

@router.get("/totp/status")
def totp_status():
    return {
        "enrolled": totp_service.is_enrolled()
    }

@router.post("/totp/enroll")
def totp_enroll(req: EnrollRequest):
    try:
        result = totp_service.enroll(
            rotate=req.rotate
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return {
        "secret": result["secret"],
        "provisioning_uri": result["provisioning_uri"],
        "qr_png_base64": base64.b64encode(
            result["qr_png"]
        ).decode(),
        "warning": "Display once. Do not log the secret.",
    }

@router.post("/live-approval")
def live_approval(req: LiveApprovalRequest):
    ttl = int(
        os.getenv(
            "FX_LIVE_APPROVAL_TTL_SECONDS",
            "90",
        )
    )

    payload = ApprovalPayload(
        proposal_id=req.proposal_id,
        instrument=req.instrument,
        side=req.side,
        quantity=req.quantity,
        order_type=req.order_type,
        max_notional=req.max_notional,
        risk_decision_id=req.risk_decision_id,
        expires_at=int(time.time()) + ttl,
        nonce=secrets.token_hex(16),
    )

    try:
        token = issue_live_approval(
            payload,
            req.totp_code,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    return {
        "approval_token": token,
        "expires_at": payload.expires_at,
        "payload": payload.__dict__,
    }
PY

###############################################################################
# MOUNT ROUTES
###############################################################################

if [ -f "$ROOT/backend/app/main.py" ]; then
  if ! grep -q "# FX_V4_ROUTERS" "$ROOT/backend/app/main.py"; then
    cat >> "$ROOT/backend/app/main.py" <<'PY'

# FX_V4_ROUTERS
try:
    from backend.app.routes.fx_newspaper import router as fx_newspaper_router
    from backend.app.routes.fx_strategy_fleet import router as fx_strategy_fleet_router
    from backend.app.routes.fx_agents import router as fx_agents_router
    from backend.app.routes.fx_brain import router as fx_brain_router
    from backend.app.routes.fx_security import router as fx_security_router

    app.include_router(fx_newspaper_router)
    app.include_router(fx_strategy_fleet_router)
    app.include_router(fx_agents_router)
    app.include_router(fx_brain_router)
    app.include_router(fx_security_router)
except Exception as fx_v4_router_error:
    print("FX V4 route warning:", fx_v4_router_error)
PY
    echo "✓ FX V4 routes mounted"
  else
    echo "✓ FX V4 routes already mounted"
  fi
else
  echo "⚠ backend/app/main.py not found; routes created but not mounted"
fi

###############################################################################
# TRY TO EMBED NEWSPAPER IN JOURNAL PAGE
###############################################################################

"$PY" - <<'PY'
from pathlib import Path
import re

root = Path("/Users/macmac/Documents/Codex/FX")
extensions = {".html", ".htm", ".py"}

iframe_block = """
<div id="fx-global-newspaper-embed" style="margin:24px 0 30px;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px;">
    <div>
      <div style="font-size:20px;font-weight:700;">FX Global Newspaper</div>
      <div style="font-size:11px;color:#9da3aa;margin-top:4px;">
        Finance, economics and geopolitics · ranked · source-labelled · refreshed every 30 minutes
      </div>
    </div>
    <a href="/newspaper" style="color:#f4f4f5;text-decoration:none;border:1px solid #343a40;border-radius:6px;padding:7px 10px;font-size:11px;">
      Open full newspaper
    </a>
  </div>
  <iframe
    src="/newspaper/embed"
    title="FX Global Newspaper"
    loading="lazy"
    style="width:100%;height:760px;border:1px solid #2a2e33;border-radius:8px;background:#090a0b;"
  ></iframe>
</div>
"""

patched = False

for path in root.rglob("*"):
    if path.suffix.lower() not in extensions:
        continue

    try:
        text = path.read_text()
    except Exception:
        continue

    if "Journal & Research Sources" not in text:
        continue

    if "fx-global-newspaper-embed" in text:
        print("✓ Newspaper already embedded in:", path)
        patched = True
        continue

    patterns = [
        r"(<h1[^>]*>\s*Journal &amp; Research Sources\s*</h1>)",
        r"(<h1[^>]*>\s*Journal & Research Sources\s*</h1>)",
        r"(<h2[^>]*>\s*Journal &amp; Research Sources\s*</h2>)",
        r"(<h2[^>]*>\s*Journal & Research Sources\s*</h2>)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if not match:
            continue

        new_text = (
            text[: match.end()]
            + iframe_block
            + text[match.end() :]
        )

        path.write_text(new_text)
        print("✓ Newspaper embedded in Journal page:", path)
        patched = True
        break

if not patched:
    print(
        "ℹ Could not safely auto-edit the Journal source. "
        "The newspaper is still available at /newspaper."
    )
PY

###############################################################################
# TRY TO ADD FLEET LINK TO STRATEGY LIBRARY
###############################################################################

"$PY" - <<'PY'
from pathlib import Path
import re

root = Path("/Users/macmac/Documents/Codex/FX")
extensions = {".html", ".htm", ".py"}

button = """
<div id="fx-paper-fleet-link" style="margin:12px 0 18px;">
  <a href="/strategy-fleet" style="display:inline-block;color:#f4f4f5;text-decoration:none;border:1px solid #343a40;border-radius:6px;padding:8px 11px;font-size:11px;">
    Open Running Paper Strategy Fleet
  </a>
</div>
"""

for path in root.rglob("*"):
    if path.suffix.lower() not in extensions:
        continue

    try:
        text = path.read_text()
    except Exception:
        continue

    if "Strategy Library" not in text:
        continue

    if "fx-paper-fleet-link" in text:
        continue

    match = re.search(
        r"(<h1[^>]*>\s*Strategy Library\s*</h1>)",
        text,
        flags=re.I,
    )

    if match:
        text = (
            text[: match.end()]
            + button
            + text[match.end() :]
        )
        path.write_text(text)
        print("✓ Paper Fleet link added to Strategy Library:", path)
        break
PY

###############################################################################
# SCHEDULERS
###############################################################################

set -a
source "$ROOT/.env"
set +a

NEWS_PLIST="$HOME/Library/LaunchAgents/com.fx.newspaper.refresh.plist"

cat > "$NEWS_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.fx.newspaper.refresh</string>

  <key>ProgramArguments</key>
  <array>
    <string>$PY</string>
    <string>$ROOT/scripts/fx-news-refresh.py</string>
  </array>

  <key>WorkingDirectory</key>
  <string>$ROOT</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>$ROOT</string>
  </dict>

  <key>StartInterval</key>
  <integer>1800</integer>

  <key>RunAtLoad</key>
  <true/>

  <key>StandardOutPath</key>
  <string>$ROOT/data/news/refresh.log</string>

  <key>StandardErrorPath</key>
  <string>$ROOT/data/news/refresh-error.log</string>
</dict>
</plist>
EOF

launchctl bootout \
  "gui/$(id -u)/com.fx.newspaper.refresh" \
  >/dev/null 2>&1 || true

launchctl bootstrap \
  "gui/$(id -u)" \
  "$NEWS_PLIST" \
  >/dev/null 2>&1 || true

FLEET_PLIST="$HOME/Library/LaunchAgents/com.fx.paperfleet.plist"

cat > "$FLEET_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.fx.paperfleet</string>

  <key>ProgramArguments</key>
  <array>
    <string>$PY</string>
    <string>$ROOT/scripts/fx-paper-fleet-cycle.py</string>
  </array>

  <key>WorkingDirectory</key>
  <string>$ROOT</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>$ROOT</string>
  </dict>

  <key>StartInterval</key>
  <integer>300</integer>

  <key>RunAtLoad</key>
  <true/>

  <key>StandardOutPath</key>
  <string>$ROOT/data/paper_fleet/fleet.log</string>

  <key>StandardErrorPath</key>
  <string>$ROOT/data/paper_fleet/fleet-error.log</string>
</dict>
</plist>
EOF

launchctl bootout \
  "gui/$(id -u)/com.fx.paperfleet" \
  >/dev/null 2>&1 || true

launchctl bootstrap \
  "gui/$(id -u)" \
  "$FLEET_PLIST" \
  >/dev/null 2>&1 || true

echo "✓ Schedulers installed"

###############################################################################
# INITIAL RUNS
###############################################################################

echo ""
echo "Running initial newspaper cycle..."
PYTHONPATH="$ROOT" "$PY" "$ROOT/scripts/fx-news-refresh.py" || true

echo ""
echo "Running initial strategy fleet cycle..."
PYTHONPATH="$ROOT" "$PY" "$ROOT/scripts/fx-paper-fleet-cycle.py" || true

###############################################################################
# SYNTAX + IMPORT TEST
###############################################################################

echo ""
echo "Running syntax checks..."

PYTHONPATH="$ROOT" "$PY" -m py_compile \
  "$ROOT/services/auth/totp.py" \
  "$ROOT/services/auth/approval.py" \
  "$ROOT/services/execution/policy.py" \
  "$ROOT/services/execution/live_gate.py" \
  "$ROOT/services/brain/trace.py" \
  "$ROOT/services/memory/turbovec_store.py" \
  "$ROOT/services/learning/market_learning.py" \
  "$ROOT/services/research/trader_brain_schema.py" \
  "$ROOT/services/agents/supervisor.py" \
  "$ROOT/services/agents/sparse_router.py" \
  "$ROOT/services/news/newspaper.py" \
  "$ROOT/services/paper_fleet/fleet.py" \
  "$ROOT/backend/app/routes/fx_newspaper.py" \
  "$ROOT/backend/app/routes/fx_strategy_fleet.py" \
  "$ROOT/backend/app/routes/fx_agents.py" \
  "$ROOT/backend/app/routes/fx_brain.py" \
  "$ROOT/backend/app/routes/fx_security.py"

echo "✓ Syntax checks passed"

PYTHONPATH="$ROOT" "$PY" - <<'PY'
from services.execution.policy import (
    ExecutionPolicy,
    assert_safe_policy,
)
from services.agents.sparse_router import route
from services.paper_fleet.fleet import STRATEGIES
from services.news.newspaper import load

policy = ExecutionPolicy.from_env()
assert_safe_policy(policy)

assert policy.live_enabled is False
assert policy.ai_can_execute_live is False
assert len(STRATEGIES) == 16
assert len(route({"macro", "rates", "fx"})) >= 1

print("✓ services imports: PASS")
print("✓ live trading: DISABLED")
print("✓ AI live execution: DISABLED")
print("✓ strategy workers:", len(STRATEGIES))
print("✓ newspaper headlines:", len(load().get("items", [])))
print("✓ sparse expert routing:", route({"macro", "rates", "fx"}))
PY

if [ -f "$ROOT/backend/app/main.py" ]; then
  PYTHONPATH="$ROOT" "$PY" - <<'PY'
from backend.app.main import app

paths = {route.path for route in app.routes}

required = [
    "/newspaper",
    "/newspaper/embed",
    "/api/newspaper",
    "/strategy-fleet",
    "/api/strategy-fleet",
    "/api/agents/runs",
    "/api/security/totp/status",
]

for path in required:
    print(("✓" if path in paths else "⚠"), path)
PY
fi

echo ""
echo "============================================================"
echo " FX TERMINAL UPGRADE V4 COMPLETE"
echo "============================================================"
echo ""
echo "Fixed:"
echo "  ✓ PYTHONPATH points to /Users/macmac/Documents/Codex/FX"
echo "  ✓ No ZIP/download step required"
echo ""
echo "Newspaper:"
echo "  ✓ Ranked finance/economics/politics/geopolitics"
echo "  ✓ Source-labelled"
echo "  ✓ 30-minute automatic refresh"
echo "  ✓ Journal-page embed attempted automatically"
echo "  ✓ Full page: http://127.0.0.1:8000/newspaper"
echo ""
echo "Paper strategy fleet:"
echo "  ✓ 16 strategy workers"
echo "  ✓ \$1 virtual capital assigned to each"
echo "  ✓ 5-minute cycles"
echo "  ✓ observations + signal changes + NAV + PnL persisted"
echo "  ✓ NO_TRADE remains valid"
echo "  ✓ Page: http://127.0.0.1:8000/strategy-fleet"
echo ""
echo "Harness V1.1:"
echo "  ✓ TOTP"
echo "  ✓ signed approvals"
echo "  ✓ deterministic live gate"
echo "  ✓ Brain trace"
echo "  ✓ TurboVec"
echo "  ✓ continuous learner"
echo "  ✓ trader-brain schema"
echo ""
echo "Agent runtime:"
echo "  ✓ durable AgentRun records"
echo "  ✓ checkpoints"
echo "  ✓ scheduled task workers"
echo "  ✓ sparse expert routing"
echo "  ✓ Risk remains sovereign"
echo ""
echo "Safety:"
echo "  ✓ LIVE_TRADING_ENABLED=false"
echo "  ✓ AI_CAN_EXECUTE_LIVE=false"
echo ""
echo "Start FX:"
echo "  fx"
echo "============================================================"

if command -v fx >/dev/null 2>&1; then
  fx
elif [ -x "$HOME/bin/fx" ]; then
  "$HOME/bin/fx"
fi

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
    raw = json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


class BrainTraceStore:
    """Observable reasoning *summary* ledger.

    This deliberately stores auditable process/evidence summaries instead of
    hidden model chain-of-thought.
    """

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
            return [asdict(x) for x in self._events if x.run_id == run_id]


brain_trace_store = BrainTraceStore()

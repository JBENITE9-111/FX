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

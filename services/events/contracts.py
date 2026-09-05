from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class SignalState(str, Enum):
    NO_SETUP = "NO_SETUP"
    WATCHING = "WATCHING"
    POTENTIAL_LONG = "POTENTIAL_LONG"
    POTENTIAL_SHORT = "POTENTIAL_SHORT"
    LONG_CONFIRMED = "LONG_CONFIRMED"
    SHORT_CONFIRMED = "SHORT_CONFIRMED"
    BLOCKED = "BLOCKED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"
    TP1_HIT = "TP1_HIT"
    TP2_HIT = "TP2_HIT"
    STOP_HIT = "STOP_HIT"
    CLOSED = "CLOSED"


class ResearchEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    source: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    subject_type: str
    subject_id: str
    state: SignalState | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    versions: dict[str, str] = Field(default_factory=dict)
    input_hash: str | None = None
    output_hash: str | None = None


class StandardSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid4()))
    instrument_id: str
    symbol: str
    asset_class: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    market_data_asof: datetime
    provider: str
    strategy_id: str
    strategy_version: str
    bot_id: str
    model_version: str | None = None
    execution_timeframe: str
    context_timeframes: list[str] = Field(default_factory=list)
    state: SignalState
    direction: str
    entry: float | None = None
    entry_zone: tuple[float, float] | None = None
    stop_loss: float | None = None
    structural_invalidation: str | float | None = None
    take_profits: list[float] = Field(default_factory=list)
    profit_plan: str | None = None
    maximum_loss: float | None = None
    position_size: float | None = None
    risk_reward: float | None = None
    expires_at: datetime | None = None
    raw_model_score: float | None = None
    calibrated_confidence: float | None = Field(default=None, ge=0, le=1)
    confidence_label: str = "UNVERIFIED_SCORE"
    supervisor_decision: str
    risk_decision: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    no_trade_conditions: list[str] = Field(default_factory=list)
    eligibility: str = "RESEARCH_ONLY"

    @model_validator(mode="after")
    def executable_plan_is_complete(self):
        actionable = self.state in {SignalState.LONG_CONFIRMED, SignalState.SHORT_CONFIRMED}
        if actionable and self.eligibility in {"PAPER_ELIGIBLE", "SHADOW_ELIGIBLE", "LIVE_ELIGIBLE"}:
            missing = [name for name, value in {
                "entry": self.entry, "stop_loss": self.stop_loss,
                "structural_invalidation": self.structural_invalidation,
                "profit_plan": self.profit_plan, "maximum_loss": self.maximum_loss,
                "position_size": self.position_size,
            }.items() if value is None or value == ""]
            if missing:
                raise ValueError("Executable signal is missing: " + ", ".join(missing))
            if self.risk_decision != "APPROVE":
                raise ValueError("Executable signal requires deterministic risk approval")
        return self

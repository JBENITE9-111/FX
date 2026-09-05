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
    historical_win_probability: float | None = Field(default=None, ge=0, le=1)
    historical_avg_win_r: float | None = None
    historical_avg_loss_r: float | None = None
    expectancy_r: float | None = None
    evidence_ids: list[str]
    assumptions: list[str] = []


class RiskSizedProposal(BaseModel):
    instrument: str
    side: str
    setup: SetupType
    evidence: TraderBrainEvidence
    allowed_account_risk: float
    proposed_quantity: float
    risk_decision_id: str
    eligibility: str  # NO_TRADE / RESEARCH_ONLY / PAPER_ELIGIBLE / LIVE_PROPOSAL_ALLOWED

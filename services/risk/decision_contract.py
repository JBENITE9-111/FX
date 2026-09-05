from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DecisionContext(BaseModel):
    regime: str | None = None
    macro_score: float | None = None
    in_play_score: float | None = None
    structure_score: float | None = None
    location_score: float | None = None
    volume_score: float | None = None
    volatility_score: float | None = None
    order_flow_score: float | None = None
    fundamental_score: float | None = None
    relative_strength_score: float | None = None
    event_risk: str | None = None
    system_health: str | None = None


class PredictionDistribution(BaseModel):
    p05_return: float | None = None
    p25_return: float | None = None
    median_return: float | None = None
    p75_return: float | None = None
    p95_return: float | None = None
    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    calibration_bucket: str | None = None


class HistoricalEvidence(BaseModel):
    sample_size: int | None = None
    win_rate: float | None = None
    avg_win_r: float | None = None
    avg_loss_r: float | None = None
    expectancy_r: float | None = None
    profit_factor: float | None = None
    confidence_interval: Any = None


class CounterThesis(BaseModel):
    score: float | None = None
    fatal_objection: str | None = None
    objections: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class TradePlan(BaseModel):
    entry: float | None = None
    stop: float | None = None
    structural_invalidation: float | None = None
    volatility_buffer: float | None = None
    target_1: float | None = None
    target_2: float | None = None
    expected_r: float | None = None
    time_stop: str | None = None


class CostEstimate(BaseModel):
    fees: float | None = None
    spread: float | None = None
    expected_slippage: float | None = None
    funding: float | None = None
    borrow: float | None = None
    market_impact: float | None = None
    total_expected_cost: float | None = None


class PortfolioImpact(BaseModel):
    existing_exposure: Any = None
    correlated_exposure: Any = None
    post_trade_exposure: Any = None
    factor_exposure: Any = None
    venue_exposure: Any = None


class RiskDecision(BaseModel):
    requested_risk: float | None = None
    approved_risk: float | None = None
    position_size: float | None = None
    risk_engine_status: str
    veto_reason: str | None = None
    probability_of_ruin: float | None = None


class ExecutionPlan(BaseModel):
    venue: str | None = None
    order_type: str | None = None
    max_slippage: float | None = None
    max_participation: float | None = None
    expected_fill: float | None = None
    status: str


class Provenance(BaseModel):
    strategy_version: str | None = None
    model_versions: dict[str, str] = Field(default_factory=dict)
    feature_version: str | None = None
    risk_policy_version: str | None = None
    dataset_version: str | None = None
    dataset_hash: str | None = None
    code_commit: str | None = None
    configuration_hash: str | None = None
    campaign_id: str | None = None
    holdout_hash: str | None = None
    approval_hash: str | None = None
    order_hash: str | None = None


class FXDecision(BaseModel):
    instrument: str
    asset_class: str
    timestamp: str
    direction: str
    action: str
    eligibility: str
    strategy_id: str | None = None
    strategy_version: str | None = None

    context: DecisionContext
    prediction: PredictionDistribution
    historical_evidence: HistoricalEvidence
    counter_thesis: CounterThesis
    trade: TradePlan
    costs: CostEstimate
    portfolio: PortfolioImpact
    risk: RiskDecision
    execution: ExecutionPlan
    provenance: Provenance

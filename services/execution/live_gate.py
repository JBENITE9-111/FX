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

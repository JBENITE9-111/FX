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

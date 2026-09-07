from __future__ import annotations

import os
from typing import Any


PLAN_VERSION = "paper-protection-v2"


def modeled_cost_bps(asset_class: str) -> float:
    key = f"FX_PAPER_COST_BPS_{asset_class.upper().replace(' ', '_')}"
    return max(0.0, float(os.getenv(key, os.getenv("FX_PAPER_MODELED_COST_BPS", "10"))))


def build_plan_options(
    *,
    instrument: str,
    asset_class: str,
    direction: str,
    entry: float,
    stop: float,
    atr_14: float,
    notional: float,
    timeframe: str,
    market_data_timestamp: str,
    strategy_id: str,
    bot_id: str,
    risk_capacity: dict[str, float],
) -> dict[str, Any]:
    if not str(market_data_timestamp).strip() or str(market_data_timestamp).upper() == "UNKNOWN":
        raise ValueError("A verified market-data timestamp is required for a protection plan.")
    side = direction.upper()
    sign = 1 if side == "BUY" else -1
    price_risk = abs(entry - stop)
    if price_risk <= 0 or (sign == 1 and stop >= entry) or (sign == -1 and stop <= entry):
        raise ValueError("The structural stop is invalid for this direction.")
    quantity = notional / entry
    loss_at_stop = quantity * price_risk
    cost_bps = modeled_cost_bps(asset_class)
    modeled_cost = notional * cost_bps / 10_000
    loss_envelope = loss_at_stop + modeled_cost
    effective_cap = max(0.0, float(risk_capacity["effective_new_trade_risk_cap"]))
    loss_rate = price_risk / entry + cost_bps / 10_000
    max_notional_by_risk = effective_cap / loss_rate if loss_rate > 0 else 0.0
    max_position = max(0.0, float(os.getenv("FX_LOCAL_PAPER_MAX_POSITION_NOTIONAL", "1000")))
    max_total = max(0.0, float(os.getenv("FX_LOCAL_PAPER_MAX_TOTAL_EXPOSURE", "10000")))
    remaining_exposure = max(0.0, max_total - float(risk_capacity.get("total_exposure", 0.0))) if max_total else max_notional_by_risk
    allowed_notional = min(value for value in (max_notional_by_risk, max_position or max_notional_by_risk, remaining_exposure or 0.0))
    if effective_cap <= 0 or allowed_notional <= 0:
        risk_decision = "BLOCK"
    elif loss_envelope > effective_cap or notional > allowed_notional + 1e-9:
        risk_decision = "REDUCE_SIZE"
    else:
        risk_decision = "PASS"

    target_1 = entry + sign * price_risk
    target_1_5 = entry + sign * 1.5 * price_risk
    target_2 = entry + sign * 2.0 * price_risk
    gross_1r = quantity * price_risk
    fixed_net = quantity * 1.5 * price_risk - modeled_cost
    scale_net = gross_1r * 1.5 - modeled_cost
    context = {
        "instrument": instrument.upper(), "asset_class": asset_class,
        "direction": side, "entry": entry, "structural_stop": stop,
        "notional": notional, "quantity": quantity, "timeframe": timeframe,
        "market_data_timestamp": market_data_timestamp, "strategy_id": strategy_id,
        "bot_id": bot_id, "plan_version": PLAN_VERSION, "atr_14": atr_14,
        "cost_bps": cost_bps, "maximum_loss": loss_envelope,
    }
    plans = [
        {
            **context, "type": "FIXED_1_5R", "label": "Fixed target at 1.5R",
            "targets": [{
                "price": target_1_5, "quantity_fraction": 1.0, "r_multiple": 1.5,
                "move_pct": 1.5 * price_risk / entry * 100,
                "estimated_gross_profit": gross_1r * 1.5,
            }],
            "gross_target_profit": gross_1r * 1.5, "estimated_net_profit": fixed_net,
            "net_reward_risk": fixed_net / loss_envelope if loss_envelope else None,
            "management": "Keep the original structural stop; exit the full position at 1.5R.",
            "best_suited_to": "Bounded directional moves where taking a defined full exit is preferred.",
            "tradeoff": "The full exit does not participate if the trend extends beyond 1.5R.",
        },
        {
            **context, "type": "SCALE_1R_2R", "label": "Scale at 1R and 2R",
            "targets": [
                {
                    "price": target_1, "quantity_fraction": 0.5, "r_multiple": 1.0,
                    "move_pct": price_risk / entry * 100,
                    "estimated_gross_profit": gross_1r * 0.5,
                },
                {
                    "price": target_2, "quantity_fraction": 0.5, "r_multiple": 2.0,
                    "move_pct": 2.0 * price_risk / entry * 100,
                    "estimated_gross_profit": gross_1r,
                },
            ],
            "gross_target_profit": gross_1r * 1.5, "estimated_net_profit": scale_net,
            "net_reward_risk": scale_net / loss_envelope if loss_envelope else None,
            "management": "Close half at 1R, move the remainder to cost-adjusted breakeven, then exit at 2R.",
            "best_suited_to": "Moves with favorable early momentum but uncertain continuation.",
            "tradeoff": "Taking partial profit reduces participation in a larger move.",
        },
        {
            **context, "type": "TRAIL_AFTER_1R", "label": "Trail after 1R",
            "targets": [{
                "price": target_1, "quantity_fraction": 0.0, "r_multiple": 1.0,
                "move_pct": price_risk / entry * 100,
                "estimated_gross_profit": None,
            }],
            "gross_target_profit": None, "estimated_net_profit": None,
            "net_reward_risk": None, "trailing_atr": 1.0,
            "management": "At 1R, move to cost-adjusted breakeven and activate a one-ATR stop that can only tighten.",
            "best_suited_to": "Sustained trends where the final exit should follow price.",
            "tradeoff": "Final profit is unknown and volatility can trigger an early trailing exit.",
        },
    ]
    return {
        "risk": {
            **risk_capacity,
            "entry": entry, "stop": stop, "stop_distance": price_risk,
            "stop_distance_pct": price_risk / entry * 100,
            "stop_distance_atr": price_risk / atr_14 if atr_14 else None,
            "quantity": quantity, "notional": notional,
            "loss_at_stop": loss_at_stop, "modeled_cost_bps": cost_bps,
            "modeled_execution_allowance": modeled_cost,
            "planned_loss_envelope": loss_envelope,
            "planned_loss_equity_pct": loss_envelope / risk_capacity["equity"] * 100 if risk_capacity["equity"] else None,
            "planned_loss_notional_pct": loss_envelope / notional * 100,
            "maximum_notional_by_risk": max(0.0, allowed_notional),
            "decision": risk_decision,
        },
        "plans": plans,
        "warning": (
            "The planned loss assumes the modeled fill. Gaps, unavailable liquidity, and slippage can create a larger loss. "
            "A short position can lose more than the planned amount if price gaps through its stop."
        ),
    }

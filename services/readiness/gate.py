from __future__ import annotations

from backend.app.services.training.trainer import load_registry


def readiness_for(*, bot_id: str, strategy_id: str, strategy_version: str,
                  instrument: str, timeframe: str, confidence: float | None = None) -> dict:
    reasons: list[str] = []
    if confidence is None:
        reasons.append("No independently calibrated trade probability is available.")
    elif confidence < 0.85:
        reasons.append(f"Calibrated trade probability {confidence:.1%} is below 85%.")
    matches = [
        record for record in load_registry().values()
        if record.get("symbol") == instrument and record.get("timeframe") == timeframe
    ]
    passed = [record for record in matches if record.get("status") == "WALK_FORWARD_PASSED"]
    if not passed:
        reasons.append("No model has passed unseen-data and walk-forward checks for these conditions.")
    eligible = not reasons
    return {
        "bot_id": bot_id, "strategy_id": strategy_id, "strategy_version": strategy_version,
        "instrument": instrument, "timeframe": timeframe,
        "status": "PAPER_ELIGIBLE" if eligible else "UNAVAILABLE",
        "eligible": eligible, "calibrated_probability": confidence,
        "required_probability": 0.85, "reasons": reasons,
        "matched_training_records": len(matches), "passed_training_records": len(passed),
    }

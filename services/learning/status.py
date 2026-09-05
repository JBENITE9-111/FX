from __future__ import annotations

from collections import Counter
from typing import Any

from backend.app.services.training.trainer import load_registry
from services.instruments.training_universe import catalog_asset_classes

OOS_AUC_MIN = 0.52
BALANCED_ACCURACY_MIN = 0.52
WALK_FORWARD_AUC_MIN = 0.52
WALK_FORWARD_BALANCED_MIN = 0.52


def _stage(record: dict[str, Any]) -> tuple[str, str, str]:
    """Derive the current gate from recorded metrics under today's policy.

    Stored status strings are historical evidence. Re-evaluating the metrics here
    prevents an earlier, looser threshold from silently remaining qualified.
    """
    test = record.get("test_metrics") or {}
    walk = record.get("walk_forward") or {}
    auc = test.get("auc")
    balanced = test.get("balanced_accuracy")
    walk_auc = walk.get("average_auc")
    walk_balanced = walk.get("average_balanced_accuracy")
    if auc is None or balanced is None:
        return "RUN_FAILED", "Training evidence is incomplete and needs investigation.", "REPAIR_RUN"
    if auc < OOS_AUC_MIN or balanced < BALANCED_ACCURACY_MIN:
        return (
            "VALIDATION_BLOCKED",
            "The brain ran correctly but did not clear the later unseen-data gate. Repeating the same data does not fix this; revise the hypothesis, features, horizon, or market regime.",
            "OOS",
        )
    if walk_auc is None or walk_balanced is None:
        return "RUN_FAILED", "Walk-forward evidence is incomplete and needs investigation.", "REPAIR_RUN"
    if walk_auc < WALK_FORWARD_AUC_MIN or walk_balanced < WALK_FORWARD_BALANCED_MIN:
        return (
            "VALIDATION_BLOCKED",
            "The brain passed one unseen test but its edge was not stable across later time windows. Investigate regimes and feature stability before retraining.",
            "WALK_FORWARD",
        )
    return (
        "EXAMINATION",
        "The brain cleared the initial unseen-data and walk-forward gates. It still needs independent calibration, cost and slippage stress, parameter stability, Monte Carlo, locked holdout, and paper examination.",
        "CALIBRATION_AND_STRESS",
    )


def learning_overview() -> dict[str, Any]:
    registry = load_registry()
    asset_classes = catalog_asset_classes()
    records = []
    latest_keys: set[tuple[str, str, int, str]] = set()
    for key, raw in sorted(registry.items(), key=lambda item: item[1].get("trained_at", ""), reverse=True):
        record = dict(raw)
        stage, explanation, blocked_at = _stage(record)
        test = record.get("test_metrics") or {}
        walk = record.get("walk_forward") or {}
        version_key = (
            str(record.get("symbol") or ""),
            str(record.get("timeframe") or ""),
            int(record.get("horizon") or 0),
            str(record.get("model") or ""),
        )
        is_current = version_key not in latest_keys
        latest_keys.add(version_key)
        records.append({
            "record_id": key, "model": record.get("model"),
            "instrument": record.get("symbol"), "timeframe": record.get("timeframe"),
            "asset_class": asset_classes.get(record.get("symbol"), "Other research"),
            "horizon": record.get("horizon"), "stage": stage, "eligible": False,
            "explanation": explanation, "trained_at": record.get("trained_at"),
            "training_observations": record.get("training_observations"),
            "test_observations": record.get("test_observations"),
            "unseen_accuracy": test.get("accuracy"), "unseen_auc": test.get("auc"),
            "unseen_balanced_accuracy": test.get("balanced_accuracy"),
            "walk_forward_auc": walk.get("average_auc"),
            "walk_forward_balanced_accuracy": walk.get("average_balanced_accuracy"),
            "calibrated_probability_available": False,
            "blocked_at": blocked_at,
            "is_current": is_current,
        })
    current_records = [item for item in records if item["is_current"]]
    counts = Counter(item["stage"] for item in current_records)
    gate_counts = Counter(item["blocked_at"] for item in current_records)
    candidates = sorted(
        (item for item in current_records if item["stage"] == "EXAMINATION"),
        key=lambda item: min(
            float(item["unseen_auc"] or 0),
            float(item["unseen_balanced_accuracy"] or 0),
            float(item["walk_forward_auc"] or 0),
            float(item["walk_forward_balanced_accuracy"] or 0),
        ),
        reverse=True,
    )
    working = counts["VALIDATION_BLOCKED"] + counts["EXAMINATION"]
    return {
        "summary": {"total_runs": len(records), "current_models": len(current_records),
                    "historical_runs": len(records) - len(current_records), "training": counts["TRAINING"],
                    "working_brains": working, "completed_safely": working,
                    "qualification_blocked": working,
                    "validation_blocked": counts["VALIDATION_BLOCKED"],
                    "oos_blocked": gate_counts["OOS"],
                    "walk_forward_blocked": gate_counts["WALK_FORWARD"],
                    "run_failed": counts["RUN_FAILED"],
                    "rejected": counts["VALIDATION_BLOCKED"] + counts["RUN_FAILED"],
                    "examining": counts["EXAMINATION"],
                    "paper_eligible": 0, "required_trade_probability": 0.85},
        "records": records,
        "qualification": {
            "candidates": candidates,
            "calibration_pipeline_available": False,
            "next_required_gates": [
                "independent probability calibration",
                "cost and slippage stress",
                "parameter stability",
                "Monte Carlo resampling",
                "locked holdout",
                "independent replay",
                "protected paper examination",
            ],
        },
        "policy": "Bots learn in research. Only immutable versions that pass every gate may enter paper campaigns.",
    }

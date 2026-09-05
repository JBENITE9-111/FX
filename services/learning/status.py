from __future__ import annotations

from collections import Counter
from typing import Any

from backend.app.services.training.trainer import load_registry
from services.instruments.training_universe import catalog_asset_classes


def _stage(record: dict[str, Any]) -> tuple[str, str]:
    status = str(record.get("status") or "UNKNOWN")
    if status == "WALK_FORWARD_PASSED":
        return "EXAMINATION", "Passed current walk-forward checks; calibration and remaining promotion gates still apply."
    if "OOS FAILED" in status:
        return (
            "RESEARCH_COMPLETE",
            "The brain trained and ran correctly. Trading qualification remains blocked because it did not prove an edge on later unseen data.",
        )
    if "FAILED" in status:
        return "RUN_FAILED", "The training or validation process failed and needs investigation."
    return "TRAINING", "Evidence is incomplete; this model cannot produce actionable entries."


def learning_overview() -> dict[str, Any]:
    registry = load_registry()
    asset_classes = catalog_asset_classes()
    records = []
    for key, raw in sorted(registry.items(), key=lambda item: item[1].get("trained_at", ""), reverse=True):
        record = dict(raw)
        stage, explanation = _stage(record)
        test = record.get("test_metrics") or {}
        walk = record.get("walk_forward") or {}
        records.append({
            "record_id": key, "model": record.get("model"),
            "instrument": record.get("symbol"), "timeframe": record.get("timeframe"),
            "asset_class": asset_classes.get(record.get("symbol"), "Other research"),
            "horizon": record.get("horizon"), "stage": stage, "eligible": False,
            "explanation": explanation, "trained_at": record.get("trained_at"),
            "training_observations": record.get("training_observations"),
            "test_observations": record.get("test_observations"),
            "unseen_accuracy": test.get("accuracy"), "unseen_auc": test.get("auc"),
            "walk_forward_auc": walk.get("average_auc"),
            "calibrated_probability_available": False,
        })
    counts = Counter(item["stage"] for item in records)
    return {
        "summary": {"total_runs": len(records), "training": counts["TRAINING"],
                    "completed_safely": counts["RESEARCH_COMPLETE"] + counts["EXAMINATION"],
                    "qualification_blocked": counts["RESEARCH_COMPLETE"] + counts["EXAMINATION"],
                    "run_failed": counts["RUN_FAILED"],
                    "rejected": counts["RESEARCH_COMPLETE"] + counts["RUN_FAILED"],
                    "examining": counts["EXAMINATION"],
                    "paper_eligible": 0, "required_trade_probability": 0.85},
        "records": records,
        "policy": "Bots learn in research. Only immutable versions that pass every gate may enter paper campaigns.",
    }

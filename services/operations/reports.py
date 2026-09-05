from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from backend.app.services.bots.registry import BOTS
from backend.app.services.strategies.catalog import STRATEGIES
from services.bot_signals.store import get_signal, list_signals
from services.learning.status import learning_overview
from services.local_paper.broker import get_account, positions
from services.operations.store import get_favorite, save_report


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def _find(items: list[dict], subject_id: str) -> dict | None:
    needle = subject_id.casefold()
    return next((item for item in items if str(item.get("id", "")).casefold() == needle
                 or str(item.get("name", "")).casefold() == needle), None)


def generate_report(report_type: str, subject_id: str, *, goal: dict | None = None) -> dict:
    kind = report_type.strip().lower()
    now = time.time()
    evidence_ids: list[str] = []
    status = "RESEARCH_ONLY"
    missing: list[str] = []

    if kind == "bot":
        source = _find(BOTS, subject_id)
        if not source:
            raise KeyError("Unknown bot identity")
        related = [item for item in list_signals(limit=500) if item["bot_id"] == source["id"]]
        evidence_ids = [item["signal_id"] for item in related[:50]]
        body = {
            "identity": source,
            "purpose": source.get("strategy"),
            "assets": source.get("markets"),
            "timeframes": source.get("timeframe"),
            "current_status": source.get("status"),
            "latest_signals": related[:10],
            "risk_rules": ["deterministic veto", "stop and structural invalidation required", "profit plan required", "paper only"],
            "training_definition": "Chronological training followed by unseen and walk-forward evaluation.",
            "limitations": [source.get("availability_reason")],
            "promotion_status": source.get("status"),
            "next_experiment": "Collect a larger locked sample and test after costs without changing the holdout.",
        }
        missing = ["calibrated confidence", "sufficient paper outcomes"]
        title = f"Bot Report · {source['name']}"
    elif kind == "strategy":
        source = _find(STRATEGIES, subject_id)
        if not source:
            raise KeyError("Unknown strategy identity")
        body = {
            "identity": source,
            "thesis": source.get("plain_english"),
            "required_data": source.get("required_data", []),
            "lifecycle_status": source.get("status"),
            "required_trade_contract": ["entry", "structural invalidation", "stop loss", "profit plan", "maximum loss", "position size"],
            "validation_required": ["chronological OOS", "walk-forward", "cost stress", "Monte Carlo", "locked holdout", "paper evidence"],
        }
        missing = ["versioned formal rule specification", "qualified OOS evidence", "paper outcome sample"]
        title = f"Strategy Report · {source['name']}"
    elif kind == "signal":
        source = get_signal(subject_id)
        if not source:
            raise KeyError("Unknown signal identity")
        evidence_ids = [source["signal_id"]]
        status = source.get("eligibility", "RESEARCH_ONLY")
        body = {
            "signal": source,
            "strongest_case": source.get("reason") or "No explanatory evidence recorded.",
            "dissent": (source.get("metadata") or {}).get("dissent", []),
            "risk_verdict": source.get("risk_status"),
            "next_condition": (source.get("metadata") or {}).get("invalidation") or "No deterministic invalidation text recorded.",
        }
        for field in ("entry", "stop", "target_1", "expected_r"):
            if source.get(field) is None:
                missing.append(field)
        title = f"Signal Report · {source['instrument']}"
    elif kind == "favorite":
        source = get_favorite(subject_id)
        if not source:
            raise KeyError("Unknown favorite identity")
        signals = [item for item in list_signals(limit=500) if item["instrument"] == source["symbol"]]
        evidence_ids = [item["signal_id"] for item in signals[:50]]
        body = {"favorite": source, "latest_signals": signals[:10],
                "decision": signals[0]["direction"] if signals else "NO_SETUP",
                "qualification": "A favorite schedules research; it does not authorize a trade."}
        if not signals:
            missing.append("completed signal evidence")
        title = f"Market Report · {source['symbol']}"
    elif kind == "goal":
        if not goal:
            raise ValueError("A goal plan requires structured goal fields")
        body = {
            "goal": str(goal.get("goal") or subject_id),
            "success_metrics": goal.get("success_metrics") or [],
            "baseline": goal.get("baseline") or "UNKNOWN",
            "hypothesis": goal.get("hypothesis") or "Not supplied",
            "experiment_plan": goal.get("experiment_plan") or [],
            "data_needed": goal.get("data_needed") or [],
            "participants": goal.get("participants") or [],
            "risk_constraints": goal.get("risk_constraints") or ["paper only", "deterministic risk veto"],
            "validation_method": goal.get("validation_method") or "chronological OOS and walk-forward",
            "pass_threshold": goal.get("pass_threshold") or "Must be specified before the experiment",
            "progress": goal.get("progress") or "NOT_STARTED",
            "next_action": goal.get("next_action") or "Specify the baseline and pass threshold",
            "stop_conditions": goal.get("stop_conditions") or ["data leakage", "risk policy violation"],
        }
        title = f"Goal Plan · {body['goal']}"
    elif kind == "system":
        source = {"learning": learning_overview(), "account": get_account(), "open_positions": positions()}
        body = source
        title = "FX System Evidence Report"
    else:
        raise ValueError("report_type must be bot, strategy, signal, favorite, goal, or system")

    body["missing_data"] = [item for item in missing if item]
    body["paper_only"] = True
    body["generated_at"] = now
    provenance = {"application": "FX", "report_generator": "deterministic-v1",
                  "generated_at": now, "market_values_invented": False}
    input_hash = _fingerprint({"type": kind, "subject": subject_id, "body": body})
    return save_report(report_type=kind, subject_id=subject_id, title=title, status=status,
                       body=body, evidence_ids=evidence_ids, provenance=provenance,
                       input_hash=input_hash)


def render_markdown(report: dict) -> str:
    body = report.get("body", {})
    lines = [f"# {report['title']}", "", f"Status: **{report['status']}**", "",
             "Research and local paper trading only.", ""]
    for key, value in body.items():
        lines.extend([f"## {key.replace('_', ' ').title()}", "",
                      json.dumps(value, indent=2, default=str) if isinstance(value, (dict, list)) else str(value), ""])
    return "\n".join(lines)

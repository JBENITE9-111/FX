from __future__ import annotations

import json
import math
from typing import Any

import numpy as np
import pandas as pd

from backend.app.services.strategies.backtester import build_positions
from services.market_memory.schema import (
    STRATEGY_EXAM_VERSION,
    git_commit,
    stable_id,
    utc_now,
)
from services.market_memory.store import MarketMemoryStore


def _metrics(
    returns: pd.Series,
    positions: pd.Series,
    turnover: pd.Series,
    annualization: int,
) -> dict[str, Any]:
    clean = returns.fillna(0.0).astype(float)
    equity = (1 + clean).cumprod()
    drawdown = equity / equity.cummax() - 1
    deviation = clean.std()
    downside = clean[clean < 0].std()
    gains = float(clean[clean > 0].sum())
    losses = abs(float(clean[clean < 0].sum()))
    active = clean[positions != 0]
    winning = active[active > 0]
    losing = active[active < 0]
    total_return = float(equity.iloc[-1] - 1) if len(equity) else None
    years = len(clean) / annualization if annualization else 0
    cagr = (
        float(equity.iloc[-1] ** (1 / years) - 1)
        if years > 0 and len(equity) and equity.iloc[-1] > 0
        else None
    )
    max_drawdown = float(drawdown.min()) if len(drawdown) else None
    annualized_volatility = (
        float(deviation * math.sqrt(annualization))
        if deviation and not np.isnan(deviation)
        else None
    )
    average_win = float(winning.mean()) if len(winning) else None
    average_loss = abs(float(losing.mean())) if len(losing) else None
    return {
        "observations": len(clean),
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "calmar": cagr / abs(max_drawdown) if cagr is not None and max_drawdown else None,
        "sharpe": float(clean.mean() / deviation * math.sqrt(annualization)) if deviation and not np.isnan(deviation) else None,
        "sortino": float(clean.mean() / downside * math.sqrt(annualization)) if downside and not np.isnan(downside) else None,
        "annualized_volatility": annualized_volatility,
        "tail_loss_5pct": float(clean.quantile(0.05)) if len(clean) else None,
        "profit_factor": gains / losses if losses else None,
        "expectancy_per_active_bar": float(active.mean()) if len(active) else None,
        "active_bar_win_rate": float((active > 0).mean()) if len(active) else None,
        "average_win": average_win,
        "average_loss": average_loss,
        "payoff_ratio": average_win / average_loss if average_win is not None and average_loss else None,
        "trades": int((turnover > 0).sum()),
        "turnover": float(turnover.sum()),
        "exposure": float((positions != 0).mean()),
    }


def examine_strategy(
    *,
    store: MarketMemoryStore,
    artifact_id: str,
    strategy_id: str,
    strategy_version: str = "1",
    cost_bps: tuple[float, ...] = (5.0, 10.0, 20.0),
) -> dict[str, Any]:
    frame, artifact = store.load_artifact(artifact_id)
    if artifact["timeframe"] != "1d":
        raise ValueError("The first strategy-exam version supports daily bars only.")
    if len(frame) < 300:
        raise ValueError("At least 300 daily bars are required for a chronological strategy exam.")

    annualization = 365 if artifact["asset_class"].lower() == "crypto" else 252

    positions = build_positions(strategy_id, frame).shift(1).fillna(0.0)
    market_returns = frame["close"].astype(float).pct_change().fillna(0.0)
    turnover = positions.diff().abs().fillna(positions.abs())
    first_end = int(len(frame) * 0.60)
    second_end = int(len(frame) * 0.80)
    slices = {
        "development": slice(0, first_end),
        "validation": slice(first_end, second_end),
        "locked_test": slice(second_end, len(frame)),
    }
    stress: dict[str, Any] = {}
    for basis_points in cost_bps:
        strategy_returns = positions * market_returns - turnover * (basis_points / 10_000)
        stress[str(basis_points)] = {
            name: _metrics(
                strategy_returns.iloc[part], positions.iloc[part],
                turnover.iloc[part], annualization,
            )
            for name, part in slices.items()
        }

    input_manifest = {
        "artifact_id": artifact_id,
        "strategy_id": strategy_id,
        "strategy_version": strategy_version,
        "exam_version": STRATEGY_EXAM_VERSION,
        "cost_bps": list(cost_bps),
        "split": {"development": 0.60, "validation": 0.20, "locked_test": 0.20},
        "signal_execution": "one_bar_lag",
        "annualization": annualization,
    }
    input_hash = stable_id("input", input_manifest)
    experiment_id = stable_id("experiment", input_manifest)
    path = store.root / "experiments" / f"{experiment_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    result = {
        "experiment_id": experiment_id,
        **input_manifest,
        "input_hash": input_hash,
        "symbol": artifact["symbol"],
        "asset_class": artifact["asset_class"],
        "coverage_start": artifact["coverage_start"],
        "coverage_end": artifact["coverage_end"],
        "rows": artifact["rows"],
        "cost_stress": stress,
        "status": "RESEARCH_ONLY",
        "eligibility": "NOT_ELIGIBLE",
        "data_quality_status": artifact["quality"]["status"],
        "current_research_position": int(build_positions(strategy_id, frame).iloc[-1]),
        "required_before_paper": [
            "parameter stability", "Monte Carlo", "multiple-testing adjustment",
            "independent replay", "protected paper examination", "portfolio risk review",
        ],
        "limitations": [
            "Daily close-to-close bar model; stops, targets, intrabar fills and market impact are not simulated.",
            "This exam cannot authorize a paper or live order.",
        ],
        "git_commit": git_commit(store.project_root),
        "created_at": utc_now(),
        "research_only": True,
    }
    if artifact["quality"]["status"] != "PASS":
        result["status"] = "BLOCKED_DATA_QUALITY"
        result["current_research_position"] = 0
        result["limitations"].insert(
            0,
            "Strategy evidence is blocked until the historical data quality review is resolved.",
        )
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    store._write_immutable(path, payload)
    store.registry.insert_experiment({
        "experiment_id": experiment_id,
        "artifact_id": artifact_id,
        "strategy_id": strategy_id,
        "strategy_version": strategy_version,
        "manifest_path": store._relative(path, store.project_root),
        "input_hash": input_hash,
        "status": "RESEARCH_ONLY",
        "created_at": result["created_at"],
    })
    return result

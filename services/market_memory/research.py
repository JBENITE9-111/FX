from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from services.market_memory.schema import ANALOGUE_SCHEMA_VERSION, FEATURE_SCHEMA_VERSION


FEATURE_COLUMNS = ["return_5", "return_20", "volatility_20", "atr_percent", "trend_gap"]


def build_market_states(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.sort_values("timestamp", kind="stable").reset_index(drop=True).copy()
    close = data["close"].astype(float)
    previous = close.shift(1)
    true_range = pd.concat([
        data["high"] - data["low"],
        (data["high"] - previous).abs(),
        (data["low"] - previous).abs(),
    ], axis=1).max(axis=1)
    returns = close.pct_change()
    data["return_5"] = close.pct_change(5)
    data["return_20"] = close.pct_change(20)
    data["volatility_20"] = returns.rolling(20).std() * math.sqrt(252)
    data["atr_percent"] = true_range.ewm(alpha=1 / 14, adjust=False).mean() / close
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    data["trend_gap"] = ema20 / ema50 - 1

    past_vol = data["volatility_20"].expanding(min_periods=60)
    high_threshold = past_vol.quantile(0.75).shift(1)
    low_threshold = past_vol.quantile(0.25).shift(1)
    direction = np.where(data["trend_gap"] > 0.005, "UP", np.where(data["trend_gap"] < -0.005, "DOWN", "RANGE"))
    volatility = np.where(
        data["volatility_20"] > high_threshold,
        "HIGH_VOL",
        np.where(data["volatility_20"] < low_threshold, "LOW_VOL", "NORMAL_VOL"),
    )
    ready = data[FEATURE_COLUMNS].notna().all(axis=1) & high_threshold.notna()
    data["regime"] = np.where(ready, np.char.add(np.char.add(direction, "_"), volatility), "INSUFFICIENT_HISTORY")
    data.attrs["feature_schema_version"] = FEATURE_SCHEMA_VERSION
    data.attrs["point_in_time"] = True
    return data


def historical_analogues(
    frame: pd.DataFrame,
    *,
    artifact_id: str,
    forward_periods: int = 5,
    top_k: int = 10,
    exclusion_periods: int = 20,
) -> dict[str, Any]:
    if forward_periods < 1 or top_k < 1:
        raise ValueError("forward_periods and top_k must be positive.")
    states = build_market_states(frame)
    usable = states.dropna(subset=FEATURE_COLUMNS).copy()
    if len(usable) < 100 + forward_periods + exclusion_periods:
        return {
            "available": False,
            "reason": "INSUFFICIENT_HISTORY",
            "observations": len(usable),
            "matches": [],
            "artifact_id": artifact_id,
            "analogue_schema_version": ANALOGUE_SCHEMA_VERSION,
        }

    current_index = usable.index[-1]
    current = states.loc[current_index]
    maximum_candidate_index = current_index - forward_periods - exclusion_periods
    candidates = states.loc[:maximum_candidate_index].dropna(subset=FEATURE_COLUMNS).copy()
    if candidates.empty:
        return {"available": False, "reason": "NO_NON_OVERLAPPING_CANDIDATES", "matches": []}

    candidate_features = candidates[FEATURE_COLUMNS].astype(float)
    current_features = current[FEATURE_COLUMNS].astype(float)
    means = candidate_features.mean()
    scales = candidate_features.std().replace(0, 1.0)
    standardized = (candidate_features - means) / scales
    current_vector = (current_features - means) / scales
    candidates["distance"] = np.sqrt(((standardized - current_vector) ** 2).mean(axis=1))
    candidates["forward_return"] = (
        states["close"].shift(-forward_periods) / states["close"] - 1
    ).reindex(candidates.index)
    matches = candidates.dropna(subset=["forward_return"]).nsmallest(top_k, "distance")
    outcomes = matches["forward_return"].astype(float)
    rendered = [{
        "timestamp": row["timestamp"].isoformat(),
        "regime": row["regime"],
        "distance": float(row["distance"]),
        "forward_return": float(row["forward_return"]),
    } for _, row in matches.iterrows()]
    return {
        "available": bool(rendered),
        "artifact_id": artifact_id,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "analogue_schema_version": ANALOGUE_SCHEMA_VERSION,
        "current_timestamp": current["timestamp"].isoformat(),
        "current_regime": current["regime"],
        "forward_periods": forward_periods,
        "candidate_observations": len(candidates),
        "sample_size": len(outcomes),
        "positive_rate": float((outcomes > 0).mean()) if len(outcomes) else None,
        "mean_forward_return": float(outcomes.mean()) if len(outcomes) else None,
        "median_forward_return": float(outcomes.median()) if len(outcomes) else None,
        "standard_deviation": float(outcomes.std(ddof=1)) if len(outcomes) > 1 else None,
        "worst_forward_return": float(outcomes.min()) if len(outcomes) else None,
        "best_forward_return": float(outcomes.max()) if len(outcomes) else None,
        "matches": rendered,
        "limitations": [
            "Historical analogues are evidence, not a forecast or trade instruction.",
            "Similarity uses daily bar features and does not model news, liquidity, spread, or execution.",
        ],
    }

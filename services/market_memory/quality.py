from __future__ import annotations

from typing import Any

import pandas as pd


class HistoricalDataQualityError(ValueError):
    pass


def normalize_and_validate_bars(
    rows: list[dict[str, Any]],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not rows:
        raise HistoricalDataQualityError("No historical rows were supplied.")

    frame = pd.DataFrame(rows).copy()
    aliases = {"t": "timestamp", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
    for old, new in aliases.items():
        if old in frame.columns and new not in frame.columns:
            frame[new] = frame[old]

    required = ["timestamp", "open", "high", "low", "close"]
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise HistoricalDataQualityError(
            "Required historical fields are missing: " + ", ".join(missing)
        )

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    for name in ["open", "high", "low", "close", "volume"]:
        if name not in frame.columns:
            frame[name] = pd.NA
        frame[name] = pd.to_numeric(frame[name], errors="coerce")

    null_counts = {name: int(frame[name].isna().sum()) for name in required}
    if any(null_counts.values()):
        raise HistoricalDataQualityError(
            f"Historical rows contain null or invalid required values: {null_counts}"
        )

    duplicate_timestamps = int(frame["timestamp"].duplicated(keep=False).sum())
    if duplicate_timestamps:
        raise HistoricalDataQualityError(
            f"Historical rows contain {duplicate_timestamps} duplicate timestamps."
        )

    numeric = frame[["open", "high", "low", "close"]]
    nonpositive = int((numeric <= 0).any(axis=1).sum())
    invalid_high = int(
        (frame["high"] < frame[["open", "low", "close"]].max(axis=1)).sum()
    )
    invalid_low = int(
        (frame["low"] > frame[["open", "high", "close"]].min(axis=1)).sum()
    )
    if nonpositive or invalid_high or invalid_low:
        raise HistoricalDataQualityError(
            "Invalid OHLC rows: "
            f"nonpositive={nonpositive}, invalid_high={invalid_high}, invalid_low={invalid_low}."
        )

    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    close_returns = frame["close"].pct_change()
    suspicious_return_rows = int((close_returns.abs() > 0.50).sum())
    status = "REVIEW_REQUIRED" if suspicious_return_rows else "PASS"
    quality_score = 0.75 if suspicious_return_rows else 1.0
    ordered = ["timestamp", "open", "high", "low", "close", "volume"]
    extras = sorted(name for name in frame.columns if name not in ordered)
    frame = frame[ordered + extras]

    report = {
        "status": status,
        "quality_score": quality_score,
        "rows": len(frame),
        "coverage_start": frame["timestamp"].iloc[0].isoformat(),
        "coverage_end": frame["timestamp"].iloc[-1].isoformat(),
        "duplicate_timestamps": 0,
        "invalid_ohlc_rows": 0,
        "suspicious_return_rows": suspicious_return_rows,
        "required_null_counts": null_counts,
        "timezone": "UTC",
        "ordering": "ascending",
        "limitations": [
            "Bar validation does not prove venue completeness or survivorship safety.",
            "Corporate-action adjustment must be declared by the provider/dataset metadata.",
            "Absolute close-to-close moves above 50% require source or corporate-action review.",
        ],
    }
    return frame, report

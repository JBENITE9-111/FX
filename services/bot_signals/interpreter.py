from __future__ import annotations

from typing import Any


def normalize_candidate(
    *,
    bot_id: str,
    bot_name: str,

    asset_class: str,

    strategy_id: str,

    instrument: str,

    candidate_score: float,

    market: dict[str, Any],

) -> dict:

    score = float(
        candidate_score
    )

    last = float(
        market.get(
            "last_price",
            market.get(
                "price",
                0,
            ),
        )
        or 0
    )

    atr = float(
        market.get(
            "atr",
            market.get(
                "atr14",
                0,
            ),
        )
        or 0
    )

    trend = str(
        market.get(
            "trend",
            "neutral",
        )
    ).lower()

    momentum = float(
        market.get(
            "momentum",
            market.get(
                "return_20",
                0,
            ),
        )
        or 0
    )

    if (
        score < 60
        or last <= 0
    ):
        direction = "NO_TRADE"

    elif (
        trend
        in (
            "up",
            "bullish",
            "positive",
        )
        or momentum > 0
    ):
        direction = "LONG"

    elif (
        trend
        in (
            "down",
            "bearish",
            "negative",
        )
        or momentum < 0
    ):
        direction = "SHORT"

    else:
        direction = (
            "NO_TRADE"
        )

    stop = None
    target_1 = None
    target_2 = None
    expected_r = None

    if (
        direction
        in (
            "LONG",
            "SHORT",
        )
        and atr > 0
    ):

        stop_distance = (
            1.5
            * atr
        )

        if direction == "LONG":

            stop = (
                last
                - stop_distance
            )

            target_1 = (
                last
                + stop_distance
            )

            target_2 = (
                last
                + 2
                * stop_distance
            )

        else:

            stop = (
                last
                + stop_distance
            )

            target_1 = (
                last
                - stop_distance
            )

            target_2 = (
                last
                - 2
                * stop_distance
            )

        expected_r = 2.0

    # Rule agreement is not a calibrated probability.
    confidence = None

    risk_status = (
        "PENDING"
        if direction
        != "NO_TRADE"
        else "NOT_REQUIRED"
    )

    eligibility = (
        "RESEARCH_ONLY"
        if direction
        != "NO_TRADE"
        else "NO_TRADE"
    )

    return {
        "bot_id":
            bot_id,

        "bot_name":
            bot_name,

        "instrument":
            instrument,

        "asset_class":
            asset_class,

        "strategy_id":
            strategy_id,

        "direction":
            direction,

        "score":
            score,

        "entry":
            last
            if last > 0
            else None,

        "stop":
            stop,

        "structural_invalidation": stop,

        "target_1":
            target_1,

        "target_2":
            target_2,

        "profit_plan": "TWO_TARGETS" if target_2 is not None else None,

        "expected_r":
            expected_r,

        "confidence":
            confidence,

        "risk_status":
            risk_status,

        "eligibility":
            eligibility,

        "reason":
            (
                f"Bot candidate score "
                f"{score:.1f}. "
                f"Trend={trend}. "
                f"Momentum={momentum:.4f}. "
                "This rule score is not a calibrated probability."
            ),
    }

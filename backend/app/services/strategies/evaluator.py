from __future__ import annotations

from typing import Any

import pandas as pd

from backend.app.services.models.features import (
    calculate_features,
    rows_to_dataframe,
)
from backend.app.services.models.kalman import (
    kalman_filter,
)


def result(
    name: str,
    view: str,
    explanation: str,
):

    return {
        "strategy": name,
        "view": view,
        "explanation": explanation,
        "status": "RESEARCH ONLY",
    }


def evaluate_strategies(
    rows: list[dict[str, Any]],
):

    features = calculate_features(
        rows
    )

    df = rows_to_dataframe(
        rows
    )

    close = float(
        df["close"].iloc[-1]
    )

    views = []

    ema20 = features[
        "ema20"
    ]

    ema50 = features[
        "ema50"
    ]

    if (
        ema20
        and ema50
    ):

        if (
            close > ema20 > ema50
        ):

            views.append(
                result(
                    "Trend Following",
                    "POSITIVE",
                    (
                        "Price is above both the shorter and longer trend averages."
                    ),
                )
            )

        elif (
            close < ema20 < ema50
        ):

            views.append(
                result(
                    "Trend Following",
                    "NEGATIVE",
                    (
                        "Price is below both the shorter and longer trend averages."
                    ),
                )
            )

        else:

            views.append(
                result(
                    "Trend Following",
                    "NEUTRAL",
                    (
                        "The short and long trend measures are not aligned."
                    ),
                )
            )

    r20 = features[
        "return_20"
    ]

    if r20 is not None:

        if r20 > 0.03:

            view = "POSITIVE"

        elif r20 < -0.03:

            view = "NEGATIVE"

        else:

            view = "NEUTRAL"

        views.append(
            result(
                "Momentum",
                view,
                (
                    f"The market's 20-period change is {r20 * 100:.2f}%."
                ),
            )
        )

    previous_high = features[
        "previous_20_high"
    ]

    previous_low = features[
        "previous_20_low"
    ]

    if (
        previous_high is not None
        and close > previous_high
    ):

        breakout_view = "POSITIVE"

        breakout_text = (
            "Price is above its previous 20-period high."
        )

    elif (
        previous_low is not None
        and close < previous_low
    ):

        breakout_view = "NEGATIVE"

        breakout_text = (
            "Price is below its previous 20-period low."
        )

    else:

        breakout_view = "NEUTRAL"

        breakout_text = (
            "Price remains inside its recent 20-period range."
        )

    views.append(
        result(
            "Breakout",
            breakout_view,
            breakout_text,
        )
    )

    z = features[
        "zscore20"
    ]

    if z is not None:

        if z < -1.5:

            mr_view = "POSITIVE"

        elif z > 1.5:

            mr_view = "NEGATIVE"

        else:

            mr_view = "NEUTRAL"

        views.append(
            result(
                "Mean Reversion",
                mr_view,
                (
                    "The price is "
                    f"{abs(z):.2f} standard deviations "
                    + (
                        "below"
                        if z < 0
                        else "above"
                    )
                    + " its recent average."
                ),
            )
        )

    rsi = features[
        "rsi14"
    ]

    if rsi is not None:

        if rsi < 30:

            rsi_view = "POSITIVE"

        elif rsi > 70:

            rsi_view = "NEGATIVE"

        else:

            rsi_view = "NEUTRAL"

        views.append(
            result(
                "RSI Reversion",
                rsi_view,
                (
                    f"RSI is currently {rsi:.1f}. "
                    "This is only a measure of recent buying and selling pressure."
                ),
            )
        )

    macd = features[
        "macd"
    ]

    macd_signal = features[
        "macd_signal"
    ]

    if (
        macd is not None
        and macd_signal is not None
    ):

        if macd > macd_signal:

            macd_view = "POSITIVE"

        elif macd < macd_signal:

            macd_view = "NEGATIVE"

        else:

            macd_view = "NEUTRAL"

        views.append(
            result(
                "MACD Trend",
                macd_view,
                (
                    "The faster trend is "
                    + (
                        "above"
                        if macd > macd_signal
                        else "below"
                    )
                    + " its slower signal line."
                ),
            )
        )

    filtered = kalman_filter(
        df["close"].tolist()
    )

    if len(filtered) >= 6:

        kalman_change = (
            filtered[-1]
            / filtered[-6]
            - 1
        )

        if kalman_change > 0.002:

            kalman_view = "POSITIVE"

        elif kalman_change < -0.002:

            kalman_view = "NEGATIVE"

        else:

            kalman_view = "NEUTRAL"

        views.append(
            result(
                "Kalman Trend",
                kalman_view,
                (
                    "The noise-filtered trend changed "
                    f"{kalman_change * 100:.2f}% "
                    "over the recent observation window."
                ),
            )
        )

    counts = {
        "POSITIVE": 0,
        "NEGATIVE": 0,
        "NEUTRAL": 0,
    }

    for item in views:

        if item[
            "view"
        ] in counts:

            counts[
                item["view"]
            ] += 1

    return {
        "features": features,
        "strategies": views,
        "agreement": counts,
        "warning": (
            "These are research signals, not validated trading instructions."
        ),
    }

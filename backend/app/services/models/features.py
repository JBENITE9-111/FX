from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def rows_to_dataframe(
    rows: list[dict[str, Any]],
) -> pd.DataFrame:

    df = pd.DataFrame(rows)

    aliases = {
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "v": "volume",
    }

    for old, new in aliases.items():

        if (
            old in df.columns
            and new not in df.columns
        ):
            df[new] = df[old]

    required = [
        "open",
        "high",
        "low",
        "close",
    ]

    for column in required:

        if column not in df.columns:
            raise ValueError(
                f"Required price field is missing: {column}"
            )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    if "volume" in df.columns:

        df["volume"] = pd.to_numeric(
            df["volume"],
            errors="coerce",
        )

    df = df.dropna(
        subset=required
    ).reset_index(drop=True)

    return df


def rsi(
    close: pd.Series,
    period: int = 14,
) -> pd.Series:

    delta = close.diff()

    gain = delta.clip(
        lower=0
    )

    loss = (
        -delta.clip(
            upper=0
        )
    )

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan,
    )

    return 100 - (
        100 / (1 + rs)
    )


def atr(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.Series:

    previous_close = (
        df["close"]
        .shift(1)
    )

    true_range = pd.concat(
        [
            df["high"]
            - df["low"],

            (
                df["high"]
                - previous_close
            ).abs(),

            (
                df["low"]
                - previous_close
            ).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.ewm(
        alpha=1 / period,
        adjust=False,
    ).mean()


def calculate_features(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:

    df = rows_to_dataframe(
        rows
    )

    if len(df) < 55:

        raise ValueError(
            "FX needs more historical information before calculating this market."
        )

    close = df["close"]

    df["ema20"] = close.ewm(
        span=20,
        adjust=False,
    ).mean()

    df["ema50"] = close.ewm(
        span=50,
        adjust=False,
    ).mean()

    df["sma20"] = close.rolling(
        20
    ).mean()

    df["std20"] = close.rolling(
        20
    ).std()

    df["rsi14"] = rsi(
        close
    )

    df["atr14"] = atr(
        df
    )

    df["return_1"] = close.pct_change(
        1
    )

    df["return_5"] = close.pct_change(
        5
    )

    df["return_20"] = close.pct_change(
        20
    )

    df["vol20"] = (
        df["return_1"]
        .rolling(20)
        .std()
        * math.sqrt(252)
    )

    df["high20_previous"] = (
        df["high"]
        .shift(1)
        .rolling(20)
        .max()
    )

    df["low20_previous"] = (
        df["low"]
        .shift(1)
        .rolling(20)
        .min()
    )

    df["zscore20"] = (
        close
        - df["sma20"]
    ) / df["std20"].replace(
        0,
        np.nan,
    )

    ema12 = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    df["macd"] = (
        ema12
        - ema26
    )

    df["macd_signal"] = (
        df["macd"]
        .ewm(
            span=9,
            adjust=False,
        )
        .mean()
    )

    last = df.iloc[-1]

    def safe(
        value,
    ):

        if pd.isna(value):
            return None

        return float(value)

    return {
        "last_price": safe(
            last["close"]
        ),

        "ema20": safe(
            last["ema20"]
        ),

        "ema50": safe(
            last["ema50"]
        ),

        "sma20": safe(
            last["sma20"]
        ),

        "rsi14": safe(
            last["rsi14"]
        ),

        "atr14": safe(
            last["atr14"]
        ),

        "atr_percent": safe(
            last["atr14"]
            / last["close"]
        ),

        "return_1": safe(
            last["return_1"]
        ),

        "return_5": safe(
            last["return_5"]
        ),

        "return_20": safe(
            last["return_20"]
        ),

        "volatility_20": safe(
            last["vol20"]
        ),

        "previous_20_high": safe(
            last[
                "high20_previous"
            ]
        ),

        "previous_20_low": safe(
            last[
                "low20_previous"
            ]
        ),

        "zscore20": safe(
            last["zscore20"]
        ),

        "macd": safe(
            last["macd"]
        ),

        "macd_signal": safe(
            last["macd_signal"]
        ),
    }

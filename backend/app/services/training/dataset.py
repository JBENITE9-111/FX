from __future__ import annotations

import numpy as np
import pandas as pd

from backend.app.services.models.features import (
    atr,
    rows_to_dataframe,
    rsi,
)


FEATURE_COLUMNS = [
    "ret1",
    "ret3",
    "ret5",
    "ret10",
    "ret20",
    "vol5",
    "vol20",
    "ema10_gap",
    "ema20_gap",
    "ema50_gap",
    "rsi14",
    "atr_pct",
    "range_pct",
    "close_location",
    "volume_change",
]


def build_dataset(
    rows,
    horizon: int = 5,
):

    df = rows_to_dataframe(
        rows
    ).copy()

    close = (
        df["close"]
        .astype(float)
    )

    df["ret1"] = (
        close
        .pct_change(1)
    )

    df["ret3"] = (
        close
        .pct_change(3)
    )

    df["ret5"] = (
        close
        .pct_change(5)
    )

    df["ret10"] = (
        close
        .pct_change(10)
    )

    df["ret20"] = (
        close
        .pct_change(20)
    )

    df["vol5"] = (
        df["ret1"]
        .rolling(5)
        .std()
    )

    df["vol20"] = (
        df["ret1"]
        .rolling(20)
        .std()
    )

    ema10 = close.ewm(
        span=10,
        adjust=False,
    ).mean()

    ema20 = close.ewm(
        span=20,
        adjust=False,
    ).mean()

    ema50 = close.ewm(
        span=50,
        adjust=False,
    ).mean()

    df["ema10_gap"] = (
        close / ema10 - 1
    )

    df["ema20_gap"] = (
        close / ema20 - 1
    )

    df["ema50_gap"] = (
        close / ema50 - 1
    )

    df["rsi14"] = (
        rsi(
            close,
            14,
        )
        / 100.0
    )

    atr_value = atr(
        df,
        14,
    )

    df["atr_pct"] = (
        atr_value
        / close
    )

    df["range_pct"] = (
        (
            df["high"]
            - df["low"]
        )
        / close
    )

    range_size = (
        df["high"]
        - df["low"]
    ).replace(
        0,
        np.nan,
    )

    df["close_location"] = (
        (
            close
            - df["low"]
        )
        / range_size
    )

    if "volume" in df.columns:

        volume = (
            df["volume"]
            .astype(float)
        )

        df["volume_change"] = (
            volume
            .pct_change(5)
        )

    else:

        df["volume_change"] = 0.0

    future_return = (
        close
        .shift(
            -horizon
        )
        / close
        - 1
    )

    # We deliberately use a modest threshold rather than labeling
    # every tiny movement as a meaningful direction.
    rolling_noise = (
        df["ret1"]
        .rolling(20)
        .std()
        .fillna(0)
    )

    threshold = (
        rolling_noise
        * np.sqrt(
            max(
                horizon,
                1,
            )
        )
        * 0.20
    )

    df["target"] = (
        future_return
        > threshold
    ).astype(int)

    df["future_return"] = (
        future_return
    )

    dataset = (
        df[
            FEATURE_COLUMNS
            + [
                "target",
                "future_return",
            ]
        ]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
        .reset_index(
            drop=True
        )
    )

    return dataset

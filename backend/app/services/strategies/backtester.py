from __future__ import annotations

import math

import numpy as np
import pandas as pd

from backend.app.services.models.features import (
    rows_to_dataframe,
    rsi,
)
from backend.app.services.models.kalman import (
    kalman_filter,
)


def build_positions(
    strategy_id: str,
    df: pd.DataFrame,
):

    close = df["close"]

    ema20 = close.ewm(
        span=20,
        adjust=False,
    ).mean()

    ema50 = close.ewm(
        span=50,
        adjust=False,
    ).mean()

    position = pd.Series(
        0.0,
        index=df.index,
    )

    if strategy_id == "trend_following":

        position[
            ema20 > ema50
        ] = 1

        position[
            ema20 < ema50
        ] = -1

    elif strategy_id == "momentum":

        momentum = (
            close.pct_change(
                20
            )
        )

        position[
            momentum > 0.03
        ] = 1

        position[
            momentum < -0.03
        ] = -1

    elif strategy_id == "breakout":

        previous_high = (
            df["high"]
            .shift(1)
            .rolling(20)
            .max()
        )

        previous_low = (
            df["low"]
            .shift(1)
            .rolling(20)
            .min()
        )

        position[
            close > previous_high
        ] = 1

        position[
            close < previous_low
        ] = -1

    elif strategy_id in {
        "mean_reversion",
        "bollinger_reversion",
    }:

        mean = close.rolling(
            20
        ).mean()

        std = close.rolling(
            20
        ).std()

        z = (
            close
            - mean
        ) / std.replace(
            0,
            np.nan,
        )

        position[
            z < -1.5
        ] = 1

        position[
            z > 1.5
        ] = -1

    elif strategy_id == "rsi_reversion":

        value = rsi(
            close,
            14,
        )

        position[
            value < 30
        ] = 1

        position[
            value > 70
        ] = -1

    elif strategy_id == "macd_trend":

        fast = close.ewm(
            span=12,
            adjust=False,
        ).mean()

        slow = close.ewm(
            span=26,
            adjust=False,
        ).mean()

        macd = (
            fast
            - slow
        )

        signal = macd.ewm(
            span=9,
            adjust=False,
        ).mean()

        position[
            macd > signal
        ] = 1

        position[
            macd < signal
        ] = -1

    elif strategy_id == "kalman_trend":

        filtered = pd.Series(
            kalman_filter(
                close.tolist()
            ),
            index=df.index,
        )

        slope = filtered.diff(
            5
        )

        position[
            slope > 0
        ] = 1

        position[
            slope < 0
        ] = -1

    elif strategy_id == "volatility_breakout":

        previous_high = (
            df["high"]
            .shift(1)
            .rolling(20)
            .max()
        )

        previous_low = (
            df["low"]
            .shift(1)
            .rolling(20)
            .min()
        )

        daily_range = (
            df["high"]
            - df["low"]
        )

        expanding = (
            daily_range
            > daily_range
            .rolling(20)
            .mean()
        )

        position[
            (
                close
                > previous_high
            )
            & expanding
        ] = 1

        position[
            (
                close
                < previous_low
            )
            & expanding
        ] = -1

    else:

        raise ValueError(
            "This strategy is not yet connected to the automatic backtest engine."
        )

    return position


def backtest(
    strategy_id: str,
    rows,
    fee_bps: float = 2.0,
):

    df = rows_to_dataframe(
        rows
    )

    if len(df) < 100:

        raise ValueError(
            "FX needs more market history before it can backtest this strategy."
        )

    position = build_positions(
        strategy_id,
        df,
    )

    returns = (
        df["close"]
        .pct_change()
        .fillna(0)
    )

    executed_position = (
        position
        .shift(1)
        .fillna(0)
    )

    turnover = (
        executed_position
        .diff()
        .abs()
        .fillna(
            executed_position.abs()
        )
    )

    fees = (
        turnover
        * (
            fee_bps
            / 10000
        )
    )

    strategy_returns = (
        executed_position
        * returns
        - fees
    )

    equity = (
        1
        + strategy_returns
    ).cumprod()

    total_return = (
        equity.iloc[-1]
        - 1
    )

    peak = (
        equity
        .cummax()
    )

    drawdown = (
        equity
        / peak
        - 1
    )

    max_drawdown = (
        drawdown.min()
    )

    active = (
        executed_position
        != 0
    )

    active_returns = (
        strategy_returns[
            active
        ]
    )

    win_rate = (
        float(
            (
                active_returns
                > 0
            ).mean()
        )
        if len(
            active_returns
        )
        else 0
    )

    trades = int(
        (
            turnover
            > 0
        ).sum()
    )

    daily_std = (
        strategy_returns.std()
    )

    sharpe = (
        float(
            strategy_returns.mean()
            / daily_std
            * math.sqrt(
                252
            )
        )
        if (
            daily_std
            and not np.isnan(
                daily_std
            )
        )
        else None
    )

    current_position = int(
        position.iloc[-1]
    )

    return {
        "total_return": float(
            total_return
        ),
        "max_drawdown": float(
            max_drawdown
        ),
        "win_rate": win_rate,
        "trades": trades,
        "sharpe": sharpe,
        "current_position": current_position,
        "fee_assumption_bps": fee_bps,
        "lookahead_protection": (
            "Signals are shifted by one bar before returns are counted."
        ),
        "warning": (
            "A backtest is historical evidence, not proof of future profitability."
        ),
    }

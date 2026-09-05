from __future__ import annotations

import numpy as np
import pandas as pd

from backend.app.services.models.features import (
    rows_to_dataframe,
)


def find_analogues(
    rows,
    window: int = 20,
    forward: int = 5,
    top_k: int = 5,
):

    df = rows_to_dataframe(
        rows
    )

    close = (
        df["close"]
        .astype(float)
    )

    returns = (
        close
        .pct_change()
        .dropna()
        .reset_index(
            drop=True
        )
    )

    needed = (
        window
        + forward
        + 30
    )

    if len(returns) < needed:

        return {
            "available": False,
            "message": (
                "FX needs more history before it can find useful historical comparisons."
            ),
            "matches": [],
        }

    current = (
        returns
        .iloc[-window:]
        .to_numpy()
    )

    current_std = (
        np.std(current)
        or 1.0
    )

    current = (
        current
        - np.mean(current)
    ) / current_std

    candidates = []

    end_limit = (
        len(returns)
        - window
        - forward
        - window
    )

    for start in range(
        0,
        max(
            end_limit,
            0,
        ),
    ):

        segment = (
            returns
            .iloc[
                start:
                start + window
            ]
            .to_numpy()
        )

        std = (
            np.std(segment)
            or 1.0
        )

        normalized = (
            segment
            - np.mean(segment)
        ) / std

        distance = float(
            np.sqrt(
                np.mean(
                    (
                        current
                        - normalized
                    ) ** 2
                )
            )
        )

        future_start = (
            start
            + window
        )

        future_end = (
            future_start
            + forward
        )

        future_return = float(
            (
                1
                + returns
                .iloc[
                    future_start:
                    future_end
                ]
            ).prod()
            - 1
        )

        candidates.append({
            "distance": distance,
            "forward_return": future_return,
            "start_index": start,
        })

    matches = sorted(
        candidates,
        key=lambda x:
            x["distance"],
    )[:top_k]

    average = (
        float(
            np.mean(
                [
                    x["forward_return"]
                    for x in matches
                ]
            )
        )
        if matches
        else None
    )

    positive = sum(
        1
        for x in matches
        if (
            x["forward_return"]
            > 0
        )
    )

    return {
        "available": bool(matches),
        "matches": matches,
        "average_forward_return": average,
        "positive_matches": positive,
        "total_matches": len(
            matches
        ),
        "important": (
            "Historical similarity does not guarantee that the current market will behave the same way."
        ),
    }

from __future__ import annotations

from typing import Iterable


def kalman_filter(
    prices: Iterable[float],
    process_variance: float = 1e-5,
    measurement_variance: float = 1e-2,
) -> list[float]:

    values = [
        float(x)
        for x in prices
    ]

    if not values:
        return []

    estimate = values[0]

    estimate_error = 1.0

    output = [
        estimate
    ]

    for measurement in values[1:]:

        prediction = estimate

        prediction_error = (
            estimate_error
            + process_variance
        )

        gain = (
            prediction_error
            /
            (
                prediction_error
                + measurement_variance
            )
        )

        estimate = (
            prediction
            + gain
            * (
                measurement
                - prediction
            )
        )

        estimate_error = (
            1
            - gain
        ) * prediction_error

        output.append(
            estimate
        )

    return output

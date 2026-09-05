from backend.app.services.strategies.evaluator import (
    evaluate_strategies,
)


def model_council(
    rows,
):

    evaluation = evaluate_strategies(
        rows
    )

    agreement = evaluation[
        "agreement"
    ]

    positive = agreement[
        "POSITIVE"
    ]

    negative = agreement[
        "NEGATIVE"
    ]

    neutral = agreement[
        "NEUTRAL"
    ]

    if (
        positive > negative
        and positive >= 3
    ):

        overall = "POSITIVE BIAS"

    elif (
        negative > positive
        and negative >= 3
    ):

        overall = "NEGATIVE BIAS"

    else:

        overall = "MIXED / NO CLEAR EDGE"

    return {
        "overall": overall,
        "agreement": agreement,
        "members": evaluation[
            "strategies"
        ],
        "features": evaluation[
            "features"
        ],
        "important": (
            "Model agreement is evidence to investigate. "
            "It is not proof that a trade will be profitable."
        ),
    }

from __future__ import annotations

from importlib.util import find_spec


def installed(
    package: str,
) -> bool:

    return (
        find_spec(package)
        is not None
    )


def brain_registry():

    return [
        {
            "id": "trend",
            "name": "Trend Model",
            "type": "Deterministic",
            "job": (
                "Checks whether price is moving consistently upward or downward."
            ),
            "status": "READY",
        },
        {
            "id": "momentum",
            "name": "Momentum Model",
            "type": "Deterministic",
            "job": (
                "Measures whether recent market movement is strengthening."
            ),
            "status": "READY",
        },
        {
            "id": "breakout",
            "name": "Breakout Model",
            "type": "Deterministic",
            "job": (
                "Checks whether price is moving beyond a recent trading range."
            ),
            "status": "READY",
        },
        {
            "id": "mean_reversion",
            "name": "Mean-Reversion Model",
            "type": "Deterministic",
            "job": (
                "Looks for unusually stretched prices that may move back toward normal."
            ),
            "status": "READY",
        },
        {
            "id": "kalman",
            "name": "Kalman Trend Model",
            "type": "Statistical",
            "job": (
                "Filters market noise to estimate the underlying direction."
            ),
            "status": "READY",
        },
        {
            "id": "regime",
            "name": "Regime Model",
            "type": "Statistical",
            "job": (
                "Separates different market environments such as quiet, volatile, trending or unstable."
            ),
            "status": (
                "READY"
                if installed(
                    "hmmlearn"
                )
                else "NOT INSTALLED"
            ),
        },
        {
            "id": "logistic",
            "name": "Logistic Regression",
            "type": "Machine Learning",
            "job": (
                "Simple probability baseline used to test whether more complicated models actually add value."
            ),
            "status": "INSTALLED · NOT TRAINED",
        },
        {
            "id": "random_forest",
            "name": "Random Forest",
            "type": "Machine Learning",
            "job": (
                "Combines many decision trees to learn nonlinear market relationships."
            ),
            "status": "INSTALLED · NOT TRAINED",
        },
        {
            "id": "lightgbm",
            "name": "LightGBM",
            "type": "Machine Learning",
            "job": (
                "Fast gradient-boosting model for structured market features."
            ),
            "status": (
                "INSTALLED · NOT VALIDATED"
                if installed(
                    "lightgbm"
                )
                else "NOT INSTALLED"
            ),
        },
        {
            "id": "xgboost",
            "name": "XGBoost",
            "type": "Machine Learning",
            "job": (
                "Gradient-boosting model used as an independent comparison with LightGBM."
            ),
            "status": (
                "INSTALLED · NOT VALIDATED"
                if installed(
                    "xgboost"
                )
                else "NOT INSTALLED"
            ),
        },
        {
            "id": "catboost",
            "name": "CatBoost",
            "type": "Machine Learning",
            "job": (
                "Another independent boosting model used to reduce dependence on a single ML approach."
            ),
            "status": (
                "INSTALLED · NOT TRAINED"
                if installed(
                    "catboost"
                )
                else "NOT INSTALLED"
            ),
        },
        {
            "id": "kronos",
            "name": "Kronos",
            "type": "Financial Foundation Model",
            "job": (
                "Produces probabilistic future candlestick paths rather than a single guaranteed forecast."
            ),
            "status": "INSTALLED · NOT VALIDATED",
        },
        {
            "id": "historical_analogues",
            "name": "Historical Analogue Engine",
            "type": "Memory",
            "job": (
                "Finds past market situations that most closely resemble the current setup."
            ),
            "status": "READY · RESEARCH",
        },
        {
            "id": "macro",
            "name": "Macro Model",
            "type": "Cross-Asset",
            "job": (
                "Connects rates, currencies, commodities and economic conditions."
            ),
            "status": "READY · RESEARCH",
        },
    ]

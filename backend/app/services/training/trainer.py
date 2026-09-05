from __future__ import annotations

import json
import os
import threading
import time

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

import joblib
import numpy as np

from sklearn.ensemble import (
    RandomForestClassifier,
)

from sklearn.linear_model import (
    LogisticRegression,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    roc_auc_score,
)

from sklearn.pipeline import (
    Pipeline,
)

from sklearn.preprocessing import (
    StandardScaler,
)

from lightgbm import (
    LGBMClassifier,
)

from xgboost import (
    XGBClassifier,
)

from catboost import (
    CatBoostClassifier,
)

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)

from backend.app.services.training.dataset import (
    FEATURE_COLUMNS,
    build_dataset,
)


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

REGISTRY = (
    ROOT
    / "data"
    / "models"
    / "registry"
    / "training_registry.json"
)

ARTIFACTS = (
    ROOT
    / "data"
    / "models"
    / "artifacts"
)

TRAINING_THREADS = max(1, int(os.getenv("FX_TRAINING_THREADS", "2")))
TRAINING_LOCK = threading.Lock()


def models():

    return {

        "logistic_regression":
            Pipeline(
                [
                    (
                        "scaler",
                        StandardScaler(),
                    ),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=1000,
                            class_weight="balanced",
                            random_state=42,
                        ),
                    ),
                ]
            ),

        "random_forest":
            RandomForestClassifier(
                n_estimators=250,
                max_depth=7,
                min_samples_leaf=8,
                class_weight="balanced",
                random_state=42,
                n_jobs=TRAINING_THREADS,
            ),

        "lightgbm":
            LGBMClassifier(
                n_estimators=250,
                learning_rate=0.035,
                max_depth=5,
                num_leaves=24,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=-1,
            ),

        "xgboost":
            XGBClassifier(
                n_estimators=250,
                learning_rate=0.035,
                max_depth=5,
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric="logloss",
                random_state=42,
                n_jobs=TRAINING_THREADS,
            ),

        "catboost":
            CatBoostClassifier(
                iterations=250,
                depth=5,
                learning_rate=0.035,
                verbose=False,
                random_seed=42,
                allow_writing_files=False,
            ),
    }


def safe_auc(
    y,
    probability,
):

    try:

        if len(
            np.unique(
                y
            )
        ) < 2:
            return None

        return float(
            roc_auc_score(
                y,
                probability,
            )
        )

    except Exception:

        return None


def evaluate(
    model,
    x,
    y,
):

    prediction = (
        model.predict(x)
    )

    probability = (
        model
        .predict_proba(x)[:, 1]
    )

    return {
        "accuracy": float(
            accuracy_score(
                y,
                prediction,
            )
        ),

        "balanced_accuracy": float(
            balanced_accuracy_score(
                y,
                prediction,
            )
        ),

        "auc": safe_auc(
            y,
            probability,
        ),

        "brier": float(
            brier_score_loss(
                y,
                probability,
            )
        ),
    }


def walk_forward(
    model_factory,
    x,
    y,
    folds=4,
):

    total = len(x)

    minimum_train = int(
        total * 0.50
    )

    remaining = (
        total
        - minimum_train
    )

    fold_size = max(
        int(
            remaining / folds
        ),
        20,
    )

    results = []

    for fold in range(
        folds
    ):

        train_end = (
            minimum_train
            + fold * fold_size
        )

        test_end = min(
            train_end
            + fold_size,
            total,
        )

        if (
            train_end >= total
            or (
                test_end
                - train_end
            ) < 15
        ):
            break

        train_x = (
            x.iloc[
                :train_end
            ]
        )

        train_y = (
            y.iloc[
                :train_end
            ]
        )

        test_x = (
            x.iloc[
                train_end:
                test_end
            ]
        )

        test_y = (
            y.iloc[
                train_end:
                test_end
            ]
        )

        model = (
            model_factory()
        )

        model.fit(
            train_x,
            train_y,
        )

        metrics = evaluate(
            model,
            test_x,
            test_y,
        )

        results.append(
            metrics
        )

    auc_values = [
        item["auc"]
        for item in results
        if item[
            "auc"
        ] is not None
    ]

    balanced = [
        item[
            "balanced_accuracy"
        ]
        for item in results
    ]

    return {
        "folds":
            results,

        "average_auc":
            float(
                np.mean(
                    auc_values
                )
            )
            if auc_values
            else None,

        "average_balanced_accuracy":
            float(
                np.mean(
                    balanced
                )
            )
            if balanced
            else None,
    }


def determine_status(
    test_metrics,
    walk,
):

    auc = (
        test_metrics[
            "auc"
        ]
    )

    balanced = (
        test_metrics[
            "balanced_accuracy"
        ]
    )

    if (
        auc is None
        or auc < 0.52
        or balanced < 0.51
    ):

        return (
            "TRAINED · OOS FAILED"
        )

    walk_auc = (
        walk[
            "average_auc"
        ]
    )

    walk_balanced = (
        walk[
            "average_balanced_accuracy"
        ]
    )

    if (
        walk_auc is None
        or walk_auc < 0.52
        or (
            walk_balanced
            is None
        )
        or walk_balanced < 0.51
    ):

        return (
            "OOS PASSED · WALK-FORWARD FAILED"
        )

    return (
        "WALK_FORWARD_PASSED"
    )


def load_registry():

    if not REGISTRY.exists():
        return {}

    try:

        return json.loads(
            REGISTRY.read_text()
        )

    except Exception:

        return {}


def save_registry(
    registry,
):

    REGISTRY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REGISTRY.write_text(
        json.dumps(
            registry,
            indent=2,
            default=str,
        )
    )


def _train_all(
    symbol: str,
    timeframe: str,
    horizon: int,
):

    started = time.time()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    service = (
        LSEGlobalMarketData()
    )

    rows = service.candles(
        symbol=symbol,
        timeframe=timeframe,
        limit=3000,
    )

    dataset = build_dataset(
        rows,
        horizon=horizon,
    )

    if len(dataset) < 300:

        raise ValueError(
            "FX does not have enough clean historical observations to train these models safely."
        )

    x = dataset[
        FEATURE_COLUMNS
    ]

    y = dataset[
        "target"
    ]

    split_1 = int(
        len(dataset)
        * 0.60
    )

    split_2 = int(
        len(dataset)
        * 0.80
    )

    train_x = x.iloc[
        :split_1
    ]

    train_y = y.iloc[
        :split_1
    ]

    test_x = x.iloc[
        split_2:
    ]

    test_y = y.iloc[
        split_2:
    ]

    registry = (
        load_registry()
    )

    all_results = []

    factory_map = {

        "logistic_regression":
            lambda:
                models()[
                    "logistic_regression"
                ],

        "random_forest":
            lambda:
                models()[
                    "random_forest"
                ],

        "lightgbm":
            lambda:
                models()[
                    "lightgbm"
                ],

        "xgboost":
            lambda:
                models()[
                    "xgboost"
                ],

        "catboost":
            lambda:
                models()[
                    "catboost"
                ],
    }

    for (
        model_name,
        factory
    ) in factory_map.items():

        model = factory()

        model.fit(
            train_x,
            train_y,
        )

        test_metrics = evaluate(
            model,
            test_x,
            test_y,
        )

        walk = walk_forward(
            factory,
            x,
            y,
        )

        status = determine_status(
            test_metrics,
            walk,
        )

        safe_symbol = (
            symbol
            .replace(
                "/",
                "_"
            )
        )

        artifact_dir = (
            ARTIFACTS
            / model_name
        )

        artifact_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifact = (
            artifact_dir
            / (
                safe_symbol
                + "_"
                + timeframe
                + "_h"
                + str(
                    horizon
                )
                + "_"
                + run_id
                + ".joblib"
            )
        )

        joblib.dump(
            model,
            artifact,
        )

        key = (
            model_name
            + ":"
            + symbol
            + ":"
            + timeframe
            + ":"
            + str(
                horizon
            )
            + ":"
            + run_id
        )

        record = {
            "model":
                model_name,

            "symbol":
                symbol,

            "timeframe":
                timeframe,

            "horizon":
                horizon,

            "trained_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "run_id":
                run_id,

            "training_observations":
                len(
                    train_x
                ),

            "test_observations":
                len(
                    test_x
                ),

            "features":
                FEATURE_COLUMNS,

            "test_metrics":
                test_metrics,

            "walk_forward":
                walk,

            "status":
                status,

            "artifact":
                str(
                    artifact
                ),

            "data_source":
                "London Strategic Edge",
        }

        registry[
            key
        ] = record

        all_results.append(
            record
        )

    save_registry(
        registry
    )

    return {
        "symbol":
            symbol,

        "timeframe":
            timeframe,

        "horizon":
            horizon,

        "dataset_rows":
            len(
                dataset
            ),

        "models":
            all_results,

        "elapsed_seconds":
            round(
                time.time()
                - started,
                2,
            ),

        "important":
            (
                "Training completion does not authorize Paper or live trading. "
                "Only models that pass validation can move to the next stage."
            ),
    }


def train_all(symbol: str, timeframe: str, horizon: int):
    """Run one bounded training job at a time across manual and continuous flows."""
    with TRAINING_LOCK:
        return _train_all(symbol, timeframe, horizon)

from fastapi import (
    APIRouter,
)

from pydantic import (
    BaseModel,
)

from starlette.concurrency import (
    run_in_threadpool,
)

from backend.app.services.training.trainer import (
    load_registry,
    train_all,
)


router = APIRouter(
    prefix="/api/training",
    tags=["Model Training"],
)


class TrainingRequest(
    BaseModel
):

    symbol: str

    timeframe: str = "1d"

    horizon: int = 5


@router.get("/registry")
async def registry():

    return {
        "ok": True,
        "registry": (
            load_registry()
        ),
    }


@router.post("/train-all")
async def train(
    request: TrainingRequest,
):

    try:

        result = (
            await run_in_threadpool(
                train_all,
                request.symbol.strip(),
                request.timeframe,
                request.horizon,
            )
        )

        return {
            "ok": True,
            "result": result,
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }

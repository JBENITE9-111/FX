from fastapi import APIRouter, Query

from services.learning.status import learning_overview
from services.learning.continuous import continuous_learning
from services.instruments.training_universe import search_training_catalog, universe

router = APIRouter(prefix="/api/learning", tags=["Learning"])


@router.get("/overview")
def overview():
    return {**learning_overview(), "continuous": continuous_learning.status()}


@router.get("/universe")
def learning_universe():
    return {"instruments": universe()}


@router.get("/catalog")
def learning_catalog(asset_class: str | None = None, market: str | None = None,
                     q: str = "", limit: int = Query(default=500, ge=1, le=1000), focused: bool = False):
    return search_training_catalog(asset_class=asset_class, market=market, query=q, limit=limit, focused=focused)


@router.post("/start")
def start_learning():
    return {"ok": True, "continuous": continuous_learning.start("USER")}


@router.post("/stop")
def stop_learning():
    return {"ok": True, "continuous": continuous_learning.stop()}

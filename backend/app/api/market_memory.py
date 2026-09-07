from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query

from backend.app.services.market_data.lse_global import LSEGlobalMarketData
from services.market_memory.research import historical_analogues
from services.market_memory.store import MarketMemoryStore
from services.market_memory.strategy_exam import examine_strategy


router = APIRouter(prefix="/api/market-memory", tags=["Market Memory"])


@router.get("/sources")
def sources():
    store = MarketMemoryStore()
    store.register_lse_source()
    return {"sources": store.registry.list_sources(), "research_only": True}


@router.get("/datasets")
def datasets():
    store = MarketMemoryStore()
    return {"datasets": store.registry.list_datasets(), "research_only": True}


@router.post("/ingest/{symbol:path}")
async def ingest(
    symbol: str,
    dataset: str,
    asset_class: str,
    timeframe: str = "1d",
    limit: int = Query(default=2000, ge=300, le=5000),
):
    provider = LSEGlobalMarketData()
    rows = await asyncio.to_thread(
        provider.candles, symbol, timeframe, limit, dataset
    )
    result = MarketMemoryStore().ingest_bars(
        rows=rows,
        provider="London Strategic Edge",
        source_id="london-strategic-edge",
        dataset_name=dataset,
        symbol=symbol,
        asset_class=asset_class,
        timeframe=timeframe,
        venue=None,
        adjustment_policy="PROVIDER_UNSPECIFIED",
    )
    return {"ok": True, "artifact": result["manifest"], "research_only": True}


@router.get("/artifacts/{artifact_id}/analogues")
def analogues(artifact_id: str, forward_periods: int = 5, top_k: int = 10):
    store = MarketMemoryStore()
    frame, artifact = store.load_artifact(artifact_id)
    if artifact["quality"]["status"] != "PASS":
        return {
            "available": False,
            "artifact_id": artifact_id,
            "reason": "Historical analogues are blocked pending data-quality review.",
            "data_quality_status": artifact["quality"]["status"],
        }
    return historical_analogues(
        frame, artifact_id=artifact_id,
        forward_periods=forward_periods, top_k=top_k,
    )


@router.post("/artifacts/{artifact_id}/exams/{strategy_id}")
def strategy_exam(artifact_id: str, strategy_id: str):
    return examine_strategy(
        store=MarketMemoryStore(), artifact_id=artifact_id, strategy_id=strategy_id
    )

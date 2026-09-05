from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.campaigns.store import campaign_store
from services.readiness.gate import readiness_for

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


class CampaignRequest(BaseModel):
    bot_id: str
    strategy_id: str
    strategy_version: str = "1"
    instrument: str
    asset_class: str
    timeframe: str = "1h"
    capital: float = Field(gt=0)
    target_type: str
    target_value: float = Field(gt=0)
    maximum_loss: float = Field(gt=0)
    deadline: float


@router.get("")
def campaigns():
    return {"campaigns": campaign_store.list()}


@router.post("")
def create_campaign(request: CampaignRequest):
    try:
        result = campaign_store.create(**request.model_dump(exclude={"timeframe"}))
        readiness = readiness_for(
            bot_id=request.bot_id, strategy_id=request.strategy_id,
            strategy_version=request.strategy_version, instrument=request.instrument,
            timeframe=request.timeframe,
        )
        if not readiness["eligible"]:
            result = campaign_store.set_status(result["campaign_id"], "WAITING_FOR_READINESS",
                                               " ".join(readiness["reasons"]))
        return {"campaign": result, "readiness": readiness}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{campaign_id}/stop")
def stop_campaign(campaign_id: str):
    try:
        return campaign_store.set_status(campaign_id, "STOPPED", "Stopped by the owner.")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

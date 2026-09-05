from fastapi import APIRouter, Query

from services.reporting.trade_report import ASSET_CLASSES, dashboard, trade_rows
from services.readiness.gate import readiness_for

router = APIRouter(prefix="/api/reporting", tags=["Reporting"])


@router.get("/dashboard")
def report_dashboard():
    return dashboard()


@router.get("/trades")
def report_trades(asset_class: str | None = None, bot_id: str | None = None,
                  campaign_id: str | None = None,
                  limit: int = Query(default=500, ge=1, le=5000)):
    return {"trades": trade_rows(asset_class=asset_class, bot_id=bot_id,
                                 campaign_id=campaign_id, limit=limit)}


@router.get("/asset-classes")
def asset_classes():
    return {"asset_classes": ASSET_CLASSES}


@router.get("/bots/{bot_id}/readiness")
def bot_readiness(bot_id: str, strategy_id: str, strategy_version: str,
                  instrument: str, timeframe: str):
    return readiness_for(bot_id=bot_id, strategy_id=strategy_id,
                         strategy_version=strategy_version, instrument=instrument,
                         timeframe=timeframe)

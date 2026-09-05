from fastapi import (
    APIRouter,
    Query,
)

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)

from backend.app.services.models.registry import (
    brain_registry,
)

from backend.app.services.models.council import (
    model_council,
)

from backend.app.services.strategies.catalog import (
    STRATEGIES,
)

from backend.app.services.intelligence.hedge_funds import (
    HedgeFundIntelligence,
)


router = APIRouter(
    prefix="/api/research",
    tags=["Research"],
)


@router.get("/brains")
async def brains():

    return {
        "ok": True,
        "brains": brain_registry(),
    }


@router.get("/strategies")
async def strategies():

    return {
        "ok": True,
        "strategies": STRATEGIES,
    }


@router.get("/council/{symbol:path}")
async def council(
    symbol: str,
    timeframe: str = "1d",
):

    try:

        service = LSEGlobalMarketData()

        rows = service.candles(
            symbol=symbol,
            timeframe=timeframe,
            limit=250,
        )

        return {
            "ok": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "source": (
                "London Strategic Edge"
            ),
            "council": model_council(
                rows
            ),
        }

    except Exception:

        return {
            "ok": False,
            "message": (
                "FX could not complete the model review for this market."
            ),
        }


@router.get("/hedge-funds/sources")
async def hedge_fund_sources():

    intelligence = (
        HedgeFundIntelligence()
    )

    return {
        "ok": True,
        "sources": (
            intelligence.sources()
        ),
    }


@router.get("/hedge-funds/cftc")
async def cftc(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
):

    try:

        intelligence = (
            HedgeFundIntelligence()
        )

        rows = await (
            intelligence.cftc_latest(
                limit=limit
            )
        )

        return {
            "ok": True,
            "source": "CFTC",
            "rows": rows,
        }

    except Exception:

        return {
            "ok": False,
            "message": (
                "Institutional futures-positioning data is temporarily unavailable."
            ),
        }


@router.get("/hedge-funds/fca-shorts")
async def fca_shorts():

    try:

        intelligence = (
            HedgeFundIntelligence()
        )

        csv_text = await (
            intelligence
            .fca_short_positions()
        )

        return {
            "ok": True,
            "source": (
                "Financial Conduct Authority"
            ),
            "csv": csv_text,
        }

    except Exception:

        return {
            "ok": False,
            "message": (
                "UK aggregate short-position data is temporarily unavailable."
            ),
        }


@router.get("/hedge-funds/ofr-counterparties")
async def ofr_counterparties():

    try:

        intelligence = (
            HedgeFundIntelligence()
        )

        data = await (
            intelligence
            .ofr_counterparties()
        )

        return {
            "ok": True,
            "source": (
                "U.S. Office of Financial Research"
            ),
            "data": data,
        }

    except Exception:

        return {
            "ok": False,
            "message": (
                "Hedge-fund counterparty information is temporarily unavailable."
            ),
        }

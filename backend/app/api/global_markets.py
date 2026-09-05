from fastapi import (
    APIRouter,
    Query,
)

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)


router = APIRouter(
    prefix="/api/global",
    tags=["Global Markets"],
)


def friendly_error(
    message: str,
):
    return {
        "ok": False,
        "message": message,
    }


@router.get("/status")
async def lse_status():

    try:

        service = LSEGlobalMarketData()

        rows = service.search(
            limit=1
        )

        return {
            "ok": True,
            "provider": (
                "London Strategic Edge"
            ),
            "message": (
                "Global market data is connected."
            ),
            "catalog_available": bool(
                rows
            ),
        }

    except Exception:

        return friendly_error(
            "Global market data is not connected right now."
        )


@router.get("/categories")
async def categories():

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "categories": (
                service.categories()
            ),
        }

    except Exception:

        return friendly_error(
            "FX could not load the market categories."
        )


@router.get("/search")
async def search(
    q: str = "",
    category: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):

    try:

        service = LSEGlobalMarketData()

        rows = service.search(
            query=q,
            category=category,
            limit=limit,
        )

        return {
            "ok": True,
            "query": q,
            "category": category,
            "count": len(rows),
            "results": rows,
        }

    except Exception:

        return friendly_error(
            "FX could not search the global market catalog."
        )


@router.get("/chart/{symbol:path}")
async def chart(
    symbol: str,
    timeframe: str = "1h",
    limit: int = Query(
        default=500,
        ge=1,
        le=5000,
    ),
    dataset: str | None = None,
):

    try:

        service = LSEGlobalMarketData()

        rows = service.candles(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            dataset=dataset,
        )

        if not rows:

            return {
                "ok": False,
                "message": (
                    "No market history was returned for this instrument."
                ),
                "bars": [],
            }

        latest = rows[-1]

        latest_price = (
            latest.get("close")
            or latest.get("price")
        )

        return {
            "ok": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "source": (
                "London Strategic Edge"
            ),
            "latest_price": latest_price,
            "bars": rows,
        }

    except Exception:

        return friendly_error(
            "FX could not load this market history right now."
        )


@router.get("/calendar")
async def calendar(
    region: str | None = None,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "source": (
                "London Strategic Edge"
            ),
            "events": (
                service.economic_calendar(
                    region=region
                )
            ),
        }

    except Exception:

        return friendly_error(
            "FX could not load the economic calendar."
        )


@router.get("/company/{symbol}")
async def company(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "profile": (
                service.company_profile(
                    symbol
                )
            ),
            "fundamentals": (
                service.fundamentals(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Company information is not available right now."
        )


@router.get("/financials/{symbol}")
async def financials(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "reports": (
                service.financial_reports(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Financial statements are not available right now."
        )


@router.get("/insiders/{symbol}")
async def insiders(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "trades": (
                service.insider_trades(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Insider activity is not available right now."
        )


@router.get("/dividends/{symbol}")
async def dividends(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "dividends": (
                service.dividends(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Dividend information is not available right now."
        )


@router.get("/splits/{symbol}")
async def splits(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "splits": (
                service.splits(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Stock split information is not available right now."
        )


@router.get("/options/{underlying}")
async def options(
    underlying: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "underlying": underlying,
            "chain": (
                service.options(
                    underlying
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Options information is not available right now."
        )


@router.get("/option-flow")
async def option_flow(
    underlying: str | None = None,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "underlying": underlying,
            "prints": (
                service.option_flow(
                    underlying
                )
            ),
        }

    except Exception:

        return friendly_error(
            "Options trading activity is not available right now."
        )


@router.get("/macro/{symbol}")
async def macro(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "source": (
                "London Strategic Edge"
            ),
            "observations": (
                service.macro_series(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "This economic series is not available right now."
        )


@router.get("/bonds/{symbol}")
async def bonds(
    symbol: str,
):

    try:

        service = LSEGlobalMarketData()

        return {
            "ok": True,
            "symbol": symbol,
            "source": (
                "London Strategic Edge"
            ),
            "observations": (
                service.bond_yields(
                    symbol
                )
            ),
        }

    except Exception:

        return friendly_error(
            "This government yield series is not available right now."
        )

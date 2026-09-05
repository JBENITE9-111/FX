import os

import httpx
from fastapi import APIRouter

from backend.app.services.brokers.alpaca_paper import (
    AlpacaPaperBroker,
)


router = APIRouter(
    prefix="/api/status",
    tags=["status"],
)


@router.get("")
async def system_status():

    ai_working = False
    alpaca_working = False
    lse_working = False

    try:

        async with httpx.AsyncClient(
            timeout=3
        ) as client:

            response = await client.get(
                "http://127.0.0.1:11434/api/tags"
            )

            ai_working = (
                response.status_code
                == 200
            )

    except Exception:
        pass

    try:

        broker = AlpacaPaperBroker()

        broker.account()

        alpaca_working = True

    except Exception:
        pass

    try:

        from backend.app.services.market_data.lse_global import (
            LSEGlobalMarketData,
        )

        lse = LSEGlobalMarketData()

        lse.search(
            limit=1
        )

        lse_working = True

    except Exception:
        pass

    return {
        "ai": ai_working,
        "ollama": ai_working,
        "kimi": bool(
            os.getenv("OPENROUTER_ENABLED", "false").lower() == "true"
            and os.getenv("OPENROUTER_API_KEY", "").strip()
        ),
        "alpaca": alpaca_working,
        "lse": lse_working,
        "hugging_face": bool(
            os.getenv(
                "HF_TOKEN",
                "",
            )
        ),
        "gold": lse_working,
        "paper_trading": True,
        "real_money": False,
    }

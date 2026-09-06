import os
import shutil

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
    headroom_working = False
    freellm_working = False

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

    headroom_enabled = os.getenv("HEADROOM_ENABLED", "false").lower() == "true"
    if headroom_enabled:
        try:
            base = os.getenv("HEADROOM_BASE_URL", "http://127.0.0.1:8787").rstrip("/")
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f"{base}/livez")
                headroom_working = response.status_code == 200
        except Exception:
            pass

    freellm_enabled = os.getenv("FREELLMAPI_ENABLED", "false").lower() == "true"
    if freellm_enabled:
        try:
            base = os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:3001/v1").rstrip("/")
            headers = {}
            if os.getenv("FREELLMAPI_API_KEY", "").strip():
                headers["Authorization"] = "Bearer " + os.getenv("FREELLMAPI_API_KEY", "").strip()
            async with httpx.AsyncClient(timeout=2, headers=headers) as client:
                response = await client.get(f"{base}/models")
                freellm_working = response.status_code == 200
        except Exception:
            pass

    goose_path = os.getenv("GOOSE_PATH", "").strip() or shutil.which("goose")
    goose_enabled = os.getenv("GOOSE_CHAT_ENABLED", "false").lower() == "true"
    openrouter_working = bool(
        os.getenv("OPENROUTER_ENABLED", "false").lower() == "true"
        and os.getenv("OPENROUTER_API_KEY", "").strip()
    )
    extra_models = [
        model.strip()
        for model in os.getenv("OPENROUTER_COUNCIL_MODELS", "").split(",")
        if model.strip()
    ][:3]

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
        "ai": ai_working or openrouter_working or freellm_working,
        "ollama": ai_working,
        "kimi": openrouter_working,
        "openrouter": openrouter_working,
        "openrouter_council_models": extra_models,
        "freellmapi": {"enabled": freellm_enabled, "responding": freellm_working},
        "goose": {"enabled": goose_enabled, "installed": bool(goose_path)},
        "headroom": {"enabled": headroom_enabled, "responding": headroom_working},
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

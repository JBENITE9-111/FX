from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.auth.middleware import TotpAccessMiddleware

from backend.app.api.chat import router as chat_router
from backend.app.api.market import router as market_router
from backend.app.api.broker import router as broker_router
from backend.app.web.chat import router as web_router
from backend.app.api.campaigns import router as campaigns_router
from backend.app.api.reporting import router as reporting_router
from backend.app.api.learning import router as learning_api_router
from backend.app.web.learning import router as learning_web_router


app = FastAPI(
    title="FX AI Quant",
    version="0.1.0",
    description=(
        "Local-first AI quantitative research and paper-trading API."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TotpAccessMiddleware)

app.include_router(chat_router)
app.include_router(market_router)
app.include_router(broker_router)
app.include_router(web_router)
app.include_router(campaigns_router)
app.include_router(reporting_router)
app.include_router(learning_api_router)
app.include_router(learning_web_router)


@app.on_event("startup")
async def start_local_research_at_login():
    from services.monitoring.sentinel import sentinel
    from services.operations.scheduler import scheduler
    from services.local_paper.broker import protect_legacy_positions
    protect_legacy_positions()
    sentinel.start()
    scheduler.start()
    if os.getenv("FX_AUTO_LEARN_ON_STARTUP", "true").lower() in {"1", "true", "yes"}:
        from services.learning.continuous import continuous_learning
        continuous_learning.start("APP_STARTUP")
    if os.getenv("FX_AUTO_START_BOTS", "false").lower() in {"1", "true", "yes"}:
        from backend.app.services.bots.runtime import bots
        for item in bots.list():
            bots.start(item["id"])


@app.on_event("shutdown")
async def stop_local_sentinel():
    from services.monitoring.sentinel import sentinel
    from services.operations.scheduler import scheduler
    sentinel.stop()
    scheduler.stop()


@app.get("/")
async def root():
    return {
        "project": "FX",
        "version": "0.1.0",
        "mode": "research",
        "live_trading": False,
    }


@app.get("/health")
async def health():
    from services.monitoring.sentinel import sentinel
    return {
        "status": "ok",
        "project": "FX",
        "version": "0.1.0",
        "live_trading": False,
        "paper_trading": True,
        "llm": "ollama",
        "sentinel": sentinel.status(),
    }

from backend.app.api.status import router as status_router
app.include_router(status_router)

from backend.app.api.global_markets import router as global_markets_router

from backend.app.web.global_markets import router as global_markets_web_router
app.include_router(global_markets_router)
app.include_router(global_markets_web_router)

from backend.app.api.research_brains import router as research_brains_router

from backend.app.web.research_hub import router as research_hub_router
app.include_router(research_brains_router)
app.include_router(research_hub_router)

from backend.app.api.strategy_lab import router as strategy_lab_router

from backend.app.web.strategy_workbench import router as strategy_workbench_router

from backend.app.web.journal import router as journal_router
app.include_router(strategy_lab_router)
app.include_router(strategy_workbench_router)
app.include_router(journal_router)

from backend.app.api.bots import router as bots_api_router

from backend.app.web.bots import router as bots_web_router
app.include_router(bots_api_router)
app.include_router(bots_web_router)

from backend.app.api.training import router as training_api_router

from backend.app.web.training import router as training_web_router
app.include_router(training_api_router)
app.include_router(training_web_router)

from backend.app.api.control_center import router as control_center_router

from backend.app.web.terminal import router as terminal_router
app.include_router(control_center_router)
app.include_router(terminal_router)

# FX_V4_ROUTERS
try:
    from backend.app.routes.fx_newspaper import router as fx_newspaper_router
    from backend.app.routes.fx_strategy_fleet import router as fx_strategy_fleet_router
    from backend.app.routes.fx_agents import router as fx_agents_router
    from backend.app.routes.fx_brain import router as fx_brain_router
    from backend.app.routes.fx_security import router as fx_security_router

    app.include_router(fx_newspaper_router)
    app.include_router(fx_strategy_fleet_router)
    app.include_router(fx_agents_router)
    app.include_router(fx_brain_router)
    app.include_router(fx_security_router)
except Exception as fx_v4_router_error:
    print("FX V4 route warning:", fx_v4_router_error)


# FX_BOT_SIGNAL_CENTER_V1
try:

    from backend.app.routes.fx_bot_signals import (
        router
        as fx_bot_signals_router,
    )

    from backend.app.routes.fx_signal_center import (
        router
        as fx_signal_center_router,
    )

    app.include_router(
        fx_bot_signals_router
    )

    app.include_router(
        fx_signal_center_router
    )

except Exception as fx_signal_error:

    print(
        "FX signal-center warning:",
        type(
            fx_signal_error
        ).__name__,
        str(
            fx_signal_error
        ),
    )



# FX_LOCAL_PAPER_V1
try:

    from backend.app.routes.fx_local_paper import (
        router as fx_local_paper_router,
    )

    from backend.app.routes.fx_local_paper_page import (
        router as fx_local_paper_page_router,
    )

    app.include_router(
        fx_local_paper_router
    )

    app.include_router(
        fx_local_paper_page_router
    )

except Exception as fx_local_paper_error:

    print(
        "FX Local Paper warning:",
        type(
            fx_local_paper_error
        ).__name__,
        str(
            fx_local_paper_error
        ),
    )

from backend.app.routes.fx_operations import router as fx_operations_router
app.include_router(fx_operations_router)

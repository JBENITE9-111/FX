from __future__ import annotations

from fastapi import (
    APIRouter,
    Query,
)

from pydantic import (
    BaseModel,
)

from backend.app.services.jobs.manager import (
    jobs,
)

from backend.app.services.llm.router import (
    FXLLMRouter,
)

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)

from backend.app.services.models.council import (
    model_council,
)

from backend.app.services.research.grounded_answer import (
    grounded_context_answer,
    identify_symbols,
    operational_answer,
    local_system_context,
)
from services.chat.memory import remember, recent, recall

from backend.app.services.training.trainer import (
    load_registry,
    train_all,
)

from backend.app.services.bots.runtime import (
    bots,
)

from backend.app.services.bots.paper_account import (
    paper_snapshot,
)


router = APIRouter(
    prefix="/api/control",
    tags=["FX Control Center"],
)


class ChatRequest(
    BaseModel
):

    message: str

    symbol: str | None = None

    timeframe: str = "1h"

    conversation_id: str = "personal"


class TrainingRequest(
    BaseModel
):

    symbol: str

    timeframe: str = "1d"

    horizon: int = 5


class TrainingBatchRequest(BaseModel):
    targets: list[TrainingRequest]


class BotConfig(
    BaseModel
):

    mode: str | None = None

    strategy: str | None = None

    timeframe: str | None = None

    watchlist: list[str] | None = None

    scan_every_seconds: int | None = None


@router.post("/chat")
async def chat(
    request: ChatRequest,
):

    remember(request.conversation_id, "user", request.message, request.symbol)

    async def worker():

        def finish(result: dict):
            remember(request.conversation_id, "assistant", str(result.get("answer") or ""), request.symbol)
            return result

        operational = operational_answer(request.message)
        if operational:
            return finish({
                "provider": "FX deterministic operations guide",
                "model": "Local verified system state",
                "answer": operational,
            })

        context = {
            "local_fx": local_system_context(),
            "recent_personal_chat": recent(request.conversation_id, 16),
            "recalled_personal_memory": recall(request.message, request.conversation_id, 12),
        }

        if "yahoo" in request.message.lower() or "spacex" in request.message.lower():
            try:
                from services.market_intelligence.yahoo_finance import lookup, render_lookup
                yahoo = await __import__("asyncio").to_thread(lookup, "SpaceX" if "spacex" in request.message.lower() else request.message)
                context["yahoo_finance"] = yahoo
                if any(term in request.message.lower() for term in ("price", "quote", "how much")):
                    return finish({
                        "provider": "FX deterministic market lookup",
                        "model": "Yahoo Finance",
                        "answer": render_lookup(yahoo),
                    })
            except Exception:
                context["yahoo_finance"] = {"status": "UNAVAILABLE", "message": "Yahoo Finance did not return verifiable data."}

        try:
            from services.news.newspaper import load as load_newspaper
            terms = {term for term in request.message.lower().split() if len(term) >= 4}
            items = load_newspaper().get("items") or []
            relevant = [item for item in items if any(term in str(item.get("title") or "").lower() for term in terms)]
            context["source_labelled_headlines"] = [{k: item.get(k) for k in ("title", "source", "published_at", "url")} for item in relevant[:8]]
        except Exception:
            context["source_labelled_headlines"] = []

        mentioned_symbols = identify_symbols(request.message)
        resolved_symbol = mentioned_symbols[0] if mentioned_symbols else request.symbol

        if resolved_symbol:

            try:

                service = (
                    LSEGlobalMarketData()
                )

                rows = await __import__(
                    "asyncio"
                ).to_thread(
                    service.candles,
                    resolved_symbol,
                    request.timeframe,
                    250,
                )

                if rows:

                    latest = rows[-1]

                    context.update({
                        "symbol":
                            resolved_symbol,

                        "timeframe":
                            request.timeframe,

                        "source":
                            "London Strategic Edge",

                        "latest_price":
                            (
                                latest.get(
                                    "close"
                                )
                                or latest.get(
                                    "c"
                                )
                            ),

                        "model_council":
                            model_council(
                                rows
                            ),
                    })

                    deterministic = grounded_context_answer(request.message, context, rows)
                    if deterministic:
                        return finish({
                            "provider": "FX deterministic research engine",
                            "model": "London Strategic Edge + Model Council",
                            "answer": deterministic,
                        })

            except Exception as exc:

                context.update({"symbol": resolved_symbol, "data_error": str(exc)})

        router_llm = (
            FXLLMRouter()
        )

        return finish(await router_llm.reason(
            request.message,
            context=context,
        ))

    job_id = jobs.submit_async(
        "CHAT",
        worker,
    )

    return {
        "ok": True,
        "job_id": job_id,
    }


@router.get("/chat/history")
async def chat_history(conversation_id: str = Query(default="personal", max_length=80)):
    return {"ok": True, "conversation_id": conversation_id, "messages": recent(conversation_id, 100)}


@router.get("/jobs/{job_id}")
async def job(
    job_id: str,
):

    item = jobs.get(
        job_id
    )

    if not item:

        return {
            "ok": False,
            "message":
                "FX could not find this background task.",
        }

    return {
        "ok": True,
        "job": item,
    }


@router.post("/training")
async def training(
    request: TrainingRequest,
):

    def worker():

        return train_all(
            request.symbol,
            request.timeframe,
            request.horizon,
        )

    job_id = jobs.submit_sync(
        "MODEL_TRAINING",
        worker,
    )

    return {
        "ok": True,
        "job_id": job_id,
    }


@router.post("/training/batch")
async def training_batch(request: TrainingBatchRequest):
    from services.instruments.training_universe import catalog_training_symbols

    approved_symbols = catalog_training_symbols()
    allowed_timeframes = {"1h", "4h", "1d"}
    allowed_horizons = {1, 3, 5, 10}
    requested = []
    for target in request.targets[:50]:
        key = (target.symbol.strip(), target.timeframe, int(target.horizon))
        if (
            key[0] not in approved_symbols
            or key[1] not in allowed_timeframes
            or key[2] not in allowed_horizons
        ):
            continue
        if key not in requested:
            requested.append(key)
    if not requested:
        return {
            "ok": False,
            "message": "Select an approved instrument, timeframe, and prediction horizon.",
        }

    def worker():
        results = []
        for symbol, timeframe, horizon in requested:
            results.append(train_all(symbol, timeframe, horizon))
        return {
            "targets": results,
            "models": [model for result in results for model in result.get("models", [])],
            "important": "Batch training creates research evidence only and cannot promote itself.",
        }

    return {"ok": True, "job_id": jobs.submit_sync("MODEL_TRAINING_BATCH", worker)}


@router.get("/training")
async def training_registry():

    return {
        "ok": True,
        "registry": (
            load_registry()
        ),
    }


@router.get("/bots")
async def bot_list():

    return {
        "ok": True,
        "bots": bots.list(),
    }


@router.post(
    "/bots/{bot_id}/start"
)
async def start_bot(
    bot_id: str,
):
    try:
        return {
            "ok": True,
            "bot": bots.start(bot_id),
        }
    except Exception as exc:
        return {
            "ok": False,
            "message": str(exc),
        }


@router.post("/bots/start-all")
async def start_all_bots():
    import os
    from services.monitoring.system_health import cpu_percent
    from services.monitoring.sentinel import sentinel

    cpu = cpu_percent()
    safe_limit = float(os.getenv("FX_BOT_MAX_CPU_PERCENT", "85"))
    resource_check = next((item for item in sentinel.status().get("checks", []) if item.get("name") == "System resource pressure"), {})
    pressure_safe = resource_check.get("status") == "PASS"
    if (cpu is None and not pressure_safe) or (cpu is not None and cpu > safe_limit):
        return {
            "ok": False,
            "message": "FX kept the scanner fleet stopped because CPU pressure could not be verified." if cpu is None else f"FX kept the scanner fleet stopped because CPU use {cpu:.1f}% exceeds the safe scanner limit {safe_limit:.1f}%.",
        }
    started = [bots.start(item["id"])["id"] for item in bots.list()]
    return {"ok": True, "started": started, "message": f"Started {len(started)} watch-only scanners."}


@router.post(
    "/bots/{bot_id}/stop"
)
async def stop_bot(
    bot_id: str,
):

    try:

        return {
            "ok": True,
            "bot": bots.stop(
                bot_id
            ),
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }


@router.post(
    "/bots/{bot_id}/scan"
)
async def scan_bot(
    bot_id: str,
):

    try:

        result = await bots.scan_once(
            bot_id
        )

        return {
            "ok": True,
            "bot": result,
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }


@router.post(
    "/bots/{bot_id}/configure"
)
async def configure_bot(
    bot_id: str,
    config: BotConfig,
):

    changes = {
        key: value
        for key, value
        in config.model_dump().items()
        if value is not None
    }

    try:

        result = bots.configure(
            bot_id,
            changes,
        )

        return {
            "ok": True,
            "bot": result,
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }


@router.get("/paper")
async def paper():

    try:

        return {
            "ok": True,
            "account":
                paper_snapshot(),
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }


@router.get(
    "/details/{symbol:path}"
)
async def details(
    symbol: str,
    tab: str = "overview",
):

    try:

        service = (
            LSEGlobalMarketData()
        )

        if tab == "overview":

            rows = service.candles(
                symbol,
                "1h",
                250,
            )

            return {
                "ok": True,
                "tab": tab,
                "data": {
                    "model_council":
                        model_council(
                            rows
                        ),
                },
            }

        if tab == "company":

            return {
                "ok": True,
                "tab": tab,
                "data":
                    service.company_profile(
                        symbol
                    ),
            }

        if tab == "fundamentals":

            return {
                "ok": True,
                "tab": tab,
                "data":
                    service.fundamentals(
                        symbol
                    ),
            }

        if tab == "financials":

            return {
                "ok": True,
                "tab": tab,
                "data":
                    service.financial_reports(
                        symbol
                    ),
            }

        if tab == "options":

            return {
                "ok": True,
                "tab": tab,
                "data":
                    service.options(
                        symbol
                    ),
            }

        if tab == "macro":

            return {
                "ok": True,
                "tab": tab,
                "data": {
                    "message":
                        (
                            "Use Ask FX while viewing this market. "
                            "The AI committee receives the current instrument "
                            "and can compare it with relevant macro evidence."
                        )
                },
            }

        if tab == "raw":

            rows = service.candles(
                symbol,
                "1h",
                50,
            )

            return {
                "ok": True,
                "tab": tab,
                "data": rows,
            }

        return {
            "ok": True,
            "tab": tab,
            "data": {
                "message":
                    "This section is available but has no additional dataset for this instrument.",
            },
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }

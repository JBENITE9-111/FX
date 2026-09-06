from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)

from backend.app.services.models.council import (
    model_council,
)


ALIASES = {
    "apple": "AAPL",
    "aapl": "AAPL",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "tesla": "TSLA",
    "tsla": "TSLA",
    "gold": "XAU/USD",
    "xau": "XAU/USD",
    "xauusd": "XAU/USD",
    "bitcoin": "BTC/USD",
    "btc": "BTC/USD",
    "eur/usd": "EUR/USD",
    "microsoft": "MSFT",
    "nike": "NKE",
    "silver": "XAG/USD",
    "ethereum": "ETH/USD",
}

DUBAI = ZoneInfo("Asia/Dubai")


def grounded_context_answer(message: str, context: dict, rows: list[dict]) -> str | None:
    """Answer simple market questions from verified rows before calling an LLM."""
    lower = message.lower()
    symbol = str(context.get("symbol") or "the selected market")
    council = context.get("model_council") or {}
    if any(term in lower for term in ("signal", "entry", "buy", "sell", "suggest")):
        agreement = council.get("agreement") or {}
        overall = str(council.get("overall") or "NO CLEAR EDGE")
        try:
            from services.learning.status import learning_overview
            evidence = [
                item for item in learning_overview()["records"]
                if item.get("is_current") and str(item.get("instrument") or "") == symbol
            ]
            approved = any(item.get("eligible") for item in evidence)
            examining = sum(item.get("stage") == "EXAMINATION" for item in evidence)
        except Exception:
            approved, examining = False, 0
        if not approved:
            return (
                f"{symbol}: WAIT. The current Model Council research view is {overall}, with "
                f"{agreement.get('POSITIVE', 0)} positive, {agreement.get('NEGATIVE', 0)} negative, and "
                f"{agreement.get('NEUTRAL', 0)} neutral votes. No strategy is approved for this instrument; "
                f"{examining} model version(s) are in examination. FX cannot provide an executable BUY or SELL entry "
                "until qualification, deterministic risk, stop, profit plan, and maximum-loss checks pass. No trade was sent."
            )
    if "strateg" in lower or "model" in lower:
        members = council.get("members") or []
        if members:
            names = ", ".join(str(item.get("strategy")) for item in members if item.get("strategy"))
            return (
                f"For {symbol}, FX currently evaluates {names}. "
                f"Their combined research view is {council.get('overall', 'not available')}. "
                "These are research signals; deterministic risk and qualification still control every executable entry."
            )

    if "price" not in lower and "how much" not in lower:
        return None

    selected = rows[-1] if rows else None
    timing = "latest available observation"
    if selected and "yesterday" in lower:
        match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", lower)
        hour = int(match.group(1)) if match else 0
        minute = int(match.group(2) or 0) if match else 0
        meridiem = match.group(3) if match else None
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        now = datetime.now(DUBAI)
        target = (now - timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        candidates = []
        for row in rows:
            raw = row.get("timestamp")
            if not raw:
                continue
            try:
                stamp = datetime.fromisoformat(str(raw).replace("Z", "+00:00")).astimezone(DUBAI)
                candidates.append((abs((stamp - target).total_seconds()), stamp, row))
            except ValueError:
                continue
        if candidates:
            _, stamp, selected = min(candidates, key=lambda item: item[0])
            timing = stamp.strftime("%Y-%m-%d %H:%M Asia/Dubai")

    if not selected:
        return f"FX does not have a verified price observation for {symbol} right now."
    price = selected.get("close") or selected.get("c")
    if price is None:
        return f"FX does not have a verified closing price for {symbol} right now."
    return (
        f"{symbol} was {price} at the {timing}, from London Strategic Edge. "
        "This is market information, not an entry signal. No trade was sent."
    )


def identify_symbols(
    message: str,
):

    lower = (
        message
        .lower()
    )

    found = []

    for term, symbol in (
        ALIASES.items()
    ):

        if (
            term in lower
            and symbol
            not in found
        ):

            found.append(
                symbol
            )

    # The local catalog lets chat understand thousands of names without a
    # hand-maintained alias list. Avoid matching short ticker fragments such
    # as C or T inside ordinary words.
    try:
        from services.instruments.training_universe import global_training_catalog

        padded = " " + re.sub(r"[^a-z0-9/.-]+", " ", lower).strip() + " "
        for item in global_training_catalog():
            symbol = str(item.get("symbol") or "")
            name = str(item.get("name") or "").lower()
            symbol_token = symbol.lower()
            exact_symbol = len(symbol_token) >= 2 and f" {symbol_token} " in padded
            named = len(name) >= 4 and name in lower
            if (exact_symbol or named) and symbol not in found:
                found.append(symbol)
                if len(found) >= 2:
                    break
    except Exception:
        pass

    return found


def operational_answer(message: str) -> str | None:
    """Answer questions about FX itself without depending on an LLM."""
    lower = message.lower()
    bot_terms = ("running bot", "bots doing", "bot doing", "where are the bots", "what are the bots")
    data_terms = ("what information", "what data", "data source", "information are getting")
    live_terms = ("trade live", "live trading", "real money")
    paper_terms = ("paper trading", "fake money", "virtual money", "paper order")

    if "strateg" in lower and "bot" in lower and not identify_symbols(message):
        from backend.app.services.bots.runtime import bots
        from backend.app.services.strategies.catalog import STRATEGIES
        strategy_lines = [f"• {item['name']} ({item['status']}) — {item['plain_english']}" for item in STRATEGIES]
        bot_lines = [f"• {item['name']} ({item['status']}) — {item['strategy']} on {item['timeframe']}; {len(item.get('watchlist') or [])} markets." for item in bots.list()]
        return ("Your private local FX inventory is:\n\nSTRATEGIES\n" + "\n".join(strategy_lines) +
                "\n\nBOTS\n" + "\n".join(bot_lines) +
                "\nThese scanners run locally, create research evidence, and do not place orders.")

    if "strateg" in lower and not identify_symbols(message):
        from backend.app.services.strategies.catalog import STRATEGIES
        selected = next((item for item in STRATEGIES if item["id"].replace("_", " ") in lower or item["name"].lower() in lower), None)
        if selected:
            return (
                f"{selected['name']} is a {selected['family']} research strategy. {selected['plain_english']} "
                f"It requires {', '.join(selected['required_data'])}. Current status: {selected['status']}; this description is not trade approval."
            )
        return "Your FX strategy library contains:\n" + "\n".join(
            f"• {item['name']} — {item['plain_english']} Status: {item['status']}." for item in STRATEGIES
        )

    if ("what" in lower or "explain" in lower or "list" in lower) and "bot" in lower:
        from backend.app.services.bots.runtime import bots
        rows = bots.list()
        selected = next((item for item in rows if item["id"].replace("_", " ") in lower or item["name"].lower() in lower), None)
        if selected:
            return (
                f"{selected['name']} is a {selected['mode']} scanner running {selected['strategy']} on {selected['timeframe']} candles. "
                f"It watches {', '.join(selected.get('watchlist') or [])}. Status: {selected['status']}. "
                "It fetches London Strategic Edge history, runs a deterministic test, and records research candidates; it cannot approve or place orders."
            )
        return "Your local FX bot fleet contains:\n" + "\n".join(
            f"• {item['name']} ({item['status']}) — {item['strategy']} on {item['timeframe']}, watching {len(item.get('watchlist') or [])} instruments." for item in rows
        ) + "\nThese watch-only scanners run locally and do not place orders."

    if any(term in lower for term in bot_terms):
        try:
            from backend.app.services.bots.runtime import bots
            running = [bot for bot in bots.list() if bot.get("status") == "RUNNING"]
        except Exception:
            running = []
        if not running:
            return (
                "No scanner bot is running in the current local FX process on this Mac. Open Trading Bots and press Start or Scan Now. "
                "These scanners observe markets and create research candidates; they do not place orders or train models."
            )
        descriptions = [
            f"{bot.get('name')} scans {len(bot.get('watchlist') or [])} instruments every "
            f"{int(bot.get('scan_every_seconds') or 300)} seconds using {bot.get('strategy')} on {bot.get('timeframe')} data"
            for bot in running
        ]
        return (
            "The running bots are local watch-only scanners inside the FX backend on this Mac. "
            + "; ".join(descriptions)
            + ". They read London Strategic Edge price history, run deterministic backtests, and record candidates. "
            "A candidate is not an approved trade and these scanners do not learn or place orders."
        )

    if any(term in lower for term in data_terms):
        return (
            "FX currently gives the scanner bots London Strategic Edge OHLCV price history, instrument identity, timeframe, "
            "and derived trend, momentum, volatility, drawdown, win-rate, and Sharpe evidence. The training center builds "
            "features from that history and tests models on later unseen data. Funding rates, DXY, economic events, COT, "
            "earnings, and other alternative data are planned but are not yet proven inputs for every bot."
        )

    if any(term in lower for term in live_terms):
        return (
            "Live trading is locked. The Live Trading Gate in FX is informational and cannot send real-money orders. "
            "Use Local Paper Trading for protected virtual-money orders and bot research suggestions. A future live pilot "
            "would still require validated models, paper and shadow evidence, deterministic risk approval, reconciliation, "
            "TOTP, and a fresh human authorization."
        )

    if any(term in lower for term in paper_terms):
        return (
            "Open Paper Portfolio in the FX sidebar. Local Paper Trading lets you choose instruments across Stocks, Forex, "
            "Crypto, Commodities, Indices, ETFs, and Futures, then enter a protected virtual-money order with a stop, "
            "profit plan, and maximum loss. Bot observations are shown as research suggestions and never bypass those controls."
        )
    return None


def local_system_context() -> dict:
    """Small, verified inventory supplied to the chat committee."""
    from backend.app.services.bots.runtime import bots
    from backend.app.services.strategies.catalog import STRATEGIES
    from services.chat.memory import status as memory_status
    from services.learning.status import learning_overview
    from services.local_paper.broker import get_account, positions

    learning = learning_overview()["summary"]
    return {
        "bots": [{"id": row["id"], "name": row["name"], "status": row["status"], "strategy": row["strategy"], "timeframe": row["timeframe"]} for row in bots.list()],
        "strategies": [{"id": row["id"], "name": row["name"], "status": row["status"], "description": row["plain_english"]} for row in STRATEGIES],
        "learning": learning,
        "paper_account": get_account(),
        "open_paper_positions": len(positions()),
        "personal_memory": memory_status(),
    }


def grounded_answer(
    message: str,
):

    symbols = identify_symbols(
        message
    )

    if not symbols:

        return None

    service = (
        LSEGlobalMarketData()
    )

    analyses = []

    for symbol in symbols[:2]:

        rows = service.candles(
            symbol=symbol,
            timeframe="1d",
            limit=250,
        )

        latest = rows[-1]

        price = (
            latest.get(
                "close"
            )
            or latest.get(
                "c"
            )
        )

        council = model_council(
            rows
        )

        analyses.append({
            "symbol": symbol,
            "price": price,
            "council": council,
        })

    if len(
        analyses
    ) == 1:

        item = analyses[0]

        agreement = (
            item[
                "council"
            ][
                "agreement"
            ]
        )

        answer = (
            f"What I found\n\n"
            f"{item['symbol']} is {item['price']} based on London Strategic Edge market data.\n\n"
            f"My current research models show "
            f"{agreement['POSITIVE']} positive, "
            f"{agreement['NEGATIVE']} negative and "
            f"{agreement['NEUTRAL']} neutral signals.\n\n"
            f"Overall view\n\n"
            f"{item['council']['overall']}.\n\n"
            f"What this means\n\n"
            f"This is evidence from current price history and deterministic models. "
            f"It is not a guarantee and it is not yet a trade order.\n\n"
            f"Current mode\n\n"
            f"Research / Paper Trading. No real money is being used."
        )

        return answer

    first = analyses[0]

    second = analyses[1]

    return (
        f"I checked both markets using London Strategic Edge.\n\n"
        f"{first['symbol']}: {first['price']} — "
        f"{first['council']['overall']}.\n\n"
        f"{second['symbol']}: {second['price']} — "
        f"{second['council']['overall']}.\n\n"
        f"I can run an individual strategy and historical test on either one before creating a Paper trade proposal."
    )

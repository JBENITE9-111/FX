from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
HEADERS = {"User-Agent": "Mozilla/5.0 FX-Research/1.0"}


def _company_score(row: dict[str, Any], query: str) -> tuple[int, int]:
    name = f"{row.get('longname', '')} {row.get('shortname', '')}".lower()
    terms = [term for term in query.lower().replace("-", " ").split() if len(term) > 2]
    asks_for_crypto = any(term in query.lower() for term in ("crypto", "bitcoin", "ethereum", "token"))
    quote_type = row.get("quoteType")
    preferred_type = 1 if (quote_type == "CRYPTOCURRENCY") == asks_for_crypto else 0
    return (preferred_type, sum(term in name for term in terms))


def lookup(query: str) -> dict[str, Any]:
    """Resolve a Yahoo Finance search result and its latest verified quote."""
    with httpx.Client(timeout=15, headers=HEADERS) as client:
        search = client.get(SEARCH_URL, params={"q": query, "quotesCount": 8, "newsCount": 5})
        search.raise_for_status()
        payload = search.json()
        quotes = payload.get("quotes") or []
        primary = max(quotes, key=lambda row: _company_score(row, query)) if quotes else None
        quote = None
        if primary and primary.get("symbol"):
            response = client.get(CHART_URL.format(symbol=primary["symbol"]), params={"range": "1d", "interval": "1m"})
            response.raise_for_status()
            results = (response.json().get("chart") or {}).get("result") or []
            if results:
                meta = results[0].get("meta") or {}
                timestamp = meta.get("regularMarketTime")
                quote = {
                    "symbol": meta.get("symbol") or primary.get("symbol"),
                    "name": meta.get("longName") or meta.get("shortName") or primary.get("longname") or primary.get("shortname"),
                    "quote_type": meta.get("instrumentType") or primary.get("quoteType"),
                    "exchange": meta.get("exchangeName"),
                    "currency": meta.get("currency"),
                    "price": meta.get("regularMarketPrice"),
                    "market_time": datetime.fromtimestamp(timestamp, timezone.utc).isoformat() if timestamp else None,
                }
        news = [{
            "title": item.get("title"), "source": item.get("publisher") or "Yahoo Finance",
            "url": item.get("link"), "published_at": datetime.fromtimestamp(item["providerPublishTime"], timezone.utc).isoformat() if item.get("providerPublishTime") else None,
        } for item in (payload.get("news") or [])[:5]]
        return {"source": "Yahoo Finance", "query": query, "quote": quote, "news": news}


def render_lookup(result: dict[str, Any]) -> str:
    quote = result.get("quote") or {}
    if quote.get("price") is None:
        return f"Yahoo Finance returned no verified public quote for {result.get('query')}. No price was invented."
    return (
        f"Yahoo Finance reports {quote.get('name')} ({quote.get('symbol')}) at "
        f"{quote.get('price')} {quote.get('currency') or ''}, market time {quote.get('market_time') or 'unavailable'}. "
        f"Instrument type: {quote.get('quote_type') or 'unavailable'}; exchange: {quote.get('exchange') or 'unavailable'}. "
        "This is market information, not a trade signal. No trade was sent."
    )

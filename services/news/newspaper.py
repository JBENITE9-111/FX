from __future__ import annotations

import email.utils
import html
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/macmac/Documents/Codex/FX")
OUTPUT = ROOT / "data" / "news" / "newspaper.json"
USER_AGENT = "Mozilla/5.0 FX-Global-Newspaper/2.0"

GOOGLE_QUERIES = [
    ("Markets", "global markets stocks forex bonds commodities oil gold bitcoin when:1d"),
    ("Economy", "inflation interest rates central bank GDP employment recession economy when:1d"),
    ("Politics & Geopolitics", "geopolitics sanctions tariffs trade war election conflict government markets when:1d"),
    ("Bloomberg", "site:bloomberg.com markets economy politics finance when:2d"),
    ("Reuters", "site:reuters.com markets economy politics finance when:2d"),
    ("Financial Times", "site:ft.com markets economy politics finance when:2d"),
    ("CNBC", "site:cnbc.com markets economy politics finance when:2d"),
    ("WSJ", "site:wsj.com markets economy politics finance when:2d"),
]

DIRECT_FEEDS = [
    ("Yahoo Finance", "Markets", "https://finance.yahoo.com/news/rssindex"),
    ("Federal Reserve", "Central Banks", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("BBC Business", "Economy", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC World", "Politics & Geopolitics", "https://feeds.bbci.co.uk/news/world/rss.xml"),
]

SOURCE_WEIGHT = {
    "Reuters": 10,
    "Bloomberg": 10,
    "Financial Times": 9,
    "WSJ": 9,
    "Federal Reserve": 10,
    "Yahoo Finance": 6,
    "CNBC": 7,
    "BBC Business": 7,
    "BBC World": 7,
}

KEYWORDS = {
    "federal reserve": 6,
    "interest rate": 5,
    "inflation": 5,
    "cpi": 5,
    "pce": 5,
    "jobs": 4,
    "payroll": 5,
    "gdp": 4,
    "recession": 5,
    "tariff": 5,
    "sanction": 5,
    "war": 4,
    "ceasefire": 4,
    "election": 4,
    "central bank": 5,
    "ecb": 5,
    "boj": 5,
    "boe": 5,
    "oil": 4,
    "gold": 3,
    "bitcoin": 4,
    "crypto": 3,
    "bond": 4,
    "yield": 4,
    "dollar": 4,
    "stocks": 3,
    "market": 3,
    "earnings": 3,
}

@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    category: str
    published_at: str | None
    timestamp: float
    aggregator: str
    relevance_score: float

def _download(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml,application/xml,text/xml,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()

def _timestamp(value: str | None) -> tuple[str | None, float]:
    if not value:
        return None, time.time()
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        return parsed.isoformat(), parsed.timestamp()
    except Exception:
        return value, time.time()

def _clean(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", "", value or ""))
    return " ".join(value.split())

def _score(title: str, source: str, timestamp: float) -> float:
    text = title.lower()
    score = float(SOURCE_WEIGHT.get(source, 5))

    for keyword, weight in KEYWORDS.items():
        if keyword in text:
            score += weight

    age_hours = max(0.0, (time.time() - timestamp) / 3600)
    score += max(0.0, 12.0 - age_hours / 2)
    return round(score, 2)

def _parse_rss(
    raw: bytes,
    *,
    fallback_source: str,
    category: str,
    aggregator: str,
) -> list[NewsItem]:
    root = ET.fromstring(raw)
    results = []

    for element in root.iter():
        if element.tag.split("}")[-1] != "item":
            continue

        fields = {}
        for child in list(element):
            fields[child.tag.split("}")[-1]] = (child.text or "").strip()

        title = _clean(fields.get("title", ""))
        link = fields.get("link", "")
        source = _clean(fields.get("source", "")) or fallback_source
        published = (
            fields.get("pubDate")
            or fields.get("published")
            or fields.get("date")
        )
        iso, ts = _timestamp(published)

        if title and link:
            results.append(
                NewsItem(
                    title=title,
                    url=link,
                    source=source,
                    category=category,
                    published_at=iso,
                    timestamp=ts,
                    aggregator=aggregator,
                    relevance_score=_score(title, source, ts),
                )
            )

    return results

def google_news_url(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote_plus(query)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

def refresh() -> dict:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    items: list[NewsItem] = []
    errors = []

    for category, query in GOOGLE_QUERIES:
        try:
            raw = _download(google_news_url(query))
            items.extend(
                _parse_rss(
                    raw,
                    fallback_source=category,
                    category=category,
                    aggregator="Google News RSS",
                )
            )
        except Exception as exc:
            errors.append({"source": category, "error": str(exc)})

    for source, category, url in DIRECT_FEEDS:
        try:
            raw = _download(url)
            items.extend(
                _parse_rss(
                    raw,
                    fallback_source=source,
                    category=category,
                    aggregator="Direct RSS",
                )
            )
        except Exception as exc:
            errors.append({"source": source, "error": str(exc)})

    unique = {}
    for item in items:
        key = re.sub(r"[^a-z0-9]+", " ", item.title.lower()).strip()
        current = unique.get(key)
        if current is None or item.relevance_score > current.relevance_score:
            unique[key] = item

    ordered = sorted(
        unique.values(),
        key=lambda item: (item.relevance_score, item.timestamp),
        reverse=True,
    )

    ordered = ordered[: int(os.getenv("FX_NEWSPAPER_MAX_ITEMS", "120"))]

    payload = {
        "generated_at": time.time(),
        "refresh_interval_seconds": int(
            os.getenv("FX_NEWSPAPER_REFRESH_SECONDS", "1800")
        ),
        "items": [asdict(item) for item in ordered],
        "errors": errors,
        "policy": (
            "Source-labelled headline metadata only. "
            "Original source links are preserved. "
            "No paywall bypass and no article-body scraping."
        ),
    }

    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp, OUTPUT)
    return payload

def load() -> dict:
    if not OUTPUT.exists():
        return refresh()
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception:
        return refresh()

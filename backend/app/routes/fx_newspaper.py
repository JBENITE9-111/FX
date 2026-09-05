from __future__ import annotations

import html
import time

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.news.newspaper import load

router = APIRouter()

@router.get("/api/newspaper")
def newspaper_api():
    return load()

def _render(data: dict, embedded: bool = False) -> str:
    age = max(
        0,
        int(
            (
                time.time()
                - data.get(
                    "generated_at",
                    time.time(),
                )
            )
            / 60
        ),
    )

    groups = {}
    for item in data.get("items", []):
        groups.setdefault(
            item.get(
                "category",
                "Latest",
            ),
            [],
        ).append(item)

    sections = []

    for category, items in groups.items():
        cards = []

        for item in items[:18]:
            cards.append(
                "<article class='story'>"
                f"<div class='src'>{html.escape(item.get('source','Unknown'))}</div>"
                f"<a href='{html.escape(item.get('url','#'))}' target='_blank' rel='noopener noreferrer'>"
                f"{html.escape(item.get('title',''))}</a>"
                f"<div class='meta'>Score {item.get('relevance_score',0)} · "
                f"{html.escape(item.get('published_at') or '')}</div>"
                "</article>"
            )

        sections.append(
            f"<section><h2>{html.escape(category)}</h2>"
            f"<div class='grid'>{''.join(cards)}</div></section>"
        )

    back = "" if embedded else "<nav><a href='/chat'>← FX Terminal</a></nav>"

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>FX Global Newspaper</title>
<style>
:root{{color-scheme:dark;--bg:#090a0b;--panel:#121417;--line:#2a2e33;--text:#f4f4f5;--muted:#9da3aa}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{width:min(1500px,96vw);margin:auto;padding:{'12px' if embedded else '28px'} 0 60px}}
nav{{margin-bottom:18px}} nav a{{color:var(--muted);text-decoration:none;font-size:12px}}
.head{{display:flex;justify-content:space-between;gap:20px;align-items:flex-end;border-bottom:1px solid var(--line);padding-bottom:18px}}
h1{{margin:0;font-size:{'24px' if embedded else '34px'};letter-spacing:-1px}}
.dek{{color:var(--muted);margin-top:7px;max-width:900px;line-height:1.5;font-size:12px}}
.age{{color:var(--muted);font-size:11px;white-space:nowrap}}
h2{{font-size:17px;border-bottom:1px solid var(--line);padding-bottom:8px;margin:28px 0 10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:9px}}
.story{{background:var(--panel);border:1px solid var(--line);padding:14px;min-height:115px}}
.src{{color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.7px;margin-bottom:9px}}
.story a{{color:var(--text);font-weight:650;text-decoration:none;line-height:1.35;font-size:14px}}
.story a:hover{{text-decoration:underline}}
.meta{{color:var(--muted);font-size:9px;margin-top:10px}}
</style>
</head>
<body>
<main>
{back}
<div class="head">
<div>
<h1>FX Global Newspaper</h1>
<div class="dek">
Ranked global finance, economics, central-bank and geopolitical headlines.
Updated every 30 minutes. Every item retains its original source.
</div>
</div>
<div class="age">Dataset age: {age} min</div>
</div>
{''.join(sections)}
</main>
</body>
</html>"""

@router.get("/newspaper", response_class=HTMLResponse)
def newspaper_page():
    return _render(load(), embedded=False)

@router.get("/newspaper/embed", response_class=HTMLResponse)
def newspaper_embed():
    return _render(load(), embedded=True)

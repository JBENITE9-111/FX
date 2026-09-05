from __future__ import annotations

import html
import time

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.paper_fleet.fleet import load_latest

router = APIRouter()

@router.get("/api/strategy-fleet")
def strategy_fleet_api():
    return load_latest()

@router.get("/strategy-fleet", response_class=HTMLResponse)
def strategy_fleet_page():
    data = load_latest()

    cards = []

    for item in data.get("strategies", []):
        cards.append(
            "<article class='card'>"
            f"<div class='top'><strong>{html.escape(item['strategy'])}</strong>"
            "<span>RUNNING · PAPER</span></div>"
            f"<div class='signal'>{html.escape(item['signal_name'])}</div>"
            "<div class='metrics'>"
            f"<div><small>Assigned</small><b>${item['capital_assigned']:.2f}</b></div>"
            f"<div><small>NAV</small><b>${item['nav']:.4f}</b></div>"
            f"<div><small>Observations</small><b>{item['observations']}</b></div>"
            f"<div><small>Signal changes</small><b>{item['signal_changes']}</b></div>"
            "</div>"
            f"<p>{html.escape(item['note'])}</p>"
            f"<p class='src'>Data: {html.escape(item.get('data_source',''))}</p>"
            "</article>"
        )

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

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="120">
<title>FX Paper Strategy Fleet</title>
<style>
:root{{color-scheme:dark;--bg:#090a0b;--panel:#121417;--line:#2a2e33;--text:#f4f4f5;--muted:#9da3aa}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{width:min(1500px,96vw);margin:auto;padding:28px 0 70px}}
nav{{margin-bottom:18px}} nav a{{color:var(--muted);text-decoration:none;font-size:12px}}
h1{{font-size:32px;margin:0;letter-spacing:-1px}}
.dek{{color:var(--muted);max-width:900px;line-height:1.5;margin:8px 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}}
.card{{background:var(--panel);border:1px solid var(--line);padding:16px}}
.top{{display:flex;justify-content:space-between;gap:10px}}
.top span{{color:var(--muted);font-size:9px;border:1px solid var(--line);border-radius:999px;padding:4px 7px}}
.signal{{font-size:24px;font-weight:750;margin:20px 0}}
.metrics{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.metrics div{{border-top:1px solid var(--line);padding-top:8px}}
small{{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;margin-bottom:4px}}
p{{color:var(--muted);font-size:11px;line-height:1.5;margin-bottom:0}}
.src{{font-size:9px}}
</style>
</head>
<body>
<main>
<nav><a href="/chat">← FX Terminal</a></nav>
<h1>FX Paper Strategy Fleet</h1>
<div class="dek">
Every strategy worker runs on schedule with its own $1 virtual paper account.
A strategy may remain NO_TRADE when its setup or required specialized data is absent.
No real-money orders are submitted. Dataset age: {age} minutes.
</div>
<div class="grid">{''.join(cards)}</div>
</main>
</body>
</html>"""

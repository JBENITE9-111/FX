from __future__ import annotations

import html
import time

from fastapi import APIRouter

from fastapi.responses import (
    HTMLResponse,
)

from services.bot_signals.store import (
    list_signals,
)


router = APIRouter()


@router.get(
    "/signals",
    response_class=HTMLResponse,
)
def signal_center():

    signals = list_signals(
        limit=200
    )

    cards = []

    for item in signals:

        direction = (
            item.get(
                "direction",
                "NO_TRADE",
            )
        )

        risk = item.get(
            "risk_status",
            "PENDING",
        )

        eligibility = item.get(
            "eligibility",
            "RESEARCH_ONLY",
        )

        created = float(
            item.get(
                "created_at",
                0,
            )
        )

        age = max(
            0,
            int(
                (
                    time.time()
                    - created
                )
                / 60
            ),
        )

        entry = item.get(
            "entry"
        )

        stop = item.get(
            "stop"
        )

        target_1 = item.get(
            "target_1"
        )

        target_2 = item.get(
            "target_2"
        )

        cards.append(
            f"""
            <article class="signal-card">

                <div class="head">

                    <div>
                        <div class="instrument">
                            {html.escape(item["instrument"])}
                        </div>

                        <div class="bot">
                            {html.escape(item["bot_name"])}
                        </div>
                    </div>

                    <div class="direction {direction.lower()}">
                        {html.escape(direction)}
                    </div>

                </div>

                <div class="grid">

                    <div>
                        <span>Strategy</span>
                        <strong>
                            {html.escape(item["strategy_id"])}
                        </strong>
                    </div>

                    <div>
                        <span>Score</span>
                        <strong>
                            {float(item["score"]):.1f}
                        </strong>
                    </div>

                    <div>
                        <span>Confidence</span>
                        <strong>
                            {(
                                float(
                                    item["confidence"]
                                    or 0
                                )
                                * 100
                            ):.0f}%
                        </strong>
                    </div>

                    <div>
                        <span>Risk</span>
                        <strong>
                            {html.escape(risk)}
                        </strong>
                    </div>

                    <div>
                        <span>Entry</span>
                        <strong>
                            {
                                f"{entry:.5f}"
                                if isinstance(
                                    entry,
                                    (int,float),
                                )
                                else "—"
                            }
                        </strong>
                    </div>

                    <div>
                        <span>Stop</span>
                        <strong>
                            {
                                f"{stop:.5f}"
                                if isinstance(
                                    stop,
                                    (int,float),
                                )
                                else "—"
                            }
                        </strong>
                    </div>

                    <div>
                        <span>Target 1</span>
                        <strong>
                            {
                                f"{target_1:.5f}"
                                if isinstance(
                                    target_1,
                                    (int,float),
                                )
                                else "—"
                            }
                        </strong>
                    </div>

                    <div>
                        <span>Target 2</span>
                        <strong>
                            {
                                f"{target_2:.5f}"
                                if isinstance(
                                    target_2,
                                    (int,float),
                                )
                                else "—"
                            }
                        </strong>
                    </div>

                </div>

                <p>
                    {html.escape(item["reason"])}
                </p>

                <div class="foot">

                    <span>
                        {html.escape(eligibility)}
                    </span>

                    <span>
                        {age} min ago
                    </span>

                </div>

            </article>
            """
        )

    if not cards:

        cards.append(
            """
            <div class="empty">
                No active signals yet.

                Start your scanners or click
                Scan Now in Trading Bots.
            </div>
            """
        )

    return f"""
    <!doctype html>

    <html>

    <head>

        <meta charset="utf-8">

        <meta
            name="viewport"
            content="width=device-width,initial-scale=1"
        >

        <meta
            http-equiv="refresh"
            content="30"
        >

        <title>
            FX Signal Center
        </title>

        <style>

            :root {{
                color-scheme:dark;

                --bg:#090a0b;
                --panel:#121417;
                --line:#2a2e33;
                --text:#f4f4f5;
                --muted:#989fa7;

                --positive:#70d69b;
                --negative:#ef8f8f;
            }}

            * {{
                box-sizing:border-box;
            }}

            body {{
                margin:0;
                background:var(--bg);
                color:var(--text);

                font-family:
                    Inter,
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    sans-serif;
            }}

            main {{
                width:min(
                    1500px,
                    96vw
                );

                margin:auto;

                padding:
                    28px
                    0
                    70px;
            }}

            nav {{
                margin-bottom:20px;
            }}

            nav a {{
                color:var(--muted);
                text-decoration:none;
                font-size:12px;
            }}

            h1 {{
                margin:0;
                font-size:32px;
                letter-spacing:-1px;
            }}

            .dek {{
                color:var(--muted);
                max-width:850px;
                line-height:1.5;
                margin:
                    8px
                    0
                    26px;
            }}

            .cards {{
                display:grid;

                grid-template-columns:
                    repeat(
                        auto-fit,
                        minmax(
                            320px,
                            1fr
                        )
                    );

                gap:10px;
            }}

            .signal-card {{
                border:
                    1px
                    solid
                    var(--line);

                background:
                    var(--panel);

                padding:16px;
            }}

            .head {{
                display:flex;
                justify-content:space-between;
                gap:14px;
                align-items:flex-start;
            }}

            .instrument {{
                font-size:21px;
                font-weight:750;
            }}

            .bot {{
                color:var(--muted);
                font-size:11px;
                margin-top:4px;
            }}

            .direction {{
                border:
                    1px
                    solid
                    var(--line);

                border-radius:6px;

                padding:
                    6px
                    9px;

                font-size:11px;
                font-weight:700;
            }}

            .direction.long {{
                color:
                    var(--positive);
            }}

            .direction.short {{
                color:
                    var(--negative);
            }}

            .grid {{
                display:grid;
                grid-template-columns:
                    1fr 1fr;

                gap:9px;

                margin-top:18px;
            }}

            .grid div {{
                border-top:
                    1px
                    solid
                    var(--line);

                padding-top:8px;
            }}

            .grid span {{
                display:block;
                color:var(--muted);
                font-size:9px;
                text-transform:uppercase;
                margin-bottom:4px;
            }}

            .grid strong {{
                font-size:13px;
            }}

            p {{
                color:var(--muted);
                font-size:11px;
                line-height:1.5;
            }}

            .foot {{
                display:flex;
                justify-content:space-between;
                color:var(--muted);
                font-size:9px;
            }}

            .empty {{
                border:
                    1px
                    solid
                    var(--line);

                padding:30px;

                color:var(--muted);
            }}

        </style>

    </head>

    <body>

        <main>

            <nav>
                <a href="/chat">
                    ← FX Terminal
                </a>
            </nav>

            <h1>
                FX Signal Center
            </h1>

            <div class="dek">

                Signals generated by your running
                market scanners.

                A candidate does not become a trade
                until strategy evidence,
                transaction costs,
                portfolio exposure and the
                deterministic Risk Engine agree.

            </div>

            <div class="cards">

                {''.join(cards)}

            </div>

        </main>

    </body>

    </html>
    """

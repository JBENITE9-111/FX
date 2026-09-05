from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get(
    "/bots",
    response_class=HTMLResponse,
)
async def bots():

    return """
<!DOCTYPE html>
<html>

<head>

<title>FX Bots</title>

<style>

body {
    margin: 0;
    background: #090a0c;
    color: #eee;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

main {
    max-width: 1100px;
    margin: auto;
    padding: 34px;
}

a {
    color: #aaa;
    text-decoration: none;
}

h1 {
    font-size: 30px;
    margin-bottom: 5px;
}

.subtitle {
    color: #8e949c;
    line-height: 1.6;
    max-width: 720px;
}

.grid {
    margin-top: 25px;

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                250px,
                1fr
            )
        );

    gap: 10px;
}

.card {
    background: #111317;
    border: 1px solid #2a2e33;
    border-radius: 10px;
    padding: 16px;
}

.title {
    font-size: 15px;
    font-weight: 700;
}

.meta {
    color: #787e86;
    font-size: 10px;
    margin-top: 5px;
}

.row {
    margin-top: 12px;
    font-size: 11px;
    color: #abb0b7;
    line-height: 1.6;
}

.status {
    margin-top: 13px;

    display: inline-block;

    border: 1px solid #33373d;

    border-radius: 6px;

    padding: 5px 7px;

    font-size: 9px;
}

button {
    margin-top: 14px;

    padding: 9px 12px;

    border-radius: 7px;

    border: 0;

    background: #eee;

    color: #111;

    cursor: pointer;

    font-weight: 700;
}

</style>

</head>

<body>

<main>

<a href="/chat">
← FX
</a>

<h1>
Trading Bots
</h1>

<div class="subtitle">

These bots continuously organize research and strategy logic.

They do not have permission to place a real-money trade by themselves.

When an eligible setup is found, FX creates a proposal for you to approve.

</div>

<div
id="grid"
class="grid"
></div>

</main>

<script>

fetch("/api/bots")
.then(r => r.json())
.then(data => {

    const grid =
        document
        .getElementById(
            "grid"
        );

    data.bots.forEach(
        bot => {

            const card =
                document
                .createElement(
                    "div"
                );

            card.className =
                "card";

            card.innerHTML = `

            <div class="title">
            ${bot.name}
            </div>

            <div class="meta">
            ${bot.markets}
            ·
            ${bot.timeframe}
            </div>

            <div class="row">

            Strategy:
            ${bot.strategy}

            <br>

            Mode:
            ${bot.mode}

            <br>

            Approval required:
            ${
                bot.requires_approval
                ? "Yes"
                : "No"
            }

            </div>

            <div class="status">
            ${bot.status}
            </div>

            <br>

            <button
            onclick="location.href='/strategies'"
            >
            Open Research
            </button>

            `;

            grid.appendChild(
                card
            );

        }
    );

});

</script>

</body>

</html>
"""

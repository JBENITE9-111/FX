from fastapi import (
    APIRouter,
)

from fastapi.responses import (
    HTMLResponse,
)


router = APIRouter()


EXECUTABLE = {
    "trend_following":
        "Trend Following",

    "momentum":
        "Momentum",

    "breakout":
        "20-Period Breakout",

    "mean_reversion":
        "Mean Reversion",

    "bollinger_reversion":
        "Bollinger Mean Reversion",

    "rsi_reversion":
        "RSI Reversion",

    "macd_trend":
        "MACD Trend",

    "volatility_breakout":
        "Volatility Breakout",

    "kalman_trend":
        "Kalman Trend",
}


@router.get(
    "/strategy/{strategy_id}",
    response_class=HTMLResponse,
)
async def strategy(
    strategy_id: str,
):

    name = EXECUTABLE.get(
        strategy_id,
        strategy_id
        .replace(
            "_",
            " "
        )
        .title(),
    )

    executable = (
        strategy_id
        in EXECUTABLE
    )

    return f"""
<!doctype html>

<html>

<head>

<title>
FX — {name}
</title>

<style>

* {{
box-sizing:border-box
}}

body {{
margin:0;
background:#090a0c;
color:#eee;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif
}}

header {{
height:62px;
border-bottom:1px solid #26292e;
display:flex;
align-items:center;
justify-content:space-between;
padding:0 24px
}}

main {{
max-width:1050px;
margin:auto;
padding:28px
}}

.back {{
color:#999;
text-decoration:none;
font-size:12px
}}

h1 {{
margin:10px 0 5px;
font-size:30px
}}

.subtitle {{
color:#8d9299;
margin-bottom:25px
}}

.controls {{
display:flex;
flex-wrap:wrap;
gap:8px;
margin-bottom:20px
}}

.catalog-status {{
width:100%;
color:#8d9299;
font-size:11px
}}

input,select {{
background:#15171a;
border:1px solid #30343a;
color:#fff;
padding:11px;
border-radius:8px
}}

button {{
background:#eee;
color:#111;
border:0;
border-radius:8px;
padding:11px 15px;
font-weight:700;
cursor:pointer
}}

.secondary {{
background:#15171a;
color:#ddd;
border:1px solid #30343a
}}

.grid {{
display:grid;
grid-template-columns:
repeat(
auto-fit,
minmax(220px,1fr)
);
gap:10px
}}

.card {{
border:1px solid #282c31;
background:#111317;
border-radius:9px;
padding:15px
}}

.label {{
color:#71767d;
font-size:10px;
text-transform:uppercase;
letter-spacing:.08em
}}

.value {{
font-size:21px;
font-weight:750;
margin-top:7px
}}

.text {{
font-size:12px;
color:#a1a6ad;
line-height:1.6;
margin-top:7px
}}

.proposal {{
margin-top:20px;
padding:18px;
border:1px solid #30343a;
border-radius:10px;
background:#111317;
display:none
}}

.warning {{
margin-top:20px;
font-size:11px;
color:#8e949b;
line-height:1.6;
border-top:1px solid #24272b;
padding-top:14px
}}

.ok {{
color:#8bd3a7
}}

.bad {{
color:#db9a9a
}}

</style>

</head>

<body>

<header>

<strong>
FX Strategy Workbench
</strong>

<div>
PAPER TRADING · NO REAL MONEY
</div>

</header>

<main>

<a
class="back"
href="/strategies"
>
← Strategy Library
</a>

<h1>
{name}
</h1>

<div class="subtitle">

{
"Real strategy engine connected to London Strategic Edge."
if executable
else
"This strategy is currently a research blueprint and has not yet been connected to automatic execution."
}

</div>

<div class="controls">

<select id="assetClass" onchange="changeAssetClass()" aria-label="Asset class">
<option>Stocks</option><option>ETFs</option><option>Indices</option><option>Forex</option>
<option>Commodities</option><option>Crypto</option><option>Futures</option>
</select>

<input id="instrumentSearch" placeholder="Search name or symbol" oninput="scheduleCatalogSearch()" aria-label="Search global instruments">

<select id="instrument" onchange="applyInstrument()" aria-label="Global instrument list"></select>

<input
id="symbol"
value="AAPL"
placeholder="Optional manual symbol"
aria-label="Selected or manual symbol"
>

<select
id="timeframe"
>
<option value="1d">
Daily
</option>

<option value="4h">
4 Hours
</option>

<option value="1h">
1 Hour
</option>
</select>

<button
onclick="analyse()"
>
Run Real Analysis
</button>

<div id="catalogStatus" class="catalog-status">Loading the global market catalog…</div>

</div>

<div
id="status"
class="text"
>
Ready.
</div>

<div
class="grid"
id="results"
></div>

<div
class="proposal"
id="proposal"
>

<h3>
Paper Trade Proposal
</h3>

<div
id="proposalText"
class="text"
></div>

<br>

<button
id="approveButton"
onclick="approveProposal()"
>
Approve Paper Trade
</button>

</div>

<div class="warning">

FX does not assume that a strategy is profitable merely because it produces a signal.

The data is real London Strategic Edge research data.

Backtests use historical data and include a basic fee assumption.

Paper Trading uses simulated capital.

Real-money execution is still disabled.

</div>

</main>

<script>

const strategyId =
"{strategy_id}";

let proposalId = null;
let catalogRows = [];
let catalogTimer = null;

function scheduleCatalogSearch() {{
    clearTimeout(catalogTimer);
    catalogTimer = setTimeout(loadCatalog, 250);
}}

async function changeAssetClass() {{
    document.getElementById("instrumentSearch").value = "";
    await loadCatalog();
}}

function applyInstrument() {{
    const row = catalogRows.find(item => item.instrument_id === document.getElementById("instrument").value);
    if (!row) return;
    document.getElementById("symbol").value = row.symbol;
    document.getElementById("timeframe").value = row.timeframe;
}}

async function loadCatalog() {{
    const assetClass = document.getElementById("assetClass").value;
    const query = document.getElementById("instrumentSearch").value.trim();
    const status = document.getElementById("catalogStatus");
    const params = new URLSearchParams({{asset_class:assetClass,limit:"100"}});
    if (query) params.set("q", query);
    status.textContent = "Searching the local global catalog…";
    try {{
        const response = await fetch("/api/learning/catalog?" + params.toString());
        if (!response.ok) throw new Error("catalog request failed");
        const payload = await response.json();
        catalogRows = payload.instruments || [];
        const select = document.getElementById("instrument");
        select.replaceChildren();
        catalogRows.forEach(item => select.add(new Option(item.name + " · " + item.symbol + " · " + item.market, item.instrument_id)));
        if (!catalogRows.length) select.add(new Option("No matching instruments", ""));
        const matched = Number(payload.matched || 0);
        status.textContent = matched.toLocaleString() + " matching " + assetClass.toLowerCase()
            + (matched > catalogRows.length ? " · showing first " + catalogRows.length : "")
            + " · search by name or symbol to narrow the list.";
        applyInstrument();
    }} catch {{
        status.textContent = "The global instrument catalog is temporarily unavailable.";
    }}
}}


function percent(value) {{

    if (
        value === null
        || value === undefined
    ) {{
        return "—";
    }}

    return (
        Number(value)
        * 100
    ).toFixed(2)
    + "%";

}}


async function analyse() {{

    const symbol =
        document
        .getElementById(
            "symbol"
        )
        .value
        .trim();

    const timeframe =
        document
        .getElementById(
            "timeframe"
        )
        .value;

    document
    .getElementById(
        "status"
    )
    .textContent =
        "Checking real market data and running the strategy...";

    const encoded =
        symbol
        .split("/")
        .map(
            encodeURIComponent
        )
        .join("/");

    try {{

        const response =
            await fetch(
                "/api/strategy-lab/"
                + strategyId
                + "/"
                + encoded
                + "?timeframe="
                + timeframe
            );

        const data =
            await response.json();

        if (!data.ok) {{

            document
            .getElementById(
                "status"
            )
            .textContent =
                data.message;

            return;
        }}

        document
        .getElementById(
            "status"
        )
        .innerHTML =
            '<span class="ok">✓ Real analysis complete</span>';

        const bt =
            data.backtest;

        const council =
            data.model_council;

        const analogues =
            data.historical_analogues;

        document
        .getElementById(
            "results"
        )
        .innerHTML = `

        <div class="card">
        <div class="label">
        Current Price
        </div>
        <div class="value">
        ${{data.latest_price}}
        </div>
        <div class="text">
        Source: London Strategic Edge
        </div>
        </div>

        <div class="card">
        <div class="label">
        Current Strategy Position
        </div>
        <div class="value">
        ${{
            bt.current_position === 1
            ? "LONG"
            :
            bt.current_position === -1
            ? "SHORT"
            : "NO TRADE"
        }}
        </div>
        </div>

        <div class="card">
        <div class="label">
        Historical Return
        </div>
        <div class="value">
        ${{percent(bt.total_return)}}
        </div>
        <div class="text">
        Historical only. Not a forecast.
        </div>
        </div>

        <div class="card">
        <div class="label">
        Maximum Historical Drawdown
        </div>
        <div class="value">
        ${{percent(bt.max_drawdown)}}
        </div>
        </div>

        <div class="card">
        <div class="label">
        Historical Win Rate
        </div>
        <div class="value">
        ${{percent(bt.win_rate)}}
        </div>
        </div>

        <div class="card">
        <div class="label">
        Historical Trades
        </div>
        <div class="value">
        ${{bt.trades}}
        </div>
        </div>

        <div class="card">
        <div class="label">
        Model Council
        </div>
        <div class="value">
        ${{council.overall}}
        </div>
        <div class="text">
        Positive:
        ${{council.agreement.POSITIVE}}
        · Negative:
        ${{council.agreement.NEGATIVE}}
        · Neutral:
        ${{council.agreement.NEUTRAL}}
        </div>
        </div>

        <div class="card">
        <div class="label">
        Historical Analogues
        </div>
        <div class="value">
        ${{
            analogues.available
            ?
            analogues.positive_matches
            + "/"
            + analogues.total_matches
            + " positive"
            :
            "Not enough data"
        }}
        </div>
        <div class="text">
        Similar historical situations only.
        </div>
        </div>
        `;

        if (
            bt.current_position === 1
            && !symbol.includes("/")
        ) {{

            const button =
                document.createElement(
                    "button"
                );

            button.textContent =
                "Create Paper Trade Proposal";

            button.className =
                "secondary";

            button.onclick =
                createProposal;

            document
            .getElementById(
                "results"
            )
            .appendChild(
                button
            );

        }}

    }}

    catch {{

        document
        .getElementById(
            "status"
        )
        .textContent =
            "FX could not finish the strategy analysis.";

    }}

}}


async function createProposal() {{

    const symbol =
        document
        .getElementById(
            "symbol"
        )
        .value
        .trim()
        .toUpperCase();

    const response =
        await fetch(
            "/api/strategy-lab/"
            + strategyId
            + "/"
            + encodeURIComponent(
                symbol
            )
            + "/propose-paper",
            {{
                method:"POST"
            }}
        );

    const data =
        await response.json();

    if (!data.ok) {{

        alert(
            data.message
        );

        return;
    }}

    const p =
        data.proposal;

    proposalId =
        p.id;

    document
    .getElementById(
        "proposal"
    )
    .style.display =
        "block";

    document
    .getElementById(
        "proposalText"
    )
    .innerHTML = `

    <strong>
    ${{p.side}}
    ${{p.quantity}}
    shares of
    ${{p.symbol}}
    </strong>

    <br><br>

    Reference price:
    $${{Number(
        p.reference_entry
    ).toFixed(2)}}

    <br>

    Protection level:
    $${{Number(
        p.stop_loss
    ).toFixed(2)}}

    <br>

    Possible profit target:
    $${{Number(
        p.take_profit
    ).toFixed(2)}}

    <br>

    Planned maximum risk:
    $${{Number(
        p.planned_risk_dollars
    ).toFixed(2)}}

    <br><br>

    This is an FX LOCAL PAPER trade.
    No real money will be used.
    `;

}}


async function approveProposal() {{

    if (!proposalId) {{
        return;
    }}

    const confirmed =
        confirm(
            "Approve this PAPER trade? No real money will be used."
        );

    if (!confirmed) {{
        return;
    }}

    const response =
        await fetch(
            "/api/strategy-lab/proposals/"
            + proposalId
            + "/approve",
            {{
                method:"POST"
            }}
        );

    const data =
        await response.json();

    if (!data.ok) {{

        alert(
            data.message
        );

        return;
    }}

    document
    .getElementById(
        "proposalText"
    )
    .innerHTML +=
        "<br><br><strong class='ok'>✓ Paper proposal approved. Use FX Local Paper Trading for execution.</strong>";

    document
    .getElementById(
        "approveButton"
    )
    .disabled =
        true;

}}

loadCatalog();

</script>


<a
 href="/terminal"
 style="
   position:fixed;
   bottom:18px;
   right:18px;
   z-index:9999;
   background:#f3f3f3;
   color:#111;
   padding:9px 13px;
   border-radius:7px;
   text-decoration:none;
   font-size:12px;
   font-weight:700;
   border:1px solid #666;
 "
>
Terminal
</a>

</body>

</html>
"""

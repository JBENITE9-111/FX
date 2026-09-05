from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get(
    "/markets",
    response_class=HTMLResponse,
)
async def markets():

    return r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>FX — Global Markets</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    width: 100%;
    height: 100%;
}

body {
    background: #090a0c;
    color: #eceef0;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

button,
input,
select {
    font: inherit;
}

.shell {
    height: 100vh;
    display: grid;
    grid-template-columns:
        220px
        380px
        minmax(500px, 1fr);
}

.sidebar {
    border-right: 1px solid #24272b;
    padding: 18px 12px;
    position: relative;
}

.brand {
    font-size: 21px;
    font-weight: 760;
    padding: 0 8px 20px;
}

.nav {
    display: block;
    width: 100%;
    border: 0;
    background: transparent;
    color: #b7bbc1;
    text-align: left;
    text-decoration: none;
    padding: 9px 9px;
    border-radius: 7px;
    font-size: 13px;
}

.nav:hover,
.nav.active {
    background: #15171b;
    color: white;
}

.section {
    margin:
        25px
        9px
        8px;
    color: #6f747c;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: .09em;
}

.paper {
    position: absolute;
    bottom: 15px;
    left: 12px;
    right: 12px;
    border: 1px solid #2a2e33;
    border-radius: 8px;
    padding: 11px;
    background: #121418;
}

.paper strong {
    font-size: 11px;
}

.paper div {
    color: #81868e;
    font-size: 10px;
    margin-top: 4px;
    line-height: 1.5;
}

.explorer {
    border-right: 1px solid #24272b;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.explorer-header {
    height: 64px;
    border-bottom: 1px solid #24272b;
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.explorer-title {
    font-size: 13px;
    font-weight: 700;
}

.connected {
    font-size: 10px;
    color: #8fd5ab;
}

.search-wrap {
    padding: 14px;
    border-bottom: 1px solid #24272b;
}

.search {
    width: 100%;
    background: #14161a;
    border: 1px solid #30343a;
    color: white;
    outline: none;
    padding: 11px 12px;
    border-radius: 9px;
}

.categories {
    display: flex;
    gap: 6px;
    padding-top: 9px;
    overflow-x: auto;
}

.category {
    white-space: nowrap;
    border: 1px solid #292d32;
    background: #111317;
    color: #aeb3ba;
    border-radius: 7px;
    padding: 6px 9px;
    cursor: pointer;
    font-size: 10px;
}

.category.active {
    background: #e9e9e9;
    color: #111;
}

.results {
    overflow-y: auto;
    flex: 1;
}

.result {
    padding: 12px 15px;
    border-bottom: 1px solid #1b1e21;
    cursor: pointer;
}

.result:hover {
    background: #121417;
}

.result-symbol {
    font-size: 13px;
    font-weight: 720;
}

.result-name {
    color: #979ca4;
    font-size: 11px;
    margin-top: 3px;
}

.result-meta {
    display: flex;
    gap: 8px;
    margin-top: 5px;
    color: #626870;
    font-size: 9px;
}

.workspace {
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.topbar {
    height: 64px;
    border-bottom: 1px solid #24272b;
    padding: 0 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.instrument-name {
    font-weight: 720;
}

.source {
    font-size: 10px;
    color: #777d85;
}

.instrument-head {
    padding: 22px 24px 12px;
}

.symbol-big {
    font-size: 22px;
    font-weight: 750;
}

.name-big {
    color: #979ca3;
    font-size: 12px;
    margin-top: 4px;
}

.price-big {
    margin-top: 12px;
    font-size: 31px;
    font-weight: 760;
    font-variant-numeric: tabular-nums;
}

.timeframes {
    display: flex;
    gap: 5px;
    padding: 10px 24px;
    flex-wrap: wrap;
}

.tf {
    border: 1px solid #2a2e33;
    background: #111317;
    color: #a5abb2;
    padding: 6px 9px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 10px;
}

.tf.active {
    background: #ececec;
    color: #111;
}

.chart-area {
    padding: 8px 20px 10px;
    height: 390px;
}

#chart {
    width: 100%;
    height: 100%;
}

.chart-message {
    color: #858b93;
    padding: 40px;
    text-align: center;
}

.tabs {
    display: flex;
    gap: 6px;
    padding: 8px 24px;
    border-top: 1px solid #202327;
    border-bottom: 1px solid #202327;
    overflow-x: auto;
}

.tab {
    border: 0;
    background: transparent;
    color: #8e949b;
    padding: 8px 7px;
    cursor: pointer;
    font-size: 11px;
}

.tab.active {
    color: white;
}

.details {
    flex: 1;
    overflow: auto;
    padding: 16px 24px;
}

.details-title {
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

.details-text {
    color: #949aa2;
    line-height: 1.6;
    font-size: 11px;
}

canvas {
    width: 100%;
    height: 100%;
}

@media(max-width: 1050px) {

    .shell {
        grid-template-columns:
            190px
            320px
            1fr;
    }

}

</style>

</head>

<body>

<div class="shell">

<div class="sidebar">

    <div class="brand">
        FX
    </div>

    <a
        class="nav"
        href="/chat"
    >
        Chat
    </a>

    <div class="section">
        Markets
    </div>

    <a
        class="nav active"
        href="/markets"
    >
        Global Market Explorer
    </a>

    <button
        class="nav"
        onclick="chooseCategory('stock')"
    >
        Stocks
    </button>

    <button
        class="nav"
        onclick="chooseCategory('forex')"
    >
        Forex
    </button>

    <button
        class="nav"
        onclick="chooseCategory('crypto')"
    >
        Crypto
    </button>

    <button
        class="nav"
        onclick="chooseCategory('commodity')"
    >
        Commodities
    </button>

    <button
        class="nav"
        onclick="chooseCategory('etf')"
    >
        ETFs
    </button>

    <button
        class="nav"
        onclick="chooseCategory('index')"
    >
        Indices
    </button>

    <button
        class="nav"
        onclick="chooseCategory('futures')"
    >
        Futures
    </button>

    <button
        class="nav"
        onclick="chooseCategory('options')"
    >
        Options
    </button>

    <div class="section">
        Research
    </div>

    <a
        class="nav"
        href="/chat"
    >
        Ask FX
    </a>

    <div class="paper">

        <strong>
            PAPER TRADING
        </strong>

        <div>
            Research uses real market data.
            Trading uses simulated money.
            Real-money trading remains disabled.
        </div>

    </div>

</div>

<div class="explorer">

    <div class="explorer-header">

        <div class="explorer-title">
            Global Markets
        </div>

        <div
            class="connected"
            id="connection"
        >
            Checking LSE...
        </div>

    </div>

    <div class="search-wrap">

        <input
            id="search"
            class="search"
            placeholder="Search Apple, gold, EUR/USD, Bitcoin..."
        >

        <div class="categories">

            <button
                class="category active"
                data-category=""
            >
                All
            </button>

            <button
                class="category"
                data-category="stock"
            >
                Stocks
            </button>

            <button
                class="category"
                data-category="forex"
            >
                Forex
            </button>

            <button
                class="category"
                data-category="crypto"
            >
                Crypto
            </button>

            <button
                class="category"
                data-category="commodity"
            >
                Commodities
            </button>

            <button
                class="category"
                data-category="etf"
            >
                ETFs
            </button>

            <button
                class="category"
                data-category="index"
            >
                Indices
            </button>

            <button
                class="category"
                data-category="futures"
            >
                Futures
            </button>

        </div>

    </div>

    <div
        class="results"
        id="results"
    ></div>

</div>

<div class="workspace">

    <div class="topbar">

        <div class="instrument-name">
            Market Evidence
        </div>

        <div class="source">
            Research source: London Strategic Edge
        </div>

    </div>

    <div class="instrument-head">

        <div
            class="symbol-big"
            id="symbol"
        >
            Select a market
        </div>

        <div
            class="name-big"
            id="name"
        >
            Search thousands of instruments on the left.
        </div>

        <div
            class="price-big"
            id="price"
        >
            —
        </div>

    </div>

    <div class="timeframes">

        <button class="tf" data-tf="1m">
            1m
        </button>

        <button class="tf" data-tf="5m">
            5m
        </button>

        <button class="tf" data-tf="15m">
            15m
        </button>

        <button class="tf active" data-tf="1h">
            1H
        </button>

        <button class="tf" data-tf="4h">
            4H
        </button>

        <button class="tf" data-tf="1d">
            1D
        </button>

        <button class="tf" data-tf="1w">
            1W
        </button>

        <button class="tf" data-tf="1mo">
            1M
        </button>

    </div>

    <div class="chart-area">

        <canvas id="chart"></canvas>

    </div>

    <div class="tabs">

        <button class="tab active">
            Overview
        </button>

        <button class="tab">
            History
        </button>

        <button class="tab">
            Company
        </button>

        <button class="tab">
            Fundamentals
        </button>

        <button class="tab">
            Options
        </button>

        <button class="tab">
            Macro
        </button>

        <button class="tab">
            Raw Data
        </button>

    </div>

    <div class="details">

        <div class="details-title">
            About this market
        </div>

        <div
            class="details-text"
            id="details"
        >
            Choose an instrument to load its real historical market data.
        </div>

    </div>

</div>

</div>

<script>

let selectedSymbol = null;
let selectedName = null;
let selectedDataset = null;
let selectedTimeframe = "1h";
let selectedCategory = "";

const search =
    document.getElementById("search");

const results =
    document.getElementById("results");


async function checkConnection() {

    try {

        const r =
            await fetch(
                "/api/global/status"
            );

        const data =
            await r.json();

        document.getElementById(
            "connection"
        ).textContent =
            data.ok
            ? "● London Edge connected"
            : "● London Edge unavailable";

    }

    catch {

        document.getElementById(
            "connection"
        ).textContent =
            "● London Edge unavailable";

    }

}


function chooseCategory(category) {

    selectedCategory = category;

    document
        .querySelectorAll(
            ".category"
        )
        .forEach(
            button => {

                button.classList.toggle(
                    "active",
                    button.dataset.category
                        === category
                );

            }
        );

    loadSearch();

}


document
    .querySelectorAll(
        ".category"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    chooseCategory(
                        button.dataset.category
                    );

                }
            );

        }
    );


let searchTimer = null;

search.addEventListener(
    "input",
    () => {

        clearTimeout(
            searchTimer
        );

        searchTimer =
            setTimeout(
                loadSearch,
                250
            );

    }
);


async function loadSearch() {

    results.innerHTML =
        '<div class="chart-message">Searching global markets...</div>';

    const params =
        new URLSearchParams();

    if (search.value.trim()) {
        params.set(
            "q",
            search.value.trim()
        );
    }

    if (selectedCategory) {
        params.set(
            "category",
            selectedCategory
        );
    }

    params.set(
        "limit",
        "150"
    );

    try {

        const r =
            await fetch(
                "/api/global/search?"
                + params.toString()
            );

        const data =
            await r.json();

        results.innerHTML = "";

        if (
            !data.ok
            || !data.results
            || !data.results.length
        ) {

            results.innerHTML =
                '<div class="chart-message">No matching markets found.</div>';

            return;

        }

        data.results.forEach(
            item => {

                const row =
                    document.createElement(
                        "div"
                    );

                row.className =
                    "result";

                row.innerHTML =
                    `
                    <div class="result-symbol">
                        ${escapeHtml(item.symbol)}
                    </div>

                    <div class="result-name">
                        ${escapeHtml(item.name || "")}
                    </div>

                    <div class="result-meta">
                        <span>
                            ${escapeHtml(item.category || item.dataset || "")}
                        </span>

                        <span>
                            ${escapeHtml(item.country || "")}
                        </span>
                    </div>
                    `;

                row.onclick =
                    () => selectInstrument(
                        item
                    );

                results.appendChild(
                    row
                );

            }
        );

    }

    catch {

        results.innerHTML =
            '<div class="chart-message">FX could not search the market catalog.</div>';

    }

}


function selectInstrument(item) {

    selectedSymbol =
        item.symbol;

    selectedName =
        item.name;

    selectedDataset =
        item.dataset || null;

    document.getElementById(
        "symbol"
    ).textContent =
        selectedSymbol;

    document.getElementById(
        "name"
    ).textContent =
        selectedName || "";

    document.getElementById(
        "details"
    ).textContent =
        (
            "Category: "
            + (
                item.category
                || "Unknown"
            )
            + (
                item.country
                ? " · Country: "
                  + item.country
                : ""
            )
            + (
                item.first
                ? " · History begins: "
                  + item.first
                : ""
            )
        );

    loadChart();

}


document
    .querySelectorAll(
        ".tf"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    selectedTimeframe =
                        button.dataset.tf;

                    document
                        .querySelectorAll(
                            ".tf"
                        )
                        .forEach(
                            x =>
                                x.classList.remove(
                                    "active"
                                )
                        );

                    button.classList.add(
                        "active"
                    );

                    loadChart();

                }
            );

        }
    );


async function loadChart() {

    if (!selectedSymbol) {
        return;
    }

    document.getElementById(
        "price"
    ).textContent =
        "Loading...";

    const encoded =
        selectedSymbol
            .split("/")
            .map(
                encodeURIComponent
            )
            .join("/");

    let url =
        "/api/global/chart/"
        + encoded
        + "?timeframe="
        + encodeURIComponent(
            selectedTimeframe
        )
        + "&limit=400";

    if (selectedDataset) {

        url +=
            "&dataset="
            + encodeURIComponent(
                selectedDataset
            );

    }

    try {

        const r =
            await fetch(url);

        const data =
            await r.json();

        if (!data.ok) {

            document.getElementById(
                "price"
            ).textContent =
                "Unavailable";

            drawMessage(
                data.message
                || "No market history was returned."
            );

            return;

        }

        if (
            data.latest_price
            !== undefined
            && data.latest_price
            !== null
        ) {

            document.getElementById(
                "price"
            ).textContent =
                formatNumber(
                    data.latest_price
                );

        }

        drawCandles(
            data.bars
        );

    }

    catch {

        document.getElementById(
            "price"
        ).textContent =
            "Unavailable";

        drawMessage(
            "FX could not load this market chart."
        );

    }

}


function drawMessage(message) {

    const canvas =
        document.getElementById("chart");

    const ctx =
        canvas.getContext("2d");

    resizeCanvas(canvas);

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    ctx.fillStyle =
        "#81868e";

    ctx.font =
        "14px -apple-system";

    ctx.textAlign =
        "center";

    ctx.fillText(
        message,
        canvas.width / 2,
        canvas.height / 2
    );

}


function extractNumber(
    row,
    names
) {

    for (const name of names) {

        if (
            row[name]
            !== undefined
            && row[name]
            !== null
        ) {

            const value =
                Number(
                    row[name]
                );

            if (
                Number.isFinite(
                    value
                )
            ) {
                return value;
            }

        }

    }

    return null;

}


function drawCandles(bars) {

    const canvas =
        document.getElementById(
            "chart"
        );

    resizeCanvas(canvas);

    const ctx =
        canvas.getContext(
            "2d"
        );

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    const parsed = [];

    for (const row of bars) {

        const open =
            extractNumber(
                row,
                ["open", "o"]
            );

        const high =
            extractNumber(
                row,
                ["high", "h"]
            );

        const low =
            extractNumber(
                row,
                ["low", "l"]
            );

        const close =
            extractNumber(
                row,
                ["close", "c"]
            );

        if (
            open === null
            || high === null
            || low === null
            || close === null
        ) {
            continue;
        }

        parsed.push({
            open,
            high,
            low,
            close,
        });

    }

    if (!parsed.length) {

        drawMessage(
            "No chartable price history was returned."
        );

        return;

    }

    const recent =
        parsed.slice(-180);

    const min =
        Math.min(
            ...recent.map(
                x => x.low
            )
        );

    const max =
        Math.max(
            ...recent.map(
                x => x.high
            )
        );

    const range =
        Math.max(
            max - min,
            0.0000001
        );

    const padX = 12;
    const padY = 15;

    const usableW =
        canvas.width
        - padX * 2;

    const usableH =
        canvas.height
        - padY * 2;

    const step =
        usableW
        / recent.length;

    const y =
        value =>
            padY
            + (
                max - value
            )
            / range
            * usableH;

    ctx.strokeStyle =
        "#202327";

    ctx.lineWidth = 1;

    for (
        let i = 1;
        i < 5;
        i++
    ) {

        const gy =
            (
                canvas.height
                / 5
            )
            * i;

        ctx.beginPath();

        ctx.moveTo(
            0,
            gy
        );

        ctx.lineTo(
            canvas.width,
            gy
        );

        ctx.stroke();

    }

    recent.forEach(
        (
            bar,
            index
        ) => {

            const x =
                padX
                + index
                * step
                + step / 2;

            const highY =
                y(bar.high);

            const lowY =
                y(bar.low);

            const openY =
                y(bar.open);

            const closeY =
                y(bar.close);

            const rising =
                bar.close
                >= bar.open;

            ctx.strokeStyle =
                rising
                ? "#b8c7bd"
                : "#737c87";

            ctx.fillStyle =
                rising
                ? "#b8c7bd"
                : "#737c87";

            ctx.beginPath();

            ctx.moveTo(
                x,
                highY
            );

            ctx.lineTo(
                x,
                lowY
            );

            ctx.stroke();

            const bodyWidth =
                Math.max(
                    step * 0.55,
                    1
                );

            const bodyTop =
                Math.min(
                    openY,
                    closeY
                );

            const bodyHeight =
                Math.max(
                    Math.abs(
                        closeY
                        - openY
                    ),
                    1
                );

            ctx.fillRect(
                x
                - bodyWidth / 2,
                bodyTop,
                bodyWidth,
                bodyHeight
            );

        }
    );

}


function resizeCanvas(
    canvas
) {

    const rect =
        canvas.getBoundingClientRect();

    const dpr =
        window.devicePixelRatio
        || 1;

    canvas.width =
        Math.floor(
            rect.width
            * dpr
        );

    canvas.height =
        Math.floor(
            rect.height
            * dpr
        );

    const ctx =
        canvas.getContext("2d");

    ctx.setTransform(
        dpr,
        0,
        0,
        dpr,
        0,
        0
    );

    canvas.width =
        rect.width;

    canvas.height =
        rect.height;

}


function escapeHtml(text) {

    return String(
        text ?? ""
    )
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");

}


function formatNumber(value) {

    const n =
        Number(value);

    if (
        !Number.isFinite(n)
    ) {
        return "—";
    }

    if (
        Math.abs(n)
        >= 1000
    ) {

        return n.toLocaleString(
            undefined,
            {
                maximumFractionDigits: 2,
            }
        );

    }

    if (
        Math.abs(n)
        >= 1
    ) {

        return n.toLocaleString(
            undefined,
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 5,
            }
        );

    }

    return n.toLocaleString(
        undefined,
        {
            maximumFractionDigits: 8,
        }
    );

}


checkConnection();

loadSearch();

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

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get(
    "/chat",
    response_class=HTMLResponse,
)
async def chat():

    return r"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>FX</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    width: 100%;
    height: 100%;
    margin: 0;
}

body {
    background: #0b0c0e;
    color: #ececec;
    overflow: hidden;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

button,
textarea {
    font-family: inherit;
}

.shell {
    height: 100vh;
    display: grid;
    grid-template-columns:
        230px
        minmax(480px, 1fr)
        390px;
}

.sidebar {
    background: #090a0b;
    border-right: 1px solid #202226;
    padding: 18px 12px;
    height: 100vh;
    min-height: 0;
    overflow: hidden;
}

.brand {
    font-size: 20px;
    font-weight: 750;
    padding: 8px 10px 22px;
}

.new-chat {
    width: 100%;
    border: 1px solid #282b30;
    background: #131519;
    color: white;
    padding: 11px 12px;
    border-radius: 9px;
    text-align: left;
    cursor: pointer;
}

.section-title {
    margin: 27px 10px 10px;
    color: #70747c;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .08em;
}

.market {
    padding: 9px 10px;
    border-radius: 7px;
    font-size: 14px;
    color: #b6bac1;
    cursor: pointer;
}

.market:hover {
    background: #15171a;
    color: white;
}

.mode-card {
    position: absolute;
    bottom: 20px;
    left: 12px;
    width: 205px;
    border: 1px solid #292c31;
    border-radius: 9px;
    padding: 12px;
    background: #111316;
}

.mode-card strong {
    font-size: 12px;
}

.mode-card p {
    color: #8c9199;
    font-size: 11px;
    line-height: 1.5;
    margin: 5px 0 0;
}

.main {
    min-width: 0;
    min-height: 0;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.topbar {
    height: 62px;
    border-bottom: 1px solid #202226;
    padding: 0 23px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.title {
    font-weight: 650;
}

.paper {
    border: 1px solid #33363c;
    background: #15171a;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 11px;
    color: #b5bac1;
}

.messages {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 35px max(30px, 8%);
}

.welcome {
    max-width: 680px;
    margin: 12vh auto 0;
}

.welcome h1 {
    font-size: 33px;
    letter-spacing: -1px;
    margin: 0 0 10px;
}

.welcome p {
    color: #92969d;
    line-height: 1.6;
}

.quick-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 9px;
    margin-top: 28px;
}

.quick {
    border: 1px solid #292c31;
    border-radius: 10px;
    padding: 14px;
    background: #111316;
    color: #c5c9ce;
    cursor: pointer;
    font-size: 13px;
    line-height: 1.4;
}

.quick:hover {
    background: #17191d;
}

.message {
    max-width: 760px;
    margin: 0 auto 29px;
    line-height: 1.7;
    font-size: 15px;
}

.message.user {
    display: flex;
    justify-content: flex-end;
}

.user-bubble {
    background: #202226;
    border: 1px solid #30333a;
    border-radius: 15px;
    padding: 12px 16px;
    max-width: 78%;
}

.fx-name {
    font-size: 12px;
    color: #8f949b;
    margin-bottom: 8px;
    font-weight: 650;
}

.fx-answer {
    white-space: pre-wrap;
}

.composer-wrap {
    padding:
        13px
        max(30px, 8%)
        22px;
    background:
        linear-gradient(
            transparent,
            #0b0c0e 24%
        );
}

.composer {
    max-width: 780px;
    margin: auto;
    border: 1px solid #34373d;
    border-radius: 16px;
    background: #15171a;
    padding: 10px;
    display: flex;
    align-items: flex-end;
}

textarea {
    flex: 1;
    resize: none;
    background: transparent;
    border: 0;
    outline: none;
    color: white;
    padding: 10px;
    min-height: 45px;
    max-height: 150px;
    font-size: 15px;
}

.send {
    border: 0;
    border-radius: 9px;
    padding: 10px 14px;
    background: #f1f1f1;
    color: #111;
    font-weight: 650;
    cursor: pointer;
}

.helper {
    max-width: 780px;
    margin: 7px auto 0;
    text-align: center;
    color: #646970;
    font-size: 10px;
}

.inspector {
    border-left: 1px solid #202226;
    background: #0d0f11;
    height: 100vh;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.inspector-head {
    height: 62px;
    padding: 0 18px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #202226;
    font-size: 13px;
    font-weight: 650;
}

.status {
    padding: 14px 18px;
    border-bottom: 1px solid #202226;
}

.status-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
}

.status-item {
    background: #131519;
    border: 1px solid #25282d;
    padding: 9px;
    border-radius: 7px;
    font-size: 11px;
}

.dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 6px;
    background: #666;
}

.dot.ok {
    background: #7bc89c;
}

.dot.no {
    background: #d18b8b;
}

.chart-controls {
    padding: 13px 17px;
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.symbol {
    border: 1px solid #2a2d32;
    background: #131519;
    color: #aeb3ba;
    border-radius: 7px;
    padding: 7px 10px;
    cursor: pointer;
    font-size: 11px;
}

.symbol:hover {
    color: white;
}

.chart-title {
    padding: 4px 18px;
}

.chart-symbol {
    font-size: 17px;
    font-weight: 700;
}

.chart-price {
    font-size: 24px;
    font-weight: 700;
    margin-top: 5px;
}

.chart-source {
    color: #6f747b;
    font-size: 10px;
    margin-top: 4px;
}

#chart {
    width: 100%;
    height: 330px;
    padding: 10px 12px;
}

.chart-note {
    padding: 12px 18px;
    color: #7b8087;
    font-size: 11px;
    line-height: 1.5;
}

svg {
    width: 100%;
    height: 100%;
    overflow: visible;
}

.grid-line {
    stroke: #24272b;
    stroke-width: 1;
}

.candle-up {
    fill: #a8b9ae;
}

.candle-down {
    fill: #7d858f;
}

.wick {
    stroke: #8e969f;
    stroke-width: 1;
}

@media(max-width: 1100px) {

    .shell {
        grid-template-columns:
            200px
            1fr;
    }

    .inspector {
        display: none;
    }

}

@media(max-width: 720px) {

    .shell {
        display: block;
    }

    .sidebar {
        display: none;
    }

    .main {
        height: 100vh;
    }

    .quick-grid {
        grid-template-columns: 1fr;
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

    <button
        class="new-chat"
        onclick="location.reload()"
    >
        + New conversation
    </button>

    <div class="section-title">
        Markets
    </div>

    <div
        class="market"
        onclick="loadChart('AAPL')"
    >
        Apple
    </div>

    <div
        class="market"
        onclick="loadChart('NVDA')"
    >
        Nvidia
    </div>

    <div
        class="market"
        onclick="loadChart('SPY')"
    >
        S&P 500
    </div>

    <div
        class="market"
        onclick="loadChart('TSLA')"
    >
        Tesla
    </div>

    <div
        class="market"
        onclick="loadChart('XAUUSD')"
    >
        Gold
    </div>

    <div class="section-title">
        Research
    </div>

    <div
        class="market"
        onclick="location.href='/markets'"
    >
        Global Market Explorer
    </div>

    <div
        class="market"
        onclick="location.href='/hedge-funds'"
    >
        Hedge Fund Intelligence
    </div>

    <div
        class="market"
        onclick="location.href='/brains'"
    >
        Model Council
    </div>

    <div
        class="market"
        onclick="location.href='/strategies'"
    >
        Strategies
    </div>

    <div
        class="market"
        role="button"
        tabindex="0"
        onclick="location.href='/paper-local'"
        onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();location.href='/paper-local'}"
    >
        Paper Portfolio
    </div>

    <div
        class="market"
        role="button"
        tabindex="0"
        onclick="location.href='/journal'"
        onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();location.href='/journal'}"
    >
        Journal
    </div>

    <div class="mode-card">

        <strong>
            PAPER TRADING
        </strong>

        <p>
            Real market information.
            Simulated money.
            Real-money trading is disabled.
        </p>

    </div>

</div>

<div class="main">

    <div class="topbar">

        <div class="title">
            FX Assistant
        </div>

        <div class="paper">
            PAPER TRADING · NO REAL MONEY
        </div>

    </div>

    <div
        class="messages"
        id="messages"
    >

        <div
            class="welcome"
            id="welcome"
        >

            <h1>
                What do you want to know?
            </h1>

            <p>
                Ask me about markets in normal English.
                I will separate real information from model opinions
                and I will tell you when I do not have enough data.
            </p>

            <div class="quick-grid">

                <div
                    class="quick"
                    onclick="example('What can you do right now?')"
                >
                    What can you do right now?
                </div>

                <div
                    class="quick"
                    onclick="example('How is Apple doing?')"
                >
                    How is Apple doing?
                </div>

                <div
                    class="quick"
                    onclick="example('Compare Apple and Nvidia.')"
                >
                    Compare Apple and Nvidia.
                </div>

                <div
                    class="quick"
                    onclick="example('Explain how you decide whether a trade looks good.')"
                >
                    How do you decide whether a trade looks good?
                </div>

            </div>

        </div>

    </div>

    <div class="composer-wrap">

        <div class="composer">

            <textarea
                id="input"
                rows="1"
                placeholder="Ask FX anything..."
            ></textarea>

            <button
                class="send"
                id="send"
                onclick="sendMessage()"
            >
                Send
            </button>

        </div>

        <div class="helper">
            FX can make mistakes.
            Current mode: Paper Trading.
            No real money is being used.
        </div>

    </div>

</div>

<div class="inspector">

    <div class="inspector-head">
        Market Evidence
    </div>

    <div class="status">

        <div class="status-grid">

            <div class="status-item">
                <span
                    class="dot"
                    id="aiDot"
                ></span>
                Local AI
            </div>

            <div class="status-item">
                <span
                    class="dot"
                    id="alpacaDot"
                ></span>
                Alpaca
            </div>

            <div class="status-item">
                <span
                    class="dot"
                    id="hfDot"
                ></span>
                Hugging Face
            </div>

            <div class="status-item">
                <span
                    class="dot"
                    id="goldDot"
                ></span>
                Gold feed
            </div>

        </div>

    </div>

    <div class="chart-controls">

        <button
            class="symbol"
            onclick="loadChart('AAPL')"
        >
            AAPL
        </button>

        <button
            class="symbol"
            onclick="loadChart('NVDA')"
        >
            NVDA
        </button>

        <button
            class="symbol"
            onclick="loadChart('SPY')"
        >
            SPY
        </button>

        <button
            class="symbol"
            onclick="loadChart('TSLA')"
        >
            TSLA
        </button>

    </div>

    <div class="chart-title">

        <div
            class="chart-symbol"
            id="chartSymbol"
        >
            AAPL
        </div>

        <div
            class="chart-price"
            id="chartPrice"
        >
            —
        </div>

        <div
            class="chart-source"
            id="chartSource"
        >
            Loading real market data...
        </div>

    </div>

    <div id="chart"></div>

    <div
        class="chart-note"
        id="chartNote"
    >
        This chart uses real historical market information
        from the connected market-data provider.
    </div>

</div>

</div>

<script>

const messages =
    document.getElementById("messages");

const input =
    document.getElementById("input");

const send =
    document.getElementById("send");


function example(text) {

    input.value = text;

    input.focus();

}


input.addEventListener(
    "keydown",
    function(e) {

        if (
            e.key === "Enter" &&
            !e.shiftKey
        ) {

            e.preventDefault();

            sendMessage();

        }

    }
);


function addUser(text) {

    const welcome =
        document.getElementById("welcome");

    if (welcome) {
        welcome.remove();
    }

    const outer =
        document.createElement("div");

    outer.className =
        "message user";

    const bubble =
        document.createElement("div");

    bubble.className =
        "user-bubble";

    bubble.textContent = text;

    outer.appendChild(bubble);

    messages.appendChild(outer);

}


function addFX(text) {

    const outer =
        document.createElement("div");

    outer.className =
        "message";

    const name =
        document.createElement("div");

    name.className =
        "fx-name";

    name.textContent =
        "FX";

    const answer =
        document.createElement("div");

    answer.className =
        "fx-answer";

    answer.textContent = text;

    outer.appendChild(name);
    outer.appendChild(answer);

    messages.appendChild(outer);

    messages.scrollTop =
        messages.scrollHeight;

    return answer;

}


async function sendMessage() {

    const text =
        input.value.trim();

    if (!text) {
        return;
    }

    input.value = "";

    send.disabled = true;

    addUser(text);

    const answer =
        addFX(
            "Thinking..."
        );

    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: text
                    }),
                }
            );

        const data =
            await response.json();

        answer.textContent =
            data.answer ||
            (
                "I could not finish that request. " +
                "No trade was sent."
            );

    }

    catch {

        answer.textContent =
            (
                "I temporarily lost contact with my local AI. " +
                "No trade was sent and your account is safe."
            );

    }

    send.disabled = false;

    input.focus();

}


async function loadStatus() {

    try {

        const r =
            await fetch(
                "/api/status"
            );

        const s =
            await r.json();

        setDot(
            "aiDot",
            s.ai
        );

        setDot(
            "alpacaDot",
            s.alpaca
        );

        setDot(
            "hfDot",
            s.hugging_face
        );

        setDot(
            "goldDot",
            s.gold
        );

    }

    catch {}

}


function setDot(
    id,
    good
) {

    const dot =
        document.getElementById(id);

    dot.className =
        good
        ? "dot ok"
        : "dot no";

}


async function loadChart(symbol) {

    document.getElementById(
        "chartSymbol"
    ).textContent = symbol;

    document.getElementById(
        "chartPrice"
    ).textContent = "Loading...";

    document.getElementById(
        "chartSource"
    ).textContent =
        "Checking market data...";

    try {

        const r =
            await fetch(
                "/api/market/" +
                symbol +
                "/chart"
            );

        const data =
            await r.json();

        if (!data.available) {

            document.getElementById(
                "chartPrice"
            ).textContent = "Not connected";

            document.getElementById(
                "chartSource"
            ).textContent =
                data.message;

            document.getElementById(
                "chart"
            ).innerHTML = "";

            return;

        }

        document.getElementById(
            "chartPrice"
        ).textContent =
            data.latest_price
            ? "$" +
              Number(
                  data.latest_price
              ).toFixed(2)
            : "—";

        document.getElementById(
            "chartSource"
        ).textContent =
            "Source: " +
            data.source;

        drawCandles(
            data.bars
        );

    }

    catch {

        document.getElementById(
            "chartPrice"
        ).textContent =
            "Unavailable";

        document.getElementById(
            "chartSource"
        ).textContent =
            "FX could not retrieve this chart right now.";

    }

}


function drawCandles(bars) {

    const el =
        document.getElementById(
            "chart"
        );

    el.innerHTML = "";

    if (
        !bars ||
        bars.length === 0
    ) {

        el.textContent =
            "No chart information is available.";

        return;

    }

    const recent =
        bars.slice(-70);

    const width = 350;
    const height = 280;

    const lows =
        recent.map(
            x => x.low
        );

    const highs =
        recent.map(
            x => x.high
        );

    const min =
        Math.min(...lows);

    const max =
        Math.max(...highs);

    const range =
        Math.max(
            max - min,
            0.0001
        );

    const y =
        price =>
            15 +
            (
                max - price
            ) /
            range *
            (
                height - 30
            );

    const step =
        width /
        recent.length;

    let content = "";

    for (
        let i = 1;
        i < 5;
        i++
    ) {

        const gy =
            height /
            5 *
            i;

        content +=
            `<line
                class="grid-line"
                x1="0"
                x2="${width}"
                y1="${gy}"
                y2="${gy}"
            />`;

    }

    recent.forEach(
        (
            bar,
            i
        ) => {

            const x =
                i * step +
                step / 2;

            const yo =
                y(bar.open);

            const yc =
                y(bar.close);

            const yh =
                y(bar.high);

            const yl =
                y(bar.low);

            const up =
                bar.close >=
                bar.open;

            const top =
                Math.min(
                    yo,
                    yc
                );

            const bodyHeight =
                Math.max(
                    Math.abs(
                        yc - yo
                    ),
                    1.5
                );

            const candleWidth =
                Math.max(
                    step * .55,
                    1
                );

            content +=
                `<line
                    class="wick"
                    x1="${x}"
                    x2="${x}"
                    y1="${yh}"
                    y2="${yl}"
                />`;

            content +=
                `<rect
                    class="${
                        up
                        ? "candle-up"
                        : "candle-down"
                    }"
                    x="${
                        x -
                        candleWidth / 2
                    }"
                    y="${top}"
                    width="${candleWidth}"
                    height="${bodyHeight}"
                />`;

        }
    );

    el.innerHTML =
        `<svg
            viewBox="0 0 ${width} ${height}"
            preserveAspectRatio="none"
        >
            ${content}
        </svg>`;

}


loadStatus();

loadChart("AAPL");

setInterval(
    loadStatus,
    15000
);

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

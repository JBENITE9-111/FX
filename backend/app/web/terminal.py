from fastapi import (
    APIRouter,
)

from fastapi.responses import (
    HTMLResponse,
)


router = APIRouter()


@router.get(
    "/terminal",
    response_class=HTMLResponse,
)
async def terminal():

    return r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>
FX
</title>

<script
src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"
></script>

<style>

* {
    box-sizing:
        border-box;
}

html,
body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

body {
    background: #08090b;
    color: #eeeeef;

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

.app {
    height: 100vh;

    display: grid;

    grid-template-columns:
        210px
        285px
        minmax(500px, 1fr)
        380px;
}

.sidebar {
    border-right:
        1px solid #24272c;

    padding:
        14px 10px;

    overflow: hidden;
}

.logo {
    font-size: 20px;
    font-weight: 800;
    margin:
        0 7px
        18px;
}

.logo::after { content: " Terminal"; color: #777c85; font-weight: 500; }

:focus-visible { outline: 2px solid #f5f5f7; outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
}

.section {
    margin:
        23px 7px
        7px;

    font-size: 9px;

    text-transform:
        uppercase;

    letter-spacing:
        .1em;

    color:
        #666b72;
}

.nav {
    width: 100%;

    border: 0;

    background:
        transparent;

    color:
        #b4b8be;

    text-align:
        left;

    padding:
        8px;

    border-radius:
        6px;

    cursor:
        pointer;

    font-size:
        12px;
}

.nav:hover,
.nav.active {
    color: white;
    background:
        #15171a;
}

.nav.learn-nav {
    margin: 8px 0 2px;
    padding: 10px 11px;
    background: #f1f2f4;
    color: #0b0c0e;
    font-weight: 760;
}

.nav.learn-nav:hover {
    background: white;
    color: #0b0c0e;
}

.learning-hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 18px;
    align-items: center;
    margin: 18px 0;
    padding: 17px;
    border: 1px solid #30343a;
    border-radius: 11px;
    background: #111317;
}

.learning-state {
    margin-top: 6px;
    color: #a5abb3;
    font-size: 11px;
    line-height: 1.55;
}

.learning-actions { display: flex; gap: 7px; flex-wrap: wrap; }
.panel-button.secondary { background: #202329; color: #d7dade; border: 1px solid #34383f; }
.training-queue { display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 14px;min-height:26px; }
.queue-chip { display:flex;align-items:center;gap:7px;border:1px solid #30343a;background:#15171a;border-radius:99px;padding:5px 8px;color:#c8ccd1;font-size:10px; }
.queue-chip button { border:0;background:transparent;color:#8f959d;cursor:pointer;padding:0; }

.market-list {
    border-right:
        1px solid #24272c;

    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.market-head {
    height: 52px;

    border-bottom:
        1px solid #24272c;

    padding:
        0 12px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    font-size:
        12px;

    font-weight:
        700;
}

.search {
    margin:
        10px;

    width:
        calc(100% - 20px);

    background:
        #15171a;

    border:
        1px solid #30343a;

    border-radius:
        7px;

    padding:
        10px;

    color:
        white;

    outline:
        none;
}

.market-results {
    flex: 1;
    overflow: hidden;
}

.market-row {
    padding:
        11px 12px;

    border-bottom:
        1px solid #1d2024;

    cursor:
        pointer;
}

.market-row:hover {
    background:
        #111316;
}

.symbol {
    font-size:
        12px;

    font-weight:
        750;
}

.market-name {
    margin-top:
        3px;

    font-size:
        10px;

    color:
        #8f949b;
}

.center {
    min-width: 0;

    display:
        flex;

    flex-direction:
        column;
}

.top {
    height:
        52px;

    border-bottom:
        1px solid #24272c;

    padding:
        0 16px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;
}

.instrument {
    padding:
        14px
        18px
        5px;
}

.instrument-symbol {
    font-size:
        18px;

    font-weight:
        800;
}

.instrument-name {
    color:
        #8d9299;

    font-size:
        10px;

    margin-top:
        3px;
}

.price {
    font-size:
        29px;

    font-weight:
        800;

    margin-top:
        7px;

    font-variant-numeric:
        tabular-nums;
}

.toolbar {
    display:
        flex;

    flex-wrap:
        wrap;

    gap:
        5px;

    padding:
        8px
        18px;
}

.tool {
    border:
        1px solid #2c3035;

    background:
        #111317;

    color:
        #aaaeb5;

    border-radius:
        6px;

    padding:
        6px 8px;

    font-size:
        9px;

    cursor:
        pointer;
}

.tool.active {
    background:
        white;

    color:
        #111;
}

.chart-wrap {
    flex: 1;

    min-height:
        280px;

    padding:
        0 12px;
}

#chart {
    width:
        100%;

    height:
        100%;
}

.tabs {
    height:
        42px;

    display:
        flex;

    align-items:
        center;

    border-top:
        1px solid #24272c;

    border-bottom:
        1px solid #24272c;

    padding:
        0 14px;

    gap:
        4px;

    overflow-x:
        auto;
}

.tab {
    border:
        0;

    background:
        transparent;

    color:
        #8c9299;

    padding:
        7px 8px;

    font-size:
        9px;

    cursor:
        pointer;
}

.tab.active {
    color:
        white;
}

.details {
    height:
        155px;

    padding:
        12px 18px;

    overflow:
        hidden;

    color:
        #a4a9af;

    font-size:
        10px;

    line-height:
        1.6;
}

.detail-summary { font-size: 15px; font-weight: 750; margin-bottom: 9px; }
.detail-note { color: #969ca4; font-size: 10px; line-height: 1.5; margin-bottom: 9px; }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap: 7px; }
.detail-item { border: 1px solid #292d32; background: #111317; border-radius: 7px; padding: 9px; }
.detail-label { color: #8e949b; font-size: 9px; text-transform: uppercase; letter-spacing: .06em; }
.detail-value { color: #eceef1; font-size: 11px; line-height: 1.45; margin-top: 4px; }

.chat {
    border-left:
        1px solid #24272c;

    display:
        flex;

    flex-direction:
        column;

    min-width: 0;
}

.chat-head {
    height:
        52px;

    padding:
        0 13px;

    border-bottom:
        1px solid #24272c;

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;
}

.ai-status {
    font-size:
        9px;

    color:
        #83cda0;
}

.messages {
    flex:
        1;

    overflow-y:
        auto;

    padding:
        14px;
}

.message {
    margin-bottom:
        13px;

    padding:
        10px 11px;

    border-radius:
        8px;

    font-size:
        11px;

    line-height:
        1.6;

    white-space:
        pre-wrap;
}

.user-message {
    background:
        #202328;

    margin-left:
        35px;
}

.fx-message {
    border:
        1px solid #25292e;
}

.thinking {
    color:
        #91979e;
}

.chat-compose {
    border-top:
        1px solid #24272c;

    padding:
        10px;
}

.chat-input {
    width:
        100%;

    min-height:
        72px;

    resize:
        none;

    background:
        #14161a;

    border:
        1px solid #30343a;

    border-radius:
        8px;

    color:
        white;

    padding:
        10px;

    outline:
        none;
}

.send {
    width:
        100%;

    margin-top:
        7px;

    border:
        0;

    border-radius:
        7px;

    padding:
        9px;

    font-weight:
        700;

    cursor:
        pointer;
}

.panel {
    display:
        none;

    position:
        fixed;

    inset:
        52px
        380px
        0
        190px;

    background:
        #090a0c;

    z-index:
        20;

    overflow:
        auto;

    padding:
        25px;
}

.panel.show {
    display:
        block;
}

.panel h1 {
    font-size:
        25px;

    margin-top:
        0;
}

.card-grid {
    display:
        grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                240px,
                1fr
            )
        );

    gap:
        9px;

    margin-top:
        18px;
}

.card {
    border:
        1px solid #292d32;

    background:
        #111317;

    padding:
        13px;

    border-radius:
        8px;
}

.card-title {
    font-size:
        12px;

    font-weight:
        750;
}

.card-meta {
    margin-top:
        5px;

    color:
        #8e949b;

    font-size:
        10px;

    line-height:
        1.6;
}

.good {
    color:
        #84cda0;
}

.warn {
    color:
        #d9b47b;
}

.bad {
    color:
        #d68d8d;
}

.big-number {
    font-size:
        25px;

    font-weight:
        800;

    margin-top:
        5px;
}

input.panel-input,
select.panel-input {
    background:
        #14161a;

    border:
        1px solid #30343a;

    color:
        white;

    border-radius:
        7px;

    padding:
        9px;
}

.panel-button {
    border:
        0;

    border-radius:
        7px;

    padding:
        9px 11px;

    font-weight:
        700;

    cursor:
        pointer;
}

.close-panel {
    float:
        right;

    cursor:
        pointer;

    background:
        none;

    border:
        0;

    color:
        #aaa;
}

@media(max-width:1200px) {

    .app {
        grid-template-columns:
            170px
            250px
            1fr
            330px;
    }

    .panel {
        left:
            170px;

        right:
            330px;
    }
}

</style>

</head>

<body>

<div class="app">

<aside class="sidebar">

<div class="logo">
FX
</div>

<button class="nav active" onclick="closePanels();document.getElementById('chatInput').focus()">Chat</button>

<button
class="nav"
onclick="closePanels()"
>
Markets
</button>

<div class="section">
Intelligence
</div>

<button
class="nav learn-nav"
onclick="startLearning()"
title="Start the continuous research and validation queue"
>
Learn
</button>

<button
class="nav"
onclick="openPanel('trainingPanel')"
>
Model Training
</button>

<button class="nav" onclick="window.location='/learning'">Learning Progress</button>

<button
class="nav"
onclick="openPanel('botsPanel');loadBots()"
>
Bots
</button>

<button class="nav" onclick="openPanel('campaignsPanel');loadCampaigns()">Campaigns</button>

<button
class="nav"
onclick="openPanel('paperPanel');loadPaper()"
>
Paper Portfolio
</button>

<button
class="nav"
onclick="window.location='/strategies'"
>
Strategies
</button>

<button
class="nav"
onclick="window.location='/brains'"
>
Model Council
</button>

<button
class="nav"
onclick="window.location='/hedge-funds'"
>
Hedge Fund Intelligence
</button>

<div class="section">
Records
</div>

<button
class="nav"
onclick="window.location='/journal'"
>
Journal
</button>

<button class="nav" onclick="window.location='/journal'">Trade Reporting</button>

<button class="nav" onclick="window.location='/security'">Security & Health</button>

<button class="nav" onclick="window.location='/operations'">Favorites & Operations</button>

<div class="section">
Trading
</div>

<div id="campaignsPanel" class="panel">
<button class="close-panel" onclick="closePanels()">Close</button>
<h1>Goal Campaigns</h1>
<p style="color:#91979e;font-size:11px">Campaigns remain waiting until their bot is qualified, protected and above the calibrated 85% threshold.</p>
<div id="campaignGrid" class="card-grid"></div>
</div>

<button
class="nav"
onclick="openPanel('livePanel')"
>
Live Trading
</button>

</aside>


<section class="market-list">

<div class="market-head">

<span>
Global Markets
</span>

<span
style="font-size:9px;color:#82cd9e"
>
● LSE
</span>

</div>

<input
id="marketSearch"
class="search"
placeholder="Search any market..."
>

<div
id="marketResults"
class="market-results"
></div>

</section>


<main class="center">

<div class="top">

<strong>
Market Workspace
</strong>

<span
style="font-size:9px;color:#888"
>
London Strategic Edge
</span>

</div>

<div class="instrument">

<div
id="selectedSymbol"
class="instrument-symbol"
>
EUR/JPY
</div>

<div
id="selectedName"
class="instrument-name"
>
Euro / Japanese Yen
</div>

<div
id="selectedPrice"
class="price"
>
—
</div>

</div>

<div class="toolbar">

<button
class="tool"
data-tf="1m"
>
1m
</button>

<button
class="tool"
data-tf="5m"
>
5m
</button>

<button
class="tool"
data-tf="15m"
>
15m
</button>

<button
class="tool active"
data-tf="1h"
>
1H
</button>

<button
class="tool"
data-tf="4h"
>
4H
</button>

<button
class="tool"
data-tf="1d"
>
1D
</button>

<button
class="tool"
data-tf="1w"
>
1W
</button>

<span
style="width:10px"
></span>

<button
class="tool"
onclick="toggleEMA20()"
>
EMA20
</button>

<button
class="tool"
onclick="toggleEMA50()"
>
EMA50
</button>

<button
class="tool"
onclick="toggleTrend()"
>
Trend
</button>

<button
class="tool"
onclick="supportResistance()"
>
Support / Resistance
</button>

<button
class="tool"
onclick="fibonacci()"
>
Fibonacci
</button>

<button
class="tool"
onclick="clearOverlays()"
>
Clear
</button>

</div>

<div class="chart-wrap">

<div id="chart"></div>

</div>

<div
id="tabs"
class="tabs"
></div>

<div
id="details"
class="details"
>
Select a section.
</div>

</main>


<aside class="chat">

<div class="chat-head">

<strong>
Ask FX
</strong>

<span class="ai-status" id="terminalAiStatus">
● Checking AI
</span>

</div>

<div
id="messages"
class="messages"
></div>

<div class="chat-compose">

<textarea
id="chatInput"
class="chat-input"
placeholder="Ask FX anything about the market you are watching..."
></textarea>

<button
class="send"
onclick="sendChat()"
>
Ask FX
</button>

</div>

</aside>

</div>


<div
id="trainingPanel"
class="panel"
>

<button
class="close-panel"
onclick="closePanels()"
>
Close
</button>

<h1>
Model Training Center
</h1>

<p style="color:#91979e;font-size:11px">
Train and validate the machine-learning brains while you continue using FX.
Training continues in the background.
</p>

<div class="learning-hero">
<div>
<div class="card-title">Continuous learning queue</div>
<div id="continuousLearningState" class="learning-state">Checking local learning status…</div>
</div>
<div class="learning-actions">
<button class="panel-button" onclick="startLearning()">Start learning</button>
<button class="panel-button secondary" onclick="stopLearning()">Pause safely</button>
</div>
</div>

<div id="learningUniverse" class="card-meta"></div>

<div class="section" style="margin-left:0">One-off experiment</div>

<div
style="display:flex;gap:7px;flex-wrap:wrap"
>

<select id="trainAssetClass" class="panel-input" onchange="changeTrainingClass()" aria-label="Asset class"></select>

<select id="trainMarket" class="panel-input" onchange="updateTrainingAssets()" aria-label="Country or market">
<option value="">All markets</option>
</select>

<input id="trainSearch" class="panel-input" value="" placeholder="Search name or symbol" oninput="scheduleTrainingSearch()" aria-label="Search global instruments">

<select id="trainAsset" class="panel-input" onchange="applyTrainingAsset()" aria-label="Approved instrument"></select>

<input id="trainSymbol" class="panel-input" value="" placeholder="Optional manual symbol">

<button class="panel-button secondary" onclick="addTrainingTarget()">Add to list</button>

<button class="panel-button secondary" onclick="addVisibleTrainingTargets()">Add visible (max 50)</button>

<select
id="trainTf"
class="panel-input"
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

<select
id="trainHorizon"
class="panel-input"
>

<option value="1">
Next 1 period
</option>

<option value="3">
Next 3 periods
</option>

<option
value="5"
selected
>
Next 5 periods
</option>

<option value="10">
Next 10 periods
</option>

</select>

<button
class="panel-button"
onclick="startTrainingQueue()"
>
Train selected list
</button>

</div>

<div id="trainingCatalogStatus" class="card-meta" aria-live="polite"></div>

<div id="trainingQueue" class="training-queue"></div>

<div
id="trainingStatus"
style="margin-top:15px;color:#aaa;font-size:11px"
>
Ready.
</div>

<div
id="trainingResults"
class="card-grid"
></div>

</div>


<div
id="botsPanel"
class="panel"
>

<button
class="close-panel"
onclick="closePanels()"
>
Close
</button>

<h1>
Trading Bots
</h1>

<p style="color:#91979e;font-size:11px">
Watch what every bot is scanning, what markets it is interested in and what candidates it currently sees.
</p>

<div style="display:flex;gap:8px;margin-bottom:12px"><button class="panel-button" onclick="startAllBots()">Start all scanners</button><span id="botFleetStatus" class="card-meta"></span></div>

<div
id="botGrid"
class="card-grid"
></div>

</div>


<div
id="paperPanel"
class="panel"
>

<button
class="close-panel"
onclick="closePanels()"
>
Close
</button>

<h1>
Paper Trading Portfolio
</h1>

<p style="color:#91979e;font-size:11px">
Create protected simulated orders and attribute each result to a bot and strategy. No real money is used.
</p>

<button class="panel-button" onclick="window.location='/paper-local'">
Create paper order
</button>

<div
id="paperSummary"
class="card-grid"
></div>

<h3>
Open Paper Positions
</h3>

<div
id="paperPositions"
class="card-grid"
></div>

</div>


<div
id="livePanel"
class="panel"
>

<button
class="close-panel"
onclick="closePanels()"
>
Close
</button>

<h1>
Live Trading Gate
</h1>

<div class="card">

<div class="card-title">
Current state
</div>

<div class="card-meta">

Real-money autonomous trading is locked.

FX will use the same trade-proposal and approval workflow after a strategy has passed its required validation, Paper and shadow stages.

A language model cannot silently unlock this mode.

</div>

</div>

</div>


<script>

async function loadCampaigns(){
    const grid=document.getElementById('campaignGrid'); grid.replaceChildren();
    try { const payload=await fetch('/api/campaigns').then(r=>r.json());
      if(!payload.campaigns.length){grid.textContent='No campaigns yet. Ask FX to prepare one for an instrument.';return;}
      payload.campaigns.forEach(c=>{const card=document.createElement('div');card.className='card';
        const title=document.createElement('div');title.className='card-title';title.textContent=c.instrument+' · '+c.bot_id;
        const meta=document.createElement('div');meta.className='card-meta';meta.textContent=c.status+' — '+c.readiness_reason;
        card.append(title,meta);grid.appendChild(card);});
    } catch(e){grid.textContent='Campaign records are temporarily unavailable.';}
}

let currentSymbol =
    "EUR/JPY";

let currentName =
    "Euro / Japanese Yen";

let currentCategory =
    "Forex";

let currentTimeframe =
    "1h";

let currentBars =
    [];

let chart = null;

let candleSeries = null;

let ema20Series = null;

let ema50Series = null;

let trendSeries = null;

let supportLines = [];

let activeChatJobs =
    JSON.parse(
        localStorage.getItem(
            "fx-chat-jobs"
        )
        || "[]"
    );

const personalConversationId = "personal";

let conversation =
    JSON.parse(
        localStorage.getItem(
            "fx-chat-history"
        )
        || "[]"
    );


function saveChat(){

    localStorage.setItem(
        "fx-chat-history",
        JSON.stringify(
            conversation
        )
    );

    localStorage.setItem(
        "fx-chat-jobs",
        JSON.stringify(
            activeChatJobs
        )
    );

}


function renderConversation(){

    const box =
        document.getElementById(
            "messages"
        );

    box.innerHTML = "";

    conversation.forEach(
        item => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "message "
                + (
                    item.role === "user"
                    ? "user-message"
                    : "fx-message"
                );

            if(
                item.status === "thinking"
            ){

                div.className +=
                    " thinking";
            }

            div.textContent =
                item.text;

            box.appendChild(
                div
            );

        }
    );

    box.scrollTop =
        box.scrollHeight;

}


async function sendChat(){

    const input =
        document.getElementById(
            "chatInput"
        );

    const message =
        input.value.trim();

    if(!message){
        return;
    }

    input.value = "";

    conversation.push({
        role:"user",
        text:message,
        symbol:currentSymbol
    });

    const pendingId =
        "pending-"
        + Date.now();

    conversation.push({
        role:"fx",
        id:pendingId,
        text:
            "FX is analysing "
            + currentSymbol
            + "...",
        status:"thinking"
    });

    renderConversation();

    saveChat();

    let response;
    let data;

    try{
        response = await fetch(
            "/api/control/chat",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        message,
                        symbol:
                            currentSymbol,

                        timeframe:
                            currentTimeframe,

                        conversation_id:
                            personalConversationId
                    })
            }
        );
        data = await response.json();
    } catch {
        const pending = conversation.find(item => item.id === pendingId);
        if(pending){
            pending.status = "complete";
            pending.text = "FX could not reach its local service. Your request was not sent as a trade.";
        }
        saveChat();
        renderConversation();
        return;
    }

    if(data.ok){

        activeChatJobs.push({
            job_id:
                data.job_id,

            pending_id:
                pendingId
        });

        saveChat();

        pollChatJob(
            data.job_id,
            pendingId
        );
    } else {
        const pending = conversation.find(item => item.id === pendingId);
        if(pending){
            pending.status = "complete";
            pending.text = data.message || "FX could not start that analysis. No trade was sent.";
        }
        saveChat();
        renderConversation();
    }

}


async function loadPersonalChatMemory(){
    try{
        const payload=await fetch("/api/control/chat/history?conversation_id="+encodeURIComponent(personalConversationId)).then(response=>response.json());
        const stored=(payload.messages||[]).map(item=>({role:item.role==="assistant"?"fx":"user",text:item.content,status:"complete",symbol:item.symbol}));
        if(stored.length){conversation=stored;saveChat();renderConversation();}
    }catch{}
}


async function pollChatJob(
    jobId,
    pendingId
){

    try{

        const response =
            await fetch(
                "/api/control/jobs/"
                + jobId
            );

        const data =
            await response.json();

        if(!data.ok){
            return;
        }

        const job =
            data.job;

        if(
            job.status === "RUNNING"
        ){

            setTimeout(
                () =>
                    pollChatJob(
                        jobId,
                        pendingId
                    ),
                1500
            );

            return;
        }

        const message =
            conversation.find(
                x =>
                    x.id ===
                    pendingId
            );

        if(message){

            message.status =
                "complete";

            if(
                job.status ===
                "COMPLETE"
            ){

                const result =
                    job.result || {};

                message.text =
                    result.answer
                    || "FX finished the analysis.";

            }

            else{

                message.text =
                    "FX could not finish that request. No trade was sent.";
            }
        }

        activeChatJobs =
            activeChatJobs.filter(
                x =>
                    x.job_id !==
                    jobId
            );

        saveChat();

        renderConversation();

    }

    catch{

        setTimeout(
            () =>
                pollChatJob(
                    jobId,
                    pendingId
                ),
            2500
        );
    }

}


function resumeChatJobs(){

    activeChatJobs.forEach(
        item => {

            pollChatJob(
                item.job_id,
                item.pending_id
            );

        }
    );

}


function openPanel(id){

    document
        .querySelectorAll(
            ".panel"
        )
        .forEach(
            x =>
                x.classList.remove(
                    "show"
                )
        );

    document
        .getElementById(
            id
        )
        .classList.add(
            "show"
        );

    if(id === "trainingPanel"){
        refreshLearningStatus();
    }

}


function closePanels(){

    document
        .querySelectorAll(
            ".panel"
        )
        .forEach(
            x =>
                x.classList.remove(
                    "show"
                )
        );

}


function createChart(){

    const container =
        document.getElementById(
            "chart"
        );

    chart =
        LightweightCharts.createChart(
            container,
            {
                layout:{
                    background:{
                        color:"#08090b"
                    },

                    textColor:
                        "#797f87"
                },

                grid:{
                    vertLines:{
                        color:
                            "#08090b"
                    },

                    horzLines:{
                        color:
                            "#202328"
                    }
                },

                crosshair:{
                    mode:0
                },

                rightPriceScale:{
                    borderColor:
                        "#25282d"
                },

                timeScale:{
                    borderColor:
                        "#25282d",

                    timeVisible:
                        true,

                    secondsVisible:
                        false
                }
            }
        );

    candleSeries =
        chart.addSeries(
            LightweightCharts
            .CandlestickSeries,
            {
                upColor:
                    "#b8c2bb",

                downColor:
                    "#69747f",

                wickUpColor:
                    "#b8c2bb",

                wickDownColor:
                    "#69747f",

                borderVisible:
                    false
            }
        );

    const resize =
        new ResizeObserver(
            entries => {

                const rect =
                    entries[0]
                    .contentRect;

                chart.applyOptions({
                    width:
                        rect.width,

                    height:
                        rect.height
                });
            }
        );

    resize.observe(
        container
    );
}


function parseTime(row){

    const raw =
        row.timestamp
        || row.time
        || row.ts;

    if(!raw){
        return null;
    }

    const value =
        Date.parse(raw);

    if(
        Number.isNaN(value)
    ){
        return null;
    }

    return Math.floor(
        value / 1000
    );
}


function parseNumber(
    row,
    names
){

    for(
        const name
        of names
    ){

        const number =
            Number(
                row[name]
            );

        if(
            Number.isFinite(
                number
            )
        ){
            return number;
        }
    }

    return null;
}


async function loadChart(){

    clearOverlays();

    const encoded =
        currentSymbol
        .split("/")
        .map(
            encodeURIComponent
        )
        .join("/");

    const url =
        "/api/global/chart/"
        + encoded
        + "?timeframe="
        + currentTimeframe
        + "&limit=500";

    try{

        const response =
            await fetch(url);

        const data =
            await response.json();

        if(!data.ok){
            return;
        }

        currentBars = [];

        data.bars.forEach(
            row => {

                const time =
                    parseTime(row);

                const open =
                    parseNumber(
                        row,
                        [
                            "open",
                            "o"
                        ]
                    );

                const high =
                    parseNumber(
                        row,
                        [
                            "high",
                            "h"
                        ]
                    );

                const low =
                    parseNumber(
                        row,
                        [
                            "low",
                            "l"
                        ]
                    );

                const close =
                    parseNumber(
                        row,
                        [
                            "close",
                            "c"
                        ]
                    );

                if(
                    time
                    && open !== null
                    && high !== null
                    && low !== null
                    && close !== null
                ){

                    currentBars.push({
                        time,
                        open,
                        high,
                        low,
                        close
                    });
                }

            }
        );

        candleSeries.setData(
            currentBars
        );

        document
            .getElementById(
                "selectedPrice"
            )
            .textContent =
                Number(
                    data.latest_price
                )
                .toLocaleString(
                    undefined,
                    {
                        maximumFractionDigits:
                            6
                    }
                );

        chart
            .timeScale()
            .fitContent();

    }

    catch(error){

        console.error(error);
    }

}


function movingAverage(
    period
){

    const result = [];

    for(
        let i =
            period - 1;
        i <
            currentBars.length;
        i++
    ){

        let sum = 0;

        for(
            let j =
                i - period + 1;
            j <= i;
            j++
        ){

            sum +=
                currentBars[j]
                .close;
        }

        result.push({
            time:
                currentBars[i]
                .time,

            value:
                sum / period
        });
    }

    return result;
}


function toggleEMA20(){

    if(ema20Series){

        chart.removeSeries(
            ema20Series
        );

        ema20Series = null;

        return;
    }

    ema20Series =
        chart.addSeries(
            LightweightCharts
            .LineSeries,
            {
                lineWidth:
                    2
            }
        );

    ema20Series.setData(
        movingAverage(
            20
        )
    );
}


function toggleEMA50(){

    if(ema50Series){

        chart.removeSeries(
            ema50Series
        );

        ema50Series = null;

        return;
    }

    ema50Series =
        chart.addSeries(
            LightweightCharts
            .LineSeries,
            {
                lineWidth:
                    2
            }
        );

    ema50Series.setData(
        movingAverage(
            50
        )
    );
}


function toggleTrend(){

    if(trendSeries){

        chart.removeSeries(
            trendSeries
        );

        trendSeries = null;

        return;
    }

    if(
        currentBars.length
        < 20
    ){
        return;
    }

    const recent =
        currentBars.slice(
            -80
        );

    const n =
        recent.length;

    let sx = 0;
    let sy = 0;
    let sxy = 0;
    let sxx = 0;

    recent.forEach(
        (bar,index) => {

            sx += index;

            sy +=
                bar.close;

            sxy +=
                index
                * bar.close;

            sxx +=
                index
                * index;
        }
    );

    const slope =
        (
            n * sxy
            - sx * sy
        )
        /
        (
            n * sxx
            - sx * sx
        );

    const intercept =
        (
            sy
            - slope * sx
        )
        / n;

    trendSeries =
        chart.addSeries(
            LightweightCharts
            .LineSeries,
            {
                lineWidth:
                    2
            }
        );

    trendSeries.setData([
        {
            time:
                recent[0]
                .time,

            value:
                intercept
        },

        {
            time:
                recent[
                    n - 1
                ]
                .time,

            value:
                intercept
                + slope
                * (
                    n - 1
                )
        }
    ]);
}


function supportResistance(){

    if(
        currentBars.length
        < 20
    ){
        return;
    }

    const recent =
        currentBars.slice(
            -50
        );

    const support =
        Math.min(
            ...recent.map(
                x => x.low
            )
        );

    const resistance =
        Math.max(
            ...recent.map(
                x => x.high
            )
        );

    const s =
        candleSeries
        .createPriceLine({
            price:
                support,

            lineWidth:
                1,

            lineStyle:
                2,

            axisLabelVisible:
                true,

            title:
                "Support"
        });

    const r =
        candleSeries
        .createPriceLine({
            price:
                resistance,

            lineWidth:
                1,

            lineStyle:
                2,

            axisLabelVisible:
                true,

            title:
                "Resistance"
        });

    supportLines.push(
        s,
        r
    );
}


function fibonacci(){

    if(
        currentBars.length
        < 20
    ){
        return;
    }

    const recent =
        currentBars.slice(
            -100
        );

    const low =
        Math.min(
            ...recent.map(
                x => x.low
            )
        );

    const high =
        Math.max(
            ...recent.map(
                x => x.high
            )
        );

    const levels = [
        0,
        .236,
        .382,
        .5,
        .618,
        .786,
        1
    ];

    levels.forEach(
        level => {

            const price =
                high
                - (
                    high - low
                )
                * level;

            const line =
                candleSeries
                .createPriceLine({
                    price,
                    lineWidth:
                        1,

                    lineStyle:
                        2,

                    axisLabelVisible:
                        true,

                    title:
                        (
                            level * 100
                        ).toFixed(1)
                        + "%"
                });

            supportLines.push(
                line
            );
        }
    );
}


function clearOverlays(){

    if(!chart){
        return;
    }

    if(ema20Series){

        chart.removeSeries(
            ema20Series
        );

        ema20Series = null;
    }

    if(ema50Series){

        chart.removeSeries(
            ema50Series
        );

        ema50Series = null;
    }

    if(trendSeries){

        chart.removeSeries(
            trendSeries
        );

        trendSeries = null;
    }

    supportLines.forEach(
        line => {

            try{

                candleSeries
                    .removePriceLine(
                        line
                    );

            }

            catch{}
        }
    );

    supportLines = [];
}


async function searchMarkets(){

    const query =
        document
        .getElementById(
            "marketSearch"
        )
        .value
        .trim();

    const response =
        await fetch(
            "/api/global/search?q="
            + encodeURIComponent(
                query
            )
            + "&limit=100"
        );

    const data =
        await response.json();

    const box =
        document
        .getElementById(
            "marketResults"
        );

    box.innerHTML = "";

    if(!data.ok){
        return;
    }

    data.results.forEach(
        item => {

            const row =
                document
                .createElement(
                    "div"
                );

            row.className =
                "market-row";

            row.innerHTML = `
            <div class="symbol">
            ${item.symbol}
            </div>

            <div class="market-name">
            ${item.name || ""}
            </div>
            `;

            row.onclick =
                () =>
                    selectMarket(
                        item
                    );

            box.appendChild(
                row
            );
        }
    );
}


function selectMarket(item){

    currentSymbol =
        item.symbol;

    currentName =
        item.name || "";

    currentCategory =
        (
            item.category
            || ""
        ).toLowerCase();

    document
        .getElementById(
            "selectedSymbol"
        )
        .textContent =
            currentSymbol;

    document
        .getElementById(
            "selectedName"
        )
        .textContent =
            currentName;

    loadChart();

    buildTabs();

    loadTab(
        "overview"
    );
}


function buildTabs(){

    let tabs = [
        "overview",
        "history",
        "technical",
        "models",
        "strategies",
        "macro"
    ];

    if(
        currentCategory
        .includes(
            "stock"
        )
        ||
        currentCategory
        .includes(
            "etf"
        )
    ){

        tabs = [
            "overview",
            "history",
            "technical",
            "company",
            "fundamentals",
            "financials",
            "options",
            "models",
            "strategies",
            "macro"
        ];
    }

    const holder =
        document
        .getElementById(
            "tabs"
        );

    holder.innerHTML = "";

    tabs.forEach(
        name => {

            const button =
                document
                .createElement(
                    "button"
                );

            button.className =
                "tab";

            button.textContent =
                name
                .replace(
                    "_",
                    " "
                )
                .replace(
                    /^\w/,
                    c =>
                        c.toUpperCase()
                );

            button.onclick =
                () =>
                    loadTab(
                        name,
                        button
                    );

            holder.appendChild(
                button
            );
        }
    );
}


async function loadTab(
    name,
    button
){

    document
        .querySelectorAll(
            ".tab"
        )
        .forEach(
            x =>
                x.classList.remove(
                    "active"
                )
        );

    if(button){

        button.classList.add(
            "active"
        );
    }

    const details =
        document
        .getElementById(
            "details"
        );

    if(
        name === "history"
    ){

        details.textContent =
            "Use the timeframe controls above to inspect historical price action.";

        return;
    }

    if(
        name === "technical"
    ){

        details.textContent =
            "Use EMA20, EMA50, Trend, Support / Resistance and Fibonacci above. You can also ask FX to explain what you are seeing.";

        return;
    }

    if(
        name === "models"
    ){

        details.innerHTML =
            'Open <button onclick="openPanel(\'trainingPanel\')">Model Training</button> or ask FX: "What do the models think about '
            + currentSymbol
            + '?"';

        return;
    }

    if(
        name === "strategies"
    ){

        details.innerHTML =
            '<button onclick="window.location=\'/strategies\'">Open Strategy Library</button>';

        return;
    }

    const encoded =
        currentSymbol
        .split("/")
        .map(
            encodeURIComponent
        )
        .join("/");

    details.textContent =
        "Loading...";

    try{

        const response =
            await fetch(
                "/api/control/details/"
                + encoded
                + "?tab="
                + name
            );

        const data =
            await response.json();

        if(!data.ok){

            details.textContent =
                data.message;

            return;
        }

        renderDetailData(name, data.data);
    }

    catch{

        details.textContent =
            "FX could not load this section.";
    }
}


function humanLabel(value){
    return String(value || "").replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());
}


function detailItem(label, value){
    const item = document.createElement("div");
    item.className = "detail-item";
    const name = document.createElement("div");
    name.className = "detail-label";
    name.textContent = humanLabel(label);
    const content = document.createElement("div");
    content.className = "detail-value";
    content.textContent = value === null || value === undefined || value === "" ? "Unavailable" : String(value);
    item.append(name, content);
    return item;
}


function renderDetailData(tabName, payload){
    const details = document.getElementById("details");
    details.replaceChildren();
    const council = payload && (payload.model_council || (payload.members ? payload : null));
    if(council){
        const title = document.createElement("div");
        title.className = "detail-summary";
        title.textContent = council.overall || "No clear model view";
        const note = document.createElement("div");
        note.className = "detail-note";
        const agreement = council.agreement || {};
        note.textContent = "Model votes: " + Number(agreement.POSITIVE || 0) + " positive · "
            + Number(agreement.NEGATIVE || 0) + " negative · " + Number(agreement.NEUTRAL || 0) + " neutral. Research evidence only.";
        const grid = document.createElement("div");
        grid.className = "detail-grid";
        (council.members || []).forEach(member => grid.append(detailItem(
            member.strategy + " · " + member.view,
            member.explanation || member.status
        )));
        details.append(title, note, grid);
        return;
    }
    const grid = document.createElement("div");
    grid.className = "detail-grid";
    Object.entries(payload || {}).forEach(([key, value]) => {
        let shown = value;
        if(Array.isArray(value)) shown = value.map(item => typeof item === "object" ? Object.values(item).join(" · ") : item).join("; ");
        else if(value && typeof value === "object") shown = Object.entries(value).map(([k,v]) => humanLabel(k) + ": " + v).join(" · ");
        grid.append(detailItem(key, shown));
    });
    if(!grid.childElementCount) grid.append(detailItem("Status", "No verified information is available for this section."));
    details.append(grid);
}


async function startTraining(){

    const symbol = document.getElementById("trainSymbol").value.trim()
        || document.getElementById("trainAsset").value;

    const timeframe =
        document
        .getElementById(
            "trainTf"
        )
        .value;

    const horizon =
        Number(
            document
            .getElementById(
                "trainHorizon"
            )
            .value
        );

    const status =
        document
        .getElementById(
            "trainingStatus"
        );

    status.textContent =
        "Training is running in the background. You may close this panel and continue using FX.";

    const response =
        await fetch(
            "/api/control/training",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        symbol,
                        timeframe,
                        horizon
                    })
            }
        );

    const data =
        await response.json();

    if(data.ok){

        pollTraining(
            data.job_id
        );
    }
}


let trainingUniverse = [];
let selectedTrainingTargets = [];
let trainingCatalogTimer = null;
const trainingAssetClasses = ["Stocks", "ETFs", "Indices", "Forex", "Commodities", "Crypto", "Futures"];


async function loadTrainingUniverse(){
    try{
        const classSelect = document.getElementById("trainAssetClass");
        classSelect.replaceChildren();
        trainingAssetClasses.forEach(name => classSelect.add(new Option(name, name)));
        await changeTrainingClass();
        addTrainingTarget();
    } catch {
        document.getElementById("trainingStatus").textContent = "FX could not load the global instrument catalog.";
    }
}


function addTrainingTarget(){
    const selected = trainingUniverse.find(item => item.instrument_id === document.getElementById("trainAsset").value);
    if(selected){
        const configured = {...selected,
            timeframe:document.getElementById("trainTf").value,
            horizon:Number(document.getElementById("trainHorizon").value)
        };
        const existing = selectedTrainingTargets.findIndex(item => item.instrument_id === selected.instrument_id);
        if(existing >= 0) selectedTrainingTargets[existing] = configured;
        else selectedTrainingTargets.push(configured);
        renderTrainingQueue();
    }
}


function addVisibleTrainingTargets(){
    const visible = trainingUniverse.slice(0, 50);
    visible.forEach(item => {
        if(!selectedTrainingTargets.some(chosen => chosen.instrument_id === item.instrument_id)) selectedTrainingTargets.push(item);
    });
    renderTrainingQueue();
    const status = document.getElementById("trainingStatus");
    status.textContent = visible.length
        ? "Added " + visible.length + " visible instruments. Narrow the country or search to choose a more specific group."
        : "No visible instruments are available to add.";
}


function removeTrainingTarget(instrumentId){
    selectedTrainingTargets = selectedTrainingTargets.filter(item => item.instrument_id !== instrumentId);
    renderTrainingQueue();
}


function renderTrainingQueue(){
    const list = document.getElementById("trainingQueue");
    list.replaceChildren();
    if(!selectedTrainingTargets.length){
        list.textContent = "Your training list is empty.";
        return;
    }
    selectedTrainingTargets.forEach(item => {
        const chip = document.createElement("div"); chip.className = "queue-chip";
        const text = document.createElement("span"); text.textContent = item.asset_class + " · " + item.symbol + " · " + item.timeframe + " · next " + item.horizon;
        const remove = document.createElement("button"); remove.type = "button"; remove.textContent = "×";
        remove.setAttribute("aria-label", "Remove " + item.symbol); remove.onclick = () => removeTrainingTarget(item.instrument_id);
        chip.append(text, remove); list.append(chip);
    });
}


async function startTrainingQueue(){
    const manual = document.getElementById("trainSymbol").value.trim();
    if(manual){
        startTraining();
        return;
    }
    const status = document.getElementById("trainingStatus");
    addTrainingTarget();
    if(!selectedTrainingTargets.length){ status.textContent = "Add one or more approved instruments to the list."; return; }
    status.textContent = "Training the selected instruments sequentially. FX remains available.";
    const response = await fetch("/api/control/training/batch", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({targets:selectedTrainingTargets.map(item => ({symbol:item.symbol,timeframe:item.timeframe,horizon:item.horizon}))})
    });
    const data = await response.json();
    if(data.ok) pollTraining(data.job_id); else status.textContent = data.message || "FX could not start this training list.";
}


async function changeTrainingClass(){
    document.getElementById("trainSearch").value = "";
    document.getElementById("trainMarket").replaceChildren(new Option("All markets", ""));
    await updateTrainingAssets(true);
}


function scheduleTrainingSearch(){
    clearTimeout(trainingCatalogTimer);
    trainingCatalogTimer = setTimeout(() => updateTrainingAssets(false), 250);
}


async function updateTrainingAssets(resetMarket = false){
    const chosenClass = document.getElementById("trainAssetClass").value;
    const marketSelect = document.getElementById("trainMarket");
    const previousMarket = resetMarket ? "" : marketSelect.value;
    const params = new URLSearchParams({asset_class:chosenClass, limit:"100"});
    if(previousMarket) params.set("market", previousMarket);
    const query = document.getElementById("trainSearch").value.trim();
    if(query) params.set("q", query);
    const catalogStatus = document.getElementById("trainingCatalogStatus");
    catalogStatus.textContent = "Searching the local global catalog…";
    let payload;
    try{
        const response = await fetch("/api/learning/catalog?" + params.toString());
        if(!response.ok) throw new Error("catalog request failed");
        payload = await response.json();
    } catch {
        catalogStatus.textContent = "The global catalog is temporarily unavailable.";
        return;
    }
    trainingUniverse = payload.instruments || [];
    marketSelect.replaceChildren(new Option("All markets", ""));
    (payload.markets || []).forEach(name => marketSelect.add(new Option(name, name)));
    if(previousMarket && [...marketSelect.options].some(option => option.value === previousMarket)) marketSelect.value = previousMarket;
    const assetSelect = document.getElementById("trainAsset");
    assetSelect.replaceChildren();
    trainingUniverse.forEach(item => {
        assetSelect.add(new Option(item.name + " · " + item.symbol + " · " + item.market, item.instrument_id));
    });
    if(!trainingUniverse.length) assetSelect.add(new Option("No matching instruments", ""));
    const matched = Number(payload.matched || 0);
    catalogStatus.textContent = matched.toLocaleString() + " matching " + chosenClass.toLowerCase()
        + (matched > trainingUniverse.length ? " · showing first " + trainingUniverse.length.toLocaleString() : "")
        + " · search and country filters use the local London Strategic Edge catalog.";
    applyTrainingAsset();
}


function applyTrainingAsset(){
    const selected = trainingUniverse.find(item => item.instrument_id === document.getElementById("trainAsset").value);
    if(!selected){ return; }
    document.getElementById("trainTf").value = selected.timeframe;
    document.getElementById("trainHorizon").value = String(selected.horizon);
}


async function loadTerminalProviderStatus(){
    const status = document.getElementById("terminalAiStatus");
    try{
        const data = await fetch("/api/status").then(response => response.json());
        if(data.kimi && data.ollama) status.textContent = "● Kimi + Ollama available";
        else if(data.ollama) status.textContent = "● Ollama available";
        else if(data.kimi) status.textContent = "● Kimi available";
        else status.textContent = "● Deterministic fallback";
    } catch {
        status.textContent = "● Provider status unavailable";
    }
}


function describeLearning(state){
    const status = String(state.status || "STOPPED").replaceAll("_", " ");
    const current = state.current;
    if(current){
        return status + " · " + current.name + " (" + current.symbol + ", " + current.timeframe + ") · "
            + Number(state.completed_jobs || 0) + " completed · " + Number(state.failed_jobs || 0) + " failed safely";
    }
    if(state.status === "PAUSED_RESOURCE_PRESSURE"){
        return "Paused to protect this Mac · CPU " + Number(state.cpu_percent || 0).toFixed(1) + "%"
            + " exceeds the safe limit " + Number(state.max_cpu_percent || 85).toFixed(0) + "%"
            + " · FX retries automatically every " + Number(state.resource_retry_seconds || 30) + " seconds";
    }
    return status + " · " + Number(state.completed_jobs || 0) + " completed · "
        + Number(state.failed_jobs || 0) + " failed safely · " + Number(state.universe_size || 0) + " approved research targets";
}


async function refreshLearningStatus(){
    const stateNode = document.getElementById("continuousLearningState");
    const universeNode = document.getElementById("learningUniverse");
    if(!stateNode){ return; }
    try{
        const [overview, universePayload] = await Promise.all([
            fetch("/api/learning/overview").then(response => response.json()),
            fetch("/api/learning/universe").then(response => response.json())
        ]);
        stateNode.textContent = describeLearning(overview.continuous || {});
        const classes = [...new Set((universePayload.instruments || []).map(item => item.asset_class))];
        universeNode.textContent = "Approved queue: " + classes.join(" · ")
            + ". Training creates challenger evidence only; it never promotes a model or sends a trade.";
    } catch {
        stateNode.textContent = "FX could not read the local learning worker status.";
    }
}


async function startLearning(){
    openPanel("trainingPanel");
    const stateNode = document.getElementById("continuousLearningState");
    stateNode.textContent = "Starting the local research queue…";
    try{
        const payload = await fetch("/api/learning/start", {method:"POST"}).then(response => response.json());
        stateNode.textContent = describeLearning(payload.continuous || {});
    } catch {
        stateNode.textContent = "FX could not start learning. No trade was sent.";
    }
}


async function stopLearning(){
    const stateNode = document.getElementById("continuousLearningState");
    stateNode.textContent = "Finishing the current safe checkpoint…";
    try{
        const payload = await fetch("/api/learning/stop", {method:"POST"}).then(response => response.json());
        stateNode.textContent = describeLearning(payload.continuous || {});
    } catch {
        stateNode.textContent = "FX could not pause the learning worker.";
    }
}


setInterval(refreshLearningStatus, 10000);


async function pollTraining(
    jobId
){

    const response =
        await fetch(
            "/api/control/jobs/"
            + jobId
        );

    const data =
        await response.json();

    if(!data.ok){
        return;
    }

    const job =
        data.job;

    const status =
        document
        .getElementById(
            "trainingStatus"
        );

    if(
        job.status === "RUNNING"
    ){

        status.textContent =
            "Training and validation are still running. You can continue using FX.";

        setTimeout(
            () =>
                pollTraining(
                    jobId
                ),
            2000
        );

        return;
    }

    if(
        job.status === "FAILED"
    ){

        status.textContent =
            "Training failed: "
            + job.error;

        return;
    }

    status.textContent =
        "Training complete.";

    const grid =
        document
        .getElementById(
            "trainingResults"
        );

    grid.innerHTML = "";

    job.result.models.forEach(
        model => {

            const card =
                document
                .createElement(
                    "div"
                );

            card.className =
                "card";

            card.innerHTML = `
            <div class="card-title">
            ${model.model}
            </div>

            <div class="card-meta">

            Status:
            <strong>
            ${model.status}
            </strong>

            <br>

            Test AUC:
            ${
                model.test_metrics.auc
                === null
                ? "—"
                :
                Number(
                    model.test_metrics.auc
                ).toFixed(3)
            }

            <br>

            Walk-forward AUC:
            ${
                model.walk_forward.average_auc
                === null
                ? "—"
                :
                Number(
                    model.walk_forward.average_auc
                ).toFixed(3)
            }

            </div>
            `;

            grid.appendChild(
                card
            );
        }
    );
}


async function loadBots(){

    const response =
        await fetch(
            "/api/control/bots"
        );

    const data =
        await response.json();

    const grid =
        document
        .getElementById(
            "botGrid"
        );

    grid.innerHTML = "";

    if(!data.ok){
        return;
    }

    data.bots.forEach(
        bot => {

            const card =
                document
                .createElement(
                    "div"
                );

            card.className =
                "card";

            const candidates =
                (
                    bot.candidates
                    || []
                )
                .map(
                    x =>
                        x.symbol
                        + " "
                        + Number(
                            x.price
                        ).toLocaleString()
                )
                .join(
                    "<br>"
                )
                ||
                "No current long candidates.";

            const watchlist =
                bot.watchlist
                .join(
                    ", "
                );

            card.innerHTML = `
            <div class="card-title">
            ${bot.name}
            </div>

            <div class="card-meta">

            Status:
            <strong>
            ${bot.status}
            </strong>

            <br>

            Mode:
            ${bot.mode}

            <br>

            Strategy:
            ${bot.strategy}

            <br>

            Timeframe:
            ${bot.timeframe}

            <br>

            Data:
            ${bot.data_source || "London Strategic Edge price history"}

            <br>

            Runs in:
            ${bot.runtime_location || "Local FX backend on this Mac"}

            <br>

            Activity:
            ${bot.activity || "Watch-only research scan"}

            <br>

            Learning:
            ${bot.learns_while_scanning ? "Yes" : "No — training is handled by the Learning Center"}

            <br>

            Orders:
            ${bot.can_place_orders ? "Enabled" : "Disabled — candidates require a separate protected paper order"}

            <br><br>

            Watching:
            <br>
            ${watchlist}

            <br><br>

            Current candidates:
            <br>
            ${candidates}

            </div>

            <button
            class="panel-button"
            onclick="scanBot('${bot.id}')"
            >
            Scan Now
            </button>

            <button
            class="panel-button"
            onclick="startBot('${bot.id}')"
            >
            Start
            </button>

            <button
            class="panel-button"
            onclick="stopBot('${bot.id}')"
            >
            Stop
            </button>
            `;

            grid.appendChild(
                card
            );
        }
    );
}

async function startAllBots(){
    const status=document.getElementById("botFleetStatus");
    status.textContent="Checking system capacity…";
    try{
        const payload=await fetch("/api/control/bots/start-all",{method:"POST"}).then(response=>response.json());
        status.textContent=payload.message||"Scanner request completed.";
        await loadBots();
    }catch{status.textContent="FX could not start the scanner fleet.";}
}


async function scanBot(id){

    await fetch(
        "/api/control/bots/"
        + id
        + "/scan",
        {
            method:"POST"
        }
    );

    loadBots();
}


async function startBot(id){

    await fetch(
        "/api/control/bots/"
        + id
        + "/start",
        {
            method:"POST"
        }
    );

    loadBots();
}


async function stopBot(id){

    await fetch(
        "/api/control/bots/"
        + id
        + "/stop",
        {
            method:"POST"
        }
    );

    loadBots();
}


async function loadPaper(){

    const response =
        await fetch(
            "/api/control/paper"
        );

    const data =
        await response.json();

    if(!data.ok){
        return;
    }

    const account =
        data.account;

    const summary =
        document
        .getElementById(
            "paperSummary"
        );

    summary.innerHTML = `
    <div class="card">
    <div class="card-title">
    Paper Equity
    </div>
    <div class="big-number">
    $${Number(
        account.equity
    ).toLocaleString(
        undefined,
        {
            maximumFractionDigits:2
        }
    )}
    </div>
    </div>

    <div class="card">
    <div class="card-title">
    Paper Cash
    </div>
    <div class="big-number">
    $${Number(
        account.cash
    ).toLocaleString(
        undefined,
        {
            maximumFractionDigits:2
        }
    )}
    </div>
    </div>

    <div class="card">
    <div class="card-title">
    Today's Paper P&L
    </div>
    <div class="big-number ${
        account.day_pnl >= 0
        ? "good"
        : "bad"
    }">
    $${Number(
        account.day_pnl
    ).toLocaleString(
        undefined,
        {
            maximumFractionDigits:2
        }
    )}
    </div>
    </div>
    `;

    const positions =
        document
        .getElementById(
            "paperPositions"
        );

    positions.innerHTML = "";

    account.positions.forEach(
        position => {

            const card =
                document
                .createElement(
                    "div"
                );

            card.className =
                "card";

            card.innerHTML = `
            <div class="card-title">
            ${position.symbol}
            </div>

            <div class="card-meta">

            Quantity:
            ${position.quantity}

            <br>

            Entry:
            $${position.average_entry}

            <br>

            Current:
            $${position.current_price}

            <br>

            P&L:
            <span class="${
                position.unrealized_pnl
                >= 0
                ? "good"
                : "bad"
            }">
            $${position.unrealized_pnl.toFixed(2)}
            (
            ${position.unrealized_percent.toFixed(2)}%
            )
            </span>

            </div>
            `;

            positions.appendChild(
                card
            );
        }
    );
}


document
    .getElementById(
        "marketSearch"
    )
    .addEventListener(
        "input",
        () => {

            clearTimeout(
                window.fxSearchTimer
            );

            window.fxSearchTimer =
                setTimeout(
                    searchMarkets,
                    250
                );
        }
    );


document
    .querySelectorAll(
        "[data-tf]"
    )
    .forEach(
        button => {

            button.onclick =
                () => {

                    document
                        .querySelectorAll(
                            "[data-tf]"
                        )
                        .forEach(
                            x =>
                                x.classList
                                .remove(
                                    "active"
                                )
                        );

                    button.classList.add(
                        "active"
                    );

                    currentTimeframe =
                        button.dataset.tf;

                    loadChart();
                };
        }
    );


document
    .getElementById(
        "chatInput"
    )
    .addEventListener(
        "keydown",
        event => {

            if(
                event.key === "Enter"
                &&
                !event.shiftKey
            ){

                event.preventDefault();

                sendChat();
            }
        }
    );


createChart();

loadTrainingUniverse();

loadTerminalProviderStatus();

setInterval(loadTerminalProviderStatus, 15000);

renderConversation();
loadPersonalChatMemory();

resumeChatJobs();

buildTabs();

searchMarkets();

loadChart();

loadTab(
    "overview"
);

const requestedPanel = new URLSearchParams(window.location.search).get("panel");
if(requestedPanel === "paper"){
    openPanel("paperPanel");
    loadPaper();
}
if(requestedPanel === "learning"){
    openPanel("trainingPanel");
    refreshLearningStatus();
}

</script>

</body>

</html>
"""

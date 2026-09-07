from __future__ import annotations

from fastapi import APIRouter

from fastapi.responses import (
    HTMLResponse,
)


router = APIRouter()


@router.get(
    "/paper-local",
    response_class=HTMLResponse,
)
def page():

    return """
<!doctype html>

<html>

<head>

<meta charset="utf-8">

<meta
 name="viewport"
 content="width=device-width,initial-scale=1"
>

<title>
FX Local Paper Trading
</title>

<style>

:root {
    color-scheme:dark;

    --bg:#08090a;
    --panel:#121417;
    --panel2:#171a1f;
    --line:#2b3036;
    --text:#f2f3f5;
    --muted:#9298a1;
    --green:#65d18b;
    --red:#ef8585;
}

* {
    box-sizing:border-box;
}

body {
    margin:0;
    background:var(--bg);
    color:var(--text);

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

main {
    width:min(
        1500px,
        97vw
    );

    margin:auto;

    padding:
        22px
        0
        80px;
}

nav {
    display:flex;
    justify-content:space-between;
    align-items:center;

    margin-bottom:22px;
}

nav a {
    color:var(--text);
    text-decoration:none;

    border:
        1px
        solid
        var(--line);

    padding:
        8px
        11px;

    border-radius:6px;

    font-size:12px;
}

h1 {
    font-size:30px;
    margin:0;
}

.dek {
    color:var(--muted);
    margin:
        7px
        0
        22px;

    line-height:1.5;
}

.stats {
    display:grid;

    grid-template-columns:
        repeat(
            4,
            1fr
        );

    gap:10px;

    margin-bottom:18px;
}

.stat {
    border:
        1px
        solid
        var(--line);

    background:
        var(--panel);

    padding:15px;
}

.stat span {
    display:block;

    color:var(--muted);

    font-size:9px;

    text-transform:uppercase;

    letter-spacing:.7px;
}

.stat strong {
    display:block;

    margin-top:6px;

    font-size:22px;
}

.layout {
    display:grid;

    grid-template-columns:
        360px
        1fr;

    gap:12px;
}

.panel {
    border:
        1px
        solid
        var(--line);

    background:
        var(--panel);

    padding:16px;
}

.panel h2 {
    margin:
        0
        0
        15px;

    font-size:17px;
}

label {
    display:block;

    color:var(--muted);

    font-size:10px;

    text-transform:uppercase;

    margin:
        10px
        0
        5px;
}

input,
select {
    width:100%;

    background:
        var(--panel2);

    border:
        1px
        solid
        var(--line);

    color:
        var(--text);

    padding:
        10px;

    border-radius:6px;
}

.side {
    display:grid;

    grid-template-columns:
        1fr
        1fr;

    gap:8px;

    margin-top:12px;
}

button {
    border:0;
    border-radius:6px;

    padding:
        11px
        12px;

    font-weight:700;

    cursor:pointer;
}

.buy {
    background:
        var(--green);
}

.sell {
    background:
        var(--red);
}
.plan-button { background:#252930;color:var(--text);border:1px solid var(--line); }

table {
    width:100%;

    border-collapse:
        collapse;
}

th {
    color:
        var(--muted);

    text-align:left;

    font-size:9px;

    text-transform:uppercase;

    padding:
        9px;

    border-bottom:
        1px
        solid
        var(--line);
}

td {
    padding:
        11px
        9px;

    border-bottom:
        1px
        solid
        var(--line);

    font-size:12px;
}

.long {
    color:
        var(--green);
}

.short {
    color:
        var(--red);
}

.close {
    background:#eee;
    color:#111;

    padding:
        6px
        8px;

    font-size:10px;
}

.note {
    color:
        var(--muted);

    font-size:11px;

    margin-top:12px;

    line-height:1.5;
}

.catalog-list { min-height:0; }
.picker-row { display:grid;grid-template-columns:1fr auto;gap:7px;align-items:end; }
.picker-row button { background:#252930;color:var(--text);border:1px solid var(--line);padding:10px; }
.suggestions { display:grid;gap:8px;margin-bottom:18px; }
.suggestion { border:1px solid var(--line);background:var(--panel2);padding:12px;border-radius:8px; }
.suggestion strong { display:block;font-size:13px;margin-bottom:5px; }
.suggestion p { margin:4px 0;color:var(--muted);font-size:11px;line-height:1.45; }
.suggestion button { margin-top:8px;background:#e9eaec;color:#111;padding:7px 9px;font-size:10px; }
.suggestion.selected { border-color:var(--green);box-shadow:0 0 0 1px rgba(101,209,139,.25); }
.risk-panel { display:none;border:1px solid var(--line);background:#0d0f12;padding:12px;margin:10px 0;border-radius:8px; }
.risk-panel.visible { display:block; }
.risk-grid { display:grid;grid-template-columns:1fr 1fr;gap:8px 12px;margin-top:9px; }
.risk-item span { display:block;color:var(--muted);font-size:9px;text-transform:uppercase; }
.risk-item strong { display:block;font-size:12px;margin-top:2px; }
.risk-decision { font-weight:800;letter-spacing:.5px; }
.risk-decision.PASS { color:var(--green); }
.risk-decision.REDUCE_SIZE,.risk-decision.BLOCK { color:var(--red); }
.warning { color:#e7bd72;border-left:2px solid #e7bd72;padding-left:9px; }
.position-detail td { background:#0d0f12;color:var(--muted);font-size:10px;line-height:1.55;padding-top:7px;padding-bottom:10px; }

@media(max-width:900px) {

    .stats {
        grid-template-columns:
            1fr
            1fr;
    }

    .layout {
        grid-template-columns:
            1fr;
    }
}

</style>

</head>

<body>

<main>

<nav>

<a href="/terminal">
← Terminal
</a>

<div>
LOCAL PAPER ONLY
</div>

</nav>

<h1>
Local Paper Trading
</h1>

<div class="dek">
Your bots and strategies trade virtual money
stored entirely on this Mac.

No Alpaca order is required.
No real money is used.
</div>

<div class="note">
These are user-directed research simulations. Their outcomes become journal and learning evidence, but they do not qualify or promote a bot by themselves.
</div>


<div class="stats">

<div class="stat">
<span>Paper Equity</span>
<strong id="equity">$—</strong>
</div>

<div class="stat">
<span>Paper Cash</span>
<strong id="cash">$—</strong>
</div>

<div class="stat">
<span>Unrealized P&L</span>
<strong id="unrealized">$—</strong>
</div>

<div class="stat">
<span>Realized P&L</span>
<strong id="realized">$—</strong>
</div>

</div>


<div class="layout">


<section class="panel">

<h2>
Local Paper Order
</h2>

<label>Quick setup</label>
<select id="preset" onchange="applyPreset()">
<option value="">Choose an example or enter your own</option>
<option value="stock">Apple stock</option>
<option value="forex">EUR/USD forex</option>
<option value="gold">Gold commodity</option>
<option value="crypto">Bitcoin crypto</option>
<option value="index">S&amp;P 500 simulated index product</option>
<option value="indexEtf">S&amp;P 500 ETF index exposure</option>
<option value="future">S&amp;P 500 futures research contract</option>
</select>

<label>
Instrument
</label>

<input
 id="instrument"
 value="AAPL"
 onchange="clearProtectionContext();loadLatestPaperPrice();loadBotSuggestions()"
>


<label>
Asset Class
</label>

<select id="assetClass" onchange="clearProtectionContext();loadMarketList(false)">

<option value="Stocks">
Stock
</option>

<option value="Forex">
Forex
</option>

<option value="Crypto">
Crypto
</option>

<option value="Commodities">
Commodity
</option>

<option value="Indices">
Index
</option>

<option value="ETFs">
ETF
</option>

<option value="Futures">
Future
</option>

</select>

<label>Choose from your focused market universe</label>
<div class="picker-row">
<input id="paperSearch" placeholder="Search name or symbol" oninput="schedulePaperSearch()">
<button type="button" onclick="loadMarketList(false)">Search</button>
</div>
<select id="marketInstrument" class="catalog-list" onchange="selectPaperInstrument()" aria-label="Global instruments"></select>
<div id="catalogMessage" class="note">Loading your focused market universe…</div>


<label>
Current Price
</label>

<input
 id="price"
 type="number"
 step="any"
 placeholder="328.10"
 oninput="clearProtectionContext()"
>


<label>
Paper Notional ($)
</label>

<input
 id="notional"
 type="number"
 step="any"
 value="100"
 oninput="clearProtectionContext()"
>


<label>
Strategy
</label>

<input
 id="strategy"
 value="manual"
 onchange="clearProtectionContext()"
>

<label>Bot ID</label>
<input id="botId" value="manual-paper" list="botOptions" onchange="clearProtectionContext()">
<datalist id="botOptions"></datalist>

<label>Strategy version</label>
<input id="strategyVersion" value="1">

<label>Campaign ID (optional)</label>
<input id="campaignId" placeholder="Leave blank for a standalone experiment">

<label>Protective stop / invalidation</label>
<input id="stop" type="number" step="any" placeholder="Required" oninput="useManualProtection()">

<label>Profit plan</label>
<input id="profitPlan" placeholder="For example: fixed target at 340" oninput="useManualProtection()">
<input id="protectionPlanId" type="hidden">
<input id="planSource" type="hidden" value="USER_DEFINED">
<div id="protectionSuggestions" class="suggestions"><div class="note">Choose a bot identity, then choose BUY or SELL to calculate protected plan options.</div></div>

<div class="side">
<button type="button" class="plan-button" onclick="loadProtectionSuggestions('BUY')">Calculate BUY plan</button>
<button type="button" class="plan-button" onclick="loadProtectionSuggestions('SELL')">Calculate SELL plan</button>
</div>

<div id="riskPanel" class="risk-panel" aria-live="polite"></div>

<label>Maximum loss ($)</label>
<input id="maximumLoss" type="number" step="any" placeholder="Required" oninput="useManualProtection()">
<div class="note warning">This is the planned loss envelope at the modeled stop fill. A gap, unavailable liquidity, or slippage can produce a larger loss. Short losses can exceed the planned amount.</div>


<div class="side">

<button
 class="buy"
 onclick="submitOrder('BUY')"
>
SUBMIT BUY PAPER
</button>

<button
 class="sell"
 onclick="submitOrder('SELL')"
>
SUBMIT SELL PAPER
</button>

</div>

<div
 id="message"
 class="note"
>
Orders are simulated locally.
</div>

</section>


<section class="panel">

<h2>
Bot Research Suggestions
</h2>

<div id="botSuggestions" class="suggestions">
<div class="note">Choose an instrument to see which local bots are watching it.</div>
</div>

<h2>
Open Local Paper Positions
</h2>

<div id="markStatus" class="note">Current prices are refreshed from London Strategic Edge every 30 seconds while this page is open.</div>

<div style="overflow:auto">

<table>

<thead>

<tr>

<th>
Instrument
</th>

<th>
Strategy / Bot
</th>

<th>
Side
</th>

<th>
Quantity
</th>

<th>
Entry
</th>

<th>
Current
</th>

<th>
P&L
</th>

<th>
Value
</th>

<th>
Action
</th>

</tr>

</thead>

<tbody id="positions">

</tbody>

</table>

</div>

</section>

</div>

</main>


<script>

function money(v) {

    return (
        "$"
        + Number(v || 0)
            .toLocaleString(
                undefined,
                {
                    minimumFractionDigits:2,
                    maximumFractionDigits:2
                }
            )
    );
}

function formatApiError(detail){
    if(typeof detail === "string") return detail;
    if(Array.isArray(detail)) return detail.map(item => {
        const field = Array.isArray(item.loc) ? item.loc.filter(value => value !== "body").join(" → ") : "request";
        return field + ": " + (item.msg || "invalid value");
    }).join(" · ");
    if(detail && typeof detail === "object") return detail.message || JSON.stringify(detail);
    return "The request could not be completed.";
}

function clearProtectionContext(){
    document.getElementById("stop").value="";
    document.getElementById("profitPlan").value="";
    document.getElementById("maximumLoss").value="";
    document.getElementById("protectionPlanId").value="";
    document.getElementById("planSource").value="USER_DEFINED";
    const root=document.getElementById("protectionSuggestions");
    root.innerHTML='<div class="note">Choose BUY or SELL to calculate a fresh plan for the current instrument, price, notional, strategy, and bot.</div>';
    const risk=document.getElementById("riskPanel");risk.className="risk-panel";risk.replaceChildren();
}

function useManualProtection(){
    if(!document.getElementById("protectionPlanId").value) return;
    document.getElementById("protectionPlanId").value="";
    document.getElementById("planSource").value="USER_DEFINED";
    document.querySelectorAll(".suggestion.selected").forEach(card=>card.classList.remove("selected"));
    const risk=document.getElementById("riskPanel");risk.className="risk-panel";risk.replaceChildren();
    document.getElementById("message").textContent="The generated plan was changed. It is now user-defined and will be revalidated before paper submission.";
}

let paperCatalog = [];
let paperSearchTimer = null;


function paperTimeframe(assetClass){
    return ({Stocks:"1d",ETFs:"1d",Indices:"1d",Futures:"1d",Forex:"1h",Crypto:"1h",Commodities:"4h"})[assetClass] || "1d";
}


function schedulePaperSearch(){
    clearTimeout(paperSearchTimer);
    paperSearchTimer = setTimeout(() => loadMarketList(true), 250);
}


async function loadMarketList(preserveInstrument = false){
    const assetClass = document.getElementById("assetClass").value;
    const query = document.getElementById("paperSearch").value.trim();
    const params = new URLSearchParams({asset_class:assetClass,limit:"100",focused:"true"});
    if(query) params.set("q",query);
    const status = document.getElementById("catalogMessage");
    status.textContent = "Searching your focused market universe…";
    try{
        const payload = await fetch("/api/learning/catalog?" + params.toString()).then(response => response.json());
        paperCatalog = payload.instruments || [];
        const select = document.getElementById("marketInstrument");
        const current = document.getElementById("instrument").value.trim().toUpperCase();
        select.replaceChildren();
        paperCatalog.forEach(item => select.add(new Option(item.name + " · " + item.symbol + " · " + item.market,item.instrument_id)));
        const existing = paperCatalog.find(item => item.symbol.toUpperCase() === current);
        if(existing) select.value = existing.instrument_id;
        else if(!preserveInstrument && paperCatalog.length){
            select.selectedIndex = 0;
            await selectPaperInstrument();
        }
        const matched = Number(payload.matched || 0);
        status.textContent = matched.toLocaleString() + " matching " + assetClass.toLowerCase()
            + (matched > paperCatalog.length ? " · showing first " + paperCatalog.length : "") + " in your focused research universe.";
        if(existing || preserveInstrument) await loadBotSuggestions();
    } catch {
        status.textContent = "FX could not load the local market list.";
    }
}


async function selectPaperInstrument(){
    const selected = paperCatalog.find(item => item.instrument_id === document.getElementById("marketInstrument").value);
    if(!selected) return;
    clearProtectionContext();
    document.getElementById("instrument").value = selected.symbol;
    await Promise.all([loadLatestPaperPrice(), loadBotSuggestions()]);
}


async function loadLatestPaperPrice(){
    const symbol = document.getElementById("instrument").value.trim();
    const timeframe = paperTimeframe(document.getElementById("assetClass").value);
    if(!symbol) return;
    try{
        const response = await fetch("/api/global/chart/" + encodeURIComponent(symbol) + "?timeframe=" + timeframe + "&limit=2");
        const payload = await response.json();
        if(payload.ok && Number(payload.latest_price) > 0) document.getElementById("price").value = Number(payload.latest_price);
    } catch {}
}


function suggestionLine(text){
    const line = document.createElement("p");line.textContent = text;return line;
}

function escapeHtml(value){
    return String(value??"").replace(/[&<>'"]/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[character]);
}

function parseJson(value, fallback={}){
    try{return value?JSON.parse(value):fallback}catch{return fallback}
}

function sourceBarAge(value){
    if(!value) return null;
    const numeric=Number(value);
    const stamp=Number.isFinite(numeric)&&numeric>1e9 ? (numeric>1e12?numeric:numeric*1000) : Date.parse(value);
    return Number.isFinite(stamp)?Date.now()-stamp:null;
}

function markFreshnessWarning(position){
    const age=sourceBarAge(position.last_evaluated_bar);
    if(age===null) return "MARK NOT YET EVALUATED";
    const limit=({Forex:6,Crypto:3,Commodities:12,Stocks:72,ETFs:72,Indices:72,Futures:72})[position.asset_class]||24;
    return age>limit*3600000?"STALE MARK OR MARKET CLOSED":null;
}


async function loadBotSuggestions(){
    const box = document.getElementById("botSuggestions");
    const symbol = document.getElementById("instrument").value.trim().toUpperCase();
    box.replaceChildren();
    const loading = document.createElement("div");loading.className="note";loading.textContent="Checking local scanner evidence for " + symbol + "…";box.append(loading);
    try{
        const encoded=symbol.split("/").map(encodeURIComponent).join("/");
        const assetClass=document.getElementById("assetClass").value;
        const [payload,approval] = await Promise.all([
            fetch("/api/control/bots").then(response => response.json()),
            fetch("/api/local-paper/strategy-suggestion/"+encoded+"?asset_class="+encodeURIComponent(assetClass)).then(response => response.json())
        ]);
        const matching = (payload.bots || [])
            .filter(bot => (bot.watchlist || []).some(item => String(item).toUpperCase() === symbol))
            .map(bot => ({bot,result:(bot.last_results||[]).find(item => String(item.symbol).toUpperCase()===symbol)}));
        box.replaceChildren();
        const approvalCard=document.createElement("article");approvalCard.className="suggestion";
        const approvalTitle=document.createElement("strong");
        approvalTitle.textContent=approval.approved_strategy ? "Approved strategy available" : "Approved strategy: none yet";
        approvalCard.append(approvalTitle,
            suggestionLine(approval.message || "Qualification evidence is unavailable."),
            suggestionLine("Executable paper decision: " + String(approval.paper_action || "WAIT").replaceAll("_"," ")));
        const evidence=approval.best_model_evidence;
        if(evidence){
            approvalCard.append(suggestionLine("Best current brain: "+String(evidence.model||"model").replaceAll("_"," ")+" · "+String(evidence.stage||"UNKNOWN").replaceAll("_"," ")+" · next gate "+String(evidence.blocked_at||"UNKNOWN").replaceAll("_"," ")));
        } else {
            approvalCard.append(suggestionLine("No completed model evidence has been recorded for "+symbol+" yet."));
        }
        if(approval.research_setup){
            approvalCard.append(suggestionLine("Suggested research setup: "+approval.research_setup.name+" · RESEARCH ONLY"));
            const research=document.createElement("button");research.type="button";research.textContent="Use research setup";
            research.onclick=()=>{
                clearProtectionContext();
                document.getElementById("strategy").value=approval.research_setup.strategy_id;
                document.getElementById("botId").value="manual-paper";
                document.getElementById("message").textContent=approval.research_setup.name+" selected as a research hypothesis. It is not approved; any paper order still requires a reviewed stop, profit plan, and maximum loss.";
            };
            approvalCard.append(research);
        }
        box.append(approvalCard);
        if(!matching.length){
            const empty=document.createElement("div");empty.className="note";empty.textContent="No scanner currently watches " + symbol + ". The research setup above remains an unapproved hypothesis.";box.append(empty);return;
        }
        matching.forEach(({bot,result}) => {
            const card=document.createElement("article");card.className="suggestion";
            const title=document.createElement("strong");title.textContent=bot.name;
            const direction=!result?"WAITING FOR FIRST SCAN":Number(result.current_position)===1?"POSITIVE":Number(result.current_position)===-1?"NEGATIVE":"NEUTRAL";
            card.append(title,
                suggestionLine("Research observation: " + direction + " · " + bot.strategy + " · " + bot.timeframe),
                suggestionLine("Source: London Strategic Edge price history · scanner " + String(bot.status||"STOPPED").toLowerCase()),
                suggestionLine(result ? "Historical test: return " + (Number(result.historical_return||0)*100).toFixed(1) + "% · drawdown " + (Number(result.max_drawdown||0)*100).toFixed(1) + "% · Sharpe " + Number(result.sharpe||0).toFixed(2) : "Historical test: not available until this scanner completes its first scan."),
                suggestionLine("Status: research only. This observation is not calibrated to 85% and cannot approve an order."));
            const use=document.createElement("button");use.type="button";use.textContent="Use bot identity";use.onclick=async()=>{
                clearProtectionContext();
                document.getElementById("botId").value=bot.id;
                document.getElementById("strategy").value=bot.strategy;
                document.getElementById("strategyVersion").value="1";
                const message=document.getElementById("message");
                message.textContent=bot.name+" identity applied to the order form. Add a structural stop, profit plan, and maximum loss before submitting a paper order.";
                document.getElementById("botId").scrollIntoView({behavior:"smooth",block:"center"});
                document.getElementById("botId").focus();
                if(direction==="POSITIVE"||direction==="NEGATIVE") await loadProtectionSuggestions(direction==="POSITIVE"?"BUY":"SELL");
            };card.append(use);box.append(card);
        });
    } catch {
        box.replaceChildren();const error=document.createElement("div");error.className="note";error.textContent="Bot suggestions are temporarily unavailable. Paper protection remains active.";box.append(error);
    }
}


async function refresh() {

    const accountResponse =
        await fetch(
            "/api/local-paper/account"
        );

    const account =
        await accountResponse.json();

    document.getElementById(
        "equity"
    ).textContent =
        money(
            account.equity
        );

    document.getElementById(
        "cash"
    ).textContent =
        money(
            account.cash
        );

    document.getElementById(
        "unrealized"
    ).textContent =
        money(
            account.unrealized_pnl
        );

    document.getElementById(
        "realized"
    ).textContent =
        money(
            account.realized_pnl
        );


    const response =
        await fetch(
            "/api/local-paper/positions"
        );

    const data =
        await response.json();

    const body =
        document.getElementById(
            "positions"
        );

    body.innerHTML = "";


    for (
        const position
        of data.positions
    ) {

        const row =
            document.createElement(
                "tr"
            );

        const pnl =
            Number(
                position.unrealized_pnl
                || 0
            );

        row.innerHTML = `

<td>
${escapeHtml(position.instrument)}
</td>

<td>
${escapeHtml(position.strategy_id || "MANUAL")}<br><span class="note">${escapeHtml(position.bot_id || "manual-paper")}</span>
</td>

<td class="${
    position.side_name
        .toLowerCase()
}">
${position.side_name}
</td>

<td>
${Number(
    position.quantity
).toFixed(6)}
</td>

<td>
${Number(
    position.average_price
).toFixed(5)}
</td>

<td>
<input
  id="mark-${position.position_id}"
  type="number"
  step="any"
  value="${
      Number(
          position.last_price
      )
  }"
  style="
    width:95px;
    padding:5px;
  "
>
</td>

<td class="${
    pnl >= 0
        ? "long"
        : "short"
}">
${money(pnl)}
</td>

<td>
${money(
    position.market_value
)}
</td>

<td>

<button
 class="close"
 onclick="
 closePosition(
   '${position.position_id}'
 )
 "
>
Close
</button>

</td>
`;

        body.appendChild(
            row
        );

        const plan=parseJson(position.protection_plan_json,parseJson(position.profit_plan,{}));
        const state=parseJson(position.plan_state_json,{});
        const targets=plan.targets||[];
        let nextTarget="User-defined / none";
        if(plan.type==="FIXED_1_5R"&&targets[0]) nextTarget=Number(targets[0].price).toPrecision(7);
        if(plan.type==="SCALE_1R_2R"&&targets.length) nextTarget=Number(targets[state.target_1_filled?1:0].price).toPrecision(7);
        if(plan.type==="TRAIL_AFTER_1R") nextTarget=state.trail_active?"1 ATR trailing stop":Number(targets[0]?.price||0).toPrecision(7)+" activation";
        const maxLoss=Number(position.maximum_loss||0);
        const currentR=maxLoss>0?pnl/maxLoss:0;
        const freshness=markFreshnessWarning(position);
        const detail=document.createElement("tr");detail.className="position-detail";
        detail.innerHTML=`<td colspan="9">
            ${freshness?'<span class="warning"><strong>'+escapeHtml(freshness)+'</strong></span> · ':''}
            Stop <strong>${Number(position.stop||0).toPrecision(7)}</strong> ·
            Next target <strong>${escapeHtml(nextTarget)}</strong> ·
            Plan <strong>${escapeHtml(plan.label||plan.type||"USER DEFINED")}</strong> ·
            Planned envelope <strong>${money(maxLoss)}</strong> ·
            Current R <strong>${currentR.toFixed(2)}R</strong> ·
            Partial realized <strong>${money(position.realized_pnl)}</strong> ·
            State <strong>${escapeHtml(state.status||"AWAITING REVIEW")}</strong> ·
            Last source bar <strong>${escapeHtml(position.last_evaluated_bar||"not evaluated")}</strong>
        </td>`;
        body.appendChild(detail);
    }
}


async function refreshLiveMarks(){
    const status=document.getElementById("markStatus");
    try{
        const response=await fetch("/api/local-paper/positions/refresh-marks",{method:"POST"});
        const payload=await response.json();
        if(!response.ok) throw new Error(payload.detail||"mark failed");
        const when=payload.marked_at?new Date(payload.marked_at).toLocaleTimeString():"now";
        status.textContent=(payload.updated||[]).length
            ? "Paper positions marked from "+payload.source+" at "+when+". "+(payload.auto_exits||[]).length+" automatic protection exits executed. "
                +((payload.failed||[]).length?"WARNING: failed refresh for "+payload.failed.join(", ")+".":"All requested instruments refreshed.")
            : "No open paper positions need a market mark.";
        await refresh();
    }catch{
        status.textContent="Live paper marks are temporarily unavailable; displayed prices are the last recorded marks.";
    }
}


async function loadProtectionSuggestions(direction){
    const root=document.getElementById("protectionSuggestions");
    root.textContent="Calculating volatility and structural invalidation…";
    document.getElementById("protectionPlanId").value="";
    const params=new URLSearchParams({
        instrument:document.getElementById("instrument").value.trim(),
        asset_class:document.getElementById("assetClass").value,direction,
        notional:document.getElementById("notional").value||"100",
        strategy_id:document.getElementById("strategy").value.trim(),
        bot_id:document.getElementById("botId").value.trim()
    });
    try{
        const response=await fetch("/api/local-paper/protection-suggestions?"+params.toString());
        const payload=await response.json();
        if(!response.ok) throw new Error(formatApiError(payload.detail||"suggestion failed"));
        document.getElementById("price").value=payload.entry;
        document.getElementById("stop").value=payload.structural_stop;
        document.getElementById("maximumLoss").value=payload.maximum_loss;
        document.getElementById("planSource").value="FX_SUGGESTED";
        const risk=payload.risk||{};
        const panel=document.getElementById("riskPanel");panel.className="risk-panel visible";panel.replaceChildren();
        const heading=document.createElement("strong");heading.textContent="Maximum-loss calculation";panel.append(heading);
        const grid=document.createElement("div");grid.className="risk-grid";
        const fields=[
            ["Paper equity",money(risk.equity)],[Number(risk.per_trade_risk_pct).toFixed(2)+"% per-trade cap",money(risk.per_trade_risk_cap)],
            ["Remaining daily capacity",money(risk.remaining_daily_loss_capacity)],["Remaining portfolio capacity",money(risk.remaining_portfolio_risk)],
            ["Entry",Number(risk.entry).toPrecision(7)],["Protective stop",Number(risk.stop).toPrecision(7)],
            ["Stop distance",Number(risk.stop_distance).toPrecision(6)+" · "+Number(risk.stop_distance_pct).toFixed(2)+"% · "+Number(risk.stop_distance_atr).toFixed(2)+" ATR"],
            ["Quantity",Number(risk.quantity).toFixed(6)],["Paper notional",money(risk.notional)],
            ["Loss at exact stop",money(risk.loss_at_stop)],["Modeled execution allowance",money(risk.modeled_execution_allowance)+" · "+Number(risk.modeled_cost_bps).toFixed(1)+" bps assumption"],
            ["Planned loss envelope",money(risk.planned_loss_envelope)+" · "+Number(risk.planned_loss_equity_pct).toFixed(4)+"% equity · "+Number(risk.planned_loss_notional_pct).toFixed(3)+"% notional"],
            ["Maximum notional by risk",money(risk.maximum_notional_by_risk)],
            ["Market-data timestamp",payload.plans?.[0]?.market_data_timestamp||"unavailable"],
            ["Plan validity","Five minutes · single use"]
        ];
        fields.forEach(([label,value])=>{const item=document.createElement("div");item.className="risk-item";const key=document.createElement("span");key.textContent=label;const val=document.createElement("strong");val.textContent=value;item.append(key,val);grid.append(item)});
        panel.append(grid);
        const decision=document.createElement("p");decision.className="risk-decision "+risk.decision;decision.textContent="Risk decision: "+String(risk.decision).replaceAll("_"," ");panel.append(decision);
        const warning=document.createElement("p");warning.className="note warning";warning.textContent=payload.warning;panel.append(warning);
        root.replaceChildren();
        (payload.plans||[]).forEach(plan=>{
            const card=document.createElement("article");card.className="suggestion";
            const title=document.createElement("strong");title.textContent=plan.label;
            card.append(title);
            (plan.targets||[]).forEach((target,index)=>card.append(suggestionLine(
                (plan.type==="TRAIL_AFTER_1R"?"Trail activation":"Target "+(index+1))+": "+Number(target.price).toPrecision(7)
                +" · "+Number(target.move_pct).toFixed(2)+"% move · "+Number(target.r_multiple).toFixed(1)+"R"
                +(plan.type==="TRAIL_AFTER_1R"?" · no sale at activation":" · close "+Number(target.quantity_fraction*100).toFixed(0)+"% · gross "+money(target.estimated_gross_profit))
            )));
            card.append(
                suggestionLine(plan.management),
                suggestionLine("Gross target profit: "+(plan.gross_target_profit==null?"variable":money(plan.gross_target_profit))+" · estimated net: "+(plan.estimated_net_profit==null?"variable":money(plan.estimated_net_profit))
                    +(plan.net_reward_risk==null?"":" · net reward/risk "+Number(plan.net_reward_risk).toFixed(2)+"R")),
                suggestionLine("Best suited to: "+plan.best_suited_to),
                suggestionLine("Tradeoff: "+plan.tradeoff)
            );
            const button=document.createElement("button");button.type="button";
            button.textContent=risk.decision==="PASS"?"Use this protected plan":"Risk capacity requires adjustment";
            button.disabled=risk.decision!=="PASS";
            button.onclick=()=>{
                document.querySelectorAll("#protectionSuggestions .suggestion").forEach(item=>item.classList.remove("selected"));card.classList.add("selected");
                document.getElementById("protectionPlanId").value=plan.plan_id;
                document.getElementById("planSource").value="FX_SUGGESTED";
                document.getElementById("profitPlan").value=plan.label+" — "+plan.management;
                document.getElementById("maximumLoss").value=Number(plan.maximum_loss).toFixed(6);
                document.getElementById("message").textContent="Protected "+direction+" plan selected. It expires in five minutes and will be checked again before submission.";
            };
            card.append(button);root.append(card)
        });
        document.getElementById("message").textContent=risk.decision==="PASS"
            ? "Fresh "+direction+" protection is ready. Review the full calculation and select one plan."
            : "The requested notional exceeds current risk capacity. Reduce it to "+money(risk.maximum_notional_by_risk)+" or less and recalculate.";
    }catch(error){root.textContent=error.message||"Protection suggestions are temporarily unavailable.";}
}


async function submitOrder(
    side
) {

    const payload = {

        instrument:
            document
            .getElementById(
                "instrument"
            )
            .value
            .trim()
            .toUpperCase(),

        asset_class:
            document
            .getElementById(
                "assetClass"
            )
            .value,

        side:
            side,

        price:
            Number(
                document
                .getElementById(
                    "price"
                )
                .value
            ),

        notional:
            Number(
                document
                .getElementById(
                    "notional"
                )
                .value
            ),

        strategy_id:
            document
            .getElementById(
                "strategy"
            )
            .value
            .trim(),

        bot_id:
            document.getElementById("botId").value.trim(),

        strategy_version:
            document.getElementById("strategyVersion").value.trim(),

        campaign_id:
            document.getElementById("campaignId").value.trim() || null,

        stop:
            Number(document.getElementById("stop").value),

        structural_invalidation:
            Number(document.getElementById("stop").value),

        profit_plan:
            document.getElementById("profitPlan").value.trim(),

        maximum_loss:
            Number(document.getElementById("maximumLoss").value),

        protection_plan_id:
            document.getElementById("protectionPlanId").value || null,

        plan_source:
            document.getElementById("planSource").value
    };


    const response =
        await fetch(
            "/api/local-paper/orders",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        payload
                    )
            }
        );


    const result =
        await response.json();


    document.getElementById(
        "message"
    ).textContent = (
        response.ok

        ? (
            "FILLED locally: "
            + result.side
            + " "
            + result.instrument
            + " — "
            + money(
                result.notional
            )
        )

        : (
            formatApiError(result.detail || "Order rejected.")
        )
    );


    await refresh();
}


const paperPresets = {
    stock:{instrument:"AAPL",assetClass:"Stocks",strategy:"manual-stock-research",bot:"stock-team"},
    forex:{instrument:"EUR/USD",assetClass:"Forex",strategy:"manual-forex-research",bot:"forex-team"},
    gold:{instrument:"XAU/USD",assetClass:"Commodities",strategy:"manual-gold-research",bot:"commodity-team"},
    crypto:{instrument:"BTC/USD",assetClass:"Crypto",strategy:"manual-crypto-research",bot:"crypto-team"},
    index:{instrument:"SPX500/USD",assetClass:"Indices",strategy:"manual-index-cfd-research",bot:"index-team"},
    indexEtf:{instrument:"SPY",assetClass:"ETFs",strategy:"manual-index-etf-research",bot:"index-team"},
    future:{instrument:"ES.F",assetClass:"Futures",strategy:"manual-index-futures-research",bot:"index-team"}
};


async function applyPreset(){
    const preset = paperPresets[document.getElementById("preset").value];
    if(!preset){ return; }
    clearProtectionContext();
    document.getElementById("instrument").value = preset.instrument;
    document.getElementById("assetClass").value = preset.assetClass;
    document.getElementById("strategy").value = preset.strategy;
    document.getElementById("botId").value = preset.bot;
    document.getElementById("paperSearch").value = "";
    await loadMarketList(true);
    await Promise.all([loadLatestPaperPrice(), loadBotSuggestions()]);
}


async function loadBotOptions(){
    try{
        const payload = await fetch("/api/control/bots").then(response => response.json());
        const list = document.getElementById("botOptions");
        list.replaceChildren();
        (payload.bots || []).forEach(bot => list.append(new Option(bot.name || bot.id, bot.id)));
    } catch {}
}


async function closePosition(
    positionId
) {

    const price =
        Number(
            document
            .getElementById(
                "mark-"
                + positionId
            )
            .value
        );


    const response =
        await fetch(
            "/api/local-paper/positions/"
            + positionId
            + "/close",

            {
                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        {
                            price:price
                        }
                    )
            }
        );


    if (!response.ok) {

        const result =
            await response.json();

        alert(
            formatApiError(result.detail || "Could not close.")
        );
    }


    await refresh();
}


refresh();
refreshLiveMarks();
loadBotOptions();
loadMarketList(true);
loadLatestPaperPrice();
loadBotSuggestions();

setInterval(
    refresh,
    5000
);
setInterval(refreshLiveMarks,30000);

</script>

</body>

</html>
"""

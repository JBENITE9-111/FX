from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

from backend.app.services.market_data.lse_global import LSEGlobalMarketData
from backend.app.services.models.council import model_council
from backend.app.services.strategies.backtester import backtest
from services.agents.sparse_router import route as route_experts
from services.bot_signals.store import create_signal
from services.instruments.training_universe import global_training_catalog, search_training_catalog
from services.operations.notifications import channel_health, route_event
from services.operations.reports import generate_report, render_markdown
from services.operations.scheduler import scheduler
from services.operations.store import (delete_favorite, delete_schedule, get_favorite, get_report, get_schedule, list_deliveries,
                                       list_events, list_favorites, list_reports, list_schedules,
                                       make_schedule_due, record_event, save_favorite, save_schedule, set_schedule_enabled)

router = APIRouter(tags=["FX Operations"])


class FavoriteInput(BaseModel):
    instrument_id: str
    symbol: str
    name: str = ""
    asset_class: str
    provider: str = "London Strategic Edge"
    enabled: bool = True
    execution_timeframe: str = "5m"
    context_timeframes: list[str] = Field(default_factory=lambda: ["4h"])
    strategy_id: str = "trend_following"
    bot_id: str = "trading_team"
    min_evidence: float | None = None
    min_rr: float = Field(default=1.5, ge=1, le=20)
    channels: list[str] = Field(default_factory=lambda: ["app"])
    event_types: list[str] = Field(default_factory=lambda: ["signal.state_changed", "risk.vetoed"])


class ScheduleInput(BaseModel):
    favorite_id: str | None = None
    action: str = "analyze_favorite"
    interval_minutes: int = Field(default=60, ge=5, le=10080)
    enabled: bool = True
    timezone: str = "Asia/Dubai"
    execution_timeframe: str = "1h"
    context_timeframes: list[str] = Field(default_factory=lambda: ["4h"])
    strategy_id: str = "model_council"
    bot_id: str = "trading_team"
    channels: list[str] = Field(default_factory=lambda: ["app"])
    event_types: list[str] = Field(default_factory=lambda: ["analysis.completed", "signal.state_changed", "risk.vetoed"])


class ReportInput(BaseModel):
    report_type: str
    subject_id: str
    goal: dict[str, Any] | None = None


def _catalog_match(instrument_id: str, symbol: str, asset_class: str) -> dict | None:
    return next((item for item in global_training_catalog()
                 if item["instrument_id"] == instrument_id and item["symbol"] == symbol
                 and item["asset_class"] == asset_class), None)


@router.get("/api/operations/status")
def operations_status():
    return {"paper_only": True, "scheduler": scheduler.status(), "channels": channel_health(),
            "favorites": len(list_favorites()), "schedules": len(list_schedules())}


@router.get("/api/operations/catalog")
def operations_catalog(asset_class: str | None = None, query: str = "", limit: int = Query(100, ge=1, le=500)):
    return search_training_catalog(asset_class=asset_class, query=query, limit=limit)


@router.get("/api/operations/favorites")
def favorites_list():
    return {"favorites": list_favorites()}


@router.post("/api/operations/favorites")
def favorites_save(value: FavoriteInput):
    data = value.model_dump()
    match = _catalog_match(data["instrument_id"], data["symbol"], data["asset_class"])
    if not match:
        raise HTTPException(422, "The favorite must resolve in the London Strategic Edge catalog.")
    data["name"] = match["name"]
    data["provider"] = "London Strategic Edge"
    favorite = save_favorite(data)
    schedule = save_schedule({
        "favorite_id": favorite["favorite_id"], "action": "analyze_favorite",
        "interval_minutes": 10, "timezone": "Asia/Dubai",
        "execution_timeframe": favorite["execution_timeframe"],
        "context_timeframes": favorite["context_timeframes"],
        "strategy_id": favorite["strategy_id"], "bot_id": favorite["bot_id"],
        "channels": favorite["channels"],
        "event_types": ["analysis.completed", "signal.state_changed", "risk.vetoed"],
    })
    return {"favorite": favorite, "schedule": schedule}


@router.delete("/api/operations/favorites/{favorite_id}")
def favorites_delete(favorite_id: str):
    return {"deleted": delete_favorite(favorite_id)}


@router.post("/api/operations/favorites/{favorite_id}/run")
async def run_favorite(favorite_id: str):
    favorite = get_favorite(favorite_id)
    if not favorite:
        raise HTTPException(404, "Favorite not found")
    try:
        rows = await asyncio.to_thread(LSEGlobalMarketData().candles, favorite["symbol"], favorite["execution_timeframe"], 500)
        analysis = await asyncio.to_thread(backtest, favorite["strategy_id"], rows)
        council = await asyncio.to_thread(model_council, rows)
    except Exception as exc:
        event = record_event(event_type="provider.error", source="favorite_runner", subject_type="favorite",
                             subject_id=favorite_id, state="PROVIDER_ERROR", payload={"error_type": type(exc).__name__},
                             provider=favorite["provider"], dedup_key=f"provider-error:{favorite_id}:{type(exc).__name__}")
        return {"ok": False, "state": "PROVIDER_ERROR", "event": event}
    current = int(analysis.get("current_position") or 0)
    state = "POTENTIAL_LONG" if current > 0 else ("POTENTIAL_SHORT" if current < 0 else "NO_SETUP")
    tags = {favorite["asset_class"].lower(), favorite["strategy_id"].lower(), "risk"}
    selected_experts = route_experts(tags)
    supervisor_decision = "WAIT" if council.get("overall") != "MIXED / NO CLEAR EDGE" else "INSUFFICIENT_DATA"
    latest = rows[-1]
    market_asof = latest.get("timestamp") or latest.get("time") or latest.get("date")
    entry = float(latest.get("close") or latest.get("c"))
    direction = "LONG" if current > 0 else ("SHORT" if current < 0 else "NO_TRADE")
    stop = target_1 = target_2 = expected_r = None
    profit_plan = None
    if direction in {"LONG", "SHORT"} and len(rows) >= 20:
        highs = [float(row.get("high") or row.get("h")) for row in rows]
        lows = [float(row.get("low") or row.get("l")) for row in rows]
        closes = [float(row.get("close") or row.get("c")) for row in rows]
        ranges = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(rows))]
        atr = sum(ranges[-14:]) / min(14, len(ranges))
        if direction == "LONG":
            stop = min(min(lows[-20:]), entry - 1.5 * atr)
            risk = entry - stop
            target_1, target_2 = entry + risk, entry + 2 * risk
        else:
            stop = max(max(highs[-20:]), entry + 1.5 * atr)
            risk = stop - entry
            target_1, target_2 = entry - risk, entry - 2 * risk
        if risk > 0:
            expected_r, profit_plan = 2.0, "Scale at 1R; exit remainder at 2R"
    signal = create_signal(
        bot_id=favorite["bot_id"], bot_name="Trading Team", instrument=favorite["symbol"],
        asset_class=favorite["asset_class"], strategy_id=favorite["strategy_id"], direction=direction,
        score=0.0, entry=entry, stop=stop, structural_invalidation=stop,
        target_1=target_1, target_2=target_2, profit_plan=profit_plan, expected_r=expected_r,
        confidence=None, risk_status="BLOCK", eligibility="RESEARCH_ONLY",
        reason="Fresh deterministic strategy and Model Council research. Entry is blocked until qualification and complete risk approval.",
        data_source=favorite["provider"], timeframe=favorite["execution_timeframe"], ttl_seconds=600,
        metadata={"market_data_asof": market_asof, "state": state, "supervisor_decision": supervisor_decision,
                  "council_overall": council.get("overall"), "paper_only": True},
    )
    event = record_event(event_type="analysis.completed", source="favorite_runner", subject_type="favorite",
                         subject_id=favorite_id, state=state,
                         payload={"symbol": favorite["symbol"], "state": state, "entry_decision": "WAIT",
                                  "research_bias": direction, "reference_price": entry, "stop": stop,
                                  "target_1": target_1, "target_2": target_2, "signal_id": signal.signal_id,
                                  "model_score": None,
                                  "historical_return": analysis.get("total_return"), "max_drawdown": analysis.get("max_drawdown"),
                                  "win_rate": analysis.get("win_rate"), "sharpe": analysis.get("sharpe"),
                                  "model_council": council, "trading_team_experts": selected_experts,
                                  "supervisor_decision": supervisor_decision, "risk_decision": "BLOCK",
                                  "risk_reason": "The strategy has not passed qualification and portfolio-risk approval; research only.",
                                  "market_data_asof_raw": market_asof},
                         provider=favorite["provider"], evidence_ids=[signal.signal_id], versions={"strategy": "catalog-current", "runner": "1"})
    channels = favorite["channels"] if state != favorite.get("state") else ["app"]
    route_event(event, channels=channels, message=f"{favorite['symbol']} · WAIT · research bias {direction}\nRisk: BLOCK · strategy not qualified\nResearch and paper only.")
    updated = save_favorite({**favorite, "state": state, "risk_state": "BLOCK", "last_analysis_at": event["occurred_at"]})
    return {"ok": True, "state": state, "favorite": updated, "event": event}


@router.get("/api/operations/schedules")
def schedules_list():
    return {"schedules": list_schedules(), "scheduler": scheduler.status()}


@router.post("/api/operations/schedules")
def schedules_save(value: ScheduleInput):
    if value.favorite_id and not get_favorite(value.favorite_id):
        raise HTTPException(404, "Favorite not found")
    if value.action not in {"analyze_favorite", "generate_report"}:
        raise HTTPException(422, "Unsupported schedule action")
    return {"schedule": save_schedule(value.model_dump())}


@router.post("/api/operations/schedules/{schedule_id}/pause")
def schedules_pause(schedule_id: str):
    item = set_schedule_enabled(schedule_id, False)
    if not item:
        raise HTTPException(404, "Schedule not found")
    return {"schedule": item}


@router.post("/api/operations/schedules/{schedule_id}/resume")
def schedules_resume(schedule_id: str):
    item = set_schedule_enabled(schedule_id, True)
    if not item:
        raise HTTPException(404, "Schedule not found")
    return {"schedule": item}


@router.post("/api/operations/schedules/{schedule_id}/run-now")
def schedules_run_now(schedule_id: str):
    if not get_schedule(schedule_id):
        raise HTTPException(404, "Schedule not found")
    make_schedule_due(schedule_id)
    return {"processed": scheduler.run_due_once(), "schedule": get_schedule(schedule_id)}


@router.delete("/api/operations/schedules/{schedule_id}")
def schedules_delete(schedule_id: str):
    return {"deleted": delete_schedule(schedule_id)}


@router.post("/api/operations/scheduler/run-due")
def scheduler_run_due():
    return {"processed": scheduler.run_due_once(), "scheduler": scheduler.status()}


@router.get("/api/operations/events")
def events_list(limit: int = Query(100, ge=1, le=500)):
    return {"events": list_events(limit)}


@router.get("/api/operations/deliveries")
def deliveries_list(limit: int = Query(100, ge=1, le=500)):
    return {"deliveries": list_deliveries(limit), "channels": channel_health()}


@router.get("/api/operations/reports")
def reports_list(limit: int = Query(100, ge=1, le=500)):
    return {"reports": list_reports(limit)}


@router.post("/api/operations/reports")
def reports_generate(value: ReportInput):
    try:
        report = generate_report(value.report_type, value.subject_id, goal=value.goal)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
    event = record_event(event_type="report.generated", source="report_generator", subject_type=value.report_type,
                         subject_id=value.subject_id, state=report["status"], payload={"report_id": report["report_id"], "title": report["title"]},
                         evidence_ids=report["evidence_ids"], versions={"report": report["report_version"]}, input_hash=report["input_hash"])
    return {"report": report, "event": event}


@router.get("/api/operations/reports/{report_id}.md", response_class=PlainTextResponse)
def report_markdown(report_id: str):
    report = get_report(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return render_markdown(report)


@router.get("/operations", response_class=HTMLResponse)
def operations_page():
    return OPERATIONS_HTML


OPERATIONS_HTML = r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FX Favorites & Operations</title><style>
*{box-sizing:border-box}body{margin:0;background:#090a0c;color:#eee;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{position:sticky;top:0;background:#0d0f12;border-bottom:1px solid #292d33;padding:14px 22px;display:flex;justify-content:space-between;z-index:2}a{color:#c7cbd1;text-decoration:none}.wrap{max-width:1240px;margin:auto;padding:24px}.notice{border:1px solid #343941;background:#12151a;padding:14px;border-radius:10px;color:#b9bec7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px;margin:14px 0}.card{border:1px solid #2c3138;background:#111318;border-radius:10px;padding:14px}.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}input,select,button{background:#171a1f;color:#eee;border:1px solid #383e47;border-radius:7px;padding:9px}button{cursor:pointer;font-weight:650}.primary{background:#f1f2f4;color:#090a0c}.muted{color:#9299a3;font-size:12px}.badge{font-size:10px;border:1px solid #343a42;border-radius:99px;padding:4px 7px}.ok{color:#70e2a4}.warn{color:#f1c56e}pre{white-space:pre-wrap;max-height:420px;overflow:auto;font-size:12px}.tabs{display:flex;gap:8px;margin:20px 0 10px}h1,h2{margin:4px 0 10px}@media(max-width:650px){.wrap{padding:14px}.row>*{width:100%}}
</style></head><body><header><b>FX · Favorites & Operations</b><a href="/terminal">← Market Workspace</a></header><main class="wrap">
<h1>Favorites Command Center</h1><div class="notice"><b>Research + local paper only.</b> Analysis frequency does not create trades. Repeated states are deduplicated. The local scheduler requires this Mac and FX to remain running.</div>
<section class="card" style="margin-top:14px"><h2>Add a verified instrument</h2><div class="row"><select id="asset"><option>Stocks</option><option>Forex</option><option>Crypto</option><option>Indices</option><option>Commodities</option><option>ETFs</option><option>Futures</option></select><input id="search" placeholder="Search symbol or name"><select id="instrument" style="min-width:330px"></select><select id="tf"><option>5m</option><option>15m</option><option>1h</option><option>4h</option><option>1d</option></select><button class="primary" onclick="addFavorite()">★ Add favorite</button></div><p id="catalogNote" class="muted"></p></section>
<div class="tabs"><button onclick="refreshAll()">Refresh</button><span id="health" class="badge">Loading health…</span></div><div id="favorites" class="grid"></div>
<section class="card"><h2>Generate evidence report</h2><div class="row"><select id="reportType"><option>system</option><option>bot</option><option>strategy</option><option>signal</option><option>favorite</option></select><input id="reportSubject" value="fx-system" placeholder="Identity"><button class="primary" onclick="makeReport()">Generate report</button></div><div id="reportOutput" class="muted" style="margin-top:14px">No report selected.</div></section>
<div class="grid"><section class="card"><h2>Recent events</h2><div id="events" class="muted"></div></section><section class="card"><h2>Notification deliveries</h2><div id="deliveries" class="muted"></div></section></div>
</main><script>
let catalog=[]; const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function loadCatalog(){let q=document.getElementById('search').value;let a=document.getElementById('asset').value;let d=await fetch(`/api/operations/catalog?asset_class=${encodeURIComponent(a)}&query=${encodeURIComponent(q)}&limit=200`).then(r=>r.json());catalog=d.instruments;instrument.innerHTML=catalog.map((x,i)=>`<option value="${i}">${esc(x.name)} · ${esc(x.symbol)} · ${esc(x.market)}</option>`).join('');catalogNote.textContent=`${d.matched.toLocaleString()} verified matches. Showing up to 200.`}
asset.onchange=loadCatalog;search.oninput=()=>{clearTimeout(window.st);window.st=setTimeout(loadCatalog,250)};
async function addFavorite(){let x=catalog[+instrument.value];if(!x)return;await fetch('/api/operations/favorites',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({instrument_id:x.instrument_id,symbol:x.symbol,name:x.name,asset_class:x.asset_class,execution_timeframe:tf.value,context_timeframes:['4h'],strategy_id:'trend_following',bot_id:'trading_team',channels:['app']})});refreshAll()}
async function removeFavorite(id){await fetch(`/api/operations/favorites/${id}`,{method:'DELETE'});refreshAll()}
async function runFavorite(id){await fetch(`/api/operations/favorites/${id}/run`,{method:'POST'});refreshAll()}
async function scheduleFavorite(id){await fetch('/api/operations/schedules',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({favorite_id:id,action:'analyze_favorite',interval_minutes:10,channels:['app'],event_types:['analysis.completed','signal.state_changed','risk.vetoed']})});refreshAll()}
function readable(v){if(v===null||v===undefined||v==='')return 'Unknown';if(Array.isArray(v))return v.length?`<ul>${v.map(x=>`<li>${readable(x)}</li>`).join('')}</ul>`:'None recorded';if(typeof v==='object')return Object.entries(v).map(([k,z])=>`<div style="margin:4px 0"><b>${esc(k.replaceAll('_',' '))}:</b> ${readable(z)}</div>`).join('');return esc(v)}
async function makeReport(){let response=await fetch('/api/operations/reports',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report_type:reportType.value,subject_id:reportSubject.value})});let d=await response.json();if(!response.ok){reportOutput.textContent=d.detail||'Report failed.';return}let r=d.report;reportOutput.innerHTML=`<h3>${esc(r.title)}</h3><p><span class="badge">${esc(r.status)}</span> <a href="/api/operations/reports/${r.report_id}.md" target="_blank">Export Markdown</a></p>`+Object.entries(r.body||{}).map(([k,v])=>`<details><summary><b>${esc(k.replaceAll('_',' '))}</b></summary><div style="padding:8px 0">${readable(v)}</div></details>`).join('')}
function row(x){return `<div><b>${esc(x.event_type||x.channel)}</b> · ${esc(x.state||x.status||'')}<br><span class="muted">${new Date(1000*(x.occurred_at||x.requested_at)).toLocaleString()}</span></div><hr style="border-color:#24282e;border-width:1px 0 0">`}
async function refreshAll(){let [s,f,e,d,sc]=await Promise.all(['/api/operations/status','/api/operations/favorites','/api/operations/events?limit=50','/api/operations/deliveries?limit=12','/api/operations/schedules'].map(u=>fetch(u).then(r=>r.json())));health.textContent=`Scheduler ${s.scheduler.status} · App ${s.channels.app.status} · Telegram ${s.channels.telegram.status} · Discord ${s.channels.discord.status}`;health.className='badge '+(s.scheduler.status==='HEALTHY'?'ok':'warn');let counts={},intervals={};(sc.schedules||[]).forEach(x=>{counts[x.favorite_id]=(counts[x.favorite_id]||0)+1;intervals[x.favorite_id]=x.interval_minutes});let latest={};(e.events||[]).filter(x=>x.event_type==='analysis.completed').forEach(x=>{if(!latest[x.subject_id])latest[x.subject_id]=x});favorites.innerHTML=(f.favorites||[]).map(x=>{let ev=latest[x.favorite_id],p=ev?.payload||{};let brief=ev?`<div class="notice" style="margin:10px 0"><b>10-minute brief: ${esc(p.entry_decision||'WAIT')}</b> · bias ${esc(p.research_bias||'NO_TRADE')}<br><span class="muted">Reference ${esc(p.reference_price??'Unknown')} · stop ${esc(p.stop??'Unknown')} · TP1 ${esc(p.target_1??'Unknown')} · TP2 ${esc(p.target_2??'Unknown')}<br>Data as of ${esc(p.market_data_asof_raw||'Unknown')} · checked ${new Date(ev.occurred_at*1000).toLocaleString()}<br>${esc(ev.provider||x.provider)} · Risk ${esc(p.risk_decision||'BLOCK')}</span></div>`:'';return `<article class="card"><div class="row" style="justify-content:space-between"><h2>★ ${esc(x.symbol)}</h2><span class="badge ${x.risk_state==='BLOCK'?'warn':'ok'}">${esc(x.state)}</span></div><p>${esc(x.name)} · ${esc(x.asset_class)}</p><p class="muted">${esc(x.provider)} · ${esc(x.execution_timeframe)}<br>Strategy: ${esc(x.strategy_id)} · Squad: ${esc(x.bot_id)}<br>Risk: ${esc(x.risk_state)} · Monitor: ${intervals[x.favorite_id]?`every ${intervals[x.favorite_id]} min`:'off'}</p>${brief}<div class="row"><button onclick="runFavorite('${x.favorite_id}')">Run analysis</button><button onclick="scheduleFavorite('${x.favorite_id}')">Monitor every 10m</button><button onclick="reportType.value='favorite';reportSubject.value='${x.favorite_id}';makeReport()">Report</button><button onclick="removeFavorite('${x.favorite_id}')">Remove</button></div></article>`}).join('')||'<p class="muted">No favorites yet.</p>';events.innerHTML=(e.events||[]).slice(0,12).map(row).join('')||'No events.';deliveries.innerHTML=(d.deliveries||[]).map(row).join('')||'No deliveries.'}
loadCatalog();refreshAll();setInterval(refreshAll,30000);
</script></body></html>'''

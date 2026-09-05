from __future__ import annotations

import base64
import os
import secrets
import time

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from services.auth.approval import ApprovalPayload, issue_live_approval
from services.auth.session import COOKIE_NAME, issue_session
from services.auth.totp import totp_service
from services.monitoring.sentinel import sentinel

router = APIRouter(tags=["security"])


class EnrollRequest(BaseModel):
    rotate: bool = False
    current_code: str = ""


class CodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=32)


class LiveApprovalRequest(BaseModel):
    proposal_id: str
    instrument: str
    side: str
    quantity: float = Field(gt=0)
    order_type: str
    max_notional: float = Field(gt=0)
    risk_decision_id: str
    totp_code: str = Field(min_length=6, max_length=8)


def _set_session(response: Response) -> None:
    response.set_cookie(
        COOKIE_NAME,
        issue_session(),
        httponly=True,
        secure=os.getenv("FX_SECURE_COOKIE", "false").lower() == "true",
        samesite="strict",
        max_age=8 * 60 * 60,
        path="/",
    )


@router.get("/security", response_class=HTMLResponse)
def security_page():
    return r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FX Security & Health</title><style>
:root{color-scheme:dark;--bg:#090a0c;--panel:#121419;--line:#2c3037;--text:#f4f5f6;--muted:#9ca2ac;--good:#70dca0;--warn:#f0c56b;--bad:#ff858b}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:920px;margin:auto;padding:36px 22px}a{color:var(--muted);text-decoration:none}h1{font-size:30px;margin:24px 0 7px}.lead{color:var(--muted);line-height:1.55}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:24px}.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}.card h2{font-size:17px;margin:0 0 9px}.row{display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--line);padding:11px 0}.status{font-size:11px;font-weight:750}.PASS{color:var(--good)}.WARN,.ACTION,.ATTENTION{color:var(--warn)}.BLOCK{color:var(--bad)}input,button{border-radius:8px;padding:11px;border:1px solid var(--line);background:#191c21;color:var(--text)}button{background:#f3f4f5;color:#111;font-weight:750;cursor:pointer}.form{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}#qr{max-width:240px;background:#fff;padding:8px;border-radius:8px;margin-top:12px}.secret{font:12px ui-monospace;word-break:break-all;color:var(--muted)}#recovery{white-space:pre-wrap;font:12px ui-monospace;color:var(--warn)}@media(max-width:700px){.grid{grid-template-columns:1fr}}
</style></head><body><main><a href="/terminal">← FX Terminal</a><h1>Security & Health</h1><p class="lead">The local sentinel runs with FX and continuously checks the safety environment. Enrolling two-factor authentication activates the access gate for the terminal and API.</p><div class="grid"><section class="card"><h2>Google Authenticator compatible 2FA</h2><p id="authState" class="lead">Checking enrollment…</p><div id="enroll"><button onclick="begin()">Begin secure enrollment</button></div><img id="qr" hidden alt="TOTP enrollment QR code"><p id="secret" class="secret"></p><div class="form"><input id="code" autocomplete="one-time-code" inputmode="numeric" placeholder="6-digit code or recovery code"><button onclick="verify()">Verify and unlock</button><button onclick="logout()">Lock session</button></div><p id="message" class="lead"></p><pre id="recovery"></pre></section><section class="card"><h2>Autopilot sentinel</h2><p class="lead">Checks every minute. It can report or block unsafe operation; it cannot enable live trading or change risk limits.</p><div id="checks"></div></section></div></main><script>
let enrolled=false;async function load(){const s=await fetch('/api/security/totp/status').then(r=>r.json());enrolled=!!s.enrolled;document.getElementById('authState').textContent=enrolled?'2FA is enrolled. Enter a current code to unlock this browser session.':'2FA is not enrolled. Begin setup, scan the QR code, then confirm a current code.';document.getElementById('enroll').hidden=enrolled;const h=await fetch('/api/security/sentinel').then(r=>r.json());const root=document.getElementById('checks');root.replaceChildren();(h.checks||[]).forEach(c=>{const row=document.createElement('div');row.className='row';const text=document.createElement('div');text.textContent=c.name+' — '+c.detail;const state=document.createElement('span');state.className='status '+c.status;state.textContent=c.status;row.append(text,state);root.append(row)})}
async function begin(){const r=await fetch('/api/security/totp/enroll',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"rotate":false}'}),d=await r.json();if(!r.ok){document.getElementById('message').textContent=d.detail||'Enrollment could not start.';return}const qr=document.getElementById('qr');qr.src='data:image/png;base64,'+d.qr_png_base64;qr.hidden=false;document.getElementById('secret').textContent='Manual setup key: '+d.secret;document.getElementById('message').textContent='Scan this once, then enter the current code below.'}
async function verify(){const code=document.getElementById('code').value.trim(),path=enrolled?'/api/security/totp/login':'/api/security/totp/confirm';const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})}),d=await r.json();if(!r.ok){document.getElementById('message').textContent=d.detail||'Verification failed.';return}document.getElementById('message').textContent='This browser is unlocked for 8 hours.';if(d.recovery_codes){document.getElementById('recovery').textContent='Save these single-use recovery codes offline now:\n'+d.recovery_codes.join('\n')}enrolled=true;setTimeout(()=>location.href='/terminal',1200)}
async function logout(){await fetch('/api/security/totp/logout',{method:'POST'});document.getElementById('message').textContent='Session locked.'}load().catch(()=>document.getElementById('message').textContent='Security status is temporarily unavailable.');setInterval(load,30000);
</script></body></html>'''


@router.get("/api/security/totp/status")
def totp_status():
    return {"enrolled": totp_service.is_enrolled(), "retry_after": totp_service.retry_after()}


@router.post("/api/security/totp/enroll")
def totp_enroll(req: EnrollRequest):
    try:
        result = totp_service.enroll(rotate=req.rotate, current_code=req.current_code)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return {"secret": result["secret"], "provisioning_uri": result["provisioning_uri"], "qr_png_base64": base64.b64encode(result["qr_png"]).decode(), "warning": "Displayed once. Store the recovery codes after confirmation."}


@router.post("/api/security/totp/confirm")
def totp_confirm(req: CodeRequest, response: Response):
    try:
        result = totp_service.confirm_enrollment(req.code)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    _set_session(response)
    sentinel.run_once()
    return {"ok": True, **result}


@router.post("/api/security/totp/login")
def totp_login(req: CodeRequest, response: Response):
    if not totp_service.verify(req.code, allow_recovery=True):
        raise HTTPException(status_code=429 if totp_service.retry_after() else 403, detail="Invalid code. Five failed attempts lock verification for 60 seconds.")
    _set_session(response)
    return {"ok": True}


@router.post("/api/security/totp/logout")
def totp_logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/api/security/sentinel")
def sentinel_status():
    return sentinel.status()


@router.post("/api/security/live-approval")
def live_approval(req: LiveApprovalRequest):
    ttl = int(os.getenv("FX_LIVE_APPROVAL_TTL_SECONDS", "90"))
    payload = ApprovalPayload(proposal_id=req.proposal_id, instrument=req.instrument, side=req.side, quantity=req.quantity, order_type=req.order_type, max_notional=req.max_notional, risk_decision_id=req.risk_decision_id, expires_at=int(time.time()) + ttl, nonce=secrets.token_hex(16))
    try:
        token = issue_live_approval(payload, req.totp_code)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return {"approval_token": token, "expires_at": payload.expires_at, "payload": payload.__dict__}

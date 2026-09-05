# FX full-conversation acceptance audit — 2026-09-05

This audit maps the accumulated requests in the FX conversation and the four source plans to observable application behavior. The source plans were read from `docs/fx_prompt.md`, `docs/fx_repair_plan.md`, `docs/fx_forensic_report.md`, and `docs/fx_plus.md`.

## Runtime acceptance matrix

| Requirement | Status | Runtime evidence |
|---|---|---|
| Only chat scrolls in the four-column terminal | Verified | The document and lateral columns are height-locked; `.messages` is the persistent scrolling region. Overlay pages may scroll within their own panel. |
| Paper Portfolio and Journal navigation | Verified | `/paper-local` and `/journal` return HTTP 200 and are linked from the terminal. |
| Multi-asset local paper orders | Verified | Local SQLite paper broker supports Stocks, ETFs, Indices, Forex, Commodities, Crypto and Futures without requiring Alpaca. |
| Mandatory protection for paper orders | Verified | Broker rejects missing stop, structural invalidation, profit plan, or maximum loss. Eight legacy AAPL positions were migrated to explicit protection plans from their latest stored marks. |
| Live marks and moving paper P&L | Verified with provider limits | Position marks refresh from London Strategic Edge; the UI refreshes every 30 seconds. Values move only when the provider has a new valid market mark. |
| Bot identity and bot protection suggestions | Verified | Selecting a bot populates order identity; BUY/SELL produces a structural stop and three profit-plan choices from provider OHLCV. |
| Personal AI chat with local knowledge and memory | Verified | SQLite retains private questions and answers. A live job correctly listed local strategies and bots. Market answers distinguish provider facts from model analysis. |
| Global stock and forex catalogs | Verified | The Training Center uses the local London Strategic Edge catalog rather than short hard-coded lists. Current stock catalog count is 3,982 and forex includes more than 50 pairs. |
| Multi-symbol and multi-asset training | Verified | The queue accepts lists across Stocks, ETFs, Indices, Forex, Commodities and Crypto. Evidence is grouped by asset and symbol. |
| XRP training evidence | Verified | Ten XRP/USD 1-hour, 10-period model records are present under Crypto. They are research-complete and currently ineligible. |
| Honest model qualification | Verified | Working models are labeled `WORKING · NOT QUALIFIED`; failures remain failures. No metric or approval is fabricated. Latest acceptance snapshot: 100 recorded runs, 81 completed safely, 81 qualification-blocked, 19 run failures, 0 paper-eligible; 25 records were in examination. Continuous learning remains active, so these counts change. |
| Start/Pause learning state | Verified | Continuous learner reports its actual worker/resource state and retries under resource pressure. |
| All bot scanners running | Verified | Equity, forex, crypto, gold, commodities, indices, ETF and futures scanners report RUNNING. They are watch-only and cannot place orders. |
| Persistent Favorites | Verified | Favorites are stored in SQLite with exact catalog identity, provider, asset class, timeframes, strategy, bot, risk state and notification policy. |
| Every-favorite 10-minute signal brief | Verified | Adding any favorite automatically creates a persistent 10-minute analysis schedule. The card shows BUY/SELL/WAIT, research bias, provider reference price, stop, targets, data timestamp and risk decision. It never converts an unqualified model into an entry. |
| Current AAPL brief | Verified | AAPL 5-minute analysis returned WAIT, SHORT research bias, reference 320.07, stop 320.20, targets 319.94/319.81, LSE data as of 2026-09-04 23:55 UTC, risk BLOCK. |
| Standard signal/event contracts | Verified | Versioned Pydantic contracts reject actionable eligibility without protection and deterministic risk approval. Events store provenance, evidence IDs and hashes. |
| On-demand reports | Verified | Bot, strategy, signal, favorite, goal and system reports persist locally, render as readable sections, and export Markdown. Missing evidence stays explicit. |
| Persistent scheduler | Verified | SQLite schedules have interval, next/last run, lease, run history, pause/resume/run-now and restart persistence. Runtime status is HEALTHY. |
| Notification router | Implemented; local verified | The app inbox is connected with deduplication, attempts and backoff. Telegram and Discord adapters are present but truthfully report NOT_CONFIGURED until credentials are supplied. |
| Council/team/supervisor integration | Verified for research | Favorite analysis invokes the existing Model Council, sparse expert selection, trading-team identity, supervisor decision and deterministic risk block. |
| Journal/evaluation | Verified | Protected paper fills and closes append canonical operation events and remain available in the local journal. |
| 2FA and app security | Implemented; enrollment required | RFC 6238/TOTP enrollment, QR, recovery codes, throttling and signed sessions are implemented. The sentinel reports ACTION until the owner completes enrollment on `/security`. |
| Always-on security/health agent | Verified | The sentinel starts with FX, checks live policy, disk, TOTP, secret permissions, SQLite integrity and CPU, and makes six-hour SQLite backups with retention. It cannot change risk controls. |
| Live autonomous trading | Intentionally locked | `AI_CAN_EXECUTE_LIVE=false`. No LLM or bot can enable or execute live orders. Live trading still requires qualified strategies, reconciliation, healthy systems, kill-switch clearance, deterministic risk, human approval and TOTP. |

## Upgrade-plan phase status

1. Persistent Favorites — complete.
2. Standard signal and event contracts — complete for the local operating layer.
3. On-demand Bot/Strategy/Signal/Goal reports — complete.
4. Persistent scheduler — complete for the local FX runtime.
5. Unified notification router — complete; external delivery awaits credentials.
6. Telegram and Discord — adapters complete; end-to-end external delivery not tested without owner credentials/recipients.
7. Model Council, Trading Team and Supervisor integration — complete for favorite research analysis.
8. Deterministic risk gate — enforced for actionable signals and paper orders.
9. Journal and evaluation — canonical paper events complete; long-horizon promotion evidence continues to accumulate.
10. UI — operations page, reports, favorites, 10-minute brief, security, learning and protected paper UI complete.
11. QA — local project suite, compile, route, JavaScript, runtime API, paper-safety, signal-contract and health checks pass. Third-party source trees are excluded from project test discovery.

## Honest remaining blockers

- Strategy qualification is evidence-gated. Current models do not pass the required locked holdout, calibration, walk-forward and portfolio-risk conditions. Lowering labels or thresholds merely to display QUALIFIED would corrupt the research record.
- TOTP protection becomes active only after the owner scans the QR and confirms a current code on `/security`.
- Telegram and Discord need owner-supplied credentials and destination identifiers. Secrets must remain in `.env`/the local credential mechanism and must not be committed.
- Live brokerage execution remains deliberately unavailable. It is a later, separately approved phase after qualification and operational gates pass.
- GitHub publication requires a valid authenticated GitHub CLI session; the previously stored token for `JBENITE9-111` is invalid.

## QA evidence

- `python -m pytest -q`: 17 passed.
- `python -m compileall -q backend services tests`: passed.
- Inline JavaScript syntax: terminal, learning, local paper, security and operations passed `node --check`.
- Required route inventory: passed; all representative pages returned HTTP 200.
- Runtime bots: 8 of 8 RUNNING, 0 allowed to place orders.
- Runtime paper positions: 8 of 8 include stop, structural invalidation, profit plan and maximum loss.
- Runtime scheduler: HEALTHY, one AAPL favorite and one 10-minute schedule.
- Security sentinel: running in autopilot; live policy, disk, secret permissions, SQLite integrity, CPU and backups pass; TOTP enrollment remains an owner action.
- Latest learning snapshot: 100 recorded runs, 81 completed safely, 81 qualification-blocked, 19 failed, 0 paper-eligible and 25 in examination.

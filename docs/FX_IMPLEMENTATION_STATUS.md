# FX Implementation Status

Verified against the running local application and repository on 2026-09-06.
This is an evidence ledger, not a profitability claim.

## Working and verified

- The API is healthy at `/health`; live trading and AI live execution are off.
- Google Authenticator compatible TOTP protects browser access and automation
  startup. The sentinel, backup checks, and 11-member health/operations team are
  running.
- Eight watch-only scanners cover the supported market groups. They research;
  they cannot place orders and are not described as learning bots.
- Continuous model research is running across a bounded 228-target multi-asset
  universe. Failed runs remain evidence and are not promoted.
- Favorites, ten-minute local scheduling, reports, event contracts,
  deduplication, app notifications, and Discord routing are implemented.
  Telegram is not part of the active notification architecture.
- Local paper execution requires strategy/bot identity, stop, structural
  invalidation, profit plan, and maximum loss. Qualified fleet execution now
  also requires and forwards those fields plus a stable signal ID.
- Chat has private SQLite history and a **Clear screen** control that keeps
  memory. Its grounded context includes the local strategy/bot inventory and
  verified market context.
- OpenRouter/Ollama committee routing, optional Goose/Freellmapi routes, and
  optional Headroom context compression exist. Model prose cannot bypass risk.
- Newspaper, strategy fleet, learning, terminal, operations, security, signal,
  journal, strategy, bot, reporting, and market routes are mounted.
- The Git remote is `https://github.com/JBENITE9-111/FX.git` on `main`.
- Ruflo 3.38.21 is installed as a bounded Codex coordination layer. See
  `docs/RUFLO_CODEX_ARCHITECTURE.md` for the verified limitations.

## Running state at verification

```text
FX API                 HEALTHY
Automation gate        UNLOCKED after TOTP
Security/health agents 11 running; kill switch clear
Watch scanners         8 / 8 running
Learning               RUNNING; 228 approved targets
Paper eligible models  0
Live trading           DISABLED
AI live execution      DISABLED
```

The 16 paper-fleet strategy records are research simulations. Their NAV and
direction values are not approved signals. Open positions are local paper
positions; marks and P&L move only when verified market updates are received.

## Incomplete or blocked

1. **Qualification evidence:** no model has cleared calibration, realistic
   spread/slippage/cost stress, parameter stability, Monte Carlo,
   multiple-testing controls, locked holdout, independent replay, and paper
   examination. Therefore paper eligibility remains zero.
2. **Experiment ledger:** model runs need immutable manifests and a complete
   research-family trial count so failed searches cannot disappear.
3. **Specialist data:** pairs, cross-sectional, regime, carry, positioning,
   activist, and options strategies still need their required verified inputs.
   FX must keep returning `NO_TRADE` where evidence is missing.
4. **Portfolio risk:** currency, correlation, concentration, liquidity, and
   combined exposure controls need deeper portfolio-level evidence.
5. **Reconciliation:** backtest-to-paper behavior and fills need a visible,
   deterministic comparison before any promotion path can be complete.
6. **Institutional desk hierarchy:** the current model council, supervisor,
   health agents, scanners, and strategy fleet provide a foundation. The full
   independent specialist desk described in the research notes is not complete.
7. **Nautilus compatibility:** this remains a design proposal. It has not been
   implemented or represented as operational.
8. **Ruflo memory:** its SQLite file passes structural integrity, but Ruflo
   store/search/status are blocked because upstream `onnxruntime-node` 1.24.3
   has no Darwin x64 binding. Existing FX databases remain authoritative.
9. **GitHub CLI:** the repository remote is connected, but `gh auth status`
   currently reports an invalid token and requires interactive reauthentication.
10. **Always-on operation:** this Intel Mac must remain awake with FX running.
    Local workers cannot continue while the computer is off.

## Next implementation phase

Build the qualification evidence pipeline before increasing bot count:

```text
immutable experiment manifest
-> calibration and cost/slippage stress
-> parameter stability and Monte Carlo
-> multiple-testing controls and locked holdout
-> independent replay
-> protected paper examination
-> portfolio/currency risk
-> backtest-to-paper reconciliation UI
```

An 85% value may be displayed only as an empirically calibrated probability for
a specific signal with adequate comparable samples. It is not a target accuracy
that every bot can be forced to reach.

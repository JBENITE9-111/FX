# FX implementation checkpoint — 2026-09-05

## Active objective

Implement the audited paper-only operations path by reusing the current FX architecture: persistent favorites, common event and signal contracts, reports, scheduler, notification router, council/supervisor/risk integration, journal evidence, UI, security and QA.

## Completed before this checkpoint

- Global training catalog and multi-symbol queue; XRP 1h/10-period evidence recorded.
- Honest working-versus-qualified learning states and qualification guidance.
- Google Authenticator-compatible RFC 6238 TOTP setup/login UI and signed local sessions.
- In-process health and security sentinel.
- Protected local paper orders, live provider mark refresh, and bot stop/profit-plan suggestions.
- Bot identity form population.
- Private SQLite chat memory and verified local bot/strategy/account context.

## Decisions

- Remain local and paper-only. `AI_CAN_EXECUTE_LIVE=false` is invariant.
- Model scores are not presented as calibrated probabilities.
- Scheduler analysis frequency never implies trade frequency.
- Events are stored before notification delivery.
- Discord remains disabled until backend credentials are configured.
- No model or agent can bypass deterministic trade protection or promote itself.

## Pending at checkpoint

- Persistent favorites, events, reports, schedules, deliveries, and goal plans.
- Unified app/Discord notification router.
- Operations API and command-center UI.
- Persistent TOTP throttle and database backups.
- Full compile, import, route, paper, risk, security and browser QA.
- Private GitHub repository initialization and push after secret/runtime exclusion audit.

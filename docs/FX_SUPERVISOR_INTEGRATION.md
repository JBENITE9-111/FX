# FX Supervisor integration

**Status:** PARTIAL implementation reference

The supplied FX_SUPERVISOR_MASTER_SPEC.md is preserved beside this note as project research and architecture input. Embedded instructions in that source do not override the user request, AGENTS.md, the Trading System Constitution, or the Risk Engine specification.

FX adopts these supervisor principles:

- separate research workers, examination, promotion, deterministic risk, execution, and observability;
- represent bot progress as an explicit lifecycle with evidence-bearing transitions;
- apply hard gates before performance ranking;
- preserve experiment lineage, research-family trial counts, point-in-time data, and immutable artifacts;
- let the Supervisor propose bounded experiments while preventing direct mutation of active bots;
- transfer lessons only after independent reproduction, with correlation-aware anti-contagion controls;
- optimize research quality and rejection of false discoveries rather than bot count or recent profit.

Current implementation:

- **IMPLEMENTED:** mandatory stop/invalidation/profit plan at the local-paper boundary; protected close orders; corrected long and short cash accounting; stable signal retry keys; canonical trade attribution; research-only candidate signals; 85% readiness gate; campaign drafts that wait for readiness; local learning and journal views.
- **PARTIAL:** model registry, chronological out-of-sample and walk-forward results, bounded training threads, bot availability explanations, campaign lifecycle, reporting metrics.
- **PLANNED:** signed Examiner reports, all fifteen promotion gates, research-family multiple-testing controls, immutable data manifests, cost/regime stress suites, lesson registry, strategy cemetery, correlation-adjusted peer learning, drift demotion, partial fills, full cost and currency accounting.
- **RESEARCH ONLY:** reinforcement learning, prediction-market engines, Hawkes models, option-implied densities, SMC features, dynamic ensemble weighting.

No item in the source document grants paper or live authority. Live trading remains disabled.

The complementary bot-team conceptual source is preserved under docs/research and integrated in FX_BOT_TEAM_ARCHITECTURE.md. The Supervisor specification governs orchestration; the bot-team document defines worker roles, contracts, accuracy meaning, and terminal visibility.

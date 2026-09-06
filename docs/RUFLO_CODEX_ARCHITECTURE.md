# Ruflo + Codex Architecture for FX

## Purpose

Ruflo 3.38.21 supports engineering coordination, independent review, bounded
workflows, and durable non-secret project memory. Codex writes and validates the
code and remains the final engineering authority. Ruflo never participates in
market execution and never receives trading authority.

```text
Codex final review
        |
Ruflo engineering supervisor
        |
+-------+----------+----------+-----------+
|                  |          |           |
Architecture   Engineering   Research   Independent review

Independent evidence -> tests -> trading validation -> risk review -> red team
```

This layer is separate from the in-app market and operations agents documented
in `docs/AGENT_ARCHITECTURE.md`, `docs/FX_BOT_TEAM_ARCHITECTURE.md`, and
`docs/FX_SUPERVISOR_INTEGRATION.md`. Existing FX signals, deterministic risk,
TOTP, local paper broker, journal, scheduler, scanners, and learning services
remain authoritative.

## Installed surface

- Ruflo version: pinned to `3.38.21`.
- Local runtime config: `.claude-flow/config.yaml`.
- Wrapper: `scripts/ruflo`.
- Memory database: a structurally valid local SQLite schema exists under
  ignored `.claude-flow/data/`. Ruflo store and semantic verification are
  blocked on Intel macOS because Ruflo's `onnxruntime-node` 1.24.3 package does
  not include a Darwin x64 binding. Do not represent Ruflo memory as active;
  existing FX SQLite evidence and chat memory remain authoritative.
- Topology: hierarchical, specialized, maximum six roles, no autoscaling.
- Daemon, automatic hooks, neural learning, HNSW, federation, cloud sync, and
  provider-executing agents: disabled.

The official `npx skills add ruvnet/ruflo --skill ruflo --yes` command was
tested. Its installer clones the complete upstream repository before pruning,
which was slow and left a large partial tree when interrupted. FX therefore
keeps only the verified core skill file and its lock hash; it does not vendor
the upstream repository.

## Selected roles

Use only roles needed by the change. A normal significant trading-system change
uses four to six independent responsibilities:

1. Researcher or quant researcher defines the claim and required evidence.
2. Backend/frontend/data/ML engineer implements within existing modules.
3. QA engineer verifies behavior and regression risk.
4. Backtesting specialist reviews costs, leakage, OOS and walk-forward evidence.
5. Risk manager checks deterministic policy and portfolio implications.
6. Adversarial reviewer attempts to reject the change before Codex decides.

The same worker must not both implement and approve a material trading change.
Disagreement is retained in the task evidence rather than averaged away.

## Required workflow

```text
RESEARCH
-> IMPLEMENTATION
-> TESTING
-> BACKTEST / EVIDENCE REVIEW
-> DETERMINISTIC RISK REVIEW
-> ADVERSARIAL REVIEW
-> FINAL CODEX REVIEW
```

Stages that do not apply may be marked `not_applicable` with a reason. Trading
changes cannot skip backtest/evidence and risk review. A Ruflo result is advice;
it cannot promote a strategy or authorize an order.

## Memory policy

Allowed namespaces should stay narrow, for example:

- `fx/architecture`
- `fx/bugs`
- `fx/rejected-approaches`
- `fx/experiments`
- `fx/data-limitations`
- `fx/risk-rules`
- `fx/testing`

Store summaries with source paths, commit IDs, evidence IDs, timestamps, and a
trust label. Preserve negative results and failed experiments. Do not store
prices or performance metrics unless they identify an authoritative FX record.

Never store API keys, passwords, broker credentials, OAuth tokens, Discord
webhooks, TOTP secrets, signing material, private keys, or unredacted logs.

## Plugins and capabilities

No optional Ruflo plugin is enabled initially. The core MCP memory, task, swarm,
status, and workflow metadata are sufficient for the first integration.

Plugin discovery was inspected on 2026-09-06. Ruflo reported a registry
signature-verification failure and fell back to its demo registry. FX installs
nothing from that fallback. Reconsider optional plugins only after the registry
signature verifies and their permissions have been reviewed.

Potential later additions after the core proves stable:

- security audit for dependency and code scans;
- test-gap analysis;
- diff-risk review;
- workflow templates;
- observability for agent traces;
- RAG memory if plain SQLite retrieval becomes insufficient.

Intentionally excluded:

- `neural-trader` and `market-data`, which duplicate FX trading/data systems;
- autopilot and loop workers, which duplicate the FX scheduler and add
  autonomous mutation risk;
- federation and hosted memory, which expand the data boundary;
- browser automation, because Codex already has controlled browser tooling;
- ruvLLM/intelligence/provider execution, which duplicates the FX model council
  and requires additional provider credentials;
- large skill/plugin catalogs, which add noise and maintenance cost.

## Trading safeguards

Paper trading remains the default. `AI_CAN_EXECUTE_LIVE=false` must remain set.
Ruflo must not receive broker or TOTP secrets and must not be wired into app
startup, automation unlock, signals, orders, or execution.

Every actionable FX signal still requires instrument, asset class, direction,
strategy and bot IDs, timestamp, entry policy, structural invalidation, stop,
profit plan, targets, size, maximum loss/account risk, expected holding period,
regime, empirically calibrated confidence, rationale, eligibility, risk status,
and data provenance. Missing protection produces `NO_TRADE`.

## Operations

```bash
cd /Users/macmac/Documents/Codex/FX

# Version and health
./scripts/ruflo --version
./scripts/ruflo status
./scripts/ruflo doctor

# MCP and plugin inspection
codex mcp get ruflo
./scripts/ruflo mcp --help
./scripts/ruflo plugins list

# Memory
./scripts/ruflo memory stats

# Bounded coordination status
./scripts/ruflo swarm status

# FX and Codex startup
./scripts/start-api.sh
cd /Users/macmac/Documents/Codex/FX && codex
```

On this Intel Mac, `--version`, `doctor`, `swarm status`, and the MCP handshake
work. The upstream `status` command and memory store/search currently fail while
loading `onnxruntime-node` because version 1.24.3 has no Darwin x64 native
binding. Treat that failure as an upstream platform blocker. Do not rebuild or
force-migrate the structurally valid database to hide it.

Do not run `init --force`, `memory init --force`, `--full`, `--all-agents`,
`--start-all`, `daemon start`, federation commands, or bulk plugin installation
without a fresh review and backup.

## Upgrade procedure

1. Read the official Ruflo release notes and open security issues.
2. Back up `.claude-flow/data/` outside Git.
3. Change the pinned version in `scripts/ruflo` and the MCP registration.
4. Run version, doctor, MCP handshake, memory store/restart/retrieve, and FX QA.
5. Revert the pin if memory compatibility or process cleanup fails.

The global Codex MCP entry should use `scripts/ruflo mcp start` or the pinned
equivalent with `CLAUDE_FLOW_CWD=/Users/macmac/Documents/Codex/FX` and a 120
second startup/tool timeout. A new Codex session is required before newly
registered MCP tools appear.

## Current FX improvement priority

The pasted analyses reinforce the current constitution rather than replacing
it. The next high-value product work is the unfinished qualification pipeline:
immutable experiment manifests, empirical calibration, realistic cost and
slippage stress, parameter stability, Monte Carlo, multiple-testing controls,
locked holdout, independent replay, protected qualified-signal execution, and
portfolio/currency risk. Example prices, returns, confidence scores, external
repository claims, and large bot counts remain hypotheses until independently
verified.

## Troubleshooting

- If `npx` reports root-owned files in `~/.npm`, use `scripts/ruflo`; it uses an
  ignored project cache and does not require `sudo chown`.
- If Ruflo tools do not appear, verify the MCP entry and restart Codex from the
  FX root.
- Inspect the Codex registration with `codex mcp get ruflo`. It is pinned to the
  absolute FX wrapper and exposes only memory, swarm, task, workflow, and system
  tool groups.
- A missing Anthropic key can be non-blocking in this Codex-only coordination
  mode. Do not copy FX provider keys into Ruflo merely to silence the warning.
- If memory fails, preserve `.claude-flow/data/` before repair. Never use
  `--force` on an existing memory database.

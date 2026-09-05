# FX repository structure

| Path | Purpose | Version-control policy |
|---|---|---|
| `backend/` | FastAPI routes, pages, and existing application services | Tracked |
| `services/` | Domain services for risk, paper execution, learning, security, operations, reports, notifications, and monitoring | Tracked |
| `tests/` | FX-owned automated acceptance tests | Tracked |
| `scripts/` | Launch, diagnostics, maintenance, and integration utilities | Tracked |
| `infrastructure/` | Local service definitions | Tracked |
| `docs/` | Active specifications, QA evidence, and curated research | Tracked |
| `docs/archive/` | Superseded or third-party source material retained only for provenance | Tracked, inactive |
| `data/catalog/` | Canonical instrument catalog | Tracked |
| `data/*` | Runtime databases, models, market data, evidence, and memory | Ignored |
| `external/` | Installed OpenBB and Backtrader systems preserved by project policy | Ignored |
| `vendor/` | Registered untrusted/reference research repositories | Ignored |
| `.venv-core/`, `.venv-kronos/` | Local Python runtimes | Ignored |
| `backups/`, `logs/`, `outputs/` | Runtime and generated artifacts | Ignored |

Run `scripts/clean-workspace.sh` to remove only reproducible caches and macOS
metadata. It deliberately preserves runtime evidence, environments, backups,
logs, registered external systems, and generated deliverables.

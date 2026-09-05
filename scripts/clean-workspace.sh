#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Remove only reproducible development caches and macOS metadata. Runtime data,
# evidence, reports, logs, environments, backups, and downloaded systems remain.
find backend services scripts tests -type d -name __pycache__ -prune -exec rm -rf {} +
find . -name .DS_Store -type f -delete
rm -rf .pytest_cache .ruff_cache .mypy_cache

echo "FX workspace caches cleaned."

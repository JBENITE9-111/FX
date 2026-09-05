#!/bin/bash

set -e

ROOT="/Users/macmac/Documents/Codex/FX"

cd "$ROOT"

source .venv-core/bin/activate

echo ""
echo "FX SYSTEM CHECK"
echo "=================================================="
echo ""

python --version

echo ""

python - <<'PY'
packages = [
    "fastapi",
    "pandas",
    "polars",
    "duckdb",
    "alpaca",
    "ccxt",
    "lightgbm",
    "xgboost",
    "skfolio",
]

for package in packages:
    try:
        __import__(package)
        print(f"✓ {package}")
    except Exception as exc:
        print(f"✗ {package}: {exc}")
PY

echo ""

python scripts/check-credentials.py

echo ""
echo "Checking Ollama API..."

if curl -s http://127.0.0.1:11434/api/tags >/dev/null; then
    echo "✓ Ollama running"
else
    echo "✗ Ollama unavailable"
fi

echo ""
echo "Checking application imports..."

python - <<'PY'
from backend.app.main import app
from backend.app.services.llm.router import FXLLMRouter

print("✓ FastAPI application import")
print("✓ FX LLM router import")
PY

echo ""
echo "FX VERIFY COMPLETE"
echo ""

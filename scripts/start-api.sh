#!/bin/bash

set -e

ROOT="/Users/macmac/Documents/Codex/FX"

cd "$ROOT"

source .venv-core/bin/activate

exec uvicorn backend.app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload

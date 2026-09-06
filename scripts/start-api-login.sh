#!/bin/zsh
set -e
cd /Users/macmac/Documents/Codex/FX
export PYTHONPATH=/Users/macmac/Documents/Codex/FX
export FX_AUTO_LEARN_ON_STARTUP=true
export FX_AUTO_START_BOTS=true
export FX_REQUIRE_TOTP_FOR_AUTOMATION=true
export FX_GLOBAL_TRAINING_LIMIT=256
export FX_TRAINING_THREADS=2

exec /Users/macmac/Documents/Codex/FX/.venv-core/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

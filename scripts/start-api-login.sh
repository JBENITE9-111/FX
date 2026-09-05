#!/bin/zsh
set -e
cd /Users/macmac/Documents/Codex/FX
export PYTHONPATH=/Users/macmac/Documents/Codex/FX
export FX_AUTO_LEARN_ON_STARTUP=true
export FX_TRAINING_THREADS=2
exec /Users/macmac/Documents/Codex/FX/.venv-core/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

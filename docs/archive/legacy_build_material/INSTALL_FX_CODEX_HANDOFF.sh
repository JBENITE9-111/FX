#!/bin/bash
set -euo pipefail

ROOT="/Users/macmac/Documents/Codex/FX"

if [ ! -d "$ROOT" ]; then
    echo "ERROR: FX root not found: $ROOT"
    exit 1
fi

cd "$ROOT"

STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ROOT/backups"

for FILE in README.md AGENTS.md FX_COMPLETE_CONVERSATION_CONTEXT.md; do
    if [ -f "$ROOT/$FILE" ]; then
        cp "$ROOT/$FILE" "$ROOT/backups/${FILE}.${STAMP}.bak"
    fi
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cp "$SCRIPT_DIR/README.md" "$ROOT/README.md"
cp "$SCRIPT_DIR/AGENTS.md" "$ROOT/AGENTS.md"
cp "$SCRIPT_DIR/FX_COMPLETE_CONVERSATION_CONTEXT.md" "$ROOT/FX_COMPLETE_CONVERSATION_CONTEXT.md"

echo ""
echo "============================================================"
echo " FX CODEX HANDOFF READY"
echo "============================================================"
echo ""
echo "Created/updated:"
echo "  $ROOT/README.md"
echo "  $ROOT/AGENTS.md"
echo "  $ROOT/FX_COMPLETE_CONVERSATION_CONTEXT.md"
echo ""
echo "Backups:"
echo "  $ROOT/backups/"
echo ""
echo "Open Codex:"
echo ""
echo "  cd \"$ROOT\""
echo "  codex"
echo ""
echo "First Codex instruction:"
echo ""
echo "  Read README.md, AGENTS.md and FX_COMPLETE_CONVERSATION_CONTEXT.md completely before changing anything."
echo ""

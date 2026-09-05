
# External Quant Framework Policy

External frameworks and strategies are not trusted merely because they are:

- popular
- open source
- profitable in published backtests
- AI generated
- widely starred
- used by other traders

All external trading logic enters FX as:

EXTERNAL_UNTRUSTED

Large frameworks should be isolated from `.venv-core`.

Approved architectural roles:

OpenBB
→ secondary research/data service

Backtrader
→ independent validator

Freqtrade Strategies
→ strategy genome source

MetaTrader strategies
→ forex/CFD genome source

FinRL-X
→ reinforcement-learning laboratory

Obsidian AI
→ agent orchestration architecture reference

Hummingbot
→ future isolated crypto execution service

No external framework receives live broker credentials through the FX LLM or general backend.

Any future live execution still requires:

deterministic risk approval
+
explicit human approval
+
isolated execution service.

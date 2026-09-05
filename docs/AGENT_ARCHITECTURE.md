# FX Agent Architecture

FX uses an agent as a durable task runner, not as a synonym for chatbot.

An FX agent:
1. has a narrowly defined goal,
2. has an explicit tool allowlist,
3. runs start-to-finish,
4. emits observable status updates,
5. checkpoints progress,
6. can be interrupted,
7. records outputs and failures,
8. cannot bypass deterministic risk.

Ideas adopted conceptually from xAI Grok Build:
- headless task execution,
- long-running tasks,
- checkpoints,
- tools,
- MCP-compatible boundaries,
- skills/plugins/hooks as modular capability layers,
- sandbox/permission concepts,
- observable execution state.

Ideas adopted conceptually from Grok-1:
- sparse expert routing.
- FX should not run every specialist on every task.
- a small number of relevant experts should be selected for each stage.

FX does NOT install Grok-1.
Its 314B-parameter model is inappropriate for this Intel Mac.

Default sparse routing:
- select the top 2 relevant specialist agents for an analytical stage,
- always keep deterministic Risk as a separate sovereign veto,
- preserve model disagreement as evidence.

Primary scheduled agents:
- Newspaper Agent: refresh global finance/economics/geopolitics every 30 minutes.
- Paper Fleet Agent: run every strategy worker every 5 minutes.
- Training Agent: queue challenger retraining on the existing FX validation pipeline.

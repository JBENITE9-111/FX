# FX QA Fix Log

## 2026-09-05

- Resolved market names mentioned in chat independently of the currently selected chart.
- Added deterministic chat explanations for bots, data sources, paper trading, and the locked live gate.
- Added chat network and API failure recovery so messages do not remain stuck in Thinking.
- Split training runtime health from trading qualification: successful weak models show `WORKING · NOT QUALIFIED`.
- Replaced the Journal's indefinite loading empty state with an explicit legacy-quarantine explanation.
- Added a searchable global instrument list to Local Paper Trading.
- Added bot research suggestions to Local Paper Trading using actual scanner results and explicit qualification limits.
- Added bot source, runtime location, activity, learning authority, and order authority to the Trading Bots view.
- Preserved live trading lock and deterministic risk controls.

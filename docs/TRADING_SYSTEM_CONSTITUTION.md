# FX Trading System Constitution

1. Capital survival outranks profit.
2. NO_TRADE is always valid.
3. No AI, LLM, strategy, agent, UI process, generated code, or research worker may override deterministic risk.
4. Backtest performance alone never authorizes deployment.
5. Holdout data cannot be reused after it influences strategy changes.
6. Broker/exchange state is authoritative for positions, orders, fills, cash, margin, and PnL.
7. Unknown or inconsistent broker state freezes new trading.
8. Strategies cannot self-modify and self-deploy.
9. Every production decision must be reproducible.
10. Every order must reference strategy, model, feature, risk-policy, dataset, code, configuration, and provenance versions.
11. Every strategy requires explicit invalidation.
12. Every live trade must have bounded risk.
13. Every deployed strategy must show positive out-of-sample expectancy after realistic costs.
14. Correlated positions count as aggregated risk.
15. System health can veto a trade.
16. Missing, stale, conflicting, or corrupted data means NO_TRADE.
17. Expected transaction costs must be included before approval.
18. Slippage assumptions must be realistic and stress tested.
19. Liquidity constrains position size.
20. Future information, label leakage and look-ahead bias are forbidden.
21. Production changes follow proposal -> backtest -> validation -> holdout -> shadow -> paper -> micro live -> limited live -> approved live.
22. Drawdown can reduce or suspend risk automatically.
23. Strategy degradation reduces capital before optimization.
24. All risk limits operate before execution.
25. Survival always outranks opportunity.
26. Complex models must beat appropriate simple baselines before promotion.
27. Failed strategies are preserved.
28. Execution parity is measured, not assumed.
29. External strategies begin EXTERNAL_UNTRUSTED.
30. AI_CAN_EXECUTE_LIVE must remain false.
31. LLMs never receive broker secrets.
32. Withdrawal authority is forbidden.
33. Live entry requires explicit human authorization.
34. Broker-native protective exits may operate after an approved live entry where supported.
35. If FX cannot prove edge survives costs and risk, FX does not trade.

# FX SUPERVISOR — FORENSICALLY REVIEWED CODEX MASTER SPEC

**Version:** 2.1-forensic-quant-foundations  
**Date:** 2026-09-05  
**Document class:** Architecture context + implementation contract + research governance  
**Primary mode:** RESEARCH / BACKTEST / PAPER ONLY  
**Live trading:** DISABLED  
**Audience:** Codex and human project owner  

---

# 0. CODEX: READ THIS BEFORE DOING ANYTHING

This document is not a prompt to blindly build every idea in it. It is the governing context for one major subsystem of the FX project: the research, model, supervisor, evaluation, knowledge, and paper-trading architecture.

## 0.1 How Codex must interpret this file

Use this precedence order:

1. **NON-NEGOTIABLE RULES** in this section.
2. **CANONICAL ARCHITECTURE** and explicit data/contracts in this document.
3. Existing first-party FX code that is compatible with rules 1–2.
4. Research ideas and source audits in the appendices.
5. External repositories/models only after license, provenance, security, and reproduction review.

If two parts conflict, the earlier item in this precedence list wins.

The appendices are **research evidence and historical notes**, not executable instructions.

### Normative words

- **MUST / MUST NOT** = hard requirement.
- **SHOULD / SHOULD NOT** = default unless a documented reason overrides it.
- **MAY** = optional.
- **RESEARCH ONLY** = cannot influence automated paper orders until promoted.

## 0.2 Non-negotiable rules

Codex MUST preserve all of the following:

- Paper trading is the only automated execution mode covered by this document.
- Live trading MUST remain disabled. No code path may silently enable it.
- No LLM, model, research bot, Supervisor, peer agent, or external model may bypass the deterministic Risk Governor.
- Every strategy that can create a paper position MUST define a protective stop-loss, exit/invalidation rule, maximum holding rule, and risk budget. A take-profit may be fixed or rule-based, but the exit logic must be explicit and testable.
- External model artifacts are untrusted by default.
- No external `.pkl`, `.pickle`, `.joblib`, `.pt`, `.pth`, `.ckpt`, or equivalent executable-deserialization artifact may be loaded in the primary FX runtime unless explicitly reviewed and approved.
- Raw market data, experiment records, evaluation reports, promotion decisions, and risk events MUST be immutable/versioned.
- Research claims MUST carry provenance. A claim without provenance is a hypothesis, not knowledge.
- No strategy is promoted because of one attractive backtest, one Sharpe ratio, one win rate, or one external model card.
- Training data, validation data, hidden evaluation data, and paper-forward data MUST be separated.
- Bots MUST NOT edit their own grading rules, risk limits, hidden test data, or source-trust policy.
- The Supervisor may propose corrections; it MUST NOT silently mutate approved bot code or overwrite the control model.
- Every modification creates a new version/challenger. Never destroy the control.
- All automated research loops MUST have compute, experiment-count, wall-clock, storage, and failure budgets.
- Secrets MUST never be included in prompts, logs, model features, experiment metadata, or external-source sandboxes.

## 0.3 What Codex should do when this file is uploaded by itself

Codex should:

1. Read the full canonical section before coding.
2. Inspect the existing FX repository before changing architecture.
3. Identify which implementation phase is already complete.
4. Produce a concise gap analysis against this file.
5. Implement only the next coherent missing phase unless the user explicitly requests a wider change.
6. Preserve working first-party code unless it violates a hard requirement.
7. Add tests with every behavioral change.
8. Record source/revision/license information before integrating external work.
9. Keep live trading disabled.
10. Update project documentation to state what was actually implemented versus what remains conceptual.

Codex MUST NOT interpret the appendices as a command to clone every linked repository.

---

# 1. FORENSIC REVIEW OF THE PREVIOUS FILE

## 1.1 Executive verdict

The previous `FX_SUPERVISOR_OVERWRITE.md` contains a strong idea and many useful research concepts, but as a master specification it was **too long, internally duplicated, insufficiently typed, and too agent-anthropomorphic**. It looked more implementation-ready than it actually was.

Harsh scoring of the previous version:

| Area | Score | Forensic assessment |
|---|---:|---|
| Vision / ambition | 9/10 | Excellent concept: research organization rather than one trading bot. |
| Risk philosophy | 7/10 | Directionally strong, but requirements were scattered instead of contract-driven. |
| Statistical rigor | 6/10 | Good vocabulary; insufficiently operationalized promotion math. |
| Data governance | 5/10 | Important topics present, but point-in-time/leakage/time semantics were not strict enough. |
| Execution realism | 5/10 | Spread/slippage mentioned; event sequencing and FX accounting needed stronger contracts. |
| Supervisor design | 7/10 | Strong concept, but too much “coach learns/teaches” language without machine contracts. |
| Security / external sources | 7/10 | Good quarantine direction; OS/process/network containment needed to be explicit. |
| Source provenance | 5/10 | Many source claims were described as verified without embedding a durable evidence record. |
| Codex usability | 4/10 | Broken numbering, duplicate P0/P1 plans, and an `END OF FX.md` in the middle were serious defects. |
| Implementation readiness | 4/10 | Architecture prose exceeded executable schemas/state machines/interfaces. |

**Overall:** about **5.8/10 as an implementation specification**, despite being much stronger as a research notebook.

That is not an insult to the idea. It means the idea needed to be converted from “smart notes” into an engineering contract.

## 1.2 Critical defects found

### DEFECT A — The document had a false end in the middle

The previous file contained `# END OF FX.md` around line 2,221 and then continued for roughly another 4,000 lines.

That is unacceptable in a Codex master context file because it creates ambiguity about whether later sections supersede or merely append earlier instructions.

**Fix in this version:** one canonical front section, one research appendix, one precedence rule.

### DEFECT B — Part numbering restarted and collided

The previous file had an initial Part I–XXXIV, then appended another Part X–XIV, then another Part XV, then Part XVI. Priority plans such as `P0`, `P1`, etc. also restarted.

**Risk:** Codex can choose the wrong “P0.”

**Fix:** one canonical implementation roadmap in Section 15. Historical plans are appendix-only.

### DEFECT C — Normative requirements and research notes were mixed

A social-media-derived idea, a Hugging Face model claim, a deterministic risk rule, and a Codex implementation command could appear at similar heading levels.

**Risk:** unverified research can become implementation policy.

**Fix:** explicit separation between canonical requirements and research appendices.

### DEFECT D — “Bot” was undefined

The old file used “bot” to mean strategy, trained model, agent, paper executor, research process, and sometimes an organizational role.

**Risk:** architecture and permissions become incoherent.

**Fix:** Section 3 defines every entity precisely.

### DEFECT E — The Supervisor was a systemic single point of intellectual failure

The previous design correctly worried about contagion but still gave one Coach broad authority to diagnose, transfer lessons, select experiments, and eventually learn how to coach.

**Risk:** one biased Supervisor can homogenize the entire research population.

**Fix:** Supervisor, Examiner, Risk Governor, Source Gate, and Promotion Service are separate authorities. The Supervisor never owns hidden evaluation or risk rules.

### DEFECT F — The scalar `BotScore` was unsafe

A weighted score such as:

```text
0.20 Edge + 0.20 Robustness + ...
```

can allow an extreme strength to compensate for a fatal weakness.

Example: very high returns could mathematically hide catastrophic drawdown or poor operational reliability.

**Fix:** hard gates first; ranking only after all gates pass. Use Pareto/frontier logic or constrained ranking, not one magic score.

### DEFECT G — Multiple-testing protection was mentioned but not enforced

The old file correctly named false discovery risk, Deflated Sharpe, etc., but did not define experiment-family accounting as a mandatory part of promotion.

**Fix:** every experiment belongs to a search family; the promotion report must include trial count, selection procedure, and multiple-testing adjustment.

### DEFECT H — Hidden-test contamination remained possible

A Coach that repeatedly sees final test results can indirectly overfit the organization to the test set.

**Fix:** the Examiner owns sealed holdouts. Supervisor receives controlled summaries, not reusable hidden labels/predictions.

### DEFECT I — “Self-improving” was too close to online self-modification

The desired behavior is useful, but uncontrolled online retraining from recent P&L can amplify noise and regime-chasing.

**Fix:** no production/paper bot mutates itself in place. Learning happens as versioned offline experiments. Promotion occurs only after evaluation.

### DEFECT J — Data timing semantics were incomplete

The previous file discussed causal computation but did not make these universally mandatory:

- event time vs ingest time;
- timezone normalization;
- DST/session handling;
- point-in-time macro releases;
- revision/vintage tracking;
- bid/ask availability at decision time;
- timestamp precision;
- stale-data semantics.

**Fix:** Section 6.

### DEFECT K — Paper fill simulation was underspecified

A credible backtest/paper simulator needs exact answers for:

- whether stop or target wins if both touch in one bar;
- bid vs ask triggering;
- latency ordering;
- partial fills;
- rejected/cancelled orders;
- gap-through stops;
- FX pip/lot/margin accounting;
- financing/rollover.

**Fix:** Section 10.

### DEFECT L — The file overemphasized model variety before baseline quality

RL, LLM councils, SMC, “quantum-inspired” transforms, deep sequence models, and huge ensembles are seductive distractions before deterministic baselines and execution accounting are rock-solid.

**Fix:** canonical roadmap delays RL and meta-learning until after data, backtest, risk, and simple models pass.

### DEFECT M — Source “verification” was not durable enough

A paragraph saying a model card was verified is not sufficient six months later.

**Fix:** every source record must include retrieval date, revision/commit, license, content hash where possible, trust class, claims extracted, and local reproduction state.

### DEFECT N — Security needed system-level containment

Avoiding pickle is not enough.

**Fix:** external repositories run only in quarantine with no broker secrets, restricted filesystem access, explicit network policy, pinned dependencies, checksums, static inspection, and no auto-start hooks.

### DEFECT O — No formal concurrency/idempotency model

Multiple bots and experiments can race to write registries, consume the same risk budget, or duplicate jobs.

**Fix:** Section 13 requires immutable IDs, idempotent task execution, transactional state changes, locks/queues where needed, and exactly-once promotion decisions.

### DEFECT P — The knowledge trust formula was too simplistic

Multiplying arbitrary quality scores can create fake precision.

**Fix:** source trust is categorical plus evidence-based. Do not convert subjective source scores into pseudo-probabilities.

---

# 2. PROJECT OBJECTIVE — REFINED

The goal is not to build a “money machine.” The engineering goal is to build a **paper-only systematic trading research organization** that can generate, test, reject, improve, specialize, and compare strategies more efficiently than a single monolithic bot.

The compounding mechanism is not guaranteed profit. It is **compounding research quality**:

```text
better provenance
+ better experiments
+ better rejection of false discoveries
+ better risk control
+ better failure memory
+ better execution realism
+ better specialization
= better odds of discovering robust paper-trading edges
```

The system should aggressively learn, but conservatively promote.

---

# 3. CANONICAL ENTITY DEFINITIONS

Codex MUST use these terms consistently.

## 3.1 `StrategySpec`

A deterministic, versioned definition of a trading hypothesis and its rules.

Contains at minimum:

```yaml
strategy_id:
version:
asset_universe:
timeframe:
signal_definition:
feature_set_version:
entry_rule:
protective_stop_rule:
exit_rule:
take_profit_rule:
max_holding_rule:
position_sizing_rule:
regime_constraints:
cost_model_version:
```

A `StrategySpec` is not an LLM agent.

## 3.2 `ModelArtifact`

A trained statistical/ML model with immutable provenance:

```yaml
model_id:
model_family:
code_commit:
data_snapshot:
feature_version:
label_version:
train_period:
validation_protocol:
hyperparameters:
seed:
artifact_hash:
serialization_format:
security_status:
```

## 3.3 `ResearchBot`

A bounded research worker that may:

- run approved experiments;
- train candidate models;
- produce evidence reports;
- propose hypotheses.

It may NOT place paper orders directly.

## 3.4 `PaperBot`

A promoted, immutable strategy/model package permitted to submit `TradeIntent` objects to the Risk Governor.

It cannot send orders directly to the broker simulator.

## 3.5 `SupervisorAgent`

An orchestration/advisory service that analyzes experiment records, detects recurring failure classes, proposes next experiments, and builds candidate lesson packages.

It does not own risk rules, hidden holdouts, or promotion authority.

## 3.6 `ExaminerService`

A deterministic evaluation service with protected holdouts and robustness tests. It produces signed/versioned evaluation reports.

## 3.7 `PromotionService`

Applies hard promotion gates to Examiner reports. It cannot modify model outputs or test results.

## 3.8 `RiskGovernor`

A deterministic service on the execution path that can reject, resize, pause, or terminate paper positions according to policy.

## 3.9 `KnowledgeItem`

A versioned proposition with provenance and evidence state. It is not automatically true because an agent wrote it.

## 3.10 `LessonPackage`

A proposed transferable finding with origin, reproduction status, applicable bot families, failure conditions, and expiration/retest criteria.

---

# 4. SYSTEM ARCHITECTURE — SEPARATE THE PLANES

Do not build one agent graph that does everything.

## 4.1 Governance plane

```text
Human Policy
    |
Policy Store
    |
+-------------------------+
| hard limits             |
| permissions             |
| approved source classes |
| paper-only mode         |
+-------------------------+
```

The governance plane defines what the system is allowed to do.

## 4.2 Data plane

```text
External / Broker / Dataset Sources
        |
Source Adapter
        |
Raw Immutable Store
        |
Data Quality Gate
        |
Point-in-Time Normalizer
        |
Feature Pipeline
        |
Versioned Feature Store
```

## 4.3 Research plane

```text
Experiment Planner
       |
Bot Factory -> ResearchBots
       |           |
       +----> Experiment Registry
                     |
                ExaminerService
                     |
               PromotionService
```

## 4.4 Knowledge plane

```text
External Source
   |
Knowledge Ingestion Gate
   |
Quarantine / Hypothesis / Validated
   |
Knowledge Registry
   |
SupervisorAgent <-> Lesson Validator
```

## 4.5 Execution plane

```text
Promoted PaperBot
      |
TradeIntent
      |
RiskGovernor
      |
ApprovedPaperOrder
      |
Paper Execution Simulator
      |
Fill / Position / PnL / Attribution
```

No LLM is required on the execution critical path.

## 4.6 Observability plane

Every plane emits structured events to:

```text
logs
metrics
traces
audit events
risk events
experiment events
```

Every event should have:

```text
event_id
correlation_id
actor_id
entity_version
timestamp_utc
source_timestamp if applicable
```

---

# 5. BOT LIFECYCLE — A STATE MACHINE, NOT A STORY

Every candidate must occupy exactly one state:

```text
IDEA
  -> TRAINING
  -> INTERNAL_VALIDATION
  -> EXAMINATION
  -> CHALLENGER
  -> SHADOW
  -> PAPER
  -> SUSPENDED
  -> RETIRED
```

Permitted reverse transitions:

```text
PAPER -> SUSPENDED
PAPER -> RETIRED
CHALLENGER -> RETIRED
SHADOW -> CHALLENGER
SUSPENDED -> EXAMINATION
```

No direct transition:

```text
IDEA -> PAPER
TRAINING -> PAPER
EXTERNAL_MODEL -> PAPER
```

Each transition MUST create a `PromotionDecision` or `LifecycleDecision` record with reason, evidence IDs, policy version, and timestamp.

---

# 6. DATA GOVERNANCE — HARD REQUIREMENTS

## 6.1 Time semantics

Internally normalize timestamps to UTC while preserving original timestamps and source timezone metadata.

For every event-based dataset retain when possible:

```text
event_time
publication_time
ingest_time
source_time_zone
received_time
```

Never use data before it would have been observable by the strategy.

## 6.2 Point-in-time correctness

Macro/fundamental/news data MUST distinguish first release from later revisions.

A backtest must not use a revised GDP/CPI value as if it was known on the original release date.

## 6.3 Bid/ask correctness

For FX research, mid-price-only results are research diagnostics, not executable PnL evidence.

Paper/execution-qualified tests should use bid/ask or a documented spread model.

## 6.4 Session and calendar correctness

Track:

- trading sessions;
- weekends;
- holidays;
- DST changes;
- rollover windows;
- broker maintenance windows;
- market-specific closures.

## 6.5 Raw data immutability

Never overwrite raw downloaded or broker-sourced data.

Each dataset snapshot gets:

```yaml
snapshot_id:
source_id:
retrieved_at:
revision_or_commit:
sha256_or_manifest_hash:
row_count:
min_event_time:
max_event_time:
schema_version:
license_status:
quality_report_id:
```

## 6.6 Leakage tests

Every feature pipeline MUST have automated checks for:

- future joins;
- forward-filled future information;
- label leakage;
- centered rolling windows;
- normalization fitted on future data;
- revised macro leakage;
- overlapping-label contamination;
- accidental use of target-derived features.

---

# 7. EXPERIMENT CONTRACT

Every experiment MUST be reproducible from a single immutable record.

```yaml
experiment_id:
parent_experiment_ids: []
research_family_id:
hypothesis:
strategy_spec_version:
model_family:
data_snapshot_ids: []
feature_version:
label_version:
training_window:
validation_window:
test_policy:
cost_model_version:
execution_model_version:
seed:
hyperparameters:
code_commit:
environment_lock_hash:
started_at:
completed_at:
status:
```

## 7.1 Research family

Every hyperparameter sweep, bot generation, or related hypothesis group MUST share a `research_family_id`.

This allows the Examiner to know whether a “winner” came from 3 attempts or 30,000 attempts.

## 7.2 Never overwrite experiments

A correction creates a child experiment.

```text
exp_1001 = control
exp_1002 = child with volatility filter
exp_1003 = child with new stop policy
```

No mutable “latest experiment” record may replace historical evidence.

---

# 8. STATISTICAL EVALUATION PROTOCOL

This section is mandatory before any automated promotion to paper.

## 8.1 Baseline before complexity

Every sophisticated model must compare against simple baselines appropriate to the task, such as:

```text
no-trade
buy/hold where relevant
simple trend
simple mean reversion
logistic regression
simple volatility-scaled rule
```

A Transformer that does not beat a robust simple baseline after costs is rejected regardless of novelty.

## 8.2 Chronological validation

Use rolling/expanding walk-forward validation.

Where labels overlap, use purging and embargo.

Use nested selection when hyperparameters/features are tuned.

## 8.3 Hidden examination

The Supervisor does not own the final holdout.

The Examiner may expose only enough aggregate output for diagnosis. It should not disclose reusable hidden labels or detailed signal-by-signal answers that enable organizational test overfitting.

## 8.4 Multiple testing

The evaluation report MUST include:

```text
research_family_id
number_of_candidates_tested
number_of_hyperparameter_trials
number_of_feature_sets
number_of_assets
number_of_horizons
selection_rule
```

Where statistically appropriate, report:

- Probabilistic Sharpe Ratio;
- Deflated Sharpe Ratio;
- bootstrap confidence intervals;
- false-discovery controls;
- backtest-overfitting diagnostics;
- Reality Check / SPA-like methods when suitable.

Do not pretend any one statistic solves data snooping.

## 8.5 Cost stress

At minimum evaluate the qualified strategy under:

```text
base spread/slippage
1.5x cost stress
2.0x cost stress
```

Strategies that collapse under modest cost stress are fragile.

## 8.6 Regime stress

Evaluate separately across meaningful regimes:

```text
trend/range
high/low volatility
risk-on/risk-off
session
liquidity state
macro-event vs non-event
```

## 8.7 Parameter perturbation

A strategy that works only at one exact parameter value is suspicious.

Test local perturbations around key settings.

## 8.8 Sample size and confidence

There is no universal magic minimum number of trades. The required evidence depends on horizon, dependence, effect size, turnover, and variance.

Therefore Codex MUST NOT hard-code a simplistic “100 trades = valid” rule.

The Examiner should report uncertainty and effective sample size where feasible.

---

# 9. PROMOTION — HARD GATES BEFORE RANKING

Do NOT use one scalar BotScore as the primary safety decision.

## 9.1 Mandatory gates

A candidate cannot advance to automated paper unless all required gates pass:

```text
G1  data provenance valid
G2  license/source policy valid
G3  leakage tests pass
G4  accounting invariants pass
G5  chronological OOS evaluation complete
G6  realistic costs modeled
G7  cost-stress survival acceptable
G8  drawdown/tail-risk limits pass
G9  operational failure tests pass
G10 model/calibration requirements pass where applicable
G11 multiple-testing report complete
G12 hidden examination pass
G13 protective stop + exit policy defined
G14 deterministic RiskGovernor compatibility pass
G15 no prohibited artifact/runtime dependency
```

Thresholds live in versioned policy configuration, not prose.

## 9.2 Ranking after gates

Only candidates that pass hard gates may be compared.

Prefer constrained multi-objective comparison or Pareto analysis across:

```text
net edge
robustness
risk
cost sensitivity
calibration
diversity
operational reliability
```

Do not allow high return to compensate for a failed risk gate.

## 9.3 Champion/challenger

A challenger replaces a champion only if it provides:

- statistically/economically meaningful improvement; or
- material diversification with acceptable standalone quality.

The previous champion remains archived and reproducible.

---

# 10. PAPER EXECUTION CONTRACT

## 10.1 Order lifecycle

```text
SignalEvent
 -> TradeIntent
 -> RiskDecision
 -> ApprovedPaperOrder
 -> OrderAccepted/Rejected
 -> SimulatedFill(s)
 -> PositionEvent
 -> Stop/Exit/TargetEvent
 -> CloseEvent
 -> AttributionRecord
```

## 10.2 TradeIntent schema

```yaml
intent_id:
bot_id:
strategy_version:
symbol:
side:
requested_notional_or_units:
entry_type:
entry_price_or_rule:
protective_stop:
take_profit_or_exit_rule:
max_holding_time:
signal_timestamp:
signal_expiry:
model_confidence_if_applicable:
evidence_snapshot_id:
```

## 10.3 FX accounting requirements

Explicitly model:

- base/quote currency;
- pip size and pip value;
- lot/unit size;
- account currency conversion;
- leverage/margin;
- spread;
- commission if applicable;
- swap/financing/rollover where relevant;
- realized and unrealized PnL.

## 10.4 Same-bar ambiguity

For bar backtests, if stop and target can both be touched inside one bar and event ordering is unknown, the simulator MUST use an explicitly documented conservative policy or higher-resolution data.

Never silently assume the favorable outcome.

## 10.5 Gap-through stop

A protective stop is not a guaranteed fill price. Simulate gap-through behavior where the data resolution permits it.

## 10.6 Partial fills / latency

If a strategy depends on intraday/tick execution, the simulator SHOULD support:

- latency;
- queue/fill assumptions where relevant;
- partial fills;
- cancellation;
- rejected orders;
- stale intent expiry.

## 10.7 Accounting invariants

Automated tests MUST verify:

```text
cash conservation within modeled costs
position quantities reconcile
realized + unrealized PnL reconcile
duplicate fill events do not double count
cancelled orders do not fill
risk-rejected orders never reach execution
```

---

# 11. DETERMINISTIC RISK GOVERNOR

The Risk Governor is not an LLM.

It receives `TradeIntent` and returns a structured decision:

```yaml
risk_decision_id:
intent_id:
decision: APPROVE | RESIZE | REJECT | HALT
approved_size:
reason_codes: []
policy_version:
portfolio_snapshot_id:
timestamp:
```

## 11.1 Mandatory controls

Per trade/strategy:

```text
protective stop required
max risk per trade
max notional/units
max leverage
max holding time
max concurrent positions
signal expiry
```

Portfolio/system:

```text
max daily loss
max weekly loss/drawdown
max portfolio drawdown
max gross/net exposure
max currency-factor exposure
max correlated exposure
max strategy-family exposure
stale-data halt
feed disconnect halt
model anomaly halt
volatility/liquidity halt
manual kill switch
```

## 11.2 Risk policy independence

Bots and Supervisor may inspect policy but may not edit it.

Any risk-policy change is a separately versioned configuration change with audit record.

---

# 12. SUPERVISOR / COACH — IMPROVED DESIGN

The original Coach concept is retained but converted into bounded responsibilities.

## 12.1 Supervisor inputs

The Supervisor reads:

- experiment summaries;
- failure taxonomy labels;
- model health/drift summaries;
- source/knowledge status;
- lineage graph;
- strategy cemetery;
- promotion/rejection reasons;
- paper attribution reports.

It does not receive broker secrets or hidden-test labels.

## 12.2 Supervisor outputs

The Supervisor may emit only structured proposals:

```yaml
proposal_id:
proposal_type: RETRAIN | ABLATION | RISK_RESEARCH | DATA_AUDIT | FEATURE_TEST | RETEST_LESSON | RETIRE_REVIEW
origin_entity_ids: []
hypothesis:
reason_codes: []
suggested_experiments: []
priority:
confidence_label: LOW | MEDIUM | HIGH
```

These are recommendations, not direct mutations.

## 12.3 Failure taxonomy

Use machine-readable categories:

```text
DATA_QUALITY
TIME_ALIGNMENT
LEAKAGE
FEATURE_INSTABILITY
MODEL_OVERFIT
CALIBRATION_FAILURE
REGIME_MISMATCH
EDGE_DECAY
RISK_OVERSIZING
EXIT_LOGIC
COST_SENSITIVITY
FILL_ASSUMPTION
OPERATIONAL_FAILURE
SOURCE_PROVENANCE
SECURITY_POLICY
LICENSE_POLICY
RULE_VIOLATION
UNKNOWN
```

A losing trade alone is not a failure category.

## 12.4 Process quality vs outcome quality

Classify incidents on two dimensions:

```text
GOOD PROCESS + GOOD OUTCOME
GOOD PROCESS + BAD OUTCOME
BAD PROCESS + GOOD OUTCOME
BAD PROCESS + BAD OUTCOME
```

The dangerous class is `BAD PROCESS + GOOD OUTCOME`, because profit can reinforce invalid behavior.

## 12.5 No direct self-modification

The Supervisor MUST NOT patch an active PaperBot in place.

Correct flow:

```text
failure observed
-> hypothesis
-> challenger experiment
-> Examiner
-> PromotionService
-> new version
```

## 12.6 Supervisor versioning

Supervisor policy/model changes are themselves experiments.

A new Coach version runs in shadow against historical and recent experiment decisions before activation.

---

# 13. BOT FACTORY, LINEAGE, AND PEER LEARNING

## 13.1 Controlled replication

The factory creates candidate configurations, not uncontrolled copies.

Allowed variation dimensions:

```text
feature subsets
model families
lookbacks
risk parameters within approved research bounds
exit rules
regime filters
assets
timeframes
cost assumptions
```

Each variant receives a new ID and parent lineage.

## 13.2 Population budget

Configuration MUST define:

```yaml
max_active_experiments:
max_new_candidates_per_day:
max_trials_per_research_family:
max_cpu_hours_per_day:
max_gpu_hours_per_day:
max_storage_growth_per_day:
max_consecutive_failures_before_pause:
```

The objective is not to maximize bot count.

## 13.3 Peer learning is evidence transfer

Bots do not copy each other’s weights or strategy code by default.

A transferable lesson must include:

```yaml
lesson_id:
origin_experiments: []
claim:
evidence_report_ids: []
reproduction_count:
applicable_context:
known_failure_context:
expires_or_retest_after:
status: HYPOTHESIS | REPRODUCED | VALIDATED | STALE | RETIRED
```

Recipients must independently retest the lesson.

## 13.4 Anti-contagion

A lesson cannot become organization-wide knowledge from one bot.

Require independent reproduction across appropriate datasets/regimes before broad propagation.

## 13.5 Preserve diversity

Measure at least:

```text
prediction correlation
return correlation
error correlation
feature-family overlap
data-source overlap
strategy-family overlap
```

Consensus among highly correlated bots is discounted.

---

# 14. KNOWLEDGE INGESTION AND SOURCE GOVERNANCE

## 14.1 Source states

Every source is assigned one of:

```text
QUARANTINED
HYPOTHESIS_ONLY
RESEARCH_REFERENCE
REPRODUCED_LOCALLY
APPROVED_COMPONENT
RETIRED
```

## 14.2 Required source record

```yaml
source_id:
url:
publisher:
source_type:
retrieved_at:
revision_or_commit:
license:
license_verified:
content_hash_if_possible:
security_status:
claims_extracted: []
local_reproduction_status:
approved_uses: []
prohibited_uses: []
notes:
```

## 14.3 Evidence classes

Do not use fake numeric trust probabilities.

Use categories:

```text
E0 — marketing / unverifiable claim
E1 — anecdotal/community idea
E2 — documented implementation without independent reproduction
E3 — reproducible research / credible primary source
E4 — independently reproduced inside FX
```

A source can be useful at E1/E2 for hypothesis generation without being trusted as evidence of edge.

## 14.4 External artifact quarantine

External code/model research occurs in an isolated environment with:

- no broker credentials;
- no user secrets;
- no access to primary FX writable directories except explicit mounted research input/output;
- restricted network access or allowlist when feasible;
- pinned dependencies;
- recorded hashes;
- static inspection;
- no shell-profile modification;
- no scheduled jobs;
- no auto-start daemons;
- no order-routing capability.

## 14.5 Serialized artifact policy

Default:

```text
ALLOW_DOWNLOAD_FOR_INSPECTION = case-by-case
ALLOW_DESERIALIZE = false
ALLOW_EXECUTE = false
ALLOW_PAPER_SIGNAL = false
```

Prefer reconstruction/retraining from documented architecture and data.

Formats such as `safetensors` reduce some deserialization risk but do not establish model trust, license safety, provenance, or trading validity.

---

# 15. CANONICAL IMPLEMENTATION ROADMAP

This is the only P-level roadmap Codex should treat as canonical.

## P0 — Repository and governance foundation

Implement/verify:

```text
paper-only configuration
live-disabled assertions
policy store
source registry
experiment registry
bot/model registry
immutable IDs
structured logging
secret handling
external quarantine
```

Exit criteria: tests prove no research component can route a live order.

## P1 — Data foundation

Implement:

```text
historical adapters
raw immutable store
UTC normalization
bid/ask support where available
quality reports
snapshot manifests
point-in-time joins
feature store basics
```

Exit criteria: deterministic data snapshot can reproduce a feature set.

## P2 — Backtest/accounting foundation

Implement only simple strategies first:

```text
trend baseline
mean-reversion baseline
no-trade baseline
```

Add:

```text
spread/slippage
FX accounting
same-bar policy
stops/exits
latency hooks
walk-forward evaluation
```

Exit criteria: accounting invariants and leakage tests pass.

## P3 — Risk Governor

Implement deterministic pre-trade and portfolio controls.

Exit criteria: adversarial tests prove rejected intents cannot reach paper execution.

## P4 — Examiner + promotion gates

Implement:

```text
hidden evaluation
cost stress
regime stress
parameter perturbation
multiple-testing metadata
promotion decisions
```

Exit criteria: no strategy can reach PAPER without a complete signed evaluation/promotion record.

## P5 — Classical challenger lab

Test:

```text
logistic/LASSO
Random Forest
XGBoost/LightGBM
calibration
simple ensembles
```

Exit criteria: models must beat appropriate baselines after costs or provide documented diversification.

## P6 — Supervisor MVP

Supervisor may:

```text
classify failures
propose experiments
build lesson candidates
identify repeated failed research
```

It may not mutate active bots.

## P7 — Bot Factory + strategy cemetery + peer learning

Add controlled variants, lineage, failure memory, and validated lesson transfer.

## P8 — Alpha Studio / cross-asset / microstructure expansion

Only after the core lab is trustworthy.

## P9 — Meta-learning for experiment selection

Use historical experiment metadata to recommend research priorities.

Must remain advisory at first.

## P10 — RL sandbox

RL is intentionally late.

It may be studied only after the environment, costs, risk, accounting, and baseline evaluation are reliable.

## P11 — Controlled autonomous research cycles

Allow bounded scheduling of research experiments under hard budgets and promotion controls.

Still:

```text
LIVE TRADING = DISABLED
```

---

# 16. CODEX IMPLEMENTATION CONTRACTS

## 16.1 Repository behavior

Codex SHOULD create first-party modules around contracts, not giant agent files.

Suggested shape:

```text
fx/
  governance/
  data/
  features/
  strategies/
  models/
  experiments/
  evaluation/
  risk/
  execution/
  agents/
    supervisor/
    research/
  knowledge/
  registries/
  observability/
```

Do not force this layout if the existing repository already has a coherent equivalent.

## 16.2 Configuration

Hard limits and promotion thresholds belong in versioned config/schema, not buried in prompts.

## 16.3 Typed schemas

Use explicit schemas/dataclasses/Pydantic models for cross-service records such as:

```text
TradeIntent
RiskDecision
PaperOrder
FillEvent
ExperimentSpec
EvaluationReport
PromotionDecision
KnowledgeItem
LessonPackage
SupervisorProposal
```

## 16.4 Idempotency and concurrency

All scheduled/retryable jobs need stable job IDs and idempotent writes.

Promotion transitions should be transactional.

Duplicate events must not double-apply fills, PnL, lessons, or promotions.

## 16.5 Testing

At minimum maintain:

```text
unit tests
property/invariant tests
leakage tests
accounting tests
risk rejection tests
data schema tests
serialization/security tests
integration tests
reproducibility tests
```

## 16.6 Documentation discipline

Every feature must be labeled:

```text
IMPLEMENTED
PARTIAL
PLANNED
RESEARCH ONLY
REJECTED
```

Do not let documentation describe planned architecture as if it already exists.

---

# 17. SUPERVISOR DASHBOARD — WHAT MATTERS

Do not build a decorative dashboard first.

When implemented, prioritize decision-useful panels:

```text
SYSTEM SAFETY
paper/live mode
RiskGovernor state
halts
feed/data health

RESEARCH
active experiments
research-family trial count
failed experiments
queued proposals

BOT LEAGUE
state
OOS evidence
cost stress
risk
calibration
diversity

KNOWLEDGE
validated lessons
stale lessons
quarantined sources
retest queue

LINEAGE
parent/child graph
version changes
promotion/demotion reasons

PAPER PERFORMANCE
PnL attribution
cost drag
slippage drag
regime attribution
risk events
```

A leaderboard sorted only by PnL is prohibited because it encourages selection bias.

---

# 18. ANTI-PATTERNS CODEX MUST REJECT

Codex should stop and flag these patterns:

```text
“download this model and let it trade”
“highest Sharpe wins”
“85% win rate means good model”
“all agents agree, therefore confidence is high”
“retrain after every losing day”
“copy the winning bot 100 times”
“increase model count to improve accuracy”
“use the test set to teach the Coach”
“LLM decides stop loss”
“mid-price backtest is executable PnL”
“pickle is safe because it came from Hugging Face”
“safetensors means the model is trustworthy”
“paper success automatically unlocks live trading”
“quantum-inspired means superior”
“social post claim becomes a feature without validation”
```

---

# 19. WHAT THE SUPERVISOR SHOULD ACTUALLY LEARN

Long term, the Supervisor may learn from the meta-dataset of experiments, but the target should be **research efficiency**, not direct price prediction.

Useful meta-learning questions:

```text
Which experiment families repeatedly fail after costs?
Which feature families transfer across regimes?
Which models become miscalibrated fastest?
Which source classes generate useful hypotheses?
Which bot families are becoming too correlated?
Which kinds of fixes survive hidden examination?
Which experiments are redundant with completed research?
```

Bad meta-learning target:

```text
“maximize recent paper PnL by changing whatever worked last week”
```

That invites regime chasing.

---

# 20. STRATEGY CEMETERY — REQUIRED FORMAT

Failure is an asset only if it is queryable.

```yaml
strategy_id:
version:
status: RETIRED
hypothesis:
research_family_id:
data_snapshots: []
assets: []
timeframes: []
what_looked_promising:
why_it_failed:
  - COST_SENSITIVITY
  - REGIME_MISMATCH
reproduction_evidence: []
salvageable_components: []
do_not_repeat: []
retired_at:
```

The Supervisor should search the cemetery before proposing a new experiment.

---

# 21. PAPER BOT HEALTH AND DEMOTION

Promotion is not permanent.

Monitor in paper-forward operation:

```text
prediction drift
feature drift
calibration drift
cost drift
fill/slippage drift
regime concentration
drawdown behavior
signal frequency change
correlation to other paper bots
operational errors
```

Demotion states:

```text
PAPER -> SUSPENDED
PAPER -> RETIRED
```

A suspended bot submits no new intents until re-examined.

Do not automatically retrain a deteriorating bot. First determine whether the issue is:

```text
data
execution
regime
model
risk
edge decay
```

---

# 22. HUMAN CONTROL

Even though this project aims for extensive automation, human policy remains outside the learning loop.

The system should make it easy for the owner to see:

```text
what changed
why it changed
which evidence supported it
what was rejected
which source was used
which bot version is active
which risk policy is active
whether live trading is disabled
```

The system must be inspectable before it is autonomous.

---

# 23. QUANTITATIVE FOUNDATIONS + FOUR ADVANCED RESEARCH ENGINES

This section is a **canonical research-capability specification** derived from the supplied image set and independently checked against primary/academic sources.

Codex MUST understand the distinction:

```text
MATHEMATICS / THEORY
        ↓
RESEARCH TOOL
        ↓
HYPOTHESIS
        ↓
VALIDATION
        ↓
PROMOTION GATES
        ↓
PAPER ELIGIBILITY
```

A formula, paper, textbook, course, or elegant model is **not a trading strategy by itself**.

The purpose of this section is to strengthen the Bot Team and Supervisor with better mathematical tools, better diagnostics, and harder falsification tests—not to grant new autonomous trading authority.

## 23.1 Image-derived concepts: source status

The supplied images describe nine main topics:

1. Prediction-market mispricing / arbitrage.
2. Hawkes-process information diffusion.
3. Breeden-Litzenberger risk-neutral densities.
4. Backtest-overfitting detection / Deflated Sharpe Ratio.
5. Linear algebra.
6. Multivariable calculus.
7. Probability and statistics.
8. Convex / numerical optimization.
9. Deep learning.

The first four are specialized quant-finance research engines.
The last five are foundational mathematical capabilities that support nearly every model already contemplated by FX.

Codex MUST NOT treat statements embedded in the images as authoritative merely because they cite academic-looking material. This file separates:

```text
IMAGE CLAIM
VERIFIED RESEARCH CONCEPT
FX IMPLEMENTATION DECISION
```

---

## 23.2 Research Engine A — Prediction-Market Mispricing and Executability

### Status

```text
RESEARCH ONLY
NO AUTOMATED PAPER ORDER AUTHORITY BY DEFAULT
```

Prediction markets are useful for FX in two ways:

1. as a separate experimental asset class / market-microstructure laboratory;
2. as a source of market-implied event probabilities that may later become macro/event features for other assets.

### Core binary-contract identity

For a perfectly complementary binary contract with identical settlement rules:

```text
YES payoff + NO payoff = 1
```

Ignoring costs, if executable ask prices satisfy:

```text
ask_yes + ask_no < 1
```

then the gross locked payoff appears positive:

```text
gross_edge = 1 - ask_yes - ask_no
```

But Codex MUST NOT call this arbitrage until it proves all of the following:

```text
same economic event
same settlement condition
same resolution source
same expiration / cutoff
same cancellation treatment
same void rules
same currency economics
both legs simultaneously executable
sufficient depth exists
fees included
slippage included
latency included
funding / transfer friction included
venue / custody / settlement risk considered
```

Cross-venue contracts that merely have similar English names are NOT automatically equivalent.

### Executable edge

Use a cost-aware quantity:

```text
net_edge(q) = guaranteed_payoff(q)
              - acquisition_cost(q)
              - fees(q)
              - expected_slippage(q)
              - funding_cost(q)
              - execution_risk_buffer(q)
```

where acquisition cost MUST consume the actual order-book curve, not only level-1 quotes.

### Depth-aware sizing

For quantity q:

```text
VWAP_yes(q) = cost_to_buy_yes(q) / q
VWAP_no(q)  = cost_to_buy_no(q) / q

net_edge_per_contract(q)
    = 1 - VWAP_yes(q) - VWAP_no(q) - all_costs_per_contract(q)
```

A positive top-of-book edge can disappear almost instantly with size.

### Empirical reality check

A 2026 study of Polymarket NBA markets reconstructed more than 75 million order-book snapshots across 173 games. It reported only 7 executable single-market arbitrage episodes, with a median duration of about 3.6 seconds. It found more combinatorial episodes, but 76.9% were liquidity-constrained, with an average executable size around 14.8 shares in those constrained cases.

Therefore the correct lesson is NOT:

```text
prediction markets contain easy arbitrage
```

It is:

```text
apparent mispricing must survive synchronization,
fees, depth, latency, and simultaneous-fill constraints.
```

Recent 2026 cross-platform research is also contested: one paper reports persistent Kalshi/Polymarket arbitrage in selected events, while a later preregistered falsification study reports that proper timestamp alignment and fees eliminate the apparent persistent edge in its sample. Codex MUST treat cross-venue arbitrage as an empirical question, never as an assumed fact.

### Kelly sizing — research use only

For a binary wager with decimal net odds b, win probability p, and q = 1-p:

```text
f* = (b*p - q) / b
```

This is the classical Kelly fraction under strong assumptions.

FX MUST NOT apply full Kelly from uncertain model probabilities.

If Kelly research is performed:

```text
fractional_kelly = haircut * max(0, estimated_kelly)
```

with:

```text
haircut << 1
hard portfolio risk caps
probability uncertainty penalty
liquidity cap
correlation cap
venue cap
loss / drawdown cap
```

The deterministic Risk Governor still wins.

### Required data contract

```yaml
PredictionMarketQuote:
  venue:
  canonical_event_id:
  venue_market_id:
  outcome_id:
  side:
  event_time:
  received_time:
  bid_levels:
  ask_levels:
  fee_schedule_version:
  settlement_rules_hash:
  resolution_source:
  expiration_time:
  source_revision:
```

### Required research modules

```text
research/prediction_markets/
    canonical_events.py
    contract_equivalence.py
    orderbook_normalizer.py
    fee_model.py
    synchronized_state.py
    single_market_arb.py
    cross_venue_arb.py
    combinatorial_arb.py
    execution_capacity.py
    settlement_risk.py
    calibration.py
```

### Mandatory falsification tests

```text
stale-quote rejection
clock-offset sensitivity
state-alignment tolerance
fee shock
slippage shock
partial-fill simulation
one-leg fill failure
order-book depletion
contract-resolution mismatch
venue outage
capital lockup
```

Do not promote merely because:

```text
YES + NO < 1 at some timestamp
```

---

## 23.3 Research Engine B — Hawkes Information-Diffusion / Market-Endogeneity Model

### Status

```text
RESEARCH FEATURE / DIAGNOSTIC
NO DIRECT TRADE AUTHORITY
```

The image correctly points toward Hawkes processes as a way to separate exogenous information shocks from endogenous event clustering.

A univariate Hawkes process can be represented as:

```text
lambda(t) = mu(t) + SUM_{ti < t} phi(t - ti)
```

For an exponential kernel:

```text
phi(u) = alpha * exp(-beta*u),  u > 0
```

A multivariate form is:

```text
lambda_i(t)
  = mu_i(t)
    + SUM_j SUM_{tk_j < t} phi_ij(t - tk_j)
```

Interpretation:

```text
mu(t)      = background / exogenous intensity
phi_ii     = self-excitation
phi_ij     = cross-excitation / contagion
lambda_i   = instantaneous conditional event intensity
```

### Branching ratio / endogeneity

For a univariate stationary Hawkes process:

```text
n = integral_0^infinity phi(u) du
```

For the exponential kernel:

```text
n = alpha / beta
```

Broad interpretation:

```text
n small  -> more activity attributable to exogenous baseline
n high   -> stronger endogenous cascading
n near 1 -> near-critical / highly self-exciting dynamics
```

Stationarity generally requires the relevant branching structure to remain subcritical; for multivariate Hawkes models this is tied to the spectral radius of the matrix of integrated kernels being below one.

### News-diffusion model

Do NOT simply fit one Hawkes model to headlines and prices and call the residual "information."

Use explicit event types:

```text
scheduled_macro_news
unscheduled_news
quote_update
midprice_up_jump
midprice_down_jump
trade_buy
trade_sell
spread_widening
spread_narrowing
volatility_jump
```

A useful conceptual decomposition is:

```text
market_response
  = scheduled/exogenous impulse
  + endogenous self-excitation
  + cross-excitation across market event types
  + residual noise / omitted structure
```

### FX-specific evidence

Rambaldi, Pennesi, and Lillo (Physical Review E, 2015) modeled FX market activity around scheduled macroeconomic announcements using a Hawkes framework with endogenous and news-related components. Their empirical setting included EUR/USD, EUR/JPY, and USD/JPY EBS data. This is directly relevant to the FX project.

Bacry, Mastromatteo, and Muzy's survey documents applications of Hawkes processes to high-frequency volatility, market stability, systemic contagion, optimal execution, and full order-book dynamics.

### Half-life

For an exponential kernel:

```text
half_life = ln(2) / beta
```

But this is the half-life of the fitted excitation kernel, not automatically the economic half-life of "information."

Codex MUST label it precisely.

### Required corrections to the image's simplified workflow

The image suggests "news → spike → echo → absorption." That is a useful intuition, but implementation MUST control for:

```text
intraday seasonality
scheduled announcement timing
announcement surprise magnitude
consensus expectations
multiple simultaneous releases
market open/close effects
quote batching
feed latency
tick-size changes
volatility regime
asset-specific microstructure
```

### Required data contract

```yaml
MarketEvent:
  event_id:
  instrument:
  event_type:
  event_time:
  received_time:
  source:
  direction:
  magnitude:
  metadata:
  source_revision:
```

For macro events also store:

```text
release_value
consensus_value
previous_value
revised_previous_value
standardized_surprise
scheduled_time
actual_publication_time
```

### Required modules

```text
research/information_diffusion/
    event_schema.py
    seasonality.py
    news_surprise.py
    hawkes_univariate.py
    hawkes_multivariate.py
    kernels.py
    goodness_of_fit.py
    residual_diagnostics.py
    endogeneity.py
    contagion.py
    event_study.py
```

### Evaluation

Use:

```text
log-likelihood
AIC/BIC where appropriate
time-rescaling residual tests
out-of-sample likelihood
parameter stability
bootstrap uncertainty
regime stability
comparison against Poisson and simpler baselines
```

Never promote a Hawkes-derived feature simply because it is mathematically sophisticated.

---

## 23.4 Research Engine C — Option-Implied Risk-Neutral Distribution

### Status

```text
OPTIONS RESEARCH
RESEARCH ONLY UNTIL OPTIONS DATA / CONVENTIONS ARE HARDENED
```

Breeden and Litzenberger showed that, under standard no-arbitrage conditions, the second derivative of a call-price function with respect to strike contains state-price information.

For maturity T and strike K, a common risk-neutral density expression is:

```text
q_Q(K) = exp(r*T) * d²C(K,T)/dK²
```

with the precise discount/carry treatment depending on market conventions.

### Critical distinction

```text
RISK-NEUTRAL DISTRIBUTION != REAL-WORLD FORECAST DISTRIBUTION
```

The risk-neutral density reflects prices under the pricing measure Q and embeds risk premia.

Codex MUST NOT tell the user:

```text
"the market says there is a 30% real-world probability"
```

merely because the risk-neutral density assigns 30% mass to a region.

The correct language is:

```text
"the option surface implies X under the risk-neutral pricing measure,
subject to data and surface-model assumptions."
```

### Numerical danger

Second derivatives amplify noise.

Naively applying:

```python
np.gradient(np.gradient(call_prices, strikes), strikes)
```

to sparse, crossed, stale, or arbitrage-violating quotes can create:

```text
negative densities
oscillating densities
fake tail mass
unstable peaks
```

### Correct implementation order

```text
raw option chain
→ quote quality
→ remove stale/crossed/invalid quotes
→ forward / discount / carry normalization
→ arbitrage diagnostics
→ implied-volatility representation
→ constrained smooth surface
→ reconstruct call-price curve
→ numerical/analytic second derivative
→ non-negativity / normalization checks
→ uncertainty bands
```

### No-arbitrage shape requirements

For a fixed maturity, call prices should satisfy basic strike monotonicity and convexity constraints. The fitted surface SHOULD avoid static butterfly arbitrage and, across maturities, calendar arbitrage.

### Market-specific conventions

For FX options, Codex MUST account for:

```text
domestic rate
foreign rate
forward FX
Garman-Kohlhagen / Black-style conventions
delta conventions
premium-adjusted vs unadjusted delta
ATM convention
RR / butterfly quoting where applicable
```

For equity/index options:

```text
dividends
forward level
borrow/carry
early exercise implications for American options
```

Do not mix conventions.

### Useful derived research outputs

```text
risk-neutral density
risk-neutral CDF
risk-neutral quantiles
implied skew
implied kurtosis proxies
left-tail / right-tail mass
probability mass in user-defined price regions
term structure of distributions
change in distribution around events
```

Potential future Alpha Studio feature:

```text
OPTION-IMPLIED EXPECTATIONS
vs
MODEL FORECAST
vs
HISTORICAL DISTRIBUTION
```

Disagreement can become research evidence.

### Required modules

```text
research/options_implied/
    option_chain_quality.py
    forwards.py
    discounting.py
    conventions_fx.py
    conventions_equity.py
    implied_vol.py
    surface_fit.py
    no_arbitrage.py
    risk_neutral_density.py
    density_uncertainty.py
    event_comparison.py
```

### Validation

Required tests:

```text
density integrates approximately to 1
no materially negative density
boundary sensitivity
strike-grid sensitivity
surface-model sensitivity
quote perturbation sensitivity
forward/rate sensitivity
synthetic Black-Scholes recovery test
```

---

## 23.5 Research Engine D — Backtest-Overfitting and Selection-Bias Detector

### Status

```text
CANONICAL PROMOTION INFRASTRUCTURE
MANDATORY FOR LARGE SEARCH FAMILIES
```

This is not optional decoration.

The more bots, strategies, hyperparameters, assets, features, timeframes, and experiments FX evaluates, the greater the probability that impressive historical results arise by chance.

### Core problem

If FX evaluates N candidate strategies and reports only the best Sharpe ratio:

```text
observed_best_sharpe
```

is a selected maximum, not an unbiased estimate of skill.

As N rises, the expected maximum rises even when all strategies have zero true edge.

### Deflated Sharpe Ratio

Bailey and López de Prado's Deflated Sharpe Ratio adjusts the significance of an observed Sharpe ratio for effects including:

```text
multiple testing / selection bias
non-normal return distributions
finite sample length
skewness
kurtosis
```

Codex SHOULD use a vetted implementation and unit-test it against published examples rather than transcribing a formula from a social-media image.

### Probability of Backtest Overfitting

Bailey, Borwein, López de Prado, and Zhu proposed a framework using Combinatorially Symmetric Cross-Validation (CSCV) to estimate the probability that a strategy selected as best in-sample underperforms out-of-sample.

PBO belongs in the Examiner / promotion system.

### Required experiment-family accounting

Every candidate MUST belong to a research family.

Store:

```yaml
research_family_id:
parent_hypothesis_id:
number_of_models_tried:
number_of_feature_sets_tried:
number_of_hyperparameter_trials:
number_of_assets_searched:
number_of_timeframes_searched:
number_of_label_variants:
number_of_cost_models:
selection_rule:
pre_registered_metrics:
```

Do not allow researchers or bots to reset the count because an experiment "felt different."

### Minimum anti-overfitting stack

For material strategy searches:

```text
chronological train/validation/test
walk-forward evaluation
purging / embargo when labels overlap
locked hidden holdout
experiment-count tracking
parameter perturbation
transaction-cost stress
bootstrap confidence intervals
Probabilistic Sharpe Ratio where applicable
Deflated Sharpe Ratio where applicable
PBO / CSCV where applicable
false-discovery controls across broad families
```

For exceptionally broad data mining, also consider research tools such as:

```text
White's Reality Check
Hansen's SPA test
backtest-overfitting diagnostics
nested time-series model selection
```

### Random-strategy null laboratory

The image's idea of generating many random rules is educationally useful.

FX SHOULD build a null laboratory:

```text
random entry rules
random feature subsets
randomized labels where appropriate
permuted signals preserving selected dependence structures
```

Purpose:

```text
show the Supervisor how impressive metrics can emerge by luck
```

This should be part of Bot curriculum training.

### Required output

```yaml
OverfitReport:
  experiment_id:
  research_family_id:
  n_trials_effective:
  raw_sharpe:
  probabilistic_sharpe:
  deflated_sharpe:
  pbo:
  bootstrap_ci:
  oos_sharpe:
  cost_stress_status:
  holdout_status:
  selection_bias_risk:
  promotion_recommendation:
```

No metric is allowed to hide uncertainty.

---

## 23.6 Mathematical Foundation I — Linear Algebra

### Why it matters to FX

Linear algebra is the language underlying:

```text
factor models
covariance matrices
portfolio optimization
least squares
PCA
Kalman filters
regression
neural networks
state-space models
risk decomposition
cross-asset exposure analysis
```

### Required concepts

```text
vectors
matrices
matrix multiplication
inner products
norms
linear independence
rank
column / row / null spaces
orthogonality
projections
least squares
eigenvalues / eigenvectors
positive-semidefinite matrices
SVD
QR decomposition
condition numbers
pseudoinverse
```

### Trading-specific examples

#### Least squares

```text
beta_hat = (X^T X)^(-1) X^T y
```

Use conceptually, but Codex SHOULD NOT numerically compute regression via an explicit matrix inverse when stable solvers such as QR/SVD/lstsq are available.

#### PCA

For covariance matrix Sigma:

```text
Sigma v_i = lambda_i v_i
```

Use for:

```text
yield-curve level/slope/curvature
factor compression
cross-asset latent risk
correlation-regime analysis
portfolio diagnostics
```

#### SVD

```text
X = U S V^T
```

Use for:

```text
low-rank structure
numerical stability
latent factor extraction
collinearity diagnosis
```

### Numerical discipline

Codex MUST monitor:

```text
matrix conditioning
near-singularity
collinearity
unstable covariance estimates
sample-size-to-dimension ratio
```

A mathematically valid matrix expression may still be numerically unusable.

MIT 18.06 (Gilbert Strang) is an appropriate foundational reference.

---

## 23.7 Mathematical Foundation II — Multivariable Calculus

### Required concepts

```text
limits
single-variable derivatives
partial derivatives
chain rule
gradient
Jacobian
Hessian
Taylor expansion
multivariable optimization
integration
constrained derivatives / Lagrange multipliers
```

### FX uses

```text
loss gradients
backpropagation
Greeks / option sensitivities
model sensitivity
optimization
likelihood maximization
continuous-time finance
local approximation / stress testing
```

### Gradient

For scalar objective f(theta):

```text
grad f(theta)
```

indicates the local direction of steepest increase.

### Hessian

```text
H_ij = d²f / dtheta_i dtheta_j
```

contains local curvature information and is important for Newton methods, uncertainty approximations, and optimization diagnostics.

### Taylor approximation

```text
f(x + h)
≈ f(x)
  + grad(f(x))^T h
  + 1/2 h^T H(x) h
```

This is extremely useful for local risk and sensitivity reasoning.

### Implementation warning

Automatic differentiation can calculate derivatives.
It does not guarantee that the objective is economically meaningful or that the model generalizes.

MIT 18.02 multivariable calculus is an appropriate foundational reference.

---

## 23.8 Mathematical Foundation III — Probability and Statistics

This is arguably the most important foundation for trading research.

### Required concepts

```text
random variables
PMF / PDF / CDF
expectation
variance
covariance
correlation
conditional probability
Bayes' rule
common distributions
law of large numbers
central limit theorem
sampling distributions
estimators
bias
variance
maximum likelihood
confidence intervals
hypothesis tests
p-values and their limitations
multiple testing
bootstrap
Monte Carlo
Bayesian updating
```

For financial data also require:

```text
stationarity
serial correlation
heteroskedasticity
fat tails
skewness
volatility clustering
regime shifts
autocorrelation
cross-correlation
non-independent observations
selection bias
survivorship bias
```

### Core principle

A model prediction is usually a distribution or conditional probability—not certainty.

Every bot SHOULD expose uncertainty where the model supports it.

### Calibration

For probabilistic predictions:

```text
predicted 70%
```

should correspond, over comparable observations, to approximately 70% empirical frequency if the model is calibrated.

Evaluate:

```text
Brier score
log loss
reliability curves
calibration slope/intercept
```

### Bayes

```text
P(theta | data)
∝ P(data | theta) * P(theta)
```

Useful conceptually for:

```text
belief updating
model uncertainty
regime inference
parameter uncertainty
```

### Financial warning

Textbook i.i.d. assumptions often fail in markets.

Do not automatically apply:

```text
sqrt(time) Sharpe scaling
normal VaR
standard t-tests
```

without checking dependence and distributional assumptions.

Harvard Stat 110 and Stanford CS229 probability review materials are appropriate foundations.

---

## 23.9 Mathematical Foundation IV — Optimization

Optimization turns objectives into decisions.
It can also turn bad objectives into very efficient mistakes.

### Required concepts

```text
objective functions
constraints
convex sets
convex functions
gradient descent
stochastic gradient descent
Newton / quasi-Newton methods
Lagrangians
KKT conditions
duality
regularization
linear programming
quadratic programming
second-order cone programming where useful
```

### Portfolio example

A stylized mean-variance problem:

```text
minimize    w^T Sigma w - lambda * mu^T w
subject to  1^T w = 1
            risk / leverage / exposure constraints
```

But historical `mu` is extremely noisy.

Codex SHOULD prefer robust constraints and uncertainty-aware approaches over blindly optimizing sample means.

### Risk-budgeting / sizing

Optimization MAY allocate among already eligible strategies.
It cannot make an invalid strategy valid.

### Regularization

```text
L1 -> sparsity
L2 -> coefficient shrinkage
```

Useful for controlling unstable high-dimensional models.

### Critical anti-pattern

Do NOT optimize directly for maximum historical Sharpe across huge parameter spaces without selection-bias correction.

Stanford EE364A / Boyd and Vandenberghe's Convex Optimization are appropriate references.

---

## 23.10 Mathematical Foundation V — Deep Learning

### Status

```text
CHALLENGER MODEL FAMILY
NOT DEFAULT AUTHORITY
```

Deep learning should come after strong statistical and classical baselines.

### Core sequence

Codex / bot curriculum should understand:

```text
linear regression
logistic regression
maximum likelihood
cross-entropy
multilayer perceptrons
activation functions
backpropagation
regularization
normalization
sequence models
attention
transformers
```

### Basic neural layer

```text
z = W x + b
a = sigma(z)
```

### Backpropagation

Backprop is repeated application of the chain rule through the computational graph.

### Attention

A common form:

```text
Attention(Q,K,V)
  = softmax(Q K^T / sqrt(d_k)) V
```

### Financial warning

Markets often provide:

```text
low signal-to-noise
nonstationarity
few truly independent samples
heavy regime dependence
large multiple-testing freedom
```

Therefore a deep network MUST beat appropriate simpler baselines such as:

```text
naive persistence
linear/logistic regression
regularized linear models
Random Forest
XGBoost/LightGBM
simple deterministic strategies
```

under the same chronological OOS and cost assumptions.

No model receives extra trust for having more parameters.

Stanford CS229 covers the progression from supervised learning and regularization through neural networks and reinforcement learning; this is a better curriculum structure than beginning with a transformer.

---

## 23.11 Mathematics Curriculum for the Bot Team

The phrase "train the bots in mathematics" MUST NOT mean copying textbooks into model context and assuming understanding.

Implement mathematics as three layers:

### Layer A — deterministic libraries

Trusted implementations for:

```text
linear algebra
statistics
optimization
option math
Hawkes estimation
risk metrics
calibration
overfitting diagnostics
```

Bots call tools rather than inventing arithmetic.

### Layer B — structured knowledge

Curated notes with:

```text
definition
assumptions
formula
failure modes
financial application
unit-tested example
source
```

### Layer C — competency evaluation

Research agents should pass scenario tests.

Example:

```text
QUESTION:
A covariance matrix has a near-zero eigenvalue.
Should the bot invert it directly?

EXPECTED:
No. Diagnose conditioning / collinearity and use a stable method,
regularization, shrinkage, pseudoinverse, or factor reduction as appropriate.
```

Another:

```text
QUESTION:
A call-price curve produces negative second derivative regions.
Does this prove negative market probability?

EXPECTED:
No. First suspect data quality, interpolation/surface fit,
and static-arbitrage violations; risk-neutral densities must be
constructed under appropriate constraints.
```

Another:

```text
QUESTION:
Out of 5,000 strategies, one has Sharpe 3.0 in-sample.
Is it promoted?

EXPECTED:
No. Trial count, OOS results, DSR/PBO, hidden holdout,
cost stress, robustness, and selection bias are required.
```

### Supervisor role

The Supervisor MAY identify competency gaps and assign research exercises.

It MUST NOT rewrite mathematical truth based on which formula recently made more money.

---

## 23.12 New Specialist Research Agents

Do not spawn all agents on every decision.

Create specialist capabilities that are invoked only when relevant:

```text
Prediction Market Microstructure Researcher
Information Diffusion / Hawkes Researcher
Options-Implied Distribution Researcher
Backtest Integrity / Multiple-Testing Examiner
Linear Algebra / Numerical Stability Auditor
Statistical Assumptions Auditor
Optimization Auditor
Deep Model Challenger Reviewer
```

These are research roles, not independent traders.

### Example workflow

```text
StrategyBot proposes edge
        ↓
Statistical Auditor
        ↓
Backtest Integrity Examiner
        ↓
Numerical Stability Auditor
        ↓
Domain specialist if applicable
        ↓
Examiner hidden tests
        ↓
Promotion Service
        ↓
Risk Governor
```

---

## 23.13 New Evidence Types

Extend the Evidence Ledger with:

```text
PREDICTION_MARKET_PROBABILITY
PREDICTION_MARKET_EXECUTABLE_EDGE
HAWKES_ENDOGENEITY
HAWKES_CROSS_EXCITATION
NEWS_IMPACT_HALF_LIFE
RISK_NEUTRAL_DENSITY
RISK_NEUTRAL_TAIL_MASS
PROBABILISTIC_SHARPE
DEFLATED_SHARPE
PBO
MULTIPLE_TESTING_WARNING
NUMERICAL_CONDITION_WARNING
MODEL_CALIBRATION
```

Each EvidenceItem MUST contain:

```text
source
instrument / event
as_of_time
calculation_version
data_version
assumptions
uncertainty
expiry / staleness policy
```

---

## 23.14 New Failure Classes for the Supervisor

Add:

```text
CONTRACT_EQUIVALENCE_ERROR
STATE_ALIGNMENT_ERROR
LATENCY_ARBITRAGE_ILLUSION
INSUFFICIENT_DEPTH
HAWKES_MISSPECIFICATION
EXOGENOUS_ENDOGENOUS_CONFUSION
RISK_NEUTRAL_REAL_WORLD_CONFUSION
OPTION_SURFACE_ARBITRAGE
NUMERICAL_DIFFERENTIATION_INSTABILITY
MULTIPLE_TESTING_INFLATION
ILL_CONDITIONED_MATRIX
INVALID_DISTRIBUTIONAL_ASSUMPTION
OPTIMIZER_OVERFIT
DEEP_MODEL_COMPLEXITY_WITHOUT_INCREMENTAL_EDGE
```

These failures should become teachable LessonPackages after independent reproduction.

---

## 23.15 New Implementation Priority — Where this belongs

This material does NOT displace the canonical roadmap.

Integrate it as follows:

```text
P0-P4
Governance, data, accounting, risk, Examiner

P5
Classical baselines + mathematical/statistical core

P6
Supervisor MVP + competency diagnostics

P7
Bot Factory + research-family accounting

P8A
Backtest Overfitting Detector (DSR/PSR/PBO + null lab)

P8B
Hawkes / information-diffusion research

P8C
Options-implied risk-neutral distribution research

P8D
Prediction-market microstructure research

P9
Meta-learning / experiment recommendation

P10+
Deep / RL challengers only after simple baselines and research controls work
```

The Backtest Overfitting Detector receives the highest priority of these four because it protects every other research program.

---

## 23.16 Source-quality conclusions from the supplied images

### Strong / worth absorbing

```text
Breeden-Litzenberger theorem
Deflated Sharpe Ratio / PBO concepts
Hawkes-process event modeling
linear algebra curriculum
multivariable calculus curriculum
probability/statistics curriculum
convex optimization curriculum
backprop / deep-learning foundations
```

### Useful but must be reframed

```text
Prediction-market arbitrage
```

Reason: real executable edges are much rarer and more capacity-constrained than simple price identities imply.

### Must not be accepted literally

```text
"risk-neutral density = actual future probability"
"Hawkes half-life = exact information half-life"
"best backtest Sharpe = best strategy"
"more deep learning = better trading"
"cross-venue price difference = arbitrage"
```

These are precisely the kinds of simplifications the Supervisor should teach bots to reject.

---

## 23.17 Primary and high-quality references for Codex research

Codex SHOULD use the following as reference anchors when implementing these modules:

```text
Breeden, D. T. & Litzenberger, R. H. (1978)
Prices of State-Contingent Claims Implicit in Option Prices
The Journal of Business 51(4), 621-651
DOI: 10.1086/296025

Bailey, D. H. & López de Prado, M. (2014)
The Deflated Sharpe Ratio: Correcting for Selection Bias,
Backtest Overfitting, and Non-Normality
The Journal of Portfolio Management 40(5), 94-107
DOI: 10.3905/jpm.2014.40.5.094

Bailey, D.; Borwein, J.; López de Prado, M.; Zhu, Q. J.
The Probability of Backtest Overfitting
Journal of Computational Finance
DOI: 10.21314/JCF.2016.322

Bacry, E.; Mastromatteo, I.; Muzy, J.-F. (2015)
Hawkes Processes in Finance
Market Microstructure and Liquidity
arXiv:1502.04592

Rambaldi, M.; Pennesi, P.; Lillo, F. (2015)
Modeling foreign exchange market activity around macroeconomic news:
Hawkes-process approach
Physical Review E 91, 012819
DOI: 10.1103/PhysRevE.91.012819

Cheng, G.; Yang, J.; Zou, H. (2026)
Arbitrage Analysis in Polymarket NBA Markets
arXiv:2605.00864

MIT OpenCourseWare 18.06 — Linear Algebra — Gilbert Strang
MIT OpenCourseWare 18.02 — Multivariable Calculus
Harvard Stat 110 — Probability
Stanford EE364A — Convex Optimization
Boyd & Vandenberghe — Convex Optimization
Stanford CS229 — Machine Learning
```

### Research-source rule

Academic citation does not remove the need to:

```text
read methodology
check assumptions
reproduce results where relevant
check code/data availability
check licensing
check whether evidence applies to FX's market/data/horizon
```

---

## 23.18 Codex implementation directive for this section

When Codex receives this file, it MUST NOT immediately install packages or create all modules above.

First:

```text
1. Inspect current FX repository.
2. Map existing capabilities to Section 23 requirements.
3. Produce a gap analysis.
4. Reuse existing DSR/PBO/statistics/options/event code if sound.
5. Add tests before wiring new research outputs to the Model Council.
6. Keep all new engines RESEARCH_ONLY initially.
7. Register every new evidence type and provenance contract.
8. Keep live trading disabled.
```

Priority implementation question:

```text
"What is the smallest first-party, testable module that improves
research integrity without increasing execution risk?"
```

Usually the answer from this section is:

```text
Backtest Integrity / Multiple-Testing Examiner
```

not prediction-market execution or a new deep neural network.

---

# 24. FINAL CODEX DIRECTIVE

Build this as a **research operating system**, not a swarm of autonomous personalities.

The right abstraction is:

```text
versioned data
+ typed strategies
+ reproducible experiments
+ independent evaluation
+ deterministic risk
+ realistic paper execution
+ bounded research agents
+ durable failure memory
+ provenance-controlled knowledge
```

The Supervisor is valuable only if it improves the quality and efficiency of this process.

The desired behavior is:

```text
TRAIN MANY CANDIDATES
BUT PROMOTE FEW

LEARN FROM FAILURES
BUT DO NOT REINFORCE NOISE

SHARE EVIDENCE
NOT BELIEFS

PRESERVE DIVERSITY
BUT MEASURE REAL INDEPENDENCE

AUTOMATE RESEARCH
BUT DO NOT AUTOMATE AWAY GOVERNANCE
```

If a proposed implementation makes the system more autonomous but less reproducible, less auditable, less statistically defensible, or less safe, **reject that implementation**.

---

# APPENDIX A — RESEARCH CONTEXT FROM THE PRIOR FILE

**Codex note:** The material below is retained because it contains useful research context, mathematical ideas, source notes, and external-resource observations. It is **NON-CANONICAL**. If it conflicts with Sections 0–23 above, the canonical section wins.

Claims labeled “verified” below reflect the earlier research pass. Before operational use, re-check the exact source/revision and record it in the Source Registry.

# PART I — SOURCE INVENTORY

## 1. User-provided source material

The pasted material contained extracted ideas from social posts and prior analysis around:

- Bloomberg-like AI market research pipelines.
- 30 quant-finance project ideas.
- EdgeBuild-like AI quant workflow ideas.
- A composite HFT objective function.
- The “12 Laws of Quant Trading.”
- Random Forest, XGBoost, Decision Tree, PCA, and LASSO use in finance.
- A five-stage AI trading loop: Scan → Research → Analyze → Risk → Plan.
- Self-improving agent ideas.
- Real-time sentiment and volume/order-flow features.
- Alpha Studio / relative-asset analytics.
- Volatility clustering and tail-risk sizing.
- Commodity cost-of-carry mathematics.
- Covered Interest Parity ideas for FX.
- Supply/demand and inventory models.
- Python/quant tooling.
- Stochastic calculus, GBM, Itô’s Lemma, Black-Scholes and Greeks.

The pasted material also referenced these GitHub organizations/repositories:

- https://github.com/orgs/deepseek-ai/repositories?type=all
- https://github.com/karimkhemkapital/janus-anti-fragility-strategy
- https://github.com/karimkhemkapital/Beta-and-trading-environement
- https://github.com/karimkhemkapital/quantitative-trading-free-lesson
- https://github.com/goldmansachs

## 2. Requested Hugging Face sources

- https://huggingface.co/mito0o852
- https://huggingface.co/Adilbai/stock-trading-rl-agent

---

# PART II — CORE TRADING PHILOSOPHY EXTRACTED FROM THE PASTED MATERIAL

## 3. Project thesis

The central idea is not “predict the next candle perfectly.” The system should search for repeatable statistical or structural edges while treating survival, capital preservation, costs, and uncertainty as first-class constraints.

The intended FX system should evolve toward an institutional-style research loop:

**Data → Features → Regime → Candidate signals → Risk gate → Portfolio construction → Cost-aware simulation → Paper execution → Attribution → Validation → Promotion/demotion**

An LLM/agent may help research, summarize evidence, generate hypotheses, compare models, inspect failures, and coordinate tools. It must not bypass deterministic validation or risk controls.

---

# PART III — THE 12 LAWS OF QUANT TRADING

## 4. Rules to encode into the platform

1. **Every model is wrong; some are temporarily useful.**  
   Treat every model as conditional on a market regime and a data-generating process that can change.

2. **Reality is messier than mathematics.**  
   Backtests must model missing data, spreads, execution delay, liquidity, broker rules, session boundaries, and market closures.

3. **Risk is about what has not happened yet.**  
   Historical volatility alone is not enough. Include stress tests, regime shocks, gap scenarios, and tail-risk estimates.

4. **Markets compensate uncertainty, not certainty.**  
   The platform should estimate distributions and confidence, not output fake certainty.

5. **Backtests describe the past.**  
   Every backtest is a hypothesis test, not a promise.

6. **Edges decay.**  
   Track live/paper degradation, feature drift, signal hit-rate decay, turnover changes, and cost inflation.

7. **Costs kill weak strategies.**  
   Spread, commission, slippage, financing, borrow, funding, and market impact must be modeled.

8. **Capacity is finite.**  
   Even in paper mode, estimate how notional size would affect fill quality and market impact.

9. **Complexity is fragile.**  
   Prefer simple models that survive purged walk-forward testing over highly tuned models with hundreds of unstable parameters.

10. **Correlation is not permanent diversification.**  
    Use regime-aware covariance, tail correlation, factor exposure, and stress correlation.

11. **Position sizing can dominate signal quality.**  
    Put the risk engine between every strategy and every order.

12. **Risk management compounds.**  
    The system’s primary objective is survival with positive expected value, not maximum activity.

---

# PART IV — BLOOMBERG-LIKE AI MARKET RESEARCH PIPELINE

## 5. Five research pillars

### 5.1 Market Data

Collect and analyze:

- price action
- volume
- realized and implied volatility when available
- sector/index performance for equities
- market breadth
- rates and yield curves
- commodities
- FX crosses
- cross-asset risk proxies
- regime labels

For FX specifically, augment with:

- spot bid/ask
- spread
- tick rate
- quote imbalance
- volatility by session
- interest-rate differential
- swap/roll proxies where available
- DXY or broad USD regime
- equity-risk sentiment
- commodity links for commodity currencies

### 5.2 News Analysis

The system should ingest headlines and structured macro events, then score:

- relevance to instrument
- novelty
- expected impact
- directionality
- confidence
- time horizon
- source quality

Do not let an LLM create trades directly from unverified news. News should become features or event flags evaluated against historical behavior.

### 5.3 Earnings

Relevant mainly to equities, equity indices, and correlated FX risk sentiment. Track:

- earnings calendar
- expectations
- surprises
- guidance
- call sentiment

### 5.4 Macro Data

Required for FX:

- CPI/PCE/inflation
- employment
- GDP/growth
- PMIs
- central-bank decisions
- speeches
- policy-rate expectations
- yield curves
- liquidity conditions
- geopolitical events
- fiscal announcements

### 5.5 Company/Fundamental Data

Relevant for stock bots and cross-asset context. It should not be forced into pure FX models where it adds no causal value.

### Research output

The analysis layer should produce a machine-readable and human-readable memo containing:

- market regime
- fundamental/macroeconomic state
- technical state
- volatility state
- liquidity/spread state
- sentiment/news state
- catalysts
- risks
- signal consensus/disagreement
- proposed scenario tree
- confidence band
- explicit reasons to **not trade**

---

# PART V — 30 QUANT PROJECTS AS FX MODULES

## 6. Foundations and market data

1. Return & Volatility Analyzer  
2. Portfolio Risk Dashboard  
3. Correlation & Covariance Engine  
4. Factor Exposure Analyzer  
5. Market Regime Detection Model

## 7. Risk and portfolio

6. Historical VaR  
7. Parametric VaR  
8. Monte Carlo VaR  
9. Expected Shortfall / CVaR  
10. Mean-Variance / constrained portfolio optimizer

## 8. Quant trading

11. Moving-average / mean-reversion research  
12. Momentum research  
13. Pairs/statistical-arbitrage research  
14. Factor long/short research  
15. Multi-asset trend following

## 9. Derivatives and pricing

16. Black-Scholes engine  
17. Implied-vol solver  
18. Greeks  
19. Binomial pricer  
20. Monte Carlo derivative pricer

## 10. Advanced quant and ML

21. GARCH volatility forecasting  
22. Yield-curve modeling  
23. Kalman-filter pairs / dynamic hedge ratios  
24. ML return/direction/volatility predictor  
25. Alternative-data alpha model

## 11. System-level projects

26. Limit-order-book / microstructure simulator  
27. Execution model  
28. Portfolio stress-testing engine  
29. End-to-end quant research pipeline  
30. Full systematic paper-trading strategy

Codex should treat these not as 30 disconnected demos but as modules of one research platform.

---

# PART VI — MATHEMATICAL FRAMEWORKS

## 12. Composite cost/risk objective

The pasted material proposed an HFT-style objective of the form:

```text
L = -E[Signal/Return]
    + α * VolatilityPenalty
    + β * DrawdownPenalty
    + γ * TradingCosts
    + δ * MarketFrictionPenalty
```

This is a useful **conceptual objective**, not a universal market law.

A safer implementation for FX strategy selection would separate hard constraints from optimization:

```text
maximize expected_net_return_or_utility
subject to:
    max_drawdown <= threshold
    expected_shortfall <= threshold
    exposure <= limits
    turnover <= limit
    spread_cost <= limit
    leverage <= limit
    minimum_sample_size >= threshold
    out_of_sample_stability == true
```

Then rank surviving strategies with a multi-objective score rather than allowing a large return term to compensate for catastrophic risk.

## 13. Commodity cost of carry

```text
F(t,T) = S(t) * exp[(r + s - y)(T-t)]
```

Where:

- `S(t)` = spot price
- `r` = risk-free rate
- `s` = storage cost
- `y` = convenience yield

Interpretation:

- `r+s-y > 0` tends toward contango.
- `r+s-y < 0` tends toward backwardation.

Use in the FX project mainly for cross-asset context and commodity-linked currencies such as CAD, AUD, NOK, etc. Do not automatically translate commodity carry into FX signals without testing the relationship.

## 14. Covered Interest Parity / FX carry concept

A standard conceptual relationship links spot FX, forward FX, and domestic/foreign rates. The project can create features such as:

- rate differential
- forward-implied carry
- deviation from covered parity when reliable funding/basis data is available
- central-bank expectation differential

These are better suited to multi-day / macro FX strategies than tick-level execution models.

## 15. Supply/demand model

```text
Qd(P) = a - bP
Qs(P) = c + dP
```

Useful for economic reasoning and commodity/inventory models, but not a standalone trading algorithm.

## 16. Geometric Brownian Motion

```text
dS_t = μ S_t dt + σ S_t dW_t
```

Use GBM as:

- a baseline simulation model
- a sanity check
- a Monte Carlo educational tool

Do **not** assume real FX returns are perfectly Gaussian or stationary. Add fat-tail, volatility clustering, jump, and regime models.

## 17. Itô’s Lemma / Black-Scholes / Greeks

These are relevant for derivatives, options, and simulation modules. They should be implemented in a separate pricing library rather than mixed into every spot-trading strategy.

---

# PART VII — MACHINE LEARNING MODEL ROLES

## 18. Random Forest

Best use:

- nonlinear feature interactions
- regime classification
- direction probability
- risk/event classification
- feature ranking as a research aid

Risks:

- leakage from temporal data
- overfit from many correlated indicators
- poor probability calibration

## 19. XGBoost

Best use:

- noisy tabular factor panels
- nonlinear ranking/classification
- return bucket, volatility, or event outcome models

Must include:

- time-series split
- purging/embargo where labels overlap
- regularization
- feature stability analysis

## 20. Decision Trees

Best use:

- interpretable rules
- regime/risk gates
- debugging learned thresholds

Do not assume a single tree is more reliable merely because it is explainable.

## 21. PCA

Best use:

- yield curves
- cross-asset factor compression
- correlated FX pair factor extraction
- portfolio exposure analysis

Potential FX example:

- PC1 = broad USD factor
- PC2 = risk/commodity currency factor
- PC3 = regional/european factor

The labels must be empirically inferred; do not hard-code these interpretations.

## 22. LASSO

Best use:

- sparse feature selection
- reducing hundreds of weak signals
- interpretable linear models

Use stability-selection and walk-forward checks because selected variables can change across regimes.

---

# PART VIII — FIVE-STAGE AUTONOMOUS TRADING LOOP

## 23. Scan

Scan the allowed universe and generate candidates from deterministic filters and approved models.

Examples:

- volatility expansion/contraction
- trend state
- mean-reversion z-score
- macro event proximity
- spread/liquidity quality
- relative strength
- cross-asset divergence

## 24. Research

For each candidate, gather:

- recent market state
- historical analogs
- macro calendar
- relevant news
- rate context
- cross-asset relationships
- model agreement/disagreement

## 25. Analyze

Compute:

- trend
- momentum
- support/resistance only as quantitative levels
- volatility
- regime
- liquidity
- volume/tick activity
- spread
- price/volume anomalies
- factor exposures

## 26. Risk

Risk engine produces or rejects:

- position size
- initial stop
- trailing logic if used
- profit target or exit rule
- invalidation rule
- max holding period
- portfolio exposure effect
- worst-case stress estimate

## 27. Plan

Generate a structured trade intent, for example:

```json
{
  "symbol": "EURUSD",
  "mode": "paper",
  "strategy_id": "trend_v3",
  "direction": "long",
  "entry_type": "limit",
  "entry": 0.0,
  "stop_loss": 0.0,
  "take_profit": 0.0,
  "max_risk_pct": 0.0,
  "expected_cost_bps": 0.0,
  "time_horizon": "intraday",
  "regime": "...",
  "confidence": 0.0,
  "invalidation": "...",
  "evidence": [],
  "risk_gate": "pending"
}
```

Only after the deterministic risk gate approves may the paper execution engine simulate the order.

---

# PART IX — HUGGING FACE: mito0o852 DETAILED REVIEW

Source: https://huggingface.co/mito0o852

The profile exposes four public datasets and no public models at the time reviewed.

## 28. `mito0o852/OHLCV-1m`

Source: https://huggingface.co/datasets/mito0o852/OHLCV-1m

### Verified characteristics

- U.S. stock minute-level OHLCV data.
- Coverage described as 1992–2026.
- Thousands of U.S. stocks.
- Origin stated as Finnhub.
- Reformatted into monthly Parquet files.
- Columns:
  - timestamp UTC
  - open
  - high
  - low
  - close
  - volume
  - ticker
- Dataset page reports about **87.7 GB**.

### How FX should use it

Use this dataset for **cross-asset research**, not as primary FX data:

- equity risk-on / risk-off features
- index/stock breadth proxies
- market-session stress features
- correlation regime research
- training generic market-regime models

Do not merge equity minute bars directly with FX timestamps without calendar/session normalization.

## 29. `mito0o852/Finnhub`

Source: https://huggingface.co/datasets/mito0o852/Finnhub

### Verified issue

The Hugging Face dataset viewer reports a split/config parsing error because the TAR archives do not match the expected WebDataset structure.

### Recommendation

Do not make this a core dependency until Codex validates:

- file structure
- archive integrity
- schema consistency
- licensing / redistribution conditions
- whether direct Finnhub ingestion is preferable

## 30. `mito0o852/dukascopy-ticks`

Source: https://huggingface.co/datasets/mito0o852/dukascopy-ticks

### Verified characteristics

The dataset page reports:

- tabular Parquet
- **1.78 billion rows**
- tick-level fields:
  - timestamp (`int64` on viewer)
  - askPrice
  - bidPrice
  - askVolume
  - bidVolume

### Why this is extremely relevant

This can support a true FX microstructure laboratory.

Derived features Codex should create:

```text
mid = (ask + bid) / 2
spread = ask - bid
relative_spread = spread / mid
microprice_proxy = weighted bid/ask price using quoted volumes
quote_imbalance = (bidVolume - askVolume) / (bidVolume + askVolume)
tick_return = log(mid_t / mid_t-1)
tick_rate = ticks per rolling interval
spread_z = normalized spread regime
vol_1s / vol_10s / vol_1m
quote_volume_change
liquidity_shock flags
```

Important caveat:

Quoted bid/ask volume from a venue/data source is **not equivalent to centralized global FX volume**, because spot FX is fragmented/OTC. Treat it as a venue/data-feed microstructure signal, not the entire market’s order book.

### Required ingestion architecture

Do not attempt to load 1.78B rows into pandas memory.

Use:

- Polars lazy scans
- DuckDB
- partitioned Parquet
- Dask only where appropriate
- symbol/date partition filters
- streaming feature generation
- cached derived bars

Create several data tiers:

```text
raw_tick
  -> validated_tick
  -> 1s microbars
  -> 5s / 15s / 1m bars
  -> feature store
  -> research samples
```

## 31. `mito0o852/OHLCV-1m-Forex`

Source: https://huggingface.co/datasets/mito0o852/OHLCV-1m-Forex

### Verified characteristics

The dataset viewer reports:

- roughly **44 million rows**
- time range visible as 2023-01-01 through 2026-02-24
- **49 ticker values**
- fields:
  - timestamp UTC
  - open
  - high
  - low
  - close
  - volume
  - ticker

### Best use

This should be one of the primary **research/backtesting candidate datasets** for the FX project because it is already minute-aggregated and manageable compared with full ticks.

Use it for:

- 1-minute backtests
- multi-timeframe aggregation
- regime classification
- trend/mean reversion
- volatility models
- cross-pair PCA
- correlation/cointegration
- ML feature research

### Mandatory validation before trusting it

Codex must audit:

1. Missing minute frequency by symbol.
2. Weekend/off-market handling.
3. Duplicates.
4. Timestamp monotonicity.
5. Price outliers and bad ticks.
6. Whether `volume` means tick/quote volume or another source-specific quantity.
7. Instrument mapping and pip conventions.
8. DST/session effects.
9. Data continuity across years.
10. Differences versus a second independent FX source.

### Recommendation

Use this dataset to train and test **research models**, then evaluate paper behavior on a live/near-real-time feed. Do not assume historical data format exactly matches the future production feed.

---

# PART X — HUGGING FACE: Adilbai STOCK TRADING RL AGENT

Source: https://huggingface.co/Adilbai/stock-trading-rl-agent

## 32. What it is

A reinforcement-learning trading agent built with:

- Stable-Baselines3
- PPO (Proximal Policy Optimization)
- MLP policy
- stock historical data via Yahoo Finance in examples

The model card states:

- 5 stocks: AAPL, MSFT, GOOGL, AMZN, TSLA
- five years of data
- daily interval
- 60-day lookback
- 500,000 training timesteps
- batch size 64
- learning rate 0.0003
- gamma 0.99
- seed 42

## 33. Observation/state space

The documented features include:

### Trend

- SMA 20
- SMA 50
- EMA 12
- EMA 26

### Momentum

- RSI
- MACD
- MACD signal
- MACD histogram

### Volatility

- Bollinger upper/lower
- Bollinger %B

### Raw market data

- OHLC
- volume

### Portfolio state

- balance
- position
- net worth
- returns

## 34. Action space

The card describes a two-dimensional action:

1. Action type:
   - Hold
   - Buy
   - Sell
2. Position size:
   - continuous 0–1 fraction of available capital

This architecture is conceptually attractive because it separates **direction/action** from **sizing**.

## 35. Environment configuration

Model card configuration includes:

- initial balance: 10,000
- transaction cost: 0.001
- maximum position size: 1.0
- reward type: return
- risk adjustment: true

## 36. Files

The model card lists:

- `best_model.zip`
- `final_model.zip`
- `scaler.pkl`
- `config.json`
- `evaluation_results.json`
- `training_summary.json`

This is a good reproducibility pattern to emulate conceptually:

```text
model artifact
preprocessing artifact
config artifact
evaluation artifact
training summary
```

## 37. Serious problems with the reported evaluation

The model card reports results including:

- MSFT total return above 7,000%
- Sharpe values that are not commensurate with the huge headline returns
- reported maximum drawdowns above 100% for several assets
- AAPL strongly negative return
- GOOGL no activity

These numbers must **not** be taken as evidence that the model is safe or production-ready.

A drawdown above 100% is a major warning sign that one or more of the following may be wrong or nonstandard:

- drawdown calculation
- leverage/accounting assumptions
- portfolio valuation logic
- evaluation methodology
- position sizing implementation
- metric labeling

The Hugging Face page marks the evaluation as self-reported.

### Codex conclusion

**Do not plug this pretrained model directly into the FX execution engine.**

Instead, absorb the following ideas:

- PPO research pipeline
- Gym-like trading environment
- explicit observation space
- explicit action space
- stored scaler
- deterministic evaluation mode
- checkpointing
- reproducible seed
- separate backtesting framework

Then rebuild a clean FX-specific environment and validate every accounting equation.

## 38. FX-specific RL design recommendation

If RL is used, the environment should expose features such as:

```text
returns
realized volatility
ATR / range
trend features
momentum
spread
relative spread
bid/ask imbalance
session
minutes to macro event
rate differential
cross-pair factors
portfolio exposure
unrealized PnL
realized PnL
drawdown
remaining risk budget
```

Action design should be safer than unconstrained 0–100% position sizing.

Recommended conceptual action:

```text
target_position ∈ [-1, +1]
```

Then a deterministic risk layer converts the target into actual paper notional under hard limits.

### Reward function

Do not use raw return alone.

Potential research objective:

```text
reward = pnl_net_of_costs
         - λ1 * turnover_cost
         - λ2 * drawdown_increment
         - λ3 * tail_risk_penalty
         - λ4 * exposure_violation
```

Hard violations should end/reject actions rather than merely applying small penalties.

---

# PART XI — GITHUB: `karimkhemkapital/janus-anti-fragility-strategy`

Source: https://github.com/karimkhemkapital/janus-anti-fragility-strategy

## 39. Core idea

The repository describes a deterministic econophysical strategy using a signed variance-response density operator.

The primitive relationship is documented as:

```text
R_excess,t = alpha - beta * sigma^2_t + epsilon_t
```

The repository interprets:

- positive beta as fragile variance drag
- negative beta as a reversed/“negative financial mass” variance-response state

Rolling response signs and causal variance stress become density fields. The strategy compares positive and negative density balances and switches between two allocation legs after confirmation, with a one-period lag.

## 40. Strategy chain

The repository expresses the mechanism approximately as:

```text
price
 -> return
 -> variance energy
 -> signed response
 -> causal stress + constrained densities
 -> density balance
 -> confirmed regime
 -> lagged allocation
 -> realized hedge
```

Canonical pair experiments named by the repository:

- SPY / GLD
- QQQ / GLD

AAPL / GLD is described as a generalization/state-change experiment.

## 41. Files / architecture worth studying

- main executable model
- diagnostics / benchmark / robustness / cost helpers
- strategy narrative
- research documents
- export workbook pipeline

## 42. Useful concepts for FX

Do **not** blindly transplant the theory. Instead test the general ideas:

### Variance-response coefficient

For an FX pair or FX-relative basket, estimate whether returns systematically change with realized variance.

### Paired regime response

Study pairs/baskets such as:

- EURUSD vs USDCHF
- AUDUSD vs USDCAD
- risk FX basket vs safe-haven basket
- commodity currencies vs commodity index

### Causal lag

Any regime signal must be computed using information available at decision time. Avoid same-bar/same-date lookahead.

### Density/regime balance

Can be reimplemented independently as a research feature family, then compared with simpler HMM/GMM/change-point/regime models.

## 43. Licensing warning

The repository explicitly states that it is **not open source** and restricts use to private/non-commercial research/education under its license.

Therefore:

- do not copy its code into a commercial or unrestricted FX product
- do not treat GitHub visibility as an open-source license
- concepts can be studied, but implementation must respect the license and legal constraints

---

# PART XII — GITHUB: `karimkhemkapital/Beta-and-trading-environement`

Source: https://github.com/karimkhemkapital/Beta-and-trading-environement

## 44. Core thesis

The repository treats “operational beta” not as a single CAPM coefficient, but as a stable/executable relation among tickers after real trading constraints are imposed.

The environment constraints explicitly include:

- instrument universe
- broker access
- margin
- borrow
- financing
- liquidity
- bid/ask spread
- slippage
- capital scale
- trading hours
- legal access

This is highly aligned with the desired FX platform philosophy: a statistically attractive relation does not count as an edge unless it survives execution constraints.

## 45. Construction described by the repository

The README describes:

1. executable universe
2. opposing buy/sell baskets
3. point-in-time inverse-volatility weights
4. hedge coordinates on returns and levels
5. causally centered spread residual
6. multi-state support
7. loading/covariance/correlation/cointegration diagnostics
8. regime persistence, transition risk, entropy
9. explicitly costed causal deployment tests

## 46. Important research discipline to absorb

The repository asks a better question than “which rule has the highest Sharpe?”

The project should instead ask:

> Does the relation remain statistically coherent, causal, executable, and positive after realistic costs?

## 47. Evidence/audit pattern worth copying conceptually

The repo separates:

- structural/statistical evidence
- regime evidence
- transition-risk evidence
- costed deployment evidence
- baselines

FX should follow the same audit philosophy with its own independently developed code.

## 48. Purged/out-of-fold validation

The repository references purged/embargoed out-of-fold evidence for transition risk. This concept should be used whenever labels overlap in financial time series.

Implement:

- walk-forward splits
- purging around training/test boundaries
- embargo after training samples where necessary
- no random shuffle for temporal prediction problems

---

# PART XIII — GITHUB: `karimkhemkapital/quantitative-trading-free-lesson`

Source: https://github.com/karimkhemkapital/quantitative-trading-free-lesson

## 49. Curriculum topics visible in the repository

The repository contains a sequence covering:

- introductory quant foundations
- minimal/arbitrage price
- delta neutrality
- Itô’s Lemma
- risk-neutral Black-Scholes pricing
- geometric Brownian motion
- Greeks
- exotic/path-dependent options
- forward rates / no arbitrage
- interest-rate swaps
- volatility in rates products
- volatility surface
- arbitrage-free construction
- local volatility
- Heston stochastic volatility
- jump diffusion
- FX smile dynamics / sticky strike vs sticky delta
- econophysics
- information theory
- entropy
- risk
- hysteresis/path dependence
- Lyapunov concepts
- Markowitz
- CAPM
- Black-Litterman
- APT / multi-factor models
- ARCH/GARCH

## 50. Best use for FX

Use the topic list as a **knowledge roadmap**, not as code to import.

Priority order for the current FX project:

### Immediate

- return/risk foundations
- stationarity
- factor/correlation methods
- ARCH/GARCH
- portfolio optimization
- entropy/regime features

### Next

- stochastic processes
- FX forward / rates relationships
- volatility models
- options smile dynamics

### Later

- advanced derivatives models
- exotic pricing
- full local-vol / Heston calibration

## 51. Licensing warning

The repository states all rights reserved and personal/private/non-commercial educational use only. It explicitly says it is not MIT/open source.

Codex must not scrape/copy its lesson content into the project as distributable training material. Use only high-level topic guidance and independently implemented mathematics from lawful/public references.

---

# PART XIV — DEEPSEEK GITHUB ORGANIZATION

Source: https://github.com/orgs/deepseek-ai/repositories?type=all

## 52. What matters to FX

The DeepSeek organization is primarily an AI/model/infrastructure source, not a trading-strategy repository.

Relevant categories include:

### `deepseek-harness`

The organization page describes it as a plugin-oriented agent harness (“Everything is a Plugin”).

Potential FX lesson:

- modular agent/tool architecture
- plugin boundaries
- interchangeable providers
- separate tools from reasoning layer

Do not restructure FX around it blindly. Study the orchestration pattern and compare with the existing FX harness.

### `DeepSeek-R1`

Reasoning-model family trained with strong RL components and cold-start data.

Potential FX use:

- research assistant
- hypothesis critique
- code review
- strategy memo generation
- model comparison

Do not treat general LLM reasoning as a market edge by itself.

### `DeepSeek-Coder` / Coder variants

Useful as a code-generation/review research option, especially for local/open workflows.

Potential use:

- writing tests
- refactoring research code
- explaining failures
- generating experiment scaffolding

### `DeepSpec`, `DeepGEMM`, `DeepEP`, `FlashMLA`, `TileKernels`, `DualPipe`, etc.

These are primarily inference/training-performance infrastructure.

They matter only if FX later runs sufficiently large local models that inference efficiency becomes a bottleneck. They are **not priority trading features**.

### Integration repositories / curated agent lists

May help discover patterns for tool integration, but third-party integrations must be security-reviewed.

## 53. DeepSeek architecture recommendation for FX

Use an LLM through a provider abstraction:

```text
Agent Interface
  -> Model Router
      -> local Ollama model
      -> DeepSeek-compatible provider
      -> other approved model
  -> Tool Registry
      -> market data
      -> research DB
      -> backtest
      -> risk engine
      -> paper broker
      -> news/macro
      -> reports
```

The model should only receive permissions for tools required for its task.

No LLM should have unrestricted access to credentials, the shell, and an execution broker simultaneously.

---

# PART XV — GOLDMAN SACHS GITHUB

Source: https://github.com/goldmansachs

## 54. Goldman Sachs organization

The organization has many public repositories. Most are enterprise/software projects and are not directly useful for the FX trading engine.

The most relevant pinned repository is:

### `goldmansachs/gs-quant`

Source: https://github.com/goldmansachs/gs-quant

The README describes GS Quant as a Python toolkit for quantitative finance built for strategy development, derivative analysis, data analytics, trading, and risk management.

It is Apache-2.0 licensed.

The public package can be installed with:

```bash
pip install gs-quant
```

However, the README states that access to certain Goldman Sachs APIs requires institutional client credentials (client ID and secret).

## 55. What to absorb from `gs-quant`

Do not assume Goldman’s private data/services are available.

Study the public package for architectural ideas around:

- quantitative data types
- risk representations
- derivatives abstractions
- portfolio/risk calculations
- time-series analytics
- scenario concepts
- clean package modularity
- typed research interfaces

### Recommendation

Use it selectively as a reference or dependency where its Apache-2.0 components provide real value, but avoid making the entire FX project dependent on institutional-only APIs.

The local FX stack should remain capable of operating with open/local market-data sources and paper execution.

---

# PART XVI — REAL-TIME MARKET SENTIMENT + VOLUME / ORDER FLOW

## 56. Required data layer

Build a unified event model with:

```text
MarketEvent
NewsEvent
MacroEvent
QuoteEvent
Trade/TickEvent
BarEvent
SignalEvent
RiskEvent
OrderIntent
PaperFillEvent
ModelDecision
```

## 57. Sentiment engine

Sentiment is not one number.

Store dimensions such as:

- source
- timestamp
- affected assets
- topic
- relevance
- polarity
- surprise
- impact horizon
- confidence
- novelty

Generate aggregated features only after preventing future leakage.

For example, a headline published at 10:03 must never influence a 10:00 bar.

## 58. FX volume reality

Spot FX is decentralized.

Therefore distinguish:

- tick volume
- quoted volume from a specific data provider/venue
- futures volume (e.g. CME, if available)
- broker-specific volume
- global proxy measures

Never label a venue’s quoted volume as “total market volume.”

## 59. Microstructure features from Dukascopy ticks

Potential feature family:

- bid/ask spread
- relative spread
- spread percentile
- quote imbalance
- quoted depth proxy
- quote update intensity
- price impact proxy
- tick arrival intensity
- realized micro-volatility
- session liquidity state
- jump flags
- stale quote flags

Use these primarily for:

- execution quality
- trade gating
- very-short-horizon models

Do not assume they improve swing strategies.

---

# PART XVII — ALPHA STUDIO

## 60. Purpose

The Alpha Studio should answer:

> “How is each asset expected to move **relative to the others**, under the current regime, according to multiple independent models?”

It must not present one deterministic future price.

## 61. Core Alpha Studio panels

### Cross-asset matrix

- expected return score
- momentum score
- carry score
- mean-reversion score
- macro score
- sentiment score
- volatility forecast
- liquidity score
- spread cost
- confidence

### Relative-value matrix

- rolling correlation
- partial correlation
- cointegration diagnostics
- z-score of spread
- dynamic hedge ratio
- PCA/factor exposures

### Regime map

- trend regime
- volatility regime
- liquidity regime
- macro regime
- risk-on/off regime

### Model council

For each symbol:

```text
trend model       -> bullish / neutral / bearish
mean reversion    -> ...
macro             -> ...
order flow        -> ...
ML classifier     -> ...
RL policy         -> ...
risk engine       -> ALLOW / REDUCE / REJECT
```

Disagreement is a feature. Do not force consensus.

---

# PART XVIII — SELF-IMPROVING AGENT: WHAT “SELF-IMPROVING” SHOULD MEAN

## 62. Safe definition

The bot may improve by:

- retraining on a scheduled research cadence
- generating new candidate hypotheses
- testing feature variants
- adjusting calibrated thresholds within bounded ranges
- identifying data-pipeline failures
- comparing challenger vs champion models
- detecting drift

It must **not** autonomously rewrite risk limits, turn on live trading, or deploy an unvalidated model.

## 63. Champion/challenger system

Maintain:

```text
champion model = current approved paper model
challenger models = newly trained candidates
```

Promotion requires:

- clean dataset audit
- reproducible training
- walk-forward OOS pass
- cost stress pass
- regime robustness pass
- risk limits pass
- minimum paper observation period
- no severe operational errors

## 64. Self-healing pipeline

Self-healing means operational resilience, for example:

- reconnect failed data streams
- retry transient requests with backoff
- quarantine corrupt partitions
- switch to secondary data source
- stop paper execution when data is stale
- emit alerts

It must never “heal” by silently filling unknown prices or fabricating data.

---

# PART XIX — VOLATILITY CLUSTERING & TAIL RISK

## 65. Volatility models

Implement progressively:

1. rolling realized volatility
2. EWMA
3. ARCH/GARCH
4. regime-switching volatility
5. optional stochastic-volatility models later

## 66. Tail-risk position sizing

Position size should be constrained by multiple risk estimates:

```text
risk_size = min(
    stop_based_size,
    volatility_based_size,
    expected_shortfall_size,
    liquidity_size,
    portfolio_exposure_size,
    strategy_cap
)
```

This ensures no single model decides notional size.

---

---

# APPENDIX B — EXTERNAL MODEL / HUGGING FACE AUDIT HISTORY

**Codex note:** This appendix preserves previous source-specific analysis. It is a research inventory, not a permission list. The canonical Source Governance policy in Section 14 controls all integration decisions.

# PART X — 2026-09-05 HUGGING FACE MODEL / AGENT AUDIT — ABSORB, EXTRACT, SANDBOX, AVOID

## X.0 Codex instruction for this update

This section supersedes any earlier blanket assumption that a Hugging Face trading model, Space, collection, serialized model file, reported win rate, or paper is automatically suitable for the FX project.

For every external artifact, Codex must classify it into one of four buckets:

- **ABSORB** — architecture or source can be integrated after normal license/security review.
- **EXTRACT IDEAS** — study the design, feature engineering, orchestration, experiments, or documentation, but independently reproduce and validate it.
- **SANDBOX ONLY** — may be tested in an isolated research environment, but must not be allowed to influence automated paper orders until it passes the FX validation pipeline.
- **AVOID** — do not install, deserialize, execute, or route into trading decisions. Preserve only high-level research notes if useful.

### Absolute rule for external model artifacts

Never directly load an untrusted `.pkl`, `.joblib`, PyTorch pickle-backed checkpoint, or similar serialized object into the main FX process merely because it is hosted on Hugging Face or GitHub.

Reasons:

1. Pickle-based formats can execute Python code during deserialization.
2. A model can be statistically invalid even when the file is technically safe.
3. Training preprocessing may be missing, inconsistent, leaked, or impossible to reproduce.
4. Published metrics may be self-reported and may omit costs, leakage checks, walk-forward validation, or realistic execution assumptions.

Preferred order:

1. Read model card / paper / source code.
2. Inspect dataset provenance and license.
3. Reproduce features locally.
4. Re-train from raw data where practical.
5. Prefer `safetensors` for neural-network weights where supported.
6. If a pickle artifact must be inspected, do it only in an isolated disposable environment with no credentials, no broker access, no writable production paths, and no secret environment variables.
7. Never allow an external binary model to bypass FX risk gates.

---

## X.1 `https://huggingface.co/Adilbai/spaces`

### What it is

The Adilbai Spaces page is not itself a trading product. It is a collection of experimental AI Spaces covering agents, MCP, sentiment analysis, computer vision, and classification. At the time reviewed, visible Spaces included:

- Kepler Automated Detection
- TOI NASA Exoplanets Classification
- EuroSAT Crop Classification
- Gemini GAIA Agent
- MCP Client Distributor
- MCP Sentiment Analyzer
- BoneAgePrediction

The creator profile lists interests in NLP, computer vision, reinforcement learning, and LLMs.

### Classification

**EXTRACT IDEAS — LOW/MEDIUM PRIORITY**

### What FX should extract

The most relevant ideas are infrastructure patterns rather than trading alpha:

- Agent orchestration patterns.
- MCP client/server patterns.
- A dedicated sentiment-analysis service as a modular callable tool.
- Separation between an agent UI and specialized backend tools.
- Gradio-style rapid research interfaces for experimenting with a model before integrating it into the main platform.

### What FX should not do

- Do not import all Spaces into FX.
- Do not assume the creator's RL expertise makes unrelated Spaces trading-valid.
- Do not make the MCP sentiment Space a trusted trading signal without independent benchmarking.
- Do not add a Space as a runtime dependency merely because it is publicly accessible.

### Recommended FX adaptation

Implement an internal tool contract such as:

```text
sentiment_service.analyze(text, source, timestamp, asset_candidates)
    -> {
         sentiment_label,
         sentiment_score,
         confidence,
         relevance,
         entities,
         event_type,
         novelty_score,
         source_quality
       }
```

This service should be swappable: Trading-Hero/FinBERT, a local LLM, or another classifier can compete behind the same interface.

---

## X.2 `https://huggingface.co/fuchenru/Trading-Hero-LLM`

### Reality check

Despite the name **Trading-Hero-LLM**, this is not a general-purpose trading LLM and not an autonomous trading agent.

It is a **BERT/FinBERT-derived financial sentiment text-classification model** with three labels:

- `0 = neutral`
- `1 = positive`
- `2 = negative`

The model card describes it as a fine-tuned FinBERT model for financial communications. The listed pretraining corpus for FinBERT includes corporate reports, earnings-call transcripts, and analyst reports. The model card reports approximately:

- Accuracy: 0.908469
- Precision: 0.927788
- Recall: 0.908469
- F1: 0.913267

License shown: MIT.

### Classification

**ABSORB AS A SENTIMENT CANDIDATE — NEVER AS A TRADER**

### High-value use in FX

Use it as one member of the **Sentiment Engine**, for example:

```text
NEWS / TRANSCRIPT / FILING
        ↓
entity recognition
        ↓
asset mapping
        ↓
Trading-Hero sentiment
        ↓
positive / neutral / negative + confidence
        ↓
relevance × novelty × source-quality weighting
        ↓
asset-level sentiment factor
```

### Improvements required before use

Raw positive/negative classification is not enough. FX should add:

1. **Asset/entity resolution** — identify which ticker, currency, commodity, company, or macro factor the text applies to.
2. **Event classification** — earnings, guidance, M&A, legal, macro, central bank, geopolitical, product, analyst action, etc.
3. **Novelty detection** — repeated headlines must not count as independent confirmations.
4. **Source reliability weighting**.
5. **Time decay** — sentiment should decay based on event type and market horizon.
6. **Price-reaction normalization** — once price has fully reacted, the same headline should not remain a fresh alpha signal.
7. **Contradiction aggregation** — allow multiple sources and models to disagree.
8. **Calibration** — convert model confidence into empirically calibrated probabilities.

### FX rule

Sentiment must be a **feature**, not a direct BUY/SELL command.

A positive headline must never automatically create an order.

---

## X.3 `https://huggingface.co/JonusNattapong/xauusd-trading-ai-smc-v2`

### What the source provides

This repository/model card provides a multi-timeframe XGBoost-centered trading research project marketed for XAUUSD/Gold with Smart Money Concepts (SMC).

Documented model artifacts include:

- Daily XGBoost model.
- 15-minute model.
- Partially trained 1-minute model.
- 30-minute model described as ready for training.
- Training and backtesting scripts.
- Feature-importance output.
- Historical datasets.
- Research/whitepaper documents.

The documented feature set contains classic technical and SMC-style features, including:

- OHLCV
- SMA 20 / SMA 50
- EMA 12 / EMA 26
- RSI
- MACD, signal, histogram
- Bollinger Bands
- Fair Value Gap size/type
- Order Block type
- recovery-pattern type
- lagged close values

The model card states a 5-day direction target for the daily setup and reports self-reported test/backtest figures including 80.3% classification accuracy and an 85.4% backtest win rate.

### Critical weaknesses

The model card itself acknowledges:

- historical training data only;
- possible failure in unprecedented regimes;
- no transaction costs;
- no slippage;
- no market-impact modeling.

Additional FX concerns:

1. The card describes XAUUSD while the documented training source is Yahoo Finance `GC=F` Gold Futures. Spot XAUUSD and COMEX gold futures are strongly related but are not identical instruments. Basis, session liquidity, rollover, exchange mechanics, and volume semantics differ.
2. The daily training period is stated as 2000–2020. That is stale for deployment in 2026 without retraining.
3. Intraday samples listed are small by institutional standards: approximately 5,204 one-minute samples, 3,814 fifteen-minute samples, and 1,910 thirty-minute samples.
4. Three-fold cross-validation is not sufficient evidence for financial time-series robustness unless it is explicitly time-ordered / purged / embargoed.
5. A high "win rate" is meaningless without payoff distribution, average win/loss, costs, drawdown, exposure, turnover, and tail behavior.
6. SMC features must be defined deterministically. Terms such as order block and fair value gap can otherwise become subjective or leak future information.

### Classification

**EXTRACT IDEAS + REBUILD LOCALLY — DO NOT TRUST THE PRETRAINED MODEL**

### What FX should absorb

- Multi-timeframe feature pipeline.
- Feature registry for deterministic SMC constructs.
- Feature importance reports.
- XGBoost as one candidate model.
- Separate train / backtest / summary tools.
- Direction probabilities rather than hard labels.

### What FX should reject or rewrite

- Do not treat the reported win rate as evidence of edge.
- Do not use the stale pretrained weights for autonomous paper trading.
- Do not equate GC=F training results with XAUUSD spot execution.
- Do not use random shuffled CV.
- Do not omit spread/slippage.
- Do not call a one-minute strategy HFT unless the infrastructure, data, latency, and execution truly qualify.

### Required FX reproduction experiment

Recreate the strategy using the FX project's own data:

```text
Experiment XAU-SMC-XGB-001

Assets:
- XAUUSD spot if reliable bid/ask source is available
- GC futures as a separate comparison instrument

Data:
- train / validation / test strictly chronological
- bid/ask-aware where available

Models:
- Logistic Regression baseline
- XGBoost
- LightGBM

Feature groups:
A. price/return
B. volatility
C. trend/momentum
D. volume/order-flow where instrument-appropriate
E. deterministic SMC
F. cross-asset macro factors

Validation:
- anchored walk-forward
- rolling walk-forward
- purged time-series CV where labels overlap
- multiple market regimes

Costs:
- spread
- slippage
- commission/fees where relevant
- latency assumption

Outputs:
- CAGR / total return
- Sharpe / Sortino
- max drawdown
- Calmar
- turnover
- win rate
- payoff ratio
- profit factor
- expected value/trade
- exposure
- tail loss
- stability by year/regime
```

---

## X.4 `https://huggingface.co/papers/2412.20138` — TradingAgents

### Paper

**TradingAgents: Multi-Agents LLM Financial Trading Framework** proposes an LLM-driven architecture modeled after a real trading organization.

Documented specialist roles include:

- fundamental analyst;
- sentiment analyst;
- technical analyst;
- bull researcher;
- bear researcher;
- traders with differing risk profiles;
- risk-management team;
- decision synthesis using debate plus historical information.

The framework reports stronger experimental performance than its baselines on cumulative return, Sharpe ratio, and maximum drawdown.

### Classification

**STRONGLY ABSORB THE ORCHESTRATION PATTERN — DO NOT GIVE LLMs EXECUTION SOVEREIGNTY**

### Direct mapping to the FX Model Council

FX should implement roles similar to:

```text
Market Data Agent
Macro Agent
Fundamental Agent
Technical Agent
Sentiment / News Agent
Order-Flow Agent
Cross-Asset Agent
Bull Thesis Agent
Bear Thesis Agent
Regime Agent
Risk Agent
Execution-Cost Agent
Portfolio Agent

                ↓
          Debate / evidence
                ↓
       Deterministic aggregator
                ↓
          Risk policy engine
                ↓
          Paper execution
```

### Critical architecture rule

The final decision must not be an unrestricted LLM string such as `BUY AAPL`.

Instead agents should emit structured evidence:

```json
{
  "asset": "EURUSD",
  "horizon": "4h",
  "direction": "long",
  "confidence": 0.64,
  "evidence_ids": ["..."],
  "features": {"...": 0.0},
  "risk_flags": [],
  "invalidation": "...",
  "timestamp": "..."
}
```

Then a deterministic controller checks:

- data freshness;
- position limits;
- portfolio correlation;
- max loss;
- stop placement;
- expected transaction cost;
- execution liquidity;
- regime restrictions;
- model calibration;
- signal disagreement;
- kill-switch state.

### FX recommendation

TradingAgents is one of the most useful sources in this batch for **agent design**, but not proof that LLM debate itself creates durable alpha.

---

## X.5 `https://huggingface.co/add54/agentic-trading-model`

### What it is

This is a PEFT/LoRA adapter based on `TinyLlama/TinyLlama-1.1B-Chat-v1.0`, trained with supervised fine-tuning (SFT) using TRL/Transformers/PEFT.

The model card provides framework versions and basic loading examples, but it does not provide convincing trading-specific evaluation, audited trading data lineage, cost-aware backtesting, or evidence that the resulting model can generate profitable or risk-controlled trading decisions.

### Classification

**SANDBOX ONLY / LOW PRIORITY**

### Potential value

Use only to study:

- PEFT / LoRA fine-tuning mechanics;
- how a small local model could be adapted to an FX-specific vocabulary;
- local inference plumbing;
- structured-output fine-tuning experiments.

### What not to absorb

- Do not treat it as a trained trading brain.
- Do not use it as the final signal model.
- Do not let its natural-language output directly generate paper orders.
- Do not spend major compute optimizing it until the deterministic research stack is already strong.

### Better use of fine-tuning inside FX

Fine-tune a small local model for **workflow tasks**, not price prophecy:

- classify research requests;
- convert analyst notes to structured schema;
- tag catalysts;
- map entities to assets;
- summarize model disagreements;
- explain risk-engine rejections;
- produce post-trade reports.

This creates operational value without pretending that text generation is a reliable alpha oracle.

---

## X.6 `https://huggingface.co/AdityaaXD/Multi-Model-AI-Trading-Bot`

### Architecture

This project combines eight models:

Traditional ML:

- Logistic Regression
- Random Forest
- XGBoost

Deep learning:

- LSTM
- GRU
- CNN
- LSTM + Attention
- Transformer

It uses majority-vote ensembling.

Documented features are ten technical indicators/features including RSI, MACD, Bollinger Band width, ATR, SMA50 distance, OBV percent change, ADX, and Stochastic RSI K/D.

It also provides SHAP values for explainability.

The documented dataset is BTC-USD daily data from 2015-01-01 to 2025-01-01, approximately 3,600 daily samples with an 80/20 train/test split.

The model card explicitly says it is for educational/research purposes and should not be used for actual trading decisions.

### Classification

**EXTRACT ENSEMBLE + EXPLAINABILITY IDEAS; REBUILD EVERYTHING**

### Useful concepts

- Heterogeneous ensemble council.
- Compare linear, tree, recurrent, convolutional, and transformer families under the same feature/label definition.
- SHAP / feature attribution.
- Early stopping, gradient clipping, class balancing.
- Store preprocessing configuration with the experiment.

### Serious research concerns

1. Roughly 3,600 daily observations are very limited for simultaneously comparing/tuning eight model families, especially deep neural networks.
2. An 80/20 split alone is not enough for robust time-series model selection.
3. Majority voting assumes each model deserves equal weight and ignores calibration and correlated errors.
4. Many models trained on the same ten technical features may create the illusion of diversity while sharing the same information bottleneck.
5. No production-grade trading metrics are documented on the model card.
6. `.pkl` artifacts are serialization security risks if loaded blindly.

### Better FX ensemble

Do not use raw majority vote. Use an **out-of-sample calibrated ensemble**:

```text
Each model outputs P(up), P(flat), P(down) or expected return distribution
                    ↓
walk-forward calibration
                    ↓
model reliability by regime
                    ↓
correlation-of-errors penalty
                    ↓
weighted ensemble / stacking
                    ↓
uncertainty estimate
                    ↓
risk gate
```

Suggested weighting inputs:

- recent OOS information coefficient;
- Brier score / calibration error;
- regime-specific Sharpe after costs;
- drawdown contribution;
- signal correlation with other models;
- turnover/cost burden;
- feature drift;
- prediction entropy.

### Security note on `xgboost.pkl`

The user specifically supplied a blame link to `xgboost.pkl`.

Do **not** treat the pickle as source code to absorb.

Codex should preferably reproduce the XGBoost model from:

- documented features;
- documented target;
- raw training data;
- hyperparameters if available;
- deterministic training seed;
- local XGBoost version.

If binary inspection is required, do so in an isolated environment only.

---

## X.7 `https://huggingface.co/collections/LilSand/trading-ai`

### What it is

This is a discovery collection, not a validated benchmark or curated safety list.

At review time it linked to a heterogeneous set of assets including:

- reinforcement-learning trading projects;
- Bitcoin-focused language models;
- XAUUSD trading models;
- ensemble trading AI;
- crypto datasets;
- financial-news datasets;
- backtesting datasets;
- price time-series datasets;
- crypto/stock tweet datasets.

### Classification

**DISCOVERY INDEX ONLY**

### Codex rule

Membership in the collection provides **zero trust inheritance**.

Every child resource must independently pass:

1. license check;
2. provenance check;
3. malware / serialization review;
4. dataset leakage review;
5. label-definition review;
6. train/test chronology review;
7. realistic cost-model review;
8. reproducibility review;
9. OOS robustness review;
10. relevance to FX project's supported asset/timeframe.

### What is potentially useful

Use the collection as a recurring research queue for:

- datasets;
- alternative data;
- new architecture candidates;
- backtesting examples;
- sentiment sources.

Do not clone the collection wholesale.

---

# PART XI — SOURCE PRIORITY MATRIX

| Source | Decision | FX value | Main reason |
|---|---|---:|---|
| TradingAgents paper | **ABSORB ARCHITECTURE** | Very High | Excellent Model Council / specialist-agent pattern |
| Trading-Hero-LLM | **ABSORB AS SENTIMENT CANDIDATE** | High | Financial-domain sentiment classifier; useful feature generator |
| XAUUSD SMC v2 | **EXTRACT + RETRAIN** | High | Useful multi-timeframe XGBoost/SMC research scaffold, but stale/self-reported/cost-free |
| Multi-Model AI Trading Bot | **EXTRACT + RETRAIN** | Medium-High | Useful heterogeneous ensemble + SHAP pattern, weak dataset/validation evidence |
| Adilbai Spaces | **EXTRACT INFRA IDEAS** | Medium | MCP/agent/sentiment service patterns rather than trading edge |
| add54 agentic-trading-model | **SANDBOX ONLY** | Low-Medium | LoRA/PEFT plumbing useful; little evidence of actual trading competence |
| LilSand Trading AI collection | **DISCOVERY ONLY** | Medium | Useful source index; no inherent quality guarantee |
| External `.pkl`/pickle artifacts | **AVOID DIRECT LOAD** | Low | Security + reproducibility + validation risk |

---

# PART XII — WHAT THIS CHANGES IN THE FX ARCHITECTURE

## XII.1 Sentiment becomes a first-class feature service

Build:

```text
services/sentiment/
    interfaces.py
    entity_resolution.py
    event_classifier.py
    trading_hero_adapter.py
    llm_adapter.py
    ensemble.py
    calibration.py
    novelty.py
    source_quality.py
    tests/
```

Never store only a label. Persist:

```text
raw_text_hash
source
timestamp
publication_timestamp
retrieval_timestamp
entities
asset_map
event_type
sentiment_label
sentiment_probability
relevance
novelty
source_quality
model_version
feature_version
```

## XII.2 Model Council becomes role-based, evidence-based, and machine-readable

Add or formalize:

```text
agents/
    market_data_agent
    macro_agent
    technical_agent
    fundamental_agent
    sentiment_agent
    orderflow_agent
    regime_agent
    bull_agent
    bear_agent
    risk_agent
    execution_agent
    portfolio_agent
```

LLM agents can debate and explain. They cannot change risk limits.

## XII.3 Model Zoo / Challenger framework

Instead of searching for one "best bot," FX should maintain a champion/challenger system:

```text
Linear baseline
Decision Tree
Random Forest
XGBoost
LightGBM
LASSO / Elastic Net
Temporal CNN
LSTM / GRU
Transformer / TFT candidate
RL candidate
Rule-based strategies
```

Every candidate competes under the exact same:

- chronological data splits;
- cost assumptions;
- metrics;
- position-sizing rules;
- paper execution simulator;
- experiment registry.

A complex model is promoted only if it beats simple baselines after costs and across regimes.

## XII.4 No equal majority vote by default

The ensemble layer should learn model weights only from **out-of-sample** behavior.

The system should be allowed to say:

```text
NO TRADE
```

when:

- ensemble confidence is weak;
- agents strongly disagree;
- expected edge is smaller than expected cost;
- data is stale;
- spread is abnormal;
- volatility regime is unsupported;
- portfolio risk budget is exhausted;
- feature drift is detected.

## XII.5 SMC becomes deterministic research features, not discretionary mythology

If FX uses concepts such as:

- Fair Value Gaps;
- Order Blocks;
- liquidity sweeps;
- structure breaks;
- recovery patterns;

then each term must have an exact algorithmic definition, unit tests, and no-lookahead proof.

Example:

```text
FVG_UP(t) = Low[t] > High[t-2]
```

is auditable.

"There appears to be institutional demand here" is not.

## XII.6 Binary safety boundary around external models

Create an explicit source-ingestion policy:

```text
external_source_status:
    discovered
    metadata_reviewed
    license_reviewed
    code_reviewed
    data_reviewed
    reproduced
    benchmarked
    sandbox_approved
    paper_signal_approved
    rejected
```

No resource may jump directly from `discovered` to `paper_signal_approved`.

---

# PART XIII — CODEX IMPLEMENTATION TASKS CREATED BY THIS UPDATE

## P0 — Security / source governance

- Add an `EXTERNAL_SOURCES.md` or source registry inside the FX project.
- Record URL, license, commit/revision, artifact type, security status, and decision.
- Block direct use of downloaded pickle/joblib artifacts by default.
- Add a quarantine directory excluded from normal runtime imports.

Suggested layout:

```text
research/external/
    registry.yaml
    notes/
    quarantine/
```

## P1 — Trading-Hero sentiment benchmark

Benchmark `fuchenru/Trading-Hero-LLM` against at least:

- FinBERT baseline;
- a zero/few-shot local LLM classification prompt;
- optionally another modern finance sentiment classifier.

Evaluate on FX-relevant text, not just generic equity headlines.

Include:

- central-bank statements;
- CPI/jobs releases;
- geopolitical headlines;
- commodity headlines;
- company-specific equity news;
- crypto regulatory/news events.

Measure:

- accuracy / macro F1 on labeled test data;
- calibration;
- latency;
- memory footprint;
- disagreement by event type.

## P2 — XAUUSD SMC independent reproduction

Rebuild the feature set locally and run the experiment specified in X.3.

Do not download-and-trust the existing model as the primary route.

## P3 — Ensemble lab

Implement a shared prediction schema across Logistic Regression, RF, XGBoost, LightGBM, LSTM/GRU, and selected transformer candidates.

Start with simpler models first.

## P4 — TradingAgents-inspired council

Refactor the existing Model Council toward specialized roles with structured outputs, evidence IDs, confidence, and explicit disagreement.

## P5 — Explainability

Add:

- SHAP for tree models;
- permutation importance;
- feature drift;
- model calibration charts;
- prediction attribution history.

Explainability is diagnostic, not proof of causality.

## P6 — Paper-only promotion gates

A model can influence paper orders only after:

```text
PASS data quality
PASS no-lookahead tests
PASS chronological OOS testing
PASS realistic costs
PASS stress tests
PASS regime breakdown
PASS reproducibility
PASS security review
PASS risk-engine integration
```

Even then, initial capital allocation should be tiny in simulation/paper mode.

---

# PART XIV — FINAL DECISION FOR CODEX

Do **not** attempt to make FX powerful by installing every AI trading model found online.

The better strategy is:

1. **Absorb architecture.**
2. **Absorb datasets when licensed and clean.**
3. **Reproduce useful features.**
4. **Retrain locally.**
5. **Validate independently.**
6. **Ensemble only validated challengers.**
7. **Let deterministic risk code dominate every model.**
8. **Paper trade first.**
9. **Measure whether the edge survives spread, slippage, latency, and regime change.**
10. **Reject attractive models aggressively when evidence is weak.**

The FX project should behave like an automated quantitative research desk, not like a model-download collection.

# PART XV — HUGGING FACE AUDIT ROUND 3

Updated: 2026-09-05

This section audits the newest Hugging Face links supplied for FX.

The rule for external trading resources is:

> Extract useful data, architecture, features, validation patterns, and engineering ideas. Never assume that a downloadable trading model is profitable, safe, secure, or production-ready. Reproduce and validate locally before it can influence paper trading.

Classification vocabulary:

- **ABSORB** — useful enough to integrate as research data or a first-party implementation pattern.
- **EXTRACT / REBUILD** — retain the ideas, but recreate/retrain locally.
- **SANDBOX ONLY** — experimental reference only.
- **AVOID / QUARANTINE** — do not install, load, or treat as evidence of trading edge.

---

## XV.1 Executive decisions

| Source | Decision | Get / absorb | Avoid |
|---|---|---|---|
| `quantumaiapp/QuantumAI` | **AVOID / QUARANTINE** | Nothing required for the primary FX stack | Promotional and unverifiable “quantum AI trading” claims |
| `jalvart/bitcoin-tick-level-trade-data-free-sample` | **ABSORB FOR RESEARCH** | Tick data, aggressor flow, OFI, VWAP, realized volatility, microstructure tests | Commercial redistribution; treating one week as proof of durable alpha |
| `AdityaaXD/Multi-Model-AI-Trading-Bot` | **EXTRACT / REBUILD** | Cross-model benchmarking, ensembles, SHAP, ML/DL challengers | Blind loading of `.pt`, `.pkl`, `.joblib` artifacts |
| `JonusNattapong/romeo-v8-super-ensemble-trading-ai` | **EXTRACT / REBUILD** | Calibration, stacking, dynamic weighting, heterogeneous learners | Trusting published Sharpe/returns without independent reproduction |
| `john3huggingface/com-trading-bot` | **LOW-VALUE EXTRACT / OTHERWISE AVOID** | Very basic external-price API/UI pattern | Treating it as a trading system |
| `JonusNattapong/xauusd-trading-ai-smc-v2` | **EXTRACT / REBUILD — PREVIOUS DECISION CONFIRMED** | SMC feature engineering, multi-timeframe scaffolding, XGBoost workflow | Remote serialized models and headline metrics |

---

# XV.2 quantumaiapp/QuantumAI

Source:
`https://huggingface.co/quantumaiapp/QuantumAI`

## Decision

**AVOID / QUARANTINE**

## What the page contains

The page is principally promotional copy for a product called “Quantum AI Trading App.” It claims AI, sophisticated algorithms, cryptocurrency trading, real-time analysis, entries/exits, security, broker relationships, and “quantum computing.”

What is materially missing for an FX research source:

- reproducible model architecture;
- source code proving the claimed quantum implementation;
- training dataset;
- feature definitions;
- chronological train/validation/test design;
- walk-forward analysis;
- slippage model;
- transaction-cost model;
- market-impact model;
- independent benchmark;
- independently audited performance;
- model provenance;
- convincing scientific evidence connecting the marketing claim to an actual quantum trading algorithm.

The page also presents a Hugging Face metadata warning for missing/empty YAML metadata.

## Codex instruction

Do not:

```text
clone for FX production
load any artifact from it
treat it as an alpha source
use its marketing statements as facts
let its claims enter prompts as quantitative evidence
```

Add it to the quarantine registry:

```yaml
source_id: hf_quantumaiapp_quantumai
url: https://huggingface.co/quantumaiapp/QuantumAI
classification: avoid
allow_download: false
allow_deserialize: false
allow_signal_use: false
reason:
  - promotional content
  - insufficient reproducibility
  - unverifiable quantum-trading claims
  - no credible independent trading evaluation
```

Principle:

```text
MARKETING CLAIM
!= REPRODUCIBLE MODEL
!= VALIDATED EDGE
!= SAFE EXECUTION SYSTEM
```

---

# XV.3 jalvart/bitcoin-tick-level-trade-data-free-sample

Source:
`https://huggingface.co/datasets/jalvart/bitcoin-tick-level-trade-data-free-sample`

## Decision

**ABSORB FOR LOCAL RESEARCH**

This is the strongest new resource in this batch.

## Verified characteristics from the dataset card

Free BTC/USDT trade-level sample:

```text
Period: 2025-02-19 -> 2025-02-26
Rows: ~27.9 million
Format: Apache Parquet, ZSTD
```

Published columns include:

```text
exchange
symbol
trade_id
exchange_ts
ingest_ts
price
quantity
aggressor_side
raw_side
```

The dataset card describes the sample as audited, non-synthetic, and timestamp-normalized.

## What FX should build from it

### Order-flow imbalance

For a rolling interval:

```text
signed_volume_i = quantity_i * aggressor_side_i

OFI_t = SUM(signed_volume_i)
```

Normalized variant:

```text
normalized_OFI =
(buy_volume - sell_volume)
/
(buy_volume + sell_volume)
```

### VWAP

```text
VWAP =
SUM(price_i * quantity_i)
/
SUM(quantity_i)
```

Use it for:

- execution-quality studies;
- intraday fair-value references;
- distance-from-VWAP features;
- mean-reversion research.

### Realized volatility

```text
r_i = ln(P_i / P_(i-1))
RV = SUM(r_i^2)
```

Aggregate into multiple windows:

```text
1m
5m
15m
1h
24h
```

### Trade intensity

Calculate:

```text
trades_per_second
trades_per_minute
volume_per_second
notional_per_second
```

### Aggressor-flow features

```text
buy_taker_volume
sell_taker_volume
net_taker_volume
buy_trade_count
sell_trade_count
average_buy_trade_size
average_sell_trade_size
buy_ratio
sell_ratio
aggressor_flip_rate
```

### Additional microstructure features

```text
price_return_1s
price_return_5s
price_return_30s
price_return_1m
rolling_ofi
ofi_zscore
trade_intensity
notional_intensity
vwap_distance
rolling_vwap
realized_volatility
volatility_of_volatility
average_trade_size
large_trade_ratio
burstiness
interarrival_time
```

## Important limitation

The free sample is roughly one week.

Good uses:

```text
pipeline development
schema validation
feature engineering
performance tests
microstructure studies
execution-simulation prototypes
```

Bad inference:

```text
one-week profitable result
=> durable strategy
```

Do not make that leap.

## License rule

The dataset card states personal research/trading-bot development use and prohibits commercial redistribution, resale, and public API deployment.

Track that restriction explicitly.

Suggested registry:

```yaml
source_id: hf_jalvart_btc_ticks_sample
classification: research_data
license: theglitchlist-personal-use
paper_research: true
commercial_redistribution: false
public_api_distribution: false
```

## Recommended first-party module

```text
fx/data/microstructure/
    tick_loader.py
    trade_normalizer.py
    aggressor_flow.py
    vwap.py
    realized_volatility.py
    trade_intensity.py
    microstructure_features.py
```

Tests must detect:

```text
future leakage
duplicate trade IDs
timestamp-unit mistakes
bad aggressor-side conversion
lookahead aggregation
```

---

# XV.4 AdityaaXD/Multi-Model-AI-Trading-Bot

Source:
`https://huggingface.co/AdityaaXD/Multi-Model-AI-Trading-Bot`

## Decision

**EXTRACT / REBUILD**

Already reviewed earlier. Current audit adds security detail.

## Useful architecture

Candidate families include:

```text
Logistic Regression
Random Forest
XGBoost
LSTM
GRU
CNN
LSTM + Attention
Transformer
```

The valuable lesson is not “more models = more edge.”

The useful design is:

> put materially different model families behind one standardized chronological validation and prediction interface.

Recommended interface:

```python
class AlphaModel:
    fit(...)
    predict(...)
    predict_proba(...)
    explain(...)
    save_safe(...)
    load_safe(...)
```

Standard output:

```json
{
  "asset": "BTCUSDT",
  "timestamp": "...",
  "horizon": "15m",
  "p_up": 0.57,
  "p_down": 0.43,
  "confidence": 0.14,
  "model_id": "...",
  "model_version": "...",
  "feature_version": "..."
}
```

## Artifact-security rule

The repository contains serialized PyTorch artifacts; Hugging Face surfaces pickle imports in at least one `.pt` artifact.

Therefore:

```text
DO NOT torch.load() remote artifacts blindly
DO NOT joblib.load() untrusted files
DO NOT pickle.load() external trading models
```

Prefer local reconstruction and retraining.

Where suitable, prefer safer persistence approaches such as:

```text
safetensors
JSON/YAML config
ONNX
XGBoost JSON/UBJ
LightGBM text
reviewed Skops
```

No format removes the need for source validation.

## Ensemble rule

Do not finish with simple equal-vote majority.

Prefer:

```text
probability calibration
+ chronological OOS scoring
+ regime-conditioned weights
+ prediction-correlation penalty
+ confidence threshold
+ deterministic risk veto
```

---

# XV.5 JonusNattapong/romeo-v8-super-ensemble-trading-ai

Source:
`https://huggingface.co/JonusNattapong/romeo-v8-super-ensemble-trading-ai`

## Decision

**EXTRACT / REBUILD**

This source contains useful ensemble architecture ideas.

## Published architecture

The model card describes:

```text
XGBoost
LightGBM
CatBoost
RandomForest
ExtraTrees
Neural Networks
SVM
KNN
Logistic Regression
Naive Bayes
```

The system then applies:

```text
base learners
-> confidence calibration
-> stacking meta-learner
-> dynamic weighting
-> cross-validation ensemble
```

The source specifically describes isotonic calibration and Logistic Regression stacking.

## What FX should absorb

### Probability calibration

A claimed probability should correspond to empirical frequency.

Evaluate:

```text
Brier score
log loss
reliability diagram
ECE
calibration slope
calibration intercept
```

Possible calibrators:

```text
sigmoid / Platt
isotonic regression
beta calibration
```

Calibration must be trained chronologically and without leakage.

### Time-series stacking

Never train the stacker on in-sample base-model predictions.

Use chronological out-of-fold predictions:

```text
Fold 1:
train 2018-2020
validate 2021

Fold 2:
train 2018-2021
validate 2022

Fold 3:
train 2018-2022
validate 2023
```

Then concatenate only validation predictions to train the meta-model.

### Dynamic weighting

Useful inputs:

```text
recent OOS log loss
recent Brier score
rolling information coefficient
net Sharpe
regime-specific hit rate
calibration drift
feature drift
prediction correlation
turnover
execution-cost sensitivity
```

Conceptual form:

```text
raw_weight_m = exp(-lambda * recent_loss_m)

adjusted_weight_m =
raw_weight_m
* regime_relevance_m
* calibration_quality_m
* independence_score_m
```

Normalize across eligible models.

Avoid rapid “winner chasing.”

### Diversity

Track:

```text
prediction correlation
error correlation
feature-family overlap
```

Ten models that all rediscover the same moving-average signal are not truly diversified.

## Published metrics: do not trust without reproduction

The model card reports approximately:

```text
Win Rate:      68.18%
Profit Factor: 2.16
Sharpe Ratio:  4.64
Max Drawdown:  11.06%
Total Return:  26.81%
Total Trades:  66
```

These are source-reported.

The key problem is:

```text
66 trades
```

That is too little evidence for FX to accept a reported Sharpe of 4.64 as a durable edge.

Correct response:

```text
interesting metric
-> reproduce
-> increase sample size
-> walk-forward
-> stress costs
-> regime test
-> bootstrap
-> decide
```

Not:

```text
high Sharpe
-> install
```

## “Quantum-inspired” features

The model card references:

```text
entropy
phase-space analysis
amplitude modulation
wavelet energy
fractal dimension
```

These can be legitimate transforms, but “quantum-inspired” adds no credibility.

Every feature must independently pass:

```text
economic rationale
no-lookahead test
stability analysis
IC / mutual-information analysis
ablation
OOS contribution
cost-adjusted contribution
regime analysis
```

## Recommended local challenger

Start smaller than the source.

```text
Logistic Regression
Random Forest
ExtraTrees
XGBoost
LightGBM
```

Then compare:

```text
best single model
simple mean
calibrated mean
static weighted ensemble
stacking
dynamic weighted stacking
```

Only add CatBoost or sequence models if the simpler challenger earns the complexity.

## Artifact security

Do not load remote joblib/pickle model files into the primary FX environment.

Reconstruct from documented architecture and retrain locally.

---

# XV.6 john3huggingface/com-trading-bot

Source:
`https://huggingface.co/john3huggingface/com-trading-bot`

## Decision

**LOW-VALUE EXTRACT / OTHERWISE AVOID**

## What it actually is

The visible code is essentially:

```text
Gradio input
-> CoinGecko simple-price REST request
-> current USD crypto price
-> text output
```

It is a price checker, not a serious trading bot.

The inspected source does not establish:

```text
alpha generation
risk engine
portfolio construction
position sizing
stop loss
take profit
execution engine
order management
backtesting
feature engineering
strategy validation
```

Do not add it to the FX model zoo.

## Tiny useful pattern

It demonstrates a minimal:

```text
UI
-> external data API
-> normalized output
```

FX should implement a much stronger native connector:

```text
connector
-> retries/backoff
-> schema validation
-> timestamp normalization
-> stale-data detection
-> source attribution
-> cache
-> rate-limit management
-> normalized market-data object
```

If CoinGecko is needed, implement it directly from official API documentation rather than cloning this repo.

---

# XV.7 JonusNattapong/xauusd-trading-ai-smc-v2

Source:
`https://huggingface.co/JonusNattapong/xauusd-trading-ai-smc-v2`

## Decision

**EXTRACT / REBUILD — PREVIOUS DECISION CONFIRMED**

Current review confirms the useful pieces:

```text
XGBoost
23-feature SMC + technical feature set
1m / 15m / 30m / daily workflows
feature importance
training scripts
backtesting scripts
multi-timeframe scaffolding
dynamic thresholds
risk-metric calculations
```

The source also acknowledges limitations including transaction costs, slippage, and market impact in its published analysis, and the performance values shown on the model card are self-reported.

## Updated security instruction

The repo advertises `joblib` loading.

Do not use that as the FX integration route.

Use:

```text
feature definitions
training logic
hyperparameter ideas
SMC definitions
backtesting structure
```

as references and recreate locally.

## Required SMC ablation

Test feature families separately:

```text
BASE:
OHLCV + returns

TECHNICAL:
SMA
EMA
RSI
MACD
Bollinger
ATR where applicable

SMC:
FVG
Order Blocks
Recovery structures

LAGS:
close_lag1
close_lag2
close_lag3
```

Run:

```text
BASE
BASE + TECHNICAL
BASE + SMC
BASE + LAGS
BASE + TECHNICAL + SMC
ALL
```

SMC only stays if it adds independent out-of-sample value.

---

# XV.8 Alpha Studio architecture update

The strongest ideas from the new and prior audits should converge into:

```text
RAW MARKET DATA
OHLCV / ticks / book / news
        |
DATA QUALITY GATE
        |
+----------------------+----------------------+----------------------+
| MICROSTRUCTURE       | TECHNICAL / SMC      | MACRO / SENTIMENT    |
| OFI / VWAP / RV      | engineered features | engineered features  |
+----------------------+----------------------+----------------------+
        |
FEATURE STORE
        |
+----------------------+----------------------+----------------------+
| TREE MODELS          | LINEAR MODELS        | SEQUENCE MODELS      |
| XGB/LGB/RF/ET        | LOGIT/LASSO          | GRU/LSTM optional    |
+----------------------+----------------------+----------------------+
        |
PROBABILITY CALIBRATION
        |
MODEL HEALTH / DRIFT
        |
STACKING / DIVERSITY-AWARE ENSEMBLE
        |
MODEL COUNCIL
(advisory)
        |
DETERMINISTIC RISK ENGINE
(sovereign veto)
        |
PAPER EXECUTION
```

The Model Council is never the final authority on risk.

---

# XV.9 External artifact security policy

Treat external model artifacts as untrusted by default.

High-risk extensions include:

```text
.pkl
.pickle
.joblib
.pt
.pth
.ckpt
```

Default policy:

```text
ALLOW_INSPECT = true
ALLOW_EXECUTE = false
ALLOW_DESERIALIZE = false
ALLOW_PAPER_SIGNAL = false
ALLOW_LIVE_SIGNAL = false
```

Promotion requires:

```text
source recorded
revision recorded
hash recorded
license reviewed
dependencies reviewed
artifact inspected
training provenance understood
evaluation independently reproduced
```

External repositories must never automatically:

```text
launch brokers
place orders
read secrets
read API keys
open persistent sockets
modify shell profiles
schedule jobs
write outside quarantine
```

Recommended directory:

```text
research/
  external_sources/
    quarantine/
    inspected/
    reproduced/
```

Only reproduced first-party code can move into the main FX modules.

---

# XV.10 Source/license registry

Maintain:

```text
config/source_registry.yaml
```

Fields:

```yaml
id:
url:
publisher:
type:
license:
commercial_use:
redistribution:
derivatives:
attribution_required:
downloaded_at:
revision:
sha256:
security_status:
validation_status:
approved_use:
notes:
```

Unknown licensing must block automatic reuse.

---

# XV.11 Implementation priorities from this audit

## P0 — External-source quarantine

Implement security and licensing controls before importing more model artifacts.

## P1 — BTC tick microstructure lab

Build:

```text
tick ingestion
aggressor flow
OFI
VWAP
realized volatility
trade intensity
latency/timestamp diagnostics
```

## P2 — Microstructure predictive tests

Measure feature value at:

```text
1s
5s
30s
1m
5m
15m
```

with chronological splits.

## P3 — Calibrated ensemble prototype

Reproduce locally:

```text
Logistic Regression
Random Forest
ExtraTrees
XGBoost
LightGBM
```

Then add:

```text
OOF predictions
probability calibration
stacking
```

## P4 — Dynamic weighting

Only after static calibrated stacking works out of sample.

## P5 — SMC ablation

Test whether SMC features add incremental predictive and PnL value.

## P6 — Model Council

Council consumes validated evidence. It does not invent evidence.

## P7 — Paper promotion

A model influences paper orders only after all existing FX promotion gates pass.

---

# XV.12 Final Codex directive

Do not make FX stronger by accumulating more downloadable “trading AI.”

Make it stronger by extracting the useful engineering and rejecting weak evidence.

This batch resolves to:

```text
QuantumAI
-> AVOID

jalvart BTC tick sample
-> ABSORB FOR MICROSTRUCTURE RESEARCH

AdityaaXD Multi-Model
-> EXTRACT / REBUILD

Romeo V8
-> EXTRACT calibration + stacking + dynamic weighting
-> REBUILD locally
-> distrust headline metrics until reproduced

com-trading-bot
-> DO NOT treat as a trading model

XAUUSD SMC v2
-> retain EXTRACT / REBUILD decision
```

FX should win through:

```text
better data
better validation
better calibration
better execution modeling
better risk controls
better model selection
better failure handling
```

not through model-count inflation.

---

# APPENDIX C — IMAGE EXTRACTION + RESEARCH VERIFICATION NOTES

This appendix records what was extracted from the supplied nine-image set and what was independently verified. It is supporting research context; Section 23 is the canonical implementation interpretation.

## C.1 Image 1 — Prediction market mispricing engine

Image claims / concepts:

```text
Polymarket + Kalshi
pull live order books
compare YES/NO contracts
look for YES + NO below 1 after costs
spread across venues
execution is harder than detection
fees, gas, slippage matter
Kelly sizing
75M-order-book NBA study
```

Verification:

The cited 2026 NBA paper exists. It analyzes over 75 million Polymarket LOB snapshots across 173 NBA games and reports rare single-market executable anomalies with median life around 3.6 seconds. It also documents severe depth/capacity constraints in combinatorial opportunities.

Research correction:

Cross-venue mispricing requires contract-equivalence proof and synchronized executable states. Recent 2026 literature contains conflicting results on whether persistent Kalshi/Polymarket arbitrage survives correct alignment and fees, so FX must test rather than assume.

## C.2 Image 2 — Information diffusion model

Image concepts:

```text
Hawkes process
news timestamps + price/event timestamps
exogenous spike vs endogenous echo
exponential decay kernel
half-life ln(2)/beta
endogeneity ratio
response around scheduled releases
```

Verification:

Hawkes processes are well-established in high-frequency finance. Bacry et al. survey volatility, market stability, systemic contagion, optimal execution, and order-book applications. Rambaldi et al. specifically model FX activity around scheduled macroeconomic news using endogenous and exogenous Hawkes components.

Research correction:

The fitted decay parameter is kernel-specific; calling it the exact "information half-life" overstates identification. Seasonality, news surprise, overlapping events, and data timing must be modeled.

## C.3 Image 3 — Breeden-Litzenberger implied risk-neutral distribution

Image concepts:

```text
option prices encode state prices
second derivative of call price wrt strike
q(K) ≈ exp(rT) d²C/dK²
butterfly-spread intuition
smooth implied vol first
negative densities signal a problem
```

Verification:

The Breeden-Litzenberger result is foundational and correctly links the strike curvature of call prices to state-price / risk-neutral density information under no-arbitrage assumptions.

Research correction:

The resulting distribution is risk-neutral, not a direct physical probability forecast. Raw finite differencing of noisy option chains is unsafe. FX must fit a clean, arbitrage-aware surface and preserve market-specific conventions.

## C.4 Image 4 — Backtest overfitting detector

Image concepts:

```text
generate many random rules
best historical Sharpe can look excellent
trial count matters
Deflated Sharpe Ratio
selection bias
non-normal returns
```

Verification:

The DSR paper and PBO research directly address these problems. The image's random-rule demonstration is pedagogically sound as a null experiment, but FX's production implementation must use formal research-family accounting and validation gates.

## C.5 Image 5 — Linear algebra

Image curriculum:

```text
vectors
matrices
rank
linear independence
subspaces
projections
least squares
eigenvalues/eigenvectors
SVD
positive-definite matrices
```

Recommended reference:

```text
MIT OCW 18.06 — Gilbert Strang
Mathematics for Machine Learning — linear algebra sections
```

FX relevance:

```text
factor models
PCA
covariance/risk
least squares
Kalman filters
portfolio construction
neural-network computation
```

## C.6 Image 6 — Calculus

Image curriculum:

```text
limits
derivatives
chain rule
integration
multivariable calculus
gradients
Jacobian
Hessian
Taylor approximation
```

Recommended reference:

```text
MIT OCW 18.02 — Multivariable Calculus
```

FX relevance:

```text
optimization
Greeks
backpropagation
sensitivity
likelihood
continuous-time models
```

## C.7 Image 7 — Probability and statistics

Image curriculum:

```text
random variables
expectation
variance
common distributions
conditional probability
Bayes
covariance
estimators
maximum likelihood
bias-variance
confidence intervals
hypothesis tests
squared error / cross entropy
```

Recommended references:

```text
Harvard Stat 110
Stanford CS229 probability review
```

FX correction:

Financial data are frequently non-i.i.d., heavy-tailed, serially dependent, heteroskedastic, and regime-changing. The bot curriculum must learn assumption checking, not just textbook formulas.

## C.8 Image 8 — Optimization

Image curriculum:

```text
objective functions
convexity
gradient descent
SGD
momentum / Adam
Newton methods
Lagrange multipliers
KKT
regularization
```

Recommended references:

```text
Stanford EE364A
Boyd & Vandenberghe — Convex Optimization
```

FX correction:

Optimization does not create information. It can overfit noise extremely efficiently. Research integrity and uncertainty constraints precede optimizer sophistication.

## C.9 Image 9 — Deep learning

Image curriculum:

```text
linear/logistic foundations
classification
neural networks
backpropagation
attention
forward pass
loss functions
chain rule
```

Recommended reference:

```text
Stanford CS229
```

FX correction:

Deep learning is a challenger family. It receives no privileged promotion and must beat simple baselines under identical OOS, cost, risk, and multiple-testing controls.

## C.10 Most important lesson from the full image set

The images collectively point toward a useful hierarchy:

```text
MATHEMATICAL FOUNDATIONS
        ↓
MARKET-SPECIFIC MODELS
        ↓
STATISTICAL FALSIFICATION
        ↓
EXECUTION REALITY
        ↓
RISK CONTROL
```

FX should absorb that hierarchy.

Do NOT reverse it into:

```text
cool formula
→ bot
→ trade
```

The Supervisor's job is increasingly to ask:

```text
What assumptions make this formula valid?
What data are required?
What could make the result spurious?
How would we falsify it?
What simpler baseline should beat?
Does the edge survive costs?
What uncertainty remains?
```

That is the intended use of this research.

---

# APPENDIX D — FORENSIC CHANGELOG

This rewrite intentionally removed the previous document's duplicated normative implementation plans and replaced them with one canonical contract.

Major changes:

1. Removed the false mid-file `END` as a governing boundary.
2. Stopped restarting Part/P-level numbering in the canonical section.
3. Added a precedence hierarchy for Codex.
4. Defined `StrategySpec`, `ModelArtifact`, `ResearchBot`, `PaperBot`, `SupervisorAgent`, `ExaminerService`, `PromotionService`, `RiskGovernor`, `KnowledgeItem`, and `LessonPackage`.
5. Separated governance, data, research, knowledge, execution, and observability planes.
6. Replaced narrative bot evolution with an explicit lifecycle state machine.
7. Added point-in-time/timezone/event-time data requirements.
8. Added a reproducible experiment contract and `research_family_id`.
9. Converted multiple-testing concerns into mandatory promotion evidence.
10. Replaced scalar BotScore safety logic with hard gates + constrained ranking.
11. Added exact paper order/event/accounting contracts.
12. Strengthened deterministic Risk Governor independence.
13. Limited Supervisor outputs to structured proposals.
14. Prohibited active-bot self-modification.
15. Added explicit experiment/population budgets.
16. Converted peer learning into versioned lesson artifacts with reproduction requirements.
17. Replaced pseudo-precise source trust formulas with evidence classes E0–E4.
18. Strengthened external code/model quarantine.
19. Created one canonical P0–P11 implementation roadmap.
20. Added idempotency, concurrency, observability, and documentation-state requirements.
21. Delayed RL/meta-learning until foundational accounting/evaluation is proven.
22. Added anti-patterns that Codex should explicitly reject.
23. Clarified that the Supervisor should optimize research quality, not chase recent PnL.
24. Preserved prior research/source notes as non-canonical appendices.

## Final forensic conclusion

The original file had a high-quality concept but suffered from “architecture inflation”: many advanced components were described before the basic contracts that make them trustworthy were formalized.

This version deliberately makes the system **less magical and more buildable**.

That is an improvement.

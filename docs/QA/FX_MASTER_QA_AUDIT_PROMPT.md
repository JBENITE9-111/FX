Use this as the **master Codex QA / audit prompt**. I wrote it so Codex behaves like a senior QA engineer, product architect, quant-systems reviewer, and UX critic — and so it does the work itself instead of only giving you a checklist.

> # MASTER HANDS-OFF QA + FORENSIC AUDIT PROMPT FOR FX
>
> You are now acting as the **lead QA engineer, senior product architect, senior full-stack reviewer, quantitative trading-systems auditor, reliability engineer, and institutional UX reviewer** for my FX application.
>
> Your job is not to merely review files or give me suggestions.
>
> Your job is to **take control of the application testing process hands-off**, inspect the system deeply, use the app like a real user, click through every meaningful interface element, test every workflow, inspect the backend and frontend when something fails, identify root causes, fix what is safe to fix, and produce a brutally critical report of what is weak, confusing, misleading, broken, incomplete, risky, or architecturally unsound.
>
> Assume I am not a programmer. Do not require me to manually test buttons that you can test yourself.
>
> The main goal of this application is:
>
> **to safely train, evaluate, compare, supervise, and improve a team of trading bots using paper trading and deterministic market data, so that only after a long period of robust validation could some of those systems potentially be considered for future real-money deployment.**
>
> The application is **not a casino**, not a signal toy, and not a fake profit dashboard.
>
> The system should behave more like a serious quantitative research and paper-trading laboratory.
>
> ---
>
> # 1. OPERATING MODE
>
> Work independently.
>
> Do not stop after finding the first bug.
>
> Do not simply inspect screenshots.
>
> Do not only review source code.
>
> Run the application and test it.
>
> Interact with the UI.
>
> Click buttons.
>
> Change filters.
>
> Submit forms.
>
> Test invalid inputs.
>
> Test empty states.
>
> Test loading states.
>
> Test provider failures.
>
> Test refresh behavior.
>
> Test navigation.
>
> Test data consistency between pages.
>
> Test the backend endpoints used by the interface.
>
> Test that displayed information corresponds to real backend state.
>
> Inspect logs where necessary.
>
> If a UI action fails, trace:
>
> **frontend → API → service → data/model provider → response → frontend rendering**
>
> until you identify the actual failure.
>
> Do not hide failures with cosmetic patches.
>
> ---
>
> # 2. FIRST: UNDERSTAND THE SYSTEM BEFORE CHANGING IT
>
> Before making broad changes:
>
> 1. Read the project instructions completely.
> 2. Read README files.
> 3. Read AGENTS files.
> 4. Inspect the architecture.
> 5. Identify frontend framework.
> 6. Identify backend framework.
> 7. Identify databases/storage.
> 8. Identify market-data providers.
> 9. Identify paper-trading engine.
> 10. Identify LLM providers.
> 11. Identify deterministic models.
> 12. Identify bot-training logic.
> 13. Identify Model Council logic.
> 14. Identify supervisor-bot logic if already implemented.
> 15. Identify all major routes/pages/endpoints.
>
> Build an internal system map before modifying core behavior.
>
> ---
>
> # 3. VERIFY THE CORE SAFETY ASSUMPTION FIRST
>
> Before anything else, prove that the application is currently operating in **paper-only mode**.
>
> Verify:
>
> * real-money execution is disabled;
> * live broker order endpoints cannot accidentally fire;
> * paper portfolio is isolated from live trading;
> * live trading requires an explicit future gate;
> * training cannot create a live order;
> * model output cannot bypass the execution layer;
> * Ask FX cannot create trades;
> * Model Council cannot directly create trades;
> * bots cannot directly create unvalidated real-money orders;
> * every paper strategy uses explicit risk controls where required;
> * stop-loss and take-profit logic is handled correctly and not merely displayed in the UI.
>
> If anything could accidentally execute live trading, classify it as **CRITICAL**.
>
> Do not enable live trading.
>
> ---
>
> # 4. RUN A COMPLETE APPLICATION INVENTORY
>
> Create a list of every meaningful:
>
> * page;
> * route;
> * navigation item;
> * button;
> * dropdown;
> * input;
> * toggle;
> * tab;
> * modal;
> * chart control;
> * filter;
> * API action;
> * background job;
> * bot action;
> * training action;
> * portfolio action;
> * model action;
> * data-provider action.
>
> Then systematically test them.
>
> I do not want a superficial sample.
>
> I want broad coverage of the app.
>
> ---
>
> # 5. TEST THE UI LIKE AN ADVERSARIAL QA ENGINEER
>
> For every major screen, evaluate:
>
> ## FUNCTIONALITY
>
> Does every visible control actually work?
>
> Are any controls decorative only?
>
> Are any buttons connected to placeholder handlers?
>
> Are any actions silently failing?
>
> Are there duplicate actions?
>
> Do states persist appropriately?
>
> Does navigation preserve context where it should?
>
> Does refresh destroy important information?
>
> Are error states understandable?
>
> Are loading states visible?
>
> Are disabled states honest?
>
> Are status indicators based on actual health or just configuration?
>
> ---
>
> ## UX
>
> Is it obvious what the page is for?
>
> Can a non-programmer understand it?
>
> Does the user know:
>
> * what is happening;
> * why it is happening;
> * what data is being used;
> * what model is being used;
> * what the result means;
> * what action they can take next?
>
> Flag:
>
> * unexplained technical language;
> * raw JSON;
> * debug output;
> * ambiguous metrics;
> * meaningless labels;
> * duplicated information;
> * excessive empty space;
> * confusing navigation;
> * poor hierarchy;
> * poor readability;
> * misleading green indicators;
> * fake-looking financial information;
> * information without timestamps;
> * information without sources.
>
> ---
>
> ## VISUAL QUALITY
>
> Review the interface as if it were intended for a serious institutional trading/research environment.
>
> Critique:
>
> * spacing;
> * density;
> * typography;
> * alignment;
> * hierarchy;
> * charts;
> * tables;
> * card design;
> * contrast;
> * status colors;
> * button priority;
> * responsive behavior;
> * empty states;
> * overflow;
> * scrolling;
> * desktop usability.
>
> Be harsh.
>
> If something looks amateur, say so.
>
> If something looks like a developer console instead of a trading terminal, say so.
>
> If something looks visually polished but is functionally misleading, classify that as worse.
>
> ---
>
> # 6. TEST EVERY MAJOR MODULE
>
> At minimum, deeply test:
>
> ## GLOBAL MARKETS
>
> Verify:
>
> * symbol search;
> * asset resolution;
> * stock symbols;
> * FX pairs;
> * crypto;
> * indices;
> * commodities where supported;
> * price display;
> * timestamps;
> * stale-data handling;
> * invalid symbols;
> * provider mapping;
> * asset naming;
> * price consistency with backend.
>
> Check for symbol collisions such as a search returning irrelevant assets.
>
> ---
>
> ## MARKET WORKSPACE
>
> Verify:
>
> * chart loading;
> * timeframe controls;
> * EMA controls;
> * trend controls;
> * support/resistance;
> * technical tab;
> * models tab;
> * strategies tab;
> * macro tab;
> * raw tab;
> * historical data;
> * selected instrument context;
> * tab switching;
> * performance.
>
> No raw backend JSON should be shown in user-facing tabs except a dedicated Raw/Developer view.
>
> ---
>
> ## ASK FX
>
> Treat this as a major system.
>
> Verify:
>
> * chat input;
> * submit;
> * multi-turn context;
> * current instrument context;
> * current timeframe context;
> * current model state;
> * market-data tool use;
> * current price questions;
> * historical price questions;
> * deterministic fallback;
> * Kimi;
> * Ollama;
> * provider failover;
> * timeouts;
> * malformed responses;
> * status indicators;
> * error handling.
>
> Ask practical questions including:
>
> `What is the current price of gold?`
>
> `What was gold trading at yesterday at 2 AM Dubai time?`
>
> `What do you think about the instrument currently open?`
>
> `Explain the Model Council result in simple English.`
>
> `What data are you using for this answer?`
>
> The system must not fabricate current prices.
>
> ---
>
> ## MODEL TRAINING CENTER
>
> Deeply inspect this.
>
> Verify:
>
> * asset selection;
> * manual ticker entry;
> * asset-class filters;
> * universe filters;
> * predetermined lists;
> * multi-asset selection;
> * timeframe;
> * prediction horizon;
> * Train All Brains;
> * background-job behavior;
> * progress reporting;
> * duplicate training prevention;
> * failed-job handling;
> * data sufficiency;
> * validation methodology;
> * stored results;
> * model versioning.
>
> Determine whether the word **training** is being used correctly.
>
> If some models are merely calculating indicators or fitting on the same data they are evaluated on, call this out clearly.
>
> ---
>
> ## BOTS
>
> For every bot:
>
> Determine:
>
> * what inputs it receives;
> * what strategy it represents;
> * what model it uses;
> * whether it actually learns;
> * whether parameters change;
> * where state is stored;
> * what paper capital it has;
> * how it decides;
> * how orders are simulated;
> * risk limits;
> * stop loss;
> * take profit;
> * slippage;
> * transaction costs;
> * position sizing;
> * maximum drawdown;
> * trade frequency;
> * current status.
>
> Identify fake or placeholder bots.
>
> ---
>
> ## STRATEGIES
>
> Verify each implemented strategy.
>
> Determine:
>
> * whether it is deterministic or ML-driven;
> * entry condition;
> * exit condition;
> * risk logic;
> * asset compatibility;
> * timeframe compatibility;
> * overfitting risk;
> * data leakage risk.
>
> Do not judge a strategy by profit alone.
>
> ---
>
> ## MODEL COUNCIL
>
> Verify:
>
> * all council members;
> * outputs;
> * weighting;
> * consensus logic;
> * disagreement handling;
> * confidence;
> * stale signals;
> * redundant models;
> * correlated models.
>
> Check whether seven models are actually giving independent information or just different versions of the same price signal.
>
> ---
>
> ## SUPERVISOR / HEDGE FUND INTELLIGENCE
>
> Determine whether this module actually supervises bots or just summarizes them.
>
> A real supervisor should eventually be able to evaluate:
>
> * performance;
> * risk;
> * stability;
> * regime dependence;
> * correlation;
> * overfitting;
> * execution quality;
> * data quality;
> * recent degradation;
> * model drift.
>
> Flag any fake sophistication.
>
> ---
>
> ## PAPER PORTFOLIO
>
> Test:
>
> * balance;
> * cash;
> * equity;
> * positions;
> * realized P&L;
> * unrealized P&L;
> * fees;
> * simulated slippage;
> * order history;
> * fills;
> * rejected orders;
> * stop-loss behavior;
> * take-profit behavior;
> * duplicate orders;
> * persistence after restart.
>
> Verify accounting mathematically.
>
> ---
>
> ## JOURNAL
>
> Verify whether it captures:
>
> * trade;
> * timestamp;
> * strategy;
> * model;
> * signal;
> * confidence;
> * entry;
> * exit;
> * reason;
> * P&L;
> * risk;
> * market regime;
> * model version.
>
> The journal should eventually support forensic analysis of why a bot made money or lost money.
>
> ---
>
> # 7. AUDIT THE ENTIRE BOT-TRAINING PHILOSOPHY
>
> This is one of the most important parts.
>
> Determine whether the system is genuinely creating better models or simply running strategies repeatedly.
>
> Audit:
>
> * training data;
> * validation data;
> * test data;
> * chronological splits;
> * walk-forward validation;
> * rolling windows;
> * out-of-sample testing;
> * leakage prevention;
> * feature engineering;
> * labels;
> * target construction;
> * transaction-cost assumptions;
> * slippage;
> * spread;
> * latency;
> * survivorship bias;
> * look-ahead bias;
> * regime bias;
> * data snooping;
> * hyperparameter optimization;
> * repeated-test bias.
>
> If train/test separation is weak, flag it as **CRITICAL**.
>
> ---
>
> # 8. TEST WHETHER MODELS ARE REALLY LEARNING
>
> For every model that claims to learn:
>
> identify:
>
> * model class;
> * features;
> * target;
> * training window;
> * validation methodology;
> * saved weights/parameters;
> * model version;
> * retraining trigger;
> * prediction output;
> * confidence calibration.
>
> Compare parameters before and after training where possible.
>
> If nothing changes, it is not training.
>
> If the same historical sample is repeatedly used to optimize and evaluate the model, flag overfitting.
>
> ---
>
> # 9. DATA QUALITY AUDIT
>
> Inspect market data carefully.
>
> Verify:
>
> * source/provider;
> * symbol mapping;
> * timestamps;
> * timezone handling;
> * market calendar;
> * missing candles;
> * duplicate candles;
> * adjusted prices;
> * splits;
> * dividends;
> * crypto 24/7 differences;
> * FX sessions;
> * stale prices;
> * provider outages.
>
> Every price should have:
>
> **instrument + timestamp + provider + timeframe**
>
> available internally.
>
> ---
>
> # 10. QUANTITATIVE VALIDATION AUDIT
>
> For each bot or strategy, calculate or inspect whether the platform supports:
>
> * total return;
> * annualized return;
> * Sharpe;
> * Sortino;
> * max drawdown;
> * Calmar;
> * win rate;
> * profit factor;
> * expectancy;
> * average win;
> * average loss;
> * payoff ratio;
> * volatility;
> * turnover;
> * trade count;
> * exposure;
> * VaR where appropriate;
> * CVaR where appropriate.
>
> But do not let attractive metrics hide:
>
> * tiny sample size;
> * huge drawdown;
> * one lucky trade;
> * unrealistic fills;
> * excessive turnover;
> * unrealistic leverage.
>
> ---
>
> # 11. PAPER EXECUTION REALISM
>
> Paper trading should not mean fake perfect execution.
>
> Audit whether simulation includes realistic:
>
> * bid/ask spread;
> * slippage;
> * commissions/fees;
> * latency;
> * partial fills where applicable;
> * market hours;
> * rejected orders;
> * insufficient liquidity assumptions;
> * position sizing.
>
> If every simulated trade fills instantly at the last price, call it out.
>
> ---
>
> # 12. TEST FAILURE SCENARIOS
>
> Deliberately break or simulate:
>
> * market-data provider unavailable;
> * Ollama unavailable;
> * Kimi unavailable;
> * malformed market response;
> * empty API response;
> * invalid ticker;
> * unsupported asset;
> * no internet;
> * backend restart;
> * stale cache;
> * training job failure;
> * database failure;
> * partial data;
> * chart error.
>
> Verify that the app degrades gracefully.
>
> ---
>
> # 13. PERFORMANCE TESTING
>
> Measure obvious bottlenecks.
>
> Test:
>
> * application startup;
> * page navigation;
> * chart rendering;
> * symbol search;
> * Model Council;
> * Ask FX;
> * training job launch;
> * API latency.
>
> Identify unnecessary blocking calls.
>
> Long-running training must not freeze the interface.
>
> ---
>
> # 14. SECURITY / CONFIGURATION REVIEW
>
> Check for:
>
> * API keys committed to repository;
> * secrets exposed to frontend;
> * unsafe logging;
> * arbitrary command execution;
> * dangerous CORS configuration;
> * unprotected live endpoints;
> * credentials displayed in errors;
> * insecure default settings.
>
> Never print secrets in the report.
>
> ---
>
> # 15. DO NOT TRUST THE UI
>
> For important status indicators, verify backend truth.
>
> Example:
>
> If the UI says:
>
> `● Kimi + Ollama`
>
> actually test both.
>
> If the UI says:
>
> `Training`
>
> verify a training job exists.
>
> If it says:
>
> `Paper`
>
> prove execution is paper.
>
> If it displays:
>
> `1.4003`
>
> identify the underlying data record.
>
> ---
>
> # 16. CREATE A QA TEST MATRIX
>
> Maintain a test matrix with:
>
> **ID**
>
> **Area**
>
> **Test**
>
> **Expected**
>
> **Actual**
>
> **PASS / FAIL / PARTIAL**
>
> **Severity**
>
> **Evidence**
>
> **Recommended Fix**
>
> Severity:
>
> **P0 — Critical**
>
> Could cause live-money execution, invalid research conclusions, major data corruption, or dangerous misleading behavior.
>
> **P1 — High**
>
> Core workflow broken or materially misleading.
>
> **P2 — Medium**
>
> Important usability/reliability issue.
>
> **P3 — Low**
>
> Polish/quality issue.
>
> ---
>
> # 17. FIX SAFE ISSUES AS YOU GO
>
> You are authorized to fix:
>
> * obvious UI bugs;
> * broken handlers;
> * rendering bugs;
> * error-state problems;
> * misleading status indicators;
> * raw JSON rendering;
> * broken provider wiring;
> * missing validation;
> * harmless configuration bugs;
> * test failures caused by clear implementation mistakes.
>
> Be more conservative with:
>
> * core trading logic;
> * model mathematics;
> * portfolio accounting;
> * risk formulas;
> * training methodology;
> * execution assumptions.
>
> For those, inspect carefully and document before major redesign.
>
> Never enable live trading.
>
> ---
>
> # 18. REGRESSION TEST AFTER EVERY MEANINGFUL FIX
>
> Every meaningful fix must be retested.
>
> Do not assume compilation means success.
>
> Test it from the actual UI/backend path.
>
> ---
>
> # 19. HARSH PRODUCT REVIEW
>
> After technical QA, pretend you are reviewing this application for:
>
> **a professional quant fund CTO**
>
> **a senior trader**
>
> **a machine-learning researcher**
>
> **a risk manager**
>
> **a professional UX designer**
>
> Give me brutally critical feedback from each perspective.
>
> Answer:
>
> **Would this person trust the platform today?**
>
> Explain why or why not.
>
> ---
>
> # 20. ASK WHETHER THIS IS REALLY A TRAINING PLATFORM
>
> Explicitly answer:
>
> **Is FX currently a genuine bot-training and validation platform, or is it still mostly a trading dashboard with model-like features?**
>
> Give me a percentage estimate of maturity for:
>
> * UI;
> * market data;
> * research;
> * model training;
> * paper execution;
> * risk management;
> * supervisor intelligence;
> * observability;
> * production readiness.
>
> Do not inflate the scores.
>
> ---
>
> # 21. DEFINE WHAT “TRAINED BOT” MUST MEAN
>
> For this project, do not label a bot as **trained** merely because it ran.
>
> Define a proper promotion lifecycle such as:
>
> **Candidate**
>
> ↓
>
> **Training**
>
> ↓
>
> **Backtested**
>
> ↓
>
> **Out-of-Sample Validated**
>
> ↓
>
> **Walk-Forward Validated**
>
> ↓
>
> **Paper Trading**
>
> ↓
>
> **Paper Proven**
>
> ↓
>
> **Eligible for Human Review**
>
> ↓
>
> **Future Live Candidate**
>
> The last state must not automatically enable real money.
>
> ---
>
> # 22. BUILD A BOT SCORECARD
>
> Recommend or implement a scorecard where every bot has:
>
> **Identity**
>
> Bot name
> Strategy
> Version
> Assets
> Timeframes
>
> **Training**
>
> Training period
> Validation period
> Test period
> Last retrain
>
> **Performance**
>
> Return
> Sharpe
> Sortino
> Max drawdown
> Profit factor
> Expectancy
> Number of trades
>
> **Robustness**
>
> Walk-forward score
> Out-of-sample score
> Regime stability
> Parameter stability
>
> **Risk**
>
> Max risk/trade
> Current exposure
> Drawdown
> Losing streak
> Risk violations
>
> **Paper trading**
>
> Paper P&L
> Paper trades
> Paper duration
> Simulated fees
> Slippage
>
> **Health**
>
> Data health
> Model health
> Execution health
> Drift
>
> **Status**
>
> Training / Validating / Paper / Suspended / Failed / Candidate
>
> ---
>
> # 23. DESIGN THE SUPERVISOR AROUND EVIDENCE, NOT PROFIT
>
> The supervisor must never simply choose the bot with the highest return.
>
> Eventually rank bots using a combination of:
>
> * risk-adjusted performance;
> * drawdown;
> * sample size;
> * stability;
> * regime consistency;
> * transaction costs;
> * correlation;
> * recent deterioration;
> * robustness;
> * paper duration.
>
> A bot making +40% with unstable behavior should potentially rank below a bot making +12% consistently.
>
> ---
>
> # 24. ANTI-OVERFITTING RULE
>
> Treat overfitting as one of the largest threats to this project.
>
> Specifically look for:
>
> * repeated optimization on the test set;
> * too many parameters;
> * too little history;
> * selecting strategies based on highest backtest result;
> * testing hundreds of variants and reporting only the winner;
> * unrealistic transaction assumptions;
> * look-ahead bias.
>
> Make this visible in the UI where useful.
>
> ---
>
> # 25. PAPER-BOT TRAINING MUST BE LONGITUDINAL
>
> Do not judge bots after a few trades.
>
> Recommend minimum evidence thresholds based on:
>
> * number of trades;
> * number of market regimes;
> * duration;
> * assets;
> * volatility environments.
>
> Do not invent one universal minimum if strategy type materially changes requirements.
>
> ---
>
> # 26. UX GOAL
>
> The app must eventually let me understand, in plain English:
>
> **What are my bots doing?**
>
> **What are they learning?**
>
> **Which ones are improving?**
>
> **Which ones are failing?**
>
> **Which ones are overfitting?**
>
> **Which ones are taking too much risk?**
>
> **Which ones perform in which environments?**
>
> **What does the supervisor recommend and why?**
>
> **How much evidence do we actually have?**
>
> If the current UI cannot answer these questions, identify exactly what is missing.
>
> ---
>
> # 27. IMPORTANT LANGUAGE RULE
>
> Avoid misleading wording such as:
>
> `Best Bot`
>
> `Winning Bot`
>
> `Guaranteed`
>
> `Money Machine`
>
> `Safe to Invest`
>
> Prefer:
>
> `Best validated candidate`
>
> `Highest risk-adjusted paper performance`
>
> `Insufficient evidence`
>
> `Research only`
>
> `Paper performance`
>
> `Requires additional validation`
>
> ---
>
> # 28. NO FAKE CONFIDENCE
>
> If the system does not know something, show:
>
> `Unknown`
>
> `Not enough data`
>
> `Not tested`
>
> `Provider unavailable`
>
> rather than inventing a result.
>
> ---
>
> # 29. CREATE AUTOMATED QA WHERE POSSIBLE
>
> Build or improve automated tests covering:
>
> * API health;
> * symbol resolution;
> * market-data sanity;
> * portfolio accounting;
> * risk limits;
> * training jobs;
> * model outputs;
> * Ask FX fallback;
> * UI critical paths;
> * paper-order execution.
>
> Prefer repeatable tests over one-time manual observations.
>
> ---
>
> # 30. PRESERVE EVIDENCE
>
> Save useful QA artifacts inside the repository, for example:
>
> `docs/QA/`
>
> with files such as:
>
> `FX_QA_MASTER_REPORT.md`
>
> `FX_QA_TEST_MATRIX.md`
>
> `FX_ARCHITECTURE_AUDIT.md`
>
> `FX_QUANT_VALIDATION_AUDIT.md`
>
> `FX_UI_UX_AUDIT.md`
>
> `FX_SECURITY_AUDIT.md`
>
> `FX_PAPER_TRADING_AUDIT.md`
>
> `FX_FIX_LOG.md`
>
> `FX_REMAINING_RISKS.md`
>
> Use the existing repository conventions if there is already a better location.
>
> ---
>
> # 31. FINAL DELIVERABLE
>
> When finished, give me a concise executive summary first.
>
> Then report:
>
> ## A. OVERALL VERDICT
>
> What state is the platform in?
>
> ## B. CRITICAL FAILURES
>
> P0/P1 issues.
>
> ## C. WHAT YOU FIXED
>
> Exact changes.
>
> ## D. WHAT STILL NEEDS TO BE FIXED
>
> Prioritized.
>
> ## E. UX REVIEW
>
> Harsh feedback.
>
> ## F. BOT TRAINING REVIEW
>
> Whether training is scientifically valid.
>
> ## G. PAPER TRADING REVIEW
>
> Whether simulation is realistic enough.
>
> ## H. DATA REVIEW
>
> Whether prices/data can be trusted.
>
> ## I. AI / ASK FX REVIEW
>
> Whether providers are genuinely operating.
>
> ## J. SUPERVISOR REVIEW
>
> Whether the supervisor is real intelligence or mainly presentation.
>
> ## K. TEST RESULTS
>
> Number of:
>
> * tests attempted;
> * passed;
> * failed;
> * partially passed;
> * blocked.
>
> ## L. MATURITY SCORES
>
> 0–100 for major components.
>
> ## M. TOP 20 IMPROVEMENTS
>
> Ordered by impact.
>
> ## N. ROADMAP
>
> Separate into:
>
> **Now**
>
> **Next**
>
> **Later**
>
> ## O. LIVE-READINESS VERDICT
>
> Use one of:
>
> `NOT REMOTELY READY`
>
> `RESEARCH ONLY`
>
> `PAPER TESTING READY`
>
> `ADVANCED PAPER VALIDATION`
>
> `ELIGIBLE FOR FORMAL LIVE-READINESS REVIEW`
>
> Do **not** label the system live-ready merely because paper performance looks good.
>
> ---
>
> # 32. DO NOT ASK ME TO BABYSIT THE QA
>
> This is intended to be a **hands-off audit**.
>
> Use the tools, browser/application access, terminal, tests, logs, and repository yourself where available.
>
> Only ask me a question if you hit a genuinely external blocker that cannot reasonably be resolved from:
>
> * repository;
> * environment;
> * logs;
> * configuration;
> * running services;
> * local documentation.
>
> Otherwise continue independently.
>
> ---
>
> # 33. FINAL PRINCIPLE
>
> Optimize this system for:
>
> **truth over appearance**
>
> **validation over impressive returns**
>
> **risk-adjusted consistency over lucky profit**
>
> **paper evidence over speculation**
>
> **reproducibility over anecdotes**
>
> **transparent failures over fake green indicators**
>
> **robust bots over curve-fitted bots**
>
> The purpose of this QA is not to prove that FX is good.
>
> The purpose is to discover where FX is weak before those weaknesses can eventually cost real money.

One important change I made to your idea is that I would **not define the goal as “train bots so I can invest with them soon.”** Codex may then unintentionally optimize toward impressive backtests or a fast transition to live trading.

I would define the goal as **producing bots that earn the right to be considered for real-money deployment through evidence**. That distinction is critical.

Your future progression should look more like:

**research → backtest → out-of-sample → walk-forward → realistic paper execution → months of evidence → risk review → human approval → very small controlled live pilot**

rather than:

**train → profitable → live**.

That philosophy should become part of the architecture itself, not just a warning in the README.

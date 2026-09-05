# FX QA Test Matrix

This matrix records verified behavior. The master QA prompt is a review checklist; it does not override the trading constitution or safety gates.

| ID | Area | Test | Expected | Actual | Status | Severity | Evidence / action |
|---|---|---|---|---|---|---|---|
| QA-001 | Safety | Read runtime mode and live flags | Live orders disabled | `real_money=false`; live gate locked | PASS | P0 | Local API health and status |
| QA-002 | Ask FX | Ask current gold price while another market is selected | Resolve Gold and use verified data | Root cause found: chat inherited selected symbol; fixed to resolve the named instrument | PASS | P1 | Deterministic LSE response |
| QA-003 | Ask FX | Ask what running bots do | Explain actual process without an LLM | Added deterministic operations answer from local bot state | PASS | P1 | `/api/control/chat` |
| QA-004 | Training | Separate model runtime health from trading qualification | Completed training must not look broken; weak evidence must remain blocked | Added `RESEARCH_COMPLETE` / `WORKING · NOT QUALIFIED` | PASS | P1 | Learning overview and UI |
| QA-005 | Journal | Empty canonical journal with legacy positions | Explain quarantine instead of displaying Loading | Empty state now identifies legacy excluded positions | PASS | P2 | Reporting API + Journal |
| QA-006 | Paper | Browse instruments across every supported asset class | Search full local catalog | Added catalog browser for Stocks, Forex, Crypto, Commodities, Indices, ETFs, Futures | PASS | P1 | Local Paper UI + catalog API |
| QA-007 | Paper | Show bot evidence beside an order | Show source, strategy, direction, metrics, and qualification | Added research suggestion cards; no automatic approval | PASS | P1 | Local bot runtime state |
| QA-008 | Bots | Explain running location and activity | Show actual source/process/authority | Added source, local runtime, activity, learning, and order authority | PASS | P2 | Trading Bots panel |
| QA-009 | Paper accounting | Reconcile open positions and canonical trades | Legacy state must not count as validated performance | Eight legacy positions quarantined; zero canonical trades | PASS | P0 | Local SQLite reporting |
| QA-010 | Live | Locate assisted live trading | Must stay unavailable until formal gates pass | Live remains locked; paper workflow is available | PASS | P0 | Live Trading Gate |
| QA-011 | Paper | Change asset class from Stocks to Indices | List, instrument, price, and bot evidence update together | Fixed async selection race; NAS100/USD loaded with its verified price and Indices Scanner | PASS | P1 | Live browser test |
| QA-012 | Bots | Cover every requested market family | Dedicated bounded scanner teams exist | Eight teams now cover equities, Forex, crypto, gold, commodities, indices, ETFs, and futures | PASS | P1 | Bot runtime API |

## Current evidence verdict

The training code is running, but the existing AAPL and NVDA models have not demonstrated predictive value on unseen data. They are functioning research brains and remain unqualified for paper automation. Approval will require better data/features, calibrated probabilities, and successful chronological validation; labels will not be changed to manufacture eligibility.

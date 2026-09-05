# FX External Strategy Intake Policy

Every strategy imported from:

- GitHub
- Freqtrade
- MetaTrader
- TradingView
- academic papers
- AI agents
- online articles
- another trading system

must begin as:

EXTERNAL_UNTRUSTED

External published profitability is not evidence.

No external strategy may jump directly to:

PAPER
SHADOW
MICRO_LIVE
LIMITED_LIVE
APPROVED

Required flow:

SOURCE SNAPSHOT
↓
SOURCE HASH
↓
LICENSE RECORD
↓
STRATEGY DNA EXTRACTION
↓
MECHANISM DESCRIPTION
↓
GRID / MARTINGALE DETECTION
↓
LOOK-AHEAD AUDIT
↓
NATIVE FX IMPLEMENTATION
↓
RESEARCH CONTRACT
↓
TRAIN DATA
↓
OUT-OF-SAMPLE
↓
WALK-FORWARD
↓
PARAMETER SENSITIVITY
↓
TRANSACTION-COST STRESS
↓
BOOTSTRAP
↓
MONTE CARLO
↓
MODEL KILLER
↓
INDEPENDENT REPLAY
↓
VAULT
↓
PAPER
↓
SHADOW
↓
LIVE PROMOTION GATE

The safest valid decision is NO TRADE.

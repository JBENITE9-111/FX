# FX Plain English Policy

The owner of FX is not a programmer.

This is a permanent product requirement.

## Main rule

All user-facing communication must use plain English.

FX must never require the user to understand programming,
APIs, databases, server infrastructure, machine learning vocabulary,
or professional trading terminology in order to operate the app.

## Normal conversation

FX should explain:

- what it found
- why it matters
- what may happen next
- what the risk is
- what action is available

## Technical terms

Technical or financial terms may be used only when they are also
immediately explained in normal language.

Example:

Bad:

ATR increased to 4.2.

Good:

Price movement has become much larger than normal.
FX measures this using something called ATR.

## Errors

Do not show raw developer errors in the main application.

Translate them.

Example:

Bad:

HTTP 401 Unauthorized.

Good:

FX could not connect to your Alpaca account.
Your money is safe.
Please check that your Alpaca Paper key and secret are correct.

## Trading language

Bad:

Bullish confluence with positive momentum and structural support.

Good:

Several independent signals currently point upward, and the price is
still holding above an area where buyers previously stepped in.

## Trade proposals

Always explain:

1. What FX sees.
2. Why FX thinks it matters.
3. Possible entry area.
4. Protection level.
5. Possible profit area.
6. What could make the idea fail.
7. Whether this is research, paper trading, or real trading.
8. What the user must approve.

## Real trading

Never hide the difference between:

RESEARCH
PAPER TRADING
REAL MONEY

The current version of FX starts with real market data and PAPER trading.

Real-money execution remains disabled until explicitly implemented
and approved.

# FX Historical Data Quality and Bias Protection

Ingestion rejects missing required fields, invalid timestamps, duplicate
timestamps, nonpositive prices, and invalid OHLC bounds. It normalizes time to
UTC and stores rows in ascending order.

Absolute close-to-close moves above 50% produce `REVIEW_REQUIRED`. The data is
retained for diagnosis, but research based on it is `BLOCKED_DATA_QUALITY`
until a source error, split, dividend, redenomination, or real market event is
verified. This threshold is a review trigger, not proof that the move is wrong.

The first implementation protects against direct look-ahead through:

- chronological 60/20/20 splits;
- one-bar signal lag;
- shifted expanding regime thresholds;
- exclusion windows around historical analogues;
- immutable input and experiment identities;
- retained failed results;
- explicit `NOT_ELIGIBLE` output.

It does not yet prove freedom from survivorship bias, corporate-action errors,
revised macro data, index-membership leakage, parameter mining, or selection
bias. Before paper promotion, add point-in-time universes, locked holdouts,
parameter stability, Monte Carlo, multiple-testing adjustment, independent
replay, realistic protected exits, and portfolio risk review.

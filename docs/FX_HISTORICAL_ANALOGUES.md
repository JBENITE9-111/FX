# FX Historical Analogues

The analogue engine compares the latest daily market state with earlier states
using return, volatility, ATR percentage, trend-gap, and regime features. It
excludes observations too close to the current window, returns actual dates and
distances, and reports the full sampled forward-outcome distribution including
the worst result.

Analogues are context, never a forecast or an executable signal. Small samples,
structural market change, missing news, spreads, and liquidity can make an
apparently close match misleading. Ask FX and the supervisor may explain this
evidence only when they cite the artifact ID, observation date, sample size,
and limitations.

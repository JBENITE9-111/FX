# FX Historical Data Sources

## Integrated

| Source | Current use | Authority | Retention status |
|---|---|---|---|
| London Strategic Edge | Multi-asset candles and catalog | Primary research provider | Local rights must be verified against the owner's provider agreement; redistribution is prohibited |

The source registry records licensing separately from data quality. A passing
OHLC check does not grant storage or redistribution rights.

## Available in the application but not retained by Market Memory

- OpenBB research integrations
- broker and exchange adapters configured elsewhere in FX
- macro, filing, news, and journal sources used by the grounded research layer

These are not described as historical coverage until a versioned adapter,
license record, timestamp policy, and immutable artifact have been verified.

## Highest-value additions

1. Official revision-aware macro series and release vintages.
2. Split/dividend-adjusted equities with security-master identifiers and
   delisting history.
3. Bid/ask or quote history for realistic spread and fill testing.
4. CFTC positioning and central-bank/rates history for Forex.
5. Exchange-native crypto trades, funding, open interest, and liquidation data.

Institutional tick/order-book/options datasets should be added only when their
incremental research value justifies cost and license restrictions. FX must not
fill unavailable history with synthetic facts.

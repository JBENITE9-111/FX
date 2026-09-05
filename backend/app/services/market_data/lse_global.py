import json
import os
import time
from pathlib import Path
from typing import Any

from lse import LSE, LSEError


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

CATALOG_FILE = (
    ROOT
    / "data"
    / "catalog"
    / "lse_catalog.json"
)

CATALOG_MAX_AGE_SECONDS = 60 * 60


class LSEGlobalMarketData:
    """
    London Strategic Edge research-data provider.

    This is research data.

    It is NOT the authority for real-money order execution.
    """

    def __init__(self) -> None:

        key = os.getenv(
            "LSE_API_KEY",
            "",
        ).strip()

        if not key:
            raise RuntimeError(
                "London Strategic Edge has not been connected."
            )

        self.client = LSE(
            api_key=key,
            timeout=60,
        )

    def _read_cached_catalog(
        self,
    ) -> list[dict[str, Any]] | None:

        if not CATALOG_FILE.exists():
            return None

        age = (
            time.time()
            - CATALOG_FILE.stat().st_mtime
        )

        if age > CATALOG_MAX_AGE_SECONDS:
            return None

        try:

            return json.loads(
                CATALOG_FILE.read_text()
            )

        except Exception:

            return None

    def _save_catalog(
        self,
        rows: list[dict[str, Any]],
    ) -> None:

        CATALOG_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        CATALOG_FILE.write_text(
            json.dumps(
                rows,
                indent=2,
                default=str,
            )
        )

    def catalog(
        self,
        refresh: bool = False,
    ) -> list[dict[str, Any]]:

        if not refresh:

            cached = (
                self._read_cached_catalog()
            )

            if cached is not None:
                return cached

        rows = self.client.catalog()

        self._save_catalog(rows)

        return rows

    def search(
        self,
        query: str = "",
        category: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        rows = self.catalog()

        query = (
            query
            .strip()
            .lower()
        )

        category_normalized = (
            category
            .strip()
            .lower()
            if category
            else None
        )

        results = []

        for row in rows:

            symbol = str(
                row.get(
                    "symbol",
                    "",
                )
            )

            name = str(
                row.get(
                    "name",
                    "",
                )
            )

            row_category = str(
                row.get(
                    "category",
                    "",
                )
            )

            dataset = str(
                row.get(
                    "dataset",
                    "",
                )
            )

            country = str(
                row.get(
                    "country",
                    "",
                )
            )

            if category_normalized:

                combined_category = (
                    row_category
                    + " "
                    + dataset
                ).lower()

                if (
                    category_normalized
                    not in combined_category
                ):
                    continue

            if query:

                searchable = (
                    symbol
                    + " "
                    + name
                    + " "
                    + row_category
                    + " "
                    + dataset
                    + " "
                    + country
                ).lower()

                if query not in searchable:
                    continue

            results.append({
                "symbol": symbol,
                "name": name,
                "category": row_category,
                "dataset": dataset,
                "country": country,
                "first": row.get("first"),
                "last": row.get("last"),
                "ticks": row.get("ticks"),
            })

            if len(results) >= limit:
                break

        return results

    def categories(
        self,
    ) -> list[dict[str, Any]]:

        rows = self.catalog()

        counts: dict[str, int] = {}

        for row in rows:

            category = (
                str(
                    row.get(
                        "category",
                        "Other",
                    )
                )
                .strip()
                or "Other"
            )

            counts[category] = (
                counts.get(
                    category,
                    0,
                )
                + 1
            )

        return [
            {
                "category": category,
                "count": count,
            }
            for category, count
            in sorted(
                counts.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

    def candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        dataset: str | None = None,
    ) -> list[dict[str, Any]]:

        kwargs: dict[str, Any] = {
            "limit": min(
                max(
                    int(limit),
                    1,
                ),
                5000,
            ),
            "order": "desc",
        }

        if dataset:
            kwargs["dataset"] = dataset

        rows = self.client.candles(
            symbol,
            timeframe,
            **kwargs,
        )

        # The API returns newest first when order=desc.
        # Charts are easier to use when oldest is first.
        return list(
            reversed(rows)
        )

    def latest(
        self,
        symbol: str,
        dataset: str | None = None,
    ) -> dict[str, Any] | None:

        rows = self.candles(
            symbol=symbol,
            timeframe="1m",
            limit=1,
            dataset=dataset,
        )

        if not rows:
            return None

        return rows[-1]

    def economic_calendar(
        self,
        region: str | None = None,
    ):

        kwargs = {}

        if region:
            kwargs["region"] = region

        return self.client.economic_calendar(
            **kwargs
        )

    def company_profile(
        self,
        symbol: str,
    ):

        return self.client.company_profiles(
            symbol
        )

    def fundamentals(
        self,
        symbol: str,
    ):

        return self.client.fundamentals(
            symbol
        )

    def financial_reports(
        self,
        symbol: str,
    ):

        return self.client.financial_reports(
            symbol
        )

    def insider_trades(
        self,
        symbol: str,
    ):

        return self.client.insider_trades(
            symbol
        )

    def dividends(
        self,
        symbol: str,
    ):

        return self.client.dividends(
            symbol
        )

    def splits(
        self,
        symbol: str,
    ):

        return self.client.splits(
            symbol
        )

    def options(
        self,
        underlying: str,
    ):

        return self.client.options(
            underlying
        )

    def option_flow(
        self,
        underlying: str | None = None,
    ):

        if underlying:

            return self.client.options_flow(
                underlying,
                limit=100,
            )

        return self.client.options_flow(
            limit=100
        )

    def macro_series(
        self,
        symbol: str,
    ):

        return self.client.series(
            symbol
        )

    def bond_yields(
        self,
        symbol: str,
    ):

        return self.client.bond_yields(
            symbol
        )

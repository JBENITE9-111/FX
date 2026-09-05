from __future__ import annotations

import httpx


CFTC_TFF = (
    "https://publicreporting.cftc.gov/"
    "resource/gpe5-46if.json"
)

OFR_BASE = (
    "https://data.financialresearch.gov/"
    "hf/v1"
)

FCA_CURRENT_SHORTS = (
    "https://www.fca.org.uk/publication/"
    "documents/"
    "aggregated-current-net-short-positions.csv"
)


class HedgeFundIntelligence:

    async def cftc_latest(
        self,
        limit: int = 100,
    ):

        params = {
            "$limit": min(
                max(limit, 1),
                1000,
            ),
            "$order": (
                "report_date_as_yyyy_mm_dd DESC"
            ),
        }

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.get(
                CFTC_TFF,
                params=params,
            )

            response.raise_for_status()

            return response.json()

    async def ofr_counterparties(
        self,
    ):

        url = (
            OFR_BASE
            + "/categories"
        )

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.get(
                url,
                params={
                    "category": (
                        "counterparties"
                    )
                },
            )

            response.raise_for_status()

            return {
                "content_type": (
                    response.headers
                    .get(
                        "content-type",
                        ""
                    )
                ),
                "data": (
                    response.text
                ),
            }

    async def fca_short_positions(
        self,
    ):

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                FCA_CURRENT_SHORTS
            )

            response.raise_for_status()

            return response.text

    def sources(
        self,
    ):

        return [
            {
                "name": (
                    "CFTC Traders in Financial Futures"
                ),
                "type": (
                    "Institutional futures positioning"
                ),
                "frequency": "Weekly",
                "status": "CONNECTED",
                "limitations": (
                    "Positions are aggregated categories, not a list of individual hedge-fund trades."
                ),
            },
            {
                "name": (
                    "FCA Aggregate Net Short Positions"
                ),
                "type": (
                    "UK short positioning"
                ),
                "frequency": "Daily",
                "status": "CONNECTED",
                "limitations": (
                    "Under the current UK regime individual short holders are anonymized."
                ),
            },
            {
                "name": (
                    "SEC Schedule 13D / 13G"
                ),
                "type": (
                    "Activist and beneficial ownership filings"
                ),
                "frequency": (
                    "Event driven"
                ),
                "status": (
                    "SOURCE REGISTERED · INGESTION NEXT"
                ),
                "limitations": (
                    "Regulatory disclosure is delayed and does not reveal intraday trading."
                ),
            },
            {
                "name": (
                    "OFR Hedge Fund Monitor"
                ),
                "type": (
                    "Leverage, prime brokers, counterparties, liquidity and systemic risk"
                ),
                "frequency": (
                    "Monthly / Quarterly"
                ),
                "status": "CONNECTED",
                "limitations": (
                    "Industry-level regulatory data, not individual fund order flow."
                ),
            },
        ]

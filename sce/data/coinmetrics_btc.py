from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlencode
from urllib.request import Request, urlopen


COMMUNITY_API = "https://community-api.coinmetrics.io/v4"
DEFAULT_METRICS = ("PriceUSD",)


@dataclass(frozen=True)
class CoinMetricsConfig:
    asset: str = "btc"
    metrics: tuple[str, ...] = DEFAULT_METRICS
    frequency: str = "1d"
    start_time: str = "2010-07-17"
    end_time: str | None = None
    page_size: int = 10000


def build_asset_metrics_url(config: CoinMetricsConfig) -> str:
    params = {
        "assets": config.asset,
        "metrics": ",".join(config.metrics),
        "frequency": config.frequency,
        "start_time": config.start_time,
        "page_size": str(config.page_size),
        "paging_from": "start",
    }
    if config.end_time:
        params["end_time"] = config.end_time
    return f"{COMMUNITY_API}/timeseries/asset-metrics?{urlencode(params)}"


def fetch_coinmetrics_daily(config: CoinMetricsConfig = CoinMetricsConfig()) -> list[dict]:
    """Fetch Community API rows, following Coin Metrics pagination.

    Network access is explicit: importing the module never downloads data.
    """
    url: str | None = build_asset_metrics_url(config)
    rows: list[dict] = []
    while url:
        request = Request(url, headers={"User-Agent": "sce-core/bitcoin-temporal-field"})
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed documented provider
            payload = json.loads(response.read().decode("utf-8"))
        rows.extend(payload.get("data", []))
        url = payload.get("next_page_url")
    return rows


def normalize_price_rows(rows: list[dict]) -> list[dict]:
    normalized = []
    for row in rows:
        price = row.get("PriceUSD")
        if price in (None, ""):
            continue
        normalized.append(
            {
                "time": row["time"],
                "price_usd": float(price),
                "source": "coinmetrics-community",
                "asset": row.get("asset", "btc"),
            }
        )
    normalized.sort(key=lambda item: item["time"])
    return normalized


def rows_to_csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["time", "price_usd", "source", "asset"])
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def provenance(config: CoinMetricsConfig, rows: list[dict]) -> dict:
    return {
        "provider": "Coin Metrics Community API",
        "endpoint": "/v4/timeseries/asset-metrics",
        "asset": config.asset,
        "metrics": list(config.metrics),
        "frequency": config.frequency,
        "requested_start": config.start_time,
        "requested_end": config.end_time,
        "retrieved_rows": len(rows),
        "first_observation": rows[0]["time"] if rows else None,
        "last_observation": rows[-1]["time"] if rows else None,
        "timezone": "UTC",
        "retrieved_on": date.today().isoformat(),
        "license_note": "Community data: verify current Coin Metrics terms before redistribution or commercial use.",
    }

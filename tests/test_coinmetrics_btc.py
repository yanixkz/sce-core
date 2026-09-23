from __future__ import annotations

from sce.data.coinmetrics_btc import (
    CoinMetricsConfig,
    build_asset_metrics_url,
    normalize_price_rows,
    provenance,
    rows_to_csv,
)


def test_build_url_is_explicit_and_causal():
    url = build_asset_metrics_url(CoinMetricsConfig(start_time="2012-01-01", end_time="2012-02-01"))
    assert "community-api.coinmetrics.io/v4/timeseries/asset-metrics" in url
    assert "assets=btc" in url
    assert "metrics=PriceUSD" in url
    assert "frequency=1d" in url
    assert "start_time=2012-01-01" in url
    assert "end_time=2012-02-01" in url
    assert "paging_from=start" in url


def test_normalization_drops_missing_price_and_sorts():
    rows = [
        {"asset": "btc", "time": "2011-01-03T00:00:00Z", "PriceUSD": "0.31"},
        {"asset": "btc", "time": "2011-01-01T00:00:00Z", "PriceUSD": "0.30"},
        {"asset": "btc", "time": "2011-01-02T00:00:00Z", "PriceUSD": None},
    ]
    normalized = normalize_price_rows(rows)
    assert [row["time"] for row in normalized] == [
        "2011-01-01T00:00:00Z",
        "2011-01-03T00:00:00Z",
    ]
    assert normalized[0]["price_usd"] == 0.30


def test_csv_contract_and_provenance():
    config = CoinMetricsConfig(start_time="2011-01-01")
    rows = normalize_price_rows(
        [{"asset": "btc", "time": "2011-01-01T00:00:00Z", "PriceUSD": "0.30"}]
    )
    csv_text = rows_to_csv(rows)
    meta = provenance(config, rows)
    assert csv_text.startswith("time,price_usd,source,asset")
    assert meta["provider"] == "Coin Metrics Community API"
    assert meta["first_observation"] == "2011-01-01T00:00:00Z"
    assert meta["timezone"] == "UTC"

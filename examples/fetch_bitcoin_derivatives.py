from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://community-api.coinmetrics.io/v4"
UA = {"User-Agent": "sce-research/1.0"}


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def paged(path: str, params: dict) -> list[dict]:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    rows: list[dict] = []
    while url:
        payload = fetch_json(url)
        rows.extend(payload.get("data", []))
        url = payload.get("next_page_url")
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    keys = sorted({k for row in rows for k in row})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path("data/bitcoin/derivatives")
    root.mkdir(parents=True, exist_ok=True)
    market = "binance-BTCUSDT-future"
    report = {"provider": "Coin Metrics Community API", "market": market, "layers": {}}

    jobs = [
        ("funding", "/timeseries/market-funding-rates",
         {"markets": market, "start_time": "2020-01-01", "paging_from": "start", "page_size": 10000}),
        ("open_interest", "/timeseries/market-openinterest",
         {"markets": market, "start_time": "2020-01-01", "paging_from": "start", "page_size": 10000, "granularity": "1h"}),
    ]

    for name, endpoint, params in jobs:
        try:
            rows = paged(endpoint, params)
            write_csv(rows, root / f"{name}.csv")
            report["layers"][name] = {
                "rows": len(rows),
                "start": rows[0].get("time") if rows else None,
                "end": rows[-1].get("time") if rows else None,
            }
        except Exception as exc:
            report["layers"][name] = {"error": repr(exc)}

    try:
        rows = paged("/timeseries/market-metrics", {
            "markets": market,
            "metrics": "liquidations_reported_future_buy_usd_1h,liquidations_reported_future_sell_usd_1h",
            "frequency": "1h",
            "start_time": "2020-01-01",
            "paging_from": "start",
            "page_size": 10000,
        })
        write_csv(rows, root / "liquidations.csv")
        report["layers"]["liquidations"] = {
            "rows": len(rows),
            "start": rows[0].get("time") if rows else None,
            "end": rows[-1].get("time") if rows else None,
        }
    except Exception as exc:
        report["layers"]["liquidations"] = {"error": repr(exc)}

    (root / "provenance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

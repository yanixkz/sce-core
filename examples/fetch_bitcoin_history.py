from __future__ import annotations

import argparse
import json
from pathlib import Path

from sce.data.coinmetrics_btc import (
    CoinMetricsConfig,
    fetch_coinmetrics_daily,
    normalize_price_rows,
    provenance,
    rows_to_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Bitcoin daily PriceUSD from Coin Metrics Community API.")
    parser.add_argument("--start", default="2010-07-17")
    parser.add_argument("--end", default=None)
    parser.add_argument("--out", type=Path, default=Path("data/bitcoin/btc_priceusd_1d.csv"))
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("data/bitcoin/btc_priceusd_1d.provenance.json"),
    )
    args = parser.parse_args()

    config = CoinMetricsConfig(start_time=args.start, end_time=args.end)
    raw = fetch_coinmetrics_daily(config)
    rows = normalize_price_rows(raw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rows_to_csv(rows), encoding="utf-8")
    args.provenance.write_text(
        json.dumps(provenance(config, rows), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} rows to {args.out}")
    if rows:
        print(f"Coverage: {rows[0]['time']} -> {rows[-1]['time']}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sce.data.coinbase_btc import fetch_candles
from sce.research.bitcoin_forecast_lab import BAR_SECONDS, backtest, issue, read_close_csv, settle


def recent_rows(now):
    candles = fetch_candles(900, (now-timedelta(hours=30)).isoformat(), now.isoformat())
    return [(x.time, x.close) for x in candles]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("backtest", "issue", "settle"))
    parser.add_argument("--csv", default="data/bitcoin/coinbase/btc_usd_15m.csv")
    parser.add_argument("--out", default="data/bitcoin/coinbase/forecast_lab")
    parser.add_argument("--record")
    parser.add_argument("--wait-for-boundary", action="store_true")
    args = parser.parse_args()
    root = Path(args.out)
    if args.mode == "backtest":
        result = backtest(read_close_csv(args.csv))
        root.mkdir(parents=True, exist_ok=True)
        (root/"retrospective_backtest.json").write_text(json.dumps(result, indent=2)+"\n")
    else:
        if args.mode == "issue" and args.wait_for_boundary:
            now = datetime.now(timezone.utc)
            wait = BAR_SECONDS-int(now.timestamp())%BAR_SECONDS+40
            time.sleep(wait)
        now = datetime.now(timezone.utc)
        rows = recent_rows(now)
        if args.mode == "issue":
            result = issue(rows, datetime.now(timezone.utc), root, os.environ.get("GITHUB_RUN_ID"))
        else:
            if not args.record:
                parser.error("--record is required for settle")
            record = json.loads(Path(args.record).read_text())
            result = settle(record, rows, datetime.now(timezone.utc), root)
        if result is None:
            print("Target candle not complete; no settlement created")
            return
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

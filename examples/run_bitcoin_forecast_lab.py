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
        if args.mode == "settle" and args.wait_for_boundary:
            if not args.record:
                parser.error("--record is required for settle")
            pending = json.loads(Path(args.record).read_text())
            final_target = max(datetime.fromisoformat(f["target_bar_close"])
                               for f in pending["forecasts"].values())
            time.sleep(max(0, (final_target+timedelta(seconds=90)-datetime.now(timezone.utc)).total_seconds()))
        now = datetime.now(timezone.utc)
        if args.mode == "issue":
            for attempt in range(9 if args.wait_for_boundary else 1):
                rows = recent_rows(datetime.now(timezone.utc))
                try:
                    result = issue(rows, datetime.now(timezone.utc), root, os.environ.get("GITHUB_RUN_ID"))
                    break
                except ValueError as exc:
                    if not args.wait_for_boundary or attempt == 8 or "not fresh" not in str(exc):
                        raise
                    time.sleep(20)
        else:
            if not args.record:
                parser.error("--record is required for settle")
            record = json.loads(Path(args.record).read_text())
            for attempt in range(12 if args.wait_for_boundary else 1):
                rows = recent_rows(datetime.now(timezone.utc))
                result = settle(record, rows, datetime.now(timezone.utc), root)
                if result is not None:
                    break
                if args.wait_for_boundary and attempt < 11:
                    time.sleep(20)
        if result is None:
            print("Target candle not complete; no settlement created")
            return
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""One idempotent prospective cycle for a separate forecast-ledger branch."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median

from sce.data.coinbase_btc import fetch_candles
from sce.data.coinbase_microstructure import fetch_snapshot
from sce.research.bitcoin_forecast_lab import BAR_SECONDS, issue, settle, immutable_json


def cycle(ledger: Path, rows, now: datetime, snapshot_provider=fetch_snapshot, run_id=None,
          volume_sample=None):
    now=now.astimezone(timezone.utc)
    ledger.mkdir(parents=True,exist_ok=True)
    pending=0;settled=0
    for path in sorted((ledger/"forecasts").glob("*.json")):
        record=json.loads(path.read_text())
        if (ledger/"outcomes"/path.name).exists():continue
        pending+=1
        if max(datetime.fromisoformat(x["target_bar_close"]) for x in record["forecasts"].values())>=now:
            continue
        result=settle(record,rows,now,ledger)
        if result is not None:settled+=1
    eligible=[t for t,p in rows if t+timedelta(seconds=BAR_SECONDS)<=now]
    last_close=eligible[-1]+timedelta(seconds=BAR_SECONDS) if eligible else None
    # At most one snapshot per observed bar for this frozen baseline version.
    existing=any(json.loads(p.read_text()).get("observed_bar_close")==last_close.isoformat()
                 for p in (ledger/"forecasts").glob("*.json")) if last_close else False
    new_id=None;reason=None
    if existing:
        reason="already_recorded"
    elif last_close is None or (now-last_close).total_seconds()>=600:
        reason="no_fresh_completed_bar"
    else:
        try:
            snapshot=snapshot_provider()
            if not isinstance(snapshot,dict):raise ValueError("invalid microstructure snapshot")
        except Exception as exc:
            snapshot={"status":"UNAVAILABLE","error_type":type(exc).__name__,
                      "note":"microstructure sample missing; price-only forecast still issued"}
        if volume_sample is not None:
            snapshot["candle_volume"] = volume_sample
        # The snapshot is collected before the issue timestamp; the frozen
        # price-only baseline does not depend on it.
        record=issue(rows,datetime.now(timezone.utc) if run_id else now,ledger,run_id)
        new_id=record["forecast_id"]
        immutable_json(ledger/"snapshots"/f"{new_id}.json",snapshot)
    return {"issued":new_id,"settled":settled,"pending":pending,"skip_reason":reason}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--ledger",required=True)
    args=ap.parse_args()
    now=datetime.now(timezone.utc)
    candles=fetch_candles(900,(now-timedelta(hours=30)).isoformat(),now.isoformat())
    complete=[c for c in candles if c.time+timedelta(seconds=BAR_SECONDS)<=now]
    volume_sample=None
    if len(complete)>=97:
        typical=median(c.volume for c in complete[-97:-1])
        volume_sample={"last_closed_btc":complete[-1].volume,
                       "prior_96_median_btc":typical,
                       "relative_to_median":complete[-1].volume/typical if typical else None,
                       "bar_open":complete[-1].time.isoformat()}
    result=cycle(Path(args.ledger),[(c.time,c.close) for c in candles],datetime.now(timezone.utc),
                 run_id=os.environ.get("GITHUB_RUN_ID"),volume_sample=volume_sample)
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()

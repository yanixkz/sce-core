from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
from sce.data.binance_btc import INTERVALS, fetch_range, normalized_rows, to_csv

def ms(s): return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",default="BTCUSDT")
    p.add_argument("--start",default="2025-01-01T00:00:00Z")
    p.add_argument("--end",default=datetime.now(timezone.utc).isoformat())
    p.add_argument("--out",default="data/bitcoin/btc_binance_multiscale.csv")
    args=p.parse_args()
    rows=[]
    for scale in INTERVALS:
        raw=fetch_range(args.symbol,scale,ms(args.start),ms(args.end))
        part=normalized_rows(raw,scale); rows.extend(part)
        print(scale,len(part))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(to_csv(rows))
    print("wrote",len(rows),"rows",out)
if __name__=="__main__":main()

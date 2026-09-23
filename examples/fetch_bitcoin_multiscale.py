from __future__ import annotations
import argparse, csv, io, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path
from sce.data.binance_btc import INTERVALS, fetch_range, normalized_rows, to_csv

def ms(s): return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)

def vision_month(symbol, interval, year, month):
    url=f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02d}.zip"
    with urllib.request.urlopen(url,timeout=60) as r:
        data=r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name=z.namelist()[0]
        rows=list(csv.reader(io.TextIOWrapper(z.open(name))))
    return rows

def fetch_vision_range(symbol, interval, start, end):
    cur=datetime(start.year,start.month,1,tzinfo=timezone.utc); raw=[]
    while cur <= end:
        try: raw.extend(vision_month(symbol,interval,cur.year,cur.month))
        except Exception as exc:
            print("vision skip",interval,cur.year,cur.month,type(exc).__name__)
        cur=datetime(cur.year+(cur.month==12),1 if cur.month==12 else cur.month+1,1,tzinfo=timezone.utc)
    lo,hi=int(start.timestamp()*1000),int(end.timestamp()*1000)
    return [r for r in raw if lo <= int(r[0]) <= hi]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",default="BTCUSDT")
    p.add_argument("--start",default="2025-01-01T00:00:00Z")
    p.add_argument("--end",default=datetime.now(timezone.utc).isoformat())
    p.add_argument("--out",default="data/bitcoin/btc_binance_multiscale.csv")
    args=p.parse_args()
    rows=[]
    for scale in INTERVALS:
        try:
            raw=fetch_range(args.symbol,scale,ms(args.start),ms(args.end))
        except Exception as exc:
            print("REST unavailable; using Binance Vision",scale,type(exc).__name__)
            raw=fetch_vision_range(args.symbol,scale,datetime.fromisoformat(args.start.replace("Z","+00:00")),datetime.fromisoformat(args.end.replace("Z","+00:00")))
        part=normalized_rows(raw,scale); rows.extend(part)
        print(scale,len(part))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(to_csv(rows))
    print("wrote",len(rows),"rows",out)
if __name__=="__main__":main()

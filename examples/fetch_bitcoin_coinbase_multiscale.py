from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse, json
from sce.data.coinbase_btc import NATIVE, fetch_candles, resample, to_csv

def chunks(start,end,days):
    x=start
    while x<end:
        y=min(end,x+timedelta(days=days));yield x,y;x=y

def main():
    p=argparse.ArgumentParser();p.add_argument("--start",default="2017-01-01");p.add_argument("--end",default=None)
    p.add_argument("--out",default="data/bitcoin/coinbase");a=p.parse_args()
    start=datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc)
    end=datetime.fromisoformat(a.end).replace(tzinfo=timezone.utc) if a.end else datetime.now(timezone.utc)
    root=Path(a.out);root.mkdir(parents=True,exist_ok=True);meta={}
    allsets={}
    # <=300 candles/request: conservative chunk sizes.
    for name,sec in NATIVE.items():
        days=max(1,int(280*sec/86400));rows=[]
        for x,y in chunks(start,end,days):
            rows.extend(fetch_candles(sec,x.isoformat(),y.isoformat()))
        uniq={r.time:r for r in rows};rows=[uniq[k] for k in sorted(uniq)]
        allsets[name]=rows;(root/f"btc_usd_{name}.csv").write_text(to_csv(rows))
        meta[name]={"rows":len(rows),"start":rows[0].time.isoformat() if rows else None,"end":rows[-1].time.isoformat() if rows else None}
    four=resample(allsets["1h"],14400);(root/"btc_usd_4h.csv").write_text(to_csv(four))
    meta["4h"]={"rows":len(four),"start":four[0].time.isoformat() if four else None,"end":four[-1].time.isoformat() if four else None,"derived_from":"1h"}
    (root/"provenance.json").write_text(json.dumps({"provider":"Coinbase Exchange BTC-USD","fetched_at":datetime.now(timezone.utc).isoformat(),"coverage":meta},indent=2))
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()

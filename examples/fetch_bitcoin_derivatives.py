from __future__ import annotations
import csv,json,urllib.parse,urllib.request
from pathlib import Path
BASE="https://community-api.coinmetrics.io/v4"

def get(path,params):
    url=BASE+path+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"sce-research/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def paged(path,params):
    out=[];url=None
    while True:
        data=get(path,params) if url is None else json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"sce-research/1.0"}),timeout=60))
        out.extend(data.get("data",[]));url=data.get("next_page_url")
        if not url:break
    return out

def write(rows,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:return
    keys=sorted({k for r in rows for k in r})
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def main():
    root=Path("data/bitcoin/derivatives")\n    root.mkdir(parents=True,exist_ok=True)
    market="binance-BTCUSDT-future"
    report={"provider":"Coin Metrics Community API","market":market,"layers":{}}
    jobs=[
      ("funding","/timeseries/market-funding-rates",{"markets":market,"start_time":"2020-01-01","paging_from":"start","page_size":10000}),
      ("open_interest","/timeseries/market-openinterest",{"markets":market,"start_time":"2020-01-01","paging_from":"start","page_size":10000,"granularity":"1h"}),
    ]
    for name,path,params in jobs:
        try:
            rows=paged(path,params);write(rows,root/f"{name}.csv")
            report["layers"][name]={"rows":len(rows),"start":rows[0].get("time") if rows else None,"end":rows[-1].get("time") if rows else None}
        except Exception as e: report["layers"][name]={"error":str(e)}
    # Community availability probe for market metrics; exact metric access varies by entitlement.
    metrics="liquidations_reported_future_buy_usd_1h,liquidations_reported_future_sell_usd_1h"
    try:
        rows=paged("/timeseries/market-metrics",{"markets":market,"metrics":metrics,"frequency":"1h","start_time":"2020-01-01","paging_from":"start","page_size":10000})
        write(rows,root/"liquidations.csv");report["layers"]["liquidations"]={"rows":len(rows),"start":rows[0].get("time") if rows else None,"end":rows[-1].get("time") if rows else None}
    except Exception as e: report["layers"]["liquidations"]={"error":str(e)}
    (root/"provenance.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=="__main__":main()

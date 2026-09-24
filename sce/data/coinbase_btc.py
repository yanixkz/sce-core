from __future__ import annotations
import csv, io, json, urllib.request, urllib.error, time, random
from dataclasses import dataclass
from datetime import datetime, timezone

BASE="https://api.exchange.coinbase.com/products/BTC-USD/candles"
# Coinbase native granularities; 4h is derived causally from 1h.
NATIVE={"15m":900,"1h":3600,"1d":86400}

@dataclass(frozen=True)
class Candle:
    time: datetime; low: float; high: float; open: float; close: float; volume: float

def fetch_candles(granularity:int,start:str,end:str):
    url=f"{BASE}?granularity={granularity}&start={start}&end={end}"
    req=urllib.request.Request(url,headers={"User-Agent":"sce-core-research/1.0"})
    raw=None\n    for attempt in range(8):\n        try:\n            with urllib.request.urlopen(req,timeout=30) as r: raw=json.load(r)\n            break\n        except urllib.error.HTTPError as e:\n            if e.code != 429 or attempt == 7: raise\n            time.sleep(min(60, 2 ** attempt) + random.random())\n    time.sleep(0.35)
    out=[Candle(datetime.fromtimestamp(x[0],timezone.utc),*map(float,x[1:])) for x in raw]
    return sorted(out,key=lambda x:x.time)

def resample(candles, seconds:int):
    groups={}
    for c in candles:
        k=int(c.time.timestamp())//seconds*seconds
        groups.setdefault(k,[]).append(c)
    out=[]
    for k,xs in sorted(groups.items()):
        out.append(Candle(datetime.fromtimestamp(k,timezone.utc),min(x.low for x in xs),
            max(x.high for x in xs),xs[0].open,xs[-1].close,sum(x.volume for x in xs)))
    return out

def to_csv(candles):
    s=io.StringIO();w=csv.writer(s);w.writerow(["time","open","high","low","close","volume"])
    for c in candles:w.writerow([c.time.isoformat(),c.open,c.high,c.low,c.close,c.volume])
    return s.getvalue()

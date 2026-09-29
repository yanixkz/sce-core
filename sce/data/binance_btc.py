from __future__ import annotations
import csv, io, json, urllib.parse, urllib.request
from datetime import datetime, timezone

BASES=("https://api.binance.com/api/v3/klines","https://api1.binance.com/api/v3/klines","https://api2.binance.com/api/v3/klines","https://api3.binance.com/api/v3/klines","https://api4.binance.com/api/v3/klines")
INTERVALS=("1m","5m","15m","30m","1h","4h","1d","1w","1M")

def fetch_klines(symbol="BTCUSDT", interval="1m", start_ms=None, end_ms=None, limit=1000):
    if interval not in INTERVALS: raise ValueError(f"unsupported interval: {interval}")
    params={"symbol":symbol,"interval":interval,"limit":min(limit,1000)}
    if start_ms is not None: params["startTime"]=int(start_ms)
    if end_ms is not None: params["endTime"]=int(end_ms)
    last=None
    for base in BASES:
        req=urllib.request.Request(base+"?"+urllib.parse.urlencode(params),headers={"User-Agent":"sce-core/bitcoin-research"})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
        except Exception as exc:
            last=exc
    raise last

def fetch_range(symbol, interval, start_ms, end_ms):
    rows=[]; cursor=int(start_ms)
    while cursor <= end_ms:
        batch=fetch_klines(symbol,interval,cursor,end_ms,1000)
        if not batch: break
        rows.extend(batch)
        nxt=int(batch[-1][0])+1
        if nxt<=cursor: break
        cursor=nxt
        if len(batch)<1000: break
    return rows

def normalized_rows(raw, scale):
    return [{"time":datetime.fromtimestamp(int(r[0])/1000,tz=timezone.utc).isoformat().replace("+00:00","Z"),
             "scale":scale,"open":float(r[1]),"high":float(r[2]),"low":float(r[3]),"close":float(r[4]),
             "volume":float(r[5]),"close_time_ms":int(r[6])} for r in raw]

def to_csv(rows):
    out=io.StringIO(); fields=("time","scale","open","high","low","close","volume","close_time_ms")
    w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows(rows);return out.getvalue()

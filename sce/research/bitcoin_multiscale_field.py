from __future__ import annotations
import csv, io, math
from collections import defaultdict
from statistics import fmean, pstdev

WINDOWS={"1m":240,"5m":192,"15m":160,"30m":144,"1h":120,"4h":90,"1d":60,"1w":40,"1M":24}

def parse_multiscale_csv(text):
    out=[]
    for r in csv.DictReader(io.StringIO(text)):
        out.append({**r,"open":float(r["open"]),"high":float(r["high"]),"low":float(r["low"]),"close":float(r["close"]),"volume":float(r["volume"])})
    return out

def build_scale_states(rows):
    """Causal per-scale state rows for propagation analysis."""
    grouped=defaultdict(list)
    for r in rows: grouped[r["scale"]].append(r)
    out=[]
    for scale,seq in grouped.items():
        seq.sort(key=lambda r:r["time"]); w=WINDOWS[scale]
        closes=[]; returns=[]
        for r in seq:
            c=r["close"]
            if closes: returns.append(math.log(c/closes[-1]))
            closes.append(c)
            if len(closes)<max(12,w//4): continue
            long=closes[-w:] if len(closes)>=w else closes[:]
            short=long[-max(6,len(long)//4):]
            trend=math.log(c/long[0]) if long[0]>0 else 0
            momentum=math.log(c/short[0]) if short[0]>0 else 0
            rv=returns[-min(len(returns),max(10,w//2)):]
            vol=pstdev(rv) if len(rv)>1 else 0
            lo,hi=min(long),max(long); pos=(c-lo)/(hi-lo) if hi>lo else .5
            dd=max(0,1-c/max(long))
            direction=max(-1,min(1,.6*(trend/.20)+.4*(momentum/.10)))
            disturbance=max(0,min(1,vol/.04 + dd))
            stability=max(0,min(1,.5*abs(direction)+.25*(1-abs(pos-.5)*2)+.25*(1-disturbance)))
            out.append({"time":r["time"],"scale":scale,"price":c,"trend":round(direction,4),
                        "volatility":round(min(1,vol/.04),4),"drawdown_pressure":round(min(1,dd),4),
                        "stability":round(stability,4),"transition_pressure":round(1-stability,4)})
    return out

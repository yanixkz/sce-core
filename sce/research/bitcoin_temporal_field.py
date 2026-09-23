from __future__ import annotations
import csv, io
from dataclasses import dataclass
from datetime import datetime
from math import log, sqrt
from statistics import fmean, pstdev
from sce.scenarios.bitcoin_temporal_field import TemporalObservation, cross_scale_coherence, directional_state, observation_stability, transition_pressure

SCALES={"1d":1,"1w":7,"1m":30}
@dataclass(frozen=True)
class PricePoint:
    time: datetime
    price: float

def parse_price_csv(text):
    rows=[]
    for row in csv.DictReader(io.StringIO(text)):
        rows.append(PricePoint(datetime.fromisoformat(row["time"].replace("Z","+00:00")),float(row["price_usd"])))
    return sorted(rows,key=lambda x:x.time)

def _signed(x): return max(-1.0,min(1.0,x))
def _unit(x): return max(0.0,min(1.0,x))
def _ret(a,b): return log(b/a) if a>0 and b>0 else 0.0
def _window(points,end,days):
    cutoff=points[end].time.timestamp()-days*86400
    return [p for p in points[:end+1] if p.time.timestamp()>=cutoff]

def build_price_observation(points,end,scale):
    days=SCALES[scale]; short=_window(points,end,max(3*days,7)); long=_window(points,end,max(12*days,30))
    if len(short)<2 or len(long)<3:return None
    price=points[end].price
    trend=_signed(_ret(long[0].price,price)/0.35); momentum=_signed(_ret(short[0].price,price)/0.18)
    returns=[_ret(long[i-1].price,long[i].price) for i in range(1,len(long))]
    volatility=_unit((pstdev(returns) if len(returns)>1 else 0.0)*sqrt(365)/1.5)
    peak=max(p.price for p in long); trough=min(p.price for p in long)
    drawdown=_unit((1-price/peak)/0.7 if peak else 0.0)
    position=0.5 if peak==trough else _unit((price-trough)/(peak-trough))
    return TemporalObservation(points[end].time.isoformat().replace("+00:00","Z"),scale,round(trend,6),round(momentum,6),round(volatility,6),round(drawdown,6),round(position,6),0.0)

def build_temporal_field(points,scales=("1d","1w","1m")):
    cells=[]; timeline=[]
    for end,point in enumerate(points):
        obs=[o for scale in scales if (o:=build_price_observation(points,end,scale)) is not None]
        if not obs:continue
        timeline.append({"time":obs[0].timestamp,"price_usd":point.price,"coherence":cross_scale_coherence(obs),"transition_pressure":transition_pressure(obs),"mean_stability":round(fmean(observation_stability(o) for o in obs),4)})
        for o in obs:
            cells.append({"time":o.timestamp,"scale":o.scale,"regime":directional_state(o),"stability":observation_stability(o),"trend":o.trend,"momentum":o.momentum,"volatility":o.volatility,"drawdown_pressure":o.drawdown_pressure,"range_position":o.range_position})
    return {"field":"F(t, tau)","empirical":True,"source_layer":"daily PriceUSD","scales":list(scales),"timeline":timeline,"cells":cells}

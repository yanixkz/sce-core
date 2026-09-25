from __future__ import annotations
from dataclasses import dataclass
from math import prod

@dataclass(frozen=True)
class SurfingConfig:
    train_days:int=730
    forward_days:int=20
    min_examples:int=8
    edge_threshold_pct:float=2.0
    fee_bps:float=10.0

FEATURES=("coherence","transition_pressure","mean_stability","price_return_5d_pct",
          "1d_trend","1w_trend","1m_trend","1d_momentum","1w_momentum","1m_momentum")

def _distance(a,b,scales):
    vals=[]
    for k in FEATURES:
        x,y=a.get(k),b.get(k)
        if x is None or y is None: continue
        s=scales.get(k,1.0) or 1.0
        vals.append(((x-y)/s)**2)
    return sum(vals)/len(vals) if vals else 1e9

def walk_forward_predictions(rows):
    out=[]
    for i,r in enumerate(rows):
        train=[x for x in rows[:i] if 20 <= (r["index"]-x["index"]) <= 730 and x.get("return_20d_pct") is not None]
        if len(train)<8: continue
        scales={}
        for k in FEATURES:
            v=[x.get(k) for x in train if x.get(k) is not None]
            if v: scales[k]=max(v)-min(v)
        neighbors=sorted(train,key=lambda x:_distance(r,x,scales))[:max(8,int(len(train)**.5))]
        edge=sum(x["return_20d_pct"] for x in neighbors)/len(neighbors)
        action=1 if edge>=2 else -1 if edge<=-2 else 0
        out.append({**r,"predicted_edge_pct":edge,"action":action,"neighbor_count":len(neighbors)})
    return out

def backtest_predictions(preds, fee_bps=10.0):
    """Non-overlapping 20-day trades entered only on causal alarm predictions."""
    trades=[]
    next_free=-1
    for r in preds:
        if r["action"]==0 or r["index"]<next_free:
            continue
        gross=r["action"]*r["return_20d_pct"]/100
        net=gross-2*fee_bps/10000
        trades.append({**r,"gross_return":gross,"net_return":net})
        next_free=r["index"]+20

    equity=1.0
    peak=1.0
    max_dd=0.0
    wins=0
    gp=0.0
    gl=0.0
    for t in trades:
        equity*=1+t["net_return"]
        peak=max(peak,equity)
        max_dd=min(max_dd,equity/peak-1)
        if t["net_return"]>0:
            wins+=1
        gp+=max(0,t["net_return"])
        gl+=min(0,t["net_return"])

    return {
        "trades":len(trades),
        "longs":sum(t["action"]==1 for t in trades),
        "shorts":sum(t["action"]==-1 for t in trades),
        "total_return_pct":(equity-1)*100,
        "win_rate":wins/len(trades) if trades else None,
        "max_drawdown_pct":max_dd*100,
        "profit_factor":gp/abs(gl) if gl else None,
        "fee_bps_per_side":fee_bps,
        "trade_records":trades,
    }

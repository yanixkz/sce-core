from __future__ import annotations
from statistics import median

LOOKBACKS=(3,5,10)
SCALES=("1d","1w","1m")

def _delta(series,i,n,key):
    j=i-n
    return None if j<0 else series[i][key]-series[j][key]

def _ret(series,i,n):
    j=i-n
    return None if j<0 else 100*(series[i]["price_usd"]/series[j]["price_usd"]-1)

def causal_alarm_features(field, alarm_responses):
    timeline=field["timeline"]; by_time={r["time"]:i for i,r in enumerate(timeline)}
    cells={(c["time"],c["scale"]):c for c in field["cells"]}
    out=[]
    for a in alarm_responses:
        i=by_time[a["time"]]; r=dict(a)
        for n in LOOKBACKS:
            r[f"coherence_delta_{n}d"]=_delta(timeline,i,n,"coherence")
            r[f"stability_delta_{n}d"]=_delta(timeline,i,n,"mean_stability")
            r[f"pressure_delta_{n}d"]=_delta(timeline,i,n,"transition_pressure")
            r[f"price_return_{n}d_pct"]=_ret(timeline,i,n)
        for s in SCALES:
            c=cells.get((a["time"],s))
            for k in ("regime","trend","momentum","volatility","drawdown_pressure","range_position","stability"):
                r[f"{s}_{k}"]=c.get(k) if c else None
        out.append(r)
    return out

def summarize_feature_separation(rows):
    groups={}
    for r in rows:
        key=(f"event_{r['from_regime']}_{r['to_regime']}" if r["associated_transition"] else "no_transition_30d")
        groups.setdefault(key,[]).append(r)
    keys=[f"{m}_delta_{n}d" for m in ("coherence","stability","pressure") for n in LOOKBACKS]
    keys += [f"price_return_{n}d_pct" for n in LOOKBACKS]
    keys += [f"{s}_{k}" for s in SCALES for k in ("regime","trend","momentum","volatility","drawdown_pressure","range_position","stability")]
    out={}
    for g,rs in groups.items():
        d={"alarms":len(rs)}
        for k in keys:
            vals=[r[k] for r in rs if r.get(k) is not None]
            d[f"median_{k}"]=median(vals) if vals else None
        out[g]=d
    return out

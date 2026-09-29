from __future__ import annotations
from statistics import fmean, median

def event_windows(field, events, radius_days=5):
    timeline=field["timeline"]
    by_time={r["time"]:i for i,r in enumerate(timeline)}
    out=[]
    for e in events:
        i=by_time.get(e["time"])
        if i is None: continue
        rows=[]
        for j in range(max(0,i-radius_days),min(len(timeline),i+radius_days+1)):
            r=timeline[j]
            rows.append({"offset":j-i,"time":r["time"],"price_usd":r.get("price_usd"),
                         "coherence":r["coherence"],"transition_pressure":r["transition_pressure"],
                         "mean_stability":r["mean_stability"]})
        out.append({"time":e["time"],"from_regime":e.get("from_regime"),"to_regime":e.get("to_regime"),"rows":rows})
    return out

def summarize_event_windows(windows):
    offsets=sorted({r["offset"] for w in windows for r in w["rows"]})
    trajectory=[]
    for off in offsets:
        rows=[r for w in windows for r in w["rows"] if r["offset"]==off]
        trajectory.append({"offset":off,"n":len(rows),
            "median_coherence":round(median(r["coherence"] for r in rows),4),
            "mean_coherence":round(fmean(r["coherence"] for r in rows),4),
            "median_transition_pressure":round(median(r["transition_pressure"] for r in rows),4),
            "median_mean_stability":round(median(r["mean_stability"] for r in rows),4)})
    return {"events":len(windows),"radius_days":5,"trajectory":trajectory}

def summarize_by_transition(windows):
    groups={}
    for w in windows:
        key=f'{w.get("from_regime")}->{w.get("to_regime")}'
        groups.setdefault(key,[]).append(w)
    return {k:summarize_event_windows(v) for k,v in groups.items()}

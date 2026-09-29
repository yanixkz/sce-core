from __future__ import annotations
from statistics import median

HORIZONS=(1,2,3,5,10,20,30)

def enrich_price_responses(price_responses, event_records):
    by_time={r["time"]:r for r in event_records}
    out=[]
    for r in price_responses:
        x=dict(r); ev=by_time.get(r["time"],{})
        x["detection"]=ev.get("classification","unknown")
        x["signal_time"]=ev.get("signal_time")
        x["lead_days"]=ev.get("lead_days")
        out.append(x)
    return out

def _median(rows,key):
    vals=[r[key] for r in rows if r.get(key) is not None]
    return round(median(vals),3) if vals else None

def summarize_signal_value(rows):
    groups={}
    for r in rows:
        key=f'{r.get("from_regime")}->{r.get("to_regime")}'
        groups.setdefault(key,[]).append(r)
    result={}
    for regime,items in groups.items():
        result[regime]={}
        for cls in ("hit","miss"):
            g=[r for r in items if r.get("detection")==cls]
            d={"events":len(g),"median_pre_5d_return_pct":_median(g,"pre_5d_return_pct"),
               "median_mfe_30d_pct":_median(g,"mfe_30d_pct"),"median_mae_30d_pct":_median(g,"mae_30d_pct"),
               "median_lead_days":_median(g,"lead_days")}
            for h in HORIZONS:
                d[f"median_return_{h}d_pct"]=_median(g,f"return_{h}d_pct")
            result[regime][cls]=d
    return result

def matched_controls(points, event_times, spacing_days=30):
    blocked=set()
    times=[(p.time.isoformat().replace("+00:00","Z") if hasattr(p,"time") else p["time"]) for p in points]
    event_idx={i for i,t in enumerate(times) if t in set(event_times)}
    for i in event_idx:
        blocked.update(range(max(0,i-spacing_days),min(len(points),i+spacing_days+1)))
    candidates=[i for i in range(5,len(points)-31) if i not in blocked]
    step=max(1,len(candidates)//max(1,len(event_idx)))
    return [{"time":times[i],"from_regime":"control","to_regime":"control"} for i in candidates[::step][:len(event_idx)]]

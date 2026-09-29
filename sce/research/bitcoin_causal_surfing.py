from __future__ import annotations
from statistics import median

HORIZONS=(1,3,5,10,20,30)
LEVELS=(.01,.02,.03,.05,.10)

def alarm_onsets(field, pressure_threshold=.65, coherence_threshold=.45):
    rows=field["timeline"]; out=[]; prev=False
    for i,r in enumerate(rows):
        active=r["transition_pressure"]>=pressure_threshold or r["coherence"]<=coherence_threshold
        if active and not prev:
            out.append({"index":i,"time":r["time"],"price_usd":r["price_usd"],
                        "coherence":r["coherence"],"transition_pressure":r["transition_pressure"],
                        "mean_stability":r["mean_stability"]})
        prev=active
    return out

def _pct(a,b): return 100*(b/a-1) if a else None

def causal_alarm_responses(field, events, horizon=30):
    rows=field["timeline"]; by_time={r["time"]:i for i,r in enumerate(rows)}
    event_indices=sorted((by_time[e["time"]],e) for e in events if e["time"] in by_time)
    out=[]
    for alarm in alarm_onsets(field):
        i=alarm["index"]
        if i+horizon>=len(rows): continue
        future=[(j,e) for j,e in event_indices if i<j<=i+horizon]
        next_event=future[0] if future else None
        p0=rows[i]["price_usd"]; path=[rows[j]["price_usd"] for j in range(i+1,i+horizon+1)]
        rec={**alarm,"associated_transition":bool(next_event),
             "event_time":next_event[1]["time"] if next_event else None,
             "from_regime":next_event[1]["from_regime"] if next_event else None,
             "to_regime":next_event[1]["to_regime"] if next_event else None,
             "days_to_event":next_event[0]-i if next_event else None,
             "mfe_30d_pct":max(_pct(p0,p) for p in path),"mae_30d_pct":min(_pct(p0,p) for p in path)}
        for h in HORIZONS: rec[f"return_{h}d_pct"]=_pct(p0,rows[i+h]["price_usd"])
        for level in LEVELS:
            n=int(level*100); up=down=None
            for d,p in enumerate(path,1):
                ret=p/p0-1
                if up is None and ret>=level: up=d
                if down is None and ret<=-level: down=d
            rec[f"up_{n}pct_day"]=up; rec[f"down_{n}pct_day"]=down
            rec[f"up_{n}pct_first"]=up is not None and (down is None or up<down)
            rec[f"down_{n}pct_first"]=down is not None and (up is None or down<up)
        out.append(rec)
    return out

def summarize_causal_alarms(records):
    groups={}
    for r in records:
        key=(("event_"+str(r["from_regime"])+"_"+str(r["to_regime"])) if r["associated_transition"] else "no_transition_30d")
        groups.setdefault(key,[]).append(r)
    result={}
    for key,rs in groups.items():
        d={"alarms":len(rs)}
        for h in HORIZONS:d[f"median_return_{h}d_pct"]=median(r[f"return_{h}d_pct"] for r in rs)
        d["median_mfe_30d_pct"]=median(r["mfe_30d_pct"] for r in rs);d["median_mae_30d_pct"]=median(r["mae_30d_pct"] for r in rs)
        if rs and rs[0]["associated_transition"]:d["median_days_to_event"]=median(r["days_to_event"] for r in rs)
        for level in LEVELS:
            n=int(level*100)
            d[f"up_{n}pct_first_rate"]=sum(r[f"up_{n}pct_first"] for r in rs)/len(rs)
            d[f"down_{n}pct_first_rate"]=sum(r[f"down_{n}pct_first"] for r in rs)/len(rs)
        result[key]=d
    return result

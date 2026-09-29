from __future__ import annotations
from statistics import median

def _alarm(row, pressure=.65, coherence=.45):
    return row["transition_pressure"] >= pressure or row["coherence"] <= coherence

def alarm_episodes(timeline, pressure=.65, coherence=.45):
    episodes=[]; start=None; end=None
    for i,row in enumerate(timeline):
        if _alarm(row,pressure,coherence):
            if start is None:start=i
            end=i
        elif start is not None:
            episodes.append((start,end)); start=end=None
    if start is not None:episodes.append((start,end))
    return episodes

def evaluate_by_era(field, events, eras, lookback_days=30, pressure=.65, coherence=.45):
    timeline=field["timeline"]; by_time={r["time"]:i for i,r in enumerate(timeline)}
    out=[]
    for name,start,end in eras:
        ev=[e for e in events if start <= e["time"][:10] <= end]
        hits=0; leads=[]; windows=set()
        for e in ev:
            idx=by_time.get(e["time"])
            if idx is None:continue
            a=max(0,idx-lookback_days)
            cand=[j for j in range(a,idx) if _alarm(timeline[j],pressure,coherence)]
            windows.update(range(a,idx+1))
            if cand:hits+=1;leads.append(idx-cand[-1])
        era_indices=[i for i,r in enumerate(timeline) if start <= r["time"][:10] <= end]
        alarms=[i for i in era_indices if _alarm(timeline[i],pressure,coherence)]
        false=sum(i not in windows for i in alarms)
        eps=[ep for ep in alarm_episodes(timeline,pressure,coherence) if ep[0] in set(era_indices)]
        false_eps=sum(not any(j in windows for j in range(a,b+1)) for a,b in eps)
        out.append({"era":name,"events":len(ev),"detected":hits,"recall":round(hits/len(ev),4) if ev else 0.0,
                    "median_lead_days":median(leads) if leads else None,"alarms":len(alarms),"false_alarm_days":false,
                    "alarm_episodes":len(eps),"false_alarm_episodes":false_eps})
    return out

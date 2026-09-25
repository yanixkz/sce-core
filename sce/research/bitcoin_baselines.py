from __future__ import annotations
from statistics import median

def _evaluate_flags(times, flags, events, lookback_days=30):
    by_time={t:i for i,t in enumerate(times)}
    hits=0; leads=[]; windows=set()
    for event in events:
        idx=by_time.get(event["time"])
        if idx is None: continue
        start=max(0,idx-lookback_days)
        candidates=[j for j in range(start,idx) if flags[j]]
        windows.update(range(start,idx+1))
        if candidates:
            hits+=1; leads.append(idx-candidates[-1])
    alarms=[i for i,v in enumerate(flags) if v]
    false=sum(i not in windows for i in alarms)
    return {"events":len(events),"detected_events":hits,
            "recall":round(hits/len(events),4) if events else 0.0,
            "median_lead_days":median(leads) if leads else None,
            "alarms":len(alarms),"false_alarms":false,
            "false_alarm_fraction":round(false/len(alarms),4) if alarms else 0.0}

def evaluate_simple_baselines(field, events, lookback_days=30):
    """Predeclared simple causal comparators; thresholds are not optimized."""
    cells={(r["time"],r["scale"]):r for r in field["cells"]}
    times=[r["time"] for r in field["timeline"]]
    one_day=[cells.get((t,"1d"),{}) for t in times]
    specs={
        "volatility_high": [r.get("volatility",0)>=0.35 for r in one_day],
        "drawdown_high": [r.get("drawdown_pressure",0)>=0.20 for r in one_day],
        "trend_weak": [abs(r.get("trend",1))<=0.15 for r in one_day],
        "mean_stability_low": [r.get("mean_stability",1)<=0.45 for r in field["timeline"]],
        "coherence_only": [r.get("coherence",1)<=0.45 for r in field["timeline"]],
        "pressure_only": [r.get("transition_pressure",0)>=0.65 for r in field["timeline"]],
    }
    return {name:_evaluate_flags(times,flags,events,lookback_days) for name,flags in specs.items()}

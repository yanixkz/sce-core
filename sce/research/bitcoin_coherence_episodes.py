from __future__ import annotations
from collections import Counter
from statistics import median

def classify_coherence_episodes(field, events, threshold=.45, lookback_days=30):
    """Compare coherence-break episodes associated with transitions vs false episodes."""
    timeline=field["timeline"]
    by_time={r["time"]:i for i,r in enumerate(timeline)}
    event_indices=[by_time[e["time"]] for e in events if e["time"] in by_time]
    episodes=[]; start=None
    flags=[r["coherence"]<=threshold for r in timeline]
    for i,flag in enumerate(flags+[False]):
        if flag and start is None:start=i
        elif not flag and start is not None:
            end=i-1
            future=[x for x in event_indices if end < x <= end+lookback_days]
            associated=min(future) if future else None
            vals=[timeline[j]["coherence"] for j in range(start,end+1)]
            episodes.append({
                "start_time":timeline[start]["time"],"end_time":timeline[end]["time"],
                "duration_days":end-start+1,"min_coherence":round(min(vals),4),
                "depth":round(threshold-min(vals),4),
                "classification":"transition_associated" if associated is not None else "false_alarm",
                "lead_days":associated-end if associated is not None else None,
                "transition_time":timeline[associated]["time"] if associated is not None else None,
            })
            start=None
    return episodes

def summarize_coherence_episodes(episodes):
    groups={}
    for label in ("transition_associated","false_alarm"):
        rows=[r for r in episodes if r["classification"]==label]
        leads=[r["lead_days"] for r in rows if r["lead_days"] is not None]
        groups[label]={
            "episodes":len(rows),
            "median_duration_days":median([r["duration_days"] for r in rows]) if rows else None,
            "median_min_coherence":median([r["min_coherence"] for r in rows]) if rows else None,
            "median_depth":median([r["depth"] for r in rows]) if rows else None,
            "median_lead_days":median(leads) if leads else None,
        }
    return groups

from __future__ import annotations
from statistics import median

SCALE_MINUTES={"1m":1,"5m":5,"15m":15,"30m":30,"1h":60,"4h":240,"1d":1440,"1w":10080,"1mth":43200}

def propagation_features(rows, event_time, lookback_minutes=43200, stability_threshold=.45, pressure_threshold=.65):
    """Extract causal scale-instability geometry in a fixed chronological window."""
    from datetime import datetime, timedelta
    event=datetime.fromisoformat(event_time.replace("Z","+00:00"))
    start=event-timedelta(minutes=lookback_minutes)
    onset={}
    for scale in SCALE_MINUTES:
        seq=sorted((r for r in rows if r.get("scale")==scale and start <= datetime.fromisoformat(r["time"].replace("Z","+00:00")) < event),key=lambda r:r["time"])
        prev=False
        for r in seq:
            bad=r.get("stability",1)<=stability_threshold or r.get("transition_pressure",0)>=pressure_threshold
            if bad and not prev:onset[scale]=r["time"]
            prev=bad
    ordered=sorted(onset,key=lambda s:onset[s])
    ranks=[SCALE_MINUTES[s] for s in ordered]
    adjacent=[1 if b>a else -1 if b<a else 0 for a,b in zip(ranks,ranks[1:])]
    return {
        "coverage":len(ordered),
        "first_scale":ordered[0] if ordered else None,
        "order":ordered,
        "direction_score":round(sum(adjacent)/len(adjacent),4) if adjacent else 0.0,
        "span_log_scale":round((max(ranks)/min(ranks)),4) if len(ranks)>=2 else 1.0,
    }

def compare_propagation_groups(signatures):
    out={}
    for label in ("hit","false_alarm"):
        rows=[r for r in signatures if r.get("classification")==label]
        out[label]={
            "events":len(rows),
            "median_coverage":median([r["coverage"] for r in rows]) if rows else None,
            "median_direction_score":median([r["direction_score"] for r in rows]) if rows else None,
            "median_span_ratio":median([r["span_log_scale"] for r in rows]) if rows else None,
        }
    return out

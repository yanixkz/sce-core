from __future__ import annotations

from collections import Counter
from statistics import median

from sce.research.bitcoin_scale_propagation import SCALE_ORDER, propagation_signature

def analyze_event_propagation(rows: list[dict], events: list[dict], lookback_steps: int = 120) -> dict:
    """Analyze causal instability propagation across every available temporal scale."""
    signatures = []
    for event in events:
        event_time = event["time"]
        before = [r for r in rows if r.get("time") <= event_time]
        onsets = {}
        for scale in SCALE_ORDER:
            seq = sorted((r for r in before if r.get("scale") == scale), key=lambda r: r["time"])[-lookback_steps:]
            previous = False
            latest_onset = None
            for row in seq:
                now = (row.get("stability") is not None and row["stability"] <= 0.45) or (row.get("transition_pressure") is not None and row["transition_pressure"] >= 0.65)
                if now and not previous:
                    latest_onset = row["time"]
                previous = now
            if latest_onset:
                onsets[scale] = latest_onset
        sig = propagation_signature(onsets)
        sig["event_time"] = event_time
        sig["from_regime"] = event.get("from_regime")
        sig["to_regime"] = event.get("to_regime")
        signatures.append(sig)

    valid = [s for s in signatures if s["coverage"] >= 2]
    starts = Counter(s["first_scale"] for s in valid)
    directions = Counter(s["direction"] for s in valid)
    orders = Counter(tuple(s["order"]) for s in valid)
    return {
        "scale_order": list(SCALE_ORDER),
        "events": len(events),
        "events_with_multiscale_pattern": len(valid),
        "first_scale_counts": dict(starts),
        "direction_counts": dict(directions),
        "median_scale_coverage": median([s["coverage"] for s in valid]) if valid else None,
        "top_orders": [{"order": list(order), "count": count} for order, count in orders.most_common(20)],
        "signatures": signatures,
    }

from __future__ import annotations
from dataclasses import dataclass
from math import log, sqrt
from statistics import median, pstdev

from sce.research.bitcoin_temporal_field import PricePoint

@dataclass(frozen=True)
class TransitionLabelConfig:
    horizon_days: int = 30
    persistence_days: int = 7
    sigma_threshold: float = 1.0
    trailing_vol_days: int = 60

def _log_return(a: float, b: float) -> float:
    return log(b / a) if a > 0 and b > 0 else 0.0

def _trailing_sigma(points: list[PricePoint], end: int, days: int) -> float:
    start = max(1, end - days + 1)
    returns = [_log_return(points[i - 1].price, points[i].price) for i in range(start, end + 1)]
    return pstdev(returns) if len(returns) > 1 else 0.0

def independent_regime_labels(points: list[PricePoint], config: TransitionLabelConfig = TransitionLabelConfig()) -> list[dict]:
    """Evaluation-only labels. Future prices are never inputs to CDS field features."""
    labels = []
    h = config.horizon_days
    for i in range(len(points)):
        if i + h >= len(points):
            break
        sigma = _trailing_sigma(points, i, config.trailing_vol_days)
        forward = _log_return(points[i].price, points[i + h].price)
        threshold = config.sigma_threshold * sigma * sqrt(h)
        regime = 1 if forward > threshold else -1 if forward < -threshold else 0
        labels.append({"time": points[i].time.isoformat().replace("+00:00", "Z"), "forward_return": round(forward, 6), "threshold": round(threshold, 6), "regime": regime})
    return labels

def persistent_transitions(labels: list[dict], persistence_days: int = 7) -> list[dict]:
    events = []
    for i in range(1, len(labels)):
        new, old = labels[i]["regime"], labels[i - 1]["regime"]
        if new == old:
            continue
        future = labels[i:i + persistence_days]
        if len(future) == persistence_days and all(x["regime"] == new for x in future):
            events.append({"time": labels[i]["time"], "from_regime": old, "to_regime": new})
    return events

def evaluate_leading_signal(field: dict, events: list[dict], lookback_days: int = 30, pressure_threshold: float = 0.65, coherence_threshold: float = 0.45) -> dict:
    timeline = field["timeline"]
    by_time = {row["time"]: i for i, row in enumerate(timeline)}
    hits, leads = 0, []
    event_windows = set()
    for event in events:
        idx = by_time.get(event["time"])
        if idx is None:
            continue
        start = max(0, idx - lookback_days)
        window = timeline[start:idx]
        candidates = [(j, row) for j, row in enumerate(window, start) if row["transition_pressure"] >= pressure_threshold or row["coherence"] <= coherence_threshold]
        if candidates:
            hits += 1
            signal_idx = candidates[-1][0]
            leads.append(idx - signal_idx)
        event_windows.update(range(start, idx + 1))
    alarms = [i for i, row in enumerate(timeline) if row["transition_pressure"] >= pressure_threshold or row["coherence"] <= coherence_threshold]
    false_alarms = sum(1 for i in alarms if i not in event_windows)
    return {
        "events": len(events),
        "detected_events": hits,
        "recall": round(hits / len(events), 4) if events else 0.0,
        "median_lead_days": median(leads) if leads else None,
        "alarms": len(alarms),
        "false_alarms": false_alarms,
        "false_alarm_fraction": round(false_alarms / len(alarms), 4) if alarms else 0.0,
        "parameters": {"lookback_days": lookback_days, "pressure_threshold": pressure_threshold, "coherence_threshold": coherence_threshold},
    }

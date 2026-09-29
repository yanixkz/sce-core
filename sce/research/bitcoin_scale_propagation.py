from __future__ import annotations

from dataclasses import dataclass
from statistics import median

SCALE_ORDER = ("1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mth")

@dataclass(frozen=True)
class PropagationConfig:
    stability_threshold: float = 0.45
    pressure_threshold: float = 0.65

def unstable(row: dict, config: PropagationConfig = PropagationConfig()) -> bool:
    stability = row.get("stability")
    pressure = row.get("transition_pressure")
    return (
        stability is not None and stability <= config.stability_threshold
    ) or (
        pressure is not None and pressure >= config.pressure_threshold
    )

def first_instability_by_scale(rows: list[dict], event_time: str, lookback_steps: int = 120, config: PropagationConfig = PropagationConfig()) -> dict:
    """Return the last stable->unstable onset before an event for each scale.

    rows must already be causal observations. Future observations are not inspected.
    """
    times = sorted({r["time"] for r in rows if r["time"] <= event_time})
    window = set(times[-lookback_steps:])
    out = {}
    for scale in SCALE_ORDER:
        seq = sorted((r for r in rows if r.get("scale") == scale and r["time"] in window), key=lambda r: r["time"])
        onset = None
        prev = False
        for row in seq:
            now = unstable(row, config)
            if now and not prev:
                onset = row["time"]
            prev = now
        if onset is not None:
            out[scale] = onset
    return out

def propagation_signature(onsets: dict) -> dict:
    ordered = [(s, onsets[s]) for s in SCALE_ORDER if s in onsets]
    chronological = sorted(ordered, key=lambda x: x[1])
    ranks = {s: i for i, (s, _) in enumerate(chronological)}
    adjacent = []
    for a, b in zip(SCALE_ORDER, SCALE_ORDER[1:]):
        if a in ranks and b in ranks:
            adjacent.append(1 if ranks[a] < ranks[b] else -1 if ranks[a] > ranks[b] else 0)
    direction = "lower_to_higher" if adjacent and sum(adjacent) > 0 else "higher_to_lower" if adjacent and sum(adjacent) < 0 else "mixed"
    return {
        "first_scale": chronological[0][0] if chronological else None,
        "order": [s for s, _ in chronological],
        "direction": direction,
        "coverage": len(chronological),
    }

def summarize_propagations(signatures: list[dict]) -> dict:
    valid = [s for s in signatures if s.get("coverage", 0) >= 2]
    starts = {}
    directions = {}
    coverages = []
    for s in valid:
        starts[s["first_scale"]] = starts.get(s["first_scale"], 0) + 1
        directions[s["direction"]] = directions.get(s["direction"], 0) + 1
        coverages.append(s["coverage"])
    return {
        "events_with_multiscale_propagation": len(valid),
        "first_scale_counts": starts,
        "direction_counts": directions,
        "median_scale_coverage": median(coverages) if coverages else None,
    }

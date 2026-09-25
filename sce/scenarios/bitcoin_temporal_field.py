from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import fmean, pstdev


@dataclass(frozen=True)
class TemporalObservation:
    timestamp: str
    scale: str
    trend: float
    momentum: float
    volatility: float
    drawdown_pressure: float
    range_position: float
    volume_pressure: float


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def directional_state(observation: TemporalObservation, threshold: float = 0.12) -> int:
    signal = 0.6 * observation.trend + 0.4 * observation.momentum
    if signal > threshold:
        return 1
    if signal < -threshold:
        return -1
    return 0


def observation_stability(observation: TemporalObservation) -> float:
    """Transparent provisional CDS score using only one causal field cell."""
    direction_strength = abs(0.6 * observation.trend + 0.4 * observation.momentum)
    disturbance = fmean(
        [
            _clamp(observation.volatility),
            _clamp(observation.drawdown_pressure),
            _clamp(abs(observation.volume_pressure)),
        ]
    )
    centered_range = 1.0 - min(1.0, abs(observation.range_position - 0.5) * 2.0)
    score = 0.50 * direction_strength + 0.25 * centered_range + 0.25 * (1.0 - disturbance)
    return round(_clamp(score), 4)


def cross_scale_coherence(observations: list[TemporalObservation]) -> float:
    """Measure structural agreement across scales at the same timestamp."""
    if not observations:
        return 0.0
    states = [directional_state(item) for item in observations]
    mean_state = fmean(states)
    dispersion = sqrt(fmean([(state - mean_state) ** 2 for state in states]))
    max_dispersion = sqrt(2.0)
    return round(_clamp(1.0 - dispersion / max_dispersion), 4)


def transition_pressure(observations: list[TemporalObservation]) -> float:
    if not observations:
        return 0.0
    stability = fmean(observation_stability(item) for item in observations)
    coherence = cross_scale_coherence(observations)
    disturbance = fmean(
        fmean([_clamp(item.volatility), _clamp(item.drawdown_pressure)])
        for item in observations
    )
    return round(_clamp(0.4 * (1.0 - stability) + 0.35 * (1.0 - coherence) + 0.25 * disturbance), 4)


def run_bitcoin_temporal_field_demo() -> dict:
    """Deterministic fixture proving the temporal-field result contract.

    Real Bitcoin ingestion is intentionally deferred until source/provenance rules are
    implemented. These values are synthetic and make no empirical market claim.
    """
    rows = [
        TemporalObservation("T0", "1m", 0.72, 0.55, 0.20, 0.10, 0.72, 0.08),
        TemporalObservation("T0", "1w", 0.60, 0.44, 0.24, 0.14, 0.67, 0.10),
        TemporalObservation("T0", "1d", 0.48, 0.31, 0.31, 0.18, 0.61, 0.16),
        TemporalObservation("T0", "4h", 0.20, 0.08, 0.42, 0.25, 0.54, 0.24),
        TemporalObservation("T0", "1h", -0.18, -0.22, 0.55, 0.32, 0.41, -0.30),
    ]
    coherence = cross_scale_coherence(rows)
    cells = [
        {
            "timestamp": item.timestamp,
            "scale": item.scale,
            "regime": directional_state(item),
            "stability": observation_stability(item),
        }
        for item in rows
    ]
    return {
        "demo": "bitcoin-temporal-field",
        "empirical": False,
        "data": "synthetic deterministic fixture",
        "question": "Do losses of cross-scale stability and coherence precede observable Bitcoin regime transitions?",
        "field": "F(t, tau)",
        "cells": cells,
        "cross_scale_coherence": coherence,
        "transition_pressure": transition_pressure(rows),
        "pipeline": [
            "Historical Time",
            "Temporal Scales",
            "Observable Constraints",
            "Cross-Scale Dynamics",
            "Stability / Coherence / Persistence",
            "Regime Transitions",
        ],
    }


def format_bitcoin_temporal_field_demo(result: dict) -> str:
    cell_lines = [
        f"{cell['scale']:>3} | regime={cell['regime']:+d} | stability={cell['stability']:.4f}"
        for cell in result["cells"]
    ]
    return "\n".join(
        [
            "Bitcoin Temporal Field",
            "======================",
            "",
            "F(t, tau): one dynamic system observed across temporal scales.",
            "Synthetic deterministic fixture only; no Bitcoin prediction or trading claim.",
            "",
            f"Cross-scale coherence: {result['cross_scale_coherence']:.4f}",
            f"Transition pressure:   {result['transition_pressure']:.4f}",
            "",
            "Temporal field cells",
            "--------------------",
            *cell_lines,
        ]
    )

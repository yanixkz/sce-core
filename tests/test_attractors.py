from __future__ import annotations

from sce.core.attractors import AttractorDetectionConfig, FixedPointAttractorDetector
from sce.core.types import State


def make_stable_state(stability: float = 0.81) -> State:
    state = State(
        state_type="memory_hypothesis",
        data={
            "entity": "supplier A",
            "claim": "supplier A is unreliable",
        },
    )
    state.stability = stability
    return state


def test_fixed_point_attractor_detector_detects_stable_repeated_context():
    detector = FixedPointAttractorDetector(
        AttractorDetectionConfig(
            window_size=3,
            stability_threshold=0.5,
            max_stability_delta=0.05,
        )
    )
    trace = [make_stable_state(0.80), make_stable_state(0.82), make_stable_state(0.81)]

    attractor = detector.detect(trace)

    assert attractor is not None
    assert attractor.attractor_type == "memory_hypothesis"
    assert attractor.stability_score > 0.5
    assert attractor.invariant["entity"] == "supplier A"
    assert attractor.invariant["claim"] == "supplier A is unreliable"
    assert attractor.meta["detector"] == "FixedPointAttractorDetector"


def test_fixed_point_attractor_detector_rejects_low_stability():
    detector = FixedPointAttractorDetector()
    trace = [make_stable_state(0.20), make_stable_state(0.21), make_stable_state(0.19)]

    assert detector.detect(trace) is None


def test_fixed_point_attractor_detector_rejects_high_stability_drift():
    detector = FixedPointAttractorDetector(
        AttractorDetectionConfig(
            window_size=3,
            stability_threshold=0.5,
            max_stability_delta=0.05,
        )
    )
    trace = [make_stable_state(0.60), make_stable_state(0.80), make_stable_state(0.95)]

    assert detector.detect(trace) is None


def test_fixed_point_attractor_detector_rejects_different_contexts():
    detector = FixedPointAttractorDetector()
    first = make_stable_state(0.81)
    second = make_stable_state(0.82)
    third = make_stable_state(0.83)
    third.data["claim"] = "supplier A is reliable"

    assert detector.detect([first, second, third]) is None

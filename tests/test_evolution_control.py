from __future__ import annotations

import pytest

from sce.core.evolution_control import EvolutionErrorTracker


def test_evolution_error_tracker_reports_empty_trajectory_as_reliable():
    report = EvolutionErrorTracker().report()

    assert report.cumulative_error == 0.0
    assert report.mean_error == 0.0
    assert report.reliability == 1.0
    assert report.trend == "empty"
    assert report.is_reliable is True


def test_evolution_error_tracker_records_weighted_step_errors():
    tracker = EvolutionErrorTracker()

    first = tracker.record_step("plan", predicted_value=0.9, actual_value=0.7)
    second = tracker.record_step("execute", predicted_value=0.8, actual_value=0.5, weight=2.0)
    report = tracker.report()

    assert first.error == pytest.approx(0.2)
    assert second.error == pytest.approx(0.6)
    assert report.cumulative_error == pytest.approx(0.8)
    assert report.mean_error == pytest.approx(0.4)
    assert report.reliability == pytest.approx(1 / 1.8)
    assert report.trend == "worsening"


def test_evolution_error_tracker_detects_improving_error_trend():
    tracker = EvolutionErrorTracker()
    tracker.record_step("first", predicted_value=1.0, actual_value=0.4)
    tracker.record_step("second", predicted_value=0.8, actual_value=0.7)

    report = tracker.report()

    assert report.trend == "improving"


def test_evolution_error_tracker_rejects_negative_weight():
    tracker = EvolutionErrorTracker()

    with pytest.raises(ValueError, match="weight"):
        tracker.record_step("bad", predicted_value=1.0, actual_value=1.0, weight=-1.0)

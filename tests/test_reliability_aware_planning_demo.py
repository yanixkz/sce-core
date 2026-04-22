from __future__ import annotations

from sce.scenarios.reliability_aware_planning_demo import (
    format_reliability_aware_planning_demo,
    run_reliability_aware_planning_demo,
)


def test_reliability_aware_planning_demo_changes_choice():
    result = run_reliability_aware_planning_demo()

    assert result["selected_without_reliability"] == "supplier_risk_plan"
    assert result["selected_with_reliability"] == "escalation_plan"
    assert result["changed_choice"] is True


def test_reliability_aware_planning_demo_pretty_output_contains_scores():
    rendered = format_reliability_aware_planning_demo(run_reliability_aware_planning_demo())

    assert "SCE Reliability-Aware Planning Demo" in rendered
    assert "Without trajectory reliability" in rendered
    assert "With trajectory reliability" in rendered
    assert "Changed choice: YES" in rendered
    assert "escalation_plan" in rendered

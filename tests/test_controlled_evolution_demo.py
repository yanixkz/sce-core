from __future__ import annotations

from sce.scenarios.controlled_evolution_demo import (
    format_controlled_evolution_demo,
    run_controlled_evolution_demo,
)


def test_controlled_evolution_demo_reports_reliable_improving_trajectory():
    result = run_controlled_evolution_demo()

    assert len(result["steps"]) == 3
    assert result["trend"] == "improving"
    assert result["is_reliable"] is True
    assert result["cumulative_error"] > 0
    assert result["reliability"] > 0.5


def test_controlled_evolution_demo_pretty_output_contains_report():
    rendered = format_controlled_evolution_demo(run_controlled_evolution_demo())

    assert "SCE Controlled Evolution Demo" in rendered
    assert "Step errors" in rendered
    assert "Trajectory report" in rendered
    assert "cumulative_error" in rendered
    assert "reliability" in rendered

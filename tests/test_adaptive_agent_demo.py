from __future__ import annotations

from sce.scenarios.adaptive_agent_demo import format_adaptive_agent_demo, run_adaptive_agent_demo


def test_adaptive_agent_demo_changes_decision_after_learning():
    result = run_adaptive_agent_demo()

    assert result["first_choice"] == "supplier_risk_plan"
    assert result["second_choice"] == "escalation_plan"
    assert result["changed_choice"] is True
    assert result["episodes_after_learning"] == 2


def test_adaptive_agent_demo_exposes_trace_and_explanation():
    result = run_adaptive_agent_demo()

    assert result["execution_trace"]
    assert any("Generated 3 candidate plans" in step for step in result["execution_trace"])
    assert any("Re-scored candidates" in step for step in result["execution_trace"])
    assert "memory bias changes" in result["explanation"]


def test_adaptive_agent_demo_pretty_output_contains_decision_change():
    rendered = format_adaptive_agent_demo(run_adaptive_agent_demo())

    assert "SCE Adaptive Agent Demo" in rendered
    assert "Execution trace" in rendered
    assert "Why the decision changed" in rendered
    assert "Changed choice: YES" in rendered
    assert "escalation_plan received a memory boost" in rendered

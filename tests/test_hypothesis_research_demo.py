from __future__ import annotations

from sce.scenarios.hypothesis_research_demo import (
    format_hypothesis_research_demo,
    run_hypothesis_research_demo,
)


def test_hypothesis_research_demo_selects_top_hypothesis():
    result = run_hypothesis_research_demo()

    assert result["research_question"] == "Why are supplier escalations increasing?"
    assert result["selected_hypothesis"] == "supplier_quality_degradation"
    assert result["scores"][0]["hypothesis"] == "supplier_quality_degradation"
    assert result["scores"][0]["confidence"] > result["scores"][1]["confidence"]
    assert len(result["next_actions"]) == 3


def test_hypothesis_research_demo_explains_decision_path():
    result = run_hypothesis_research_demo()

    assert "research_decision" in result["backbone_nodes"]
    assert "supplier_quality_degradation" in result["backbone_nodes"]
    assert "regional_onboarding_gap" in result["backbone_nodes"]
    assert "marketing_noise" in result["dangling_nodes"]
    assert "reporting_artifact" in result["dangling_nodes"]


def test_hypothesis_research_demo_pretty_output_is_simple():
    rendered = format_hypothesis_research_demo(run_hypothesis_research_demo())

    assert "SCE Hypothesis Research Demo" in rendered
    assert "Question. Rank. Investigate." in rendered
    assert "1) Rank hypotheses" in rendered
    assert "2) Explain evidence path" in rendered
    assert "3) Next research actions" in rendered
    assert "Selected hypothesis: supplier_quality_degradation" in rendered

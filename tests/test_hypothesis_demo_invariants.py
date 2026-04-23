from __future__ import annotations

from sce.scenarios.hypothesis_research_demo import format_hypothesis_research_demo, run_hypothesis_research_demo


def test_hypothesis_scores_are_sorted_and_selected_matches_top_ranked():
    result = run_hypothesis_research_demo()
    scores = result["scores"]

    confidences = [row["confidence"] for row in scores]
    assert confidences == sorted(confidences, reverse=True)
    assert result["selected_hypothesis"] == scores[0]["hypothesis"]


def test_hypothesis_backbone_and_actions_are_semantically_non_empty():
    result = run_hypothesis_research_demo()

    assert "research_decision" in result["backbone_nodes"]
    assert "supplier_quality_degradation" in result["backbone_nodes"]
    assert "marketing_noise" in result["dangling_nodes"]
    assert result["next_actions"]
    assert all(isinstance(action, str) and action.strip() for action in result["next_actions"])


def test_hypothesis_pretty_output_keeps_core_sections_without_snapshot_lock_in():
    rendered = format_hypothesis_research_demo(run_hypothesis_research_demo())

    assert "1) Rank hypotheses" in rendered
    assert "2) Explain evidence path" in rendered
    assert "3) Next research actions" in rendered
    assert "Selected hypothesis:" in rendered

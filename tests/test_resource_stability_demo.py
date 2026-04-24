from __future__ import annotations

from sce.scenarios.resource_stability_demo import format_resource_stability_demo, run_resource_stability_demo


def test_resource_stability_demo_output_shape_and_selection():
    result = run_resource_stability_demo()

    expected_keys = {
        "research_question",
        "initial_state",
        "candidates",
        "selected_state",
        "scores",
        "stability_explanation",
        "constraints",
        "next_research_actions",
    }
    assert expected_keys.issubset(result.keys())

    candidate_names = {candidate["name"] for candidate in result["candidates"]}
    assert result["selected_state"]["name"] in candidate_names


def test_resource_stability_demo_scores_are_sorted():
    result = run_resource_stability_demo()
    stability_scores = [row["stability"] for row in result["scores"]]
    assert stability_scores == sorted(stability_scores, reverse=True)


def test_resource_stability_demo_pretty_output_sections():
    rendered = format_resource_stability_demo(run_resource_stability_demo())

    assert "SCE Resource Stability Demo" in rendered
    assert "Research question" in rendered
    assert "1) Initial unstable regime" in rendered
    assert "2) Candidate regimes and ranking" in rendered
    assert "Selected stable regime" in rendered
    assert "3) Constraint effects" in rendered
    assert "Next research actions" in rendered

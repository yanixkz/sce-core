from __future__ import annotations

from sce.scenarios.epidemic_regime_demo import format_epidemic_regime_demo, run_epidemic_regime_demo


def test_epidemic_regime_demo_output_shape_and_selection():
    result = run_epidemic_regime_demo()

    expected_keys = {
        "research_question",
        "initial_state",
        "candidates",
        "selected_regime",
        "scores",
        "stability_explanation",
        "constraints",
        "next_research_actions",
        "parameters",
    }
    assert expected_keys.issubset(result.keys())

    candidate_names = {candidate["name"] for candidate in result["candidates"]}
    assert result["selected_regime"]["name"] in candidate_names


def test_epidemic_regime_demo_scores_are_sorted_and_deterministic():
    first = run_epidemic_regime_demo()
    second = run_epidemic_regime_demo()

    first_scores = [row["stability"] for row in first["scores"]]
    second_scores = [row["stability"] for row in second["scores"]]

    assert first_scores == sorted(first_scores, reverse=True)
    assert first_scores == second_scores
    assert first["selected_regime"]["name"] == second["selected_regime"]["name"]


def test_epidemic_regime_demo_pretty_output_sections():
    rendered = format_epidemic_regime_demo(run_epidemic_regime_demo())

    assert "SCE Epidemic Regime Stability Demo" in rendered
    assert "Research question" in rendered
    assert "1) Initial epidemic regime" in rendered
    assert "2) Candidate regimes and ranking" in rendered
    assert "Selected stable epidemic regime" in rendered
    assert "3) Constraint effects" in rendered
    assert "Next research actions" in rendered

from __future__ import annotations

from sce.scenarios.selection_landscape import (
    build_stability_distribution,
    generate_candidate_population,
    rank_candidates,
    run_selection_landscape_demo,
)


def test_population_generation_is_deterministic():
    first = generate_candidate_population(12)
    second = generate_candidate_population(12)

    assert first == second
    assert len(first) == 12
    assert first[0]["label"] == "Candidate 1"


def test_rankings_are_stable_and_sorted():
    ranked = rank_candidates(generate_candidate_population(16))

    assert ranked == rank_candidates(generate_candidate_population(16))
    assert [candidate["stability"] for candidate in ranked] == sorted(
        [candidate["stability"] for candidate in ranked], reverse=True
    )
    assert [candidate["rank"] for candidate in ranked] == list(range(1, 17))


def test_distribution_generation_counts_population():
    population = generate_candidate_population(20)
    distribution = build_stability_distribution(population)

    assert sum(bucket["count"] for bucket in distribution) == 20
    assert distribution[0]["bucket"] == "1.00"
    assert distribution[-1]["bucket"] == "0.00"


def test_result_schema_exposes_landscape_summary():
    result = run_selection_landscape_demo(18)

    assert result["population_size"] == 18
    expected_keys = {
        "population_size",
        "best_candidate",
        "worst_candidate",
        "median_candidate",
        "stability_distribution",
    }
    assert expected_keys.issubset(result)
    assert result["best_candidate"]["rank"] == 1
    assert result["worst_candidate"]["rank"] == 18
    assert isinstance(result["stability_distribution"], list)
    assert "1.00 |" in result["ascii_visualization"]

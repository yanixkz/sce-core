from __future__ import annotations

from sce.scenarios.constraint_sweep import (
    detect_winner_transitions,
    generate_constraint_sweep_population,
    run_constraint_sweep_demo,
)


def test_constraint_sweep_is_deterministic():
    first = run_constraint_sweep_demo()
    second = run_constraint_sweep_demo()

    assert first == second
    assert generate_constraint_sweep_population() == generate_constraint_sweep_population()


def test_constraint_sweep_has_stable_winner_history():
    result = run_constraint_sweep_demo()

    assert [step["constraint_strength"] for step in result["winner_history"]] == [
        0.0,
        0.2,
        0.4,
        0.6,
        0.8,
        1.0,
    ]
    assert [step["winner"] for step in result["winner_history"]] == [
        "Candidate A",
        "Candidate A",
        "Candidate B",
        "Candidate C",
        "Candidate D",
        "Candidate D",
    ]


def test_constraint_sweep_transition_detection():
    result = run_constraint_sweep_demo()

    assert result["winner_transitions"] == [
        {"constraint_strength": 0.4, "from": "Candidate A", "to": "Candidate B"},
        {"constraint_strength": 0.6, "from": "Candidate B", "to": "Candidate C"},
        {"constraint_strength": 0.8, "from": "Candidate C", "to": "Candidate D"},
    ]
    assert detect_winner_transitions(result["winner_history"]) == result["winner_transitions"]


def test_constraint_sweep_result_schema():
    result = run_constraint_sweep_demo()

    assert {
        "sweep_steps",
        "winner_history",
        "winner_transitions",
        "constraint_values",
        "ranking_history",
    }.issubset(result)
    assert len(result["sweep_steps"]) == 6
    assert len(result["ranking_history"]) == 6
    assert result["ranking_history"][0]["ranking"][0]["rank"] == 1
    assert "0.4 | B" in result["ascii_visualization"]

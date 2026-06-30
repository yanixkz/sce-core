from __future__ import annotations

from sce.scenarios.persistence_demo import (
    render_persistence_ascii,
    run_persistence_demo,
)


def test_persistence_scores_are_deterministic():
    first = run_persistence_demo()
    second = run_persistence_demo()

    assert first == second
    assert first["scores"] == {
        "Candidate A": 1.00,
        "Candidate B": 0.84,
        "Candidate C": 0.35,
        "Candidate D": 0.07,
    }


def test_candidate_traces_cover_t0_through_t100():
    result = run_persistence_demo()

    for candidate in result["candidates"]:
        assert candidate["trace"][0]["time"] == "t0"
        assert candidate["trace"][-1]["time"] == "t100"
        assert len(candidate["trace"]) == 101


def test_elimination_statuses_are_exposed():
    result = run_persistence_demo()
    by_id = {candidate["id"]: candidate for candidate in result["candidates"]}

    assert by_id["A"]["status"] == "survived"
    assert by_id["A"]["elimination_step"] is None
    assert by_id["B"]["elimination_step"] == 85
    assert by_id["C"]["elimination_step"] == 36
    assert by_id["D"]["elimination_step"] == 8


def test_ascii_visualization_matches_scores():
    result = run_persistence_demo()

    assert render_persistence_ascii(result["candidates"]) == "A ██████████\nB ████████\nC ███\nD █"
    assert result["ascii_visualization"].startswith("A ██████████")

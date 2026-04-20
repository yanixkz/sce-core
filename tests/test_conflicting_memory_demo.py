from __future__ import annotations

from sce.scenarios.conflicting_memory import run_conflicting_memory_demo


def test_conflicting_memory_demo_selects_unreliable_state():
    result = run_conflicting_memory_demo()

    assert result["scenario"] == "conflicting_memory"
    assert result["selected_claim"] == "supplier A is unreliable"
    assert len(result["candidates"]) == 2

    for candidate in result["candidates"]:
        assert "coherence" in candidate
        assert "conflict" in candidate
        assert "entropy" in candidate
        assert "support" in candidate
        assert "stability" in candidate
        assert isinstance(candidate["stability"], float)

from __future__ import annotations

from typing import Any, Dict

from sce.core.llm_candidates import LLMCandidateGenerator
from sce.core.types import State


class FakeLLM:
    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "candidates": [
                {
                    "state_type": "memory_hypothesis",
                    "data": {"claim": "supplier A is reliable"},
                },
                {
                    "state_type": "memory_hypothesis",
                    "data": {"claim": "supplier A is unreliable"},
                },
            ]
        }


def test_llm_candidate_generator():
    current = State(state_type="context", data={"entity": "supplier A"})

    generator = LLMCandidateGenerator(client=FakeLLM(), task="generate hypotheses")
    candidates = generator.generate(current)

    assert len(candidates) == 2
    assert candidates[0].state.data["claim"] == "supplier A is reliable"
    assert candidates[1].state.data["claim"] == "supplier A is unreliable"

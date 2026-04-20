from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol

from sce.core.candidates import CandidateResult
from sce.core.types import State


class LLMClient(Protocol):
    """Minimal interface for an LLM client used as a candidate source."""

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        ...


@dataclass(frozen=True)
class LLMCandidatePrompt:
    """Prompt payload for generating candidate states."""

    task: str
    current_state: State
    max_candidates: int = 3

    def render(self) -> str:
        return (
            "Generate candidate next states for SCE Core.\n"
            "Return JSON with a top-level 'candidates' list.\n"
            "Each candidate must include 'state_type' and 'data'.\n\n"
            f"Task: {self.task}\n"
            f"Current state type: {self.current_state.state_type}\n"
            f"Current state data: {self.current_state.data}\n"
            f"Max candidates: {self.max_candidates}\n"
        )


class LLMCandidateGenerator:
    """Generate candidate states from an LLM JSON response.

    This class does not depend on a specific LLM provider. Any client that
    implements `complete_json(prompt) -> dict` can be used.
    """

    def __init__(self, client: LLMClient, task: str, max_candidates: int = 3) -> None:
        self.client = client
        self.task = task
        self.max_candidates = max_candidates

    def generate(self, current_state: State) -> List[CandidateResult]:
        prompt = LLMCandidatePrompt(
            task=self.task,
            current_state=current_state,
            max_candidates=self.max_candidates,
        )
        payload = self.client.complete_json(prompt.render())
        return parse_candidate_states(payload)


def parse_candidate_states(payload: Dict[str, Any]) -> List[CandidateResult]:
    """Parse an LLM JSON payload into candidate states.

    Expected shape:

    {
        "candidates": [
            {"state_type": "hypothesis", "data": {"claim": "..."}}
        ]
    }
    """

    raw_candidates = payload.get("candidates", [])
    if not isinstance(raw_candidates, list):
        raise ValueError("LLM payload field 'candidates' must be a list")

    results: List[CandidateResult] = []
    for index, item in enumerate(raw_candidates):
        if not isinstance(item, dict):
            raise ValueError(f"Candidate at index {index} must be an object")

        state_type = item.get("state_type")
        data = item.get("data")
        if not isinstance(state_type, str) or not state_type:
            raise ValueError(f"Candidate at index {index} must include a non-empty state_type")
        if not isinstance(data, dict):
            raise ValueError(f"Candidate at index {index} must include object data")

        state = State(state_type=state_type, data=data, status="candidate")
        results.append(CandidateResult(state=state, rule=None, source="llm"))

    return results

from __future__ import annotations

import os
from typing import Any, Dict

from sce.core.explain import SCEExplainer
from sce.core.llm_candidates import LLMCandidateGenerator
from sce.core.scoring import SCEScoringEngine
from sce.core.types import Link, RelationType, State
from sce.storage.memory import MemoryRepository


class FakeLLM:
    """Deterministic fake LLM used for demos and tests."""

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "candidates": [
                {
                    "state_type": "memory_hypothesis",
                    "data": {
                        "entity": "supplier A",
                        "claim": "supplier A is reliable",
                        "late_delivery_rate": 0.08,
                    },
                },
                {
                    "state_type": "memory_hypothesis",
                    "data": {
                        "entity": "supplier A",
                        "claim": "supplier A is unreliable",
                        "late_delivery_rate": 0.31,
                    },
                },
            ]
        }


def _build_llm_client() -> Any:
    """Use OpenAI if enabled and configured; otherwise fall back to FakeLLM."""

    use_openai = os.getenv("SCE_USE_OPENAI", "false").lower() in {"1", "true", "yes"}
    if not use_openai:
        return FakeLLM()

    try:
        from sce.core.llm_openai import OpenAIJSONClient

        return OpenAIJSONClient(model=os.getenv("SCE_OPENAI_MODEL", "gpt-4o-mini"))
    except Exception:
        return FakeLLM()


def run_llm_memory_demo() -> Dict[str, Any]:
    """Demonstrate the LLM proposes / SCE decides pattern.

    By default this uses FakeLLM for deterministic local execution.
    Set SCE_USE_OPENAI=true and OPENAI_API_KEY to use a real OpenAI model.
    """

    repo = MemoryRepository()
    context = State(
        state_type="memory_context",
        data={
            "entity": "supplier A",
            "facts": [
                "92% of historical orders were on time",
                "31% of recent orders were late",
                "support team received multiple recent complaints",
            ],
        },
    )
    repo.add_state(context)

    client = _build_llm_client()
    llm_source = "openai" if client.__class__.__name__ == "OpenAIJSONClient" else "fake"

    generator = LLMCandidateGenerator(
        client=client,
        task=(
            "Generate exactly two competing memory hypotheses about supplier reliability. "
            "One hypothesis should represent reliability and one should represent unreliability. "
            "Each candidate data object must include entity, claim, and late_delivery_rate."
        ),
        max_candidates=2,
    )
    candidates = [candidate.state for candidate in generator.generate(context)]

    evidence_on_time = State("evidence", {"fact": "92% of historical orders were on time"})
    evidence_late = State("evidence", {"fact": "31% of recent orders were late"})
    evidence_complaints = State("evidence", {"fact": "multiple recent complaints"})

    for state in [evidence_on_time, evidence_late, evidence_complaints, *candidates]:
        repo.add_state(state)

    reliable = _find_candidate(candidates, "reliable")
    unreliable = _find_candidate(candidates, "unreliable")

    if reliable is not None:
        repo.add_link(Link(evidence_on_time.state_id, reliable.state_id, RelationType.SUPPORTS, 0.8))
        repo.add_link(Link(evidence_late.state_id, reliable.state_id, RelationType.CONTRADICTS, 0.9))
        repo.add_link(Link(evidence_complaints.state_id, reliable.state_id, RelationType.CONTRADICTS, 0.6))

    if unreliable is not None:
        repo.add_link(Link(evidence_late.state_id, unreliable.state_id, RelationType.SUPPORTS, 0.9))
        repo.add_link(Link(evidence_complaints.state_id, unreliable.state_id, RelationType.SUPPORTS, 0.6))
        repo.add_link(Link(evidence_on_time.state_id, unreliable.state_id, RelationType.CONTRADICTS, 0.4))

    scorer = SCEScoringEngine(repo)
    for state in candidates:
        scorer.compute_stability(state)

    selected = max(candidates, key=lambda state: state.stability)
    explanation = SCEExplainer(repo).explain_comparison([state.state_id for state in candidates])

    return {
        "scenario": "llm_memory",
        "llm_source": llm_source,
        "pattern": "LLM proposes candidates; SCE scores, selects and explains.",
        "generated_candidates": [
            {
                "claim": state.data.get("claim"),
                "stability": state.stability,
                "support": state.support,
                "conflict": state.conflict,
                "entropy": state.entropy,
                "coherence": state.coherence,
            }
            for state in candidates
        ],
        "selected_claim": selected.data.get("claim"),
        "explanation": explanation,
    }


def _find_candidate(candidates: list[State], keyword: str) -> State | None:
    for state in candidates:
        claim = str(state.data.get("claim", "")).lower()
        if keyword in claim:
            return state
    return None

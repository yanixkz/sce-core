from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from sce.core.explain import SCEExplainer
from sce.core.llm_candidates import LLMCandidateGenerator, LLMClient
from sce.core.scoring import SCEScoringEngine
from sce.core.types import Link, RelationType, State
from sce.storage.memory import MemoryRepository


@dataclass(frozen=True)
class AgentStep:
    """One iteration of the SCE agent loop."""

    step: int
    current_state_id: str
    selected_state_id: str
    selected_claim: Any
    explanation: Dict[str, Any]


@dataclass(frozen=True)
class AgentLoopResult:
    """Result of a multi-step SCE agent loop."""

    initial_state_id: str
    final_state_id: str
    final_claim: Any
    steps: List[AgentStep]


class SCEAgentLoop:
    """Minimal multi-step loop: LLM proposes, SCE selects, selected state becomes context."""

    def __init__(
        self,
        repo: MemoryRepository,
        llm_client: LLMClient,
        task: str,
        max_candidates: int = 2,
    ) -> None:
        self.repo = repo
        self.llm_client = llm_client
        self.task = task
        self.max_candidates = max_candidates
        self.scorer = SCEScoringEngine(repo)
        self.explainer = SCEExplainer(repo)

    def run(self, initial_state: State, steps: int = 3) -> AgentLoopResult:
        self.repo.add_state(initial_state)
        current = initial_state
        trace: List[AgentStep] = []

        for step_index in range(1, steps + 1):
            generator = LLMCandidateGenerator(
                client=self.llm_client,
                task=self.task,
                max_candidates=self.max_candidates,
            )
            candidate_results = generator.generate(current)
            candidates = [candidate.state for candidate in candidate_results]

            if not candidates:
                break

            evidence = self._evidence_from_state(current)
            for state in evidence:
                self.repo.add_state(state)
            for candidate in candidates:
                self.repo.add_state(candidate)
                self._connect_evidence(evidence, candidate)
                self.scorer.compute_stability(candidate)

            selected = max(candidates, key=lambda state: state.stability)
            explanation = self.explainer.explain_comparison([state.state_id for state in candidates])
            trace.append(
                AgentStep(
                    step=step_index,
                    current_state_id=str(current.state_id),
                    selected_state_id=str(selected.state_id),
                    selected_claim=selected.data.get("claim"),
                    explanation=explanation,
                )
            )
            current = selected

        return AgentLoopResult(
            initial_state_id=str(initial_state.state_id),
            final_state_id=str(current.state_id),
            final_claim=current.data.get("claim"),
            steps=trace,
        )

    def _evidence_from_state(self, state: State) -> List[State]:
        facts = state.data.get("facts")
        if isinstance(facts, list):
            return [State("evidence", {"fact": str(fact)}) for fact in facts]
        claim = state.data.get("claim")
        if claim:
            return [State("evidence", {"fact": str(claim)})]
        return []

    def _connect_evidence(self, evidence: List[State], candidate: State) -> None:
        claim = str(candidate.data.get("claim", "")).lower()
        for item in evidence:
            fact = str(item.data.get("fact", "")).lower()
            relation = RelationType.SUPPORTS if self._supports(fact, claim) else RelationType.CONTRADICTS
            strength = 0.8 if relation == RelationType.SUPPORTS else 0.4
            self.repo.add_link(Link(item.state_id, candidate.state_id, relation, strength))

    def _supports(self, fact: str, claim: str) -> bool:
        positive_terms = ["reliable", "stable", "safe", "acceptable", "on time"]
        negative_terms = ["unreliable", "risky", "late", "breach", "complaint"]

        if any(term in fact for term in positive_terms) and any(term in claim for term in positive_terms):
            return True
        if any(term in fact for term in negative_terms) and any(term in claim for term in negative_terms):
            return True
        return False

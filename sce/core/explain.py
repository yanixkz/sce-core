from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from sce.core.types import RelationType, State
from sce.storage.memory import MemoryRepository


class SCEExplainer:
    def __init__(self, repo: MemoryRepository) -> None:
        self.repo = repo

    def explain_state(self, state_id: UUID) -> Dict[str, Any]:
        state = self.repo.get_state(state_id)
        incoming = self.repo.incoming_links(state_id)
        supporting_links = [
            link
            for link in incoming
            if link.relation_type
            in {RelationType.SUPPORTS, RelationType.RESONATES_WITH, RelationType.DERIVED_FROM, RelationType.SIMILAR_TO}
        ]
        contradicting_links = [link for link in incoming if link.relation_type == RelationType.CONTRADICTS]

        active_constraints = []
        violated_constraints = []
        satisfied_constraints = []
        for constraint in self.repo.constraints.values():
            if constraint.applies_to(state):
                active_constraints.append(constraint.name)
                if constraint.is_satisfied(state):
                    satisfied_constraints.append(constraint.name)
                else:
                    violated_constraints.append(constraint.name)

        support_strength = sum(link.strength for link in supporting_links)
        contradiction_strength = sum(link.strength for link in contradicting_links)

        return {
            "state_id": str(state.state_id),
            "state_type": state.state_type,
            "status": state.status,
            "data": state.data,
            "metrics": self._metrics(state),
            "stability_breakdown": self._stability_breakdown(state),
            "constraint_status": {
                "active": active_constraints,
                "satisfied": satisfied_constraints,
                "violated": violated_constraints,
            },
            "support_factors": {
                "total_strength": support_strength,
                "links": [
                    {"from": str(link.source_state_id), "relation": link.relation_type.value, "strength": link.strength}
                    for link in supporting_links
                ],
            },
            "conflict_factors": {
                "total_strength": contradiction_strength,
                "links": [
                    {"from": str(link.source_state_id), "relation": link.relation_type.value, "strength": link.strength}
                    for link in contradicting_links
                ],
                "violated_constraints": violated_constraints,
            },
            "decision_summary": self._decision_summary(state, support_strength, contradiction_strength, violated_constraints),
            # Backward-compatible fields
            "active_constraints": active_constraints,
            "violated_constraints": violated_constraints,
            "supporting_links": [
                {"from": str(link.source_state_id), "relation": link.relation_type.value, "strength": link.strength}
                for link in supporting_links
            ],
            "contradicting_links": [
                {"from": str(link.source_state_id), "relation": link.relation_type.value, "strength": link.strength}
                for link in contradicting_links
            ],
        }

    def explain_comparison(self, state_ids: List[UUID]) -> Dict[str, Any]:
        if not state_ids:
            raise ValueError("state_ids must not be empty")

        states = [self.repo.get_state(state_id) for state_id in state_ids]
        winner = max(states, key=lambda state: state.stability)
        explanations = [self.explain_state(state.state_id) for state in states]

        ranked = sorted(
            [
                {
                    "state_id": str(state.state_id),
                    "claim": state.data.get("claim"),
                    "stability": state.stability,
                    "coherence": state.coherence,
                    "conflict": state.conflict,
                    "entropy": state.entropy,
                    "support": state.support,
                }
                for state in states
            ],
            key=lambda item: item["stability"],
            reverse=True,
        )

        return {
            "winner_state_id": str(winner.state_id),
            "winner_claim": winner.data.get("claim"),
            "ranked_candidates": ranked,
            "reason": self._comparison_reason(ranked),
            "explanations": explanations,
        }

    def _metrics(self, state: State) -> Dict[str, float]:
        return {
            "coherence": state.coherence,
            "conflict": state.conflict,
            "entropy": state.entropy,
            "support": state.support,
            "stability": state.stability,
        }

    def _stability_breakdown(self, state: State) -> Dict[str, float]:
        return {
            "positive": state.coherence + state.support,
            "negative": state.conflict + state.entropy,
            "coherence": state.coherence,
            "support": state.support,
            "conflict": state.conflict,
            "entropy": state.entropy,
            "stability": state.stability,
        }

    def _decision_summary(
        self,
        state: State,
        support_strength: float,
        contradiction_strength: float,
        violated_constraints: List[str],
    ) -> str:
        if violated_constraints:
            return "State is weakened by violated constraints and should be treated cautiously."
        if support_strength > contradiction_strength:
            return "State is primarily supported by incoming evidence."
        if contradiction_strength > support_strength:
            return "State is primarily weakened by contradictory evidence."
        return "State has balanced support and contradiction signals."

    def _comparison_reason(self, ranked: List[Dict[str, Any]]) -> str:
        if len(ranked) == 1:
            return "Only one candidate was provided."
        winner = ranked[0]
        runner_up = ranked[1]
        delta = winner["stability"] - runner_up["stability"]
        return (
            f"Selected candidate has the highest stability score. "
            f"Stability margin over runner-up: {delta:.4f}."
        )
